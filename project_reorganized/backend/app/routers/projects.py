"""
Router de projetos - TecnoCursos AI
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..schemas.base import ApiResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_projects(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Listar projetos com paginação
    """
    return ApiResponse(
        success=True,
        message="Lista de projetos obtida com sucesso",
        data={
            "projects": [
                {"id": 1, "name": "Projeto Demo 1", "status": "active"},
                {"id": 2, "name": "Projeto Demo 2", "status": "completed"}
            ],
            "pagination": {
                "page": pagination.page,
                "size": pagination.size,
                "total": 2
            }
        }
    )


@router.get("/{project_id}", response_model=ApiResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Obter projeto por ID
    """
    return ApiResponse(
        success=True,
        message="Projeto obtido com sucesso",
        data={
            "project": {
                "id": project_id,
                "name": f"Projeto Demo {project_id}",
                "description": "Projeto de demonstração",
                "status": "active"
            }
        }
    )


@router.post("/", response_model=ApiResponse)
async def create_project(db: Session = Depends(get_db)):
    """
    Criar novo projeto
    """
    return ApiResponse(
        success=True,
        message="Projeto criado com sucesso",
        data={"project_id": 1}
    )


@router.put("/{project_id}", response_model=ApiResponse)
async def update_project(project_id: int, db: Session = Depends(get_db)):
    """
    Atualizar projeto
    """
    return ApiResponse(
        success=True,
        message="Projeto atualizado com sucesso",
        data={"project_id": project_id}
    )


@router.delete("/{project_id}", response_model=ApiResponse)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Deletar projeto
    """
    return ApiResponse(
        success=True,
        message="Projeto deletado com sucesso",
        data={"project_id": project_id}
    ) 