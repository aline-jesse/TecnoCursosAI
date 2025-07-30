"""
Rate Limiting Middleware - TecnoCursos AI
Sistema avançado de rate limiting com múltiplas estratégias
"""

import time
import hashlib
from typing import Dict, Optional, Callable
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import asyncio
import redis
from datetime import datetime, timedelta

class RateLimitConfig:
    """Configuração de rate limiting"""
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_limit: int = 10,
        block_duration: int = 300,  # 5 minutos
        whitelist: list = None,
        blacklist: list = None
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.block_duration = block_duration
        self.whitelist = whitelist or []
        self.blacklist = blacklist or []

class AdvancedRateLimiter:
    """Rate limiter avançado com múltiplas estratégias"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_store: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}
        
        # Configurações por endpoint
        self.endpoint_configs = {
            "/api/auth/login": RateLimitConfig(
                requests_per_minute=5,
                burst_limit=3,
                block_duration=900  # 15 minutos para login
            ),
            "/api/auth/register": RateLimitConfig(
                requests_per_minute=3,
                burst_limit=2,
                block_duration=1800  # 30 minutos para registro
            ),
            "/api/files/upload": RateLimitConfig(
                requests_per_minute=10,
                burst_limit=5,
                block_duration=300
            ),
            "default": RateLimitConfig(
                requests_per_minute=100,
                burst_limit=20,
                block_duration=60
            )
        }
    
    def get_client_id(self, request: Request) -> str:
        """Identifica cliente único (IP + User-Agent)"""
        # Tentar obter IP real através de proxies
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host
        
        # Combinar IP com User-Agent para identificação mais precisa
        user_agent = request.headers.get("User-Agent", "")
        client_id = hashlib.md5(f"{client_ip}:{user_agent}".encode()).hexdigest()
        
        return client_id
    
    def get_endpoint_config(self, path: str) -> RateLimitConfig:
        """Obtém configuração específica do endpoint"""
        # Buscar configuração exata
        if path in self.endpoint_configs:
            return self.endpoint_configs[path]
        
        # Buscar por padrão de path
        for pattern, config in self.endpoint_configs.items():
            if pattern != "default" and path.startswith(pattern):
                return config
        
        return self.endpoint_configs["default"]
    
    async def is_rate_limited(self, request: Request) -> tuple[bool, Dict[str, any]]:
        """Verifica se request deve ser limitado"""
        client_id = self.get_client_id(request)
        path = request.url.path
        config = self.get_endpoint_config(path)
        current_time = time.time()
        
        # Verificar se IP está bloqueado
        if client_id in self.blocked_ips:
            if current_time < self.blocked_ips[client_id]:
                return True, {
                    "error": "IP temporariamente bloqueado",
                    "retry_after": int(self.blocked_ips[client_id] - current_time),
                    "reason": "Muitas tentativas"
                }
            else:
                # Remover do bloqueio se expirou
                del self.blocked_ips[client_id]
        
        # Verificar whitelist/blacklist
        client_ip = request.client.host
        if client_ip in config.blacklist:
            return True, {"error": "IP bloqueado permanentemente"}
        
        if client_ip in config.whitelist:
            return False, {}
        
        # Rate limiting baseado em janela deslizante
        window_start = current_time - 60  # Janela de 1 minuto
        
        if self.redis_client:
            # Usar Redis para armazenamento distribuído
            return await self._check_redis_limit(client_id, path, config, current_time)
        else:
            # Usar memória local
            return self._check_memory_limit(client_id, path, config, current_time, window_start)
    
    async def _check_redis_limit(
        self, 
        client_id: str, 
        path: str, 
        config: RateLimitConfig, 
        current_time: float
    ) -> tuple[bool, Dict[str, any]]:
        """Rate limiting usando Redis"""
        key = f"rate_limit:{client_id}:{path}"
        window_start = current_time - 60
        
        pipe = self.redis_client.pipeline()
        
        # Remover requests antigas
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Contar requests na janela atual
        pipe.zcard(key)
        
        # Adicionar request atual
        pipe.zadd(key, {str(current_time): current_time})
        
        # Definir expiração
        pipe.expire(key, 120)
        
        results = await pipe.execute()
        request_count = results[1]
        
        if request_count >= config.requests_per_minute:
            # Bloquear IP se necessário
            if request_count >= config.requests_per_minute + config.burst_limit:
                self.blocked_ips[client_id] = current_time + config.block_duration
            
            return True, {
                "error": "Rate limit excedido",
                "limit": config.requests_per_minute,
                "window": "1 minuto",
                "retry_after": 60,
                "current_count": request_count
            }
        
        return False, {
            "limit": config.requests_per_minute,
            "remaining": config.requests_per_minute - request_count - 1,
            "window": "1 minuto"
        }
    
    def _check_memory_limit(
        self, 
        client_id: str, 
        path: str, 
        config: RateLimitConfig, 
        current_time: float,
        window_start: float
    ) -> tuple[bool, Dict[str, any]]:
        """Rate limiting usando memória local"""
        key = f"{client_id}:{path}"
        requests = self.memory_store[key]
        
        # Remover requests antigas
        while requests and requests[0] < window_start:
            requests.popleft()
        
        request_count = len(requests)
        
        if request_count >= config.requests_per_minute:
            # Bloquear IP se necessário
            if request_count >= config.requests_per_minute + config.burst_limit:
                self.blocked_ips[client_id] = current_time + config.block_duration
            
            return True, {
                "error": "Rate limit excedido",
                "limit": config.requests_per_minute,
                "window": "1 minuto",
                "retry_after": 60,
                "current_count": request_count
            }
        
        # Adicionar request atual
        requests.append(current_time)
        
        return False, {
            "limit": config.requests_per_minute,
            "remaining": config.requests_per_minute - request_count - 1,
            "window": "1 minuto"
        }

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.rate_limiter = AdvancedRateLimiter(redis_client)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Pular rate limiting para endpoints específicos
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/favicon.ico"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Verificar rate limit
        is_limited, info = await self.rate_limiter.is_rate_limited(request)
        
        if is_limited:
            return Response(
                content=f'{{"error": "{info.get("error", "Rate limit exceeded")}", "details": {info}}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(info.get("retry_after", 60)),
                    "X-RateLimit-Limit": str(info.get("limit", 0)),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Processar request normalmente
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        if "remaining" in info:
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Window"] = info["window"]
        
        return response

# Factory function
def create_rate_limit_middleware(app, redis_url: Optional[str] = None):
    """Cria middleware de rate limiting"""
    redis_client = None
    if redis_url:
        try:
            redis_client = redis.from_url(redis_url)
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}")
    
    return RateLimitMiddleware(app, redis_client)
