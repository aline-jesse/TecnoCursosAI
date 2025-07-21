"""
Sistema completo de notificações para TecnoCursos AI
Inclui emails, WebSocket em tempo real, alertas do sistema e templates customizados
"""

import asyncio
import json
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import jinja2
import aioredis
import websockets
from sqlalchemy.orm import Session

from app.config import get_settings
from app.logger import get_logger, log_business_event, log_performance_metric
from app.database import get_db
from app.models import User, FileUpload, Project

settings = get_settings()
logger = get_logger("notification_service")

class NotificationType(Enum):
    """Tipos de notificação"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    UPLOAD_COMPLETE = "upload_complete"
    PROCESSING_COMPLETE = "processing_complete"
    PROCESSING_ERROR = "processing_error"
    SYSTEM_ALERT = "system_alert"
    SECURITY_ALERT = "security_alert"
    QUOTA_WARNING = "quota_warning"
    WELCOME = "welcome"

class NotificationChannel(Enum):
    """Canais de notificação"""
    EMAIL = "email"
    WEBSOCKET = "websocket"
    DATABASE = "database"
    PUSH = "push"
    SMS = "sms"

@dataclass
class NotificationTemplate:
    """Template de notificação"""
    subject: str
    html_template: str
    text_template: str
    variables: Dict[str, Any]

@dataclass
class Notification:
    """Estrutura de notificação"""
    id: str
    user_id: int
    type: NotificationType
    channel: NotificationChannel
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    template: Optional[str] = None
    priority: int = 1  # 1=baixa, 2=média, 3=alta, 4=crítica
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=30)

class NotificationService:
    """Serviço principal de notificações"""
    
    def __init__(self):
        self.templates_dir = Path("templates/notifications")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # WebSocket connections
        self.websocket_connections: Dict[int, set] = {}
        
        # Queue de notificações
        self.notification_queue = asyncio.Queue()
        
        # Redis para cache e pub/sub
        self.redis = None
        
        # Workers de processamento
        self.workers_running = False
        
        # Statistics
        self.stats = {
            'total_sent': 0,
            'email_sent': 0,
            'websocket_sent': 0,
            'failed_deliveries': 0,
            'retry_count': 0
        }
    
    async def initialize(self):
        """Inicializar serviço"""
        try:
            # Conectar ao Redis se disponível
            try:
                self.redis = await aioredis.from_url("redis://localhost:6379")
                logger.info("Conectado ao Redis para notificações")
            except Exception as e:
                logger.warning(f"Redis não disponível: {e}")
            
            # Criar templates padrão
            await self.create_default_templates()
            
            # Iniciar workers
            await self.start_workers()
            
            logger.info("Serviço de notificações inicializado")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar serviço de notificações: {e}")
    
    async def create_default_templates(self):
        """Criar templates padrão"""
        templates = {
            "welcome.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bem-vindo ao TecnoCursos AI</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #ddd; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .stats { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Bem-vindo ao TecnoCursos AI!</h1>
        </div>
        <div class="content">
            <h2>Olá, {{ user_name }}!</h2>
            <p>Ficamos felizes em tê-lo conosco. Sua conta foi criada com sucesso e você já pode começar a usar nossa plataforma.</p>
            
            <h3>O que você pode fazer:</h3>
            <ul>
                <li>📁 Fazer upload de arquivos PDF, PowerPoint e Word</li>
                <li>🔍 Buscar conteúdo dentro dos seus documentos</li>
                <li>📊 Visualizar estatísticas dos seus arquivos</li>
                <li>⚡ Processamento automático com IA</li>
            </ul>
            
            <div class="stats">
                <strong>Limites da sua conta:</strong><br>
                • Máximo de {{ max_files }} arquivos<br>
                • Até {{ max_storage }} de armazenamento<br>
                • {{ max_uploads_per_day }} uploads por dia
            </div>
            
            <a href="{{ dashboard_url }}" class="button">Acessar Dashboard</a>
        </div>
        <div class="footer">
            <p>TecnoCursos AI - Processamento Inteligente de Documentos</p>
            <p>Se você não criou esta conta, ignore este email.</p>
        </div>
    </div>
</body>
</html>""",

            "upload_complete.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Upload Concluído</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #27ae60; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #ddd; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }
        .file-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Upload Concluído!</h1>
        </div>
        <div class="content">
            <p>Olá, {{ user_name }}!</p>
            <p class="success">Seu arquivo foi enviado com sucesso!</p>
            
            <div class="file-info">
                <strong>Detalhes do arquivo:</strong><br>
                • Nome: {{ filename }}<br>
                • Tamanho: {{ file_size }}<br>
                • Tipo: {{ file_type }}<br>
                • Projeto: {{ project_name }}<br>
                • Data: {{ upload_date }}
            </div>
            
            {% if processing_started %}
            <p>🔄 O processamento automático foi iniciado. Você receberá uma notificação quando estiver concluído.</p>
            {% endif %}
        </div>
        <div class="footer">
            <p>TecnoCursos AI</p>
        </div>
    </div>
