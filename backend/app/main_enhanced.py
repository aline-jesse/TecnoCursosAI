"""
TecnoCursos AI - Sistema Principal Aprimorado
===========================================

Versão Enterprise com todas as funcionalidades avançadas:
- Rate limiting inteligente com múltiplas estratégias
- Health checks abrangentes de todos os componentes
- Validação robusta com sanitização automática
- Monitoramento avançado de API com métricas em tempo real
- Sistema de backup aprimorado com criptografia
- Integração completa de todos os serviços
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import time

# Importações dos módulos existentes
from app.config import settings
from app.database import init_db
from app.logger import get_logger
from app.middleware import setup_middleware
from app.auth import get_current_user

# Importações dos novos serviços
from app.middleware.rate_limiting import AdvancedRateLimitMiddleware, setup_rate_limiting
from app.services.health_check_service import health_service
from app.services.api_monitoring_service import monitoring_service, track_api_call
from app.services.enhanced_backup_service import enhanced_backup_service, BackupConfig, BackupType, CompressionType
from app.validators.advanced_validators import validator_service, ValidationResult

# Importações dos routers existentes
from app.routers import (
    auth, users, projects, files, tts, tts_advanced,
    video_generation, avatar, batch_upload, analytics,
    stats, audio_admin, advanced_video_processing,
    websocket_router, enterprise_router
)

logger = get_logger("main_enhanced")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação"""
    startup_time = time.time()
    
    logger.info("🚀 TecnoCursos AI Enterprise Edition - Inicializando...")
    
    try:
        # 1. Inicializar banco de dados
        logger.info("📊 Inicializando banco de dados...")
        await init_db()
        
        # 2. Configurar sistema de backup
        logger.info("💾 Configurando sistema de backup...")
        await setup_backup_system()
        
        # 3. Inicializar monitoramento de API
        logger.info("📈 Inicializando monitoramento de API...")
        await monitoring_service.start_monitoring(check_interval=30)
        
        # 4. Configurar health checks
        logger.info("🏥 Configurando health checks...")
        await setup_health_monitoring()
        
        # 5. Executar health check inicial
        logger.info("🔍 Executando health check inicial...")
        initial_health = await health_service.run_all_checks()
        healthy_components = sum(1 for result in initial_health.values() 
                               if hasattr(result, 'status') and result.status.value == 'healthy')
        logger.info(f"✅ Health check inicial: {healthy_components}/{len(initial_health)} componentes saudáveis")
        
        # 6. Configurar validação global
        logger.info("🛡️ Configurando sistema de validação...")
        setup_global_validation()
        
        startup_duration = time.time() - startup_time
        logger.info(f"🎉 TecnoCursos AI Enterprise Edition iniciado em {startup_duration:.2f}s")
        logger.info("="*60)
        logger.info("🌟 SISTEMA ENTERPRISE TOTALMENTE OPERACIONAL 🌟")
        logger.info("="*60)
        
        yield  # Aplicação está rodando
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    
    finally:
        # Cleanup durante shutdown
        logger.info("🔄 Finalizando serviços...")
        
        try:
            # Parar monitoramento
            await monitoring_service.stop_monitoring()
            logger.info("📈 Monitoramento de API finalizado")
            
            # Executar backup final de emergência
            await emergency_backup()
            logger.info("💾 Backup de emergência concluído")
            
            logger.info("👋 TecnoCursos AI Enterprise Edition finalizado")
            
        except Exception as e:
            logger.error(f"❌ Erro no shutdown: {e}")

# Criar aplicação FastAPI com lifespan
app = FastAPI(
    title="TecnoCursos AI - Enterprise Edition",
    description="Sistema avançado de criação de cursos com IA, rate limiting, monitoramento e backup",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# === MIDDLEWARES AVANÇADOS ===

# 1. Middleware de compressão (primeiro)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. Rate limiting avançado
setup_rate_limiting(app, redis_url=getattr(settings, 'REDIS_URL', None), config_name="premium")

# 3. Middleware de monitoramento personalizado
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """Middleware para monitoramento avançado de API"""
    start_time = time.time()
    
    # Executar requisição
    try:
        response = await call_next(request)
        response_time_ms = (time.time() - start_time) * 1000
        
        # Registrar no sistema de monitoramento
        track_api_call(request, response, response_time_ms)
        
        # Adicionar headers de monitoramento
        response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"
        response.headers["X-Timestamp"] = str(int(time.time()))
        
        return response
        
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        
        # Registrar erro no monitoramento
        error_response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
        track_api_call(request, error_response, response_time_ms, str(e))
        
        logger.error(f"❌ Erro na requisição {request.url.path}: {e}")
        raise

# 4. Middleware de validação
@app.middleware("http")
async def validation_middleware(request: Request, call_next):
    """Middleware para validação automática"""
    
    # Validar cabeçalhos básicos de segurança
    user_agent = request.headers.get("user-agent", "")
    if not user_agent or len(user_agent) < 5:
        logger.warning(f"⚠️ User-Agent suspeito: {user_agent}")
    
    # Validar tamanho do request
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=413, detail="Request muito grande")
    
    return await call_next(request)

