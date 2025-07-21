#!/usr/bin/env python3
"""
Servidor mínimo apenas para testar o sistema de login
"""

import os
import sys
from pathlib import Path

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import uvicorn
import logging

# Configurar logging simples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar apenas o necessário
from app.database import engine, Base, get_db
from app.models import User
from app.auth import auth_manager
from app.schemas import UserResponse

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Criar app
app = FastAPI(title="TecnoCursos AI - Login Test")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas simples
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    username: str

# Endpoints
@app.get("/")
async def root():
    """Página inicial com informações do sistema"""
    return {
        "message": "TecnoCursos AI - Sistema de Login",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/api/health",
            "login": "/api/auth/login",
            "register": "/api/auth/register",
            "refresh": "/api/auth/refresh",
            "user_info": "/api/users/me",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "test_credentials": {
            "admin": {
                "email": "admin@tecnocursos.ai",
                "password": "admin123"
            },
            "user": {
                "email": "teste@tecnocursos.ai",
                "password": "senha123"
            }
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
async def login_page():
    """Página de login"""
    try:
        # Tentar ler o arquivo HTML
        login_file = Path(__file__).parent / "login_page.html"
        if login_file.exists():
            return login_file.read_text(encoding='utf-8')
        else:
            # Retornar HTML inline se o arquivo não existir
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login - TecnoCursos AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f0f0f0; }
                    .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; margin-bottom: 20px; }
                    .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                    .endpoint { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; font-family: monospace; }
                    a { color: #1976d2; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎓 TecnoCursos AI - Login</h1>
                    <div class="info">
                        <p><strong>Sistema de Login Funcionando!</strong></p>
                        <p>Use um cliente HTTP ou a interface React para fazer login.</p>
                    </div>
                    <h3>📍 Endpoints Disponíveis:</h3>
                    <div class="endpoint">POST /api/auth/login</div>
                    <div class="endpoint">POST /api/auth/register</div>
                    <div class="endpoint">GET /api/users/me</div>
                    <h3>🔑 Credenciais de Teste:</h3>
                    <div class="info">
                        <p><strong>Admin:</strong> admin@tecnocursos.ai / admin123</p>
                        <p><strong>Usuário:</strong> teste@tecnocursos.ai / senha123</p>
                    </div>
                    <p style="margin-top: 20px;">
                        <a href="/docs">📚 Documentação Interativa</a> | 
                        <a href="/redoc">📖 ReDoc</a>
                    </p>
                </div>
            </body>
            </html>
            """
    except Exception as e:
        logger.error(f"Erro ao servir página de login: {e}")
        raise HTTPException(status_code=500, detail="Erro ao carregar página")

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    try:
        # Autenticar
        user = auth_manager.authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos"
            )
        
        # Criar tokens
        access_token = auth_manager.create_access_token(user.id)
        refresh_token = auth_manager.create_refresh_token(user.id)
        
        # Atualizar último login
        auth_manager.update_last_login(db, user)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.post("/api/auth/register", response_model=LoginResponse)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register endpoint"""
    try:
        # Verificar se já existe
        existing = db.query(User).filter(
            (User.email == register_data.email) | 
            (User.username == register_data.username)
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email ou username já em uso"
            )
        
        # Criar usuário
        user = auth_manager.create_user(
            db,
            email=register_data.email,
            username=register_data.username,
            password=register_data.password,
            full_name=register_data.full_name
        )
        
        # Criar tokens
        access_token = auth_manager.create_access_token(user.id)
        refresh_token = auth_manager.create_refresh_token(user.id)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.post("/api/auth/refresh")
async def refresh_token(
    refresh_data: dict,
    db: Session = Depends(get_db)
):
    """Refresh token endpoint"""
    try:
        refresh_token = refresh_data.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token necessário")
        
        result = auth_manager.refresh_access_token(db, refresh_token)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no refresh: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(auth_manager.oauth2_scheme)
):
    """Get current user endpoint"""
    try:
        # Verificar token
        payload = auth_manager.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Buscar usuário
        user = auth_manager.get_user_by_id(db, int(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

if __name__ == "__main__":
    try:
        logger.info("🚀 Iniciando servidor de teste de login...")
        logger.info("🌐 URL: http://localhost:8000")
        logger.info("📚 Docs: http://localhost:8000/docs")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar: {e}")
        sys.exit(1) 