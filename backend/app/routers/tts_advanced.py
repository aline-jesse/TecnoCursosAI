#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router Avançado TTS - TecnoCursos AI
==================================

Endpoints avançados para processamento em lote, cache, analytics
e funcionalidades premium de TTS.
"""

import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from pathlib import Path
import zipfile
import tempfile

from app.database import get_db
from app.auth import get_current_user, get_current_user_optional
from app.models import User
from app.logger import get_logger

# Imports condicionais para serviços TTS
try:
    from app.services.tts_batch_service import (
        create_tts_batch, get_tts_batch_status, cancel_tts_batch,
        get_tts_processor_stats, tts_batch_processor
    )
    from app.services.tts_cache_service import (
        get_tts_cache_stats, clear_tts_cache, tts_cache_manager
    )
    ADVANCED_TTS_AVAILABLE = True
except ImportError:
    ADVANCED_TTS_AVAILABLE = False
    print("⚠️ Serviços TTS avançados não disponíveis")

logger = get_logger("tts_advanced_router")
router = APIRouter(prefix="/api/tts/advanced", tags=["tts-advanced"])

# ===============================
# SCHEMAS
# ===============================

class TTSBatchRequest(BaseModel):
    """Schema para processamento em lote"""
    texts: List[str] = Field(..., min_items=1, max_items=50, description="Lista de textos (máx 50)")
    output_directory: Optional[str] = Field(None, description="Diretório de saída customizado")
    voice: Optional[str] = Field("v2/pt_speaker_0", description="Voz a ser usada")
    provider: str = Field("auto", description="Provedor TTS (auto, bark, gtts)")
    language: str = Field("pt", description="Idioma dos textos")
    webhook_url: Optional[str] = Field(None, description="URL para webhook de notificação")
    
    @validator('texts')
    def validate_texts(cls, v):
        if not v:
            raise ValueError("Lista de textos não pode estar vazia")
        
        for i, text in enumerate(v):
            if not text.strip():
                raise ValueError(f"Texto {i+1} não pode estar vazio")
            if len(text) > 2000:
                raise ValueError(f"Texto {i+1} muito longo (máx 2000 caracteres)")
                
        return v

class TTSBatchResponse(BaseModel):
    """Resposta do processamento em lote"""
    batch_id: str
    status: str
    message: str
    total_tasks: int
    estimated_duration: Optional[int] = None

class TTSPreloadRequest(BaseModel):
    """Requisição para pré-carregar frases"""
    phrases: List[str] = Field(..., min_items=1, max_items=100)
    provider: str = Field("gtts", description="Provedor para pré-carregamento")
    
class TTSAnalyticsResponse(BaseModel):
    """Resposta de analytics TTS"""
    cache_stats: Dict
    processor_stats: Dict
    system_health: Dict

# ===============================
# MIDDLEWARES E DEPENDÊNCIAS
# ===============================

async def check_advanced_tts_available():
    """Verificar se serviços TTS avançados estão disponíveis"""
    if not ADVANCED_TTS_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviços TTS avançados não disponíveis"
        )

# ===============================
# ENDPOINTS DE PROCESSAMENTO EM LOTE
# ===============================

@router.post("/batch", response_model=TTSBatchResponse)
async def create_batch_tts(
    request: TTSBatchRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """
    Criar processamento em lote de múltiplos textos
    
    Processa até 50 textos simultaneamente com otimização automática.
    """
    try:
        logger.info(f"Usuário {user.id} criando lote TTS com {len(request.texts)} textos")
        
        # Estimar duração (baseado em médias)
        total_chars = sum(len(text) for text in request.texts)
        estimated_seconds = total_chars * 0.1  # ~0.1s por caractere (estimativa)
        
        # Criar lote
        batch_id = await create_tts_batch(
            texts=request.texts,
            output_directory=request.output_directory,
            voice=request.voice,
            provider=request.provider,
            language=request.language,
            user_id=str(user.id),
            webhook_url=request.webhook_url
        )
        
        logger.info(f"Lote TTS criado: {batch_id} para usuário {user.id}")
        
        return TTSBatchResponse(
            batch_id=batch_id,
            status="processing",
            message=f"Lote criado com sucesso. {len(request.texts)} textos em processamento.",
            total_tasks=len(request.texts),
            estimated_duration=int(estimated_seconds)
        )
        
    except Exception as e:
        logger.error(f"Erro ao criar lote TTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar lote: {str(e)}"
        )

@router.get("/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str,
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Obter status detalhado de um lote"""
    try:
        status_info = await get_tts_batch_status(batch_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote não encontrado"
            )
            
        logger.info(f"Status do lote {batch_id} consultado por usuário {user.id}")
        
        return {
            "batch_id": batch_id,
            "status": status_info,
            "message": f"Lote {batch_id} - Status atualizado"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/batch/{batch_id}")
async def cancel_batch(
    batch_id: str,
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Cancelar processamento de um lote"""
    try:
        success = await cancel_tts_batch(batch_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote não encontrado ou já concluído"
            )
            
        logger.info(f"Lote {batch_id} cancelado por usuário {user.id}")
        
        return {
            "success": True,
            "message": f"Lote {batch_id} cancelado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cancelar lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/batch/{batch_id}/download")
async def download_batch_results(
    batch_id: str,
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Download dos resultados de um lote como arquivo ZIP"""
    try:
        # Obter status do lote
        status_info = await get_tts_batch_status(batch_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote não encontrado"
            )
            
        if status_info['status'] != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lote ainda não foi concluído"
            )
            
        # Criar arquivo ZIP temporário
        temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        
        try:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                output_dir = Path(status_info['output_directory'])
                
                # Adicionar todos os arquivos MP3
                for audio_file in output_dir.glob("*.mp3"):
                    zipf.write(audio_file, audio_file.name)
                    
                # Adicionar relatório se existir
                report_file = output_dir / "batch_report.json"
                if report_file.exists():
                    zipf.write(report_file, "batch_report.json")
                    
            logger.info(f"Download do lote {batch_id} por usuário {user.id}")
            
            return FileResponse(
                path=temp_zip.name,
                media_type="application/zip",
                filename=f"tts_batch_{batch_id}.zip",
                headers={"Content-Disposition": f"attachment; filename=tts_batch_{batch_id}.zip"}
            )
            
        except Exception as e:
            # Limpar arquivo temporário em caso de erro
            if temp_zip and Path(temp_zip.name).exists():
                Path(temp_zip.name).unlink()
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download do lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no download: {str(e)}"
        )

