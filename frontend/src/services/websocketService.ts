/**
 * WebSocketService - Serviço de Comunicação em Tempo Real
 *
 * Este serviço gerencia a comunicação WebSocket para notificações
 * em tempo real, incluindo progresso de renderização e colaboração.
 */

// import { authService } from './authService'; // Removed - using local token management

// ============================================================================
// 🔌 SERVIÇO DE WEBSOCKET - TECNOCURSOS AI
// ============================================================================

// ============================================================================
// TIPOS
// ============================================================================

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  userId?: string;
}

interface WebSocketEventHandlers {
  [key: string]: (data: any) => void;
}

// ============================================================================
// SERVIÇO PRINCIPAL
// ============================================================================

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, Function[]> = new Map();

  connect(projectId: string): WebSocket {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return this.socket;
    }

    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/project/${projectId}`;
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log('WebSocket conectado');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = event => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Erro ao processar mensagem WebSocket:', error);
      }
    };

    this.socket.onclose = () => {
      console.log('WebSocket desconectado');
      this.handleReconnect();
    };

    this.socket.onerror = error => {
      console.error('Erro no WebSocket:', error);
    };

    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event: string, data: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ event, data }));
    }
  }

  private handleMessage(data: any): void {
    const { event, payload } = data;
    const callbacks = this.listeners.get(event);

    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(payload);
        } catch (error) {
          console.error(`Erro no callback do evento ${event}:`, error);
        }
      });
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `Tentativa de reconexão ${this.reconnectAttempts}/${this.maxReconnectAttempts}`
      );

      setTimeout(() => {
        // Tentar reconectar
        if (this.socket) {
          this.socket.close();
        }
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Máximo de tentativas de reconexão atingido');
    }
  }

  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
}

export const websocketService = new WebSocketService();

// ============================================================================
// HOOKS PARA REACT
// ============================================================================

export const useWebSocketService = () => {
  return websocketService;
};

// ============================================================================
// EXPORTAÇÕES
// ============================================================================

export default websocketService;
