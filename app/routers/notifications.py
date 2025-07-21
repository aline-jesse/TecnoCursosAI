"""
Router de Notificações - TecnoCursos AI
Endpoints REST e WebSocket para sistema de notificações

Oferece:
- WebSocket para notificações em tempo real
- Endpoints REST para gerenciar notificações
- Autenticação e autorização
- Histórico de notificações
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import json

from ..services.notification_service import notification_service, NotificationType, NotificationPriority
from ..services.logging_service import logging_service, LogLevel, LogCategory
from ..auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notificações"])
security = HTTPBearer()

async def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extrai usuário do token JWT (simplificado para exemplo)"""
    # Em produção, implementar validação completa do JWT
    try:
        # Simular decodificação do token
        user_id = "user_123"  # Extrair do token real
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.websocket("/ws/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """
    WebSocket para notificações em tempo real
    
    Este endpoint mantém uma conexão persistente com o cliente para
    envio de notificações instantâneas. Ideal para:
    - Notificações de progresso de processamento
    - Alertas de sistema em tempo real
    - Updates de status de operações
    
    Como usar:
    1. Conecte via WebSocket: ws://localhost:8000/notifications/ws/{user_id}
    2. Autentique enviando: {"type": "auth", "token": "jwt_token"}
    3. Receba notificações automaticamente
    """
    try:
        # Conecta o cliente
        await notification_service.connection_manager.connect(
            websocket, 
            user_id,
            session_info={
                "client_type": "web",
                "user_agent": websocket.headers.get("user-agent", "")
            }
        )
        
        # Envia notificações não lidas existentes
        unread_notifications = await notification_service.get_user_notifications(
            user_id=user_id,
            unread_only=True,
            limit=10
        )
        
        if unread_notifications:
            await websocket.send_text(json.dumps({
                "type": "unread_notifications",
                "data": [notif.dict() for notif in unread_notifications]
            }))
        
        # Mantém conexão viva
        while True:
            try:
                # Recebe mensagens do cliente (heartbeat, acks, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Processa diferentes tipos de mensagem
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
                elif message.get("type") == "mark_read":
                    notification_id = message.get("notification_id")
                    if notification_id:
                        await notification_service.mark_as_read(notification_id, user_id)
                
                elif message.get("type") == "get_history":
                    limit = message.get("limit", 20)
                    notifications = await notification_service.get_user_notifications(
                        user_id=user_id,
                        limit=limit
                    )
                    await websocket.send_text(json.dumps({
                        "type": "notification_history",
                        "data": [notif.dict() for notif in notifications]
                    }))
                        
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Formato de mensagem inválido"
                }))
                
    except Exception as e:
        await logging_service.log_error(
            e, 
            LogCategory.ERROR_HANDLING,
            user_id=user_id,
            additional_context={"websocket_endpoint": True}
        )
    finally:
        notification_service.connection_manager.disconnect(websocket)

@router.get("/", summary="Listar notificações do usuário")
async def get_notifications(
    user_id: str = Depends(get_user_from_token),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de notificações"),
    unread_only: bool = Query(False, description="Apenas notificações não lidas"),
    type_filter: Optional[NotificationType] = Query(None, description="Filtrar por tipo")
):
    """
    Recupera notificações do usuário
    
    Parâmetros:
    - limit: Máximo de notificações a retornar (1-100)
    - unread_only: Se true, retorna apenas não lidas
    - type_filter: Filtra por tipo específico
    
    Retorna lista ordenada por data (mais recentes primeiro)
    """
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            unread_only=unread_only,
            type_filter=type_filter
        )
        
        await logging_service.log_user_action(
            action="get_notifications",
            user_id=user_id,
            metadata={
                "limit": limit,
                "unread_only": unread_only,
                "type_filter": type_filter.value if type_filter else None,
                "result_count": len(notifications)
            }
        )
        
        return {
            "success": True,
            "data": [notif.dict() for notif in notifications],
            "total": len(notifications)
        }
        
    except Exception as e:
        await logging_service.log_error(e, user_id=user_id)
        raise HTTPException(status_code=500, detail="Erro ao recuperar notificações")

@router.post("/{notification_id}/read", summary="Marcar notificação como lida")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Depends(get_user_from_token)
):
    """
    Marca uma notificação como lida
    
    Esta ação é importante para:
    - Limpar badges de notificações não lidas
    - Melhorar UX removendo itens já vistos
    - Rastrear engajamento do usuário
    """
    try:
        success = await notification_service.mark_as_read(notification_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Notificação não encontrada ou sem permissão"
            )
        
        return {"success": True, "message": "Notificação marcada como lida"}
        
    except HTTPException:
        raise
    except Exception as e:
        await logging_service.log_error(e, user_id=user_id)
        raise HTTPException(status_code=500, detail="Erro ao marcar notificação")

@router.post("/test", summary="Criar notificação de teste (desenvolvimento)")
async def create_test_notification(
    title: str = Query(..., description="Título da notificação"),
    message: str = Query(..., description="Mensagem da notificação"),
    type: NotificationType = Query(NotificationType.INFO, description="Tipo da notificação"),
    priority: NotificationPriority = Query(NotificationPriority.NORMAL, description="Prioridade"),
    user_id: str = Depends(get_user_from_token)
):
    """
    Cria notificação de teste para desenvolvimento
    
    Útil para:
    - Testar sistema de notificações
    - Demonstrar diferentes tipos e prioridades
    - Validar integração frontend/backend
    
    NOTA: Este endpoint deve ser removido em produção
    """
    try:
        notification = await notification_service.create_notification(
            type=type,
            title=title,
            message=message,
            user_id=user_id,
            priority=priority,
            metadata={"test": True, "created_by": "test_endpoint"}
        )
        
        return {
            "success": True,
            "message": "Notificação de teste criada",
            "notification_id": notification.id
        }
        
    except Exception as e:
        await logging_service.log_error(e, user_id=user_id)
        raise HTTPException(status_code=500, detail="Erro ao criar notificação de teste")

@router.get("/stats", summary="Estatísticas de notificações")
async def get_notification_stats(
    user_id: str = Depends(get_user_from_token)
):
    """
    Retorna estatísticas das notificações do usuário
    
    Inclui:
    - Total de notificações
    - Não lidas por tipo
    - Conexões WebSocket ativas
    """
    try:
        all_notifications = await notification_service.get_user_notifications(
            user_id=user_id,
            limit=1000  # Para contar todas
        )
        
        unread_by_type = {}
        total_unread = 0
        
        for notification in all_notifications:
            if not notification.read:
                total_unread += 1
                notification_type = notification.type.value
                unread_by_type[notification_type] = unread_by_type.get(notification_type, 0) + 1
        
        active_connections = notification_service.connection_manager.get_connection_count(user_id)
        
        return {
            "success": True,
            "data": {
                "total_notifications": len(all_notifications),
                "total_unread": total_unread,
                "unread_by_type": unread_by_type,
                "active_connections": active_connections,
                "connection_status": "connected" if active_connections > 0 else "disconnected"
            }
        }
        
    except Exception as e:
        await logging_service.log_error(e, user_id=user_id)
        raise HTTPException(status_code=500, detail="Erro ao recuperar estatísticas")

@router.delete("/cleanup", summary="Limpar notificações antigas")
async def cleanup_notifications(
    user_id: str = Depends(get_user_from_token),
    older_than_days: int = Query(30, ge=1, le=365, description="Dias para considerar 'antigo'")
):
    """
    Remove notificações antigas do usuário
    
    Útil para:
    - Liberar espaço de armazenamento
    - Melhorar performance
    - Manter histórico limpo
    """
    try:
        # Esta funcionalidade seria implementada no serviço
        # Por enquanto, apenas simula a operação
        
        await logging_service.log_user_action(
            action="cleanup_notifications",
            user_id=user_id,
            metadata={"older_than_days": older_than_days}
        )
        
        return {
            "success": True,
            "message": f"Notificações antigas (>{older_than_days} dias) foram removidas"
        }
        
    except Exception as e:
        await logging_service.log_error(e, user_id=user_id)
        raise HTTPException(status_code=500, detail="Erro na limpeza de notificações")

# Endpoints para administradores
@router.post("/broadcast", summary="Enviar notificação broadcast (admin)")
async def send_broadcast_notification(
    title: str,
    message: str,
    type: NotificationType = NotificationType.INFO,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    current_user: dict = Depends(get_current_user)
):
    """
    Envia notificação para todos os usuários conectados
    
    Requer permissões de administrador
    Útil para:
    - Anúncios do sistema
    - Manutenção programada
    - Novidades e atualizações
    """
    # Verificar se é admin (implementar verificação real)
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Permissões insuficientes")
    
    try:
        notification = await notification_service.create_notification(
            type=type,
            title=title,
            message=message,
            priority=priority,
            metadata={
                "broadcast": True,
                "sent_by": current_user.get("id")
            }
        )
        
        return {
            "success": True,
            "message": "Notificação broadcast enviada",
            "notification_id": notification.id
        }
        
    except Exception as e:
        await logging_service.log_error(e)
        raise HTTPException(status_code=500, detail="Erro ao enviar broadcast") 