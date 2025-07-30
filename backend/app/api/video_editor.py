"""
Video Editor API - Backend para processamento de vídeo
Integrado ao sistema TecnoCursos AI
"""

import os
import asyncio
import uuid
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import ffmpeg
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Request, Depends
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.settings import settings
from app.core.logging import get_logger
from app.core.cache import cache_manager
from app.core.validators import FileValidator, validate_data
from app.security.auth_manager import get_current_user
from app.core.notifications import notification_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/api/video-editor", tags=["video-editor"])

# Modelos Pydantic
class VideoClip(BaseModel):
    id: str
    name: str
    type: str = Field(..., regex=r'^(video|audio|image|text)$')
    src: Optional[str] = None
    start_time: float = Field(ge=0)
    end_time: float = Field(gt=0)
    layer: int = Field(ge=0, le=10)
    volume: Optional[float] = Field(100, ge=0, le=200)
    opacity: Optional[float] = Field(100, ge=0, le=100)
    visible: bool = True
    locked: bool = False
    position: Optional[Dict[str, float]] = None
    filters: Optional[Dict[str, float]] = None
    text_properties: Optional[Dict[str, Any]] = None
    effects: List[str] = []

class ProjectSettings(BaseModel):
    resolution: Dict[str, int] = {"width": 1920, "height": 1080}
    frame_rate: int = Field(30, ge=1, le=120)
    duration: float = Field(300, gt=0)
    background_color: str = "#000000"
    audio_sample_rate: int = 44100

class VideoProject(BaseModel):
    id: Optional[str] = None
    name: str
    clips: List[VideoClip]
    settings: ProjectSettings
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ExportSettings(BaseModel):
    format: str = Field("mp4", regex=r'^(mp4|mov|avi|webm)$')
    quality: str = Field("high", regex=r'^(low|medium|high|ultra)$')
    resolution: Optional[Dict[str, int]] = None
    frame_rate: Optional[int] = None
    bitrate: Optional[str] = None
    audio_bitrate: Optional[str] = None

