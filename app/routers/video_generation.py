#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router para API de Geração de Vídeos Automática - TecnoCursos AI

Este módulo implementa endpoints REST completos para criação automatizada
de vídeos a partir de texto, incluindo pipeline TTS, templates avançados,
processamento em batch e otimização para plataformas.

Funcionalidades:
- Pipeline completo Texto → TTS → Vídeo
- Templates visuais avançados
- Múltiplas resoluções e formatos
- Processamento em batch
- Otimização para plataformas (YouTube, Instagram, TikTok, etc.)
- Upload e download de vídeos
- Monitoramento de progresso

Autor: TecnoCursos AI
Data: 17/01/2025
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import time
import uuid
from datetime import datetime

# Importar funções de geração de vídeo
try:
    from app.utils import (
        create_video_from_text_and_audio,
        create_video_pipeline_automatic,
        create_batch_videos,
        optimize_video_for_platform
    )
    VIDEO_FUNCTIONS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Funções de vídeo não disponíveis: {e}")
    VIDEO_FUNCTIONS_AVAILABLE = False

# Importar dependências do sistema
try:
    from app.auth import get_current_user
    from app.models import User
    from app.database import get_db
    AUTH_AVAILABLE = True
except ImportError:
    print("⚠️ Sistema de autenticação não disponível")
    AUTH_AVAILABLE = False

