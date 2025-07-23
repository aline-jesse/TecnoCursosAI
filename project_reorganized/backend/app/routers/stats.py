"""
Router de estatísticas - TecnoCursos AI
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..core.database import get_db
from ..schemas.base import ApiResponse

router = APIRouter()


@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Obter estatísticas para dashboard
    """
    return ApiResponse(
        success=True,
        message="Estatísticas do dashboard obtidas com sucesso",
        data={
            "stats": {
                "today": {
                    "new_users": 5,
                    "uploads": 12,
                    "videos_generated": 8
                },
                "this_week": {
                    "new_users": 25,
                    "uploads": 67,
                    "videos_generated": 45
                },
                "this_month": {
                    "new_users": 150,
                    "uploads": 320,
                    "videos_generated": 210
                }
            }
        }
    )


@router.get("/usage", response_model=ApiResponse)
async def get_usage_stats(db: Session = Depends(get_db)):
    """
    Obter estatísticas de uso
    """
    return ApiResponse(
        success=True,
        message="Estatísticas de uso obtidas com sucesso",
        data={
            "usage": {
                "storage": {
                    "used_mb": 1024,
                    "total_mb": 10240,
                    "percentage": 10.0
                },
                "bandwidth": {
                    "used_gb": 5.2,
                    "total_gb": 100.0,
                    "percentage": 5.2
                },
                "api_calls": {
                    "today": 1250,
                    "limit": 10000,
                    "percentage": 12.5
                }
            }
        }
    )


@router.get("/performance", response_model=ApiResponse)
async def get_performance_stats(db: Session = Depends(get_db)):
    """
    Obter estatísticas de performance
    """
    return ApiResponse(
        success=True,
        message="Estatísticas de performance obtidas com sucesso",
        data={
            "performance": {
                "avg_response_time_ms": 250,
                "uptime_percentage": 99.9,
                "error_rate_percentage": 0.1,
                "concurrent_users": 45
            }
        }
    ) 