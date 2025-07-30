"""
Configuração Centralizada da API - TecnoCursos AI
Sistema unificado de configuração com validação e ambiente-específico
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import secrets
from pydantic import BaseSettings, validator, Field
from enum import Enum

class Environment(str, Enum):
    """Ambientes disponíveis"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(str, Enum):
    """Níveis de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class DatabaseConfig:
    """Configuração do banco de dados"""
    url: str = "sqlite:///./tecnocursos.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Configurações específicas por ambiente
    test_url: str = "sqlite:///./test_tecnocursos.db"
    
    @property
    def connection_args(self) -> Dict[str, Any]:
        """Argumentos de conexão baseados no tipo de banco"""
        if self.url.startswith("sqlite"):
            return {"check_same_thread": False}
        elif self.url.startswith("postgresql"):
            return {"pool_pre_ping": True}
        return {}

@dataclass 
class RedisConfig:
    """Configuração do Redis"""
    url: str = "redis://localhost:6379/0"
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    health_check_interval: int = 30
    
    # Cache específico
    cache_db: int = 0
    session_db: int = 1
    celery_db: int = 2

@dataclass
class SecurityConfig:
    """Configuração de segurança"""
    secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Senhas
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # CORS
    allowed_origins: List[str] = field(default_factory=list)
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    allowed_headers: List[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = True

@dataclass
class FileConfig:
    """Configuração de arquivos"""
    upload_dir: str = "./uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".pdf", ".pptx", ".docx", ".txt", ".md",
        ".mp4", ".avi", ".mov", ".mp3", ".wav"
    ])
    
    # Processamento
    temp_dir: str = "./temp"
    video_output_dir: str = "./videos"
    audio_output_dir: str = "./audios"
    
    # Limpeza automática
    cleanup_temp_files: bool = True
    temp_file_ttl_hours: int = 24

@dataclass
class AIConfig:
    """Configuração de IA/ML"""
    # APIs externas
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    
    # Modelos padrão
    default_text_model: str = "gpt-3.5-turbo"
    default_voice_model: str = "eleven_multilingual_v2"
    default_image_model: str = "dall-e-3"
    
    # Configurações de geração
    max_tokens: int = 2000
    temperature: float = 0.7
    voice_stability: float = 0.5
    voice_similarity: float = 0.8

@dataclass
class MonitoringConfig:
    """Configuração de monitoramento"""
    enable_metrics: bool = True
    enable_health_checks: bool = True
    enable_profiling: bool = False
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    log_rotation: str = "1 day"
    log_retention: int = 7
    
    # Métricas
    metrics_endpoint: str = "/metrics"
    health_endpoint: str = "/health"

class AppSettings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Informações básicas
    app_name: str = "TecnoCursos AI"
    app_version: str = "1.0.0"
    app_description: str = "Sistema de geração automática de cursos"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Host e porta
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Configurações por seção
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    files: FileConfig = field(default_factory=FileConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
    
    @validator("environment")
    def validate_environment(cls, v):
        """Valida ambiente"""
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                raise ValueError(f"Invalid environment: {v}")
        return v
    
    @validator("port")
    def validate_port(cls, v):
        """Valida porta"""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    def update_from_env(self):
        """Atualiza configurações específicas baseadas no ambiente"""
        if self.environment == Environment.PRODUCTION:
            self.debug = False
            self.monitoring.log_level = LogLevel.WARNING
            self.security.allowed_origins = [
                "https://tecnocursos.ai",
                "https://www.tecnocursos.ai"
            ]
        elif self.environment == Environment.STAGING:
            self.debug = False
            self.monitoring.log_level = LogLevel.INFO
            self.security.allowed_origins = [
                "https://staging.tecnocursos.ai"
            ]
        elif self.environment == Environment.DEVELOPMENT:
            self.debug = True
            self.monitoring.log_level = LogLevel.DEBUG
            self.security.allowed_origins = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000"
            ]
        elif self.environment == Environment.TESTING:
            self.debug = True
            self.monitoring.log_level = LogLevel.DEBUG
            self.database.url = self.database.test_url
    
    def create_directories(self):
        """Cria diretórios necessários"""
        directories = [
            self.files.upload_dir,
            self.files.temp_dir,
            self.files.video_output_dir,
            self.files.audio_output_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate_required_settings(self):
        """Valida configurações obrigatórias"""
        errors = []
        
        # Verificar chaves de segurança em produção
        if self.environment == Environment.PRODUCTION:
            if self.security.secret_key == "your-secret-key-here":
                errors.append("SECRET_KEY must be set in production")
            
            if not self.ai.openai_api_key:
                errors.append("OPENAI_API_KEY is required in production")
        
        # Verificar configurações de banco
        if not self.database.url:
            errors.append("DATABASE_URL is required")
        
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configurações para dicionário (sem dados sensíveis)"""
        config_dict = {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment.value,
            "debug": self.debug,
            "host": self.host,
            "port": self.port,
            "database": {
                "echo": self.database.echo,
                "pool_size": self.database.pool_size
            },
            "files": {
                "max_file_size": self.files.max_file_size,
                "allowed_extensions": self.files.allowed_extensions
            },
            "monitoring": {
                "enable_metrics": self.monitoring.enable_metrics,
                "log_level": self.monitoring.log_level.value
            }
        }
        return config_dict

# Instância global das configurações
settings = AppSettings()

def get_settings() -> AppSettings:
    """Retorna instância das configurações"""
    return settings

def load_config(config_file: Optional[str] = None) -> AppSettings:
    """Carrega configurações de arquivo"""
    global settings
    
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            # Atualizar settings com dados do arquivo
            for key, value in config_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
    
    # Aplicar configurações específicas do ambiente
    settings.update_from_env()
    
    # Criar diretórios necessários
    settings.create_directories()
    
    # Validar configurações
    settings.validate_required_settings()
    
    return settings

def save_config(config_file: str):
    """Salva configurações atuais em arquivo"""
    config_data = settings.to_dict()
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)

# Configurações específicas para FastAPI
def get_fastapi_config() -> Dict[str, Any]:
    """Retorna configurações para inicialização do FastAPI"""
    return {
        "title": settings.app_name,
        "description": settings.app_description,
        "version": settings.app_version,
        "debug": settings.debug,
        "docs_url": "/docs" if settings.environment != Environment.PRODUCTION else None,
        "redoc_url": "/redoc" if settings.environment != Environment.PRODUCTION else None,
    }

# Utilitários de configuração
def is_development() -> bool:
    """Verifica se está em ambiente de desenvolvimento"""
    return settings.environment == Environment.DEVELOPMENT

def is_production() -> bool:
    """Verifica se está em ambiente de produção"""
    return settings.environment == Environment.PRODUCTION

def is_testing() -> bool:
    """Verifica se está em ambiente de teste"""
    return settings.environment == Environment.TESTING
