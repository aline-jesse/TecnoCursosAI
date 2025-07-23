"""
Router de Arquivos - TecnoCursosAI
Endpoints para upload, download e gestão de arquivos
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query, BackgroundTasks, Body
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid

from ..database import get_db
from ..auth import get_current_user_optional
from ..schemas import FileUploadResponse, FileUploadCreate
from ..models import FileUpload, User
from ..logger import get_logger
from ..utils import extract_pdf_text, extract_text_from_pptx, create_videos_for_slides, concatenate_videos
from app.models import Project, Scene, Asset
from app.database import get_db
from sqlalchemy.orm import Session
from app.parsers import get_parser, PARSER_REGISTRY
import logging

logger = get_logger("files_router")

router = APIRouter(
    tags=["📁 Arquivos"],
    responses={404: {"description": "Não encontrado"}}
)

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Upload de arquivo com processamento automático

    - **file**: Arquivo para upload (PDF, PPTX, DOCX)
    - **project_id**: ID do projeto (opcional)
    - **description**: Descrição do arquivo (opcional)
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )

    try:
        # Validar tipo de arquivo
        allowed_extensions = ['.pdf', '.pptx', '.docx']
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não suportado. Tipos permitidos: {', '.join(allowed_extensions)}"
            )

        # Validar tamanho do arquivo (100MB máximo)
        max_size = 100 * 1024 * 1024  # 100MB
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo muito grande. Tamanho máximo: 100MB"
            )

        # Gerar nome único para o arquivo
        file_uuid = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        safe_filename = f"{file_uuid}{file_extension}"

        # Criar diretório de upload se não existir
        upload_dir = Path("app/static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Salvar arquivo
        file_path = upload_dir / safe_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extrair texto do arquivo
        extracted_text = ""
        text_extraction_method = ""

        if file_extension == '.pdf':
            try:
                extracted_text = extract_pdf_text(str(file_path))
                text_extraction_method = "PyMuPDF"
            except Exception as e:
                logger.error(f"Erro ao extrair texto do PDF: {e}")
                extracted_text = ""
        elif file_extension == '.pptx':
            try:
                extracted_text = extract_text_from_pptx(str(file_path))
                text_extraction_method = "python-pptx"
            except Exception as e:
                logger.error(f"Erro ao extrair texto do PPTX: {e}")
                extracted_text = ""

        # Após extrair texto, se for PDF ou PPTX, criar cenas automaticamente
        created_scenes = []
        if file_extension in ['.pdf', '.pptx'] and extracted_text:
            from app.models import Scene, Asset
            from app.utils import extract_pdf_slides_as_images, extract_text_from_pptx
            import json
            # Extrair slides como imagens (PDF)
            slides_imgs = []
            if file_extension == '.pdf':
                slides_imgs = extract_pdf_slides_as_images(str(file_path), output_folder='app/static/uploads/slides')
            elif file_extension == '.pptx':
                # Para PPTX, extrair imagens e textos por slide
                slides_imgs = []  # TODO: implementar extração de imagens de slides PPTX se necessário
            # Criar uma cena para cada slide
            for idx, slide_img in enumerate(slides_imgs):
                scene = Scene(
                    project_id=project_id,
                    name=f"Slide {idx+1}",
                    ordem=idx,
                    texto=extracted_text if isinstance(extracted_text, str) else (extracted_text[idx] if idx < len(extracted_text) else ""),
                    duracao=5.0,
                    background_type="image",
                    background_config=json.dumps({"image": slide_img}),
                    is_active=True
                )
                db.add(scene)
                db.commit()
                db.refresh(scene)
                # Criar asset de imagem para o slide
                asset = Asset(
                    name=f"Slide {idx+1} - Imagem",
                    tipo="image",
                    caminho_arquivo=slide_img,
                    scene_id=scene.id,
                    project_id=project_id,
                    is_library_asset=False,
                    is_public=False
                )
                db.add(asset)
                db.commit()
                db.refresh(asset)
                created_scenes.append(scene.id)

        # Criar registro no banco
        file_upload = FileUpload(
            filename=file.filename,
            file_path=str(file_path),
            file_size=file.size or 0,
            file_type=file_extension,
            user_id=current_user.id,
            project_id=project_id,
            description=description,
            extracted_text=extracted_text,
            text_extraction_method=text_extraction_method,
            upload_date=datetime.now()
        )

        db.add(file_upload)
        db.commit()
        db.refresh(file_upload)

        logger.info(f"Arquivo enviado com sucesso",
                   filename=file.filename,
                   user_id=current_user.id,
                   file_id=file_upload.id)

        # Processar em background se houver texto extraído
        if extracted_text:
            background_tasks.add_task(process_file_background, file_upload.id, db)

        # Adicionar IDs das cenas criadas na resposta
        response = FileUploadResponse.from_orm(file_upload)
        response.created_scenes = created_scenes
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no upload"
        )

async def process_file_background(file_id: int, db: Session):
    """Processar arquivo em background"""
    try:
        file_upload = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        if not file_upload:
            return

        # Aqui você pode adicionar processamento adicional
        # como geração de vídeo, TTS, etc.

        logger.info(f"Processamento em background concluído", file_id=file_id)

    except Exception as e:
        logger.error(f"Erro no processamento em background: {e}")

@router.post("/import-presentations/")
async def import_presentations(
    project_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Importa múltiplos arquivos PDF/PPTX (ou outros), extrai slides e cria cenas associadas ao projeto.
    Retorna preview das cenas para o front-end.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    created_scenes = []
    for upload in files:
        filename = upload.filename
        ext = os.path.splitext(filename)[1].lower()
        parser = get_parser(ext)
        if not parser:
            logging.warning(f"Extensão não suportada: {ext}")
            continue
        temp_path = f"temp/{filename}"
        with open(temp_path, "wb") as f:
            f.write(await upload.read())
        output_dir = f"app/static/uploads/slides/project_{project_id}_{os.path.splitext(filename)[0]}"
        try:
            slides = parser(temp_path, output_dir)
        except Exception as e:
            logging.error(f"Erro ao importar {filename}: {e}")
            os.remove(temp_path)
            continue
        for idx, slide in enumerate(slides):
            scene = Scene(
                project_id=project_id,
                name=f"{filename} - Slide {idx+1}",
                ordem=idx,
                texto=slide["texto"],
                duracao=5.0,
                background_type="image" if slide["imagens"] else "solid",
                background_config="{}",
                is_active=True
            )
            db.add(scene)
            db.commit()
            db.refresh(scene)
            for img_path in slide["imagens"]:
                asset = Asset(
                    name=f"{filename} - Slide {idx+1} - Imagem",
                    tipo="image",
                    caminho_arquivo=img_path,
                    scene_id=scene.id,
                    project_id=project_id,
                    is_library_asset=False,
                    is_public=False
                )
                db.add(asset)
                db.commit()
            created_scenes.append({
                "scene_id": scene.id,
                "name": scene.name,
                "texto": scene.texto,
                "imagens": slide["imagens"]
            })
        os.remove(temp_path)
    return {"success": True, "created_scenes": created_scenes}

@router.get("/import-supported-formats/")
def list_supported_import_formats():
    """
    Lista as extensões de arquivo suportadas para importação automática.
    """
    return {"supported_formats": list(PARSER_REGISTRY.keys())}

@router.get("/", response_model=List[FileUploadResponse])
async def list_files(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = Query(None),
    file_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Listar arquivos do usuário

    - **skip**: Número de registros para pular
    - **limit**: Número máximo de registros a retornar
    - **project_id**: Filtrar por projeto (opcional)
    - **file_type**: Filtrar por tipo de arquivo (opcional)
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )

    query = db.query(FileUpload).filter(FileUpload.user_id == current_user.id)

    if project_id:
        query = query.filter(FileUpload.project_id == project_id)

    if file_type:
        query = query.filter(FileUpload.file_type == file_type)

    files = query.offset(skip).limit(limit).all()
    return [FileUploadResponse.from_orm(file) for file in files]

@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obter informações de um arquivo específico

    - **file_id**: ID do arquivo
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )

    file_upload = db.query(FileUpload).filter(
        FileUpload.id == file_id,
        FileUpload.user_id == current_user.id
    ).first()

    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )

    return FileUploadResponse.from_orm(file_upload)

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Deletar arquivo

    - **file_id**: ID do arquivo
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )

    file_upload = db.query(FileUpload).filter(
        FileUpload.id == file_id,
        FileUpload.user_id == current_user.id
    ).first()

    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )

    try:
        # Deletar arquivo físico
        if os.path.exists(file_upload.file_path):
            os.remove(file_upload.file_path)

        # Deletar registro do banco
        db.delete(file_upload)
        db.commit()

        logger.info(f"Arquivo deletado", file_id=file_id, user_id=current_user.id)

        return {"message": "Arquivo deletado com sucesso"}

    except Exception as e:
        logger.error(f"Erro ao deletar arquivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar arquivo"
        )

@router.get("/stats/summary")
async def get_file_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obter estatísticas dos arquivos do usuário
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )

    try:
        # Total de arquivos
        total_files = db.query(func.count(FileUpload.id)).filter(
            FileUpload.user_id == current_user.id
        ).scalar()

        # Total de storage usado
        total_size = db.query(func.sum(FileUpload.file_size)).filter(
            FileUpload.user_id == current_user.id
        ).scalar() or 0

        # Arquivos por tipo
        files_by_type = db.query(
            FileUpload.file_type,
            func.count(FileUpload.id)
        ).filter(
            FileUpload.user_id == current_user.id
        ).group_by(FileUpload.file_type).all()

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files_by_type": dict(files_by_type),
            "user_id": current_user.id
        }

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter estatísticas"
        )
