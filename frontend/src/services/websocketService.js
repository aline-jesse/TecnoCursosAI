/**
 * Serviço WebSocket - TecnoCursos AI Editor
 * Comunicação em tempo real com backend FastAPI
 */

import React from 'react';
import { config, logger } from '../config/environment';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
    this.connectionPromise = null;
    this.isConnecting = false;
    this.heartbeatInterval = null;
    this.heartbeatTimeout = null;
    this.lastPong = Date.now();
  }

  /**
   * Conectar ao WebSocket do backend
   */
  async connect(token = null) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    if (this.isConnecting) {
      return this.connectionPromise;
    }

    this.isConnecting = true;

    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        // Obter token se não fornecido
        if (!token) {
          token = localStorage.getItem('tecnocursos_token');
        }

        if (!token) {
          throw new Error('Token de autenticação não encontrado');
        }

        // Construir URL do WebSocket com token
        const wsUrl = `${config.WS_URL}?token=${token}`;

        logger.debug('Conectando ao WebSocket:', wsUrl);

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          logger.info('WebSocket conectado com sucesso');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.emit('connected');
          resolve();
        };

        this.ws.onmessage = event => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            logger.error('Erro ao processar mensagem WebSocket:', error);
          }
        };

        this.ws.onclose = event => {
          logger.warn('WebSocket desconectado:', event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          this.emit('disconnected', { code: event.code, reason: event.reason });

          // Tentar reconectar se não foi fechamento intencional
          if (event.code !== 1000) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = error => {
          logger.error('Erro WebSocket:', error);
          this.isConnecting = false;
          this.emit('error', error);
          reject(error);
        };
      } catch (error) {
        this.isConnecting = false;
        logger.error('Erro ao conectar WebSocket:', error);
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  /**
   * Desconectar WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Desconexão solicitada pelo cliente');
      this.ws = null;
    }
    this.stopHeartbeat();
    this.reconnectAttempts = this.maxReconnectAttempts; // Evitar reconexão
    logger.info('WebSocket desconectado');
  }

  /**
   * Enviar mensagem
   */
  send(type, data = {}) {
    if (!this.isConnected()) {
      logger.warn('WebSocket não conectado. Tentando reconectar...');
      this.connect()
        .then(() => {
          this.send(type, data);
        })
        .catch(error => {
          logger.error('Falha ao reconectar para enviar mensagem:', error);
        });
      return;
    }

    const message = {
      type,
      data,
      timestamp: new Date().toISOString(),
    };

    try {
      this.ws.send(JSON.stringify(message));
      logger.debug('Mensagem WebSocket enviada:', message);
    } catch (error) {
      logger.error('Erro ao enviar mensagem WebSocket:', error);
    }
  }

  /**
   * Verificar se está conectado
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Adicionar listener para eventos
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Remover listener
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Emitir evento para listeners
   */
  emit(event, data = null) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          logger.error('Erro no callback do listener:', error);
        }
      });
    }
  }

  /**
   * Processar mensagens recebidas
   */
  handleMessage(message) {
    logger.debug('Mensagem WebSocket recebida:', message);

    const { type, data } = message;

    switch (type) {
      case 'pong':
        this.lastPong = Date.now();
        break;

      case 'upload_progress':
        this.emit('uploadProgress', data);
        break;

      case 'video_generation_progress':
        this.emit('videoProgress', data);
        break;

      case 'notification':
        this.emit('notification', data);
        break;

      case 'project_update':
        this.emit('projectUpdate', data);
        break;

      case 'collaboration_update':
        this.emit('collaborationUpdate', data);
        break;

      case 'system_status':
        this.emit('systemStatus', data);
        break;

      case 'error':
        this.emit('error', data);
        break;

      default:
        logger.warn('Tipo de mensagem WebSocket desconhecido:', type);
        this.emit('message', message);
    }
  }

  /**
   * Agendar reconexão
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      logger.error('Máximo de tentativas de reconexão atingido');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);

    logger.info(
      `Tentando reconectar em ${delay}ms... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`
    );

    setTimeout(() => {
      this.reconnectAttempts++;
      this.connect().catch(error => {
        logger.error('Falha na reconexão:', error);
      });
    }, delay);
  }

  /**
   * Iniciar heartbeat para manter conexão viva
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send('ping');

        // Verificar se recebeu pong
        this.heartbeatTimeout = setTimeout(() => {
          if (Date.now() - this.lastPong > 30000) {
            // 30 segundos
            logger.warn('Heartbeat timeout - reconectando...');
            this.ws.close();
          }
        }, 5000);
      }
    }, 25000); // Ping a cada 25 segundos
  }

  /**
   * Parar heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  /**
   * Métodos específicos para funcionalidades do editor
   */

  // Entrar em sala de projeto
  joinProject(projectId) {
    this.send('join_project', { project_id: projectId });
  }

  // Sair de sala de projeto
  leaveProject(projectId) {
    this.send('leave_project', { project_id: projectId });
  }

  // Sincronizar posição do cursor de colaboração
  updateCursor(projectId, position) {
    this.send('cursor_update', {
      project_id: projectId,
      position,
    });
  }

  // Sincronizar mudanças no canvas
  syncCanvasUpdate(projectId, operation) {
    this.send('canvas_update', {
      project_id: projectId,
      operation,
    });
  }

  // Solicitar status de geração de vídeo
  requestVideoStatus(taskId) {
    this.send('get_video_status', { task_id: taskId });
  }

  // Cancelar operação em andamento
  cancelOperation(operationId) {
    this.send('cancel_operation', { operation_id: operationId });
  }
}

