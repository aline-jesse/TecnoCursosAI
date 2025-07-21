#!/usr/bin/env python3
"""
Script de Instalação Completa - TecnoCursosAI
Instala todas as dependências necessárias para o sistema completo
"""

import subprocess
import sys
import os
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

def run_command(command, description):
    """Executar comando e mostrar resultado"""
    print_status(f"Executando: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print_status(f"✅ {description} - Sucesso", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"❌ {description} - Erro: {e.stderr}", "ERROR")
        return False

def install_python_dependencies():
    """Instalar dependências Python"""
    print_status("📦 Instalando dependências Python...", "INFO")
    
    # Dependências básicas
    basic_deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "sqlalchemy==2.0.23",
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "aiofiles==23.2.1",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "bcrypt==4.0.1",
        "cryptography==41.0.7"
    ]
    
    for dep in basic_deps:
        if not run_command(f"pip install {dep}", f"Instalando {dep}"):
            return False
    
    # Dependências de processamento de documentos
    doc_deps = [
        "PyPDF2==3.0.1",
        "PyMuPDF==1.23.8", 
        "python-pptx==0.6.23",
        "python-docx==1.1.0",
        "openpyxl==3.1.2"
    ]
    
    for dep in doc_deps:
        if not run_command(f"pip install {dep}", f"Instalando {dep}"):
            return False
    
    # Dependências de mídia
    media_deps = [
        "moviepy==1.0.3",
        "opencv-python==4.8.1.78",
        "Pillow==10.1.0",
        "numpy==1.24.4"
    ]
    
    for dep in media_deps:
        if not run_command(f"pip install {dep}", f"Instalando {dep}"):
            return False
    
    # Dependências TTS completas
    tts_deps = [
        "gtts==2.4.0",
        "pydub==0.25.1",
        "scipy==1.11.4",
        "librosa==0.10.1",
        "soundfile==0.12.1"
    ]
    
    for dep in tts_deps:
        if not run_command(f"pip install {dep}", f"Instalando {dep}"):
            return False
    
    # Dependências de IA (opcionais mas recomendadas)
    ai_deps = [
        "openai==1.3.7",
        "transformers==4.35.2",
        "torch==2.1.1",
        "torchaudio==2.1.1",
        "sentence-transformers==2.2.2",
        "faiss-cpu==1.7.4"
    ]
    
    print_status("🤖 Instalando dependências de IA (pode demorar)...", "WARNING")
    for dep in ai_deps:
        if not run_command(f"pip install {dep}", f"Instalando {dep}"):
            print_status(f"⚠️ {dep} falhou, continuando...", "WARNING")
    
    # Dependências de monitoramento
    monitoring_deps = [
        "prometheus-client==0.19.0",
        "psutil==5.9.6",
        "loguru==0.7.2"
    ]
    
    for dep in monitoring_deps:
        if not run_command(f"pip install {dep}", f"Instalando {dep}"):
            return False
    
    return True

def install_node_dependencies():
    """Instalar dependências Node.js"""
    print_status("📦 Instalando dependências Node.js...", "INFO")
    
    if not run_command("npm install", "Instalando dependências npm"):
        return False
    
    return True

def create_directories():
    """Criar diretórios necessários"""
    print_status("📁 Criando diretórios...", "INFO")
    
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
        print_status(f"✅ Criado: {directory}", "SUCCESS")
    
    return True

def setup_environment():
    """Configurar arquivo .env"""
    print_status("⚙️ Configurando ambiente...", "INFO")
    
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

def test_installation():
    """Testar instalação"""
    print_status("🧪 Testando instalação...", "INFO")
    
    # Testar importações Python
    test_imports = [
        "fastapi",
        "sqlalchemy", 
        "moviepy",
        "gtts",
        "openai"
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print_status(f"✅ {module} importado com sucesso", "SUCCESS")
        except ImportError:
            print_status(f"❌ {module} não encontrado", "ERROR")
            return False
    
    return True

def main():
    """Função principal"""
    print_status("🚀 Iniciando instalação completa do TecnoCursosAI...", "INFO")
    print_status("=" * 60, "INFO")
    
    # Criar diretórios
    if not create_directories():
        return False
    
    # Instalar dependências Python
    if not install_python_dependencies():
        return False
    
    # Instalar dependências Node.js
    if not install_node_dependencies():
        return False
    
    # Configurar ambiente
    if not setup_environment():
        return False
    
    # Testar instalação
    if not test_installation():
        return False
    
    print_status("=" * 60, "INFO")
    print_status("🎉 INSTALAÇÃO COMPLETA COM SUCESSO!", "SUCCESS")
    print_status("=" * 60, "INFO")
    print_status("📋 Próximos passos:", "INFO")
    print_status("1. Configure as variáveis no arquivo .env", "INFO")
    print_status("2. Execute: python main.py", "INFO")
    print_status("3. Acesse: http://localhost:8000", "INFO")
    print_status("4. Para frontend: npm run dev", "INFO")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 