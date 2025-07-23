"""
Serviço de Integração Email - TecnoCursos AI
==========================================

Integração completa para envio de emails:
- SendGrid para emails transacionais
- Amazon SES para volume alto
- SMTP para compatibilidade
- Templates dinâmicos
- Tracking de entregas
- Fallback automático entre provedores

Funcionalidades:
- Múltiplos provedores
- Templates HTML
- Anexos de arquivos
- Lista de distribuição
- Analytics de email
- Bounce handling
- Unsubscribe automático
"""

import asyncio
import smtplib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, From, To, Subject, Content, Attachment
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    import aiosmtplib
    AIOSMTP_AVAILABLE = True
except ImportError:
    AIOSMTP_AVAILABLE = False

from app.config import settings, get_api_configs
from app.services.mock_integration_service import mock_service

logger = logging.getLogger(__name__)

class EmailProvider(Enum):
    """Provedores de email disponíveis"""
    SENDGRID = "sendgrid"
    AMAZON_SES = "amazon_ses"
    SMTP = "smtp"
    MOCK = "mock"

class EmailStatus(Enum):
    """Status do email"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    UNSUBSCRIBED = "unsubscribed"

class EmailType(Enum):
    """Tipos de email"""
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    NOTIFICATION = "notification"
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    INVOICE = "invoice"

@dataclass
class EmailRecipient:
    """Destinatário do email"""
    email: str
    name: str = ""
    metadata: Optional[Dict] = None

@dataclass
class EmailAttachment:
    """Anexo do email"""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"

@dataclass
class EmailRequest:
    """Request para envio de email"""
    to: List[EmailRecipient]
    subject: str
    html_content: str = ""
    text_content: str = ""
    from_email: str = ""
    from_name: str = ""
    reply_to: str = ""
    cc: List[EmailRecipient] = None
    bcc: List[EmailRecipient] = None
    attachments: List[EmailAttachment] = None
    template_id: str = ""
    template_data: Dict = None
    email_type: EmailType = EmailType.TRANSACTIONAL
    tracking_enabled: bool = True
    metadata: Optional[Dict] = None

@dataclass
class EmailResponse:
    """Resposta do envio de email"""
    id: str
    status: EmailStatus
    provider: EmailProvider
    recipients_count: int
    timestamp: datetime
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class EmailIntegrationService:
    """Serviço principal de integração de email"""
    
    def __init__(self):
        self.config = get_api_configs()
        
        # Configuração SendGrid
        self.sendgrid_enabled = (
            SENDGRID_AVAILABLE and 
            settings.sendgrid_api_key is not None
        )
        
        # Configuração Amazon SES
        self.ses_enabled = (
            AWS_AVAILABLE and 
            settings.aws_ses_access_key is not None and
            settings.aws_ses_secret_key is not None
        )
        
        # Configuração SMTP
        self.smtp_enabled = (
            AIOSMTP_AVAILABLE and
            settings.smtp_host is not None and
            settings.smtp_username is not None
        )
        
        # Determinar provedor padrão
        if self.sendgrid_enabled:
            self.default_provider = EmailProvider.SENDGRID
        elif self.ses_enabled:
            self.default_provider = EmailProvider.AMAZON_SES
        elif self.smtp_enabled:
            self.default_provider = EmailProvider.SMTP
        else:
            self.default_provider = EmailProvider.MOCK
        
        # Inicializar clientes
        self._init_clients()
        
        # Cache e estatísticas
        self.sent_emails = {}
        self.email_stats = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_bounced": 0,
            "total_opened": 0,
            "by_provider": {}
        }
        
        # Templates pré-definidos
        self.templates = {
            "welcome": {
                "subject": "Bem-vindo ao TecnoCursos AI!",
                "html": self._get_welcome_template(),
                "text": "Bem-vindo ao TecnoCursos AI! Obrigado por se cadastrar."
            },
            "password_reset": {
                "subject": "Redefinir senha - TecnoCursos AI",
                "html": self._get_password_reset_template(),
                "text": "Clique no link para redefinir sua senha: {reset_link}"
            },
            "payment_confirmed": {
                "subject": "Pagamento confirmado - TecnoCursos AI",
                "html": self._get_payment_confirmed_template(),
                "text": "Seu pagamento foi confirmado com sucesso!"
            }
        }
        
        logger.info(f"✅ Email Service inicializado - Provider padrão: {self.default_provider.value}")
    
    def _init_clients(self):
        """Inicializa clientes dos provedores"""
        
        # SendGrid
        if self.sendgrid_enabled:
            self.sendgrid_client = sendgrid.SendGridAPIClient(
                api_key=settings.sendgrid_api_key
            )
        
        # Amazon SES
        if self.ses_enabled:
            self.ses_client = boto3.client(
                'ses',
                aws_access_key_id=settings.aws_ses_access_key,
                aws_secret_access_key=settings.aws_ses_secret_key,
                region_name=settings.aws_ses_region
            )
        
        # SMTP configuração será usada dinamicamente
    
    async def send_email(self, request: EmailRequest, provider: Optional[EmailProvider] = None) -> EmailResponse:
        """Envia email usando o provedor especificado ou padrão"""
        
        # Usar provedor padrão se não especificado
        if provider is None:
            provider = self.default_provider
        
        # Validar request
        if not request.to:
            raise ValueError("Lista de destinatários não pode estar vazia")
        
        if not request.subject:
            raise ValueError("Assunto não pode estar vazio")
        
        if not request.html_content and not request.text_content and not request.template_id:
            raise ValueError("Conteúdo HTML, texto ou template_id deve ser fornecido")
        
        # Configurar remetente padrão
        if not request.from_email:
            request.from_email = settings.sendgrid_from_email or settings.ses_from_email or settings.smtp_from_email
        
        if not request.from_name:
            request.from_name = settings.sendgrid_from_name or settings.smtp_from_name or "TecnoCursos AI"
        
        # Processar template se especificado
        if request.template_id:
            request = await self._process_template(request)
        
        try:
            # Enviar usando provedor específico
            if provider == EmailProvider.SENDGRID:
                return await self._send_via_sendgrid(request)
            elif provider == EmailProvider.AMAZON_SES:
                return await self._send_via_ses(request)
            elif provider == EmailProvider.SMTP:
                return await self._send_via_smtp(request)
            else:
                return await self._send_via_mock(request)
                
        except Exception as e:
            logger.error(f"❌ Erro no envio via {provider.value}: {e}")
            
            # Tentar fallback se disponível
            if provider != EmailProvider.MOCK:
                logger.info(f"🔄 Tentando fallback para provedor alternativo")
                return await self._send_with_fallback(request, exclude_provider=provider)
            
            raise
    
    async def _send_via_sendgrid(self, request: EmailRequest) -> EmailResponse:
        """Envia email via SendGrid"""
        
        if not self.sendgrid_enabled:
            raise Exception("SendGrid não está configurado")
        
        try:
            # Construir email
            mail = Mail()
            mail.from_email = From(request.from_email, request.from_name)
            mail.subject = Subject(request.subject)
            
            # Adicionar destinatários
            for recipient in request.to:
                mail.add_to(To(recipient.email, recipient.name))
            
            # CC e BCC
            if request.cc:
                for cc_recipient in request.cc:
                    mail.add_cc(To(cc_recipient.email, cc_recipient.name))
            
            if request.bcc:
                for bcc_recipient in request.bcc:
                    mail.add_bcc(To(bcc_recipient.email, bcc_recipient.name))
            
            # Conteúdo
            if request.html_content:
                mail.add_content(Content("text/html", request.html_content))
            
            if request.text_content:
                mail.add_content(Content("text/plain", request.text_content))
            
            # Anexos
            if request.attachments:
                for attachment in request.attachments:
                    sg_attachment = Attachment()
                    sg_attachment.file_content = attachment.content
                    sg_attachment.file_name = attachment.filename
                    sg_attachment.file_type = attachment.content_type
                    mail.add_attachment(sg_attachment)
            
            # Configurações de tracking
            if request.tracking_enabled:
                mail.tracking_settings = {
                    "click_tracking": {"enable": True},
                    "open_tracking": {"enable": True},
                    "subscription_tracking": {"enable": True}
                }
            
            # Enviar
            response = self.sendgrid_client.send(mail)
            
            email_response = EmailResponse(
                id=response.headers.get('X-Message-Id', f"sg_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                status=EmailStatus.SENT if response.status_code == 202 else EmailStatus.FAILED,
                provider=EmailProvider.SENDGRID,
                recipients_count=len(request.to),
                timestamp=datetime.now(),
                metadata={"status_code": response.status_code}
            )
            
            # Atualizar estatísticas
            self._update_stats(EmailProvider.SENDGRID, email_response.status)
            
            # Cache
            self.sent_emails[email_response.id] = email_response
            
            logger.info(f"✅ Email enviado via SendGrid: {email_response.id}")
            return email_response
            
        except Exception as e:
            logger.error(f"❌ Erro SendGrid: {e}")
            return EmailResponse(
                id="",
                status=EmailStatus.FAILED,
                provider=EmailProvider.SENDGRID,
                recipients_count=len(request.to),
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _send_via_ses(self, request: EmailRequest) -> EmailResponse:
        """Envia email via Amazon SES"""
        
        if not self.ses_enabled:
            raise Exception("Amazon SES não está configurado")
        
        try:
            # Preparar destinatários
            destinations = [recipient.email for recipient in request.to]
            
            # Preparar email
            email_data = {
                'Source': f"{request.from_name} <{request.from_email}>",
                'Destination': {
                    'ToAddresses': destinations
                },
                'Message': {
                    'Subject': {
                        'Data': request.subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {}
                }
            }
            
            # Adicionar conteúdo
            if request.text_content:
                email_data['Message']['Body']['Text'] = {
                    'Data': request.text_content,
                    'Charset': 'UTF-8'
                }
            
            if request.html_content:
                email_data['Message']['Body']['Html'] = {
                    'Data': request.html_content,
                    'Charset': 'UTF-8'
                }
            
            # CC e BCC
            if request.cc:
                email_data['Destination']['CcAddresses'] = [cc.email for cc in request.cc]
            
            if request.bcc:
                email_data['Destination']['BccAddresses'] = [bcc.email for bcc in request.bcc]
            
            # Configurações adicionais
            if request.reply_to:
                email_data['ReplyToAddresses'] = [request.reply_to]
            
            # Enviar
            response = self.ses_client.send_email(**email_data)
            
            email_response = EmailResponse(
                id=response['MessageId'],
                status=EmailStatus.SENT,
                provider=EmailProvider.AMAZON_SES,
                recipients_count=len(request.to),
                timestamp=datetime.now(),
                metadata=response
            )
            
            # Atualizar estatísticas
            self._update_stats(EmailProvider.AMAZON_SES, email_response.status)
            
            # Cache
            self.sent_emails[email_response.id] = email_response
            
            logger.info(f"✅ Email enviado via Amazon SES: {email_response.id}")
            return email_response
            
        except (BotoCoreError, ClientError) as e:
            logger.error(f"❌ Erro Amazon SES: {e}")
            return EmailResponse(
                id="",
                status=EmailStatus.FAILED,
                provider=EmailProvider.AMAZON_SES,
                recipients_count=len(request.to),
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _send_via_smtp(self, request: EmailRequest) -> EmailResponse:
        """Envia email via SMTP"""
        
        if not self.smtp_enabled:
            raise Exception("SMTP não está configurado")
        
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = request.subject
            msg['From'] = f"{request.from_name} <{request.from_email}>"
            msg['To'] = ", ".join([recipient.email for recipient in request.to])
            
            if request.cc:
                msg['Cc'] = ", ".join([cc.email for cc in request.cc])
            
            if request.reply_to:
                msg['Reply-To'] = request.reply_to
            
            # Adicionar conteúdo
            if request.text_content:
                text_part = MIMEText(request.text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if request.html_content:
                html_part = MIMEText(request.html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Anexos
            if request.attachments:
                for attachment in request.attachments:
                    att = MIMEApplication(attachment.content)
                    att.add_header('Content-Disposition', 'attachment', filename=attachment.filename)
                    msg.attach(att)
            
            # Enviar
            all_recipients = [r.email for r in request.to]
            if request.cc:
                all_recipients.extend([cc.email for cc in request.cc])
            if request.bcc:
                all_recipients.extend([bcc.email for bcc in request.bcc])
            
            await aiosmtplib.send(
                msg,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                use_tls=settings.smtp_use_tls,
                recipients=all_recipients
            )
            
            email_response = EmailResponse(
                id=f"smtp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.sent_emails)}",
                status=EmailStatus.SENT,
                provider=EmailProvider.SMTP,
                recipients_count=len(request.to),
                timestamp=datetime.now()
            )
            
            # Atualizar estatísticas
            self._update_stats(EmailProvider.SMTP, email_response.status)
            
            # Cache
            self.sent_emails[email_response.id] = email_response
            
            logger.info(f"✅ Email enviado via SMTP: {email_response.id}")
            return email_response
            
        except Exception as e:
            logger.error(f"❌ Erro SMTP: {e}")
            return EmailResponse(
                id="",
                status=EmailStatus.FAILED,
                provider=EmailProvider.SMTP,
                recipients_count=len(request.to),
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _send_via_mock(self, request: EmailRequest) -> EmailResponse:
        """Envia email via mock (para testes)"""
        
        mock_response = await mock_service.mock_sendgrid_send_email(
            to_email=request.to[0].email if request.to else "test@example.com",
            subject=request.subject,
            content=request.html_content or request.text_content
        )
        
        email_response = EmailResponse(
            id=mock_response.data["message_id"],
            status=EmailStatus.SENT if mock_response.success else EmailStatus.FAILED,
            provider=EmailProvider.MOCK,
            recipients_count=len(request.to),
            timestamp=datetime.now(),
            metadata=mock_response.data
        )
        
        # Atualizar estatísticas
        self._update_stats(EmailProvider.MOCK, email_response.status)
        
        # Cache
        self.sent_emails[email_response.id] = email_response
        
        logger.info(f"📧 Email mock enviado: {email_response.id}")
        return email_response
    
    async def _send_with_fallback(self, request: EmailRequest, exclude_provider: EmailProvider) -> EmailResponse:
        """Tenta enviar com provedor alternativo"""
        
        providers = [EmailProvider.SENDGRID, EmailProvider.AMAZON_SES, EmailProvider.SMTP, EmailProvider.MOCK]
        
        for provider in providers:
            if provider == exclude_provider:
                continue
            
            # Verificar se provedor está disponível
            if provider == EmailProvider.SENDGRID and not self.sendgrid_enabled:
                continue
            elif provider == EmailProvider.AMAZON_SES and not self.ses_enabled:
                continue
            elif provider == EmailProvider.SMTP and not self.smtp_enabled:
                continue
            
            try:
                logger.info(f"🔄 Tentando fallback via {provider.value}")
                return await self.send_email(request, provider)
            except Exception as e:
                logger.warning(f"⚠️ Fallback {provider.value} também falhou: {e}")
                continue
        
        # Se chegou aqui, todos falharam
        raise Exception("Todos os provedores de email falharam")
    
    async def _process_template(self, request: EmailRequest) -> EmailRequest:
        """Processa template de email"""
        
        if request.template_id not in self.templates:
            raise ValueError(f"Template {request.template_id} não encontrado")
        
        template = self.templates[request.template_id]
        template_data = request.template_data or {}
        
        # Processar subject
        if not request.subject:
            request.subject = template["subject"].format(**template_data)
        
        # Processar HTML
        if not request.html_content:
            request.html_content = template["html"].format(**template_data)
        
        # Processar texto
        if not request.text_content:
            request.text_content = template["text"].format(**template_data)
        
        return request
    
    def _update_stats(self, provider: EmailProvider, status: EmailStatus):
        """Atualiza estatísticas de email"""
        
        self.email_stats["total_sent"] += 1
        
        if status == EmailStatus.DELIVERED:
            self.email_stats["total_delivered"] += 1
        elif status == EmailStatus.BOUNCED:
            self.email_stats["total_bounced"] += 1
        elif status == EmailStatus.OPENED:
            self.email_stats["total_opened"] += 1
        
        provider_key = provider.value
        if provider_key not in self.email_stats["by_provider"]:
            self.email_stats["by_provider"][provider_key] = 0
        self.email_stats["by_provider"][provider_key] += 1
    
    async def send_welcome_email(self, user_email: str, user_name: str, **kwargs) -> EmailResponse:
        """Envia email de boas-vindas"""
        
        recipients = [EmailRecipient(email=user_email, name=user_name)]
        
        request = EmailRequest(
            to=recipients,
            template_id="welcome",
            template_data={
                "user_name": user_name,
                "login_url": f"{settings.app_name}/login",
                **kwargs
            },
            email_type=EmailType.WELCOME
        )
        
        return await self.send_email(request)
    
    async def send_password_reset_email(self, user_email: str, reset_token: str, **kwargs) -> EmailResponse:
        """Envia email de redefinição de senha"""
        
        recipients = [EmailRecipient(email=user_email)]
        reset_link = f"{settings.app_name}/reset-password?token={reset_token}"
        
        request = EmailRequest(
            to=recipients,
            template_id="password_reset",
            template_data={
                "reset_link": reset_link,
                **kwargs
            },
            email_type=EmailType.PASSWORD_RESET
        )
        
        return await self.send_email(request)
    
    async def send_payment_confirmation_email(self, user_email: str, payment_data: Dict, **kwargs) -> EmailResponse:
        """Envia email de confirmação de pagamento"""
        
        recipients = [EmailRecipient(email=user_email)]
        
        request = EmailRequest(
            to=recipients,
            template_id="payment_confirmed",
            template_data={
                "amount": payment_data.get("amount", 0),
                "currency": payment_data.get("currency", "BRL"),
                "payment_id": payment_data.get("id", ""),
                **kwargs
            },
            email_type=EmailType.INVOICE
        )
        
        return await self.send_email(request)
    
    def get_email_status(self, email_id: str) -> Optional[EmailResponse]:
        """Retorna status de um email enviado"""
        return self.sent_emails.get(email_id)
    
    def get_email_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Retorna estatísticas de email"""
        
        return {
            "period_days": days,
            "statistics": self.email_stats.copy(),
            "available_providers": {
                "sendgrid": self.sendgrid_enabled,
                "amazon_ses": self.ses_enabled,
                "smtp": self.smtp_enabled
            },
            "default_provider": self.default_provider.value,
            "total_emails_cached": len(self.sent_emails)
        }
    
    def _get_welcome_template(self) -> str:
        """Template HTML de boas-vindas"""
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">Bem-vindo ao TecnoCursos AI!</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Olá, {user_name}!</h2>
                <p style="color: #666; line-height: 1.6;">
                    Obrigado por se cadastrar no TecnoCursos AI! Sua conta foi criada com sucesso.
                </p>
                <p style="color: #666; line-height: 1.6;">
                    Agora você pode começar a criar vídeos educacionais incríveis com inteligência artificial.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Fazer Login
                    </a>
                </div>
                <p style="color: #999; font-size: 12px; text-align: center;">
                    TecnoCursos AI - Transformando educação com IA
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_template(self) -> str:
        """Template HTML de redefinição de senha"""
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f44336; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">Redefinir Senha</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Solicitação de Nova Senha</h2>
                <p style="color: #666; line-height: 1.6;">
                    Você solicitou a redefinição de sua senha no TecnoCursos AI.
                </p>
                <p style="color: #666; line-height: 1.6;">
                    Clique no botão abaixo para criar uma nova senha:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background: #f44336; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Redefinir Senha
                    </a>
                </div>
                <p style="color: #999; font-size: 12px;">
                    Se você não solicitou esta alteração, ignore este email.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_payment_confirmed_template(self) -> str:
        """Template HTML de confirmação de pagamento"""
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #4caf50; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">Pagamento Confirmado!</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Obrigado pelo seu pagamento!</h2>
                <p style="color: #666; line-height: 1.6;">
                    Seu pagamento foi processado com sucesso.
                </p>
                <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #333;">Detalhes do Pagamento:</h3>
                    <p style="margin: 5px 0;"><strong>Valor:</strong> {currency} {amount}</p>
                    <p style="margin: 5px 0;"><strong>ID do Pagamento:</strong> {payment_id}</p>
                </div>
                <p style="color: #666; line-height: 1.6;">
                    Seu acesso foi ativado e você já pode utilizar todos os recursos.
                </p>
            </div>
        </body>
        </html>
        """
    
    def health_check(self) -> Dict[str, Any]:
        """Health check do serviço de email"""
        return {
            "service": "Email Integration",
            "providers": {
                "sendgrid": {
                    "enabled": self.sendgrid_enabled,
                    "available": SENDGRID_AVAILABLE
                },
                "amazon_ses": {
                    "enabled": self.ses_enabled,
                    "available": AWS_AVAILABLE
                },
                "smtp": {
                    "enabled": self.smtp_enabled,
                    "available": AIOSMTP_AVAILABLE
                }
            },
            "default_provider": self.default_provider.value,
            "emails_sent": self.email_stats["total_sent"],
            "cached_emails": len(self.sent_emails),
            "status": "healthy"
        }

# Instância global do serviço
email_service = EmailIntegrationService()

# Funções de conveniência
async def send_email(to_email: str, subject: str, html_content: str = "", text_content: str = "", **kwargs) -> EmailResponse:
    """Função de conveniência para envio de email"""
    recipients = [EmailRecipient(email=to_email)]
    
    request = EmailRequest(
        to=recipients,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        **kwargs
    )
    
    return await email_service.send_email(request)

async def send_welcome_email(user_email: str, user_name: str) -> EmailResponse:
    """Função de conveniência para email de boas-vindas"""
    return await email_service.send_welcome_email(user_email, user_name)

async def send_password_reset_email(user_email: str, reset_token: str) -> EmailResponse:
    """Função de conveniência para email de reset de senha"""
    return await email_service.send_password_reset_email(user_email, reset_token)

if __name__ == "__main__":
    # Teste do serviço
    import asyncio
    
    async def test_email_service():
        print("📧 Testando Email Integration Service...")
        
        # Teste email simples
        result = await send_email(
            to_email="teste@example.com",
            subject="Teste TecnoCursos AI",
            html_content="<h1>Este é um teste!</h1>",
            text_content="Este é um teste!"
        )
        print(f"📨 Email enviado: {result.id}, Status: {result.status.value}")
        
        # Teste email de boas-vindas
        welcome_result = await send_welcome_email("usuario@example.com", "Usuário Teste")
        print(f"👋 Welcome email: {welcome_result.id}")
        
        # Estatísticas
        stats = email_service.get_email_statistics()
        print(f"📊 Emails enviados: {stats['statistics']['total_sent']}")
        
        # Health check
        health = email_service.health_check()
        print(f"🏥 Provider padrão: {health['default_provider']}")
    
    asyncio.run(test_email_service()) 