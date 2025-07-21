#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CONFIGURAÇÃO UNIFICADA - TECNOCURSOS AI
=========================================

Sistema centralizado de configuração que unifica todas as configurações
dispersas do sistema, garantindo consistência e facilidade de manutenção.

Configurações Unificadas:
- Configurações de vídeo
- Configurações de áudio/TTS
- Configurações de IA
- Configurações de banco de dados
- Configurações de cache
- Configurações de segurança
- Configurações de performance
- Configurações de integração

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json

# === CONFIGURAÇÕES BASE ===

@dataclass
class DatabaseConfig:
    """Configurações de banco de dados"""
    url: str = "sqlite:///tecnocursos.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    pool_recycle: int = 3600

@dataclass
class VideoConfig:
    """Configurações de vídeo unificadas"""
    # Resoluções suportadas
    resolutions: Dict[str, tuple] = field(default_factory=lambda: {
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160)
    })
    
    # Configurações padrão
    default_resolution: str = "1080p"
    default_fps: int = 30
    default_codec: str = "libx264"
    default_audio_codec: str = "aac"
    default_bitrate: str = "2000k"
    
    # Templates disponíveis
    templates: List[str] = field(default_factory=lambda: [
        "modern", "corporate", "tech", "educational", "minimal"
    ])
    
    # Diretórios
    output_dir: str = "static/videos"
    temp_dir: str = "temp/videos"
    cache_dir: str = "cache/videos"
    
    # Limites
    max_duration: int = 3600  # 1 hora
    max_file_size_mb: int = 500
    max_concurrent_renders: int = 3

@dataclass
class AudioConfig:
    """Configurações de áudio/TTS unificadas"""
    # Provedores TTS disponíveis
    tts_providers: List[str] = field(default_factory=lambda: [
        "gtts", "bark", "azure", "elevenlabs", "openai"
    ])
    
    # Configurações padrão
    default_provider: str = "gtts"
    default_language: str = "pt-BR"
    default_voice: str = "pt_speaker_0"
    
    # Qualidade de áudio
    sample_rate: int = 22050
    bitrate: str = "128k"
    format: str = "mp3"
    
    # Diretórios
    output_dir: str = "static/audios"
    temp_dir: str = "temp/audios"
    cache_dir: str = "cache/audios"
    
    # Limites
    max_text_length: int = 5000
    max_file_size_mb: int = 50

@dataclass
class AIConfig:
    """Configurações de IA unificadas"""
    # Provedores disponíveis
    providers: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "openai": {
            "models": ["gpt-4", "gpt-3.5-turbo", "dall-e-3"],
            "max_tokens": 4096,
            "temperature": 0.7
        },
        "anthropic": {
            "models": ["claude-3-sonnet", "claude-3-haiku"],
            "max_tokens": 4096,
            "temperature": 0.7
        },
        "google": {
            "models": ["gemini-pro", "gemini-pro-vision"],
            "max_tokens": 4096,
            "temperature": 0.7
        }
    })
    
    # Avatar providers
    avatar_providers: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "did": {
            "api_url": "https://api.d-id.com",
            "presenters": ["amy-jcu4GGiYNQ", "daniel-C2Y3dHl1eHE"]
        },
        "synthesia": {
            "api_url": "https://api.synthesia.io",
            "avatars": ["anna", "james", "sophia"]
        }
    })
    
    # Configurações padrão
    default_provider: str = "openai"
    default_model: str = "gpt-3.5-turbo"
    
    # Limites
    max_requests_per_minute: int = 60
    max_concurrent_requests: int = 5

@dataclass
class CacheConfig:
    """Configurações de cache unificadas"""
    # Tipos de cache
    redis_url: str = "redis://localhost:6379/0"
    file_cache_dir: str = "cache"
    memory_cache_size: int = 1000
    
    # TTL (Time To Live) em segundos
    ttl_video: int = 86400  # 24 horas
    ttl_audio: int = 43200  # 12 horas
    ttl_image: int = 21600  # 6 horas
    ttl_api: int = 3600     # 1 hora
    
    # Limpeza automática
    auto_cleanup: bool = True
    cleanup_interval: int = 3600  # 1 hora
    max_cache_size_gb: int = 5

