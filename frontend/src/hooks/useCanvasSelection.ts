import { useCallback, useRef } from 'react';
import { EditorElement } from '../types/editor';

interface SelectionBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface SelectionState {
  selectedElements: EditorElement[];
  selectionBounds: SelectionBounds | null;
  isDragging: boolean;
  dragStartX: number;
  dragStartY: number;
  dragOffsetX: number;
  dragOffsetY: number;
}

export const useCanvasSelection = () => {
  const stateRef = useRef<SelectionState>({
    selectedElements: [],
    selectionBounds: null,
    isDragging: false,
    dragStartX: 0,
    dragStartY: 0,
    dragOffsetX: 0,
    dragOffsetY: 0,
  });

  // Selecionar elementos
  const selectElements = useCallback((elements: EditorElement[]) => {
    stateRef.current.selectedElements = elements;
    stateRef.current.selectionBounds = calculateSelectionBounds(elements);
  }, []);

  // Limpar seleção
  const clearSelection = useCallback(() => {
    stateRef.current.selectedElements = [];
    stateRef.current.selectionBounds = null;
  }, []);

  // Calcular bounds da seleção
  const calculateSelectionBounds = useCallback(
    (elements: EditorElement[]): SelectionBounds | null => {
      if (elements.length === 0) return null;

      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;

      elements.forEach(element => {
        minX = Math.min(minX, element.x);
        minY = Math.min(minY, element.y);
        maxX = Math.max(maxX, element.x + element.width);
        maxY = Math.max(maxY, element.y + element.height);
      });

      return {
        x: minX,
        y: minY,
        width: maxX - minX,
        height: maxY - minY,
      };
    },
    []
  );

  // Verificar se um ponto está dentro da seleção
  const isPointInSelection = useCallback((x: number, y: number): boolean => {
    const { selectionBounds } = stateRef.current;
    if (!selectionBounds) return false;

    return (
      x >= selectionBounds.x &&
      x <= selectionBounds.x + selectionBounds.width &&
      y >= selectionBounds.y &&
      y <= selectionBounds.y + selectionBounds.height
    );
  }, []);

  // Iniciar arrasto da seleção
  const startDragging = useCallback((x: number, y: number) => {
    const { selectionBounds } = stateRef.current;
    if (!selectionBounds) return;

    stateRef.current.isDragging = true;
    stateRef.current.dragStartX = x;
    stateRef.current.dragStartY = y;
    stateRef.current.dragOffsetX = x - selectionBounds.x;
    stateRef.current.dragOffsetY = y - selectionBounds.y;
  }, []);

  // Atualizar posição durante arrasto
  const updateDragging = useCallback(
    (x: number, y: number) => {
      const state = stateRef.current;
      if (!state.isDragging) return;

      const dx = x - state.dragStartX;
      const dy = y - state.dragStartY;

      state.selectedElements = state.selectedElements.map(element => ({
        ...element,
        x: element.x + dx,
        y: element.y + dy,
      }));

      state.selectionBounds = calculateSelectionBounds(state.selectedElements);
      state.dragStartX = x;
      state.dragStartY = y;
    },
    [calculateSelectionBounds]
  );

  // Finalizar arrasto
  const stopDragging = useCallback(() => {
    stateRef.current.isDragging = false;
  }, []);

  // Desenhar borda da seleção
  const drawSelectionBorder = useCallback((ctx: CanvasRenderingContext2D) => {
    const { selectionBounds } = stateRef.current;
    if (!selectionBounds) return;

    ctx.save();
    ctx.strokeStyle = '#0095ff';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.strokeRect(
      selectionBounds.x,
      selectionBounds.y,
      selectionBounds.width,
      selectionBounds.height
    );

    // Desenhar alças de redimensionamento
    const handleSize = 8;
    const handles = [
      { x: selectionBounds.x, y: selectionBounds.y }, // Top-left
      {
        x: selectionBounds.x + selectionBounds.width / 2,
        y: selectionBounds.y,
      }, // Top-center
      { x: selectionBounds.x + selectionBounds.width, y: selectionBounds.y }, // Top-right
      {
        x: selectionBounds.x + selectionBounds.width,
        y: selectionBounds.y + selectionBounds.height / 2,
      }, // Middle-right
      {
        x: selectionBounds.x + selectionBounds.width,
        y: selectionBounds.y + selectionBounds.height,
      }, // Bottom-right
      {
        x: selectionBounds.x + selectionBounds.width / 2,
        y: selectionBounds.y + selectionBounds.height,
      }, // Bottom-center
      { x: selectionBounds.x, y: selectionBounds.y + selectionBounds.height }, // Bottom-left
      {
        x: selectionBounds.x,
        y: selectionBounds.y + selectionBounds.height / 2,
      }, // Middle-left
    ];

    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#0095ff';
    ctx.lineWidth = 1;
    ctx.setLineDash([]);

    handles.forEach(handle => {
      ctx.beginPath();
      ctx.rect(
        handle.x - handleSize / 2,
        handle.y - handleSize / 2,
        handleSize,
        handleSize
      );
      ctx.fill();
      ctx.stroke();
    });

    ctx.restore();
  }, []);

  // Obter elementos selecionados
  const getSelectedElements = useCallback(() => {
    return [...stateRef.current.selectedElements];
  }, []);

  // Verificar se há elementos selecionados
  const hasSelection = useCallback(() => {
    return stateRef.current.selectedElements.length > 0;
  }, []);

  return {
    selectElements,
    clearSelection,
    isPointInSelection,
    startDragging,
    updateDragging,
    stopDragging,
    drawSelectionBorder,
    getSelectedElements,
    hasSelection,
  };
};