# 5. Middleware existente do sistema
setup_middleware(app)

# 6. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else ["https://seu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ROUTERS ===

# Incluir todos os routers existentes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(tts.router, prefix="/api/tts", tags=["tts"])
app.include_router(tts_advanced.router, prefix="/api/tts-advanced", tags=["tts-advanced"])
app.include_router(video_generation.router, prefix="/api/video", tags=["video"])
app.include_router(avatar.router, prefix="/api/avatar", tags=["avatar"])
app.include_router(batch_upload.router, prefix="/api/batch", tags=["batch"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(audio_admin.router, prefix="/api/audio-admin", tags=["audio-admin"])
app.include_router(advanced_video_processing.router, prefix="/api/video-advanced", tags=["video-advanced"])
app.include_router(websocket_router.router, prefix="/api/ws", tags=["websocket"])
app.include_router(enterprise_router.router, prefix="/api/enterprise", tags=["enterprise"])

# === NOVOS ENDPOINTS AVANÇADOS ===

@app.get("/health", tags=["system"])
async def health_check():
    """Health check básico"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/detailed", tags=["system"])
async def detailed_health_check():
    """Health check detalhado de todos os componentes"""
    health_results = await health_service.run_all_checks()
    summary = health_service.get_system_health_summary()
    
    return {
        "summary": summary,
        "components": {name: {
            "status": result.status.value,
            "response_time_ms": result.response_time_ms,
            "details": result.details,
            "error": result.error
        } for name, result in health_results.items()}
    }

@app.get("/metrics", tags=["system"])
async def get_metrics():
    """Obter métricas do sistema"""
    return monitoring_service.get_dashboard_data()

@app.get("/metrics/detailed", tags=["system"])
async def get_detailed_metrics():
    """Obter métricas detalhadas"""
    from datetime import timedelta
    return monitoring_service.get_detailed_report(timedelta(hours=1))

@app.get("/backup/status", tags=["system"])
async def backup_status():
    """Status do sistema de backup"""
    stats = enhanced_backup_service.get_backup_statistics()
    
    # Adicionar status dos backups ativos
    active_backups = {
        backup_id: {
            "status": record.status.value,
            "start_time": record.start_time.isoformat(),
            "config_name": record.config_name
        }
        for backup_id, record in enhanced_backup_service.active_backups.items()
    }
    
    return {
        "statistics": stats,
        "active_backups": active_backups,
        "configs_count": len(enhanced_backup_service.configs)
    }

@app.post("/backup/run/{config_name}", tags=["system"])
async def run_backup(config_name: str, current_user = Depends(get_current_user)):
    """Executar backup manual (requer autenticação)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem executar backups")
    
    try:
        record = await enhanced_backup_service.run_backup(config_name)
        return {
            "backup_id": record.id,
            "status": record.status.value,
            "message": f"Backup {record.status.value}"
        }
    except Exception as e:
        logger.error(f"❌ Erro ao executar backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/performance", tags=["system"])
async def system_performance():
    """Informações de performance do sistema"""
    import psutil
    
    # Coletar métricas do sistema
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Obter métricas da aplicação
    dashboard_data = monitoring_service.get_dashboard_data()
    
    return {
        "system_resources": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": memory.used / (1024**3),
            "memory_total_gb": memory.total / (1024**3),
            "disk_percent": (disk.used / disk.total) * 100,
            "disk_free_gb": disk.free / (1024**3)
        },
        "application_metrics": {
            "requests_per_minute": dashboard_data.get("requests_per_minute", 0),
            "active_alerts": dashboard_data.get("active_alerts", 0),
            "response_time_grade": dashboard_data.get("response_time_analysis", {}).get("performance_grade", "unknown")
        }
    }

@app.post("/validate/text", tags=["validation"])
async def validate_text_content(data: dict):
    """Validar conteúdo de texto"""
    text = data.get("text", "")
    max_length = data.get("max_length", 10000)
    
    from app.validators.advanced_validators import TextValidator
    result = TextValidator.validate_text_content(text, max_length)
    
    return {
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "sanitized_text": result.sanitized_data
    }

@app.post("/validate/file", tags=["validation"])
async def validate_file_info(data: dict):
    """Validar informações de arquivo"""
    from app.validators.advanced_validators import FileValidator
    
    filename = data.get("filename", "")
    file_type = data.get("type", "unknown")
    file_size = data.get("size", 0)
    
    # Validar nome
    name_result = FileValidator.validate_filename(filename)
    
    # Validar tamanho
    size_result = FileValidator.validate_file_size(file_size, file_type)
    
    return {
        "filename_validation": {
            "is_valid": name_result.is_valid,
            "errors": name_result.errors,
            "warnings": name_result.warnings,
            "sanitized_filename": name_result.sanitized_data
        },
        "size_validation": {
            "is_valid": size_result.is_valid,
            "errors": size_result.errors
        }
    }

# === ARQUIVOS ESTÁTICOS ===
app.mount("/static", StaticFiles(directory="static"), name="static")

# === FUNÇÕES DE SETUP ===

async def setup_backup_system():
    """Configurar sistema de backup"""
    # Configuração para backup do sistema
    system_config = BackupConfig(
        name="sistema_completo",
        source_paths=["app/", "templates/", "static/", "alembic/"],
        destination_path="backups/sistema",
        backup_type=BackupType.INCREMENTAL,
        compression=CompressionType.TAR_GZ,
        encryption=True,
        retention_days=30,
        verify_integrity=True
    )
    
    # Configuração para backup de uploads
    uploads_config = BackupConfig(
        name="uploads_dados",
        source_paths=["uploads/", "app/static/uploads/"],
        destination_path="backups/uploads",
        backup_type=BackupType.INCREMENTAL,
        compression=CompressionType.TAR_GZ,
        encryption=False,  # Uploads já podem ser criptografados
        retention_days=90,
        verify_integrity=True
    )
    
    enhanced_backup_service.add_backup_config(system_config)
    enhanced_backup_service.add_backup_config(uploads_config)
    
    logger.info("✅ Sistema de backup configurado")

async def setup_health_monitoring():
    """Configurar monitoramento de saúde"""
    # Executar health check inicial para estabelecer baseline
    await health_service.run_all_checks()
    logger.info("✅ Monitoramento de saúde configurado")

def setup_global_validation():
    """Configurar validação global"""
    # Configurações já estão no validator_service
    logger.info("✅ Sistema de validação configurado")

async def emergency_backup():
    """Executar backup de emergência durante shutdown"""
    try:
        logger.info("💾 Executando backup de emergência...")
        
        # Backup apenas dos dados críticos (configurações, logs recentes)
        emergency_config = BackupConfig(
            name="emergency_shutdown",
            source_paths=["logs/", "backups/"],
            destination_path="backups/emergency",
            backup_type=BackupType.FULL,
            compression=CompressionType.GZIP,
            encryption=False,
            retention_days=7,
            verify_integrity=False  # Rápido durante shutdown
        )
        
        enhanced_backup_service.add_backup_config(emergency_config)
        record = await enhanced_backup_service.run_backup("emergency_shutdown")
        
        if record.status.value == "completed":
            logger.info("✅ Backup de emergência concluído")
        else:
            logger.warning("⚠️ Backup de emergência com problemas")
            
    except Exception as e:
        logger.error(f"❌ Erro no backup de emergência: {e}")

# === HANDLERS DE ERRO ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler personalizado para exceções HTTP"""
    logger.warning(f"⚠️ HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc):
    """Handler para erros internos do servidor"""
    logger.error(f"❌ Internal Server Error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

# === ENDPOINTS DE TEMPLATE (existentes) ===

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página inicial"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/files", response_class=HTMLResponse)
async def files_page(request: Request):
    """Página de arquivos"""
    return templates.TemplateResponse("files.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Página de administração"""
    return templates.TemplateResponse("admin.html", {"request": request})

# === EXECUÇÃO PRINCIPAL ===

if __name__ == "__main__":
    print("🌟 TECNOCURSOS AI - ENTERPRISE EDITION 2025")
    print("=" * 60)
    print("🚀 Funcionalidades Enterprise:")
    print("   ✅ Rate Limiting Avançado com múltiplas estratégias")
    print("   ✅ Health Checks abrangentes de todos os componentes")
    print("   ✅ Validação robusta com sanitização automática")
    print("   ✅ Monitoramento de API com métricas em tempo real")
    print("   ✅ Sistema de backup aprimorado com criptografia")
    print("   ✅ Alertas automáticos e detecção de anomalias")
    print("   ✅ SLA monitoring e compliance")
    print("   ✅ Compressão inteligente e otimização")
    print("=" * 60)
    
    uvicorn.run(
        "app.main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        workers=1,  # Usar 1 worker para desenvolvimento, mais em produção
        log_level="info"
    ) 