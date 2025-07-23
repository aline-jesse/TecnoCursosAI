#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Cache para Cenas - TecnoCursos AI

Este módulo implementa cache inteligente com Redis para otimizar performance
dos endpoints de cenas, seguindo as melhores práticas do FastAPI.

Funcionalidades:
- Cache automático de consultas frequentes
- Invalidação inteligente de cache
- Compressão de dados para economia de memória
- TTL dinâmico baseado no tipo de dados
- Métricas de cache para monitoramento
- Fallback para operação sem Redis

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import json
import redis
import pickle
import gzip
import hashlib
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass

try:
    from app.config import get_settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Estatísticas de cache"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

class ScenesCacheService:
    """
    Serviço de cache inteligente para cenas
    
    Implementa cache com Redis seguindo as melhores práticas:
    - Chaves estruturadas e previsíveis
    - TTL baseado no tipo de conteúdo
    - Compressão para economia de memória
    - Fallback para operação sem Redis
    - Invalidação em cascata
    """
    
    def __init__(self):
        self.redis_client = None
        self.stats = CacheStats()
        self.cache_enabled = False
        self._init_redis()
        
        # Configurações de TTL por tipo de dados
        self.ttl_config = {
            'scene_list': 300,      # 5 minutos - listagens mudam frequentemente
            'scene_detail': 900,    # 15 minutos - detalhes mudam menos
            'scene_summary': 600,   # 10 minutos - resumos para dashboard
            'project_scenes': 300,  # 5 minutos - cenas por projeto
            'user_stats': 1800,     # 30 minutos - estatísticas do usuário
            'templates': 3600       # 1 hora - templates mudam raramente
        }
    
    def _init_redis(self):
        """Inicializar conexão Redis com fallback"""
        try:
            if CONFIG_AVAILABLE:
                settings = get_settings()
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'redis_host', 'localhost'),
                    port=getattr(settings, 'redis_port', 6379),
                    db=getattr(settings, 'redis_db', 0),
                    decode_responses=False,  # Para suportar dados binários
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                    max_connections=20
                )
                
                # Testar conexão
                self.redis_client.ping()
                self.cache_enabled = True
                logger.info("✅ Cache Redis conectado com sucesso")
                
            else:
                logger.warning("⚠️ Configurações não disponíveis - cache desabilitado")
                
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível: {e} - operando sem cache")
            self.redis_client = None
            self.cache_enabled = False
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Gerar chave de cache estruturada e única"""
        # Ordenar parâmetros para consistência
        sorted_params = sorted(kwargs.items())
        
        # Criar hash dos parâmetros para chaves curtas
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        
        return f"scenes:{prefix}:{params_hash}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serializar dados com compressão"""
        try:
            # Serializar com pickle
            pickled_data = pickle.dumps(data)
            
            # Comprimir se vantajoso
            if len(pickled_data) > 1024:  # Comprimir apenas dados grandes
                compressed_data = gzip.compress(pickled_data)
                if len(compressed_data) < len(pickled_data) * 0.9:  # 10% economia mínima
                    return b'GZIP:' + compressed_data
            
            return b'RAW:' + pickled_data
            
        except Exception as e:
            logger.error(f"Erro ao serializar dados: {e}")
            raise
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserializar dados com descompressão"""
        try:
            if data.startswith(b'GZIP:'):
                # Descomprimir
                compressed_data = data[5:]  # Remove 'GZIP:' prefix
                pickled_data = gzip.decompress(compressed_data)
            elif data.startswith(b'RAW:'):
                # Dados não comprimidos
                pickled_data = data[4:]  # Remove 'RAW:' prefix
            else:
                # Formato antigo (compatibilidade)
                pickled_data = data
            
            return pickle.loads(pickled_data)
            
        except Exception as e:
            logger.error(f"Erro ao deserializar dados: {e}")
            raise
    
    def get(self, cache_type: str, **kwargs) -> Optional[Any]:
        """
        Recuperar dados do cache
        
        Args:
            cache_type: Tipo de cache (scene_list, scene_detail, etc.)
            **kwargs: Parâmetros para gerar chave única
        
        Returns:
            Dados do cache ou None se não encontrado
        """
        if not self.cache_enabled:
            return None
        
        try:
            key = self._generate_cache_key(cache_type, **kwargs)
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                self.stats.hits += 1
                data = self._deserialize_data(cached_data)
                
                logger.debug(f"Cache HIT: {key}")
                return data
            else:
                self.stats.misses += 1
                logger.debug(f"Cache MISS: {key}")
                return None
                
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Erro ao recuperar cache: {e}")
            return None
    
    def set(self, cache_type: str, data: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """
        Armazenar dados no cache
        
        Args:
            cache_type: Tipo de cache
            data: Dados para cachear
            ttl: TTL customizado (opcional)
            **kwargs: Parâmetros para gerar chave
        
        Returns:
            True se sucesso, False caso contrário
        """
        if not self.cache_enabled:
            return False
        
        try:
            key = self._generate_cache_key(cache_type, **kwargs)
            serialized_data = self._serialize_data(data)
            
            # Usar TTL configurado ou padrão
            cache_ttl = ttl or self.ttl_config.get(cache_type, 300)
            
            result = self.redis_client.setex(key, cache_ttl, serialized_data)
            
            if result:
                self.stats.sets += 1
                logger.debug(f"Cache SET: {key} (TTL: {cache_ttl}s)")
                return True
            else:
                logger.warning(f"Falha ao armazenar cache: {key}")
                return False
                
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Erro ao armazenar cache: {e}")
            return False
    
    def delete(self, cache_type: str, **kwargs) -> bool:
        """Deletar entrada específica do cache"""
        if not self.cache_enabled:
            return False
        
        try:
            key = self._generate_cache_key(cache_type, **kwargs)
            result = self.redis_client.delete(key)
            
            if result:
                self.stats.deletes += 1
                logger.debug(f"Cache DELETE: {key}")
                return True
            else:
                return False
                
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Erro ao deletar cache: {e}")
            return False
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """
        Invalidar todo cache relacionado a um usuário
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Número de chaves deletadas
        """
        if not self.cache_enabled:
            return 0
        
        try:
            # Buscar todas as chaves relacionadas ao usuário
            pattern = f"scenes:*:*user_id*{user_id}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                self.stats.deletes += deleted_count
                logger.info(f"Cache invalidado para usuário {user_id}: {deleted_count} chaves")
                return deleted_count
            else:
                return 0
                
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Erro ao invalidar cache do usuário {user_id}: {e}")
            return 0
    
    def invalidate_project_cache(self, project_id: int) -> int:
        """Invalidar cache relacionado a um projeto"""
        if not self.cache_enabled:
            return 0
        
        try:
            pattern = f"scenes:*:*project_id*{project_id}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                self.stats.deletes += deleted_count
                logger.info(f"Cache invalidado para projeto {project_id}: {deleted_count} chaves")
                return deleted_count
            else:
                return 0
                
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Erro ao invalidar cache do projeto {project_id}: {e}")
            return 0
    
    def invalidate_scene_cache(self, scene_id: int) -> int:
        """Invalidar cache relacionado a uma cena específica"""
        if not self.cache_enabled:
            return 0
        
        try:
            pattern = f"scenes:*:*scene_id*{scene_id}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                self.stats.deletes += deleted_count
                logger.info(f"Cache invalidado para cena {scene_id}: {deleted_count} chaves")
                return deleted_count
            else:
                return 0
                
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Erro ao invalidar cache da cena {scene_id}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de cache"""
        return {
            "enabled": self.cache_enabled,
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "sets": self.stats.sets,
            "deletes": self.stats.deletes,
            "errors": self.stats.errors,
            "hit_rate": round(self.stats.hit_rate, 2),
            "ttl_config": self.ttl_config
        }
    
    def flush_all(self) -> bool:
        """Limpar todo cache de cenas (usar com cuidado)"""
        if not self.cache_enabled:
            return False
        
        try:
            pattern = "scenes:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                logger.warning(f"Cache FLUSH: {deleted_count} chaves de cenas deletadas")
                return True
            else:
                return True
                
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False

