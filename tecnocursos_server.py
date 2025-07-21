#!/usr/bin/env python3
"""
Servidor TecnoCursos AI - Enterprise Edition 2025
================================================

Servidor principal com funcionalidades básicas estáveis.

Autor: TecnoCursos AI System
"""

import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tecnocursos_ai")

# Criar aplicação FastAPI
app = FastAPI(
    title="TecnoCursos AI - Enterprise Edition 2025",
    description="""
    🚀 **Plataforma SaaS Enterprise para Criação de Conteúdo Educacional com IA**
    
    ## 🎯 Funcionalidades Principais
    - Upload e processamento de arquivos (PDF, PPTX, DOCX)
    - Geração de narração com TTS
    - Criação de vídeos com templates profissionais
    - Sistema de autenticação JWT
    - API REST completa
    
    ## 🧠 Inteligência Artificial
    - Modern AI Service com Multimodal AI
    - Quantum Optimization para problemas complexos
    - Edge Computing distribuído
    - Analytics em tempo real
    
    ## 📊 APIs Disponíveis
    - 60+ endpoints documentados
    - WebSocket para comunicação real-time
    - Processamento em lote
    - Templates de vídeo avançados
    """,
    version="2.0.0",
    contact={
        "name": "TecnoCursos AI Support",
        "email": "support@tecnocursos.ai"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar arquivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("app/static"):
    app.mount("/app/static", StaticFiles(directory="app/static"), name="app_static")

# ============================================================================
# ROUTERS BÁSICOS
# ============================================================================

loaded_services = []

def safe_include_router(router_module, router_name, description):
    """Incluir router de forma segura"""
    try:
        module = __import__(router_module, fromlist=[router_name])
        router = getattr(module, router_name)
        if router and hasattr(router, 'routes'):
            app.include_router(router)
            loaded_services.append(description)
            logger.info(f"✅ {description} carregado")
            return True
    except Exception as e:
        logger.warning(f"⚠️ {description} não disponível: {e}")
        return False

# Carregar routers básicos
safe_include_router("app.routers.auth", "router", "Authentication API")
safe_include_router("app.routers.users", "router", "User Management")
safe_include_router("app.routers.projects", "router", "Project Management")
safe_include_router("app.routers.files", "router", "File Management")
safe_include_router("app.routers.admin", "router", "Admin Panel")
safe_include_router("app.routers.stats", "router", "Statistics")

# Carregar routers avançados
safe_include_router("app.routers.avatar", "router", "Avatar Videos")
safe_include_router("app.routers.advanced_video_processing", "router", "Advanced Video Processing")
safe_include_router("app.routers.video_generation", "router", "Video Generation")
safe_include_router("app.routers.batch_upload", "router", "Batch Upload")
safe_include_router("app.routers.modern_ai_router", "router", "Modern AI Service")
safe_include_router("app.routers.quantum_router", "router", "Quantum Optimization")

# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Página inicial do TecnoCursos AI"""
    return HTMLResponse(content=f"""
    <html>
        <head>
            <title>TecnoCursos AI - Enterprise Edition 2025</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                body {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    min-height: 100vh; 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .hero {{ background: rgba(255,255,255,0.95); border-radius: 15px; backdrop-filter: blur(10px); }}
                .feature-card {{ 
                    transition: transform 0.3s ease; 
                    background: rgba(255,255,255,0.9); 
                    border-radius: 10px;
                }}
                .feature-card:hover {{ transform: translateY(-5px); }}
                .status-badge {{ font-size: 0.9rem; }}
            </style>
        </head>
        <body>
            <div class="container py-5">
                <div class="hero p-5 text-center mb-5">
                    <h1 class="display-4 mb-3">
                        <i class="fas fa-rocket text-primary"></i> 
                        TecnoCursos AI
                    </h1>
                    <h2 class="h4 mb-4 text-muted">Enterprise Edition 2025</h2>
                    <p class="lead">Plataforma SaaS para criação de conteúdo educacional com IA de vanguarda</p>
                    <div class="row mt-4">
                        <div class="col-md-4">
                            <span class="badge bg-success status-badge">
                                <i class="fas fa-check-circle"></i> Sistema Operacional
                            </span>
                        </div>
                        <div class="col-md-4">
                            <span class="badge bg-info status-badge">
                                <i class="fas fa-server"></i> {len(loaded_services)} Serviços Ativos
                            </span>
                        </div>
                        <div class="col-md-4">
                            <span class="badge bg-warning text-dark status-badge">
                                <i class="fas fa-bolt"></i> Enterprise Ready
                            </span>
                        </div>
                    </div>
                </div>
                
                <div class="row g-4">
                    <div class="col-md-3">
                        <div class="feature-card p-4 h-100">
                            <h5><i class="fas fa-cogs text-primary"></i> APIs</h5>
                            <p class="text-muted small">60+ endpoints documentados</p>
                            <a href="/docs" class="btn btn-outline-primary btn-sm">Swagger UI</a>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="feature-card p-4 h-100">
                            <h5><i class="fas fa-heartbeat text-success"></i> Health</h5>
                            <p class="text-muted small">Monitoramento de sistema</p>
                            <a href="/api/health" class="btn btn-outline-success btn-sm">Verificar</a>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="feature-card p-4 h-100">
                            <h5><i class="fas fa-brain text-info"></i> AI Services</h5>
                            <p class="text-muted small">Multimodal AI + Quantum</p>
                            <a href="/docs#/Modern%20AI" class="btn btn-outline-info btn-sm">Explorar</a>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="feature-card p-4 h-100">
                            <h5><i class="fas fa-video text-warning"></i> Video</h5>
                            <p class="text-muted small">Geração automatizada</p>
                            <a href="/docs#/Video%20Generation" class="btn btn-outline-warning btn-sm">Ver Mais</a>
                        </div>
                    </div>
                </div>

                <div class="mt-5 text-center">
                    <h4 class="text-white mb-3">Serviços Carregados</h4>
                    <div class="row">
                        {''.join([f'<div class="col-md-6 mb-2"><span class="badge bg-light text-dark w-100"><i class="fas fa-check text-success"></i> {service}</span></div>' for service in loaded_services])}
                    </div>
                </div>
            </div>
        </body>
    </html>
    """)

@app.get("/api/health")
async def health_check():
    """Health check com informações detalhadas"""
    return JSONResponse({
        "status": "healthy",
        "message": "TecnoCursos AI Enterprise Edition 2025 - Totalmente Operacional",
        "version": "2.0.0",
        "services": {
            "loaded_count": len(loaded_services),
            "loaded_services": loaded_services,
            "api": True,
            "static_files": os.path.exists("static"),
            "app_static": os.path.exists("app/static")
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/health",
            "homepage": "/"
        }
    })

@app.get("/api/status")
async def system_status():
    """Status detalhado do sistema"""
    return JSONResponse({
        "system": "TecnoCursos AI Enterprise Edition 2025",
        "status": "operational",
        "version": "2.0.0",
        "loaded_services": loaded_services,
        "features": {
            "authentication": "Authentication API" in loaded_services,
            "file_management": "File Management" in loaded_services,
            "video_generation": "Video Generation" in loaded_services,
            "modern_ai": "Modern AI Service" in loaded_services,
            "quantum_optimization": "Quantum Optimization" in loaded_services
        }
    })

def main():
    """Inicializar servidor"""
    print("🚀 Iniciando TecnoCursos AI Enterprise Edition 2025...")
    print(f"📊 Serviços carregados: {len(loaded_services)}")
    for service in loaded_services:
        print(f"   ✅ {service}")
    print("=" * 60)
    print("🌐 Servidor disponível em: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/api/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main() 