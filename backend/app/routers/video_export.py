#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router para Exportação de Vídeo Final - TecnoCursos AI

Este módulo implementa endpoints REST para exportação completa de vídeos
com integração de TTS, avatar e montagem usando MoviePy.

Funcionalidades:
- Geração de áudio TTS com Hugging Face Bark
- Integração com avatar Hunyuan3D-2 (simulação no MVP)
- Montagem de vídeo com MoviePy
- Transições entre cenas
- Efeitos visuais e animações
- Download do vídeo final

Autor: TecnoCursos AI
Data: 17/01/2025
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import os
import time
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
import json
import logging
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Project, Scene, Asset
from app.services.video_pipeline_service import export_project_video_with_ia
import smtplib
from email.mime.text import MIMEText

# Importar funções de geração de vídeo e TTS
try:
    from app.utils import (
        generate_narration,
        generate_avatar_video,
        create_video_from_text_and_audio
    )
    VIDEO_FUNCTIONS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Funções de vídeo não disponíveis: {e}")
    VIDEO_FUNCTIONS_AVAILABLE = False

# Importar serviços TTS
try:
    from backend.services.tts_service import TTSConfig, TTSProvider
except ImportError:
    print("⚠️ Serviço TTS não disponível para video_export")
    # Definir TTSConfig localmente se não estiver disponível
    class TTSConfig:
        def __init__(self, **kwargs):
            pass
    TTSProvider = None

# Importar dependências do sistema
try:
    from app.auth import get_current_user
    from app.models import User
    from app.database import get_db
    AUTH_AVAILABLE = True
except ImportError:
    print("⚠️ Sistema de autenticação não disponível")
    AUTH_AVAILABLE = False

# Importar MoviePy para montagem de vídeo
try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip, TextClip, CompositeAudioClip
    )
    from moviepy.video.fx import resize, fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    VideoFileClip = None
    AudioFileClip = None
    ImageClip = None
    ColorClip = None
    TextClip = None
    CompositeVideoClip = None
    concatenate_videoclips = None
    CompositeAudioClip = None
    import logging
    logging.warning('MoviePy não disponível - funcionalidades de vídeo avançado desativadas.')
    MOVIEPY_AVAILABLE = False

