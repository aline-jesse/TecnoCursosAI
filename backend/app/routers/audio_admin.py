"""
Router de Administração de Áudios - TecnoCursos AI
===============================================

Endpoints administrativos para gerenciamento avançado de áudios:
- Limpeza automática do sistema
- Analytics e relatórios
- Monitoramento de performance
- Configurações de TTS
- Processamento em lote
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from pathlib import Path

from app.database import get_db
from app.models import User, Audio, FileUpload, Project
from app.auth import get_current_user_optional
from app.config import get_settings

# Importar serviços avançados
try:
    from app.services.audio_cleanup_service import cleanup_service, get_cleanup_recommendations, run_audio_cleanup
    _cleanup_available = True
except ImportError:
    _cleanup_available = False

try:
    from app.services.tts_analytics_service import analytics_service
    _analytics_available = True
except ImportError:
    _analytics_available = False

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/admin/audios", tags=["audio-admin"])

def require_admin(current_user: User = Depends(get_current_user_optional)):
    """Verificar se usuário é administrador"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário deve estar autenticado"
        )
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar esta funcionalidade"
        )
    
    return current_user

@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Dashboard administrativo com estatísticas gerais do sistema de áudios
    """
    try:
        # Estatísticas gerais
        total_audios = db.query(Audio).count()
        total_users_with_audios = db.query(func.count(func.distinct(Audio.user_id))).scalar()
        total_size_bytes = db.query(func.sum(Audio.file_size)).scalar() or 0
        total_duration = db.query(func.sum(Audio.duration)).scalar() or 0
        
        # Estatísticas dos últimos 30 dias
        last_30_days = datetime.now() - timedelta(days=30)
        recent_audios = db.query(Audio).filter(Audio.created_at >= last_30_days).count()
        
        # Top usuários por número de áudios
        top_users = db.query(
            User.username,
            func.count(Audio.id).label('audio_count'),
            func.sum(Audio.duration).label('total_duration')
        ).join(Audio).group_by(User.id).order_by(desc('audio_count')).limit(10).all()
        
        # Distribuição por provider TTS
        provider_stats = db.query(
            Audio.tts_provider,
            func.count(Audio.id).label('count'),
            func.avg(Audio.processing_time).label('avg_processing_time')
        ).group_by(Audio.tts_provider).all()
        
        # Estatísticas de cache
        cache_hits = db.query(Audio).filter(Audio.cache_hit == True).count()
        cache_misses = db.query(Audio).filter(Audio.cache_hit == False).count()
        cache_hit_rate = (cache_hits / (cache_hits + cache_misses) * 100) if (cache_hits + cache_misses) > 0 else 0
        
        # Status de saúde do sistema
        health_status = {
            "storage_usage_mb": total_size_bytes / (1024 * 1024),
            "avg_processing_time": db.query(func.avg(Audio.processing_time)).scalar() or 0,
            "failed_audios": db.query(Audio).filter(Audio.status == 'failed').count(),
            "pending_audios": db.query(Audio).filter(Audio.status == 'queued').count()
        }
        
        return {
            "success": True,
            "overview": {
                "total_audios": total_audios,
                "total_users": total_users_with_audios,
                "total_size_mb": total_size_bytes / (1024 * 1024),
                "total_duration_minutes": total_duration / 60,
                "recent_audios_30d": recent_audios,
                "cache_hit_rate": round(cache_hit_rate, 2)
            },
            "top_users": [
                {
                    "username": user.username,
                    "audio_count": user.audio_count,
                    "total_duration_minutes": (user.total_duration or 0) / 60
                }
                for user in top_users
            ],
            "provider_stats": [
                {
                    "provider": stat.tts_provider,
                    "count": stat.count,
                    "avg_processing_time": stat.avg_processing_time or 0
                }
                for stat in provider_stats
            ],
            "health": health_status,
            "services_available": {
                "cleanup": _cleanup_available,
                "analytics": _analytics_available
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter dashboard admin: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/cleanup/recommendations")
async def get_cleanup_recommendations_endpoint(
    current_user: User = Depends(require_admin)
):
    """
    Obter recomendações de limpeza do sistema
    """
    if not _cleanup_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de limpeza não disponível"
        )
    
    try:
        recommendations = await get_cleanup_recommendations()
        return {
            "success": True,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter recomendações de limpeza: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/cleanup/execute")
async def execute_cleanup(
    background_tasks: BackgroundTasks,
    max_age_days: int = Query(90, ge=1, le=365, description="Idade máxima em dias para manter áudios"),
    dry_run: bool = Query(False, description="Se true, apenas simula a limpeza"),
    current_user: User = Depends(require_admin)
):
    """
    Executar limpeza automática do sistema de áudios
    """
    if not _cleanup_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de limpeza não disponível"
        )
    
    try:
        # Executar limpeza em background
        background_tasks.add_task(
            run_cleanup_task,
            max_age_days=max_age_days,
            dry_run=dry_run,
            admin_user_id=current_user.id
        )
        
        return {
            "success": True,
            "message": f"Limpeza {'simulada' if dry_run else 'real'} iniciada em background",
            "max_age_days": max_age_days,
            "dry_run": dry_run,
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar limpeza: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/users/{user_id}/audios")
async def get_user_audios_admin(
    user_id: int,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Obter áudios de um usuário específico (visão administrativa)
    """
    try:
        # Verificar se usuário existe
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Buscar áudios do usuário
        query = db.query(Audio).filter(Audio.user_id == user_id)
        total_count = query.count()
        
        audios = query.order_by(Audio.created_at.desc()).offset(offset).limit(limit).all()
        
        # Estatísticas do usuário
        user_stats = {
            "total_audios": total_count,
            "total_duration": db.query(func.sum(Audio.duration)).filter(Audio.user_id == user_id).scalar() or 0,
            "total_size_mb": (db.query(func.sum(Audio.file_size)).filter(Audio.user_id == user_id).scalar() or 0) / (1024 * 1024),
            "avg_processing_time": db.query(func.avg(Audio.processing_time)).filter(Audio.user_id == user_id).scalar() or 0,
            "cache_hit_rate": 0
        }
        
        # Calcular cache hit rate
        cache_hits = db.query(Audio).filter(and_(Audio.user_id == user_id, Audio.cache_hit == True)).count()
        if total_count > 0:
            user_stats["cache_hit_rate"] = (cache_hits / total_count) * 100
        
        audio_list = []
        for audio in audios:
            audio_data = {
                "id": audio.id,
                "uuid": audio.uuid,
                "title": audio.title,
                "filename": audio.filename,
                "file_size": audio.file_size,
                "duration": audio.duration,
                "status": audio.status,
                "tts_provider": audio.tts_provider,
                "voice_type": audio.voice_type,
                "processing_time": audio.processing_time,
                "cache_hit": audio.cache_hit,
                "created_at": audio.created_at,
                "play_count": audio.play_count,
                "download_count": audio.download_count,
                "text_length": audio.text_length
            }
            audio_list.append(audio_data)
        
        return {
            "success": True,
            "user": {
                "id": target_user.id,
                "username": target_user.username,
                "email": target_user.email,
                "is_active": target_user.is_active
            },
            "stats": user_stats,
            "audios": audio_list,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter áudios do usuário: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/users/{user_id}/audios")
async def delete_user_audios_admin(
    user_id: int,
    background_tasks: BackgroundTasks,
    confirm: bool = Query(False, description="Confirmação necessária para deletar"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Deletar todos os áudios de um usuário (operação administrativa)
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmação necessária. Use o parâmetro confirm=true"
        )
    
    try:
        # Verificar se usuário existe
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Contar áudios do usuário
        audio_count = db.query(Audio).filter(Audio.user_id == user_id).count()
        
        if audio_count == 0:
            return {
                "success": True,
                "message": "Usuário não possui áudios para deletar",
                "deleted_count": 0
            }
        
        # Executar deleção em background
        background_tasks.add_task(
            delete_user_audios_task,
            user_id=user_id,
            admin_user_id=current_user.id
        )
        
        return {
            "success": True,
            "message": f"Deleção de {audio_count} áudios do usuário '{target_user.username}' iniciada",
            "user": {
                "id": target_user.id,
                "username": target_user.username
            },
            "audio_count": audio_count,
            "started_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar áudios do usuário: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/analytics/performance")
async def get_performance_analytics(
    days: int = Query(30, ge=1, le=365, description="Período em dias para análise"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Análise de performance do sistema de áudios
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Métricas de processamento
        processing_stats = db.query(
            func.avg(Audio.processing_time).label('avg_time'),
            func.min(Audio.processing_time).label('min_time'),
            func.max(Audio.processing_time).label('max_time'),
            func.count(Audio.id).label('total_count')
        ).filter(
            and_(
                Audio.created_at >= start_date,
                Audio.processing_time.isnot(None)
            )
        ).first()
        
        # Análise por provider
        provider_performance = db.query(
            Audio.tts_provider,
            func.avg(Audio.processing_time).label('avg_time'),
            func.count(Audio.id).label('count'),
            func.avg(Audio.duration).label('avg_duration')
        ).filter(
            Audio.created_at >= start_date
        ).group_by(Audio.tts_provider).all()
        
        # Análise temporal (por dia)
        daily_stats = db.query(
            func.date(Audio.created_at).label('date'),
            func.count(Audio.id).label('count'),
            func.avg(Audio.processing_time).label('avg_time'),
            func.sum(Audio.file_size).label('total_size')
        ).filter(
            Audio.created_at >= start_date
        ).group_by(func.date(Audio.created_at)).order_by('date').all()
        
        # Taxa de erro
        total_audios = db.query(Audio).filter(Audio.created_at >= start_date).count()
        failed_audios = db.query(Audio).filter(
            and_(
                Audio.created_at >= start_date,
                Audio.status == 'failed'
            )
        ).count()
        
        error_rate = (failed_audios / total_audios * 100) if total_audios > 0 else 0
        
        return {
            "success": True,
            "period_days": days,
            "overview": {
                "avg_processing_time": processing_stats.avg_time or 0,
                "min_processing_time": processing_stats.min_time or 0,
                "max_processing_time": processing_stats.max_time or 0,
                "total_audios": processing_stats.total_count or 0,
                "error_rate": round(error_rate, 2)
            },
            "provider_performance": [
                {
                    "provider": stat.tts_provider,
                    "avg_processing_time": stat.avg_time or 0,
                    "count": stat.count,
                    "avg_duration": stat.avg_duration or 0
                }
                for stat in provider_performance
            ],
            "daily_stats": [
                {
                    "date": stat.date.isoformat(),
                    "count": stat.count,
                    "avg_processing_time": stat.avg_time or 0,
                    "total_size_mb": (stat.total_size or 0) / (1024 * 1024)
                }
                for stat in daily_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics de performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# Tarefas em background
async def run_cleanup_task(max_age_days: int, dry_run: bool, admin_user_id: int):
    """Tarefa em background para limpeza do sistema"""
    try:
        logger.info(f"Iniciando limpeza em background (Admin ID: {admin_user_id})")
        report = await run_audio_cleanup(max_age_days, dry_run)
        
        # Log do resultado
        if report.get("success"):
            logger.info(f"Limpeza concluída: {report.get('stats', {}).get('summary', 'N/A')}")
        else:
            logger.error(f"Limpeza falhou: {report.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        logger.error(f"Erro na tarefa de limpeza: {e}", exc_info=True)

async def delete_user_audios_task(user_id: int, admin_user_id: int):
    """Tarefa em background para deletar áudios de um usuário"""
    try:
        logger.info(f"Iniciando deleção de áudios do usuário {user_id} (Admin ID: {admin_user_id})")
        
        db = next(get_db())
        try:
            # Buscar áudios do usuário
            audios = db.query(Audio).filter(Audio.user_id == user_id).all()
            
            deleted_count = 0
            errors = 0
            
            for audio in audios:
                try:
                    # Deletar arquivo físico se existir
                    if audio.file_path:
                        file_path = Path(audio.file_path)
                        if file_path.exists():
                            file_path.unlink()
                    
                    # Deletar registro do banco
                    db.delete(audio)
                    deleted_count += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao deletar áudio {audio.id}: {e}")
                    errors += 1
            
            db.commit()
            
            logger.info(f"Deleção concluída: {deleted_count} áudios deletados, {errors} erros")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro na tarefa de deleção: {e}", exc_info=True) 