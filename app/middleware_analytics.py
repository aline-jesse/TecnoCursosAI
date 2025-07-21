#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de Analytics - TecnoCursos AI

Este módulo implementa middleware para coleta automática de métricas
e integração perfeita do sistema de analytics com o FastAPI.

Funcionalidades:
- Coleta automática de métricas de requisições
- Rastreamento de performance por endpoint
- Detecção de usuários ativos
- Coleta de estatísticas de erro
- Integração com sistema de cache
- Monitoramento de WebSocket

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import time
import asyncio
from datetime import datetime
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
import logging

try:
    from app.services.analytics_service import get_analytics_service, start_analytics_system
    from app.services.websocket_service import get_websocket_services
    from app.services.cache_service import get_default_cache
    from app.auth import decode_jwt_token
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False

logger = logging.getLogger("analytics_middleware")

# ============================================================================
# MIDDLEWARE DE ANALYTICS
# ============================================================================

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para coleta automática de métricas de analytics.
    
    Intercepta todas as requisições HTTP e coleta métricas de:
    - Tempo de resposta
    - Status codes
    - Endpoints acessados
    - Usuários ativos
    - Padrões de uso
    """
    
    def __init__(self, app: ASGIApp, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled and SERVICES_AVAILABLE
        self.analytics_service = None
        self.websocket_service = None
        self.cache_service = None
        
        # Contadores locais para performance
        self.request_count = 0
        self.error_count = 0
        
        if self.enabled:
            self._initialize_services()
    
    def _initialize_services(self):
        """Inicializar serviços de analytics."""
        try:
            # Inicializar sistema se necessário
            start_analytics_system()
            
            # Obter instâncias dos serviços
            self.analytics_service = get_analytics_service()
            self.websocket_service = get_websocket_services()
            self.cache_service = get_default_cache()
            
            logger.info("✅ Middleware de analytics inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar middleware de analytics: {e}")
            self.enabled = False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processar requisição com coleta de métricas."""
        if not self.enabled:
            return await call_next(request)
        
        # Início da medição
        start_time = time.time()
        request_timestamp = datetime.now()
        
        # Extrair informações da requisição
        endpoint = request.url.path
        method = request.method
        user_agent = request.headers.get("user-agent", "unknown")
        ip_address = self._get_client_ip(request)
        user_id = await self._extract_user_id(request)
        
        # Atualizar contador de requisições
        self.request_count += 1
        
        try:
            # Processar requisição
            response = await call_next(request)
            
            # Calcular métricas
            response_time = time.time() - start_time
            status_code = response.status_code
            
            # Coletar métricas se for endpoint da API
            if endpoint.startswith("/api/"):
                await self._collect_api_metrics(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=status_code,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=request_timestamp
                )
            
            # Rastrear usuário ativo se autenticado
            if user_id:
                await self._track_active_user(user_id, endpoint, timestamp=request_timestamp)
            
            # Log de requisições importantes
            if response_time > 2.0:  # Requisições lentas
                logger.warning(f"⚠️ Requisição lenta: {endpoint} ({response_time:.2f}s)")
            
            if status_code >= 400:  # Erros
                self.error_count += 1
                logger.warning(f"❌ Erro HTTP {status_code}: {endpoint}")
            
            return response
            
        except Exception as e:
            # Erro na aplicação
            self.error_count += 1
            response_time = time.time() - start_time
            
            # Registrar erro
            await self._collect_api_metrics(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=500,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=request_timestamp,
                error=str(e)
            )
            
            logger.error(f"💥 Erro na aplicação: {endpoint} - {e}")
            raise  # Re-raise para tratamento normal
    
    async def _collect_api_metrics(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_id: Optional[int],
        ip_address: str,
        user_agent: str,
        timestamp: datetime,
        error: Optional[str] = None
    ):
        """Coletar métricas da API."""
        try:
            if not self.analytics_service:
                return
            
            collector = self.analytics_service['collector']
            
            # Registrar métricas básicas
            collector.record_request(
                endpoint=endpoint,
                response_time=response_time,
                status_code=status_code,
                user_id=user_id
            )
            
            # Métricas detalhadas para cache/análise
            detailed_metrics = {
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'status_code': status_code,
                'user_id': user_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': timestamp.isoformat(),
                'error': error
            }
            
            # Salvar no cache para análise posterior
            if self.cache_service:
                cache_key = f"request_metrics:{timestamp.timestamp()}"
                await self.cache_service.set_async(
                    cache_key, 
                    detailed_metrics, 
                    ttl_seconds=3600,  # 1 hora
                    tags=['metrics', 'requests']
                )
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas da API: {e}")
    
    async def _track_active_user(self, user_id: int, endpoint: str, timestamp: datetime):
        """Rastrear usuário ativo."""
        try:
            if not self.cache_service:
                return
            
            # Atualizar última atividade do usuário
            user_activity = {
                'user_id': user_id,
                'last_endpoint': endpoint,
                'last_activity': timestamp.isoformat(),
                'request_count': 1
            }
            
            # Verificar atividade anterior
            cache_key = f"user_activity:{user_id}"
            existing_activity = await self.cache_service.get_async(cache_key)
            
            if existing_activity:
                user_activity['request_count'] = existing_activity.get('request_count', 0) + 1
            
            # Salvar atividade atualizada (TTL 30 minutos)
            await self.cache_service.set_async(
                cache_key,
                user_activity,
                ttl_seconds=1800,
                tags=['user_activity', f'user_{user_id}']
            )
            
        except Exception as e:
            logger.error(f"Erro ao rastrear usuário ativo: {e}")
    
    async def _extract_user_id(self, request: Request) -> Optional[int]:
        """Extrair ID do usuário da requisição."""
        try:
            # Tentar extrair do cabeçalho Authorization
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remover "Bearer "
                user_data = decode_jwt_token(token)
                return user_data.get('sub') if user_data else None
            
            # Tentar extrair de cookie de sessão
            session_token = request.cookies.get("session_token")
            if session_token:
                user_data = decode_jwt_token(session_token)
                return user_data.get('sub') if user_data else None
            
            return None
            
        except Exception:
            return None
    
    def _get_client_ip(self, request: Request) -> str:
        """Obter IP do cliente considerando proxies."""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # IP direto
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"

