"""
CONFIGURAÇÃO DE PRODUÇÃO - TECNOCURSOS AI ENTERPRISE
=====================================================
Configurações otimizadas para ambiente de produção com:
- Segurança avançada
- Performance otimizada  
- Monitoramento completo
- Cache distribuído
- Backup automático
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator
from functools import lru_cache

class ProductionSettings(BaseSettings):
    """Configurações de produção otimizadas"""
    
    # === CONFIGURAÇÕES BÁSICAS ===
    app_name: str = "TecnoCursos AI Enterprise"
    app_version: str = "2.0.0"
    environment: str = "production"
    debug: bool = False
    testing: bool = False
    
    # === SEGURANÇA ===
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Security Headers
    security_headers: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # === BANCO DE DADOS ===
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = 20
    database_max_overflow: int = 40
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    database_echo: bool = False
    
    # === REDIS CACHE ===
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = 0
    redis_ssl: bool = Field(False, env="REDIS_SSL")
    redis_pool_size: int = 50
    
    # === PERFORMANCE ===
    max_workers: int = 8
    worker_timeout: int = 300
    max_requests: int = 1000
    max_requests_jitter: int = 100
    preload_app: bool = True
    
    # Rate Limiting
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour
    rate_limit_burst: int = 100
    
    # === APIs EXTERNAS ===
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    d_id_api_key: Optional[str] = Field(None, env="D_ID_API_KEY")
    elevenlabs_api_key: Optional[str] = Field(None, env="ELEVENLABS_API_KEY")
    stripe_api_key: Optional[str] = Field(None, env="STRIPE_API_KEY")
    
    # === STORAGE ===
    upload_path: str = "/var/app/uploads"
    max_upload_size: int = 500 * 1024 * 1024  # 500MB
    allowed_extensions: List[str] = ['.pdf', '.pptx', '.docx', '.txt', '.mp4', '.mp3', '.wav']
    
    # Cloud Storage
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field("us-east-1", env="AWS_REGION")
    s3_bucket: Optional[str] = Field(None, env="S3_BUCKET")
    
    # === BACKUP ===
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days: int = 30
    backup_storage_path: str = "/var/backups/tecnocursos"
    
    # === MONITORAMENTO ===
    monitoring_enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    log_level: str = "INFO"
    log_format: str = "json"
    
    # External Monitoring
    datadog_api_key: Optional[str] = Field(None, env="DATADOG_API_KEY")
    new_relic_license_key: Optional[str] = Field(None, env="NEW_RELIC_LICENSE_KEY")
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    
    # === EMAIL ===
    smtp_host: str = Field("smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    smtp_tls: bool = True
    
    # === WEBSOCKET ===
    websocket_enabled: bool = True
    websocket_max_connections: int = 1000
    websocket_heartbeat_interval: int = 30
    
    # === CORS ===
    cors_origins: List[str] = [
        "https://tecnocursos.ai",
        "https://app.tecnocursos.ai",
        "https://admin.tecnocursos.ai"
    ]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    cors_headers: List[str] = ["*"]
    
    # === FEATURES FLAGS ===
    feature_ai_generation: bool = True
    feature_advanced_analytics: bool = True
    feature_real_time_collaboration: bool = True
    feature_enterprise_sso: bool = True
    feature_api_versioning: bool = True
    
    # === COMPLIANCE ===
    gdpr_enabled: bool = True
    lgpd_enabled: bool = True
    data_retention_days: int = 2555  # 7 years
    audit_logging: bool = True
    
    # === CACHE CONFIGURAÇÕES ===
    cache_ttl_default: int = 3600  # 1 hour
    cache_ttl_assets: int = 86400  # 24 hours
    cache_ttl_scenes: int = 1800   # 30 minutes
    cache_ttl_users: int = 900     # 15 minutes
    
    # === KUBERNETES ===
    kubernetes_namespace: str = "tecnocursos-prod"
    kubernetes_service_name: str = "tecnocursos-api"
    pod_name: Optional[str] = Field(None, env="HOSTNAME")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        if not v or "sqlite" in v.lower():
            raise ValueError("SQLite não é suportado em produção")
        return v
    
    @property
    def redis_url(self) -> str:
        """Constrói URL do Redis"""
        scheme = "rediss" if self.redis_ssl else "redis"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"{scheme}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Configurações do banco otimizadas"""
        return {
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_recycle": self.database_pool_recycle,
            "echo": self.database_echo,
            "pool_pre_ping": True,
            "connect_args": {
                "charset": "utf8mb4",
                "connect_timeout": 60,
                "read_timeout": 60,
                "write_timeout": 60,
            }
        }
    
    @property
    def gunicorn_config(self) -> Dict[str, Any]:
        """Configurações do Gunicorn otimizadas"""
        return {
            "bind": "0.0.0.0:8000",
            "workers": self.max_workers,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "timeout": self.worker_timeout,
            "max_requests": self.max_requests,
            "max_requests_jitter": self.max_requests_jitter,
            "preload_app": self.preload_app,
            "worker_connections": 1000,
            "keepalive": 5,
        }
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True

# === CONFIGURAÇÕES ESPECIALIZADAS ===

class SecurityConfig:
    """Configurações de segurança avançadas"""
    
    RATE_LIMITING = {
        "default": "1000/hour",
        "auth": "10/minute", 
        "upload": "50/hour",
        "api": "5000/hour",
        "premium": "unlimited"
    }
    
    PASSWORD_POLICY = {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": True,
        "max_age_days": 90
    }
    
    SESSION_CONFIG = {
        "secure": True,
        "httponly": True,
        "samesite": "strict",
        "max_age": 86400,  # 24 hours
        "domain": None,
        "path": "/"
    }

class MonitoringConfig:
    """Configurações de monitoramento"""
    
    HEALTH_CHECKS = {
        "database": {"timeout": 5, "interval": 30},
        "redis": {"timeout": 3, "interval": 15},
        "external_apis": {"timeout": 10, "interval": 60},
        "disk_space": {"threshold": 0.85, "interval": 300},
        "memory": {"threshold": 0.90, "interval": 60}
    }
    
    METRICS = {
        "response_time": True,
        "request_count": True,
        "error_rate": True,
        "database_connections": True,
        "cache_hit_rate": True,
        "queue_size": True
    }
    
    ALERTS = {
        "error_rate_threshold": 0.05,  # 5%
        "response_time_threshold": 2000,  # 2 seconds
        "disk_usage_threshold": 0.85,  # 85%
        "memory_usage_threshold": 0.90,  # 90%
    }

class PerformanceConfig:
    """Configurações de performance"""
    
    CACHE_STRATEGIES = {
        "user_sessions": {"ttl": 900, "strategy": "write_through"},
        "api_responses": {"ttl": 300, "strategy": "write_behind"},
        "static_assets": {"ttl": 86400, "strategy": "cache_aside"},
        "database_queries": {"ttl": 600, "strategy": "read_through"}
    }
    
    CONNECTION_POOLS = {
        "database": {"min": 10, "max": 20, "timeout": 30},
        "redis": {"min": 5, "max": 15, "timeout": 10},
        "http_client": {"min": 20, "max": 100, "timeout": 30}
    }

# === SINGLETON PATTERN ===

@lru_cache()
def get_production_settings() -> ProductionSettings:
    """Singleton para configurações de produção"""
    return ProductionSettings()

# Instância global
settings = get_production_settings()

# === EXPORT ===
__all__ = [
    "ProductionSettings",
    "SecurityConfig", 
    "MonitoringConfig",
    "PerformanceConfig",
    "get_production_settings",
    "settings"
] 