</body>
</html>""",

            "processing_complete.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Processamento Concluído</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #3498db; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #ddd; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }
        .stats { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .button { display: inline-block; background: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Processamento Concluído!</h1>
        </div>
        <div class="content">
            <p>Olá, {{ user_name }}!</p>
            <p>O processamento do arquivo <strong>{{ filename }}</strong> foi concluído com sucesso!</p>
            
            <div class="stats">
                <strong>Resultados do processamento:</strong><br>
                • Páginas processadas: {{ page_count }}<br>
                • Palavras extraídas: {{ word_count }}<br>
                • Caracteres: {{ character_count }}<br>
                • Tempo de processamento: {{ processing_time }}
                {% if thumbnail_created %}
                <br>• Thumbnail criado ✅
                {% endif %}
            </div>
            
            <p>Agora você pode:</p>
            <ul>
                <li>🔍 Buscar texto dentro do documento</li>
                <li>📄 Visualizar o conteúdo extraído</li>
                <li>📊 Ver estatísticas detalhadas</li>
            </ul>
            
            <a href="{{ file_url }}" class="button">Ver Arquivo</a>
            <a href="{{ dashboard_url }}" class="button">Ir para Dashboard</a>
        </div>
        <div class="footer">
            <p>TecnoCursos AI</p>
        </div>
    </div>
</body>
</html>""",

            "processing_error.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Erro no Processamento</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #e74c3c; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #ddd; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }
        .error-info { background: #fdf2f2; padding: 15px; border-left: 4px solid #e74c3c; margin: 15px 0; }
        .button { display: inline-block; background: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>❌ Erro no Processamento</h1>
        </div>
        <div class="content">
            <p>Olá, {{ user_name }}!</p>
            <p>Infelizmente ocorreu um erro durante o processamento do arquivo <strong>{{ filename }}</strong>.</p>
            
            <div class="error-info">
                <strong>Detalhes do erro:</strong><br>
                {{ error_message }}
            </div>
            
            <p><strong>O que fazer agora:</strong></p>
            <ul>
                <li>Verifique se o arquivo não está corrompido</li>
                <li>Tente fazer o upload novamente</li>
                <li>Entre em contato conosco se o problema persistir</li>
            </ul>
            
            <a href="{{ dashboard_url }}" class="button">Voltar ao Dashboard</a>
        </div>
        <div class="footer">
            <p>TecnoCursos AI - Suporte: suporte@tecnocursos.ai</p>
        </div>
    </div>
</body>
</html>""",

            "system_alert.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Alerta do Sistema</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f39c12; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #ddd; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }
        .alert-info { background: #fef9e7; padding: 15px; border-left: 4px solid #f39c12; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ {{ alert_title }}</h1>
        </div>
        <div class="content">
            <p>Olá, {{ user_name }}!</p>
            
            <div class="alert-info">
                <strong>{{ alert_type }}</strong><br>
                {{ alert_message }}
            </div>
            
            {% if action_required %}
            <p><strong>Ação necessária:</strong></p>
            <p>{{ action_message }}</p>
            {% endif %}
            
            <p><em>Data: {{ alert_date }}</em></p>
        </div>
        <div class="footer">
            <p>TecnoCursos AI</p>
        </div>
    </div>
</body>
</html>"""
        }
        
        # Criar arquivos de template
        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                template_path.write_text(content, encoding='utf-8')
                logger.info(f"Template criado: {filename}")
    
    async def start_workers(self):
        """Iniciar workers de processamento"""
        if self.workers_running:
            return
        
        self.workers_running = True
        
        # Worker principal de processamento
        asyncio.create_task(self._notification_worker())
        
        # Worker de limpeza (remover notificações expiradas)
        asyncio.create_task(self._cleanup_worker())
        
        logger.info("Workers de notificação iniciados")
    
    async def _notification_worker(self):
        """Worker principal de processamento de notificações"""
        while self.workers_running:
            try:
                # Processar notificação da queue
                notification = await asyncio.wait_for(
                    self.notification_queue.get(), 
                    timeout=5.0
                )
                
                await self._process_notification(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erro no worker de notificações: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_worker(self):
        """Worker de limpeza de notificações expiradas"""
        while self.workers_running:
            try:
                # Limpeza a cada hora
                await asyncio.sleep(3600)
                await self._cleanup_expired_notifications()
                
            except Exception as e:
                logger.error(f"Erro no worker de limpeza: {e}")
    
    async def _process_notification(self, notification: Notification):
        """Processar uma notificação"""
        try:
            success = False
            
            if notification.channel == NotificationChannel.EMAIL:
                success = await self._send_email(notification)
            elif notification.channel == NotificationChannel.WEBSOCKET:
                success = await self._send_websocket(notification)
            elif notification.channel == NotificationChannel.DATABASE:
                success = await self._save_to_database(notification)
            
            if success:
                notification.sent_at = datetime.now()
                self.stats['total_sent'] += 1
                
                if notification.channel == NotificationChannel.EMAIL:
                    self.stats['email_sent'] += 1
                elif notification.channel == NotificationChannel.WEBSOCKET:
                    self.stats['websocket_sent'] += 1
                
                log_business_event(
                    "notification_sent",
                    {
                        "notification_id": notification.id,
                        "user_id": notification.user_id,
                        "type": notification.type.value,
                        "channel": notification.channel.value
                    }
                )
            else:
                # Retry logic
                if notification.retry_count < notification.max_retries:
                    notification.retry_count += 1
                    await asyncio.sleep(2 ** notification.retry_count)  # Exponential backoff
                    await self.notification_queue.put(notification)
                    self.stats['retry_count'] += 1
                else:
                    self.stats['failed_deliveries'] += 1
                    logger.error(f"Falha definitiva na entrega da notificação {notification.id}")
                    
        except Exception as e:
            logger.error(f"Erro ao processar notificação {notification.id}: {e}")
    
    async def _send_email(self, notification: Notification) -> bool:
        """Enviar notificação por email"""
        try:
            # Carregar dados do usuário
            with Session(get_db().bind) as db:
                user = db.query(User).filter(User.id == notification.user_id).first()
                if not user or not user.email:
                    logger.warning(f"Usuário {notification.user_id} não encontrado ou sem email")
                    return False
            
            # Preparar dados do template
            template_data = {
                'user_name': user.name or user.email.split('@')[0],
                'user_email': user.email,
                **notification.data or {}
            }
            
            # Renderizar template se especificado
            if notification.template:
                try:
                    template = self.jinja_env.get_template(notification.template)
                    html_content = template.render(**template_data)
                    subject = notification.title
                except Exception as e:
                    logger.error(f"Erro ao renderizar template {notification.template}: {e}")
                    html_content = notification.message
                    subject = notification.title
            else:
                html_content = notification.message
                subject = notification.title
            
            # Criar mensagem
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.email_from
            msg['To'] = user.email
            
            # Adicionar conteúdo
            text_part = MimeText(notification.message, 'plain', 'utf-8')
            html_part = MimeText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Enviar email
            if hasattr(settings, 'smtp_server') and settings.smtp_server:
                context = ssl.create_default_context()
                with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                    if settings.smtp_use_tls:
                        server.starttls(context=context)
                    if settings.smtp_username:
                        server.login(settings.smtp_username, settings.smtp_password)
                    
                    server.send_message(msg)
                    
                logger.info(f"Email enviado para {user.email}")
                return True
            else:
                # Log do email para desenvolvimento
                logger.info(f"Email simulado para {user.email}: {subject}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    async def _send_websocket(self, notification: Notification) -> bool:
        """Enviar notificação via WebSocket"""
        try:
            user_connections = self.websocket_connections.get(notification.user_id, set())
            
            if not user_connections:
                logger.debug(f"Usuário {notification.user_id} não possui conexões WebSocket ativas")
                return True  # Não é erro, usuário apenas não está online
            
            message = {
                'id': notification.id,
                'type': notification.type.value,
                'title': notification.title,
                'message': notification.message,
                'data': notification.data or {},
                'priority': notification.priority,
                'timestamp': notification.created_at.isoformat()
            }
            
            message_json = json.dumps(message)
            
            # Enviar para todas as conexões do usuário
            disconnected = set()
            for ws in user_connections:
                try:
                    await ws.send(message_json)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(ws)
                except Exception as e:
                    logger.error(f"Erro ao enviar WebSocket: {e}")
                    disconnected.add(ws)
            
            # Remover conexões desconectadas
            user_connections -= disconnected
            
            if not user_connections:
                del self.websocket_connections[notification.user_id]
            
            logger.debug(f"Notificação WebSocket enviada para usuário {notification.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação WebSocket: {e}")
            return False
    
    async def _save_to_database(self, notification: Notification) -> bool:
        """Salvar notificação no banco de dados"""
        try:
            # TODO: Implementar tabela de notificações
            # Por enquanto, apenas log
            logger.info(f"Notificação salva no DB: {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar notificação no DB: {e}")
            return False
    
    async def _cleanup_expired_notifications(self):
        """Limpar notificações expiradas"""
        try:
            # TODO: Implementar limpeza no banco de dados
            logger.info("Limpeza de notificações expiradas executada")
            
        except Exception as e:
            logger.error(f"Erro na limpeza de notificações: {e}")
    
    # Métodos públicos de envio
    
    async def send_notification(
        self, 
        user_id: int,
        notification_type: NotificationType,
        channel: NotificationChannel,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
        priority: int = 1
    ) -> str:
        """Enviar notificação"""
        notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}_{notification_type.value}"
        
        notification = Notification(
            id=notification_id,
            user_id=user_id,
            type=notification_type,
            channel=channel,
            title=title,
            message=message,
            data=data,
            template=template,
            priority=priority
        )
        
        await self.notification_queue.put(notification)
        
        logger.info(f"Notificação enfileirada: {notification_id}")
        return notification_id
    
    async def send_welcome_notification(self, user_id: int, user_data: Dict[str, Any]):
        """Enviar notificação de boas-vindas"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.WELCOME,
            channel=NotificationChannel.EMAIL,
            title="Bem-vindo ao TecnoCursos AI!",
            message="Sua conta foi criada com sucesso.",
            data={
                **user_data,
                'max_files': 1000,
                'max_storage': '10GB',
                'max_uploads_per_day': 50,
                'dashboard_url': f"{settings.base_url}/dashboard"
            },
            template="welcome.html",
            priority=2
        )
    
    async def send_upload_complete(self, user_id: int, file_data: Dict[str, Any]):
        """Notificar upload concluído"""
        # Email
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.UPLOAD_COMPLETE,
            channel=NotificationChannel.EMAIL,
            title="Upload concluído com sucesso",
            message=f"O arquivo {file_data.get('filename')} foi enviado com sucesso.",
            data=file_data,
            template="upload_complete.html",
            priority=1
        )
        
        # WebSocket para atualização em tempo real
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.UPLOAD_COMPLETE,
            channel=NotificationChannel.WEBSOCKET,
            title="Upload concluído",
            message=f"Arquivo {file_data.get('filename')} enviado com sucesso",
            data=file_data,
            priority=2
        )
    
    async def send_processing_complete(self, user_id: int, file_data: Dict[str, Any]):
        """Notificar processamento concluído"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PROCESSING_COMPLETE,
            channel=NotificationChannel.EMAIL,
            title="Processamento concluído",
            message=f"O arquivo {file_data.get('filename')} foi processado com sucesso.",
            data={
                **file_data,
                'file_url': f"{settings.base_url}/files/{file_data.get('file_id')}",
                'dashboard_url': f"{settings.base_url}/dashboard"
            },
            template="processing_complete.html",
            priority=2
        )
        
        # WebSocket
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PROCESSING_COMPLETE,
            channel=NotificationChannel.WEBSOCKET,
            title="Processamento concluído",
            message=f"Arquivo {file_data.get('filename')} processado",
            data=file_data,
            priority=3
        )
    
    async def send_processing_error(self, user_id: int, file_data: Dict[str, Any], error: str):
        """Notificar erro no processamento"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PROCESSING_ERROR,
            channel=NotificationChannel.EMAIL,
            title="Erro no processamento",
            message=f"Ocorreu um erro ao processar {file_data.get('filename')}.",
            data={
                **file_data,
                'error_message': error,
                'dashboard_url': f"{settings.base_url}/dashboard"
            },
            template="processing_error.html",
            priority=3
        )
        
        # WebSocket
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PROCESSING_ERROR,
            channel=NotificationChannel.WEBSOCKET,
            title="Erro no processamento",
            message=f"Erro ao processar {file_data.get('filename')}: {error}",
            data={'error': error, **file_data},
            priority=4
        )
    
    async def send_system_alert(self, user_id: int, alert_data: Dict[str, Any]):
        """Enviar alerta do sistema"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.SYSTEM_ALERT,
            channel=NotificationChannel.EMAIL,
            title=alert_data.get('title', 'Alerta do Sistema'),
            message=alert_data.get('message', ''),
            data={
                **alert_data,
                'alert_date': datetime.now().strftime('%d/%m/%Y %H:%M')
            },
            template="system_alert.html",
            priority=alert_data.get('priority', 3)
        )
    
    # WebSocket management
    
    async def add_websocket_connection(self, user_id: int, websocket):
        """Adicionar conexão WebSocket"""
        if user_id not in self.websocket_connections:
            self.websocket_connections[user_id] = set()
        
        self.websocket_connections[user_id].add(websocket)
        logger.info(f"Conexão WebSocket adicionada para usuário {user_id}")
    
    async def remove_websocket_connection(self, user_id: int, websocket):
        """Remover conexão WebSocket"""
        if user_id in self.websocket_connections:
            self.websocket_connections[user_id].discard(websocket)
            
            if not self.websocket_connections[user_id]:
                del self.websocket_connections[user_id]
        
        logger.info(f"Conexão WebSocket removida para usuário {user_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do serviço"""
        return {
            **self.stats,
            'active_websocket_users': len(self.websocket_connections),
            'total_websocket_connections': sum(len(connections) for connections in self.websocket_connections.values()),
            'queue_size': self.notification_queue.qsize()
        }

# Instância global do serviço
notification_service = NotificationService()

# Funções de conveniência
async def send_welcome_notification(user_id: int, user_data: Dict[str, Any]):
    """Função de conveniência para notificação de boas-vindas"""
    await notification_service.send_welcome_notification(user_id, user_data)

async def send_upload_complete(user_id: int, file_data: Dict[str, Any]):
    """Função de conveniência para upload concluído"""
    await notification_service.send_upload_complete(user_id, file_data)

async def send_processing_complete(user_id: int, file_data: Dict[str, Any]):
    """Função de conveniência para processamento concluído"""
    await notification_service.send_processing_complete(user_id, file_data)

async def send_processing_error(user_id: int, file_data: Dict[str, Any], error: str):
    """Função de conveniência para erro no processamento"""
    await notification_service.send_processing_error(user_id, file_data, error)

async def send_system_alert(user_id: int, alert_data: Dict[str, Any]):
    """Função de conveniência para alerta do sistema"""
    await notification_service.send_system_alert(user_id, alert_data) 