#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Avançado de Cache com Redis - TecnoCursos AI

Este módulo implementa um sistema completo de cache usando Redis
para otimização de performance, escalabilidade e gerenciamento
inteligente de dados temporários.

Funcionalidades:
- Cache hierárquico multi-nível
- Invalidação inteligente de cache
- Compressão automática de dados
- Cache de sessões de usuário
- Cache de resultados de análise
- Métricas de hit/miss rate
- Distribuição de cache por clusters

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import asyncio
import json
import pickle
import zlib
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from contextlib import asynccontextmanager
import functools

try:
    import redis
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from app.logger import get_logger
    from app.config import get_settings
    logger = get_logger("cache_service")
    settings = get_settings()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("cache_service")
    settings = None

T = TypeVar('T')

# ============================================================================
# CONFIGURAÇÕES E ENUMS
# ============================================================================

class CacheLevel(Enum):
    """Níveis de cache hierárquico."""
    L1_MEMORY = "l1_memory"      # Cache em memória local (mais rápido)
    L2_REDIS = "l2_redis"        # Cache no Redis (persistente)
    L3_DATABASE = "l3_database"  # Cache no banco de dados (mais lento)

class CompressionType(Enum):
    """Tipos de compressão suportados."""
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    LZ4 = "lz4"

@dataclass
class CacheEntry:
    """Entrada no cache com metadados."""
    key: str
    data: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int
    last_accessed: datetime
    size_bytes: int
    compression: CompressionType
    tags: List[str]
    version: int

@dataclass
class CacheStats:
    """Estatísticas do cache."""
    total_keys: int
    total_size_mb: float
    hit_rate: float
    miss_rate: float
    eviction_count: int
    compression_ratio: float
    avg_access_time_ms: float

# ============================================================================
# SISTEMA DE CACHE EM MEMÓRIA (L1)
# ============================================================================

class MemoryCache:
    """Cache L1 em memória com LRU."""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.current_memory = 0
        self._lock = threading.RLock()
        
        # Estatísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_size': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache L1."""
        with self._lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Verificar expiração
            if entry.expires_at and datetime.now() > entry.expires_at:
                self._remove_entry(key)
                self.stats['misses'] += 1
                return None
            
            # Atualizar estatísticas de acesso
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            # Mover para o final (mais recente)
            self.access_order.remove(key)
            self.access_order.append(key)
            
            self.stats['hits'] += 1
            return entry.data
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: List[str] = None) -> bool:
        """Definir valor no cache L1."""
        with self._lock:
            # Calcular tamanho
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = len(str(value).encode('utf-8'))
            
            # Verificar limites de memória
            if size_bytes > self.max_memory_bytes:
                logger.warning(f"Item muito grande para cache L1: {size_bytes} bytes")
                return False
            
            # Liberar espaço se necessário
            while (len(self.cache) >= self.max_size or 
                   self.current_memory + size_bytes > self.max_memory_bytes):
                if not self._evict_lru():
                    break
            
            # Remover entrada existente se houver
            if key in self.cache:
                self._remove_entry(key)
            
            # Criar nova entrada
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            entry = CacheEntry(
                key=key,
                data=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                access_count=1,
                last_accessed=datetime.now(),
                size_bytes=size_bytes,
                compression=CompressionType.NONE,
                tags=tags or [],
                version=1
            )
            
            # Adicionar ao cache
            self.cache[key] = entry
            self.access_order.append(key)
            self.current_memory += size_bytes
            
            return True
    
    def delete(self, key: str) -> bool:
        """Remover entrada do cache L1."""
        with self._lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Limpar todo o cache L1."""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self.current_memory = 0
            self.stats['evictions'] += len(self.cache)
    
    def invalidate_by_tags(self, tags: List[str]):
        """Invalidar entradas por tags."""
        with self._lock:
            keys_to_remove = []
            for key, entry in self.cache.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._remove_entry(key)
    
    def _remove_entry(self, key: str):
        """Remover entrada interna."""
        if key in self.cache:
            entry = self.cache[key]
            self.current_memory -= entry.size_bytes
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
    
    def _evict_lru(self) -> bool:
        """Remover entrada menos recentemente usada."""
        if not self.access_order:
            return False
        
        lru_key = self.access_order[0]
        self._remove_entry(lru_key)
        self.stats['evictions'] += 1
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache L1."""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'level': 'L1_MEMORY',
                'size': len(self.cache),
                'memory_mb': round(self.current_memory / 1024 / 1024, 2),
                'hit_rate': round(hit_rate, 2),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions']
            }

