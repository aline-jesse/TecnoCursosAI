/**
 * ToastItem - Componente Individual de Toast
 * TecnoCursos AI - Sistema de Notificações
 * 
 * Funcionalidades:
 * - Diferentes estilos visuais por tipo (success, error, warning, info, progress)
 * - Animações suaves de entrada e saída
 * - Barra de progresso para operações longas
 * - Botões de ação e fechamento
 * - Hover para pausar auto-close
 * - Responsividade para mobile
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ToastConfig, ToastPosition, useToast } from '../../contexts/ToastContext';

interface ToastItemProps {
  toast: ToastConfig;
  index: number;
  position: ToastPosition;
}

const ToastItem: React.FC<ToastItemProps> = ({ 
  toast, 
  index, 
  position 
}) => {
  const { closeToast } = useToast();
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // Animação de entrada
  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  // Ícones para cada tipo de toast
  const getIcon = (type: ToastConfig['type']): string => {
    const iconMap = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️',
      progress: '⏳'
    };
    return iconMap[type];
  };

  // Classes CSS baseadas no tipo
  const getTypeClasses = (type: ToastConfig['type']): string => {
    const baseClasses = 'toast-item';
    const typeMap = {
      success: `${baseClasses} toast-item--success`,
      error: `${baseClasses} toast-item--error`,
      warning: `${baseClasses} toast-item--warning`,
      info: `${baseClasses} toast-item--info`,
      progress: `${baseClasses} toast-item--progress`
    };
    return typeMap[type];
  };

  // Handler para fechar toast
  const handleClose = useCallback(() => {
    setIsVisible(false);
    // Aguarda animação antes de remover completamente
    setTimeout(() => closeToast(toast.id), 300);
  }, [closeToast, toast.id]);

  // Handler para ação do toast
  const handleAction = useCallback(() => {
    if (toast.onAction) {
      toast.onAction();
    } else if (toast.actionUrl) {
      window.open(toast.actionUrl, '_blank');
    }
  }, [toast.onAction, toast.actionUrl]);

  // Calcula delay de animação baseado no índice
  const animationDelay = index * 100; // 100ms entre cada toast

  const toastClasses = `
    ${getTypeClasses(toast.type)}
    ${isVisible ? 'toast-item--visible' : 'toast-item--hidden'}
    ${isHovered ? 'toast-item--hovered' : ''}
  `.trim();

  return (
    <div
      className={toastClasses}
      style={{
        '--animation-delay': `${animationDelay}ms`,
        '--stack-index': index
      } as React.CSSProperties}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      role="alert"
      aria-live="polite"
    >
      {/* Conteúdo principal */}
      <div className="toast-content">
        {/* Ícone */}
        <div className="toast-icon">
          {getIcon(toast.type)}
        </div>

        {/* Texto */}
        <div className="toast-text">
          <div className="toast-title">
            {toast.title}
          </div>
          {toast.message && (
            <div className="toast-message">
              {toast.message}
            </div>
          )}
        </div>

        {/* Botão de fechar */}
        {toast.showClose && (
          <button
            className="toast-close"
            onClick={handleClose}
            aria-label="Fechar notificação"
          >
            ✕
          </button>
        )}
      </div>

      {/* Barra de progresso */}
      {toast.showProgress && toast.progress !== undefined && (
        <div className="toast-progress-container">
          <div 
            className="toast-progress-bar"
            style={{ width: `${toast.progress}%` }}
          />
          <div className="toast-progress-text">
            {toast.progress}%
          </div>
        </div>
      )}

      {/* Botão de ação */}
      {(toast.actionLabel || toast.actionUrl) && (
        <div className="toast-actions">
          <button
            className="toast-action-button"
            onClick={handleAction}
          >
            {toast.actionLabel || 'Ver Mais'}
          </button>
        </div>
      )}

      {/* Barra de tempo (para toasts com duração) */}
      {!toast.persistent && toast.duration && toast.duration > 0 && (
        <div className="toast-timer">
          <div 
            className="toast-timer-bar"
            style={{
              '--duration': `${toast.duration}ms`,
              animationPlayState: isHovered ? 'paused' : 'running'
            } as React.CSSProperties}
          />
        </div>
      )}
    </div>
  );
};

export default ToastItem; 