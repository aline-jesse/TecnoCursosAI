import { useCallback, useRef } from 'react';

interface KeyState {
  isPressed: boolean;
  timestamp: number;
}

interface KeyboardState {
  keys: { [key: string]: KeyState };
  modifiers: {
    ctrl: boolean;
    shift: boolean;
    alt: boolean;
    meta: boolean;
  };
  lastKey: string | null;
  isComposing: boolean;
}

interface KeyboardHandlers {
  onKeyDown?: (key: string, event: KeyboardEvent) => void;
  onKeyUp?: (key: string, event: KeyboardEvent) => void;
  onKeyPress?: (key: string, event: KeyboardEvent) => void;
  onShortcut?: (keys: string[], event: KeyboardEvent) => void;
  onCompositionStart?: (event: CompositionEvent) => void;
  onCompositionEnd?: (event: CompositionEvent) => void;
}

interface ShortcutConfig {
  keys: string[];
  callback: (event: KeyboardEvent) => void;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  requireFocus?: boolean;
}

export const useCanvasKeyboard = (
  handlers: KeyboardHandlers = {},
  shortcuts: ShortcutConfig[] = []
) => {
  const keyboardState = useRef<KeyboardState>({
    keys: {},
    modifiers: {
      ctrl: false,
      shift: false,
      alt: false,
      meta: false,
    },
    lastKey: null,
    isComposing: false,
  });

  // Atualizar estado dos modificadores
  const updateModifiers = useCallback((event: KeyboardEvent) => {
    keyboardState.current.modifiers = {
      ctrl: event.ctrlKey,
      shift: event.shiftKey,
      alt: event.altKey,
      meta: event.metaKey,
    };
  }, []);

  // Verificar se tecla está pressionada
  const isKeyPressed = useCallback((key: string): boolean => {
    return !!keyboardState.current.keys[key]?.isPressed;
  }, []);

  // Verificar se modificador está ativo
  const isModifierActive = useCallback(
    (modifier: keyof KeyboardState['modifiers']): boolean => {
      return keyboardState.current.modifiers[modifier];
    },
    []
  );

  // Verificar se combinação de teclas está ativa
  const areKeysPressed = useCallback(
    (keys: string[]): boolean => {
      return keys.every(key => isKeyPressed(key));
    },
    [isKeyPressed]
  );

  // Verificar se atalho está ativo
  const isShortcutActive = useCallback(
    (shortcut: ShortcutConfig): boolean => {
      const { keys, requireFocus = true } = shortcut;

      if (requireFocus && document.activeElement !== document.body) {
        return false;
      }

      return areKeysPressed(keys);
    },
    [areKeysPressed]
  );

  // Handler para keydown
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const { key, repeat } = event;

      // Ignorar eventos durante composição de IME
      if (keyboardState.current.isComposing) return;

      // Atualizar estado da tecla
      if (!repeat) {
        keyboardState.current.keys[key] = {
          isPressed: true,
          timestamp: performance.now(),
        };
        keyboardState.current.lastKey = key;
      }

      // Atualizar modificadores
      updateModifiers(event);

      // Verificar atalhos
      for (const shortcut of shortcuts) {
        if (isShortcutActive(shortcut)) {
          if (shortcut.preventDefault) {
            event.preventDefault();
          }
          if (shortcut.stopPropagation) {
            event.stopPropagation();
          }
          shortcut.callback(event);
          handlers.onShortcut?.(shortcut.keys, event);
          break;
        }
      }

      handlers.onKeyDown?.(key, event);
    },
    [updateModifiers, isShortcutActive, shortcuts, handlers]
  );

  // Handler para keyup
  const handleKeyUp = useCallback(
    (event: KeyboardEvent) => {
      const { key } = event;

      // Ignorar eventos durante composição de IME
      if (keyboardState.current.isComposing) return;

      // Atualizar estado da tecla
      delete keyboardState.current.keys[key];
      if (keyboardState.current.lastKey === key) {
        keyboardState.current.lastKey = null;
      }

      // Atualizar modificadores
      updateModifiers(event);

      handlers.onKeyUp?.(key, event);
    },
    [updateModifiers, handlers]
  );

  // Handler para keypress
  const handleKeyPress = useCallback(
    (event: KeyboardEvent) => {
      const { key } = event;

      // Ignorar eventos durante composição de IME
      if (keyboardState.current.isComposing) return;

      handlers.onKeyPress?.(key, event);
    },
    [handlers]
  );

  // Handler para compositionstart
  const handleCompositionStart = useCallback(
    (event: CompositionEvent) => {
      keyboardState.current.isComposing = true;
      handlers.onCompositionStart?.(event);
    },
    [handlers]
  );

  // Handler para compositionend
  const handleCompositionEnd = useCallback(
    (event: CompositionEvent) => {
      keyboardState.current.isComposing = false;
      handlers.onCompositionEnd?.(event);
    },
    [handlers]
  );

  // Obter última tecla pressionada
  const getLastKey = useCallback((): string | null => {
    return keyboardState.current.lastKey;
  }, []);

  // Obter estado dos modificadores
  const getModifiers = useCallback(() => {
    return { ...keyboardState.current.modifiers };
  }, []);

  // Obter estado de todas as teclas
  const getAllKeys = useCallback(() => {
    return { ...keyboardState.current.keys };
  }, []);

  // Limpar estado do teclado
  const clearKeyboardState = useCallback(() => {
    keyboardState.current = {
      keys: {},
      modifiers: {
        ctrl: false,
        shift: false,
        alt: false,
        meta: false,
      },
      lastKey: null,
      isComposing: false,
    };
  }, []);

  return {
    handleKeyDown,
    handleKeyUp,
    handleKeyPress,
    handleCompositionStart,
    handleCompositionEnd,
    isKeyPressed,
    isModifierActive,
    areKeysPressed,
    isShortcutActive,
    getLastKey,
    getModifiers,
    getAllKeys,
    clearKeyboardState,
  };
};
