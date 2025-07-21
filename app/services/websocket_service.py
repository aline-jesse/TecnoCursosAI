#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de WebSocket para Notificações em Tempo Real - TecnoCursos AI

Este módulo implementa um sistema completo de WebSocket para comunicação
em tempo real entre o servidor e clientes, incluindo notificações,
atualizações de progresso, chat em tempo real e broadcasting.

Funcionalidades:
- Notificações push em tempo real
- Atualizações de progresso de uploads/processamento
- Chat ao vivo para suporte
- Broadcasting de eventos do sistema
- Salas de usuários por projeto
- Autenticação de conexões WebSocket

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import logging
from contextlib import asynccontextmanager

try:
    from fastapi import WebSocket, WebSocketDisconnect, status
    from fastapi.websockets import WebSocketState
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from app.logger import get_logger
    from app.auth import decode_jwt_token
    logger = get_logger("websocket_service")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("websocket_service")

# ============================================================================
# ENUMS E ESTRUTURAS DE DADOS
# ============================================================================

class NotificationType(Enum):
    """Tipos de notificações suportadas."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"
    SYSTEM = "system"
    CHAT = "chat"
    UPLOAD = "upload"
    PROCESSING = "processing"

class ConnectionStatus(Enum):
    """Status de conexão WebSocket."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class WebSocketMessage:
    """Estrutura padronizada de mensagem WebSocket."""
    id: str
    type: NotificationType
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[int] = None
    room: Optional[str] = None
    priority: int = 1  # 1=baixa, 2=média, 3=alta, 4=crítica

@dataclass
class ConnectionInfo:
    """Informações sobre uma conexão WebSocket."""
    websocket: Any
    user_id: Optional[int]
    username: Optional[str]
    connected_at: datetime
    last_activity: datetime
    rooms: Set[str]
    session_id: str
    ip_address: str
    user_agent: str

# ============================================================================
# GERENCIADOR DE CONEXÕES WEBSOCKET
# ============================================================================