# Configurar router
router = APIRouter(
    prefix="/api/video-export",
    tags=["Video Export"],
    responses={
        404: {"description": "Video not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# Configurar logger
logger = logging.getLogger(__name__)

# ===============================================================
# MODELOS PYDANTIC PARA REQUESTS/RESPONSES
# ===============================================================

class SceneElement(BaseModel):
    """Elemento de uma cena (texto, imagem, áudio)"""
    type: str = Field(..., description="Tipo do elemento: text, image, audio, avatar")
    content: str = Field(..., description="Conteúdo do elemento")
    duration: float = Field(default=3.0, description="Duração em segundos")
    position: Dict[str, float] = Field(default={"x": 0.5, "y": 0.5}, description="Posição na tela")
    size: Dict[str, float] = Field(default={"width": 0.8, "height": 0.6}, description="Tamanho relativo")
    animation: Optional[str] = Field(default=None, description="Tipo de animação")
    style: Optional[Dict[str, Any]] = Field(default=None, description="Estilo visual")

class Scene(BaseModel):
    """Configuração de uma cena"""
    id: str = Field(..., description="ID único da cena")
    title: str = Field(..., description="Título da cena")
    duration: float = Field(default=5.0, description="Duração total da cena")
    background: Optional[str] = Field(default=None, description="Imagem de fundo")
    elements: List[SceneElement] = Field(default=[], description="Elementos da cena")
    transition: Optional[str] = Field(default="fade", description="Transição para próxima cena")
    tts_enabled: bool = Field(default=True, description="Se deve gerar TTS para texto")
    avatar_enabled: bool = Field(default=False, description="Se deve usar avatar")
    avatar_style: Optional[str] = Field(default="professional", description="Estilo do avatar")

class VideoExportRequest(BaseModel):
    """Request para exportação de vídeo"""
    title: str = Field(..., description="Título do vídeo")
    description: Optional[str] = Field(default=None, description="Descrição do vídeo")
    scenes: List[Scene] = Field(..., description="Lista de cenas")
    resolution: str = Field(default="1080p", description="Resolução: 720p, 1080p, 4k")
    fps: int = Field(default=30, description="Frames por segundo")
    tts_voice: str = Field(default="pt_speaker_0", description="Voz para TTS")
    tts_provider: str = Field(default="auto", description="Provider TTS: auto, bark, gtts")
    background_music: Optional[str] = Field(default=None, description="Música de fundo")
    output_format: str = Field(default="mp4", description="Formato de saída")
    quality: str = Field(default="high", description="Qualidade: low, medium, high, ultra")

class VideoExportResponse(BaseModel):
    """Response da exportação de vídeo"""
    success: bool
    video_id: str
    message: str
    data: Dict[str, Any]

class VideoStatusResponse(BaseModel):
    """Status do processamento de vídeo"""
    video_id: str
    status: str  # queued, processing, completed, failed
    progress: float
    current_stage: str
    estimated_time: Optional[int] = None
    error_message: Optional[str] = None
    video_url: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None

# ===============================================================
# VARIÁVEIS GLOBAIS E CONFIGURAÇÕES
# ===============================================================

# Armazenamento temporário de jobs (em produção usar Redis)
video_jobs = {}

# Configurações de resolução
RESOLUTION_CONFIGS = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160)
}

# Configurações de qualidade
QUALITY_CONFIGS = {
    "low": {"bitrate": "1000k", "crf": 28},
    "medium": {"bitrate": "2000k", "crf": 23},
    "high": {"bitrate": "4000k", "crf": 18},
    "ultra": {"bitrate": "8000k", "crf": 15}
}

# ===============================================================
# FUNÇÕES AUXILIARES
# ===============================================================

def create_text_clip(text: str, duration: float, resolution: tuple, style: Dict = None) -> Optional[Any]:
    """Cria clip de texto com MoviePy"""
    try:
        # Configurações padrão
        default_style = {
            "fontsize": 48,
            "color": "white",
            "font": "Arial-Bold",
            "stroke_color": "black",
            "stroke_width": 2
        }

        if style:
            default_style.update(style)

        # Criar clip de texto
        txt_clip = TextClip(
            text,
            fontsize=default_style["fontsize"],
            color=default_style["color"],
            font=default_style["font"],
            stroke_color=default_style["stroke_color"],
            stroke_width=default_style["stroke_width"]
        )

        # Centralizar na tela
        txt_clip = txt_clip.set_position('center').set_duration(duration)

        return txt_clip

    except Exception as e:
        logger.error(f"Erro ao criar clip de texto: {e}")
        # Fallback: clip simples
        return TextClip(text, fontsize=36, color='white').set_position('center').set_duration(duration)

def create_image_clip(image_path: str, duration: float, resolution: tuple) -> Optional[Any]:
    if ImageClip is None:
        return None
    """Cria clip de imagem com MoviePy"""
    try:
        # Verificar se arquivo existe
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

        # Criar clip de imagem
        img_clip = ImageClip(image_path)

        # Redimensionar para resolução desejada
        img_clip = img_clip.resize(resolution)

        # Definir duração
        img_clip = img_clip.set_duration(duration)

        return img_clip

    except Exception as e:
        logger.error(f"Erro ao criar clip de imagem: {e}")
        # Fallback: clip colorido
        return ColorClip(resolution, color=(100, 100, 100)).set_duration(duration)

def create_audio_clip(audio_path: str) -> AudioFileClip:
    """Cria clip de áudio com MoviePy"""
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")

        return AudioFileClip(audio_path)

    except Exception as e:
        logger.error(f"Erro ao criar clip de áudio: {e}")
        return None

def add_transition(clip1, clip2, transition_type: str = "fade"):
    """Adiciona transição entre clips"""
    try:
        if transition_type == "fade":
            # Fade out no primeiro clip
            clip1 = clip1.fadeout(0.5)
            # Fade in no segundo clip
            clip2 = clip2.fadein(0.5)
        elif transition_type == "slide":
            # Slide transition (implementação básica)
            clip1 = clip1.fadeout(0.3)
            clip2 = clip2.fadein(0.3)
        elif transition_type == "zoom":
            # Zoom transition
            clip1 = clip1.fadeout(0.4)
            clip2 = clip2.fadein(0.4)

        return clip1, clip2

    except Exception as e:
        logger.error(f"Erro ao adicionar transição: {e}")
        return clip1, clip2

async def generate_tts_for_scene(scene: Scene, tts_config: TTSConfig) -> Dict[str, str]:
    """Gera áudio TTS para elementos de texto da cena"""
    audio_files = {}

    if not TTSProvider:
        logger.warning("TTS não disponível, pulando geração de áudio")
        return audio_files

    try:
        tts_service = TTSService()

        for element in scene.elements:
            if element.type == "text" and scene.tts_enabled:
                # Gerar áudio para texto
                text_content = element.content

                # Criar nome único para arquivo
                audio_filename = f"tts_{scene.id}_{hash(text_content) % 100000}.mp3"
                audio_path = f"app/static/audios/{audio_filename}"

                # Garantir que diretório existe
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)

                # Gerar áudio
                result = await tts_service.generate_speech(text_content, tts_config, audio_path)

                if result.success:
                    audio_files[element.content] = audio_path
                    logger.info(f"✅ Áudio TTS gerado: {audio_path}")
                else:
                    logger.error(f"❌ Erro ao gerar TTS: {result.error}")

        return audio_files

    except Exception as e:
        logger.error(f"Erro na geração TTS: {e}")
        return audio_files

