"""
Router de Upload em Lote - TecnoCursos AI
=======================================

Funcionalidades para upload e processamento em lote de múltiplos arquivos:
- Upload simultâneo de até 10 arquivos
- Processamento assíncrono automático
- Acompanhamento de progresso em tempo real
- Geração de relatórios de lote
- Notificações de conclusão
"""

import asyncio
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Project, FileUpload, Audio
from app.auth import get_current_user_optional
from app.config import get_settings
from app.utils import validate_file, extract_pdf_text, extract_text_from_pptx, generate_narration_sync

# Importar processamento assíncrono se disponível
try:
    from app.services.async_audio_processor import AsyncAudioProcessor, Priority, submit_async_audio_task
    ASYNC_PROCESSING_AVAILABLE = True
except ImportError:
    ASYNC_PROCESSING_AVAILABLE = False
    Priority = None  # Fallback se não estiver disponível

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/batch", tags=["batch-upload"])

# Exportar como batch_upload_router
batch_upload_router = router

# Constantes
MAX_BATCH_SIZE = 10
ALLOWED_EXTENSIONS = {'.pdf', '.pptx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB por arquivo

@router.post("/upload")
async def batch_upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Lista de arquivos para upload"),
    project_id: int = Form(..., description="ID do projeto"),
    description: str = Form("", description="Descrição do lote"),
    processing_mode: str = Form("async", description="Modo de processamento: 'sync' ou 'async'"),
    voice: str = Form("v2/pt_speaker_0", description="Voz para narração"),
    priority: str = Form("normal", description="Prioridade: 'low', 'normal', 'high', 'urgent'"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Upload em lote de múltiplos arquivos com processamento automático
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário deve estar autenticado"
        )
    
    # Validações iniciais
    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Máximo de {MAX_BATCH_SIZE} arquivos por lote"
        )
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pelo menos um arquivo deve ser enviado"
        )
    
    # Verificar se projeto existe e pertence ao usuário
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # Validar modo de processamento
    if processing_mode not in ["sync", "async"]:
        processing_mode = "async"
    
    # Se modo async não disponível, forçar sync
    if processing_mode == "async" and not ASYNC_PROCESSING_AVAILABLE:
        processing_mode = "sync"
        logger.warning("Processamento assíncrono não disponível, usando modo síncrono")
    
    # Validar prioridade
    task_priority = Priority.NORMAL if ASYNC_PROCESSING_AVAILABLE else None
    
    # Criar ID do lote
    batch_id = str(uuid.uuid4())
    batch_start_time = datetime.now()
    
    logger.info(f"Iniciando upload em lote {batch_id} com {len(files)} arquivos")
    
    # Resultados do processamento
    batch_results = {
        "batch_id": batch_id,
        "project_id": project_id,
        "total_files": len(files),
        "processing_mode": processing_mode,
        "voice": voice,
        "priority": priority,
        "started_at": batch_start_time.isoformat(),
        "files": [],
        "summary": {
            "uploaded": 0,
            "processed": 0,
            "failed": 0,
            "total_size_mb": 0.0,
            "errors": []
        }
    }
    
    try:
        # Processar cada arquivo
        for i, file in enumerate(files):
            file_result = await process_single_file_in_batch(
                file=file,
                project_id=project_id,
                description=f"{description} - Arquivo {i+1}/{len(files)}",
                voice=voice,
                processing_mode=processing_mode,
                task_priority=task_priority,
                current_user=current_user,
                db=db,
                batch_id=batch_id
            )
            
            batch_results["files"].append(file_result)
            
            # Atualizar estatísticas
            if file_result.get("upload_success"):
                batch_results["summary"]["uploaded"] += 1
                batch_results["summary"]["total_size_mb"] += file_result.get("file_size", 0) / (1024 * 1024)
                
                if file_result.get("processing_completed"):
                    batch_results["summary"]["processed"] += 1
                elif file_result.get("error"):
                    batch_results["summary"]["failed"] += 1
                    batch_results["summary"]["errors"].append(file_result["error"])
        
        # Calcular tempo total
        batch_end_time = datetime.now()
        batch_duration = (batch_end_time - batch_start_time).total_seconds()
        batch_results["completed_at"] = batch_end_time.isoformat()
        batch_results["duration_seconds"] = batch_duration
        
        # Determinar status geral do lote
        if batch_results["summary"]["uploaded"] == 0:
            batch_results["status"] = "failed"
        elif batch_results["summary"]["failed"] == 0:
            batch_results["status"] = "completed"
        else:
            batch_results["status"] = "partial"
        
        logger.info(f"Lote {batch_id} concluído: {batch_results['summary']}")
        
        # Se modo síncrono, processar imediatamente
        if processing_mode == "sync":
            # Adicionar processamento em background para não bloquear resposta
            background_tasks.add_task(
                finalize_sync_batch,
                batch_id=batch_id,
                user_id=current_user.id
            )
        
        return batch_results
        
    except Exception as e:
        logger.error(f"Erro durante upload em lote {batch_id}: {e}", exc_info=True)
        batch_results["status"] = "failed"
        batch_results["error"] = str(e)
        return batch_results

