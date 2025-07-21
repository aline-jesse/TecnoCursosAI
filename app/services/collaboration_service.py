"""
Serviço de Colaboração em Tempo Real - TecnoCursos AI
Sistema completo para edição colaborativa de projetos de vídeo
"""

import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

try:
    from fastapi import WebSocket, WebSocketDisconnect
    from sqlalchemy.orm import Session
    from app.database import get_db_session
    from app.models import Project, User
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Tipos de ação colaborativa"""
    JOIN_PROJECT = "join_project"
    LEAVE_PROJECT = "leave_project"
    CURSOR_MOVE = "cursor_move"
    ELEMENT_SELECT = "element_select"
    ELEMENT_MOVE = "element_move"
    ELEMENT_RESIZE = "element_resize"
    ELEMENT_ADD = "element_add"
    ELEMENT_DELETE = "element_delete"
    ELEMENT_EDIT = "element_edit"
    SCENE_ADD = "scene_add"
    SCENE_DELETE = "scene_delete"
    SCENE_EDIT = "scene_edit"
    TIMELINE_UPDATE = "timeline_update"
    CHAT_MESSAGE = "chat_message"
    VOICE_START = "voice_start"
    VOICE_END = "voice_end"
    USER_TYPING = "user_typing"
    PROJECT_SAVE = "project_save"
    PERMISSION_CHANGE = "permission_change"

class Permission(Enum):
    """Níveis de permissão"""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    COMMENTER = "commenter"

@dataclass
class CollaborationUser:
    """Usuário em sessão colaborativa"""
    id: int
    name: str
    email: str
    avatar: Optional[str]
    permission: Permission
    cursor_position: Dict[str, float]
    selected_elements: List[str]
    is_active: bool
    last_seen: datetime
    connection_id: str

@dataclass
class CollaborationAction:
    """Ação colaborativa"""
    id: str
    action_type: ActionType
    user_id: int
    user_name: str
    project_id: int
    data: Dict[str, Any]
    timestamp: datetime
    target_element_id: Optional[str] = None

@dataclass
class CollaborationSession:
    """Sessão de colaboração"""
    project_id: int
    owner_id: int
    active_users: Dict[int, CollaborationUser]
    recent_actions: List[CollaborationAction]
    websocket_connections: Dict[str, WebSocket]
    created_at: datetime
    last_activity: datetime
    settings: Dict[str, Any]

class CollaborationService:
    """Serviço completo para colaboração em tempo real"""
    
    def __init__(self):
        self.data_dir = Path("data/collaboration")
        self.sessions_dir = self.data_dir / "sessions"
        self.chat_dir = self.data_dir / "chat"
        
        # Criar diretórios
        for directory in [self.data_dir, self.sessions_dir, self.chat_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Estado interno
        self.active_sessions: Dict[int, CollaborationSession] = {}
        self.user_to_project: Dict[int, int] = {}  # user_id -> project_id
        self.websocket_to_user: Dict[str, int] = {}  # connection_id -> user_id
        
        # Configurações
        self.max_users_per_project = 20
        self.action_history_limit = 1000
        self.inactive_timeout = timedelta(minutes=30)
        self.cursor_update_throttle = 0.1  # segundos
        
        # Rate limiting
        self.rate_limits = {
            ActionType.CURSOR_MOVE: 10,  # por segundo
            ActionType.CHAT_MESSAGE: 5,  # por segundo
            ActionType.ELEMENT_MOVE: 20,  # por segundo
        }
        
        logger.info("👥 Collaboration Service inicializado")
    
    async def start_service(self):
        """Iniciar serviço de colaboração"""
        # Iniciar workers
        asyncio.create_task(self._cleanup_worker())
        asyncio.create_task(self._heartbeat_worker())
        
        logger.info("🚀 Serviço de colaboração iniciado")
    
    async def join_project(self, project_id: int, user_id: int, user_name: str,
                          user_email: str, websocket: WebSocket, 
                          permission: Permission = Permission.VIEWER) -> bool:
        """Usuário se junta a um projeto"""
        try:
            # Verificar se o projeto existe
            if not await self._project_exists(project_id):
                await websocket.send_json({
                    "type": "error",
                    "message": "Projeto não encontrado"
                })
                return False
            
            # Verificar permissões
            if not await self._check_user_permission(user_id, project_id, permission):
                await websocket.send_json({
                    "type": "error", 
                    "message": "Sem permissão para acessar este projeto"
                })
                return False
            
            # Verificar limite de usuários
            if project_id in self.active_sessions:
                session = self.active_sessions[project_id]
                if len(session.active_users) >= self.max_users_per_project:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Projeto lotado. Tente novamente mais tarde."
                    })
                    return False
            
            # Aceitar conexão WebSocket
            await websocket.accept()
            connection_id = str(uuid.uuid4())
            
            # Criar ou obter sessão
            if project_id not in self.active_sessions:
                session = await self._create_session(project_id)
                self.active_sessions[project_id] = session
            else:
                session = self.active_sessions[project_id]
            
            # Criar usuário colaborativo
            collab_user = CollaborationUser(
                id=user_id,
                name=user_name,
                email=user_email,
                avatar=None,  # TODO: buscar avatar do usuário
                permission=permission,
                cursor_position={"x": 0, "y": 0},
                selected_elements=[],
                is_active=True,
                last_seen=datetime.now(),
                connection_id=connection_id
            )
            
            # Adicionar usuário à sessão
            session.active_users[user_id] = collab_user
            session.websocket_connections[connection_id] = websocket
            session.last_activity = datetime.now()
            
            # Mapear conexões
            self.user_to_project[user_id] = project_id
            self.websocket_to_user[connection_id] = user_id
            
            # Notificar outros usuários
            join_action = CollaborationAction(
                id=str(uuid.uuid4()),
                action_type=ActionType.JOIN_PROJECT,
                user_id=user_id,
                user_name=user_name,
                project_id=project_id,
                data={"permission": permission.value},
                timestamp=datetime.now()
            )
            
            await self._broadcast_action(session, join_action, exclude_user=user_id)
            
            # Enviar estado atual para o novo usuário
            await self._send_current_state(websocket, session)
            
            logger.info(f"👤 {user_name} entrou no projeto {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer join no projeto: {e}")
            return False
    
    async def leave_project(self, user_id: int, connection_id: str = None):
        """Usuário sai do projeto"""
        try:
            if user_id not in self.user_to_project:
                return
            
            project_id = self.user_to_project[user_id]
            
            if project_id not in self.active_sessions:
                return
            
            session = self.active_sessions[project_id]
            
            if user_id not in session.active_users:
                return
            
            user = session.active_users[user_id]
            
            # Remover usuário
            del session.active_users[user_id]
            del self.user_to_project[user_id]
            
            # Remover conexão WebSocket
            if connection_id and connection_id in session.websocket_connections:
                del session.websocket_connections[connection_id]
            if connection_id and connection_id in self.websocket_to_user:
                del self.websocket_to_user[connection_id]
            
            # Notificar outros usuários
            leave_action = CollaborationAction(
                id=str(uuid.uuid4()),
                action_type=ActionType.LEAVE_PROJECT,
                user_id=user_id,
                user_name=user.name,
                project_id=project_id,
                data={},
                timestamp=datetime.now()
            )
            
            await self._broadcast_action(session, leave_action)
            
            # Limpar sessão se vazia
            if not session.active_users:
                del self.active_sessions[project_id]
            
            logger.info(f"👤 {user.name} saiu do projeto {project_id}")
            
        except Exception as e:
            logger.error(f"Erro ao sair do projeto: {e}")
    
    async def handle_websocket_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Processar mensagem WebSocket"""
        try:
            # Identificar usuário
            connection_id = None
            user_id = None
            
            for conn_id, ws in self.websocket_to_user.items():
                if id(websocket) == id(self._get_websocket_by_connection(conn_id)):
                    connection_id = conn_id
                    user_id = ws
                    break
            
            if not user_id or user_id not in self.user_to_project:
                await websocket.send_json({
                    "type": "error",
                    "message": "Usuário não identificado"
                })
                return
            
            project_id = self.user_to_project[user_id]
            session = self.active_sessions.get(project_id)
            
            if not session:
                return
            
            user = session.active_users.get(user_id)
            if not user:
                return
            
            # Processar ação
            action_type = ActionType(message.get("type"))
            
            # Verificar permissões
            if not self._check_action_permission(user, action_type):
                await websocket.send_json({
                    "type": "error",
                    "message": "Sem permissão para esta ação"
                })
                return
            
            # Verificar rate limiting
            if not await self._check_rate_limit(user_id, action_type):
                await websocket.send_json({
                    "type": "error",
                    "message": "Muitas ações. Aguarde um momento."
                })
                return
            
            # Criar ação
            action = CollaborationAction(
                id=str(uuid.uuid4()),
                action_type=action_type,
                user_id=user_id,
                user_name=user.name,
                project_id=project_id,
                data=message.get("data", {}),
                timestamp=datetime.now(),
                target_element_id=message.get("target_element_id")
            )
            
            # Processar ação específica
            await self._process_action(session, action)
            
            # Broadcast para outros usuários
            await self._broadcast_action(session, action, exclude_user=user_id)
            
            # Atualizar atividade
            user.last_seen = datetime.now()
            session.last_activity = datetime.now()
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem WebSocket: {e}")
    
    async def _process_action(self, session: CollaborationSession, action: CollaborationAction):
        """Processar ação específica"""
        try:
            if action.action_type == ActionType.CURSOR_MOVE:
                # Atualizar posição do cursor
                user = session.active_users.get(action.user_id)
                if user:
                    user.cursor_position = action.data.get("position", {"x": 0, "y": 0})
            
            elif action.action_type == ActionType.ELEMENT_SELECT:
                # Atualizar elementos selecionados
                user = session.active_users.get(action.user_id)
                if user:
                    user.selected_elements = action.data.get("elements", [])
            
            elif action.action_type in [ActionType.ELEMENT_MOVE, ActionType.ELEMENT_RESIZE, 
                                      ActionType.ELEMENT_EDIT]:
                # Estas ações são apenas broadcastadas para sincronizar estado
                pass
            
            elif action.action_type == ActionType.CHAT_MESSAGE:
                # Salvar mensagem de chat
                await self._save_chat_message(session.project_id, action)
            
            elif action.action_type == ActionType.USER_TYPING:
                # Indicar que usuário está digitando (tempo limitado)
                # Não salvar, apenas broadcast
                pass
            
            # Adicionar à história de ações
            session.recent_actions.append(action)
            
            # Limitar histórico
            if len(session.recent_actions) > self.action_history_limit:
                session.recent_actions = session.recent_actions[-self.action_history_limit:]
            
        except Exception as e:
            logger.error(f"Erro ao processar ação: {e}")
    
    async def _broadcast_action(self, session: CollaborationSession, 
                              action: CollaborationAction, exclude_user: int = None):
        """Broadcast de ação para todos os usuários"""
        try:
            message = {
                "type": "collaboration_action",
                "action": {
                    "id": action.id,
                    "type": action.action_type.value,
                    "user_id": action.user_id,
                    "user_name": action.user_name,
                    "data": action.data,
                    "timestamp": action.timestamp.isoformat(),
                    "target_element_id": action.target_element_id
                }
            }
            
            # Enviar para todos os usuários conectados (exceto o originador)
            disconnected_connections = []
            
            for conn_id, websocket in session.websocket_connections.items():
                user_id = self.websocket_to_user.get(conn_id)
                
                if user_id == exclude_user:
                    continue
                
                try:
                    await websocket.send_json(message)
                except:
                    # Conexão perdida
                    disconnected_connections.append(conn_id)
            
            # Limpar conexões perdidas
            for conn_id in disconnected_connections:
                await self._cleanup_disconnected_connection(conn_id)
            
        except Exception as e:
            logger.error(f"Erro no broadcast: {e}")
    
    async def _send_current_state(self, websocket: WebSocket, session: CollaborationSession):
        """Enviar estado atual do projeto para novo usuário"""
        try:
            # Preparar estado atual
            current_state = {
                "type": "project_state",
                "data": {
                    "project_id": session.project_id,
                    "active_users": [
                        {
                            "id": user.id,
                            "name": user.name,
                            "avatar": user.avatar,
                            "permission": user.permission.value,
                            "cursor_position": user.cursor_position,
                            "selected_elements": user.selected_elements,
                            "is_active": user.is_active
                        }
                        for user in session.active_users.values()
                    ],
                    "recent_actions": [
                        {
                            "id": action.id,
                            "type": action.action_type.value,
                            "user_name": action.user_name,
                            "data": action.data,
                            "timestamp": action.timestamp.isoformat()
                        }
                        for action in session.recent_actions[-50:]  # Últimas 50 ações
                    ],
                    "settings": session.settings
                }
            }
            
            await websocket.send_json(current_state)
            
        except Exception as e:
            logger.error(f"Erro ao enviar estado atual: {e}")
    
    async def _create_session(self, project_id: int) -> CollaborationSession:
        """Criar nova sessão de colaboração"""
        try:
            # Buscar owner do projeto
            owner_id = await self._get_project_owner(project_id)
            
            session = CollaborationSession(
                project_id=project_id,
                owner_id=owner_id,
                active_users={},
                recent_actions=[],
                websocket_connections={},
                created_at=datetime.now(),
                last_activity=datetime.now(),
                settings={
                    "allow_anonymous": False,
                    "require_approval": False,
                    "max_users": self.max_users_per_project,
                    "chat_enabled": True,
                    "voice_enabled": False
                }
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão: {e}")
            raise
    
    async def _save_chat_message(self, project_id: int, action: CollaborationAction):
        """Salvar mensagem de chat"""
        try:
            chat_file = self.chat_dir / f"project_{project_id}_chat.jsonl"
            
            chat_message = {
                "id": action.id,
                "user_id": action.user_id,
                "user_name": action.user_name,
                "message": action.data.get("message", ""),
                "timestamp": action.timestamp.isoformat(),
                "type": action.data.get("type", "text")  # text, emoji, file
            }
            
            # Append to chat file
            with open(chat_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(chat_message) + "\n")
            
        except Exception as e:
            logger.error(f"Erro ao salvar chat: {e}")
    
    async def get_chat_history(self, project_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Obter histórico de chat"""
        try:
            chat_file = self.chat_dir / f"project_{project_id}_chat.jsonl"
            
            if not chat_file.exists():
                return []
            
            messages = []
            with open(chat_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                # Pegar últimas 'limit' mensagens
                for line in lines[-limit:]:
                    try:
                        message = json.loads(line.strip())
                        messages.append(message)
                    except:
                        continue
            
            return messages
            
        except Exception as e:
            logger.error(f"Erro ao obter chat: {e}")
            return []
    
    def get_active_users(self, project_id: int) -> List[Dict[str, Any]]:
        """Obter usuários ativos no projeto"""
        try:
            if project_id not in self.active_sessions:
                return []
            
            session = self.active_sessions[project_id]
            
            return [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "avatar": user.avatar,
                    "permission": user.permission.value,
                    "cursor_position": user.cursor_position,
                    "selected_elements": user.selected_elements,
                    "is_active": user.is_active,
                    "last_seen": user.last_seen.isoformat()
                }
                for user in session.active_users.values()
            ]
            
        except Exception as e:
            logger.error(f"Erro ao obter usuários ativos: {e}")
            return []
    
    async def _cleanup_worker(self):
        """Worker para limpeza de sessões inativas"""
        while True:
            try:
                current_time = datetime.now()
                inactive_projects = []
                
                for project_id, session in self.active_sessions.items():
                    # Verificar timeout de inatividade
                    if current_time - session.last_activity > self.inactive_timeout:
                        inactive_projects.append(project_id)
                        continue
                    
                    # Limpar usuários inativos
                    inactive_users = []
                    for user_id, user in session.active_users.items():
                        if current_time - user.last_seen > self.inactive_timeout:
                            inactive_users.append(user_id)
                    
                    for user_id in inactive_users:
                        await self.leave_project(user_id)
                
                # Limpar sessões inativas
                for project_id in inactive_projects:
                    if project_id in self.active_sessions:
                        del self.active_sessions[project_id]
                        logger.info(f"🧹 Sessão inativa removida: projeto {project_id}")
                
                await asyncio.sleep(300)  # Check a cada 5 minutos
                
            except Exception as e:
                logger.error(f"Erro no worker de limpeza: {e}")
                await asyncio.sleep(60)
    
    async def _heartbeat_worker(self):
        """Worker para heartbeat das conexões"""
        while True:
            try:
                for session in self.active_sessions.values():
                    disconnected_connections = []
                    
                    for conn_id, websocket in session.websocket_connections.items():
                        try:
                            # Enviar ping
                            await websocket.send_json({
                                "type": "ping",
                                "timestamp": datetime.now().isoformat()
                            })
                        except:
                            disconnected_connections.append(conn_id)
                    
                    # Limpar conexões perdidas
                    for conn_id in disconnected_connections:
                        await self._cleanup_disconnected_connection(conn_id)
                
                await asyncio.sleep(30)  # Heartbeat a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no heartbeat: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_disconnected_connection(self, connection_id: str):
        """Limpar conexão desconectada"""
        try:
            if connection_id in self.websocket_to_user:
                user_id = self.websocket_to_user[connection_id]
                await self.leave_project(user_id, connection_id)
            
        except Exception as e:
            logger.error(f"Erro ao limpar conexão: {e}")
    
    def _get_websocket_by_connection(self, connection_id: str) -> Optional[WebSocket]:
        """Obter WebSocket por connection_id"""
        for session in self.active_sessions.values():
            if connection_id in session.websocket_connections:
                return session.websocket_connections[connection_id]
        return None
    
    def _check_action_permission(self, user: CollaborationUser, action_type: ActionType) -> bool:
        """Verificar se usuário tem permissão para ação"""
        # Viewers só podem ver e mover cursor
        if user.permission == Permission.VIEWER:
            return action_type in [ActionType.CURSOR_MOVE, ActionType.ELEMENT_SELECT]
        
        # Commenters podem comentar
        elif user.permission == Permission.COMMENTER:
            return action_type in [
                ActionType.CURSOR_MOVE, ActionType.ELEMENT_SELECT, 
                ActionType.CHAT_MESSAGE, ActionType.USER_TYPING
            ]
        
        # Editors podem editar (mas não mudar permissões)
        elif user.permission == Permission.EDITOR:
            return action_type != ActionType.PERMISSION_CHANGE
        
        # Owners podem tudo
        elif user.permission == Permission.OWNER:
            return True
        
        return False
    
    async def _check_rate_limit(self, user_id: int, action_type: ActionType) -> bool:
        """Verificar rate limiting (implementação básica)"""
        # TODO: Implementar rate limiting real com Redis ou cache
        return True
    
    async def _project_exists(self, project_id: int) -> bool:
        """Verificar se projeto existe"""
        try:
            if not FASTAPI_AVAILABLE:
                return True  # Assumir que existe em modo de desenvolvimento
            
            db = get_db_session()
            project = db.query(Project).filter(Project.id == project_id).first()
            db.close()
            
            return project is not None
            
        except Exception as e:
            logger.error(f"Erro ao verificar projeto: {e}")
            return False
    
    async def _get_project_owner(self, project_id: int) -> int:
        """Obter owner do projeto"""
        try:
            if not FASTAPI_AVAILABLE:
                return 1  # Owner padrão em modo de desenvolvimento
            
            db = get_db_session()
            project = db.query(Project).filter(Project.id == project_id).first()
            db.close()
            
            return project.user_id if project else 1
            
        except Exception as e:
            logger.error(f"Erro ao obter owner: {e}")
            return 1
    
    async def _check_user_permission(self, user_id: int, project_id: int, 
                                   permission: Permission) -> bool:
        """Verificar permissão do usuário no projeto"""
        try:
            # TODO: Implementar sistema real de permissões
            # Por ora, permitir acesso
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissão: {e}")
            return False

# Instância global do serviço
collaboration_service = CollaborationService()

# Funções de conveniência
async def start_collaboration():
    """Iniciar serviço de colaboração"""
    await collaboration_service.start_service()

async def join_project_collaboration(project_id: int, user_id: int, user_name: str,
                                   user_email: str, websocket: WebSocket,
                                   permission: Permission = Permission.VIEWER):
    """Entrar em projeto colaborativo"""
    return await collaboration_service.join_project(
        project_id, user_id, user_name, user_email, websocket, permission
    )

async def handle_collaboration_message(websocket: WebSocket, message: Dict[str, Any]):
    """Processar mensagem de colaboração"""
    await collaboration_service.handle_websocket_message(websocket, message)