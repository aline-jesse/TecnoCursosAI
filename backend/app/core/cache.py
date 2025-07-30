"""
Sistema de Cache Avançado - TecnoCursos AI
Cache distribuído com Redis e fallback para memória local
"""

import json
import pickle
import hashlib
import asyncio
from typing import Any, Optional, Union, Dict, List, Callable
from datetime import datetime, timedelta
from functools import wraps
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError
import logging

logger = logging.getLogger(__name__)

class CacheConfig:
    """Configuração do sistema de cache"""
    
    # TTL padrão por tipo de cache (em segundos)
    DEFAULT_TTL = {
        "user_session": 3600,      # 1 hora
        "user_profile": 1800,      # 30 minutos
        "project_list": 300,       # 5 minutos
        "project_detail": 600,     # 10 minutos
        "file_metadata": 1800,     # 30 minutos
        "video_info": 3600,        # 1 hora
        "api_response": 60,        # 1 minuto
        "search_results": 300,     # 5 minutos
        "analytics": 900,          # 15 minutos
        "static_data": 86400,      # 24 horas
    }
    
    # Prefixos para organização
    PREFIXES = {
        "user": "user:",
        "project": "proj:",
        "file": "file:",
        "video": "video:",
        "api": "api:",
        "search": "search:",
        "analytics": "analytics:",
        "session": "session:",
        "temp": "temp:",
    }

