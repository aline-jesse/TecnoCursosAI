#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Modern AI Router - TecnoCursos AI Enterprise Edition 2025
===========================================================

Router REST para exposição das capacidades de IA de última geração:
- Endpoints para geração inteligente de conteúdo
- Processamento multimodal
- RAG (Retrieval-Augmented Generation)
- Orquestração de agentes
- Análise de performance de IA

Autor: TecnoCursos AI Team
Data: 2025-01-17
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import asyncio
import json

try:
    from app.services.modern_ai_service import (
        get_modern_ai_service,
        initialize_modern_ai,
        AIPrompt,
        MultimodalInput,
        ReasoningMode,
        SafetyLevel,
        AIModelType
    )
    MODERN_AI_AVAILABLE = True
except ImportError:
    MODERN_AI_AVAILABLE = False

try:
    from app.auth import get_current_user, get_current_admin_user
    from app.models import User
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

from app.logger import get_logger

logger = get_logger("modern_ai_router")

# ============================================================================
# CONFIGURAÇÃO DO ROUTER
# ============================================================================

router = APIRouter(
    prefix="/api/ai",
    tags=["🤖 Modern AI"],
    responses={
        500: {"description": "Erro interno do servidor"},
        503: {"description": "Serviço de IA indisponível"}
    }
)

# ============================================================================
# SCHEMAS DE REQUEST/RESPONSE
# ============================================================================

class IntelligentContentRequest(BaseModel):
    """Request para geração inteligente de conteúdo"""
    topic: str = Field(..., min_length=3, max_length=500, description="Tópico para o conteúdo")
    content_type: str = Field("explicação didática", description="Tipo de conteúdo a gerar")
    target_audience: str = Field("estudantes universitários", description="Público-alvo")
    reasoning_mode: str = Field("chain_of_thought", description="Modo de raciocínio")
    use_rag: bool = Field(True, description="Usar Retrieval-Augmented Generation")
    safety_level: str = Field("moderate", description="Nível de segurança")
    additional_context: Optional[str] = Field(None, description="Contexto adicional")
    examples: List[str] = Field(default_factory=list, description="Exemplos para few-shot learning")
    constraints: List[str] = Field(default_factory=list, description="Restrições para o conteúdo")

class MultimodalAnalysisRequest(BaseModel):
    """Request para análise multimodal"""
    text: Optional[str] = Field(None, description="Texto para análise")
    image_urls: List[str] = Field(default_factory=list, description="URLs das imagens")
    audio_urls: List[str] = Field(default_factory=list, description="URLs dos áudios") 
    video_urls: List[str] = Field(default_factory=list, description="URLs dos vídeos")
    analysis_type: str = Field("comprehensive", description="Tipo de análise")

class VideoOptimizationRequest(BaseModel):
    """Request para otimização de vídeo"""
    video_metadata: Dict[str, Any] = Field(..., description="Metadados do vídeo")
    target_platform: str = Field("youtube", description="Plataforma alvo")
    optimization_goals: List[str] = Field(default_factory=list, description="Objetivos de otimização")

class AIResponse(BaseModel):
    """Response padrão da IA"""
    id: str
    content: str
    confidence: float
    reasoning_trace: List[str]
    sources: List[str]
    metadata: Dict[str, Any]
    safety_flags: List[str]
    processing_time: float

class PerformanceReport(BaseModel):
    """Relatório de performance da IA"""
    service: str
    status: str
    metrics: Dict[str, Any]
    capabilities: Dict[str, Any]
    knowledge_base: Dict[str, Any]
    active_agents: int
    cache_stats: Dict[str, Any]

# ============================================================================
# ENDPOINTS DE GERAÇÃO DE CONTEÚDO
# ============================================================================

