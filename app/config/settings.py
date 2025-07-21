#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Configuração Avançado - TecnoCursos AI

Este módulo implementa gerenciamento de configuração seguindo as melhores
práticas do FastAPI para diferentes ambientes (dev, staging, production).

Baseado em:
- Pydantic Settings
- 12-Factor App methodology
- Environment-based configuration
- Type-safe settings
- Validation and documentation

Funcionalidades:
- Configuração por ambiente
- Validação automática de types
- Settings cacheados
- Documentação automática
- Secrets management
- Database configuration
- Redis configuration
- API keys management

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import os
from functools import lru_cache

try:
    from pydantic import BaseSettings, validator, Field
    from pydantic import PostgresDsn, RedisDsn, HttpUrl
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback para versões antigas do Pydantic
    try:
        from pydantic import BaseSettings, validator, Field
        from pydantic.types import PostgresDsn, RedisDsn, HttpUrl
        PYDANTIC_AVAILABLE = True
    except ImportError:
        BaseSettings = object
        PYDANTIC_AVAILABLE = False

class DatabaseSettings(BaseSettings):
    """Configurações de banco de dados"""
    
    # Database connection
    database_url: str = Field(
        "mysql+pymysql://root:password@localhost:3306/tecnocursos_ai",
        description="URL de conexão com o banco de dados"
    )
    database_pool_size: int = Field(20, description="Tamanho do pool de conexões")
    database_max_overflow: int = Field(30, description="Máximo de conexões extras")
    database_pool_timeout: int = Field(30, description="Timeout do pool em segundos")
    database_pool_recycle: int = Field(3600, description="Recycle connections em segundos")
    
    # Database behavior
    database_echo: bool = Field(False, description="Log SQL queries")
    database_echo_pool: bool = Field(False, description="Log pool operations")
    database_autocommit: bool = Field(False, description="Auto commit transactions")
    database_autoflush: bool = Field(True, description="Auto flush changes")
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validar URL do banco de dados"""
        if not v or not v.startswith(("mysql", "postgresql", "sqlite")):
            raise ValueError("Database URL deve começar com mysql, postgresql ou sqlite")
        return v
    
    class Config:
        env_prefix = "DB_"
        case_sensitive = False

class RedisSettings(BaseSettings):
    """Configurações do Redis"""
    
    # Redis connection
    redis_host: str = Field("localhost", description="Host do Redis")
    redis_port: int = Field(6379, description="Porta do Redis")
    redis_db: int = Field(0, description="Database do Redis")
    redis_password: Optional[str] = Field(None, description="Senha do Redis")
    redis_username: Optional[str] = Field(None, description="Usuário do Redis")
    
    # Redis behavior
    redis_max_connections: int = Field(20, description="Máximo de conexões")
    redis_socket_timeout: int = Field(5, description="Socket timeout")
    redis_socket_connect_timeout: int = Field(5, description="Connect timeout")
    redis_retry_on_timeout: bool = Field(True, description="Retry on timeout")
    
    # Cache settings
    cache_ttl_default: int = Field(300, description="TTL padrão do cache em segundos")
    cache_ttl_short: int = Field(60, description="TTL curto do cache")
    cache_ttl_long: int = Field(3600, description="TTL longo do cache")
    
    @property
    def redis_url(self) -> str:
        """Construir URL do Redis"""
        auth = ""
        if self.redis_username and self.redis_password:
            auth = f"{self.redis_username}:{self.redis_password}@"
        elif self.redis_password:
            auth = f":{self.redis_password}@"
        
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_prefix = "REDIS_"
        case_sensitive = False

class SecuritySettings(BaseSettings):
    """Configurações de segurança"""
    
    # JWT Settings
    secret_key: str = Field(
        "your-secret-key-change-in-production",
        description="Chave secreta para JWT"
    )
    algorithm: str = Field("HS256", description="Algoritmo para JWT")
    access_token_expire_minutes: int = Field(30, description="Expiração do access token")
    refresh_token_expire_days: int = Field(7, description="Expiração do refresh token")
    
    # Password Settings
    password_min_length: int = Field(8, description="Tamanho mínimo da senha")
    password_require_uppercase: bool = Field(True, description="Requer maiúscula")
    password_require_lowercase: bool = Field(True, description="Requer minúscula")
    password_require_numbers: bool = Field(True, description="Requer números")
    password_require_symbols: bool = Field(False, description="Requer símbolos")
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(60, description="Requests por minuto")
    rate_limit_burst_size: int = Field(10, description="Tamanho do burst")
    
    # CORS Settings
    cors_allowed_origins: List[str] = Field(
        ["*"], 
        description="Origins permitidas para CORS"
    )
    cors_allow_credentials: bool = Field(False, description="Permitir credentials")
    cors_allowed_methods: List[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Métodos permitidos"
    )
    cors_allowed_headers: List[str] = Field(
        ["*"],
        description="Headers permitidos"
    )
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validar chave secreta"""
        if len(v) < 32:
            raise ValueError("Secret key deve ter pelo menos 32 caracteres")
        return v
    
    class Config:
        env_prefix = "SECURITY_"
        case_sensitive = False

