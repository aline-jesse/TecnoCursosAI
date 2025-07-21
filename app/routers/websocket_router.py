#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router WebSocket - TecnoCursos AI

Este módulo implementa endpoints WebSocket para comunicação em tempo real
entre o servidor e clientes, incluindo notificações, progresso e chat.

Funcionalidades:
- Conexões WebSocket autenticadas
- Salas de usuários por projeto
- Notificações em tempo real
- Atualizações de progresso
- Chat ao vivo
- Broadcasting de eventos

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from typing import Optional, Dict, Any
import json
import asyncio
from datetime import datetime

try:
    from app.services.websocket_service import (
        get_websocket_services,
        NotificationType
    )
    from app.auth import decode_jwt_token
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

# ============================================================================
# CONFIGURAÇÃO DO ROUTER
# ============================================================================

router = APIRouter(
    prefix="/ws",
    tags=["🌐 WebSocket Real-time"]
)

# ============================================================================
# ENDPOINTS WEBSOCKET
# ============================================================================

@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT token para autenticação"),
    room: Optional[str] = Query(None, description="Sala para entrar automaticamente")
):
    """
    Endpoint principal de conexão WebSocket.
    
    Estabelece conexão WebSocket com autenticação opcional
    e permite entrada automática em salas.
    
    Query Parameters:
        token: JWT token para autenticação (opcional)
        room: Nome da sala para entrar automaticamente (opcional)
    
    Eventos suportados:
        - connection: Confirmação de conexão
        - notification: Notificações do sistema
        - progress: Atualizações de progresso
        - chat: Mensagens de chat
        - system: Eventos do sistema
    """
    if not WEBSOCKET_AVAILABLE:
        await websocket.close(code=1013, reason="WebSocket services not available")
        return
    
    try:
        # Obter serviços WebSocket
        ws_services = get_websocket_services()
        connection_manager = ws_services['connection_manager']
        notification_service = ws_services['notification_service']
        
        # Extrair informações da conexão
        client_ip = websocket.client.host if websocket.client else "unknown"
        user_agent = websocket.headers.get("user-agent", "unknown")
        
        # Conectar cliente
        session_id = await connection_manager.connect(
            websocket=websocket,
            token=token,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Entrar em sala se especificada
        if room:
            await connection_manager.join_room(session_id, room)
        
        try:
            # Loop principal de comunicação
            while True:
                # Aguardar mensagens do cliente
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Processar mensagem do cliente
                    await handle_client_message(
                        session_id=session_id,
                        message=message,
                        connection_manager=connection_manager,
                        notification_service=notification_service
                    )
                    
                except json.JSONDecodeError:
                    # Mensagem inválida - enviar erro
                    error_response = {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(error_response))
                
        except WebSocketDisconnect:
            # Cliente desconectou
            pass
            
    except Exception as e:
        # Erro na conexão
        try:
            await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        except:
            pass
    
    finally:
        # Limpar conexão
        if WEBSOCKET_AVAILABLE and 'session_id' in locals():
            try:
                await connection_manager.disconnect(session_id)
            except:
                pass

@router.websocket("/room/{room_name}")
async def websocket_room_endpoint(
    websocket: WebSocket,
    room_name: str,
    token: Optional[str] = Query(None, description="JWT token para autenticação")
):
    """
    Conexão WebSocket direta para uma sala específica.
    
    Path Parameters:
        room_name: Nome da sala para conectar
    
    Query Parameters:
        token: JWT token para autenticação (opcional)
    """
    if not WEBSOCKET_AVAILABLE:
        await websocket.close(code=1013, reason="WebSocket services not available")
        return
    
    try:
        # Conectar e entrar na sala automaticamente
        ws_services = get_websocket_services()
        connection_manager = ws_services['connection_manager']
        
        client_ip = websocket.client.host if websocket.client else "unknown"
        user_agent = websocket.headers.get("user-agent", "unknown")
        
        session_id = await connection_manager.connect(
            websocket=websocket,
            token=token,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Entrar na sala especificada
        await connection_manager.join_room(session_id, room_name)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Adicionar sala à mensagem automaticamente
                message['room'] = room_name
                
                await handle_client_message(
                    session_id=session_id,
                    message=message,
                    connection_manager=connection_manager,
                    notification_service=ws_services['notification_service']
                )
                
        except WebSocketDisconnect:
            pass
            
    except Exception as e:
        try:
            await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        except:
            pass
    
    finally:
        if WEBSOCKET_AVAILABLE and 'session_id' in locals():
            try:
                await connection_manager.disconnect(session_id)
            except:
                pass

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

async def handle_client_message(
    session_id: str,
    message: Dict[str, Any],
    connection_manager,
    notification_service
):
    """Processar mensagem recebida do cliente."""
    try:
        message_type = message.get('type', 'unknown')
        
        if message_type == 'join_room':
            # Cliente quer entrar em uma sala
            room_name = message.get('room')
            if room_name:
                success = await connection_manager.join_room(session_id, room_name)
                
                response = {
                    "type": "room_joined" if success else "room_join_failed",
                    "room": room_name,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                }
                
                await connection_manager._send_to_connection(
                    session_id,
                    create_websocket_message(response)
                )
        
        elif message_type == 'leave_room':
            # Cliente quer sair de uma sala
            room_name = message.get('room')
            if room_name:
                success = await connection_manager.leave_room(session_id, room_name)
                
                response = {
                    "type": "room_left",
                    "room": room_name,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                }
                
                await connection_manager._send_to_connection(
                    session_id,
                    create_websocket_message(response)
                )
        
        elif message_type == 'chat':
            # Mensagem de chat para sala
            room_name = message.get('room')
            chat_message = message.get('message', '')
            
            if room_name and chat_message:
                # Obter info da conexão para user info
                connection_info = connection_manager.active_connections.get(session_id)
                username = connection_info.username if connection_info else "Usuário"
                
                # Enviar mensagem para toda a sala
                await notification_service.notify_room(
                    room=room_name,
                    title=f"💬 {username}",
                    message=chat_message,
                    type=NotificationType.CHAT,
                    data={
                        'user_id': connection_info.user_id if connection_info else None,
                        'username': username,
                        'session_id': session_id
                    }
                )
        
        elif message_type == 'ping':
            # Ping/pong para manter conexão viva
            response = {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }
            
            await connection_manager._send_to_connection(
                session_id,
                create_websocket_message(response)
            )
        
        elif message_type == 'get_room_list':
            # Cliente quer lista de salas disponíveis
            rooms = list(connection_manager.rooms.keys())
            
            response = {
                "type": "room_list",
                "rooms": [
                    {
                        "name": room,
                        "user_count": len(connection_manager.rooms[room])
                    }
                    for room in rooms
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            await connection_manager._send_to_connection(
                session_id,
                create_websocket_message(response)
            )
        
        else:
            # Tipo de mensagem não reconhecido
            response = {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.now().isoformat()
            }
            
            await connection_manager._send_to_connection(
                session_id,
                create_websocket_message(response)
            )
    
    except Exception as e:
        # Erro ao processar mensagem
        error_response = {
            "type": "error",
            "message": f"Error processing message: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await connection_manager._send_to_connection(
                session_id,
                create_websocket_message(error_response)
            )
        except:
            pass

def create_websocket_message(data: Dict[str, Any]):
    """Criar mensagem WebSocket padronizada."""
    from app.services.websocket_service import WebSocketMessage, NotificationType
    import uuid
    
    return WebSocketMessage(
        id=str(uuid.uuid4()),
        type=NotificationType.INFO,
        title=data.get('type', 'message'),
        message=json.dumps(data),
        data=data,
        timestamp=datetime.now()
    )

# ============================================================================
# ENDPOINTS REST PARA CONTROLE
# ============================================================================

@router.get("/stats")
async def get_websocket_stats():
    """
    Obter estatísticas das conexões WebSocket.
    
    Retorna informações sobre conexões ativas, salas,
    mensagens enviadas e performance.
    """
    if not WEBSOCKET_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="WebSocket services not available"
        )
    
    try:
        ws_services = get_websocket_services()
        connection_manager = ws_services['connection_manager']
        
        stats = connection_manager.get_connection_stats()
        
        return {
            "status": "active",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting WebSocket stats: {str(e)}"
        )

@router.get("/rooms")
async def get_active_rooms():
    """
    Listar salas ativas.
    
    Retorna lista de todas as salas com usuários conectados
    e contagem de participantes.
    """
    if not WEBSOCKET_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="WebSocket services not available"
        )
    
    try:
        ws_services = get_websocket_services()
        connection_manager = ws_services['connection_manager']
        
        rooms_info = []
        for room_name, sessions in connection_manager.rooms.items():
            # Obter informações dos usuários na sala
            users = []
            for session_id in sessions:
                connection_info = connection_manager.active_connections.get(session_id)
                if connection_info:
                    users.append({
                        "session_id": session_id[:8] + "...",
                        "username": connection_info.username,
                        "connected_at": connection_info.connected_at.isoformat(),
                        "user_id": connection_info.user_id
                    })
            
            rooms_info.append({
                "name": room_name,
                "user_count": len(sessions),
                "users": users
            })
        
        return {
            "rooms": rooms_info,
            "total_rooms": len(rooms_info),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting rooms: {str(e)}"
        )

@router.post("/broadcast")
async def broadcast_message(
    title: str,
    message: str,
    type: str = "info",
    data: Optional[Dict[str, Any]] = None
):
    """
    Enviar mensagem broadcast para todas as conexões.
    
    Body Parameters:
        title: Título da notificação
        message: Conteúdo da mensagem
        type: Tipo da notificação (info, success, warning, error)
        data: Dados adicionais (opcional)
    """
    if not WEBSOCKET_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="WebSocket services not available"
        )
    
    try:
        ws_services = get_websocket_services()
        notification_service = ws_services['notification_service']
        
        # Converter tipo para enum
        notification_type = NotificationType.INFO
        if type.lower() == "success":
            notification_type = NotificationType.SUCCESS
        elif type.lower() == "warning":
            notification_type = NotificationType.WARNING
        elif type.lower() == "error":
            notification_type = NotificationType.ERROR
        
        # Enviar broadcast
        await notification_service.broadcast_notification(
            title=title,
            message=message,
            type=notification_type,
            data=data or {},
            priority=2
        )
        
        return {
            "success": True,
            "message": "Broadcast sent successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending broadcast: {str(e)}"
        ) 

# Exportar router para uso na aplicação
websocket_router = router