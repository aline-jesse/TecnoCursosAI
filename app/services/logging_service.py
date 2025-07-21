"""
Serviço de Logging - TecnoCursos AI
Sistema completo para rastreamento de operações, erros e eventos

Este serviço centraliza todos os logs do sistema, oferecendo:
- Logs estruturados em JSON
- Diferentes níveis de severidade
- Rastreamento de operações por usuário
- Métricas de performance
- Logs de auditoria para compliance
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel
import uuid
from contextlib import asynccontextmanager

class LogLevel(str, Enum):
    """Níveis de log disponíveis"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(str, Enum):
    """Categorias de eventos para facilitar filtragem"""
    USER_ACTION = "user_action"
    SYSTEM_OPERATION = "system_operation"
    VIDEO_PROCESSING = "video_processing"
    AI_GENERATION = "ai_generation"
    AUTHENTICATION = "authentication"
    DATA_EXPORT = "data_export"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    SECURITY = "security"

class LogEntry(BaseModel):
    """Modelo estruturado para entradas de log"""
    id: str
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    duration_ms: Optional[float] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class OperationContext:
    """Contexto para rastreamento de operações"""
    def __init__(self, operation_id: str, user_id: str = None):
        self.operation_id = operation_id
        self.user_id = user_id
        self.start_time = datetime.now(timezone.utc)
        self.metadata = {}

