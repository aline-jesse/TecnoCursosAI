import { Toast } from '../components/Toast/ToastContainer';

export const useNotification = () => {
  const showToast = (toast: Omit<Toast, 'id'>) => {
    const event = new CustomEvent('toast', {
      detail: toast,
    });
    window.dispatchEvent(event);
  };

  const showSuccess = (message: string, duration?: number) => {
    showToast({
      type: 'success',
      message,
      duration,
    });
  };

  const showError = (message: string, duration?: number) => {
    showToast({
      type: 'error',
      message,
      duration,
    });
  };

  const showWarning = (message: string, duration?: number) => {
    showToast({
      type: 'warning',
      message,
      duration,
    });
  };

  const showInfo = (message: string, duration?: number) => {
    showToast({
      type: 'info',
      message,
      duration,
    });
  };

  return {
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
};
