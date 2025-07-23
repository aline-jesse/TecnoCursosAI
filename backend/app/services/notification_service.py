"""
Serviço de Notificações - TecnoCursos AI
Sistema de notificações em tempo real com WebSocket

Este serviço oferece:
- Notificações push em tempo real
- Diferentes tipos de notificação (sucesso, erro, info, warning)
- Histórico de notificações persistente
- Integração com sistema de logging
- Suporte a broadcast e notificações direcionadas
"""

import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any
from enum import Enum
from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect
import uuid

from .logging_service import logging_service, LogLevel, LogCategory

class NotificationType(str, Enum):
    """Tipos de notificação disponíveis"""
    SUCCESS = "success"      # Verde - operações bem-sucedidas
    ERROR = "error"          # Vermelho - erros críticos
    WARNING = "warning"      # Amarelo - avisos importantes
    INFO = "info"            # Azul - informações gerais
    PROGRESS = "progress"    # Azul claro - progresso de operações

class NotificationPriority(str, Enum):
    """Prioridade das notificações"""
    LOW = "low"              # Notificações informativas
    NORMAL = "normal"        # Notificações padrão
    HIGH = "high"            # Notificações importantes
    URGENT = "urgent"        # Notificações críticas

class Notification(BaseModel):
    """Modelo de notificação"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    timestamp: datetime
    user_id: Optional[str] = None
    operation_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    read: bool = False
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_label: Optional[str] = None

class ConnectionManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        # Conexões ativas por usuário
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Metadados das conexões
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, session_info: Dict[str, Any] = None):
        """Conecta um cliente WebSocket"""
        await websocket.accept()
        
        # Adiciona à lista de conexões do usuário
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Armazena metadados da conexão
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.now(timezone.utc),
            "session_info": session_info or {}
        }
        
        await logging_service.log_user_action(
            action="websocket_connected",
            user_id=user_id,
            metadata={"session_info": session_info}
        )
    
    def disconnect(self, websocket: WebSocket):
        """Desconecta um cliente WebSocket"""
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket]["user_id"]
            
            # Remove da lista de conexões do usuário
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove metadados
            del self.connection_metadata[websocket]
    
    async def send_to_user(self, user_id: str, message: dict):
        """Envia mensagem para todas as conexões de um usuário"""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(websocket)
            
            # Remove conexões mortas
            for ws in disconnected:
                self.disconnect(ws)
    
    async def broadcast(self, message: dict, exclude_user: str = None):
        """Envia mensagem para todos os usuários conectados"""
        for user_id in list(self.active_connections.keys()):
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_to_user(user_id, message)
    
    def get_connected_users(self) -> List[str]:
        """Retorna lista de usuários conectados"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, user_id: str = None) -> int:
        """Retorna número de conexões ativas"""
        if user_id:
            return len(self.active_connections.get(user_id, set()))
        return sum(len(connections) for connections in self.active_connections.values())

