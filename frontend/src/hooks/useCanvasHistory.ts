import { useCallback, useRef } from 'react';
import { History, HistoryUpdate, Scene } from '../types/editor';

export const useCanvasHistory = (initialScenes: Scene[]) => {
  const historyRef = useRef<History>({
    past: [],
    present: initialScenes,
    future: [],
  });

  // Adicionar estado ao histórico
  const pushState = useCallback((update: HistoryUpdate) => {
    historyRef.current = {
      past: [...historyRef.current.past, historyRef.current.present],
      present: [...historyRef.current.present],
      future: [],
    };
  }, []);

  // Desfazer última ação
  const undo = useCallback(() => {
    const { past, present, future } = historyRef.current;

    if (past.length === 0) return;

    const previous = past[past.length - 1];
    const newPast = past.slice(0, -1);

    historyRef.current = {
      past: newPast,
      present: previous,
      future: [present, ...future],
    };

    return previous;
  }, []);

  // Refazer última ação desfeita
  const redo = useCallback(() => {
    const { past, present, future } = historyRef.current;

    if (future.length === 0) return;

    const next = future[0];
    const newFuture = future.slice(1);

    historyRef.current = {
      past: [...past, present],
      present: next,
      future: newFuture,
    };

    return next;
  }, []);

  // Limpar histórico
  const clearHistory = useCallback(() => {
    historyRef.current = {
      past: [],
      present: historyRef.current.present,
      future: [],
    };
  }, []);

  // Verificar se é possível desfazer/refazer
  const canUndo = useCallback(() => {
    return historyRef.current.past.length > 0;
  }, []);

  const canRedo = useCallback(() => {
    return historyRef.current.future.length > 0;
  }, []);

  // Obter estado atual
  const getCurrentState = useCallback(() => {
    return historyRef.current.present;
  }, []);

  return {
    pushState,
    undo,
    redo,
    clearHistory,
    canUndo,
    canRedo,
    getCurrentState,
    history: historyRef.current,
  };
};
