"""
Serviço de Transições e Efeitos Visuais - TecnoCursos AI
Sistema completo para aplicar transições e efeitos em vídeos
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
from enum import Enum

try:
    from moviepy.editor import *
    from moviepy.video.fx import resize, fadeout, fadein
    from moviepy.video.fx.accel_decel import accel_decel
    from moviepy.video.fx.blackwhite import blackwhite
    from moviepy.video.fx.blink import blink
    from moviepy.video.fx.crop import crop
    from moviepy.video.fx.lum_contrast import lum_contrast
    from moviepy.video.fx.mirror_x import mirror_x
    from moviepy.video.fx.mirror_y import mirror_y
    from moviepy.video.fx.rotate import rotate
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import numpy as np

logger = logging.getLogger(__name__)

class TransitionType(Enum):
    """Tipos de transição disponíveis"""
    FADE = "fade"
    CROSSFADE = "crossfade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    CIRCLE_IN = "circle_in"
    CIRCLE_OUT = "circle_out"
    DISSOLVE = "dissolve"
    FLIP_HORIZONTAL = "flip_horizontal"
    FLIP_VERTICAL = "flip_vertical"

class EffectType(Enum):
    """Tipos de efeito disponíveis"""
    BLUR = "blur"
    SHARPEN = "sharpen"
    BLACK_WHITE = "black_white"
    SEPIA = "sepia"
    VINTAGE = "vintage"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    MIRROR_X = "mirror_x"
    MIRROR_Y = "mirror_y"
    ROTATE = "rotate"
    SCALE = "scale"
    GLOW = "glow"
    SHADOW = "shadow"
    CHROMAKEY = "chromakey"

@dataclass
class Transition:
    """Configuração de transição"""
    id: str
    name: str
    type: TransitionType
    duration: float = 1.0
    easing: str = "ease_in_out"  # linear, ease_in, ease_out, ease_in_out
    direction: Optional[str] = None  # up, down, left, right
    intensity: float = 1.0
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}

@dataclass
class Effect:
    """Configuração de efeito"""
    id: str
    name: str
    type: EffectType
    intensity: float = 1.0
    duration: Optional[float] = None  # None = aplicar por toda duração
    start_time: float = 0.0
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class TransitionsEffectsService:
    """Serviço completo para transições e efeitos visuais"""
    
    def __init__(self):
        self.temp_dir = Path("temp/transitions_effects")
        self.output_dir = Path("static/effects")
        self.presets_dir = Path("static/presets")
        
        # Criar diretórios
        for directory in [self.temp_dir, self.output_dir, self.presets_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configurações
        self.default_resolution = (1920, 1080)
        self.supported_formats = [".mp4", ".avi", ".mov", ".mkv"]
        
        # Cache de efeitos processados
        self.effects_cache = {}
        
        # Presets de transições e efeitos
        self.transition_presets = self._load_transition_presets()
        self.effect_presets = self._load_effect_presets()
        
        logger.info("🎬 Transitions & Effects Service inicializado")
    
    def _load_transition_presets(self) -> List[Dict[str, Any]]:
        """Carregar presets de transições"""
        return [
            {
                "id": "smooth_fade",
                "name": "Fade Suave",
                "category": "fade",
                "transition": Transition(
                    id="smooth_fade",
                    name="Fade Suave",
                    type=TransitionType.FADE,
                    duration=0.8,
                    easing="ease_out"
                ),
                "description": "Transição suave com fade",
                "preview": "/static/previews/smooth_fade.gif"
            },
            {
                "id": "dynamic_slide",
                "name": "Slide Dinâmico",
                "category": "slide",
                "transition": Transition(
                    id="dynamic_slide",
                    name="Slide Dinâmico",
                    type=TransitionType.SLIDE_LEFT,
                    duration=1.2,
                    easing="ease_in_out",
                    direction="left"
                ),
                "description": "Slide com movimento dinâmico",
                "preview": "/static/previews/dynamic_slide.gif"
            },
            {
                "id": "zoom_transition",
                "name": "Zoom Cinematográfico",
                "category": "zoom",
                "transition": Transition(
                    id="zoom_transition",
                    name="Zoom Cinematográfico",
                    type=TransitionType.ZOOM_IN,
                    duration=1.5,
                    easing="ease_in",
                    intensity=2.0
                ),
                "description": "Zoom com efeito cinematográfico",
                "preview": "/static/previews/zoom_transition.gif"
            },
            {
                "id": "circle_reveal",
                "name": "Revelação Circular",
                "category": "reveal",
                "transition": Transition(
                    id="circle_reveal",
                    name="Revelação Circular",
                    type=TransitionType.CIRCLE_IN,
                    duration=1.0,
                    easing="ease_out"
                ),
                "description": "Revelação em formato circular",
                "preview": "/static/previews/circle_reveal.gif"
            },
            {
                "id": "wipe_modern",
                "name": "Wipe Moderno",
                "category": "wipe",
                "transition": Transition(
                    id="wipe_modern",
                    name="Wipe Moderno",
                    type=TransitionType.WIPE_RIGHT,
                    duration=0.6,
                    easing="ease_in_out",
                    direction="right"
                ),
                "description": "Wipe com estilo moderno",
                "preview": "/static/previews/wipe_modern.gif"
            }
        ]
    
    def _load_effect_presets(self) -> List[Dict[str, Any]]:
        """Carregar presets de efeitos"""
        return [
            {
                "id": "cinematic_glow",
                "name": "Brilho Cinematográfico",
                "category": "glow",
                "effect": Effect(
                    id="cinematic_glow",
                    name="Brilho Cinematográfico",
                    type=EffectType.GLOW,
                    intensity=0.7,
                    parameters={"radius": 10, "strength": 1.5}
                ),
                "description": "Brilho suave para efeito cinematográfico",
                "preview": "/static/previews/cinematic_glow.jpg"
            },
            {
                "id": "vintage_film",
                "name": "Filme Vintage",
                "category": "vintage",
                "effect": Effect(
                    id="vintage_film",
                    name="Filme Vintage",
                    type=EffectType.VINTAGE,
                    intensity=0.8,
                    parameters={"grain": 0.3, "vignette": 0.5, "sepia": 0.6}
                ),
                "description": "Efeito de filme antigo",
                "preview": "/static/previews/vintage_film.jpg"
            },
            {
                "id": "dramatic_contrast",
                "name": "Contraste Dramático",
                "category": "contrast",
                "effect": Effect(
                    id="dramatic_contrast",
                    name="Contraste Dramático",
                    type=EffectType.CONTRAST,
                    intensity=1.3,
                    parameters={"gamma": 1.2, "saturation": 1.1}
                ),
                "description": "Alto contraste para efeito dramático",
                "preview": "/static/previews/dramatic_contrast.jpg"
            },
            {
                "id": "soft_blur",
                "name": "Desfoque Suave",
                "category": "blur",
                "effect": Effect(
                    id="soft_blur",
                    name="Desfoque Suave",
                    type=EffectType.BLUR,
                    intensity=0.4,
                    parameters={"radius": 3, "fade_edges": True}
                ),
                "description": "Desfoque suave para foco seletivo",
                "preview": "/static/previews/soft_blur.jpg"
            },
            {
                "id": "color_pop",
                "name": "Pop de Cor",
                "category": "color",
                "effect": Effect(
                    id="color_pop",
                    name="Pop de Cor",
                    type=EffectType.SATURATION,
                    intensity=1.5,
                    parameters={"selective_colors": ["red", "blue"], "boost": 1.3}
                ),
                "description": "Realce de cores específicas",
                "preview": "/static/previews/color_pop.jpg"
            }
        ]
    
    async def apply_transition(self, clip1: VideoClip, clip2: VideoClip, 
                             transition: Transition) -> VideoClip:
        """Aplicar transição entre dois clips"""
        try:
            if not MOVIEPY_AVAILABLE:
                logger.warning("MoviePy não disponível, retornando concatenação simples")
                return concatenate_videoclips([clip1, clip2])
            
            logger.info(f"🎭 Aplicando transição: {transition.name}")
            
            # Aplicar transição baseada no tipo
            if transition.type == TransitionType.FADE:
                return self._apply_fade_transition(clip1, clip2, transition)
            elif transition.type == TransitionType.CROSSFADE:
                return self._apply_crossfade_transition(clip1, clip2, transition)
            elif transition.type in [TransitionType.SLIDE_LEFT, TransitionType.SLIDE_RIGHT,
                                   TransitionType.SLIDE_UP, TransitionType.SLIDE_DOWN]:
                return self._apply_slide_transition(clip1, clip2, transition)
            elif transition.type in [TransitionType.ZOOM_IN, TransitionType.ZOOM_OUT]:
                return self._apply_zoom_transition(clip1, clip2, transition)
            elif transition.type in [TransitionType.WIPE_LEFT, TransitionType.WIPE_RIGHT]:
                return self._apply_wipe_transition(clip1, clip2, transition)
            elif transition.type in [TransitionType.CIRCLE_IN, TransitionType.CIRCLE_OUT]:
                return self._apply_circle_transition(clip1, clip2, transition)
            else:
                logger.warning(f"Tipo de transição não implementado: {transition.type}")
                return self._apply_fade_transition(clip1, clip2, transition)
                
        except Exception as e:
            logger.error(f"Erro ao aplicar transição: {e}")
            # Fallback para concatenação simples
            return concatenate_videoclips([clip1, clip2])
    
    def _apply_fade_transition(self, clip1: VideoClip, clip2: VideoClip, 
                              transition: Transition) -> VideoClip:
        """Aplicar transição fade"""
        duration = transition.duration
        
        # Fade out no primeiro clip
        clip1_faded = clip1.fadeout(duration)
        
        # Fade in no segundo clip
        clip2_faded = clip2.fadein(duration)
        
        # Sobrepor os clips durante a transição
        transition_clip = CompositeVideoClip([
            clip1_faded,
            clip2_faded.set_start(clip1.duration - duration)
        ])
        
        return transition_clip
    
    def _apply_crossfade_transition(self, clip1: VideoClip, clip2: VideoClip,
                                   transition: Transition) -> VideoClip:
        """Aplicar transição crossfade"""
        duration = transition.duration
        
        # Crossfade usando opacidade
        clip1_end = clip1.fadeout(duration)
        clip2_start = clip2.fadein(duration).set_start(clip1.duration - duration)
        
        return CompositeVideoClip([clip1_end, clip2_start])
    
    def _apply_slide_transition(self, clip1: VideoClip, clip2: VideoClip,
                               transition: Transition) -> VideoClip:
        """Aplicar transição slide"""
        duration = transition.duration
        w, h = clip1.size
        
        # Determinar direção do slide
        if transition.type == TransitionType.SLIDE_LEFT:
            # Clip2 entra pela direita
            clip2_pos = lambda t: (w * (1 - t/duration), 0) if t < duration else (0, 0)
        elif transition.type == TransitionType.SLIDE_RIGHT:
            # Clip2 entra pela esquerda
            clip2_pos = lambda t: (-w * (1 - t/duration), 0) if t < duration else (0, 0)
        elif transition.type == TransitionType.SLIDE_UP:
            # Clip2 entra por baixo
            clip2_pos = lambda t: (0, h * (1 - t/duration)) if t < duration else (0, 0)
        else:  # SLIDE_DOWN
            # Clip2 entra por cima
            clip2_pos = lambda t: (0, -h * (1 - t/duration)) if t < duration else (0, 0)
        
        # Posicionar clip2 durante a transição
        clip2_sliding = clip2.set_position(clip2_pos).set_start(clip1.duration - duration)
        
        return CompositeVideoClip([clip1, clip2_sliding])
    
    def _apply_zoom_transition(self, clip1: VideoClip, clip2: VideoClip,
                              transition: Transition) -> VideoClip:
        """Aplicar transição zoom"""
        duration = transition.duration
        
        if transition.type == TransitionType.ZOOM_IN:
            # Zoom in no final do clip1
            def zoom_func(t):
                if t > clip1.duration - duration:
                    progress = (t - (clip1.duration - duration)) / duration
                    return 1 + (transition.intensity - 1) * progress
                return 1
            
            clip1_zoomed = clip1.resize(zoom_func)
            clip2_start = clip2.set_start(clip1.duration)
            
        else:  # ZOOM_OUT
            # Zoom out no início do clip2
            def zoom_func(t):
                if t < duration:
                    progress = t / duration
                    return transition.intensity * (1 - progress) + progress
                return 1
            
            clip2_zoomed = clip2.resize(zoom_func)
            clip2_start = clip2_zoomed.set_start(clip1.duration - duration)
            clip1_end = clip1.fadeout(duration)
        
        return CompositeVideoClip([clip1_zoomed if transition.type == TransitionType.ZOOM_IN else clip1_end,
                                  clip2_start if transition.type == TransitionType.ZOOM_IN else clip2_start])
    
    def _apply_wipe_transition(self, clip1: VideoClip, clip2: VideoClip,
                              transition: Transition) -> VideoClip:
        """Aplicar transição wipe"""
        duration = transition.duration
        w, h = clip1.size
        
        def make_wipe_mask(t):
            if t < duration:
                progress = t / duration
                if transition.type == TransitionType.WIPE_RIGHT:
                    wipe_pos = int(w * progress)
                    mask = np.zeros((h, w))
                    mask[:, :wipe_pos] = 1
                else:  # WIPE_LEFT
                    wipe_pos = int(w * (1 - progress))
                    mask = np.zeros((h, w))
                    mask[:, wipe_pos:] = 1
                return mask
            return np.ones((h, w))
        
        # Aplicar máscara de wipe
        clip2_wiped = clip2.set_mask(lambda t: make_wipe_mask(t)).set_start(clip1.duration - duration)
        
        return CompositeVideoClip([clip1, clip2_wiped])
    
    def _apply_circle_transition(self, clip1: VideoClip, clip2: VideoClip,
                                transition: Transition) -> VideoClip:
        """Aplicar transição circular"""
        duration = transition.duration
        w, h = clip1.size
        center_x, center_y = w // 2, h // 2
        max_radius = max(w, h)
        
        def make_circle_mask(t):
            if t < duration:
                progress = t / duration
                if transition.type == TransitionType.CIRCLE_IN:
                    radius = max_radius * progress
                else:  # CIRCLE_OUT
                    radius = max_radius * (1 - progress)
                
                # Criar máscara circular
                Y, X = np.ogrid[:h, :w]
                mask = (X - center_x)**2 + (Y - center_y)**2 <= radius**2
                return mask.astype(float)
            return np.ones((h, w))
        
        clip2_circled = clip2.set_mask(lambda t: make_circle_mask(t)).set_start(clip1.duration - duration)
        
        return CompositeVideoClip([clip1, clip2_circled])
    
    async def apply_effect(self, clip: VideoClip, effect: Effect) -> VideoClip:
        """Aplicar efeito a um clip"""
        try:
            if not MOVIEPY_AVAILABLE:
                logger.warning("MoviePy não disponível, retornando clip original")
                return clip
            
            logger.info(f"✨ Aplicando efeito: {effect.name}")
            
            # Aplicar efeito baseado no tipo
            if effect.type == EffectType.BLUR:
                return self._apply_blur_effect(clip, effect)
            elif effect.type == EffectType.BLACK_WHITE:
                return self._apply_blackwhite_effect(clip, effect)
            elif effect.type == EffectType.BRIGHTNESS:
                return self._apply_brightness_effect(clip, effect)
            elif effect.type == EffectType.CONTRAST:
                return self._apply_contrast_effect(clip, effect)
            elif effect.type == EffectType.MIRROR_X:
                return clip.fx(mirror_x)
            elif effect.type == EffectType.MIRROR_Y:
                return clip.fx(mirror_y)
            elif effect.type == EffectType.ROTATE:
                angle = effect.parameters.get("angle", 90)
                return clip.fx(rotate, angle)
            elif effect.type == EffectType.SCALE:
                scale_factor = effect.intensity
                return clip.resize(scale_factor)
            else:
                logger.warning(f"Tipo de efeito não implementado: {effect.type}")
                return clip
                
        except Exception as e:
            logger.error(f"Erro ao aplicar efeito: {e}")
            return clip
    
    def _apply_blur_effect(self, clip: VideoClip, effect: Effect) -> VideoClip:
        """Aplicar efeito de desfoque"""
        blur_radius = effect.parameters.get("radius", 5) * effect.intensity
        
        def blur_frame(frame):
            if PIL_AVAILABLE:
                img = Image.fromarray(frame)
                blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                return np.array(blurred)
            return frame
        
        return clip.fl_image(blur_frame)
    
    def _apply_blackwhite_effect(self, clip: VideoClip, effect: Effect) -> VideoClip:
        """Aplicar efeito preto e branco"""
        return clip.fx(blackwhite)
    
    def _apply_brightness_effect(self, clip: VideoClip, effect: Effect) -> VideoClip:
        """Aplicar efeito de brilho"""
        brightness_factor = effect.intensity
        
        def adjust_brightness(frame):
            if PIL_AVAILABLE:
                img = Image.fromarray(frame)
                enhancer = ImageEnhance.Brightness(img)
                enhanced = enhancer.enhance(brightness_factor)
                return np.array(enhanced)
            return frame
        
        return clip.fl_image(adjust_brightness)
    
    def _apply_contrast_effect(self, clip: VideoClip, effect: Effect) -> VideoClip:
        """Aplicar efeito de contraste"""
        contrast_factor = effect.intensity
        
        def adjust_contrast(frame):
            if PIL_AVAILABLE:
                img = Image.fromarray(frame)
                enhancer = ImageEnhance.Contrast(img)
                enhanced = enhancer.enhance(contrast_factor)
                return np.array(enhanced)
            return frame
        
        return clip.fl_image(adjust_contrast)
    
    async def create_transition_preview(self, transition: Transition) -> str:
        """Criar preview de transição"""
        try:
            # Gerar preview usando imagens de exemplo
            preview_filename = f"transition_preview_{transition.id}.gif"
            preview_path = self.output_dir / preview_filename
            
            # Por ora, retornar placeholder
            # Em produção, geraria um GIF real mostrando a transição
            
            return f"/static/effects/{preview_filename}"
            
        except Exception as e:
            logger.error(f"Erro ao criar preview de transição: {e}")
            return "/static/images/transition_placeholder.gif"
    
    async def create_effect_preview(self, effect: Effect) -> str:
        """Criar preview de efeito"""
        try:
            # Gerar preview usando imagem de exemplo
            preview_filename = f"effect_preview_{effect.id}.jpg"
            preview_path = self.output_dir / preview_filename
            
            # Por ora, retornar placeholder
            # Em produção, aplicaria o efeito a uma imagem de exemplo
            
            return f"/static/effects/{preview_filename}"
            
        except Exception as e:
            logger.error(f"Erro ao criar preview de efeito: {e}")
            return "/static/images/effect_placeholder.jpg"
    
    def get_transition_presets(self) -> List[Dict[str, Any]]:
        """Obter presets de transições"""
        return [
            {
                "id": preset["id"],
                "name": preset["name"],
                "category": preset["category"],
                "description": preset["description"],
                "preview": preset["preview"],
                "duration": preset["transition"].duration,
                "type": preset["transition"].type.value
            }
            for preset in self.transition_presets
        ]
    
    def get_effect_presets(self) -> List[Dict[str, Any]]:
        """Obter presets de efeitos"""
        return [
            {
                "id": preset["id"],
                "name": preset["name"],
                "category": preset["category"],
                "description": preset["description"],
                "preview": preset["preview"],
                "intensity": preset["effect"].intensity,
                "type": preset["effect"].type.value
            }
            for preset in self.effect_presets
        ]
    
    def validate_transition_data(self, transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar dados de transição"""
        errors = []
        warnings = []
        
        # Validar tipo
        transition_type = transition_data.get("type")
        if not transition_type:
            errors.append("Tipo de transição é obrigatório")
        elif transition_type not in [t.value for t in TransitionType]:
            errors.append(f"Tipo de transição inválido: {transition_type}")
        
        # Validar duração
        duration = transition_data.get("duration", 1.0)
        if duration <= 0 or duration > 10:
            warnings.append("Duração da transição fora do range recomendado (0.1-10s)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_effect_data(self, effect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar dados de efeito"""
        errors = []
        warnings = []
        
        # Validar tipo
        effect_type = effect_data.get("type")
        if not effect_type:
            errors.append("Tipo de efeito é obrigatório")
        elif effect_type not in [e.value for e in EffectType]:
            errors.append(f"Tipo de efeito inválido: {effect_type}")
        
        # Validar intensidade
        intensity = effect_data.get("intensity", 1.0)
        if intensity < 0 or intensity > 5:
            warnings.append("Intensidade do efeito fora do range recomendado (0-5)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# Instância global do serviço
transitions_effects_service = TransitionsEffectsService()

# Funções de conveniência
async def apply_transition(clip1, clip2, transition_data: Dict[str, Any]):
    """Função de conveniência para aplicar transição"""
    transition = Transition(**transition_data)
    return await transitions_effects_service.apply_transition(clip1, clip2, transition)

async def apply_effect(clip, effect_data: Dict[str, Any]):
    """Função de conveniência para aplicar efeito"""
    effect = Effect(**effect_data)
    return await transitions_effects_service.apply_effect(clip, effect)

def get_transition_presets():
    """Função de conveniência para obter presets de transições"""
    return transitions_effects_service.get_transition_presets()

def get_effect_presets():
    """Função de conveniência para obter presets de efeitos"""
    return transitions_effects_service.get_effect_presets()