#!/usr/bin/env python3
"""
Inicializador Simples TecnoCursos AI
"""

import subprocess
import time
import os
import sys
from pathlib import Path

def run_command(command, cwd=None, background=False):
    """Executa um comando"""
    try:
        if background:
            if os.name == 'nt':  # Windows
                subprocess.Popen(command, shell=True, cwd=cwd, 
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix/Linux
                subprocess.Popen(command, shell=True, cwd=cwd)
        else:
            result = subprocess.run(command, shell=True, cwd=cwd, 
                                  capture_output=True, text=True)
            return result
    except Exception as e:
        print(f"Erro ao executar comando: {e}")
        return None

def main():
    print("🚀 INICIALIZANDO TECNOCURSOS AI")
    print("=" * 40)
    
    # Verificar se estamos no diretório correto
    root_dir = Path.cwd()
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"
    
    if not backend_dir.exists() or not frontend_dir.exists():
        print("❌ Execute este script do diretório raiz do projeto")
        return
    
    print("📁 Diretórios encontrados:")
    print(f"   Backend: {backend_dir}")
    print(f"   Frontend: {frontend_dir}")
    
    # 1. Verificar e ativar ambiente virtual do backend
    print("\n🐍 Configurando Backend...")
    
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("   Criando ambiente virtual...")
        run_command("python -m venv venv", cwd=backend_dir)
    
    # Instalar dependências
    print("   Instalando dependências...")
    if os.name == 'nt':
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    deps = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
        "python-multipart", "jinja2", "aiofiles", 
        "pydantic-settings", "python-dotenv", 
        "python-jose[cryptography]", "passlib[bcrypt]", 
        "email-validator", "requests"
    ]
    
    for dep in deps:
        print(f"   Instalando {dep}...")
        run_command(f"{pip_cmd} install {dep}", cwd=backend_dir)
    
    # 2. Iniciar Backend
    print("\n🔧 Iniciando Backend...")
    backend_cmd = f"{python_cmd} -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
    run_command(backend_cmd, cwd=backend_dir, background=True)
    
    print("   ⏳ Aguardando backend inicializar...")
    time.sleep(5)
    
    # 3. Configurar Frontend
    print("\n🎨 Configurando Frontend...")
    
    # Verificar se node_modules existe
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("   Instalando dependências do frontend...")
        run_command("npm install", cwd=frontend_dir)
    
    # 4. Iniciar Frontend
    print("\n🌐 Iniciando Frontend...")
    frontend_cmd = "npm run dev"
    run_command(frontend_cmd, cwd=frontend_dir, background=True)
    
    print("   ⏳ Aguardando frontend inicializar...")
    time.sleep(3)
    
    # 5. Verificar serviços
    print("\n✅ SERVIÇOS INICIADOS!")
    print("=" * 30)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend:  http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print("❤️ Health:   http://localhost:8001/health")
    
    print("\n💡 Para parar os serviços:")
    print("   - Feche as janelas de terminal abertas")
    print("   - Ou use Ctrl+C nos processos")
    
    print("\n🎉 TecnoCursos AI está rodando!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Inicialização cancelada")
    except Exception as e:
        print(f"\n❌ Erro durante inicialização: {e}")
        sys.exit(1)