// Instância singleton
const websocketService = new WebSocketService();

// Hooks personalizados para React
export const useWebSocket = () => {
  const [isConnected, setIsConnected] = React.useState(false);
  const [connectionStatus, setConnectionStatus] =
    React.useState('disconnected');

  React.useEffect(() => {
    const handleConnect = () => {
      setIsConnected(true);
      setConnectionStatus('connected');
    };

    const handleDisconnect = () => {
      setIsConnected(false);
      setConnectionStatus('disconnected');
    };

    const handleError = () => {
      setConnectionStatus('error');
    };

    websocketService.on('connected', handleConnect);
    websocketService.on('disconnected', handleDisconnect);
    websocketService.on('error', handleError);

    // Conectar automaticamente se autenticado
    if (localStorage.getItem('tecnocursos_token')) {
      websocketService.connect();
    }

    return () => {
      websocketService.off('connected', handleConnect);
      websocketService.off('disconnected', handleDisconnect);
      websocketService.off('error', handleError);
    };
  }, []);

  return {
    isConnected,
    connectionStatus,
    connect: websocketService.connect.bind(websocketService),
    disconnect: websocketService.disconnect.bind(websocketService),
    send: websocketService.send.bind(websocketService),
    on: websocketService.on.bind(websocketService),
    off: websocketService.off.bind(websocketService),
  };
};

// Hook para notificações em tempo real
export const useNotifications = () => {
  const [notifications, setNotifications] = React.useState([]);

  React.useEffect(() => {
    const handleNotification = notification => {
      setNotifications(prev => [
        ...prev,
        {
          ...notification,
          id: Date.now(),
          timestamp: new Date(),
        },
      ]);
    };

    websocketService.on('notification', handleNotification);

    return () => {
      websocketService.off('notification', handleNotification);
    };
  }, []);

  const removeNotification = id => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  return {
    notifications,
    removeNotification,
    clearNotifications,
  };
};

// Hook para progress tracking
export const useProgressTracking = () => {
  const [uploadProgress, setUploadProgress] = React.useState({});
  const [videoProgress, setVideoProgress] = React.useState({});

  React.useEffect(() => {
    const handleUploadProgress = data => {
      setUploadProgress(prev => ({
        ...prev,
        [data.upload_id]: data,
      }));
    };

    const handleVideoProgress = data => {
      setVideoProgress(prev => ({
        ...prev,
        [data.task_id]: data,
      }));
    };

    websocketService.on('uploadProgress', handleUploadProgress);
    websocketService.on('videoProgress', handleVideoProgress);

    return () => {
      websocketService.off('uploadProgress', handleUploadProgress);
      websocketService.off('videoProgress', handleVideoProgress);
    };
  }, []);

  return {
    uploadProgress,
    videoProgress,
  };
};

export default websocketService;
