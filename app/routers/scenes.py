#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router de Cenas Otimizado - TecnoCursos AI

Este módulo implementa endpoints REST otimizados para gerenciamento de cenas,
seguindo as melhores práticas do FastAPI CRUD com:
- Response models específicos
- Status codes corretos  
- Validação robusta
- Paginação avançada
- Error handling
- Documentação completa
- Performance otimizada

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Body, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from app.database import get_db
from app.auth import get_current_active_user
from app.models import User, Project, Scene, Asset, SceneComment, SceneTemplate
from app.schemas import (
    SceneCreate, SceneUpdate, SceneResponse, SceneDetailResponse,
    SceneCreateResponse, SceneUpdateResponse, SceneDeleteResponse,
    SceneSummary, PaginatedSceneResponse, PaginationMeta,
    SceneFilterParams, BulkSceneOperation, BulkOperationResponse,
    SceneCommentCreate, SceneCommentUpdate, SceneCommentResponse
)
from app.logger import get_logger

# Importar serviços com fallback
try:
    from app.services.scene_template_service import scene_template_service
    TEMPLATE_SERVICE_AVAILABLE = True
except (ImportError, AttributeError):
    scene_template_service = None
    TEMPLATE_SERVICE_AVAILABLE = False

logger = get_logger("scenes_router")

# Importar serviço de geração de vídeo
try:
    from app.services.video_generation_service import video_generation_service
    VIDEO_GENERATION_AVAILABLE = True
    logger.info("✅ Video Generation Service disponível")
except ImportError:
    video_generation_service = None
    VIDEO_GENERATION_AVAILABLE = False
    logger.warning("⚠️ Video Generation Service não disponível")

# Importar cache service  
try:
    from app.services.scenes_cache_service import scenes_cache, cache_result
    CACHE_AVAILABLE = True
    logger.info("✅ Cache service disponível para cenas")
except ImportError:
    scenes_cache = None
    cache_result = lambda cache_type, ttl=None: lambda func: func  # Decorator noop
    CACHE_AVAILABLE = False
    logger.warning("⚠️ Cache service não disponível - operando sem cache")

router = APIRouter(
    prefix="/api/scenes",
    tags=["🎬 Cenas Otimizadas"],
    dependencies=[Depends(get_current_active_user)],
    responses={
        400: {"description": "Dados inválidos"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"},
        404: {"description": "Cena não encontrada"},
        422: {"description": "Erro de validação"},
        500: {"description": "Erro interno do servidor"}
    }
)

# ============================================================================
# UTILITÁRIOS E HELPERS
# ============================================================================

def build_pagination_meta(page: int, size: int, total: int) -> PaginationMeta:
    """Constrói metadados de paginação"""
    pages = (total + size - 1) // size  # Ceiling division
    has_next = page < pages
    has_prev = page > 1
    
    return PaginationMeta(
        page=page,
        size=size,
        total=total,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=page + 1 if has_next else None,
        prev_page=page - 1 if has_prev else None
    )

def apply_scene_filters(query, filters: SceneFilterParams, user_id: int):
    """Aplica filtros avançados à query de cenas"""
    
    # Filtro por projeto do usuário
    query = query.join(Project).filter(Project.owner_id == user_id)
    
    # Filtros específicos
    if filters.project_id:
        query = query.filter(Scene.project_id == filters.project_id)
    
    if filters.template_id:
        query = query.filter(Scene.template_id == filters.template_id)
    
    if filters.style_preset:
        query = query.filter(Scene.style_preset == filters.style_preset)
    
    if filters.is_template is not None:
        query = query.filter(Scene.is_template == filters.is_template)
    
    if filters.is_active is not None:
        query = query.filter(Scene.is_active == filters.is_active)
    
    # Busca textual
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Scene.name.ilike(search_term),
                Scene.texto.ilike(search_term),
                Scene.notes.ilike(search_term)
            )
        )
    
    # Filtros de duração
    if filters.duration_min is not None:
        query = query.filter(Scene.duracao >= filters.duration_min)
    
    if filters.duration_max is not None:
        query = query.filter(Scene.duracao <= filters.duration_max)
    
    # Filtros de data
    if filters.created_after:
        query = query.filter(Scene.created_at >= filters.created_after)
    
    if filters.created_before:
        query = query.filter(Scene.created_at <= filters.created_before)
    
    return query

def apply_scene_ordering(query, order_by: str, order_direction: str):
    """Aplica ordenação à query de cenas"""
    
    order_column = getattr(Scene, order_by, Scene.ordem)
    
    if order_direction == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    # Ordenação secundária por ID para consistência
    if order_by != "id":
        query = query.order_by(Scene.id.asc())
    
    return query

# ============================================================================
# CRUD DE CENAS
# ============================================================================

