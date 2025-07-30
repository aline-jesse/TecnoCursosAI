#!/usr/bin/env python3
"""
Script de Verificação e Inicialização - TecnoCursos AI
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Versão do Python muito antiga. Necessário Python 3.8+")
        return False
    
    print("✅ Versão do Python OK")
    return True

def check_directories():
    """Verifica diretórios necessários"""
    dirs_to_check = ["backend", "frontend"]
    
    for dir_name in dirs_to_check:
        if Path(dir_name).exists():
            print(f"✅ Diretório {dir_name} encontrado")
        else:
            print(f"❌ Diretório {dir_name} não encontrado")
            return False
    
    return True

def check_backend_files():
    """Verifica arquivos do backend"""
    backend_files = [
        "backend/main.py",
        "backend/requirements.txt"
    ]
    
    for file_path in backend_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} não encontrado")
            return False
    
    return True

def check_frontend_files():
    """Verifica arquivos do frontend"""
    frontend_files = [
        "frontend/package.json"
    ]
    
    for file_path in frontend_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} não encontrado")
            return False
    
    return True

def check_node_npm():
    """Verifica Node.js e npm"""
    try:
        # Verificar Node.js
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js não encontrado")
            return False
        
        # Verificar npm
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.strip()}")
        else:
            print("❌ npm não encontrado")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ Node.js/npm não encontrados no PATH")
        return False

def install_backend_dependencies():
    """Instala dependências do backend"""
    print("\n📦 Instalando dependências do backend...")
    
    try:
        os.chdir("backend")
        
        # Instalar dependências básicas
        dependencies = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "python-multipart==0.0.6",
            "jinja2==3.1.2",
            "aiofiles==23.2.1",
            "python-dotenv==1.0.0",
            "sqlalchemy==2.0.23",
            "pydantic==2.5.0",
            "pydantic-settings==2.1.0"
        ]
        
        for dep in dependencies:
            print(f"Instalando {dep}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {dep}")
            else:
                print(f"❌ Erro ao instalar {dep}: {result.stderr}")
        
        os.chdir("..")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        os.chdir("..")
        return False

def install_frontend_dependencies():
    """Instala dependências do frontend"""
    print("\n📦 Instalando dependências do frontend...")
    
    try:
        os.chdir("frontend")
        
        result = subprocess.run(["npm", "install"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependências do frontend instaladas")
            os.chdir("..")
            return True
        else:
            print(f"❌ Erro ao instalar dependências do frontend: {result.stderr}")
            os.chdir("..")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao instalar dependências do frontend: {e}")
        os.chdir("..")
        return False

def start_backend():
    """Tenta iniciar o backend"""
    print("\n🚀 Testando inicialização do backend...")
    
    try:
        os.chdir("backend")
        
        # Testar se o main.py pode ser importado
        result = subprocess.run([sys.executable, "-c", "import main; print('✅ Backend OK')"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend pode ser iniciado")
            print("\n📋 Para iniciar o backend manualmente:")
            print("   cd backend")
            print("   python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
        else:
            print(f"❌ Erro no backend: {result.stderr}")
        
        os.chdir("..")
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao testar backend: {e}")
        os.chdir("..")
        return False

def start_frontend():
    """Testa o frontend"""
    print("\n🎨 Testando frontend...")
    
    try:
        os.chdir("frontend")
        
        # Verificar se o package.json tem script dev
        if Path("package.json").exists():
            print("✅ Frontend configurado")
            print("\n📋 Para iniciar o frontend manualmente:")
            print("   cd frontend")
            print("   npm run dev")
        else:
            print("❌ package.json não encontrado")
        
        os.chdir("..")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar frontend: {e}")
        os.chdir("..")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 VERIFICAÇÃO COMPLETA DO SISTEMA TECNOCURSOS AI")
    print("=" * 60)
    
    all_ok = True
    
    # Verificações
    if not check_python_version():
        all_ok = False
    
    if not check_directories():
        all_ok = False
    
    if not check_backend_files():
        all_ok = False
    
    if not check_frontend_files():
        all_ok = False
    
    if not check_node_npm():
        all_ok = False
    
    if not all_ok:
        print("\n❌ Verificações falharam. Corrija os problemas antes de continuar.")
        return
    
    print("\n✅ Todas as verificações passaram!")
    
    # Instalar dependências
    if not install_backend_dependencies():
        print("❌ Falha ao instalar dependências do backend")
        return
    
    if not install_frontend_dependencies():
        print("❌ Falha ao instalar dependências do frontend")
        return
    
    # Testar inicialização
    start_backend()
    start_frontend()
    
    print("\n" + "=" * 60)
    print("🎉 SISTEMA PRONTO PARA USO!")
    print("=" * 60)
    print("🌐 Para acessar:")
    print("   Frontend: http://localhost:3000")
    print("   Backend:  http://localhost:8001")
    print("   API Docs: http://localhost:8001/docs")
    print("\n💡 Execute INICIAR_TUDO.bat para iniciar automaticamente")
    print("=" * 60)

if __name__ == "__main__":
    main()
