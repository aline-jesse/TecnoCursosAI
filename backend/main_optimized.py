#!/usr/bin/env python3
"""
TecnoCursos AI - Sistema de Geração de Vídeos
Aplicação FastAPI principal com todas as otimizações implementadas

Nova estrutura com:
- Sistema de configuração centralizado
- Autenticação JWT robusta  
- Rate limiting avançado
- Cache distribuído
- Logging estruturado
- Monitoramento em tempo real
- Consultas otimizadas
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Imports das nossas melhorias
from app.core.settings import get_settings, get_fastapi_config, load_config
from app.core.logging import configure_logging, get_logger
from app.core.cache import init_cache
from app.security.rate_limiter import create_rate_limit_middleware
from app.security.auth_manager import SecureAuthManager
from app.middleware.monitoring import (
    get_monitoring_middleware, 
    system_metrics_collector,
    get_metrics_summary,
    get_health_status,
    get_active_alerts
)
from app.core.query_optimizer import get_optimized_queries

# Import dos routers existentes
from app.routers.dashboard import router as dashboard_router
from app.routers.notifications import router as notifications_router
from app.routers import preview

# Import de serviços
from app.services.notification_service import cleanup_notifications_task
from app.database import create_tables

# Configurações globais
settings = get_settings()
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação"""
    
    # ========== INICIALIZAÇÃO ==========
    logger.info("🚀 Iniciando TecnoCursos AI...")
    
    # 1. Carregar configurações
    load_config()
    logger.info(f"✅ Configurações carregadas - Ambiente: {settings.environment}")
    
    # 2. Configurar logging
    configure_logging(
        log_level=settings.monitoring.log_level.value,
        log_file="tecnocursos.log" if settings.monitoring.log_file else None,
        enable_json=settings.environment.value == "production"
    )
    logger.info("✅ Sistema de logging configurado")
    
    # 3. Inicializar cache
    init_cache(settings.redis.url if hasattr(settings.redis, 'url') else None)
    logger.info("✅ Sistema de cache inicializado")
    
    # 4. Criar tabelas do banco
    try:
        create_tables()
        logger.info("✅ Banco de dados inicializado")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {e}")
    
    # 5. Inicializar gerenciador de autenticação
    auth_manager = SecureAuthManager(
        secret_key=settings.security.jwt_secret_key,
        algorithm=settings.security.jwt_algorithm,
        access_token_expire_minutes=settings.security.jwt_access_token_expire_minutes
    )
    app.state.auth_manager = auth_manager
    logger.info("✅ Autenticação segura configurada")
    
    # 6. Iniciar tasks em background
    background_tasks = [
        asyncio.create_task(system_metrics_collector()),
        asyncio.create_task(cleanup_notifications_task())
    ]
    logger.info("✅ Tasks em background iniciadas")
    
    logger.info("🎉 TecnoCursos AI inicializado com sucesso!")
    
    yield  # Aplicação em execução
    
    # ========== FINALIZAÇÃO ==========
    logger.info("🛑 Finalizando TecnoCursos AI...")
    
    # Cancelar tasks em background
    for task in background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    logger.info("✅ TecnoCursos AI finalizado")

# Criar aplicação FastAPI com configurações centralizadas
app = FastAPI(
    lifespan=lifespan,
    **get_fastapi_config()
)

# ========== MIDDLEWARES ==========

# 1. Middleware de compressão
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. Middleware de hosts confiáveis (em produção)
if settings.environment.value == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["tecnocursos.ai", "www.tecnocursos.ai"]
    )

# 3. Middleware de CORS com configuração segura
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.allowed_origins,
    allow_credentials=settings.security.allow_credentials,
    allow_methods=settings.security.allowed_methods,
    allow_headers=settings.security.allowed_headers,
)

# 4. Rate limiting
rate_limiter = create_rate_limit_middleware(app, settings.redis.url if hasattr(settings.redis, 'url') else None)
app.add_middleware(type(rate_limiter), **rate_limiter.__dict__)

# 5. Monitoring (deve ser último)
monitoring_middleware = get_monitoring_middleware(app)
app.add_middleware(type(monitoring_middleware), **monitoring_middleware.__dict__)

# ========== ARQUIVOS ESTÁTICOS E TEMPLATES ==========

# Templates Jinja2
templates = Jinja2Templates(directory="app/templates")

# Arquivos estáticos
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    logger.info("✅ Arquivos estáticos configurados")
except Exception as e:
    logger.warning(f"⚠️ Erro ao configurar arquivos estáticos: {e}")

# ========== ROUTERS ==========

# Incluir routers existentes
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(preview.router, prefix="/preview", tags=["Preview"])

# ========== ENDPOINTS DE SISTEMA ==========

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Dashboard principal"""
    try:
        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request,
                "app_name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment.value
            }
        )
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard: {e}")
        return HTMLResponse("Dashboard temporariamente indisponível", status_code=503)

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    health_status = await get_health_status()
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)

@app.get("/metrics")
async def metrics_endpoint():
    """Endpoint de métricas (apenas em desenvolvimento/staging)"""
    if settings.environment.value == "production":
        return JSONResponse(
            {"error": "Metrics endpoint disabled in production"}, 
            status_code=404
        )
    
    metrics = await get_metrics_summary()
    return JSONResponse(content=metrics)

@app.get("/alerts")
async def alerts_endpoint():
    """Endpoint de alertas ativos"""
    if settings.environment.value == "production":
        return JSONResponse(
            {"error": "Alerts endpoint disabled in production"}, 
            status_code=404
        )
    
    alerts = get_active_alerts()
    return JSONResponse(content={"alerts": alerts})

@app.get("/config")
async def config_endpoint():
    """Endpoint de configuração (sem dados sensíveis)"""
    if settings.environment.value == "production":
        return JSONResponse(
            {"error": "Config endpoint disabled in production"}, 
            status_code=404
        )
    
    config = settings.to_dict()
    return JSONResponse(content=config)

# ========== TRATAMENTO DE ERROS ==========

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler para 404"""
    logger.warning(f"404 - Path not found: {request.url.path}")
    return JSONResponse(
        content={"error": "Endpoint não encontrado", "path": request.url.path},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler para 500"""
    logger.error(f"500 - Internal error: {exc}", exc_info=True)
    return JSONResponse(
        content={"error": "Erro interno do servidor"},
        status_code=500
    )

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    """Handler para rate limiting"""
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return JSONResponse(
        content={"error": "Muitas requisições. Tente novamente em alguns instantes."},
        status_code=429
    )

# ========== STARTUP MESSAGE ==========

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"""
    🚀 Iniciando TecnoCursos AI
    📍 Ambiente: {settings.environment.value}
    🌐 Host: {settings.host}:{settings.port}
    🐛 Debug: {settings.debug}
    📊 Monitoramento: {'Ativo' if settings.monitoring.enable_metrics else 'Inativo'}
    🔒 Rate Limiting: Ativo
    💾 Cache: {'Redis' if hasattr(settings.redis, 'url') else 'Memória'}
    """)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.monitoring.log_level.value.lower(),
        access_log=True
    )