class LoggingService:
    """Serviço principal de logging"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.active_operations: Dict[str, OperationContext] = {}
    
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger com formatação JSON"""
        logger = logging.getLogger("tecnocursos_ai")
        logger.setLevel(logging.DEBUG)
        
        # Evita duplicação de handlers
        if logger.handlers:
            return logger
        
        # Handler para arquivo
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/application.log", encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formatador JSON personalizado
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Adiciona dados extras se disponíveis
                if hasattr(record, 'extra_data'):
                    log_data.update(record.extra_data)
                
                return json.dumps(log_data, ensure_ascii=False)
        
        formatter = JSONFormatter()
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        operation_id: Optional[str] = None,
        metadata: Dict[str, Any] = None,
        duration_ms: Optional[float] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LogEntry:
        """Log uma entrada estruturada"""
        
        entry = LogEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            level=level,
            category=category,
            message=message,
            user_id=user_id,
            session_id=session_id,
            operation_id=operation_id,
            metadata=metadata or {},
            duration_ms=duration_ms,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Log usando o logger Python
        extra_data = {
            "entry_id": entry.id,
            "category": entry.category,
            "user_id": entry.user_id,
            "session_id": entry.session_id,
            "operation_id": entry.operation_id,
            "metadata": entry.metadata,
            "duration_ms": entry.duration_ms,
            "ip_address": entry.ip_address
        }
        
        self.logger.log(
            getattr(logging, level.value),
            message,
            extra={'extra_data': extra_data}
        )
        
        return entry
    
    def start_operation(self, operation_name: str, user_id: str = None) -> str:
        """Inicia rastreamento de uma operação"""
        operation_id = str(uuid.uuid4())
        context = OperationContext(operation_id, user_id)
        self.active_operations[operation_id] = context
        
        # Log início da operação
        self.logger.info(
            f"Operação iniciada: {operation_name}",
            extra={'extra_data': {
                'operation_id': operation_id,
                'operation_name': operation_name,
                'user_id': user_id,
                'start_time': context.start_time.isoformat()
            }}
        )
        
        return operation_id
    
    async def end_operation(
        self,
        operation_id: str,
        success: bool = True,
        result_data: Dict[str, Any] = None,
        error_message: str = None
    ):
        """Finaliza rastreamento de uma operação"""
        if operation_id not in self.active_operations:
            await self.log(
                LogLevel.WARNING,
                LogCategory.SYSTEM_OPERATION,
                f"Tentativa de finalizar operação inexistente: {operation_id}"
            )
            return
        
        context = self.active_operations[operation_id]
        end_time = datetime.now(timezone.utc)
        duration_ms = (end_time - context.start_time).total_seconds() * 1000
        
        level = LogLevel.INFO if success else LogLevel.ERROR
        message = f"Operação finalizada: {operation_id}"
        if error_message:
            message += f" - Erro: {error_message}"
        
        await self.log(
            level=level,
            category=LogCategory.SYSTEM_OPERATION,
            message=message,
            user_id=context.user_id,
            operation_id=operation_id,
            duration_ms=duration_ms,
            metadata={
                "success": success,
                "result_data": result_data or {},
                "error_message": error_message,
                "operation_metadata": context.metadata
            }
        )
        
        # Remove da lista de operações ativas
        del self.active_operations[operation_id]
    
    @asynccontextmanager
    async def operation_context(self, operation_name: str, user_id: str = None):
        """Context manager para operações automáticas"""
        operation_id = self.start_operation(operation_name, user_id)
        try:
            yield operation_id
            await self.end_operation(operation_id, success=True)
        except Exception as e:
            await self.end_operation(
                operation_id,
                success=False,
                error_message=str(e)
            )
            raise
    
    # Métodos de conveniência para diferentes tipos de log
    async def log_user_action(
        self,
        action: str,
        user_id: str,
        session_id: str = None,
        metadata: Dict[str, Any] = None,
        ip_address: str = None
    ):
        """Log ações do usuário"""
        await self.log(
            LogLevel.INFO,
            LogCategory.USER_ACTION,
            f"Usuário executou ação: {action}",
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            ip_address=ip_address
        )
    
    async def log_video_processing(
        self,
        operation: str,
        status: str,
        video_id: str = None,
        duration_ms: float = None,
        metadata: Dict[str, Any] = None
    ):
        """Log processamento de vídeo"""
        await self.log(
            LogLevel.INFO,
            LogCategory.VIDEO_PROCESSING,
            f"Processamento de vídeo - {operation}: {status}",
            metadata={
                "video_id": video_id,
                "operation": operation,
                "status": status,
                **(metadata or {})
            },
            duration_ms=duration_ms
        )
    
    async def log_ai_generation(
        self,
        type: str,
        status: str,
        tokens_used: int = None,
        model: str = None,
        duration_ms: float = None,
        user_id: str = None
    ):
        """Log gerações de IA"""
        await self.log(
            LogLevel.INFO,
            LogCategory.AI_GENERATION,
            f"Geração IA - {type}: {status}",
            user_id=user_id,
            metadata={
                "type": type,
                "status": status,
                "tokens_used": tokens_used,
                "model": model
            },
            duration_ms=duration_ms
        )
    
    async def log_error(
        self,
        error: Exception,
        category: LogCategory = LogCategory.ERROR_HANDLING,
        user_id: str = None,
        operation_id: str = None,
        additional_context: Dict[str, Any] = None
    ):
        """Log erros com contexto completo"""
        import traceback
        
        await self.log(
            LogLevel.ERROR,
            category,
            f"Erro: {str(error)}",
            user_id=user_id,
            operation_id=operation_id,
            metadata={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "additional_context": additional_context or {}
            }
        )
    
    async def log_security_event(
        self,
        event_type: str,
        description: str,
        user_id: str = None,
        ip_address: str = None,
        severity: LogLevel = LogLevel.WARNING
    ):
        """Log eventos de segurança"""
        await self.log(
            severity,
            LogCategory.SECURITY,
            f"Evento de segurança - {event_type}: {description}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={
                "event_type": event_type,
                "severity": severity.value
            }
        )
    
    async def get_logs(
        self,
        limit: int = 100,
        level: LogLevel = None,
        category: LogCategory = None,
        user_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """Recupera logs com filtros (implementação básica para arquivo)"""
        # Para produção, recomenda-se usar banco de dados ou ELK stack
        logs = []
        
        try:
            with open("logs/application.log", "r", encoding='utf-8') as f:
                for line in f:
                    try:
                        log_data = json.loads(line.strip())
                        
                        # Aplicar filtros
                        if level and log_data.get("level") != level.value:
                            continue
                        if category and log_data.get("category") != category.value:
                            continue
                        if user_id and log_data.get("user_id") != user_id:
                            continue
                        
                        logs.append(log_data)
                        
                        if len(logs) >= limit:
                            break
                            
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return list(reversed(logs))  # Mais recentes primeiro

# Instância global do serviço
logging_service = LoggingService() 