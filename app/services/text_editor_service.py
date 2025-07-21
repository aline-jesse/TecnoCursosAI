"""
Serviço de Editor de Texto Avançado - TecnoCursos AI
Sistema completo para criação e formatação de textos profissionais
"""

import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL import ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class TextStyle:
    """Configuração de estilo de texto"""
    font_family: str = "Arial"
    font_size: int = 24
    font_weight: str = "normal"  # normal, bold
    font_style: str = "normal"  # normal, italic
    color: str = "#ffffff"
    background_color: Optional[str] = None
    stroke_color: Optional[str] = None
    stroke_width: int = 0
    shadow_color: Optional[str] = None
    shadow_offset: Tuple[int, int] = (0, 0)
    shadow_blur: int = 0
    letter_spacing: float = 0.0
    line_height: float = 1.2
    text_align: str = "left"  # left, center, right, justify
    text_transform: str = "none"  # none, uppercase, lowercase, capitalize

@dataclass
class TextAnimation:
    """Configuração de animação de texto"""
    type: str = "none"  # none, fade_in, slide_in, typewriter, bounce
    duration: float = 1.0
    delay: float = 0.0
    direction: str = "up"  # up, down, left, right
    easing: str = "ease_in_out"  # linear, ease_in, ease_out, ease_in_out

