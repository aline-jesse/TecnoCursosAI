"""
TecnoCursos AI - Sistema Backend Reorganizado
Sistema SaaS para criação de vídeos educacionais com IA

Versão: 2.0.0 (Reorganizado)
Data: Janeiro 2025
"""

from __future__ import annotations

import logging
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Importações locais
from .core.config import get_settings
from .core.database import get_db, init_database
from .core.logging_config import setup_logging
from .models.base import Base
from .schemas.base import HealthCheck, SystemStatus

# Configuração de logging
setup_logging()
logger = logging.getLogger(__name__)

# Configurações
settings = get_settings()

def create_app() -> FastAPI:
    """Factory para criar a aplicação FastAPI"""
    
    # Criar aplicação
    app = FastAPI(
        title="TecnoCursos AI",
        description="Sistema SaaS para criação de vídeos educacionais com IA",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configurar diretórios estáticos
    static_path = Path("static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Configurar templates
    templates_path = Path("templates")
    if templates_path.exists():
        app.state.templates = Jinja2Templates(directory="templates")
    
    # Configurar tempo de início
    app.state.start_time = time.time()
    
    # Incluir routers
    include_routers(app)
    
    # Configurar eventos
    setup_events(app)
    
    return app

def include_routers(app: FastAPI) -> None:
    """Incluir todos os routers disponíveis"""
    
    try:
        # Importar routers diretamente
        from .routers.auth import router as auth_router
        from .routers.users import router as users_router
        from .routers.projects import router as projects_router
        from .routers.files import router as files_router
        from .routers.admin import router as admin_router
        from .routers.stats import router as stats_router
        
        app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
        app.include_router(users_router, prefix="/api/users", tags=["Usuários"])
        app.include_router(projects_router, prefix="/api/projects", tags=["Projetos"])
        app.include_router(files_router, prefix="/api/files", tags=["Arquivos"])
        app.include_router(admin_router, prefix="/admin", tags=["Administração"])
        app.include_router(stats_router, prefix="/api/stats", tags=["Estatísticas"])
        
        logger.info("✅ Routers principais incluídos")
        
    except ImportError as e:
        logger.warning(f"⚠️ Alguns routers principais não disponíveis: {e}")
    
    # Routers opcionais - tentar importar se existirem
    optional_routers = [
        ("video_processing", "/api/video", ["Processamento de Vídeo"]),
        ("tts", "/api/tts", ["Text-to-Speech"]),
        ("avatar", "/api/avatar", ["Avatar"]),
        ("analytics", "/api/analytics", ["Analytics"]),
    ]
    
    for router_name, prefix, tags in optional_routers:
        try:
            router_module = __import__(f"app.routers.{router_name}", fromlist=["router"])
            app.include_router(router_module.router, prefix=prefix, tags=tags)
            logger.info(f"✅ Router {router_name} incluído")
        except ImportError:
            logger.info(f"ℹ️ Router {router_name} não disponível")

def setup_events(app: FastAPI) -> None:
    """Configurar eventos de startup e shutdown"""
    
    @app.on_event("startup")
    async def startup_event():
        """Inicialização da aplicação"""
        try:
            # Criar diretórios necessários
            create_directories()
            
            # Inicializar banco de dados
            await init_database()
            
            logger.info("🚀 TecnoCursos AI iniciado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Encerramento da aplicação"""
        logger.info("👋 Encerrando TecnoCursos AI...")

def create_directories() -> None:
    """Criar diretórios necessários"""
    directories = [
        "static/uploads",
        "static/videos", 
        "static/audios",
        "static/thumbnails",
        "data/cache",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"📁 Diretório criado: {directory}")

# Criar aplicação
app = create_app()

# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página inicial"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TecnoCursos AI</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 800px; margin: 0 auto; }
            .title { color: #2563eb; font-size: 2.5em; margin-bottom: 20px; }
            .subtitle { color: #64748b; font-size: 1.2em; margin-bottom: 30px; }
            .links { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
            .link { 
                background: #2563eb; color: white; padding: 12px 24px; 
                text-decoration: none; border-radius: 8px; 
                transition: background 0.3s;
            }
            .link:hover { background: #1d4ed8; }
            .status { 
                background: #10b981; color: white; padding: 8px 16px; 
                border-radius: 20px; font-size: 0.9em; margin-top: 20px;
                display: inline-block;
            }
            .features {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin: 40px 0; text-align: left;
            }
            .feature {
                background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb;
            }
            .feature h3 { margin-top: 0; color: #2563eb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="title">🚀 TecnoCursos AI</h1>
            <p class="subtitle">Sistema SaaS para criação de vídeos educacionais com IA</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🎬 Geração de Vídeos</h3>
                    <p>Crie vídeos educacionais automaticamente a partir de documentos PDF e PPTX</p>
                </div>
                <div class="feature">
                    <h3>🤖 IA Integrada</h3>
                    <p>Text-to-Speech avançado e avatares virtuais para narração</p>
                </div>
                <div class="feature">
                    <h3>📊 Analytics</h3>
                    <p>Métricas e estatísticas detalhadas de uso e performance</p>
                </div>
                <div class="feature">
                    <h3>☁️ SaaS Ready</h3>
                    <p>Arquitetura escalável e pronta para produção em nuvem</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs" class="link">📖 Documentação da API</a>
                <a href="/api/health" class="link">❤️ Health Check</a>
                <a href="/api/stats/dashboard" class="link">📊 Dashboard</a>
                <a href="/admin/stats" class="link">👨‍💼 Admin</a>
            </div>
            
            <div class="status">✅ Sistema Online v2.0.0</div>
        </div>
    </body>
    </html>
    """)

@app.get("/api/health", response_model=HealthCheck)
async def health_check():
    """Verificação de saúde da aplicação"""
    try:
        # Verificar banco de dados
        from .core.database import check_database_health
        db_healthy = await check_database_health()
        
        # Calcular uptime
        uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
        
        return HealthCheck(
            status="healthy" if db_healthy else "unhealthy",
            timestamp=datetime.now(),
            version="2.0.0",
            uptime_seconds=uptime,
            database_status="connected" if db_healthy else "disconnected"
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthCheck(
            status="error",
            timestamp=datetime.now(),
            version="2.0.0",
            uptime_seconds=0,
            database_status="error"
        )

@app.get("/api/status", response_model=SystemStatus)
async def system_status(db: Session = Depends(get_db)):
    """Status detalhado do sistema"""
    try:
        # Estatísticas básicas do banco
        total_users = 0
        total_projects = 0
        total_files = 0
        
        try:
            from .models.base import User, Project, FileUpload
            
            total_users = db.query(User).count()
            total_projects = db.query(Project).count()
            total_files = db.query(FileUpload).count()
        except Exception:
            pass  # Modelos podem não estar disponíveis ainda
        
        return SystemStatus(
            total_users=total_users,
            total_projects=total_projects,
            total_files=total_files,
            system_load=0.0,  # Placeholder
            memory_usage=0.0,  # Placeholder
            disk_usage=0.0,    # Placeholder
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ============================================================================
# INICIALIZAÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando TecnoCursos AI...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 