"""
Router de Integrações - TecnoCursos AI
=====================================

Endpoints para gerenciar todas as integrações externas:
- Integrações de IA (OpenAI, Anthropic, etc.)
- Serviços de avatar (D-ID, Synthesia)
- Pagamentos (Stripe, PayPal, PicPay)
- Comunicação (Email, SMS, WhatsApp)
- Autenticação social
- Monitoramento
- Mocks e testes

Funcionalidades:
- Health checks de todas as integrações
- Configuração dinâmica
- Estatísticas de uso
- Logs de chamadas
- Sistema de fallback
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import logging

# Importar serviços de integração
try:
    from app.services.mock_integration_service import mock_service, MockMode
    from app.services.openai_integration_service import (
        openai_service, 
        ContentStructureRequest, 
        NarrationScriptRequest,
        structure_content,
        generate_script,
        improve_text,
        analyze_content
    )
    from app.services.d_id_integration_service import (
        did_service,
        DIDVideoRequest,
        create_avatar_video,
        wait_and_download_video,
        get_account_credits
    )
    from app.services.stripe_integration_service import (
        stripe_service,
        PaymentRequest,
        SubscriptionRequest,
        create_payment,
        create_plan_subscription,
        check_payment
    )
    INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    INTEGRATIONS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Serviços de integração não disponíveis: {e}")

from app.auth import get_current_user
from app.models import User
from app.config import settings, get_api_configs, get_feature_flags

# Router principal
integrations_router = APIRouter(
    prefix="/api/integrations",
    tags=["Integrações"],
    dependencies=[Depends(get_current_user)]
)

logger = logging.getLogger(__name__)

# === ENDPOINTS DE STATUS E HEALTH CHECK ===

@integrations_router.get("/health", summary="Health check de todas as integrações")
async def health_check_all():
    """Verifica status de todas as integrações"""
    
    if not INTEGRATIONS_AVAILABLE:
        return {
            "status": "error",
            "message": "Serviços de integração não disponíveis",
            "services": {}
        }
    
    services_health = {}
    overall_status = "healthy"
    
    try:
        # OpenAI
        services_health["openai"] = openai_service.health_check()
        
        # D-ID
        services_health["d_id"] = did_service.health_check()
        
        # Stripe
        services_health["stripe"] = stripe_service.health_check()
        
        # Mock Service
        services_health["mock_service"] = mock_service.health_check()
        
        # Verificar se algum serviço está com problema
        for service_name, health in services_health.items():
            if health.get("status") not in ["healthy", "mock_mode"]:
                overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": services_health,
            "feature_flags": get_feature_flags(),
            "api_configs": {
                service: config.get("enabled", False) 
                for service, config in get_api_configs().items()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {e}")
        return {
            "status": "error",
            "message": str(e),
            "services": services_health
        }

@integrations_router.get("/config", summary="Configurações das integrações")
async def get_integrations_config(current_user: User = Depends(get_current_user)):
    """Retorna configurações das integrações (sem secrets)"""
    
    # Verificar se usuário é admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    api_configs = get_api_configs()
    
    # Remover informações sensíveis
    safe_configs = {}
    for service, config in api_configs.items():
        safe_config = {
            "enabled": config.get("enabled", False),
            "api_url": config.get("api_url", ""),
            "model": config.get("model", ""),
            "timeout": config.get("timeout", 60)
        }
        
        # Indicar se há API key configurada (sem mostrar)
        if config.get("api_key"):
            safe_config["api_key_configured"] = True
            safe_config["api_key_preview"] = config["api_key"][:10] + "..." if len(config["api_key"]) > 10 else "***"
        else:
            safe_config["api_key_configured"] = False
        
        safe_configs[service] = safe_config
    
    return {
        "configurations": safe_configs,
        "feature_flags": get_feature_flags(),
        "environment": settings.environment,
        "mock_mode": settings.mock_external_apis
    }

# === ENDPOINTS DE MOCK SERVICE ===

@integrations_router.get("/mock/status", summary="Status do sistema de mocks")
async def get_mock_status():
    """Retorna status do sistema de mocks"""
    
    if not INTEGRATIONS_AVAILABLE:
        return {"error": "Mock service não disponível"}
    
    return {
        "service": "Mock Integration Service",
        "statistics": mock_service.get_statistics(),
        "mode": mock_service.mode.value,
        "failure_rate": mock_service.failure_rate,
        "call_history_size": len(mock_service.call_history)
    }

@integrations_router.post("/mock/configure", summary="Configurar sistema de mocks")
async def configure_mock_service(
    mode: str = Body(..., description="Modo: success, failure, realistic, slow, fast"),
    failure_rate: float = Body(0.05, description="Taxa de falhas (0.0 a 1.0)"),
    current_user: User = Depends(get_current_user)
):
    """Configura comportamento do sistema de mocks"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Mock service não disponível")
    
    try:
        # Configurar modo
        mock_mode = MockMode(mode.lower())
        mock_service.set_mode(mock_mode)
        
        # Configurar taxa de falhas
        mock_service.set_failure_rate(failure_rate)
        
        return {
            "success": True,
            "message": f"Mock service configurado para modo {mode}",
            "mode": mock_service.mode.value,
            "failure_rate": mock_service.failure_rate
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Modo inválido: {mode}")
    
    except Exception as e:
        logger.error(f"❌ Erro ao configurar mocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.get("/mock/history", summary="Histórico de chamadas mock")
async def get_mock_history(
    service: Optional[str] = Query(None, description="Filtrar por serviço"),
    limit: int = Query(50, description="Limite de registros")
):
    """Retorna histórico de chamadas dos mocks"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Mock service não disponível")
    
    history = mock_service.get_call_history(service, limit)
    
    return {
        "history": history,
        "total_calls": len(mock_service.call_history),
        "filtered": len(history),
        "service_filter": service
    }

@integrations_router.delete("/mock/history", summary="Limpar histórico de mocks")
async def clear_mock_history(current_user: User = Depends(get_current_user)):
    """Limpa histórico de chamadas dos mocks"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Mock service não disponível")
    
    mock_service.clear_history()
    
    return {
        "success": True,
        "message": "Histórico de mocks limpo"
    }

# === ENDPOINTS DE IA ===

@integrations_router.post("/ai/structure-content", summary="Estruturar conteúdo educacional")
async def structure_educational_content(
    text: str = Body(..., description="Texto para estruturar"),
    content_type: str = Body("educational", description="Tipo: educational, course, presentation"),
    target_audience: str = Body("general", description="Público: general, beginner, intermediate, advanced"),
    max_sections: int = Body(10, description="Máximo de seções"),
    include_examples: bool = Body(True, description="Incluir exemplos")
):
    """Estrutura conteúdo educacional usando IA"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de IA não disponíveis")
    
    try:
        result = await structure_content(
            text=text,
            content_type=content_type,
            target_audience=target_audience,
            max_sections=max_sections,
            include_examples=include_examples
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na estruturação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.post("/ai/generate-script", summary="Gerar script de narração")
async def generate_narration_script(
    content: str = Body(..., description="Conteúdo para converter em script"),
    tone: str = Body("professional", description="Tom: professional, friendly, casual, academic"),
    duration_minutes: int = Body(5, description="Duração alvo em minutos"),
    voice_style: str = Body("neutral", description="Estilo: neutral, enthusiastic, calm"),
    include_pauses: bool = Body(True, description="Incluir marcadores de pausa")
):
    """Gera script otimizado para narração TTS"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de IA não disponíveis")
    
    try:
        result = await generate_script(
            content=content,
            tone=tone,
            duration_minutes=duration_minutes,
            voice_style=voice_style,
            include_pauses=include_pauses
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na geração de script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.post("/ai/improve-text", summary="Melhorar qualidade do texto")
async def improve_text_quality(
    text: str = Body(..., description="Texto para melhorar"),
    improvement_type: str = Body("general", description="Tipo: general, educational, professional, simplify, academic")
):
    """Melhora qualidade e clareza do texto usando IA"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de IA não disponíveis")
    
    try:
        result = await improve_text(text, improvement_type)
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na melhoria de texto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.post("/ai/analyze-content", summary="Analisar e gerar metadados")
async def analyze_content_metadata(
    content: str = Body(..., description="Conteúdo para analisar"),
    max_title_length: int = Body(100, description="Tamanho máximo do título")
):
    """Analisa conteúdo e gera título, resumo e metadados"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de IA não disponíveis")
    
    try:
        result = await analyze_content(content, max_title_length=max_title_length)
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.get("/ai/usage-stats", summary="Estatísticas de uso de IA")
async def get_ai_usage_statistics(
    days: int = Query(7, description="Últimos X dias"),
    current_user: User = Depends(get_current_user)
):
    """Retorna estatísticas de uso dos serviços de IA"""
    
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de IA não disponíveis")
    
    try:
        stats = openai_service.get_usage_statistics(days)
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro nas estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINTS DE AVATAR ===

