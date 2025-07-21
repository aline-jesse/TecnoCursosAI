"""
Router para geração de vídeos do avatar - TecnoCursos AI
Endpoints para criar vídeos educacionais com avatar animado
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import os
from pathlib import Path
import json
import logging

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Project, Video
from app.schemas import VideoCreate, VideoResponse
from services.avatar_video_generator import (
    generate_avatar_video,
    AvatarVideoGenerator, 
    VideoContent,
    AvatarConfig,
    VideoConfig,
    SlideConfig,
    AvatarStyle,
    VideoQuality
)
# Importar serviços TTS
try:
    from services.tts_service import TTSConfig, TTSProvider
except ImportError:
    print("⚠️ Serviço TTS não disponível para avatar")
    TTSConfig = None
    TTSProvider = None
# Use logging diretamente para evitar import circular
logger = logging.getLogger("avatar_router")
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/avatar", tags=["Avatar Videos"])

# Exportar router para uso principal
avatar_router = router

# Schemas específicos para avatar
from pydantic import BaseModel, Field

class SlideData(BaseModel):
    """Dados de um slide"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=2000)

class AvatarVideoRequest(BaseModel):
    """Requisição para gerar vídeo do avatar"""
    project_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    slides: List[SlideData] = Field(..., min_items=1, max_items=50)
    audio_texts: List[str] = Field(..., min_items=1, max_items=50)
    
    # Configurações do avatar
    avatar_style: str = Field("professional", regex="^(professional|friendly|teacher|minimal)$")
    avatar_skin_tone: Optional[str] = Field("#fdbcb4", regex="^#[0-9a-fA-F]{6}$")
    avatar_hair_color: Optional[str] = Field("#8b4513", regex="^#[0-9a-fA-F]{6}$")
    avatar_shirt_color: Optional[str] = Field("#4a90e2", regex="^#[0-9a-fA-F]{6}$")
    
    # Configurações do vídeo
    video_quality: str = Field("1080p", regex="^(720p|1080p|4k)$")
    video_fps: Optional[int] = Field(30, ge=15, le=60)
    enable_animation: Optional[bool] = True
    background_music: Optional[str] = None
    
    # Configurações TTS
    tts_provider: str = Field("auto", regex="^(auto|bark|gtts)$")
    tts_voice: Optional[str] = "pt_speaker_0"
    tts_language: str = Field("pt", regex="^(pt|en|es|fr)$")
    
    # Configurações dos slides
    slide_template: str = Field("modern", regex="^(modern|classic|minimal)$")
    slide_title_color: Optional[str] = Field("#2c3e50", regex="^#[0-9a-fA-F]{6}$")
    slide_content_color: Optional[str] = Field("#34495e", regex="^#[0-9a-fA-F]{6}$")
    slide_accent_color: Optional[str] = Field("#3498db", regex="^#[0-9a-fA-F]{6}$")

class AvatarVideoResponse(BaseModel):
    """Resposta da geração de vídeo do avatar"""
    video_id: int
    status: str
    message: str
    generation_progress: float = 0.0
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    metadata: Optional[Dict] = None

class AvatarVideoStatus(BaseModel):
    """Status da geração de vídeo"""
    video_id: int
    status: str
    progress: float
    estimated_time_remaining: Optional[int] = None
    error_message: Optional[str] = None

