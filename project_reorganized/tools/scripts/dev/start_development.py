#!/usr/bin/env python3
"""
Script de inicialização para desenvolvimento - TecnoCursos AI
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """Configurar logging básico"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_requirements():
    """Verificar se as dependências estão instaladas"""
    logger = logging.getLogger(__name__)
    
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        logger.info("✅ Dependências principais verificadas")
        return True
    except ImportError as e:
        logger.error(f"❌ Dependência faltando: {e}")
        logger.info("💡 Execute: pip install -r backend/requirements.txt")
        return False

def setup_environment():
    """Configurar variáveis de ambiente para desenvolvimento"""
    env_vars = {
        "DEBUG": "true",
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "HOST": "localhost",
        "PORT": "8000",
        "DATABASE_URL": "sqlite:///./data/tecnocursos_dev.db"
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

def create_directories():
    """Criar diretórios necessários"""
    directories = [
        "data",
        "logs", 
        "static/uploads",
        "static/videos",
        "static/audios",
        "static/thumbnails"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def start_backend():
    """Iniciar o servidor backend"""
    logger = logging.getLogger(__name__)
    
    # Mudar para o diretório do backend
    backend_dir = Path(__file__).parent.parent.parent.parent / "backend"
    os.chdir(backend_dir)
    
    logger.info("🚀 Iniciando TecnoCursos AI Backend...")
    
    try:
        # Executar o servidor
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "localhost",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("👋 Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🎯 TecnoCursos AI - Inicialização para Desenvolvimento")
    logger.info("=" * 60)
    
    # Verificações
    if not check_requirements():
        sys.exit(1)
    
    # Setup
    setup_environment()
    create_directories()
    
    # Iniciar servidor
    start_backend()

if __name__ == "__main__":
    main() 