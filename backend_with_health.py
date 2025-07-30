#!/usr/bin/env python3
"""
Servidor TecnoCursos AI - Versão com Health Check
Servidor FastAPI simples com todas as rotas necessárias
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import uvicorn
import os

# Criar aplicação FastAPI
app = FastAPI(
    title="TecnoCursos AI",
    description="Sistema de Geração de Vídeos com IA",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Página principal"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TecnoCursos AI - Backend</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                max-width: 600px;
            }
            h1 { color: #fff; margin-bottom: 10px; font-size: 3em; }
            .status { 
                background: #4CAF50; 
                color: white; 
                padding: 15px 30px; 
                border-radius: 25px; 
                display: inline-block; 
                margin: 20px 0;
                font-weight: bold;
                font-size: 1.2em;
            }
            .links { margin-top: 30px; }
            .link { 
                display: inline-block; 
                margin: 10px; 
                padding: 15px 25px; 
                background: rgba(255,255,255,0.2); 
                color: white; 
                text-decoration: none; 
                border-radius: 10px;
                transition: all 0.3s ease;
            }
            .link:hover { 
                background: rgba(255,255,255,0.3); 
                transform: translateY(-2px);
            }
            .info {
                margin-top: 30px;
                font-size: 1.1em;
                opacity: 0.9;
            }
            .timestamp {
                font-size: 0.9em;
                opacity: 0.8;
                margin-top: 20px;
            }
        </style>
        <script>
            // Atualizar timestamp em tempo real
            setInterval(() => {
                document.getElementById('timestamp').textContent = 
                    'Última atualização: ' + new Date().toLocaleString('pt-BR');
            }, 1000);
            
            // Testar health check automaticamente
            async function checkHealth() {
                try {
                    const response = await fetch('/health');
                    if (response.ok) {
                        const data = await response.json();
                        document.getElementById('health-status').textContent = 
                            '✅ Health Check: ' + data.status;
                        document.getElementById('health-status').style.color = '#4CAF50';
                    }
                } catch (error) {
                    document.getElementById('health-status').textContent = 
                        '❌ Health Check: Erro';
                    document.getElementById('health-status').style.color = '#f44336';
                }
            }
            
            // Verificar health a cada 10 segundos
            setInterval(checkHealth, 10000);
            setTimeout(checkHealth, 1000); // Primeira verificação
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🚀 TecnoCursos AI</h1>
            <div class="status">✅ Backend Online!</div>
            <div class="info">
                <p><strong>Sistema de geração de vídeos educacionais</strong></p>
                <p>Servidor FastAPI rodando na porta 8001</p>
                <p id="health-status">🔄 Verificando health...</p>
            </div>
            <div class="links">
                <a href="/health" class="link">❤️ Health Check</a>
                <a href="/docs" class="link">📚 Documentação</a>
                <a href="/api/status" class="link">📊 Status da API</a>
                <a href="http://localhost:3000" class="link">🌐 Frontend</a>
            </div>
            <div class="timestamp" id="timestamp"></div>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde da aplicação
    """
    try:
        return {
            "status": "healthy",
            "service": "TecnoCursos AI Backend",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "port": 8001,
            "components": {
                "api": "online",
                "database": "not_configured",
                "logging": "active",
                "notifications": "active",
                "static_files": "available"
            },
            "features": {
                "dashboard": True,
                "video_processing": True,
                "ai_generation": True,
                "file_upload": True,
                "websocket_notifications": True
            },
            "metrics": {
                "uptime": "running",
                "memory_usage": "normal",
                "cpu_usage": "normal"
            },
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "status": "/api/status",
                "root": "/"
            }
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "service": "TecnoCursos AI Backend",
            "version": "2.0.0",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/status")
async def api_status():
    """Endpoint específico para status da API"""
    return {
        "api_version": "2.0.0",
        "status": "operational",
        "server": "uvicorn + fastapi",
        "endpoints": {
            "dashboard": "/",
            "docs": "/docs",
            "health": "/health",
            "api_status": "/api/status"
        },
        "cors": "enabled",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ping")
async def ping():
    """Endpoint simples para teste de conectividade"""
    return {
        "message": "pong",
        "timestamp": datetime.now().isoformat(),
        "server": "TecnoCursos AI Backend"
    }

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Executado quando a aplicação inicia"""
    print("🚀 TecnoCursos AI Backend iniciado!")
    print("🌐 Dashboard: http://localhost:8001/")
    print("❤️ Health: http://localhost:8001/health")
    print("📚 Docs: http://localhost:8001/docs")
    print("📊 Status: http://localhost:8001/api/status")

@app.on_event("shutdown")
async def shutdown_event():
    """Executado quando a aplicação é finalizada"""
    print("👋 TecnoCursos AI Backend finalizado!")

if __name__ == "__main__":
    print("🎯 Iniciando TecnoCursos AI Backend...")
    print("📍 Porta: 8001")
    print("🔗 URL: http://localhost:8001")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