@router.post("/generate/content", response_model=AIResponse)
async def generate_intelligent_content(
    request: IntelligentContentRequest,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Gerar conteúdo educacional inteligente usando IA avançada.
    
    Utiliza técnicas de prompt engineering, chain-of-thought reasoning
    e RAG para criar conteúdo de alta qualidade.
    """
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA moderna não disponível"
        )
    
    try:
        ai_service = get_modern_ai_service()
        
        # Criar prompt estruturado
        prompt = AIPrompt(
            id=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=f"Crie um {request.content_type} sobre {request.topic} para {request.target_audience}",
            type="educational_content",
            reasoning_mode=ReasoningMode(request.reasoning_mode),
            context=request.additional_context,
            examples=request.examples,
            constraints=request.constraints,
            safety_level=SafetyLevel(request.safety_level),
            metadata={
                "topic": request.topic,
                "content_type": request.content_type,
                "target_audience": request.target_audience
            }
        )
        
        # Gerar resposta inteligente
        response = await ai_service.generate_intelligent_response(
            prompt=prompt,
            use_rag=request.use_rag
        )
        
        logger.info(f"Conteúdo gerado para tópico: {request.topic}")
        
        return AIResponse(
            id=response.id,
            content=response.content,
            confidence=response.confidence,
            reasoning_trace=response.reasoning_trace,
            sources=response.sources,
            metadata=response.metadata,
            safety_flags=response.safety_flags,
            processing_time=response.processing_time
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar conteúdo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na geração: {str(e)}")

@router.post("/analyze/multimodal")
async def analyze_multimodal_content(
    request: MultimodalAnalysisRequest,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Análise multimodal avançada de conteúdo.
    
    Processa texto, imagens, áudios e vídeos simultaneamente
    para extrair insights cross-modais.
    """
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        ai_service = get_modern_ai_service()
        
        # Criar entrada multimodal
        multimodal_input = MultimodalInput(
            text=request.text,
            image_urls=request.image_urls,
            audio_urls=request.audio_urls,
            video_urls=request.video_urls,
            metadata={"analysis_type": request.analysis_type}
        )
        
        # Processar conteúdo multimodal
        analysis_result = await ai_service.multimodal_processor.analyze_multimodal_content(
            multimodal_input
        )
        
        return {
            "analysis_id": f"multimodal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "input_summary": {
                "has_text": bool(request.text),
                "image_count": len(request.image_urls),
                "audio_count": len(request.audio_urls),
                "video_count": len(request.video_urls)
            },
            "analysis_results": analysis_result,
            "processing_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro na análise multimodal: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.post("/optimize/video", response_model=AIResponse)
async def optimize_video_with_ai(
    request: VideoOptimizationRequest,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Otimização inteligente de vídeo usando IA.
    
    Analisa metadados do vídeo e fornece recomendações
    específicas para melhorar engajamento e performance.
    """
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        ai_service = get_modern_ai_service()
        
        # Atribuir tarefa ao agente especializado
        task_id = await ai_service.agent_orchestrator.assign_task(
            "video_analysis",
            {
                "metadata": request.video_metadata,
                "platform": request.target_platform,
                "goals": request.optimization_goals
            }
        )
        
        # Otimizar usando IA
        response = await ai_service.optimize_video_content(request.video_metadata)
        
        # Adicionar informações específicas da tarefa
        response.metadata.update({
            "task_id": task_id,
            "target_platform": request.target_platform,
            "optimization_goals": request.optimization_goals
        })
        
        logger.info(f"Vídeo otimizado - Task ID: {task_id}")
        
        return AIResponse(
            id=response.id,
            content=response.content,
            confidence=response.confidence,
            reasoning_trace=response.reasoning_trace,
            sources=response.sources,
            metadata=response.metadata,
            safety_flags=response.safety_flags,
            processing_time=response.processing_time
        )
        
    except Exception as e:
        logger.error(f"Erro na otimização de vídeo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na otimização: {str(e)}")

# ============================================================================
# ENDPOINTS DE EDUCATIONAL CONTENT
# ============================================================================

@router.post("/educational/course-outline")
async def generate_course_outline(
    topic: str = Form(...),
    duration_hours: int = Form(8),
    difficulty_level: str = Form("intermediate"),
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """Gerar esboço de curso educacional completo"""
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        ai_service = get_modern_ai_service()
        
        response = await ai_service.create_educational_content(
            topic=f"Estrutura de curso sobre {topic}",
            target_audience=f"estudantes de nível {difficulty_level}",
            content_type=f"esboço de curso de {duration_hours} horas"
        )
        
        return {
            "course_outline": response.content,
            "metadata": {
                "topic": topic,
                "duration_hours": duration_hours,
                "difficulty_level": difficulty_level,
                "generated_at": datetime.now().isoformat()
            },
            "confidence": response.confidence,
            "processing_time": response.processing_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/educational/quiz-generation")
async def generate_quiz(
    content: str = Form(...),
    question_count: int = Form(5),
    question_type: str = Form("multiple_choice"),
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """Gerar quiz baseado em conteúdo fornecido"""
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        ai_service = get_modern_ai_service()
        
        prompt = AIPrompt(
            id=f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=f"Crie um quiz com {question_count} questões do tipo {question_type}",
            type="quiz_generation",
            reasoning_mode=ReasoningMode.CHAIN_OF_THOUGHT,
            context=f"Conteúdo base: {content[:500]}...",
            constraints=[
                f"Exatamente {question_count} questões",
                f"Formato: {question_type}",
                "Questões variadas em dificuldade",
                "Inclua explicações para as respostas"
            ]
        )
        
        response = await ai_service.generate_intelligent_response(prompt)
        
        return {
            "quiz": response.content,
            "question_count": question_count,
            "question_type": question_type,
            "confidence": response.confidence,
            "processing_time": response.processing_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# ============================================================================
# ENDPOINTS DE KNOWLEDGE BASE
# ============================================================================

@router.post("/knowledge/add-document")
async def add_knowledge_document(
    content: str = Form(...),
    title: str = Form(...),
    category: str = Form("general"),
    importance: str = Form("medium"),
    current_user: User = Depends(get_current_admin_user) if AUTH_AVAILABLE else None
):
    """Adicionar documento à base de conhecimento (Admin only)"""
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        ai_service = get_modern_ai_service()
        
        from app.services.modern_ai_service import KnowledgeDocument
        
        document = KnowledgeDocument(
            id=f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content,
            metadata={
                "title": title,
                "category": category,
                "importance": importance,
                "added_by": current_user.email if current_user else "system"
            }
        )
        
        success = await ai_service.knowledge_base.add_document(document)
        
        if success:
            return {
                "message": "Documento adicionado com sucesso",
                "document_id": document.id,
                "knowledge_base_size": len(ai_service.knowledge_base.documents)
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao adicionar documento")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/knowledge/search")
async def search_knowledge(
    query: str,
    top_k: int = 5,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """Buscar na base de conhecimento usando similarity search"""
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        ai_service = get_modern_ai_service()
        
        documents = await ai_service.knowledge_base.search_similar(query, top_k)
        
        return {
            "query": query,
            "results": [
                {
                    "id": doc.id,
                    "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "metadata": doc.metadata,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ],
            "total_found": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# ============================================================================
# ENDPOINTS DE MONITORAMENTO
# ============================================================================

@router.get("/performance", response_model=PerformanceReport)
async def get_ai_performance():
    """Obter relatório de performance do sistema de IA"""
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        ai_service = get_modern_ai_service()
        report = ai_service.get_performance_report()
        
        return PerformanceReport(
            service=report["service"],
            status=report["status"],
            metrics=report["metrics"],
            capabilities=report["capabilities"],
            knowledge_base=report["knowledge_base"],
            active_agents=report["active_agents"],
            cache_stats=report["cache_stats"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/capabilities")
async def get_ai_capabilities():
    """Listar todas as capacidades de IA disponíveis"""
    if not MODERN_AI_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "Serviço de IA moderna não configurado"
        }
    
    return {
        "status": "available",
        "capabilities": {
            "content_generation": {
                "description": "Geração inteligente de conteúdo educacional",
                "endpoints": ["/api/ai/generate/content", "/api/ai/educational/course-outline"]
            },
            "multimodal_analysis": {
                "description": "Análise de múltiplos tipos de mídia",
                "endpoints": ["/api/ai/analyze/multimodal"]
            },
            "video_optimization": {
                "description": "Otimização automática de vídeos",
                "endpoints": ["/api/ai/optimize/video"]
            },
            "knowledge_management": {
                "description": "Gestão inteligente de base de conhecimento",
                "endpoints": ["/api/ai/knowledge/add-document", "/api/ai/knowledge/search"]
            },
            "educational_tools": {
                "description": "Ferramentas específicas para educação",
                "endpoints": ["/api/ai/educational/quiz-generation"]
            }
        },
        "reasoning_modes": [mode.value for mode in ReasoningMode],
        "safety_levels": [level.value for level in SafetyLevel],
        "model_types": [model.value for model in AIModelType]
    }

# ============================================================================
# ENDPOINTS DE INICIALIZAÇÃO
# ============================================================================

@router.post("/initialize")
async def initialize_ai_service(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user) if AUTH_AVAILABLE else None
):
    """Inicializar serviço de IA com base de conhecimento (Admin only)"""
    if not MODERN_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    try:
        # Executar inicialização em background
        background_tasks.add_task(initialize_modern_ai)
        
        return {
            "message": "Inicialização do serviço de IA iniciada",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na inicialização: {str(e)}")

# ============================================================================
# ENDPOINT DE INFO
# ============================================================================

@router.get("/info")
async def get_ai_service_info():
    """Informações gerais sobre o serviço de IA"""
    return {
        "service": "Modern AI Service - TecnoCursos AI",
        "version": "2.0.0",
        "description": "Sistema de IA de última geração com capacidades multimodais, RAG e orquestração de agentes",
        "features": [
            "Geração inteligente de conteúdo educacional",
            "Análise multimodal (texto, imagem, áudio, vídeo)",
            "Retrieval-Augmented Generation (RAG)",
            "Chain-of-Thought Reasoning",
            "AI Agent Orchestration",
            "Knowledge Base vetorial",
            "Prompt Engineering avançado",
            "Safety e compliance automática"
        ],
        "status": "operational" if MODERN_AI_AVAILABLE else "unavailable",
        "documentation": "/docs#/🤖 Modern AI",
        "support": "support@tecnocursos.ai"
    } 