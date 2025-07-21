"""
Servidor FastAPI simples para teste inicial
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Criar instância do FastAPI
app = FastAPI(
    title="TecnoCursos AI - Sistema de Upload de Arquivos",
    description="Sistema SaaS para upload de PDF/PPTX e geração de vídeos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos (se existirem)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Rotas básicas para teste
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página inicial com links para todas as páginas"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>TecnoCursos AI - Sistema de Upload</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                .card { box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15); border: none; }
                .nav-link { color: #495057; text-decoration: none; padding: 0.5rem 1rem; border-radius: 0.25rem; }
                .nav-link:hover { background-color: #e9ecef; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h2 class="mb-0">🚀 TecnoCursos AI - Sistema de Upload</h2>
                            </div>
                            <div class="card-body">
                                <h5>Sistema SaaS para upload de PDF/PPTX e geração automática de vídeos educacionais</h5>
                                <p class="text-muted">Status: <span class="badge bg-success">Online</span></p>
                                
                                <hr>
                                
                                <h6>📄 Páginas Disponíveis:</h6>
                                <div class="list-group">
                                    <a href="/login.html" class="list-group-item list-group-item-action">
                                        🔐 Login
                                    </a>
                                    <a href="/dashboard" class="list-group-item list-group-item-action">
                                        📊 Dashboard
                                    </a>
                                    <a href="/files" class="list-group-item list-group-item-action">
                                        📁 Gestão de Arquivos
                                    </a>
                                    <a href="/admin.html" class="list-group-item list-group-item-action">
                                        ⚙️ Administração
                                    </a>
                                </div>
                                
                                <hr>
                                
                                <h6>🔗 API Endpoints:</h6>
                                <div class="list-group">
                                    <a href="/docs" class="list-group-item list-group-item-action" target="_blank">
                                        📖 Documentação Swagger
                                    </a>
                                    <a href="/redoc" class="list-group-item list-group-item-action" target="_blank">
                                        📋 Documentação ReDoc
                                    </a>
                                    <a href="/health" class="list-group-item list-group-item-action">
                                        💚 Health Check
                                    </a>
                                </div>
                                
                                <hr>
                                
                                <h6>🆕 Funcionalidades Avatar:</h6>
                                <div class="list-group">
                                    <a href="/api/avatar/generate" class="list-group-item list-group-item-action">
                                        🎭 Gerar Vídeo Avatar
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check básico"""
    return {"status": "healthy", "message": "TecnoCursos AI está funcionando"}

@app.get("/api/info")
async def api_info():
    """Informações da API"""
    return {
        "name": "TecnoCursos AI",
        "version": "1.0.0",
        "description": "Sistema SaaS para upload de arquivos e geração de vídeos",
        "features": [
            "Upload de PDF/PPTX",
            "Geração de vídeos educacionais",
            "TTS com Bark AI",
            "Avatar virtual",
            "Dashboard administrativo"
        ]
    }

# Servir arquivos do template diretamente se não existir static
@app.get("/login.html", response_class=HTMLResponse)
async def serve_login():
    """Servir página de login"""
    try:
        with open("templates/login.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html><body>
        <h1>Login - TecnoCursos AI</h1>
        <p>Arquivo de template não encontrado. Verifique se templates/login.html existe.</p>
        <a href="/">Voltar ao início</a>
        </body></html>
        """, status_code=404)

@app.get("/admin.html", response_class=HTMLResponse) 
async def serve_admin():
    """Servir página de admin"""
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html><body>
        <h1>Admin - TecnoCursos AI</h1>
        <p>Arquivo de template não encontrado. Verifique se templates/admin.html existe.</p>
        <a href="/">Voltar ao início</a>
        </body></html>
        """, status_code=404)

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Servir página de dashboard"""
    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html><body>
        <h1>Dashboard - TecnoCursos AI</h1>
        <p>Arquivo de template não encontrado. Verifique se templates/dashboard.html existe.</p>
        <a href="/">Voltar ao início</a>
        </body></html>
        """, status_code=404)

@app.get("/files", response_class=HTMLResponse)
async def serve_files():
    """Servir página de arquivos"""
    try:
        with open("templates/files.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html><body>
        <h1>Arquivos - TecnoCursos AI</h1>
        <p>Arquivo de template não encontrado. Verifique se templates/files.html existe.</p>
        <a href="/">Voltar ao início</a>
        </body></html>
        """, status_code=404)

# Endpoint básico do avatar
@app.post("/api/avatar/generate")
async def generate_avatar_video():
    """Endpoint básico para geração de avatar"""
    return {
        "message": "Funcionalidade de avatar disponível!",
        "status": "ready", 
        "note": "Use o sistema completo no app/main.py para funcionalidade completa"
    }

if __name__ == "__main__":
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8001,  # Usar porta diferente para evitar conflito
        reload=True
    ) 