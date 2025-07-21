"""
Sistema de Geração de Vídeo Avatar - TecnoCursosAI
Gera vídeos educacionais com avatar virtual e slides sincronizados
"""

import asyncio
import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple
import logging

# Imports básicos
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# MoviePy imports (corrigidos)
try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip,
        concatenate_videoclips, CompositeAudioClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    print(f"Aviso: MoviePy não disponível: {e}")
    MOVIEPY_AVAILABLE = False

# Imports opcionais
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from services.tts_service import TTSService, TTSConfig, TTSProvider
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.config import get_settings
from app.logger import logger

settings = get_settings()

class AvatarStyle(Enum):
    """Estilos de avatar disponíveis"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TEACHER = "teacher"
    MINIMAL = "minimal"

class VideoQuality(Enum):
    """Qualidades de vídeo"""
    HD = "720p"
    FULL_HD = "1080p"
    ULTRA_HD = "4k"

@dataclass
class AvatarConfig:
    """Configurações do avatar"""
    style: AvatarStyle = AvatarStyle.PROFESSIONAL
    gender: str = "neutral"  # male, female, neutral
    skin_tone: str = "#fdbcb4"
    hair_color: str = "#8b4513"
    shirt_color: str = "#4a90e2"
    background_color: str = "#f0f0f0"
    enable_animation: bool = True
    enable_gestures: bool = True
    eye_blink: bool = True
    mouth_animation: bool = True

@dataclass
class VideoConfig:
    """Configurações do vídeo"""
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    quality: VideoQuality = VideoQuality.FULL_HD
    codec: str = "libx264"
    audio_codec: str = "aac"
    bitrate: str = "2000k"
    background_music: Optional[str] = None
    music_volume: float = 0.1
    fade_in_duration: float = 0.5
    fade_out_duration: float = 0.5

@dataclass
class SlideConfig:
    """Configurações dos slides"""
    template: str = "modern"
    font_family: str = "Arial"
    title_size: int = 48
    content_size: int = 32
    title_color: str = "#2c3e50"
    content_color: str = "#34495e"
    background_color: str = "#ffffff"
    accent_color: str = "#3498db"
    show_slide_numbers: bool = True
    transition_duration: float = 0.3

@dataclass
class VideoContent:
    """Conteúdo para geração do vídeo"""
    slides: List[Dict]  # Lista de slides com título e conteúdo
    audio_texts: List[str]  # Textos para narração
    background_images: List[str] = None  # Imagens de fundo opcionais
    metadata: Dict = None

class AvatarGenerator:
    """Gerador de avatar usando PIL"""
    
    def __init__(self, config: AvatarConfig):
        self.config = config
        self.avatar_size = (400, 600)  # Largura x Altura do avatar
        
    def create_base_avatar(self) -> Image.Image:
        """Cria avatar base"""
        width, height = self.avatar_size
        avatar = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(avatar)
        
        # Cabeça (círculo)
        head_center = (width // 2, height // 3)
        head_radius = 80
        
        # Rosto
        draw.ellipse(
            [head_center[0] - head_radius, head_center[1] - head_radius,
             head_center[0] + head_radius, head_center[1] + head_radius],
            fill=self.config.skin_tone,
            outline="#d4a574"
        )
        
        # Corpo (retângulo arredondado)
        body_top = head_center[1] + head_radius - 20
        body_width = 120
        body_height = 200
        
        draw.rectangle(
            [head_center[0] - body_width//2, body_top,
             head_center[0] + body_width//2, body_top + body_height],
            fill=self.config.shirt_color,
            outline="#2c3e50"
        )
        
        # Cabelo
        hair_points = [
            (head_center[0] - head_radius + 10, head_center[1] - head_radius + 20),
            (head_center[0], head_center[1] - head_radius - 10),
            (head_center[0] + head_radius - 10, head_center[1] - head_radius + 20)
        ]
        draw.polygon(hair_points, fill=self.config.hair_color)
        
        return avatar
    
    def add_facial_features(self, avatar: Image.Image, mouth_state: str = "neutral") -> Image.Image:
        """Adiciona características faciais"""
        draw = ImageDraw.Draw(avatar)
        width, height = self.avatar_size
        head_center = (width // 2, height // 3)
        
        # Olhos
        eye_y = head_center[1] - 20
        left_eye = (head_center[0] - 25, eye_y)
        right_eye = (head_center[0] + 25, eye_y)
        
        # Desenhar olhos
        eye_radius = 6
        draw.ellipse([left_eye[0] - eye_radius, left_eye[1] - eye_radius,
                     left_eye[0] + eye_radius, left_eye[1] + eye_radius],
                    fill="white", outline="black")
        draw.ellipse([right_eye[0] - eye_radius, right_eye[1] - eye_radius,
                     right_eye[0] + eye_radius, right_eye[1] + eye_radius],
                    fill="white", outline="black")
        
        # Pupilas
        pupil_radius = 3
        draw.ellipse([left_eye[0] - pupil_radius, left_eye[1] - pupil_radius,
                     left_eye[0] + pupil_radius, left_eye[1] + pupil_radius],
                    fill="black")
        draw.ellipse([right_eye[0] - pupil_radius, right_eye[1] - pupil_radius,
                     right_eye[0] + pupil_radius, right_eye[1] + pupil_radius],
                    fill="black")
        
        # Nariz
        nose_center = (head_center[0], head_center[1] + 5)
        draw.line([nose_center[0], nose_center[1], nose_center[0], nose_center[1] + 10], 
                 fill="#d4a574", width=2)
        
        # Boca baseada no estado
        mouth_center = (head_center[0], head_center[1] + 30)
        
        if mouth_state == "talking":
            # Boca aberta falando
            mouth_points = [
                (mouth_center[0] - 12, mouth_center[1] - 5),
                (mouth_center[0] + 12, mouth_center[1] - 5),
                (mouth_center[0] + 8, mouth_center[1] + 8),
                (mouth_center[0] - 8, mouth_center[1] + 8)
            ]
            draw.polygon(mouth_points, fill="#8b0000")
        elif mouth_state == "smiling":
            # Sorriso
            draw.arc([mouth_center[0] - 15, mouth_center[1] - 5,
                     mouth_center[0] + 15, mouth_center[1] + 10],
                    0, 180, fill="black", width=2)
        else:
            # Neutro
            draw.line([mouth_center[0] - 10, mouth_center[1],
                      mouth_center[0] + 10, mouth_center[1]],
                     fill="black", width=2)
        
        return avatar
    
    def create_animated_frames(self, audio_duration: float, fps: int = 30) -> List[Image.Image]:
        """Cria frames animados do avatar sincronizados com o áudio"""
        total_frames = int(audio_duration * fps)
        frames = []
        
        for frame_num in range(total_frames):
            time_pos = frame_num / fps
            
            # Criar avatar base
            avatar = self.create_base_avatar()
            
            # Determinar estado da boca baseado no tempo
            # Simula movimento de fala
            mouth_cycle = (time_pos * 4) % 1.0  # 4 ciclos por segundo
            
            if mouth_cycle < 0.3:
                mouth_state = "talking"
            elif mouth_cycle < 0.6:
                mouth_state = "neutral"
            else:
                mouth_state = "talking"
            
            # Piscar olhos ocasionalmente
            if frame_num % (fps * 3) == 0:  # Piscar a cada 3 segundos
                mouth_state = "neutral"  # Sincronizar com piscar
            
            # Adicionar características faciais
            avatar = self.add_facial_features(avatar, mouth_state)
            
            frames.append(avatar)
        
        return frames

class SlideGenerator:
    """Gerador de slides usando PIL"""
    
    def __init__(self, config: SlideConfig, resolution: Tuple[int, int] = (1920, 1080)):
        self.config = config
        self.resolution = resolution
        
    def create_slide(self, title: str, content: str, slide_number: int = 1) -> Image.Image:
        """Cria um slide com título e conteúdo"""
        width, height = self.resolution
        slide = Image.new('RGB', (width, height), self.config.background_color)
        draw = ImageDraw.Draw(slide)
        
        # Tentar carregar fonte personalizada
        try:
            title_font = ImageFont.truetype("arial.ttf", self.config.title_size)
            content_font = ImageFont.truetype("arial.ttf", self.config.content_size)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        # Área de conteúdo (lado direito - deixar espaço para avatar)
        content_x = width // 2 + 50
        content_width = width // 2 - 100
        
        # Título
        title_y = 150
        
        # Quebrar título em linhas se necessário
        title_lines = self._wrap_text(title, title_font, content_width, draw)
        for i, line in enumerate(title_lines):
            y_pos = title_y + (i * (self.config.title_size + 10))
            draw.text((content_x, y_pos), line, font=title_font, fill=self.config.title_color)
        
        # Conteúdo
        content_y = title_y + len(title_lines) * (self.config.title_size + 10) + 50
        
        # Quebrar conteúdo em linhas
        content_lines = self._wrap_text(content, content_font, content_width, draw)
        for i, line in enumerate(content_lines):
            y_pos = content_y + (i * (self.config.content_size + 5))
            if y_pos < height - 100:  # Verificar se cabe na tela
                draw.text((content_x, y_pos), line, font=content_font, fill=self.config.content_color)
        
        # Número do slide (se habilitado)
        if self.config.show_slide_numbers:
            slide_num_text = f"Slide {slide_number}"
            draw.text((width - 150, height - 50), slide_num_text, 
                     font=content_font, fill=self.config.accent_color)
        
        # Linha de separação
        draw.line([(content_x - 30, 100), (content_x - 30, height - 100)], 
                 fill=self.config.accent_color, width=3)
        
        return slide
    
    def _wrap_text(self, text: str, font, max_width: int, draw) -> List[str]:
        """Quebra texto em linhas para caber na largura especificada"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Palavra muito longa
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

