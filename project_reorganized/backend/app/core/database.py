"""
Sistema de banco de dados do TecnoCursos AI
SQLite com SQLAlchemy 2.0
"""

import logging
from typing import Generator, AsyncGenerator
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

from .config import get_settings, get_database_url

logger = logging.getLogger(__name__)

# Configurações
settings = get_settings()

# Base para modelos
Base = declarative_base()

# Engine do SQLAlchemy
engine = create_engine(
    get_database_url(),
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},  # SQLite
    echo=settings.debug,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_db_async() -> AsyncGenerator[Session, None]:
    """
    Versão assíncrona do dependency de banco
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão assíncrona do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_database() -> None:
    """
    Criar todas as tabelas do banco de dados
    """
    try:
        # Importar todos os modelos para registrar no metadata
        from ..models import base  # Import para registrar modelos
        
        # Criar diretório do banco se necessário
        db_url = get_database_url()
        if db_url.startswith("sqlite"):
            db_path = db_url.replace("sqlite:///", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Banco de dados criado com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar banco de dados: {e}")
        raise


async def init_database() -> None:
    """
    Inicializar banco de dados de forma assíncrona
    """
    try:
        create_database()
        
        # Verificar conexão
        if await check_database_health():
            logger.info("✅ Banco de dados inicializado e funcionando")
        else:
            logger.warning("⚠️ Banco de dados inicializado mas com problemas de conexão")
            
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do banco: {e}")
        raise


def check_database_health_sync() -> bool:
    """
    Verificar saúde do banco de dados (versão síncrona)
    """
    try:
        db = SessionLocal()
        # Executar query simples para testar conexão
        result = db.execute(text("SELECT 1"))
        db.close()
        return result.scalar() == 1
    except Exception as e:
        logger.error(f"Erro no health check do banco: {e}")
        return False


async def check_database_health() -> bool:
    """
    Verificar saúde do banco de dados (versão assíncrona)
    """
    try:
        # Por enquanto usar versão síncrona
        return check_database_health_sync()
    except Exception as e:
        logger.error(f"Erro no health check assíncrono do banco: {e}")
        return False


def reset_database() -> None:
    """
    Resetar banco de dados (apenas para desenvolvimento)
    """
    if not settings.debug:
        raise ValueError("Reset de banco só permitido em modo debug")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        
        # Recreate all tables
        create_database()
        
        logger.info("🔄 Banco de dados resetado com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao resetar banco de dados: {e}")
        raise


def get_database_info() -> dict:
    """
    Obter informações sobre o banco de dados
    """
    try:
        db = SessionLocal()
        
        # Informações básicas
        info = {
            "engine": str(engine.url),
            "dialect": engine.dialect.name,
            "tables": list(Base.metadata.tables.keys()),
            "health": check_database_health_sync()
        }
        
        # Estatísticas se SQLite
        if engine.dialect.name == "sqlite":
            result = db.execute(text("PRAGMA database_list"))
            info["sqlite_info"] = [dict(row._mapping) for row in result]
        
        db.close()
        return info
        
    except Exception as e:
        logger.error(f"Erro ao obter informações do banco: {e}")
        return {"error": str(e)} 