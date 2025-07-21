#!/usr/bin/env python3
"""
Script principal para executar o TecnoCursos AI
Sistema SaaS para upload de arquivos e geração de vídeos
"""

import sys
import os
import uvicorn
import logging
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Função principal para iniciar o servidor"""
    try:
        # Importar a aplicação
        from app.main import app
        
        # Configurações do servidor
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        debug = os.getenv("DEBUG", "true").lower() == "true"
        
        logger.info(f"Iniciando TecnoCursos AI em {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # Iniciar servidor
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug"
        )
        
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 