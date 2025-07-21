"""
Router de Projetos - TecnoCursosAI
Endpoints para gestão de projetos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_user_optional
from ..schemas import ProjectResponse, ProjectCreate, ProjectUpdate
from ..models import Project, User
from ..logger import get_logger

logger = get_logger("projects_router")

router = APIRouter(
    tags=["📁 Projetos"],
    responses={404: {"description": "Não encontrado"}}
)

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Listar projetos do usuário
    
    - **skip**: Número de registros para pular
    - **limit**: Número máximo de registros a retornar
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    
    projects = db.query(Project).filter(
        Project.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [ProjectResponse.from_orm(project) for project in projects]

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Criar novo projeto
    
    - **name**: Nome do projeto
    - **description**: Descrição do projeto (opcional)
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    
    try:
        project = Project(
            name=project_data.name,
            description=project_data.description or "",
            owner_id=current_user.id,
            status="active"
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        logger.info(f"Projeto criado", project_id=project.id, user_id=current_user.id)
        
        return ProjectResponse.from_orm(project)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar projeto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar projeto"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obter informações de um projeto específico
    
    - **project_id**: ID do projeto
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    return ProjectResponse.from_orm(project)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Atualizar projeto
    
    - **project_id**: ID do projeto
    - **name**: Nome do projeto (opcional)
    - **description**: Descrição do projeto (opcional)
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    try:
        # Atualizar campos fornecidos
        for field, value in project_data.dict(exclude_unset=True).items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"Projeto atualizado", project_id=project.id, user_id=current_user.id)
        
        return ProjectResponse.from_orm(project)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar projeto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar projeto"
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Deletar projeto
    
    - **project_id**: ID do projeto
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    try:
        db.delete(project)
        db.commit()
        
        logger.info(f"Projeto deletado", project_id=project_id, user_id=current_user.id)
        
        return {"message": "Projeto deletado com sucesso"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar projeto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar projeto"
        ) 