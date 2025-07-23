"""
Modelos básicos do banco de dados
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func

from ..core.database import Base


class TimestampMixin:
    """Mixin para adicionar timestamps automáticos"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class User(Base, TimestampMixin):
    """Modelo de usuário"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Project(Base, TimestampMixin):
    """Modelo de projeto"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=False, index=True)  # FK para User
    status = Column(String(50), default="active", nullable=False)
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class FileUpload(Base, TimestampMixin):
    """Modelo de arquivo uploadado"""
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100), nullable=True)
    user_id = Column(Integer, nullable=False, index=True)  # FK para User
    project_id = Column(Integer, nullable=True, index=True)  # FK para Project
    status = Column(String(50), default="uploaded", nullable=False)
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename='{self.filename}')>"


class Video(Base, TimestampMixin):
    """Modelo de vídeo gerado"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    duration = Column(Float, nullable=True)  # em segundos
    file_size = Column(Integer, nullable=True)
    resolution = Column(String(20), nullable=True)  # ex: "1920x1080"
    user_id = Column(Integer, nullable=False, index=True)  # FK para User
    project_id = Column(Integer, nullable=True, index=True)  # FK para Project
    status = Column(String(50), default="processing", nullable=False)
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}')>"


class AudioFile(Base, TimestampMixin):
    """Modelo de arquivo de áudio"""
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    duration = Column(Float, nullable=True)  # em segundos
    file_size = Column(Integer, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    text_content = Column(Text, nullable=True)  # texto usado para TTS
    user_id = Column(Integer, nullable=False, index=True)  # FK para User
    project_id = Column(Integer, nullable=True, index=True)  # FK para Project
    
    def __repr__(self):
        return f"<AudioFile(id={self.id}, filename='{self.filename}')>"


class Scene(Base, TimestampMixin):
    """Modelo de cena do editor"""
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    duration = Column(Float, nullable=False, default=5.0)  # em segundos
    order_index = Column(Integer, nullable=False, default=0)
    template = Column(String(100), nullable=True)
    background_path = Column(String(500), nullable=True)
    audio_path = Column(String(500), nullable=True)
    text_content = Column(Text, nullable=True)
    config_json = Column(Text, nullable=True)  # Configurações em JSON
    project_id = Column(Integer, nullable=False, index=True)  # FK para Project
    
    def __repr__(self):
        return f"<Scene(id={self.id}, name='{self.name}')>"


# Importar todos os modelos para registrar no metadata
__all__ = ["Base", "User", "Project", "FileUpload", "Video", "AudioFile", "Scene"] 