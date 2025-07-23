"""
Aplicação principal FastAPI - TecnoCursos AI
Sistema SaaS para upload de arquivos e geração de vídeos
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import uvicorn
import logging
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Importações locais - usando imports absolutos
from app.config import get_settings
from app.database import get_db, create_database, check_database_health_async, engine, Base
from app.models import User, Project, FileUpload, Video
from app.auth import get_current_user_optional, auth_manager
from app.schemas import HealthCheck, SystemStats
from quick_server import get_dashboard_context

def create_directories():
    """Cria diretórios necessários para a aplicação"""
    directories = [
        "uploads",
        "uploads/pdf",
        "uploads/pptx",
        "static/videos",
        "static/audios",
        "static/thumbnails",
        "cache",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Importar routers principais
try:
    from app.routers import auth_router, users_router, projects_router, files_router, admin_router, stats_router
    _core_routers_available = True
except ImportError as e:
    print(f"⚠️ Erro ao importar routers principais: {e}")
    _core_routers_available = False

# Tentar importar router do editor de vídeo
try:
    from app.routers.video_editor_advanced import router as video_editor_router
    _video_editor_available = True
except ImportError:
    video_editor_router = None
    _video_editor_available = False
    print("⚠️ Video Editor Router não disponível")

# Tentar importar router do avatar
try:
    from app.routers import avatar_router
    _avatar_available = True
    if avatar_router is None:
        _avatar_available = False
        print("⚠️ Avatar router é None")
except ImportError as e:
    avatar_router = None
    _avatar_available = False
    print(f"⚠️ Avatar router não disponível: {e}")

# Tentar importar routers TTS
try:
    from app.routers import tts
    from app.routers import tts_advanced
    _tts_available = True
except ImportError:
    tts = None
    tts_advanced = None
    _tts_available = False
    print("⚠️ Routers TTS não disponíveis")

# Tentar importar router de admin de áudios
try:
    from app.routers import audio_admin
    _audio_admin_available = True
except ImportError:
    audio_admin = None
    _audio_admin_available = False
    print("⚠️ Router de admin de áudios não disponível")

# Tentar importar router de notificações
try:
    from app.routers.notifications import router as notifications_router
    _notifications_available = True
    print("✅ Router de notificações disponível")
except ImportError:
    notifications_router = None
    _notifications_available = False
    print("⚠️ Router de notificações não disponível")

# Tentar importar routers avançados
try:
    from app.routers import batch_upload, websocket_router, analytics
    _advanced_routers_available = True
except ImportError:
    batch_upload = None
    websocket_router = None
    analytics = None
    _advanced_routers_available = False
    print("⚠️ Routers avançados não disponíveis")

# Tentar importar router de cenas e assets
try:
    from app.routers import scenes_router
    _scenes_available = True
except ImportError:
    scenes_router = None
    _scenes_available = False
    print("⚠️ Router de cenas não disponível")

# Tentar importar routers enterprise
try:
    from app.routers import enterprise_router, system_control
    _enterprise_available = True
except ImportError:
    enterprise_router = None
    system_control = None
    _enterprise_available = False
    print("⚠️ Routers enterprise não disponíveis")

# Tentar importar routers de vídeo
try:
    from app.routers import video_generation, advanced_video_processing, video_export
    _video_routers_available = True
except ImportError:
    video_generation = None
    advanced_video_processing = None
    video_export = None
    _video_routers_available = False
    print("⚠️ Routers de vídeo não disponíveis")

# Importar novos routers
try:
    from app.routers.analytics import router as analytics_router
    from app.routers.export import router as export_router
    _new_routers_available = True
    print("✅ Novos routers (analytics, export) disponíveis")
except ImportError:
    analytics_router = None
    export_router = None
    _new_routers_available = False
    print("⚠️ Novos routers não disponíveis")

# 🆕 NOVOS SERVIÇOS 2025 - Tecnologias de Vanguarda
# Tentar importar routers dos novos serviços de última geração
try:
    from app.routers.modern_ai_router import router as modern_ai_router
    _modern_ai_available = True
    print("✅ Modern AI Router disponível")
except ImportError:
    modern_ai_router = None
    _modern_ai_available = False
    print("⚠️ Modern AI Router não disponível")

try:
    from app.routers.quantum_router import router as quantum_router
    _quantum_available = True
    print("✅ Quantum Optimization Router disponível")
except ImportError:
    quantum_router = None
    _quantum_available = False
    print("⚠️ Quantum Router não disponível")

try:
    from app.services.edge_computing_service import get_edge_computing_service, initialize_edge_computing
    _edge_computing_available = True
    print("✅ Edge Computing Service disponível")
except ImportError:
    get_edge_computing_service = None
    initialize_edge_computing = None
    _edge_computing_available = False
    print("⚠️ Edge Computing Service não disponível")

# Configuração de logging
try:
    from app.logger import get_logger
    logger = get_logger("main")
except ImportError:
    # Fallback para logging básico
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("main")

# Configurações
settings = get_settings()

# Criar diretórios necessários
create_directories()

# Configurar templates (melhor prática: sempre procurar na raiz e em app/templates)
templates_path = Path(__file__).parent / "templates"
if templates_path.exists():
    templates = Jinja2Templates(directory=str(templates_path))
else:
    fallback_templates = Path.cwd() / "templates"
    if fallback_templates.exists():
        templates = Jinja2Templates(directory=str(fallback_templates))
    else:
        templates = Jinja2Templates(directory="templates")

# Criar aplicação FastAPI
app = FastAPI(
    title="TecnoCursos AI - Enterprise Edition 2025",
    description="""
    🚀 **Plataforma SaaS Enterprise para Criação de Conteúdo Educacional com IA**
    
    ## 🎯 Funcionalidades Core
    - Upload e processamento inteligente de arquivos (PDF, PPTX, DOCX)
    - Geração automática de narração com TTS avançado (Bark + gTTS)
    - Criação de vídeos com avatar e templates profissionais
    - Sistema de autenticação JWT robusto
    - API REST completa com documentação automática
    
    ## 🧠 Inteligência Artificial Avançada (2025)
    - **Modern AI Service**: Multimodal AI, RAG, Chain-of-Thought Reasoning
    - **Quantum Optimization**: Algoritmos quânticos para otimização
    - **Edge Computing**: Processamento distribuído em tempo real
    - **AI Guardrails**: Supervisão ética e compliance automática
    
    ## 🏢 Funcionalidades Enterprise
    - Monitoramento inteligente com machine learning
    - Segurança avançada multicamada
    - Analytics em tempo real com dashboards
    - Sistema de backup automatizado
    - WebSocket para notificações em tempo real
    - Pipeline CI/CD completo
    
    ## 📊 APIs Disponíveis
    - **60+ endpoints** documentados e testados
    - **WebSocket** para comunicação em tempo real
    - **Batch processing** para operações em lote
    - **Advanced video processing** com templates profissionais
    - **Modern AI** com capacidades multimodais
    - **Quantum optimization** para problemas complexos
    
    ## 🔗 Links Úteis
    - **Documentação Interativa**: `/docs` (Swagger UI)
    - **Documentação Alternativa**: `/redoc` (ReDoc)
    - **Health Check**: `/api/health`
    - **Dashboard**: `/dashboard`
    - **Login**: `/login`
    
    ---
    **TecnoCursos AI Enterprise Edition 2025** - Revolucionando a educação com IA de vanguarda!
    """,
    version="2.0.0",
    contact={
        "name": "TecnoCursos AI Support Team",
        "email": "support@tecnocursos.ai",
        "url": "https://tecnocursos.ai"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Configurar arquivos estáticos
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
else:
    # Fallback para o diretório static na raiz
    fallback_static = Path.cwd() / "static"
    if fallback_static.exists():
        app.mount("/static", StaticFiles(directory=str(fallback_static)), name="static")
    else:
        print("⚠️ Diretório static não encontrado")

# Configurar tempo de início
app.state.start_time = time.time()

# ============================================================================
# INCLUSÃO DE ROUTERS
# ============================================================================

# Routers principais (obrigatórios)
if _core_routers_available:
    try:
        app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
        app.include_router(users_router, prefix="/api/users", tags=["Usuários"])
        app.include_router(projects_router, prefix="/api/projects", tags=["Projetos"])
        app.include_router(files_router, prefix="/api/files", tags=["Arquivos"])
        app.include_router(admin_router, prefix="/admin", tags=["Administração"])
        app.include_router(stats_router, prefix="/api/stats", tags=["Estatísticas"])
        logger.info("✅ Routers principais incluídos com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir routers principais: {e}")

# Router do editor de vídeo
if _video_editor_available and video_editor_router:
    try:
        app.include_router(video_editor_router, prefix="/api/editor", tags=["Editor de Vídeo"])
        logger.info("✅ Video Editor Router incluído")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir Video Editor router: {e}")

# Router de avatar
if _avatar_available and avatar_router:
    try:
        app.include_router(avatar_router, prefix="/api/avatar", tags=["Avatar"])
        logger.info("✅ Avatar Router incluído")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir Avatar router: {e}")

# Routers TTS
if _tts_available:
    try:
        if tts:
            app.include_router(tts.router, prefix="/api/tts", tags=["TTS"])
        if tts_advanced:
            app.include_router(tts_advanced.router, prefix="/api/tts/advanced", tags=["TTS Avançado"])
        logger.info("✅ Routers TTS incluídos")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir routers TTS: {e}")

# Router de admin de áudios
if _audio_admin_available and audio_admin:
    try:
        app.include_router(audio_admin.router, prefix="/api/audio", tags=["Admin de Áudios"])
        logger.info("✅ Audio Admin Router incluído")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir Audio Admin router: {e}")

# Router de notificações
if _notifications_available and notifications_router:
    try:
        app.include_router(notifications_router, prefix="/api", tags=["Notificações"])
        logger.info("✅ Router de notificações incluído")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir router de notificações: {e}")

# Routers avançados
if _advanced_routers_available:
    try:
        if batch_upload:
            app.include_router(batch_upload, prefix="/api/batch", tags=["Upload em Lote"])
        if websocket_router:
            app.include_router(websocket_router, prefix="/api/websocket", tags=["WebSocket"])
        if analytics:
            app.include_router(analytics, prefix="/api/analytics", tags=["Analytics"])
        logger.info("✅ Routers avançados incluídos")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir routers avançados: {e}")

# Router de cenas
if _scenes_available and scenes_router:
    try:
        app.include_router(scenes_router, prefix="/api/scenes", tags=["Cenas"])
        logger.info("✅ Scenes Router incluído")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir Scenes router: {e}")

# Routers enterprise
if _enterprise_available:
    try:
        if enterprise_router:
            app.include_router(enterprise_router, prefix="/enterprise", tags=["Enterprise"])
        if system_control:
            app.include_router(system_control, prefix="/api/system", tags=["Controle do Sistema"])
        logger.info("✅ Routers enterprise incluídos")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir routers enterprise: {e}")

# Routers de vídeo
if _video_routers_available:
    try:
        if video_generation:
            app.include_router(video_generation, prefix="/api/video/generation", tags=["Geração de Vídeo"])
        if advanced_video_processing:
            app.include_router(advanced_video_processing, prefix="/api/video/processing", tags=["Processamento Avançado"])
        if video_export:
            app.include_router(video_export, prefix="/api/video/export", tags=["Exportação de Vídeo"])
        logger.info("✅ Routers de vídeo incluídos")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir routers de vídeo: {e}")

# Novos routers (analytics e export)
if _new_routers_available:
    try:
        if analytics_router:
            app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
        if export_router:
            app.include_router(export_router, prefix="/api/export", tags=["Export"])
        logger.info("✅ Novos routers (analytics, export) incluídos")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir novos routers: {e}")

# 🆕 NOVOS SERVIÇOS 2025
# Modern AI Router
if _modern_ai_available and modern_ai_router:
    try:
        app.include_router(modern_ai_router, prefix="/api/modern-ai", tags=["Modern AI"])
        logger.info("🤖 Modern AI Router incluído - Multimodal AI")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir Modern AI router: {e}")

# Quantum Optimization Router
if _quantum_available and quantum_router:
    try:
        app.include_router(quantum_router, prefix="/api/quantum", tags=["Quantum Optimization"])
        logger.info("🔬 Quantum Optimization Router incluído - Quantum Algorithms")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir Quantum router: {e}")

# ============================================================================
# EVENTOS DE INICIALIZAÇÃO
# ============================================================================

async def initialize_services():
    """Inicializa todos os serviços principais da aplicação."""
    if _modern_ai_available:
        try:
            from app.services.modern_ai_service import initialize_modern_ai
            await initialize_modern_ai()
            logger.info("🤖 Modern AI Service inicializado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar Modern AI: {e}")

    if _edge_computing_available:
        try:
            await initialize_edge_computing()
            logger.info("🌐 Edge Computing Service inicializado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar Edge Computing: {e}")

    if _quantum_available:
        try:
            from app.services.quantum_optimization_service import get_quantum_optimization_service
            quantum_service = get_quantum_optimization_service()
            logger.info("🔬 Quantum Optimization Service inicializado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar Quantum Service: {e}")

    # Inicializar outros serviços enterprise se disponíveis
    try:
        from app.services.intelligent_monitoring_service import monitoring_service
        logger.info("🧠 Intelligent Monitoring ativo")
    except ImportError:
        pass

    try:
        from app.services.performance_optimization_service import performance_service
        logger.info("⚡ Performance Optimization ativo")
    except ImportError:
        pass

@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da aplicação"""
    try:
        # Criar diretórios necessários
        create_directories()
        
        # Inicializar banco de dados (versão síncrona)
        from app.database import create_database_sync
        create_database_sync()
        
        # Verificar saúde do banco
        await check_database_health_async()
        
        # Inicializar serviços
        await initialize_services()
        
        logger.info("✅ Sistema inicializado com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro crítico na inicialização: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos executados no encerramento da aplicação"""
    logger.info("🔄 Encerrando TecnoCursos AI Enterprise Edition 2025...")
    
    # Fechar conexões de banco
    try:
        engine.dispose()
        logger.info("✅ Conexões de banco fechadas")
    except:
        pass
    
    logger.info("👋 TecnoCursos AI encerrado com sucesso")

# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial: redireciona para login se não autenticado, senão dashboard"""
    token = request.cookies.get("access_token") or request.headers.get("Authorization")
    if not token:
        return RedirectResponse(url="/login")
    # Aqui pode-se adicionar lógica para validar o token se necessário
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal da aplicação"""
    context = get_dashboard_context(request)
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login.html", response_class=HTMLResponse)
async def login_page_html(request: Request):
    """Página de login (com extensão .html)"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    """Favicon da aplicação"""
    return FileResponse("static/favicon.ico")

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard_html(request: Request):
    """Dashboard (com extensão .html)"""
    context = get_dashboard_context(request)
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/files.html", response_class=HTMLResponse)
async def files_html(request: Request):
    """Página de arquivos (com extensão .html)"""
    return templates.TemplateResponse("files.html", {"request": request})

@app.get("/admin.html", response_class=HTMLResponse)
async def admin_html(request: Request):
    """Página de administração (com extensão .html)"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/audios.html", response_class=HTMLResponse)
