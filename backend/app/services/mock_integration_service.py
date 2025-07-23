"""
Serviço de Mocks Inteligentes para APIs Externas
===============================================

Este serviço fornece mocks realistas para todas as integrações externas do TecnoCursos AI,
permitindo desenvolvimento e testes sem depender de APIs reais.

Funcionalidades:
- Mocks para todas as APIs de IA (OpenAI, Anthropic, etc.)
- Mocks para serviços de avatar (D-ID, Synthesia)
- Mocks para pagamentos (Stripe, PayPal, PicPay)
- Mocks para comunicação (SendGrid, Twilio)
- Mocks para autenticação social
- Mocks para monitoramento e analytics
- Respostas realistas com delays simulados
- Sistema de falhas controladas para testes
- Logs detalhados de todas as chamadas
"""

import asyncio
import json
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MockMode(Enum):
    """Modos de operação dos mocks"""
    SUCCESS = "success"  # Sempre retorna sucesso
    FAILURE = "failure"  # Sempre retorna erro
    REALISTIC = "realistic"  # Comportamento realista (padrão)
    SLOW = "slow"  # Adiciona delays longos
    FAST = "fast"  # Sem delays

@dataclass
class MockResponse:
    """Resposta padrão dos mocks"""
    success: bool
    data: Any
    status_code: int = 200
    headers: Dict[str, str] = None
    latency_ms: int = 0
    mock_source: str = "TecnoCursos Mock Service"
    timestamp: str = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class MockIntegrationService:
    """Serviço principal de mocks para integrações"""
    
    def __init__(self):
        self.mode = MockMode.REALISTIC
        self.call_history: List[Dict] = []
        self.failure_rate = 0.05  # 5% de falhas por padrão
        self.base_latency = 200  # 200ms base
        self.max_latency = 2000  # 2s máximo
        
        # Contadores para IDs únicos
        self._counters = {
            "openai_completion": 0,
            "d_id_video": 0,
            "stripe_payment": 0,
            "email_sent": 0,
            "analytics_event": 0
        }
        
        logger.info("🎭 Mock Integration Service inicializado")
    
    def set_mode(self, mode: MockMode):
        """Define o modo de operação"""
        self.mode = mode
        logger.info(f"🎭 Mock mode alterado para: {mode.value}")
    
    def set_failure_rate(self, rate: float):
        """Define a taxa de falhas (0.0 a 1.0)"""
        self.failure_rate = max(0.0, min(1.0, rate))
        logger.info(f"🎭 Taxa de falhas definida para: {rate:.2%}")
    
    async def _simulate_latency(self) -> int:
        """Simula latência de rede"""
        if self.mode == MockMode.FAST:
            return 0
        elif self.mode == MockMode.SLOW:
            delay = random.randint(2000, 5000)
        else:
            delay = random.randint(self.base_latency, self.max_latency)
        
        await asyncio.sleep(delay / 1000)
        return delay
    
    def _should_fail(self) -> bool:
        """Determina se deve simular uma falha"""
        if self.mode == MockMode.SUCCESS:
            return False
        elif self.mode == MockMode.FAILURE:
            return True
        else:
            return random.random() < self.failure_rate
    
    def _log_call(self, service: str, method: str, params: Dict = None):
        """Registra chamada no histórico"""
        call = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "method": method,
            "params": params or {},
            "mode": self.mode.value
        }
        self.call_history.append(call)
        logger.debug(f"🎭 Mock call: {service}.{method}")
    
    # === MOCKS DE IA ===
    
    async def mock_openai_completion(self, prompt: str, **kwargs) -> MockResponse:
        """Mock para OpenAI Chat Completion"""
        self._log_call("openai", "completion", {"prompt_length": len(prompt)})
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=429,
                data={"error": "Rate limit exceeded", "code": "rate_limit"},
                latency_ms=latency
            )
        
        self._counters["openai_completion"] += 1
        
        # Simular resposta realista
        mock_response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:10]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": kwargs.get("model", "gpt-4-turbo-preview"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": self._generate_mock_ai_response(prompt)
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": random.randint(50, 300),
                "total_tokens": len(prompt.split()) + random.randint(50, 300)
            }
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    async def mock_anthropic_completion(self, prompt: str, **kwargs) -> MockResponse:
        """Mock para Anthropic Claude"""
        self._log_call("anthropic", "completion", {"prompt_length": len(prompt)})
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=400,
                data={"error": "Invalid request", "code": "invalid_request"},
                latency_ms=latency
            )
        
        mock_response = {
            "id": f"msg_{uuid.uuid4().hex[:10]}",
            "type": "message",
            "role": "assistant",
            "content": [{
                "type": "text",
                "text": self._generate_mock_ai_response(prompt)
            }],
            "model": kwargs.get("model", "claude-3-sonnet-20240229"),
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": len(prompt.split()),
                "output_tokens": random.randint(50, 300)
            }
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    def _generate_mock_ai_response(self, prompt: str) -> str:
        """Gera resposta de IA mock baseada no prompt"""
        if "estrutur" in prompt.lower() or "organiz" in prompt.lower():
            return """# Estrutura Sugerida

## Introdução
- Apresentação do tema
- Objetivos do conteúdo

## Desenvolvimento
- Conceitos fundamentais
- Exemplos práticos
- Aplicações

## Conclusão
- Resumo dos pontos principais
- Próximos passos"""
        
        elif "narr" in prompt.lower() or "script" in prompt.lower():
            return """Olá! Bem-vindos a esta apresentação. Hoje vamos explorar um tema muito importante e interessante. 

Durante nossa jornada, vamos descobrir conceitos fundamentais que irão ampliar nosso conhecimento e nos ajudar a compreender melhor este assunto.

Vamos começar nossa exploração!"""
        
        else:
            responses = [
                "Baseado no conteúdo fornecido, posso ajudar a estruturar e organizar as informações de forma clara e didática.",
                "Aqui está uma análise detalhada do material apresentado, com sugestões de melhorias.",
                "O conteúdo pode ser aprimorado com uma estrutura mais didática e exemplos práticos.",
                "Vou ajudar a transformar este material em um conteúdo educacional envolvente e eficaz."
            ]
            return random.choice(responses)
    
    # === MOCKS DE AVATAR ===
    
    async def mock_d_id_create_video(self, script: str, presenter_id: str = None, **kwargs) -> MockResponse:
        """Mock para D-ID video generation"""
        self._log_call("d_id", "create_video", {
            "script_length": len(script),
            "presenter_id": presenter_id
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=400,
                data={"error": "Insufficient credits", "code": "insufficient_credits"},
                latency_ms=latency
            )
        
        self._counters["d_id_video"] += 1
        video_id = f"vid_{uuid.uuid4().hex[:12]}"
        
        mock_response = {
            "id": video_id,
            "object": "video",
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "presenter_id": presenter_id or "amy-jcu4GGiYNQ",
            "script": script,
            "video_url": f"https://d-id-mock-videos.com/{video_id}.mp4",
            "thumbnail_url": f"https://d-id-mock-videos.com/{video_id}_thumb.jpg",
            "duration": random.randint(30, 180),
            "resolution": "1080p"
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    async def mock_synthesia_create_video(self, script: str, avatar: str = None, **kwargs) -> MockResponse:
        """Mock para Synthesia video generation"""
        self._log_call("synthesia", "create_video", {
            "script_length": len(script),
            "avatar": avatar
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=402,
                data={"error": "Payment required", "code": "payment_required"},
                latency_ms=latency
            )
        
        video_id = f"synth_{uuid.uuid4().hex[:12]}"
        
        mock_response = {
            "id": video_id,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "avatar": avatar or "anna_costume1_cameraA",
            "script": script,
            "video_url": f"https://synthesia-mock-videos.com/{video_id}.mp4",
            "webhook_url": kwargs.get("webhook_url"),
            "estimated_duration": random.randint(45, 240)
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    # === MOCKS DE TTS ===
    
    async def mock_elevenlabs_tts(self, text: str, voice_id: str = None, **kwargs) -> MockResponse:
        """Mock para ElevenLabs TTS"""
        self._log_call("elevenlabs", "tts", {
            "text_length": len(text),
            "voice_id": voice_id
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=429,
                data={"error": "Rate limit exceeded", "code": "rate_limit"},
                latency_ms=latency
            )
        
        audio_id = f"audio_{uuid.uuid4().hex[:12]}"
        
        mock_response = {
            "audio_url": f"https://elevenlabs-mock-audio.com/{audio_id}.mp3",
            "duration": len(text) * 0.05,  # ~50ms por caractere
            "voice_id": voice_id or "21m00Tcm4TlvDq8ikWAM",
            "model": kwargs.get("model", "eleven_monolingual_v1"),
            "text_length": len(text),
            "format": "mp3"
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    async def mock_azure_speech_tts(self, text: str, voice: str = None, **kwargs) -> MockResponse:
        """Mock para Azure Speech Services"""
        self._log_call("azure_speech", "tts", {
            "text_length": len(text),
            "voice": voice
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=401,
                data={"error": "Unauthorized", "code": "invalid_key"},
                latency_ms=latency
            )
        
        mock_response = {
            "audio_data": f"base64_encoded_audio_data_{uuid.uuid4().hex[:16]}",
            "voice": voice or "pt-BR-FranciscaNeural",
            "format": "mp3",
            "sample_rate": 24000,
            "duration": len(text) * 0.06
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    # === MOCKS DE PAGAMENTO ===
    
    async def mock_stripe_create_payment_intent(self, amount: int, currency: str = "brl", **kwargs) -> MockResponse:
        """Mock para Stripe Payment Intent"""
        self._log_call("stripe", "create_payment_intent", {
            "amount": amount,
            "currency": currency
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=400,
                data={"error": "Invalid amount", "code": "amount_too_small"},
                latency_ms=latency
            )
        
        self._counters["stripe_payment"] += 1
        
        mock_response = {
            "id": f"pi_{uuid.uuid4().hex[:24]}",
            "object": "payment_intent",
            "amount": amount,
            "currency": currency,
            "status": "requires_payment_method",
            "client_secret": f"pi_{uuid.uuid4().hex[:24]}_secret_{uuid.uuid4().hex[:16]}",
            "created": int(time.time()),
            "description": kwargs.get("description", "TecnoCursos AI Payment"),
            "metadata": kwargs.get("metadata", {})
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    async def mock_paypal_create_order(self, amount: float, currency: str = "BRL", **kwargs) -> MockResponse:
        """Mock para PayPal Order Creation"""
        self._log_call("paypal", "create_order", {
            "amount": amount,
            "currency": currency
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=400,
                data={"error": "INVALID_REQUEST", "error_description": "Invalid order"},
                latency_ms=latency
            )
        
        mock_response = {
            "id": f"ORDER_{uuid.uuid4().hex[:16].upper()}",
            "status": "CREATED",
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": currency,
                    "value": str(amount)
                }
            }],
            "links": [{
                "href": f"https://api-m.sandbox.paypal.com/v2/checkout/orders/ORDER_{uuid.uuid4().hex[:16].upper()}",
                "rel": "self",
                "method": "GET"
            }],
            "create_time": datetime.now().isoformat() + "Z"
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    # === MOCKS DE COMUNICAÇÃO ===
    
    async def mock_sendgrid_send_email(self, to_email: str, subject: str, content: str, **kwargs) -> MockResponse:
        """Mock para SendGrid Email"""
        self._log_call("sendgrid", "send_email", {
            "to_email": to_email,
            "subject": subject
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=400,
                data={"errors": [{"message": "Invalid email address", "field": "to"}]},
                latency_ms=latency
            )
        
        self._counters["email_sent"] += 1
        
        mock_response = {
            "message_id": f"msg_{uuid.uuid4().hex[:16]}",
            "status": "queued",
            "to": to_email,
            "subject": subject,
            "timestamp": datetime.now().isoformat(),
            "tracking_id": f"track_{uuid.uuid4().hex[:12]}"
        }
        
        return MockResponse(
            success=True,
            status_code=202,
            data=mock_response,
            latency_ms=latency
        )
    
    async def mock_twilio_send_sms(self, to_number: str, message: str, **kwargs) -> MockResponse:
        """Mock para Twilio SMS"""
        self._log_call("twilio", "send_sms", {
            "to_number": to_number,
            "message_length": len(message)
        })
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=400,
                data={"error": "Invalid phone number", "code": 21211},
                latency_ms=latency
            )
        
        mock_response = {
            "sid": f"SM{uuid.uuid4().hex[:32]}",
            "account_sid": f"AC{uuid.uuid4().hex[:32]}",
            "to": to_number,
            "from": "+15551234567",
            "body": message,
            "status": "queued",
            "direction": "outbound-api",
            "date_created": datetime.now().isoformat(),
            "price": "-0.0075",
            "price_unit": "USD"
        }
        
        return MockResponse(
            success=True,
            status_code=201,
            data=mock_response,
            latency_ms=latency
        )
    
    # === MOCKS DE AUTENTICAÇÃO SOCIAL ===
    
    async def mock_google_oauth_validate(self, token: str) -> MockResponse:
        """Mock para validação Google OAuth"""
        self._log_call("google_oauth", "validate_token", {"token_length": len(token)})
        latency = await self._simulate_latency()
        
        if self._should_fail():
            return MockResponse(
                success=False,
                status_code=401,
                data={"error": "Invalid token"},
                latency_ms=latency
            )
        
        mock_response = {
            "id": str(random.randint(100000000000000000000, 999999999999999999999)),
            "email": f"user_{uuid.uuid4().hex[:8]}@gmail.com",
            "verified_email": True,
            "name": f"Usuário {random.randint(1, 1000)}",
            "given_name": f"Usuário",
            "family_name": f"{random.randint(1, 1000)}",
            "picture": f"https://lh3.googleusercontent.com/a/default-user={uuid.uuid4().hex[:8]}",
            "locale": "pt-BR"
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    # === MOCKS DE MONITORAMENTO ===
    
    async def mock_sentry_capture_event(self, event_data: Dict) -> MockResponse:
        """Mock para Sentry event capture"""
        self._log_call("sentry", "capture_event", {"event_type": event_data.get("type", "unknown")})
        latency = await self._simulate_latency()
        
        mock_response = {
            "id": uuid.uuid4().hex,
            "project": "tecnocursos-ai",
            "timestamp": datetime.now().isoformat(),
            "status": "accepted"
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    async def mock_datadog_send_metric(self, metric_name: str, value: float, **kwargs) -> MockResponse:
        """Mock para DataDog metrics"""
        self._log_call("datadog", "send_metric", {
            "metric_name": metric_name,
            "value": value
        })
        latency = await self._simulate_latency()
        
        mock_response = {
            "status": "accepted",
            "metric": metric_name,
            "value": value,
            "timestamp": int(time.time()),
            "host": "tecnocursos-api"
        }
        
        return MockResponse(
            success=True,
            data=mock_response,
            latency_ms=latency
        )
    
    # === MÉTODOS DE UTILIDADE ===
    
    def get_call_history(self, service: str = None, limit: int = 100) -> List[Dict]:
        """Retorna histórico de chamadas"""
        history = self.call_history[-limit:]
        if service:
            history = [call for call in history if call["service"] == service]
        return history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos mocks"""
        total_calls = len(self.call_history)
        services = {}
        
        for call in self.call_history:
            service = call["service"]
            if service not in services:
                services[service] = {"calls": 0, "methods": set()}
            services[service]["calls"] += 1
            services[service]["methods"].add(call["method"])
        
        # Converter sets para lists para serialização JSON
        for service in services:
            services[service]["methods"] = list(services[service]["methods"])
        
        return {
            "total_calls": total_calls,
            "services": services,
            "counters": self._counters.copy(),
            "mode": self.mode.value,
            "failure_rate": self.failure_rate,
            "uptime": datetime.now().isoformat()
        }
    
    def clear_history(self):
        """Limpa histórico de chamadas"""
        self.call_history.clear()
        self._counters = {key: 0 for key in self._counters.keys()}
        logger.info("🎭 Histórico de mocks limpo")
    
    def health_check(self) -> Dict[str, Any]:
        """Health check do serviço de mocks"""
        return {
            "service": "Mock Integration Service",
            "status": "healthy",
            "mode": self.mode.value,
            "total_calls": len(self.call_history),
            "failure_rate": self.failure_rate,
            "timestamp": datetime.now().isoformat()
        }

# Instância global do serviço de mocks
mock_service = MockIntegrationService()

# Funções de conveniência para uso direto
async def mock_openai_chat(prompt: str, **kwargs) -> MockResponse:
    """Função de conveniência para OpenAI mock"""
    return await mock_service.mock_openai_completion(prompt, **kwargs)

async def mock_d_id_video(script: str, **kwargs) -> MockResponse:
    """Função de conveniência para D-ID mock"""
    return await mock_service.mock_d_id_create_video(script, **kwargs)

async def mock_stripe_payment(amount: int, **kwargs) -> MockResponse:
    """Função de conveniência para Stripe mock"""
    return await mock_service.mock_stripe_create_payment_intent(amount, **kwargs)

async def mock_send_email(to_email: str, subject: str, content: str, **kwargs) -> MockResponse:
    """Função de conveniência para email mock"""
    return await mock_service.mock_sendgrid_send_email(to_email, subject, content, **kwargs)

def get_mock_stats() -> Dict[str, Any]:
    """Função de conveniência para estatísticas"""
    return mock_service.get_statistics()

if __name__ == "__main__":
    # Teste básico do serviço de mocks
    import asyncio
    
    async def test_mocks():
        print("🎭 Testando Mock Integration Service...")
        
        # Teste OpenAI
        result = await mock_openai_chat("Estruture este conteúdo educacional")
        print(f"✅ OpenAI Mock: {result.success}")
        
        # Teste D-ID
        result = await mock_d_id_video("Olá! Este é um teste de avatar.")
        print(f"✅ D-ID Mock: {result.success}")
        
        # Teste Stripe
        result = await mock_stripe_payment(2999, currency="brl")
        print(f"✅ Stripe Mock: {result.success}")
        
        # Estatísticas
        stats = get_mock_stats()
        print(f"📊 Total de chamadas: {stats['total_calls']}")
        print(f"🎯 Serviços testados: {list(stats['services'].keys())}")
    
    asyncio.run(test_mocks()) 