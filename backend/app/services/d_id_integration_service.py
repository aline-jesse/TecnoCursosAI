"""
Serviço de Integração D-ID - TecnoCursos AI
==========================================

Integração completa com D-ID API para criação de avatares 3D realistas:
- Criação de vídeos com avatares
- Upload de áudio personalizado
- Configuração de apresentadores
- Monitoramento de progresso
- Webhook para notificações
- Fallback para mocks

Funcionalidades:
- Múltiplos modelos de avatar
- Sincronização labial automática
- Customização de background
- Queue de processamento
- Retry automático
- Cache de resultados
"""

import asyncio
import base64
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import aiohttp
    import aiofiles
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from app.config import settings, get_api_configs
from app.services.mock_integration_service import mock_service

logger = logging.getLogger(__name__)

class VideoStatus(Enum):
    """Status do vídeo D-ID"""
    CREATED = "created"
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"
    REJECTED = "rejected"

class PresenterModel(Enum):
    """Modelos de apresentador disponíveis"""
    AMY_PROFESSIONAL = "amy-jcu4GGiYNQ"
    DANIEL_FRIENDLY = "daniel-C2Y3dHl1eHE"
    LUCIA_TECH = "lucia-MdE2NDk4ZTk4ZQ"
    MARCUS_CORPORATE = "marcus-dHB1Z2VkdWM"
    SOFIA_EDUCATIONAL = "sofia-dGV0Z2VkdWM"

@dataclass
class DIDVideoRequest:
    """Request para criação de vídeo D-ID"""
    script: str
    presenter_id: str = PresenterModel.AMY_PROFESSIONAL.value
    background_color: str = "#ffffff"
    audio_url: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded
    voice_id: Optional[str] = None
    webhook_url: Optional[str] = None
    config: Optional[Dict] = None

