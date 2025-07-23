"""
Router de autenticação - TecnoCursos AI
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..schemas.base import ApiResponse

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/login", response_model=ApiResponse)
async def login(db: Session = Depends(get_db)):
    """
    Endpoint de login (básico para demonstração)
    """
    return ApiResponse(
        success=True,
        message="Login endpoint disponível",
        data={"status": "not_implemented"}
    )


@router.post("/register", response_model=ApiResponse) 
async def register(db: Session = Depends(get_db)):
    """
    Endpoint de registro (básico para demonstração)
    """
    return ApiResponse(
        success=True,
        message="Register endpoint disponível",
        data={"status": "not_implemented"}
    )


@router.post("/logout", response_model=ApiResponse)
async def logout():
    """
    Endpoint de logout (básico para demonstração)
    """
    return ApiResponse(
        success=True,
        message="Logout realizado com sucesso",
        data={}
    )


@router.get("/me", response_model=ApiResponse)
async def get_current_user(db: Session = Depends(get_db)):
    """
    Obter usuário atual (básico para demonstração)
    """
    return ApiResponse(
        success=True,
        message="Usuário obtido com sucesso",
        data={"user": "demo_user"}
    ) 