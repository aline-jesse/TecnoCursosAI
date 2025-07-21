#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Biblioteca de Assets - TecnoCursos AI

Este módulo implementa um sistema completo de gerenciamento de biblioteca
de assets para uso em cenas e projetos, incluindo upload, processamento,
categorização, busca e marketplace.

Funcionalidades:
- Upload e processamento automático de assets
- Biblioteca pública e privada
- Sistema de categorização e tags
- Busca avançada com filtros
- Sistema de avaliação e favoritos
- Marketplace de assets premium
- Processamento e otimização automática
- Geração de thumbnails
- Análise de metadados

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
import shutil
import hashlib
import mimetypes
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, BinaryIO
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import uuid

try:
    from PIL import Image, ImageOps
    from PIL.ExifTags import TAGS
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.wav import WAVE
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    from sqlalchemy.orm import Session
    from sqlalchemy import func, and_, or_, desc
    from app.database import get_db_session
    from app.models import Asset, User, Project, AssetRating
    from app.schemas import (
        AssetCreate, AssetUpdate, AssetResponse,
        AssetRatingCreate, AssetRatingResponse
    )
    from app.config import get_settings
    DATABASE_AVAILABLE = True
    settings = get_settings()
except ImportError:
    DATABASE_AVAILABLE = False
    settings = None

logger = logging.getLogger(__name__)

class AssetType(Enum):
    """Tipos de assets suportados"""
    CHARACTER = "character"
    BACKGROUND = "background"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    OVERLAY = "overlay"
    ICON = "icon"
    LOGO = "logo"
    TEMPLATE = "template"

class AssetCategory(Enum):
    """Categorias da biblioteca"""
    BUSINESS = "business"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    NATURE = "nature"
    TECHNOLOGY = "technology"
    PEOPLE = "people"
    ABSTRACT = "abstract"
    OBJECTS = "objects"
    BACKGROUNDS = "backgrounds"
    ANIMATIONS = "animations"

class LicenseType(Enum):
    """Tipos de licença"""
    STANDARD = "standard"
    PREMIUM = "premium"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    CUSTOM = "custom"

@dataclass
class AssetMetadata:
    """Metadados extraídos do asset"""
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    format: Optional[str] = None
    color_profile: Optional[str] = None
    exif_data: Optional[Dict[str, Any]] = None
    audio_info: Optional[Dict[str, Any]] = None
    video_info: Optional[Dict[str, Any]] = None

@dataclass
class ProcessingResult:
    """Resultado do processamento de um asset"""
    success: bool
    asset_id: Optional[int] = None
    thumbnail_path: Optional[str] = None
    optimized_variants: Optional[Dict[str, str]] = None
    metadata: Optional[AssetMetadata] = None
    error: Optional[str] = None

