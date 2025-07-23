"""
Configuração de logging do TecnoCursos AI
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import get_settings


def setup_logging(log_file: Optional[str] = None) -> None:
    """
    Configurar logging da aplicação
    """
    settings = get_settings()
    
    # Criar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar nível de log
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para arquivo se especificado ou em produção
    if log_file or not settings.debug:
        file_path = log_dir / (log_file or "tecnocursos.log")
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    configure_specific_loggers()


def configure_specific_loggers() -> None:
    """
    Configurar loggers específicos para diferentes módulos
    """
    # SQLAlchemy - reduzir verbosidade em produção
    settings = get_settings()
    if not settings.debug:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    
    # FastAPI
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    
    # Nossa aplicação
    logging.getLogger('app').setLevel(logging.DEBUG if settings.debug else logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Obter logger configurado para um módulo específico
    """
    return logging.getLogger(f"app.{name}")


class LoggerMixin:
    """
    Mixin para adicionar logger a classes
    """
    
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__) 