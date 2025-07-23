"""
Sistema de Cache Redis
Gerencia cache para melhorar performance da aplicação
"""

import json
import pickle
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import redis
import asyncio
from functools import wraps

from backend.app.config import settings
from backend.app.logger import logger


class CacheService:
    """Serviço de cache Redis"""
    
    def __init__(self):
        self.redis_client = None
        self.is_connected = False
        self._connection_retries = 0
        self._max_retries = 3
        
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Testar conexão
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.ping
            )
            
            self.is_connected = True
            self._connection_retries = 0
            logger.info("Conectado ao Redis com sucesso")
            
        except Exception as e:
            self.is_connected = False
            self._connection_retries += 1
            logger.error(f"Erro ao conectar ao Redis: {e}")
            
            if self._connection_retries < self._max_retries:
                logger.info(f"Tentativa {self._connection_retries}/{self._max_retries} de reconexão em 5s")
                await asyncio.sleep(5)
                await self.connect()
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.close
            )
            self.is_connected = False
            logger.info("Desconectado do Redis")
    
    def _ensure_connection(func):
        """Decorator para garantir conexão"""
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                logger.warning("Redis não disponível, operação ignorada")
                return None
            
            try:
                return await func(self, *args, **kwargs)
            except redis.ConnectionError:
                self.is_connected = False
                logger.error("Conexão Redis perdida")
                return None
            except Exception as e:
                logger.error(f"Erro na operação Redis: {e}")
                return None
        
        return wrapper
    
    @_ensure_connection
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Define um valor no cache"""
        try:
            if serialize:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, default=str)
                elif not isinstance(value, str):
                    value = pickle.dumps(value)
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.redis_client.set(key, value, ex=expire)
            )
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao definir cache {key}: {e}")
            return False
    
    @_ensure_connection
    async def get(
        self, 
        key: str, 
        deserialize: bool = True,
        default: Any = None
    ) -> Any:
        """Obtém um valor do cache"""
        try:
            value = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.get, key
            )
            
            if value is None:
                return default
            
            if deserialize:
                try:
                    # Tentar JSON primeiro
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    try:
                        # Tentar pickle
                        return pickle.loads(value)
                    except:
                        # Retornar string original
                        return value
            
            return value
            
        except Exception as e:
            logger.error(f"Erro ao obter cache {key}: {e}")
            return default
    
    @_ensure_connection
    async def delete(self, key: str) -> bool:
        """Remove um valor do cache"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.delete, key
            )
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    @_ensure_connection
    async def exists(self, key: str) -> bool:
        """Verifica se uma chave existe"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.exists, key
            )
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao verificar existência de {key}: {e}")
            return False
    
    @_ensure_connection
    async def expire(self, key: str, seconds: int) -> bool:
        """Define expiração para uma chave"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.expire, key, seconds
            )
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao definir expiração para {key}: {e}")
            return False
    
    @_ensure_connection
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Incrementa um valor numérico"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.incrby, key, amount
            )
            return result
            
        except Exception as e:
            logger.error(f"Erro ao incrementar {key}: {e}")
            return None
    
    @_ensure_connection
    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrementa um valor numérico"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.decrby, key, amount
            )
            return result
            
        except Exception as e:
            logger.error(f"Erro ao decrementar {key}: {e}")
            return None
    
    @_ensure_connection
    async def set_hash(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Define um hash"""
        try:
            # Serializar valores do hash
            serialized_mapping = {}
            for field, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[field] = json.dumps(value, default=str)
                elif not isinstance(value, str):
                    serialized_mapping[field] = str(value)
                else:
                    serialized_mapping[field] = value
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.hset, key, mapping=serialized_mapping
            )
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao definir hash {key}: {e}")
            return False
    
    @_ensure_connection
    async def get_hash(self, key: str, field: Optional[str] = None) -> Any:
        """Obtém valor(es) de um hash"""
        try:
            if field:
                value = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.hget, key, field
                )
                if value:
                    try:
                        return json.loads(value)
                    except:
                        return value
                return None
            else:
                hash_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.hgetall, key
                )
                
                # Deserializar valores
                result = {}
                for field, value in hash_data.items():
                    try:
                        result[field] = json.loads(value)
                    except:
                        result[field] = value
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao obter hash {key}: {e}")
            return None
    
    @_ensure_connection
    async def add_to_list(self, key: str, value: Any, position: str = "right") -> bool:
        """Adiciona item a uma lista"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            elif not isinstance(value, str):
                value = str(value)
            
            if position == "left":
                result = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.lpush, key, value
                )
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.rpush, key, value
                )
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar à lista {key}: {e}")
            return False
    
    @_ensure_connection
    async def get_list(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Obtém itens de uma lista"""
        try:
            items = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.lrange, key, start, end
            )
            
            # Deserializar itens
            result = []
            for item in items:
                try:
                    result.append(json.loads(item))
                except:
                    result.append(item)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter lista {key}: {e}")
            return []
    
    @_ensure_connection
    async def add_to_set(self, key: str, *values: Any) -> int:
        """Adiciona valores a um conjunto"""
        try:
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, default=str))
                elif not isinstance(value, str):
                    serialized_values.append(str(value))
                else:
                    serialized_values.append(value)
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.sadd, key, *serialized_values
            )
            return result
            
        except Exception as e:
            logger.error(f"Erro ao adicionar ao conjunto {key}: {e}")
            return 0
    
    @_ensure_connection
    async def get_set(self, key: str) -> set:
        """Obtém membros de um conjunto"""
        try:
            members = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.smembers, key
            )
            
            # Deserializar membros
            result = set()
            for member in members:
                try:
                    result.add(json.loads(member))
                except:
                    result.add(member)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter conjunto {key}: {e}")
            return set()
    
    @_ensure_connection
    async def clear_pattern(self, pattern: str) -> int:
        """Remove todas as chaves que correspondem ao padrão"""
        try:
            keys = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.keys, pattern
            )
            
            if keys:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.delete, *keys
                )
                return result
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao limpar padrão {pattern}: {e}")
            return 0
    
    @_ensure_connection
    async def get_info(self) -> Dict[str, Any]:
        """Obtém informações do Redis"""
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.info
            )
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do Redis: {e}")
            return {}


# Instância global do serviço de cache
cache_service = CacheService()


def cache_result(key_prefix: str, expire: int = 3600):
    """Decorator para cache de resultados de função"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave do cache
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Tentar obter do cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit para {cache_key}")
                return cached_result
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Salvar no cache
            if result is not None:
                await cache_service.set(cache_key, result, expire=expire)
                logger.debug(f"Resultado cacheado para {cache_key}")
            
            return result
        
        return wrapper
    return decorator


async def initialize_cache():
    """Inicializa o serviço de cache"""
    await cache_service.connect()


async def cleanup_cache():
    """Limpa e desconecta o cache"""
    await cache_service.disconnect()


# Funções específicas para diferentes tipos de cache
class UserCache:
    """Cache específico para usuários"""
    
    @staticmethod
    async def set_user(user_id: str, user_data: Dict[str, Any], expire: int = 1800):
        """Cache de dados do usuário"""
        return await cache_service.set(f"user:{user_id}", user_data, expire=expire)
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Obtém dados do usuário do cache"""
        return await cache_service.get(f"user:{user_id}")
    
    @staticmethod
    async def invalidate_user(user_id: str):
        """Invalida cache do usuário"""
        return await cache_service.delete(f"user:{user_id}")


class ProjectCache:
    """Cache específico para projetos"""
    
    @staticmethod
    async def set_projects(user_id: str, projects: List[Dict[str, Any]], expire: int = 600):
        """Cache de projetos do usuário"""
        return await cache_service.set(f"projects:{user_id}", projects, expire=expire)
    
    @staticmethod
    async def get_projects(user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Obtém projetos do cache"""
        return await cache_service.get(f"projects:{user_id}")
    
    @staticmethod
    async def invalidate_projects(user_id: str):
        """Invalida cache de projetos"""
        return await cache_service.delete(f"projects:{user_id}")


class StatsCache:
    """Cache específico para estatísticas"""
    
    @staticmethod
    async def set_dashboard_stats(user_id: str, stats: Dict[str, Any], expire: int = 300):
        """Cache de estatísticas do dashboard"""
        return await cache_service.set(f"stats:dashboard:{user_id}", stats, expire=expire)
    
    @staticmethod
    async def get_dashboard_stats(user_id: str) -> Optional[Dict[str, Any]]:
        """Obtém estatísticas do dashboard"""
        return await cache_service.get(f"stats:dashboard:{user_id}")
    
    @staticmethod
    async def increment_file_upload(user_id: str):
        """Incrementa contador de uploads"""
        return await cache_service.increment(f"counter:uploads:{user_id}")
    
    @staticmethod
    async def increment_video_generation(user_id: str):
        """Incrementa contador de vídeos gerados"""
        return await cache_service.increment(f"counter:videos:{user_id}")


class SessionCache:
    """Cache para sessões"""
    
    @staticmethod
    async def set_active_session(user_id: str, session_data: Dict[str, Any], expire: int = 86400):
        """Define sessão ativa"""
        return await cache_service.set(f"session:{user_id}", session_data, expire=expire)
    
    @staticmethod
    async def get_active_session(user_id: str) -> Optional[Dict[str, Any]]:
        """Obtém sessão ativa"""
        return await cache_service.get(f"session:{user_id}")
    
    @staticmethod
    async def invalidate_session(user_id: str):
        """Invalida sessão"""
        return await cache_service.delete(f"session:{user_id}")
    
    @staticmethod
    async def add_activity(user_id: str, activity: Dict[str, Any]):
        """Adiciona atividade recente"""
        await cache_service.add_to_list(f"activity:{user_id}", activity, position="left")
        # Manter apenas as 20 atividades mais recentes
        activities = await cache_service.get_list(f"activity:{user_id}", 0, 19)
        await cache_service.delete(f"activity:{user_id}")
        for act in reversed(activities):
            await cache_service.add_to_list(f"activity:{user_id}", act, position="right")
    
    @staticmethod
    async def get_recent_activities(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém atividades recentes"""
        return await cache_service.get_list(f"activity:{user_id}", 0, limit - 1) 