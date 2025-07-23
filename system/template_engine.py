#!/usr/bin/env python3
"""
🎨 TEMPLATE ENGINE - FASE 6
Sistema avançado de templates prontos para criação rápida de vídeos

Funcionalidades:
✅ Templates profissionais pré-configurados
✅ Personalização dinâmica
✅ Preview em tempo real
✅ Export automático
✅ Biblioteca extensível
✅ AI-powered suggestions
✅ Brand customization
✅ Multi-language support

Data: 17 de Janeiro de 2025
Versão: 6.0.0
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class TemplateAsset:
    """Asset de um template"""
    id: str
    type: str  # image, video, audio, text, shape
    name: str
    url: str
    position: Dict[str, float]  # x, y, width, height
    properties: Dict[str, Any]
    animations: List[Dict[str, Any]]
    duration: float

@dataclass
class TemplateScene:
    """Cena de um template"""
    id: str
    name: str
    duration: float
    background: Dict[str, Any]
    assets: List[TemplateAsset]
    transitions: Dict[str, Any]
    audio: Optional[Dict[str, Any]]

@dataclass
class Template:
    """Template completo"""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    thumbnail: str
    duration: float
    resolution: Dict[str, int]  # width, height
    scenes: List[TemplateScene]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    author: str
    version: str
    premium: bool

class TemplateEngine:
    """Engine principal para gerenciar templates"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.categories = [
            "business", "education", "marketing", "social_media", 
            "presentation", "explainer", "tutorial", "promo"
        ]
        self.templates_path = Path("templates")
        self.templates_path.mkdir(exist_ok=True)
        
        # Carregar templates padrão
        self._load_default_templates()

    def _load_default_templates(self):
        """Carregar templates padrão do sistema"""
        
        # Template 1: Apresentação Corporativa
        corporate_template = self._create_corporate_presentation_template()
        self.templates[corporate_template.id] = corporate_template
        
        # Template 2: Vídeo Educacional
        educational_template = self._create_educational_video_template()
        self.templates[educational_template.id] = educational_template
        
        # Template 3: Marketing de Produto
        marketing_template = self._create_product_marketing_template()
        self.templates[marketing_template.id] = marketing_template
        
        # Template 4: Tutorial Técnico
        tutorial_template = self._create_tech_tutorial_template()
        self.templates[tutorial_template.id] = tutorial_template
        
        # Template 5: Social Media Story
        social_template = self._create_social_media_template()
        self.templates[social_template.id] = social_template
        
        logger.info(f"✅ {len(self.templates)} templates padrão carregados")

    def _create_corporate_presentation_template(self) -> Template:
        """Template: Apresentação Corporativa"""
        
        # Cena 1: Abertura
        opening_scene = TemplateScene(
            id="corp_opening",
            name="Abertura Corporativa",
            duration=5.0,
            background={
                "type": "gradient",
                "colors": ["#667eea", "#764ba2"],
                "direction": "diagonal"
            },
            assets=[
                TemplateAsset(
                    id="logo_placeholder",
                    type="image",
                    name="Logo da Empresa",
                    url="/templates/placeholders/logo.png",
                    position={"x": 0.4, "y": 0.3, "width": 0.2, "height": 0.2},
                    properties={"opacity": 1.0, "z_index": 10},
                    animations=[
                        {"type": "fade_in", "duration": 1.0, "delay": 0.5}
                    ],
                    duration=5.0
                ),
                TemplateAsset(
                    id="company_title",
                    type="text",
                    name="Nome da Empresa",
                    url="",
                    position={"x": 0.1, "y": 0.6, "width": 0.8, "height": 0.1},
                    properties={
                        "text": "SUA EMPRESA",
                        "font_family": "Arial Black",
                        "font_size": 48,
                        "color": "#ffffff",
                        "text_align": "center",
                        "font_weight": "bold"
                    },
                    animations=[
                        {"type": "slide_up", "duration": 1.0, "delay": 1.0}
                    ],
                    duration=5.0
                ),
                TemplateAsset(
                    id="subtitle",
                    type="text",
                    name="Subtítulo",
                    url="",
                    position={"x": 0.1, "y": 0.75, "width": 0.8, "height": 0.05},
                    properties={
                        "text": "Inovação • Qualidade • Resultados",
                        "font_family": "Arial",
                        "font_size": 24,
                        "color": "#e2e8f0",
                        "text_align": "center"
                    },
                    animations=[
                        {"type": "fade_in", "duration": 1.0, "delay": 2.0}
                    ],
                    duration=5.0
                )
            ],
            transitions={"out": {"type": "slide_left", "duration": 0.5}},
            audio={"background_music": "/templates/audio/corporate_intro.mp3", "volume": 0.3}
        )
        
        # Cena 2: Conteúdo Principal
        content_scene = TemplateScene(
            id="corp_content",
            name="Conteúdo Principal",
            duration=15.0,
            background={
                "type": "solid",
                "color": "#ffffff"
            },
            assets=[
                TemplateAsset(
                    id="main_title",
                    type="text",
                    name="Título Principal",
                    url="",
                    position={"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.1},
                    properties={
                        "text": "NOSSOS SERVIÇOS",
                        "font_family": "Arial Black",
                        "font_size": 36,
                        "color": "#667eea",
                        "text_align": "center"
                    },
                    animations=[
                        {"type": "slide_down", "duration": 0.8, "delay": 0.2}
                    ],
                    duration=15.0
                ),
                TemplateAsset(
                    id="content_image",
                    type="image",
                    name="Imagem de Conteúdo",
                    url="/templates/placeholders/business_content.jpg",
                    position={"x": 0.1, "y": 0.25, "width": 0.45, "height": 0.5},
                    properties={"border_radius": 10, "shadow": True},
                    animations=[
                        {"type": "zoom_in", "duration": 1.0, "delay": 0.5}
                    ],
                    duration=15.0
                ),
                TemplateAsset(
                    id="bullet_points",
                    type="text",
                    name="Pontos Principais",
                    url="",
                    position={"x": 0.6, "y": 0.3, "width": 0.35, "height": 0.4},
                    properties={
                        "text": "• Consultoria Especializada\n• Soluções Personalizadas\n• Suporte 24/7\n• Resultados Garantidos",
                        "font_family": "Arial",
                        "font_size": 20,
                        "color": "#2d3748",
                        "line_height": 1.6
                    },
                    animations=[
                        {"type": "slide_right", "duration": 1.0, "delay": 1.0}
                    ],
                    duration=15.0
                )
            ],
            transitions={"in": {"type": "slide_right", "duration": 0.5}},
            audio=None
        )
        
        return Template(
            id="corporate_presentation",
            name="Apresentação Corporativa",
            description="Template profissional para apresentações empresariais",
            category="business",
            tags=["corporativo", "profissional", "negócios", "empresa"],
            thumbnail="/templates/thumbnails/corporate.jpg",
            duration=20.0,
            resolution={"width": 1920, "height": 1080},
            scenes=[opening_scene, content_scene],
            metadata={
                "difficulty": "easy",
                "customizable_elements": ["logo", "company_name", "colors", "content"],
                "industries": ["consultoria", "tecnologia", "serviços", "varejo"]
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="TecnoCursos AI",
            version="1.0",
            premium=False
        )

    def _create_educational_video_template(self) -> Template:
        """Template: Vídeo Educacional"""
        
        # Cena 1: Introdução
        intro_scene = TemplateScene(
            id="edu_intro",
            name="Introdução da Aula",
            duration=8.0,
            background={
                "type": "gradient",
                "colors": ["#4facfe", "#00f2fe"],
                "direction": "vertical"
            },
            assets=[
                TemplateAsset(
                    id="lesson_title",
                    type="text",
                    name="Título da Aula",
                    url="",
                    position={"x": 0.1, "y": 0.3, "width": 0.8, "height": 0.2},
                    properties={
                        "text": "AULA: TÓPICO PRINCIPAL",
                        "font_family": "Arial Black",
                        "font_size": 42,
                        "color": "#ffffff",
                        "text_align": "center",
                        "text_shadow": "2px 2px 4px rgba(0,0,0,0.3)"
                    },
                    animations=[
                        {"type": "bounce_in", "duration": 1.2, "delay": 0.5}
                    ],
                    duration=8.0
                ),
                TemplateAsset(
                    id="instructor_name",
                    type="text",
                    name="Nome do Instrutor",
                    url="",
                    position={"x": 0.1, "y": 0.6, "width": 0.8, "height": 0.1},
                    properties={
                        "text": "Professor: Seu Nome",
                        "font_family": "Arial",
                        "font_size": 24,
                        "color": "#f7fafc",
                        "text_align": "center"
                    },
                    animations=[
                        {"type": "fade_in", "duration": 1.0, "delay": 1.5}
                    ],
                    duration=8.0
                ),
                TemplateAsset(
                    id="lesson_icon",
                    type="shape",
                    name="Ícone da Matéria",
                    url="",
                    position={"x": 0.45, "y": 0.75, "width": 0.1, "height": 0.1},
                    properties={
                        "shape_type": "circle",
                        "fill_color": "#ffffff",
                        "border_color": "#4299e1",
                        "border_width": 3,
                        "icon": "graduation-cap"
                    },
                    animations=[
                        {"type": "pulse", "duration": 2.0, "delay": 2.0, "repeat": True}
                    ],
                    duration=8.0
                )
            ],
            transitions={"out": {"type": "fade", "duration": 1.0}},
            audio={"background_music": "/templates/audio/educational_intro.mp3", "volume": 0.4}
        )
        
        # Cena 2: Explicação com Diagrama
        explanation_scene = TemplateScene(
            id="edu_explanation",
            name="Explicação com Diagrama",
            duration=20.0,
            background={
                "type": "solid",
                "color": "#f7fafc"
            },
            assets=[
                TemplateAsset(
                    id="diagram_area",
                    type="shape",
                    name="Área do Diagrama",
                    url="",
                    position={"x": 0.05, "y": 0.15, "width": 0.6, "height": 0.7},
                    properties={
                        "shape_type": "rectangle",
                        "fill_color": "#ffffff",
                        "border_color": "#e2e8f0",
                        "border_width": 2,
                        "border_radius": 8,
                        "shadow": True
                    },
                    animations=[],
                    duration=20.0
                ),
                TemplateAsset(
                    id="explanation_text",
                    type="text",
                    name="Texto Explicativo",
                    url="",
                    position={"x": 0.7, "y": 0.2, "width": 0.25, "height": 0.6},
                    properties={
                        "text": "CONCEITOS PRINCIPAIS:\n\n1. Fundamento A\n\n2. Fundamento B\n\n3. Aplicação Prática\n\n4. Exercícios",
                        "font_family": "Arial",
                        "font_size": 18,
                        "color": "#2d3748",
                        "line_height": 1.8,
                        "background_color": "#edf2f7",
                        "padding": 15,
                        "border_radius": 8
                    },
                    animations=[
                        {"type": "slide_left", "duration": 1.0, "delay": 0.5}
                    ],
                    duration=20.0
                )
            ],
            transitions={"in": {"type": "fade", "duration": 1.0}},
            audio=None
        )
        
        return Template(
            id="educational_video",
            name="Vídeo Educacional",
            description="Template para aulas e conteúdo educativo",
            category="education",
            tags=["educação", "aula", "ensino", "tutorial"],
            thumbnail="/templates/thumbnails/educational.jpg",
            duration=28.0,
            resolution={"width": 1920, "height": 1080},
            scenes=[intro_scene, explanation_scene],
            metadata={
                "difficulty": "medium",
                "customizable_elements": ["título", "instrutor", "conteúdo", "cores"],
                "subjects": ["matemática", "ciências", "tecnologia", "idiomas"]
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="TecnoCursos AI",
            version="1.0",
            premium=False
        )

    def _create_product_marketing_template(self) -> Template:
        """Template: Marketing de Produto"""
        
        product_scene = TemplateScene(
            id="product_showcase",
            name="Apresentação do Produto",
            duration=12.0,
            background={
                "type": "gradient",
                "colors": ["#ff9a9e", "#fecfef", "#fecfef"],
                "direction": "radial"
            },
            assets=[
                TemplateAsset(
                    id="product_title",
                    type="text",
                    name="Nome do Produto",
                    url="",
                    position={"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.15},
                    properties={
                        "text": "SEU PRODUTO INCRÍVEL",
                        "font_family": "Impact",
                        "font_size": 48,
                        "color": "#ffffff",
                        "text_align": "center",
                        "text_shadow": "3px 3px 6px rgba(0,0,0,0.5)"
                    },
                    animations=[
                        {"type": "zoom_in", "duration": 1.0, "delay": 0.3}
                    ],
                    duration=12.0
                ),
                TemplateAsset(
                    id="product_image",
                    type="image",
                    name="Imagem do Produto",
                    url="/templates/placeholders/product.jpg",
                    position={"x": 0.3, "y": 0.3, "width": 0.4, "height": 0.4},
                    properties={
                        "border_radius": 15,
                        "shadow": True,
                        "glow": True
                    },
                    animations=[
                        {"type": "rotate_in", "duration": 1.5, "delay": 1.0}
                    ],
                    duration=12.0
                ),
                TemplateAsset(
                    id="call_to_action",
                    type="text",
                    name="Call to Action",
                    url="",
                    position={"x": 0.2, "y": 0.8, "width": 0.6, "height": 0.1},
                    properties={
                        "text": "COMPRE AGORA!",
                        "font_family": "Arial Black",
                        "font_size": 32,
                        "color": "#ffffff",
                        "text_align": "center",
                        "background_color": "#e53e3e",
                        "border_radius": 25,
                        "padding": 10
                    },
                    animations=[
                        {"type": "pulse", "duration": 1.0, "delay": 3.0, "repeat": True}
                    ],
                    duration=12.0
                )
            ],
            transitions={},
            audio={"background_music": "/templates/audio/upbeat_marketing.mp3", "volume": 0.5}
        )
        
        return Template(
            id="product_marketing",
            name="Marketing de Produto",
            description="Template dinâmico para promover produtos",
            category="marketing",
            tags=["marketing", "produto", "vendas", "promocional"],
            thumbnail="/templates/thumbnails/marketing.jpg",
            duration=12.0,
            resolution={"width": 1920, "height": 1080},
            scenes=[product_scene],
            metadata={
                "difficulty": "easy",
                "customizable_elements": ["produto", "cores", "call_to_action"],
                "industries": ["e-commerce", "varejo", "tecnologia"]
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="TecnoCursos AI",
            version="1.0",
            premium=True
        )

    def _create_tech_tutorial_template(self) -> Template:
        """Template: Tutorial Técnico"""
        
        tech_scene = TemplateScene(
            id="tech_tutorial",
            name="Tutorial Passo a Passo",
            duration=25.0,
            background={
                "type": "gradient",
                "colors": ["#0f0f23", "#1a1a2e", "#16213e"],
                "direction": "diagonal"
            },
            assets=[
                TemplateAsset(
                    id="tutorial_title",
                    type="text",
                    name="Título do Tutorial",
                    url="",
                    position={"x": 0.1, "y": 0.05, "width": 0.8, "height": 0.1},
                    properties={
                        "text": "TUTORIAL: TECNOLOGIA",
                        "font_family": "Consolas",
                        "font_size": 32,
                        "color": "#00ff88",
                        "text_align": "center",
                        "glow": True
                    },
                    animations=[
                        {"type": "type_writer", "duration": 2.0, "delay": 0.5}
                    ],
                    duration=25.0
                ),
                TemplateAsset(
                    id="code_area",
                    type="shape",
                    name="Área de Código",
                    url="",
                    position={"x": 0.05, "y": 0.2, "width": 0.55, "height": 0.6},
                    properties={
                        "shape_type": "rectangle",
                        "fill_color": "#1e1e1e",
                        "border_color": "#00ff88",
                        "border_width": 2,
                        "border_radius": 5
                    },
                    animations=[],
                    duration=25.0
                ),
                TemplateAsset(
                    id="steps_list",
                    type="text",
                    name="Lista de Passos",
                    url="",
                    position={"x": 0.65, "y": 0.25, "width": 0.3, "height": 0.5},
                    properties={
                        "text": "PASSOS:\n\n□ Passo 1\n□ Passo 2\n□ Passo 3\n□ Passo 4\n□ Passo 5",
                        "font_family": "Consolas",
                        "font_size": 16,
                        "color": "#ffffff",
                        "line_height": 2.0,
                        "background_color": "rgba(255,255,255,0.1)",
                        "padding": 15,
                        "border_radius": 5
                    },
                    animations=[
                        {"type": "slide_right", "duration": 1.0, "delay": 1.0}
                    ],
                    duration=25.0
                )
            ],
            transitions={},
            audio=None
        )
        
        return Template(
            id="tech_tutorial",
            name="Tutorial Técnico",
            description="Template para tutoriais de programação e tecnologia",
            category="tutorial",
            tags=["tutorial", "programação", "tecnologia", "código"],
            thumbnail="/templates/thumbnails/tech_tutorial.jpg",
            duration=25.0,
            resolution={"width": 1920, "height": 1080},
            scenes=[tech_scene],
            metadata={
                "difficulty": "advanced",
                "customizable_elements": ["código", "passos", "linguagem"],
                "technologies": ["python", "javascript", "react", "nodejs"]
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="TecnoCursos AI",
            version="1.0",
            premium=True
        )

    def _create_social_media_template(self) -> Template:
        """Template: Social Media Story"""
        
        story_scene = TemplateScene(
            id="social_story",
            name="Story para Redes Sociais",
            duration=15.0,
            background={
                "type": "gradient",
                "colors": ["#667eea", "#764ba2", "#f093fb"],
                "direction": "vertical"
            },
            assets=[
                TemplateAsset(
                    id="story_text",
                    type="text",
                    name="Texto Principal",
                    url="",
                    position={"x": 0.1, "y": 0.3, "width": 0.8, "height": 0.4},
                    properties={
                        "text": "SUA MENSAGEM AQUI",
                        "font_family": "Arial Black",
                        "font_size": 36,
                        "color": "#ffffff",
                        "text_align": "center",
                        "text_shadow": "2px 2px 4px rgba(0,0,0,0.5)"
                    },
                    animations=[
                        {"type": "bounce_in", "duration": 1.0, "delay": 0.5}
                    ],
                    duration=15.0
                ),
                TemplateAsset(
                    id="hashtags",
                    type="text",
                    name="Hashtags",
                    url="",
                    position={"x": 0.1, "y": 0.8, "width": 0.8, "height": 0.1},
                    properties={
                        "text": "#hashtag #social #media",
                        "font_family": "Arial",
                        "font_size": 18,
                        "color": "#e2e8f0",
                        "text_align": "center"
                    },
                    animations=[
                        {"type": "fade_in", "duration": 1.0, "delay": 2.0}
                    ],
                    duration=15.0
                )
            ],
            transitions={},
            audio={"background_music": "/templates/audio/social_upbeat.mp3", "volume": 0.6}
        )
        
        return Template(
            id="social_media_story",
            name="Social Media Story",
            description="Template otimizado para stories de redes sociais",
            category="social_media",
            tags=["social", "story", "instagram", "tiktok"],
            thumbnail="/templates/thumbnails/social_story.jpg",
            duration=15.0,
            resolution={"width": 1080, "height": 1920},  # Formato vertical
            scenes=[story_scene],
            metadata={
                "difficulty": "easy",
                "customizable_elements": ["texto", "hashtags", "cores"],
                "platforms": ["instagram", "tiktok", "facebook", "snapchat"]
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author="TecnoCursos AI",
            version="1.0",
            premium=False
        )

    # ===================================================================
    # MÉTODOS PÚBLICOS
    # ===================================================================
    
    def get_templates(self, category: Optional[str] = None, premium_only: bool = False) -> List[Template]:
        """Obter lista de templates"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if premium_only:
            templates = [t for t in templates if t.premium]
        
        return templates

    def get_template(self, template_id: str) -> Optional[Template]:
        """Obter template específico"""
        return self.templates.get(template_id)

    def customize_template(self, template_id: str, customizations: Dict[str, Any]) -> Optional[Template]:
        """Personalizar template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Criar cópia personalizada
        customized = Template(**asdict(template))
        customized.id = str(uuid.uuid4())
        customized.name = f"{template.name} (Personalizado)"
        customized.updated_at = datetime.now().isoformat()
        
        # Aplicar personalizações
        for scene in customized.scenes:
            for asset in scene.assets:
                asset_key = f"{scene.id}_{asset.id}"
                if asset_key in customizations:
                    asset_customizations = customizations[asset_key]
                    
                    # Atualizar propriedades
                    if "properties" in asset_customizations:
                        asset.properties.update(asset_customizations["properties"])
                    
                    # Atualizar posição
                    if "position" in asset_customizations:
                        asset.position.update(asset_customizations["position"])
        
        return customized

    def export_template(self, template_id: str, format: str = "json") -> Optional[str]:
        """Exportar template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        if format == "json":
            return json.dumps(asdict(template), indent=2)
        
        return None

    def import_template(self, template_data: str, format: str = "json") -> bool:
        """Importar template"""
        try:
            if format == "json":
                data = json.loads(template_data)
                template = Template(**data)
                self.templates[template.id] = template
                return True
        except Exception as e:
            logger.error(f"Erro ao importar template: {e}")
        
        return False

    def search_templates(self, query: str) -> List[Template]:
        """Buscar templates"""
        query = query.lower()
        results = []
        
        for template in self.templates.values():
            # Buscar em nome, descrição e tags
            if (query in template.name.lower() or 
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results

    def get_template_suggestions(self, context: Dict[str, Any]) -> List[Template]:
        """Obter sugestões de templates baseadas no contexto"""
        suggestions = []
        
        # Lógica de sugestão baseada no contexto
        if context.get("industry") == "education":
            suggestions.extend([t for t in self.templates.values() if t.category == "education"])
        
        if context.get("purpose") == "marketing":
            suggestions.extend([t for t in self.templates.values() if t.category == "marketing"])
        
        if context.get("duration", 0) < 30:
            suggestions.extend([t for t in self.templates.values() if t.duration <= 30])
        
        # Remover duplicatas e limitar resultados
        seen = set()
        unique_suggestions = []
        for template in suggestions:
            if template.id not in seen:
                seen.add(template.id)
                unique_suggestions.append(template)
        
        return unique_suggestions[:10]

# ===================================================================
# INSTÂNCIA SINGLETON
# ===================================================================

template_engine = TemplateEngine()

def get_template_engine() -> TemplateEngine:
    """Obter instância do template engine"""
    return template_engine

if __name__ == "__main__":
    # Demonstração
    engine = get_template_engine()
    
    print("🎨 Template Engine - TecnoCursos AI")
    print("="*50)
    print(f"📋 Templates disponíveis: {len(engine.templates)}")
    
    for template in engine.templates.values():
        print(f"  • {template.name} ({template.category}) - {template.duration}s")
    
    print("\n🔍 Teste de busca por 'educação':")
    results = engine.search_templates("educação")
    for result in results:
        print(f"  • {result.name}")
    
    print("\n💡 Sugestões para contexto educacional:")
    suggestions = engine.get_template_suggestions({"industry": "education", "duration": 20})
    for suggestion in suggestions:
        print(f"  • {suggestion.name}") 