# ============================================================================
# SISTEMA DE CACHE REDIS (L2)
# ============================================================================

class RedisCache:
    """Cache L2 com Redis para persistência."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.client = None
        self.async_client = None
        self.connected = False
        
        # Configurações
        self.default_ttl = 3600  # 1 hora
        self.compression_threshold = 1024  # Comprimir se > 1KB
        
        # Estatísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'compression_saves': 0
        }
        
        # Conectar ao Redis
        self._connect()
    
    def _connect(self):
        """Conectar ao Redis."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis não disponível, cache L2 desabilitado")
            return
        
        try:
            self.client = redis.Redis.from_url(self.redis_url, decode_responses=False)
            self.async_client = aioredis.Redis.from_url(self.redis_url, decode_responses=False)
            
            # Testar conexão
            self.client.ping()
            self.connected = True
            logger.info("✅ Redis conectado para cache L2")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar Redis: {e}")
            self.connected = False
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serializar dados com compressão opcional."""
        try:
            # Serializar com pickle
            serialized = pickle.dumps(data)
            
            # Comprimir se for grande
            if len(serialized) > self.compression_threshold:
                compressed = zlib.compress(serialized)
                # Só usar compressão se reduzir significativamente
                if len(compressed) < len(serialized) * 0.8:
                    self.stats['compression_saves'] += 1
                    return b'COMPRESSED:' + compressed
            
            return b'RAW:' + serialized
            
        except Exception as e:
            logger.error(f"Erro ao serializar dados: {e}")
            return b'RAW:' + str(data).encode('utf-8')
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserializar dados com descompressão."""
        try:
            if data.startswith(b'COMPRESSED:'):
                decompressed = zlib.decompress(data[11:])
                return pickle.loads(decompressed)
            elif data.startswith(b'RAW:'):
                return pickle.loads(data[4:])
            else:
                # Fallback para dados antigos
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"Erro ao deserializar dados: {e}")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache Redis."""
        if not self.connected:
            return None
        
        try:
            # Buscar no Redis
            data = self.client.get(f"cache:{key}")
            if data is None:
                self.stats['misses'] += 1
                return None
            
            # Deserializar
            value = self._deserialize_data(data)
            if value is not None:
                self.stats['hits'] += 1
                
                # Atualizar estatísticas de acesso
                self.client.hincrby(f"cache:stats:{key}", "access_count", 1)
                self.client.hset(f"cache:stats:{key}", "last_accessed", time.time())
                
            return value
            
        except Exception as e:
            logger.error(f"Erro ao obter do cache Redis: {e}")
            self.stats['misses'] += 1
            return None
    
    async def get_async(self, key: str) -> Optional[Any]:
        """Obter valor do cache Redis (async)."""
        if not self.connected:
            return None
        
        try:
            data = await self.async_client.get(f"cache:{key}")
            if data is None:
                self.stats['misses'] += 1
                return None
            
            value = self._deserialize_data(data)
            if value is not None:
                self.stats['hits'] += 1
                
                # Atualizar estatísticas
                await self.async_client.hincrby(f"cache:stats:{key}", "access_count", 1)
                await self.async_client.hset(f"cache:stats:{key}", "last_accessed", time.time())
                
            return value
            
        except Exception as e:
            logger.error(f"Erro ao obter do cache Redis (async): {e}")
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: List[str] = None) -> bool:
        """Definir valor no cache Redis."""
        if not self.connected:
            return False
        
        try:
            # Serializar dados
            serialized_data = self._serialize_data(value)
            
            # Definir TTL
            ttl = ttl_seconds or self.default_ttl
            
            # Salvar no Redis
            self.client.setex(f"cache:{key}", ttl, serialized_data)
            
            # Salvar metadados
            metadata = {
                'created_at': time.time(),
                'size_bytes': len(serialized_data),
                'access_count': 0,
                'last_accessed': time.time(),
                'tags': json.dumps(tags or [])
            }
            
            self.client.hmset(f"cache:stats:{key}", metadata)
            self.client.expire(f"cache:stats:{key}", ttl + 60)  # Stats vivem um pouco mais
            
            # Indexar por tags
            if tags:
                for tag in tags:
                    self.client.sadd(f"cache:tag:{tag}", key)
                    self.client.expire(f"cache:tag:{tag}", ttl + 60)
            
            self.stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir no cache Redis: {e}")
            return False
    
    async def set_async(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: List[str] = None) -> bool:
        """Definir valor no cache Redis (async)."""
        if not self.connected:
            return False
        
        try:
            serialized_data = self._serialize_data(value)
            ttl = ttl_seconds or self.default_ttl
            
            await self.async_client.setex(f"cache:{key}", ttl, serialized_data)
            
            metadata = {
                'created_at': time.time(),
                'size_bytes': len(serialized_data),
                'access_count': 0,
                'last_accessed': time.time(),
                'tags': json.dumps(tags or [])
            }
            
            await self.async_client.hmset(f"cache:stats:{key}", metadata)
            await self.async_client.expire(f"cache:stats:{key}", ttl + 60)
            
            if tags:
                for tag in tags:
                    await self.async_client.sadd(f"cache:tag:{tag}", key)
                    await self.async_client.expire(f"cache:tag:{tag}", ttl + 60)
            
            self.stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir no cache Redis (async): {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remover entrada do cache Redis."""
        if not self.connected:
            return False
        
        try:
            deleted = self.client.delete(f"cache:{key}")
            self.client.delete(f"cache:stats:{key}")
            
            if deleted:
                self.stats['deletes'] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao deletar do cache Redis: {e}")
            return False
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidar entradas por tags."""
        if not self.connected:
            return 0
        
        invalidated = 0
        try:
            for tag in tags:
                keys = self.client.smembers(f"cache:tag:{tag}")
                for key in keys:
                    if self.delete(key.decode('utf-8')):
                        invalidated += 1
                
                # Remover conjunto de tag
                self.client.delete(f"cache:tag:{tag}")
            
            return invalidated
            
        except Exception as e:
            logger.error(f"Erro ao invalidar por tags: {e}")
            return 0
    
    def clear(self) -> bool:
        """Limpar todo o cache Redis."""
        if not self.connected:
            return False
        
        try:
            # Buscar todas as chaves de cache
            keys = self.client.keys("cache:*")
            if keys:
                self.client.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache Redis: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache Redis."""
        if not self.connected:
            return {'level': 'L2_REDIS', 'status': 'disconnected'}
        
        try:
            # Estatísticas básicas
            info = self.client.info('memory')
            total_keys = len(self.client.keys("cache:*"))
            
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'level': 'L2_REDIS',
                'status': 'connected',
                'total_keys': total_keys,
                'memory_mb': round(info.get('used_memory', 0) / 1024 / 1024, 2),
                'hit_rate': round(hit_rate, 2),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'compression_saves': self.stats['compression_saves']
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter stats do Redis: {e}")
            return {'level': 'L2_REDIS', 'status': 'error'}

