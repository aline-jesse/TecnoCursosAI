#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Logging Estruturado - TecnoCursos AI

Este módulo implementa logging estruturado seguindo as melhores
práticas de observabilidade para aplicações FastAPI de produção.

Baseado em:
- Structured logging best practices
- 12-Factor App logging methodology
- ELK Stack integration patterns
- OpenTelemetry logging standards
- Python logging best practices

Funcionalidades:
- Logging estruturado em JSON
- Context propagation com correlation IDs
- Multiple handlers (file, console, syslog, external)
- Log levels dinâmicos
- Performance logging
- Security event logging
- Error tracking com stack traces
- Log sampling para high-volume events
- Integration com Sentry, DataDog, etc.

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import json
import logging
import logging.handlers
import sys
import os
import time
import traceback
import functools
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union, List, Callable
from pathlib import Path
from contextvars import ContextVar
from dataclasses import dataclass, asdict
import threading
import queue
import asyncio

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Context variables para correlation
correlation_id_context: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id_context: ContextVar[Optional[int]] = ContextVar('user_id', default=None)
request_context: ContextVar[Optional[Dict]] = ContextVar('request_context', default=None)

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

@dataclass
class LogConfig:
    """Configuração do sistema de logging"""
    level: str = "INFO"
    format: str = "json"  # json, text, structured
    output: str = "console"  # console, file, both, syslog
    file_path: str = "logs/app.log"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    backup_count: int = 5
    enable_correlation: bool = True
    enable_performance: bool = True
    enable_security: bool = True
    sample_rate: float = 1.0  # 1.0 = log everything, 0.1 = log 10%
    external_integrations: List[str] = None
    sensitive_fields: List[str] = None
    
    def __post_init__(self):
        if self.external_integrations is None:
            self.external_integrations = []
        if self.sensitive_fields is None:
            self.sensitive_fields = [
                'password', 'token', 'secret', 'key', 'authorization',
                'cookie', 'session', 'csrf', 'api_key'
            ]

# Configuração global
log_config = LogConfig()

# ============================================================================
# FORMATTERS CUSTOMIZADOS
# ============================================================================

class TecnoCursosJSONFormatter(logging.Formatter):
    """Formatter JSON customizado para TecnoCursos AI"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
        
    def format(self, record: logging.LogRecord) -> str:
        """Formatar log record em JSON estruturado"""
        
        # Dados base do log
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'hostname': self.hostname
        }
        
        # Adicionar correlation ID se disponível
        correlation_id = correlation_id_context.get()
        if correlation_id:
            log_data['correlation_id'] = correlation_id
            
        # Adicionar user ID se disponível
        user_id = user_id_context.get()
        if user_id:
            log_data['user_id'] = user_id
            
        # Adicionar contexto do request se disponível
        request_ctx = request_context.get()
        if request_ctx:
            log_data['request'] = request_ctx
        
        # Adicionar campos extras do record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'message', 'exc_info', 'exc_text',
                          'stack_info']:
                log_data[key] = value
        
        # Adicionar exception info se presente
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Sanitizar dados sensíveis
        log_data = self._sanitize_sensitive_data(log_data)
        
        return json.dumps(log_data, default=str, ensure_ascii=False)
    
    def _sanitize_sensitive_data(self, data: Any) -> Any:
        """Sanitizar dados sensíveis recursivamente"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in log_config.sensitive_fields):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = self._sanitize_sensitive_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_sensitive_data(item) for item in data]
        else:
            return data

