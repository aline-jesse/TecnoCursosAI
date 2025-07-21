/**
 * Hook de Notificações
 *
 * Gerencia notificações toast/snackbar para feedback ao usuário
 * Pode ser integrado com bibliotecas como react-toastify, notistack, etc.
 */

import { useCallback } from 'react';
import { toast } from 'react-toastify'; // Ou outra biblioteca de sua preferência

export const useNotification = () => {
  /**
   * Mostrar notificação de sucesso
   */
  const showSuccess = useCallback((message, options = {}) => {
    toast.success(message, {
      position: 'top-right',
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  }, []);

  /**
   * Mostrar notificação de erro
   */
  const showError = useCallback((message, options = {}) => {
    toast.error(message, {
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  }, []);

  /**
   * Mostrar notificação de aviso
   */
  const showWarning = useCallback((message, options = {}) => {
    toast.warning(message, {
      position: 'top-right',
      autoClose: 4000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  }, []);

  /**
   * Mostrar notificação informativa
   */
  const showInfo = useCallback((message, options = {}) => {
    toast.info(message, {
      position: 'top-right',
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  }, []);

  /**
   * Mostrar notificação com loading
   */
  const showLoading = useCallback((message = 'Carregando...') => {
    return toast.loading(message, {
      position: 'top-center',
    });
  }, []);

  /**
   * Atualizar notificação existente
   */
  const updateNotification = useCallback((toastId, options) => {
    toast.update(toastId, {
      ...options,
      autoClose: 3000,
      isLoading: false,
    });
  }, []);

  /**
   * Fechar notificação específica
   */
  const dismissNotification = useCallback(toastId => {
    if (toastId) {
      toast.dismiss(toastId);
    }
  }, []);

  /**
   * Fechar todas as notificações
   */
  const dismissAll = useCallback(() => {
    toast.dismiss();
  }, []);

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showLoading,
    updateNotification,
    dismissNotification,
    dismissAll,
  };
};