# ============================================================================
# MIDDLEWARE DE CACHE INTELIGENTE
# ============================================================================

class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware para cache automático de respostas da API.
    
    Cacheia automaticamente respostas de endpoints GET
    que são adequados para cache, melhorando performance.
    """
    
    def __init__(self, app: ASGIApp, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled and SERVICES_AVAILABLE
        self.cache_service = None
        
        # Configurações de cache
        self.cacheable_endpoints = {
            "/api/stats": 300,        # 5 minutos
            "/api/health": 60,        # 1 minuto
            "/api/analytics": 180,    # 3 minutos
            "/api/files": 120,        # 2 minutos
        }
        
        self.cache_headers = {
            "X-Cache": "HIT",
            "X-Cache-TTL": "",
            "X-Cache-Key": ""
        }
        
        if self.enabled:
            self.cache_service = get_default_cache()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processar requisição com cache inteligente."""
        if not self.enabled or request.method != "GET":
            return await call_next(request)
        
        endpoint = request.url.path
        
        # Verificar se endpoint é cacheável
        cache_ttl = self._get_cache_ttl(endpoint)
        if not cache_ttl:
            return await call_next(request)
        
        # Gerar chave de cache
        cache_key = self._generate_cache_key(request)
        
        try:
            # Tentar obter do cache
            cached_response = await self.cache_service.get_async(cache_key)
            
            if cached_response:
                # Cache HIT
                logger.debug(f"🎯 Cache HIT: {endpoint}")
                
                response_data = cached_response['data']
                headers = cached_response.get('headers', {})
                status_code = cached_response.get('status_code', 200)
                
                # Adicionar headers de cache
                headers.update({
                    "X-Cache": "HIT",
                    "X-Cache-Key": cache_key[:16] + "...",
                    "X-Cache-Time": cached_response.get('cached_at', '')
                })
                
                from starlette.responses import JSONResponse
                return JSONResponse(
                    content=response_data,
                    status_code=status_code,
                    headers=headers
                )
            
            # Cache MISS - processar requisição
            response = await call_next(request)
            
            # Cachear resposta se for sucesso
            if 200 <= response.status_code < 300:
                await self._cache_response(cache_key, response, cache_ttl)
                
                # Adicionar header indicando cache miss
                response.headers["X-Cache"] = "MISS"
                response.headers["X-Cache-Key"] = cache_key[:16] + "..."
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no middleware de cache: {e}")
            return await call_next(request)
    
    def _get_cache_ttl(self, endpoint: str) -> Optional[int]:
        """Obter TTL de cache para endpoint."""
        for pattern, ttl in self.cacheable_endpoints.items():
            if endpoint.startswith(pattern):
                return ttl
        return None
    
    def _generate_cache_key(self, request: Request) -> str:
        """Gerar chave única para cache."""
        import hashlib
        
        # Componentes da chave
        components = [
            request.url.path,
            str(sorted(request.query_params.items())),
            request.headers.get("accept", ""),
            request.headers.get("accept-language", "")
        ]
        
        # Hash MD5 da combinação
        key_string = "|".join(components)
        hash_obj = hashlib.md5(key_string.encode('utf-8'))
        
        return f"api_cache:{hash_obj.hexdigest()}"
    
    async def _cache_response(self, cache_key: str, response: Response, ttl: int):
        """Cachear resposta da API."""
        try:
            # Ler corpo da resposta
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Tentar decodificar como JSON
            import json
            try:
                response_data = json.loads(body.decode('utf-8'))
            except:
                response_data = body.decode('utf-8')
            
            # Preparar dados para cache
            cache_data = {
                'data': response_data,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'cached_at': datetime.now().isoformat()
            }
            
            # Salvar no cache
            await self.cache_service.set_async(
                cache_key,
                cache_data,
                ttl_seconds=ttl,
                tags=['api_cache', 'responses']
            )
            
            # Recriar response com mesmo corpo
            from starlette.responses import Response as StarletteResponse
            new_response = StarletteResponse(
                content=body,
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.media_type
            )
            
            # Substituir iterador de corpo
            response.body_iterator = iter([body])
            
        except Exception as e:
            logger.error(f"Erro ao cachear resposta: {e}")