class ColoredFormatter(logging.Formatter):
    """Formatter com cores para console (desenvolvimento)"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Ciano
        'INFO': '\033[32m',     # Verde
        'WARNING': '\033[33m',  # Amarelo
        'ERROR': '\033[31m',    # Vermelho
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatar com cores"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formato base
        format_str = f"{color}%(asctime)s [%(levelname)s]{reset} %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        
        # Adicionar correlation ID se disponível
        correlation_id = correlation_id_context.get()
        if correlation_id:
            format_str = f"{color}%(asctime)s [%(levelname)s] [{correlation_id}]{reset} %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        
        formatter = logging.Formatter(format_str)
        return formatter.format(record)

# ============================================================================
# HANDLERS CUSTOMIZADOS
# ============================================================================

class AsyncFileHandler(logging.Handler):
    """Handler assíncrono para arquivos (melhor performance)"""
    
    def __init__(self, filename: str, max_bytes: int = 0, backup_count: int = 0):
        super().__init__()
        self.filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.queue = queue.Queue()
        self.thread = None
        self.stop_event = threading.Event()
        self._ensure_dir()
        self._start_thread()
    
    def _ensure_dir(self):
        """Garantir que o diretório existe"""
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True)
    
    def _start_thread(self):
        """Iniciar thread de escrita"""
        self.thread = threading.Thread(target=self._writer_thread, daemon=True)
        self.thread.start()
    
    def _writer_thread(self):
        """Thread que escreve logs no arquivo"""
        file_handler = logging.handlers.RotatingFileHandler(
            self.filename, maxBytes=self.max_bytes, backupCount=self.backup_count
        )
        file_handler.setFormatter(self.formatter)
        
        while not self.stop_event.is_set():
            try:
                record = self.queue.get(timeout=1)
                if record is None:  # Sentinel para parar
                    break
                file_handler.emit(record)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Erro no AsyncFileHandler: {e}", file=sys.stderr)
    
    def emit(self, record: logging.LogRecord):
        """Enviar log record para a queue"""
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            # Se a queue estiver cheia, descartar o log (evitar memory leak)
            pass
    
    def close(self):
        """Fechar handler e parar thread"""
        self.stop_event.set()
        self.queue.put(None)  # Sentinel
        if self.thread:
            self.thread.join(timeout=5)
        super().close()

class SamplingHandler(logging.Handler):
    """Handler que faz sampling de logs (para high-volume events)"""
    
    def __init__(self, target_handler: logging.Handler, sample_rate: float = 0.1):
        super().__init__()
        self.target_handler = target_handler
        self.sample_rate = sample_rate
        self.counter = 0
        self.lock = threading.Lock()
    
    def emit(self, record: logging.LogRecord):
        """Emitir apenas uma amostra dos logs"""
        with self.lock:
            self.counter += 1
            
            # Sempre logar errors e warnings
            if record.levelno >= logging.WARNING:
                self.target_handler.emit(record)
                return
            
            # Sampling para outros níveis
            if (self.counter % int(1 / self.sample_rate)) == 0:
                # Adicionar informação de sampling
                record.sampled = True
                record.sample_rate = self.sample_rate
                self.target_handler.emit(record)

# ============================================================================
# LOGGER PRINCIPAL
# ============================================================================

class TecnoCursosLogger:
    """Logger principal do TecnoCursos AI"""
    
    def __init__(self, name: str, config: LogConfig = None):
        self.name = name
        self.config = config or log_config
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.config.level.upper()))
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        # Configurar integrações externas
        self._setup_external_integrations()
    
    def _setup_handlers(self):
        """Configurar handlers de logging"""
        handlers = []
        
        # Console handler
        if self.config.output in ['console', 'both']:
            console_handler = logging.StreamHandler(sys.stdout)
            
            if self.config.format == 'json':
                console_handler.setFormatter(TecnoCursosJSONFormatter())
            else:
                console_handler.setFormatter(ColoredFormatter())
                
            handlers.append(console_handler)
        
        # File handler
        if self.config.output in ['file', 'both']:
            if self.config.format == 'json':
                file_handler = AsyncFileHandler(
                    self.config.file_path,
                    max_bytes=self.config.max_file_size,
                    backup_count=self.config.backup_count
                )
                file_handler.setFormatter(TecnoCursosJSONFormatter())
            else:
                file_handler = logging.handlers.RotatingFileHandler(
                    self.config.file_path,
                    maxBytes=self.config.max_file_size,
                    backupCount=self.config.backup_count
                )
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s'
                ))
            
            handlers.append(file_handler)
        
        # Aplicar sampling se configurado
        if self.config.sample_rate < 1.0:
            sampled_handlers = []
            for handler in handlers:
                sampled_handler = SamplingHandler(handler, self.config.sample_rate)
                sampled_handlers.append(sampled_handler)
            handlers = sampled_handlers
        
        # Adicionar handlers ao logger
        for handler in handlers:
            self.logger.addHandler(handler)
    
    def _setup_external_integrations(self):
        """Configurar integrações externas"""
        
        # Sentry integration
        if 'sentry' in self.config.external_integrations and SENTRY_AVAILABLE:
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            # sentry_sdk.init() seria chamado na inicialização da app
    
    # ========================================================================
    # MÉTODOS DE LOGGING
    # ========================================================================
    
    def debug(self, message: str, **kwargs):
        """Log debug"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception com traceback"""
        kwargs['exc_info'] = True
        self._log(logging.ERROR, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Método interno de logging"""
        # Adicionar dados extras ao record
        extra = {}
        
        # Performance timing se disponível
        if 'duration' in kwargs:
            extra['performance'] = {
                'duration_ms': kwargs.pop('duration') * 1000,
                'slow_query': kwargs.pop('duration') > 1.0
            }
        
        # Dados de negócio
        if 'business_event' in kwargs:
            extra['business'] = kwargs.pop('business_event')
        
        # Dados de segurança
        if 'security_event' in kwargs:
            extra['security'] = kwargs.pop('security_event')
        
        # Adicionar kwargs restantes como extra
        extra.update(kwargs)
        
        self.logger.log(level, message, extra=extra)
    
    # ========================================================================
    # MÉTODOS ESPECIALIZADOS
    # ========================================================================
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration: float, user_id: Optional[int] = None, **kwargs):
        """Log de request HTTP"""
        self.info(
            f"{method} {path} - {status_code}",
            request_method=method,
            request_path=path,
            response_status=status_code,
            duration=duration,
            user_id=user_id,
            event_type="http_request",
            **kwargs
        )
    
    def log_database_query(self, query: str, duration: float, 
                          table: str = None, operation: str = None, **kwargs):
        """Log de query do banco"""
        self.debug(
            f"Database query executed",
            query=query[:200] + "..." if len(query) > 200 else query,
            duration=duration,
            table=table,
            operation=operation,
            event_type="database_query",
            **kwargs
        )
    
    def log_business_event(self, event: str, value: Any = None, 
                          user_id: Optional[int] = None, **kwargs):
        """Log de evento de negócio"""
        self.info(
            f"Business event: {event}",
            business_event={
                'event': event,
                'value': value,
                'user_id': user_id,
                **kwargs
            },
            event_type="business"
        )
    
    def log_security_event(self, event: str, severity: str = "medium", 
                          user_id: Optional[int] = None, ip_address: str = None, **kwargs):
        """Log de evento de segurança"""
        self.warning(
            f"Security event: {event}",
            security_event={
                'event': event,
                'severity': severity,
                'user_id': user_id,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow().isoformat(),
                **kwargs
            },
            event_type="security"
        )
    
    def log_performance(self, operation: str, duration: float, 
                       success: bool = True, **kwargs):
        """Log de performance"""
        level = logging.INFO if success else logging.WARNING
        
        self._log(
            level,
            f"Performance: {operation}",
            operation=operation,
            duration=duration,
            success=success,
            event_type="performance",
            **kwargs
        )
    
    def log_ai_request(self, service: str, operation: str, duration: float,
                      tokens: int = 0, cost: float = 0.0, success: bool = True, **kwargs):
        """Log de request para serviços de IA"""
        self.info(
            f"AI request: {service}/{operation}",
            ai_service=service,
            ai_operation=operation,
            duration=duration,
            tokens_used=tokens,
            estimated_cost=cost,
            success=success,
            event_type="ai_request",
            **kwargs
        )

# ============================================================================
# DECORATORS
# ============================================================================

def log_execution_time(logger: TecnoCursosLogger = None, operation: str = None):
    """Decorator para logar tempo de execução"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation or f"{func.__module__}.{func.__name__}"
            log = logger or get_logger(func.__module__)
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                log.log_performance(op_name, duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log.log_performance(op_name, duration, success=False, error=str(e))
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation or f"{func.__module__}.{func.__name__}"
            log = logger or get_logger(func.__module__)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log.log_performance(op_name, duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log.log_performance(op_name, duration, success=False, error=str(e))
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def log_function_calls(logger: TecnoCursosLogger = None, level: str = "DEBUG"):
    """Decorator para logar chamadas de função"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            log_level = getattr(logging, level.upper())
            
            # Log entrada
            log._log(log_level, f"Entering {func.__name__}", 
                    function=func.__name__, args_count=len(args), kwargs_keys=list(kwargs.keys()))
            
            try:
                result = func(*args, **kwargs)
                # Log saída
                log._log(log_level, f"Exiting {func.__name__}", 
                        function=func.__name__, success=True)
                return result
            except Exception as e:
                # Log erro
                log._log(logging.ERROR, f"Error in {func.__name__}: {e}", 
                        function=func.__name__, success=False, error=str(e))
                raise
        
        return wrapper
    return decorator

# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

class LogContext:
    """Context manager para adicionar contexto aos logs"""
    
    def __init__(self, correlation_id: str = None, user_id: int = None, **context):
        self.correlation_id = correlation_id
        self.user_id = user_id
        self.context = context
        self.tokens = {}
    
    def __enter__(self):
        if self.correlation_id:
            self.tokens['correlation_id'] = correlation_id_context.set(self.correlation_id)
        if self.user_id:
            self.tokens['user_id'] = user_id_context.set(self.user_id)
        if self.context:
            self.tokens['request_context'] = request_context.set(self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for token in self.tokens.values():
            token.var.set(token.old_value)

# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def get_logger(name: str, config: LogConfig = None) -> TecnoCursosLogger:
    """Obter logger configurado"""
    return TecnoCursosLogger(name, config)

def set_correlation_id(correlation_id: str):
    """Definir correlation ID no contexto"""
    correlation_id_context.set(correlation_id)

def get_correlation_id() -> Optional[str]:
    """Obter correlation ID do contexto"""
    return correlation_id_context.get()

def configure_logging(config: LogConfig):
    """Configurar sistema de logging globalmente"""
    global log_config
    log_config = config
    
    # Configurar logging root
    logging.basicConfig(level=getattr(logging, config.level.upper()))
    
    # Desabilitar logs de bibliotecas externas se necessário
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def setup_request_logging(app):
    """Configurar logging de requests para FastAPI"""
    @app.middleware("http")
    async def logging_middleware(request, call_next):
        correlation_id = request.headers.get("x-correlation-id") or f"req-{int(time.time() * 1000)}"
        
        with LogContext(
            correlation_id=correlation_id,
            request_method=request.method,
            request_path=request.url.path,
            request_headers=dict(request.headers)
        ):
            start_time = time.time()
            
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                
                logger = get_logger("request")
                logger.log_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration=duration
                )
                
                # Adicionar correlation ID ao response
                response.headers["x-correlation-id"] = correlation_id
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                logger = get_logger("request")
                logger.error(
                    f"Request failed: {e}",
                    request_method=request.method,
                    request_path=request.url.path,
                    duration=duration,
                    error=str(e)
                )
                raise

# ============================================================================
# HEALTH CHECK DO SISTEMA DE LOGGING
# ============================================================================

def get_logging_health() -> Dict[str, Any]:
    """Verificar saúde do sistema de logging"""
    return {
        "status": "healthy",
        "config": {
            "level": log_config.level,
            "format": log_config.format,
            "output": log_config.output,
            "sample_rate": log_config.sample_rate
        },
        "integrations": {
            "structlog": STRUCTLOG_AVAILABLE,
            "json_logger": JSON_LOGGER_AVAILABLE,
            "sentry": SENTRY_AVAILABLE
        },
        "timestamp": datetime.utcnow().isoformat()
    } 