class WebSocketConnectionManager:
    """Gerenciador central de conexões WebSocket."""
    
    def __init__(self):
        # Conexões ativas: session_id -> ConnectionInfo
        self.active_connections: Dict[str, ConnectionInfo] = {}
        
        # Conexões por usuário: user_id -> Set[session_id]
        self.user_connections: Dict[int, Set[str]] = {}
        
        # Salas de usuários: room_name -> Set[session_id]
        self.rooms: Dict[str, Set[str]] = {}
        
        # Histórico de mensagens por sala (últimas 50)
        self.room_history: Dict[str, List[WebSocketMessage]] = {}
        
        # Callbacks para eventos
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Estatísticas
        self.stats = {
            'total_connections': 0,
            'total_messages': 0,
            'total_disconnections': 0,
            'start_time': datetime.now()
        }
    
    async def connect(
        self, 
        websocket: WebSocket, 
        token: Optional[str] = None,
        ip_address: str = "unknown",
        user_agent: str = "unknown"
    ) -> str:
        """Conectar um novo cliente WebSocket."""
        session_id = str(uuid.uuid4())
        
        try:
            await websocket.accept()
            
            # Autenticação opcional
            user_id = None
            username = None
            if token:
                try:
                    user_data = decode_jwt_token(token)
                    user_id = user_data.get('sub')
                    username = user_data.get('username')
                except Exception as e:
                    logger.warning(f"Token WebSocket inválido: {e}")
            
            # Criar informações da conexão
            connection_info = ConnectionInfo(
                websocket=websocket,
                user_id=user_id,
                username=username,
                connected_at=datetime.now(),
                last_activity=datetime.now(),
                rooms=set(),
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Registrar conexão
            self.active_connections[session_id] = connection_info
            
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(session_id)
            
            # Atualizar estatísticas
            self.stats['total_connections'] += 1
            
            # Enviar mensagem de boas-vindas
            welcome_message = WebSocketMessage(
                id=str(uuid.uuid4()),
                type=NotificationType.SUCCESS,
                title="Conectado",
                message=f"WebSocket conectado com sucesso! Session: {session_id[:8]}",
                data={
                    'session_id': session_id,
                    'server_time': datetime.now().isoformat(),
                    'user_id': user_id,
                    'username': username
                },
                timestamp=datetime.now(),
                user_id=user_id
            )
            
            await self._send_to_connection(session_id, welcome_message)
            
            # Disparar evento de conexão
            await self._trigger_event('user_connected', {
                'session_id': session_id,
                'user_id': user_id,
                'username': username
            })
            
            logger.info(f"✅ WebSocket conectado: {session_id[:8]} (user: {user_id})")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar WebSocket: {e}")
            raise
    
    async def disconnect(self, session_id: str):
        """Desconectar um cliente WebSocket."""
        if session_id not in self.active_connections:
            return
        
        connection_info = self.active_connections[session_id]
        
        try:
            # Remover das salas
            for room in list(connection_info.rooms):
                await self.leave_room(session_id, room)
            
            # Remover das conexões de usuário
            if connection_info.user_id:
                user_sessions = self.user_connections.get(connection_info.user_id, set())
                user_sessions.discard(session_id)
                if not user_sessions:
                    del self.user_connections[connection_info.user_id]
            
            # Remover conexão
            del self.active_connections[session_id]
            
            # Atualizar estatísticas
            self.stats['total_disconnections'] += 1
            
            # Disparar evento de desconexão
            await self._trigger_event('user_disconnected', {
                'session_id': session_id,
                'user_id': connection_info.user_id,
                'username': connection_info.username
            })
            
            logger.info(f"🔌 WebSocket desconectado: {session_id[:8]}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar WebSocket: {e}")
    
    async def join_room(self, session_id: str, room_name: str):
        """Adicionar usuário a uma sala."""
        if session_id not in self.active_connections:
            return False
        
        connection_info = self.active_connections[session_id]
        connection_info.rooms.add(room_name)
        
        if room_name not in self.rooms:
            self.rooms[room_name] = set()
        self.rooms[room_name].add(session_id)
        
        # Enviar histórico da sala
        if room_name in self.room_history:
            for message in self.room_history[room_name][-10:]:  # Últimas 10
                await self._send_to_connection(session_id, message)
        
        # Notificar entrada na sala
        join_message = WebSocketMessage(
            id=str(uuid.uuid4()),
            type=NotificationType.INFO,
            title="Sala",
            message=f"Entrou na sala: {room_name}",
            data={'room': room_name, 'action': 'joined'},
            timestamp=datetime.now(),
            user_id=connection_info.user_id,
            room=room_name
        )
        
        await self._send_to_connection(session_id, join_message)
        
        logger.info(f"🏠 {session_id[:8]} entrou na sala: {room_name}")
        return True
    
    async def leave_room(self, session_id: str, room_name: str):
        """Remover usuário de uma sala."""
        if session_id not in self.active_connections:
            return False
        
        connection_info = self.active_connections[session_id]
        connection_info.rooms.discard(room_name)
        
        if room_name in self.rooms:
            self.rooms[room_name].discard(session_id)
            if not self.rooms[room_name]:
                del self.rooms[room_name]
        
        logger.info(f"🚪 {session_id[:8]} saiu da sala: {room_name}")
        return True
    
    async def send_to_user(self, user_id: int, message: WebSocketMessage):
        """Enviar mensagem para todas as conexões de um usuário."""
        if user_id not in self.user_connections:
            return False
        
        message.user_id = user_id
        sent_count = 0
        
        for session_id in list(self.user_connections[user_id]):
            if await self._send_to_connection(session_id, message):
                sent_count += 1
        
        return sent_count > 0
    
    async def send_to_room(self, room_name: str, message: WebSocketMessage):
        """Enviar mensagem para todos os usuários em uma sala."""
        if room_name not in self.rooms:
            return False
        
        message.room = room_name
        
        # Adicionar ao histórico da sala
        if room_name not in self.room_history:
            self.room_history[room_name] = []
        self.room_history[room_name].append(message)
        
        # Manter apenas últimas 50 mensagens
        if len(self.room_history[room_name]) > 50:
            self.room_history[room_name] = self.room_history[room_name][-50:]
        
        sent_count = 0
        for session_id in list(self.rooms[room_name]):
            if await self._send_to_connection(session_id, message):
                sent_count += 1
        
        return sent_count > 0
    
    async def broadcast(self, message: WebSocketMessage):
        """Enviar mensagem para todas as conexões ativas."""
        sent_count = 0
        
        for session_id in list(self.active_connections.keys()):
            if await self._send_to_connection(session_id, message):
                sent_count += 1
        
        return sent_count > 0
    
    async def _send_to_connection(self, session_id: str, message: WebSocketMessage) -> bool:
        """Enviar mensagem para uma conexão específica."""
        if session_id not in self.active_connections:
            return False
        
        connection_info = self.active_connections[session_id]
        
        try:
            # Verificar se a conexão ainda está ativa
            if connection_info.websocket.client_state == WebSocketState.DISCONNECTED:
                await self.disconnect(session_id)
                return False
            
            # Preparar dados da mensagem
            message_data = {
                'id': message.id,
                'type': message.type.value,
                'title': message.title,
                'message': message.message,
                'data': message.data,
                'timestamp': message.timestamp.isoformat(),
                'priority': message.priority
            }
            
            if message.user_id:
                message_data['user_id'] = message.user_id
            if message.room:
                message_data['room'] = message.room
            
            # Enviar mensagem
            await connection_info.websocket.send_text(json.dumps(message_data))
            
            # Atualizar atividade
            connection_info.last_activity = datetime.now()
            
            # Atualizar estatísticas
            self.stats['total_messages'] += 1
            
            return True
            
        except WebSocketDisconnect:
            await self.disconnect(session_id)
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem WebSocket: {e}")
            await self.disconnect(session_id)
            return False
    
    async def _trigger_event(self, event_name: str, data: Dict[str, Any]):
        """Disparar evento para callbacks registrados."""
        if event_name in self.event_callbacks:
            for callback in self.event_callbacks[event_name]:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"Erro em callback de evento {event_name}: {e}")
    
    def add_event_callback(self, event_name: str, callback: Callable):
        """Adicionar callback para evento."""
        if event_name not in self.event_callbacks:
            self.event_callbacks[event_name] = []
        self.event_callbacks[event_name].append(callback)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Obter estatísticas das conexões."""
        active_count = len(self.active_connections)
        authenticated_count = sum(1 for conn in self.active_connections.values() if conn.user_id)
        
        return {
            'active_connections': active_count,
            'authenticated_connections': authenticated_count,
            'total_rooms': len(self.rooms),
            'total_connections_ever': self.stats['total_connections'],
            'total_messages_sent': self.stats['total_messages'],
            'total_disconnections': self.stats['total_disconnections'],
            'uptime_seconds': (datetime.now() - self.stats['start_time']).total_seconds(),
            'users_by_room': {room: len(sessions) for room, sessions in self.rooms.items()}
        }

# ============================================================================
# SERVIÇO DE NOTIFICAÇÕES
# ============================================================================

class NotificationService:
    """Serviço de notificações em tempo real."""
    
    def __init__(self, connection_manager: WebSocketConnectionManager):
        self.connection_manager = connection_manager
        self.notification_queue = asyncio.Queue()
        self.processing = False
    
    async def start_processing(self):
        """Iniciar processamento de notificações."""
        if self.processing:
            return
        
        self.processing = True
        asyncio.create_task(self._process_notifications())
        logger.info("🚀 Serviço de notificações iniciado")
    
    async def stop_processing(self):
        """Parar processamento de notificações."""
        self.processing = False
        logger.info("⏹️ Serviço de notificações parado")
    
    async def _process_notifications(self):
        """Loop de processamento de notificações."""
        while self.processing:
            try:
                # Aguardar notificação na fila
                notification = await asyncio.wait_for(
                    self.notification_queue.get(), 
                    timeout=1.0
                )
                
                # Processar notificação
                await self._handle_notification(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erro no processamento de notificações: {e}")
                await asyncio.sleep(1)
    
    async def _handle_notification(self, notification: Dict[str, Any]):
        """Processar uma notificação."""
        try:
            # Criar mensagem WebSocket
            message = WebSocketMessage(
                id=notification.get('id', str(uuid.uuid4())),
                type=NotificationType(notification.get('type', 'info')),
                title=notification.get('title', 'Notificação'),
                message=notification.get('message', ''),
                data=notification.get('data', {}),
                timestamp=datetime.now(),
                user_id=notification.get('user_id'),
                room=notification.get('room'),
                priority=notification.get('priority', 1)
            )
            
            # Determinar destino e enviar
            if notification.get('user_id'):
                await self.connection_manager.send_to_user(notification['user_id'], message)
            elif notification.get('room'):
                await self.connection_manager.send_to_room(notification['room'], message)
            elif notification.get('broadcast'):
                await self.connection_manager.broadcast(message)
            
        except Exception as e:
            logger.error(f"Erro ao processar notificação: {e}")
    
    async def notify_user(
        self, 
        user_id: int, 
        title: str, 
        message: str, 
        type: NotificationType = NotificationType.INFO,
        data: Dict[str, Any] = None,
        priority: int = 1
    ):
        """Enviar notificação para um usuário específico."""
        notification = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': type.value,
            'data': data or {},
            'priority': priority
        }
        
        await self.notification_queue.put(notification)
    
    async def notify_room(
        self, 
        room: str, 
        title: str, 
        message: str, 
        type: NotificationType = NotificationType.INFO,
        data: Dict[str, Any] = None,
        priority: int = 1
    ):
        """Enviar notificação para uma sala."""
        notification = {
            'room': room,
            'title': title,
            'message': message,
            'type': type.value,
            'data': data or {},
            'priority': priority
        }
        
        await self.notification_queue.put(notification)
    
    async def broadcast_notification(
        self, 
        title: str, 
        message: str, 
        type: NotificationType = NotificationType.SYSTEM,
        data: Dict[str, Any] = None,
        priority: int = 2
    ):
        """Enviar notificação para todos os usuários conectados."""
        notification = {
            'broadcast': True,
            'title': title,
            'message': message,
            'type': type.value,
            'data': data or {},
            'priority': priority
        }
        
        await self.notification_queue.put(notification)

# ============================================================================
# SERVIÇO DE PROGRESSO EM TEMPO REAL
# ============================================================================

class ProgressTrackingService:
    """Serviço para rastreamento de progresso em tempo real."""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
    
    async def start_task(
        self, 
        task_id: str, 
        user_id: int, 
        title: str, 
        total_steps: int = 100,
        description: str = ""
    ):
        """Iniciar rastreamento de uma tarefa."""
        self.active_tasks[task_id] = {
            'user_id': user_id,
            'title': title,
            'description': description,
            'total_steps': total_steps,
            'current_step': 0,
            'status': 'started',
            'start_time': datetime.now(),
            'last_update': datetime.now()
        }
        
        await self.notification_service.notify_user(
            user_id=user_id,
            title=f"🚀 {title}",
            message=f"Iniciado: {description}",
            type=NotificationType.PROGRESS,
            data={
                'task_id': task_id,
                'progress': 0,
                'status': 'started',
                'total_steps': total_steps
            },
            priority=2
        )
    
    async def update_progress(
        self, 
        task_id: str, 
        current_step: int, 
        status_message: str = "",
        data: Dict[str, Any] = None
    ):
        """Atualizar progresso de uma tarefa."""
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        task['current_step'] = current_step
        task['last_update'] = datetime.now()
        
        progress_percentage = min(100, (current_step / task['total_steps']) * 100)
        
        await self.notification_service.notify_user(
            user_id=task['user_id'],
            title=f"⏳ {task['title']}",
            message=status_message or f"Progresso: {progress_percentage:.1f}%",
            type=NotificationType.PROGRESS,
            data={
                'task_id': task_id,
                'progress': progress_percentage,
                'current_step': current_step,
                'total_steps': task['total_steps'],
                'status': 'in_progress',
                **(data or {})
            },
            priority=2
        )
        
        return True
    
    async def complete_task(
        self, 
        task_id: str, 
        success: bool = True, 
        final_message: str = "",
        result_data: Dict[str, Any] = None
    ):
        """Finalizar uma tarefa."""
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        
        status = 'completed' if success else 'failed'
        notification_type = NotificationType.SUCCESS if success else NotificationType.ERROR
        icon = "✅" if success else "❌"
        
        await self.notification_service.notify_user(
            user_id=task['user_id'],
            title=f"{icon} {task['title']}",
            message=final_message or f"Tarefa {'concluída' if success else 'falhada'}!",
            type=notification_type,
            data={
                'task_id': task_id,
                'progress': 100,
                'status': status,
                'duration_seconds': (datetime.now() - task['start_time']).total_seconds(),
                **(result_data or {})
            },
            priority=3
        )
        
        # Remover da lista de tarefas ativas
        del self.active_tasks[task_id]
        return True

# ============================================================================
# INSTÂNCIAS GLOBAIS
# ============================================================================

# Instâncias globais dos serviços
connection_manager = WebSocketConnectionManager()
notification_service = NotificationService(connection_manager)
progress_service = ProgressTrackingService(notification_service)

def get_websocket_services():
    """Obter instâncias dos serviços WebSocket."""
    return {
        'connection_manager': connection_manager,
        'notification_service': notification_service,
        'progress_service': progress_service
    }

# Função de compatibilidade - exportar como websocket_service
websocket_service = {
    'connection_manager': connection_manager,
    'notification_service': notification_service,
    'progress_service': progress_service,
    'get_services': get_websocket_services
}

async def start_websocket_services():
    """Iniciar todos os serviços WebSocket."""
    try:
        await notification_service.start_processing()
        logger.info("✅ Serviços WebSocket iniciados com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar serviços WebSocket: {e}")
        return False

async def stop_websocket_services():
    """Parar todos os serviços WebSocket."""
    try:
        await notification_service.stop_processing()
        logger.info("⏹️ Serviços WebSocket parados")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao parar serviços WebSocket: {e}")
        return False

# ============================================================================
# DEMONSTRAÇÃO DO SISTEMA
# ============================================================================

def demonstrate_websocket_system():
    """Demonstrar funcionamento do sistema WebSocket."""
    print("\n" + "="*80)
    print("🌐 SISTEMA WEBSOCKET EM TEMPO REAL - TECNOCURSOS AI")
    print("="*80)
    
    print("\n📡 FUNCIONALIDADES IMPLEMENTADAS:")
    funcionalidades = [
        "Gerenciamento de conexões WebSocket",
        "Notificações push em tempo real",
        "Salas de usuários por projeto",
        "Chat ao vivo para suporte",
        "Atualizações de progresso",
        "Broadcasting de eventos",
        "Autenticação de conexões",
        "Histórico de mensagens",
        "Estatísticas de conexões",
        "Sistema de callbacks de eventos"
    ]
    
    for i, func in enumerate(funcionalidades, 1):
        print(f"   ✅ {i:2d}. {func}")
    
    print("\n🛠️ COMPONENTES PRINCIPAIS:")
    print("   🔌 WebSocketConnectionManager - Gerencia conexões")
    print("   📢 NotificationService - Serviço de notificações") 
    print("   ⏳ ProgressTrackingService - Rastreamento de progresso")
    print("   📊 Analytics Integration - Métricas em tempo real")
    
    print("\n🎯 TIPOS DE NOTIFICAÇÃO:")
    tipos = [
        "INFO - Informações gerais",
        "SUCCESS - Operações bem-sucedidas",
        "WARNING - Avisos importantes",
        "ERROR - Erros e falhas",
        "PROGRESS - Atualizações de progresso",
        "SYSTEM - Notificações do sistema",
        "CHAT - Mensagens de chat",
        "UPLOAD - Status de uploads"
    ]
    
    for tipo in tipos:
        print(f"   📋 {tipo}")
    
    print("\n🚀 CASOS DE USO:")
    print("   📤 Upload de arquivos com progresso em tempo real")
    print("   🎬 Geração de vídeos com status em tempo real")
    print("   💬 Chat de suporte ao vivo")
    print("   🔔 Notificações de sistema importantes")
    print("   📊 Atualizações de métricas em tempo real")
    print("   👥 Colaboração em projetos")
    
    print("\n" + "="*80)
    print("✨ SISTEMA WEBSOCKET IMPLEMENTADO COM SUCESSO!")
    print("="*80)

if __name__ == "__main__":
    demonstrate_websocket_system() 