# Processador de Vídeo
class VideoProcessor:
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "tecnocursos_video"
        self.temp_dir.mkdir(exist_ok=True)
        self.active_exports = {}
        
    async def process_upload(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Processa upload de arquivo de mídia"""
        try:
            # Validar arquivo
            temp_path = self.temp_dir / f"{uuid.uuid4()}_{file.filename}"
            
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Validar com FileValidator
            file_validator = FileValidator(
                max_size=500 * 1024 * 1024,  # 500MB
                allowed_types=[
                    'video/mp4', 'video/quicktime', 'video/x-msvideo',
                    'audio/mpeg', 'audio/wav', 'audio/ogg',
                    'image/jpeg', 'image/png', 'image/gif'
                ]
            )
            
            validation_result = file_validator.validate_file(str(temp_path), file.filename)
            
            if not validation_result['valid']:
                temp_path.unlink()
                raise HTTPException(400, f"Arquivo inválido: {validation_result['errors']}")
            
            # Extrair metadados
            metadata = await self._extract_metadata(str(temp_path))
            
            # Gerar thumbnail se for vídeo
            thumbnail_path = None
            if file.content_type.startswith('video/'):
                thumbnail_path = await self._generate_thumbnail(str(temp_path))
            
            # Mover para diretório permanente
            final_path = settings.files.upload_dir / f"{user_id}" / f"{uuid.uuid4()}_{file.filename}"
            final_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.rename(final_path)
            
            return {
                "id": str(uuid.uuid4()),
                "filename": file.filename,
                "path": str(final_path),
                "url": f"/api/files/{final_path.name}",
                "thumbnail": thumbnail_path,
                "size": validation_result['size'],
                "duration": metadata.get('duration', 0),
                "width": metadata.get('width'),
                "height": metadata.get('height'),
                "mime_type": validation_result['mime_type'],
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            if temp_path.exists():
                temp_path.unlink()
            raise HTTPException(500, f"Erro no processamento: {str(e)}")
    
    async def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados do arquivo de mídia"""
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            metadata = {
                "duration": float(probe['format'].get('duration', 0)),
                "size": int(probe['format'].get('size', 0)),
                "format": probe['format'].get('format_name', ''),
                "bit_rate": int(probe['format'].get('bit_rate', 0))
            }
            
            if video_stream:
                metadata.update({
                    "width": int(video_stream.get('width', 0)),
                    "height": int(video_stream.get('height', 0)),
                    "fps": eval(video_stream.get('r_frame_rate', '0/1')),
                    "video_codec": video_stream.get('codec_name', ''),
                    "pixel_format": video_stream.get('pix_fmt', '')
                })
            
            if audio_stream:
                metadata.update({
                    "audio_codec": audio_stream.get('codec_name', ''),
                    "sample_rate": int(audio_stream.get('sample_rate', 0)),
                    "channels": int(audio_stream.get('channels', 0)),
                    "audio_bitrate": int(audio_stream.get('bit_rate', 0))
                })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erro ao extrair metadados: {e}")
            return {}
    
    async def _generate_thumbnail(self, video_path: str) -> str:
        """Gera thumbnail do vídeo"""
        try:
            thumbnail_path = self.temp_dir / f"thumb_{uuid.uuid4()}.jpg"
            
            (
                ffmpeg
                .input(video_path)
                .filter('scale', 320, 180)
                .output(str(thumbnail_path), vframes=1, ss=1)
                .overwrite_output()
                .run(quiet=True)
            )
            
            return str(thumbnail_path)
            
        except Exception as e:
            logger.error(f"Erro ao gerar thumbnail: {e}")
            return None
    
    async def export_video(self, project: VideoProject, export_settings: ExportSettings, user_id: str) -> str:
        """Exporta o projeto de vídeo"""
        export_id = str(uuid.uuid4())
        
        try:
            self.active_exports[export_id] = {
                "status": "starting",
                "progress": 0,
                "user_id": user_id,
                "started_at": datetime.utcnow()
            }
            
            # Criar arquivo temporário de saída
            output_path = self.temp_dir / f"export_{export_id}.{export_settings.format}"
            
            # Resolver configurações de export
            resolution = export_settings.resolution or project.settings.resolution
            frame_rate = export_settings.frame_rate or project.settings.frame_rate
            
            # Configurações de qualidade
            quality_settings = self._get_quality_settings(export_settings.quality)
            
            # Processar clipes por tipo
            video_clips = [c for c in project.clips if c.type == 'video']
            audio_clips = [c for c in project.clips if c.type == 'audio']
            image_clips = [c for c in project.clips if c.type == 'image']
            text_clips = [c for c in project.clips if c.type == 'text']
            
            # Atualizar progresso
            self.active_exports[export_id]["status"] = "processing_video"
            self.active_exports[export_id]["progress"] = 10
            
            # Criar pipeline FFmpeg
            inputs = []
            filters = []
            
            # Vídeo de fundo
            background = ffmpeg.input('color=c=black:s={}x{}:d={}'.format(
                resolution['width'], 
                resolution['height'], 
                project.settings.duration
            ), f='lavfi')
            inputs.append(background)
            
            # Processar clipes de vídeo
            for i, clip in enumerate(video_clips):
                if not clip.src or not Path(clip.src).exists():
                    continue
                    
                video_input = ffmpeg.input(clip.src)
                
                # Aplicar filtros de tempo
                video_filtered = video_input.filter(
                    'trim',
                    start=clip.start_time,
                    end=clip.end_time
                ).filter('setpts', 'PTS-STARTPTS')
                
                # Aplicar transformações
                if clip.position:
                    video_filtered = video_filtered.filter(
                        'scale',
                        clip.position.get('width', resolution['width']),
                        clip.position.get('height', resolution['height'])
                    )
                
                # Aplicar filtros visuais
                if clip.filters:
                    if clip.filters.get('brightness', 0) != 0:
                        video_filtered = video_filtered.filter('eq', brightness=clip.filters['brightness']/100)
                    if clip.filters.get('contrast', 0) != 0:
                        video_filtered = video_filtered.filter('eq', contrast=1 + clip.filters['contrast']/100)
                    if clip.filters.get('saturation', 0) != 0:
                        video_filtered = video_filtered.filter('eq', saturation=1 + clip.filters['saturation']/100)
                
                inputs.append(video_filtered)
            
            # Processar clipes de texto
            self.active_exports[export_id]["progress"] = 30
            
            for clip in text_clips:
                if not clip.text_properties or not clip.text_properties.get('content'):
                    continue
                
                text_filter = self._create_text_filter(clip, resolution)
                filters.append(text_filter)
            
            # Processar áudio
            self.active_exports[export_id]["status"] = "processing_audio"
            self.active_exports[export_id]["progress"] = 50
            
            audio_inputs = []
            for clip in audio_clips:
                if not clip.src or not Path(clip.src).exists():
                    continue
                    
                audio_input = ffmpeg.input(clip.src)
                audio_filtered = audio_input.filter(
                    'atrim',
                    start=clip.start_time,
                    end=clip.end_time
                ).filter('asetpts', 'PTS-STARTPTS')
                
                if clip.volume and clip.volume != 100:
                    audio_filtered = audio_filtered.filter('volume', clip.volume/100)
                
                audio_inputs.append(audio_filtered)
            
            # Mixar áudio
            if audio_inputs:
                mixed_audio = ffmpeg.filter(audio_inputs, 'amix', inputs=len(audio_inputs))
            else:
                # Áudio silencioso se não houver áudio
                mixed_audio = ffmpeg.input('anullsrc=channel_layout=stereo:sample_rate=44100', f='lavfi')
            
            # Combinar vídeo e áudio
            self.active_exports[export_id]["status"] = "encoding"
            self.active_exports[export_id]["progress"] = 70
            
            final_video = inputs[0]  # Background
            for video_input in inputs[1:]:
                final_video = ffmpeg.filter([final_video, video_input], 'overlay')
            
            # Output final
            output = ffmpeg.output(
                final_video,
                mixed_audio,
                str(output_path),
                vcodec='libx264',
                acodec='aac',
                **quality_settings,
                r=frame_rate,
                t=project.settings.duration
            )
            
            # Executar FFmpeg
            self.active_exports[export_id]["progress"] = 80
            
            process = ffmpeg.run_async(output, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
            
            # Monitorar progresso
            await self._monitor_ffmpeg_progress(export_id, process, project.settings.duration)
            
            # Finalizar
            self.active_exports[export_id]["status"] = "completed"
            self.active_exports[export_id]["progress"] = 100
            self.active_exports[export_id]["output_path"] = str(output_path)
            
            # Notificar usuário
            await notification_manager.send_notification(
                "video_exported",
                user_id=user_id,
                variables={
                    "project_name": project.name,
                    "export_id": export_id
                }
            )
            
            return export_id
            
        except Exception as e:
            logger.error(f"Erro na exportação: {e}")
            self.active_exports[export_id]["status"] = "error"
            self.active_exports[export_id]["error"] = str(e)
            
            await notification_manager.send_notification(
                "video_export_failed",
                user_id=user_id,
                variables={
                    "project_name": project.name,
                    "error": str(e)
                }
            )
            
            raise HTTPException(500, f"Erro na exportação: {str(e)}")
    
    def _get_quality_settings(self, quality: str) -> Dict[str, Any]:
        """Retorna configurações de qualidade para export"""
        settings_map = {
            "low": {
                "video_bitrate": "1M",
                "audio_bitrate": "128k",
                "crf": 28
            },
            "medium": {
                "video_bitrate": "2M",
                "audio_bitrate": "192k",
                "crf": 23
            },
            "high": {
                "video_bitrate": "4M",
                "audio_bitrate": "256k",
                "crf": 18
            },
            "ultra": {
                "video_bitrate": "8M",
                "audio_bitrate": "320k",
                "crf": 15
            }
        }
        return settings_map.get(quality, settings_map["medium"])
    
    def _create_text_filter(self, clip: VideoClip, resolution: Dict[str, int]) -> str:
        """Cria filtro de texto para FFmpeg"""
        text_props = clip.text_properties
        
        # Configurações básicas de texto
        text = text_props.get('content', '').replace("'", "\\'")
        fontsize = text_props.get('fontSize', 32)
        fontcolor = text_props.get('color', 'white')
        
        # Posição
        x = clip.position.get('x', resolution['width'] // 2) if clip.position else resolution['width'] // 2
        y = clip.position.get('y', resolution['height'] // 2) if clip.position else resolution['height'] // 2
        
        return f"drawtext=text='{text}':fontsize={fontsize}:fontcolor={fontcolor}:x={x}:y={y}:enable='between(t,{clip.start_time},{clip.end_time})'"
    
    async def _monitor_ffmpeg_progress(self, export_id: str, process, total_duration: float):
        """Monitora progresso do FFmpeg"""
        try:
            while True:
                output = await asyncio.get_event_loop().run_in_executor(
                    None, process.stderr.readline
                )
                
                if not output:
                    break
                
                line = output.decode('utf-8').strip()
                
                # Extrair tempo atual do output do FFmpeg
                if 'time=' in line:
                    time_str = line.split('time=')[1].split()[0]
                    try:
                        time_parts = time_str.split(':')
                        current_time = float(time_parts[0]) * 3600 + float(time_parts[1]) * 60 + float(time_parts[2])
                        progress = min(90, int((current_time / total_duration) * 70) + 20)  # 20-90%
                        
                        self.active_exports[export_id]["progress"] = progress
                    except:
                        pass
                
            await asyncio.get_event_loop().run_in_executor(None, process.wait)
            
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
    
    def get_export_status(self, export_id: str) -> Dict[str, Any]:
        """Retorna status da exportação"""
        return self.active_exports.get(export_id, {"status": "not_found"})
    
    def cancel_export(self, export_id: str):
        """Cancela exportação em andamento"""
        if export_id in self.active_exports:
            self.active_exports[export_id]["status"] = "cancelled"

# Instância global do processador
video_processor = VideoProcessor()

# Endpoints da API

@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload de arquivo de mídia"""
    result = await video_processor.process_upload(file, current_user.id)
    return {"success": True, "data": result}

@router.post("/projects")
async def create_project(
    project: VideoProject,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo projeto de vídeo"""
    project.id = str(uuid.uuid4())
    project.created_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()
    
    # Salvar no cache por enquanto (implementar BD depois)
    cache_key = f"video_project:{current_user.id}:{project.id}"
    await cache_manager.set(cache_key, project.dict(), ttl=86400)  # 24h
    
    return {"success": True, "project": project}

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user = Depends(get_current_user)
):
    """Buscar projeto por ID"""
    cache_key = f"video_project:{current_user.id}:{project_id}"
    project_data = await cache_manager.get(cache_key)
    
    if not project_data:
        raise HTTPException(404, "Projeto não encontrado")
    
    return {"success": True, "project": project_data}

@router.put("/projects/{project_id}")
async def update_project(
    project_id: str,
    project: VideoProject,
    current_user = Depends(get_current_user)
):
    """Atualizar projeto"""
    project.id = project_id
    project.updated_at = datetime.utcnow()
    
    cache_key = f"video_project:{current_user.id}:{project_id}"
    await cache_manager.set(cache_key, project.dict(), ttl=86400)
    
    return {"success": True, "project": project}

@router.post("/projects/{project_id}/export")
async def export_project(
    project_id: str,
    export_settings: ExportSettings,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Exportar projeto de vídeo"""
    # Buscar projeto
    cache_key = f"video_project:{current_user.id}:{project_id}"
    project_data = await cache_manager.get(cache_key)
    
    if not project_data:
        raise HTTPException(404, "Projeto não encontrado")
    
    project = VideoProject(**project_data)
    
    # Iniciar exportação em background
    export_id = await video_processor.export_video(project, export_settings, current_user.id)
    
    return {"success": True, "export_id": export_id}

@router.get("/exports/{export_id}/status")
async def get_export_status(
    export_id: str,
    current_user = Depends(get_current_user)
):
    """Status da exportação"""
    status = video_processor.get_export_status(export_id)
    return {"success": True, "status": status}

@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: str,
    current_user = Depends(get_current_user)
):
    """Download do vídeo exportado"""
    status = video_processor.get_export_status(export_id)
    
    if status.get("status") != "completed":
        raise HTTPException(400, "Exportação não concluída")
    
    output_path = status.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(404, "Arquivo não encontrado")
    
    return FileResponse(
        output_path,
        media_type='video/mp4',
        filename=f"video_{export_id}.mp4"
    )

@router.post("/exports/{export_id}/cancel")
async def cancel_export(
    export_id: str,
    current_user = Depends(get_current_user)
):
    """Cancelar exportação"""
    video_processor.cancel_export(export_id)
    return {"success": True, "message": "Exportação cancelada"}

@router.get("/projects")
async def list_projects(
    current_user = Depends(get_current_user)
):
    """Listar projetos do usuário"""
    # Por enquanto, buscar do cache (implementar BD depois)
    pattern = f"video_project:{current_user.id}:*"
    projects = []
    
    # Esta seria a implementação real com busca no BD
    # Por enquanto retornamos lista vazia
    
    return {"success": True, "projects": projects}