@dataclass
class DIDVideoResponse:
    """Resposta da criação de vídeo D-ID"""
    id: str
    status: VideoStatus
    result_url: Optional[str] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class DIDIntegrationService:
    """Serviço principal de integração D-ID"""
    
    def __init__(self):
        self.config = get_api_configs().get("d_id", {})
        self.enabled = self.config.get("enabled", False) and AIOHTTP_AVAILABLE
        self.api_url = self.config.get("api_url", "https://api.d-id.com")
        self.api_key = self.config.get("api_key")
        
        # Cache e queue
        self.video_cache = {}
        self.processing_queue = []
        self.completed_videos = {}
        
        # Rate limiting
        self.requests_per_minute = 20  # D-ID limit
        self.requests_history = []
        
        # Webhook
        self.webhook_url = self.config.get("webhook_url")
        
        if self.enabled:
            logger.info("✅ D-ID Integration Service inicializado")
        else:
            logger.warning("⚠️ D-ID não disponível - usando mocks")
    
    async def _check_rate_limit(self):
        """Verifica e aplica rate limiting"""
        now = time.time()
        self.requests_history = [
            req_time for req_time in self.requests_history 
            if now - req_time < 60
        ]
        
        if len(self.requests_history) >= self.requests_per_minute:
            wait_time = 60 - (now - self.requests_history[0])
            if wait_time > 0:
                logger.warning(f"🚦 D-ID rate limit, aguardando {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self.requests_history.append(now)
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, files: Dict = None) -> Dict:
        """Faz requisição para D-ID API"""
        if not self.enabled:
            # Fallback para mock
            if endpoint.endswith("/talks"):
                script = data.get("script", "") if data else ""
                mock_response = await mock_service.mock_d_id_create_video(script)
                return mock_response.data
            else:
                return {"error": "D-ID not available"}
        
        await self._check_rate_limit()
        
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        timeout = aiohttp.ClientTimeout(total=60)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method.upper() == "POST":
                    if files:
                        # Para upload de arquivos
                        data_form = aiohttp.FormData()
                        for key, value in (data or {}).items():
                            data_form.add_field(key, str(value))
                        for key, file_data in files.items():
                            data_form.add_field(key, file_data)
                        
                        headers.pop("Content-Type", None)  # FormData define automaticamente
                        async with session.post(url, headers=headers, data=data_form) as response:
                            response_data = await response.json()
                    else:
                        async with session.post(url, headers=headers, json=data) as response:
                            response_data = await response.json()
                
                elif method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        response_data = await response.json()
                
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")
                
                if response.status >= 400:
                    logger.error(f"❌ D-ID API error: {response.status} - {response_data}")
                    return {"error": response_data.get("message", "API Error")}
                
                return response_data
                
        except asyncio.TimeoutError:
            logger.error("⏰ Timeout na requisição D-ID")
            return {"error": "Request timeout"}
        
        except Exception as e:
            logger.error(f"❌ Erro na requisição D-ID: {e}")
            return {"error": str(e)}
    
    async def create_video_from_text(self, request: DIDVideoRequest) -> DIDVideoResponse:
        """Cria vídeo D-ID a partir de texto"""
        
        # Preparar payload
        payload = {
            "script": {
                "type": "text",
                "input": request.script,
                "provider": {
                    "type": "microsoft",
                    "voice_id": request.voice_id or "pt-BR-FranciscaNeural"
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0,
                "stitch": True,
                "result_format": "mp4"
            },
            "source_url": f"https://d-id-public-bucket.s3.amazonaws.com/or-roman.jpg"  # Avatar padrão
        }
        
        # Adicionar presenter se especificado
        if request.presenter_id:
            payload["presenter_id"] = request.presenter_id
        
        # Adicionar configurações customizadas
        if request.config:
            payload["config"].update(request.config)
        
        # Adicionar webhook
        if request.webhook_url or self.webhook_url:
            payload["webhook"] = request.webhook_url or self.webhook_url
        
        try:
            response_data = await self._make_request("POST", "/talks", payload)
            
            if "error" in response_data:
                return DIDVideoResponse(
                    id="",
                    status=VideoStatus.ERROR,
                    error=response_data["error"]
                )
            
            video_response = DIDVideoResponse(
                id=response_data.get("id", ""),
                status=VideoStatus(response_data.get("status", "created")),
                created_at=response_data.get("created_at", datetime.now().isoformat()),
                metadata=response_data
            )
            
            # Adicionar à queue de monitoramento
            self.processing_queue.append(video_response.id)
            self.video_cache[video_response.id] = video_response
            
            logger.info(f"✅ Vídeo D-ID criado: {video_response.id}")
            return video_response
            
        except Exception as e:
            logger.error(f"❌ Erro na criação do vídeo D-ID: {e}")
            return DIDVideoResponse(
                id="",
                status=VideoStatus.ERROR,
                error=str(e)
            )
    
    async def create_video_from_audio(self, request: DIDVideoRequest, audio_file_path: str) -> DIDVideoResponse:
        """Cria vídeo D-ID a partir de arquivo de áudio"""
        
        try:
            # Ler arquivo de áudio
            async with aiofiles.open(audio_file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Preparar payload
            payload = {
                "script": {
                    "type": "audio",
                    "audio_url": f"data:audio/mp3;base64,{audio_base64}"
                },
                "config": {
                    "fluent": True,
                    "pad_audio": 0.0,
                    "stitch": True,
                    "result_format": "mp4"
                },
                "source_url": f"https://d-id-public-bucket.s3.amazonaws.com/or-roman.jpg"
            }
            
            # Adicionar presenter
            if request.presenter_id:
                payload["presenter_id"] = request.presenter_id
            
            # Webhook
            if request.webhook_url or self.webhook_url:
                payload["webhook"] = request.webhook_url or self.webhook_url
            
            response_data = await self._make_request("POST", "/talks", payload)
            
            if "error" in response_data:
                return DIDVideoResponse(
                    id="",
                    status=VideoStatus.ERROR,
                    error=response_data["error"]
                )
            
            video_response = DIDVideoResponse(
                id=response_data.get("id", ""),
                status=VideoStatus(response_data.get("status", "created")),
                created_at=response_data.get("created_at", datetime.now().isoformat()),
                metadata=response_data
            )
            
            self.processing_queue.append(video_response.id)
            self.video_cache[video_response.id] = video_response
            
            logger.info(f"✅ Vídeo D-ID criado com áudio: {video_response.id}")
            return video_response
            
        except Exception as e:
            logger.error(f"❌ Erro na criação com áudio: {e}")
            return DIDVideoResponse(
                id="",
                status=VideoStatus.ERROR,
                error=str(e)
            )
    
    async def get_video_status(self, video_id: str) -> DIDVideoResponse:
        """Verifica status do vídeo"""
        
        # Verificar cache primeiro
        if video_id in self.video_cache:
            cached_video = self.video_cache[video_id]
            if cached_video.status in [VideoStatus.DONE, VideoStatus.ERROR]:
                return cached_video
        
        try:
            response_data = await self._make_request("GET", f"/talks/{video_id}")
            
            if "error" in response_data:
                return DIDVideoResponse(
                    id=video_id,
                    status=VideoStatus.ERROR,
                    error=response_data["error"]
                )
            
            video_response = DIDVideoResponse(
                id=response_data.get("id", video_id),
                status=VideoStatus(response_data.get("status", "processing")),
                result_url=response_data.get("result_url"),
                created_at=response_data.get("created_at", ""),
                started_at=response_data.get("started_at"),
                completed_at=response_data.get("completed_at"),
                metadata=response_data
            )
            
            # Atualizar cache
            self.video_cache[video_id] = video_response
            
            # Remover da queue se completo
            if video_response.status in [VideoStatus.DONE, VideoStatus.ERROR]:
                if video_id in self.processing_queue:
                    self.processing_queue.remove(video_id)
                self.completed_videos[video_id] = video_response
            
            return video_response
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status: {e}")
            return DIDVideoResponse(
                id=video_id,
                status=VideoStatus.ERROR,
                error=str(e)
            )
    
    async def download_video(self, video_id: str, output_path: str) -> bool:
        """Download do vídeo finalizado"""
        
        video_info = await self.get_video_status(video_id)
        
        if video_info.status != VideoStatus.DONE or not video_info.result_url:
            logger.error(f"❌ Vídeo não está pronto para download: {video_info.status}")
            return False
        
        try:
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutos para download
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(video_info.result_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(output_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        logger.info(f"✅ Vídeo baixado: {output_path}")
                        return True
                    else:
                        logger.error(f"❌ Erro no download: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Erro no download do vídeo: {e}")
            return False
    
    async def wait_for_completion(self, video_id: str, max_wait_minutes: int = 10) -> DIDVideoResponse:
        """Aguarda conclusão do vídeo com polling"""
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            video_info = await self.get_video_status(video_id)
            
            if video_info.status in [VideoStatus.DONE, VideoStatus.ERROR, VideoStatus.REJECTED]:
                return video_info
            
            # Aguardar antes da próxima verificação
            await asyncio.sleep(10)
        
        # Timeout
        logger.warning(f"⏰ Timeout aguardando vídeo {video_id}")
        return DIDVideoResponse(
            id=video_id,
            status=VideoStatus.ERROR,
            error="Timeout waiting for completion"
        )
    
    async def get_credits_info(self) -> Dict[str, Any]:
        """Verifica informações de créditos da conta"""
        
        try:
            response_data = await self._make_request("GET", "/credits")
            
            if "error" in response_data:
                return {"error": response_data["error"]}
            
            return {
                "remaining": response_data.get("remaining", 0),
                "total": response_data.get("total", 0),
                "used": response_data.get("used", 0),
                "subscription": response_data.get("subscription", {}),
                "status": "active" if response_data.get("remaining", 0) > 0 else "insufficient"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar créditos: {e}")
            return {"error": str(e)}
    
    def get_available_presenters(self) -> List[Dict[str, str]]:
        """Retorna lista de apresentadores disponíveis"""
        return [
            {
                "id": PresenterModel.AMY_PROFESSIONAL.value,
                "name": "Amy (Professional)",
                "description": "Avatar feminina profissional"
            },
            {
                "id": PresenterModel.DANIEL_FRIENDLY.value,
                "name": "Daniel (Friendly)",
                "description": "Avatar masculino amigável"
            },
            {
                "id": PresenterModel.LUCIA_TECH.value,
                "name": "Lucia (Tech)",
                "description": "Avatar feminina tecnológica"
            },
            {
                "id": PresenterModel.MARCUS_CORPORATE.value,
                "name": "Marcus (Corporate)",
                "description": "Avatar masculino corporativo"
            },
            {
                "id": PresenterModel.SOFIA_EDUCATIONAL.value,
                "name": "Sofia (Educational)",
                "description": "Avatar feminina educacional"
            }
        ]
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Retorna status do processamento geral"""
        return {
            "queue_size": len(self.processing_queue),
            "completed_videos": len(self.completed_videos),
            "cached_videos": len(self.video_cache),
            "recent_requests": len([
                req for req in self.requests_history 
                if time.time() - req < 300
            ]),
            "processing_videos": [
                {"id": vid_id, "status": self.video_cache.get(vid_id, {}).status}
                for vid_id in self.processing_queue
            ]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check do serviço D-ID"""
        return {
            "service": "D-ID Integration",
            "enabled": self.enabled,
            "api_available": AIOHTTP_AVAILABLE,
            "api_url": self.api_url,
            "cache_size": len(self.video_cache),
            "queue_size": len(self.processing_queue),
            "status": "healthy" if self.enabled else "mock_mode"
        }

# Instância global do serviço
did_service = DIDIntegrationService()

# Funções de conveniência
async def create_avatar_video(script: str, presenter: str = "amy", audio_file: str = None, **kwargs) -> DIDVideoResponse:
    """Função de conveniência para criação de vídeo avatar"""
    
    # Mapear nomes amigáveis para IDs
    presenter_map = {
        "amy": PresenterModel.AMY_PROFESSIONAL.value,
        "daniel": PresenterModel.DANIEL_FRIENDLY.value,
        "lucia": PresenterModel.LUCIA_TECH.value,
        "marcus": PresenterModel.MARCUS_CORPORATE.value,
        "sofia": PresenterModel.SOFIA_EDUCATIONAL.value
    }
    
    presenter_id = presenter_map.get(presenter.lower(), PresenterModel.AMY_PROFESSIONAL.value)
    
    request = DIDVideoRequest(
        script=script,
        presenter_id=presenter_id,
        **kwargs
    )
    
    if audio_file:
        return await did_service.create_video_from_audio(request, audio_file)
    else:
        return await did_service.create_video_from_text(request)

async def wait_and_download_video(video_id: str, output_path: str, max_wait: int = 10) -> bool:
    """Função de conveniência para aguardar e baixar vídeo"""
    video_info = await did_service.wait_for_completion(video_id, max_wait)
    
    if video_info.status == VideoStatus.DONE:
        return await did_service.download_video(video_id, output_path)
    else:
        logger.error(f"❌ Vídeo não foi concluído: {video_info.status}")
        return False

async def get_account_credits() -> Dict[str, Any]:
    """Função de conveniência para verificar créditos"""
    return await did_service.get_credits_info()

if __name__ == "__main__":
    # Teste do serviço
    import asyncio
    
    async def test_did_service():
        print("🎭 Testando D-ID Integration Service...")
        
        # Verificar créditos
        credits = await get_account_credits()
        print(f"💳 Créditos: {credits}")
        
        # Criar vídeo teste
        script = "Olá! Eu sou um avatar 3D criado com inteligência artificial. Posso falar qualquer texto que você quiser!"
        
        video_result = await create_avatar_video(script, "amy")
        print(f"🎬 Vídeo criado: {video_result.id}, Status: {video_result.status}")
        
        if video_result.status != VideoStatus.ERROR:
            # Verificar status
            status = await did_service.get_video_status(video_result.id)
            print(f"📊 Status atual: {status.status}")
        
        # Health check
        health = did_service.health_check()
        print(f"🏥 Service status: {health['status']}")
        
        # Apresentadores disponíveis
        presenters = did_service.get_available_presenters()
        print(f"👥 Apresentadores: {len(presenters)} disponíveis")
    
    asyncio.run(test_did_service()) 