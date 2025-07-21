#\!/usr/bin/env python3
"""
Servidor mínimo para TecnoCursos AI Editor
Versão simplificada para debug e testes
"""

import os
import sys
from pathlib import Path

# Configurar variáveis de ambiente antes de qualquer import
os.environ['DATABASE_URL'] = 'sqlite:///./tecnocursos.db'
os.environ['SECRET_KEY'] = 'test-secret-key-for-development'
os.environ['DEBUG'] = 'True'

# Remover variáveis problemáticas
for var in list(os.environ.keys()):
    if 'ALLOWED_EXTENSIONS' in var or 'CORS_' in var:
        del os.environ[var]

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
from datetime import datetime
import uvicorn

# Criar app FastAPI básica
app = FastAPI(
    title="TecnoCursos AI - Minimal Server",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except:
    pass

# Endpoints básicos
@app.get("/")
async def read_root():
    return {"message": "TecnoCursos AI Server - Running", "status": "ok"}

@app.get("/test_editor.html", response_class=HTMLResponse)
async def serve_test_editor():
    try:
        with open("test_editor.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("<h1>Erro: test_editor.html não encontrado</h1>")

@app.get("/editor_integrated.html", response_class=HTMLResponse)
async def serve_editor():
    try:
        with open("editor_integrated.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("<h1>Erro: editor_integrated.html não encontrado</h1>")

# API Endpoints de teste
@app.get("/api/editor/health")
async def api_health():
    return {
        "status": "healthy",
        "service": "TecnoCursos AI Minimal",
        "version": "1.0.0"
    }

@app.get("/api/editor/test/projects/list")
async def test_projects():
    return {
        "success": True,
        "projects": [
            {
                "id": 1,
                "name": "Projeto Demo",
                "description": "Projeto de demonstração",
                "scenes_count": 3,
                "duration": 30
            },
            {
                "id": 2,
                "name": "Tutorial Python", 
                "description": "Tutorial básico de Python",
                "scenes_count": 5,
                "duration": 45
            }
        ]
    }

@app.get("/api/editor/test/assets/list")
async def test_assets():
    return {
        "success": True,
        "assets": [
            {
                "id": "asset-1",
                "name": "sample-image.jpg",
                "type": "image",
                "size": 1024000,
                "url": "/uploads/sample-image.jpg"
            },
            {
                "id": "asset-2",
                "name": "background-music.mp3",
                "type": "audio",
                "size": 2048000,
                "url": "/uploads/background-music.mp3"
            }
        ]
    }

@app.post("/api/editor/test/assets/upload")
async def test_upload(files: List[UploadFile] = File(...)):
    try:
        uploaded_assets = []
        
        for file in files:
            asset_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                asset_type = 'image'
            elif file_extension in ['.mp4', '.avi', '.mov']:
                asset_type = 'video'
            elif file_extension in ['.mp3', '.wav', '.m4a']:
                asset_type = 'audio'
            else:
                asset_type = 'document'
            
            uploaded_assets.append({
                "id": asset_id,
                "name": file.filename,
                "type": asset_type,
                "size": getattr(file, 'size', 0),
                "url": f"/uploads/{asset_id}{file_extension}",
                "uploaded_at": datetime.now().isoformat()
            })
        
        return {
            "success": True,
            "assets": uploaded_assets,
            "message": f"{len(uploaded_assets)} arquivo(s) enviado(s) com sucesso"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro no upload"
        }

def main():
    print("=== TecnoCursos AI - Servidor Minimal ===")
    print("URLs disponíveis:")
    print("  http://localhost:8001/")
    print("  http://localhost:8001/test_editor.html")
    print("  http://localhost:8001/editor_integrated.html")
    print("  http://localhost:8001/docs")
    print("  http://localhost:8001/api/editor/health")
    print()
    print("Pressione Ctrl+C para parar")
    print("-" * 50)
    
    # Criar diretórios necessários
    for directory in ['uploads', 'static/videos', 'static/audios']:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    uvicorn.run(
        app,
        host="localhost",
        port=8001,
        log_level="info"
    )

if __name__ == "__main__":
    main()
