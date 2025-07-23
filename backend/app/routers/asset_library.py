#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router de Biblioteca de Assets - TecnoCursos AI

Este módulo implementa endpoints REST completos para gerenciamento da biblioteca
de assets, incluindo upload, CRUD, busca avançada, sistema de avaliação e marketplace.

Funcionalidades:
- Upload e processamento de assets
- CRUD completo de assets
- Biblioteca pública e privada
- Busca avançada com filtros
- Sistema de avaliação e favoritos
- Marketplace de assets premium
- Estatísticas e analytics

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Body, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, BinaryIO
import json
import logging
import shutil
from pathlib import Path

from app.database import get_db
from app.auth import get_current_active_user, get_current_user_optional
from app.models import User, Asset, AssetRating, Project
from app.schemas import (
    AssetCreate, AssetUpdate, AssetResponse,
    AssetRatingCreate, AssetRatingUpdate, AssetRatingResponse
)
from app.logger import get_logger

# Importar serviços
try:
    from app.services.asset_library_service import asset_library_service
    ASSET_SERVICE_AVAILABLE = True
except ImportError:
    ASSET_SERVICE_AVAILABLE = False

logger = get_logger("asset_library_router")

router = APIRouter(
    prefix="/api/assets",
    tags=["🎨 Assets"],
    responses={404: {"description": "Asset não encontrado"}}
)

# ============================================================================
# UPLOAD DE ASSETS
# ============================================================================

