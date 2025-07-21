"""
Sistema de Notificações WebSocket - TecnoCursos AI
================================================

Sistema de notificações em tempo real para acompanhar:
- Progresso de upload de arquivos
- Status de processamento de áudios
- Notificações de conclusão
- Alertas do sistema
- Atualizações de dashboard

Funcionalidades:
1. WebSocket para conexões em tempo real
2. Salas de usuários para notificações privadas
3. Broadcasting de eventos do sistema
4. Autenticação por token JWT
5. Reconexão automática
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.routing import APIRouter
import jwt

from app.config import get_settings
from app.auth import get_user_from_token
from app.models import User

logger = logging.getLogger(__name__)
settings = get_settings()

class ConnectionManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        # Conexões ativas por usuário
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        
        # Conexões ativas por sala
        self.room_connections: Dict[str, Set[WebSocket]] = {}
        
        # Mapeamento de WebSocket para usuário
        self.connection_users: Dict[WebSocket, int] = {}
        
        # Estatísticas
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "started_at": datetime.now()
        }
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Conectar um usuário"""
        await websocket.accept()
        
        # Adicionar à lista de conexões do usuário
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # Mapear conexão para usuário
        self.connection_users[websocket] = user_id
        
        # Atualizar estatísticas
        self.stats["total_connections"] += 1
        self.stats["active_connections"] = len(self.connection_users)
        
        logger.info(f"Usuário {user_id} conectado via WebSocket. Total ativo: {self.stats['active_connections']}")
        
        # Enviar mensagem de boas-vindas
        await self.send_to_user(user_id, {
            "type": "connection_established",
            "message": "Conectado ao sistema de notificações",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        })
    
    def disconnect(self, websocket: WebSocket):
        """Desconectar um usuário"""
        user_id = self.connection_users.get(websocket)
        
        if user_id:
            # Remover da lista do usuário
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                
                # Se não há mais conexões, remover o usuário
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remover mapeamento
            del self.connection_users[websocket]
            
            # Remover de salas
            for room_connections in self.room_connections.values():
                room_connections.discard(websocket)
            
            # Atualizar estatísticas
            self.stats["active_connections"] = len(self.connection_users)
            
            logger.info(f"Usuário {user_id} desconectado. Total ativo: {self.stats['active_connections']}")
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """Enviar mensagem para um usuário específico"""
        if user_id not in self.user_connections:
            return False
        
        connections = self.user_connections[user_id].copy()
        message_json = json.dumps(message)
        
        # Remover conexões mortas
        dead_connections = set()
        
        for websocket in connections:
            try:
                await websocket.send_text(message_json)
                self.stats["messages_sent"] += 1
            except Exception as e:
                logger.warning(f"Erro ao enviar mensagem para usuário {user_id}: {e}")
                dead_connections.add(websocket)
        
        # Limpar conexões mortas
        for websocket in dead_connections:
            self.disconnect(websocket)
        
        return len(connections) - len(dead_connections) > 0
    
    async def send_to_room(self, room: str, message: Dict[str, Any]):
        """Enviar mensagem para uma sala"""
        if room not in self.room_connections:
            return 0
        
        connections = self.room_connections[room].copy()
        message_json = json.dumps(message)
        
        sent_count = 0
        dead_connections = set()
        
        for websocket in connections:
            try:
                await websocket.send_text(message_json)
                sent_count += 1
                self.stats["messages_sent"] += 1
            except Exception as e:
                logger.warning(f"Erro ao enviar mensagem para sala {room}: {e}")
                dead_connections.add(websocket)
        
        # Limpar conexões mortas
        for websocket in dead_connections:
            self.disconnect(websocket)
        
        return sent_count
    
    async def broadcast(self, message: Dict[str, Any], exclude_user: Optional[int] = None):
        """Broadcast para todos os usuários conectados"""
        message_json = json.dumps(message)
        sent_count = 0
        dead_connections = set()
        
        for websocket, user_id in self.connection_users.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(message_json)
                sent_count += 1
                self.stats["messages_sent"] += 1
            except Exception as e:
                logger.warning(f"Erro ao enviar broadcast: {e}")
                dead_connections.add(websocket)
        
        # Limpar conexões mortas
        for websocket in dead_connections:
            self.disconnect(websocket)
        
        return sent_count
    
    def join_room(self, websocket: WebSocket, room: str):
        """Adicionar conexão a uma sala"""
        if room not in self.room_connections:
            self.room_connections[room] = set()
        self.room_connections[room].add(websocket)
    
    def leave_room(self, websocket: WebSocket, room: str):
        """Remover conexão de uma sala"""
        if room in self.room_connections:
            self.room_connections[room].discard(websocket)
            
            # Se sala vazia, remover
            if not self.room_connections[room]:
                del self.room_connections[room]
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do sistema"""
        uptime = (datetime.now() - self.stats["started_at"]).total_seconds()
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "active_users": len(self.user_connections),
            "active_rooms": len(self.room_connections),
            "avg_messages_per_second": self.stats["messages_sent"] / max(uptime, 1)
        }

# Instância global do gerenciador
manager = ConnectionManager()

# Router para WebSocket
router = APIRouter()

async def get_websocket_user(websocket: WebSocket) -> Optional[User]:
    """Autenticar usuário via WebSocket usando token JWT"""
    try:
        # Obter token do query parameter ou header
        token = None
        
        # Tentar query parameter primeiro
        if "token" in websocket.query_params:
            token = websocket.query_params["token"]
        
        # Tentar header Authorization
        elif "authorization" in websocket.headers:
            auth_header = websocket.headers["authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
        
        if not token:
            return None
        
        # Verificar token
        user = get_user_from_token(token)
        return user
        
    except Exception as e:
        logger.error(f"Erro na autenticação WebSocket: {e}")
        return None

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    Endpoint WebSocket para notificações em tempo real
    
    Parâmetros de conexão:
    - token: JWT token para autenticação (query param ou header Authorization)
    
    Tipos de mensagem enviados:
    - connection_established: Conexão estabelecida
    - upload_progress: Progresso de upload
    - processing_progress: Progresso de processamento
    - processing_completed: Processamento concluído
    - system_alert: Alertas do sistema
    """
    user = await get_websocket_user(websocket)
    
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await manager.connect(websocket, user.id)
    
    try:
        while True:
            # Aguardar mensagens do cliente
            message = await websocket.receive_text()
            
            try:
                data = json.loads(message)
                await handle_client_message(websocket, user.id, data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Formato de mensagem inválido"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_client_message(websocket: WebSocket, user_id: int, data: Dict[str, Any]):
    """Processar mensagem do cliente"""
    message_type = data.get("type")
    
    if message_type == "ping":
        # Responder ping com pong
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }))
    
    elif message_type == "join_room":
        # Entrar em uma sala
        room = data.get("room")
        if room:
            manager.join_room(websocket, room)
            await websocket.send_text(json.dumps({
                "type": "room_joined",
                "room": room
            }))
    
    elif message_type == "leave_room":
        # Sair de uma sala
        room = data.get("room")
        if room:
            manager.leave_room(websocket, room)
            await websocket.send_text(json.dumps({
                "type": "room_left",
                "room": room
            }))
    
    elif message_type == "get_stats":
        # Enviar estatísticas (apenas para admins)
        # TODO: Verificar se usuário é admin
        stats = manager.get_stats()
        await websocket.send_text(json.dumps({
            "type": "stats",
            "data": stats
        }))

