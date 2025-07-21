#!/usr/bin/env python3
"""
TecnoCursos AI - Sistema de Geração de Vídeos
Aplicação FastAPI principal com dashboard personalizado

Configurações principais:
- Dashboard moderno na rota "/"
- Templates Jinja2 responsivos
- Arquivos estáticos (CSS, JS, imagens)
- Sistema de logging integrado
- Notificações em tempo real
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio

# Import dos routers
from app.routers.dashboard import router as dashboard_router
from app.routers.notifications import router as notifications_router
from app.services.notification_service import cleanup_notifications_task
from app.services.logging_service import logging_service, LogLevel, LogCategory

# Configuração da aplicação FastAPI
app = FastAPI(
    title="TecnoCursos AI",
    description="Sistema de Geração de Vídeos com Inteligência Artificial",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios exatos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de arquivos estáticos
# IMPORTANTE: A ordem importa! Rotas específicas devem vir antes de StaticFiles
try:
    # Monta arquivos estáticos (CSS, JS, imagens)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("✅ Arquivos estáticos configurados em /static")
except Exception as e:
    print(f"⚠️  Erro ao configurar arquivos estáticos: {e}")
    print("💡 Certifique-se de que a pasta 'static' existe na raiz do projeto")

# Configuração de templates
try:
    # Templates Jinja2 para renderização HTML
    templates = Jinja2Templates(directory="templates")
    print("✅ Templates Jinja2 configurados em /templates")
except Exception as e:
    print(f"⚠️  Erro ao configurar templates: {e}")
    print("💡 Certifique-se de que a pasta 'templates' existe na raiz do projeto")

# Incluir routers
app.include_router(dashboard_router, tags=["dashboard"])
app.include_router(notifications_router, tags=["notificações"])

# Eventos de startup e shutdown
@app.on_event("startup")
async def startup_event():
    """
    Eventos executados na inicialização da aplicação
    
    Inclui:
    - Inicialização do sistema de logging
    - Start de tasks assíncronas (cleanup de notificações)
    - Verificação de dependências
    - Log de startup da aplicação
    """
    try:
        # Log de inicialização
        await logging_service.log(
            LogLevel.INFO,
            LogCategory.SYSTEM_OPERATION,
            "TecnoCursos AI iniciado com sucesso",
            metadata={
                "version": "2.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "features": ["dashboard", "notifications", "logging", "video_processing"]
            }
        )
        
        # Iniciar task de limpeza de notificações
        asyncio.create_task(cleanup_notifications_task())
        print("🧹 Task de limpeza de notificações iniciada")
        
        # Verificar estrutura de pastas necessárias
        required_dirs = ["static", "templates", "logs", "uploads", "static/css", "static/js"]
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"📁 Pasta criada: {dir_path}")
        
        print("🚀 TecnoCursos AI iniciado com sucesso!")
        print("🌐 Dashboard disponível em: http://localhost:8000/")
        print("📚 Documentação API: http://localhost:8000/docs")
        print("🔔 WebSocket Notificações: ws://localhost:8000/notifications/ws/{user_id}")
        
    except Exception as e:
        print(f"❌ Erro durante startup: {e}")
        # Em produção, considere fazer raise para falhar explicitamente
        await logging_service.log_error(e, LogCategory.SYSTEM_OPERATION)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Eventos executados no shutdown da aplicação
    
    Inclui:
    - Log de shutdown
    - Cleanup de conexões WebSocket
    - Finalização de operações pendentes
    """
    try:
        # Log de shutdown
        await logging_service.log(
            LogLevel.INFO,
            LogCategory.SYSTEM_OPERATION,
            "TecnoCursos AI sendo finalizado"
        )
        
        # Cleanup de conexões WebSocket
        from app.services.notification_service import notification_service
        
        connected_users = notification_service.connection_manager.get_connected_users()
        for user_id in connected_users:
            connections = notification_service.connection_manager.active_connections.get(user_id, set())
            for ws in connections.copy():
                try:
                    await ws.close()
                except Exception:
                    pass  # Ignora erros de conexões já fechadas
        
        print("👋 TecnoCursos AI finalizado")
        
    except Exception as e:
        print(f"❌ Erro durante shutdown: {e}")

