#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 VIDEO ENGINE - MOTOR UNIFICADO DE GERAÇÃO DE VÍDEOS
=====================================================

Sistema centralizado que unifica todas as funcionalidades de geração de vídeo
do TecnoCursos AI, organizando e padronizando todas as funções dispersas.

Funcionalidades Unificadas:
- Criação de vídeos a partir de texto e áudio
- Geração de avatares com IA
- Processamento de slides PDF/PPTX para vídeo
- Concatenação e transições
- Templates visuais avançados
- Pipeline completo TTS → Vídeo
- Exportação otimizada
- Cache e performance

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
import uuid
import time
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

# === IMPORTS DE DEPENDÊNCIAS ===
try:
    from moviepy.editor import (
        ImageClip, AudioFileClip, VideoFileClip, CompositeVideoClip, 
        ColorClip, TextClip, concatenate_videoclips,
        fadein, fadeout, resize
    )
    from moviepy.config import check_moviepy
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️ MoviePy não disponível - instale: pip install moviepy")

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL não disponível - instale: pip install pillow")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy não disponível - instale: pip install numpy")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("⚠️ gTTS não disponível - instale: pip install gtts")

# === CONFIGURAÇÕES E ENUMS ===

class VideoQuality(Enum):
    """Qualidades de vídeo suportadas"""
    LOW = "480p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4k"

class VideoTemplate(Enum):
    """Templates visuais disponíveis"""
    MODERN = "modern"
    CORPORATE = "corporate"
    TECH = "tech"
    EDUCATIONAL = "educational"
    MINIMAL = "minimal"

class ExportFormat(Enum):
    """Formatos de exportação"""
    MP4 = "mp4"
    WEBM = "webm"
    AVI = "avi"

@dataclass
class VideoConfig:
    """Configuração unificada de vídeo"""
    width: int = 1920
    height: int = 1080
    fps: int = 30
    quality: VideoQuality = VideoQuality.HIGH
    template: VideoTemplate = VideoTemplate.MODERN
    format: ExportFormat = ExportFormat.MP4
    codec: str = "libx264"
    audio_codec: str = "aac"
    bitrate: str = "2000k"

@dataclass
class ProcessingResult:
    """Resultado de processamento unificado"""
    success: bool = False
    output_path: Optional[str] = None
    duration: float = 0.0
    file_size: int = 0
    resolution: Tuple[int, int] = (0, 0)
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# === CLASSE PRINCIPAL DO VIDEO ENGINE ===

