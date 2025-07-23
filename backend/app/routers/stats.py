"""
Router de Estatísticas - TecnoCursosAI
Endpoints para métricas e estatísticas do sistema
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, Project, FileUpload, Video
from ..logger import get_logger

logger = get_logger("stats_router")

router = APIRouter(
    prefix="/api/stats",
    tags=["📊 Estatísticas"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Não encontrado"}}
)

class SystemStatsResponse(BaseModel):
    """Schema para estatísticas do sistema"""
    total_users: int
    total_projects: int
    total_uploads: int
    total_videos: int
    total_storage_mb: float

@router.get("/system", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obter estatísticas gerais do sistema
    
    TODO: Implementar verificação de permissão
    """
    
    try:
        logger.info("Consulta de estatísticas do sistema", user_id=current_user.id)
        
        # Contar totais
        total_users = db.query(User).count()
        total_projects = db.query(Project).count()
        total_uploads = db.query(FileUpload).count()
        total_videos = db.query(Video).count()
        
        # Calcular storage total (simplificado)
        from sqlalchemy import func
        total_storage_bytes = db.query(func.sum(FileUpload.file_size)).scalar() or 0
        total_storage_mb = total_storage_bytes / (1024 * 1024)
        
        return SystemStatsResponse(
            total_users=total_users,
            total_projects=total_projects,
            total_uploads=total_uploads,
            total_videos=total_videos,
            total_storage_mb=round(total_storage_mb, 2)
        )
        
    except Exception as e:
        logger.error("Erro ao obter estatísticas", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter estatísticas"
        ) 