# ============================================================================
# DECORADORES DE CACHE
# ============================================================================

def cache_result(cache_type: str, ttl: Optional[int] = None):
    """
    Decorador para cachear automaticamente resultados de funções
    
    Args:
        cache_type: Tipo de cache
        ttl: TTL customizado
    
    Usage:
        @cache_result('scene_list', ttl=300)
        async def get_scenes(user_id: int, project_id: int):
            return scenes
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair parâmetros para chave de cache
            cache_params = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': kwargs
            }
            
            # Tentar recuperar do cache
            cached_result = scenes_cache.get(cache_type, **cache_params)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = await func(*args, **kwargs)
            scenes_cache.set(cache_type, result, ttl, **cache_params)
            
            return result
        
        return wrapper
    return decorator

# ============================================================================
# INSTÂNCIA GLOBAL DO SERVIÇO
# ============================================================================

# Instância singleton do serviço de cache
scenes_cache = ScenesCacheService()

# Funções de conveniência para uso direto
def get_cache(cache_type: str, **kwargs) -> Optional[Any]:
    """Função de conveniência para recuperar cache"""
    return scenes_cache.get(cache_type, **kwargs)

def set_cache(cache_type: str, data: Any, ttl: Optional[int] = None, **kwargs) -> bool:
    """Função de conveniência para armazenar cache"""
    return scenes_cache.set(cache_type, data, ttl, **kwargs)

def invalidate_cache(cache_type: str, **kwargs) -> bool:
    """Função de conveniência para invalidar cache"""
    return scenes_cache.delete(cache_type, **kwargs) 