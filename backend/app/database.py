"""
Sistema de banco de dados para TecnoCursos AI
Usando SQLite para simplicidade e portabilidade
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging
import asyncio

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Configuração do SQLite com pooling
SQLALCHEMY_DATABASE_URL = settings.database_url

# Engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,  # Necessário para SQLite
    },
    echo=settings.debug,  # Log SQL queries em debug
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos - Usando SQLAlchemy 2.0 compatible
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

metadata = MetaData()

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

async def create_database():
    """Cria o banco de dados e todas as tabelas"""
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados criado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        return False

def create_database_sync():
    """
    Cria todas as tabelas no banco de dados (versão síncrona)
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados criado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        raise

def drop_database():
    """
    Remove todas as tabelas do banco de dados
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Banco de dados removido com sucesso")
    except Exception as e:
        logger.error(f"Erro ao remover banco de dados: {e}")
        raise

def reset_database():
    """
    Reseta o banco de dados (remove e recria)
    """
    drop_database()
    create_database_sync()
    logger.info("Banco de dados resetado com sucesso")

# Health check do banco
def check_database_health() -> bool:
    """
    Verifica se o banco de dados está saudável (versão síncrona)
    """
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Erro na verificação de saúde do banco: {e}")
        return False

async def check_database_health_async() -> bool:
    """
    Verifica se o banco de dados está saudável (versão assíncrona)
    """
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, check_database_health)
    except Exception as e:
        logger.error(f"Erro na verificação assíncrona de saúde do banco: {e}")
        return False 