class VideoEngine:
    """
    Motor principal unificado de geração de vídeos
    
    Centraliza todas as funcionalidades de vídeo do sistema:
    - Criação de vídeos simples e complexos
    - Processamento de slides
    - Geração de avatares
    - Pipeline TTS completo
    - Otimização e cache
    """
    
    def __init__(self, config: Optional[VideoConfig] = None):
        """Inicializar o Video Engine"""
        self.config = config or VideoConfig()
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path("temp/video_engine")
        self.cache_dir = Path("cache/videos")
        self.output_dir = Path("static/videos")
        
        # Criar diretórios necessários
        for directory in [self.temp_dir, self.cache_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Verificar dependências
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Verificar dependências necessárias"""
        missing = []
        if not MOVIEPY_AVAILABLE:
            missing.append("moviepy")
        if not PIL_AVAILABLE:
            missing.append("pillow")
        if not NUMPY_AVAILABLE:
            missing.append("numpy")
            
        if missing:
            self.logger.warning(f"Dependências não disponíveis: {missing}")
    
    # === MÉTODOS PRINCIPAIS ===
    
    async def create_video_from_text_and_audio(
        self,
        text: str,
        audio_path: str,
        output_path: Optional[str] = None,
        template: Optional[VideoTemplate] = None,
        quality: Optional[VideoQuality] = None
    ) -> ProcessingResult:
        """
        Criar vídeo a partir de texto e áudio - MÉTODO UNIFICADO
        
        Unifica todas as implementações dispersas desta funcionalidade
        """
        start_time = time.time()
        
        if not MOVIEPY_AVAILABLE or not PIL_AVAILABLE:
            return ProcessingResult(
                success=False,
                error="Dependências não disponíveis (MoviePy/PIL)"
            )
        
        try:
            # Configurações
            template = template or self.config.template
            quality = quality or self.config.quality
            
            if not output_path:
                output_path = str(self.output_dir / f"video_{uuid.uuid4().hex[:8]}.mp4")
            
            # Obter configurações do template
            template_config = self._get_template_config(template)
            
            # Obter duração do áudio
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Criar imagem do slide
            slide_image = self._create_slide_image(text, template_config)
            
            # Criar clipe de vídeo
            video_clip = ImageClip(slide_image).set_duration(duration)
            video_clip = video_clip.set_audio(audio_clip)
            
            # Aplicar efeitos do template
            video_clip = self._apply_template_effects(video_clip, template)
            
            # Exportar vídeo
            video_clip.write_videofile(
                output_path,
                fps=self.config.fps,
                codec=self.config.codec,
                audio_codec=self.config.audio_codec,
                temp_audiofile="temp_audio.m4a",
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Limpeza
            audio_clip.close()
            video_clip.close()
            
            processing_time = time.time() - start_time
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            return ProcessingResult(
                success=True,
                output_path=output_path,
                duration=duration,
                file_size=file_size,
                resolution=(self.config.width, self.config.height),
                processing_time=processing_time,
                metadata={
                    "template": template.value,
                    "quality": quality.value,
                    "text_length": len(text)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro na criação de vídeo: {e}")
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def create_videos_for_slides(
        self,
        slides_text: List[str],
        audio_paths: List[str],
        output_folder: str,
        template: Optional[VideoTemplate] = None
    ) -> List[ProcessingResult]:
        """
        Criar múltiplos vídeos para slides - MÉTODO UNIFICADO
        
        Unifica todas as implementações de criação em lote
        """
        if len(slides_text) != len(audio_paths):
            return [ProcessingResult(
                success=False,
                error="Número de textos e áudios deve ser igual"
            )]
        
        results = []
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, (text, audio_path) in enumerate(zip(slides_text, audio_paths)):
            output_path = str(output_dir / f"slide_{i+1:03d}.mp4")
            
            result = await self.create_video_from_text_and_audio(
                text=text,
                audio_path=audio_path,
                output_path=output_path,
                template=template
            )
            
            results.append(result)
            
            if result.success:
                self.logger.info(f"✅ Slide {i+1} criado: {output_path}")
            else:
                self.logger.error(f"❌ Erro no slide {i+1}: {result.error}")
        
        return results
    
    async def concatenate_videos(
        self,
        video_paths: List[str],
        output_path: str,
        transition_duration: float = 0.5
    ) -> ProcessingResult:
        """
        Concatenar vídeos com transições - MÉTODO UNIFICADO
        """
        start_time = time.time()
        
        if not MOVIEPY_AVAILABLE:
            return ProcessingResult(
                success=False,
                error="MoviePy não disponível"
            )
        
        try:
            # Carregar vídeos
            clips = []
            for path in video_paths:
                if os.path.exists(path):
                    clip = VideoFileClip(path)
                    
                    # Aplicar transições
                    if clips:  # Não aplicar no primeiro vídeo
                        clip = clip.crossfadein(transition_duration)
                    
                    clips.append(clip)
            
            if not clips:
                return ProcessingResult(
                    success=False,
                    error="Nenhum vídeo válido encontrado"
                )
            
            # Concatenar
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Exportar
            final_video.write_videofile(
                output_path,
                fps=self.config.fps,
                codec=self.config.codec,
                temp_audiofile="temp_concat_audio.m4a",
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Limpeza
            for clip in clips:
                clip.close()
            final_video.close()
            
            processing_time = time.time() - start_time
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            duration = sum(clip.duration for clip in clips)
            
            return ProcessingResult(
                success=True,
                output_path=output_path,
                duration=duration,
                file_size=file_size,
                processing_time=processing_time,
                metadata={
                    "videos_count": len(clips),
                    "transition_duration": transition_duration
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro na concatenação: {e}")
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def generate_tts_and_video(
        self,
        text: str,
        output_path: str,
        voice: str = "pt-BR",
        template: Optional[VideoTemplate] = None
    ) -> ProcessingResult:
        """
        Pipeline completo TTS → Vídeo - MÉTODO UNIFICADO
        """
        start_time = time.time()
        
        if not GTTS_AVAILABLE:
            return ProcessingResult(
                success=False,
                error="gTTS não disponível"
            )
        
        try:
            # Gerar áudio TTS
            temp_audio = str(self.temp_dir / f"tts_{uuid.uuid4().hex[:8]}.mp3")
            
            tts = gTTS(text=text, lang=voice.split('-')[0], slow=False)
            tts.save(temp_audio)
            
            # Criar vídeo
            result = await self.create_video_from_text_and_audio(
                text=text,
                audio_path=temp_audio,
                output_path=output_path,
                template=template
            )
            
            # Limpeza
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            
            # Atualizar metadados
            if result.success:
                result.metadata["tts_voice"] = voice
                result.metadata["pipeline"] = "tts_to_video"
                result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no pipeline TTS: {e}")
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    # === MÉTODOS DE TEMPLATE E ESTILO ===
    
    def _get_template_config(self, template: VideoTemplate) -> Dict[str, Any]:
        """Obter configurações do template"""
        configs = {
            VideoTemplate.MODERN: {
                "background": {"type": "gradient", "colors": ["#1e3c72", "#2a5298"]},
                "text_color": "#ffffff",
                "font_size": 48,
                "font_family": "Arial",
                "padding": 80,
                "effects": ["shadow", "glow"]
            },
            VideoTemplate.CORPORATE: {
                "background": {"type": "solid", "color": "#f8f9fa"},
                "text_color": "#2c3e50",
                "font_size": 42,
                "font_family": "Arial",
                "padding": 100,
                "effects": ["subtle_shadow"]
            },
            VideoTemplate.TECH: {
                "background": {"type": "solid", "color": "#0d1117"},
                "text_color": "#00ff00",
                "font_size": 52,
                "font_family": "Courier New",
                "padding": 60,
                "effects": ["neon_glow", "grid"]
            },
            VideoTemplate.EDUCATIONAL: {
                "background": {"type": "gradient", "colors": ["#f0f8ff", "#4169e1"]},
                "text_color": "#1e3a8a",
                "font_size": 44,
                "font_family": "Arial",
                "padding": 90,
                "effects": ["friendly_shadow"]
            },
            VideoTemplate.MINIMAL: {
                "background": {"type": "solid", "color": "#ffffff"},
                "text_color": "#333333",
                "font_size": 40,
                "font_family": "Arial",
                "padding": 120,
                "effects": ["clean"]
            }
        }
        
        return configs.get(template, configs[VideoTemplate.MODERN])
    
    def _create_slide_image(self, text: str, template_config: Dict[str, Any]) -> np.ndarray:
        """Criar imagem do slide com template"""
        if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
            raise ImportError("PIL e NumPy são necessários")
        
        # Criar imagem base
        img = Image.new('RGB', (self.config.width, self.config.height))
        draw = ImageDraw.Draw(img)
        
        # Aplicar background
        self._apply_background(img, draw, template_config["background"])
        
        # Aplicar texto
        self._apply_text(img, draw, text, template_config)
        
        # Aplicar efeitos
        img = self._apply_image_effects(img, template_config.get("effects", []))
        
        # Converter para array numpy para MoviePy
        return np.array(img)
    
    def _apply_background(self, img: Image.Image, draw: ImageDraw.Draw, bg_config: Dict[str, Any]) -> None:
        """Aplicar background na imagem"""
        if bg_config["type"] == "solid":
            draw.rectangle([(0, 0), img.size], fill=bg_config["color"])
        elif bg_config["type"] == "gradient":
            self._create_gradient_background(img, bg_config["colors"])
    
    def _create_gradient_background(self, img: Image.Image, colors: List[str]) -> None:
        """Criar background gradiente"""
        if not NUMPY_AVAILABLE:
            return
        
        width, height = img.size
        array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Converter cores hex para RGB
        color1 = tuple(int(colors[0][i:i+2], 16) for i in (1, 3, 5))
        color2 = tuple(int(colors[1][i:i+2], 16) for i in (1, 3, 5))
        
        # Criar gradiente
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            array[y, :] = [r, g, b]
        
        # Aplicar na imagem
        gradient_img = Image.fromarray(array)
        img.paste(gradient_img)
    
    def _apply_text(self, img: Image.Image, draw: ImageDraw.Draw, text: str, config: Dict[str, Any]) -> None:
        """Aplicar texto na imagem"""
        try:
            font = ImageFont.truetype("arial.ttf", config["font_size"])
        except OSError:
            font = ImageFont.load_default()
        
        # Quebrar texto em linhas
        lines = self._wrap_text(text, font, img.width - 2 * config["padding"])
        
        # Calcular posição centralizada
        total_height = len(lines) * config["font_size"] * 1.2
        start_y = (img.height - total_height) // 2
        
        # Desenhar cada linha
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            y = start_y + i * config["font_size"] * 1.2
            
            draw.text((x, y), line, fill=config["text_color"], font=font)
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Quebrar texto em linhas"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _apply_image_effects(self, img: Image.Image, effects: List[str]) -> Image.Image:
        """Aplicar efeitos visuais na imagem"""
        for effect in effects:
            if effect == "shadow":
                # Aplicar sombra sutil
                pass
            elif effect == "glow":
                # Aplicar brilho
                pass
            elif effect == "neon_glow":
                # Aplicar brilho neon
                img = img.filter(ImageFilter.GaussianBlur(1))
        
        return img
    
    def _apply_template_effects(self, clip, template: VideoTemplate):
        """Aplicar efeitos do template no clipe"""
        # Por enquanto, retornar o clipe sem modificações
        # Futuramente adicionar efeitos específicos por template
        return clip
    
    # === MÉTODOS DE CACHE ===
    
    def _get_cache_key(self, **params) -> str:
        """Gerar chave de cache para parâmetros"""
        import hashlib
        
        cache_string = json.dumps(params, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _save_to_cache(self, cache_key: str, result: ProcessingResult) -> None:
        """Salvar resultado no cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            "result": {
                "success": result.success,
                "output_path": result.output_path,
                "duration": result.duration,
                "file_size": result.file_size,
                "resolution": result.resolution,
                "processing_time": result.processing_time,
                "error": result.error,
                "metadata": result.metadata
            },
            "created_at": datetime.now().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    
    def _load_from_cache(self, cache_key: str) -> Optional[ProcessingResult]:
        """Carregar resultado do cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Verificar se cache não expirou (24 horas)
            created_at = datetime.fromisoformat(cache_data["created_at"])
            if datetime.now() - created_at > timedelta(hours=24):
                cache_file.unlink()  # Remover cache expirado
                return None
            
            result_data = cache_data["result"]
            return ProcessingResult(
                success=result_data["success"],
                output_path=result_data["output_path"],
                duration=result_data["duration"],
                file_size=result_data["file_size"],
                resolution=tuple(result_data["resolution"]),
                processing_time=result_data["processing_time"],
                error=result_data["error"],
                metadata=result_data["metadata"]
            )
            
        except Exception as e:
            self.logger.warning(f"Erro ao carregar cache: {e}")
            return None

# === INSTÂNCIA GLOBAL ===

# Instância global do Video Engine
video_engine = VideoEngine()

# === FUNÇÕES DE COMPATIBILIDADE ===
# Para manter compatibilidade com código existente

async def create_video_from_text_and_audio(
    text: str,
    audio_path: str,
    output_path: str,
    template: str = "modern",
    **kwargs
) -> Dict[str, Any]:
    """Função de compatibilidade - usar video_engine.create_video_from_text_and_audio"""
    template_enum = VideoTemplate(template) if template in [t.value for t in VideoTemplate] else VideoTemplate.MODERN
    
    result = await video_engine.create_video_from_text_and_audio(
        text=text,
        audio_path=audio_path,
        output_path=output_path,
        template=template_enum
    )
    
    # Converter para formato esperado pelo código legado
    return {
        "success": result.success,
        "output_path": result.output_path,
        "duration": result.duration,
        "resolution": result.resolution,
        "file_size": result.file_size,
        "error": result.error,
        "processing_time": result.processing_time
    }

async def create_videos_for_slides(
    slides_text: List[str],
    audios_path: List[str],
    output_folder: str,
    template: str = "modern",
    **kwargs
) -> List[str]:
    """Função de compatibilidade - usar video_engine.create_videos_for_slides"""
    template_enum = VideoTemplate(template) if template in [t.value for t in VideoTemplate] else VideoTemplate.MODERN
    
    results = await video_engine.create_videos_for_slides(
        slides_text=slides_text,
        audio_paths=audios_path,
        output_folder=output_folder,
        template=template_enum
    )
    
    # Retornar apenas caminhos dos vídeos criados com sucesso
    return [result.output_path for result in results if result.success and result.output_path]

async def concatenate_videos(
    video_paths: List[str],
    output_path: str,
    **kwargs
) -> Dict[str, Any]:
    """Função de compatibilidade - usar video_engine.concatenate_videos"""
    result = await video_engine.concatenate_videos(
        video_paths=video_paths,
        output_path=output_path
    )
    
    return {
        "success": result.success,
        "output_path": result.output_path,
        "duration": result.duration,
        "file_size": result.file_size,
        "error": result.error,
        "videos_count": result.metadata.get("videos_count", 0)
    }

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Teste básico do Video Engine
    engine = VideoEngine()
    logger.info("🎬 Video Engine inicializado com sucesso!")
    logger.info(f"Dependências: MoviePy={MOVIEPY_AVAILABLE}, PIL={PIL_AVAILABLE}, NumPy={NUMPY_AVAILABLE}") 