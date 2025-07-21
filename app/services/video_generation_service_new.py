"""
Serviço de Geração Real de Vídeos - TecnoCursos AI
Implementação completa com MoviePy para renderização profissional
"""

import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

try:
    from moviepy.editor import *
    from moviepy.config import check_moviepy
    MOVIEPY_AVAILABLE = True
    VideoClipType = VideoClip
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoClipType = Any  # Fallback para quando MoviePy não estiver disponível

from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Configurar logger
logger = logging.getLogger(__name__)

class VideoGenerationService:
    """Serviço completo para geração de vídeos a partir de projetos"""
    
    def __init__(self):
        self.temp_dir = Path("temp/video_generation")
        self.output_dir = Path("static/videos")
        self.assets_dir = Path("uploads")
        
        # Criar diretórios
        for directory in [self.temp_dir, self.output_dir, self.assets_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configurações padrão
        self.default_settings = {
            "resolution": (1920, 1080),
            "fps": 30,
            "background_color": "#1a202c",
            "font_family": "Arial",
            "font_size": 48,
            "text_color": "#ffffff"
        }
        
        # Verificar disponibilidade do MoviePy
        if not MOVIEPY_AVAILABLE:
            logger.warning("MoviePy não disponível. Usando modo de simulação.")
    
    async def generate_video_from_project(self, project_data: Dict[str, Any], 
                                        export_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gerar vídeo completo a partir dos dados do projeto"""
        try:
            if not MOVIEPY_AVAILABLE:
                return await self._simulate_video_generation(project_data, export_settings)
            
            # Configurações finais
            settings = {**self.default_settings, **(export_settings or {})}
            
            # Extrair dados do projeto
            scenes = project_data.get("scenes", [])
            timeline = project_data.get("timeline", [])
            project_settings = project_data.get("settings", {})
            
            if not scenes:
                raise ValueError("Projeto deve ter pelo menos uma cena")
            
            # Gerar clips para cada cena
            scene_clips = []
            total_duration = 0
            
            for i, scene in enumerate(scenes):
                logger.info(f"Processando cena {i+1}/{len(scenes)}: {scene.get('title', f'Cena {i+1}')}")
                
                clip = await self._create_scene_clip(scene, settings)
                if clip:
                    scene_clips.append(clip)
                    total_duration += scene.get("duration", 3)
            
            if not scene_clips:
                raise ValueError("Nenhuma cena válida encontrada")
            
            # Combinar cenas com transições
            logger.info("Combinando cenas...")
            final_video = self._combine_scenes_with_transitions(scene_clips, settings)
            
            # Adicionar áudio se disponível
            audio_clips = await self._process_audio_tracks(timeline, total_duration)
            if audio_clips:
                logger.info("Adicionando trilha sonora...")
                final_audio = CompositeAudioClip(audio_clips)
                final_video = final_video.set_audio(final_audio)
            
            # Configurar output
            output_filename = f"project_{uuid.uuid4()}.mp4"
            output_path = self.output_dir / output_filename
            
            # Renderizar vídeo final
            logger.info(f"Renderizando vídeo final: {output_path}")
            final_video.write_videofile(
                str(output_path),
                fps=settings.get("fps", 30),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(self.temp_dir / "temp_audio.m4a"),
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Cleanup
            final_video.close()
            for clip in scene_clips:
                clip.close()
            
            return {
                "success": True,
                "video_path": str(output_path),
                "video_url": f"/static/videos/{output_filename}",
                "duration": total_duration,
                "resolution": f"{settings['resolution'][0]}x{settings['resolution'][1]}",
                "file_size": os.path.getsize(output_path),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na geração do vídeo: {e}")
            return {
                "success": False,
                "error": str(e),
                "details": "Verifique os logs para mais informações"
            }
    
    async def _create_scene_clip(self, scene: Dict[str, Any], settings: Dict[str, Any]) -> Optional[VideoClipType]:
        """Criar clip de vídeo para uma cena específica"""
        try:
            duration = scene.get("duration", 3)
            elements = scene.get("elements", [])
            scene_type = scene.get("type", "default")
            
            # Criar background base
            background = self._create_background_clip(duration, settings)
            
            # Lista de clips para composição
            clips = [background]
            
            # Processar elementos da cena
            for element in elements:
                element_clip = await self._create_element_clip(element, duration, settings)
                if element_clip:
                    clips.append(element_clip)
            
            # Adicionar título se especificado
            title = scene.get("title")
            if title and scene_type in ["title", "intro", "outro"]:
                title_clip = self._create_title_clip(title, duration, settings)
                clips.append(title_clip)
            
            # Compor cena final
            if len(clips) > 1:
                scene_clip = CompositeVideoClip(clips, size=settings["resolution"])
            else:
                scene_clip = clips[0]
            
            return scene_clip.set_duration(duration)
            
        except Exception as e:
            logger.error(f"Erro ao criar clip da cena: {e}")
            return None
    
    def _create_background_clip(self, duration: float, settings: Dict[str, Any]) -> VideoClip:
        """Criar clip de background"""
        resolution = settings["resolution"]
        bg_color = settings.get("background_color", "#1a202c")
        
        # Converter cor hex para RGB
        if bg_color.startswith("#"):
            bg_color = bg_color[1:]
            rgb = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            rgb = (26, 32, 44)  # Fallback
        
        # Criar imagem de background
        img = Image.new("RGB", resolution, rgb)
        
        # Adicionar gradiente sutil
        draw = ImageDraw.Draw(img)
        for i in range(resolution[1]//2):
            alpha = i / (resolution[1]//2) * 0.1
            color = tuple(max(0, min(255, int(c * (1 + alpha)))) for c in rgb)
            draw.line([(0, i), (resolution[0], i)], fill=color)
        
        # Converter para array numpy
        img_array = np.array(img)
        
        # Criar VideoClip
        return ImageClip(img_array, duration=duration)
    
    async def _create_element_clip(self, element: Dict[str, Any], 
                                 duration: float, settings: Dict[str, Any]) -> Optional[VideoClip]:
        """Criar clip para um elemento específico"""
        try:
            element_type = element.get("type", "unknown")
            asset_path = element.get("asset_path")
            position = (element.get("x", 0), element.get("y", 0))
            size = (element.get("width", 100), element.get("height", 100))
            
            if not asset_path or not os.path.exists(asset_path):
                return None
            
            if element_type == "image":
                return self._create_image_clip(asset_path, duration, position, size)
            elif element_type == "video":
                return self._create_video_clip(asset_path, duration, position, size)
            elif element_type == "text":
                return self._create_text_clip(element, duration, settings)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar clip do elemento: {e}")
            return None
    
    def _create_image_clip(self, image_path: str, duration: float, 
                          position: Tuple[int, int], size: Tuple[int, int]) -> VideoClip:
        """Criar clip de imagem"""
        # Abrir e redimensionar imagem
        img = Image.open(image_path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Converter para RGB se necessário
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Criar clip
        clip = ImageClip(np.array(img), duration=duration)
        clip = clip.set_position(position)
        
        # Adicionar fade in/out
        clip = clip.fadein(0.5).fadeout(0.5)
        
        return clip
    
    def _create_video_clip(self, video_path: str, duration: float,
                          position: Tuple[int, int], size: Tuple[int, int]) -> VideoClip:
        """Criar clip de vídeo"""
        # Carregar vídeo
        clip = VideoFileClip(video_path)
        
        # Ajustar duração
        if clip.duration > duration:
            clip = clip.subclip(0, duration)
        else:
            # Loop se o vídeo for menor que a duração necessária
            clip = clip.loop(duration=duration)
        
        # Redimensionar e posicionar
        clip = clip.resize(size)
        clip = clip.set_position(position)
        
        # Adicionar fade in/out
        clip = clip.fadein(0.5).fadeout(0.5)
        
        return clip
    
    def _create_text_clip(self, element: Dict[str, Any], duration: float, 
                         settings: Dict[str, Any]) -> VideoClip:
        """Criar clip de texto"""
        text = element.get("text", "Texto")
        position = (element.get("x", 100), element.get("y", 100))
        font_size = element.get("font_size", settings.get("font_size", 48))
        color = element.get("color", settings.get("text_color", "white"))
        font_family = element.get("font_family", settings.get("font_family", "Arial"))
        
        # Criar clip de texto
        txt_clip = TextClip(
            text,
            fontsize=font_size,
            color=color,
            font=font_family,
            stroke_color='black',
            stroke_width=2
        ).set_duration(duration).set_position(position)
        
        # Adicionar animação de entrada
        txt_clip = txt_clip.fadein(0.5).fadeout(0.5)
        
        return txt_clip
    
    def _create_title_clip(self, title: str, duration: float, settings: Dict[str, Any]) -> VideoClip:
        """Criar clip de título principal"""
        resolution = settings["resolution"]
        font_size = int(settings.get("font_size", 48) * 1.5)  # Título maior
        
        # Posição centralizada
        position = ("center", "center")
        
        txt_clip = TextClip(
            title,
            fontsize=font_size,
            color=settings.get("text_color", "white"),
            font=settings.get("font_family", "Arial"),
            stroke_color='black',
            stroke_width=3
        ).set_duration(duration).set_position(position)
        
        # Animação de entrada mais elaborada
        txt_clip = txt_clip.fadein(1.0).fadeout(1.0)
        
        return txt_clip
    
    def _combine_scenes_with_transitions(self, clips: List[VideoClip], 
                                       settings: Dict[str, Any]) -> VideoClip:
        """Combinar cenas com transições"""
        if len(clips) == 1:
            return clips[0]
        
        # Adicionar transições entre cenas
        transition_duration = 0.5
        final_clips = []
        
        for i, clip in enumerate(clips):
            if i > 0:
                # Crossfade entre cenas
                prev_clip = final_clips[-1]
                transition = CompositeVideoClip([
                    prev_clip.fadeout(transition_duration),
                    clip.fadein(transition_duration)
                ])
                final_clips[-1] = prev_clip.set_end(prev_clip.duration - transition_duration)
                final_clips.append(clip.set_start(transition_duration))
            else:
                final_clips.append(clip)
        
        return concatenate_videoclips(final_clips, method="compose")
    
    async def _process_audio_tracks(self, timeline: List[Dict[str, Any]], 
                                  total_duration: float) -> List[AudioClip]:
        """Processar trilhas de áudio"""
        audio_clips = []
        
        for track in timeline:
            if track.get("type") == "audio":
                audio_path = track.get("asset_path")
                if audio_path and os.path.exists(audio_path):
                    try:
                        audio_clip = AudioFileClip(audio_path)
                        
                        # Ajustar duração
                        start_time = track.get("start_time", 0)
                        if audio_clip.duration > total_duration - start_time:
                            audio_clip = audio_clip.subclip(0, total_duration - start_time)
                        
                        # Definir posição temporal
                        audio_clip = audio_clip.set_start(start_time)
                        
                        # Ajustar volume
                        volume = track.get("volume", 1.0)
                        if volume != 1.0:
                            audio_clip = audio_clip.volumex(volume)
                        
                        audio_clips.append(audio_clip)
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar áudio {audio_path}: {e}")
        
        return audio_clips
    
    async def _simulate_video_generation(self, project_data: Dict[str, Any], 
                                       export_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simular geração de vídeo quando MoviePy não está disponível"""
        logger.info("Simulando geração de vídeo (MoviePy não disponível)")
        
        # Simular tempo de processamento
        await asyncio.sleep(3)
        
        # Criar arquivo placeholder
        output_filename = f"project_simulation_{uuid.uuid4()}.mp4"
        output_path = self.output_dir / output_filename
        
        with open(output_path, "w") as f:
            f.write("Placeholder video file - MoviePy not available")
        
        scenes_count = len(project_data.get("scenes", []))
        estimated_duration = sum(scene.get("duration", 3) for scene in project_data.get("scenes", []))
        
        return {
            "success": True,
            "video_path": str(output_path),
            "video_url": f"/static/videos/{output_filename}",
            "duration": estimated_duration,
            "resolution": "1920x1080",
            "file_size": os.path.getsize(output_path),
            "created_at": datetime.now().isoformat(),
            "note": "Arquivo simulado - MoviePy não disponível"
        }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Obter formatos suportados"""
        return {
            "video_input": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
            "image_input": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "audio_input": [".mp3", ".wav", ".m4a", ".aac", ".ogg"],
            "video_output": [".mp4", ".avi", ".mov"],
            "audio_output": [".mp3", ".wav", ".aac"]
        }
    
    def validate_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar dados do projeto antes da geração"""
        errors = []
        warnings = []
        
        # Verificar cenas
        scenes = project_data.get("scenes", [])
        if not scenes:
            errors.append("Projeto deve ter pelo menos uma cena")
        
        # Verificar elementos de cada cena
        for i, scene in enumerate(scenes):
            if not scene.get("duration") or scene["duration"] <= 0:
                warnings.append(f"Cena {i+1} tem duração inválida")
            
            elements = scene.get("elements", [])
            for j, element in enumerate(elements):
                asset_path = element.get("asset_path")
                if asset_path and not os.path.exists(asset_path):
                    warnings.append(f"Asset não encontrado na cena {i+1}, elemento {j+1}: {asset_path}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# Instância global do serviço
video_service = VideoGenerationService()

# Funções de conveniência
async def generate_video(project_data: Dict[str, Any], export_settings: Dict[str, Any] = None):
    """Função de conveniência para gerar vídeo"""
    return await video_service.generate_video_from_project(project_data, export_settings)

def validate_project(project_data: Dict[str, Any]):
    """Função de conveniência para validar projeto"""
    return video_service.validate_project_data(project_data)

def get_supported_formats():
    """Função de conveniência para obter formatos suportados"""
    return video_service.get_supported_formats()