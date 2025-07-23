/**
 * ToastContainer - Container Principal dos Toasts
 * TecnoCursos AI - Sistema de Notificações
 *
 * Componente responsável por:
 * - Renderizar e posicionar todos os toasts ativos
 * - Gerenciar animações de entrada e saída
 * - Implementar stacking e ordenação
 * - Responsividade para diferentes dispositivos
 */

import React, { useEffect, useState } from 'react';
import ToastItem from './ToastItem';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

interface ToastContainerProps {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

const ToastContainer: React.FC<ToastContainerProps> = ({
  position = 'top-right',
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handleToast = (event: CustomEvent<Toast>) => {
      const newToast = {
        ...event.detail,
        id: `toast-${Date.now()}`,
        duration: event.detail.duration || 5000,
      };
      setToasts(prev => [...prev, newToast]);

      setTimeout(() => {
        removeToast(newToast.id);
      }, newToast.duration);
    };

    window.addEventListener('toast' as any, handleToast as any);
    return () => window.removeEventListener('toast' as any, handleToast as any);
  }, []);

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
  };

  return (
    <div
      className={`fixed z-50 flex flex-col gap-2 ${positionClasses[position]}`}
    >
      {toasts.map(toast => (
        <ToastItem
          key={toast.id}
          toast={toast}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
};

export default ToastContainer;