@dataclass
class SecurityConfig:
    """Configurações de segurança unificadas"""
    # JWT
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ])
    
    # Rate limiting
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    
    # Upload security
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".pdf", ".pptx", ".docx", ".txt", ".mp3", ".wav", ".mp4", ".avi"
    ])
    max_upload_size_mb: int = 100
    
    # Password policy
    min_password_length: int = 8
    require_special_chars: bool = True
    require_numbers: bool = True
    require_uppercase: bool = True

@dataclass
class PerformanceConfig:
    """Configurações de performance unificadas"""
    # Threading
    max_workers: int = 4
    thread_pool_size: int = 10
    
    # Processing
    max_concurrent_uploads: int = 5
    max_concurrent_video_renders: int = 2
    max_concurrent_ai_requests: int = 3
    
    # Timeouts
    http_timeout: int = 30
    ai_timeout: int = 120
    video_render_timeout: int = 600
    
    # Memory
    max_memory_usage_percent: int = 80
    gc_threshold: int = 1000
    
    # Monitoring
    enable_metrics: bool = True
    metrics_interval: int = 60

@dataclass
class IntegrationConfig:
    """Configurações de integração unificadas"""
    # APIs externas
    apis: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "timeout": 30,
            "retry_attempts": 3
        },
        "did": {
            "base_url": "https://api.d-id.com",
            "timeout": 60,
            "retry_attempts": 2
        },
        "elevenlabs": {
            "base_url": "https://api.elevenlabs.io/v1",
            "timeout": 45,
            "retry_attempts": 3
        }
    })
    
    # Webhooks
    webhook_timeout: int = 30
    webhook_retry_attempts: int = 3
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "ai_generation": True,
        "avatar_videos": True,
        "real_time_preview": True,
        "batch_processing": True,
        "advanced_analytics": True
    })

