#!/usr/bin/env python3
import subprocess
import sys
import os

print("🚀 TecnoCursos AI - Iniciador Direto")
print("="*50)

# Verificar dependências
print("📦 Instalando dependências...")
dependencies = ["fastapi", "uvicorn", "python-multipart", "pyjwt"]

for dep in dependencies:
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                      capture_output=True, check=True)
        print(f"✅ {dep}")
    except:
        print(f"⚠️ {dep}")

print("\n🌐 Iniciando servidor...")
print("📍 URL: http://localhost:8000")
print("📚 Docs: http://localhost:8000/docs")
print("❤️ Health: http://localhost:8000/health")
print("\n🔑 Credenciais:")
print("Email: admin@tecnocursos.com")
print("Senha: admin123")
print("="*50)

# Iniciar servidor
try:
    import uvicorn
    from simple_backend import app
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )
except Exception as e:
    print(f"❌ Erro: {e}")
    input("Pressione Enter para sair...")