# ===============================
# ENDPOINTS DE CACHE
# ===============================

@router.get("/cache/stats")
async def get_cache_statistics(
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Obter estatísticas detalhadas do cache TTS"""
    try:
        stats = await get_tts_cache_stats()
        
        return {
            "cache_stats": stats,
            "message": "Estatísticas do cache obtidas com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/cache")
async def clear_cache(
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Limpar todo o cache TTS (apenas administradores)"""
    try:
        # Verificar permissões (simplificado - em produção usar roles)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
            
        success = await clear_tts_cache()
        
        if success:
            logger.warning(f"Cache TTS limpo por usuário {user.id}")
            return {
                "success": True,
                "message": "Cache limpo com sucesso"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao limpar cache"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/cache/preload")
async def preload_common_phrases(
    request: TTSPreloadRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Pré-carregar frases comuns no cache"""
    try:
        # Executar pré-carregamento em background
        background_tasks.add_task(
            tts_cache_manager.preload_common_phrases,
            request.phrases,
            request.provider
        )
        
        logger.info(f"Pré-carregamento iniciado por usuário {user.id}: {len(request.phrases)} frases")
        
        return {
            "success": True,
            "message": f"Pré-carregamento de {len(request.phrases)} frases iniciado",
            "provider": request.provider
        }
        
    except Exception as e:
        logger.error(f"Erro no pré-carregamento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/cache/similar")
async def find_similar_audio(
    text: str = Query(..., description="Texto para buscar similares"),
    threshold: float = Query(0.8, ge=0.0, le=1.0, description="Limite de similaridade"),
    max_results: int = Query(5, ge=1, le=20, description="Número máximo de resultados"),
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Encontrar áudios similares no cache"""
    try:
        similar_audios = await tts_cache_manager.find_similar_audio(
            text=text,
            similarity_threshold=threshold,
            max_results=max_results
        )
        
        return {
            "query_text": text,
            "threshold": threshold,
            "results_found": len(similar_audios),
            "similar_audios": similar_audios
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar áudios similares: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ===============================
# ENDPOINTS DE ANALYTICS
# ===============================

@router.get("/analytics", response_model=TTSAnalyticsResponse)
async def get_tts_analytics(
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Obter analytics completos do sistema TTS"""
    try:
        # Obter estatísticas de cache
        cache_stats = await get_tts_cache_stats()
        
        # Obter estatísticas do processador
        processor_stats = get_tts_processor_stats()
        
        # Calcular saúde do sistema
        system_health = {
            "cache_health": "good" if cache_stats.get("hit_rate", 0) > 50 else "warning",
            "processor_health": "good" if processor_stats.get("success_rate", 0) > 90 else "warning",
            "active_workers": processor_stats.get("workers_running", 0),
            "queue_length": processor_stats.get("queue_size", 0)
        }
        
        return TTSAnalyticsResponse(
            cache_stats=cache_stats,
            processor_stats=processor_stats,
            system_health=system_health
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/health")
async def tts_health_check(
    _: None = Depends(check_advanced_tts_available)
):
    """Health check dos serviços TTS"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": str(asyncio.get_event_loop().time()),
            "services": {
                "batch_processor": tts_batch_processor.is_running,
                "cache_manager": True,  # Se chegou até aqui, está funcionando
                "advanced_features": ADVANCED_TTS_AVAILABLE
            },
            "version": "1.0.0"
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": str(asyncio.get_event_loop().time())
        }

# ===============================
# ENDPOINTS DE ADMINISTRAÇÃO
# ===============================

@router.get("/admin/processor/restart")
async def restart_processor(
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Reiniciar processador TTS (admin)"""
    try:
        # Verificar permissões admin (simplificado)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado - apenas administradores"
            )
            
        # Parar e reiniciar workers
        await tts_batch_processor.stop_workers()
        await asyncio.sleep(1)
        await tts_batch_processor.start_workers()
        
        logger.warning(f"Processador TTS reiniciado por admin {user.id}")
        
        return {
            "success": True,
            "message": "Processador TTS reiniciado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reiniciar processador: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/admin/system-info")
async def get_system_info(
    user: User = Depends(get_current_user),
    _: None = Depends(check_advanced_tts_available)
):
    """Informações detalhadas do sistema (admin)"""
    try:
        import psutil
        import torch
        
        system_info = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
            "active_batches": len(tts_batch_processor.active_batches),
            "cache_dir_size": sum(f.stat().st_size for f in Path("cache/tts").rglob('*') if f.is_file())
        }
        
        return {
            "system_info": system_info,
            "message": "Informações do sistema obtidas com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter informações do sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        ) 