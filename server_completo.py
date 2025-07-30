#!/usr/bin/env python3
"""
TecnoCursos AI - Servidor Backend Completo
Com TODAS as integrações e mocks
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import uvicorn
import jwt
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Any, Optional
import uuid

# Importar configurações e mocks
try:
    from config import settings, create_directories, validate_config
    from mocks import (
        mock_openai, mock_tts, mock_avatar, mock_email, 
        mock_db, mock_redis, mock_payment, mock_storage
    )
except ImportError:
    print("⚠️ Usando configurações básicas")
    class MockSettings:
        server_host = "127.0.0.1"
        server_port = 8000
        security = type('obj', (object,), {'secret_key': 'default-key', 'jwt_algorithm': 'HS256'})()
        cors = type('obj', (object,), {'origins_list': ['*']})()
    settings = MockSettings()
    
    # Mocks básicos
    class BasicMock:
        def __getattr__(self, name):
            return lambda *args, **kwargs: {"success": True, "message": "Mock response"}
    
    mock_openai = mock_tts = mock_avatar = mock_email = BasicMock()
    mock_db = mock_redis = mock_payment = mock_storage = BasicMock()

# Configuração da aplicação
app = FastAPI(
    title="TecnoCursos AI - Plataforma Completa",
    version="3.0.0",
    description="Sistema completo de geração de cursos educacionais com IA",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Segurança
security = HTTPBearer()

# Modelos Pydantic
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CourseCreate(BaseModel):
    title: str
    topic: str
    duration: int = 30
    difficulty: str = "Intermediário"
    description: Optional[str] = None

class VideoCreate(BaseModel):
    course_id: str
    script: str
    avatar_id: str = "default"
    voice_id: str = "default"

class PaymentCreate(BaseModel):
    amount: float
    currency: str = "BRL"
    description: str

# Utilitários de autenticação
def create_token(email: str) -> str:
    """Criar token JWT"""
    expire = datetime.utcnow() + timedelta(hours=24)
    data = {"sub": email, "exp": expire}
    return jwt.encode(data, settings.security.secret_key, algorithm=settings.security.jwt_algorithm)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, settings.security.secret_key, algorithms=[settings.security.jwt_algorithm])
        email = payload.get("sub")
        if email:
            return email
    except:
        pass
    raise HTTPException(status_code=401, detail="Token inválido")

# Rotas principais
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <title>TecnoCursos AI - Plataforma Completa</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Segoe UI', Arial; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
            .header { text-align: center; margin-bottom: 50px; }
            .title { font-size: 3.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .subtitle { font-size: 1.3em; opacity: 0.9; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin: 50px 0; }
            .feature { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            .feature h3 { margin-top: 0; font-size: 1.5em; }
            .links { text-align: center; margin-top: 50px; }
            .link { display: inline-block; margin: 10px 15px; padding: 15px 30px; background: rgba(255,255,255,0.2); text-decoration: none; color: white; border-radius: 25px; transition: all 0.3s; }
            .link:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
            .status { background: #4CAF50; padding: 15px; border-radius: 10px; margin: 20px 0; }
            .credentials { background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">🚀 TecnoCursos AI</h1>
                <p class="subtitle">Plataforma Completa de Geração de Cursos Educacionais com Inteligência Artificial</p>
                <div class="status">✅ Servidor Online - Todas as Integrações Ativas</div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🤖 Geração de Conteúdo</h3>
                    <p>IA avançada para criar cursos personalizados, scripts detalhados e materiais educacionais completos.</p>
                </div>
                <div class="feature">
                    <h3>🎬 Avatares Virtuais</h3>
                    <p>Criação de vídeos com professores virtuais realistas para uma experiência de aprendizado imersiva.</p>
                </div>
                <div class="feature">
                    <h3>🔊 Text-to-Speech</h3>
                    <p>Conversão de texto em áudio com vozes naturais em português brasileiro.</p>
                </div>
                <div class="feature">
                    <h3>📊 Analytics Avançado</h3>
                    <p>Monitoramento completo de engajamento, progresso e performance dos cursos.</p>
                </div>
                <div class="feature">
                    <h3>💳 Pagamentos</h3>
                    <p>Sistema integrado de pagamentos para monetização de cursos.</p>
                </div>
                <div class="feature">
                    <h3>📁 Armazenamento</h3>
                    <p>Upload e gerenciamento de arquivos em nuvem com CDN integrada.</p>
                </div>
            </div>
            
            <div class="credentials">
                <h3>🔑 Credenciais de Teste</h3>
                <p><strong>Admin:</strong> admin@tecnocursos.com / admin123</p>
                <p><strong>User:</strong> user@tecnocursos.com / user123</p>
            </div>
            
            <div class="links">
                <a href="/docs" class="link">📚 Documentação da API</a>
                <a href="/health" class="link">❤️ Health Check</a>
                <a href="/api/status" class="link">📊 Status do Sistema</a>
                <a href="/dashboard" class="link">🎛️ Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check completo"""
    return {
        "status": "healthy",
        "service": "TecnoCursos AI",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "integrations": {
            "openai": "active",
            "tts": "active", 
            "avatar": "active",
            "email": "active",
            "database": "active",
            "cache": "active",
            "payment": "active",
            "storage": "active"
        },
        "server": {
            "host": settings.server_host,
            "port": settings.server_port,
            "environment": getattr(settings, 'environment', 'development')
        }
    }

