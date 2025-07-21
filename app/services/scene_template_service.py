#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Templates de Cenas - TecnoCursos AI

Este módulo implementa um sistema completo de gerenciamento de templates
de cenas para criação rápida e eficiente de apresentações visuais.

Funcionalidades:
- Biblioteca de templates predefinidos
- Templates customizados por usuário
- Sistema de categorização e busca
- Templates públicos e premium
- Sistema de avaliação e favoritos
- Aplicação automática de templates
- Versionamento de templates

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import uuid

try:
    from sqlalchemy.orm import Session
    from sqlalchemy import func, and_, or_
    from app.database import get_db_session
    from app.models import SceneTemplate, User, Scene, Asset
    from app.schemas import (
        SceneTemplateCreate, SceneTemplateUpdate, SceneTemplateResponse,
        SceneCreate, AssetCreate
    )
    DATABASE_AVAILABLE = True
except ImportError:
    # Fallback para quando as importações falham
    DATABASE_AVAILABLE = False
    Session = Any
    SceneTemplateCreate = Any
    SceneTemplateUpdate = Any  
    SceneTemplateResponse = Any
    SceneCreate = Any
    AssetCreate = Any

logger = logging.getLogger(__name__)

class TemplateCategory(Enum):
    """Categorias de templates"""
    PRESENTATION = "presentation"
    EDUCATION = "education"
    MARKETING = "marketing"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    SOCIAL_MEDIA = "social_media"
    TUTORIAL = "tutorial"
    REPORT = "report"

class TemplateStyle(Enum):
    """Estilos visuais dos templates"""
    MODERN = "modern"
    CORPORATE = "corporate"
    TECH = "tech"
    EDUCATION = "education"
    MINIMAL = "minimal"

@dataclass
class TemplateConfig:
    """Configuração de um template"""
    name: str
    description: str
    category: TemplateCategory
    style: TemplateStyle
    aspect_ratio: str = "16:9"
    resolution: str = "1920x1080"
    background_type: str = "solid"
    background_config: Dict[str, Any] = None
    layout_type: str = "free"
    layout_config: Dict[str, Any] = None
    default_assets: List[Dict[str, Any]] = None
    tags: List[str] = None