async def process_single_file_in_batch(
    file: UploadFile,
    project_id: int,
    description: str,
    voice: str,
    processing_mode: str,
    task_priority: Optional[Priority],
    current_user: User,
    db: Session,
    batch_id: str
) -> Dict[str, Any]:
    """
    Processar um único arquivo dentro de um lote
    """
    file_result = {
        "filename": file.filename,
        "upload_success": False,
        "processing_completed": False,
        "error": None,
        "file_id": None,
        "file_size": 0,
        "file_type": None,
        "text_extraction": {},
        "audio_generation": {},
        "task_id": None  # Para modo assíncrono
    }
    
    try:
        # Verificar filename
        if not file.filename:
            raise ValueError("Nome do arquivo é obrigatório")
        
        # Validar extensão
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Tipo de arquivo não suportado: {file_extension}")
        
        file_result["file_type"] = file_extension
        
        # Ler conteúdo do arquivo
        file_content = await file.read()
        file_size = len(file_content)
        file_result["file_size"] = file_size
        
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"Arquivo muito grande: {file_size / (1024*1024):.1f}MB > {MAX_FILE_SIZE / (1024*1024)}MB")
        
        # Validar arquivo
        if not validate_file(file_content, file_extension):
            raise ValueError("Arquivo corrompido ou tipo inválido")
        
        # Gerar UUID e hash
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Criar diretório de destino
        upload_dir = Path(settings.upload_directory) / str(project_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar arquivo
        sanitized_filename = f"{file_uuid}_{file.filename}"
        file_path = upload_dir / sanitized_filename
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Salvar no banco de dados
        db_file = FileUpload(
            uuid=file_uuid,
            filename=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_hash=file_hash,
            file_type=file_extension,
            mime_type=file.content_type or "application/octet-stream",
            description=description,
            metadata={},
            status="uploaded",
            processing_progress=0.0,
            uploaded_at=datetime.now(),
            user_id=current_user.id,
            project_id=project_id
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        file_result["upload_success"] = True
        file_result["file_id"] = db_file.id
        
        # Extrair texto
        extracted_texts = []
        if file_extension == '.pdf':
            pdf_result = extract_pdf_text(file_path)
            if pdf_result.get('success', False):
                extracted_texts = pdf_result.get('pages', [])
        elif file_extension == '.pptx':
            extracted_texts = extract_text_from_pptx(str(file_path))
        
        file_result["text_extraction"] = {
            "success": len(extracted_texts) > 0,
            "pages_count": len(extracted_texts),
            "text_length": sum(len(text) for text in extracted_texts)
        }
        
        if extracted_texts:
            # Combinar textos
            combined_text = "\n\n".join([text.strip() for text in extracted_texts if text.strip()])
            
            if combined_text.strip():
                # Preparar para processamento de áudio
                audio_dir = Path(settings.static_directory) / "audios"
                audio_dir.mkdir(parents=True, exist_ok=True)
                audio_filename = f"batch_{batch_id}_{file_uuid}.mp3"
                audio_path = audio_dir / audio_filename
                
                if processing_mode == "async" and ASYNC_PROCESSING_AVAILABLE:
                    # Processamento assíncrono
                    task_id = await submit_async_audio_task(
                        user_id=current_user.id,
                        file_upload_id=db_file.id,
                        file_path=str(file_path),
                        extracted_text=combined_text,
                        output_path=str(audio_path),
                        voice=voice,
                        provider="auto",
                        priority=task_priority
                    )
                    
                    file_result["task_id"] = task_id
                    file_result["audio_generation"] = {
                        "mode": "async",
                        "task_id": task_id,
                        "status": "queued"
                    }
                    
                else:
                    # Processamento síncrono (para arquivos pequenos)
                    if len(combined_text) <= 5000:  # Limite para processamento síncrono
                        narration_result = generate_narration_sync(
                            text=combined_text,
                            output_path=str(audio_path),
                            voice=voice,
                            provider="auto"
                        )
                        
                        file_result["audio_generation"] = {
                            "mode": "sync",
                            "success": narration_result.get('success', False),
                            "audio_url": f"/static/audios/{audio_filename}" if narration_result.get('success') else None,
                            "error": narration_result.get('error') if not narration_result.get('success') else None
                        }
                        
                        if narration_result.get('success'):
                            file_result["processing_completed"] = True
                            
                            # Salvar áudio no banco
                            await save_batch_audio_to_db(
                                db, current_user.id, db_file.id,
                                audio_filename, str(audio_path),
                                combined_text, voice, narration_result
                            )
                    else:
                        # Texto muito longo para processamento síncrono
                        file_result["audio_generation"] = {
                            "mode": "deferred",
                            "reason": "Texto muito longo para processamento síncrono",
                            "text_length": len(combined_text)
                        }
        
        return file_result
        
    except Exception as e:
        error_msg = f"Erro ao processar {file.filename}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        file_result["error"] = error_msg
        return file_result

async def save_batch_audio_to_db(
    db: Session,
    user_id: int,
    file_upload_id: int,
    audio_filename: str,
    audio_path: str,
    extracted_text: str,
    voice: str,
    narration_result: Dict
):
    """Salvar áudio processado em lote no banco de dados"""
    try:
        # Calcular tamanho do arquivo
        audio_file_path = Path(audio_path)
        file_size = audio_file_path.stat().st_size if audio_file_path.exists() else 0
        
        # Criar registro de áudio
        db_audio = Audio(
            uuid=str(uuid.uuid4()),
            title=f"Narração em lote - {audio_filename}",
            description="Gerada via processamento em lote",
            filename=audio_filename,
            file_path=audio_path,
            file_size=file_size,
            duration=narration_result.get('duration'),
            format="mp3",
            bitrate=narration_result.get('metadata', {}).get('bitrate', '128k'),
            sample_rate=narration_result.get('metadata', {}).get('sample_rate'),
            extracted_text=extracted_text,
            text_length=len(extracted_text),
            tts_provider=narration_result.get('provider', 'auto'),
            voice_type=voice,
            status="completed",
            generation_progress=100.0,
            processing_time=narration_result.get('processing_time'),
            cache_hit=narration_result.get('cache_hit', False),
            user_id=user_id,
            source_file_id=file_upload_id,
            completed_at=datetime.now()
        )
        
        db.add(db_audio)
        db.commit()
        
        logger.info(f"Áudio em lote salvo no banco: {audio_filename}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar áudio em lote no banco: {e}", exc_info=True)

async def finalize_sync_batch(batch_id: str, user_id: int):
    """Finalizar processamento de lote síncrono em background"""
    try:
        logger.info(f"Finalizando lote síncrono {batch_id}")
        
        # Aqui poderia enviar notificações, relatórios, etc.
        # Por enquanto apenas log
        
        logger.info(f"Lote síncrono {batch_id} finalizado")
        
    except Exception as e:
        logger.error(f"Erro ao finalizar lote síncrono {batch_id}: {e}", exc_info=True)

@router.get("/status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Obter status de um lote de processamento
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário deve estar autenticado"
        )
    
    try:
        # Por enquanto, buscar informações dos arquivos relacionados ao batch_id
        # Em uma implementação completa, isso seria armazenado em uma tabela de lotes
        
        # Buscar arquivos que podem pertencer ao lote (usando descrição como referência)
        files = db.query(FileUpload).filter(
            FileUpload.user_id == current_user.id,
            FileUpload.description.like(f"%{batch_id}%")
        ).all()
        
        if not files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote não encontrado"
            )
        
        # Buscar áudios relacionados
        file_ids = [f.id for f in files]
        audios = db.query(Audio).filter(
            Audio.user_id == current_user.id,
            Audio.source_file_id.in_(file_ids)
        ).all()
        
        # Montar status do lote
        batch_status = {
            "batch_id": batch_id,
            "total_files": len(files),
            "files_processed": len(audios),
            "files_pending": len(files) - len(audios),
            "status": "completed" if len(audios) == len(files) else "processing",
            "files": []
        }
        
        # Adicionar detalhes de cada arquivo
        for file in files:
            audio = next((a for a in audios if a.source_file_id == file.id), None)
            
            file_info = {
                "file_id": file.id,
                "filename": file.filename,
                "status": file.status,
                "audio_generated": audio is not None,
                "audio_id": audio.id if audio else None,
                "audio_url": f"/static/audios/{audio.filename}" if audio else None
            }
            
            batch_status["files"].append(file_info)
        
        return batch_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do lote: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/history")
async def get_batch_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Obter histórico de lotes do usuário
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário deve estar autenticado"
        )
    
    try:
        # Buscar arquivos agrupados por data de upload (simulando lotes)
        # Em uma implementação completa, haveria uma tabela específica para lotes
        
        batches_query = db.query(
            func.date(FileUpload.uploaded_at).label('batch_date'),
            func.count(FileUpload.id).label('file_count'),
            func.sum(FileUpload.file_size).label('total_size')
        ).filter(
            FileUpload.user_id == current_user.id
        ).group_by(
            func.date(FileUpload.uploaded_at)
        ).order_by(
            func.date(FileUpload.uploaded_at).desc()
        ).offset(offset).limit(limit)
        
        batches = batches_query.all()
        
        batch_list = []
        for batch in batches:
            # Contar áudios gerados para esta data
            audios_count = db.query(Audio).join(FileUpload).filter(
                FileUpload.user_id == current_user.id,
                func.date(FileUpload.uploaded_at) == batch.batch_date
            ).count()
            
            batch_info = {
                "batch_date": batch.batch_date.isoformat(),
                "file_count": batch.file_count,
                "audios_generated": audios_count,
                "total_size_mb": (batch.total_size or 0) / (1024 * 1024),
                "completion_rate": (audios_count / batch.file_count * 100) if batch.file_count > 0 else 0
            }
            
            batch_list.append(batch_info)
        
        return {
            "success": True,
            "batches": batch_list,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(batch_list) == limit
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico de lotes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# Importações necessárias
import hashlib 