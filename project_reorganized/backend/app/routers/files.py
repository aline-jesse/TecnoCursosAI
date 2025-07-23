"""
Router de arquivos - TecnoCursos AI
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..schemas.base import ApiResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_files(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Listar arquivos com paginação
    """
    return ApiResponse(
        success=True,
        message="Lista de arquivos obtida com sucesso",
        data={
            "files": [
                {"id": 1, "filename": "documento1.pdf", "size": 1024000},
                {"id": 2, "filename": "apresentacao.pptx", "size": 2048000}
            ],
            "pagination": {
                "page": pagination.page,
                "size": pagination.size,
                "total": 2
            }
        }
    )


@router.get("/{file_id}", response_model=ApiResponse)
async def get_file(file_id: int, db: Session = Depends(get_db)):
    """
    Obter arquivo por ID
    """
    return ApiResponse(
        success=True,
        message="Arquivo obtido com sucesso",
        data={
            "file": {
                "id": file_id,
                "filename": f"arquivo_{file_id}.pdf",
                "size": 1024000,
                "type": "application/pdf",
                "status": "uploaded"
            }
        }
    )


@router.post("/upload", response_model=ApiResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload de arquivo
    """
    return ApiResponse(
        success=True,
        message="Arquivo enviado com sucesso",
        data={
            "file_id": 1,
            "filename": file.filename,
            "size": len(await file.read()) if file.size else 0
        }
    )


@router.delete("/{file_id}", response_model=ApiResponse)
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """
    Deletar arquivo
    """
    return ApiResponse(
        success=True,
        message="Arquivo deletado com sucesso",
        data={"file_id": file_id}
    ) 