class AdvancedCacheManager:
    """Gerenciador de cache avançado com Redis e fallback"""
    
    def __init__(
        self, 
        redis_url: Optional[str] = None,
        default_ttl: int = 300,
        max_memory_items: int = 1000
    ):
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = default_ttl
        self.max_memory_items = max_memory_items
        
        # Cache em memória como fallback
        self.memory_cache: Dict[str, Dict] = {}
        self.memory_access_times: Dict[str, datetime] = {}
        
        # Conectar ao Redis se disponível
        if redis_url:
            self._connect_redis(redis_url)
    
    def _connect_redis(self, redis_url: str):
        """Conecta ao Redis com tratamento de erro"""
        try:
            self.redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            logger.info("Conectado ao Redis para cache distribuído")
        except Exception as e:
            logger.warning(f"Falha ao conectar Redis: {e}. Usando cache em memória.")
            self.redis_client = None
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Busca valor no cache"""
        try:
            # Tentar Redis primeiro
            if self.redis_client:
                result = await self._get_from_redis(key)
                if result is not None:
                    return result
            
            # Fallback para memória
            return self._get_from_memory(key, default)
            
        except Exception as e:
            logger.error(f"Erro ao buscar cache {key}: {e}")
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        cache_type: str = "api"
    ) -> bool:
        """Define valor no cache"""
        try:
            # Determinar TTL
            if ttl is None:
                ttl = CacheConfig.DEFAULT_TTL.get(cache_type, self.default_ttl)
            
            # Tentar Redis primeiro
            if self.redis_client:
                success = await self._set_in_redis(key, value, ttl)
                if success:
                    return True
            
            # Fallback para memória
            return self._set_in_memory(key, value, ttl)
            
        except Exception as e:
            logger.error(f"Erro ao definir cache {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            success = True
            
            # Remover do Redis
            if self.redis_client:
                await self.redis_client.delete(key)
            
            # Remover da memória
            if key in self.memory_cache:
                del self.memory_cache[key]
                del self.memory_access_times[key]
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover cache {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Remove chaves que correspondem ao padrão"""
        try:
            count = 0
            
            # Limpar no Redis
            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    count += await self.redis_client.delete(*keys)
            
            # Limpar na memória
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern.replace("*", "") in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
                del self.memory_access_times[key]
                count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Erro ao limpar padrão {pattern}: {e}")
            return 0
    
    async def _get_from_redis(self, key: str) -> Any:
        """Busca valor no Redis"""
        try:
            data = await self.redis_client.get(key)
            if data:
                # Tentar decodificar JSON primeiro
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    # Fallback para pickle
                    return pickle.loads(data.encode('latin1'))
            return None
        except (ConnectionError, TimeoutError):
            logger.warning("Redis indisponível, usando cache local")
            return None
    
    async def _set_in_redis(self, key: str, value: Any, ttl: int) -> bool:
        """Define valor no Redis"""
        try:
            # Tentar JSON primeiro (mais eficiente)
            try:
                serialized = json.dumps(value, default=str)
            except (TypeError, ValueError):
                # Fallback para pickle
                serialized = pickle.dumps(value).decode('latin1')
            
            await self.redis_client.setex(key, ttl, serialized)
            return True
            
        except (ConnectionError, TimeoutError):
            logger.warning("Redis indisponível para escrita")
            return False
    
    def _get_from_memory(self, key: str, default: Any = None) -> Any:
        """Busca valor na memória local"""
        if key in self.memory_cache:
            cache_entry = self.memory_cache[key]
            
            # Verificar expiração
            if datetime.now() < cache_entry["expires_at"]:
                # Atualizar tempo de acesso
                self.memory_access_times[key] = datetime.now()
                return cache_entry["value"]
            else:
                # Remover entrada expirada
                del self.memory_cache[key]
                del self.memory_access_times[key]
        
        return default
    
    def _set_in_memory(self, key: str, value: Any, ttl: int) -> bool:
        """Define valor na memória local"""
        try:
            # Verificar limite de memória
            if len(self.memory_cache) >= self.max_memory_items:
                self._evict_lru()
            
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self.memory_cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.now()
            }
            self.memory_access_times[key] = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir cache em memória: {e}")
            return False
    
    def _evict_lru(self):
        """Remove entradas menos usadas (LRU)"""
        if not self.memory_access_times:
            return
        
        # Encontrar chave menos recentemente acessada
        lru_key = min(self.memory_access_times.items(), key=lambda x: x[1])[0]
        
        # Remover da cache
        del self.memory_cache[lru_key]
        del self.memory_access_times[lru_key]
    
    async def get_or_set(
        self, 
        key: str, 
        func: Callable,
        ttl: Optional[int] = None,
        cache_type: str = "api"
    ) -> Any:
        """Busca no cache ou executa função e armazena resultado"""
        # Tentar buscar no cache primeiro
        result = await self.get(key)
        if result is not None:
            return result
        
        # Executar função
        if asyncio.iscoroutinefunction(func):
            result = await func()
        else:
            result = func()
        
        # Armazenar no cache
        await self.set(key, result, ttl, cache_type)
        
        return result
    
    def make_key(self, prefix: str, *args) -> str:
        """Cria chave de cache consistente"""
        # Combinar argumentos
        key_parts = [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        
        # Criar hash se muito longo
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            key_string = f"{key_parts[0]}:...:{key_hash}"
        
        return f"{CacheConfig.PREFIXES.get(prefix, prefix)}{key_string}"

# Instância global do cache
cache_manager = AdvancedCacheManager()

# Decorador para cache automático
def cached(
    ttl: Optional[int] = None,
    cache_type: str = "api",
    key_prefix: str = "func"
):
    """Decorador para cache automático de funções"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Criar chave única
            key_parts = [func.__name__] + list(args) + [f"{k}={v}" for k, v in kwargs.items()]
            cache_key = cache_manager.make_key(key_prefix, *key_parts)
            
            return await cache_manager.get_or_set(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl,
                cache_type
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Funções de conveniência
async def get_cached(key: str, default: Any = None) -> Any:
    """Busca valor no cache global"""
    return await cache_manager.get(key, default)

async def set_cached(key: str, value: Any, ttl: int = 300) -> bool:
    """Define valor no cache global"""
    return await cache_manager.set(key, value, ttl)

async def delete_cached(key: str) -> bool:
    """Remove valor do cache global"""
    return await cache_manager.delete(key)

async def clear_cache_pattern(pattern: str) -> int:
    """Limpa cache por padrão"""
    return await cache_manager.clear_pattern(pattern)

# Inicialização do cache
def init_cache(redis_url: Optional[str] = None):
    """Inicializa sistema de cache"""
    global cache_manager
    cache_manager = AdvancedCacheManager(redis_url)
    logger.info("Sistema de cache inicializado")