class AvatarVideoGenerator:
    """Classe principal para geração de vídeos do avatar"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "avatar_video_generation"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configurações padrão
        self.avatar_config = AvatarConfig()
        self.video_config = VideoConfig()
        self.slide_config = SlideConfig()
        
        self.avatar_generator = AvatarGenerator(self.avatar_config)
        self.slide_generator = SlideGenerator(self.slide_config, self.video_config.resolution)
    
    async def generate_video(
        self,
        content: VideoContent,
        output_path: str,
        tts_config: Optional[TTSConfig] = None
    ) -> Dict:
        """
        Gera vídeo completo do avatar com áudio e slides
        
        Args:
            content: Conteúdo do vídeo (slides e textos)
            output_path: Caminho de saída do vídeo
            tts_config: Configurações do TTS
            
        Returns:
            Dict com informações do vídeo gerado
        """
        try:
            logger.info("🎬 Iniciando geração de vídeo do avatar...")
            
            # Configurar TTS se não fornecido
            if not tts_config:
                tts_config = TTSConfig(
                    provider=TTSProvider.AUTO,
                    language="pt",
                    voice="pt_speaker_0"
                )
            
            # 1. Gerar áudios para cada slide
            logger.info("🎤 Gerando narração com TTS...")
            audio_files = await self._generate_audio_narration(content.audio_texts, tts_config)
            
            # 2. Criar slides
            logger.info("📄 Gerando slides...")
            slide_images = self._create_slides(content.slides)
            
            # 3. Gerar clips de vídeo para cada slide
            logger.info("🎭 Gerando animações do avatar...")
            video_clips = []
            
            for i, (slide_img, audio_file) in enumerate(zip(slide_images, audio_files)):
                if not audio_file or not os.path.exists(audio_file):
                    logger.warning(f"Áudio não encontrado para slide {i+1}, pulando...")
                    continue
                
                # Carregar áudio para obter duração
                audio_clip = AudioFileClip(audio_file)
                duration = audio_clip.duration
                
                # Criar frames animados do avatar
                avatar_frames = self.avatar_generator.create_animated_frames(
                    duration, self.video_config.fps
                )
                
                # Combinar slide com avatar animado
                clip = await self._create_slide_clip(slide_img, avatar_frames, audio_clip, i + 1)
                video_clips.append(clip)
                
                logger.info(f"✅ Slide {i+1} processado - Duração: {duration:.2f}s")
            
            if not video_clips:
                raise ValueError("Nenhum clip de vídeo foi criado")
            
            # 4. Combinar todos os clips
            logger.info("🎬 Combinando clips finais...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # 5. Adicionar música de fundo se especificada
            if self.video_config.background_music:
                final_video = self._add_background_music(final_video)
            
            # 6. Exportar vídeo final
            logger.info(f"💾 Exportando vídeo para: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=self.video_config.fps,
                codec=self.video_config.codec,
                audio_codec=self.video_config.audio_codec,
                bitrate=self.video_config.bitrate,
                verbose=False,
                logger=None
            )
            
            # Limpar recursos
            for clip in video_clips:
                clip.close()
            final_video.close()
            
            # Calcular informações do vídeo
            video_info = {
                "success": True,
                "output_path": output_path,
                "duration": sum(clip.duration for clip in video_clips),
                "slides_count": len(content.slides),
                "resolution": f"{self.video_config.resolution[0]}x{self.video_config.resolution[1]}",
                "fps": self.video_config.fps,
                "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }
            
            logger.info(f"✅ Vídeo gerado com sucesso!")
            logger.info(f"   Duração: {video_info['duration']:.2f}s")
            logger.info(f"   Slides: {video_info['slides_count']}")
            logger.info(f"   Tamanho: {video_info['file_size'] / (1024*1024):.1f}MB")
            
            return video_info
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do vídeo: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": output_path
            }
    
    async def _generate_audio_narration(self, texts: List[str], tts_config: TTSConfig) -> List[str]:
        """Gera narração em áudio para os textos"""
        audio_files = []
        
        for i, text in enumerate(texts):
            try:
                audio_path = self.temp_dir / f"narration_{i}.mp3"
                
                # Usar o serviço TTS do sistema
                result = await tts_service.generate_speech(text, tts_config, str(audio_path))
                
                if result.success:
                    audio_files.append(result.audio_path)
                    logger.info(f"✅ Áudio {i+1} gerado: {result.duration:.2f}s")
                else:
                    logger.error(f"❌ Erro no áudio {i+1}: {result.error}")
                    # Criar áudio em branco como fallback
                    silence_path = await self._create_silence_audio(5.0, str(audio_path))
                    audio_files.append(silence_path)
                    
            except Exception as e:
                logger.error(f"Erro ao gerar áudio para texto {i+1}: {e}")
                audio_files.append("")
        
        return audio_files
    
    async def _create_silence_audio(self, duration: float, output_path: str) -> str:
        """Cria áudio em branco"""
        try:
            from pydub import AudioSegment
            silence = AudioSegment.silent(duration=int(duration * 1000))
            silence.export(output_path, format="mp3")
            return output_path
        except ImportError:
            logger.warning("Pydub não disponível para criar áudio em branco")
            return ""
    
    def _create_slides(self, slides_data: List[Dict]) -> List[str]:
        """Cria imagens dos slides"""
        slide_paths = []
        
        for i, slide_data in enumerate(slides_data):
            title = slide_data.get("title", f"Slide {i+1}")
            content = slide_data.get("content", "")
            
            # Gerar slide
            slide_img = self.slide_generator.create_slide(title, content, i + 1)
            
            # Salvar slide
            slide_path = self.temp_dir / f"slide_{i+1}.png"
            slide_img.save(str(slide_path), "PNG")
            slide_paths.append(str(slide_path))
        
        return slide_paths
    
    async def _create_slide_clip(
        self, 
        slide_path: str, 
        avatar_frames: List[Image.Image], 
        audio_clip: AudioFileClip,
        slide_number: int
    ) -> CompositeVideoClip:
        """Cria clip de vídeo combinando slide e avatar animado"""
        
        # Carregar slide como clip de fundo
        slide_clip = ImageClip(slide_path, duration=audio_clip.duration)
        
        # Criar clipe do avatar animado
        avatar_clip = await self._create_avatar_video_clip(avatar_frames, audio_clip.duration)
        
        # Posicionar avatar no lado esquerdo
        avatar_position = (50, (self.video_config.resolution[1] - self.avatar_generator.avatar_size[1]) // 2)
        avatar_clip = avatar_clip.set_position(avatar_position)
        
        # Combinar slide e avatar
        video_clip = CompositeVideoClip([slide_clip, avatar_clip])
        
        # Adicionar áudio
        final_clip = video_clip.set_audio(audio_clip)
        
        # Adicionar fade in/out
        if self.video_config.fade_in_duration > 0:
            final_clip = final_clip.fadein(self.video_config.fade_in_duration)
        if self.video_config.fade_out_duration > 0:
            final_clip = final_clip.fadeout(self.video_config.fade_out_duration)
        
        return final_clip
    
    async def _create_avatar_video_clip(self, frames: List[Image.Image], duration: float) -> VideoFileClip:
        """Cria clip de vídeo do avatar a partir dos frames"""
        
        # Salvar frames como imagens temporárias
        frame_paths = []
        for i, frame in enumerate(frames):
            frame_path = self.temp_dir / f"avatar_frame_{i:04d}.png"
            frame.save(str(frame_path), "PNG")
            frame_paths.append(str(frame_path))
        
        # Criar vídeo usando OpenCV
        avatar_video_path = self.temp_dir / "avatar_animation.mp4"
        
        # Configurar codec de vídeo
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        width, height = self.avatar_generator.avatar_size
        
        out = cv2.VideoWriter(
            str(avatar_video_path), 
            fourcc, 
            self.video_config.fps, 
            (width, height)
        )
        
        for frame_path in frame_paths:
            frame_cv = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
            
            # Converter RGBA para RGB se necessário
            if frame_cv.shape[2] == 4:
                # Criar fundo transparente
                rgb_frame = np.zeros((height, width, 3), dtype=np.uint8)
                alpha = frame_cv[:, :, 3] / 255.0
                
                for c in range(3):
                    rgb_frame[:, :, c] = (1 - alpha) * 255 + alpha * frame_cv[:, :, c]
                
                frame_cv = rgb_frame
            
            out.write(frame_cv)
        
        out.release()
        
        # Carregar como clip do MoviePy
        avatar_clip = VideoFileClip(str(avatar_video_path))
        
        return avatar_clip
    
    def _add_background_music(self, video_clip: CompositeVideoClip) -> CompositeVideoClip:
        """Adiciona música de fundo ao vídeo"""
        try:
            if os.path.exists(self.video_config.background_music):
                music_clip = AudioFileClip(self.video_config.background_music)
                
                # Ajustar duração da música
                if music_clip.duration < video_clip.duration:
                    # Repetir música se for menor que o vídeo
                    repeats = int(video_clip.duration / music_clip.duration) + 1
                    music_clip = concatenate_videoclips([music_clip] * repeats)
                
                # Cortar música para a duração do vídeo
                music_clip = music_clip.subclip(0, video_clip.duration)
                
                # Reduzir volume da música
                music_clip = music_clip.volumex(self.video_config.music_volume)
                
                # Combinar áudio original com música
                final_audio = CompositeAudioClip([video_clip.audio, music_clip])
                return video_clip.set_audio(final_audio)
                
        except Exception as e:
            logger.warning(f"Erro ao adicionar música de fundo: {e}")
        
        return video_clip
    
    def update_avatar_config(self, **kwargs):
        """Atualiza configurações do avatar"""
        for key, value in kwargs.items():
            if hasattr(self.avatar_config, key):
                setattr(self.avatar_config, key, value)
        
        # Recriar generator com nova configuração
        self.avatar_generator = AvatarGenerator(self.avatar_config)
    
    def update_video_config(self, **kwargs):
        """Atualiza configurações do vídeo"""
        for key, value in kwargs.items():
            if hasattr(self.video_config, key):
                setattr(self.video_config, key, value)
    
    def update_slide_config(self, **kwargs):
        """Atualiza configurações dos slides"""
        for key, value in kwargs.items():
            if hasattr(self.slide_config, key):
                setattr(self.slide_config, key, value)
        
        # Recriar generator com nova configuração
        self.slide_generator = SlideGenerator(self.slide_config, self.video_config.resolution)

# Função auxiliar para uso fácil
async def generate_avatar_video(
    slides: List[Dict],
    audio_texts: List[str],
    output_path: str,
    avatar_style: str = "professional",
    video_quality: str = "1080p"
) -> Dict:
    """
    Função simplificada para gerar vídeo do avatar
    
    Args:
        slides: Lista de dicts com 'title' e 'content'
        audio_texts: Lista de textos para narração
        output_path: Caminho de saída do vídeo
        avatar_style: Estilo do avatar (professional, friendly, teacher, minimal)
        video_quality: Qualidade do vídeo (720p, 1080p, 4k)
    
    Returns:
        Dict com resultado da geração
    """
    
    generator = AvatarVideoGenerator()
    
    # Configurar estilo do avatar
    if avatar_style in [e.value for e in AvatarStyle]:
        generator.update_avatar_config(style=AvatarStyle(avatar_style))
    
    # Configurar qualidade do vídeo
    if video_quality == "720p":
        generator.update_video_config(resolution=(1280, 720))
    elif video_quality == "1080p":
        generator.update_video_config(resolution=(1920, 1080))
    elif video_quality == "4k":
        generator.update_video_config(resolution=(3840, 2160))
    
    # Criar conteúdo
    content = VideoContent(
        slides=slides,
        audio_texts=audio_texts
    )
    
    # Gerar vídeo
    result = await generator.generate_video(content, output_path)
    
    return result

# Exemplo de uso
if __name__ == "__main__":
    async def exemplo_uso():
        """Exemplo de como usar o gerador de vídeo do avatar"""
        
        # Dados de exemplo
        slides_exemplo = [
            {
                "title": "Bem-vindos ao TecnoCursos AI",
                "content": "Neste curso você aprenderá sobre inteligência artificial e suas aplicações práticas no mundo real."
            },
            {
                "title": "O que é Inteligência Artificial?",
                "content": "IA é a capacidade de máquinas executarem tarefas que normalmente requerem inteligência humana, como reconhecimento de padrões e tomada de decisões."
            },
            {
                "title": "Aplicações Práticas",
                "content": "A IA está presente em assistentes virtuais, carros autônomos, diagnósticos médicos e muito mais."
            }
        ]
        
        textos_narracao = [
            "Olá! Seja bem-vindo ao nosso curso sobre inteligência artificial. Meu nome é Alex e eu serei seu instrutor nesta jornada de aprendizado.",
            "Vamos começar entendendo o que é inteligência artificial. De forma simples, é quando ensinamos computadores a pensar e resolver problemas como nós humanos.",
            "A inteligência artificial já faz parte do nosso dia a dia. Você a encontra no seu celular, no GPS do seu carro e até em recomendações de filmes na Netflix."
        ]
        
        # Gerar vídeo
        resultado = await generate_avatar_video(
            slides=slides_exemplo,
            audio_texts=textos_narracao,
            output_path="./exemplo_avatar_video.mp4",
            avatar_style="teacher",
            video_quality="1080p"
        )
        
        if resultado["success"]:
            print(f"✅ Vídeo gerado com sucesso!")
            print(f"   Arquivo: {resultado['output_path']}")
            print(f"   Duração: {resultado['duration']:.2f}s")
            print(f"   Tamanho: {resultado['file_size'] / (1024*1024):.1f}MB")
        else:
            print(f"❌ Erro na geração: {resultado['error']}")
    
    # Executar exemplo
    asyncio.run(exemplo_uso()) 