@dataclass
class LoggingConfig:
    """Configurações de logging unificadas"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/tecnocursos.log"
    max_file_size_mb: int = 10
    backup_count: int = 5
    
    # Loggers específicos
    loggers: Dict[str, str] = field(default_factory=lambda: {
        "video_engine": "INFO",
        "ai_service": "INFO",
        "auth": "WARNING",
        "database": "WARNING"
    })

# === CLASSE PRINCIPAL DE CONFIGURAÇÃO ===

class UnifiedConfig:
    """Configuração unificada do sistema TecnoCursos AI"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Inicializar configuração"""
        # Configurações padrão
        self.database = DatabaseConfig()
        self.video = VideoConfig()
        self.audio = AudioConfig()
        self.ai = AIConfig()
        self.cache = CacheConfig()
        self.security = SecurityConfig()
        self.performance = PerformanceConfig()
        self.integration = IntegrationConfig()
        self.logging = LoggingConfig()
        
        # Carregar configurações de arquivo se especificado
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Sobrescrever com variáveis de ambiente
        self.load_from_env()
        
        # Validar configurações
        self.validate()
    
    def load_from_file(self, config_file: str) -> None:
        """Carregar configurações de arquivo JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Atualizar configurações
            for section_name, section_data in config_data.items():
                if hasattr(self, section_name):
                    section = getattr(self, section_name)
                    for key, value in section_data.items():
                        if hasattr(section, key):
                            setattr(section, key, value)
        
        except Exception as e:
            print(f"⚠️ Erro ao carregar configurações do arquivo: {e}")
    
    def load_from_env(self) -> None:
        """Carregar configurações de variáveis de ambiente"""
        # Database
        if os.getenv("DATABASE_URL"):
            self.database.url = os.getenv("DATABASE_URL")
        
        # Security
        if os.getenv("SECRET_KEY"):
            self.security.secret_key = os.getenv("SECRET_KEY")
        
        # AI APIs
        if os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("DID_API_KEY"):
            os.environ["DID_API_KEY"] = os.getenv("DID_API_KEY")
        
        # Redis
        if os.getenv("REDIS_URL"):
            self.cache.redis_url = os.getenv("REDIS_URL")
        
        # Debug mode
        if os.getenv("DEBUG") == "true":
            self.logging.level = "DEBUG"
            self.database.echo = True
    
    def validate(self) -> None:
        """Validar configurações"""
        errors = []
        
        # Validar diretórios
        directories = [
            self.video.output_dir,
            self.video.temp_dir,
            self.video.cache_dir,
            self.audio.output_dir,
            self.audio.temp_dir,
            self.audio.cache_dir,
            self.cache.file_cache_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Validar limites
        if self.video.max_duration <= 0:
            errors.append("video.max_duration deve ser positivo")
        
        if self.audio.max_text_length <= 0:
            errors.append("audio.max_text_length deve ser positivo")
        
        if self.performance.max_workers <= 0:
            errors.append("performance.max_workers deve ser positivo")
        
        if errors:
            raise ValueError(f"Erros de configuração: {', '.join(errors)}")
    
    def save_to_file(self, config_file: str) -> None:
        """Salvar configurações em arquivo JSON"""
        config_data = {}
        
        for attr_name in ['database', 'video', 'audio', 'ai', 'cache', 
                         'security', 'performance', 'integration', 'logging']:
            if hasattr(self, attr_name):
                section = getattr(self, attr_name)
                if hasattr(section, '__dict__'):
                    config_data[attr_name] = section.__dict__
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def get_video_resolution(self, quality: str) -> tuple:
        """Obter resolução para qualidade específica"""
        return self.video.resolutions.get(quality, self.video.resolutions[self.video.default_resolution])
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Verificar se feature está habilitada"""
        return self.integration.features.get(feature, False)
    
    def get_api_config(self, provider: str) -> Dict[str, Any]:
        """Obter configuração de API"""
        return self.integration.apis.get(provider, {})
    
    def get_cache_ttl(self, cache_type: str) -> int:
        """Obter TTL para tipo de cache"""
        ttl_map = {
            "video": self.cache.ttl_video,
            "audio": self.cache.ttl_audio,
            "image": self.cache.ttl_image,
            "api": self.cache.ttl_api
        }
        return ttl_map.get(cache_type, self.cache.ttl_api)

# === INSTÂNCIA GLOBAL ===

# Instância global de configuração
config = UnifiedConfig()

# === FUNÇÕES DE CONVENIÊNCIA ===

def get_config() -> UnifiedConfig:
    """Obter instância global de configuração"""
    return config

def reload_config(config_file: Optional[str] = None) -> UnifiedConfig:
    """Recarregar configuração"""
    global config
    config = UnifiedConfig(config_file)
    return config

def get_video_config() -> VideoConfig:
    """Obter configuração de vídeo"""
    return config.video

def get_audio_config() -> AudioConfig:
    """Obter configuração de áudio"""
    return config.audio

def get_ai_config() -> AIConfig:
    """Obter configuração de IA"""
    return config.ai

def get_security_config() -> SecurityConfig:
    """Obter configuração de segurança"""
    return config.security

def is_development() -> bool:
    """Verificar se está em modo desenvolvimento"""
    return config.logging.level == "DEBUG"

def is_production() -> bool:
    """Verificar se está em modo produção"""
    return not is_development()

# === INICIALIZAÇÃO ===

if __name__ == "__main__":
    # Teste da configuração
    test_config = UnifiedConfig()
    print("🔧 Configuração unificada carregada com sucesso!")
    print(f"Resolução padrão de vídeo: {test_config.get_video_resolution(test_config.video.default_resolution)}")
    print(f"Provedor TTS padrão: {test_config.audio.default_provider}")
    print(f"Feature IA habilitada: {test_config.is_feature_enabled('ai_generation')}") 