class AIServicesSettings(BaseSettings):
    """Configurações dos serviços de IA"""
    
    # OpenAI
    openai_api_key: Optional[str] = Field(None, description="API Key do OpenAI")
    openai_model: str = Field("gpt-3.5-turbo", description="Modelo padrão do OpenAI")
    openai_max_tokens: int = Field(1000, description="Máximo de tokens")
    openai_temperature: float = Field(0.7, description="Temperature para geração")
    
    # Azure Cognitive Services
    azure_speech_key: Optional[str] = Field(None, description="Chave do Azure Speech")
    azure_speech_region: str = Field("eastus", description="Região do Azure Speech")
    azure_speech_voice: str = Field("pt-BR-FranciscaNeural", description="Voz padrão")
    
    # D-ID (Avatar)
    d_id_api_key: Optional[str] = Field(None, description="API Key do D-ID")
    d_id_presenter_id: str = Field("amy-jcwCkr1grs", description="Presenter padrão")
    
    # ElevenLabs (TTS)
    elevenlabs_api_key: Optional[str] = Field(None, description="API Key do ElevenLabs")
    elevenlabs_voice_id: str = Field("Rachel", description="Voz padrão")
    
    # Stability AI (Stable Diffusion)
    stability_api_key: Optional[str] = Field(None, description="API Key do Stability AI")
    stability_engine: str = Field("stable-diffusion-xl-1024-v1-0", description="Engine padrão")
    
    class Config:
        env_prefix = "AI_"
        case_sensitive = False

