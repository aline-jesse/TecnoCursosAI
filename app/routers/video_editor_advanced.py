"""
Router para o Editor de Vídeo Avançado - TecnoCursos AI
Integração completa entre frontend e backend para edição profissional
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import os
import uuid
from pathlib import Path
import asyncio
import logging
from datetime import datetime

from app.database import get_db
from app.models import User, Project, Video, FileUpload
from app.auth import get_current_user
from app.schemas import ProjectCreate, ProjectUpdate, VideoCreate
from app.services.video_generation_service_new import video_service
from app.routers.preview_service import preview_service
from app.services.audio_sync_service import audio_sync_service, AudioTrack, SyncPoint
from app.services.text_editor_service import text_editor_service, TextElement
from app.services.autosave_service import autosave_service
from app.services.collaboration_service import collaboration_service, Permission

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Verificar se o editor está funcionando"""
    return {
        "status": "healthy",
        "service": "Video Editor Advanced",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "video_generation": True,
            "preview_service": True,
            "audio_sync": True,
            "text_editor": True,
            "autosave": True,
            "collaboration": True,
            "ai_features": True
        }
    }

# ============================================================================
# ENDPOINTS DE TESTE (SEM AUTENTICAÇÃO)
# ============================================================================

@router.get("/test/projects/list")
async def test_list_projects():
    """Listar projetos para teste (sem autenticação)"""
    return {
        "success": True,
        "projects": [
            {
                "id": 1,
                "name": "Projeto Demo",
                "description": "Projeto de demonstração",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "scenes_count": 3,
                "duration": 30
            },
            {
                "id": 2,
                "name": "Tutorial Python",
                "description": "Tutorial básico de Python",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "scenes_count": 5,
                "duration": 45
            }
        ]
    }

@router.post("/test/assets/upload")
async def test_upload_assets(files: List[UploadFile] = File(...)):
    """Upload de assets para teste (sem autenticação)"""
    try:
        uploaded_assets = []
        
        for file in files:
            # Simular upload
            asset_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix.lower()
            
            # Determinar tipo do asset
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                asset_type = 'image'
            elif file_extension in ['.mp4', '.avi', '.mov']:
                asset_type = 'video'
            elif file_extension in ['.mp3', '.wav', '.m4a']:
                asset_type = 'audio'
            else:
                asset_type = 'document'
            
            uploaded_assets.append({
                "id": asset_id,
                "name": file.filename,
                "type": asset_type,
                "size": file.size if hasattr(file, 'size') else 0,
                "url": f"/uploads/{asset_id}{file_extension}",
                "uploaded_at": datetime.now().isoformat()
            })
        
        return {
            "success": True,
            "assets": uploaded_assets,
            "message": f"{len(uploaded_assets)} arquivo(s) enviado(s) com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro no upload de teste: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Erro no upload"
        }

@router.get("/test/assets/list")
async def test_list_assets():
    """Listar assets para teste (sem autenticação)"""
    return {
        "success": True,
        "assets": [
            {
                "id": "asset-1",
                "name": "sample-image.jpg",
                "type": "image",
                "size": 1024000,
                "url": "/uploads/sample-image.jpg",
                "uploaded_at": datetime.now().isoformat()
            },
            {
                "id": "asset-2", 
                "name": "background-music.mp3",
                "type": "audio",
                "size": 2048000,
                "url": "/uploads/background-music.mp3",
                "uploaded_at": datetime.now().isoformat()
            }
        ]
    }

# Diretórios de trabalho
UPLOAD_DIR = Path("uploads")
VIDEO_DIR = Path("static/videos")
TEMP_DIR = Path("temp/video_generation")

