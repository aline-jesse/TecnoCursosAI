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

import React from 'react';
import { createPortal } from 'react-dom';
import { ToastConfig, ToastPosition, useToast } from '../../contexts/ToastContext';
import ToastItem from './ToastItem';
import './ToastContainer.css';

interface ToastContainerProps {
  position?: ToastPosition;
}

const ToastContainer: React.FC<ToastContainerProps> = ({ 
  position: propPosition 
}) => {
  const { toasts, position: contextPosition } = useToast();
  const finalPosition = propPosition || contextPosition;

  // Não renderiza se não há toasts
  if (toasts.length === 0) {
    return null;
  }

  // Calcula classes CSS baseadas na posição
  const getPositionClasses = (position: ToastPosition): string => {
    const baseClasses = 'toast-container';
    
    const positionMap: Record<ToastPosition, string> = {
      'top-left': `${baseClasses} toast-container--top-left`,
      'top-center': `${baseClasses} toast-container--top-center`,
      'top-right': `${baseClasses} toast-container--top-right`,
      'bottom-left': `${baseClasses} toast-container--bottom-left`,
      'bottom-center': `${baseClasses} toast-container--bottom-center`,
      'bottom-right': `${baseClasses} toast-container--bottom-right`
    };
    
    return positionMap[position];
  };

  // Ordena toasts baseado na posição
  const getSortedToasts = (toasts: ToastConfig[], position: ToastPosition): ToastConfig[] => {
    // Para posições 'top-*', mostra mais recentes primeiro (no topo)
    // Para posições 'bottom-*', mostra mais recentes por último (embaixo)
    if (position.startsWith('top-')) {
      return [...toasts].reverse(); // Mais recentes primeiro
    }
    return toasts; // Ordem original (mais antigos primeiro)
  };

  const sortedToasts = getSortedToasts(toasts, finalPosition);
  const containerClasses = getPositionClasses(finalPosition);

  // Renderiza usando portal para evitar problemas de z-index
  return createPortal(
    <div className={containerClasses}>
      <div className="toast-list">
        {sortedToasts.map((toast, index) => (
          <ToastItem
            key={toast.id}
            toast={toast}
            index={index}
            position={finalPosition}
          />
        ))}
      </div>
    </div>,
    document.body
  );
};

export default ToastContainer; 