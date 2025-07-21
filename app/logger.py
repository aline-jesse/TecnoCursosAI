"""
Sistema de logging avançado para TecnoCursos AI
Inclui rotação de logs, formatação customizada, métricas de performance e alertas
"""

import os
import sys
import json
import time
import logging
import logging.handlers
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import wraps
from contextlib import contextmanager

# Configurações de logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Níveis customizados
PERFORMANCE_LEVEL = 25
SECURITY_LEVEL = 35
BUSINESS_LEVEL = 45

logging.addLevelName(PERFORMANCE_LEVEL, "PERFORMANCE")
logging.addLevelName(SECURITY_LEVEL, "SECURITY")
logging.addLevelName(BUSINESS_LEVEL, "BUSINESS")

class CustomFormatter(logging.Formatter):
    """Formatador customizado com cores e estrutura JSON opcional"""
    
    # Cores ANSI
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'PERFORMANCE': '\033[35m',  # Magenta
        'WARNING': '\033[33m',   # Yellow
        'SECURITY': '\033[31m',  # Red
        'ERROR': '\033[31m',     # Red
        'BUSINESS': '\033[34m',  # Blue
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }
    
    def __init__(self, use_color=True, use_json=False):
        super().__init__()
        self.use_color = use_color
        self.use_json = use_json
    
    def format(self, record):
        if self.use_json:
            return self._format_json(record)
        else:
            return self._format_text(record)
    
    def _format_json(self, record):
        """Formato JSON estruturado"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_name': record.threadName
        }
        
        # Adicionar dados extras se existirem
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_data['execution_time'] = record.execution_time
        if hasattr(record, 'file_size'):
            log_data['file_size'] = record.file_size
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        if hasattr(record, 'user_agent'):
            log_data['user_agent'] = record.user_agent
        
        # Adicionar stack trace para erros
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)
    
    def _format_text(self, record):
        """Formato de texto com cores"""
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()
        
        # Aplicar cores se habilitado
        if self.use_color and sys.stderr.isatty():
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            level = f"{color}{level}{reset}"
        
        # Formato base
        formatted = f"{timestamp} | {level:12} | {logger_name:20} | {message}"
        
        # Adicionar informações extras
        extras = []
        if hasattr(record, 'user_id'):
            extras.append(f"user_id={record.user_id}")
        if hasattr(record, 'execution_time'):
            extras.append(f"time={record.execution_time:.3f}s")
        if hasattr(record, 'file_size'):
            extras.append(f"size={self._format_bytes(record.file_size)}")
        
        if extras:
            formatted += f" [{', '.join(extras)}]"
        
        # Adicionar localização para DEBUG
        if record.levelno == logging.DEBUG:
            formatted += f" ({record.module}:{record.lineno})"
        
        return formatted
    
    def _format_bytes(self, bytes_size):
        """Formatar bytes em formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f}TB"

class PerformanceFilter(logging.Filter):
    """Filtro para logs de performance"""
    
    def filter(self, record):
        return record.levelno >= PERFORMANCE_LEVEL

class SecurityFilter(logging.Filter):
    """Filtro para logs de segurança"""
    
    def filter(self, record):
        return record.levelno >= SECURITY_LEVEL or hasattr(record, 'security_event')

class MetricsCollector:
    """Coletor de métricas para logging"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'error_count': 0,
            'performance_issues': 0,
            'security_events': 0,
            'file_uploads': 0,
            'total_upload_size': 0,
            'avg_response_time': 0.0,
            'peak_memory_usage': 0
        }
        self.response_times = []
    
    def record_request(self, response_time: float, status_code: int = 200):
        """Registrar uma requisição"""
        self.metrics['total_requests'] += 1
        self.response_times.append(response_time)
        
        # Manter apenas os últimos 1000 tempos de resposta
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Calcular média
        self.metrics['avg_response_time'] = sum(self.response_times) / len(self.response_times)
        
        # Contabilizar erros
        if status_code >= 400:
            self.metrics['error_count'] += 1
    
    def record_file_upload(self, file_size: int):
        """Registrar upload de arquivo"""
        self.metrics['file_uploads'] += 1
        self.metrics['total_upload_size'] += file_size
    
    def record_performance_issue(self):
        """Registrar problema de performance"""
        self.metrics['performance_issues'] += 1
    
    def record_security_event(self):
        """Registrar evento de segurança"""
        self.metrics['security_events'] += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obter resumo das métricas"""
        return {
            **self.metrics,
            'uptime_hours': (datetime.now() - start_time).total_seconds() / 3600,
            'error_rate': (self.metrics['error_count'] / max(1, self.metrics['total_requests'])) * 100,
            'avg_upload_size': self.metrics['total_upload_size'] / max(1, self.metrics['file_uploads'])
        }