# Middleware para logging de requests (opcional)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logging automático de todas as requisições
    
    Para produção, considere usar ferramentas como Prometheus + Grafana
    ou integração com serviços de monitoramento como DataDog, New Relic
    """
    start_time = asyncio.get_event_loop().time()
    
    # Executa a requisição
    response = await call_next(request)
    
    # Calcula tempo de processamento
    process_time = asyncio.get_event_loop().time() - start_time
    
    # Log apenas se não for arquivo estático (para evitar spam)
    if not request.url.path.startswith("/static"):
        try:
            await logging_service.log(
                LogLevel.INFO,
                LogCategory.USER_ACTION,
                f"HTTP {request.method} {request.url.path}",
                metadata={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                    "user_agent": request.headers.get("user-agent", ""),
                    "ip_address": request.client.host
                }
            )
        except Exception:
            # Ignora erros de logging para não quebrar a aplicação
            pass
    
    return response

# Template de erro personalizado (opcional)
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Handler personalizado para página 404"""
    try:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "error_code": 404,
            "error_message": "Página não encontrada",
            "back_url": "/"
        }, status_code=404)
    except Exception:
        # Fallback se template não existir
        return HTMLResponse(
            content="""
            <html>
                <head><title>404 - Página não encontrada</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>404 - Página não encontrada</h1>
                    <p>A página que você está procurando não existe.</p>
                    <a href="/">← Voltar ao Dashboard</a>
                </body>
            </html>
            """,
            status_code=404
        )

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc):
    """Handler personalizado para erro interno"""
    try:
        # Log do erro
        await logging_service.log_error(exc, LogCategory.ERROR_HANDLING)
        
        return templates.TemplateResponse("500.html", {
            "request": request,
            "error_code": 500,
            "error_message": "Erro interno do servidor",
            "back_url": "/"
        }, status_code=500)
    except Exception:
        # Fallback se template não existir
        return HTMLResponse(
            content="""
            <html>
                <head><title>500 - Erro interno</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>500 - Erro interno do servidor</h1>
                    <p>Ocorreu um erro interno. Tente novamente em alguns minutos.</p>
                    <a href="/">← Voltar ao Dashboard</a>
                </body>
            </html>
            """,
            status_code=500
        )

# Endpoint adicional para favicon
@app.get("/favicon.ico")
async def favicon():
    """Endpoint para favicon (evita erro 404 no navegador)"""
    from fastapi.responses import FileResponse
    
    favicon_path = "static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        # Retorna um favicon padrão se não existir
        return HTMLResponse(content="", status_code=204)

# Informações para desenvolvedor
if __name__ == "__main__":
    print("""
    🎬 TecnoCursos AI - Sistema de Geração de Vídeos
    
    📋 Para executar a aplicação:
    
    Desenvolvimento:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
    Produção:
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    
    🌐 URLs importantes:
    - Dashboard: http://localhost:8000/
    - API Docs: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - Health Check: http://localhost:8000/health
    - Logs: http://localhost:8000/admin/logs (se implementado)
    
    📁 Estrutura esperada:
    ├── main.py
    ├── app/
    │   ├── routers/
    │   │   ├── dashboard.py
    │   │   └── notifications.py
    │   └── services/
    │       ├── logging_service.py
    │       └── notification_service.py
    ├── templates/
    │   ├── dashboard.html
    │   ├── 404.html
    │   └── 500.html
    ├── static/
    │   ├── css/
    │   │   └── dashboard.css
    │   ├── js/
    │   │   └── dashboard.js
    │   └── favicon.ico
    └── logs/ (criado automaticamente)
    
    ⚙️  Variáveis de ambiente opcionais:
    - SYSTEM_NAME: Nome do sistema (default: "TecnoCursosAI")
    - SYSTEM_VERSION: Versão (default: "2.0.0")
    - ENVIRONMENT: Ambiente (default: "development")
    - LOG_LEVEL: Nível de log (default: "INFO")
    """)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 