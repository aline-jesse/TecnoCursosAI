"""
Sistema de Logging Centralizado - TecnoCursos AI
Logging estruturado com múltiplos handlers e contexto
"""

import sys
import json
import logging
import logging.handlers
from typing import Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from enum import Enum
import traceback
from contextvars import ContextVar
import uuid

# Context variables para rastreamento
request_id_context: ContextVar[str] = ContextVar('request_id', default='')
user_id_context: ContextVar[str] = ContextVar('user_id', default='')

class LogLevel(Enum):
    """Níveis de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata log record como JSON estruturado"""
        
        # Dados básicos do log
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar contexto de request se disponível
        request_id = request_id_context.get('')
        if request_id:
            log_data["request_id"] = request_id
        
        user_id = user_id_context.get('')
        if user_id:
            log_data["user_id"] = user_id
        
        # Adicionar informações de exceção
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Adicionar dados extras do record
        extra_data = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'message'
            }:
                extra_data[key] = value
        
        if extra_data:
            log_data["extra"] = extra_data
        
        return json.dumps(log_data, default=str, ensure_ascii=False)

class ColoredConsoleFormatter(logging.Formatter):
    """Formatter colorido para console"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata log com cores para console"""
        
        # Cor baseada no nível
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Contexto de request
        request_id = request_id_context.get('')
        user_id = user_id_context.get('')
        
        context_info = ""
        if request_id:
            context_info += f" [req:{request_id[:8]}]"
        if user_id:
            context_info += f" [user:{user_id}]"
        
        # Formato básico
        formatted = (
            f"{color}[{record.levelname}]{reset} "
            f"{datetime.utcnow().strftime('%H:%M:%S')} "
            f"{record.name}:{record.funcName}:{record.lineno}"
            f"{context_info} - {record.getMessage()}"
        )
        
        # Adicionar traceback se houver exceção
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted

