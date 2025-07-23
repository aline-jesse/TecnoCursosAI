import { useCallback, useRef } from 'react';

interface FocusState {
  isFocused: boolean;
  lastFocusTime: number;
  lastBlurTime: number;
  focusCount: number;
  blurCount: number;
  focusHistory: Array<{
    type: 'focus' | 'blur';
    timestamp: number;
    relatedTarget: EventTarget | null;
  }>;
}

interface FocusHandlers {
  onFocus?: (event: FocusEvent) => void;
  onBlur?: (event: FocusEvent) => void;
  onFocusChange?: (isFocused: boolean) => void;
  onFocusIn?: (event: FocusEvent) => void;
  onFocusOut?: (event: FocusEvent) => void;
}

interface FocusOptions {
  trackHistory?: boolean;
  historySize?: number;
  preventScroll?: boolean;
  focusOnMount?: boolean;
  restoreFocus?: boolean;
}

export const useCanvasFocus = (
  handlers: FocusHandlers = {},
  options: FocusOptions = {}
) => {
  const {
    trackHistory = false,
    historySize = 10,
    preventScroll = true,
    focusOnMount = false,
    restoreFocus = true,
  } = options;

  const focusState = useRef<FocusState>({
    isFocused: false,
    lastFocusTime: 0,
    lastBlurTime: 0,
    focusCount: 0,
    blurCount: 0,
    focusHistory: [],
  });

  const previousFocus = useRef<HTMLElement | null>(null);

  // Adicionar evento ao histórico
  const addToHistory = useCallback(
    (type: 'focus' | 'blur', relatedTarget: EventTarget | null) => {
      if (!trackHistory) return;

      focusState.current.focusHistory.push({
        type,
        timestamp: performance.now(),
        relatedTarget,
      });

      // Manter tamanho máximo do histórico
      if (focusState.current.focusHistory.length > historySize) {
        focusState.current.focusHistory.shift();
      }
    },
    [trackHistory, historySize]
  );

  // Handler para focus
  const handleFocus = useCallback(
    (event: FocusEvent) => {
      focusState.current.isFocused = true;
      focusState.current.lastFocusTime = performance.now();
      focusState.current.focusCount++;

      addToHistory('focus', event.relatedTarget);
      handlers.onFocus?.(event);
      handlers.onFocusChange?.(true);
    },
    [addToHistory, handlers]
  );

  // Handler para blur
  const handleBlur = useCallback(
    (event: FocusEvent) => {
      focusState.current.isFocused = false;
      focusState.current.lastBlurTime = performance.now();
      focusState.current.blurCount++;

      addToHistory('blur', event.relatedTarget);
      handlers.onBlur?.(event);
      handlers.onFocusChange?.(false);
    },
    [addToHistory, handlers]
  );

  // Handler para focusin
  const handleFocusIn = useCallback(
    (event: FocusEvent) => {
      if (preventScroll) {
        event.preventDefault();
      }

      // Armazenar elemento anteriormente focado
      if (event.relatedTarget instanceof HTMLElement) {
        previousFocus.current = event.relatedTarget;
      }

      handlers.onFocusIn?.(event);
    },
    [preventScroll, handlers]
  );

  // Handler para focusout
  const handleFocusOut = useCallback(
    (event: FocusEvent) => {
      handlers.onFocusOut?.(event);

      // Restaurar foco anterior se necessário
      if (restoreFocus && previousFocus.current) {
        previousFocus.current.focus({ preventScroll });
        previousFocus.current = null;
      }
    },
    [restoreFocus, preventScroll, handlers]
  );

  // Focar canvas
  const focus = useCallback(
    (element: HTMLElement) => {
      element.focus({ preventScroll });
    },
    [preventScroll]
  );

  // Remover foco do canvas
  const blur = useCallback((element: HTMLElement) => {
    element.blur();
  }, []);

  // Verificar se canvas está focado
  const isFocused = useCallback((): boolean => {
    return focusState.current.isFocused;
  }, []);

  // Obter tempo desde último foco/blur
  const getTimeSinceLastFocus = useCallback((): number => {
    return performance.now() - focusState.current.lastFocusTime;
  }, []);

  const getTimeSinceLastBlur = useCallback((): number => {
    return performance.now() - focusState.current.lastBlurTime;
  }, []);

  // Obter contagem de eventos
  const getFocusCount = useCallback((): number => {
    return focusState.current.focusCount;
  }, []);

  const getBlurCount = useCallback((): number => {
    return focusState.current.blurCount;
  }, []);

  // Obter histórico de foco
  const getFocusHistory = useCallback(() => {
    return [...focusState.current.focusHistory];
  }, []);

  // Limpar estado de foco
  const clearFocusState = useCallback(() => {
    focusState.current = {
      isFocused: false,
      lastFocusTime: 0,
      lastBlurTime: 0,
      focusCount: 0,
      blurCount: 0,
      focusHistory: [],
    };
    previousFocus.current = null;
  }, []);

  return {
    handleFocus,
    handleBlur,
    handleFocusIn,
    handleFocusOut,
    focus,
    blur,
    isFocused,
    getTimeSinceLastFocus,
    getTimeSinceLastBlur,
    getFocusCount,
    getBlurCount,
    getFocusHistory,
    clearFocusState,
  };
};
