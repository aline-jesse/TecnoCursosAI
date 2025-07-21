"""
Router para gerenciamento de templates de cenas - TecnoCursos AI

Este módulo implementa endpoints para:
- Listar templates disponíveis
- Obter detalhes de templates
- Criar cenas a partir de templates
- Salvar cenas como templates
- Gerenciar templates personalizados

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Scene
from ..services.scene_template_service import SceneTemplateService
from ..logger import get_logger

logger = get_logger("scene_templates_router")

router = APIRouter(
    prefix="/templates",
    tags=["Templates de Cenas"],
    responses={404: {"description": "Não encontrado"}}
)

# ============================================================================
# ENDPOINTS PARA GERENCIAMENTO DE TEMPLATES
# ============================================================================

@router.get("/", response_model=List[Dict[str, Any]])
async def list_templates(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    search: Optional[str] = Query(None, description="Termo de busca"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar templates de cenas disponíveis
    """
    try:
        templates = await SceneTemplateService.get_templates(
            category=category,
            search=search
        )
        
        logger.info(f"🔍 Listagem de templates por {current_user.username}: {len(templates)} resultados")
        return templates
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao listar templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar templates: {str(e)}"
        )

@router.get("/categories", response_model=List[Dict[str, str]])
async def get_template_categories():
    """
    Retorna as categorias de templates disponíveis
    """
    try:
        return await SceneTemplateService.get_template_categories()
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter categorias de templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter categorias: {str(e)}"
        )

@router.get("/{template_id}", response_model=Dict[str, Any])
async def get_template_details(
    template_id: str = Path(..., description="ID do template"),
    current_user: User = Depends(get_current_user)
):
    """
    Obter detalhes de um template específico
    """
    try:
        template = await SceneTemplateService.get_template_details(template_id)
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter detalhes do template {template_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter detalhes do template: {str(e)}"
        )

@router.post("/create-scene", response_model=Dict[str, Any])
async def create_scene_from_template(
    template_id: str = Body(..., embed=True),
    project_id: int = Body(..., embed=True),
    name: Optional[str] = Body(None, embed=True),
    ordem: Optional[int] = Body(None, embed=True),
    customizations: Optional[Dict[str, Any]] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar uma nova cena a partir de um template
    """
    try:
        result = await SceneTemplateService.create_scene_from_template(
            template_id=template_id,
            project_id=project_id,
            name=name,
            ordem=ordem,
            customizations=customizations,
            db=db
        )
        
        logger.info(f"✅ Cena criada a partir do template {template_id} por {current_user.username}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao criar cena a partir do template {template_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cena: {str(e)}"
        )

@router.post("/save", response_model=Dict[str, Any])
async def save_scene_as_template(
    scene_id: int = Body(..., embed=True),
    name: str = Body(..., embed=True),
    category: str = Body(..., embed=True),
    description: str = Body(..., embed=True),
    tags: List[str] = Body([], embed=True),
    is_public: bool = Body(False, embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Salvar uma cena existente como template
    """
    try:
        # Verificar se o usuário tem acesso à cena
        scene = db.query(Scene).filter(Scene.id == scene_id).first()
        if not scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cena não encontrada"
            )
        
        # Verificar se o usuário é dono do projeto
        project = scene.project
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar esta cena"
            )
        
        result = await SceneTemplateService.save_as_template(
            scene_id=scene_id,
            name=name,
            category=category,
            description=description,
            tags=tags,
            is_public=is_public,
            db=db
        )
        
        logger.info(f"✅ Cena {scene_id} salva como template '{name}' por {current_user.username}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao salvar cena {scene_id} como template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar template: {str(e)}"
        )

@router.delete("/{template_id}", response_model=Dict[str, Any])
async def delete_template(
    template_id: str = Path(..., description="ID do template"),
    current_user: User = Depends(get_current_user)
):
    """
    Remover um template personalizado
    """
    try:
        # Apenas administradores podem remover templates
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem remover templates"
            )
        
        result = await SceneTemplateService.delete_template(template_id)
        
        logger.info(f"🗑️ Template {template_id} removido por {current_user.username}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao remover template {template_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover template: {str(e)}"
        )

@router.get("/{template_id}/preview")
async def get_template_preview(
    template_id: str = Path(..., description="ID do template")
):
    """
    Obter imagem de preview do template
    """
    try:
        # Esta implementação é simplificada - em produção, seria necessário
        # gerar ou recuperar uma imagem de preview real
        
        # Por ora, retorna um JSON com uma mensagem
        return {
            "message": "Preview do template não disponível",
            "template_id": template_id
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter preview do template {template_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter preview: {str(e)}"
        ) 