"""
Configurações centralizadas do TecnoCursos AI
"""

import os
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel, field_validator
from functools import lru_cache


class Settings(BaseModel):
    """Configurações da aplicação"""
    
    # Aplicação
    app_name: str = "TecnoCursos AI"
    version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Servidor
    host: str = "localhost"
    port: int = 8000
    log_level: str = "INFO"
    
    # Database
    database_url: str = "sqlite:///./data/tecnocursos.db"
    
    # Segurança
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Upload
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = [".pdf", ".pptx", ".docx", ".txt"]
    upload_path: str = "static/uploads"
    
    # Redis (opcional)
    redis_url: Optional[str] = None
    redis_enabled: bool = False
    
    # APIs externas (opcionais)
    openai_api_key: Optional[str] = None
    d_id_api_key: Optional[str] = None
    google_cloud_credentials: Optional[str] = None
    
    @field_validator('allowed_extensions')
    @classmethod
    def validate_extensions(cls, v):
        """Validar extensões permitidas"""
        if not v:
            return [".pdf", ".pptx", ".docx", ".txt"]
        return [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in v]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Obter configurações com cache
    """
    # Carregar variáveis de ambiente
    settings = Settings()
    
    # Sobrescrever com variáveis de ambiente se disponíveis
    settings.debug = os.getenv("DEBUG", "false").lower() == "true"
    settings.environment = os.getenv("ENVIRONMENT", "development")
    settings.host = os.getenv("HOST", "localhost")
    settings.port = int(os.getenv("PORT", "8000"))
    settings.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    settings.database_url = os.getenv("DATABASE_URL", "sqlite:///./data/tecnocursos.db")
    
    # Segurança
    settings.secret_key = os.getenv("SECRET_KEY", settings.secret_key)
    settings.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # APIs externas
    settings.openai_api_key = os.getenv("OPENAI_API_KEY")
    settings.d_id_api_key = os.getenv("D_ID_API_KEY")
    settings.google_cloud_credentials = os.getenv("GOOGLE_CLOUD_CREDENTIALS")
    
    # Redis
    settings.redis_url = os.getenv("REDIS_URL")
    settings.redis_enabled = settings.redis_url is not None
    
    return settings


def get_database_url() -> str:
    """Obter URL do banco de dados"""
    settings = get_settings()
    
    # Garantir que o diretório do banco existe
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    return settings.database_url


def get_upload_path() -> Path:
    """Obter caminho de upload"""
    settings = get_settings()
    upload_path = Path(settings.upload_path)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def is_production() -> bool:
    """Verificar se está em produção"""
    return get_settings().environment.lower() == "production"


def is_development() -> bool:
    """Verificar se está em desenvolvimento"""
    return get_settings().environment.lower() == "development" 