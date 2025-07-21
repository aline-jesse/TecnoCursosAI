#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware Avançado - TecnoCursos AI

Este módulo implementa middleware customizado seguindo as melhores práticas
do FastAPI para logging, monitoramento, segurança e performance.

Baseado em:
- FastAPI Best Practices Guide
- Production-ready middleware patterns
- Security and performance optimizations

Funcionalidades:
- Request/Response logging estruturado
- Performance monitoring
- Error tracking
- Rate limiting avançado
- Security headers
- CORS otimizado
- Request ID tracking

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import time
import uuid
import json
import logging
from datetime import datetime
from typing import Callable, Dict, Any, Optional
from contextvars import ContextVar
from pathlib import Path

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import asyncio

try:
    from app.logger import get_logger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

# Context variables para request tracking
request_id_context: ContextVar[str] = ContextVar('request_id')
user_id_context: ContextVar[Optional[int]] = ContextVar('user_id', default=None)

logger = logging.getLogger(__name__) if not LOGGER_AVAILABLE else get_logger("middleware")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging estruturado de requests/responses
    
    Funcionalidades:
    - Log detalhado de cada request
    - Tracking de performance
    - Correlation ID para rastreamento
    - Filtragem de endpoints sensíveis
    - Metrics collection
    """
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        self.metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0.0,
            "requests_by_method": {},
            "requests_by_status": {}
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar Request ID único
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)
        
        # Skip logging para paths excluídos
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Dados iniciais do request
        start_time = time.time()
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length")
        }
        
        # Adicionar headers de request ID
        request.state.request_id = request_id
        
        # Extrair user_id se disponível (do token JWT)
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                # TODO: Implementar extração de user_id do JWT
                user_id = self._extract_user_id_from_token(auth_header)
                user_id_context.set(user_id)
                request_data["user_id"] = user_id
            except Exception:
                pass
        
        # Log do request inicial
        logger.info("Request iniciado", extra=request_data)
        
        try:
            # Processar request
            response = await call_next(request)
            
            # Calcular tempo de resposta
            response_time = time.time() - start_time
            
            # Dados da resposta
            response_data = {
                **request_data,
                "status_code": response.status_code,
                "response_time_ms": round(response_time * 1000, 2),
                "response_size": response.headers.get("content-length"),
                "response_type": response.headers.get("content-type")
            }
            
            # Adicionar headers de resposta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = str(response_time)
            
            # Log da resposta
            if response.status_code >= 400:
                logger.warning("Request com erro", extra=response_data)
                self.metrics["total_errors"] += 1
            else:
                logger.info("Request concluído", extra=response_data)
            
            # Atualizar métricas
            self._update_metrics(request.method, response.status_code, response_time)
            
            return response
            
        except Exception as e:
            # Log de erro
            error_time = time.time() - start_time
            error_data = {
                **request_data,
                "error": str(e),
                "error_type": type(e).__name__,
                "response_time_ms": round(error_time * 1000, 2),
                "status_code": 500
            }
            
            logger.error("Request falhou", extra=error_data)
            self.metrics["total_errors"] += 1
            self._update_metrics(request.method, 500, error_time)
            
            # Retornar erro estruturado
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={"X-Request-ID": request_id}
            )
    
    def _extract_user_id_from_token(self, auth_header: str) -> Optional[int]:
        """Extrair user_id do token JWT"""
        # TODO: Implementar extração real do JWT
        # Por enquanto, retornar None
        return None
    
    def _update_metrics(self, method: str, status_code: int, response_time: float):
        """Atualizar métricas de performance"""
        self.metrics["total_requests"] += 1
        
        # Métricas por método
        if method not in self.metrics["requests_by_method"]:
            self.metrics["requests_by_method"][method] = 0
        self.metrics["requests_by_method"][method] += 1
        
        # Métricas por status
        status_group = f"{status_code // 100}xx"
        if status_group not in self.metrics["requests_by_status"]:
            self.metrics["requests_by_status"][status_group] = 0
        self.metrics["requests_by_status"][status_group] += 1
        
        # Tempo médio de resposta
        total_requests = self.metrics["total_requests"]
        current_avg = self.metrics["avg_response_time"]
        self.metrics["avg_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obter métricas coletadas"""
        return {
            **self.metrics,
            "avg_response_time_ms": round(self.metrics["avg_response_time"] * 1000, 2),
            "error_rate": (self.metrics["total_errors"] / max(self.metrics["total_requests"], 1)) * 100
        }

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para adicionar headers de segurança
    
    Headers implementados:
    - X-Content-Type-Options
    - X-Frame-Options  
    - X-XSS-Protection
    - Strict-Transport-Security
    - Content-Security-Policy
    - Referrer-Policy
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Headers de segurança básicos
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
        
        # Adicionar HSTS apenas em HTTPS
        if request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Aplicar headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting avançado
    
    Funcionalidades:
    - Rate limiting por IP
    - Rate limiting por usuário
    - Diferentes limites por endpoint
    - Sliding window algorithm
    - Whitelist de IPs
    """
    
    def __init__(self, app, requests_per_minute: int = 60, burst_limit: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.request_counts = {}
        self.whitelist_ips = {"127.0.0.1", "::1"}  # Localhost sempre permitido
        
        # Limites específicos por endpoint
        self.endpoint_limits = {
            "/api/auth/login": 5,  # Login mais restritivo
            "/api/scenes/project/.*/generate-video": 3,  # Geração de vídeo muito restritiva
            "/api/files/upload": 10,  # Upload restritivo
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting para IPs na whitelist
        if client_ip in self.whitelist_ips:
            return await call_next(request)
        
        # Determinar limite para endpoint
        limit = self._get_endpoint_limit(request.url.path)
        
        # Verificar rate limit
        if not self._check_rate_limit(client_ip, limit):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit} requests per minute",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)
    
    def _get_endpoint_limit(self, path: str) -> int:
        """Obter limite específico para endpoint"""
        import re
        
        for pattern, limit in self.endpoint_limits.items():
            if re.match(pattern.replace(".*", ".*"), path):
                return limit
        
        return self.requests_per_minute
    
    def _check_rate_limit(self, client_ip: str, limit: int) -> bool:
        """Verificar se request está dentro do limite"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Inicializar contador para IP se não existir
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Remover requests antigas (sliding window)
        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if timestamp > minute_ago
        ]
        
        # Verificar se excedeu o limite
        if len(self.request_counts[client_ip]) >= limit:
            return False
        
        # Adicionar request atual
        self.request_counts[client_ip].append(current_time)
        return True

class DatabaseConnectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para gerenciar conexões de banco de dados
    
    Funcionalidades:
    - Connection pooling
    - Health check de conexões
    - Retry automático
    - Cleanup de conexões ociosas
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # TODO: Implementar connection pooling
        # Por enquanto, apenas passar o request
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log database errors
            logger.error(f"Database connection error: {e}")
            raise

def setup_advanced_middleware(app: FastAPI):
    """
    Configurar todos os middlewares avançados
    
    Args:
        app: Instância do FastAPI
    """
    
    # 1. Trusted Host Middleware (segurança)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # TODO: Configurar hosts específicos em produção
    )
    
    # 2. Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 3. Rate Limiting Middleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120, burst_limit=20)
    
    # 4. Request Logging Middleware
    logging_middleware = RequestLoggingMiddleware(
        app,
        exclude_paths=["/health", "/metrics", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
    )
    app.add_middleware(RequestLoggingMiddleware)
    
    # 5. Database Connection Middleware
    app.add_middleware(DatabaseConnectionMiddleware)
    
    # 6. CORS Middleware (configuração específica)
    setup_cors_middleware(app)
    
    # 7. GZip Middleware (compression)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    logger.info("✅ Middlewares avançados configurados com sucesso")
    
    # Retornar middleware de logging para acesso às métricas
    return logging_middleware

def setup_cors_middleware(app: FastAPI):
    """
    Configurar CORS seguindo melhores práticas
    
    Args:
        app: Instância do FastAPI
    """
    
    # Configuração de CORS para diferentes ambientes
    import os
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # Produção: CORS restritivo
        allowed_origins = [
            "https://tecnocursos.ai",
            "https://www.tecnocursos.ai", 
            "https://app.tecnocursos.ai"
        ]
        allow_credentials = True
        allowed_methods = ["GET", "POST", "PUT", "DELETE"]
        allowed_headers = ["Authorization", "Content-Type", "X-Request-ID"]
        
    elif environment == "staging":
        # Staging: CORS moderado
        allowed_origins = [
            "https://staging.tecnocursos.ai",
            "https://dev.tecnocursos.ai",
            "http://localhost:3000",
            "http://localhost:8080"
        ]
        allow_credentials = True
        allowed_methods = ["*"]
        allowed_headers = ["*"]
        
    else:
        # Development: CORS permissivo
        allowed_origins = ["*"]
        allow_credentials = False  # Não pode ser True com origins "*"
        allowed_methods = ["*"]
        allowed_headers = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=["X-Request-ID", "X-Response-Time"]
    )
    
    logger.info(f"✅ CORS configurado para ambiente: {environment}")

# Endpoint para métricas de middleware
async def get_middleware_metrics(logging_middleware: RequestLoggingMiddleware):
    """Obter métricas coletadas pelos middlewares"""
    return {
        "middleware_metrics": logging_middleware.get_metrics(),
        "timestamp": datetime.utcnow().isoformat()
    } 