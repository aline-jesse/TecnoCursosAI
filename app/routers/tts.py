"""
Router para TTS (Text-to-Speech) - TecnoCursos AI
API endpoints para geração de áudio usando Bark TTS e gTTS
"""

import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile, status, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from pathlib import Path
import tempfile

from app.database import get_db
from app.auth import get_current_user_optional
from app.models import User
from app.logger import get_logger
from app.config import get_settings, get_tts_config, get_bark_voices, validate_tts_config

# Importar serviços TTS
try:
    from services.tts_service import (
        tts_service, TTSConfig, TTSProvider, AudioResult,
        generate_narration, generate_course_narration, test_tts_providers
    )
except ImportError:
    # Fallback se o serviço TTS não estiver disponível
    print("⚠️ Serviço TTS não disponível")
    tts_service = None
    TTSConfig = None
    TTSProvider = None
    AudioResult = None
    generate_narration = None
    generate_course_narration = None
    test_tts_providers = None

# Imports condicionais para funcionalidades avançadas
try:
    from app.services.tts_batch_service import create_tts_batch, get_tts_batch_status
    from app.services.tts_cache_service import get_tts_cache_stats
    from app.services.tts_analytics_service import get_tts_performance_report
    ADVANCED_TTS_FEATURES = True
except ImportError:
    ADVANCED_TTS_FEATURES = False
    print("⚠️ Funcionalidades TTS avançadas não disponíveis")

# Configurações
settings = get_settings()
logger = get_logger("tts_router")
router = APIRouter(prefix="/api/tts", tags=["tts"])

# ===============================
# SCHEMAS
# ===============================

class TTSRequest(BaseModel):
    """Schema para requisição de TTS"""
    text: str = Field(..., min_length=1, max_length=5000, description="Texto para converter em áudio")
    provider: str = Field("auto", description="Provider TTS (auto, bark, gtts)")
    voice: Optional[str] = Field("pt_speaker_0", description="Voz a ser usada (para Bark)")
    language: str = Field("pt", description="Idioma do texto")
    output_format: str = Field("mp3", description="Formato de saída (mp3, wav)")

class TTSBatchRequest(BaseModel):
    """Schema para requisição TTS em lote"""
    texts: List[str] = Field(..., min_items=1, max_items=10, description="Lista de textos")
    provider: str = Field("auto", description="Provider TTS")
    voice: Optional[str] = Field("pt_speaker_0", description="Voz a ser usada")
    language: str = Field("pt", description="Idioma dos textos")

class CourseSection(BaseModel):
    """Schema para seção de curso"""
    title: str = Field(..., description="Título da seção")
    content: str = Field(..., description="Conteúdo da seção")
    notes: Optional[str] = Field("", description="Notas adicionais")

class CourseNarrationRequest(BaseModel):
    """Schema para narração de curso"""
    sections: List[CourseSection] = Field(..., min_items=1, max_items=20)
    voice: Optional[str] = Field("pt_speaker_0", description="Voz para narração")
    provider: str = Field("auto", description="Provider TTS")

class TTSResponse(BaseModel):
    """Schema para resposta de TTS"""
    success: bool
    audio_url: Optional[str] = None
    duration: float = 0.0
    provider_used: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class TTSBatchResponse(BaseModel):
    """Schema para resposta TTS em lote"""
    success: bool
    total_files: int
    successful_files: int
    results: List[TTSResponse]
    total_duration: float
    error: Optional[str] = None

class TTSStatusResponse(BaseModel):
    """Schema para status do sistema TTS"""
    available_providers: List[str]
    available_voices: List[str]
    config: Dict[str, Any]
    system_status: Dict[str, Any]

# ===============================
# ENDPOINTS
# ===============================

