"""
Sistema Avançado de Rate Limiting - TecnoCursos AI
=================================================

Middleware de rate limiting com múltiplas estratégias:
- Rate limiting por IP
- Rate limiting por usuário autenticado  
- Rate limiting por endpoint
- Rate limiting adaptativo baseado em carga do sistema
- Cache distribuído com Redis
- Configurações personalizáveis por rota
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis

try:
    from app.logger import get_logger
    logger = get_logger("rate_limiting")
except ImportError:
    import logging
    logger = logging.getLogger("rate_limiting")

class RateLimitStrategy:
    """Estratégias de rate limiting"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    ADAPTIVE = "adaptive"

class RateLimitConfig:
    """Configuração de rate limiting por endpoint"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10,
        strategy: str = RateLimitStrategy.SLIDING_WINDOW,
        exempt_roles: Optional[Set[str]] = None,
        custom_key_func: Optional[callable] = None
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        self.strategy = strategy
        self.exempt_roles = exempt_roles or set()
        self.custom_key_func = custom_key_func

class AdvancedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware avançado de rate limiting com múltiplas estratégias
    """
    
    def __init__(
        self,
        app,
        redis_url: Optional[str] = None,
        enable_redis: bool = True,
        default_config: Optional[RateLimitConfig] = None
    ):
        super().__init__(app)
        self.redis_client = None
        self.enable_redis = enable_redis
        self.local_cache = defaultdict(lambda: defaultdict(deque))
        self.token_buckets = defaultdict(dict)
        self.system_load_factor = 1.0
        
        # Configuração padrão
        self.default_config = default_config or RateLimitConfig()
        
        # Configurações específicas por endpoint
        self.endpoint_configs = {
            "/api/auth/login": RateLimitConfig(
                requests_per_minute=5,
                requests_per_hour=50,
                burst_limit=2,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            "/api/auth/register": RateLimitConfig(
                requests_per_minute=3,
                requests_per_hour=10,
                burst_limit=1,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            "/api/files/upload": RateLimitConfig(
                requests_per_minute=20,
                requests_per_hour=200,
                burst_limit=5,
                strategy=RateLimitStrategy.TOKEN_BUCKET
            ),
            "/api/tts/generate": RateLimitConfig(
                requests_per_minute=30,
                requests_per_hour=500,
                burst_limit=10,
                strategy=RateLimitStrategy.ADAPTIVE
            ),
            "/api/video/generate": RateLimitConfig(
                requests_per_minute=10,
                requests_per_hour=100,
                burst_limit=3,
                strategy=RateLimitStrategy.TOKEN_BUCKET
            )
        }
        
        # Inicializar Redis se disponível
        if enable_redis and redis_url:
            asyncio.create_task(self._init_redis(redis_url))
            
        logger.info("✅ Advanced Rate Limiting Middleware inicializado")

    async def _init_redis(self, redis_url: str):
        """Inicializar conexão Redis"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Cache Redis conectado para rate limiting")
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível para rate limiting: {e}")
            self.redis_client = None

    def _get_client_key(self, request: Request) -> str:
        """Gerar chave única para identificar cliente"""
        # Priorizar usuário autenticado
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Usar IP como fallback
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Hash para evitar chaves muito longas
        key_data = f"{client_ip}:{user_agent}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        
        return f"ip:{key_hash}"

    def _get_endpoint_config(self, request: Request) -> RateLimitConfig:
        """Obter configuração específica do endpoint"""
        path = request.url.path
        
        # Verificar configurações específicas
        for endpoint_pattern, config in self.endpoint_configs.items():
            if path.startswith(endpoint_pattern):
                return config
        
        return self.default_config

    async def _check_rate_limit_redis(
        self, 
        client_key: str, 
        config: RateLimitConfig, 
        endpoint: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Verificar rate limit usando Redis"""
        now = time.time()
        
        # Chaves para diferentes janelas de tempo
        minute_key = f"rl:{client_key}:{endpoint}:minute:{int(now // 60)}"
        hour_key = f"rl:{client_key}:{endpoint}:hour:{int(now // 3600)}"
        
        pipe = self.redis_client.pipeline()
        
        # Incrementar contadores
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)
        pipe.incr(hour_key) 
        pipe.expire(hour_key, 3600)
        
        # Obter contadores atuais
        pipe.get(minute_key)
        pipe.get(hour_key)
        
        results = await pipe.execute()
        
        minute_count = int(results[4] or 0)
        hour_count = int(results[5] or 0)
        
        # Aplicar fator de carga do sistema
        minute_limit = int(config.requests_per_minute * self.system_load_factor)
        hour_limit = int(config.requests_per_hour * self.system_load_factor)
        
        # Verificar limites
        if minute_count > minute_limit or hour_count > hour_limit:
            return False, {
                "minute_count": minute_count,
                "hour_count": hour_count,
                "minute_limit": minute_limit,
                "hour_limit": hour_limit,
                "reset_time": int((now // 60 + 1) * 60)
            }
        
        return True, {
            "minute_count": minute_count,
            "hour_count": hour_count,
            "minute_limit": minute_limit,
            "hour_limit": hour_limit,
            "remaining_minute": minute_limit - minute_count,
            "remaining_hour": hour_limit - hour_count
        }

    def _check_rate_limit_local(
        self, 
        client_key: str, 
        config: RateLimitConfig, 
        endpoint: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Verificar rate limit usando cache local"""
        now = time.time()
        
        # Limpar entradas antigas
        self._cleanup_local_cache(now)
        
        # Obter histórico do cliente
        client_history = self.local_cache[client_key][endpoint]
        
        # Contar requisições na última hora e minuto
        minute_ago = now - 60
        hour_ago = now - 3600
        
        minute_count = sum(1 for req_time in client_history if req_time > minute_ago)
        hour_count = sum(1 for req_time in client_history if req_time > hour_ago)
        
        # Aplicar fator de carga do sistema
        minute_limit = int(config.requests_per_minute * self.system_load_factor)
        hour_limit = int(config.requests_per_hour * self.system_load_factor)
        
        # Verificar limites
        if minute_count >= minute_limit or hour_count >= hour_limit:
            return False, {
                "minute_count": minute_count,
                "hour_count": hour_count,
                "minute_limit": minute_limit,
                "hour_limit": hour_limit,
                "reset_time": int(now + 60)
            }
        
        # Adicionar requisição atual
        client_history.append(now)
        
        return True, {
            "minute_count": minute_count + 1,
            "hour_count": hour_count + 1,
            "minute_limit": minute_limit,
            "hour_limit": hour_limit,
            "remaining_minute": minute_limit - minute_count - 1,
            "remaining_hour": hour_limit - hour_count - 1
        }

    def _cleanup_local_cache(self, now: float):
        """Limpar entradas antigas do cache local"""
        hour_ago = now - 3600
        
        for client_key in list(self.local_cache.keys()):
            for endpoint in list(self.local_cache[client_key].keys()):
                history = self.local_cache[client_key][endpoint]
                
                # Remover entradas antigas
                while history and history[0] < hour_ago:
                    history.popleft()
                
                # Remover endpoint se vazio
                if not history:
                    del self.local_cache[client_key][endpoint]
            
            # Remover cliente se vazio
            if not self.local_cache[client_key]:
                del self.local_cache[client_key]

    def _check_token_bucket(
        self, 
        client_key: str, 
        config: RateLimitConfig, 
        endpoint: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Implementar estratégia de token bucket"""
        now = time.time()
        bucket_key = f"{client_key}:{endpoint}"
        
        if bucket_key not in self.token_buckets:
            self.token_buckets[bucket_key] = {
                "tokens": config.burst_limit,
                "last_refill": now
            }
        
        bucket = self.token_buckets[bucket_key]
        
        # Calcular tokens a adicionar
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * (config.requests_per_minute / 60.0)
        
        # Atualizar bucket
        bucket["tokens"] = min(
            config.burst_limit,
            bucket["tokens"] + tokens_to_add
        )
        bucket["last_refill"] = now
        
        # Verificar se há tokens disponíveis
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, {
                "tokens_remaining": int(bucket["tokens"]),
                "bucket_capacity": config.burst_limit
            }
        
        return False, {
            "tokens_remaining": 0,
            "bucket_capacity": config.burst_limit,
            "retry_after": int(60 / config.requests_per_minute)
        }

    def _update_system_load_factor(self):
        """Atualizar fator de carga do sistema (implementação adaptativa)"""
        # Implementação simplificada - pode ser expandida
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Calcular fator de carga (1.0 = normal, < 1.0 = restrito)
            if cpu_percent > 80 or memory_percent > 80:
                self.system_load_factor = 0.5  # Reduzir limites pela metade
            elif cpu_percent > 60 or memory_percent > 60:
                self.system_load_factor = 0.7  # Reduzir limites em 30%
            else:
                self.system_load_factor = 1.0  # Limites normais
                
        except ImportError:
            self.system_load_factor = 1.0

    async def dispatch(self, request: Request, call_next):
        """Processar requisição através do middleware"""
        try:
            # Verificar se é endpoint excluído
            if self._should_skip_rate_limiting(request):
                return await call_next(request)
            
            # Obter configuração do endpoint
            config = self._get_endpoint_config(request)
            client_key = self._get_client_key(request)
            endpoint = request.url.path
            
            # Verificar se usuário tem role exempta
            if self._user_is_exempt(request, config):
                return await call_next(request)
            
            # Atualizar fator de carga para estratégia adaptativa
            if config.strategy == RateLimitStrategy.ADAPTIVE:
                self._update_system_load_factor()
            
            # Escolher estratégia de verificação
            if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                allowed, info = self._check_token_bucket(client_key, config, endpoint)
            elif self.redis_client:
                allowed, info = await self._check_rate_limit_redis(client_key, config, endpoint)
            else:
                allowed, info = self._check_rate_limit_local(client_key, config, endpoint)
            
            # Aplicar rate limiting
            if not allowed:
                logger.warning(
                    f"🚫 Rate limit excedido - Cliente: {client_key}, Endpoint: {endpoint}"
                )
                
                headers = {
                    "X-RateLimit-Limit-Minute": str(info.get("minute_limit", 0)),
                    "X-RateLimit-Limit-Hour": str(info.get("hour_limit", 0)),
                    "X-RateLimit-Remaining-Minute": "0",
                    "X-RateLimit-Remaining-Hour": "0",
                    "X-RateLimit-Reset": str(info.get("reset_time", 0)),
                    "Retry-After": str(info.get("retry_after", 60))
                }
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": "Rate limit exceeded",
                        "info": info,
                        "strategy": config.strategy
                    },
                    headers=headers
                )
            
            # Processar requisição
            response = await call_next(request)
            
            # Adicionar headers informativos
            if "minute_limit" in info:
                response.headers["X-RateLimit-Limit-Minute"] = str(info["minute_limit"])
                response.headers["X-RateLimit-Remaining-Minute"] = str(info.get("remaining_minute", 0))
            
            if "hour_limit" in info:
                response.headers["X-RateLimit-Limit-Hour"] = str(info["hour_limit"])
                response.headers["X-RateLimit-Remaining-Hour"] = str(info.get("remaining_hour", 0))
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro no rate limiting middleware: {e}")
            # Em caso de erro, permitir requisição
            return await call_next(request)

    def _should_skip_rate_limiting(self, request: Request) -> bool:
        """Verificar se endpoint deve ser excluído do rate limiting"""
        skip_paths = {
            "/health",
            "/metrics", 
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static/"
        }
        
        path = request.url.path
        return any(path.startswith(skip_path) for skip_path in skip_paths)

    def _user_is_exempt(self, request: Request, config: RateLimitConfig) -> bool:
        """Verificar se usuário tem role exempta"""
        if not config.exempt_roles:
            return False
        
        user_role = getattr(request.state, 'user_role', None)
        return user_role in config.exempt_roles

# Configurações pré-definidas para diferentes tipos de API
API_CONFIGS = {
    "auth": RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=100,
        burst_limit=3,
        strategy=RateLimitStrategy.SLIDING_WINDOW
    ),
    "upload": RateLimitConfig(
        requests_per_minute=20,
        requests_per_hour=200,
        burst_limit=5,
        strategy=RateLimitStrategy.TOKEN_BUCKET
    ),
    "processing": RateLimitConfig(
        requests_per_minute=30,
        requests_per_hour=500,
        burst_limit=10,
        strategy=RateLimitStrategy.ADAPTIVE
    ),
    "premium": RateLimitConfig(
        requests_per_minute=100,
        requests_per_hour=2000,
        burst_limit=20,
        strategy=RateLimitStrategy.SLIDING_WINDOW,
        exempt_roles={"admin", "premium"}
    )
}

def setup_rate_limiting(app, redis_url: Optional[str] = None, config_name: str = "default"):
    """
    Configurar rate limiting na aplicação
    
    Args:
        app: Instância do FastAPI
        redis_url: URL do Redis (opcional)
        config_name: Nome da configuração pré-definida
    """
    config = API_CONFIGS.get(config_name, RateLimitConfig())
    
    middleware = AdvancedRateLimitMiddleware(
        app,
        redis_url=redis_url,
        enable_redis=bool(redis_url),
        default_config=config
    )
    
    app.add_middleware(AdvancedRateLimitMiddleware, **middleware.__dict__)
    logger.info(f"✅ Rate limiting configurado com profile: {config_name}")

if __name__ == "__main__":
    print("🔧 SISTEMA AVANÇADO DE RATE LIMITING - TECNOCURSOS AI")
    print("=" * 60)
    print("\n📊 ESTRATÉGIAS IMPLEMENTADAS:")
    
    strategies = [
        "Fixed Window - Janela fixa de tempo",
        "Sliding Window - Janela deslizante",
        "Token Bucket - Balde de tokens para rajadas", 
        "Adaptive - Adaptativo baseado na carga do sistema"
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"   ✅ {i}. {strategy}")
    
    print("\n🎯 RECURSOS:")
    features = [
        "Rate limiting por IP e usuário autenticado",
        "Configurações específicas por endpoint",
        "Cache distribuído com Redis",
        "Fallback para cache local",
        "Headers informativos de rate limit",
        "Roles e usuários exempts",
        "Monitoramento de carga do sistema",
        "Estratégias múltiplas por endpoint"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"   🚀 {i}. {feature}")
    
    print("\n✨ RATE LIMITING AVANÇADO IMPLEMENTADO!") 