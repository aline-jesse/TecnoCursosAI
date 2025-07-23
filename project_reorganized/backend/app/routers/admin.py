"""
Router de administração - TecnoCursos AI
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.base import ApiResponse

router = APIRouter()


@router.get("/stats", response_model=ApiResponse)
async def get_admin_stats(db: Session = Depends(get_db)):
    """
    Obter estatísticas administrativas
    """
    return ApiResponse(
        success=True,
        message="Estatísticas obtidas com sucesso",
        data={
            "stats": {
                "total_users": 10,
                "total_projects": 25,
                "total_files": 100,
                "storage_used_mb": 1024
            }
        }
    )


@router.get("/system", response_model=ApiResponse)
async def get_system_info(db: Session = Depends(get_db)):
    """
    Obter informações do sistema
    """
    return ApiResponse(
        success=True,
        message="Informações do sistema obtidas com sucesso",
        data={
            "system": {
                "version": "2.0.0",
                "environment": "development",
                "database": "sqlite",
                "uptime": "5 minutes"
            }
        }
    )


@router.post("/maintenance", response_model=ApiResponse)
async def toggle_maintenance_mode(db: Session = Depends(get_db)):
    """
    Alternar modo de manutenção
    """
    return ApiResponse(
        success=True,
        message="Modo de manutenção alterado",
        data={"maintenance_mode": False}
    ) 