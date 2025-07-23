"""
Configurações da aplicação TecnoCursos AI Enterprise
Sistema completo com integrações de IA, pagamentos, comunicação e monitoramento
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações completas da aplicação enterprise"""
    
    # === CONFIGURAÇÕES BÁSICAS ===
    app_name: str = "TecnoCursosAI"
    version: str = "2.0.0"
    description: str = "SaaS Upload de Arquivos e Geração de Vídeos IA"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    encryption_key: str = "your-encryption-key-change-in-production"
    
    # === CONFIGURAÇÕES ADICIONAIS ===
    jwt_secret_key: str = "jwt-secret-key-tecnocursos-2025"
    max_file_size_mb: str = "100"
    upload_path: str = "app/static/uploads"
    video_path: str = "app/static/videos"
    thumbnail_path: str = "app/static/thumbnails"
    mock_external_apis: str = "true"
    tts_provider: str = "gtts"
    gtts_language: str = "pt"
    enable_ai_features: str = "true"
    
    # === CONFIGURAÇÕES DE BANCO DE DADOS ===
    database_url: str = "sqlite:///./tecnocursos.db"
    
    # === CONFIGURAÇÕES DE SERVIDOR ===
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # === CONFIGURAÇÕES DE SEGURANÇA ===
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # === CONFIGURAÇÕES DE ARQUIVOS ===
    upload_dir: str = "uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = [
        ".pdf", ".pptx", ".docx", ".txt", ".mp4", ".avi", ".mov",
        ".jpg", ".jpeg", ".png", ".gif", ".mp3", ".wav", ".m4a"
    ]
    
    @field_validator('allowed_extensions', mode='before')
    @classmethod
    def parse_allowed_extensions(cls, v):
        """Parse allowed extensions from environment variable string or list"""
        if isinstance(v, str):
            # Skip empty strings
            if not v.strip():
                return [".pdf", ".pptx", ".docx", ".txt", ".mp4", ".avi", ".mov",
                       ".jpg", ".jpeg", ".png", ".gif", ".mp3", ".wav", ".m4a"]
            
            # Try to parse as JSON first
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [ext if ext.startswith('.') else f'.{ext}' for ext in parsed]
            except (json.JSONDecodeError, ValueError):
                # Fall back to comma-separated string
                extensions = [ext.strip() for ext in v.split(',') if ext.strip()]
                if not extensions:
                    return [".pdf", ".pptx", ".docx", ".txt", ".mp4", ".avi", ".mov",
                           ".jpg", ".jpeg", ".png", ".gif", ".mp3", ".wav", ".m4a"]
                return [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
        return v
    
    # === CONFIGURAÇÕES DE IA ===
    openai_api_key: Optional[str] = None
    azure_openai_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    
    # === CONFIGURAÇÕES DE TTS ===
    azure_tts_key: Optional[str] = None
    azure_tts_region: Optional[str] = None
    
    # === CONFIGURAÇÕES DE AVATAR ===
    d_id_api_key: Optional[str] = None
    avatar_service_url: Optional[str] = None
    
    # === CONFIGURAÇÕES DE EMAIL ===
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # === CONFIGURAÇÕES DE PAGAMENTO ===
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # === CONFIGURAÇÕES DE MONITORAMENTO ===
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    
    # === CONFIGURAÇÕES DE CACHE ===
    redis_url: Optional[str] = None
    
    # === CONFIGURAÇÕES DE STORAGE ===
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    
    # === CONFIGURAÇÕES DE WEBSOCKET ===
    websocket_enabled: bool = True
    websocket_ping_interval: int = 25
    websocket_ping_timeout: int = 10
    
    # === CONFIGURAÇÕES DE RATE LIMITING ===
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # === CONFIGURAÇÕES DE BACKUP ===
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    
    # === CONFIGURAÇÕES DE ANALYTICS ===
    analytics_enabled: bool = True
    google_analytics_id: Optional[str] = None
    
    # === CONFIGURAÇÕES DE NOTIFICAÇÕES ===
    push_notifications_enabled: bool = True
    firebase_project_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    
    # === CONFIGURAÇÕES DE INTEGRAÇÃO ===
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    teams_webhook_url: Optional[str] = None
    
    # === CONFIGURAÇÕES DE PERFORMANCE ===
    worker_processes: int = 1
    max_connections: int = 1000
    connection_timeout: int = 30
    
    # === CONFIGURAÇÕES DE SEGURANÇA AVANÇADA ===
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    password_require_special: bool = True
    
    # === CONFIGURAÇÕES DE COMPLIANCE ===
    gdpr_enabled: bool = True
    data_retention_days: int = 365
    privacy_policy_url: Optional[str] = None
    terms_of_service_url: Optional[str] = None
    
    # === CONFIGURAÇÕES DE API ===
    api_version: str = "v1"
    api_prefix: str = "/api"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # === CONFIGURAÇÕES DE DEPLOYMENT ===
    docker_enabled: bool = False
    kubernetes_enabled: bool = False
    health_check_path: str = "/api/health"
    
    # === CONFIGURAÇÕES DE TESTING ===
    testing_enabled: bool = False
    test_database_url: Optional[str] = None
    
    # === CONFIGURAÇÕES DE DEVELOPMENT ===
    hot_reload: bool = True
    auto_migrate: bool = True
    seed_data: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
_settings = None

def get_settings() -> Settings:
    """Retorna a instância global das configurações"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Função de conveniência para obter configurações
def get_config() -> Settings:
    """Alias para get_settings()"""
    return get_settings() 