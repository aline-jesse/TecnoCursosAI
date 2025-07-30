"""
Sistema de Notificações em Tempo Real - TecnoCursos AI
WebSockets, email, SMS e notificações push
"""

import asyncio
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Any, Optional, Set, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
from collections import defaultdict
import aiohttp
import websockets
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

from ..core.logging import get_logger
from ..core.cache import cache_manager
from ..core.settings import get_settings

logger = get_logger("notifications")
settings = get_settings()

class NotificationType(str, Enum):
    """Tipos de notificação"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"
    USER_ACTION = "user_action"
    PROGRESS = "progress"

class NotificationPriority(str, Enum):
    """Prioridades de notificação"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    """Canais de notificação"""
    WEBSOCKET = "websocket"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    DATABASE = "database"

@dataclass
class NotificationTemplate:
    """Template de notificação"""
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    channels: List[NotificationChannel]
    email_template: Optional[str] = None
    sms_template: Optional[str] = None
    variables: Dict[str, Any] = None

@dataclass
class Notification:
    """Modelo de notificação"""
    id: str
    user_id: Optional[str]
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    channels: List[NotificationChannel]
    data: Dict[str, Any]
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"  # pending, sent, failed, expired

class WebSocketManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        # Conexões ativas: user_id -> conjunto de WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, metadata: Dict[str, Any] = None):
        """Conecta cliente WebSocket"""
        await websocket.accept()
        
        self.active_connections[user_id].add(websocket)
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        logger.info(f"WebSocket connected for user {user_id}")
        
        # Enviar notificações pendentes
        await self._send_pending_notifications(user_id, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Desconecta cliente WebSocket"""
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket]["user_id"]
            
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Envia mensagem para todos os WebSockets de um usuário"""
        if user_id not in self.active_connections:
            return False
        
        dead_connections = set()
        message_json = json.dumps(message, default=str)
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(message_json)
            except WebSocketDisconnect:
                dead_connections.add(websocket)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                dead_connections.add(websocket)
        
        # Remover conexões mortas
        for websocket in dead_connections:
            self.disconnect(websocket)
        
        return len(self.active_connections.get(user_id, [])) > 0
    
    async def broadcast(self, message: Dict[str, Any], user_filter: Callable = None):
        """Envia mensagem broadcast para todos os usuários conectados"""
        message_json = json.dumps(message, default=str)
        sent_count = 0
        
        for user_id, websockets in self.active_connections.items():
            # Aplicar filtro se fornecido
            if user_filter and not user_filter(user_id):
                continue
            
            dead_connections = set()
            
            for websocket in websockets:
                try:
                    await websocket.send_text(message_json)
                    sent_count += 1
                except WebSocketDisconnect:
                    dead_connections.add(websocket)
                except Exception as e:
                    logger.error(f"Error broadcasting WebSocket message: {e}")
                    dead_connections.add(websocket)
            
            # Remover conexões mortas
            for websocket in dead_connections:
                self.disconnect(websocket)
        
        return sent_count
    
    async def _send_pending_notifications(self, user_id: str, websocket: WebSocket):
        """Envia notificações pendentes para usuário recém-conectado"""
        try:
            # Buscar notificações pendentes do cache
            pending_key = f"notifications:pending:{user_id}"
            pending_notifications = await cache_manager.get(pending_key, [])
            
            for notification_data in pending_notifications:
                try:
                    await websocket.send_text(json.dumps(notification_data, default=str))
                except Exception as e:
                    logger.error(f"Error sending pending notification: {e}")
            
            # Limpar notificações pendentes após envio
            if pending_notifications:
                await cache_manager.delete(pending_key)
                
        except Exception as e:
            logger.error(f"Error sending pending notifications: {e}")
    
    def get_active_users(self) -> List[str]:
        """Retorna lista de usuários ativos"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Retorna número total de conexões ativas"""
        return sum(len(connections) for connections in self.active_connections.values())