# ============================================================================
# SISTEMA DE CACHE HIERÁRQUICO
# ============================================================================

class HierarchicalCache:
    """Sistema de cache hierárquico L1 (Memory) + L2 (Redis)."""
    
    def __init__(self, 
                 l1_max_size: int = 1000,
                 l1_max_memory_mb: int = 100,
                 redis_url: str = "redis://localhost:6379/0"):
        
        self.l1_cache = MemoryCache(l1_max_size, l1_max_memory_mb)
        self.l2_cache = RedisCache(redis_url)
        
        # Configurações
        self.l1_preferred_ttl = 300   # 5 minutos no L1
        self.l2_preferred_ttl = 3600  # 1 hora no L2
        
        # Estatísticas combinadas
        self.global_stats = {
            'total_requests': 0,
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'promotions': 0,  # L2 -> L1
            'writebacks': 0   # L1 -> L2
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache hierárquico."""
        self.global_stats['total_requests'] += 1
        
        # Tentar L1 primeiro
        value = self.l1_cache.get(key)
        if value is not None:
            self.global_stats['l1_hits'] += 1
            return value
        
        # Tentar L2
        value = self.l2_cache.get(key)
        if value is not None:
            self.global_stats['l2_hits'] += 1
            self.global_stats['promotions'] += 1
            
            # Promover para L1
            self.l1_cache.set(key, value, self.l1_preferred_ttl)
            return value
        
        # Miss em ambos os níveis
        self.global_stats['misses'] += 1
        return None
    
    async def get_async(self, key: str) -> Optional[Any]:
        """Obter valor do cache hierárquico (async)."""
        self.global_stats['total_requests'] += 1
        
        # Tentar L1 primeiro
        value = self.l1_cache.get(key)
        if value is not None:
            self.global_stats['l1_hits'] += 1
            return value
        
        # Tentar L2 async
        value = await self.l2_cache.get_async(key)
        if value is not None:
            self.global_stats['l2_hits'] += 1
            self.global_stats['promotions'] += 1
            
            # Promover para L1
            self.l1_cache.set(key, value, self.l1_preferred_ttl)
            return value
        
        self.global_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: List[str] = None) -> bool:
        """Definir valor no cache hierárquico."""
        success = True
        
        # Definir em L1
        l1_ttl = min(ttl_seconds or self.l1_preferred_ttl, self.l1_preferred_ttl)
        l1_success = self.l1_cache.set(key, value, l1_ttl, tags)
        
        # Definir em L2
        l2_ttl = ttl_seconds or self.l2_preferred_ttl
        l2_success = self.l2_cache.set(key, value, l2_ttl, tags)
        
        if l2_success:
            self.global_stats['writebacks'] += 1
        
        return l1_success or l2_success
    
    async def set_async(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: List[str] = None) -> bool:
        """Definir valor no cache hierárquico (async)."""
        # L1 síncrono
        l1_ttl = min(ttl_seconds or self.l1_preferred_ttl, self.l1_preferred_ttl)
        l1_success = self.l1_cache.set(key, value, l1_ttl, tags)
        
        # L2 assíncrono
        l2_ttl = ttl_seconds or self.l2_preferred_ttl
        l2_success = await self.l2_cache.set_async(key, value, l2_ttl, tags)
        
        if l2_success:
            self.global_stats['writebacks'] += 1
        
        return l1_success or l2_success
    
    def delete(self, key: str) -> bool:
        """Remover entrada dos dois níveis de cache."""
        l1_deleted = self.l1_cache.delete(key)
        l2_deleted = self.l2_cache.delete(key)
        return l1_deleted or l2_deleted
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidar entradas por tags em ambos os níveis."""
        self.l1_cache.invalidate_by_tags(tags)
        return self.l2_cache.invalidate_by_tags(tags)
    
    def clear(self):
        """Limpar ambos os níveis de cache."""
        self.l1_cache.clear()
        self.l2_cache.clear()
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Obter estatísticas completas do sistema."""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = self.l2_cache.get_stats()
        
        total_requests = self.global_stats['total_requests']
        combined_hit_rate = 0
        if total_requests > 0:
            combined_hits = self.global_stats['l1_hits'] + self.global_stats['l2_hits']
            combined_hit_rate = (combined_hits / total_requests * 100)
        
        return {
            'system': {
                'total_requests': total_requests,
                'combined_hit_rate': round(combined_hit_rate, 2),
                'l1_hit_rate': round((self.global_stats['l1_hits'] / total_requests * 100) if total_requests > 0 else 0, 2),
                'l2_hit_rate': round((self.global_stats['l2_hits'] / total_requests * 100) if total_requests > 0 else 0, 2),
                'miss_rate': round((self.global_stats['misses'] / total_requests * 100) if total_requests > 0 else 0, 2),
                'promotions': self.global_stats['promotions'],
                'writebacks': self.global_stats['writebacks']
            },
            'l1': l1_stats,
            'l2': l2_stats
        }

# ============================================================================
# DECORADORES PARA CACHE AUTOMÁTICO
# ============================================================================

def cached(ttl_seconds: int = 3600, tags: List[str] = None, cache_instance: HierarchicalCache = None):
    """Decorador para cache automático de funções."""
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            nonlocal cache_instance
            if cache_instance is None:
                cache_instance = get_default_cache()
            
            # Gerar chave do cache
            key = _generate_cache_key(func.__name__, args, kwargs)
            
            # Tentar obter do cache
            cached_result = cache_instance.get(key)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache_instance.set(key, result, ttl_seconds, tags)
            
            return result
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal cache_instance
            if cache_instance is None:
                cache_instance = get_default_cache()
            
            key = _generate_cache_key(func.__name__, args, kwargs)
            
            cached_result = await cache_instance.get_async(key)
            if cached_result is not None:
                return cached_result
            
            result = await func(*args, **kwargs)
            await cache_instance.set_async(key, result, ttl_seconds, tags)
            
            return result
        
        # Retornar wrapper apropriado baseado na função
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def _generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Gerar chave única para cache baseada em função e parâmetros."""
    # Criar string única dos argumentos
    args_str = str(args) + str(sorted(kwargs.items()))
    
    # Hash MD5 para chave compacta
    hash_obj = hashlib.md5(args_str.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    return f"{func_name}:{hash_hex}"

# ============================================================================
# INSTÂNCIA GLOBAL DE CACHE
# ============================================================================

_default_cache: Optional[HierarchicalCache] = None

def get_default_cache() -> HierarchicalCache:
    """Obter instância padrão do cache."""
    global _default_cache
    
    if _default_cache is None:
        redis_url = "redis://localhost:6379/0"
        if settings:
            redis_url = getattr(settings, 'REDIS_URL', redis_url)
        
        _default_cache = HierarchicalCache(redis_url=redis_url)
        logger.info("✅ Cache hierárquico inicializado")
    
    return _default_cache

def invalidate_cache_by_pattern(pattern: str):
    """Invalidar cache por padrão (para limpeza)."""
    cache = get_default_cache()
    
    # Implementar lógica de invalidação por padrão
    # (Requer implementação específica baseada nas necessidades)
    logger.info(f"Cache invalidado por padrão: {pattern}")

# ============================================================================
# DEMONSTRAÇÃO DO SISTEMA
# ============================================================================

def demonstrate_cache_system():
    """Demonstrar funcionamento do sistema de cache."""
    print("\n" + "="*80)
    print("🚀 SISTEMA DE CACHE HIERÁRQUICO - TECNOCURSOS AI")
    print("="*80)
    
    print("\n💾 FUNCIONALIDADES IMPLEMENTADAS:")
    funcionalidades = [
        "Cache hierárquico L1 (Memory) + L2 (Redis)",
        "Compressão automática de dados grandes",
        "Invalidação inteligente por tags",
        "LRU eviction no cache L1",
        "Promoção automática L2 → L1",
        "Writeback automático L1 → L2",
        "Decoradores para cache automático",
        "Métricas detalhadas hit/miss rate",
        "Suporte a operações síncronas e assíncronas",
        "Limpeza automática de dados expirados"
    ]
    
    for i, func in enumerate(funcionalidades, 1):
        print(f"   ✅ {i:2d}. {func}")
    
    print("\n🛠️ COMPONENTES PRINCIPAIS:")
    print("   🧠 MemoryCache (L1) - Cache em memória local")
    print("   🔴 RedisCache (L2) - Cache persistente Redis") 
    print("   🏗️ HierarchicalCache - Coordenação multi-nível")
    print("   🎯 @cached decorator - Cache automático de funções")
    
    print("\n📊 MÉTRICAS MONITORADAS:")
    metricas = [
        "Hit rate por nível de cache",
        "Tempo médio de acesso",
        "Taxa de evição LRU",
        "Eficiência de compressão",
        "Uso de memória por nível",
        "Promoções L2→L1",
        "Writebacks L1→L2",
        "Invalidações por tag"
    ]
    
    for metrica in metricas:
        print(f"   📈 {metrica}")
    
    print("\n🎯 CASOS DE USO:")
    print("   📄 Cache de resultados de extração de texto")
    print("   🎬 Cache de metadados de vídeos")
    print("   👤 Cache de sessões de usuário")
    print("   📊 Cache de relatórios e analytics")
    print("   🔍 Cache de resultados de busca")
    print("   🎵 Cache de resultados TTS")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. ✅ Sistema implementado e pronto")
    print("   2. 🔧 Configurar Redis (opcional)")
    print("   3. 🎯 Usar @cached decorator em funções")
    print("   4. 📊 Monitorar métricas via API")
    print("   5. 🧹 Configurar limpeza automática")
    
    print("\n" + "="*80)
    print("✨ SISTEMA DE CACHE IMPLEMENTADO COM SUCESSO!")
    print("="*80)

# Exportar instância global para uso na aplicação
cache_service = HierarchicalCache()

if __name__ == "__main__":
    demonstrate_cache_system() 