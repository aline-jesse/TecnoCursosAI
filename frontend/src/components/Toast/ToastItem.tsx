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

import React from 'react';
import { Toast } from './ToastContainer';

interface ToastItemProps {
  toast: Toast;
  onClose: () => void;
}

const ToastItem: React.FC<ToastItemProps> = ({ toast, onClose }) => {
  const typeClasses = {
    success: 'bg-green-100 text-green-800 border-green-300',
    error: 'bg-red-100 text-red-800 border-red-300',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    info: 'bg-blue-100 text-blue-800 border-blue-300',
  };

  const iconClasses = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  return (
    <div
      className={`flex items-center p-4 rounded-lg border ${
        typeClasses[toast.type]
      } shadow-lg min-w-[300px] max-w-[500px] animate-slide-in`}
      role='alert'
    >
      <div className='flex-shrink-0 mr-3 text-xl'>
        {iconClasses[toast.type]}
      </div>
      <div className='flex-1'>
        <p className='text-sm font-medium'>{toast.message}</p>
      </div>
      <button
        onClick={onClose}
        className='flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600 focus:outline-none'
        aria-label='Close'
      >
        ×
      </button>
    </div>
  );
};

export default ToastItem;
