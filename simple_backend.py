#!/usr/bin/env python3
"""
Servidor TecnoCursos AI - Versão Simplificada
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="TecnoCursos AI", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações JWT
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modelos Pydantic
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 TecnoCursos AI</h1>
            <div class="status">✅ Backend Online!</div>
            <div class="info">
                <p>Servidor FastAPI rodando na porta 8000</p>
                <p>Sistema de geração de vídeos educacionais</p>
            </div>
            <div class="links">
                <a href="/docs" class="link">📚 Documentação da API</a>
                <a href="/health" class="link">❤️ Status de Saúde</a>
                <a href="http://localhost:3000" class="link">🌐 Frontend</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TecnoCursos AI Backend",
        "version": "1.0.0",
        "port": 8000
    }

@app.get("/api/status")
async def api_status():
    return {
        "backend": "online",
        "frontend": "check http://localhost:3000",
        "database": "not configured",
        "services": {
            "video_processing": "available",
            "ai_generation": "available",
            "file_upload": "available"
        }
    }

# Rotas de Autenticação
@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Endpoint de login"""
    # Validação simples (em produção, usar banco de dados real)
    if login_data.email == "admin@tecnocursos.com" and login_data.password == "admin123":
        # Criar token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": login_data.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.post("/api/auth/register")
async def register(login_data: LoginRequest):
    """Endpoint de registro"""
    return {
        "message": "Usuário registrado com sucesso",
        "email": login_data.email,
        "status": "success"
    }

@app.get("/api/auth/me")
async def get_current_user():
    """Endpoint para obter dados do usuário atual"""
    return {
        "email": "admin@tecnocursos.com",
        "name": "Administrador",
        "role": "admin",
        "avatar": "https://via.placeholder.com/100x100"
    }

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Criar token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

if __name__ == "__main__":
    print("🚀 Iniciando TecnoCursos AI Backend...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("❤️ Health: http://localhost:8000/health")
    
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