@router.post("/upload", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo do asset"),
    name: str = Form(..., description="Nome do asset"),
    description: Optional[str] = Form(None, description="Descrição do asset"),
    tipo: str = Form(..., description="Tipo do asset"),
    subtipo: Optional[str] = Form(None, description="Subtipo específico"),
    scene_id: Optional[int] = Form(None, description="ID da cena (se aplicável)"),
    project_id: Optional[int] = Form(None, description="ID do projeto"),
    is_library_asset: bool = Form(False, description="Se é asset de biblioteca"),
    is_public: bool = Form(False, description="Se é público"),
    is_premium: bool = Form(False, description="Se é premium"),
    library_category: Optional[str] = Form(None, description="Categoria na biblioteca"),
    library_tags: Optional[str] = Form(None, description="Tags (separadas por vírgula)"),
    license_type: str = Form("standard", description="Tipo de licença"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload de novo asset com processamento automático.
    
    - **file**: Arquivo a ser uploaded
    - **name**: Nome identificador
    - **tipo**: Tipo do asset (image, video, audio, etc.)
    - **is_library_asset**: Se deve ir para a biblioteca
    - **is_public**: Se é público para outros usuários
    """
    
    if not ASSET_SERVICE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de assets não disponível"
        )
    
    try:
        # Preparar dados do asset
        tags_list = [tag.strip() for tag in library_tags.split(",")] if library_tags else None
        
        asset_data = AssetCreate(
            name=name,
            description=description,
            tipo=tipo,
            subtipo=subtipo,
            scene_id=scene_id,
            project_id=project_id,
            is_library_asset=is_library_asset,
            is_public=is_public,
            is_premium=is_premium,
            library_category=library_category,
            library_tags=tags_list,
            license_type=license_type
        )
        
        # Fazer upload usando o serviço
        result = asset_library_service.upload_asset(
            file.file, 
            file.filename,
            asset_data,
            current_user.id,
            db
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error or "Erro no upload do asset"
            )
        
        # Buscar asset criado
        asset = db.query(Asset).filter(Asset.id == result.asset_id).first()
        
        logger.info(f"Asset uploaded: {asset.name} por usuário {current_user.id}")
        return AssetResponse.from_orm(asset)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload de asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no upload"
        )

# ============================================================================
# BUSCA E LISTAGEM
# ============================================================================

@router.get("/", response_model=List[AssetResponse])
async def search_assets(
    query: Optional[str] = Query(None, description="Termo de busca"),
    asset_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    is_public: Optional[bool] = Query(None, description="Filtrar públicos"),
    is_premium: Optional[bool] = Query(None, description="Filtrar premium"),
    license_type: Optional[str] = Query(None, description="Tipo de licença"),
    tags: Optional[str] = Query(None, description="Tags (separadas por vírgula)"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Rating mínimo"),
    sort_by: str = Query("created_at", description="Campo para ordenação"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Ordem"),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(50, ge=1, le=100, description="Máximo de registros"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Buscar assets na biblioteca com filtros avançados.
    
    - **query**: Busca por nome, descrição ou tags
    - **asset_type**: image, video, audio, character, etc.
    - **category**: business, education, entertainment, etc.
    - **is_public**: assets públicos
    - **is_premium**: assets premium
    - **min_rating**: rating mínimo (0-5)
    """
    
    if not ASSET_SERVICE_AVAILABLE:
        return []
    
    try:
        # Converter tags para lista
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else None
        
        # Buscar assets
        assets = asset_library_service.search_assets(
            query=query,
            asset_type=asset_type,
            category=category,
            is_public=is_public,
            is_premium=is_premium,
            license_type=license_type,
            tags=tags_list,
            user_id=current_user.id if current_user else None,
            min_rating=min_rating,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            db=db
        )
        
        return assets
        
    except Exception as e:
        logger.error(f"Erro na busca de assets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na busca"
        )

@router.get("/library", response_model=List[AssetResponse])
async def get_library_assets(
    category: Optional[str] = Query(None, description="Categoria"),
    featured: bool = Query(False, description="Apenas em destaque"),
    public_only: bool = Query(True, description="Apenas públicos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Obter assets da biblioteca pública."""
    
    if not ASSET_SERVICE_AVAILABLE:
        return []
    
    try:
        # Buscar apenas assets de biblioteca
        assets = asset_library_service.search_assets(
            category=category,
            is_public=public_only,
            user_id=current_user.id if current_user else None,
            sort_by="usage_count" if featured else "created_at",
            sort_order="desc",
            skip=skip,
            limit=limit,
            db=db
        )
        
        # Filtrar apenas assets de biblioteca
        library_assets = [asset for asset in assets if asset.is_library_asset]
        
        return library_assets
        
    except Exception as e:
        logger.error(f"Erro ao obter assets da biblioteca: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )

@router.get("/my-assets", response_model=List[AssetResponse])
async def get_my_assets(
    asset_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    project_id: Optional[int] = Query(None, description="Filtrar por projeto"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter assets do usuário atual."""
    try:
        query = db.query(Asset).filter(Asset.created_by == current_user.id)
        
        if asset_type:
            query = query.filter(Asset.tipo == asset_type)
        
        if project_id:
            query = query.filter(Asset.project_id == project_id)
        
        query = query.order_by(Asset.created_at.desc())
        assets = query.offset(skip).limit(limit).all()
        
        return [AssetResponse.from_orm(asset) for asset in assets]
        
    except Exception as e:
        logger.error(f"Erro ao obter assets do usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )

# ============================================================================
# CRUD DE ASSETS
# ============================================================================

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Obter asset por ID."""
    
    if not ASSET_SERVICE_AVAILABLE:
        # Fallback para busca direta no banco
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado"
            )
        return AssetResponse.from_orm(asset)
    
    try:
        asset = asset_library_service.get_asset(
            asset_id, 
            current_user.id if current_user else None,
            db
        )
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado"
            )
        
        return asset
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )

@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualizar asset."""
    
    if not ASSET_SERVICE_AVAILABLE:
        # Fallback para atualização direta
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.created_by == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado"
            )
        
        # Atualizar campos
        update_data = asset_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        
        db.commit()
        db.refresh(asset)
        return AssetResponse.from_orm(asset)
    
    try:
        updated_asset = asset_library_service.update_asset(
            asset_id, asset_data, current_user.id, db
        )
        
        if not updated_asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado ou sem permissão"
            )
        
        return updated_asset
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar"
        )

@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deletar asset."""
    
    if not ASSET_SERVICE_AVAILABLE:
        # Fallback para deleção direta
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.created_by == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado"
            )
        
        asset_name = asset.name
        db.delete(asset)
        db.commit()
        return {"message": f"Asset '{asset_name}' deletado com sucesso"}
    
    try:
        success = asset_library_service.delete_asset(
            asset_id, current_user.id, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado ou sem permissão"
            )
        
        return {"message": "Asset deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar"
        )

# ============================================================================
# SISTEMA DE AVALIAÇÃO
# ============================================================================

@router.post("/{asset_id}/rate", response_model=AssetRatingResponse)
async def rate_asset(
    asset_id: int,
    rating_data: AssetRatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Avaliar um asset."""
    
    if not ASSET_SERVICE_AVAILABLE:
        # Implementação básica
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado"
            )
        
        # Verificar se já existe avaliação
        existing_rating = db.query(AssetRating).filter(
            AssetRating.asset_id == asset_id,
            AssetRating.user_id == current_user.id
        ).first()
        
        if existing_rating:
            existing_rating.rating = rating_data.rating
            existing_rating.comment = rating_data.comment
            asset_rating = existing_rating
        else:
            asset_rating = AssetRating(
                asset_id=asset_id,
                user_id=current_user.id,
                rating=rating_data.rating,
                comment=rating_data.comment
            )
            db.add(asset_rating)
        
        db.commit()
        db.refresh(asset_rating)
        return AssetRatingResponse.from_orm(asset_rating)
    
    try:
        rating = asset_library_service.rate_asset(
            asset_id, rating_data.rating, rating_data.comment, current_user.id, db
        )
        
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado"
            )
        
        return rating
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao avaliar asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao avaliar"
        )

@router.get("/{asset_id}/ratings", response_model=List[AssetRatingResponse])
async def get_asset_ratings(
    asset_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Obter avaliações de um asset."""
    
    # Verificar se asset existe
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset não encontrado"
        )
    
    try:
        ratings = db.query(AssetRating).filter(
            AssetRating.asset_id == asset_id
        ).order_by(AssetRating.created_at.desc()).offset(skip).limit(limit).all()
        
        return [AssetRatingResponse.from_orm(rating) for rating in ratings]
        
    except Exception as e:
        logger.error(f"Erro ao obter avaliações: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )

@router.post("/{asset_id}/favorite")
async def toggle_favorite(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Alternar favorito de um asset."""
    
    if not ASSET_SERVICE_AVAILABLE:
        # Implementação básica
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset não encontrado"
            )
        
        asset.is_favorite = not asset.is_favorite
        db.commit()
        
        return {
            "asset_id": asset_id,
            "is_favorite": asset.is_favorite,
            "message": "Favorito atualizado"
        }
    
    try:
        is_favorite = asset_library_service.toggle_favorite(
            asset_id, current_user.id, db
        )
        
        return {
            "asset_id": asset_id,
            "is_favorite": is_favorite,
            "message": "Favorito atualizado"
        }
        
    except Exception as e:
        logger.error(f"Erro ao alternar favorito: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )

# ============================================================================
# DOWNLOAD E ACESSO A ARQUIVOS
# ============================================================================

@router.get("/{asset_id}/download")
async def download_asset(
    asset_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Download do arquivo do asset."""
    
    # Buscar asset
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset não encontrado"
        )
    
    # Verificar permissão de acesso
    if not asset.is_public and (not current_user or asset.created_by != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Verificar se arquivo existe
    if not asset.caminho_arquivo or not Path(asset.caminho_arquivo).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    try:
        # Incrementar contador de downloads
        asset.download_count = (asset.download_count or 0) + 1
        db.commit()
        
        # Retornar arquivo
        return FileResponse(
            path=asset.caminho_arquivo,
            filename=f"{asset.name}_{asset.id}{Path(asset.caminho_arquivo).suffix}",
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.error(f"Erro no download do asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no download"
        )

@router.get("/{asset_id}/thumbnail")
async def get_asset_thumbnail(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """Obter thumbnail do asset."""
    
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset não encontrado"
        )
    
    if not asset.thumbnail_path or not Path(asset.thumbnail_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail não disponível"
        )
    
    return FileResponse(
        path=asset.thumbnail_path,
        media_type="image/jpeg"
    )

# ============================================================================
# ESTATÍSTICAS E ANALYTICS
# ============================================================================

@router.get("/statistics/library")
async def get_library_statistics(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obter estatísticas da biblioteca de assets."""
    
    if not ASSET_SERVICE_AVAILABLE:
        return {"error": "Serviço de estatísticas não disponível"}
    
    try:
        stats = asset_library_service.get_asset_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )

@router.get("/categories")
async def get_asset_categories():
    """Obter lista de categorias disponíveis."""
    
    categories = [
        {"value": "business", "label": "Negócios", "icon": "briefcase"},
        {"value": "education", "label": "Educação", "icon": "graduation-cap"},
        {"value": "entertainment", "label": "Entretenimento", "icon": "play"},
        {"value": "nature", "label": "Natureza", "icon": "leaf"},
        {"value": "technology", "label": "Tecnologia", "icon": "cpu"},
        {"value": "people", "label": "Pessoas", "icon": "users"},
        {"value": "abstract", "label": "Abstrato", "icon": "shapes"},
        {"value": "objects", "label": "Objetos", "icon": "cube"},
        {"value": "backgrounds", "label": "Fundos", "icon": "image"},
        {"value": "animations", "label": "Animações", "icon": "play-circle"}
    ]
    
    return {"categories": categories}

@router.get("/types")
async def get_asset_types():
    """Obter lista de tipos de assets disponíveis."""
    
    types = [
        {"value": "character", "label": "Personagem/Avatar", "extensions": [".png", ".svg", ".gif"]},
        {"value": "background", "label": "Fundo/Cenário", "extensions": [".jpg", ".png", ".webp"]},
        {"value": "music", "label": "Música", "extensions": [".mp3", ".wav", ".ogg"]},
        {"value": "sound_effect", "label": "Efeito Sonoro", "extensions": [".mp3", ".wav"]},
        {"value": "image", "label": "Imagem", "extensions": [".jpg", ".png", ".gif", ".webp"]},
        {"value": "video", "label": "Vídeo", "extensions": [".mp4", ".webm", ".mov"]},
        {"value": "audio", "label": "Áudio", "extensions": [".mp3", ".wav", ".ogg", ".m4a"]},
        {"value": "text", "label": "Texto", "extensions": []},
        {"value": "overlay", "label": "Sobreposição", "extensions": [".png", ".svg"]},
        {"value": "icon", "label": "Ícone", "extensions": [".svg", ".png"]},
        {"value": "logo", "label": "Logo", "extensions": [".svg", ".png"]},
        {"value": "template", "label": "Template", "extensions": []}
    ]
    
    return {"types": types}

# ============================================================================
# OPERAÇÕES EM LOTE
# ============================================================================

@router.post("/batch/delete")
async def batch_delete_assets(
    asset_ids: List[int] = Body(..., description="Lista de IDs dos assets"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deletar múltiplos assets em lote."""
    
    try:
        deleted_count = 0
        errors = []
        
        for asset_id in asset_ids:
            try:
                if ASSET_SERVICE_AVAILABLE:
                    success = asset_library_service.delete_asset(asset_id, current_user.id, db)
                    if success:
                        deleted_count += 1
                    else:
                        errors.append(f"Asset {asset_id}: não encontrado ou sem permissão")
                else:
                    # Fallback
                    asset = db.query(Asset).filter(
                        Asset.id == asset_id,
                        Asset.created_by == current_user.id
                    ).first()
                    
                    if asset:
                        db.delete(asset)
                        deleted_count += 1
                    else:
                        errors.append(f"Asset {asset_id}: não encontrado")
                        
            except Exception as e:
                errors.append(f"Asset {asset_id}: {str(e)}")
        
        if not ASSET_SERVICE_AVAILABLE:
            db.commit()
        
        return {
            "deleted_count": deleted_count,
            "total_requested": len(asset_ids),
            "errors": errors,
            "success": deleted_count > 0
        }
        
    except Exception as e:
        if not ASSET_SERVICE_AVAILABLE:
            db.rollback()
        logger.error(f"Erro na deleção em lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na deleção em lote"
        )

@router.put("/batch/update")
async def batch_update_assets(
    updates: Dict[int, AssetUpdate] = Body(..., description="Dicionário de ID -> dados de atualização"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualizar múltiplos assets em lote."""
    
    try:
        updated_count = 0
        errors = []
        
        for asset_id, asset_data in updates.items():
            try:
                if ASSET_SERVICE_AVAILABLE:
                    updated_asset = asset_library_service.update_asset(asset_id, asset_data, current_user.id, db)
                    if updated_asset:
                        updated_count += 1
                    else:
                        errors.append(f"Asset {asset_id}: não encontrado ou sem permissão")
                else:
                    # Fallback
                    asset = db.query(Asset).filter(
                        Asset.id == asset_id,
                        Asset.created_by == current_user.id
                    ).first()
                    
                    if asset:
                        update_data = asset_data.dict(exclude_unset=True)
                        for field, value in update_data.items():
                            setattr(asset, field, value)
                        updated_count += 1
                    else:
                        errors.append(f"Asset {asset_id}: não encontrado")
                        
            except Exception as e:
                errors.append(f"Asset {asset_id}: {str(e)}")
        
        if not ASSET_SERVICE_AVAILABLE:
            db.commit()
        
        return {
            "updated_count": updated_count,
            "total_requested": len(updates),
            "errors": errors,
            "success": updated_count > 0
        }
        
    except Exception as e:
        if not ASSET_SERVICE_AVAILABLE:
            db.rollback()
        logger.error(f"Erro na atualização em lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na atualização em lote"
        ) 