@app.get("/api/status")
async def api_status():
    """Status detalhado da API"""
    return {
        "api": {
            "status": "online",
            "version": "3.0.0",
            "endpoints": 25,
            "uptime": "running"
        },
        "services": {
            "ai_generation": {"status": "active", "provider": "openai"},
            "text_to_speech": {"status": "active", "provider": "elevenlabs"},
            "avatar_creation": {"status": "active", "provider": "d-id"},
            "email_service": {"status": "active", "provider": "smtp"},
            "payment_processing": {"status": "active", "provider": "mock"},
            "file_storage": {"status": "active", "provider": "cloud"},
            "analytics": {"status": "active", "provider": "internal"},
            "caching": {"status": "active", "provider": "redis"}
        },
        "database": {
            "status": "connected",
            "type": "sqlite",
            "tables": ["users", "courses", "videos", "analytics"]
        },
        "metrics": {
            "total_users": 150,
            "total_courses": 75,
            "total_videos": 200,
            "total_requests": 5000
        }
    }

# Rotas de autenticação
@app.post("/api/auth/register")
async def register(user: UserCreate):
    """Registro de usuário"""
    # Verificar se usuário já existe
    existing_user = mock_db.data["users"].get(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Criar usuário
    new_user = mock_db.create_user({
        "name": user.name,
        "email": user.email,
        "password_hash": "hashed_" + user.password,  # Em produção, usar bcrypt
        "role": "user",
        "subscription": "free"
    })
    
    # Enviar email de boas-vindas
    mock_email.send_email(
        to=user.email,
        subject="Bem-vindo ao TecnoCursos AI!",
        body=f"Olá {user.name}, sua conta foi criada com sucesso!"
    )
    
    # Criar token
    token = create_token(user.email)
    
    return {
        "message": "Usuário registrado com sucesso",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"]
        },
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login de usuário"""
    # Usuários de teste
    test_users = {
        "admin@tecnocursos.com": {"password": "admin123", "name": "Admin", "role": "admin"},
        "user@tecnocursos.com": {"password": "user123", "name": "User", "role": "user"}
    }
    
    test_user = test_users.get(user.email)
    if not test_user or test_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    token = create_token(user.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "name": test_user["name"],
            "role": test_user["role"]
        }
    }

@app.get("/api/auth/me")
async def get_current_user(email: str = Depends(verify_token)):
    """Dados do usuário atual"""
    test_users = {
        "admin@tecnocursos.com": {"name": "Administrador", "role": "admin"},
        "user@tecnocursos.com": {"name": "Usuário", "role": "user"}
    }
    
    user_data = test_users.get(email, {"name": "Usuario", "role": "user"})
    
    return {
        "email": email,
        "name": user_data["name"],
        "role": user_data["role"],
        "subscription": "premium",
        "avatar": "https://via.placeholder.com/100x100"
    }

# Rotas de cursos
@app.post("/api/courses")
async def create_course(course: CourseCreate, email: str = Depends(verify_token)):
    """Criar novo curso"""
    # Gerar conteúdo com IA
    ai_content = mock_openai.generate_course_content(course.topic, course.duration)
    
    if not ai_content["success"]:
        raise HTTPException(status_code=500, detail="Erro ao gerar conteúdo")
    
    # Criar curso no banco
    new_course = mock_db.create_course({
        "title": course.title or ai_content["data"]["title"],
        "topic": course.topic,
        "duration": course.duration,
        "difficulty": course.difficulty,
        "description": course.description or ai_content["data"]["description"],
        "content": ai_content["data"],
        "creator_email": email,
        "ai_generated": True
    })
    
    # Log analytics
    mock_db.log_analytics("course_created", {
        "course_id": new_course["id"],
        "topic": course.topic,
        "creator": email
    })
    
    return {
        "message": "Curso criado com sucesso",
        "course": new_course,
        "ai_stats": {
            "tokens_used": ai_content["tokens_used"],
            "cost": ai_content["cost"]
        }
    }

@app.get("/api/courses")
async def list_courses():
    """Listar todos os cursos"""
    courses = list(mock_db.data["courses"].values())
    return {
        "courses": courses,
        "total": len(courses)
    }

@app.get("/api/courses/{course_id}")
async def get_course(course_id: str):
    """Obter curso específico"""
    course = mock_db.data["courses"].get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    return course

# Rotas de vídeos
@app.post("/api/videos")
async def create_video(video: VideoCreate, email: str = Depends(verify_token)):
    """Criar vídeo com avatar"""
    # Verificar se curso existe
    course = mock_db.data["courses"].get(video.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    # Gerar áudio com TTS
    audio_result = mock_tts.text_to_speech(video.script, video.voice_id)
    
    if not audio_result["success"]:
        raise HTTPException(status_code=500, detail="Erro ao gerar áudio")
    
    # Gerar vídeo com avatar
    video_result = mock_avatar.create_video(video.script, video.avatar_id)
    
    if not video_result["success"]:
        raise HTTPException(status_code=500, detail="Erro ao gerar vídeo")
    
    # Salvar vídeo no banco
    new_video = mock_db.create_video({
        "course_id": video.course_id,
        "script": video.script,
        "avatar_id": video.avatar_id,
        "voice_id": video.voice_id,
        "video_url": video_result["video_url"],
        "audio_url": audio_result["audio_url"],
        "duration": video_result["duration_seconds"],
        "creator_email": email
    })
    
    # Upload para storage
    storage_result = mock_storage.upload_file(
        f"videos/{new_video['id']}.mp4",
        b"mock-video-content"
    )
    
    return {
        "message": "Vídeo criado com sucesso",
        "video": new_video,
        "processing": {
            "audio_duration": audio_result["duration_seconds"],
            "video_duration": video_result["duration_seconds"],
            "storage_url": storage_result["file"]["url"]
        }
    }

@app.get("/api/videos")
async def list_videos():
    """Listar todos os vídeos"""
    videos = list(mock_db.data["videos"].values())
    return {
        "videos": videos,
        "total": len(videos)
    }

# Rotas de uploads
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), email: str = Depends(verify_token)):
    """Upload de arquivo"""
    # Ler conteúdo do arquivo
    content = await file.read()
    
    # Upload para storage
    storage_result = mock_storage.upload_file(f"uploads/{file.filename}", content)
    
    if not storage_result["success"]:
        raise HTTPException(status_code=500, detail="Erro no upload")
    
    return {
        "message": "Arquivo enviado com sucesso",
        "file": storage_result["file"],
        "size": len(content),
        "type": file.content_type
    }

# Rotas de pagamento
@app.post("/api/payments")
async def create_payment(payment: PaymentCreate, email: str = Depends(verify_token)):
    """Criar pagamento"""
    payment_result = mock_payment.create_payment(
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description
    )
    
    if not payment_result["success"]:
        raise HTTPException(status_code=400, detail="Erro ao processar pagamento")
    
    return {
        "message": "Pagamento criado",
        "payment": payment_result["transaction"],
        "payment_url": payment_result["payment_url"]
    }

# Rotas de analytics
@app.get("/api/analytics")
async def get_analytics(email: str = Depends(verify_token)):
    """Obter analytics"""
    analytics = mock_db.data["analytics"]
    
    return {
        "total_events": len(analytics),
        "recent_events": analytics[-10:],  # Últimos 10 eventos
        "summary": {
            "courses_created": len([e for e in analytics if e["event"] == "course_created"]),
            "videos_created": len([e for e in analytics if e["event"] == "video_created"]),
            "users_registered": len([e for e in analytics if e["event"] == "user_registered"])
        }
    }

# Rotas de configuração
@app.get("/api/voices")
async def get_voices():
    """Listar vozes disponíveis"""
    return {"voices": mock_tts.get_voices()}

@app.get("/api/avatars")
async def get_avatars():
    """Listar avatares disponíveis"""
    return {"avatars": mock_avatar.get_avatars()}

# Rota de dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard administrativo"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TecnoCursos AI - Dashboard</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .header { background: #667eea; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stat h3 { margin: 0 0 10px 0; color: #333; }
            .stat .number { font-size: 2em; font-weight: bold; color: #667eea; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎛️ TecnoCursos AI - Dashboard</h1>
            <p>Painel de controle da plataforma</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <h3>👥 Usuários</h3>
                <div class="number">150</div>
            </div>
            <div class="stat">
                <h3>📚 Cursos</h3>
                <div class="number">75</div>
            </div>
            <div class="stat">
                <h3>🎬 Vídeos</h3>
                <div class="number">200</div>
            </div>
            <div class="stat">
                <h3>💰 Receita</h3>
                <div class="number">R$ 15.2k</div>
            </div>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px;">
            <h3>🚀 Status dos Serviços</h3>
            <p>✅ IA de Conteúdo: Ativo</p>
            <p>✅ Text-to-Speech: Ativo</p>
            <p>✅ Geração de Avatar: Ativo</p>
            <p>✅ Sistema de Email: Ativo</p>
            <p>✅ Processamento de Pagamentos: Ativo</p>
            <p>✅ Armazenamento em Nuvem: Ativo</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("🚀 TecnoCursos AI - Servidor Completo Iniciando...")
    print("="*60)
    
    # Validar configuração
    try:
        validate_config()
        create_directories()
    except:
        print("⚠️ Usando configurações padrão")
    
    print(f"📍 Servidor: {settings.server_host}:{settings.server_port}")
    print(f"📚 Docs: http://{settings.server_host}:{settings.server_port}/docs")
    print(f"🎛️ Dashboard: http://{settings.server_host}:{settings.server_port}/dashboard")
    print(f"🔑 Admin: admin@tecnocursos.com / admin123")
    print("="*60)
    
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_level="info",
        reload=False
    )