class EmailProvider:
    """Provedor de email SMTP"""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'smtp_host', 'localhost')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
        self.email_from = getattr(settings, 'email_from', 'noreply@tecnocursos.ai')
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Envia email"""
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            # Adicionar corpo em texto simples
            part1 = MimeText(body, 'plain', 'utf-8')
            msg.attach(part1)
            
            # Adicionar corpo HTML se fornecido
            if html_body:
                part2 = MimeText(html_body, 'html', 'utf-8')
                msg.attach(part2)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

class SlackProvider:
    """Provedor de notificações Slack"""
    
    def __init__(self):
        self.webhook_url = getattr(settings, 'slack_webhook_url', None)
    
    async def send_slack_message(self, message: str, channel: str = None) -> bool:
        """Envia mensagem para Slack"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            payload = {
                "text": message,
                "username": "TecnoCursos AI",
                "icon_emoji": ":robot_face:"
            }
            
            if channel:
                payload["channel"] = channel
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    success = response.status == 200
                    
                    if success:
                        logger.info("Slack message sent successfully")
                    else:
                        logger.error(f"Failed to send Slack message: {response.status}")
                    
                    return success
                    
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False

class NotificationManager:
    """Gerenciador principal de notificações"""
    
    def __init__(self):
        self.websocket_manager = WebSocketManager()
        self.email_provider = EmailProvider()
        self.slack_provider = SlackProvider()
        
        # Queue de notificações para processamento
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
        # Templates de notificação
        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_default_templates()
        
        # Redis para notificações distribuídas
        self.redis_client: Optional[redis.Redis] = None
        self._init_redis()
    
    def _init_redis(self):
        """Inicializa conexão Redis para pub/sub"""
        try:
            redis_url = getattr(settings.redis, 'url', None)
            if redis_url:
                self.redis_client = redis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Could not connect to Redis for notifications: {e}")
    
    def _load_default_templates(self):
        """Carrega templates padrão de notificação"""
        self.templates.update({
            "user_registered": NotificationTemplate(
                title="Bem-vindo ao TecnoCursos AI!",
                message="Sua conta foi criada com sucesso. Comece criando seu primeiro projeto.",
                type=NotificationType.SUCCESS,
                priority=NotificationPriority.NORMAL,
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET],
                email_template="welcome_email.html"
            ),
            "project_created": NotificationTemplate(
                title="Projeto criado",
                message="Seu projeto '{project_name}' foi criado com sucesso.",
                type=NotificationType.SUCCESS,
                priority=NotificationPriority.NORMAL,
                channels=[NotificationChannel.WEBSOCKET]
            ),
            "video_generation_started": NotificationTemplate(
                title="Geração de vídeo iniciada",
                message="A geração do vídeo '{video_title}' foi iniciada.",
                type=NotificationType.INFO,
                priority=NotificationPriority.NORMAL,
                channels=[NotificationChannel.WEBSOCKET]
            ),
            "video_generation_completed": NotificationTemplate(
                title="Vídeo gerado com sucesso!",
                message="Seu vídeo '{video_title}' foi gerado e está disponível para download.",
                type=NotificationType.SUCCESS,
                priority=NotificationPriority.HIGH,
                channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL]
            ),
            "video_generation_failed": NotificationTemplate(
                title="Falha na geração de vídeo",
                message="Houve um erro ao gerar o vídeo '{video_title}'. Tente novamente.",
                type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL]
            ),
            "system_maintenance": NotificationTemplate(
                title="Manutenção programada",
                message="O sistema entrará em manutenção em {maintenance_time}.",
                type=NotificationType.WARNING,
                priority=NotificationPriority.HIGH,
                channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            "backup_completed": NotificationTemplate(
                title="Backup concluído",
                message="Backup do sistema concluído com sucesso em {backup_time}.",
                type=NotificationType.SYSTEM,
                priority=NotificationPriority.LOW,
                channels=[NotificationChannel.SLACK]
            )
        })
    
    async def start(self):
        """Inicia processamento de notificações"""
        if self.processing_task is None or self.processing_task.done():
            self.processing_task = asyncio.create_task(self._process_notification_queue())
            logger.info("Notification manager started")
    
    async def stop(self):
        """Para processamento de notificações"""
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            logger.info("Notification manager stopped")
    
    async def send_notification(
        self,
        template_name: str,
        user_id: Optional[str] = None,
        variables: Dict[str, Any] = None,
        channels: List[NotificationChannel] = None,
        priority: NotificationPriority = None
    ) -> str:
        """Envia notificação usando template"""
        
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")
        
        template = self.templates[template_name]
        variables = variables or {}
        
        # Criar notificação
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=template.title.format(**variables),
            message=template.message.format(**variables),
            type=template.type,
            priority=priority or template.priority,
            channels=channels or template.channels,
            data=variables,
            created_at=datetime.utcnow()
        )
        
        # Adicionar à queue para processamento
        await self.notification_queue.put(notification)
        
        return notification.id
    
    async def send_custom_notification(
        self,
        title: str,
        message: str,
        user_id: Optional[str] = None,
        type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: List[NotificationChannel] = None,
        data: Dict[str, Any] = None
    ) -> str:
        """Envia notificação customizada"""
        
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            priority=priority,
            channels=channels or [NotificationChannel.WEBSOCKET],
            data=data or {},
            created_at=datetime.utcnow()
        )
        
        await self.notification_queue.put(notification)
        return notification.id
    
    async def _process_notification_queue(self):
        """Processa queue de notificações"""
        while True:
            try:
                # Buscar próxima notificação
                notification = await self.notification_queue.get()
                
                # Processar notificação
                await self._process_notification(notification)
                
                # Marcar como processada
                self.notification_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
                await asyncio.sleep(1)  # Evitar loop infinito em caso de erro
    
    async def _process_notification(self, notification: Notification):
        """Processa uma notificação individual"""
        try:
            success_channels = []
            failed_channels = []
            
            for channel in notification.channels:
                try:
                    success = await self._send_to_channel(notification, channel)
                    if success:
                        success_channels.append(channel)
                    else:
                        failed_channels.append(channel)
                except Exception as e:
                    logger.error(f"Error sending notification to {channel}: {e}")
                    failed_channels.append(channel)
            
            # Atualizar status da notificação
            if success_channels:
                notification.sent_at = datetime.utcnow()
                notification.status = "sent" if not failed_channels else "partial"
            else:
                notification.status = "failed"
                notification.retry_count += 1
            
            # Salvar notificação no cache/banco
            await self._save_notification(notification)
            
            # Retry se necessário
            if failed_channels and notification.retry_count < notification.max_retries:
                notification.channels = failed_channels
                await asyncio.sleep(2 ** notification.retry_count)  # Backoff exponencial
                await self.notification_queue.put(notification)
            
        except Exception as e:
            logger.error(f"Error processing notification {notification.id}: {e}")
    
    async def _send_to_channel(self, notification: Notification, channel: NotificationChannel) -> bool:
        """Envia notificação para um canal específico"""
        
        if channel == NotificationChannel.WEBSOCKET:
            return await self._send_websocket(notification)
        
        elif channel == NotificationChannel.EMAIL:
            return await self._send_email(notification)
        
        elif channel == NotificationChannel.SLACK:
            return await self._send_slack(notification)
        
        elif channel == NotificationChannel.DATABASE:
            return await self._save_to_database(notification)
        
        else:
            logger.warning(f"Unsupported notification channel: {channel}")
            return False
    
    async def _send_websocket(self, notification: Notification) -> bool:
        """Envia notificação via WebSocket"""
        message = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type.value,
            "priority": notification.priority.value,
            "data": notification.data,
            "timestamp": notification.created_at.isoformat()
        }
        
        if notification.user_id:
            # Enviar para usuário específico
            sent = await self.websocket_manager.send_to_user(notification.user_id, message)
            
            # Se usuário não está conectado, salvar para entrega posterior
            if not sent:
                await self._save_pending_notification(notification.user_id, message)
                return True  # Consideramos sucesso mesmo se salvo para depois
            
            return sent
        else:
            # Broadcast para todos os usuários
            sent_count = await self.websocket_manager.broadcast(message)
            return sent_count > 0
    
    async def _send_email(self, notification: Notification) -> bool:
        """Envia notificação via email"""
        if not notification.user_id:
            return False
        
        # Buscar email do usuário (implementar busca no banco)
        user_email = await self._get_user_email(notification.user_id)
        if not user_email:
            return False
        
        # Corpo do email
        body = f"{notification.title}\n\n{notification.message}"
        
        # HTML body se disponível
        html_body = None
        template_name = notification.data.get('email_template')
        if template_name:
            html_body = await self._render_email_template(template_name, notification.data)
        
        return await self.email_provider.send_email(
            user_email,
            notification.title,
            body,
            html_body
        )
    
    async def _send_slack(self, notification: Notification) -> bool:
        """Envia notificação via Slack"""
        message = f"*{notification.title}*\n{notification.message}"
        
        if notification.priority == NotificationPriority.URGENT:
            message = f"🚨 {message}"
        elif notification.type == NotificationType.ERROR:
            message = f"❌ {message}"
        elif notification.type == NotificationType.SUCCESS:
            message = f"✅ {message}"
        elif notification.type == NotificationType.WARNING:
            message = f"⚠️ {message}"
        
        return await self.slack_provider.send_slack_message(message)
    
    async def _save_pending_notification(self, user_id: str, message: Dict[str, Any]):
        """Salva notificação pendente para usuário offline"""
        pending_key = f"notifications:pending:{user_id}"
        pending_notifications = await cache_manager.get(pending_key, [])
        
        # Limitar número de notificações pendentes
        if len(pending_notifications) >= 100:
            pending_notifications = pending_notifications[-99:]
        
        pending_notifications.append(message)
        await cache_manager.set(pending_key, pending_notifications, ttl=86400)  # 24 horas
    
    async def _save_notification(self, notification: Notification):
        """Salva notificação no cache para histórico"""
        notification_key = f"notification:{notification.id}"
        await cache_manager.set(notification_key, asdict(notification), ttl=604800)  # 7 dias
        
        # Adicionar ao histórico do usuário se aplicável
        if notification.user_id:
            history_key = f"notifications:history:{notification.user_id}"
            history = await cache_manager.get(history_key, [])
            
            # Manter apenas últimas 50 notificações
            if len(history) >= 50:
                history = history[-49:]
            
            history.append(notification.id)
            await cache_manager.set(history_key, history, ttl=604800)
    
    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Busca email do usuário (implementar conforme necessário)"""
        # Implementar busca no banco de dados
        # Por enquanto, retornar None
        return None
    
    async def _render_email_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Renderiza template de email (implementar conforme necessário)"""
        # Implementar renderização de templates
        return None
    
    async def get_user_notifications(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca notificações do usuário"""
        history_key = f"notifications:history:{user_id}"
        notification_ids = await cache_manager.get(history_key, [])
        
        notifications = []
        for notification_id in notification_ids[-limit:]:
            notification_key = f"notification:{notification_id}"
            notification_data = await cache_manager.get(notification_key)
            if notification_data:
                notifications.append(notification_data)
        
        return list(reversed(notifications))  # Mais recentes primeiro

# Instância global do gerenciador
notification_manager = NotificationManager()

# Funções de conveniência
async def send_notification(template_name: str, user_id: str = None, **variables):
    """Envia notificação usando template"""
    return await notification_manager.send_notification(template_name, user_id, variables)

async def send_custom_notification(title: str, message: str, user_id: str = None, **kwargs):
    """Envia notificação customizada"""
    return await notification_manager.send_custom_notification(title, message, user_id, **kwargs)

async def connect_websocket(websocket: WebSocket, user_id: str, metadata: Dict[str, Any] = None):
    """Conecta WebSocket"""
    await notification_manager.websocket_manager.connect(websocket, user_id, metadata)

def disconnect_websocket(websocket: WebSocket):
    """Desconecta WebSocket"""
    notification_manager.websocket_manager.disconnect(websocket)

async def get_user_notifications(user_id: str, limit: int = 20):
    """Busca notificações do usuário"""
    return await notification_manager.get_user_notifications(user_id, limit)

async def start_notification_system():
    """Inicia sistema de notificações"""
    await notification_manager.start()

async def stop_notification_system():
    """Para sistema de notificações"""
    await notification_manager.stop()