@dataclass
class TextElement:
    """Elemento de texto completo"""
    id: str
    text: str
    x: int
    y: int
    width: int
    height: int
    style: TextStyle
    animation: Optional[TextAnimation] = None
    is_editable: bool = True
    layer: int = 0
    rotation: float = 0.0
    opacity: float = 1.0
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class TextEditorService:
    """Serviço completo para edição de texto avançada"""
    
    def __init__(self):
        self.temp_dir = Path("temp/text_editor")
        self.output_dir = Path("static/text/generated")
        self.fonts_dir = Path("static/fonts")
        
        # Criar diretórios
        for directory in [self.temp_dir, self.output_dir, self.fonts_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configurações
        self.max_canvas_size = (4000, 3000)
        self.default_canvas_size = (1920, 1080)
        
        # Cache de fontes
        self.font_cache = {}
        self.available_fonts = self._load_available_fonts()
        
        # Templates de texto
        self.text_templates = self._load_text_templates()
        
        logger.info("📝 Text Editor Service inicializado")
    
    def _load_available_fonts(self) -> List[Dict[str, str]]:
        """Carregar fontes disponíveis no sistema"""
        fonts = []
        
        # Fontes padrão do sistema
        system_fonts = [
            {"name": "Arial", "family": "Arial", "category": "sans-serif"},
            {"name": "Times New Roman", "family": "Times New Roman", "category": "serif"},
            {"name": "Helvetica", "family": "Helvetica", "category": "sans-serif"},
            {"name": "Georgia", "family": "Georgia", "category": "serif"},
            {"name": "Verdana", "family": "Verdana", "category": "sans-serif"},
            {"name": "Courier New", "family": "Courier New", "category": "monospace"},
            {"name": "Comic Sans MS", "family": "Comic Sans MS", "category": "cursive"},
            {"name": "Impact", "family": "Impact", "category": "display"},
            {"name": "Trebuchet MS", "family": "Trebuchet MS", "category": "sans-serif"},
            {"name": "Palatino", "family": "Palatino", "category": "serif"}
        ]
        
        fonts.extend(system_fonts)
        
        # Verificar fontes customizadas na pasta fonts
        if self.fonts_dir.exists():
            for font_file in self.fonts_dir.glob("*.ttf"):
                fonts.append({
                    "name": font_file.stem,
                    "family": font_file.stem,
                    "category": "custom",
                    "file_path": str(font_file)
                })
        
        logger.info(f"🔤 {len(fonts)} fontes carregadas")
        return fonts
    
    def _load_text_templates(self) -> List[Dict[str, Any]]:
        """Carregar templates de texto predefinidos"""
        return [
            {
                "id": "title_modern",
                "name": "Título Moderno",
                "category": "titles",
                "style": TextStyle(
                    font_family="Arial",
                    font_size=48,
                    font_weight="bold",
                    color="#ffffff",
                    stroke_color="#000000",
                    stroke_width=2,
                    shadow_color="#00000080",
                    shadow_offset=(2, 2),
                    shadow_blur=4
                ),
                "animation": TextAnimation(
                    type="fade_in",
                    duration=1.0,
                    easing="ease_out"
                )
            },
            {
                "id": "subtitle_elegant",
                "name": "Legenda Elegante",
                "category": "subtitles",
                "style": TextStyle(
                    font_family="Georgia",
                    font_size=24,
                    font_style="italic",
                    color="#e2e8f0",
                    letter_spacing=1.0,
                    line_height=1.4
                ),
                "animation": TextAnimation(
                    type="slide_in",
                    duration=0.8,
                    direction="up"
                )
            },
            {
                "id": "call_to_action",
                "name": "Call to Action",
                "category": "buttons",
                "style": TextStyle(
                    font_family="Arial",
                    font_size=28,
                    font_weight="bold",
                    color="#ffffff",
                    background_color="#667eea",
                    text_align="center",
                    text_transform="uppercase",
                    letter_spacing=2.0
                ),
                "animation": TextAnimation(
                    type="bounce",
                    duration=1.2,
                    delay=0.5
                )
            },
            {
                "id": "tech_title",
                "name": "Título Tech",
                "category": "tech",
                "style": TextStyle(
                    font_family="Courier New",
                    font_size=36,
                    font_weight="bold",
                    color="#00ff00",
                    stroke_color="#003300",
                    stroke_width=1,
                    background_color="#001100",
                    letter_spacing=1.5
                ),
                "animation": TextAnimation(
                    type="typewriter",
                    duration=2.0
                )
            },
            {
                "id": "corporate_heading",
                "name": "Cabeçalho Corporativo",
                "category": "corporate",
                "style": TextStyle(
                    font_family="Helvetica",
                    font_size=32,
                    font_weight="bold",
                    color="#2d3748",
                    text_align="center",
                    letter_spacing=0.5,
                    line_height=1.3
                ),
                "animation": TextAnimation(
                    type="slide_in",
                    duration=1.0,
                    direction="left"
                )
            }
        ]
    
    async def create_text_element(self, text: str, x: int, y: int, 
                                style: Dict[str, Any] = None,
                                animation: Dict[str, Any] = None) -> TextElement:
        """Criar novo elemento de texto"""
        try:
            # Configurar estilo
            text_style = TextStyle()
            if style:
                for key, value in style.items():
                    if hasattr(text_style, key):
                        setattr(text_style, key, value)
            
            # Configurar animação
            text_animation = None
            if animation:
                text_animation = TextAnimation(**animation)
            
            # Calcular dimensões aproximadas do texto
            width, height = self._calculate_text_dimensions(text, text_style)
            
            # Criar elemento
            text_element = TextElement(
                id=str(uuid.uuid4()),
                text=text,
                x=x,
                y=y,
                width=width,
                height=height,
                style=text_style,
                animation=text_animation
            )
            
            logger.info(f"📝 Elemento de texto criado: {text[:30]}...")
            return text_element
            
        except Exception as e:
            logger.error(f"Erro ao criar elemento de texto: {e}")
            raise
    
    async def apply_template(self, text: str, template_id: str, 
                           x: int = 100, y: int = 100) -> TextElement:
        """Aplicar template predefinido ao texto"""
        try:
            # Buscar template
            template = next((t for t in self.text_templates if t["id"] == template_id), None)
            if not template:
                raise ValueError(f"Template não encontrado: {template_id}")
            
            # Criar elemento com template
            text_element = await self.create_text_element(
                text=text,
                x=x,
                y=y,
                style=template["style"].__dict__,
                animation=template.get("animation").__dict__ if template.get("animation") else None
            )
            
            logger.info(f"🎨 Template aplicado: {template_id}")
            return text_element
            
        except Exception as e:
            logger.error(f"Erro ao aplicar template: {e}")
            raise
    
    async def render_text_element(self, text_element: TextElement, 
                                canvas_size: Tuple[int, int] = None) -> str:
        """Renderizar elemento de texto como imagem"""
        try:
            if not PIL_AVAILABLE:
                raise Exception("PIL não disponível para renderização")
            
            canvas_size = canvas_size or self.default_canvas_size
            
            # Criar canvas
            img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Configurar fonte
            font = self._get_font(text_element.style)
            
            # Preparar texto
            text = self._prepare_text(text_element.text, text_element.style)
            
            # Calcular posição
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Ajustar posição baseada no alinhamento
            x, y = self._calculate_text_position(
                text_element.x, text_element.y,
                text_width, text_height,
                text_element.style.text_align,
                canvas_size
            )
            
            # Desenhar sombra se configurada
            if text_element.style.shadow_color:
                self._draw_text_shadow(draw, text, x, y, font, text_element.style)
            
            # Desenhar background se configurado
            if text_element.style.background_color:
                self._draw_text_background(draw, x, y, text_width, text_height, text_element.style)
            
            # Desenhar texto principal
            self._draw_text_main(draw, text, x, y, font, text_element.style)
            
            # Aplicar efeitos adicionais
            img = self._apply_text_effects(img, text_element)
            
            # Salvar imagem
            output_filename = f"text_{text_element.id}.png"
            output_path = self.output_dir / output_filename
            
            img.save(output_path, "PNG")
            
            return f"/static/text/generated/{output_filename}"
            
        except Exception as e:
            logger.error(f"Erro ao renderizar texto: {e}")
            raise
    
    def _calculate_text_dimensions(self, text: str, style: TextStyle) -> Tuple[int, int]:
        """Calcular dimensões aproximadas do texto"""
        try:
            if not PIL_AVAILABLE:
                # Estimativa baseada em caracteres
                char_width = style.font_size * 0.6
                char_height = style.font_size * 1.2
                
                lines = text.split('\n')
                max_line_length = max(len(line) for line in lines) if lines else 0
                
                width = int(max_line_length * char_width)
                height = int(len(lines) * char_height * style.line_height)
                
                return width, height
            
            # Usar PIL para cálculo preciso
            font = self._get_font(style)
            
            # Criar imagem temporária para medição
            temp_img = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(temp_img)
            
            # Medir texto
            text_bbox = draw.textbbox((0, 0), text, font=font)
            width = text_bbox[2] - text_bbox[0]
            height = text_bbox[3] - text_bbox[1]
            
            # Adicionar margens
            width += style.stroke_width * 2
            height += style.stroke_width * 2
            
            return width, height
            
        except Exception as e:
            logger.error(f"Erro ao calcular dimensões: {e}")
            # Fallback
            return 200, 50
    
    def _get_font(self, style: TextStyle) -> ImageFont.ImageFont:
        """Obter fonte configurada"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            font_key = f"{style.font_family}_{style.font_size}_{style.font_weight}_{style.font_style}"
            
            if font_key in self.font_cache:
                return self.font_cache[font_key]
            
            # Tentar carregar fonte customizada
            font_info = next((f for f in self.available_fonts 
                             if f["family"] == style.font_family), None)
            
            if font_info and "file_path" in font_info:
                font = ImageFont.truetype(font_info["file_path"], style.font_size)
            else:
                # Usar fonte padrão do sistema
                try:
                    font_name = self._get_system_font_name(style.font_family, style.font_weight, style.font_style)
                    font = ImageFont.truetype(font_name, style.font_size)
                except:
                    font = ImageFont.load_default()
            
            self.font_cache[font_key] = font
            return font
            
        except Exception as e:
            logger.warning(f"Erro ao carregar fonte {style.font_family}: {e}")
            return ImageFont.load_default()
    
    def _get_system_font_name(self, family: str, weight: str, style: str) -> str:
        """Obter nome da fonte do sistema"""
        font_map = {
            "Arial": "arial.ttf",
            "Times New Roman": "times.ttf",
            "Helvetica": "arial.ttf",  # Fallback
            "Georgia": "georgia.ttf",
            "Verdana": "verdana.ttf",
            "Courier New": "cour.ttf",
            "Comic Sans MS": "comic.ttf",
            "Impact": "impact.ttf",
            "Trebuchet MS": "trebuc.ttf"
        }
        
        base_font = font_map.get(family, "arial.ttf")
        
        # Ajustar para peso e estilo
        if weight == "bold" and style == "italic":
            base_font = base_font.replace(".ttf", "bi.ttf")
        elif weight == "bold":
            base_font = base_font.replace(".ttf", "bd.ttf")
        elif style == "italic":
            base_font = base_font.replace(".ttf", "i.ttf")
        
        return base_font
    
    def _prepare_text(self, text: str, style: TextStyle) -> str:
        """Preparar texto para renderização"""
        if style.text_transform == "uppercase":
            text = text.upper()
        elif style.text_transform == "lowercase":
            text = text.lower()
        elif style.text_transform == "capitalize":
            text = text.title()
        
        return text
    
    def _calculate_text_position(self, x: int, y: int, text_width: int, text_height: int,
                               align: str, canvas_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calcular posição final do texto baseada no alinhamento"""
        if align == "center":
            x = x - text_width // 2
        elif align == "right":
            x = x - text_width
        
        # Garantir que o texto não saia do canvas
        x = max(0, min(x, canvas_size[0] - text_width))
        y = max(0, min(y, canvas_size[1] - text_height))
        
        return x, y
    
    def _draw_text_shadow(self, draw: ImageDraw.Draw, text: str, x: int, y: int,
                         font: ImageFont.ImageFont, style: TextStyle):
        """Desenhar sombra do texto"""
        if not style.shadow_color:
            return
        
        shadow_x = x + style.shadow_offset[0]
        shadow_y = y + style.shadow_offset[1]
        
        draw.text((shadow_x, shadow_y), text, fill=style.shadow_color, font=font)
    
    def _draw_text_background(self, draw: ImageDraw.Draw, x: int, y: int,
                            width: int, height: int, style: TextStyle):
        """Desenhar background do texto"""
        if not style.background_color:
            return
        
        # Adicionar padding
        padding = 8
        bg_rect = [
            x - padding,
            y - padding,
            x + width + padding,
            y + height + padding
        ]
        
        draw.rectangle(bg_rect, fill=style.background_color)
    
    def _draw_text_main(self, draw: ImageDraw.Draw, text: str, x: int, y: int,
                       font: ImageFont.ImageFont, style: TextStyle):
        """Desenhar texto principal"""
        # Desenhar contorno se configurado
        if style.stroke_width > 0 and style.stroke_color:
            for adj_x in range(-style.stroke_width, style.stroke_width + 1):
                for adj_y in range(-style.stroke_width, style.stroke_width + 1):
                    draw.text((x + adj_x, y + adj_y), text, fill=style.stroke_color, font=font)
        
        # Desenhar texto principal
        draw.text((x, y), text, fill=style.color, font=font)
    
    def _apply_text_effects(self, img: Image.Image, text_element: TextElement) -> Image.Image:
        """Aplicar efeitos adicionais ao texto"""
        try:
            # Aplicar opacidade
            if text_element.opacity < 1.0:
                img = img.convert("RGBA")
                alpha = img.split()[-1]
                alpha = ImageEnhance.Brightness(alpha).enhance(text_element.opacity)
                img.putalpha(alpha)
            
            # Aplicar rotação
            if text_element.rotation != 0:
                img = img.rotate(text_element.rotation, expand=True)
            
            # Aplicar blur na sombra se configurado
            if text_element.style.shadow_blur > 0:
                # Este é um efeito básico - em produção seria mais sofisticado
                img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            return img
            
        except Exception as e:
            logger.warning(f"Erro ao aplicar efeitos: {e}")
            return img
    
    def get_available_fonts(self) -> List[Dict[str, str]]:
        """Obter lista de fontes disponíveis"""
        return self.available_fonts
    
    def get_text_templates(self) -> List[Dict[str, Any]]:
        """Obter templates de texto disponíveis"""
        return [
            {
                "id": template["id"],
                "name": template["name"],
                "category": template["category"],
                "preview": f"/static/previews/{template['id']}.jpg"
            }
            for template in self.text_templates
        ]
    
    def export_text_styles(self) -> Dict[str, Any]:
        """Exportar estilos para uso no frontend"""
        return {
            "fonts": self.available_fonts,
            "templates": self.get_text_templates(),
            "default_styles": {
                "font_sizes": [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 64, 72, 96],
                "font_weights": ["normal", "bold"],
                "font_styles": ["normal", "italic"],
                "text_aligns": ["left", "center", "right", "justify"],
                "text_transforms": ["none", "uppercase", "lowercase", "capitalize"],
                "animation_types": ["none", "fade_in", "slide_in", "typewriter", "bounce"],
                "animation_directions": ["up", "down", "left", "right"],
                "animation_easings": ["linear", "ease_in", "ease_out", "ease_in_out"]
            }
        }
    
    async def validate_text_element(self, text_element_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar dados do elemento de texto"""
        errors = []
        warnings = []
        
        # Validar texto
        if not text_element_data.get("text"):
            errors.append("Texto não pode estar vazio")
        
        # Validar posição
        x = text_element_data.get("x", 0)
        y = text_element_data.get("y", 0)
        
        if x < 0 or y < 0:
            warnings.append("Posição negativa pode causar problemas de renderização")
        
        # Validar estilo
        style = text_element_data.get("style", {})
        font_size = style.get("font_size", 24)
        
        if font_size < 8 or font_size > 200:
            warnings.append("Tamanho de fonte fora do range recomendado (8-200)")
        
        # Validar fonte
        font_family = style.get("font_family", "Arial")
        if not any(f["family"] == font_family for f in self.available_fonts):
            warnings.append(f"Fonte '{font_family}' não encontrada, usando Arial como fallback")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# Instância global do serviço
text_editor_service = TextEditorService()

# Funções de conveniência
async def create_text(text: str, x: int, y: int, style: Dict[str, Any] = None) -> TextElement:
    """Função de conveniência para criar texto"""
    return await text_editor_service.create_text_element(text, x, y, style)

async def apply_text_template(text: str, template_id: str, x: int = 100, y: int = 100) -> TextElement:
    """Função de conveniência para aplicar template"""
    return await text_editor_service.apply_template(text, template_id, x, y)

def get_fonts() -> List[Dict[str, str]]:
    """Função de conveniência para obter fontes"""
    return text_editor_service.get_available_fonts()

def get_templates() -> List[Dict[str, Any]]:
    """Função de conveniência para obter templates"""
    return text_editor_service.get_text_templates()