@router.get("/status", response_model=TTSStatusResponse)
async def get_tts_status():
    """Obtém status do sistema TTS"""
    try:
        # Obter providers disponíveis
        providers = tts_service.get_available_providers()
        
        # Obter vozes disponíveis
        voices = get_bark_voices()
        
        # Configurações TTS
        config = get_tts_config()
        
        # Validar configurações
        validation = validate_tts_config()
        
        # Testar providers
        provider_tests = await test_tts_providers()
        
        return TTSStatusResponse(
            available_providers=providers,
            available_voices=voices,
            config=config,
            system_status={
                "config_valid": validation["valid"],
                "config_issues": validation["issues"],
                "provider_tests": provider_tests,
                "temp_dir": str(tts_service.temp_dir),
                "cache_enabled": True
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter status TTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/generate", response_model=TTSResponse)
async def generate_speech(
    request: TTSRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Gera áudio a partir de texto"""
    try:
        logger.info(f"Gerando TTS: {len(request.text)} chars, provider: {request.provider}")
        
        # Validar provider
        valid_providers = ["auto", "bark", "gtts"]
        if request.provider not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider inválido. Use: {', '.join(valid_providers)}"
            )
        
        # Configurar TTS
        config = TTSConfig(
            provider=TTSProvider(request.provider),
            voice=request.voice,
            language=request.language,
            output_format=request.output_format
        )
        
        # Gerar áudio
        result = await tts_service.generate_speech(request.text, config)
        
        if result.success:
            # Obter tamanho do arquivo
            file_size = Path(result.audio_path).stat().st_size if result.audio_path else 0
            
            # Agendar limpeza automática
            background_tasks.add_task(cleanup_audio_file, result.audio_path, delay_hours=1)
            
            return TTSResponse(
                success=True,
                audio_url=f"/api/tts/download/{Path(result.audio_path).name}",
                duration=result.duration,
                provider_used=result.provider_used,
                file_size=file_size,
                metadata=result.metadata
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na geração: {result.error}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na geração de TTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/generate-batch", response_model=TTSBatchResponse)
async def generate_speech_batch(
    request: TTSBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Gera múltiplos áudios em lote"""
    try:
        logger.info(f"Gerando TTS em lote: {len(request.texts)} textos")
        
        # Configurar TTS
        config = TTSConfig(
            provider=TTSProvider(request.provider),
            voice=request.voice,
            language=request.language
        )
        
        # Gerar áudios
        results = await tts_service.generate_batch_speech(request.texts, config)
        
        # Processar resultados
        responses = []
        successful_count = 0
        total_duration = 0
        
        for result in results:
            if result.success:
                file_size = Path(result.audio_path).stat().st_size if result.audio_path else 0
                successful_count += 1
                total_duration += result.duration
                
                # Agendar limpeza
                background_tasks.add_task(cleanup_audio_file, result.audio_path, delay_hours=1)
                
                responses.append(TTSResponse(
                    success=True,
                    audio_url=f"/api/tts/download/{Path(result.audio_path).name}",
                    duration=result.duration,
                    provider_used=result.provider_used,
                    file_size=file_size,
                    metadata=result.metadata
                ))
            else:
                responses.append(TTSResponse(
                    success=False,
                    error=result.error
                ))
        
        return TTSBatchResponse(
            success=successful_count > 0,
            total_files=len(results),
            successful_files=successful_count,
            results=responses,
            total_duration=total_duration
        )
        
    except Exception as e:
        logger.error(f"Erro na geração em lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/generate-course", response_model=TTSBatchResponse)
async def generate_course_narration_endpoint(
    request: CourseNarrationRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Gera narração para curso completo"""
    try:
        logger.info(f"Gerando narração de curso: {len(request.sections)} seções")
        
        # Converter seções para formato esperado
        course_sections = []
        for section in request.sections:
            course_sections.append({
                "title": section.title,
                "content": section.content,
                "notes": section.notes or ""
            })
        
        # Gerar narração
        results = await generate_course_narration(course_sections, voice=request.voice)
        
        # Processar resultados
        responses = []
        successful_count = 0
        total_duration = 0
        
        for i, result in enumerate(results):
            if result.success:
                file_size = Path(result.audio_path).stat().st_size if result.audio_path else 0
                successful_count += 1
                total_duration += result.duration
                
                # Agendar limpeza
                background_tasks.add_task(cleanup_audio_file, result.audio_path, delay_hours=2)
                
                responses.append(TTSResponse(
                    success=True,
                    audio_url=f"/api/tts/download/{Path(result.audio_path).name}",
                    duration=result.duration,
                    provider_used=result.provider_used,
                    file_size=file_size,
                    metadata={
                        **(result.metadata or {}),
                        "section_title": course_sections[i]["title"]
                    }
                ))
            else:
                responses.append(TTSResponse(
                    success=False,
                    error=result.error
                ))
        
        return TTSBatchResponse(
            success=successful_count > 0,
            total_files=len(results),
            successful_files=successful_count,
            results=responses,
            total_duration=total_duration
        )
        
    except Exception as e:
        logger.error(f"Erro na geração de narração de curso: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_audio(filename: str):
    """Download de arquivo de áudio gerado"""
    try:
        audio_path = tts_service.temp_dir / filename
        
        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo de áudio não encontrado"
            )
        
        # Determinar tipo de mídia
        media_type = "audio/mpeg" if filename.endswith('.mp3') else "audio/wav"
        
        return FileResponse(
            path=str(audio_path),
            media_type=media_type,
            filename=filename,
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache por 1 hora
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao baixar arquivo"
        )

@router.post("/test")
async def test_tts_system():
    """Testa todos os providers TTS disponíveis"""
    try:
        logger.info("Testando sistema TTS")
        
        # Executar testes
        provider_results = await test_tts_providers()
        
        # Teste adicional com texto em português
        test_text = "Este é um teste do sistema de síntese de voz TecnoCursos AI."
        
        test_results = {}
        for provider in ["gtts", "bark"]:
            try:
                config = TTSConfig(provider=TTSProvider(provider))
                result = await tts_service.generate_speech(test_text, config)
                
                test_results[provider] = {
                    "success": result.success,
                    "duration": result.duration,
                    "error": result.error,
                    "provider_used": result.provider_used
                }
                
                # Limpar arquivo de teste
                if result.success and result.audio_path:
                    Path(result.audio_path).unlink(missing_ok=True)
                    
            except Exception as e:
                test_results[provider] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": True,
            "provider_availability": provider_results,
            "test_results": test_results,
            "available_providers": tts_service.get_available_providers(),
            "available_voices": get_bark_voices()[:5]  # Primeiras 5 vozes
        }
        
    except Exception as e:
        logger.error(f"Erro no teste TTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no teste: {str(e)}"
        )

@router.delete("/cleanup")
async def cleanup_temp_files():
    """Limpa arquivos temporários de TTS"""
    try:
        await tts_service.cleanup_temp_files(max_age_hours=0)  # Limpar tudo
        
        return {
            "success": True,
            "message": "Arquivos temporários limpos com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na limpeza: {str(e)}"
        )

@router.post("/generate-narration")
async def generate_narration_endpoint(
    request: TTSRequest,
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Endpoint para geração de narração usando a função generate_narration do utils.py
    
    Args:
        request: Dados da requisição TTS
        user: Usuário autenticado (opcional)
    
    Returns:
        JSON com resultado da geração de áudio
        
    Example:
        POST /api/tts/generate-narration
        {
            "text": "Olá! Este é um teste de narração.",
            "provider": "gtts",
            "voice": "pt_speaker_0",
            "language": "pt"
        }
    """
    try:
        # Importar função do utils.py
        from app.utils import generate_narration
        
        # Validar dados
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Texto não pode estar vazio"
            )
        
        if len(request.text) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Texto muito longo ({len(request.text)} caracteres). Máximo: 2000."
            )
        
        # Gerar nome único para o arquivo
        import uuid
        filename = f"narration_{uuid.uuid4().hex[:8]}.mp3"
        output_path = f"temp/{filename}"
        
        # Garantir que o diretório temp existe
        Path("temp").mkdir(exist_ok=True)
        
        logger.info(f"Gerando narração para {'usuário ' + str(user.id) if user else 'usuário anônimo'}")
        logger.info(f"Texto: {request.text[:100]}{'...' if len(request.text) > 100 else ''}")
        logger.info(f"Provedor: {request.provider}, Voz: {request.voice}")
        
        # Gerar narração
        result = await generate_narration(
            text=request.text,
            output_path=output_path,
            voice=request.voice,
            provider=request.provider,
            language=request.language
        )
        
        if result['success']:
            # Agendar limpeza do arquivo após 1 hora
            import asyncio
            from fastapi import BackgroundTasks
            
            logger.info(f"Narração gerada com sucesso: {result['audio_path']}")
            
            # Retornar dados do resultado
            return {
                "success": True,
                "message": "Narração gerada com sucesso",
                "audio_path": result['audio_path'],
                "duration": result['duration'],
                "provider_used": result['provider_used'],
                "filename": filename,
                "download_url": f"/api/tts/download/{filename}",
                "metadata": result.get('metadata', {})
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na geração de narração: {result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no endpoint generate_narration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_narration(filename: str):
    """
    Download de arquivo de narração gerado
    
    Args:
        filename: Nome do arquivo para download
        
    Returns:
        FileResponse com o arquivo de áudio
    """
    try:
        file_path = Path(f"temp/{filename}")
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo não encontrado"
            )
        
        # Verificar se é um arquivo de áudio válido
        if not filename.endswith(('.mp3', '.wav')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de arquivo inválido"
            )
        
        logger.info(f"Download do arquivo: {filename}")
        
        return FileResponse(
            path=file_path,
            media_type="audio/mpeg" if filename.endswith('.mp3') else "audio/wav",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Erro no download: {str(e)}"
         )

@router.get("/stats")
async def get_tts_statistics(
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Obter estatísticas básicas do sistema TTS
    """
    try:
        stats = {
            "basic_tts": {
                "available": True,
                "providers": ["gtts", "bark", "auto"]
            },
            "advanced_features": {
                "available": ADVANCED_TTS_FEATURES,
                "batch_processing": ADVANCED_TTS_FEATURES,
                "caching": ADVANCED_TTS_FEATURES,
                "analytics": ADVANCED_TTS_FEATURES
            }
        }
        
        # Adicionar estatísticas detalhadas se disponíveis
        if ADVANCED_TTS_FEATURES:
            try:
                cache_stats = await get_tts_cache_stats()
                stats["cache"] = {
                    "total_entries": cache_stats.get("total_entries", 0),
                    "hit_rate": cache_stats.get("hit_rate", 0),
                    "total_size_mb": cache_stats.get("total_size_mb", 0)
                }
            except Exception as e:
                logger.warning(f"Erro ao obter stats do cache: {e}")
                
        return {
            "success": True,
            "statistics": stats,
            "message": "Estatísticas obtidas com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {
            "success": False,
            "error": str(e),
            "statistics": {}
        }

@router.post("/quick-batch")
async def create_quick_batch(
    texts: List[str],
    provider: str = "auto",
    voice: Optional[str] = None,
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Criar processamento rápido em lote (versão simplificada)
    
    Máximo 10 textos para usuários não autenticados,
    50 para usuários autenticados.
    """
    try:
        # Validar limite
        max_texts = 50 if user else 10
        if len(texts) > max_texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Máximo de {max_texts} textos permitido"
            )
            
        # Validar textos
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Texto {i+1} não pode estar vazio"
                )
            if len(text) > 1000:  # Limite menor para lotes
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Texto {i+1} muito longo (máx 1000 caracteres para lotes)"
                )
                
        if ADVANCED_TTS_FEATURES:
            # Usar sistema avançado de lotes
            batch_id = await create_tts_batch(
                texts=texts,
                voice=voice,
                provider=provider,
                user_id=str(user.id) if user else None
            )
            
            return {
                "success": True,
                "message": f"Lote criado com {len(texts)} textos",
                "batch_id": batch_id,
                "status_url": f"/api/tts/advanced/batch/{batch_id}/status",
                "download_url": f"/api/tts/advanced/batch/{batch_id}/download"
            }
        else:
            # Processamento sequencial simples
            results = []
            for i, text in enumerate(texts):
                try:
                    from app.utils import generate_narration_sync
                    
                    filename = f"quick_batch_{i:03d}.mp3"
                    output_path = f"temp/{filename}"
                    
                    # Garantir diretório
                    Path("temp").mkdir(exist_ok=True)
                    
                    result = generate_narration_sync(
                        text=text,
                        output_path=output_path,
                        voice=voice,
                        provider=provider
                    )
                    
                    if result['success']:
                        results.append({
                            "index": i,
                            "success": True,
                            "filename": filename,
                            "download_url": f"/api/tts/download/{filename}",
                            "duration": result['duration']
                        })
                    else:
                        results.append({
                            "index": i,
                            "success": False,
                            "error": result['error']
                        })
                        
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": str(e)
                    })
                    
            success_count = sum(1 for r in results if r['success'])
            
            return {
                "success": True,
                "message": f"Processamento concluído: {success_count}/{len(texts)} sucessos",
                "results": results,
                "total_processed": len(texts),
                "success_count": success_count,
                "failure_count": len(texts) - success_count
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no quick-batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ===============================
# FUNÇÕES AUXILIARES
# ===============================

async def cleanup_audio_file(file_path: str, delay_hours: int = 1):
    """Limpa arquivo de áudio após delay"""
    try:
        # Aguardar delay
        await asyncio.sleep(delay_hours * 3600)
        
        # Remover arquivo
        audio_path = Path(file_path)
        if audio_path.exists():
            audio_path.unlink()
            logger.info(f"Arquivo temporário removido: {audio_path.name}")
            
    except Exception as e:
        logger.error(f"Erro ao limpar arquivo {file_path}: {e}")

# ===============================
# WEBSOCKET (FUTURO)
# ===============================

# TODO: Implementar WebSocket para progresso em tempo real
# @router.websocket("/ws/generate")
# async def websocket_tts_progress(websocket: WebSocket):
#     """WebSocket para acompanhar progresso de geração TTS"""
#     pass 