class SceneTemplateService:
    """
    Serviço de gerenciamento de templates de cenas.
    
    Responsável por:
    - CRUD de templates
    - Biblioteca pública de templates
    - Aplicação de templates a cenas
    - Sistema de busca e filtros
    - Avaliações e favoritos
    """
    
    def __init__(self):
        self.predefined_templates = self._load_predefined_templates()
        logger.info("✅ Scene Template Service inicializado")
    
    def _load_predefined_templates(self) -> Dict[str, TemplateConfig]:
        """Carrega templates predefinidos do sistema."""
        templates = {
            "modern_presentation": TemplateConfig(
                name="Apresentação Moderna",
                description="Template moderno com gradientes azuis e efeitos visuais",
                category=TemplateCategory.PRESENTATION,
                style=TemplateStyle.MODERN,
                background_type="gradient",
                background_config={
                    "gradient": {
                        "type": "linear",
                        "angle": 135,
                        "colors": ["#667eea", "#764ba2"]
                    }
                },
                layout_type="centered",
                layout_config={
                    "padding": 80,
                    "title_area": 0.3,
                    "content_area": 0.7
                },
                default_assets=[
                    {
                        "tipo": "text",
                        "name": "Título Principal",
                        "texto_conteudo": "Título da Apresentação",
                        "fonte_familia": "Arial",
                        "fonte_tamanho": 48,
                        "fonte_cor": "#ffffff",
                        "fonte_peso": "bold",
                        "posicao_x": 0.5,
                        "posicao_y": 0.3,
                        "camada": 10
                    }
                ],
                tags=["moderno", "apresentação", "profissional", "gradiente"]
            ),
            
            "corporate_clean": TemplateConfig(
                name="Corporativo Limpo",
                description="Template corporativo profissional com layout estruturado",
                category=TemplateCategory.CORPORATE,
                style=TemplateStyle.CORPORATE,
                background_type="solid",
                background_config={
                    "color": "#f8f9fa"
                },
                layout_type="grid",
                layout_config={
                    "columns": 2,
                    "rows": 3,
                    "padding": 60,
                    "spacing": 20
                },
                default_assets=[
                    {
                        "tipo": "text",
                        "name": "Título Corporativo",
                        "texto_conteudo": "Título da Seção",
                        "fonte_familia": "Roboto",
                        "fonte_tamanho": 36,
                        "fonte_cor": "#2c3e50",
                        "fonte_peso": "bold",
                        "posicao_x": 0.5,
                        "posicao_y": 0.15,
                        "camada": 10
                    },
                    {
                        "tipo": "background",
                        "name": "Linha Decorativa",
                        "background_type": "solid",
                        "background_config": {"color": "#3498db"},
                        "posicao_x": 0.1,
                        "posicao_y": 0.25,
                        "largura": 0.8,
                        "altura": 0.005,
                        "camada": 5
                    }
                ],
                tags=["corporativo", "profissional", "limpo", "estruturado"]
            ),
            
            "tech_futuristic": TemplateConfig(
                name="Tech Futurista",
                description="Template futurista com efeitos neon e grid cyberpunk",
                category=TemplateCategory.TECH,
                style=TemplateStyle.TECH,
                background_type="gradient",
                background_config={
                    "gradient": {
                        "type": "radial",
                        "colors": ["#0f0f23", "#1a1a2e", "#16213e"]
                    },
                    "overlay": {
                        "type": "grid",
                        "color": "#00ff88",
                        "opacity": 0.1
                    }
                },
                layout_type="free",
                default_assets=[
                    {
                        "tipo": "text",
                        "name": "Título Tech",
                        "texto_conteudo": "SISTEMA DIGITAL",
                        "fonte_familia": "Courier New",
                        "fonte_tamanho": 42,
                        "fonte_cor": "#00ff88",
                        "fonte_peso": "bold",
                        "posicao_x": 0.5,
                        "posicao_y": 0.3,
                        "camada": 10,
                        "animacao_tipo": "glow",
                        "animacao_config": {
                            "glow_color": "#00ff88",
                            "intensity": 0.8
                        }
                    }
                ],
                tags=["tech", "futurista", "neon", "cyberpunk", "digital"]
            ),
            
            "education_friendly": TemplateConfig(
                name="Educação Amigável",
                description="Template educacional com cores suaves e layout acessível",
                category=TemplateCategory.EDUCATION,
                style=TemplateStyle.EDUCATION,
                background_type="gradient",
                background_config={
                    "gradient": {
                        "type": "linear",
                        "angle": 45,
                        "colors": ["#ffeaa7", "#fab1a0"]
                    }
                },
                layout_type="columns",
                layout_config={
                    "columns": 1,
                    "padding": 100,
                    "content_spacing": 40
                },
                default_assets=[
                    {
                        "tipo": "text",
                        "name": "Título da Aula",
                        "texto_conteudo": "Título da Aula",
                        "fonte_familia": "Open Sans",
                        "fonte_tamanho": 40,
                        "fonte_cor": "#2d3436",
                        "fonte_peso": "bold",
                        "posicao_x": 0.5,
                        "posicao_y": 0.2,
                        "camada": 10
                    },
                    {
                        "tipo": "image",
                        "name": "Ícone Educacional",
                        "caminho_arquivo": "/assets/education/book-icon.svg",
                        "posicao_x": 0.1,
                        "posicao_y": 0.1,
                        "escala": 0.8,
                        "camada": 8
                    }
                ],
                tags=["educação", "amigável", "acessível", "colorido", "ensino"]
            ),
            
            "minimal_elegant": TemplateConfig(
                name="Minimalista Elegante",
                description="Template limpo e minimalista focado no conteúdo",
                category=TemplateCategory.MINIMAL,
                style=TemplateStyle.MINIMAL,
                background_type="solid",
                background_config={
                    "color": "#ffffff"
                },
                layout_type="centered",
                layout_config={
                    "padding": 120,
                    "max_width": 0.8
                },
                default_assets=[
                    {
                        "tipo": "text",
                        "name": "Título Minimalista",
                        "texto_conteudo": "Título",
                        "fonte_familia": "Georgia",
                        "fonte_tamanho": 44,
                        "fonte_cor": "#2c3e50",
                        "fonte_peso": "normal",
                        "posicao_x": 0.5,
                        "posicao_y": 0.4,
                        "camada": 10,
                        "texto_alinhamento": "center"
                    }
                ],
                tags=["minimal", "elegante", "limpo", "simples", "foco"]
            )
        }
        
        return templates
    
    def create_template(self, template_data: SceneTemplateCreate, created_by: int, db: Session = None) -> SceneTemplateResponse:
        """Criar novo template."""
        if not DATABASE_AVAILABLE:
            raise Exception("Database não disponível")
        
        if db is None:
            db = get_db_session()
        
        try:
            # Validar dados do template
            if isinstance(template_data.template_data, str):
                template_json = json.loads(template_data.template_data)
            else:
                template_json = template_data.template_data
            
            # Criar template no banco
            template = SceneTemplate(
                name=template_data.name,
                description=template_data.description,
                category=template_data.category,
                style=template_data.style,
                aspect_ratio=template_data.aspect_ratio,
                resolution=template_data.resolution,
                background_type=template_data.background_type,
                background_config=json.dumps(template_data.background_config) if template_data.background_config else None,
                layout_type=template_data.layout_type,
                layout_config=json.dumps(template_data.layout_config) if template_data.layout_config else None,
                template_data=json.dumps(template_json),
                default_assets=json.dumps(template_data.default_assets) if template_data.default_assets else None,
                is_public=template_data.is_public,
                is_premium=template_data.is_premium,
                is_featured=template_data.is_featured,
                tags=json.dumps(template_data.tags) if template_data.tags else None,
                created_by=created_by
            )
            
            db.add(template)
            db.commit()
            db.refresh(template)
            
            logger.info(f"Template criado: {template.name} por usuário {created_by}")
            return SceneTemplateResponse.from_orm(template)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar template: {e}")
            raise
        finally:
            db.close()
    
    def get_template(self, template_id: int, db: Session = None) -> Optional[SceneTemplateResponse]:
        """Obter template por ID."""
        if not DATABASE_AVAILABLE:
            return None
        
        if db is None:
            db = get_db_session()
        
        try:
            template = db.query(SceneTemplate).filter(SceneTemplate.id == template_id).first()
            if template:
                return SceneTemplateResponse.from_orm(template)
            return None
        finally:
            db.close()
    
    def list_templates(self, 
                      category: Optional[str] = None,
                      style: Optional[str] = None,
                      is_public: Optional[bool] = None,
                      is_featured: Optional[bool] = None,
                      search: Optional[str] = None,
                      user_id: Optional[int] = None,
                      skip: int = 0,
                      limit: int = 50,
                      db: Session = None) -> List[SceneTemplateResponse]:
        """Listar templates com filtros."""
        if not DATABASE_AVAILABLE:
            return []
        
        if db is None:
            db = get_db_session()
        
        try:
            query = db.query(SceneTemplate)
            
            # Filtros
            if category:
                query = query.filter(SceneTemplate.category == category)
            
            if style:
                query = query.filter(SceneTemplate.style == style)
            
            if is_public is not None:
                query = query.filter(SceneTemplate.is_public == is_public)
            
            if is_featured is not None:
                query = query.filter(SceneTemplate.is_featured == is_featured)
            
            if user_id is not None:
                # Mostrar templates públicos OU do usuário
                query = query.filter(
                    or_(
                        SceneTemplate.is_public == True,
                        SceneTemplate.created_by == user_id
                    )
                )
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        SceneTemplate.name.ilike(search_term),
                        SceneTemplate.description.ilike(search_term),
                        SceneTemplate.tags.ilike(search_term)
                    )
                )
            
            # Ordenação: featured primeiro, depois por rating, depois por uso
            query = query.order_by(
                SceneTemplate.is_featured.desc(),
                SceneTemplate.rating_avg.desc().nullslast(),
                SceneTemplate.usage_count.desc(),
                SceneTemplate.created_at.desc()
            )
            
            templates = query.offset(skip).limit(limit).all()
            return [SceneTemplateResponse.from_orm(t) for t in templates]
            
        finally:
            db.close()
    
    def update_template(self, template_id: int, template_data: SceneTemplateUpdate, user_id: int, db: Session = None) -> Optional[SceneTemplateResponse]:
        """Atualizar template."""
        if not DATABASE_AVAILABLE:
            return None
        
        if db is None:
            db = get_db_session()
        
        try:
            template = db.query(SceneTemplate).filter(
                and_(
                    SceneTemplate.id == template_id,
                    SceneTemplate.created_by == user_id
                )
            ).first()
            
            if not template:
                return None
            
            # Atualizar campos
            update_data = template_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field in ['background_config', 'layout_config', 'template_data', 'default_assets', 'tags'] and value is not None:
                    setattr(template, field, json.dumps(value))
                else:
                    setattr(template, field, value)
            
            db.commit()
            db.refresh(template)
            
            logger.info(f"Template atualizado: {template.name}")
            return SceneTemplateResponse.from_orm(template)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao atualizar template: {e}")
            raise
        finally:
            db.close()
    
    def delete_template(self, template_id: int, user_id: int, db: Session = None) -> bool:
        """Deletar template."""
        if not DATABASE_AVAILABLE:
            return False
        
        if db is None:
            db = get_db_session()
        
        try:
            template = db.query(SceneTemplate).filter(
                and_(
                    SceneTemplate.id == template_id,
                    SceneTemplate.created_by == user_id
                )
            ).first()
            
            if not template:
                return False
            
            db.delete(template)
            db.commit()
            
            logger.info(f"Template deletado: {template.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao deletar template: {e}")
            raise
        finally:
            db.close()
    
    def apply_template_to_scene(self, template_id: int, scene_id: int, user_id: int, db: Session = None) -> bool:
        """Aplicar template a uma cena existente."""
        if not DATABASE_AVAILABLE:
            return False
        
        if db is None:
            db = get_db_session()
        
        try:
            # Buscar template
            template = db.query(SceneTemplate).filter(SceneTemplate.id == template_id).first()
            if not template:
                return False
            
            # Buscar cena
            scene = db.query(Scene).filter(
                and_(
                    Scene.id == scene_id,
                    Scene.project.has(owner_id=user_id)
                )
            ).first()
            if not scene:
                return False
            
            # Aplicar configurações do template
            template_data = json.loads(template.template_data)
            
            # Atualizar cena
            scene.template_id = str(template.id)
            scene.style_preset = template.style
            scene.background_type = template.background_type
            scene.background_config = template.background_config
            scene.layout_type = template.layout_type
            scene.layout_config = template.layout_config
            scene.aspect_ratio = template.aspect_ratio
            scene.resolution = template.resolution
            
            # Aplicar assets padrão se especificados
            if template.default_assets:
                default_assets = json.loads(template.default_assets)
                
                for asset_data in default_assets:
                    asset = Asset(
                        scene_id=scene.id,
                        name=asset_data.get('name', 'Asset do Template'),
                        tipo=asset_data.get('tipo', 'text'),
                        **{k: v for k, v in asset_data.items() if k not in ['name', 'tipo']}
                    )
                    db.add(asset)
            
            # Incrementar contador de uso do template
            template.usage_count = (template.usage_count or 0) + 1
            
            db.commit()
            
            logger.info(f"Template {template.name} aplicado à cena {scene.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao aplicar template: {e}")
            return False
        finally:
            db.close()
    
    def create_scene_from_template(self, template_id: int, project_id: int, scene_name: str, user_id: int, db: Session = None) -> Optional[int]:
        """Criar nova cena a partir de um template."""
        if not DATABASE_AVAILABLE:
            return None
        
        if db is None:
            db = get_db_session()
        
        try:
            # Buscar template
            template = db.query(SceneTemplate).filter(SceneTemplate.id == template_id).first()
            if not template:
                return None
            
            # Criar nova cena baseada no template
            scene = Scene(
                project_id=project_id,
                name=scene_name,
                template_id=str(template.id),
                style_preset=template.style,
                background_type=template.background_type,
                background_config=template.background_config,
                layout_type=template.layout_type,
                layout_config=template.layout_config,
                aspect_ratio=template.aspect_ratio,
                resolution=template.resolution,
                created_by=user_id,
                ordem=0  # Será ajustado depois
            )
            
            db.add(scene)
            db.flush()  # Para obter o ID da cena
            
            # Adicionar assets padrão do template
            if template.default_assets:
                default_assets = json.loads(template.default_assets)
                
                for asset_data in default_assets:
                    asset = Asset(
                        scene_id=scene.id,
                        project_id=project_id,
                        name=asset_data.get('name', 'Asset do Template'),
                        tipo=asset_data.get('tipo', 'text'),
                        created_by=user_id,
                        **{k: v for k, v in asset_data.items() if k not in ['name', 'tipo']}
                    )
                    db.add(asset)
            
            # Incrementar contador de uso do template
            template.usage_count = (template.usage_count or 0) + 1
            
            db.commit()
            
            logger.info(f"Nova cena criada do template {template.name}: {scene.name}")
            return scene.id
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar cena do template: {e}")
            return None
        finally:
            db.close()
    
    def get_template_categories(self) -> List[Dict[str, str]]:
        """Obter lista de categorias disponíveis."""
        return [
            {"value": cat.value, "label": cat.value.replace("_", " ").title()}
            for cat in TemplateCategory
        ]
    
    def get_template_styles(self) -> List[Dict[str, str]]:
        """Obter lista de estilos disponíveis."""
        return [
            {"value": style.value, "label": style.value.replace("_", " ").title()}
            for style in TemplateStyle
        ]
    
    def populate_predefined_templates(self, db: Session = None) -> int:
        """Popular banco com templates predefinidos."""
        if not DATABASE_AVAILABLE:
            return 0
        
        if db is None:
            db = get_db_session()
        
        try:
            created_count = 0
            
            for template_key, template_config in self.predefined_templates.items():
                # Verificar se já existe
                existing = db.query(SceneTemplate).filter(
                    SceneTemplate.name == template_config.name
                ).first()
                
                if existing:
                    continue
                
                # Criar template
                template = SceneTemplate(
                    name=template_config.name,
                    description=template_config.description,
                    category=template_config.category.value,
                    style=template_config.style.value,
                    aspect_ratio=template_config.aspect_ratio,
                    resolution=template_config.resolution,
                    background_type=template_config.background_type,
                    background_config=json.dumps(template_config.background_config) if template_config.background_config else None,
                    layout_type=template_config.layout_type,
                    layout_config=json.dumps(template_config.layout_config) if template_config.layout_config else None,
                    template_data=json.dumps({"predefined": True, "key": template_key}),
                    default_assets=json.dumps(template_config.default_assets) if template_config.default_assets else None,
                    is_public=True,
                    is_featured=True,
                    tags=json.dumps(template_config.tags) if template_config.tags else None,
                    created_by=1  # Sistema
                )
                
                db.add(template)
                created_count += 1
            
            db.commit()
            logger.info(f"Criados {created_count} templates predefinidos")
            return created_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao popular templates: {e}")
            return 0
        finally:
            db.close()

# Instância global do serviço
scene_template_service = SceneTemplateService() 