async def audios_html(request: Request):
    """Página de áudios (com extensão .html)"""
    return templates.TemplateResponse("audios.html", {"request": request})

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Retorna página 404 customizada"""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

# ============================================================================
# API HEALTH CHECK E STATUS
# ============================================================================

@app.get("/api/health", response_model=HealthCheck)
async def health_check():
    """
    Verificação de saúde da aplicação
    
    Retorna status detalhado de todos os componentes críticos:
    - Database connectivity
    - Services availability  
    - System resources
    - AI capabilities
    """
    try:
        # Verificar banco de dados
        db_healthy = await check_database_health_async()
        
        # Verificar serviços disponíveis
        services_status = {
            "database": "connected" if db_healthy else "disconnected",
            "avatar_service": "available" if _avatar_available else "unavailable",
            "tts_service": "available" if _tts_available else "unavailable",
            "audio_admin": "available" if _audio_admin_available else "unavailable",
            "advanced_features": "available" if _advanced_routers_available else "unavailable",
            "enterprise_features": "available" if _enterprise_available else "unavailable",
            "video_processing": "available" if _video_routers_available else "unavailable",
            "modern_ai": "available" if _modern_ai_available else "unavailable",
            "quantum_optimization": "available" if _quantum_available else "unavailable",
            "edge_computing": "available" if _edge_computing_available else "unavailable"
        }
        
        # Calcular score de saúde geral
        healthy_services = sum(1 for status in services_status.values() if "available" in status or "connected" in status)
        total_services = len(services_status)
        health_score = (healthy_services / total_services) * 100
        
        # Determinar status geral
        if health_score >= 90:
            overall_status = "excellent"
        elif health_score >= 70:
            overall_status = "good"
        elif health_score >= 50:
            overall_status = "fair"
        else:
            overall_status = "poor"
        
        return HealthCheck(
            status=overall_status,
            timestamp=datetime.now(),
            version="2.0.0",
            uptime_seconds=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
            database_status="connected" if db_healthy else "disconnected",
            services_status=services_status
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthCheck(
            status="error",
            timestamp=datetime.now(),
            version="2.0.0",
            uptime_seconds=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
            database_status="error",
            services_status={}
        )

@app.get("/api/status", response_model=SystemStats)
async def system_status(db: Session = Depends(get_db)):
    """
    Estatísticas detalhadas do sistema
    
    Inclui métricas de uso, performance e recursos.
    """
    try:
        # Consultar estatísticas do banco
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_projects = db.query(func.count(Project.id)).scalar() or 0
        total_files = db.query(func.count(FileUpload.id)).scalar() or 0
        total_videos = db.query(func.count(Video.id)).scalar() or 0
        
        # Métricas de sistema (se psutil disponível)
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_metrics = {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "available_memory_gb": memory.available / (1024**3),
                "free_disk_gb": disk.free / (1024**3)
            }
        except ImportError:
            system_metrics = {
                "cpu_usage_percent": 0,
                "memory_usage_percent": 0,
                "disk_usage_percent": 0,
                "available_memory_gb": 0,
                "free_disk_gb": 0
            }
        
        return SystemStats(
            total_users=total_users,
            total_projects=total_projects,
            total_files=total_files,
            total_videos=total_videos,
            system_metrics=system_metrics,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/info")
async def system_info():
    """
    Informações gerais do sistema
    
    Retorna informações sobre versão, ambiente e funcionalidades disponíveis.
    """
    return {
        "name": "TecnoCursos AI Enterprise Edition 2025",
        "version": "2.0.0",
        "environment": settings.environment,
        "description": "Plataforma SaaS para criação de conteúdo educacional com IA",
        "features": {
            "authentication": True,
            "file_upload": True,
            "video_generation": _video_routers_available,
            "tts": _tts_available,
            "avatar": _avatar_available,
            "enterprise": _enterprise_available,
            "modern_ai": _modern_ai_available,
            "quantum": _quantum_available,
            "edge_computing": _edge_computing_available
        },
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Iniciar servidor
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    ) 