class NotificationService:
    """Serviço principal de notificações"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        # Armazena notificações em memória (em produção, usar banco de dados)
        self.notifications: Dict[str, Notification] = {}
        # Índice por usuário para busca rápida
        self.user_notifications: Dict[str, List[str]] = {}
    
    async def create_notification(
        self,
        type: NotificationType,
        title: str,
        message: str,
        user_id: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        operation_id: Optional[str] = None,
        metadata: Dict[str, Any] = None,
        expires_in_minutes: Optional[int] = None,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        send_immediately: bool = True
    ) -> Notification:
        """Cria uma nova notificação"""
        
        notification_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Calcula expiração se especificada
        expires_at = None
        if expires_in_minutes:
            expires_at = now.replace(
                minute=now.minute + expires_in_minutes
            )
        
        notification = Notification(
            id=notification_id,
            type=type,
            priority=priority,
            title=title,
            message=message,
            timestamp=now,
            user_id=user_id,
            operation_id=operation_id,
            metadata=metadata or {},
            expires_at=expires_at,
            action_url=action_url,
            action_label=action_label
        )
        
        # Armazena a notificação
        self.notifications[notification_id] = notification
        
        # Indexa por usuário
        if user_id:
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            self.user_notifications[user_id].append(notification_id)
        
        # Log da criação
        await logging_service.log(
            LogLevel.INFO,
            LogCategory.SYSTEM_OPERATION,
            f"Notificação criada: {title}",
            user_id=user_id,
            operation_id=operation_id,
            metadata={
                "notification_id": notification_id,
                "type": type.value,
                "priority": priority.value,
                "title": title
            }
        )
        
        # Envia imediatamente se solicitado
        if send_immediately:
            await self.send_notification(notification)
        
        return notification
    
    async def send_notification(self, notification: Notification):
        """Envia notificação via WebSocket"""
        message = {
            "type": "notification",
            "data": notification.dict()
        }
        
        if notification.user_id:
            # Notificação direcionada
            await self.connection_manager.send_to_user(
                notification.user_id,
                message
            )
        else:
            # Broadcast para todos
            await self.connection_manager.broadcast(message)
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Marca notificação como lida"""
        if notification_id in self.notifications:
            notification = self.notifications[notification_id]
            
            # Verifica se o usuário tem permissão
            if notification.user_id == user_id or notification.user_id is None:
                notification.read = True
                
                await logging_service.log_user_action(
                    action="notification_read",
                    user_id=user_id,
                    metadata={"notification_id": notification_id}
                )
                
                return True
        
        return False
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False,
        type_filter: NotificationType = None
    ) -> List[Notification]:
        """Recupera notificações de um usuário"""
        
        if user_id not in self.user_notifications:
            return []
        
        notifications = []
        for notification_id in reversed(self.user_notifications[user_id]):  # Mais recentes primeiro
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                
                # Aplica filtros
                if unread_only and notification.read:
                    continue
                if type_filter and notification.type != type_filter:
                    continue
                
                # Verifica expiração
                if (notification.expires_at and 
                    notification.expires_at < datetime.now(timezone.utc)):
                    continue
                
                notifications.append(notification)
                
                if len(notifications) >= limit:
                    break
        
        return notifications
    
    async def cleanup_expired_notifications(self):
        """Remove notificações expiradas"""
        now = datetime.now(timezone.utc)
        expired_ids = []
        
        for notification_id, notification in self.notifications.items():
            if (notification.expires_at and 
                notification.expires_at < now):
                expired_ids.append(notification_id)
        
        for notification_id in expired_ids:
            notification = self.notifications[notification_id]
            
            # Remove do índice do usuário
            if notification.user_id and notification.user_id in self.user_notifications:
                self.user_notifications[notification.user_id].remove(notification_id)
            
            # Remove da lista principal
            del self.notifications[notification_id]
        
        if expired_ids:
            await logging_service.log(
                LogLevel.INFO,
                LogCategory.SYSTEM_OPERATION,
                f"Removidas {len(expired_ids)} notificações expiradas"
            )
    
    # Métodos de conveniência para diferentes tipos de notificação
    async def notify_success(
        self,
        title: str,
        message: str,
        user_id: str = None,
        operation_id: str = None,
        action_url: str = None,
        action_label: str = None
    ) -> Notification:
        """Notificação de sucesso"""
        return await self.create_notification(
            type=NotificationType.SUCCESS,
            title=title,
            message=message,
            user_id=user_id,
            operation_id=operation_id,
            action_url=action_url,
            action_label=action_label
        )
    
    async def notify_error(
        self,
        title: str,
        message: str,
        user_id: str = None,
        operation_id: str = None,
        priority: NotificationPriority = NotificationPriority.HIGH
    ) -> Notification:
        """Notificação de erro"""
        return await self.create_notification(
            type=NotificationType.ERROR,
            title=title,
            message=message,
            user_id=user_id,
            operation_id=operation_id,
            priority=priority
        )
    
    async def notify_warning(
        self,
        title: str,
        message: str,
        user_id: str = None,
        operation_id: str = None
    ) -> Notification:
        """Notificação de aviso"""
        return await self.create_notification(
            type=NotificationType.WARNING,
            title=title,
            message=message,
            user_id=user_id,
            operation_id=operation_id
        )
    
    async def notify_info(
        self,
        title: str,
        message: str,
        user_id: str = None,
        operation_id: str = None
    ) -> Notification:
        """Notificação informativa"""
        return await self.create_notification(
            type=NotificationType.INFO,
            title=title,
            message=message,
            user_id=user_id,
            operation_id=operation_id
        )
    
    async def notify_progress(
        self,
        title: str,
        message: str,
        progress_percent: int,
        user_id: str = None,
        operation_id: str = None
    ) -> Notification:
        """Notificação de progresso"""
        return await self.create_notification(
            type=NotificationType.PROGRESS,
            title=title,
            message=message,
            user_id=user_id,
            operation_id=operation_id,
            metadata={"progress": progress_percent}
        )
    
    # Notificações específicas do domínio
    async def notify_video_processing_complete(
        self,
        video_name: str,
        download_url: str,
        user_id: str,
        operation_id: str = None
    ):
        """Notifica conclusão do processamento de vídeo"""
        await self.notify_success(
            title="Vídeo Processado! 🎬",
            message=f"O vídeo '{video_name}' foi processado com sucesso e está pronto para download.",
            user_id=user_id,
            operation_id=operation_id,
            action_url=download_url,
            action_label="Baixar Vídeo"
        )
    
    async def notify_video_processing_failed(
        self,
        video_name: str,
        error_details: str,
        user_id: str,
        operation_id: str = None
    ):
        """Notifica falha no processamento de vídeo"""
        await self.notify_error(
            title="Erro no Processamento ❌",
            message=f"Falha ao processar o vídeo '{video_name}': {error_details}",
            user_id=user_id,
            operation_id=operation_id,
            priority=NotificationPriority.HIGH
        )
    
    async def notify_ai_generation_complete(
        self,
        generation_type: str,
        result_description: str,
        user_id: str,
        operation_id: str = None,
        action_url: str = None
    ):
        """Notifica conclusão de geração IA"""
        await self.notify_success(
            title=f"{generation_type} Gerado! ✨",
            message=result_description,
            user_id=user_id,
            operation_id=operation_id,
            action_url=action_url,
            action_label="Ver Resultado"
        )
    
    async def notify_export_ready(
        self,
        export_type: str,
        download_url: str,
        user_id: str,
        expires_in_hours: int = 24
    ):
        """Notifica que exportação está pronta"""
        await self.create_notification(
            type=NotificationType.SUCCESS,
            title="Exportação Concluída! 📦",
            message=f"Sua exportação ({export_type}) está pronta para download.",
            user_id=user_id,
            action_url=download_url,
            action_label="Baixar Arquivo",
            expires_in_minutes=expires_in_hours * 60
        )

# Instância global do serviço
notification_service = NotificationService()

# Task para limpeza automática de notificações expiradas
async def cleanup_notifications_task():
    """Task executada periodicamente para limpar notificações expiradas"""
    while True:
        try:
            await notification_service.cleanup_expired_notifications()
            await asyncio.sleep(3600)  # Executa a cada hora
        except Exception as e:
            await logging_service.log_error(e, LogCategory.SYSTEM_OPERATION) 