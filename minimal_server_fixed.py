#!/usr/bin/env python3
"""
Servidor mínimo do TecnoCursos AI - Versão corrigida
"""

import os
import sys
from pathlib import Path

# Configurar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Importar routers e dependências
from app.database import engine, Base, get_db
from app.routers import auth, users, projects, files, scenes, assets
from app.models import User, Project, Scene, Asset

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando TecnoCursos AI...")
    
    # Criar tabelas
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Banco de dados inicializado")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
    
    yield
    
    logger.info("👋 Encerrando TecnoCursos AI...")

# Criar aplicação
app = FastAPI(
    title="TecnoCursos AI",
    description="Sistema de geração de vídeos educacionais",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "TecnoCursos AI"}

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(users.router, prefix="/api/users", tags=["Usuários"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projetos"])
app.include_router(files.router, prefix="/api/files", tags=["Arquivos"])
app.include_router(scenes.router, prefix="/api/scenes", tags=["Cenas"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])

# Handler de erro global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )

if __name__ == "__main__":
    try:
        logger.info("🌐 Servidor disponível em: http://localhost:8000")
        logger.info("📚 Documentação em: http://localhost:8000/docs")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)
