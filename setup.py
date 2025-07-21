#!/usr/bin/env python3
"""
Script de Setup Automático - TecnoCursosAI
Configura automaticamente o ambiente de desenvolvimento
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

class Colors:
    """Cores para output colorido"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_colored(message, color=Colors.WHITE):
    """Imprimir mensagem colorida"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(title):
    """Imprimir cabeçalho decorado"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored(f"🚀 {title}", Colors.BOLD + Colors.CYAN)
    print_colored("="*60 + "\n", Colors.CYAN)

def check_python_version():
    """Verificar versão do Python"""
    print_colored("🔍 Verificando versão do Python...", Colors.BLUE)
    
    if sys.version_info < (3, 8):
        print_colored("❌ Erro: Python 3.8+ é necessário!", Colors.RED)
        print_colored(f"Versão atual: {sys.version}", Colors.YELLOW)
        sys.exit(1)
    
    print_colored(f"✅ Python {sys.version.split()[0]} - OK!", Colors.GREEN)

def check_dependencies():
    """Verificar dependências do sistema"""
    print_colored("🔍 Verificando dependências...", Colors.BLUE)
    
    # Verificar se pip está disponível
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print_colored("✅ pip - OK!", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_colored("❌ pip não encontrado!", Colors.RED)
        sys.exit(1)

def create_virtual_environment():
    """Criar ambiente virtual"""
    print_colored("🏗️ Criando ambiente virtual...", Colors.BLUE)
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_colored("⚠️ Ambiente virtual já existe!", Colors.YELLOW)
        response = input("Deseja recriá-lo? (s/N): ").lower()
        if response == 's':
            shutil.rmtree(venv_path)
        else:
            print_colored("✅ Usando ambiente virtual existente", Colors.GREEN)
            return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_colored("✅ Ambiente virtual criado!", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_colored("❌ Erro ao criar ambiente virtual!", Colors.RED)
        sys.exit(1)

def install_dependencies():
    """Instalar dependências"""
    print_colored("📦 Instalando dependências...", Colors.BLUE)
    
    # Determinar caminho do pip no venv
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # Linux/Mac
        pip_path = Path("venv/bin/pip")
    
    try:
        # Atualizar pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # Instalar dependências
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        
        print_colored("✅ Dependências instaladas!", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_colored("❌ Erro ao instalar dependências!", Colors.RED)
        print_colored("Tentando instalação alternativa...", Colors.YELLOW)
        
        # Tentar com python -m pip
        try:
            if os.name == 'nt':
                python_path = "venv/Scripts/python"
            else:
                python_path = "venv/bin/python"
            
            subprocess.run([python_path, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print_colored("✅ Dependências instaladas (método alternativo)!", Colors.GREEN)
        except subprocess.CalledProcessError:
            print_colored("❌ Falha na instalação das dependências!", Colors.RED)
            sys.exit(1)

def create_directories():
    """Criar estrutura de diretórios"""
    print_colored("📁 Criando estrutura de diretórios...", Colors.BLUE)
    
    directories = [
        "app/static/uploads/pdf",
        "app/static/uploads/pptx", 
        "app/static/videos/processed",
        "app/static/thumbnails/videos",
        "logs",
        "tests",
        "alembic/versions"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_colored(f"✅ Criado: {directory}", Colors.GREEN)

def setup_environment_file():
    """Configurar arquivo de ambiente"""
    print_colored("⚙️ Configurando arquivo de ambiente...", Colors.BLUE)
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print_colored("✅ Arquivo .env criado a partir do exemplo!", Colors.GREEN)
        print_colored("⚠️ Configure as variáveis em .env conforme necessário", Colors.YELLOW)
    elif env_file.exists():
        print_colored("ℹ️ Arquivo .env já existe", Colors.BLUE)
    else:
        print_colored("⚠️ Arquivo env.example não encontrado", Colors.YELLOW)

def test_database_connection():
    """Testar conexão com banco de dados"""
    print_colored("🗄️ Testando conexão com banco de dados...", Colors.BLUE)
    
    try:
        # Importar e testar database
        sys.path.insert(0, str(Path.cwd()))
        from app.database import test_connection, create_database_if_not_exists
        
        # Tentar criar banco se não existir
        if create_database_if_not_exists():
            print_colored("✅ Banco de dados configurado!", Colors.GREEN)
        
        # Testar conexão
        if test_connection():
            print_colored("✅ Conexão com banco de dados OK!", Colors.GREEN)
        else:
            print_colored("⚠️ Problema na conexão com banco de dados", Colors.YELLOW)
            print_colored("Verifique se o XAMPP/MySQL está rodando", Colors.YELLOW)
            
    except Exception as e:
        print_colored(f"⚠️ Erro ao testar banco: {e}", Colors.YELLOW)
        print_colored("Configure o MySQL manualmente", Colors.YELLOW)

def initialize_database():
    """Inicializar tabelas do banco"""
    print_colored("🗃️ Inicializando tabelas do banco...", Colors.BLUE)
    
    try:
        from app.database import init_database
        from app.models import create_sample_data, SessionLocal
        
        # Criar tabelas
        init_database()
        
        # Criar dados de exemplo
        db = SessionLocal()
        create_sample_data(db)
        db.close()
        
        print_colored("✅ Banco de dados inicializado!", Colors.GREEN)
        
    except Exception as e:
        print_colored(f"⚠️ Erro na inicialização: {e}", Colors.YELLOW)

def test_application():
    """Testar aplicação"""
    print_colored("🧪 Testando aplicação...", Colors.BLUE)
    
    try:
        # Testar imports principais
        from app.main import app
        from app import models, schemas, utils
        
        print_colored("✅ Todos os módulos importados com sucesso!", Colors.GREEN)
        
        # Testar utilitários
        from app.utils import test_utils
        test_utils()
        
        print_colored("✅ Testes básicos passaram!", Colors.GREEN)
        
    except Exception as e:
        print_colored(f"⚠️ Erro nos testes: {e}", Colors.YELLOW)

def show_next_steps():
    """Mostrar próximos passos"""
    print_header("CONFIGURAÇÃO CONCLUÍDA! 🎉")
    
    print_colored("📋 PRÓXIMOS PASSOS:", Colors.BOLD + Colors.CYAN)
    print_colored("\n1. Configure o MySQL no XAMPP:", Colors.WHITE)
    print_colored("   - Abra o painel do XAMPP", Colors.YELLOW)
    print_colored("   - Inicie Apache e MySQL", Colors.YELLOW)
    print_colored("   - Acesse phpMyAdmin e crie o banco 'tecnocursosai'", Colors.YELLOW)
    
    print_colored("\n2. Ative o ambiente virtual:", Colors.WHITE)
    if os.name == 'nt':
        print_colored("   venv\\Scripts\\activate", Colors.GREEN)
    else:
        print_colored("   source venv/bin/activate", Colors.GREEN)
    
    print_colored("\n3. Execute o servidor:", Colors.WHITE)
    print_colored("   uvicorn app.main:app --reload", Colors.GREEN)
    
    print_colored("\n4. Acesse a documentação:", Colors.WHITE)
    print_colored("   http://localhost:8000/docs", Colors.BLUE)
    
    print_colored("\n5. Configure variáveis em .env conforme necessário", Colors.WHITE)
    
    print_colored(f"\n🚀 {Colors.BOLD}TecnoCursosAI está pronto para uso!{Colors.ENDC}", Colors.GREEN)

def main():
    """Função principal do setup"""
    print_header("SETUP AUTOMÁTICO - TECNOCURSOSAI")
    
    print_colored("🎯 Configurando ambiente de desenvolvimento...\n", Colors.BLUE)
    
    # Executar verificações e configurações
    check_python_version()
    check_dependencies()
    create_virtual_environment()
    install_dependencies()
    create_directories()
    setup_environment_file()
    
    print_colored("\n⏳ Aguarde, finalizando configurações...", Colors.BLUE)
    time.sleep(2)
    
    test_database_connection()
    initialize_database()
    test_application()
    
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n❌ Setup interrompido pelo usuário", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Erro durante setup: {e}", Colors.RED)
        sys.exit(1) 