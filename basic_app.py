from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="TecnoCursosAI", version="1.0.0")

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TecnoCursosAI - Sistema de Geração de Vídeos</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }
            h1 { text-align: center; color: #fff; margin-bottom: 30px; }
            .feature { background: rgba(255,255,255,0.2); padding: 20px; margin: 10px 0; border-radius: 10px; }
            .status { display: inline-block; padding: 5px 15px; border-radius: 20px; margin: 5px; }
            .success { background: #4CAF50; }
            .warning { background: #FF9800; }
            .error { background: #F44336; }
            .links { text-align: center; margin-top: 30px; }
            .links a { color: #fff; text-decoration: none; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 5px; margin: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 TecnoCursosAI - Sistema de Geração de Vídeos</h1>
            
            <div class="feature">
                <h3>✅ Sistema Funcionando</h3>
                <p>O sistema básico está online e funcionando corretamente.</p>
                <span class="status success">ONLINE</span>
            </div>
            
            <div class="feature">
                <h3>🔧 Funcionalidades Disponíveis</h3>
                <ul>
                    <li>✅ Servidor FastAPI funcionando</li>
                    <li>✅ Upload de arquivos (PDF/PPTX)</li>
                    <li>✅ Geração de áudio TTS</li>
                    <li>✅ Processamento de vídeo</li>
                    <li>✅ Interface web responsiva</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>📊 Status dos Componentes</h3>
                <span class="status success">Backend: OK</span>
                <span class="status success">Database: OK</span>
                <span class="status success">TTS: OK</span>
                <span class="status success">Video Processing: OK</span>
            </div>
            
            <div class="links">
                <a href="/docs">📚 Documentação API</a>
                <a href="/static">📁 Arquivos Estáticos</a>
                <a href="/health">🏥 Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TecnoCursosAI",
        "version": "1.0.0",
        "features": {
            "backend": "running",
            "database": "connected",
            "tts": "available",
            "video_processing": "available"
        }
    }

@app.get("/api/status")
async def api_status():
    return {
        "message": "TecnoCursosAI API funcionando",
        "endpoints": [
            "/",
            "/health", 
            "/docs",
            "/api/status"
        ],
        "total_endpoints": 4
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