# Instância global do coletor de métricas
metrics_collector = MetricsCollector()
start_time = datetime.now()

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configurar logger com handlers múltiplos e formatação avançada
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Handler para console (colorido)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CustomFormatter(use_color=True, use_json=False))
    logger.addHandler(console_handler)
    
    # Handler para arquivo geral (rotativo)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(CustomFormatter(use_color=False, use_json=False))
    logger.addHandler(file_handler)
    
    # Handler para logs estruturados (JSON)
    json_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{name}_structured.log",
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10,
        encoding='utf-8'
    )
    json_handler.setLevel(logging.INFO)
    json_handler.setFormatter(CustomFormatter(use_color=False, use_json=True))
    logger.addHandler(json_handler)
    
    # Handler específico para erros
    error_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "errors.log",
        maxBytes=50*1024*1024,  # 50MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(CustomFormatter(use_color=False, use_json=True))
    logger.addHandler(error_handler)
    
    # Handler para performance
    performance_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "performance.log",
        maxBytes=30*1024*1024,  # 30MB
        backupCount=3,
        encoding='utf-8'
    )
    performance_handler.setLevel(PERFORMANCE_LEVEL)
    performance_handler.addFilter(PerformanceFilter())
    performance_handler.setFormatter(CustomFormatter(use_color=False, use_json=True))
    logger.addHandler(performance_handler)
    
    # Handler para segurança
    security_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "security.log",
        maxBytes=100*1024*1024,  # 100MB
        backupCount=10,
        encoding='utf-8'
    )
    security_handler.setLevel(SECURITY_LEVEL)
    security_handler.addFilter(SecurityFilter())
    security_handler.setFormatter(CustomFormatter(use_color=False, use_json=True))
    logger.addHandler(security_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Obter logger configurado"""
    return setup_logger(name)

# Decoradores para logging automático

def log_execution_time(logger_name: str = None):
    """Decorator para logar tempo de execução"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = get_logger(logger_name or func.__module__)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log de performance se demorar mais que 1 segundo
                if execution_time > 1.0:
                    logger.log(PERFORMANCE_LEVEL, 
                             f"Slow execution: {func.__name__}",
                             extra={'execution_time': execution_time})
                    metrics_collector.record_performance_issue()
                else:
                    logger.debug(f"Executed {func.__name__}",
                               extra={'execution_time': execution_time})
                
                metrics_collector.record_request(execution_time)
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Error in {func.__name__}: {str(e)}",
                           extra={'execution_time': execution_time},
                           exc_info=True)
                metrics_collector.record_request(execution_time, 500)
                raise
                
        return wrapper
    return decorator

def log_file_operation(logger_name: str = None):
    """Decorator para operações de arquivo"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            start_time = time.time()
            
            # Tentar extrair informações do arquivo dos argumentos
            file_info = {}
            if args and hasattr(args[0], 'filename'):
                file_info['filename'] = args[0].filename
                file_info['file_size'] = getattr(args[0], 'size', 0)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"File operation completed: {func.__name__}",
                          extra={
                              'execution_time': execution_time,
                              **file_info
                          })
                
                if 'file_size' in file_info:
                    metrics_collector.record_file_upload(file_info['file_size'])
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"File operation failed: {func.__name__}: {str(e)}",
                           extra={
                               'execution_time': execution_time,
                               **file_info
                           },
                           exc_info=True)
                raise
                
        return wrapper
    return decorator

def log_security_event(event_type: str, logger_name: str = None):
    """Decorator para eventos de segurança"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            
            try:
                result = func(*args, **kwargs)
                logger.log(SECURITY_LEVEL,
                         f"Security event: {event_type} - {func.__name__} succeeded",
                         extra={'security_event': event_type})
                return result
                
            except Exception as e:
                logger.log(SECURITY_LEVEL,
                         f"Security event: {event_type} - {func.__name__} failed: {str(e)}",
                         extra={'security_event': event_type},
                         exc_info=True)
                metrics_collector.record_security_event()
                raise
                
        return wrapper
    return decorator

@contextmanager
def log_context(logger_name: str, operation: str, **context):
    """Context manager para logging com contexto"""
    logger = get_logger(logger_name)
    start_time = time.time()
    
    logger.info(f"Starting {operation}", extra=context)
    
    try:
        yield logger
        execution_time = time.time() - start_time
        logger.info(f"Completed {operation}",
                   extra={**context, 'execution_time': execution_time})
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Failed {operation}: {str(e)}",
                    extra={**context, 'execution_time': execution_time},
                    exc_info=True)
        raise

def log_performance_metric(metric_name: str, value: float, logger_name: str = None):
    """Logar métrica de performance"""
    logger = get_logger(logger_name or "performance")
    logger.log(PERFORMANCE_LEVEL,
             f"Performance metric: {metric_name}",
             extra={'metric_name': metric_name, 'metric_value': value})

def log_business_event(event: str, details: Dict[str, Any] = None, logger_name: str = None):
    """Logar evento de negócio"""
    logger = get_logger(logger_name or "business")
    logger.log(BUSINESS_LEVEL,
             f"Business event: {event}",
             extra={'business_event': event, 'details': details or {}})

def get_system_metrics() -> Dict[str, Any]:
    """Obter métricas do sistema"""
    import psutil
    
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'active_connections': len(psutil.net_connections()),
        'process_count': len(psutil.pids()),
        'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
    }

def log_system_status(logger_name: str = "system"):
    """Logar status do sistema"""
    logger = get_logger(logger_name)
    
    try:
        system_metrics = get_system_metrics()
        app_metrics = metrics_collector.get_metrics_summary()
        
        logger.info("System status check",
                   extra={
                       'system_metrics': system_metrics,
                       'app_metrics': app_metrics
                   })
        
        # Alertas de sistema
        if system_metrics['memory_percent'] > 85:
            logger.warning("High memory usage detected",
                         extra={'memory_percent': system_metrics['memory_percent']})
        
        if system_metrics['cpu_percent'] > 90:
            logger.warning("High CPU usage detected",
                         extra={'cpu_percent': system_metrics['cpu_percent']})
        
        if app_metrics['error_rate'] > 5:
            logger.warning("High error rate detected",
                         extra={'error_rate': app_metrics['error_rate']})
            
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}", exc_info=True)

# Configurar logging principal ao importar
main_logger = get_logger("tecnocursos_ai")
main_logger.info("Logging system initialized") 