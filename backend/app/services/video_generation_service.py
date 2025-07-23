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
from dataclasses import dataclass

try:
    from moviepy.editor import VideoFileClip, ColorClip, TextClip
except ImportError:
    VideoFileClip = None
    ColorClip = None
    TextClip = None
    import logging
    logging.warning('MoviePy não disponível - funcionalidades de vídeo avançado desativadas.')

from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Imports locais
from ..models import Scene, Asset, Audio
from ..database import get_db
from sqlalchemy.orm import Session

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    VideoFileClip = None
    import logging
    logging.warning('MoviePy não disponível - funcionalidades de vídeo avançado desativadas.')

@dataclass
class VideoConfig:
    """Configurações padrão de vídeo"""
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    width: int = 1920
    height: int = 1080
    codec: str = "libx264"
    audio_codec: str = "aac"
    bitrate: str = "2000k"

# Configurar logger
logger = logging.getLogger(__name__)

@dataclass
class SceneVideoData:
    """Estrutura de dados para representar uma cena de vídeo"""
    scene_id: int
    name: str
    duration: float
    text_content: str
    background_config: Dict[str, Any]
    assets: List[Dict[str, Any]]
    style_preset: str = "modern"
    order: int = 0

class VideoGenerationService:
    """
    Serviço principal de geração de vídeo com IA
    
    Funcionalidades:
    - Geração de vídeos a partir de cenas do projeto
    - Integração com IA para narração e avatares
    - Composição automática com MoviePy
    - Export otimizado em diferentes qualidades
    - Cache de assets processados
    """
    
    def __init__(self):
        self.config = VideoConfig()
        self.output_dir = Path("app/static/videos/generated")
        self.temp_dir = Path("temp/video_generation")
        self.assets_dir = Path("app/static")
        
        # Criar diretórios necessários
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Verificar dependências
        self._check_dependencies()
        
        logger.info("🎬 Video Generation Service inicializado")
    
    def _check_dependencies(self):
        """Verificar dependências necessárias"""
        status = {
            "moviepy": VideoFileClip is not None,
        }
        
        if not VideoFileClip:
            logger.warning("⚠️ MoviePy não disponível - funcionalidade limitada")
        else:
            logger.info("✅ MoviePy disponível")
        
        logger.info(f"📊 Status dependências: {status}")
    
    async def generate_project_video(
        self, 
        project_id: int, 
        user_id: int,
        quality: str = "high",
        include_avatar: bool = True,
        include_narration: bool = True
    ) -> Dict[str, Any]:
        """
        Gerar vídeo completo do projeto
        
        Args:
            project_id: ID do projeto
            user_id: ID do usuário
            quality: Qualidade do vídeo (low, medium, high, ultra)
            include_avatar: Incluir avatar nas cenas
            include_narration: Incluir narração por IA
        
        Returns:
            Dict com informações do vídeo gerado
        """
        if not VideoFileClip:
            raise Exception("MoviePy não disponível")
        
        logger.info(f"🎬 Iniciando geração de vídeo: projeto {project_id}")
        
        try:
            # 1. Buscar dados do projeto e cenas
            scenes_data = await self._fetch_project_scenes(project_id, user_id)
            
            if not scenes_data:
                raise Exception("Nenhuma cena encontrada no projeto")
            
            # 2. Configurar qualidade
            self._set_quality_config(quality)
            
            # 3. Processar cada cena individual
            scene_clips = []
            total_duration = 0
            
            for i, scene_data in enumerate(scenes_data):
                logger.info(f"🎭 Processando cena {i+1}/{len(scenes_data)}: {scene_data.name}")
                
                # Gerar clipe da cena
                scene_clip = await self._generate_scene_clip(
                    scene_data, 
                    include_avatar, 
                    include_narration
                )
                
                if scene_clip:
                    scene_clips.append(scene_clip)
                    total_duration += scene_clip.duration
                    logger.info(f"✅ Cena processada: {scene_clip.duration:.2f}s")
            
            if not scene_clips:
                raise Exception("Nenhuma cena foi processada com sucesso")
            
            # 4. Concatenar cenas com transições
            logger.info("🔗 Concatenando cenas com transições")
            final_video = self._concatenate_scenes_with_transitions(scene_clips)
            
            # 5. Adicionar elementos globais (intro, outro, watermark)
            final_video = await self._add_global_elements(final_video, project_id)
            
            # 6. Exportar vídeo final
            video_filename = f"project_{project_id}_{uuid.uuid4().hex[:8]}.mp4"
            video_path = self.output_dir / video_filename
            
            logger.info(f"📹 Exportando vídeo final: {video_path}")
            await self._export_video(final_video, video_path)
            
            # 7. Limpar arquivos temporários
            self._cleanup_temp_files()
            
            # 8. Retornar informações do vídeo
            video_info = {
                "success": True,
                "video_path": str(video_path),
                "video_url": f"/static/videos/generated/{video_filename}",
                "filename": video_filename,
                "duration": total_duration,
                "scenes_count": len(scenes_data),
                "quality": quality,
                "file_size": video_path.stat().st_size if video_path.exists() else 0,
                "created_at": datetime.utcnow().isoformat(),
                "config": {
                    "width": self.config.width,
                    "height": self.config.height,
                    "fps": self.config.fps,
                    "include_avatar": include_avatar,
                    "include_narration": include_narration
                }
            }
            
            logger.info(f"✅ Vídeo gerado com sucesso: {video_filename}")
            return video_info
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de vídeo: {e}")
            self._cleanup_temp_files()
            return {
                "success": False,
                "error": str(e),
                "video_path": None,
                "video_url": None
            }
    
    async def _fetch_project_scenes(self, project_id: int, user_id: int) -> List[SceneVideoData]:
        """
        Buscar cenas do projeto no banco de dados
        
        Args:
            project_id: ID do projeto
            user_id: ID do usuário
        
        Returns:
            Lista de dados das cenas para vídeo
        """
        if not DATABASE_AVAILABLE:
            # Dados mock para desenvolvimento
            return self._get_mock_scenes_data()
        
        try:
            db = get_db_session()
            
            # Buscar projeto e verificar permissões
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.owner_id == user_id
            ).first()
            
            if not project:
                raise Exception("Projeto não encontrado ou sem permissão")
            
            # Buscar cenas ordenadas
            scenes = db.query(Scene).filter(
                Scene.project_id == project_id,
                Scene.is_active == True
            ).order_by(Scene.ordem, Scene.created_at).all()
            
            scenes_data = []
            
            for scene in scenes:
                # Buscar assets da cena
                assets = db.query(Asset).filter(
                    Asset.scene_id == scene.id,
                    Asset.is_active == True
                ).order_by(Asset.camada, Asset.created_at).all()
                
                # Converter assets para dict
                assets_data = []
                for asset in assets:
                    assets_data.append({
                        "id": asset.id,
                        "name": asset.name,
                        "tipo": asset.tipo,
                        "arquivo_path": asset.arquivo_path,
                        "posicao_x": asset.posicao_x or 0,
                        "posicao_y": asset.posicao_y or 0,
                        "escala": asset.escala or 1.0,
                        "rotacao": asset.rotacao or 0,
                        "opacidade": asset.opacidade or 1.0,
                        "camada": asset.camada or 0,
                        "timeline_start": asset.timeline_start or 0,
                        "timeline_end": asset.timeline_end or scene.duracao
                    })
                
                # Configuração de background
                background_config = {
                    "color": scene.background_color or "#ffffff",
                    "type": getattr(scene, 'background_type', 'solid'),
                    "asset_id": getattr(scene, 'background_asset_id', None)
                }
                
                # Criar SceneVideoData a partir da scene do banco
                scene_data = SceneVideoData(
                    scene_id=scene.id,
                    name=scene.name,
                    duration=scene.duracao or 5.0,
                    text_content=scene.texto or "",
                    background_config=background_config,
                    assets=assets_data,
                    style_preset=scene.style_preset or "modern",
                    order=scene.ordem or 0
                )
                
                scenes_data.append(scene_data)
            
            db.close()
            return scenes_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cenas: {e}")
            if 'db' in locals():
                db.close()
            raise
    
    def _get_mock_scenes_data(self) -> List[SceneVideoData]:
        """Dados mock para desenvolvimento quando banco não disponível"""
        return [
            SceneVideoData(
                scene_id=1,
                name="Introdução",
                duration=5.0,
                text_content="Bem-vindos ao nosso curso",
                background_config={"color": "#4a90e2", "type": "solid"},
                assets=[],
                style_preset="modern"
            ),
            SceneVideoData(
                scene_id=2,
                name="Conteúdo Principal",
                duration=8.0,
                text_content="Vamos aprender sobre tecnologia",
                background_config={"color": "#f39c12", "type": "solid"},
                assets=[],
                style_preset="corporate"
            )
        ]
    
    def _set_quality_config(self, quality: str):
        """Configurar qualidade do vídeo"""
        quality_configs = {
            "low": {"width": 854, "height": 480, "fps": 24},
            "medium": {"width": 1280, "height": 720, "fps": 30},
            "high": {"width": 1920, "height": 1080, "fps": 30},
            "ultra": {"width": 3840, "height": 2160, "fps": 60}
        }
        
        if quality in quality_configs:
            config = quality_configs[quality]
            self.config.width = config["width"]
            self.config.height = config["height"]
            self.config.fps = config["fps"]
            
        logger.info(f"📺 Qualidade configurada: {quality} ({self.config.width}x{self.config.height}@{self.config.fps}fps)")
    
    async def _generate_scene_clip(
        self, 
        scene_data: SceneVideoData,
        include_avatar: bool,
        include_narration: bool
    ) -> Optional[VideoFileClip]:
        """
        Gerar clipe de vídeo para uma cena individual
        
        Args:
            scene_data: Dados da cena
            include_avatar: Incluir avatar
            include_narration: Incluir narração
        
        Returns:
            Clipe de vídeo da cena ou None se erro
        """
        try:
            clips = []
            
            # 1. Background da cena
            background_clip = self._create_background_clip(scene_data)
            clips.append(background_clip)
            
            # 2. Assets da cena (imagens, vídeos, etc.)
            for asset_data in scene_data.assets:
                asset_clip = self._create_asset_clip(asset_data, scene_data.duration)
                if asset_clip:
                    clips.append(asset_clip)
            
            # 3. Texto da cena
            if scene_data.text_content:
                text_clip = self._create_text_clip(scene_data)
                if text_clip:
                    clips.append(text_clip)
            
            # 4. Avatar (se habilitado)
            if include_avatar:
                avatar_clip = await self._create_avatar_clip(scene_data)
                if avatar_clip:
                    clips.append(avatar_clip)
            
            # 5. Narração (se habilitado)
            audio_clip = None
            if include_narration and scene_data.text_content:
                audio_clip = await self._generate_narration(scene_data)
            
            # 6. Compor cena final
            if clips:
                scene_clip = CompositeVideoClip(
                    clips, 
                    size=(self.config.width, self.config.height)
                ).set_duration(scene_data.duration)
                
                # Adicionar áudio se disponível
                if audio_clip:
                    scene_clip = scene_clip.set_audio(audio_clip)
                
                return scene_clip
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar clipe da cena {scene_data.scene_id}: {e}")
            return None
    
    def _create_background_clip(self, scene_data: SceneVideoData) -> ColorClip:
        """
        Criar background da cena
        
        Args:
            scene_data: Dados da cena
        
        Returns:
            Clipe de background
        """
        bg_config = scene_data.background_config
        
        # Por enquanto, usar cor sólida
        # TODO: Integrar com IA para gerar backgrounds dinâmicos
        background_color = bg_config.get("color", "#ffffff")
        
        return ColorClip(
            size=(self.config.width, self.config.height),
            color=background_color,
            duration=scene_data.duration
        )
    
    def _create_asset_clip(self, asset_data: Dict[str, Any], scene_duration: float):
        """
        Criar clipe para um asset
        
        Args:
            asset_data: Dados do asset
            scene_duration: Duração da cena
        
        Returns:
            Clipe do asset ou None
        """
        try:
            asset_path = Path(self.assets_dir) / asset_data.get("arquivo_path", "")
            
            if not asset_path.exists():
                logger.warning(f"⚠️ Asset não encontrado: {asset_path}")
                return None
            
            asset_type = asset_data.get("tipo", "").lower()
            
            # Timeline do asset
            start_time = asset_data.get("timeline_start", 0)
            end_time = asset_data.get("timeline_end", scene_duration)
            duration = min(end_time - start_time, scene_duration - start_time)
            
            if duration <= 0:
                return None
            
            # Posição e transformações
            pos_x = asset_data.get("posicao_x", 0)
            pos_y = asset_data.get("posicao_y", 0)
            scale = asset_data.get("escala", 1.0)
            rotation = asset_data.get("rotacao", 0)
            opacity = asset_data.get("opacidade", 1.0)
            
            if asset_type in ["image", "imagem"]:
                clip = ImageClip(str(asset_path))
                clip = clip.set_duration(duration)
                
            elif asset_type in ["video", "vídeo"]:
                clip = VideoFileClip(str(asset_path))
                clip = clip.subclip(0, min(clip.duration, duration))
                
            else:
                logger.warning(f"⚠️ Tipo de asset não suportado: {asset_type}")
                return None
            
            # Aplicar transformações
            if scale != 1.0:
                clip = clip.resize(scale)
            
            if rotation != 0:
                clip = clip.rotate(rotation)
            
            if opacity != 1.0:
                clip = clip.set_opacity(opacity)
            
            # Posicionar
            clip = clip.set_position((pos_x, pos_y))
            clip = clip.set_start(start_time)
            
            return clip
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar clipe do asset: {e}")
            return None
    
    def _create_text_clip(self, scene_data: SceneVideoData) -> Optional[Any]:
        if TextClip is None:
            return None
        try:
            # Configurações de texto baseadas no estilo
            text_configs = {
                "modern": {
                    "fontsize": 48,
                    "color": "white",
                    "font": "Arial-Bold",
                    "stroke_color": "black",
                    "stroke_width": 2
                },
                "corporate": {
                    "fontsize": 42,
                    "color": "#2c3e50",
                    "font": "Arial",
                    "stroke_color": None,
                    "stroke_width": 0
                },
                "tech": {
                    "fontsize": 52,
                    "color": "#00ff00",
                    "font": "Courier-Bold",
                    "stroke_color": "#003300",
                    "stroke_width": 1
                }
            }
            
            config = text_configs.get(scene_data.style_preset, text_configs["modern"])
            
            text_clip = TextClip(
                scene_data.text_content,
                fontsize=config["fontsize"],
                color=config["color"],
                font=config["font"],
                stroke_color=config["stroke_color"],
                stroke_width=config["stroke_width"]
            ).set_duration(scene_data.duration)
            
            # Posicionar texto (centro-inferior por padrão)
            text_clip = text_clip.set_position(("center", "bottom")).set_margin(50)
            
            return text_clip
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar clipe de texto: {e}")
            return None
    
    async def _create_avatar_clip(self, scene_data: SceneVideoData):
        """
        Criar clipe de avatar usando IA
        
        Args:
            scene_data: Dados da cena
        
        Returns:
            Clipe de avatar ou None
        
        TODO: Integrar com serviços de IA para geração de avatar
        - D-ID para avatar falante
        - HeyGen para apresentador virtual
        - Synthesia para avatar customizado
        - RunwayML para animação de personagem
        """
        try:
            # TODO: Implementar integração com IA de avatar
            
            # Por enquanto, retornar placeholder
            placeholder_path = self.assets_dir / "images" / "avatar_placeholder.png"
            
            if placeholder_path.exists():
                avatar_clip = ImageClip(str(placeholder_path))
                avatar_clip = avatar_clip.set_duration(scene_data.duration)
                avatar_clip = avatar_clip.resize(self.config.avatar_size)
                avatar_clip = avatar_clip.set_position(("right", "center"))
                
                logger.info("🤖 Avatar placeholder adicionado")
                return avatar_clip
            
            logger.info("🤖 Avatar não disponível - implementar integração com IA")
            return None
            
            # Exemplo de integração futura:
            """
            if AI_D_ID_AVAILABLE:
                # Gerar avatar falante com D-ID
                avatar_video = await generate_d_id_avatar(
                    text=scene_data.text_content,
                    presenter_id="amy-jcwCkr1grs",
                    voice_id="microsoft"
                )
                return VideoFileClip(avatar_video)
            """
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar avatar: {e}")
            return None
    
    async def _generate_narration(self, scene_data: SceneVideoData):
        """
        Gerar narração usando IA
        
        Args:
            scene_data: Dados da cena
        
        Returns:
            Clipe de áudio ou None
        
        TODO: Integrar com serviços de TTS/IA
        - Azure Cognitive Services Speech
        - OpenAI TTS
        - Google Cloud Text-to-Speech
        - ElevenLabs para vozes naturais
        """
        try:
            # TODO: Implementar integração com TTS
            
            audio_filename = f"narration_{scene_data.scene_id}_{uuid.uuid4().hex[:8]}.wav"
            audio_path = self.temp_dir / audio_filename
            
            # Exemplo de integração futura com Azure TTS:
            if AI_AZURE_TTS_AVAILABLE:
                """
                speech_config = speechsdk.SpeechConfig(
                    subscription=AZURE_SPEECH_KEY, 
                    region=AZURE_SPEECH_REGION
                )
                speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"
                
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=speech_config,
                    audio_config=speechsdk.audio.AudioOutputConfig(filename=str(audio_path))
                )
                
                result = synthesizer.speak_text_async(scene_data.text_content).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return AudioFileClip(str(audio_path))
                """
                
            # Por enquanto, retornar None
            logger.info("🎵 Narração não disponível - implementar integração com TTS")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar narração: {e}")
            return None
    
    def _concatenate_scenes_with_transitions(self, scene_clips: List[VideoFileClip]) -> VideoFileClip:
        """
        Concatenar cenas com transições suaves
        
        Args:
            scene_clips: Lista de clipes das cenas
        
        Returns:
            Vídeo final concatenado
        """
        if len(scene_clips) == 1:
            return scene_clips[0]
        
        try:
            # Aplicar transições entre cenas
            final_clips = [scene_clips[0]]
            
            for i in range(1, len(scene_clips)):
                # Transição fade
                previous_clip = final_clips[-1]
                current_clip = scene_clips[i]
                
                # Fade out no final da cena anterior
                previous_clip = previous_clip.fadeout(self.config.transition_duration)
                final_clips[-1] = previous_clip
                
                # Fade in no início da cena atual
                current_clip = current_clip.fadein(self.config.transition_duration)
                final_clips.append(current_clip)
            
            # Concatenar todos os clipes
            final_video = concatenate_videoclips(final_clips, method="compose")
            
            logger.info(f"🔗 {len(scene_clips)} cenas concatenadas com transições")
            return final_video
            
        except Exception as e:
            logger.error(f"❌ Erro na concatenação: {e}")
            # Fallback: concatenação simples sem transições
            return concatenate_videoclips(scene_clips)
    
    async def _add_global_elements(self, video: VideoFileClip, project_id: int) -> VideoFileClip:
        """
        Adicionar elementos globais ao vídeo
        
        Args:
            video: Vídeo base
            project_id: ID do projeto
        
        Returns:
            Vídeo com elementos globais
        
        TODO: Adicionar elementos como:
        - Intro/outro automático
        - Watermark/logo
        - Música de fundo
        - Créditos finais
        """
        try:
            # TODO: Implementar intro/outro
            
            # Por enquanto, retornar vídeo original
            logger.info("🎬 Elementos globais não implementados")
            return video
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar elementos globais: {e}")
            return video
    
    async def _export_video(self, video: VideoFileClip, output_path: Path):
        """
        Exportar vídeo final
        
        Args:
            video: Vídeo para exportar
            output_path: Caminho de saída
        """
        try:
            # Configurações de export baseadas na qualidade
            codec_configs = {
                "low": {"codec": "libx264", "bitrate": "1000k"},
                "medium": {"codec": "libx264", "bitrate": "2500k"},
                "high": {"codec": "libx264", "bitrate": "5000k"},
                "ultra": {"codec": "libx264", "bitrate": "10000k"}
            }
            
            config = codec_configs.get(self.config.quality, codec_configs["high"])
            
            # Exportar vídeo
            video.write_videofile(
                str(output_path),
                fps=self.config.fps,
                codec=config["codec"],
                bitrate=config["bitrate"],
                audio_codec="aac",
                temp_audiofile=str(self.temp_dir / "temp_audio.m4a"),
                remove_temp=True,
                verbose=False,
                logger=None  # Suprimir logs do MoviePy
            )
            
            logger.info(f"✅ Vídeo exportado: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro no export: {e}")
            raise
    
    def _cleanup_temp_files(self):
        """Limpar arquivos temporários"""
        try:
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    temp_file.unlink()
            
            logger.info("🧹 Arquivos temporários limpos")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na limpeza: {e}")

# ============================================================================
# INSTÂNCIA GLOBAL DO SERVIÇO
# ============================================================================

# Instância singleton do serviço de geração de vídeo
video_generation_service = VideoGenerationService()

# Funções de conveniência
async def generate_project_video(
    project_id: int, 
    user_id: int, 
    quality: str = "high",
    include_avatar: bool = True,
    include_narration: bool = True
) -> Dict[str, Any]:
    """
    Função de conveniência para gerar vídeo do projeto
    
    Args:
        project_id: ID do projeto
        user_id: ID do usuário
        quality: Qualidade do vídeo
        include_avatar: Incluir avatar
        include_narration: Incluir narração
    
    Returns:
        Informações do vídeo gerado
    """
    return await video_generation_service.generate_project_video(
        project_id=project_id,
        user_id=user_id,
        quality=quality,
        include_avatar=include_avatar,
        include_narration=include_narration
    ) 