class MediaSettings(BaseSettings):
    """Configurações de mídia e processamento"""
    
    # File Upload
    max_file_size_mb: int = Field(100, description="Tamanho máximo de arquivo em MB")
    allowed_image_types: List[str] = Field(
        [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        description="Tipos de imagem permitidos"
    )
    allowed_video_types: List[str] = Field(
        [".mp4", ".avi", ".mov", ".webm"],
        description="Tipos de vídeo permitidos"
    )
    allowed_audio_types: List[str] = Field(
        [".mp3", ".wav", ".aac", ".ogg"],
        description="Tipos de áudio permitidos"
    )
    
    # Video Generation
    video_default_fps: int = Field(30, description="FPS padrão para vídeos")
    video_default_quality: str = Field("high", description="Qualidade padrão")
    video_max_duration_seconds: int = Field(600, description="Duração máxima em segundos")
    video_output_format: str = Field("mp4", description="Formato de saída")
    
    # Paths
    upload_dir: str = Field("app/static/uploads", description="Diretório de upload")
    temp_dir: str = Field("temp", description="Diretório temporário")
    output_dir: str = Field("app/static/videos/generated", description="Diretório de saída")
    
    @validator("max_file_size_mb")
    def validate_file_size(cls, v):
        """Validar tamanho máximo de arquivo"""
        if v <= 0 or v > 1000:  # Máximo 1GB
            raise ValueError("Tamanho de arquivo deve estar entre 1MB e 1000MB")
        return v
    
    class Config:
        env_prefix = "MEDIA_"
        case_sensitive = False

class MonitoringSettings(BaseSettings):
    """Configurações de monitoramento e logging"""
    
    # Logging
    log_level: str = Field("INFO", description="Nível de log")
    log_format: str = Field("json", description="Formato de log (json|text)")
    log_file: Optional[str] = Field("logs/app.log", description="Arquivo de log")
    log_max_size_mb: int = Field(100, description="Tamanho máximo do log em MB")
    log_backup_count: int = Field(5, description="Número de backups do log")
    
    # Metrics
    metrics_enabled: bool = Field(True, description="Habilitar métricas")
    metrics_endpoint: str = Field("/metrics", description="Endpoint de métricas")
    
    # Health Check
    health_check_enabled: bool = Field(True, description="Habilitar health check")
    health_check_endpoint: str = Field("/health", description="Endpoint de health check")
    
    # Sentry (Error Tracking)
    sentry_dsn: Optional[str] = Field(None, description="DSN do Sentry")
    sentry_environment: str = Field("development", description="Ambiente do Sentry")
    sentry_release: Optional[str] = Field(None, description="Versão do release")
    
    class Config:
        env_prefix = "MONITORING_"
        case_sensitive = False

class AppSettings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # App Info
    app_name: str = Field("TecnoCursos AI", description="Nome da aplicação")
    app_version: str = Field("2.0.0", description="Versão da aplicação")
    app_description: str = Field(
        "Sistema avançado de geração de cursos com IA",
        description="Descrição da aplicação"
    )
    
    # Environment
    environment: str = Field("development", description="Ambiente (development|staging|production)")
    debug: bool = Field(True, description="Modo debug")
    testing: bool = Field(False, description="Modo teste")
    
    # Server
    host: str = Field("0.0.0.0", description="Host do servidor")
    port: int = Field(8000, description="Porta do servidor")
    reload: bool = Field(True, description="Auto reload em desenvolvimento")
    workers: int = Field(1, description="Número de workers")
    
    # API
    api_v1_prefix: str = Field("/api", description="Prefixo da API v1")
    docs_url: str = Field("/docs", description="URL da documentação")
    redoc_url: str = Field("/redoc", description="URL do ReDoc")
    openapi_url: str = Field("/openapi.json", description="URL do OpenAPI")
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validar ambiente"""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment deve ser um de: {valid_envs}")
        return v
    
    @validator("port")
    def validate_port(cls, v):
        """Validar porta"""
        if v < 1000 or v > 65535:
            raise ValueError("Porta deve estar entre 1000 e 65535")
        return v
    
    class Config:
        env_prefix = "APP_"
        case_sensitive = False

class Settings(BaseSettings):
    """Configurações centralizadas da aplicação"""
    
    # Sub-configurações
    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    ai_services: AIServicesSettings = AIServicesSettings()
    media: MediaSettings = MediaSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Campos que devem ser mantidos em segredo nos logs
        env_secrets = {
            "secret_key",
            "database_url", 
            "openai_api_key",
            "azure_speech_key",
            "d_id_api_key",
            "elevenlabs_api_key",
            "stability_api_key",
            "sentry_dsn"
        }

@lru_cache()
def get_settings() -> Settings:
    """
    Obter configurações da aplicação (cached)
    
    Returns:
        Instância das configurações
    """
    return Settings()

def get_database_url() -> str:
    """Obter URL do banco de dados"""
    return get_settings().database.database_url

def get_redis_url() -> str:
    """Obter URL do Redis"""
    return get_settings().redis.redis_url

def is_development() -> bool:
    """Verificar se está em desenvolvimento"""
    return get_settings().app.environment == "development"

def is_production() -> bool:
    """Verificar se está em produção"""
    return get_settings().app.environment == "production"

def is_testing() -> bool:
    """Verificar se está em modo teste"""
    return get_settings().app.testing

def get_cors_origins() -> List[str]:
    """Obter origins permitidas para CORS"""
    settings = get_settings()
    
    if settings.app.environment == "production":
        return [
            "https://tecnocursos.ai",
            "https://www.tecnocursos.ai",
            "https://app.tecnocursos.ai"
        ]
    elif settings.app.environment == "staging":
        return [
            "https://staging.tecnocursos.ai",
            "https://dev.tecnocursos.ai",
            "http://localhost:3000",
            "http://localhost:8080"
        ]
    else:
        return ["*"]  # Development

# Função para validar configurações críticas
def validate_critical_settings():
    """
    Validar configurações críticas antes do startup
    
    Raises:
        ValueError: Se configurações críticas estão inválidas
    """
    settings = get_settings()
    errors = []
    
    # Validar secret key em produção
    if settings.app.environment == "production":
        if settings.security.secret_key == "your-secret-key-change-in-production":
            errors.append("Secret key deve ser alterada em produção")
        
        if not settings.security.cors_allowed_origins or "*" in settings.security.cors_allowed_origins:
            errors.append("CORS deve ser configurado restritivamente em produção")
    
    # Validar conexão de banco
    if not settings.database.database_url:
        errors.append("Database URL é obrigatória")
    
    # Validar diretórios
    required_dirs = [
        settings.media.upload_dir,
        settings.media.temp_dir,
        settings.media.output_dir
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    if errors:
        raise ValueError(f"Configurações inválidas: {', '.join(errors)}")

# Configurações para diferentes ambientes
def get_environment_settings() -> Dict[str, Any]:
    """Obter configurações específicas do ambiente"""
    settings = get_settings()
    
    return {
        "environment": settings.app.environment,
        "debug": settings.app.debug,
        "database_echo": settings.database.database_echo,
        "cors_origins": get_cors_origins(),
        "rate_limit": settings.security.rate_limit_requests_per_minute,
        "cache_enabled": bool(settings.redis.redis_host),
        "ai_services_enabled": bool(settings.ai_services.openai_api_key),
        "monitoring_enabled": settings.monitoring.metrics_enabled
    } 