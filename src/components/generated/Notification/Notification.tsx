// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

import React from 'react';
import './Notification.css';

import { useEffect } from 'react';
import {
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';

interface NotificationProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose: () => void;
  autoClose: boolean;
}

/**
 * Componente Notification
 * Gerado automaticamente pelo sistema de code generation
 */
const Notification: React.FC<NotificationProps> = ({
  message,
  type,
  onClose,
  autoClose,
}: NotificationProps) => {
  return (
    <div className='notification-container'>
      <h3>Notification</h3>
      {/* Conteúdo do componente */}
    </div>
  );
};

export default Notification;