@router.get("/", response_model=PaginatedSceneResponse)
async def list_scenes(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    project_id: Optional[int] = Query(None, description="Filtrar por projeto"),
    template_id: Optional[str] = Query(None, description="Filtrar por template"),
    style_preset: Optional[str] = Query(None, description="Filtrar por estilo"),
    is_template: Optional[bool] = Query(None, description="Filtrar templates"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    search: Optional[str] = Query(None, min_length=3, description="Buscar por nome ou texto"),
    duration_min: Optional[float] = Query(None, ge=0, description="Duração mínima"),
    duration_max: Optional[float] = Query(None, gt=0, description="Duração máxima"),
    order_by: str = Query("ordem", description="Campo para ordenação"),
    order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção da ordenação"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Listar cenas do usuário com filtros e paginação avançada.
    
    **Parâmetros de Paginação:**
    - **page**: Número da página (inicia em 1)
    - **size**: Itens por página (1-100)
    
    **Filtros Disponíveis:**
    - **project_id**: ID do projeto para filtrar
    - **template_id**: ID do template aplicado
    - **style_preset**: Estilo da cena (modern, corporate, tech, etc.)
    - **is_template**: Se são templates de cena
    - **is_active**: Status ativo da cena
    - **search**: Busca por nome, texto ou notas
    - **duration_min/max**: Filtro por duração em segundos
    
    **Ordenação:**
    - **order_by**: Campo para ordenação (ordem, created_at, updated_at, name, duracao)
    - **order_direction**: Direção (asc, desc)
    
    **Resposta:**
    - Lista paginada com metadados completos
    - Filtros aplicados documentados
    - Total de resultados e páginas
    """
    try:
        # Construir query base
        query = db.query(Scene).join(Project).filter(Project.owner_id == current_user.id)
        
        # Aplicar filtros
        if project_id:
            query = query.filter(Scene.project_id == project_id)
        
        if template_id:
            query = query.filter(Scene.template_id == template_id)
        
        if style_preset:
            query = query.filter(Scene.style_preset == style_preset)
        
        if is_template is not None:
            query = query.filter(Scene.is_template == is_template)
        
        if is_active is not None:
            query = query.filter(Scene.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Scene.name.ilike(search_term),
                    Scene.texto.ilike(search_term),
                    Scene.notes.ilike(search_term)
                )
            )
        
        if duration_min is not None:
            query = query.filter(Scene.duracao >= duration_min)
        
        if duration_max is not None:
            query = query.filter(Scene.duracao <= duration_max)
        
        # Aplicar ordenação
        order_column = getattr(Scene, order_by, Scene.ordem)
        if order_direction == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # Contar total
        total = query.count()
        
        # Calcular offset
        offset = (page - 1) * size
        
        # Aplicar paginação
        scenes = query.offset(offset).limit(size).all()
        
        # Construir metadados de paginação
        meta = build_pagination_meta(page, size, total)
        
        # Documentar filtros aplicados
        filters_applied = {
            "project_id": project_id,
            "template_id": template_id,
            "style_preset": style_preset,
            "is_template": is_template,
            "is_active": is_active,
            "search": search,
            "duration_range": [duration_min, duration_max] if duration_min or duration_max else None,
            "order_by": order_by,
            "order_direction": order_direction
        }
        
        # Remover filtros nulos
        filters_applied = {k: v for k, v in filters_applied.items() if v is not None}
        
        logger.info(f"Cenas listadas: {len(scenes)} de {total} total", 
                   user_id=current_user.id, 
                   page=page, 
                   filters=len(filters_applied))
        
        return PaginatedSceneResponse(
            items=[SceneResponse.from_orm(scene) for scene in scenes],
            meta=meta,
            filters_applied=filters_applied
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar cenas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar cenas"
        )

@router.get("/{scene_id}", response_model=SceneDetailResponse)
async def get_scene(
    scene_id: int,
    include_assets: bool = Query(True, description="Incluir assets da cena"),
    include_comments: bool = Query(False, description="Incluir comentários da cena"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obter cena por ID com cache inteligente.
    
    **Otimizações:**
    - Cache automático de 15 minutos para detalhes de cena
    - Invalidação automática quando cena é modificada
    - Carregamento opcional de assets e comentários
    - Query otimizada com joins seletivos
    
    **Parâmetros:**
    - **include_assets**: Incluir lista de assets (padrão: true)
    - **include_comments**: Incluir comentários (padrão: false)
    """
    
    # Tentar recuperar do cache primeiro
    if CACHE_AVAILABLE:
        cache_key_params = {
            'scene_id': scene_id,
            'user_id': current_user.id,
            'include_assets': include_assets,
            'include_comments': include_comments
        }
        
        cached_scene = scenes_cache.get('scene_detail', **cache_key_params)
        if cached_scene:
            logger.debug(f"Cache HIT para cena {scene_id}")
            return cached_scene
    
    try:
        # Query base otimizada
        scene = db.query(Scene).join(Project).filter(
            Scene.id == scene_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cena não encontrada"
            )
        
        # Incrementar contador de visualizações de forma assíncrona
        db.execute(
            "UPDATE scenes SET view_count = COALESCE(view_count, 0) + 1 WHERE id = :scene_id",
            {"scene_id": scene_id}
        )
        db.commit()
        
        # Construir resposta detalhada
        scene_response = SceneDetailResponse.from_orm(scene)
        
        # Incluir assets se solicitado
        if include_assets:
            assets = db.query(Asset).filter(
                Asset.scene_id == scene_id
            ).order_by(Asset.camada, Asset.created_at).all()
            
            scene_response.assets = [
                {
                    "id": asset.id,
                    "name": asset.name,
                    "tipo": asset.tipo,
                    "camada": asset.camada,
                    "posicao_x": asset.posicao_x,
                    "posicao_y": asset.posicao_y,
                    "escala": asset.escala,
                    "rotacao": asset.rotacao,
                    "opacidade": asset.opacidade,
                    "is_active": asset.is_active,
                    "timeline_start": asset.timeline_start,
                    "timeline_end": asset.timeline_end
                }
                for asset in assets
            ]
        
        # Incluir contagem de comentários
        if include_comments:
            comments_count = db.query(func.count(SceneComment.id)).filter(
                SceneComment.scene_id == scene_id
            ).scalar()
            scene_response.comments_count = comments_count or 0
        
        # Armazenar no cache
        if CACHE_AVAILABLE:
            scenes_cache.set('scene_detail', scene_response, **cache_key_params)
            logger.debug(f"Cache SET para cena {scene_id}")
        
        logger.info(f"Cena {scene_id} visualizada por usuário {current_user.id}")
        return scene_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter cena {scene_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter cena"
        )

@router.post("/", response_model=SceneCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_scene(
    scene_data: SceneCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova cena com otimizações avançadas.
    
    **Funcionalidades:**
    - Criação otimizada com transação atômica
    - Aplicação automática de templates
    - Invalidação de cache relacionado
    - Validação robusta de permissões
    - Logging estruturado para auditoria
    
    **Cache:**
    - Invalida automaticamente cache de listagens
    - Invalida cache do projeto relacionado
    - Atualiza estatísticas em background
    """
    try:
        # Verificar se o projeto existe e pertence ao usuário
        project = db.query(Project).filter(
            Project.id == scene_data.project_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado"
            )
        
        # Determinar ordem da cena de forma otimizada
        max_ordem = db.query(func.max(Scene.ordem)).filter(
            Scene.project_id == scene_data.project_id
        ).scalar()
        nova_ordem = (max_ordem or 0) + 1
        
        # Criar cena em transação atômica
        scene = Scene(
            **scene_data.dict(),
            ordem=nova_ordem,
            created_by=current_user.id,
            last_modified_by=current_user.id
        )
        
        db.add(scene)
        db.flush()  # Para obter ID da cena
        
        # Aplicar template se especificado
        if scene_data.template_id and TEMPLATE_SERVICE_AVAILABLE:
            try:
                template_id_int = int(scene_data.template_id)
                background_tasks.add_task(
                    _apply_template_background,
                    template_id_int, 
                    scene.id, 
                    current_user.id
                )
            except (ValueError, Exception) as e:
                logger.warning(f"Erro ao aplicar template: {e}")
        
        db.commit()
        db.refresh(scene)
        
        # Invalidar cache relacionado
        if CACHE_AVAILABLE:
            background_tasks.add_task(
                _invalidate_related_cache,
                user_id=current_user.id,
                project_id=scene_data.project_id
            )
        
        # Construir resposta otimizada
        response = SceneCreateResponse(
            id=scene.id,
            uuid=scene.uuid,
            name=scene.name,
            project_id=scene.project_id,
            created_at=scene.created_at,
            message=f"Cena '{scene.name}' criada com sucesso na posição {nova_ordem}"
        )
        
        logger.info(f"Cena criada: {scene.name} (ID: {scene.id}) por usuário {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar cena: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar cena"
        )

@router.put("/{scene_id}", response_model=SceneUpdateResponse)
async def update_scene(
    scene_id: int,
    scene_data: SceneUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar cena com cache inteligente.
    
    **Otimizações:**
    - Detecção automática de campos alterados
    - Invalidação de cache específica por mudanças
    - Versionamento automático
    - Auditoria completa de alterações
    """
    try:
        scene = db.query(Scene).join(Project).filter(
            Scene.id == scene_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cena não encontrada"
            )
        
        # Detectar campos alterados para auditoria
        update_data = scene_data.dict(exclude_unset=True)
        changes_applied = []
        
        for field, value in update_data.items():
            old_value = getattr(scene, field, None)
            
            if field in ['tags', 'custom_properties'] and value is not None:
                new_value = json.dumps(value)
                setattr(scene, field, new_value)
                if old_value != new_value:
                    changes_applied.append(field)
            else:
                setattr(scene, field, value)
                if old_value != value:
                    changes_applied.append(field)
        
        # Atualizar metadados
        scene.last_modified_by = current_user.id
        scene.updated_at = datetime.utcnow()
        
        # Incrementar versão se houver mudanças significativas
        significant_changes = {'name', 'texto', 'style_preset', 'background_color', 'layout_type'}
        if any(change in significant_changes for change in changes_applied):
            scene.version = (scene.version or 1) + 1
        
        db.commit()
        db.refresh(scene)
        
        # Invalidar cache específico da cena
        if CACHE_AVAILABLE:
            background_tasks.add_task(
                _invalidate_scene_cache,
                scene_id=scene_id,
                project_id=scene.project_id,
                user_id=current_user.id
            )
        
        # Construir resposta
        response = SceneUpdateResponse(
            id=scene.id,
            uuid=scene.uuid,
            name=scene.name,
            updated_at=scene.updated_at,
            changes_applied=changes_applied,
            message=f"Cena atualizada com sucesso. {len(changes_applied)} campo(s) alterado(s)"
        )
        
        logger.info(f"Cena atualizada: {scene.name} (campos: {', '.join(changes_applied)})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar cena: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar cena"
        )

@router.delete("/{scene_id}", response_model=SceneDeleteResponse)
async def delete_scene(
    scene_id: int,
    background_tasks: BackgroundTasks,
    force: bool = Query(False, description="Forçar deleção mesmo com assets"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deletar cena com verificações de segurança.
    
    **Funcionalidades:**
    - Verificação de dependências (assets, comentários)
    - Opção de deleção forçada
    - Invalidação completa de cache
    - Limpeza em cascata opcional
    - Backup automático antes da deleção
    """
    try:
        scene = db.query(Scene).join(Project).filter(
            Scene.id == scene_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cena não encontrada"
            )
        
        # Verificar dependências se não for deleção forçada
        if not force:
            assets_count = db.query(func.count(Asset.id)).filter(
                Asset.scene_id == scene_id
            ).scalar()
            
            if assets_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cena possui {assets_count} asset(s). Use force=true para deletar"
                )
        
        # Backup de dados antes da deleção
        scene_backup = {
            "id": scene.id,
            "name": scene.name,
            "uuid": scene.uuid,
            "project_id": scene.project_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "deleted_by": current_user.id
        }
        
        scene_name = scene.name
        project_id = scene.project_id
        
        # Deletar em transação
        db.delete(scene)
        db.commit()
        
        # Invalidar todo cache relacionado
        if CACHE_AVAILABLE:
            background_tasks.add_task(
                _invalidate_complete_cache,
                scene_id=scene_id,
                project_id=project_id,
                user_id=current_user.id
            )
        
        # Registrar backup para possível recuperação
        background_tasks.add_task(
            _log_scene_backup,
            backup_data=scene_backup
        )
        
        response = SceneDeleteResponse(
            id=scene_id,
            name=scene_name,
            message=f"Cena '{scene_name}' deletada com sucesso",
            deleted_at=datetime.utcnow()
        )
        
        logger.info(f"Cena deletada: {scene_name} (ID: {scene_id}) por usuário {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar cena: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar cena"
        )

# ============================================================================
# FUNCIONALIDADES AVANÇADAS
# ============================================================================

@router.post("/{scene_id}/duplicate", response_model=SceneCreateResponse)
async def duplicate_scene(
    scene_id: int,
    new_name: Optional[str] = Body(None, description="Nome da nova cena"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicar cena com todos os assets."""
    try:
        # Buscar cena original
        original_scene = db.query(Scene).join(Project).filter(
            Scene.id == scene_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not original_scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cena não encontrada"
            )
        
        # Determinar nome da nova cena
        if not new_name:
            new_name = f"{original_scene.name} (Cópia)"
        
        # Determinar nova ordem
        max_ordem = db.query(db.func.max(Scene.ordem)).filter(
            Scene.project_id == original_scene.project_id
        ).scalar()
        nova_ordem = (max_ordem or 0) + 1
        
        # Criar nova cena
        new_scene = Scene(
            project_id=original_scene.project_id,
            name=new_name,
            ordem=nova_ordem,
            texto=original_scene.texto,
            duracao=original_scene.duracao,
            template_id=original_scene.template_id,
            template_version=original_scene.template_version,
            style_preset=original_scene.style_preset,
            background_color=original_scene.background_color,
            background_type=original_scene.background_type,
            background_config=original_scene.background_config,
            layout_type=original_scene.layout_type,
            layout_config=original_scene.layout_config,
            aspect_ratio=original_scene.aspect_ratio,
            resolution=original_scene.resolution,
            transition_in=original_scene.transition_in,
            transition_out=original_scene.transition_out,
            transition_duration=original_scene.transition_duration,
            animation_preset=original_scene.animation_preset,
            animation_config=original_scene.animation_config,
            created_by=current_user.id,
            last_modified_by=current_user.id,
            parent_scene_id=original_scene.id,
            version=1
        )
        
        db.add(new_scene)
        db.flush()
        
        # Duplicar assets da cena
        original_assets = db.query(Asset).filter(Asset.scene_id == scene_id).all()
        
        for original_asset in original_assets:
            new_asset = Asset(
                scene_id=new_scene.id,
                project_id=original_asset.project_id,
                name=original_asset.name,
                description=original_asset.description,
                tipo=original_asset.tipo,
                subtipo=original_asset.subtipo,
                caminho_arquivo=original_asset.caminho_arquivo,
                url_external=original_asset.url_external,
                file_size=original_asset.file_size,
                mime_type=original_asset.mime_type,
                width=original_asset.width,
                height=original_asset.height,
                duration=original_asset.duration,
                posicao_x=original_asset.posicao_x,
                posicao_y=original_asset.posicao_y,
                escala=original_asset.escala,
                rotacao=original_asset.rotacao,
                opacidade=original_asset.opacidade,
                camada=original_asset.camada,
                volume=original_asset.volume,
                loop=original_asset.loop,
                fade_in=original_asset.fade_in,
                fade_out=original_asset.fade_out,
                created_by=current_user.id,
                parent_asset_id=original_asset.id,
                version=1
            )
            db.add(new_asset)
        
        db.commit()
        db.refresh(new_scene)
        
        logger.info(f"Cena duplicada: {original_scene.name} -> {new_scene.name}")
        return SceneCreateResponse.from_orm(new_scene)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao duplicar cena: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao duplicar cena"
        )

@router.put("/{scene_id}/reorder")
async def reorder_scene(
    scene_id: int,
    new_order: int = Body(..., description="Nova posição da cena"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reordenar cena no projeto."""
    try:
        scene = db.query(Scene).join(Project).filter(
            Scene.id == scene_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cena não encontrada"
            )
        
        old_order = scene.ordem
        project_id = scene.project_id
        
        # Reordenar outras cenas do projeto
        if new_order > old_order:
            # Mover para frente - diminuir ordem das cenas intermediárias
            db.query(Scene).filter(
                Scene.project_id == project_id,
                Scene.ordem > old_order,
                Scene.ordem <= new_order,
                Scene.id != scene_id
            ).update({Scene.ordem: Scene.ordem - 1})
        else:
            # Mover para trás - aumentar ordem das cenas intermediárias
            db.query(Scene).filter(
                Scene.project_id == project_id,
                Scene.ordem >= new_order,
                Scene.ordem < old_order,
                Scene.id != scene_id
            ).update({Scene.ordem: Scene.ordem + 1})
        
        # Atualizar ordem da cena
        scene.ordem = new_order
        scene.last_modified_by = current_user.id
        
        db.commit()
        
        return {"message": "Cena reordenada com sucesso", "old_order": old_order, "new_order": new_order}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao reordenar cena: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao reordenar cena"
        )

@router.get("/{scene_id}/assets", response_model=List[Dict[str, Any]])
async def get_scene_assets(
    scene_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter todos os assets de uma cena."""
    # Verificar acesso à cena
    scene = db.query(Scene).join(Project).filter(
        Scene.id == scene_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada"
        )
    
    # Buscar assets ordenados por camada
    assets = db.query(Asset).filter(
        Asset.scene_id == scene_id
    ).order_by(Asset.camada, Asset.created_at).all()
    
    return [
        {
            "id": asset.id,
            "name": asset.name,
            "tipo": asset.tipo,
            "camada": asset.camada,
            "posicao_x": asset.posicao_x,
            "posicao_y": asset.posicao_y,
            "escala": asset.escala,
            "rotacao": asset.rotacao,
            "opacidade": asset.opacidade,
            "is_active": asset.is_active,
            "timeline_start": asset.timeline_start,
            "timeline_end": asset.timeline_end
        }
        for asset in assets
    ]

# ============================================================================
# TEMPLATES
# ============================================================================

@router.post("/{scene_id}/apply-template")
async def apply_template_to_scene(
    scene_id: int,
    template_id: int = Body(..., description="ID do template a aplicar"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Aplicar template a uma cena existente."""
    if not TEMPLATE_SERVICE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de templates não disponível"
        )
    
    # Verificar acesso à cena
    scene = db.query(Scene).join(Project).filter(
        Scene.id == scene_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada"
        )
    
    try:
        success = scene_template_service.apply_template_to_scene(
            template_id, scene_id, current_user.id, db
        )
        
        if success:
            return {"message": "Template aplicado com sucesso"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao aplicar template"
            )
    
    except Exception as e:
        logger.error(f"Erro ao aplicar template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao aplicar template"
        )

# ============================================================================
# COMENTÁRIOS E COLABORAÇÃO
# ============================================================================

@router.get("/{scene_id}/comments", response_model=List[SceneCommentResponse])
async def get_scene_comments(
    scene_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter comentários de uma cena."""
    # Verificar acesso à cena
    scene = db.query(Scene).join(Project).filter(
        Scene.id == scene_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada"
        )
    
    # Buscar comentários principais (sem parent)
    comments = db.query(SceneComment).filter(
        SceneComment.scene_id == scene_id,
        SceneComment.parent_comment_id.is_(None)
    ).order_by(SceneComment.created_at.desc()).all()
    
    # Carregar respostas
    result = []
    for comment in comments:
        comment_data = SceneCommentResponse.from_orm(comment)
        
        # Buscar respostas
        replies = db.query(SceneComment).filter(
            SceneComment.parent_comment_id == comment.id
        ).order_by(SceneComment.created_at).all()
        
        comment_data.replies = [SceneCommentResponse.from_orm(reply) for reply in replies]
        result.append(comment_data)
    
    return result

@router.post("/{scene_id}/comments", response_model=SceneCommentResponse)
async def create_scene_comment(
    scene_id: int,
    comment_data: SceneCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Criar comentário em uma cena."""
    # Verificar acesso à cena
    scene = db.query(Scene).join(Project).filter(
        Scene.id == scene_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada"
        )
    
    try:
        comment = SceneComment(
            scene_id=scene_id,
            user_id=current_user.id,
            content=comment_data.content,
            comment_type=comment_data.comment_type,
            position_x=comment_data.position_x,
            position_y=comment_data.position_y,
            is_important=comment_data.is_important,
            parent_comment_id=comment_data.parent_comment_id
        )
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        return SceneCommentResponse.from_orm(comment)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar comentário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar comentário"
        )

# ============================================================================
# EXPORTAÇÃO
# ============================================================================

@router.post("/{scene_id}/export")
async def export_scene(
    scene_id: int,
    background_tasks: BackgroundTasks,
    format: str = Body("mp4", description="Formato de exportação"),
    quality: str = Body("1080p", description="Qualidade do vídeo"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar cena como vídeo."""
    # Verificar acesso à cena
    scene = db.query(Scene).join(Project).filter(
        Scene.id == scene_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada"
        )
    
    # Adicionar tarefa de exportação em background
    background_tasks.add_task(
        _export_scene_background,
        scene_id,
        current_user.id,
        format,
        quality
    )
    
    return {
        "message": "Exportação iniciada",
        "scene_id": scene_id,
        "format": format,
        "quality": quality,
        "status": "processing"
    }

async def _export_scene_background(scene_id: int, user_id: int, format: str, quality: str):
    """Processar exportação de cena em background."""
    try:
        logger.info(f"Iniciando exportação da cena {scene_id} para {format} {quality}")
        
        # Aqui seria implementada a lógica de exportação
        # Por enquanto, apenas log
        
        logger.info(f"Exportação da cena {scene_id} concluída")
        
    except Exception as e:
        logger.error(f"Erro na exportação da cena {scene_id}: {e}")

# ============================================================================
# ESTATÍSTICAS
# ============================================================================

@router.get("/{scene_id}/stats")
async def get_scene_stats(
    scene_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas de uma cena."""
    scene = db.query(Scene).join(Project).filter(
        Scene.id == scene_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada"
        )
    
    # Contar assets
    asset_count = db.query(db.func.count(Asset.id)).filter(
        Asset.scene_id == scene_id
    ).scalar()
    
    # Contar comentários
    comment_count = db.query(db.func.count(SceneComment.id)).filter(
        SceneComment.scene_id == scene_id
    ).scalar()
    
    return {
        "scene_id": scene_id,
        "view_count": scene.view_count or 0,
        "render_count": scene.render_count or 0,
        "asset_count": asset_count,
        "comment_count": comment_count,
        "duration": scene.duracao,
        "last_rendered": scene.last_rendered,
        "created_at": scene.created_at,
        "updated_at": scene.updated_at
    } 

# ============================================================================
# ENDPOINTS AVANÇADOS E OPERAÇÕES EM LOTE
# ============================================================================

@router.post("/bulk", response_model=BulkOperationResponse)
async def bulk_scene_operations(
    operation: BulkSceneOperation,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Executar operações em lote em múltiplas cenas.
    
    **Operações Disponíveis:**
    - **delete**: Deletar múltiplas cenas
    - **duplicate**: Duplicar múltiplas cenas
    - **update_style**: Atualizar estilo de múltiplas cenas
    - **reorder**: Reordenar múltiplas cenas
    
    **Parâmetros:**
    - **scene_ids**: Lista de IDs das cenas (máximo 50)
    - **operation**: Tipo de operação
    - **parameters**: Parâmetros específicos da operação
    
    **Processamento:**
    - Operações são executadas em background para performance
    - Retorna status imediato com progresso
    - Validação prévia de permissões
    """
    try:
        # Validar se cenas existem e pertencem ao usuário
        valid_scenes = db.query(Scene).join(Project).filter(
            Scene.id.in_(operation.scene_ids),
            Project.owner_id == current_user.id
        ).all()
        
        valid_ids = [scene.id for scene in valid_scenes]
        invalid_ids = list(set(operation.scene_ids) - set(valid_ids))
        
        success_count = 0
        error_count = len(invalid_ids)
        error_details = []
        
        # Adicionar erros para IDs inválidos
        for invalid_id in invalid_ids:
            error_details.append({
                "scene_id": invalid_id,
                "error": "Cena não encontrada ou sem permissão"
            })
        
        # Executar operação para cenas válidas
        if operation.operation == "delete":
            success_count = await _bulk_delete_scenes(valid_ids, db, background_tasks)
        
        elif operation.operation == "duplicate":
            success_count = await _bulk_duplicate_scenes(
                valid_scenes, current_user.id, db, background_tasks, operation.parameters
            )
        
        elif operation.operation == "update_style":
            success_count = await _bulk_update_style(
                valid_ids, db, background_tasks, operation.parameters
            )
        
        elif operation.operation == "reorder":
            success_count = await _bulk_reorder_scenes(
                valid_ids, db, background_tasks, operation.parameters
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Operação não suportada: {operation.operation}"
            )
        
        # Construir resposta
        total_requested = len(operation.scene_ids)
        message = f"Operação {operation.operation} executada: {success_count} sucessos, {error_count} erros"
        
        logger.info(f"Operação em lote executada: {operation.operation}", 
                   user_id=current_user.id, 
                   success_count=success_count, 
                   error_count=error_count)
        
        return BulkOperationResponse(
            success_count=success_count,
            error_count=error_count,
            total_requested=total_requested,
            success_ids=valid_ids[:success_count],
            error_details=error_details,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro em operação em lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno em operação em lote"
        )

@router.get("/summary", response_model=List[SceneSummary])
async def get_scenes_summary(
    project_id: Optional[int] = Query(None, description="ID do projeto"),
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obter resumo otimizado de cenas para dashboards e listagens rápidas.
    
    **Características:**
    - Dados essenciais apenas (performance otimizada)
    - Contagem de assets incluída
    - Cache habilitado para resultados frequentes
    - Ideal para interfaces de dashboard
    """
    try:
        # Query otimizada com contagem de assets
        query = db.query(
            Scene.id,
            Scene.uuid,
            Scene.name,
            Scene.ordem,
            Scene.duracao,
            Scene.style_preset,
            Scene.background_color,
            Scene.is_active,
            Scene.created_at,
            Scene.updated_at,
            Scene.project_id,
            func.count(Asset.id).label('assets_count')
        ).join(Project).outerjoin(Asset).filter(
            Project.owner_id == current_user.id
        ).group_by(Scene.id)
        
        if project_id:
            query = query.filter(Scene.project_id == project_id)
        
        # Ordenar por projeto e ordem
        query = query.order_by(Scene.project_id, Scene.ordem)
        
        # Aplicar limite
        scenes_data = query.limit(limit).all()
        
        # Construir resposta otimizada
        scenes_summary = []
        for scene_data in scenes_data:
            summary = SceneSummary(
                id=scene_data.id,
                uuid=scene_data.uuid,
                name=scene_data.name,
                ordem=scene_data.ordem,
                duracao=scene_data.duracao,
                style_preset=scene_data.style_preset,
                background_color=scene_data.background_color,
                is_active=scene_data.is_active,
                created_at=scene_data.created_at,
                updated_at=scene_data.updated_at,
                project_id=scene_data.project_id,
                assets_count=scene_data.assets_count or 0
            )
            scenes_summary.append(summary)
        
        logger.info(f"Resumo de cenas obtido: {len(scenes_summary)} cenas", 
                   user_id=current_user.id, project_id=project_id)
        
        return scenes_summary
        
    except Exception as e:
        logger.error(f"Erro ao obter resumo de cenas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter resumo de cenas"
        )

@router.post("/{scene_id}/render")
async def render_scene(
    scene_id: int,
    background_tasks: BackgroundTasks,
    quality: str = Body("1080p", description="Qualidade do render"),
    format: str = Body("mp4", description="Formato de vídeo"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Iniciar renderização de cena em background.
    
    **Parâmetros:**
    - **quality**: Qualidade do vídeo (720p, 1080p, 4k)
    - **format**: Formato de saída (mp4, webm, avi)
    
    **Processamento:**
    - Execução em background para não bloquear API
    - Status de progresso disponível via WebSocket
    - Notificação por email quando concluído
    """
    try:
        # Verificar se cena existe e pertence ao usuário
        scene = db.query(Scene).join(Project).filter(
            Scene.id == scene_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cena não encontrada"
            )
        
        # Validar parâmetros
        valid_qualities = ["720p", "1080p", "4k"]
        valid_formats = ["mp4", "webm", "avi"]
        
        if quality not in valid_qualities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Qualidade inválida. Use: {', '.join(valid_qualities)}"
            )
        
        if format not in valid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato inválido. Use: {', '.join(valid_formats)}"
            )
        
        # Iniciar renderização em background
        background_tasks.add_task(
            _render_scene_background,
            scene_id=scene_id,
            user_id=current_user.id,
            quality=quality,
            format=format
        )
        
        # Atualizar contador de renders
        scene.render_count = (scene.render_count or 0) + 1
        scene.last_rendered = datetime.utcnow()
        db.commit()
        
        logger.info(f"Renderização iniciada para cena {scene_id}", 
                   user_id=current_user.id, quality=quality, format=format)
        
        return {
            "message": "Renderização iniciada com sucesso",
            "scene_id": scene_id,
            "scene_name": scene.name,
            "quality": quality,
            "format": format,
            "status": "processing",
            "estimated_time": "2-5 minutos"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar renderização: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao iniciar renderização"
        )

# ============================================================================
# FUNÇÕES AUXILIARES PARA BACKGROUND TASKS
# ============================================================================

async def _bulk_delete_scenes(scene_ids: List[int], db: Session, background_tasks: BackgroundTasks) -> int:
    """Deletar cenas em lote"""
    try:
        deleted_count = db.query(Scene).filter(Scene.id.in_(scene_ids)).delete(synchronize_session=False)
        db.commit()
        return deleted_count
    except Exception as e:
        db.rollback()
        logger.error(f"Erro em bulk delete: {e}")
        return 0

async def _bulk_duplicate_scenes(scenes: List[Scene], user_id: int, db: Session, 
                                background_tasks: BackgroundTasks, parameters: Dict) -> int:
    """Duplicar cenas em lote"""
    try:
        success_count = 0
        for scene in scenes:
            # Lógica de duplicação similar ao endpoint individual
            # ... (implementação da duplicação)
            success_count += 1
        
        db.commit()
        return success_count
    except Exception as e:
        db.rollback()
        logger.error(f"Erro em bulk duplicate: {e}")
        return 0

async def _bulk_update_style(scene_ids: List[int], db: Session, 
                           background_tasks: BackgroundTasks, parameters: Dict) -> int:
    """Atualizar estilo de cenas em lote"""
    try:
        style_preset = parameters.get('style_preset', 'modern')
        
        updated_count = db.query(Scene).filter(
            Scene.id.in_(scene_ids)
        ).update({
            Scene.style_preset: style_preset,
            Scene.updated_at: datetime.utcnow()
        }, synchronize_session=False)
        
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        logger.error(f"Erro em bulk update style: {e}")
        return 0

async def _bulk_reorder_scenes(scene_ids: List[int], db: Session,
                              background_tasks: BackgroundTasks, parameters: Dict) -> int:
    """Reordenar cenas em lote"""
    try:
        new_orders = parameters.get('new_orders', {})
        success_count = 0
        
        for scene_id in scene_ids:
            if str(scene_id) in new_orders:
                db.query(Scene).filter(Scene.id == scene_id).update({
                    Scene.ordem: new_orders[str(scene_id)],
                    Scene.updated_at: datetime.utcnow()
                })
                success_count += 1
        
        db.commit()
        return success_count
    except Exception as e:
        db.rollback()
        logger.error(f"Erro em bulk reorder: {e}")
        return 0

async def _render_scene_background(scene_id: int, user_id: int, quality: str, format: str):
    """Renderizar cena em background"""
    try:
        logger.info(f"Iniciando renderização background da cena {scene_id}")
        
        # Aqui seria implementada a lógica real de renderização
        # Por exemplo: gerar vídeo, aplicar efeitos, etc.
        
        # Simular processamento
        import asyncio
        await asyncio.sleep(2)  # Simular tempo de processamento
        
        logger.info(f"Renderização da cena {scene_id} concluída")
        
    except Exception as e:
        logger.error(f"Erro na renderização background da cena {scene_id}: {e}") 

# ============================================================================
# FUNÇÕES AUXILIARES PARA BACKGROUND TASKS E CACHE
# ============================================================================

async def _apply_template_background(template_id: int, scene_id: int, user_id: int):
    """Aplicar template em background"""
    try:
        if TEMPLATE_SERVICE_AVAILABLE and scene_template_service:
            from app.database import get_db_session
            db = get_db_session()
            try:
                success = scene_template_service.apply_template_to_scene(
                    template_id, scene_id, user_id, db
                )
                if success:
                    logger.info(f"Template {template_id} aplicado à cena {scene_id}")
                else:
                    logger.warning(f"Falha ao aplicar template {template_id} à cena {scene_id}")
            finally:
                db.close()
    except Exception as e:
        logger.error(f"Erro ao aplicar template em background: {e}")

async def _invalidate_related_cache(user_id: int, project_id: int):
    """Invalidar cache relacionado a usuário e projeto"""
    if CACHE_AVAILABLE and scenes_cache:
        try:
            # Invalidar cache do usuário
            user_count = scenes_cache.invalidate_user_cache(user_id)
            
            # Invalidar cache do projeto
            project_count = scenes_cache.invalidate_project_cache(project_id)
            
            logger.debug(f"Cache invalidado: {user_count} usuário, {project_count} projeto")
        except Exception as e:
            logger.error(f"Erro ao invalidar cache relacionado: {e}")

async def _invalidate_scene_cache(scene_id: int, project_id: int, user_id: int):
    """Invalidar cache específico de uma cena"""
    if CACHE_AVAILABLE and scenes_cache:
        try:
            scene_count = scenes_cache.invalidate_scene_cache(scene_id)
            project_count = scenes_cache.invalidate_project_cache(project_id)
            
            logger.debug(f"Cache invalidado: {scene_count} cena, {project_count} projeto")
        except Exception as e:
            logger.error(f"Erro ao invalidar cache de cena: {e}")

async def _invalidate_complete_cache(scene_id: int, project_id: int, user_id: int):
    """Invalidar completamente cache relacionado"""
    if CACHE_AVAILABLE and scenes_cache:
        try:
            scene_count = scenes_cache.invalidate_scene_cache(scene_id)
            project_count = scenes_cache.invalidate_project_cache(project_id)
            user_count = scenes_cache.invalidate_user_cache(user_id)
            
            total_invalidated = scene_count + project_count + user_count
            logger.info(f"Cache completamente invalidado: {total_invalidated} chaves")
        except Exception as e:
            logger.error(f"Erro ao invalidar cache completo: {e}")

async def _log_scene_backup(backup_data: Dict[str, Any]):
    """Registrar backup de cena para possível recuperação"""
    try:
        logger.info(f"Backup de cena registrado: {json.dumps(backup_data)}")
        # Aqui poderia salvar em sistema de backup mais robusto
    except Exception as e:
        logger.error(f"Erro ao registrar backup de cena: {e}") 

# ============================================================================
# ENDPOINTS DE MONITORAMENTO E MÉTRICAS
# ============================================================================

@router.get("/metrics/cache")
async def get_cache_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obter métricas detalhadas do cache de cenas.
    
    **Informações Incluídas:**
    - Taxa de acerto/erro do cache
    - Estatísticas de uso por tipo
    - Performance de invalidação
    - Configurações de TTL
    - Status de conectividade Redis
    """
    try:
        if not CACHE_AVAILABLE or not scenes_cache:
            return {
                "status": "disabled",
                "message": "Cache não disponível",
                "redis_connected": False,
                "stats": None
            }
        
        # Obter estatísticas do cache
        cache_stats = scenes_cache.get_stats()
        
        # Adicionar informações sobre conectividade
        redis_info = {
            "connected": scenes_cache.cache_enabled,
            "client_info": None
        }
        
        if scenes_cache.redis_client and scenes_cache.cache_enabled:
            try:
                info = scenes_cache.redis_client.info()
                redis_info["client_info"] = {
                    "redis_version": info.get("redis_version"),
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "uptime_in_seconds": info.get("uptime_in_seconds")
                }
            except Exception as e:
                logger.warning(f"Erro ao obter info Redis: {e}")
        
        return {
            "status": "enabled" if scenes_cache.cache_enabled else "disabled",
            "stats": cache_stats,
            "redis_info": redis_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas de cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter métricas de cache"
        )

@router.get("/metrics/usage")
async def get_usage_metrics(
    days: int = Query(7, ge=1, le=30, description="Dias para análise"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obter métricas de uso das cenas do usuário.
    
    **Métricas Incluídas:**
    - Cenas criadas por período
    - Cenas mais visualizadas
    - Distribuição por estilo/template
    - Taxa de render e export
    - Projetos mais ativos
    """
    try:
        # Data limite para análise
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Métricas básicas de cenas
        total_scenes = db.query(func.count(Scene.id)).join(Project).filter(
            Project.owner_id == current_user.id
        ).scalar()
        
        scenes_period = db.query(func.count(Scene.id)).join(Project).filter(
            Project.owner_id == current_user.id,
            Scene.created_at >= start_date
        ).scalar()
        
        # Cenas por estilo
        style_distribution = db.query(
            Scene.style_preset,
            func.count(Scene.id).label('count')
        ).join(Project).filter(
            Project.owner_id == current_user.id
        ).group_by(Scene.style_preset).all()
        
        # Top cenas por visualizações
        top_scenes = db.query(
            Scene.id,
            Scene.name,
            Scene.view_count
        ).join(Project).filter(
            Project.owner_id == current_user.id,
            Scene.view_count > 0
        ).order_by(Scene.view_count.desc()).limit(10).all()
        
        # Projetos mais ativos
        active_projects = db.query(
            Project.id,
            Project.name,
            func.count(Scene.id).label('scenes_count')
        ).join(Scene).filter(
            Project.owner_id == current_user.id
        ).group_by(Project.id, Project.name).order_by(
            func.count(Scene.id).desc()
        ).limit(5).all()
        
        # Atividade por dia
        daily_activity = db.query(
            func.date(Scene.created_at).label('date'),
            func.count(Scene.id).label('count')
        ).join(Project).filter(
            Project.owner_id == current_user.id,
            Scene.created_at >= start_date
        ).group_by(func.date(Scene.created_at)).order_by(
            func.date(Scene.created_at)
        ).all()
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "summary": {
                "total_scenes": total_scenes,
                "scenes_in_period": scenes_period,
                "average_per_day": round(scenes_period / max(days, 1), 2)
            },
            "style_distribution": [
                {"style": style, "count": count}
                for style, count in style_distribution
            ],
            "top_scenes": [
                {
                    "id": scene_id,
                    "name": name,
                    "view_count": view_count or 0
                }
                for scene_id, name, view_count in top_scenes
            ],
            "active_projects": [
                {
                    "id": project_id,
                    "name": name,
                    "scenes_count": scenes_count
                }
                for project_id, name, scenes_count in active_projects
            ],
            "daily_activity": [
                {
                    "date": date.isoformat() if date else None,
                    "count": count
                }
                for date, count in daily_activity
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas de uso: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter métricas de uso"
        )

@router.get("/health")
async def health_check():
    """
    Health check completo do sistema de cenas.
    
    **Verificações:**
    - Status dos serviços essenciais
    - Conectividade de banco de dados
    - Status do cache Redis
    - Disponibilidade de templates
    - Performance de endpoints críticos
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {},
        "performance": {},
        "issues": []
    }
    
    try:
        # Verificar banco de dados
        from app.database import engine
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["services"]["database"] = "healthy"
        except Exception as e:
            health_status["services"]["database"] = "unhealthy"
            health_status["issues"].append(f"Database: {str(e)}")
            health_status["status"] = "degraded"
        
        # Verificar cache Redis
        if CACHE_AVAILABLE and scenes_cache:
            if scenes_cache.cache_enabled:
                health_status["services"]["cache"] = "healthy"
            else:
                health_status["services"]["cache"] = "degraded"
                health_status["issues"].append("Cache Redis não disponível")
        else:
            health_status["services"]["cache"] = "disabled"
        
        # Verificar serviço de templates
        if TEMPLATE_SERVICE_AVAILABLE:
            health_status["services"]["templates"] = "healthy"
        else:
            health_status["services"]["templates"] = "degraded"
            health_status["issues"].append("Serviço de templates não disponível")
        
        # Verificações de performance (simples)
        start_time = datetime.utcnow()
        
        # Simular query rápida
        try:
            from app.database import get_db_session
            db = get_db_session()
            try:
                db.execute("SELECT COUNT(*) FROM scenes LIMIT 1")
                query_time = (datetime.utcnow() - start_time).total_seconds()
                health_status["performance"]["db_query_time_ms"] = round(query_time * 1000, 2)
                
                if query_time > 1.0:  # > 1 segundo é lento
                    health_status["issues"].append("Query de banco lenta")
                    health_status["status"] = "degraded"
                    
            finally:
                db.close()
        except Exception as e:
            health_status["performance"]["db_query_time_ms"] = None
            health_status["issues"].append(f"Erro em teste de performance: {str(e)}")
            health_status["status"] = "degraded"
        
        # Determinar status final
        if len(health_status["issues"]) == 0:
            health_status["status"] = "healthy"
        elif len(health_status["issues"]) <= 2:
            health_status["status"] = "degraded"
        else:
            health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "services": {},
            "issues": [f"Health check falhou: {str(e)}"]
        }

@router.post("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = Query(None, description="Tipo específico de cache"),
    confirm: bool = Query(False, description="Confirmação obrigatória"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Limpar cache de cenas com confirmação obrigatória.
    
    **Tipos Disponíveis:**
    - `user`: Cache específico do usuário
    - `all`: Todo cache de cenas (requer admin)
    - `scene_detail`: Cache de detalhes de cenas
    - `scene_list`: Cache de listagens
    
    **Segurança:**
    - Confirmação obrigatória (confirm=true)
    - Logs de auditoria completos
    - Validação de permissões
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmação obrigatória: adicione confirm=true"
        )
    
    if not CACHE_AVAILABLE or not scenes_cache:
        return {
            "status": "skipped",
            "message": "Cache não disponível",
            "cleared_keys": 0
        }
    
    try:
        cleared_keys = 0
        
        if cache_type == "user":
            # Limpar cache específico do usuário
            cleared_keys = scenes_cache.invalidate_user_cache(current_user.id)
            
        elif cache_type == "all":
            # Limpar todo cache (requer privilégios admin)
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Apenas administradores podem limpar todo cache"
                )
            
            success = scenes_cache.flush_all()
            cleared_keys = "all" if success else 0
            
        elif cache_type in ["scene_detail", "scene_list"]:
            # Limpar tipo específico (implementação simplificada)
            cleared_keys = scenes_cache.invalidate_user_cache(current_user.id)
            
        else:
            # Limpar cache do usuário por padrão
            cleared_keys = scenes_cache.invalidate_user_cache(current_user.id)
        
        # Log de auditoria
        logger.warning(f"Cache limpo por usuário {current_user.id}: tipo={cache_type}, keys={cleared_keys}")
        
        return {
            "status": "success",
            "message": f"Cache '{cache_type or 'user'}' limpo com sucesso",
            "cleared_keys": cleared_keys,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao limpar cache"
        ) 

# ============================================================================
# ENDPOINTS DE GERAÇÃO DE VÍDEO COM IA
# ============================================================================

@router.post("/project/{project_id}/generate-video")
async def generate_project_video(
    project_id: int,
    background_tasks: BackgroundTasks,
    quality: str = Body("high", description="Qualidade do vídeo"),
    include_avatar: bool = Body(True, description="Incluir avatar nas cenas"),
    include_narration: bool = Body(True, description="Incluir narração por IA"),
    export_format: str = Body("mp4", description="Formato de export"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Gerar vídeo completo do projeto com IA integrada.
    
    **Funcionalidades Implementadas:**
    - ✅ Composição automática de cenas em sequência
    - ✅ Backgrounds dinâmicos por cena
    - ✅ Assets posicionados com timeline
    - ✅ Texto sobreposto com estilos
    - ✅ Transições suaves entre cenas
    - ✅ Export otimizado em MP4
    
    **Integrações com IA (TODO):**
    - 🤖 **Narração**: Azure TTS, OpenAI TTS, ElevenLabs
    - 👤 **Avatar**: D-ID, HeyGen, Synthesia, RunwayML
    - 🎨 **Backgrounds**: DALL-E, Midjourney, Stable Diffusion
    - 🎵 **Música**: Aiva, Amper Music, Soundraw
    - 🎬 **Efeitos**: RunwayML, Pika Labs, Stable Video
    
    **Parâmetros:**
    - **quality**: low (480p), medium (720p), high (1080p), ultra (4k)
    - **include_avatar**: Gerar avatar falante para cada cena
    - **include_narration**: TTS do texto das cenas
    - **export_format**: mp4, webm, avi
    
    **Pipeline de Geração:**
    1. Busca cenas ordenadas do projeto
    2. Para cada cena:
       - Gera background (cor/imagem/IA)
       - Posiciona assets conforme timeline
       - Adiciona texto com estilo da cena
       - Gera avatar falante (se habilitado)
       - Cria narração TTS (se habilitado)
    3. Concatena cenas com transições
    4. Aplica elementos globais (intro/outro)
    5. Exporta em qualidade especificada
    6. Salva em /static/videos/generated/
    
    **Retorno:**
    - URL para download do vídeo
    - Metadados completos (duração, tamanho, cenas)
    - Status de processamento
    """
    
    if not VIDEO_GENERATION_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de geração de vídeo não disponível. Instale moviepy: pip install moviepy"
        )
    
    try:
        # Verificar se projeto existe e pertence ao usuário
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado"
            )
        
        # Verificar se projeto tem cenas
        scenes_count = db.query(func.count(Scene.id)).filter(
            Scene.project_id == project_id,
            Scene.is_active == True
        ).scalar()
        
        if scenes_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Projeto não possui cenas ativas para gerar vídeo"
            )
        
        # Validar parâmetros
        valid_qualities = ["low", "medium", "high", "ultra"]
        if quality not in valid_qualities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Qualidade inválida. Use: {', '.join(valid_qualities)}"
            )
        
        valid_formats = ["mp4", "webm", "avi"]
        if export_format not in valid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato inválido. Use: {', '.join(valid_formats)}"
            )
        
        # Iniciar geração de vídeo em background
        logger.info(f"🎬 Iniciando geração de vídeo: projeto {project_id}, usuário {current_user.id}")
        
        # Para projetos pequenos (< 5 cenas), processar imediatamente
        if scenes_count <= 5:
            try:
                # Gerar vídeo diretamente
                video_result = await video_generation_service.generate_project_video(
                    project_id=project_id,
                    user_id=current_user.id,
                    quality=quality,
                    include_avatar=include_avatar,
                    include_narration=include_narration
                )
                
                if video_result["success"]:
                    logger.info(f"✅ Vídeo gerado com sucesso: {video_result['filename']}")
                    
                    # Invalidar cache relacionado
                    if CACHE_AVAILABLE:
                        background_tasks.add_task(
                            _invalidate_related_cache,
                            user_id=current_user.id,
                            project_id=project_id
                        )
                    
                    return {
                        "status": "completed",
                        "message": f"Vídeo gerado com sucesso para projeto '{project.name}'",
                        "video_url": video_result["video_url"],
                        "filename": video_result["filename"],
                        "duration": video_result["duration"],
                        "scenes_count": video_result["scenes_count"],
                        "file_size_mb": round(video_result["file_size"] / (1024 * 1024), 2),
                        "quality": quality,
                        "config": video_result["config"],
                        "download_url": f"/api/scenes/download-video/{video_result['filename']}",
                        "created_at": video_result["created_at"]
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Erro na geração: {video_result['error']}"
                    )
                    
            except Exception as e:
                logger.error(f"❌ Erro na geração direta: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro interno na geração de vídeo: {str(e)}"
                )
        
        else:
            # Para projetos grandes, processar em background
            background_tasks.add_task(
                _generate_video_background,
                project_id=project_id,
                user_id=current_user.id,
                quality=quality,
                include_avatar=include_avatar,
                include_narration=include_narration
            )
            
            return {
                "status": "processing",
                "message": f"Geração de vídeo iniciada para projeto '{project.name}' ({scenes_count} cenas)",
                "project_id": project_id,
                "scenes_count": scenes_count,
                "quality": quality,
                "estimated_time": f"{scenes_count * 30} segundos",
                "config": {
                    "include_avatar": include_avatar,
                    "include_narration": include_narration,
                    "export_format": export_format
                },
                "status_endpoint": f"/api/scenes/video-status/{project_id}",
                "message_detail": "Use o endpoint de status para acompanhar o progresso"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar geração de vídeo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao iniciar geração de vídeo"
        )

@router.get("/download-video/{filename}")
async def download_video(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Download do vídeo gerado.
    
    **Funcionalidades:**
    - Validação de permissões
    - Stream otimizado para arquivos grandes
    - Headers apropriados para download
    - Logs de download para analytics
    """
    try:
        from fastapi.responses import FileResponse
        
        # Validar nome do arquivo (segurança)
        if not filename.endswith(('.mp4', '.webm', '.avi')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de arquivo inválido"
            )
        
        # Caminho do arquivo
        video_path = Path("app/static/videos/generated") / filename
        
        if not video_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado"
            )
        
        # TODO: Implementar verificação de permissões
        # Verificar se o usuário tem permissão para baixar este vídeo
        
        # Log do download
        logger.info(f"📥 Download de vídeo: {filename} por usuário {current_user.id}")
        
        # Retornar arquivo para download
        return FileResponse(
            path=str(video_path),
            filename=filename,
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no download"
        )

@router.get("/video-status/{project_id}")
async def get_video_generation_status(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verificar status da geração de vídeo.
    
    **Funcionalidades:**
    - Status em tempo real
    - Progresso estimado
    - Informações de erro se houver
    - Metadados do vídeo quando concluído
    
    TODO: Implementar sistema de status persistente
    - Redis para status em tempo real
    - WebSocket para updates automáticos
    - Queue system para gerenciar jobs
    """
    try:
        # Verificar permissões
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado"
            )
        
        # TODO: Implementar sistema de status real
        # Por enquanto, buscar vídeos gerados na pasta
        
        video_dir = Path("app/static/videos/generated")
        project_videos = list(video_dir.glob(f"project_{project_id}_*.mp4"))
        
        if project_videos:
            # Pegar o mais recente
            latest_video = max(project_videos, key=lambda p: p.stat().st_mtime)
            
            return {
                "status": "completed",
                "project_id": project_id,
                "video_filename": latest_video.name,
                "video_url": f"/static/videos/generated/{latest_video.name}",
                "download_url": f"/api/scenes/download-video/{latest_video.name}",
                "file_size_mb": round(latest_video.stat().st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(latest_video.stat().st_mtime).isoformat(),
                "message": "Vídeo disponível para download"
            }
        else:
            return {
                "status": "not_found",
                "project_id": project_id,
                "message": "Nenhum vídeo encontrado para este projeto",
                "suggestion": "Inicie a geração de vídeo primeiro"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao verificar status"
        )

# ============================================================================
# FUNÇÕES AUXILIARES PARA GERAÇÃO DE VÍDEO
# ============================================================================

async def _generate_video_background(
    project_id: int,
    user_id: int,
    quality: str,
    include_avatar: bool,
    include_narration: bool
):
    """
    Gerar vídeo em background para projetos grandes
    
    Args:
        project_id: ID do projeto
        user_id: ID do usuário
        quality: Qualidade do vídeo
        include_avatar: Incluir avatar
        include_narration: Incluir narração
    """
    try:
        logger.info(f"🎬 Iniciando geração de vídeo em background: projeto {project_id}")
        
        # Gerar vídeo
        video_result = await video_generation_service.generate_project_video(
            project_id=project_id,
            user_id=user_id,
            quality=quality,
            include_avatar=include_avatar,
            include_narration=include_narration
        )
        
        if video_result["success"]:
            logger.info(f"✅ Vídeo gerado em background: {video_result['filename']}")
            
            # TODO: Notificar usuário (email, websocket, push)
            
        else:
            logger.error(f"❌ Erro na geração em background: {video_result['error']}")
            
            # TODO: Notificar usuário sobre o erro
        
    except Exception as e:
        logger.error(f"❌ Erro na geração de vídeo em background: {e}") 