# Configurar router
router = APIRouter(
    prefix="/api/videos",
    tags=["Video Generation"],
    responses={
        404: {"description": "Video not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# ===============================================================
# MODELOS PYDANTIC PARA VALIDAÇÃO DE DADOS
# ===============================================================

class VideoCreationRequest(BaseModel):
    """Modelo para requisição de criação de vídeo simples."""
    text: str = Field(..., min_length=10, max_length=2000, description="Texto para o vídeo")
    audio_file_id: Optional[str] = Field(None, description="ID do arquivo de áudio (opcional)")
    template: str = Field("modern", description="Template visual")
    resolution: str = Field("hd", description="Resolução do vídeo")
    animations: bool = Field(True, description="Ativar animações")
    background_style: str = Field("gradient", description="Estilo do background")

class PipelineVideoRequest(BaseModel):
    """Modelo para requisição de pipeline completo (TTS + Vídeo)."""
    text: str = Field(..., min_length=10, max_length=2000, description="Texto para narração")
    voice: str = Field("pt", description="Idioma/voz para TTS")
    template: str = Field("modern", description="Template visual")
    resolution: str = Field("hd", description="Resolução do vídeo")
    animations: bool = Field(True, description="Ativar animações")
    background_style: str = Field("gradient", description="Estilo do background")
    title: Optional[str] = Field(None, description="Título do vídeo")

class BatchVideoRequest(BaseModel):
    """Modelo para requisição de criação em batch."""
    texts: List[str] = Field(..., min_items=1, max_items=50, description="Lista de textos")
    template: str = Field("modern", description="Template para todos os vídeos")
    resolution: str = Field("hd", description="Resolução dos vídeos")
    voice: str = Field("pt", description="Voz para TTS")
    project_name: Optional[str] = Field(None, description="Nome do projeto")

class PlatformOptimizationRequest(BaseModel):
    """Modelo para requisição de otimização para plataforma."""
    video_id: str = Field(..., description="ID do vídeo para otimizar")
    platform: str = Field(..., description="Plataforma alvo")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Configurações customizadas")

class VideoResponse(BaseModel):
    """Modelo de resposta padrão para operações de vídeo."""
    success: bool
    video_id: str
    message: str
    data: Optional[Dict[str, Any]] = None

# ===============================================================
# ENDPOINTS PRINCIPAIS DE GERAÇÃO DE VÍDEO
# ===============================================================

@router.post("/create", response_model=VideoResponse)
async def create_video_from_text(
    request: VideoCreationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Cria vídeo a partir de texto e áudio existente.
    
    Endpoint para criação de vídeo usando texto e arquivo de áudio já disponível.
    Suporta templates avançados, múltiplas resoluções e animações.
    """
    try:
        if not VIDEO_FUNCTIONS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de geração de vídeo temporariamente indisponível"
            )
        
        # Gerar ID único para o vídeo
        video_id = f"video_{uuid.uuid4().hex[:12]}"
        
        # Verificar se áudio foi fornecido
        if request.audio_file_id:
            audio_path = f"app/static/audios/{request.audio_file_id}"
            if not os.path.exists(audio_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Arquivo de áudio não encontrado: {request.audio_file_id}"
                )
        else:
            # Usar pipeline completo com TTS
            return await create_video_pipeline(
                PipelineVideoRequest(
                    text=request.text,
                    template=request.template,
                    resolution=request.resolution,
                    animations=request.animations,
                    background_style=request.background_style
                ),
                background_tasks,
                current_user
            )
        
        # Caminho de saída
        output_path = f"app/static/videos/{video_id}.mp4"
        
        # Processar vídeo em background
        background_tasks.add_task(
            process_video_creation,
            video_id,
            request.text,
            audio_path,
            output_path,
            request.template,
            request.resolution,
            request.animations,
            request.background_style,
            current_user.id if current_user else None
        )
        
        return VideoResponse(
            success=True,
            video_id=video_id,
            message="Vídeo em processamento. Use o ID para verificar o status.",
            data={
                "estimated_completion": "2-5 minutos",
                "status_endpoint": f"/api/videos/{video_id}/status",
                "download_endpoint": f"/api/videos/{video_id}/download"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/pipeline", response_model=VideoResponse)
async def create_video_pipeline(
    request: PipelineVideoRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Pipeline completo: Texto → TTS → Vídeo.
    
    Endpoint que automatiza todo o processo de criação, desde geração
    de áudio com TTS até vídeo final com templates avançados.
    """
    try:
        if not VIDEO_FUNCTIONS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de pipeline de vídeo temporariamente indisponível"
            )
        
        # Gerar ID único
        video_id = f"pipeline_{uuid.uuid4().hex[:12]}"
        output_path = f"app/static/videos/{video_id}.mp4"
        
        # Processar pipeline em background
        background_tasks.add_task(
            process_video_pipeline,
            video_id,
            request.text,
            output_path,
            request.voice,
            request.template,
            request.resolution,
            request.animations,
            request.title,
            current_user.id if current_user else None
        )
        
        return VideoResponse(
            success=True,
            video_id=video_id,
            message="Pipeline iniciado. TTS + Vídeo em processamento.",
            data={
                "stages": ["TTS Generation", "Video Creation", "Finalization"],
                "estimated_completion": "3-8 minutos",
                "status_endpoint": f"/api/videos/{video_id}/status",
                "preview_endpoint": f"/api/videos/{video_id}/preview"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no pipeline: {str(e)}")


@router.post("/batch", response_model=VideoResponse)
async def create_batch_videos_endpoint(
    request: BatchVideoRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Criação de múltiplos vídeos em batch.
    
    Processa uma lista de textos criando vídeos individuais
    com configurações uniformes. Ideal para automação.
    """
    try:
        if not VIDEO_FUNCTIONS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de batch não disponível"
            )
        
        if len(request.texts) > 50:
            raise HTTPException(
                status_code=400,
                detail="Máximo de 50 vídeos por batch"
            )
        
        # Gerar ID único para o batch
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        output_dir = f"app/static/videos/batch/{batch_id}"
        
        # Processar batch em background
        background_tasks.add_task(
            process_batch_videos,
            batch_id,
            request.texts,
            output_dir,
            request.template,
            request.resolution,
            request.voice,
            request.project_name,
            current_user.id if current_user else None
        )
        
        return VideoResponse(
            success=True,
            video_id=batch_id,
            message=f"Batch de {len(request.texts)} vídeos iniciado.",
            data={
                "total_videos": len(request.texts),
                "estimated_completion": f"{len(request.texts) * 2}-{len(request.texts) * 5} minutos",
                "batch_status_endpoint": f"/api/videos/batch/{batch_id}/status",
                "download_zip_endpoint": f"/api/videos/batch/{batch_id}/download"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no batch: {str(e)}")


# ===============================================================
# ENDPOINTS DE OTIMIZAÇÃO E PLATAFORMAS
# ===============================================================

@router.post("/optimize", response_model=VideoResponse)
async def optimize_video_for_platform_endpoint(
    request: PlatformOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Otimiza vídeo para plataformas específicas.
    
    Converte vídeos existentes para formatos otimizados para
    YouTube, Instagram, TikTok, LinkedIn, etc.
    """
    try:
        if not VIDEO_FUNCTIONS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de otimização indisponível"
            )
        
        # Verificar se vídeo existe
        original_path = f"app/static/videos/{request.video_id}.mp4"
        if not os.path.exists(original_path):
            raise HTTPException(
                status_code=404,
                detail=f"Vídeo não encontrado: {request.video_id}"
            )
        
        # Plataformas suportadas
        supported_platforms = ["youtube", "instagram", "tiktok", "linkedin", "twitter"]
        if request.platform not in supported_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Plataforma não suportada. Válidas: {supported_platforms}"
            )
        
        # Gerar ID para vídeo otimizado
        optimized_id = f"{request.video_id}_{request.platform}"
        
        # Processar otimização em background
        background_tasks.add_task(
            process_video_optimization,
            optimized_id,
            original_path,
            request.platform,
            request.custom_settings,
            current_user.id if current_user else None
        )
        
        return VideoResponse(
            success=True,
            video_id=optimized_id,
            message=f"Otimização para {request.platform} iniciada.",
            data={
                "original_video": request.video_id,
                "target_platform": request.platform,
                "estimated_completion": "1-3 minutos",
                "status_endpoint": f"/api/videos/{optimized_id}/status"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na otimização: {str(e)}")


# ===============================================================
# ENDPOINTS DE STATUS E MONITORAMENTO
# ===============================================================

@router.get("/{video_id}/status")
async def get_video_status(
    video_id: str,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Verifica o status de processamento de um vídeo.
    
    Retorna informações sobre o progresso, estágio atual
    e estimativa de conclusão.
    """
    try:
        # Verificar se existe arquivo de status
        status_file = f"app/static/videos/status/{video_id}.json"
        
        if os.path.exists(status_file):
            import json
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            return status_data
        
        # Verificar se vídeo já está pronto
        video_path = f"app/static/videos/{video_id}.mp4"
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            return {
                "video_id": video_id,
                "status": "completed",
                "progress": 100,
                "stage": "finished",
                "file_size": file_size,
                "download_url": f"/api/videos/{video_id}/download",
                "completed_at": datetime.fromtimestamp(os.path.getmtime(video_path)).isoformat()
            }
        
        # Status padrão se não encontrado
        return {
            "video_id": video_id,
            "status": "not_found",
            "progress": 0,
            "message": "Vídeo não encontrado ou ainda não iniciado"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")


@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Download de vídeo gerado.
    
    Retorna o arquivo de vídeo para download direto.
    """
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
# ENDPOINTS DE UPLOAD E GESTÃO
# ===============================================================

@router.post("/upload-audio")
async def upload_audio_for_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Upload de arquivo de áudio para uso em vídeos.
    
    Permite upload de arquivos de áudio (WAV, MP3) para
    usar como narração em vídeos customizados.
    """
    try:
        # Validar tipo de arquivo
        allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de arquivo não suportado. Permitidos: {allowed_types}"
            )
        
        # Gerar nome único
        file_id = f"audio_{uuid.uuid4().hex[:12]}"
        file_extension = os.path.splitext(file.filename)[1]
        audio_path = f"app/static/audios/{file_id}{file_extension}"
        
        # Garantir que diretório existe
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        # Salvar arquivo
        with open(audio_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Informações do arquivo
        file_size = os.path.getsize(audio_path)
        
        return {
            "success": True,
            "audio_id": file_id,
            "filename": file.filename,
            "file_size": file_size,
            "content_type": file.content_type,
            "message": "Áudio carregado com sucesso. Use audio_id para criar vídeos."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")


@router.get("/templates")
async def list_available_templates():
    """
    Lista templates disponíveis para vídeos.
    
    Retorna informações sobre todos os templates visuais
    disponíveis com suas características.
    """
    try:
        templates = {
            "modern": {
                "name": "Modern",
                "description": "Design moderno com gradientes azuis",
                "best_for": ["Tecnologia", "Negócios", "Apresentações"],
                "colors": ["Azul", "Branco", "Cinza"],
                "animations": ["fade_in", "slide_up", "text_glow"]
            },
            "corporate": {
                "name": "Corporate",
                "description": "Estilo corporativo profissional",
                "best_for": ["Empresas", "Relatórios", "Treinamentos"],
                "colors": ["Azul escuro", "Branco", "Cinza"],
                "animations": ["fade_in", "professional_reveal"]
            },
            "tech": {
                "name": "Tech",
                "description": "Visual futurista com efeitos neon",
                "best_for": ["Tecnologia", "Gaming", "Inovação"],
                "colors": ["Verde neon", "Preto", "Cinza escuro"],
                "animations": ["matrix_effect", "neon_glow", "cyber_reveal"]
            },
            "education": {
                "name": "Education",
                "description": "Design amigável para educação",
                "best_for": ["Cursos", "Tutoriais", "Ensino"],
                "colors": ["Laranja", "Bege", "Marrom claro"],
                "animations": ["friendly_bounce", "warm_fade"]
            },
            "minimal": {
                "name": "Minimal",
                "description": "Design limpo e minimalista",
                "best_for": ["Apresentações simples", "Texto focado"],
                "colors": ["Branco", "Cinza", "Preto"],
                "animations": ["subtle_fade"]
            }
        }
        
        return {
            "success": True,
            "templates": templates,
            "total_templates": len(templates),
            "default_template": "modern"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar templates: {str(e)}")


# ===============================================================
# FUNÇÕES DE PROCESSAMENTO EM BACKGROUND
# ===============================================================

async def process_video_creation(
    video_id: str, text: str, audio_path: str, output_path: str,
    template: str, resolution: str, animations: bool, background_style: str,
    user_id: Optional[int] = None
):
    """Processa criação de vídeo em background."""
    try:
        # Salvar status inicial
        _save_video_status(video_id, {
            "status": "processing",
            "progress": 10,
            "stage": "video_creation",
            "started_at": datetime.now().isoformat()
        })
        
        # Criar vídeo
        result = create_video_from_text_and_audio(
            text=text,
            audio_path=audio_path,
            output_path=output_path,
            template=template,
            resolution=resolution,
            animations=animations,
            background_style=background_style
        )
        
        # Atualizar status final
        if result['success']:
            _save_video_status(video_id, {
                "status": "completed",
                "progress": 100,
                "stage": "finished",
                "result": result,
                "completed_at": datetime.now().isoformat()
            })
        else:
            _save_video_status(video_id, {
                "status": "failed",
                "progress": 0,
                "stage": "error",
                "error": result['error'],
                "failed_at": datetime.now().isoformat()
            })
            
    except Exception as e:
        _save_video_status(video_id, {
            "status": "failed",
            "progress": 0,
            "stage": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })


async def process_video_pipeline(
    video_id: str, text: str, output_path: str, voice: str,
    template: str, resolution: str, animations: bool, title: Optional[str],
    user_id: Optional[int] = None
):
    """Processa pipeline completo em background."""
    try:
        # Status inicial
        _save_video_status(video_id, {
            "status": "processing",
            "progress": 5,
            "stage": "tts_generation",
            "started_at": datetime.now().isoformat()
        })
        
        # Executar pipeline
        result = create_video_pipeline_automatic(
            text=text,
            output_path=output_path,
            voice=voice,
            template=template,
            resolution=resolution,
            animations=animations
        )
        
        # Status final
        if result['success']:
            _save_video_status(video_id, {
                "status": "completed",
                "progress": 100,
                "stage": "finished",
                "result": result,
                "completed_at": datetime.now().isoformat()
            })
        else:
            _save_video_status(video_id, {
                "status": "failed",
                "progress": 0,
                "stage": result.get('stage', 'unknown'),
                "error": result['error'],
                "failed_at": datetime.now().isoformat()
            })
            
    except Exception as e:
        _save_video_status(video_id, {
            "status": "failed",
            "progress": 0,
            "stage": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })


async def process_batch_videos(
    batch_id: str, texts: List[str], output_dir: str,
    template: str, resolution: str, voice: str, project_name: Optional[str],
    user_id: Optional[int] = None
):
    """Processa batch de vídeos em background."""
    try:
        # Status inicial
        _save_video_status(batch_id, {
            "status": "processing",
            "progress": 0,
            "stage": "batch_processing",
            "total_videos": len(texts),
            "completed_videos": 0,
            "started_at": datetime.now().isoformat()
        })
        
        # Executar batch
        result = create_batch_videos(
            texts=texts,
            output_dir=output_dir,
            template=template,
            resolution=resolution
        )
        
        # Status final
        if result['success']:
            _save_video_status(batch_id, {
                "status": "completed",
                "progress": 100,
                "stage": "finished",
                "result": result,
                "completed_at": datetime.now().isoformat()
            })
        else:
            _save_video_status(batch_id, {
                "status": "failed",
                "progress": 0,
                "stage": "batch_error",
                "error": result['error'],
                "failed_at": datetime.now().isoformat()
            })
            
    except Exception as e:
        _save_video_status(batch_id, {
            "status": "failed",
            "progress": 0,
            "stage": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })


async def process_video_optimization(
    optimized_id: str, original_path: str, platform: str,
    custom_settings: Optional[Dict], user_id: Optional[int] = None
):
    """Processa otimização de vídeo em background."""
    try:
        # Status inicial
        _save_video_status(optimized_id, {
            "status": "processing",
            "progress": 10,
            "stage": "optimization",
            "platform": platform,
            "started_at": datetime.now().isoformat()
        })
        
        # Executar otimização
        result = optimize_video_for_platform(
            input_path=original_path,
            platform=platform
        )
        
        # Status final
        if result['success']:
            _save_video_status(optimized_id, {
                "status": "completed",
                "progress": 100,
                "stage": "finished",
                "result": result,
                "completed_at": datetime.now().isoformat()
            })
        else:
            _save_video_status(optimized_id, {
                "status": "failed",
                "progress": 0,
                "stage": "optimization_error",
                "error": result['error'],
                "failed_at": datetime.now().isoformat()
            })
            
    except Exception as e:
        _save_video_status(optimized_id, {
            "status": "failed",
            "progress": 0,
            "stage": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })


def _save_video_status(video_id: str, status_data: dict):
    """Salva status do vídeo em arquivo JSON."""
    try:
        status_dir = "app/static/videos/status"
        os.makedirs(status_dir, exist_ok=True)
        
        status_file = os.path.join(status_dir, f"{video_id}.json")
        
        # Adicionar ID e timestamp
        status_data['video_id'] = video_id
        status_data['last_updated'] = datetime.now().isoformat()
        
        import json
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"⚠️ Erro ao salvar status: {e}")


# ===============================================================
# INFORMAÇÕES DO ROUTER
# ===============================================================

@router.get("/info")
async def get_video_generation_info():
    """
    Informações sobre o serviço de geração de vídeos.
    
    Retorna capacidades, limitações e configurações do sistema.
    """
    return {
        "service": "TecnoCursos AI - Video Generation API",
        "version": "2.0.0",
        "status": "operational" if VIDEO_FUNCTIONS_AVAILABLE else "limited",
        "capabilities": {
            "text_to_video": True,
            "tts_pipeline": True,
            "batch_processing": True,
            "platform_optimization": True,
            "custom_templates": True,
            "multiple_resolutions": True,
            "animations": True
        },
        "supported_formats": {
            "input_audio": ["WAV", "MP3"],
            "output_video": ["MP4"],
            "resolutions": ["HD (720p)", "FHD (1080p)", "4K (2160p)"]
        },
        "templates": ["modern", "corporate", "tech", "education", "minimal"],
        "platforms": ["youtube", "instagram", "tiktok", "linkedin", "twitter"],
        "limits": {
            "max_text_length": 2000,
            "max_batch_size": 50,
            "max_file_size": "100MB",
            "processing_timeout": "30 minutes"
        },
        "endpoints": {
            "create_simple": "/api/videos/create",
            "create_pipeline": "/api/videos/pipeline", 
            "batch_processing": "/api/videos/batch",
            "optimize": "/api/videos/optimize",
            "status": "/api/videos/{id}/status",
            "download": "/api/videos/{id}/download",
            "templates": "/api/videos/templates"
        }
    } 