async def generate_avatar_for_scene(scene: Scene, audio_files: Dict[str, str]) -> Dict[str, str]:
    """Gera vídeos de avatar para cenas que habilitaram avatar"""
    avatar_files = {}

    if not scene.avatar_enabled:
        return avatar_files

    try:
        for element in scene.elements:
            if element.type == "text" and element.content in audio_files:
                # Gerar avatar para este texto
                audio_path = audio_files[element.content]

                # Nome único para vídeo do avatar
                avatar_filename = f"avatar_{scene.id}_{hash(element.content) % 100000}.mp4"
                avatar_path = f"app/static/videos/avatars/{avatar_filename}"

                # Garantir que diretório existe
                os.makedirs(os.path.dirname(avatar_path), exist_ok=True)

                # Gerar vídeo do avatar
                result = generate_avatar_video(
                    text=element.content,
                    audio_path=audio_path,
                    output_path=avatar_path,
                    avatar_style=scene.avatar_style or "professional",
                    quality="high"
                )

                if result['success']:
                    avatar_files[element.content] = avatar_path
                    logger.info(f"✅ Avatar gerado: {avatar_path}")
                else:
                    logger.error(f"❌ Erro ao gerar avatar: {result['error']}")

        return avatar_files

    except Exception as e:
        logger.error(f"Erro na geração de avatar: {e}")
        return avatar_files

def create_scene_clip(scene: Scene, audio_files: Dict[str, str], avatar_files: Dict[str, str],
                     resolution: tuple, fps: int) -> VideoFileClip:
    """Cria clip completo de uma cena"""
    try:
        clips = []
        audio_clips = []

        # Processar elementos da cena
        for element in scene.elements:
            if element.type == "text":
                # Criar clip de texto
                text_clip = create_text_clip(
                    element.content,
                    element.duration,
                    resolution,
                    element.style
                )

                # Adicionar áudio se disponível
                if element.content in audio_files:
                    audio_clip = create_audio_clip(audio_files[element.content])
                    if audio_clip:
                        text_clip = text_clip.set_audio(audio_clip)
                        audio_clips.append(audio_clip)

                # Adicionar avatar se disponível
                if element.content in avatar_files:
                    avatar_clip = VideoFileClip(avatar_files[element.content])
                    # Redimensionar avatar para tamanho do elemento
                    avatar_clip = avatar_clip.resize(element.size)
                    # Posicionar avatar
                    avatar_clip = avatar_clip.set_position((
                        element.position["x"] * resolution[0],
                        element.position["y"] * resolution[1]
                    ))
                    clips.append(avatar_clip)

                clips.append(text_clip)

            elif element.type == "image":
                # Criar clip de imagem
                img_clip = create_image_clip(
                    element.content,
                    element.duration,
                    resolution
                )
                clips.append(img_clip)

            elif element.type == "audio":
                # Criar clip de áudio
                audio_clip = create_audio_clip(element.content)
                if audio_clip:
                    # Criar clip visual para áudio
                    audio_visual = ColorClip(resolution, color=(50, 50, 50)).set_duration(audio_clip.duration)
                    audio_visual = audio_visual.set_audio(audio_clip)
                    clips.append(audio_visual)
                    audio_clips.append(audio_clip)

        # Combinar todos os clips da cena
        if clips:
            # Se há múltiplos clips, combinar
            if len(clips) > 1:
                scene_clip = CompositeVideoClip(clips, size=resolution)
            else:
                scene_clip = clips[0]

            # Combinar áudios se houver múltiplos
            if len(audio_clips) > 1:
                combined_audio = CompositeAudioClip(audio_clips)
                scene_clip = scene_clip.set_audio(combined_audio)

            return scene_clip
        else:
            # Fallback: clip vazio
            return ColorClip(resolution, color=(0, 0, 0)).set_duration(scene.duration)

    except Exception as e:
        logger.error(f"Erro ao criar clip da cena: {e}")
        # Fallback: clip simples
        return ColorClip(resolution, color=(100, 100, 100)).set_duration(scene.duration)

