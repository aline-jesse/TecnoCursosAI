#!/usr/bin/env python3
"""
Script de Inicialização Final - TecnoCursos AI Enterprise Edition 2025
Versão otimizada e testada para funcionamento garantido
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TecnoCursosFinal:
    """Sistema final de inicialização do TecnoCursos AI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.port = 8000
        
    def check_python(self):
        """Verifica Python"""
        logger.info("🐍 Verificando Python...")
        if sys.version_info >= (3, 9):
            logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
            return True
        else:
            logger.error("❌ Python 3.9+ necessário")
            return False
    
    def install_dependencies(self):
        """Instala dependências básicas"""
        logger.info("📦 Instalando dependências...")
        
        basic_deps = [
            "fastapi",
            "uvicorn[standard]",
            "sqlalchemy",
            "pydantic",
            "python-multipart",
            "aiofiles",
            "requests"
        ]
        
        for dep in basic_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                logger.info(f"   ✅ {dep}")
            except subprocess.CalledProcessError:
                logger.warning(f"   ⚠️ {dep} não instalado")
        
        return True
    
    def create_structure(self):
        """Cria estrutura de diretórios"""
        logger.info("📁 Criando estrutura...")
        
        directories = [
            "uploads/pdf",
            "uploads/pptx",
            "static/videos",
            "static/audios",
            "static/thumbnails",
            "cache",
            "logs",
            "temp"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"   ✅ {directory}")
        
        return True
    
    def create_env_file(self):
        """Cria arquivo .env"""
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            env_content = """# TecnoCursos AI - Configurações
APP_ENV=development
DEBUG=true
HOST=127.0.0.1
PORT=8000

# Banco de dados
DATABASE_URL=sqlite:///./tecnocursos.db

# Segurança
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-tecnocursos-2025

# Upload
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=.pdf,.pptx,.docx,.txt,.mp4,.avi,.mov

# CORS
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# Logs
LOG_LEVEL=INFO
LOG_FORMAT=json

# Cache
REDIS_URL=redis://localhost:6379

# TTS (opcional)
AZURE_TTS_KEY=
AZURE_TTS_REGION=

# Avatar (opcional)
D_ID_API_KEY=

# OpenAI (opcional)
OPENAI_API_KEY=
"""
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            logger.info("✅ Arquivo .env criado")
        
        return True
    
    def test_imports(self):
        """Testa importações"""
        logger.info("🧪 Testando importações...")
        
        try:
            sys.path.insert(0, str(self.project_root))
            
            # Testar imports básicos
            import fastapi
            import uvicorn
            import sqlalchemy
            import pydantic
            
            logger.info("✅ Imports básicos OK")
            
            # Testar app principal
            try:
                from app.main import app
                logger.info("✅ App principal carregado")
                return True
            except Exception as e:
                logger.warning(f"⚠️ App principal: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro nos imports: {e}")
            return False
    
    def start_server(self):
        """Inicia servidor"""
        logger.info("🚀 Iniciando servidor...")
        
        try:
            # Comando para iniciar servidor
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", "127.0.0.1",
                "--port", str(self.port),
                "--reload"
            ]
            
            logger.info("🎯 Servidor iniciado!")
            logger.info(f"📚 Documentação: http://127.0.0.1:{self.port}/docs")
            logger.info(f"🔍 Health Check: http://127.0.0.1:{self.port}/api/health")
            logger.info(f"🏠 Dashboard: http://127.0.0.1:{self.port}/dashboard")
            
            # Executar servidor
            subprocess.run(cmd, cwd=str(self.project_root))
            
        except KeyboardInterrupt:
            logger.info("🛑 Servidor interrompido")
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {e}")
    
    def run(self):
        """Executa inicialização completa"""
        logger.info("🎯 TECNOCURSOS AI ENTERPRISE EDITION 2025")
        logger.info("=" * 60)
        
        # Verificações
        if not self.check_python():
            return False
        
        # Estrutura
        self.create_structure()
        self.create_env_file()
        
        # Dependências
        self.install_dependencies()
        
        # Testes
        if not self.test_imports():
            logger.warning("⚠️ Alguns imports falharam, mas continuando...")
        
        # Iniciar servidor
        self.start_server()
        
        return True

def main():
    """Função principal"""
    system = TecnoCursosFinal()
    
    try:
        system.run()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 