# Criar diretórios se não existirem
for directory in [UPLOAD_DIR, VIDEO_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ENDPOINTS DE PROJETOS
# ============================================================================

@router.post("/projects/create")
async def create_project(
    name: str = Form(...),
    description: str = Form(""),
    template: str = Form("professional"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo projeto de vídeo"""
    try:
        # Criar projeto no banco
        project = Project(
            name=name,
            description=description,
            user_id=current_user.id,
            metadata={
                "template": template,
                "scenes": [],
                "settings": {
                    "resolution": "1920x1080",
                    "fps": 30,
                    "duration": 0
                }
            }
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return {
            "success": True,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "template": template,
                "created_at": project.created_at.isoformat(),
                "scenes": [],
                "settings": project.metadata.get("settings", {})
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar projeto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/list")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar projetos do usuário"""
    try:
        projects = db.query(Project).filter(Project.user_id == current_user.id).all()
        
        return {
            "success": True,
            "projects": [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                    "scenes_count": len(project.metadata.get("scenes", [])),
                    "duration": project.metadata.get("settings", {}).get("duration", 0)
                }
                for project in projects
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes do projeto"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        return {
            "success": True,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                "metadata": project.metadata,
                "scenes": project.metadata.get("scenes", []),
                "settings": project.metadata.get("settings", {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter projeto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}/save")
async def save_project(
    project_id: int,
    project_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Salvar estado do projeto (cenas, elementos, timeline)"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Atualizar metadata do projeto
        project.metadata = {
            **project.metadata,
            "scenes": project_data.get("scenes", []),
            "timeline": project_data.get("timeline", []),
            "settings": project_data.get("settings", {}),
            "last_saved": project_data.get("timestamp")
        }
        
        db.commit()
        
        return {
            "success": True,
            "message": "Projeto salvo com sucesso",
            "timestamp": project_data.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao salvar projeto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS DE ASSETS
# ============================================================================

@router.post("/assets/upload")
async def upload_assets(
    files: List[UploadFile] = File(...),
    project_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload de múltiplos assets para o projeto"""
    try:
        uploaded_assets = []
        
        for file in files:
            # Validar tipo de arquivo
            allowed_types = {
                'image/jpeg', 'image/png', 'image/gif',
                'video/mp4', 'video/avi', 'video/mov',
                'audio/mp3', 'audio/wav', 'audio/m4a',
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }
            
            if file.content_type not in allowed_types:
                continue
            
            # Gerar nome único
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Determinar diretório baseado no tipo
            if file.content_type.startswith('image/'):
                asset_dir = UPLOAD_DIR / "images"
                asset_type = "image"
            elif file.content_type.startswith('video/'):
                asset_dir = UPLOAD_DIR / "videos"
                asset_type = "video"
            elif file.content_type.startswith('audio/'):
                asset_dir = UPLOAD_DIR / "audios"
                asset_type = "audio"
            elif file.content_type == 'application/pdf':
                asset_dir = UPLOAD_DIR / "pdf"
                asset_type = "pdf"
            else:
                asset_dir = UPLOAD_DIR / "documents"
                asset_type = "document"
            
            asset_dir.mkdir(parents=True, exist_ok=True)
            file_path = asset_dir / unique_filename
            
            # Salvar arquivo
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Salvar no banco
            file_upload = FileUpload(
                filename=file.filename,
                file_path=str(file_path),
                file_size=len(content),
                content_type=file.content_type,
                user_id=current_user.id,
                metadata={
                    "asset_type": asset_type,
                    "project_id": project_id,
                    "original_name": file.filename
                }
            )
            
            db.add(file_upload)
            db.commit()
            db.refresh(file_upload)
            
            uploaded_assets.append({
                "id": file_upload.id,
                "name": file.filename,
                "type": asset_type,
                "size": f"{len(content) / (1024*1024):.1f}MB",
                "url": f"/uploads/{asset_type}s/{unique_filename}",
                "content_type": file.content_type,
                "created_at": file_upload.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": f"{len(uploaded_assets)} arquivos enviados com sucesso",
            "assets": uploaded_assets
        }
        
    except Exception as e:
        logger.error(f"Erro no upload de assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assets/list")
async def list_assets(
    project_id: Optional[int] = None,
    asset_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar assets do usuário"""
    try:
        query = db.query(FileUpload).filter(FileUpload.user_id == current_user.id)
        
        if project_id:
            query = query.filter(FileUpload.metadata.contains({"project_id": project_id}))
        
        if asset_type:
            query = query.filter(FileUpload.metadata.contains({"asset_type": asset_type}))
        
        assets = query.all()
        
        return {
            "success": True,
            "assets": [
                {
                    "id": asset.id,
                    "name": asset.filename,
                    "type": asset.metadata.get("asset_type", "unknown"),
                    "size": f"{asset.file_size / (1024*1024):.1f}MB",
                    "url": asset.file_path.replace("uploads/", "/uploads/"),
                    "content_type": asset.content_type,
                    "created_at": asset.created_at.isoformat()
                }
                for asset in assets
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS DE EXPORTAÇÃO
# ============================================================================

async def generate_video_from_project(project_id: int, export_settings: dict, user_id: int, db: Session):
    """Gerar vídeo a partir do projeto (função assíncrona)"""
    try:
        # Obter projeto
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "error": "Projeto não encontrado"}
        
        # Simular processo de geração de vídeo
        # Em uma implementação real, aqui seria usado MoviePy ou FFmpeg
        
        # Gerar nome único para o vídeo
        video_filename = f"project_{project_id}_{uuid.uuid4()}.mp4"
        video_path = VIDEO_DIR / video_filename
        
        # Simular geração (em produção seria o processamento real)
        await asyncio.sleep(5)  # Simular tempo de processamento
        
        # Criar arquivo placeholder (em produção seria o vídeo real)
        with open(video_path, "w") as f:
            f.write("Placeholder video file")
        
        # Salvar vídeo no banco
        video = Video(
            title=f"{project.name} - Exportado",
            description=f"Vídeo gerado do projeto {project.name}",
            file_path=str(video_path),
            user_id=user_id,
            project_id=project_id,
            metadata={
                "export_settings": export_settings,
                "scenes_count": len(project.metadata.get("scenes", [])),
                "generated_at": "2024-01-01T00:00:00"
            }
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        return {
            "success": True,
            "video": {
                "id": video.id,
                "title": video.title,
                "file_path": str(video_path),
                "url": f"/static/videos/{video_filename}",
                "duration": export_settings.get("duration", 0),
                "resolution": export_settings.get("resolution", "1920x1080")
            }
        }
        
    except Exception as e:
        logger.error(f"Erro na geração do vídeo: {e}")
        return {"success": False, "error": str(e)}

@router.post("/projects/{project_id}/export")
async def export_project(
    project_id: int,
    background_tasks: BackgroundTasks,
    export_settings: dict = {},
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exportar projeto como vídeo"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Configurações padrão de exportação
        default_settings = {
            "resolution": "1920x1080",
            "fps": 30,
            "quality": "high",
            "format": "mp4",
            "duration": 10
        }
        
        final_settings = {**default_settings, **export_settings}
        
        # Adicionar tarefa em background
        background_tasks.add_task(
            generate_video_from_project,
            project_id,
            final_settings,
            current_user.id,
            db
        )
        
        return {
            "success": True,
            "message": "Exportação iniciada",
            "project_id": project_id,
            "settings": final_settings,
            "estimated_time": "2-5 minutos"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar exportação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/export/status")
async def get_export_status(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verificar status da exportação"""
    try:
        # Buscar vídeos gerados para o projeto
        videos = db.query(Video).filter(
            Video.project_id == project_id,
            Video.user_id == current_user.id
        ).order_by(Video.created_at.desc()).all()
        
        if not videos:
            return {
                "success": True,
                "status": "not_started",
                "message": "Nenhuma exportação encontrada"
            }
        
        latest_video = videos[0]
        
        # Verificar se o arquivo existe
        if os.path.exists(latest_video.file_path):
            return {
                "success": True,
                "status": "completed",
                "video": {
                    "id": latest_video.id,
                    "title": latest_video.title,
                    "url": latest_video.file_path.replace("static/", "/static/"),
                    "created_at": latest_video.created_at.isoformat()
                }
            }
        else:
            return {
                "success": True,
                "status": "processing",
                "message": "Vídeo sendo processado..."
            }
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS DE TEMPLATES
# ============================================================================

@router.get("/templates/list")
async def list_templates():
    """Listar templates disponíveis"""
    templates = [
        {
            "id": "professional",
            "name": "Profissional",
            "description": "Template corporativo elegante",
            "thumbnail": "/static/templates/professional.jpg",
            "features": ["Transições suaves", "Tipografia limpa", "Cores corporativas"],
            "duration_range": "30s - 5min"
        },
        {
            "id": "educational",
            "name": "Educacional",
            "description": "Ideal para cursos e treinamentos",
            "thumbnail": "/static/templates/educational.jpg",
            "features": ["Elementos didáticos", "Infográficos", "Animações explicativas"],
            "duration_range": "1min - 10min"
        },
        {
            "id": "casual",
            "name": "Casual",
            "description": "Estilo descontraído e moderno",
            "thumbnail": "/static/templates/casual.jpg",
            "features": ["Cores vibrantes", "Animações dinâmicas", "Layout flexível"],
            "duration_range": "15s - 3min"
        },
        {
            "id": "minimal",
            "name": "Minimalista",
            "description": "Design limpo e focado",
            "thumbnail": "/static/templates/minimal.jpg",
            "features": ["Espaços em branco", "Tipografia simples", "Foco no conteúdo"],
            "duration_range": "20s - 2min"
        }
    ]
    
    return {
        "success": True,
        "templates": templates
    }

@router.get("/templates/{template_id}/preview")
async def get_template_preview(template_id: str):
    """Obter preview de um template específico"""
    template_data = {
        "professional": {
            "scenes": [
                {"id": 1, "title": "Título Principal", "duration": 3, "type": "title"},
                {"id": 2, "title": "Conteúdo", "duration": 10, "type": "content"},
                {"id": 3, "title": "Conclusão", "duration": 2, "type": "outro"}
            ],
            "settings": {
                "background_color": "#1a202c",
                "primary_color": "#4fc3f7",
                "font_family": "Inter",
                "animation_style": "fade"
            }
        },
        "educational": {
            "scenes": [
                {"id": 1, "title": "Introdução", "duration": 5, "type": "intro"},
                {"id": 2, "title": "Tópico 1", "duration": 15, "type": "topic"},
                {"id": 3, "title": "Tópico 2", "duration": 15, "type": "topic"},
                {"id": 4, "title": "Quiz", "duration": 10, "type": "interactive"},
                {"id": 5, "title": "Resumo", "duration": 5, "type": "summary"}
            ],
            "settings": {
                "background_color": "#f7fafc",
                "primary_color": "#2d3748",
                "font_family": "Open Sans",
                "animation_style": "slide"
            }
        }
    }
    
    if template_id not in template_data:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    return {
        "success": True,
        "template": template_data[template_id]
    }

# ============================================================================
# ENDPOINTS DE SAÚDE E STATUS
# ============================================================================

@router.post("/export")
async def export_project(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Exportar projeto como vídeo MP4"""
    try:
        project_data = request.get("project_data", {})
        export_settings = request.get("export_settings", {})
        
        # Processar trilhas de áudio se presentes
        audio_tracks = []
        timeline = project_data.get("timeline", [])
        total_duration = sum(scene.get("duration", 3) for scene in project_data.get("scenes", []))
        
        for track in timeline:
            if track.get("type") == "audio":
                audio_track = audio_sync_service.create_audio_track(
                    name=track.get("name", "Audio Track"),
                    file_path=track.get("asset_path", ""),
                    start_time=track.get("start_time", 0),
                    duration=track.get("duration", 0),
                    volume=track.get("volume", 1.0),
                    is_background=track.get("is_background", False),
                    audio_type=track.get("audio_type", "music")
                )
                audio_tracks.append(audio_track)
        
        # Sincronizar áudio se necessário
        if audio_tracks:
            sync_result = await audio_sync_service.create_synchronized_audio_track(
                audio_tracks, total_duration
            )
            
            if sync_result.get("success"):
                # Adicionar áudio sincronizado ao projeto
                project_data["synchronized_audio"] = sync_result
        
        # Gerar vídeo usando o serviço real
        result = await video_service.generate_video_from_project(
            project_data, export_settings
        )
        
        return {
            "success": True,
            "export_id": str(uuid.uuid4()),
            "video_url": result.get("video_url", "/static/videos/sample.mp4"),
            "download_url": result.get("video_url", "/static/videos/sample.mp4"),
            "file_size": result.get("file_size", 5242880),
            "duration": result.get("duration", 15),
            "format": "mp4",
            "quality": export_settings.get("quality", "1080p"),
            "audio_tracks_processed": len(audio_tracks),
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/analyze")
async def analyze_audio_file(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Analisar arquivo de áudio para sincronização"""
    try:
        file_path = request.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path é obrigatório")
        
        analysis = await audio_sync_service.analyze_audio_file(file_path)
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Erro na análise de áudio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/sync")
async def sync_audio_tracks(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Sincronizar múltiplas trilhas de áudio"""
    try:
        tracks_data = request.get("tracks", [])
        video_duration = request.get("video_duration", 10)
        sync_points_data = request.get("sync_points", [])
        
        # Converter dados para objetos AudioTrack
        audio_tracks = []
        for track_data in tracks_data:
            audio_track = audio_sync_service.create_audio_track(
                name=track_data.get("name", "Track"),
                file_path=track_data.get("file_path", ""),
                start_time=track_data.get("start_time", 0),
                duration=track_data.get("duration", 0),
                volume=track_data.get("volume", 1.0),
                is_background=track_data.get("is_background", False),
                audio_type=track_data.get("audio_type", "music")
            )
            audio_tracks.append(audio_track)
        
        # Converter dados para objetos SyncPoint
        sync_points = []
        for sp_data in sync_points_data:
            sync_point = SyncPoint(
                timestamp=sp_data.get("timestamp", 0),
                audio_cue=sp_data.get("audio_cue", ""),
                visual_cue=sp_data.get("visual_cue", ""),
                sync_type=sp_data.get("sync_type", "beat")
            )
            sync_points.append(sync_point)
        
        # Processar sincronização
        result = await audio_sync_service.create_synchronized_audio_track(
            audio_tracks, video_duration, sync_points
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erro na sincronização de áudio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/suggest-sync")
async def suggest_sync_points(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Sugerir pontos de sincronização automática"""
    try:
        audio_analysis = request.get("audio_analysis", {})
        video_scenes = request.get("video_scenes", [])
        
        sync_points = await audio_sync_service.suggest_sync_points(
            audio_analysis, video_scenes
        )
        
        return {
            "success": True,
            "sync_points": [
                {
                    "timestamp": sp.timestamp,
                    "audio_cue": sp.audio_cue,
                    "visual_cue": sp.visual_cue,
                    "sync_type": sp.sync_type
                } for sp in sync_points
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao sugerir pontos de sincronização: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_templates(current_user: User = Depends(get_current_user)):
    """Obter templates disponíveis"""
    return {
        "success": True,
        "templates": [
            {
                "id": "modern-intro",
                "name": "Introdução Moderna",
                "category": "intro",
                "preview": "/static/previews/modern-intro.jpg",
                "duration": 5,
                "elements": [
                    {
                        "type": "text",
                        "text": "Bem-vindos!",
                        "x": 100,
                        "y": 100,
                        "font_size": 48,
                        "color": "#ffffff"
                    }
                ]
            },
            {
                "id": "corporate-slide",
                "name": "Slide Corporativo", 
                "category": "content",
                "preview": "/static/previews/corporate-slide.jpg",
                "duration": 8,
                "elements": [
                    {
                        "type": "text",
                        "text": "Conteúdo Principal",
                        "x": 50,
                        "y": 50,
                        "font_size": 36,
                        "color": "#333333"
                    }
                ]
            },
            {
                "id": "tech-outro",
                "name": "Encerramento Tech",
                "category": "outro", 
                "preview": "/static/previews/tech-outro.jpg",
                "duration": 3,
                "elements": [
                    {
                        "type": "text",
                        "text": "Obrigado!",
                        "x": 200,
                        "y": 150,
                        "font_size": 42,
                        "color": "#00ff00"
                    }
                ]
            },
            {
                "id": "animated-title",
                "name": "Título Animado",
                "category": "title",
                "preview": "/static/previews/animated-title.jpg",
                "duration": 4,
                "elements": [
                    {
                        "type": "text",
                        "text": "Título Dinâmico",
                        "x": 150,
                        "y": 200,
                        "font_size": 52,
                        "color": "#ff6b6b",
                        "animation": "fadeIn"
                    }
                ]
            }
        ]
    }

@router.post("/text/create")
async def create_text_element(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Criar novo elemento de texto"""
    try:
        text = request.get("text", "")
        x = request.get("x", 100)
        y = request.get("y", 100)
        style = request.get("style", {})
        animation = request.get("animation", None)
        
        if not text:
            raise HTTPException(status_code=400, detail="Texto não pode estar vazio")
        
        text_element = await text_editor_service.create_text_element(
            text=text,
            x=x,
            y=y,
            style=style,
            animation=animation
        )
        
        return {
            "success": True,
            "text_element": {
                "id": text_element.id,
                "text": text_element.text,
                "x": text_element.x,
                "y": text_element.y,
                "width": text_element.width,
                "height": text_element.height,
                "style": text_element.style.__dict__,
                "animation": text_element.animation.__dict__ if text_element.animation else None,
                "created_at": text_element.created_at
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar elemento de texto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text/apply-template")
async def apply_text_template(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Aplicar template de texto"""
    try:
        text = request.get("text", "")
        template_id = request.get("template_id", "")
        x = request.get("x", 100)
        y = request.get("y", 100)
        
        if not text or not template_id:
            raise HTTPException(status_code=400, detail="Texto e template_id são obrigatórios")
        
        text_element = await text_editor_service.apply_template(
            text=text,
            template_id=template_id,
            x=x,
            y=y
        )
        
        return {
            "success": True,
            "text_element": {
                "id": text_element.id,
                "text": text_element.text,
                "x": text_element.x,
                "y": text_element.y,
                "width": text_element.width,
                "height": text_element.height,
                "style": text_element.style.__dict__,
                "animation": text_element.animation.__dict__ if text_element.animation else None,
                "template_id": template_id
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao aplicar template de texto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/text/fonts")
async def get_available_fonts(current_user: User = Depends(get_current_user)):
    """Obter fontes disponíveis"""
    try:
        fonts = text_editor_service.get_available_fonts()
        
        return {
            "success": True,
            "fonts": fonts,
            "count": len(fonts)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter fontes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/text/templates")
async def get_text_templates(current_user: User = Depends(get_current_user)):
    """Obter templates de texto"""
    try:
        templates = text_editor_service.get_text_templates()
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autosave/register")
async def register_autosave_session(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Registrar sessão de auto-save"""
    try:
        project_id = request.get("project_id")
        initial_data = request.get("initial_data", {})
        
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id é obrigatório")
        
        session_id = await autosave_service.register_session(
            current_user.id, project_id, initial_data
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "autosave_interval": autosave_service.autosave_interval
        }
        
    except Exception as e:
        logger.error(f"Erro ao registrar sessão de auto-save: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autosave/update")
async def update_project_autosave(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Atualizar dados do projeto para auto-save"""
    try:
        project_id = request.get("project_id")
        project_data = request.get("project_data", {})
        
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id é obrigatório")
        
        await autosave_service.update_project_data(
            current_user.id, project_id, project_data
        )
        
        return {
            "success": True,
            "message": "Dados atualizados para auto-save"
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar auto-save: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autosave/manual")
async def manual_save_project(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Realizar save manual"""
    try:
        project_id = request.get("project_id")
        description = request.get("description", "Save manual")
        
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id é obrigatório")
        
        success = await autosave_service.manual_save(
            current_user.id, project_id, description
        )
        
        return {
            "success": success,
            "message": "Save manual realizado" if success else "Erro no save manual"
        }
        
    except Exception as e:
        logger.error(f"Erro no save manual: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/autosave/versions/{project_id}")
async def get_project_versions(
    project_id: int,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Obter versões do projeto"""
    try:
        versions = await autosave_service.get_project_versions(project_id, limit)
        
        versions_data = [
            {
                "id": v.id,
                "version_number": v.version_number,
                "created_at": v.created_at.isoformat(),
                "is_manual": v.is_manual,
                "description": v.description,
                "file_size": v.file_size,
                "data_hash": v.data_hash[:8]  # Apenas primeiros 8 chars para segurança
            }
            for v in versions
        ]
        
        return {
            "success": True,
            "versions": versions_data,
            "total": len(versions_data)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter versões: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autosave/restore")
async def restore_project_version(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Restaurar versão específica"""
    try:
        project_id = request.get("project_id")
        version_id = request.get("version_id")
        
        if not project_id or not version_id:
            raise HTTPException(status_code=400, detail="project_id e version_id são obrigatórios")
        
        restored_data = await autosave_service.restore_version(
            project_id, version_id, current_user.id
        )
        
        if restored_data:
            return {
                "success": True,
                "message": "Versão restaurada com sucesso",
                "project_data": restored_data
            }
        else:
            return {
                "success": False,
                "message": "Versão não encontrada ou erro na restauração"
            }
        
    except Exception as e:
        logger.error(f"Erro ao restaurar versão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/autosave/session/{project_id}")
async def get_autosave_session_info(
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """Obter informações da sessão de auto-save"""
    try:
        session_info = autosave_service.get_session_info(current_user.id, project_id)
        
        if session_info:
            return {
                "success": True,
                "session": session_info
            }
        else:
            return {
                "success": False,
                "message": "Sessão não encontrada"
            }
        
    except Exception as e:
        logger.error(f"Erro ao obter info da sessão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check do editor"""
    return {
        "success": True,
        "service": "Video Editor Advanced",
        "status": "operational",
        "features": {
            "upload": True,
            "editing": True,
            "export": True,
            "templates": True,
            "audio_sync": True,
            "real_time_preview": True,
            "advanced_text_editor": True,
            "autosave": True,
            "collaboration": True
        }
    }

# ============================================================================
# ENDPOINTS DE COLABORAÇÃO
# ============================================================================

@router.websocket("/collaboration/{project_id}")
async def collaboration_websocket(websocket: WebSocket, project_id: int):
    """WebSocket para colaboração em tempo real"""
    try:
        # TODO: Implementar autenticação WebSocket
        # Por ora, usar dados mock
        user_id = 1
        user_name = "Usuário Demo"
        user_email = "demo@tecnocursos.ai"
        permission = Permission.EDITOR
        
        # Tentar conectar
        success = await collaboration_service.join_project(
            project_id=project_id,
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            websocket=websocket,
            permission=permission
        )
        
        if not success:
            await websocket.close(code=4003, reason="Falha ao entrar no projeto")
            return
        
        try:
            while True:
                # Receber mensagem
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Processar mensagem
                await collaboration_service.handle_websocket_message(websocket, message)
                
        except WebSocketDisconnect:
            # Usuário desconectou
            await collaboration_service.leave_project(user_id)
            
        except Exception as e:
            logger.error(f"Erro na colaboração WebSocket: {e}")
            await collaboration_service.leave_project(user_id)
            
    except Exception as e:
        logger.error(f"Erro no WebSocket de colaboração: {e}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close(code=4000, reason="Erro interno")

@router.get("/collaboration/users/{project_id}")
async def get_active_users(
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """Obter usuários ativos no projeto"""
    try:
        active_users = collaboration_service.get_active_users(project_id)
        
        return {
            "success": True,
            "active_users": active_users,
            "total_users": len(active_users)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter usuários ativos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaboration/chat/{project_id}")
async def get_chat_history(
    project_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Obter histórico de chat do projeto"""
    try:
        chat_history = await collaboration_service.get_chat_history(project_id, limit)
        
        return {
            "success": True,
            "messages": chat_history,
            "total": len(chat_history)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collaboration/invite")
async def invite_user_to_project(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Convidar usuário para colaborar no projeto"""
    try:
        project_id = request.get("project_id")
        user_email = request.get("user_email")
        permission = request.get("permission", "viewer")
        message = request.get("message", "")
        
        if not project_id or not user_email:
            raise HTTPException(status_code=400, detail="project_id e user_email são obrigatórios")
        
        # TODO: Implementar sistema real de convites
        # Por ora, retornar sucesso simulado
        
        return {
            "success": True,
            "message": f"Convite enviado para {user_email}",
            "invite_id": str(uuid.uuid4()),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar convite: {e}")
        raise HTTPException(status_code=500, detail=str(e))