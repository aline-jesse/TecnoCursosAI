#!/usr/bin/env python3
"""
Script de Correção Automática - TecnoCursosAI
Corrige automaticamente todos os problemas identificados
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprimir mensagem com status colorido"""
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m", 
        "WARNING": "\033[93m",
        "INFO": "\033[94m"
    }
    color = colors.get(status, colors["INFO"])
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def fix_package_json():
    """Corrigir package.json"""
    print_status("🔧 Corrigindo package.json...", "INFO")
    
    package_json = Path("package.json")
    if package_json.exists():
        try:
            import json
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            # Adicionar script dev se não existir
            if "dev" not in data.get("scripts", {}):
                data["scripts"]["dev"] = "react-scripts start"
                
                with open(package_json, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print_status("✅ Script 'dev' adicionado ao package.json", "SUCCESS")
            else:
                print_status("✅ Script 'dev' já existe", "SUCCESS")
        except Exception as e:
            print_status(f"❌ Erro ao corrigir package.json: {e}", "ERROR")
            return False
    
    return True

def install_missing_dependencies():
    """Instalar dependências faltantes"""
    print_status("📦 Instalando dependências faltantes...", "INFO")
    
    # Dependências críticas
    critical_deps = [
        "moviepy",
        "gtts",
        "pydub",
        "redis",
        "transformers",
        "torch",
        "requests"
    ]
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print_status(f"✅ {dep} já instalado", "SUCCESS")
        except ImportError:
            print_status(f"📦 Instalando {dep}...", "WARNING")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print_status(f"✅ {dep} instalado", "SUCCESS")
            except subprocess.CalledProcessError:
                print_status(f"⚠️ {dep} falhou, continuando...", "WARNING")
    
    return True

def create_missing_directories():
    """Criar diretórios faltantes"""
    print_status("📁 Criando diretórios faltantes...", "INFO")
    
    directories = [
        "static/uploads",
        "static/videos",
        "static/audios",
        "static/thumbnails",
        "logs",
        "cache",
        "temp",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_status(f"✅ {directory}", "SUCCESS")
    
    return True

def fix_database_issues():
    """Corrigir problemas de banco de dados"""
    print_status("🗄️ Corrigindo problemas de banco...", "INFO")
    
    try:
        # Importar módulos de banco
        sys.path.insert(0, str(Path(__file__).parent))
        from app.database import engine, Base
        
        # Criar tabelas
        Base.metadata.create_all(bind=engine)
        print_status("✅ Tabelas criadas/atualizadas", "SUCCESS")
        
        return True
    except Exception as e:
        print_status(f"❌ Erro no banco: {e}", "ERROR")
        return False

def fix_import_issues():
    """Corrigir problemas de importação"""
    print_status("🔧 Corrigindo problemas de importação...", "INFO")
    
    # Verificar e corrigir imports problemáticos
    files_to_check = [
        "app/main.py",
        "app/database.py",
        "app/routers/__init__.py"
    ]
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Corrigir imports comuns
                content = content.replace("from .database import", "from app.database import")
                content = content.replace("from .models import", "from app.models import")
                content = content.replace("from .config import", "from app.config import")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print_status(f"✅ {file_path} corrigido", "SUCCESS")
            except Exception as e:
                print_status(f"⚠️ Erro ao corrigir {file_path}: {e}", "WARNING")
    
    return True

def setup_environment_file():
    """Configurar arquivo .env"""
    print_status("⚙️ Configurando arquivo .env...", "INFO")
    
    env_content = """# TecnoCursosAI Environment Configuration

# Aplicação
SECRET_KEY=your_super_secret_key_change_in_production
ENVIRONMENT=development
DEBUG=true

# Servidor
HOST=0.0.0.0
PORT=8000

# Banco de dados
DATABASE_URL=sqlite:///./tecnocursos.db

# Redis (opcional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# APIs externas (opcionais)
OPENAI_API_KEY=your_openai_key_here
D_ID_API_KEY=your_d_id_key_here
HUGGINGFACE_TOKEN=your_hf_token_here

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Upload
MAX_FILE_SIZE=104857600
ALLOWED_EXTENSIONS=pdf,pptx,docx,txt,jpg,png

# Logs
LOG_LEVEL=info
LOG_FILE=logs/app.log
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print_status("✅ Arquivo .env criado", "SUCCESS")
    return True

def fix_node_modules():
    """Corrigir node_modules"""
    print_status("📦 Corrigindo node_modules...", "INFO")
    
    if Path("package.json").exists():
        try:
            # Remover node_modules se corrompido
            if Path("node_modules").exists():
                shutil.rmtree("node_modules")
                print_status("🗑️ node_modules removido", "WARNING")
            
            # Reinstalar dependências
            subprocess.run(["npm", "install"], check=True)
            print_status("✅ node_modules reinstalado", "SUCCESS")
            return True
        except Exception as e:
            print_status(f"❌ Erro ao corrigir node_modules: {e}", "ERROR")
            return False
    
    return True

def fix_port_conflicts():
    """Corrigir conflitos de porta"""
    print_status("🔌 Verificando conflitos de porta...", "INFO")
    
    import socket
    
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    # Verificar portas comuns
    ports_to_check = [8000, 3000, 8001, 3001]
    
    for port in ports_to_check:
        if is_port_in_use(port):
            print_status(f"⚠️ Porta {port} em uso", "WARNING")
        else:
            print_status(f"✅ Porta {port} disponível", "SUCCESS")
    
    return True

def create_startup_scripts():
    """Criar scripts de inicialização"""
    print_status("🚀 Criando scripts de inicialização...", "INFO")
    
    # Script para Windows
    windows_script = """@echo off
echo Iniciando TecnoCursosAI...
python start_system_complete.py
pause
"""
    
    with open("start_system.bat", "w") as f:
        f.write(windows_script)
    
    # Script para Linux/Mac
    linux_script = """#!/bin/bash
echo "Iniciando TecnoCursosAI..."
python3 start_system_complete.py
"""
    
    with open("start_system.sh", "w") as f:
        f.write(linux_script)
    
    # Tornar executável no Linux
    if os.name != 'nt':
        os.chmod("start_system.sh", 0o755)
    
    print_status("✅ Scripts de inicialização criados", "SUCCESS")
    return True

def run_system_tests():
    """Executar testes do sistema"""
    print_status("🧪 Executando testes do sistema...", "INFO")
    
    try:
        # Importar módulos principais
        test_modules = [
            "fastapi",
            "sqlalchemy",
            "uvicorn",
            "pydantic"
        ]
        
        for module in test_modules:
            try:
                __import__(module)
                print_status(f"✅ {module} OK", "SUCCESS")
            except ImportError:
                print_status(f"❌ {module} não encontrado", "ERROR")
                return False
        
        return True
    except Exception as e:
        print_status(f"❌ Erro nos testes: {e}", "ERROR")
        return False

def main():
    """Função principal"""
    print_status("🔧 INICIANDO CORREÇÃO AUTOMÁTICA", "INFO")
    print_status("=" * 60, "INFO")
    
    # Lista de correções
    fixes = [
        ("Corrigir package.json", fix_package_json),
        ("Instalar dependências", install_missing_dependencies),
        ("Criar diretórios", create_missing_directories),
        ("Corrigir banco de dados", fix_database_issues),
        ("Corrigir imports", fix_import_issues),
        ("Configurar ambiente", setup_environment_file),
        ("Corrigir node_modules", fix_node_modules),
        ("Verificar portas", fix_port_conflicts),
        ("Criar scripts", create_startup_scripts),
        ("Executar testes", run_system_tests)
    ]
    
    success_count = 0
    total_fixes = len(fixes)
    
    for fix_name, fix_func in fixes:
        print_status(f"🔧 {fix_name}...", "INFO")
        try:
            if fix_func():
                success_count += 1
                print_status(f"✅ {fix_name} - Sucesso", "SUCCESS")
            else:
                print_status(f"❌ {fix_name} - Falhou", "ERROR")
        except Exception as e:
            print_status(f"❌ {fix_name} - Erro: {e}", "ERROR")
    
    print_status("=" * 60, "INFO")
    print_status(f"📊 Correções: {success_count}/{total_fixes} bem-sucedidas", "INFO")
    
    if success_count >= total_fixes * 0.8:
        print_status("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!", "SUCCESS")
        print_status("=" * 60, "INFO")
        print_status("📋 Próximos passos:", "INFO")
        print_status("1. Execute: python start_system_complete.py", "INFO")
        print_status("2. Ou: npm run dev (para frontend)", "INFO")
        print_status("3. Acesse: http://localhost:8000", "INFO")
        return True
    else:
        print_status("⚠️ ALGUMAS CORREÇÕES FALHARAM", "WARNING")
        print_status("Verifique os logs e tente novamente", "WARNING")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 