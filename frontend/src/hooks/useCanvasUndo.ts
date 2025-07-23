import { useCallback, useRef } from 'react';
import { Scene } from '../types/editor';

interface UndoState {
  past: Scene[][];
  present: Scene[];
  future: Scene[][];
  maxHistorySize: number;
  isUndoing: boolean;
  isRedoing: boolean;
  lastActionTime: number;
  actionCount: number;
}

interface UndoHandlers {
  onUndo?: (scenes: Scene[]) => void;
  onRedo?: (scenes: Scene[]) => void;
  onStateChange?: (scenes: Scene[]) => void;
  onHistoryChange?: (past: Scene[][], future: Scene[][]) => void;
}

interface UndoOptions {
  maxHistorySize?: number;
  debounceTime?: number;
  groupSimilarActions?: boolean;
  similarityThreshold?: number;
}

export const useCanvasUndo = (
  initialScenes: Scene[],
  handlers: UndoHandlers = {},
  options: UndoOptions = {}
) => {
  const {
    maxHistorySize = 50,
    debounceTime = 1000,
    groupSimilarActions = true,
    similarityThreshold = 0.8,
  } = options;

  const undoState = useRef<UndoState>({
    past: [],
    present: initialScenes,
    future: [],
    maxHistorySize,
    isUndoing: false,
    isRedoing: false,
    lastActionTime: 0,
    actionCount: 0,
  });

  const debounceTimer = useRef<number | null>(null);

  // Calcular similaridade entre estados
  const calculateSimilarity = useCallback(
    (state1: Scene[], state2: Scene[]): number => {
      if (!groupSimilarActions) return 0;

      // Comparar número de cenas
      if (state1.length !== state2.length) return 0;

      let similarScenes = 0;

      state1.forEach((scene1, index) => {
        const scene2 = state2[index];

        // Comparar elementos
        const elements1 = scene1.elements;
        const elements2 = scene2.elements;

        if (elements1.length === elements2.length) {
          let similarElements = 0;

          elements1.forEach((element1, elementIndex) => {
            const element2 = elements2[elementIndex];

            // Comparar propriedades básicas
            if (
              element1.type === element2.type &&
              element1.x === element2.x &&
              element1.y === element2.y &&
              element1.width === element2.width &&
              element1.height === element2.height &&
              element1.rotation === element2.rotation
            ) {
              similarElements++;
            }
          });

          if (similarElements / elements1.length >= similarityThreshold) {
            similarScenes++;
          }
        }
      });

      return similarScenes / state1.length;
    },
    [groupSimilarActions, similarityThreshold]
  );

  // Adicionar estado ao histórico
  const pushState = useCallback(
    (newState: Scene[]) => {
      const state = undoState.current;

      // Limpar timer de debounce anterior
      if (debounceTimer.current !== null) {
        clearTimeout(debounceTimer.current);
      }

      // Criar novo timer de debounce
      debounceTimer.current = window.setTimeout(() => {
        const timeSinceLastAction = performance.now() - state.lastActionTime;
        const similarity = calculateSimilarity(state.present, newState);

        // Verificar se deve agrupar com ação anterior
        if (
          groupSimilarActions &&
          timeSinceLastAction < debounceTime &&
          similarity >= similarityThreshold
        ) {
          // Atualizar estado presente sem adicionar ao histórico
          state.present = newState;
        } else {
          // Adicionar novo estado ao histórico
          state.past = [
            ...state.past.slice(-(maxHistorySize - 1)),
            state.present,
          ];
          state.present = newState;
          state.future = [];
        }

        state.lastActionTime = performance.now();
        state.actionCount++;

        handlers.onStateChange?.(newState);
        handlers.onHistoryChange?.(state.past, state.future);

        debounceTimer.current = null;
      }, debounceTime);
    },
    [
      maxHistorySize,
      debounceTime,
      groupSimilarActions,
      similarityThreshold,
      calculateSimilarity,
      handlers,
    ]
  );

  // Desfazer última ação
  const undo = useCallback(() => {
    const state = undoState.current;

    if (state.past.length === 0 || state.isUndoing) return;

    state.isUndoing = true;
    const previous = state.past[state.past.length - 1];
    const newPast = state.past.slice(0, -1);

    state.future = [state.present, ...state.future];
    state.present = previous;
    state.past = newPast;

    handlers.onUndo?.(previous);
    handlers.onStateChange?.(previous);
    handlers.onHistoryChange?.(newPast, state.future);

    state.isUndoing = false;
  }, [handlers]);

  // Refazer última ação desfeita
  const redo = useCallback(() => {
    const state = undoState.current;

    if (state.future.length === 0 || state.isRedoing) return;

    state.isRedoing = true;
    const next = state.future[0];
    const newFuture = state.future.slice(1);

    state.past = [...state.past, state.present];
    state.present = next;
    state.future = newFuture;

    handlers.onRedo?.(next);
    handlers.onStateChange?.(next);
    handlers.onHistoryChange?.(state.past, newFuture);

    state.isRedoing = false;
  }, [handlers]);

  // Limpar histórico
  const clearHistory = useCallback(() => {
    const state = undoState.current;

    state.past = [];
    state.future = [];
    state.actionCount = 0;
    state.lastActionTime = 0;

    handlers.onHistoryChange?.([], []);
  }, [handlers]);

  // Verificar se pode desfazer
  const canUndo = useCallback((): boolean => {
    return undoState.current.past.length > 0;
  }, []);

  // Verificar se pode refazer
  const canRedo = useCallback((): boolean => {
    return undoState.current.future.length > 0;
  }, []);

  // Obter estado atual
  const getCurrentState = useCallback((): Scene[] => {
    return undoState.current.present;
  }, []);

  // Obter tamanho do histórico
  const getHistorySize = useCallback(() => {
    const { past, future } = undoState.current;
    return {
      past: past.length,
      future: future.length,
      total: past.length + 1 + future.length,
    };
  }, []);

  // Obter contagem de ações
  const getActionCount = useCallback((): number => {
    return undoState.current.actionCount;
  }, []);

  return {
    pushState,
    undo,
    redo,
    clearHistory,
    canUndo,
    canRedo,
    getCurrentState,
    getHistorySize,
    getActionCount,
  };
};