class LoggerManager:
    """Gerenciador centralizado de loggers"""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.configured = False
        self.log_level = logging.INFO
        self.log_file: Optional[str] = None
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.enable_console = True
        self.enable_json = False
        
    def configure(
        self,
        log_level: Union[str, int] = "INFO",
        log_file: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        enable_console: bool = True,
        enable_json: bool = False,
        log_dir: str = "./logs"
    ):
        """Configura sistema de logging"""
        
        # Converter nível se necessário
        if isinstance(log_level, str):
            self.log_level = getattr(logging, log_level.upper())
        else:
            self.log_level = log_level
        
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_json = enable_json
        
        # Criar diretório de logs
        if log_file:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            self.log_file = str(log_path / log_file)
        
        # Configurar logger root
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remover handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Adicionar handlers
        self._add_console_handler(root_logger)
        if self.log_file:
            self._add_file_handler(root_logger)
        
        self.configured = True
    
    def _add_console_handler(self, logger: logging.Logger):
        """Adiciona handler para console"""
        if not self.enable_console:
            return
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        if self.enable_json:
            formatter = StructuredFormatter()
        else:
            formatter = ColoredConsoleFormatter()
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    def _add_file_handler(self, logger: logging.Logger):
        """Adiciona handler para arquivo"""
        if not self.log_file:
            return
        
        # Handler com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # Sempre usar JSON para arquivos
        formatter = StructuredFormatter()
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Obtém logger por nome"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def log_request_start(
        self, 
        method: str, 
        path: str, 
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log início de request"""
        if not request_id:
            request_id = str(uuid.uuid4())
        
        request_id_context.set(request_id)
        if user_id:
            user_id_context.set(str(user_id))
        
        logger = self.get_logger("request")
        logger.info("Request started", extra={
            "event": "request_start",
            "method": method,
            "path": path,
            "request_id": request_id,
            "user_id": user_id
        })
        
        return request_id
    
    def log_request_end(
        self, 
        request_id: str,
        status_code: int,
        duration_ms: float,
        response_size: Optional[int] = None
    ):
        """Log fim de request"""
        logger = self.get_logger("request")
        logger.info("Request completed", extra={
            "event": "request_end",
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "response_size": response_size
        })
        
        # Limpar contexto
        request_id_context.set('')
        user_id_context.set('')
    
    def log_database_query(
        self, 
        query: str, 
        duration_ms: float,
        table: Optional[str] = None
    ):
        """Log consultas de banco"""
        logger = self.get_logger("database")
        
        # Log apenas se duração for alta ou em debug
        if duration_ms > 100 or logger.isEnabledFor(logging.DEBUG):
            logger.info("Database query", extra={
                "event": "db_query",
                "query": query[:500],  # Truncar query longa
                "duration_ms": duration_ms,
                "table": table,
                "slow_query": duration_ms > 100
            })
    
    def log_cache_operation(
        self, 
        operation: str, 
        key: str, 
        hit: bool = None,
        duration_ms: Optional[float] = None
    ):
        """Log operações de cache"""
        logger = self.get_logger("cache")
        logger.debug("Cache operation", extra={
            "event": "cache_operation",
            "operation": operation,
            "key": key,
            "hit": hit,
            "duration_ms": duration_ms
        })
    
    def log_ai_request(
        self,
        provider: str,
        model: str,
        tokens_used: Optional[int] = None,
        duration_ms: Optional[float] = None,
        cost: Optional[float] = None
    ):
        """Log requests para APIs de IA"""
        logger = self.get_logger("ai")
        logger.info("AI API request", extra={
            "event": "ai_request",
            "provider": provider,
            "model": model,
            "tokens_used": tokens_used,
            "duration_ms": duration_ms,
            "cost": cost
        })
    
    def log_file_operation(
        self,
        operation: str,
        filename: str,
        file_size: Optional[int] = None,
        duration_ms: Optional[float] = None,
        success: bool = True
    ):
        """Log operações de arquivo"""
        logger = self.get_logger("files")
        level = logging.INFO if success else logging.ERROR
        logger.log(level, f"File {operation}", extra={
            "event": "file_operation",
            "operation": operation,
            "filename": filename,
            "file_size": file_size,
            "duration_ms": duration_ms,
            "success": success
        })
    
    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log eventos de segurança"""
        logger = self.get_logger("security")
        logger.warning("Security event", extra={
            "event": "security_event",
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {}
        })

# Instância global do gerenciador
logger_manager = LoggerManager()

# Funções de conveniência
def configure_logging(**kwargs):
    """Configura sistema de logging"""
    return logger_manager.configure(**kwargs)

def get_logger(name: str) -> logging.Logger:
    """Obtém logger por nome"""
    return logger_manager.get_logger(name)

def log_request_start(method: str, path: str, user_id: str = None, request_id: str = None) -> str:
    """Log início de request"""
    return logger_manager.log_request_start(method, path, user_id, request_id)

def log_request_end(request_id: str, status_code: int, duration_ms: float, response_size: int = None):
    """Log fim de request"""
    return logger_manager.log_request_end(request_id, status_code, duration_ms, response_size)

def log_database_query(query: str, duration_ms: float, table: str = None):
    """Log consultas de banco"""
    return logger_manager.log_database_query(query, duration_ms, table)

def log_cache_operation(operation: str, key: str, hit: bool = None, duration_ms: float = None):
    """Log operações de cache"""
    return logger_manager.log_cache_operation(operation, key, hit, duration_ms)

def log_ai_request(provider: str, model: str, tokens_used: int = None, duration_ms: float = None, cost: float = None):
    """Log requests para APIs de IA"""
    return logger_manager.log_ai_request(provider, model, tokens_used, duration_ms, cost)

def log_file_operation(operation: str, filename: str, file_size: int = None, duration_ms: float = None, success: bool = True):
    """Log operações de arquivo"""
    return logger_manager.log_file_operation(operation, filename, file_size, duration_ms, success)

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, details: Dict[str, Any] = None):
    """Log eventos de segurança"""
    return logger_manager.log_security_event(event_type, user_id, ip_address, details)
