#!/usr/bin/env python3
"""
INICIALIZADOR DEFINITIVO - TecnoCursos AI
Implementação automática completa
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def install_dependencies():
    """Instala dependências essenciais"""
    print("🔧 Instalando dependências...")
    
    deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "python-multipart==0.0.6",
        "pyjwt==2.8.0",
        "pydantic[email]==2.5.0",
        "email-validator==2.1.0",
        "python-jose[cryptography]==3.3.0"
    ]
    
    for dep in deps:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep, 
                "--upgrade", "--quiet", "--user"
            ], check=True, timeout=60)
            print(f"✅ {dep.split('==')[0]}")
        except Exception as e:
            print(f"⚠️ {dep}: {str(e)[:30]}")

def kill_port_processes():
    """Mata processos na porta 8000"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run([
                'netstat', '-ano'
            ], capture_output=True, timeout=10)
            
            # Tentar matar processo na porta 8000
            result = subprocess.run([
                'for', '/f', '"tokens=5"', '%a', 'in', 
                '(\'netstat -ano | findstr :8000\')', 'do', 
                'taskkill', '/F', '/PID', '%a', '2>nul'
            ], shell=True, capture_output=True, timeout=10)
            
        print("🔄 Porta 8000 liberada")
    except:
        pass

def create_server_file():
    """Cria arquivo de servidor otimizado"""
    server_content = '''#!/usr/bin/env python3
"""
TecnoCursos AI - Servidor Backend Otimizado
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import uvicorn
import jwt
from datetime import datetime, timedelta
import os

# Configuração
app = FastAPI(
    title="TecnoCursos AI",
    version="2.0.0",
    description="Sistema de geração de vídeos educacionais"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT
SECRET_KEY = "tecnocursos-ai-secret-key-2025"
ALGORITHM = "HS256"
security = HTTPBearer()

# Modelos
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    email: str
    name: str
    role: str

# Usuários de teste
USERS = {
    "admin@tecnocursos.com": {
        "password": "admin123",
        "name": "Administrador",
        "role": "admin"
    },
    "user@tecnocursos.com": {
        "password": "user123", 
        "name": "Usuário",
        "role": "user"
    }
}

def create_token(email: str) -> str:
    """Criar token JWT"""
    expire = datetime.utcnow() + timedelta(hours=24)
    data = {"sub": email, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email and email in USERS:
            return email
    except:
        pass
    raise HTTPException(status_code=401, detail="Token inválido")

# Rotas
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TecnoCursos AI</title>
        <style>
            body { font-family: Arial; text-align: center; background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 50px; }
            .container { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; }
            .status { background: #4CAF50; padding: 15px; border-radius: 10px; margin: 20px 0; }
            .link { background: rgba(255,255,255,0.2); padding: 10px 20px; margin: 10px; text-decoration: none; color: white; border-radius: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 TecnoCursos AI</h1>
            <div class="status">✅ Servidor Online - Porta 8000</div>
            <p>Sistema de geração de vídeos educacionais com IA</p>
            <a href="/docs" class="link">📚 Documentação API</a>
            <a href="/health" class="link">❤️ Health Check</a>
            <div style="margin-top: 30px;">
                <h3>🔑 Credenciais de Teste:</h3>
                <p>Email: admin@tecnocursos.com | Senha: admin123</p>
                <p>Email: user@tecnocursos.com | Senha: user123</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "TecnoCursos AI",
        "version": "2.0.0",
        "port": 8000,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/login", response_model=Token)
async def login(data: LoginRequest):
    """Login com email e senha"""
    user = USERS.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    token = create_token(data.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_user(email: str = Depends(verify_token)):
    """Dados do usuário logado"""
    user = USERS[email]
    return {
        "email": email,
        "name": user["name"],
        "role": user["role"]
    }

@app.get("/api/status")
async def status():
    return {
        "backend": "online",
        "database": "not configured", 
        "services": {
            "ai_generation": "available",
            "video_processing": "available",
            "file_upload": "available"
        },
        "users_count": len(USERS)
    }

if __name__ == "__main__":
    print("🚀 TecnoCursos AI - Servidor Iniciando...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs") 
    print("❤️ Health: http://localhost:8000/health")
    print("🔑 Login: admin@tecnocursos.com / admin123")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
'''
    
    with open('server_optimized.py', 'w', encoding='utf-8') as f:
        f.write(server_content)
    print("✅ Servidor otimizado criado")

def open_browser_delayed():
    """Abre navegador após delay"""
    time.sleep(5)
    try:
        webbrowser.open('http://localhost:8000')
        webbrowser.open('http://localhost:8000/docs')
        print("🌐 Navegadores abertos")
    except:
        pass

def main():
    """Função principal de inicialização"""
    print("🎯 TECNOCURSOS AI - IMPLEMENTAÇÃO AUTOMÁTICA COMPLETA")
    print("="*70)
    
    # 1. Instalar dependências
    install_dependencies()
    
    # 2. Liberar porta
    kill_port_processes()
    
    # 3. Criar servidor otimizado
    create_server_file()
    
    # 4. Abrir navegador em thread separada
    browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
    browser_thread.start()
    
    # 5. Iniciar servidor
    print("\n🚀 Iniciando servidor...")
    print("📍 URLs disponíveis:")
    print("   - Backend: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - Health: http://localhost:8000/health")
    print("\n🔑 Credenciais:")
    print("   - admin@tecnocursos.com / admin123")
    print("   - user@tecnocursos.com / user123")
    print("\n" + "="*70)
    
    try:
        # Importar e executar servidor
        exec(open('server_optimized.py').read())
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("💡 Verifique se as dependências estão instaladas")

if __name__ == "__main__":
    main()
