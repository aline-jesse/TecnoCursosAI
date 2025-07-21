"""
WebSocket Manager
Gerencia conexões WebSocket para atualizações em tempo real
"""

from typing import Dict, List, Set, Optional, Any
import json
import asyncio
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import jwt

from config import settings
from logger import logger
from services.cache_service import cache_service
from database import get_db
from models import User


class ConnectionManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        # Conexões ativas: {user_id: [websockets]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # Salas/canais: {room_name: {user_ids}}
        self.rooms: Dict[str, Set[str]] = {}
        
        # Metadados das conexões
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, room: Optional[str] = None):
        """Conecta um usuário"""
        await websocket.accept()
        
        # Adicionar à lista de conexões do usuário
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        # Adicionar metadados
        connection_id = f"{user_id}_{len(self.active_connections[user_id])}"
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "websocket": websocket,
            "connected_at": datetime.now(),
            "room": room,
            "last_ping": datetime.now()
        }
        
        # Adicionar à sala se especificada
        if room:
            await self.join_room(user_id, room)
        
        # Notificar conexão
        await self._send_system_message(
            user_id, 
            "connection_established", 
            {"status": "connected", "user_id": user_id}
        )
        
        # Enviar dados iniciais
        await self._send_initial_data(user_id, websocket)
        
        logger.info(f"Usuário {user_id} conectado via WebSocket")
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Desconecta um usuário"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Remover conexão vazia
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Remover de todas as salas
                for room_name, users in self.rooms.items():
                    users.discard(user_id)
        
        # Limpar metadados
        to_remove = []
        for conn_id, metadata in self.connection_metadata.items():
            if metadata["websocket"] == websocket:
                to_remove.append(conn_id)
        
        for conn_id in to_remove:
            del self.connection_metadata[conn_id]
        
        logger.info(f"Usuário {user_id} desconectado do WebSocket")
    
    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Envia mensagem para um usuário específico"""
        if user_id not in self.active_connections:
            return False
        
        message["timestamp"] = datetime.now().isoformat()
        
        # Enviar para todas as conexões do usuário
        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem para {user_id}: {e}")
                disconnected.append(websocket)
        
        # Remover conexões com falha
        for ws in disconnected:
            await self.disconnect(ws, user_id)
        
        return True
    
    async def send_room_message(self, room: str, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Envia mensagem para todos os usuários de uma sala"""
        if room not in self.rooms:
            return False
        
        message["timestamp"] = datetime.now().isoformat()
        message["room"] = room
        
        for user_id in self.rooms[room]:
            if exclude_user and user_id == exclude_user:
                continue
            
            await self.send_personal_message(user_id, message)
        
        return True
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Envia mensagem para todos os usuários conectados"""
        message["timestamp"] = datetime.now().isoformat()
        message["broadcast"] = True
        
        for user_id in self.active_connections.keys():
            if exclude_user and user_id == exclude_user:
                continue
            
            await self.send_personal_message(user_id, message)
    
    async def join_room(self, user_id: str, room: str):
        """Adiciona usuário a uma sala"""
        if room not in self.rooms:
            self.rooms[room] = set()
        
        self.rooms[room].add(user_id)
        
        # Notificar outros usuários da sala
        await self.send_room_message(
            room,
            {
                "type": "user_joined",
                "user_id": user_id,
                "message": f"Usuário {user_id} entrou na sala"
            },
            exclude_user=user_id
        )
        
        logger.info(f"Usuário {user_id} entrou na sala {room}")
    
    async def leave_room(self, user_id: str, room: str):
        """Remove usuário de uma sala"""
        if room in self.rooms:
            self.rooms[room].discard(user_id)
            
            # Remover sala vazia
            if not self.rooms[room]:
                del self.rooms[room]
            else:
                # Notificar outros usuários
                await self.send_room_message(
                    room,
                    {
                        "type": "user_left",
                        "user_id": user_id,
                        "message": f"Usuário {user_id} saiu da sala"
                    },
                    exclude_user=user_id
                )
        
        logger.info(f"Usuário {user_id} saiu da sala {room}")
    
    async def get_room_users(self, room: str) -> List[str]:
        """Obtém usuários de uma sala"""
        return list(self.rooms.get(room, set()))
    
    async def get_user_rooms(self, user_id: str) -> List[str]:
        """Obtém salas de um usuário"""
        rooms = []
        for room_name, users in self.rooms.items():
            if user_id in users:
                rooms.append(room_name)
        return rooms
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas das conexões"""
        total_connections = sum(len(conns) for conns in self.active_connections.values())
        
        return {
            "total_users": len(self.active_connections),
            "total_connections": total_connections,
            "total_rooms": len(self.rooms),
            "connections_by_user": {
                user_id: len(conns) 
                for user_id, conns in self.active_connections.items()
            },
            "users_by_room": {
                room: len(users) 
                for room, users in self.rooms.items()
            }
        }
    
    async def _send_system_message(self, user_id: str, message_type: str, data: Dict[str, Any]):
        """Envia mensagem do sistema"""
        message = {
            "type": "system",
            "system_type": message_type,
            "data": data
        }
        await self.send_personal_message(user_id, message)
    
    async def _send_initial_data(self, user_id: str, websocket: WebSocket):
        """Envia dados iniciais após conexão"""
        try:
            # Obter dados do usuário do cache
            user_data = await cache_service.get(f"user:{user_id}")
            
            if not user_data:
                # Buscar do banco se não estiver no cache
                db = next(get_db())
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user_data = {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "is_active": user.is_active,
                        "is_admin": user.is_admin
                    }
                    # Cachear para futuras conexões
                    await cache_service.set(f"user:{user_id}", user_data, expire=1800)
                db.close()
            
            # Enviar dados iniciais
            initial_data = {
                "type": "initial_data",
                "user": user_data,
                "server_time": datetime.now().isoformat(),
                "features": {
                    "file_upload": True,
                    "real_time_processing": True,
                    "notifications": True,
                    "collaboration": True
                }
            }
            
            await websocket.send_json(initial_data)
            
        except Exception as e:
            logger.error(f"Erro ao enviar dados iniciais para {user_id}: {e}")
    
    async def handle_ping(self, user_id: str, websocket: WebSocket):
        """Manipula ping/pong para manter conexão viva"""
        try:
            pong_message = {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(pong_message)
            
            # Atualizar último ping nos metadados
            for metadata in self.connection_metadata.values():
                if metadata["websocket"] == websocket:
                    metadata["last_ping"] = datetime.now()
                    break
                    
        except Exception as e:
            logger.error(f"Erro ao responder ping de {user_id}: {e}")
    
    async def cleanup_stale_connections(self):
        """Remove conexões inativas"""
        current_time = datetime.now()
        stale_connections = []
        
        for conn_id, metadata in self.connection_metadata.items():
            # Conexões sem ping há mais de 60 segundos
            if (current_time - metadata["last_ping"]).seconds > 60:
                stale_connections.append((metadata["websocket"], metadata["user_id"]))
        
        for websocket, user_id in stale_connections:
            await self.disconnect(websocket, user_id)
            logger.info(f"Conexão inativa removida: {user_id}")


# Instância global do gerenciador
connection_manager = ConnectionManager()


class WebSocketHandler:
    """Manipulador de mensagens WebSocket"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
    
    async def handle_message(self, websocket: WebSocket, user_id: str, message: Dict[str, Any]):
        """Manipula mensagens recebidas via WebSocket"""
        try:
            message_type = message.get("type")
            
            if message_type == "ping":
                await self.manager.handle_ping(user_id, websocket)
            
            elif message_type == "join_room":
                room = message.get("room")
                if room:
                    await self.manager.join_room(user_id, room)
            
            elif message_type == "leave_room":
                room = message.get("room")
                if room:
                    await self.manager.leave_room(user_id, room)
            
            elif message_type == "room_message":
                room = message.get("room")
                content = message.get("content")
                if room and content:
                    await self.manager.send_room_message(
                        room,
                        {
                            "type": "room_message",
                            "from_user": user_id,
                            "content": content
                        },
                        exclude_user=user_id
                    )
            
            elif message_type == "get_stats":
                stats = await self.manager.get_connection_stats()
                await self.manager.send_personal_message(
                    user_id,
                    {
                        "type": "stats_response",
                        "stats": stats
                    }
                )
            
            elif message_type == "subscribe_notifications":
                # Subscrever a notificações específicas
                categories = message.get("categories", [])
                await self._subscribe_notifications(user_id, categories)
            
            else:
                logger.warning(f"Tipo de mensagem não reconhecido: {message_type}")
        
        except Exception as e:
            logger.error(f"Erro ao processar mensagem WebSocket de {user_id}: {e}")
            await self.manager.send_personal_message(
                user_id,
                {
                    "type": "error",
                    "message": "Erro ao processar mensagem",
                    "error": str(e)
                }
            )
    
    async def _subscribe_notifications(self, user_id: str, categories: List[str]):
        """Subscreve usuário a categorias de notificação"""
        # Salvar preferências no cache
        await cache_service.set(
            f"notification_preferences:{user_id}",
            {"categories": categories},
            expire=86400  # 24 horas
        )
        
        await self.manager.send_personal_message(
            user_id,
            {
                "type": "notification_subscription",
                "message": "Preferências de notificação atualizadas",
                "categories": categories
            }
        )


# Instância global do handler
websocket_handler = WebSocketHandler(connection_manager)


# Funções utilitárias para notificações específicas
async def notify_file_upload_progress(user_id: str, file_name: str, progress: int):
    """Notifica progresso de upload"""
    await connection_manager.send_personal_message(
        user_id,
        {
            "type": "file_upload_progress",
            "file_name": file_name,
            "progress": progress
        }
    )


async def notify_file_processing_status(user_id: str, file_name: str, status: str, details: Optional[Dict] = None):
    """Notifica status de processamento"""
    await connection_manager.send_personal_message(
        user_id,
        {
            "type": "file_processing_status",
            "file_name": file_name,
            "status": status,
            "details": details or {}
        }
    )


async def notify_video_ready(user_id: str, video_id: str, video_name: str, video_url: str):
    """Notifica que vídeo está pronto"""
    await connection_manager.send_personal_message(
        user_id,
        {
            "type": "video_ready",
            "video_id": video_id,
            "video_name": video_name,
            "video_url": video_url,
            "message": f"Vídeo '{video_name}' está pronto para visualização!"
        }
    )


async def notify_project_update(user_id: str, project_id: str, update_type: str, details: Dict[str, Any]):
    """Notifica atualização de projeto"""
    await connection_manager.send_personal_message(
        user_id,
        {
            "type": "project_update",
            "project_id": project_id,
            "update_type": update_type,
            "details": details
        }
    )


async def notify_system_maintenance(message: str, scheduled_time: Optional[str] = None):
    """Notifica manutenção do sistema"""
    await connection_manager.broadcast_message({
        "type": "system_maintenance",
        "message": message,
        "scheduled_time": scheduled_time,
        "severity": "warning"
    })


async def notify_new_feature(feature_name: str, description: str, learn_more_url: Optional[str] = None):
    """Notifica nova funcionalidade"""
    await connection_manager.broadcast_message({
        "type": "new_feature",
        "feature_name": feature_name,
        "description": description,
        "learn_more_url": learn_more_url,
        "severity": "info"
    })


# Função para autenticar WebSocket
def authenticate_websocket_token(token: str) -> Optional[str]:
    """Autentica token WebSocket e retorna user_id"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id:
            return user_id
    except jwt.PyJWTError:
        pass
    
    return None


# Task para limpeza periódica
async def cleanup_task():
    """Task para limpeza periódica de conexões inativas"""
    while True:
        try:
            await connection_manager.cleanup_stale_connections()
            await asyncio.sleep(30)  # Verificar a cada 30 segundos
        except Exception as e:
            logger.error(f"Erro na limpeza de conexões: {e}")
            await asyncio.sleep(60)  # Aguardar mais tempo em caso de erro


# Inicializar task de limpeza
def start_cleanup_task():
    """Inicia a task de limpeza"""
    asyncio.create_task(cleanup_task()) 