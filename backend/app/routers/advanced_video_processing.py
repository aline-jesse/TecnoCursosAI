"""
Router para Processamento Avançado de Vídeos - TecnoCursos AI
===========================================================

Este router implementa endpoints avançados para processamento de vídeos,
incluindo extração de slides de PDF, criação de vídeos em lote,
união de vídeos e pipeline completo de PDF para apresentação final.

Funcionalidades:
- Extração de slides de PDF como imagens
- Criação de vídeos em lote a partir de textos e áudios
- Conversão direta de PDF + áudio em vídeos
- União de múltiplos vídeos em apresentação final
- Pipeline completo automatizado

Autor: Sistema TecnoCursos AI
Data: Janeiro 2025
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
from pathlib import Path
import json

# Importar funções do utils
from app.utils import (
    extract_pdf_slides_as_images,
    create_videos_for_slides,
    create_videos_from_pdf_and_audio,
    stitch_videos_to_presentation,
    create_complete_presentation_from_pdf,
    optimize_batch_processing,
    validate_batch_creation_params,
    batch_create_videos_info,
    save_uploaded_file
)

# Configurar router
router = APIRouter(
    prefix="/advanced-video",
    tags=["Processamento Avançado de Vídeos"],
    responses={404: {"description": "Endpoint não encontrado"}}
)

# ==========================================
# MODELOS PYDANTIC PARA REQUESTS/RESPONSES
# ==========================================

class SlideExtractionRequest(BaseModel):
    """Modelo para solicitação de extração de slides de PDF."""
    dpi: int = Field(default=150, ge=72, le=300, description="Resolução em DPI (72-300)")
    image_format: str = Field(default="PNG", description="Formato da imagem (PNG, JPEG, WEBP)")

class SlideExtractionResponse(BaseModel):
    """Modelo para resposta de extração de slides."""
    success: bool
    slides_extracted: List[str]
    total_slides: int
    output_folder: str
    total_size_mb: float
    processing_time: float
    error: Optional[str] = None

class BatchVideoRequest(BaseModel):
    """Modelo para criação de vídeos em lote."""
    slides_text: List[str] = Field(..., min_items=1, description="Lista de textos dos slides")
    audio_files: List[str] = Field(..., min_items=1, description="Lista de arquivos de áudio")
    output_folder: str = Field(..., description="Pasta de saída dos vídeos")
    template: str = Field(default="modern", description="Template visual")
    resolution: str = Field(default="hd", description="Resolução (hd, fhd, 4k)")
    animations: bool = Field(default=True, description="Ativar animações")
    background_style: str = Field(default="gradient", description="Estilo do background")

class BatchVideoResponse(BaseModel):
    """Modelo para resposta de criação de vídeos em lote."""
    success: bool
    videos_created: List[str]
    total_videos: int
    processing_time: float
    output_folder: str
    error: Optional[str] = None

class PresentationStitchingRequest(BaseModel):
    """Modelo para união de vídeos em apresentação."""
    video_paths: List[str] = Field(..., min_items=1, description="Caminhos dos vídeos")
    output_path: str = Field(..., description="Caminho do vídeo final")
    transition_duration: float = Field(default=0.5, ge=0, le=2, description="Duração das transições")
    add_intro: bool = Field(default=True, description="Adicionar slide de introdução")
    add_outro: bool = Field(default=True, description="Adicionar slide de encerramento")
    background_music: Optional[str] = Field(default=None, description="Caminho da música de fundo")

class PresentationStitchingResponse(BaseModel):
    """Modelo para resposta de união de vídeos."""
    success: bool
    final_video_path: str
    total_duration: float
    videos_processed: int
    file_size_mb: float
    processing_time: float
    error: Optional[str] = None

class CompletePipelineRequest(BaseModel):
    """Modelo para pipeline completo PDF → Vídeo."""
    template: str = Field(default="modern", description="Template visual")
    resolution: str = Field(default="hd", description="Resolução")
    add_transitions: bool = Field(default=True, description="Adicionar transições")
    add_music: bool = Field(default=False, description="Adicionar música de fundo")

class ProcessingOptimizationResponse(BaseModel):
    """Modelo para resposta de otimização de processamento."""
    batch_size: int
    parallel_workers: int
    memory_per_worker: int
    processing_strategy: str
    estimated_time_minutes: float
    recommendations: List[str]
    system_info: Dict[str, Any]

# ==========================================
# ENDPOINTS PARA EXTRAÇÃO DE SLIDES
# ==========================================

@router.post("/extract-pdf-slides", response_model=SlideExtractionResponse)
async def extract_slides_from_pdf(
    pdf_file: UploadFile = File(..., description="Arquivo PDF para extração"),
    request_data: SlideExtractionRequest = Form(...)
):
    """
    Extrai cada página de um PDF como imagem individual (slide).

    Este endpoint processa um arquivo PDF enviado e converte cada página
    em uma imagem separada, ideal para criar slides individuais.

    - **pdf_file**: Arquivo PDF a ser processado
    - **dpi**: Resolução da imagem (72-300 DPI)
    - **image_format**: Formato da imagem de saída

    Returns:
        SlideExtractionResponse: Informações dos slides extraídos
    """
    try:
        # Validar arquivo PDF
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser um PDF")

        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            content = await pdf_file.read()
            temp_pdf.write(content)
            temp_pdf_path = temp_pdf.name

        # Criar pasta de output única
        output_folder = os.path.join("temp", f"slides_{Path(pdf_file.filename).stem}")
        os.makedirs(output_folder, exist_ok=True)

        # Extrair slides
        slides_extracted = extract_pdf_slides_as_images(
            pdf_path=temp_pdf_path,
            output_folder=output_folder,
            dpi=request_data.dpi,
            image_format=request_data.image_format
        )

        # Calcular tamanho total
        total_size = sum(os.path.getsize(slide) for slide in slides_extracted if os.path.exists(slide))
        total_size_mb = total_size / 1024 / 1024

        # Limpeza
        os.unlink(temp_pdf_path)

        return SlideExtractionResponse(
            success=True,
            slides_extracted=slides_extracted,
            total_slides=len(slides_extracted),
            output_folder=output_folder,
            total_size_mb=round(total_size_mb, 2),
            processing_time=0.0  # TODO: implementar timing
        )

    except Exception as e:
        # Limpeza em caso de erro
        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)

        raise HTTPException(status_code=500, detail=f"Erro ao extrair slides: {str(e)}")

@router.get("/download-slide/{slide_filename}")
async def download_slide_image(slide_filename: str):
    """
    Baixa uma imagem de slide específica.

    Args:
        slide_filename: Nome do arquivo de slide gerado

    Returns:
        FileResponse: Arquivo de imagem do slide
    """
    try:
        # Construir caminho do arquivo
        # Assumindo que os slides estão em temp/slides_*
        slide_path = None
        for root, dirs, files in os.walk("temp"):
            if slide_filename in files:
                slide_path = os.path.join(root, slide_filename)
                break

        if not slide_path or not os.path.exists(slide_path):
            raise HTTPException(status_code=404, detail="Slide não encontrado")

        return FileResponse(
            path=slide_path,
            filename=slide_filename,
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar slide: {str(e)}")

# ==========================================
# ENDPOINTS PARA CRIAÇÃO DE VÍDEOS EM LOTE
# ==========================================

@router.post("/create-batch-videos", response_model=BatchVideoResponse)
async def create_videos_batch(request: BatchVideoRequest):
    """
    Cria múltiplos vídeos a partir de listas de textos e áudios.

    Este endpoint usa a função create_videos_for_slides para processar
    múltiplos slides automaticamente, criando um vídeo para cada par.

    Body Parameters:
        - **slides_text**: Lista de textos para cada slide
        - **audio_files**: Lista de caminhos dos arquivos de áudio
        - **output_folder**: Pasta onde salvar os vídeos
        - **template**: Template visual (modern, corporate, tech, etc.)
        - **resolution**: Resolução (hd, fhd, 4k)
        - **animations**: Se deve adicionar animações
        - **background_style**: Estilo do background

    Returns:
        BatchVideoResponse: Informações dos vídeos criados
    """
    try:
        import time
        start_time = time.time()

        # Validar parâmetros de entrada
        validation_result = validate_batch_creation_params(
            slides_text_list=request.slides_text,
            audios_path_list=request.audio_files,
            output_folder=request.output_folder
        )

        if not validation_result["is_valid"]:
            error_details = {
                "errors": validation_result["errors"],
                "warnings": validation_result.get("warnings", [])
            }
            raise HTTPException(status_code=400, detail=error_details)

        # Criar vídeos em lote
        videos_created = create_videos_for_slides(
            slides_text_list=request.slides_text,
            audios_path_list=request.audio_files,
            output_folder=request.output_folder,
            template=request.template,
            resolution=request.resolution,
            animations=request.animations,
            background_style=request.background_style
        )

        processing_time = time.time() - start_time

        return BatchVideoResponse(
            success=True,
            videos_created=videos_created,
            total_videos=len(videos_created),
            processing_time=round(processing_time, 2),
            output_folder=request.output_folder
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na criação de vídeos: {str(e)}")

@router.post("/optimize-batch-processing")
async def optimize_batch_processing_endpoint(
    slides_count: int = Form(..., ge=1, description="Número de slides para processar"),
    available_cores: Optional[int] = Form(default=None, description="Cores CPU disponíveis"),
    memory_limit_gb: int = Form(default=8, ge=1, le=64, description="Limite de RAM em GB")
) -> ProcessingOptimizationResponse:
    """
    Calcula otimizações para processamento em lote.

    Este endpoint analisa o sistema e sugere a melhor estratégia
    para processar múltiplos vídeos de forma eficiente.

    Args:
        slides_count: Número de slides para processar
        available_cores: Cores CPU disponíveis (auto-detectar se None)
        memory_limit_gb: Limite de memória RAM em GB

    Returns:
        ProcessingOptimizationResponse: Configurações otimizadas
    """
    try:
        optimization_config = optimize_batch_processing(
            slides_count=slides_count,
            available_cores=available_cores,
            memory_limit_gb=memory_limit_gb
        )

        return ProcessingOptimizationResponse(**optimization_config)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular otimização: {str(e)}")

# ==========================================
# ENDPOINTS PARA UNIÃO DE VÍDEOS
# ==========================================

@router.post("/stitch-presentation", response_model=PresentationStitchingResponse)
async def stitch_videos_to_final_presentation(request: PresentationStitchingRequest):
    """
    Une múltiplos vídeos em uma apresentação final completa.

    Este endpoint combina vários vídeos de slides em uma apresentação
    contínua, adicionando transições, intro/outro e música de fundo.

    Body Parameters:
        - **video_paths**: Lista de caminhos dos vídeos para unir
        - **output_path**: Caminho do vídeo final
        - **transition_duration**: Duração das transições em segundos
        - **add_intro**: Se deve adicionar slide de introdução
        - **add_outro**: Se deve adicionar slide de encerramento
        - **background_music**: Caminho opcional para música de fundo

    Returns:
        PresentationStitchingResponse: Informações da apresentação criada
    """
    try:
        # Executar união dos vídeos
        result = stitch_videos_to_presentation(
            video_paths=request.video_paths,
            output_path=request.output_path,
            transition_duration=request.transition_duration,
            add_intro=request.add_intro,
            add_outro=request.add_outro,
            background_music=request.background_music
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Erro desconhecido"))

        return PresentationStitchingResponse(
            success=True,
            final_video_path=result["final_video_path"],
            total_duration=result["total_duration"],
            videos_processed=result["videos_processed"],
            file_size_mb=round(result["file_size"] / 1024 / 1024, 2),
            processing_time=result["processing_time"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na união de vídeos: {str(e)}")

# ==========================================
# PIPELINE COMPLETO
# ==========================================

@router.post("/complete-pipeline")
async def complete_pdf_to_video_pipeline(
    pdf_file: UploadFile = File(..., description="Arquivo PDF da apresentação"),
    audio_file: UploadFile = File(..., description="Arquivo de áudio/narração"),
    music_file: Optional[UploadFile] = File(default=None, description="Música de fundo opcional"),
    request_data: CompletePipelineRequest = Form(...)
):
    """
    Pipeline completo: PDF + Áudio → Apresentação de Vídeo Final.

    Este é o endpoint mais avançado do sistema, que automatiza todo o processo:
    1. Extrai slides do PDF
    2. Cria vídeos individuais
    3. Une tudo em uma apresentação final
    4. Adiciona intro/outro e música se solicitado

    Form Parameters:
        - **pdf_file**: Arquivo PDF da apresentação
        - **audio_file**: Arquivo de áudio/narração
        - **music_file**: Arquivo de música de fundo (opcional)
        - **template**: Template visual
        - **resolution**: Resolução do vídeo
        - **add_transitions**: Adicionar transições entre slides
        - **add_music**: Adicionar música de fundo

    Returns:
        dict: Resultado completo do pipeline com todas as etapas
    """
    try:
        # Validar arquivos
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Arquivo PDF inválido")

        audio_extensions = ['.mp3', '.wav', '.aac', '.m4a', '.ogg']
        if not any(audio_file.filename.lower().endswith(ext) for ext in audio_extensions):
            raise HTTPException(status_code=400, detail="Arquivo de áudio inválido")

        # Criar pasta temporária para processamento
        with tempfile.TemporaryDirectory() as temp_dir:
            # Salvar arquivos temporariamente
            pdf_path = os.path.join(temp_dir, "presentation.pdf")
            audio_path = os.path.join(temp_dir, f"audio.{audio_file.filename.split('.')[-1]}")

            with open(pdf_path, "wb") as f:
                f.write(await pdf_file.read())

            with open(audio_path, "wb") as f:
                f.write(await audio_file.read())

            # Salvar música se fornecida
            music_path = None
            if music_file and request_data.add_music:
                music_path = os.path.join(temp_dir, f"music.{music_file.filename.split('.')[-1]}")
                with open(music_path, "wb") as f:
                    f.write(await music_file.read())

            # Criar pasta de saída
            output_folder = os.path.join("outputs", f"presentation_{int(time.time())}")
            os.makedirs(output_folder, exist_ok=True)

            final_video_path = os.path.join(output_folder, "final_presentation.mp4")

            # Executar pipeline completo
            result = create_complete_presentation_from_pdf(
                pdf_path=pdf_path,
                audio_path=audio_path,
                output_path=final_video_path,
                template=request_data.template,
                resolution=request_data.resolution,
                add_transitions=request_data.add_transitions,
                add_music=request_data.add_music,
                music_path=music_path
            )

            # Copiar vídeo final para pasta permanente se bem-sucedido
            if result["success"] and os.path.exists(final_video_path):
                # O arquivo já está na pasta permanente
                pass
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "Falha no pipeline"))

            # Após extrair slides e criar vídeo, criar cenas e assets no banco
            from app.models import Scene, Asset
            import json
            created_scenes = []
            for idx, slide_img in enumerate(slides_extracted):
                scene = Scene(
                    project_id=request_data.project_id if hasattr(request_data, 'project_id') else None,
                    name=f"Slide {idx+1}",
                    ordem=idx,
                    texto="",  # Pode ser extraído se necessário
                    duracao=5.0,
                    background_type="image",
                    background_config=json.dumps({"image": slide_img}),
                    is_active=True
                )
                db.add(scene)
                db.commit()
                db.refresh(scene)
                asset = Asset(
                    name=f"Slide {idx+1} - Imagem",
                    tipo="image",
                    caminho_arquivo=slide_img,
                    scene_id=scene.id,
                    project_id=request_data.project_id if hasattr(request_data, 'project_id') else None,
                    is_library_asset=False,
                    is_public=False
                )
                db.add(asset)
                db.commit()
                db.refresh(asset)
                created_scenes.append(scene.id)

            return {
                "success": True,
                "final_video_path": final_video_path,
                "pdf_slides_processed": len(result.get("pdf_processing", {}).get("pdf_slides", [])),
                "videos_created": len(result.get("pdf_processing", {}).get("videos_created", [])),
                "total_duration": result.get("final_stitching", {}).get("total_duration", 0),
                "processing_time": result.get("total_processing_time", 0),
                "file_size_mb": round(result.get("final_stitching", {}).get("file_size", 0) / 1024 / 1024, 2),
                "template_used": request_data.template,
                "resolution_used": request_data.resolution,
                "transitions_added": request_data.add_transitions,
                "music_added": request_data.add_music and music_file is not None
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no pipeline completo: {str(e)}")

@router.get("/download-final-video/{video_filename}")
async def download_final_video(video_filename: str):
    """
    Baixa o vídeo final gerado pelo pipeline completo.

    Args:
        video_filename: Nome do arquivo de vídeo final

    Returns:
        FileResponse: Arquivo de vídeo para download
    """
    try:
        # Procurar o vídeo na pasta de outputs
        video_path = None
        for root, dirs, files in os.walk("outputs"):
            if video_filename in files:
                video_path = os.path.join(root, video_filename)
                break

        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Vídeo não encontrado")

        return FileResponse(
            path=video_path,
            filename=video_filename,
            media_type='video/mp4'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar vídeo: {str(e)}")

# ==========================================
# ENDPOINTS DE INFORMAÇÕES E STATUS
# ==========================================

@router.get("/batch-info/{slides_count}")
async def get_batch_processing_info(
    slides_count: int,
    template: str = "modern",
    resolution: str = "hd"
):
    """
    Obtém informações estimadas para processamento em lote.

    Args:
        slides_count: Número de slides para processar
        template: Template a ser usado
        resolution: Resolução dos vídeos

    Returns:
        dict: Estimativas de tempo, espaço e recursos necessários
    """
    try:
        batch_info = batch_create_videos_info(
            slides_count=slides_count,
            template=template,
            resolution=resolution
        )

        return batch_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular informações: {str(e)}")

@router.get("/system-status")
async def get_system_status():
    """
    Obtém status do sistema e recursos disponíveis.

    Returns:
        dict: Informações sobre recursos do sistema e capacidade de processamento
    """
    try:
        import psutil
        import os

        # Informações do sistema
        cpu_count = os.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')

        # Verificar dependências
        dependencies_status = {
            "moviepy": "available" if MOVIEPY_AVAILABLE else "missing",
            "pil": "available" if PIL_AVAILABLE else "missing",
            "pymupdf": "available",  # Já importado no utils.py
        }

        return {
            "system_resources": {
                "cpu_cores": cpu_count,
                "memory_total_gb": round(memory.total / 1024**3, 2),
                "memory_available_gb": round(memory.available / 1024**3, 2),
                "memory_usage_percent": memory.percent,
                "disk_total_gb": round(disk.total / 1024**3, 2),
                "disk_free_gb": round(disk.free / 1024**3, 2),
                "disk_usage_percent": round((disk.used / disk.total) * 100, 2)
            },
            "dependencies": dependencies_status,
            "capabilities": {
                "pdf_slide_extraction": True,
                "batch_video_creation": True,
                "video_stitching": dependencies_status["moviepy"] == "available",
                "complete_pipeline": all(status == "available" for status in dependencies_status.values())
            },
            "recommended_limits": {
                "max_concurrent_videos": min(cpu_count, 4),
                "max_slides_per_batch": min(cpu_count * 2, 10),
                "recommended_memory_gb": 8
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

# ==========================================
# IMPORTS E CONFIGURAÇÕES GLOBAIS
# ==========================================

# Importar variáveis globais do utils
from app.utils import MOVIEPY_AVAILABLE, PIL_AVAILABLE
import time

# Inicialização do router
print("🚀 Router de Processamento Avançado de Vídeos carregado com sucesso!")
print(f"   🎬 MoviePy: {'✅ Disponível' if MOVIEPY_AVAILABLE else '❌ Indisponível'}")
print(f"   🖼️ PIL: {'✅ Disponível' if PIL_AVAILABLE else '❌ Indisponível'}")
print(f"   📄 PyMuPDF: ✅ Disponível")
print(f"   🔗 Total de endpoints: {len(router.routes)}")
