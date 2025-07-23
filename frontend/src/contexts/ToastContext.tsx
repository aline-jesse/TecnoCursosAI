/**
 * ToastContext - Context API para Notificações Toast
 * TecnoCursos AI - Sistema de Notificações
 *
 * Oferece funcionalidades completas de toast:
 * - Diferentes tipos de notificação (success, error, warning, info)
 * - Controle de duração e posicionamento
 * - Stacking automático de múltiplas notificações
 * - Animações suaves de entrada e saída
 * - Integração com sistema de logging
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
} from 'react';

// Tipos de toast disponíveis
export type ToastType = 'success' | 'error' | 'warning' | 'info' | 'progress';

// Posições possíveis para os toasts
export type ToastPosition =
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-center'
  | 'bottom-right';

// Tipo para metadata do toast
export interface ToastMetadata {
  operationId?: string;
  operationName?: string;
  [key: string]: string | undefined;
}

// Interface para configuração de toast
export interface ToastConfig {
  id: string;
  type: ToastType;
  title: string;
  message: string;
  duration?: number; // Duração em ms (0 = infinito)
  persistent?: boolean; // Se deve permanecer até ser fechado manualmente
  showClose?: boolean; // Se deve mostrar botão de fechar
  showProgress?: boolean; // Se deve mostrar barra de progresso
  progress?: number; // Progresso atual (0-100)
  actionLabel?: string; // Label do botão de ação
  actionUrl?: string; // URL para navegação
  onAction?: () => void; // Callback para ação customizada
  onClose?: () => void; // Callback ao fechar
  metadata?: ToastMetadata; // Dados extras tipados
}

// Interface do contexto
interface ToastContextType {
  toasts: ToastConfig[];
  position: ToastPosition;
  showToast: (config: Omit<ToastConfig, 'id'>) => string;
  updateToast: (id: string, updates: Partial<ToastConfig>) => void;
  closeToast: (id: string) => void;
  clearAllToasts: () => void;
  setPosition: (position: ToastPosition) => void;

  // Métodos de conveniência
  success: (
    title: string,
    message?: string,
    options?: Partial<ToastConfig>
  ) => string;
  error: (
    title: string,
    message?: string,
    options?: Partial<ToastConfig>
  ) => string;
  warning: (
    title: string,
    message?: string,
    options?: Partial<ToastConfig>
  ) => string;
  info: (
    title: string,
    message?: string,
    options?: Partial<ToastConfig>
  ) => string;
  progress: (
    title: string,
    progress: number,
    message?: string,
    options?: Partial<ToastConfig>
  ) => string;
}

// Configurações padrão
const DEFAULT_DURATIONS = {
  success: 4000, // 4 segundos
  info: 5000, // 5 segundos
  warning: 6000, // 6 segundos
  error: 8000, // 8 segundos (ou infinito se crítico)
  progress: 0, // Infinito até atualizar/fechar
};

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast deve ser usado dentro de ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: React.ReactNode;
  defaultPosition?: ToastPosition;
  maxToasts?: number;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  defaultPosition = 'top-right',
  maxToasts = 5,
}) => {
  const [toasts, setToasts] = useState<ToastConfig[]>([]);
  const [position, setPosition] = useState<ToastPosition>(defaultPosition);
  const timeoutRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Gera ID único para toast
  const generateId = useCallback(() => {
    return `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // Programa fechamento automático do toast
  const scheduleAutoClose = useCallback((id: string, duration: number) => {
    if (duration > 0) {
      const timeout = setTimeout(() => {
        closeToast(id);
      }, duration);

      timeoutRefs.current.set(id, timeout);
    }
  }, []);

  // Cancela fechamento automático
  const cancelAutoClose = useCallback((id: string) => {
    const timeout = timeoutRefs.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      timeoutRefs.current.delete(id);
    }
  }, []);

  // Função principal para mostrar toast
  const showToast = useCallback(
    (config: Omit<ToastConfig, 'id'>) => {
      const id = generateId();

      const toastConfig: ToastConfig = {
        id,
        showClose: true,
        showProgress: false,
        duration: DEFAULT_DURATIONS[config.type],
        ...config,
      };

      setToasts(prev => {
        // Remove toasts excessivos se necessário
        let newToasts = prev;
        if (prev.length >= maxToasts) {
          newToasts = prev.slice(-(maxToasts - 1));
        }

        return [...newToasts, toastConfig];
      });

      // Programa fechamento automático se não for persistente
      if (!toastConfig.persistent && toastConfig.duration! > 0) {
        scheduleAutoClose(id, toastConfig.duration!);
      }

      // Log da criação do toast
      console.log(`Toast criado: ${toastConfig.type} - ${toastConfig.title}`, {
        id,
        type: toastConfig.type,
        title: toastConfig.title,
        duration: toastConfig.duration,
      });

      return id;
    },
    [generateId, maxToasts, scheduleAutoClose]
  );

  // Atualiza toast existente
  const updateToast = useCallback(
    (id: string, updates: Partial<ToastConfig>) => {
      setToasts(prev =>
        prev.map(toast => (toast.id === id ? { ...toast, ...updates } : toast))
      );

      // Se atualizou a duração, reagenda o fechamento
      if (updates.duration !== undefined) {
        cancelAutoClose(id);
        if (updates.duration > 0) {
          scheduleAutoClose(id, updates.duration);
        }
      }
    },
    [cancelAutoClose, scheduleAutoClose]
  );

  // Fecha toast específico
  const closeToast = useCallback(
    (id: string) => {
      setToasts(prev => {
        const toast = prev.find(t => t.id === id);
        if (toast?.onClose) {
          toast.onClose();
        }
        return prev.filter(t => t.id !== id);
      });

      // Cancela fechamento automático
      cancelAutoClose(id);

      console.log(`Toast fechado: ${id}`);
    },
    [cancelAutoClose]
  );

  // Limpa todos os toasts
  const clearAllToasts = useCallback(() => {
    // Cancela todos os timeouts
    timeoutRefs.current.forEach(timeout => clearTimeout(timeout));
    timeoutRefs.current.clear();

    // Executa callbacks onClose
    toasts.forEach(toast => {
      if (toast.onClose) {
        toast.onClose();
      }
    });

    setToasts([]);
    console.log('Todos os toasts foram limpos');
  }, [toasts]);

  // Métodos de conveniência
  const success = useCallback(
    (title: string, message = '', options: Partial<ToastConfig> = {}) => {
      return showToast({
        type: 'success',
        title,
        message,
        ...options,
      });
    },
    [showToast]
  );

  const error = useCallback(
    (title: string, message = '', options: Partial<ToastConfig> = {}) => {
      return showToast({
        type: 'error',
        title,
        message,
        persistent: options.persistent ?? true, // Erros são persistentes por padrão
        ...options,
      });
    },
    [showToast]
  );

  const warning = useCallback(
    (title: string, message = '', options: Partial<ToastConfig> = {}) => {
      return showToast({
        type: 'warning',
        title,
        message,
        ...options,
      });
    },
    [showToast]
  );

  const info = useCallback(
    (title: string, message = '', options: Partial<ToastConfig> = {}) => {
      return showToast({
        type: 'info',
        title,
        message,
        ...options,
      });
    },
    [showToast]
  );

  const progress = useCallback(
    (
      title: string,
      progressValue: number,
      message = '',
      options: Partial<ToastConfig> = {}
    ) => {
      return showToast({
        type: 'progress',
        title,
        message,
        progress: Math.max(0, Math.min(100, progressValue)),
        showProgress: true,
        persistent: true, // Progresso é sempre persistente
        ...options,
      });
    },
    [showToast]
  );

  const value: ToastContextType = {
    toasts,
    position,
    showToast,
    updateToast,
    closeToast,
    clearAllToasts,
    setPosition,
    success,
    error,
    warning,
    info,
    progress,
  };

  return (
    <ToastContext.Provider value={value}>{children}</ToastContext.Provider>
  );
};

// Hook para notificações relacionadas a operações específicas
export const useOperationToast = () => {
  const toast = useToast();

  const notifyOperationStart = useCallback(
    (operationName: string, operationId?: string) => {
      return toast.progress(
        `Iniciando ${operationName}...`,
        0,
        'Preparando operação',
        {
          metadata: { operationId, operationName },
        }
      );
    },
    [toast]
  );

  const notifyOperationProgress = useCallback(
    (toastId: string, progress: number, message?: string) => {
      toast.updateToast(toastId, {
        progress,
        message: message || `Progresso: ${progress}%`,
      });
    },
    [toast]
  );

  const notifyOperationSuccess = useCallback(
    (
      toastId: string,
      operationName: string,
      result?: { url?: string; label?: string }
    ) => {
      toast.updateToast(toastId, {
        type: 'success',
        title: `${operationName} Concluído! ✅`,
        message: 'Operação realizada com sucesso',
        showProgress: false,
        persistent: false,
        duration: 5000,
        actionUrl: result?.url,
        actionLabel: result?.label || 'Ver Resultado',
      });
    },
    [toast]
  );

  const notifyOperationError = useCallback(
    (toastId: string, operationName: string, error: string) => {
      toast.updateToast(toastId, {
        type: 'error',
        title: `Erro em ${operationName} ❌`,
        message: error,
        showProgress: false,
        persistent: true,
      });
    },
    [toast]
  );

  return {
    notifyOperationStart,
    notifyOperationProgress,
    notifyOperationSuccess,
    notifyOperationError,
  };
};

// Hook para notificações do sistema
export const useSystemToast = () => {
  const toast = useToast();

  const notifyVideoProcessingComplete = useCallback(
    (videoName: string, downloadUrl: string) => {
      return toast.success(
        'Vídeo Processado! 🎬',
        `O vídeo "${videoName}" está pronto para download`,
        {
          actionUrl: downloadUrl,
          actionLabel: 'Baixar Vídeo',
          duration: 10000,
        }
      );
    },
    [toast]
  );

  const notifyExportReady = useCallback(
    (exportType: string, downloadUrl: string) => {
      return toast.success(
        'Exportação Concluída! 📦',
        `Sua exportação (${exportType}) está pronta`,
        {
          actionUrl: downloadUrl,
          actionLabel: 'Baixar Arquivo',
          duration: 15000,
        }
      );
    },
    [toast]
  );

  const notifyAIGenerationComplete = useCallback(
    (generationType: string, resultUrl?: string) => {
      return toast.success(
        `${generationType} Gerado! ✨`,
        'Geração de IA concluída com sucesso',
        {
          actionUrl: resultUrl,
          actionLabel: 'Ver Resultado',
          duration: 8000,
        }
      );
    },
    [toast]
  );

  return {
    notifyVideoProcessingComplete,
    notifyExportReady,
    notifyAIGenerationComplete,
  };
};
