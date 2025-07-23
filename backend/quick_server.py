#!/usr/bin/env python3
"""
Servidor rápido em porta 8001 para teste

============================================
Acesso à documentação automática da API:
- Swagger UI:  http://localhost:8001/docs
  (Interface interativa para testar e explorar os endpoints da API)
- ReDoc:       http://localhost:8001/redoc
  (Documentação detalhada, ideal para leitura e referência)

Essas rotas são geradas automaticamente pelo FastAPI e refletem todos os endpoints disponíveis.
Utilize /docs para testes rápidos e /redoc para navegação e leitura aprofundada.
============================================
"""
import os
import pathlib
import platform
import socket
import datetime
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

# Criar app
app = FastAPI(title="TecnoCursos AI - Teste Rápido")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração dos templates Jinja2
PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")

# Variável de ambiente para nome do sistema (permite customização sem alterar código)
SYSTEM_NAME = os.getenv("SYSTEM_NAME", "TecnoCursos AI")
SYSTEM_VERSION = os.getenv("SYSTEM_VERSION", "2.0.0")
SYSTEM_ENV = os.getenv("SYSTEM_ENV", "dev")
SYSTEM_SUBTITLE = os.getenv("SYSTEM_SUBTITLE", "Monitoramento Inteligente de Vídeos e IA")
SYSTEM_AUTHOR = os.getenv("SYSTEM_AUTHOR", "Equipe TecnoCursos")

# Função utilitária para montar o contexto do dashboard
# Para adicionar novos dados dinâmicos, basta incluir no dicionário abaixo
# Exemplo: para adicionar um novo componente, adicione no array component_status

def get_dashboard_context(request: Request):
    """Monta o contexto dinâmico para o dashboard."""
    server_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname()
    }
    system_info = {
        "name": SYSTEM_NAME,  # Nome do sistema vindo de variável de ambiente
        "version": SYSTEM_VERSION,
        "status": "online",
        "description": "Dashboard de Controle do Sistema TecnoCursos AI",
        "author": SYSTEM_AUTHOR,
        "subtitle": SYSTEM_SUBTITLE,
        "environment": SYSTEM_ENV,
        "server_info": server_info,
        "last_updated": datetime.datetime.now().isoformat()
    }
    overall_status = "online"
    status_message = "Todos os sistemas operando normalmente."
    stats = {
        "online": 8,
        "warning": 0,
        "error": 0
    }
    component_status = [
        {
            "name": "API Principal",
            "status": "online",
            "icon": "🔗",
            "description": "Backend FastAPI",
            "details": "Responde em <100ms"
        },
        {
            "name": "Banco de Dados",
            "status": "online",
            "icon": "🗄️",
            "description": "PostgreSQL",
            "details": "Conexão estável"
        },
        {
            "name": "Processador de Vídeo",
            "status": "online",
            "icon": "🎬",
            "description": "MoviePy Engine",
            "details": "Sem filas"
        },
        {
            "name": "TTS (Narração)",
            "status": "warning",
            "icon": "🗣️",
            "description": "Text-to-Speech",
            "details": "Dependências opcionais ausentes"
        },
        {
            "name": "Cache",
            "status": "online",
            "icon": "⚡",
            "description": "Redis",
            "details": "Cache L2 ativo"
        },
        {
            "name": "Monitoramento",
            "status": "online",
            "icon": "📈",
            "description": "Prometheus",
            "details": "Métricas em tempo real"
        },
        {
            "name": "Backup",
            "status": "online",
            "icon": "💾",
            "description": "Backup Automático",
            "details": "Último: 1h atrás"
        },
        {
            "name": "Frontend",
            "status": "online",
            "icon": "🖥️",
            "description": "React App",
            "details": "Build atualizado"
        }
    ]
    system_metrics = {
        "cpu_usage": 12.5,
        "memory_usage": 48.2,
        "uptime": "3d 4h 12m",
        "active_processes": 7
    }
    quick_actions = [
        {
            "title": "Abrir Editor",
            "description": "Acesse o editor de vídeos",
            "url": "/editor_integrated.html",
            "icon": "📝",
            "color": "blue"
        },
        {
            "title": "Painel de Projetos",
            "description": "Gerencie seus projetos",
            "url": "/frontend_complete.html",
            "icon": "📁",
            "color": "green"
        },
        {
            "title": "Upload de Arquivos",
            "description": "Envie PDFs, PPTX ou imagens",
            "url": "/files.html",
            "icon": "⬆️",
            "color": "orange"
        },
        {
            "title": "Dashboard Admin",
            "description": "Acesse o painel administrativo",
            "url": "/admin.html",
            "icon": "🔒",
            "color": "purple"
        }
    ]
    return {
        "request": request,
        "system_info": system_info,
        "overall_status": overall_status,
        "status_message": status_message,
        "stats": stats,
        "component_status": component_status,
        "system_metrics": system_metrics,
        "quick_actions": quick_actions
    }

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    """Endpoint raiz que renderiza o dashboard.html com contexto completo."""
    try:
        context = get_dashboard_context(request)
        return templates.TemplateResponse("dashboard.html", context)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"[ERRO 500] Falha ao renderizar dashboard: {exc}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        
        context = {
            "request": request,
            "error_message": "Erro interno ao carregar o dashboard.",
            "error_details": str(exc),
            "error_code": 500,
            "system_info": {  # Adicionando um fallback para system_info
                "name": SYSTEM_NAME,
                "version": SYSTEM_VERSION,
                "environment": SYSTEM_ENV
            }
        }
        
        return templates.TemplateResponse(
            "500.html",
            context,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/api/health")
def health(request: Request):
    """Endpoint de health check simples."""
    return {"status": "ok", "service": "TecnoCursos AI", "port": request.scope['server'][1]}

def find_free_port(start_port=8001, max_retries=10):
    """Encontra uma porta TCP livre, começando de `start_port`."""
    port = start_port
    for attempt in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                print(f"✅ Porta {port} está disponível")
                return port
        except OSError:
            if attempt == 0:
                print(f"⚠️  Porta {port} está ocupada, buscando porta livre...")
            port += 1
    raise ConnectionError(f"❌ Não foi possível encontrar uma porta livre após {max_retries} tentativas (testadas: {start_port}-{start_port + max_retries - 1})")

if __name__ == "__main__":
    try:
        PORT = find_free_port()
        print(f"🚀 Servidor rápido na porta {PORT}")
        print(f"💚 Health: http://localhost:{PORT}/api/health")
        print(f"📚 Docs: http://localhost:{PORT}/docs")
        print(f"🏠 Dashboard: http://localhost:{PORT}/")
        print(f"")
        print(f"🔥 Pressione Ctrl+C para parar o servidor")
        print(f"" + "="*50)

        uvicorn.run(
            app,
            host="127.0.0.1",
            port=PORT,
            log_level="info"
        )
    except ConnectionError as e:
        print(f"❌ Erro de porta: {e}")
        print(f"💡 Dica: Verifique se algum processo está usando as portas 8001-8010")
        print(f"💡 Para verificar: netstat -ano | findstr :8001")
    except KeyboardInterrupt:
        print(f"\n👋 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print(f"📝 Traceback completo:")
        print(traceback.format_exc()) 