# ============================================================================
# MIDDLEWARE DE MONITORAMENTO DE WEBSOCKET
# ============================================================================

class WebSocketMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware para monitoramento de conexões WebSocket.
    
    Rastreia conexões WebSocket e integra com sistema de analytics.
    """
    
    def __init__(self, app: ASGIApp, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled and SERVICES_AVAILABLE
        self.websocket_service = None
        
        if self.enabled:
            self.websocket_service = get_websocket_services()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitorar conexões WebSocket."""
        if not self.enabled:
            return await call_next(request)
        
        # Verificar se é upgrade para WebSocket
        if (request.headers.get("upgrade", "").lower() == "websocket" and
            request.headers.get("connection", "").lower() == "upgrade"):
            
            logger.info(f"🔌 Nova conexão WebSocket: {request.url.path}")
            
            # Coletar informações da conexão
            connection_info = {
                'path': request.url.path,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.headers.get("user-agent", "unknown"),
                'timestamp': datetime.now().isoformat()
            }
            
            # Salvar no analytics se disponível
            try:
                analytics = get_analytics_service()
                collector = analytics['collector']
                
                # Incrementar contador de conexões WebSocket
                collector.active_connections.add(connection_info['ip_address'])
                
            except Exception as e:
                logger.error(f"Erro ao registrar conexão WebSocket: {e}")
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Obter IP do cliente."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"

# ============================================================================
# FUNÇÃO DE CONFIGURAÇÃO
# ============================================================================

def setup_analytics_middlewares(app, enable_analytics: bool = True, enable_cache: bool = True):
    """
    Configurar todos os middlewares de analytics na aplicação FastAPI.
    
    Args:
        app: Instância do FastAPI
        enable_analytics: Se deve habilitar coleta de métricas
        enable_cache: Se deve habilitar cache automático
    """
    try:
        if enable_analytics:
            app.add_middleware(AnalyticsMiddleware, enabled=True)
            logger.info("✅ Middleware de analytics adicionado")
        
        if enable_cache:
            app.add_middleware(CacheMiddleware, enabled=True)
            logger.info("✅ Middleware de cache adicionado")
        
        # WebSocket monitoring sempre habilitado se serviços disponíveis
        app.add_middleware(WebSocketMonitoringMiddleware, enabled=SERVICES_AVAILABLE)
        logger.info("✅ Middleware de WebSocket adicionado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar middlewares: {e}")
        return False

# ============================================================================
# DEMONSTRAÇÃO
# ============================================================================

def demonstrate_middleware_system():
    """Demonstrar configuração dos middlewares."""
    print("\n" + "="*80)
    print("🔧 SISTEMA DE MIDDLEWARES ANALYTICS - TECNOCURSOS AI")
    print("="*80)
    
    print("\n⚙️ MIDDLEWARES IMPLEMENTADOS:")
    middlewares = [
        "AnalyticsMiddleware - Coleta automática de métricas",
        "CacheMiddleware - Cache inteligente de APIs",
        "WebSocketMonitoringMiddleware - Monitoramento de conexões",
        "Integração automática com FastAPI",
        "Coleta de métricas por endpoint",
        "Rastreamento de usuários ativos",
        "Cache automático de respostas",
        "Monitoramento de performance",
        "Detecção de requisições lentas",
        "Logging automático de erros"
    ]
    
    for i, middleware in enumerate(middlewares, 1):
        print(f"   ✅ {i:2d}. {middleware}")
    
    print("\n📊 MÉTRICAS COLETADAS:")
    metricas = [
        "Tempo de resposta por endpoint",
        "Status codes de resposta",
        "Usuários ativos em tempo real",
        "IPs e User-Agents",
        "Padrões de uso da API",
        "Taxa de cache hit/miss",
        "Conexões WebSocket ativas",
        "Erros e exceções"
    ]
    
    for metrica in metricas:
        print(f"   📈 {metrica}")
    
    print("\n🚀 CONFIGURAÇÃO AUTOMÁTICA:")
    print("   1. Adicionar ao FastAPI: setup_analytics_middlewares(app)")
    print("   2. Analytics automático para todas as rotas")
    print("   3. Cache inteligente para endpoints GET")
    print("   4. Monitoramento WebSocket transparente")
    print("   5. Integração com Redis e sistema de alertas")
    
    print("\n" + "="*80)
    print("✨ MIDDLEWARES DE ANALYTICS IMPLEMENTADOS!")
    print("="*80)

if __name__ == "__main__":
    demonstrate_middleware_system() 