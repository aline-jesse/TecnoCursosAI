"""
Router de usuários - TecnoCursos AI
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..schemas.base import ApiResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Listar usuários com paginação
    """
    return ApiResponse(
        success=True,
        message="Lista de usuários obtida com sucesso",
        data={
            "users": [],
            "pagination": {
                "page": pagination.page,
                "size": pagination.size,
                "total": 0
            }
        }
    )


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obter usuário por ID
    """
    return ApiResponse(
        success=True,
        message="Usuário obtido com sucesso",
        data={"user": {"id": user_id, "name": "Demo User"}}
    )


@router.post("/", response_model=ApiResponse)
async def create_user(db: Session = Depends(get_db)):
    """
    Criar novo usuário
    """
    return ApiResponse(
        success=True,
        message="Usuário criado com sucesso",
        data={"user_id": 1}
    )


@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(user_id: int, db: Session = Depends(get_db)):
    """
    Atualizar usuário
    """
    return ApiResponse(
        success=True,
        message="Usuário atualizado com sucesso",
        data={"user_id": user_id}
    )


@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deletar usuário
    """
    return ApiResponse(
        success=True,
        message="Usuário deletado com sucesso",
        data={"user_id": user_id}
    ) 