# Funções para envio de notificações específicas

async def notify_upload_progress(user_id: int, file_id: int, filename: str, progress: float):
    """Notificar progresso de upload"""
    await manager.send_to_user(user_id, {
        "type": "upload_progress",
        "file_id": file_id,
        "filename": filename,
        "progress": progress,
        "timestamp": datetime.now().isoformat()
    })

async def notify_processing_progress(user_id: int, task_id: str, progress: float, status: str):
    """Notificar progresso de processamento"""
    await manager.send_to_user(user_id, {
        "type": "processing_progress",
        "task_id": task_id,
        "progress": progress,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })

async def notify_processing_completed(user_id: int, task_id: str, audio_id: int, audio_url: str):
    """Notificar conclusão de processamento"""
    await manager.send_to_user(user_id, {
        "type": "processing_completed",
        "task_id": task_id,
        "audio_id": audio_id,
        "audio_url": audio_url,
        "timestamp": datetime.now().isoformat()
    })

async def notify_processing_failed(user_id: int, task_id: str, error: str):
    """Notificar falha no processamento"""
    await manager.send_to_user(user_id, {
        "type": "processing_failed",
        "task_id": task_id,
        "error": error,
        "timestamp": datetime.now().isoformat()
    })

async def notify_batch_progress(user_id: int, batch_id: str, completed: int, total: int):
    """Notificar progresso de lote"""
    await manager.send_to_user(user_id, {
        "type": "batch_progress",
        "batch_id": batch_id,
        "completed": completed,
        "total": total,
        "progress": (completed / total * 100) if total > 0 else 0,
        "timestamp": datetime.now().isoformat()
    })

async def notify_system_alert(message: str, level: str = "info", target_user: Optional[int] = None):
    """Enviar alerta do sistema"""
    alert = {
        "type": "system_alert",
        "message": message,
        "level": level,  # info, warning, error, success
        "timestamp": datetime.now().isoformat()
    }
    
    if target_user:
        await manager.send_to_user(target_user, alert)
    else:
        await manager.broadcast(alert)

# Callbacks para integração com outros serviços

async def on_async_task_progress(task):
    """Callback para progresso de tarefa assíncrona"""
    await notify_processing_progress(
        user_id=task.user_id,
        task_id=task.id,
        progress=task.progress,
        status=task.status.value
    )

async def on_async_task_completion(task):
    """Callback para conclusão de tarefa assíncrona"""
    if task.status.value == "completed":
        await notify_processing_completed(
            user_id=task.user_id,
            task_id=task.id,
            audio_id=task.audio_id,
            audio_url=f"/static/audios/{Path(task.audio_path).name}" if task.audio_path else ""
        )
    elif task.status.value == "failed":
        await notify_processing_failed(
            user_id=task.user_id,
            task_id=task.id,
            error=task.error_message or "Erro desconhecido"
        )

# Integração com processador assíncrono
def setup_async_processor_callbacks():
    """Configurar callbacks do processador assíncrono"""
    try:
        from app.services.async_audio_processor import async_processor
        
        # Adicionar callbacks
        async_processor.add_progress_callback(on_async_task_progress)
        async_processor.add_completion_callback(on_async_task_completion)
        
        logger.info("✅ Callbacks do processador assíncrono configurados")
        
    except ImportError:
        logger.warning("⚠️ Processador assíncrono não disponível para callbacks")

# Função para obter estatísticas (endpoint REST)
@router.get("/ws/stats")
async def get_websocket_stats():
    """Obter estatísticas das conexões WebSocket"""
    return manager.get_stats()

# Função para enviar notificação via API (apenas admins)
@router.post("/ws/notify")
async def send_notification(
    message: str,
    level: str = "info",
    target_user: Optional[int] = None,
    # current_user: User = Depends(require_admin)  # Descomentar quando auth estiver disponível
):
    """Enviar notificação do sistema via API"""
    await notify_system_alert(message, level, target_user)
    
    return {
        "success": True,
        "message": "Notificação enviada",
        "target": "all users" if target_user is None else f"user {target_user}"
    } 