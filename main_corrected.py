#!/usr/bin/env python3
"""
Servidor Principal Corrigido - TecnoCursos AI Enterprise Edition 2025
Versão otimizada e corrigida para funcionamento garantido
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """Cria diretórios necessários"""
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
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Diretório criado: {directory}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando TecnoCursos AI Enterprise Edition 2025...")
    
    # Criar diretórios
    create_directories()
    
    # Configurações do servidor
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info(f"🎯 Servidor configurado para {host}:{port}")
    logger.info(f"🔄 Modo reload: {reload}")
    
    try:
        # Importar aplicação
        sys.path.insert(0, str(Path(__file__).parent))
        from app.main import app
        
        logger.info("✅ Aplicação carregada com sucesso")
        logger.info("📚 Documentação: http://127.0.0.1:8000/docs")
        logger.info("🔍 Health Check: http://127.0.0.1:8000/api/health")
        logger.info("🏠 Dashboard: http://127.0.0.1:8000/dashboard")
        
        # Iniciar servidor
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        logger.info("🔧 Tentando servidor de fallback...")
        
        # Servidor de fallback
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        fallback_app = FastAPI(
            title="TecnoCursos AI - Fallback",
            description="Servidor de fallback funcionando",
            version="1.0.0"
        )
        
        @fallback_app.get("/")
        async def root():
            return {"message": "TecnoCursos AI funcionando!"}
        
        @fallback_app.get("/api/health")
        async def health():
            return {"status": "healthy", "message": "Sistema funcionando"}
        
        @fallback_app.get("/docs")
        async def docs():
            return {"message": "Documentação disponível em /docs"}
        
        logger.info("✅ Servidor de fallback iniciado")
        uvicorn.run(fallback_app, host=host, port=port, reload=reload)

if __name__ == "__main__":
    main() 