@integrations_router.post("/avatar/create-video", summary="Criar vídeo com avatar")
async def create_avatar_video_endpoint(
    script: str = Body(..., description="Script para o avatar falar"),
    presenter: str = Body("amy", description="Apresentador: amy, daniel, lucia, marcus, sofia"),
    background_color: str = Body("#ffffff", description="Cor de fundo"),
    webhook_url: Optional[str] = Body(None, description="URL para webhook de conclusão")
):
    """Cria vídeo com avatar 3D usando D-ID"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de avatar não disponíveis")
    
    try:
        result = await create_avatar_video(
            script=script,
            presenter=presenter,
            background_color=background_color,
            webhook_url=webhook_url
        )
        
        return {
            "success": result.status.value not in ["error"],
            "video_id": result.id,
            "status": result.status.value,
            "created_at": result.created_at,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na criação de avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.get("/avatar/video/{video_id}", summary="Status do vídeo avatar")
async def get_avatar_video_status(video_id: str):
    """Verifica status de processamento do vídeo avatar"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de avatar não disponíveis")
    
    try:
        result = await did_service.get_video_status(video_id)
        
        return {
            "video_id": result.id,
            "status": result.status.value,
            "result_url": result.result_url,
            "created_at": result.created_at,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.get("/avatar/credits", summary="Verificar créditos D-ID")
async def check_avatar_credits(current_user: User = Depends(get_current_user)):
    """Verifica créditos disponíveis na conta D-ID"""
    
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de avatar não disponíveis")
    
    try:
        credits = await get_account_credits()
        return credits
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar créditos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.get("/avatar/presenters", summary="Listar apresentadores disponíveis")
async def list_avatar_presenters():
    """Lista apresentadores/avatares disponíveis"""
    
    if not INTEGRATIONS_AVAILABLE:
        return {"presenters": []}
    
    try:
        presenters = did_service.get_available_presenters()
        return {"presenters": presenters}
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar apresentadores: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINTS DE PAGAMENTO ===

@integrations_router.post("/payments/create", summary="Criar pagamento")
async def create_payment_endpoint(
    amount: int = Body(..., description="Valor em centavos"),
    description: str = Body(..., description="Descrição do pagamento"),
    customer_email: str = Body("", description="Email do cliente"),
    customer_name: str = Body("", description="Nome do cliente"),
    payment_method: str = Body("card", description="Método: card, pix, boleto"),
    current_user: User = Depends(get_current_user)
):
    """Cria novo pagamento via Stripe"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de pagamento não disponíveis")
    
    try:
        result = await create_payment(
            amount=amount,
            description=description,
            customer_email=customer_email or current_user.email,
            customer_name=customer_name or current_user.name,
            payment_method=payment_method
        )
        
        return {
            "payment_id": result.id,
            "status": result.status.value,
            "amount": result.amount,
            "currency": result.currency,
            "client_secret": result.client_secret,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no pagamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.get("/payments/{payment_id}", summary="Status do pagamento")
async def get_payment_status_endpoint(
    payment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Verifica status de um pagamento"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de pagamento não disponíveis")
    
    try:
        result = await check_payment(payment_id)
        
        return {
            "payment_id": result.id,
            "status": result.status.value,
            "amount": result.amount,
            "currency": result.currency,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar pagamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.post("/payments/subscription", summary="Criar assinatura")
async def create_subscription_endpoint(
    plan: str = Body(..., description="Plano: basic, pro, enterprise"),
    trial_days: int = Body(0, description="Dias de teste grátis"),
    coupon_code: Optional[str] = Body(None, description="Código de cupom"),
    current_user: User = Depends(get_current_user)
):
    """Cria nova assinatura recorrente"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de pagamento não disponíveis")
    
    try:
        result = await create_plan_subscription(
            customer_email=current_user.email,
            plan=plan,
            trial_days=trial_days,
            coupon_code=coupon_code
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na assinatura: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integrations_router.get("/payments/stats", summary="Estatísticas de pagamentos")
async def get_payment_statistics_endpoint(
    days: int = Query(30, description="Últimos X dias"),
    current_user: User = Depends(get_current_user)
):
    """Retorna estatísticas de pagamentos"""
    
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços de pagamento não disponíveis")
    
    try:
        stats = stripe_service.get_payment_statistics(days)
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro nas estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINTS DE WEBHOOK ===

@integrations_router.post("/webhooks/stripe", summary="Webhook Stripe")
async def stripe_webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Processa webhooks do Stripe"""
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Webhooks não disponíveis")
    
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature", "")
        
        # Processar em background
        background_tasks.add_task(
            stripe_service.handle_webhook,
            payload,
            signature
        )
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook Stripe: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# === ENDPOINTS DE TESTE ===

@integrations_router.post("/test/all-services", summary="Testar todas as integrações")
async def test_all_integrations(current_user: User = Depends(get_current_user)):
    """Executa teste básico em todas as integrações"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Integrações não disponíveis")
    
    test_results = {}
    
    try:
        # Teste OpenAI
        ai_result = await structure_content("Este é um teste de conteúdo educacional.")
        test_results["openai"] = {"success": ai_result.get("success", False)}
        
        # Teste D-ID
        avatar_result = await create_avatar_video("Olá! Este é um teste.", "amy")
        test_results["d_id"] = {"success": avatar_result.status.value != "error"}
        
        # Teste Stripe
        payment_result = await create_payment(100, "Teste", current_user.email)
        test_results["stripe"] = {"success": payment_result.status.value != "failed"}
        
        # Teste Mocks
        mock_stats = mock_service.get_statistics()
        test_results["mock_service"] = {"success": True, "total_calls": mock_stats["total_calls"]}
        
        overall_success = all(result.get("success", False) for result in test_results.values())
        
        return {
            "overall_success": overall_success,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro nos testes: {e}")
        return {
            "overall_success": False,
            "error": str(e),
            "test_results": test_results
        }

# === ENDPOINT PRINCIPAL ===

@integrations_router.get("/", summary="Visão geral das integrações")
async def integrations_overview():
    """Retorna visão geral de todas as integrações disponíveis"""
    
    return {
        "service": "TecnoCursos AI - Integrations Manager",
        "version": "2.0.0",
        "available_services": {
            "ai": {
                "openai": "Estruturação de conteúdo e geração de scripts",
                "anthropic": "Análise avançada de texto",
                "hugging_face": "Modelos de IA especializados"
            },
            "avatar": {
                "d_id": "Criação de avatares 3D realistas",
                "synthesia": "Vídeos corporativos com avatares"
            },
            "payments": {
                "stripe": "Pagamentos e assinaturas",
                "paypal": "Pagamentos internacionais",
                "picpay": "Pagamentos nacionais"
            },
            "communication": {
                "sendgrid": "Email transacional",
                "twilio": "SMS e comunicação",
                "whatsapp": "WhatsApp Business"
            },
            "monitoring": {
                "sentry": "Monitoramento de erros",
                "datadog": "Métricas e APM",
                "analytics": "Analytics de uso"
            }
        },
        "integrations_available": INTEGRATIONS_AVAILABLE,
        "mock_mode": settings.mock_external_apis,
        "environment": settings.environment
    }

# Adicionar router à aplicação será feito no main.py 