def send_export_notification(email: str, project_name: str, video_url: str):
    msg = MIMEText(f"Seu vídeo do projeto '{project_name}' está pronto! Baixe em: {video_url}")
    msg['Subject'] = f"Exportação IA concluída - {project_name}"
    msg['From'] = 'no-reply@tecnocursos.ai'
    msg['To'] = email
    try:
        with smtplib.SMTP('localhost') as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")

# ===============================================================
# ENDPOINTS PRINCIPAIS
# ===============================================================

@router.post("/export", response_model=VideoExportResponse)
async def export_video(
    request: VideoExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Exporta vídeo final com todas as cenas e configurações.

    Processo completo:
    1. Gera áudio TTS para textos com narração IA
    2. Gera vídeos de avatar (se habilitado)
    3. Monta cada cena com MoviePy
    4. Une todas as cenas com transições
    5. Salva vídeo final em MP4
    """
    try:
        if not VIDEO_FUNCTIONS_AVAILABLE or not MOVIEPY_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de exportação de vídeo temporariamente indisponível"
            )

        # Gerar ID único para o vídeo
        video_id = f"export_{uuid.uuid4().hex[:12]}"

        # Validar resolução
        if request.resolution not in RESOLUTION_CONFIGS:
            raise HTTPException(
                status_code=400,
                detail=f"Resolução inválida. Válidas: {list(RESOLUTION_CONFIGS.keys())}"
            )

        # Validar qualidade
        if request.quality not in QUALITY_CONFIGS:
            raise HTTPException(
                status_code=400,
                detail=f"Qualidade inválida. Válidas: {list(QUALITY_CONFIGS.keys())}"
            )

        # Configurar TTS
        tts_config = TTSConfig(
            provider=TTSProvider(request.tts_provider),
            voice=request.tts_voice,
            language="pt",
            output_format="mp3"
        )

        # Após iniciar exportação, registrar vídeo no banco
        from app.models import Video
        from app.database import get_db
        db = get_db()
        video = Video(
            title=request.title,
            filename=f"{video_id}.mp4",
            file_path=f"app/static/videos/{video_id}.mp4",
            file_size=0,  # Atualizar após renderização
            duration=None,
            format="mp4",
            status="queued",
            project_id=getattr(request, 'project_id', None),
            source_file_id=None
        )
        db.add(video)
        db.commit()
        db.refresh(video)

        # Processar vídeo em background
        background_tasks.add_task(
            process_video_export,
            video_id,
            request,
            tts_config,
            current_user.id if current_user else None
        )

        return VideoExportResponse(
            success=True,
            video_id=video_id,
            message="Exportação de vídeo iniciada. Use o ID para verificar o status.",
            data={
                "estimated_completion": "5-15 minutos",
                "status_endpoint": f"/api/video-export/{video_id}/status",
                "download_endpoint": f"/api/video-export/{video_id}/download",
                "scenes_count": len(request.scenes),
                "resolution": request.resolution,
                "quality": request.quality
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/export-ia", response_model=VideoExportResponse)
async def export_video_ia(
    project_id: int,
    tts_model: str = "coqui",
    avatar_model: str = "hunyuan3d2",
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    db: Session = Depends(get_db)
):
    """
    Exporta vídeo final do projeto com pipeline IA (TTS, avatar, assets, MoviePy).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.ordem).all()
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    final_video_path = export_project_video_with_ia(project, scenes, assets, tts_model, avatar_model)
    # Salvar/atualizar vídeo no banco
    from app.models import Video
    video = Video(
        title=f"Exportação IA {project.name}",
        filename=os.path.basename(final_video_path),
        file_path=final_video_path,
        file_size=os.path.getsize(final_video_path),
        duration=None,
        format="mp4",
        status="completed",
        project_id=project.id,
        source_file_id=None
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return VideoExportResponse(
        success=True,
        video_id=video.id,
        message="Exportação IA concluída com sucesso.",
        data={
            "download_url": f"/static/videos/generated/project_{project.id}/final_project_video.mp4",
            "project_id": project.id,
            "video_id": video.id
        }
    )

@router.post("/export-ia-async", response_model=VideoExportResponse)
async def export_video_ia_async(
    project_id: int,
    tts_model: str = "coqui",
    avatar_model: str = "hunyuan3d2",
    background_tasks: BackgroundTasks = Depends(),
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    db: Session = Depends(get_db)
):
    """
    Exporta vídeo final do projeto com pipeline IA de forma assíncrona/background.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.ordem).all()
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    def on_finish(final_video_path):
        from app.models import Video
        video = Video(
            title=f"Exportação IA {project.name}",
            filename=os.path.basename(final_video_path),
            file_path=final_video_path,
            file_size=os.path.getsize(final_video_path),
            duration=None,
            format="mp4",
            status="completed",
            project_id=project.id,
            source_file_id=None
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        # Notificar usuário por e-mail se disponível
        if hasattr(project, 'owner') and getattr(project.owner, 'email', None):
            send_export_notification(project.owner.email, project.name, final_video_path)
    from app.services.video_pipeline_service import export_project_video_with_ia_async
    background_tasks.add_task(export_project_video_with_ia_async(project, scenes, assets, tts_model, avatar_model, on_finish))
    return VideoExportResponse(
        success=True,
        video_id=None,
        message="Exportação IA agendada em background. Você será notificado ao finalizar.",
        data={
            "project_id": project.id
        }
    )

@router.get("/export-ia-status/{project_id}")
async def get_export_ia_status(project_id: int, db: Session = Depends(get_db)):
    """
    Consulta o status da última exportação IA do projeto.
    """
    from app.models import Video
    video = db.query(Video).filter(Video.project_id == project_id).order_by(Video.id.desc()).first()
    if not video:
        return JSONResponse(status_code=404, content={"status": "not_found", "message": "Nenhuma exportação encontrada."})
    status = video.status or "unknown"
    data = {"status": status}
    if status == "completed":
        data["download_url"] = video.file_path
    return data

@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_export_status(
    video_id: str,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """Verifica o status de exportação de um vídeo"""
    try:
        # Verificar se job existe
        if video_id not in video_jobs:
            raise HTTPException(
                status_code=404,
                detail="Vídeo não encontrado"
            )

        job = video_jobs[video_id]

        # Verificar se vídeo está pronto
        video_path = f"app/static/videos/{video_id}.mp4"
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            return VideoStatusResponse(
                video_id=video_id,
                status="completed",
                progress=100.0,
                current_stage="finished",
                video_url=f"/api/video-export/{video_id}/download",
                file_size=file_size,
                duration=job.get("duration", 0)
            )

        # Retornar status atual
        return VideoStatusResponse(
            video_id=video_id,
            status=job.get("status", "unknown"),
            progress=job.get("progress", 0),
            current_stage=job.get("current_stage", "unknown"),
            estimated_time=job.get("estimated_time"),
            error_message=job.get("error_message")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")

@router.get("/{video_id}/download")
async def download_exported_video(
    video_id: str,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """Download do vídeo exportado"""
    try:
        video_path = f"app/static/videos/{video_id}.mp4"

        if not os.path.exists(video_path):
            raise HTTPException(
                status_code=404,
                detail="Vídeo não encontrado ou ainda não processado"
            )

        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=f"{video_id}.mp4",
            headers={"Content-Disposition": f"attachment; filename={video_id}.mp4"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no download: {str(e)}")

# ===============================================================
# FUNÇÃO DE PROCESSAMENTO EM BACKGROUND
# ===============================================================

async def process_video_export(
    video_id: str,
    request: VideoExportRequest,
    tts_config: TTSConfig,
    user_id: Optional[int] = None
):
    """Processa exportação de vídeo em background"""

    # Registrar job
    video_jobs[video_id] = {
        "status": "processing",
        "progress": 0,
        "current_stage": "Iniciando processamento",
        "start_time": time.time()
    }

    try:
        logger.info(f"🎬 Iniciando exportação de vídeo {video_id}")

        # Configurar resolução
        resolution = RESOLUTION_CONFIGS[request.resolution]
        quality_config = QUALITY_CONFIGS[request.quality]

        # Atualizar progresso
        video_jobs[video_id]["progress"] = 5
        video_jobs[video_id]["current_stage"] = "Configurando projeto"

        # ========================================================================
        # ETAPA 1: GERAR ÁUDIOS TTS PARA TODAS AS CENAS
        # ========================================================================
        logger.info("🎤 ETAPA 1: Gerando áudios TTS...")
        video_jobs[video_id]["current_stage"] = "Gerando narrações TTS"
        video_jobs[video_id]["progress"] = 10

        all_audio_files = {}
        for i, scene in enumerate(request.scenes):
            # Gerar TTS para esta cena
            scene_audio_files = await generate_tts_for_scene(scene, tts_config)
            all_audio_files[scene.id] = scene_audio_files

            # Atualizar progresso
            progress = 10 + (i + 1) * 20 // len(request.scenes)
            video_jobs[video_id]["progress"] = progress

        # ========================================================================
        # ETAPA 2: GERAR VÍDEOS DE AVATAR (SE HABILITADO)
        # ========================================================================
        logger.info("🎭 ETAPA 2: Gerando avatares...")
        video_jobs[video_id]["current_stage"] = "Gerando avatares"
        video_jobs[video_id]["progress"] = 30

        all_avatar_files = {}
        avatar_scenes = [s for s in request.scenes if s.avatar_enabled]

        for i, scene in enumerate(avatar_scenes):
            # Gerar avatares para esta cena
            scene_avatar_files = await generate_avatar_for_scene(
                scene,
                all_audio_files.get(scene.id, {})
            )
            all_avatar_files[scene.id] = scene_avatar_files

            # Atualizar progresso
            if avatar_scenes:
                progress = 30 + (i + 1) * 20 // len(avatar_scenes)
                video_jobs[video_id]["progress"] = progress

        # ========================================================================
        # ETAPA 3: MONTAR CLIPS DE CADA CENA
        # ========================================================================
        logger.info("🎬 ETAPA 3: Montando cenas...")
        video_jobs[video_id]["current_stage"] = "Montando cenas"
        video_jobs[video_id]["progress"] = 50

        scene_clips = []
        for i, scene in enumerate(request.scenes):
            # Criar clip da cena
            scene_clip = create_scene_clip(
                scene,
                all_audio_files.get(scene.id, {}),
                all_avatar_files.get(scene.id, {}),
                resolution,
                request.fps
            )
            scene_clips.append(scene_clip)

            # Atualizar progresso
            progress = 50 + (i + 1) * 30 // len(request.scenes)
            video_jobs[video_id]["progress"] = progress

        # ========================================================================
        # ETAPA 4: UNIR CENAS COM TRANSIÇÕES
        # ========================================================================
        logger.info("🔗 ETAPA 4: Unindo cenas...")
        video_jobs[video_id]["current_stage"] = "Unindo cenas"
        video_jobs[video_id]["progress"] = 80

        final_clips = []
        for i, clip in enumerate(scene_clips):
            # Adicionar transição se não for o primeiro clip
            if i > 0 and i < len(request.scenes):
                prev_scene = request.scenes[i-1]
                transition_type = prev_scene.transition or "fade"
                clip, scene_clips[i] = add_transition(
                    scene_clips[i-1], clip, transition_type
                )

            final_clips.append(clip)

        # Concatenar todos os clips
        final_video = concatenate_videoclips(final_clips)

        # ========================================================================
        # ETAPA 5: ADICIONAR MÚSICA DE FUNDO (SE ESPECIFICADA)
        # ========================================================================
        if request.background_music and os.path.exists(request.background_music):
            logger.info("🎵 ETAPA 5: Adicionando música de fundo...")
            video_jobs[video_id]["current_stage"] = "Adicionando música"

            try:
                background_audio = AudioFileClip(request.background_music)

                # Loop música se necessário
                if background_audio.duration < final_video.duration:
                    loops_needed = int(final_video.duration / background_audio.duration) + 1
                    background_audio = concatenate_videoclips([background_audio] * loops_needed)

                # Cortar para duração exata
                background_audio = background_audio.subclip(0, final_video.duration)

                # Reduzir volume da música
                background_audio = background_audio.volumex(0.3)

                # Combinar com áudio do vídeo
                if final_video.audio:
                    final_audio = CompositeAudioClip([final_video.audio, background_audio])
                    final_video = final_video.set_audio(final_audio)
                else:
                    final_video = final_video.set_audio(background_audio)

            except Exception as e:
                logger.error(f"Erro ao adicionar música de fundo: {e}")

        # ========================================================================
        # ETAPA 6: SALVAR VÍDEO FINAL
        # ========================================================================
        logger.info("💾 ETAPA 6: Salvando vídeo final...")
        video_jobs[video_id]["current_stage"] = "Salvando vídeo"
        video_jobs[video_id]["progress"] = 90

        # Configurar caminho de saída
        output_path = f"app/static/videos/{video_id}.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Configurações de qualidade
        codec = "libx264"
        audio_codec = "aac"
        bitrate = quality_config["bitrate"]
        crf = quality_config["crf"]

        # Salvar vídeo
        final_video.write_videofile(
            output_path,
            codec=codec,
            audio_codec=audio_codec,
            bitrate=bitrate,
            fps=request.fps,
            preset="medium",
            threads=4,
            verbose=False,
            logger=None
        )

        # Obter informações do vídeo
        file_size = os.path.getsize(output_path)
        duration = final_video.duration

        # Atualizar job com sucesso
        video_jobs[video_id].update({
            "status": "completed",
            "progress": 100,
            "current_stage": "Concluído",
            "duration": duration,
            "file_size": file_size,
            "completed_at": datetime.now().isoformat()
        })

        logger.info(f"✅ Exportação de vídeo {video_id} concluída!")
        logger.info(f"📁 Arquivo: {output_path}")
        logger.info(f"⏱️ Duração: {duration:.2f}s")
        logger.info(f"💾 Tamanho: {file_size/1024/1024:.2f}MB")

        # Limpar recursos
        final_video.close()
        for clip in scene_clips:
            clip.close()

        # Após exportar vídeo, registrar no banco
        from app.models import Video
        db = get_db()
        video = Video(
            title=f"Exportação {video_id}",
            filename=f"{video_id}.mp4",
            file_path=output_path,
            file_size=os.path.getsize(output_path) if os.path.exists(output_path) else 0,
            duration=request.duration if hasattr(request, 'duration') else None,
            format="mp4",
            status="completed",
            project_id=request.project_id if hasattr(request, 'project_id') else None,
            source_file_id=None
        )
        db.add(video)
        db.commit()
        db.refresh(video)

    except Exception as e:
        error_msg = f"Erro na exportação: {str(e)}"
        logger.error(f"❌ {error_msg}")

        # Atualizar job com erro
        video_jobs[video_id].update({
            "status": "failed",
            "progress": 0,
            "current_stage": "Erro",
            "error_message": error_msg
        })

# ===============================================================
# ENDPOINTS DE INFORMAÇÃO E STATUS
# ===============================================================

@router.get("/info")
async def get_video_export_info():
    """Informações sobre o serviço de exportação de vídeo"""
    return {
        "service": "TecnoCursos AI - Video Export API",
        "version": "1.0.0",
        "status": "operational" if VIDEO_FUNCTIONS_AVAILABLE and MOVIEPY_AVAILABLE else "limited",
        "capabilities": {
            "tts_generation": TTSProvider is not None,
            "avatar_generation": True,
            "video_montage": MOVIEPY_AVAILABLE,
            "transitions": True,
            "background_music": True,
            "multiple_resolutions": True
        },
        "supported_formats": {
            "input_audio": ["MP3", "WAV"],
            "output_video": ["MP4"],
            "resolutions": list(RESOLUTION_CONFIGS.keys()),
            "qualities": list(QUALITY_CONFIGS.keys())
        },
        "tts_providers": ["auto", "bark", "gtts"] if TTSProvider else [],
        "avatar_styles": ["professional", "educational", "tech", "minimal"],
        "transitions": ["fade", "slide", "zoom"],
        "limits": {
            "max_scenes": 50,
            "max_scene_duration": 300,  # 5 minutos
            "max_total_duration": 3600,  # 1 hora
            "max_file_size": "500MB"
        },
        "endpoints": {
            "export": "/api/video-export/export",
            "status": "/api/video-export/{id}/status",
            "download": "/api/video-export/{id}/download",
            "info": "/api/video-export/info"
        }
    }

# Exportar router
video_export_router = router
