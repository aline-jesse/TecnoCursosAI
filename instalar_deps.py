#!/usr/bin/env python3
"""
Instalação de Dependências - TecnoCursos AI
"""

import subprocess
import sys
import os

def install_backend_deps():
    """Instala dependências do backend"""
    print("📦 Instalando dependências do backend...")
    
    deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "python-multipart==0.0.6",
        "jinja2==3.1.2",
        "aiofiles==23.2.1",
        "python-dotenv==1.0.0",
        "sqlalchemy==2.0.23",
        "pydantic==2.5.0",
        "requests>=2.25.0",
        "psutil>=5.8.0"
    ]
    
    for dep in deps:
        print(f"Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {dep}")

def main():
    print("🚀 Instalando todas as dependências...")
    install_backend_deps()
    print("✅ Instalação concluída!")

if __name__ == "__main__":
    main()