@router.post("/generate", response_model=AvatarVideoResponse)
async def generate_avatar_video_endpoint(
    request: AvatarVideoRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera vídeo do avatar com slides e narração
    """
    try:
        # Verificar se o projeto existe e pertence ao usuário
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado"
            )
        
        # Validar dados
        if len(request.slides) != len(request.audio_texts):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de slides deve ser igual ao número de textos de narração"
            )
        
        # Criar registro do vídeo no banco
        video = Video(
            project_id=request.project_id,
            title=request.title,
            description=request.description,
            status="queued",
            generation_progress=0.0,
            voice_type=request.tts_voice,
            include_captions=True,
            video_path="",  # Será definido após geração
            format="mp4",
            resolution=request.video_quality,
            fps=request.video_fps
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Adicionar tarefa em background
        background_tasks.add_task(
            process_avatar_video_generation,
            video.id,
            request,
            current_user.id
        )
        
        logger.info(f"Vídeo do avatar #{video.id} adicionado à fila de processamento")
        
        return AvatarVideoResponse(
            video_id=video.id,
            status="queued",
            message="Vídeo adicionado à fila de processamento",
            generation_progress=0.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar vídeo do avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar solicitação"
        )

@router.get("/status/{video_id}", response_model=AvatarVideoStatus)
async def get_avatar_video_status(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém status da geração de vídeo do avatar
    """
    try:
        # Buscar vídeo
        video = db.query(Video).filter(
            Video.id == video_id
        ).first()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado"
            )
        
        # Verificar se o usuário tem acesso
        project = db.query(Project).filter(
            Project.id == video.project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        # Estimar tempo restante
        estimated_time = None
        if video.status == "generating" and video.generation_progress > 0:
            # Estimativa simples baseada no progresso
            time_per_percent = 2  # segundos por porcentagem
            remaining_percent = 100 - video.generation_progress
            estimated_time = int(remaining_percent * time_per_percent)
        
        return AvatarVideoStatus(
            video_id=video.id,
            status=video.status,
            progress=video.generation_progress,
            estimated_time_remaining=estimated_time,
            error_message=video.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do vídeo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter status"
        )

@router.get("/video/{video_id}", response_model=AvatarVideoResponse)
async def get_avatar_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém informações do vídeo do avatar gerado
    """
    try:
        # Buscar vídeo
        video = db.query(Video).filter(
            Video.id == video_id
        ).first()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado"
            )
        
        # Verificar acesso
        project = db.query(Project).filter(
            Project.id == video.project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        # Gerar URLs se vídeo estiver pronto
        video_url = None
        thumbnail_url = None
        
        if video.status == "completed" and video.video_path:
            video_url = f"/static/videos/{os.path.basename(video.video_path)}"
            # Thumbnail seria gerado automaticamente
            thumbnail_path = video.video_path.replace('.mp4', '_thumb.jpg')
            if os.path.exists(thumbnail_path):
                thumbnail_url = f"/static/thumbnails/{os.path.basename(thumbnail_path)}"
        
        return AvatarVideoResponse(
            video_id=video.id,
            status=video.status,
            message="Vídeo obtido com sucesso",
            generation_progress=video.generation_progress,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            duration=video.duration,
            file_size=video.file_size,
            metadata=json.loads(video.metadata) if video.metadata else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter vídeo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter vídeo"
        )

@router.get("/styles")
async def get_avatar_styles():
    """
    Lista estilos de avatar disponíveis
    """
    return {
        "styles": [
            {
                "id": "professional",
                "name": "Profissional",
                "description": "Avatar com aparência formal e corporativa"
            },
            {
                "id": "friendly", 
                "name": "Amigável",
                "description": "Avatar com aparência calorosa e acessível"
            },
            {
                "id": "teacher",
                "name": "Professor",
                "description": "Avatar otimizado para ensino e educação"
            },
            {
                "id": "minimal",
                "name": "Minimalista", 
                "description": "Avatar com design simples e clean"
            }
        ],
        "video_qualities": [
            {"id": "720p", "name": "HD (720p)", "resolution": "1280x720"},
            {"id": "1080p", "name": "Full HD (1080p)", "resolution": "1920x1080"},
            {"id": "4k", "name": "Ultra HD (4K)", "resolution": "3840x2160"}
        ],
        "tts_providers": [
            {"id": "auto", "name": "Automático", "description": "Seleciona melhor provider disponível"},
            {"id": "bark", "name": "Bark AI", "description": "TTS avançado com vozes naturais"},
            {"id": "gtts", "name": "Google TTS", "description": "TTS rápido e confiável"}
        ]
    }

async def process_avatar_video_generation(
    video_id: int,
    request: AvatarVideoRequest,
    user_id: int
):
    """
    Processa geração de vídeo do avatar em background
    """
    db = next(get_db())
    
    try:
        # Buscar vídeo
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            logger.error(f"Vídeo {video_id} não encontrado para processamento")
            return
        
        # Atualizar status
        video.status = "generating"
        video.generation_progress = 10.0
        db.commit()
        
        logger.info(f"Iniciando geração do vídeo do avatar #{video_id}")
        
        # Criar gerador personalizado
        generator = AvatarVideoGenerator()
        
        # Configurar avatar
        avatar_style = AvatarStyle(request.avatar_style)
        generator.update_avatar_config(
            style=avatar_style,
            skin_tone=request.avatar_skin_tone,
            hair_color=request.avatar_hair_color,
            shirt_color=request.avatar_shirt_color,
            enable_animation=request.enable_animation
        )
        
        # Configurar vídeo
        resolution_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        generator.update_video_config(
            resolution=resolution_map[request.video_quality],
            fps=request.video_fps,
            background_music=request.background_music
        )
        
        # Configurar slides
        generator.update_slide_config(
            template=request.slide_template,
            title_color=request.slide_title_color,
            content_color=request.slide_content_color,
            accent_color=request.slide_accent_color
        )
        
        # Atualizar progresso
        video.generation_progress = 30.0
        db.commit()
        
        # Preparar conteúdo
        slides_data = [
            {"title": slide.title, "content": slide.content}
            for slide in request.slides
        ]
        
        content = VideoContent(
            slides=slides_data,
            audio_texts=request.audio_texts
        )
        
        # Configurar TTS
        tts_config = TTSConfig(
            provider=TTSProvider(request.tts_provider),
            language=request.tts_language,
            voice=request.tts_voice
        )
        
        # Gerar caminho de saída
        videos_dir = Path(settings.static_directory) / "videos"
        videos_dir.mkdir(exist_ok=True)
        output_path = videos_dir / f"avatar_video_{video_id}.mp4"
        
        # Atualizar progresso
        video.generation_progress = 50.0
        db.commit()
        
        # Gerar vídeo
        result = await generator.generate_video(
            content=content,
            output_path=str(output_path),
            tts_config=tts_config
        )
        
        if result["success"]:
            # Sucesso - atualizar banco
            video.status = "completed"
            video.generation_progress = 100.0
            video.video_path = str(output_path)
            video.duration = result["duration"]
            video.file_size = result["file_size"]
            video.metadata = json.dumps({
                "slides_count": result["slides_count"],
                "resolution": result["resolution"],
                "fps": result["fps"],
                "avatar_style": request.avatar_style,
                "tts_provider": request.tts_provider
            })
            
            logger.info(f"✅ Vídeo do avatar #{video_id} gerado com sucesso")
            
        else:
            # Erro - atualizar status
            video.status = "failed"
            video.error_message = result.get("error", "Erro desconhecido")
            
            logger.error(f"❌ Erro na geração do vídeo #{video_id}: {video.error_message}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Erro no processamento do vídeo #{video_id}: {e}")
        
        # Atualizar status de erro
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.status = "failed"
                video.error_message = str(e)
                db.commit()
        except:
            pass
    
    finally:
        db.close()

@router.delete("/video/{video_id}")
async def delete_avatar_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exclui vídeo do avatar
    """
    try:
        # Buscar vídeo
        video = db.query(Video).filter(Video.id == video_id).first()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado"
            )
        
        # Verificar acesso
        project = db.query(Project).filter(
            Project.id == video.project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        # Excluir arquivo físico se existir
        if video.video_path and os.path.exists(video.video_path):
            try:
                os.remove(video.video_path)
                
                # Excluir thumbnail se existir
                thumbnail_path = video.video_path.replace('.mp4', '_thumb.jpg')
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                    
            except Exception as e:
                logger.warning(f"Erro ao excluir arquivo do vídeo {video_id}: {e}")
        
        # Excluir registro do banco
        db.delete(video)
        db.commit()
        
        logger.info(f"Vídeo do avatar #{video_id} excluído")
        
        return {"message": "Vídeo excluído com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir vídeo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir vídeo"
        ) 