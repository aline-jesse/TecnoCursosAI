#!/usr/bin/env python3
"""
Sistema de Configuração Avançado - TecnoCursos AI
Gerencia todas as variáveis de ambiente e configurações
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field
from functools import lru_cache

class DatabaseConfig(BaseSettings):
    """Configurações do banco de dados"""
    url: str = Field(default="sqlite:///./tecnocursos.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

class RedisConfig(BaseSettings):
    """Configurações do Redis/Cache"""
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    ttl: int = Field(default=3600, env="CACHE_TTL")
    enabled: bool = Field(default=True, env="CACHE_ENABLED")

class SecurityConfig(BaseSettings):
    """Configurações de segurança"""
    secret_key: str = Field(default="tecnocursos-ai-secret-key", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_hours: int = Field(default=24, env="JWT_EXPIRE_HOURS")
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")

class EmailConfig(BaseSettings):
    """Configurações de email"""
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    email_from: str = Field(default="noreply@tecnocursos.com", env="EMAIL_FROM")
    templates_dir: str = Field(default="./templates/email", env="EMAIL_TEMPLATES_DIR")

class OpenAIConfig(BaseSettings):
    """Configurações da OpenAI"""
    api_key: str = Field(default="", env="OPENAI_API_KEY")
    model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")

class AvatarConfig(BaseSettings):
    """Configurações de Avatar/Video"""
    api_url: str = Field(default="https://api.d-id.com", env="AVATAR_API_URL")
    api_key: str = Field(default="", env="AVATAR_API_KEY")
    video_output_dir: str = Field(default="./videos", env="VIDEO_OUTPUT_DIR")
    video_temp_dir: str = Field(default="./temp", env="VIDEO_TEMP_DIR")

class TTSConfig(BaseSettings):
    """Configurações de Text-to-Speech"""
    provider: str = Field(default="elevenlabs", env="TTS_PROVIDER")
    elevenlabs_api_key: str = Field(default="", env="ELEVENLABS_API_KEY")
    voice_id: str = Field(default="default", env="TTS_VOICE_ID")
    output_dir: str = Field(default="./audio", env="TTS_OUTPUT_DIR")

class UploadConfig(BaseSettings):
    """Configurações de upload"""
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: str = Field(default="100MB", env="MAX_FILE_SIZE")
    allowed_extensions: str = Field(default="pdf,docx,txt,mp4,mp3,jpg,png,gif", env="ALLOWED_EXTENSIONS")
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

class MonitoringConfig(BaseSettings):
    """Configurações de monitoramento"""
    sentry_dsn: str = Field(default="", env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

class CORSConfig(BaseSettings):
    """Configurações de CORS"""
    origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")
    allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.origins.split(",")]

class RateLimitConfig(BaseSettings):
    """Configurações de rate limiting"""
    enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    window: int = Field(default=60, env="RATE_LIMIT_WINDOW")

class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Configurações do servidor
    server_host: str = Field(default="127.0.0.1", env="SERVER_HOST")
    server_port: int = Field(default=8000, env="SERVER_PORT")
    server_reload: bool = Field(default=True, env="SERVER_RELOAD")
    server_log_level: str = Field(default="info", env="SERVER_LOG_LEVEL")
    
    # Configurações de ambiente
    debug: bool = Field(default=True, env="DEBUG")
    testing: bool = Field(default=False, env="TESTING")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Sub-configurações
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    security: SecurityConfig = SecurityConfig()
    email: EmailConfig = EmailConfig()
    openai: OpenAIConfig = OpenAIConfig()
    avatar: AvatarConfig = AvatarConfig()
    tts: TTSConfig = TTSConfig()
    upload: UploadConfig = UploadConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    cors: CORSConfig = CORSConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    return Settings()

# Instância global das configurações
settings = get_settings()

# Funções utilitárias
def is_production() -> bool:
    """Verifica se está em produção"""
    return settings.environment.lower() == "production"

def is_development() -> bool:
    """Verifica se está em desenvolvimento"""
    return settings.environment.lower() == "development"

def is_testing() -> bool:
    """Verifica se está em modo de teste"""
    return settings.testing

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        settings.upload.upload_dir,
        settings.avatar.video_output_dir,
        settings.avatar.video_temp_dir,
        settings.tts.output_dir,
        settings.email.templates_dir,
        "./logs",
        "./backups",
        "./static",
        "./templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")

def validate_config():
    """Valida configurações essenciais"""
    issues = []
    
    # Verificar chaves obrigatórias em produção
    if is_production():
        if not settings.security.secret_key or settings.security.secret_key == "tecnocursos-ai-secret-key":
            issues.append("SECRET_KEY deve ser definida em produção")
        
        if not settings.openai.api_key:
            issues.append("OPENAI_API_KEY deve ser definida")
        
        if not settings.monitoring.sentry_dsn:
            issues.append("SENTRY_DSN recomendado para produção")
    
    # Verificar diretórios
    try:
        create_directories()
    except Exception as e:
        issues.append(f"Erro ao criar diretórios: {e}")
    
    if issues:
        print("⚠️ Problemas de configuração encontrados:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ Configuração validada com sucesso")
    
    return len(issues) == 0

if __name__ == "__main__":
    print("🔧 TecnoCursos AI - Sistema de Configuração")
    print("="*50)
    
    # Validar configuração
    validate_config()
    
    # Mostrar configurações
    print(f"\n📍 Servidor: {settings.server_host}:{settings.server_port}")
    print(f"🗃️ Banco: {settings.database.url}")
    print(f"🔒 Segurança: JWT com {settings.security.jwt_algorithm}")
    print(f"📁 Uploads: {settings.upload.upload_dir}")
    print(f"🤖 IA: {settings.openai.model}")
    print(f"🎬 Vídeos: {settings.avatar.video_output_dir}")
    print(f"🔊 Áudio: {settings.tts.output_dir}")
    print(f"🌍 Ambiente: {settings.environment}")
    print(f"🐛 Debug: {settings.debug}")
    
    print("\n✅ Sistema de configuração carregado!")