class AssetLibraryService:
    """
    Serviço de gerenciamento da biblioteca de assets.
    
    Responsável por:
    - Upload e processamento de assets
    - Extração de metadados
    - Geração de thumbnails
    - Sistema de busca e filtros
    - Avaliações e favoritos
    - Marketplace de assets
    """
    
    def __init__(self):
        self.upload_directory = Path("app/static/assets")
        self.thumbnail_directory = Path("app/static/thumbnails/assets")
        self.temp_directory = Path("temp/assets")
        
        # Criar diretórios se não existirem
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        self.thumbnail_directory.mkdir(parents=True, exist_ok=True)
        self.temp_directory.mkdir(parents=True, exist_ok=True)
        
        # Configurações de processamento
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.thumbnail_size = (300, 300)
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        self.supported_video_formats = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}
        self.supported_audio_formats = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
        
        logger.info("✅ Asset Library Service inicializado")
    
    def upload_asset(self, 
                    file_data: BinaryIO,
                    filename: str,
                    asset_data: AssetCreate,
                    user_id: int,
                    db: Session = None) -> ProcessingResult:
        """Upload e processamento de um novo asset."""
        if not DATABASE_AVAILABLE:
            return ProcessingResult(success=False, error="Database não disponível")
        
        if db is None:
            db = get_db_session()
        
        try:
            # Validar arquivo
            file_extension = Path(filename).suffix.lower()
            if not self._is_supported_format(file_extension):
                return ProcessingResult(success=False, error=f"Formato {file_extension} não suportado")
            
            # Gerar nome único
            file_uuid = str(uuid.uuid4())
            safe_filename = f"{file_uuid}{file_extension}"
            file_path = self.upload_directory / safe_filename
            
            # Salvar arquivo
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_data, f)
            
            # Verificar tamanho
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                file_path.unlink()
                return ProcessingResult(success=False, error="Arquivo muito grande")
            
            # Extrair metadados
            metadata = self._extract_metadata(file_path)
            
            # Gerar thumbnail
            thumbnail_path = self._generate_thumbnail(file_path, file_uuid)
            
            # Calcular hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Criar asset no banco
            asset = Asset(
                name=asset_data.name,
                description=asset_data.description,
                tipo=asset_data.tipo,
                subtipo=asset_data.subtipo,
                caminho_arquivo=str(file_path),
                file_size=file_size,
                file_hash=file_hash,
                mime_type=metadata.mime_type,
                scene_id=asset_data.scene_id,
                project_id=asset_data.project_id,
                is_library_asset=asset_data.is_library_asset,
                is_public=asset_data.is_public,
                is_premium=asset_data.is_premium,
                library_category=asset_data.library_category,
                library_tags=json.dumps(asset_data.library_tags) if asset_data.library_tags else None,
                license_type=asset_data.license_type,
                width=metadata.width,
                height=metadata.height,
                duration=metadata.duration,
                format=metadata.format,
                color_profile=metadata.color_profile,
                metadata_json=json.dumps(metadata.__dict__),
                thumbnail_path=thumbnail_path,
                created_by=user_id,
                processing_status="ready"
            )
            
            # Aplicar outras configurações do asset_data
            for field in ['posicao_x', 'posicao_y', 'escala', 'rotacao', 'opacidade', 'camada',
                         'largura', 'altura', 'volume', 'loop', 'fade_in', 'fade_out',
                         'texto_conteudo', 'fonte_familia', 'fonte_tamanho', 'fonte_cor']:
                if hasattr(asset_data, field):
                    setattr(asset, field, getattr(asset_data, field))
            
            db.add(asset)
            db.commit()
            db.refresh(asset)
            
            # Processar otimizações em background
            optimized_variants = self._create_optimized_variants(file_path, file_uuid, metadata)
            
            if optimized_variants:
                asset.optimized_variants = json.dumps(optimized_variants)
                db.commit()
            
            logger.info(f"Asset uploaded: {asset.name} por usuário {user_id}")
            
            return ProcessingResult(
                success=True,
                asset_id=asset.id,
                thumbnail_path=thumbnail_path,
                optimized_variants=optimized_variants,
                metadata=metadata
            )
            
        except Exception as e:
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            
            if db:
                db.rollback()
            
            logger.error(f"Erro no upload de asset: {e}")
            return ProcessingResult(success=False, error=str(e))
        finally:
            if db:
                db.close()
    
    def search_assets(self,
                     query: Optional[str] = None,
                     asset_type: Optional[str] = None,
                     category: Optional[str] = None,
                     is_public: Optional[bool] = None,
                     is_premium: Optional[bool] = None,
                     license_type: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     user_id: Optional[int] = None,
                     min_rating: Optional[float] = None,
                     sort_by: str = "created_at",
                     sort_order: str = "desc",
                     skip: int = 0,
                     limit: int = 50,
                     db: Session = None) -> List[AssetResponse]:
        """Buscar assets na biblioteca com filtros avançados."""
        if not DATABASE_AVAILABLE:
            return []
        
        if db is None:
            db = get_db_session()
        
        try:
            query_obj = db.query(Asset).filter(Asset.is_library_asset == True)
            
            # Filtros de acesso
            if user_id is not None:
                # Mostrar assets públicos OU do usuário
                query_obj = query_obj.filter(
                    or_(
                        Asset.is_public == True,
                        Asset.created_by == user_id
                    )
                )
            elif is_public is not None:
                query_obj = query_obj.filter(Asset.is_public == is_public)
            
            # Filtros de conteúdo
            if query:
                search_term = f"%{query}%"
                query_obj = query_obj.filter(
                    or_(
                        Asset.name.ilike(search_term),
                        Asset.description.ilike(search_term),
                        Asset.library_tags.ilike(search_term)
                    )
                )
            
            if asset_type:
                query_obj = query_obj.filter(Asset.tipo == asset_type)
            
            if category:
                query_obj = query_obj.filter(Asset.library_category == category)
            
            if is_premium is not None:
                query_obj = query_obj.filter(Asset.is_premium == is_premium)
            
            if license_type:
                query_obj = query_obj.filter(Asset.license_type == license_type)
            
            if min_rating is not None:
                query_obj = query_obj.filter(Asset.rating_avg >= min_rating)
            
            if tags:
                for tag in tags:
                    query_obj = query_obj.filter(Asset.library_tags.ilike(f"%{tag}%"))
            
            # Ordenação
            order_column = getattr(Asset, sort_by, Asset.created_at)
            if sort_order.lower() == "desc":
                order_column = desc(order_column)
            
            query_obj = query_obj.order_by(order_column)
            
            # Paginação
            assets = query_obj.offset(skip).limit(limit).all()
            
            return [AssetResponse.from_orm(asset) for asset in assets]
            
        finally:
            db.close()
    
    def get_asset(self, asset_id: int, user_id: Optional[int] = None, db: Session = None) -> Optional[AssetResponse]:
        """Obter asset por ID."""
        if not DATABASE_AVAILABLE:
            return None
        
        if db is None:
            db = get_db_session()
        
        try:
            query_obj = db.query(Asset).filter(Asset.id == asset_id)
            
            # Verificar acesso
            if user_id is not None:
                query_obj = query_obj.filter(
                    or_(
                        Asset.is_public == True,
                        Asset.created_by == user_id
                    )
                )
            
            asset = query_obj.first()
            if asset:
                # Incrementar contador de visualizações
                asset.usage_count = (asset.usage_count or 0) + 1
                db.commit()
                
                return AssetResponse.from_orm(asset)
            
            return None
            
        finally:
            db.close()
    
    def update_asset(self, asset_id: int, asset_data: AssetUpdate, user_id: int, db: Session = None) -> Optional[AssetResponse]:
        """Atualizar asset."""
        if not DATABASE_AVAILABLE:
            return None
        
        if db is None:
            db = get_db_session()
        
        try:
            asset = db.query(Asset).filter(
                and_(
                    Asset.id == asset_id,
                    Asset.created_by == user_id
                )
            ).first()
            
            if not asset:
                return None
            
            # Atualizar campos
            update_data = asset_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == 'library_tags' and value is not None:
                    setattr(asset, field, json.dumps(value))
                elif field in ['filters', 'animacao_config', 'custom_properties'] and value is not None:
                    setattr(asset, field, json.dumps(value))
                else:
                    setattr(asset, field, value)
            
            asset.last_modified_by = user_id
            
            db.commit()
            db.refresh(asset)
            
            logger.info(f"Asset atualizado: {asset.name}")
            return AssetResponse.from_orm(asset)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao atualizar asset: {e}")
            raise
        finally:
            db.close()
    
    def delete_asset(self, asset_id: int, user_id: int, db: Session = None) -> bool:
        """Deletar asset."""
        if not DATABASE_AVAILABLE:
            return False
        
        if db is None:
            db = get_db_session()
        
        try:
            asset = db.query(Asset).filter(
                and_(
                    Asset.id == asset_id,
                    Asset.created_by == user_id
                )
            ).first()
            
            if not asset:
                return False
            
            # Remover arquivos físicos
            if asset.caminho_arquivo and Path(asset.caminho_arquivo).exists():
                Path(asset.caminho_arquivo).unlink()
            
            if asset.thumbnail_path and Path(asset.thumbnail_path).exists():
                Path(asset.thumbnail_path).unlink()
            
            # Remover variantes otimizadas
            if asset.optimized_variants:
                variants = json.loads(asset.optimized_variants)
                for variant_path in variants.values():
                    if Path(variant_path).exists():
                        Path(variant_path).unlink()
            
            db.delete(asset)
            db.commit()
            
            logger.info(f"Asset deletado: {asset.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao deletar asset: {e}")
            return False
        finally:
            db.close()
    
    def rate_asset(self, asset_id: int, rating: int, comment: Optional[str], user_id: int, db: Session = None) -> Optional[AssetRatingResponse]:
        """Avaliar um asset."""
        if not DATABASE_AVAILABLE:
            return None
        
        if db is None:
            db = get_db_session()
        
        try:
            # Verificar se já existe avaliação do usuário
            existing_rating = db.query(AssetRating).filter(
                and_(
                    AssetRating.asset_id == asset_id,
                    AssetRating.user_id == user_id
                )
            ).first()
            
            if existing_rating:
                # Atualizar avaliação existente
                existing_rating.rating = rating
                existing_rating.comment = comment
                asset_rating = existing_rating
            else:
                # Criar nova avaliação
                asset_rating = AssetRating(
                    asset_id=asset_id,
                    user_id=user_id,
                    rating=rating,
                    comment=comment
                )
                db.add(asset_rating)
            
            db.flush()
            
            # Recalcular rating médio do asset
            avg_rating = db.query(func.avg(AssetRating.rating)).filter(
                AssetRating.asset_id == asset_id
            ).scalar()
            
            rating_count = db.query(func.count(AssetRating.id)).filter(
                AssetRating.asset_id == asset_id
            ).scalar()
            
            # Atualizar asset
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if asset:
                asset.rating_avg = float(avg_rating) if avg_rating else None
                asset.rating_count = rating_count
            
            db.commit()
            db.refresh(asset_rating)
            
            logger.info(f"Asset {asset_id} avaliado com {rating} estrelas por usuário {user_id}")
            return AssetRatingResponse.from_orm(asset_rating)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao avaliar asset: {e}")
            return None
        finally:
            db.close()
    
    def toggle_favorite(self, asset_id: int, user_id: int, db: Session = None) -> bool:
        """Alternar favorito de um asset."""
        if not DATABASE_AVAILABLE:
            return False
        
        if db is None:
            db = get_db_session()
        
        try:
            # Esta implementação seria mais complexa com uma tabela de favoritos
            # Por simplicidade, vamos usar um campo no asset
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return False
            
            # Toggle do favorito (implementação simplificada)
            asset.is_favorite = not asset.is_favorite
            db.commit()
            
            return asset.is_favorite
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao alternar favorito: {e}")
            return False
        finally:
            db.close()
    
    def get_asset_statistics(self, db: Session = None) -> Dict[str, Any]:
        """Obter estatísticas da biblioteca de assets."""
        if not DATABASE_AVAILABLE:
            return {}
        
        if db is None:
            db = get_db_session()
        
        try:
            stats = {}
            
            # Total de assets
            stats['total_assets'] = db.query(func.count(Asset.id)).filter(
                Asset.is_library_asset == True
            ).scalar()
            
            # Assets públicos
            stats['public_assets'] = db.query(func.count(Asset.id)).filter(
                and_(Asset.is_library_asset == True, Asset.is_public == True)
            ).scalar()
            
            # Assets premium
            stats['premium_assets'] = db.query(func.count(Asset.id)).filter(
                and_(Asset.is_library_asset == True, Asset.is_premium == True)
            ).scalar()
            
            # Por tipo
            stats['by_type'] = {}
            for asset_type in AssetType:
                count = db.query(func.count(Asset.id)).filter(
                    and_(Asset.is_library_asset == True, Asset.tipo == asset_type.value)
                ).scalar()
                stats['by_type'][asset_type.value] = count
            
            # Por categoria
            stats['by_category'] = {}
            for category in AssetCategory:
                count = db.query(func.count(Asset.id)).filter(
                    and_(
                        Asset.is_library_asset == True,
                        Asset.library_category == category.value
                    )
                ).scalar()
                stats['by_category'][category.value] = count
            
            # Assets mais populares
            stats['most_popular'] = []
            popular_assets = db.query(Asset).filter(
                Asset.is_library_asset == True
            ).order_by(desc(Asset.usage_count)).limit(10).all()
            
            for asset in popular_assets:
                stats['most_popular'].append({
                    'id': asset.id,
                    'name': asset.name,
                    'usage_count': asset.usage_count,
                    'rating_avg': asset.rating_avg
                })
            
            # Tamanho total da biblioteca
            total_size = db.query(func.sum(Asset.file_size)).filter(
                Asset.is_library_asset == True
            ).scalar()
            stats['total_size_mb'] = round((total_size or 0) / 1024 / 1024, 2)
            
            return stats
            
        finally:
            db.close()
    
    def _is_supported_format(self, file_extension: str) -> bool:
        """Verificar se o formato é suportado."""
        return (file_extension in self.supported_image_formats or
                file_extension in self.supported_video_formats or
                file_extension in self.supported_audio_formats)
    
    def _extract_metadata(self, file_path: Path) -> AssetMetadata:
        """Extrair metadados do arquivo."""
        file_size = file_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        metadata = AssetMetadata(
            file_size=file_size,
            mime_type=mime_type or "application/octet-stream"
        )
        
        file_extension = file_path.suffix.lower()
        
        # Metadados de imagem
        if file_extension in self.supported_image_formats and PILLOW_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    metadata.width, metadata.height = img.size
                    metadata.format = img.format
                    metadata.color_profile = img.mode
                    
                    # EXIF data
                    if hasattr(img, '_getexif') and img._getexif():
                        exif_data = {}
                        for tag_id, value in img._getexif().items():
                            tag = TAGS.get(tag_id, tag_id)
                            exif_data[tag] = str(value)
                        metadata.exif_data = exif_data
            except Exception as e:
                logger.warning(f"Erro ao extrair metadados de imagem: {e}")
        
        # Metadados de vídeo
        elif file_extension in self.supported_video_formats and MOVIEPY_AVAILABLE:
            try:
                with mp.VideoFileClip(str(file_path)) as clip:
                    metadata.width = clip.w
                    metadata.height = clip.h
                    metadata.duration = clip.duration
                    metadata.format = file_extension[1:].upper()
                    
                    metadata.video_info = {
                        'fps': clip.fps,
                        'duration': clip.duration,
                        'audio': clip.audio is not None
                    }
            except Exception as e:
                logger.warning(f"Erro ao extrair metadados de vídeo: {e}")
        
        # Metadados de áudio
        elif file_extension in self.supported_audio_formats and MUTAGEN_AVAILABLE:
            try:
                audio_file = mutagen.File(str(file_path))
                if audio_file:
                    metadata.duration = audio_file.info.length
                    metadata.format = file_extension[1:].upper()
                    
                    metadata.audio_info = {
                        'bitrate': getattr(audio_file.info, 'bitrate', None),
                        'sample_rate': getattr(audio_file.info, 'sample_rate', None),
                        'channels': getattr(audio_file.info, 'channels', None)
                    }
            except Exception as e:
                logger.warning(f"Erro ao extrair metadados de áudio: {e}")
        
        return metadata
    
    def _generate_thumbnail(self, file_path: Path, file_uuid: str) -> Optional[str]:
        """Gerar thumbnail do arquivo."""
        if not PILLOW_AVAILABLE:
            return None
        
        file_extension = file_path.suffix.lower()
        thumbnail_path = self.thumbnail_directory / f"{file_uuid}_thumb.jpg"
        
        try:
            # Thumbnail de imagem
            if file_extension in self.supported_image_formats:
                with Image.open(file_path) as img:
                    # Converter para RGB se necessário
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Redimensionar mantendo proporção
                    img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, 'JPEG', quality=85)
                    
                    return str(thumbnail_path)
            
            # Thumbnail de vídeo (primeiro frame)
            elif file_extension in self.supported_video_formats and MOVIEPY_AVAILABLE:
                with mp.VideoFileClip(str(file_path)) as clip:
                    # Pegar frame no segundo 1 ou primeiro frame
                    frame_time = min(1.0, clip.duration / 2)
                    frame = clip.get_frame(frame_time)
                    
                    # Converter para PIL Image
                    img = Image.fromarray(frame)
                    img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, 'JPEG', quality=85)
                    
                    return str(thumbnail_path)
            
        except Exception as e:
            logger.warning(f"Erro ao gerar thumbnail: {e}")
        
        return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcular hash SHA256 do arquivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _create_optimized_variants(self, file_path: Path, file_uuid: str, metadata: AssetMetadata) -> Optional[Dict[str, str]]:
        """Criar variantes otimizadas do arquivo."""
        variants = {}
        file_extension = file_path.suffix.lower()
        
        try:
            # Variantes de imagem
            if file_extension in self.supported_image_formats and PILLOW_AVAILABLE:
                # Versão pequena (para previews)
                small_path = self.upload_directory / f"{file_uuid}_small.jpg"
                with Image.open(file_path) as img:
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                    img.save(small_path, 'JPEG', quality=80, optimize=True)
                    variants['small'] = str(small_path)
                
                # Versão WebP (se não for WebP original)
                if file_extension != '.webp':
                    webp_path = self.upload_directory / f"{file_uuid}.webp"
                    with Image.open(file_path) as img:
                        img.save(webp_path, 'WEBP', quality=85, optimize=True)
                        variants['webp'] = str(webp_path)
            
            # Variantes de vídeo
            elif file_extension in self.supported_video_formats and MOVIEPY_AVAILABLE:
                # Versão comprimida (se for muito grande)
                if metadata.file_size > 50 * 1024 * 1024:  # 50MB
                    compressed_path = self.upload_directory / f"{file_uuid}_compressed.mp4"
                    with mp.VideoFileClip(str(file_path)) as clip:
                        # Reduzir qualidade se necessário
                        if clip.w > 1920:
                            clip = clip.resize(width=1920)
                        
                        clip.write_videofile(
                            str(compressed_path),
                            codec='libx264',
                            audio_codec='aac',
                            temp_audiofile='temp-audio.m4a',
                            remove_temp=True,
                            verbose=False,
                            logger=None
                        )
                        variants['compressed'] = str(compressed_path)
            
        except Exception as e:
            logger.warning(f"Erro ao criar variantes otimizadas: {e}")
        
        return variants if variants else None

# Instância global do serviço
asset_library_service = AssetLibraryService() 