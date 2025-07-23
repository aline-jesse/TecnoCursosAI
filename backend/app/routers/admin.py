"""
Router Administrativo - TecnoCursosAI
Endpoints para administração do sistema
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User
from ..logger import get_logger

logger = get_logger("admin_router")

router = APIRouter(
    prefix="/api/admin",
    tags=["🔧 Administração"],
    dependencies=[Depends(get_current_active_user)],
    responses={403: {"description": "Acesso negado"}}
)

@router.get("/system-info")
async def get_system_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obter informações do sistema
    
    TODO: Implementar verificação de permissão de admin
    """
    
    # Placeholder para funcionalidades administrativas
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidades administrativas em desenvolvimento"
    ) 