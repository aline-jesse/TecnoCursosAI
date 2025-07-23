import { useCallback, useRef } from 'react';
import { EditorElement } from '../types/editor';

interface Point {
  x: number;
  y: number;
}

interface ResizeState {
  isResizing: boolean;
  startPoint: Point | null;
  currentPoint: Point | null;
  resizeElement: EditorElement | null;
  resizeHandle: ResizeHandle | null;
  originalDimensions: {
    x: number;
    y: number;
    width: number;
    height: number;
  } | null;
  aspectRatio: number | null;
}

type ResizeHandle =
  | 'top-left'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-right'
  | 'top'
  | 'right'
  | 'bottom'
  | 'left';

interface ResizeHandlers {
  onResizeStart?: (element: EditorElement, handle: ResizeHandle) => void;
  onResize?: (element: EditorElement) => void;
  onResizeEnd?: (element: EditorElement) => void;
}

interface ResizeOptions {
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
  aspectRatio?: boolean | number;
  snapToGrid?: boolean;
  gridSize?: number;
  handles?: ResizeHandle[];
  handleSize?: number;
  handleStyle?: {
    fillColor?: string;
    strokeColor?: string;
    strokeWidth?: number;
    size?: number;
  };
}

export const useCanvasResize = (
  handlers: ResizeHandlers = {},
  options: ResizeOptions = {}
) => {
  const {
    minWidth = 10,
    minHeight = 10,
    maxWidth = Infinity,
    maxHeight = Infinity,
    aspectRatio = false,
    snapToGrid = false,
    gridSize = 10,
    handles = [
      'top-left',
      'top-right',
      'bottom-left',
      'bottom-right',
      'top',
      'right',
      'bottom',
      'left',
    ],
    handleSize = 8,
    handleStyle = {
      fillColor: '#ffffff',
      strokeColor: '#0095ff',
      strokeWidth: 2,
      size: 8,
    },
  } = options;

  const resizeState = useRef<ResizeState>({
    isResizing: false,
    startPoint: null,
    currentPoint: null,
    resizeElement: null,
    resizeHandle: null,
    originalDimensions: null,
    aspectRatio: null,
  });

  // Verificar se ponto está dentro da alça de redimensionamento
  const isPointInHandle = useCallback(
    (point: Point, element: EditorElement, handle: ResizeHandle): boolean => {
      const { x, y, width, height } = element;
      const halfHandle = handleSize / 2;

      let handleX: number;
      let handleY: number;

      switch (handle) {
        case 'top-left':
          handleX = x;
          handleY = y;
          break;
        case 'top-right':
          handleX = x + width;
          handleY = y;
          break;
        case 'bottom-left':
          handleX = x;
          handleY = y + height;
          break;
        case 'bottom-right':
          handleX = x + width;
          handleY = y + height;
          break;
        case 'top':
          handleX = x + width / 2;
          handleY = y;
          break;
        case 'right':
          handleX = x + width;
          handleY = y + height / 2;
          break;
        case 'bottom':
          handleX = x + width / 2;
          handleY = y + height;
          break;
        case 'left':
          handleX = x;
          handleY = y + height / 2;
          break;
        default:
          return false;
      }

      return (
        point.x >= handleX - halfHandle &&
        point.x <= handleX + halfHandle &&
        point.y >= handleY - halfHandle &&
        point.y <= handleY + halfHandle
      );
    },
    [handleSize]
  );

  // Encontrar alça sob o ponto
  const findHandleAtPoint = useCallback(
    (point: Point, element: EditorElement): ResizeHandle | null => {
      for (const handle of handles) {
        if (isPointInHandle(point, element, handle)) {
          return handle;
        }
      }
      return null;
    },
    [handles, isPointInHandle]
  );

  // Desenhar alças de redimensionamento
  const drawResizeHandles = useCallback(
    (ctx: CanvasRenderingContext2D, element: EditorElement) => {
      const { x, y, width, height } = element;
      const { fillColor, strokeColor, strokeWidth, size } = handleStyle;
      const halfSize = size! / 2;

      ctx.save();
      ctx.fillStyle = fillColor!;
      ctx.strokeStyle = strokeColor!;
      ctx.lineWidth = strokeWidth!;

      handles.forEach(handle => {
        let handleX: number;
        let handleY: number;

        switch (handle) {
          case 'top-left':
            handleX = x;
            handleY = y;
            break;
          case 'top-right':
            handleX = x + width;
            handleY = y;
            break;
          case 'bottom-left':
            handleX = x;
            handleY = y + height;
            break;
          case 'bottom-right':
            handleX = x + width;
            handleY = y + height;
            break;
          case 'top':
            handleX = x + width / 2;
            handleY = y;
            break;
          case 'right':
            handleX = x + width;
            handleY = y + height / 2;
            break;
          case 'bottom':
            handleX = x + width / 2;
            handleY = y + height;
            break;
          case 'left':
            handleX = x;
            handleY = y + height / 2;
            break;
        }

        ctx.beginPath();
        ctx.rect(handleX - halfSize, handleY - halfSize, size!, size!);
        ctx.fill();
        ctx.stroke();
      });

      ctx.restore();
    },
    [handles, handleStyle]
  );

  // Iniciar redimensionamento
  const startResize = useCallback(
    (point: Point, element: EditorElement, handle: ResizeHandle) => {
      resizeState.current = {
        isResizing: true,
        startPoint: point,
        currentPoint: point,
        resizeElement: element,
        resizeHandle: handle,
        originalDimensions: {
          x: element.x,
          y: element.y,
          width: element.width,
          height: element.height,
        },
        aspectRatio:
          typeof aspectRatio === 'number'
            ? aspectRatio
            : aspectRatio
              ? element.width / element.height
              : null,
      };

      handlers.onResizeStart?.(element, handle);
    },
    [aspectRatio, handlers]
  );

  // Atualizar redimensionamento
  const updateResize = useCallback(
    (point: Point) => {
      const state = resizeState.current;
      if (
        !state.isResizing ||
        !state.resizeElement ||
        !state.originalDimensions
      )
        return;

      const { startPoint, resizeHandle, originalDimensions, aspectRatio } =
        state;
      if (!startPoint) return;

      let deltaX = point.x - startPoint.x;
      let deltaY = point.y - startPoint.y;

      // Snap to grid
      if (snapToGrid) {
        deltaX = Math.round(deltaX / gridSize) * gridSize;
        deltaY = Math.round(deltaY / gridSize) * gridSize;
      }

      let newX = originalDimensions.x;
      let newY = originalDimensions.y;
      let newWidth = originalDimensions.width;
      let newHeight = originalDimensions.height;

      // Calcular novas dimensões baseado na alça
      switch (resizeHandle) {
        case 'top-left':
          newX += deltaX;
          newY += deltaY;
          newWidth -= deltaX;
          newHeight -= deltaY;
          break;
        case 'top-right':
          newY += deltaY;
          newWidth += deltaX;
          newHeight -= deltaY;
          break;
        case 'bottom-left':
          newX += deltaX;
          newWidth -= deltaX;
          newHeight += deltaY;
          break;
        case 'bottom-right':
          newWidth += deltaX;
          newHeight += deltaY;
          break;
        case 'top':
          newY += deltaY;
          newHeight -= deltaY;
          break;
        case 'right':
          newWidth += deltaX;
          break;
        case 'bottom':
          newHeight += deltaY;
          break;
        case 'left':
          newX += deltaX;
          newWidth -= deltaX;
          break;
      }

      // Manter proporção se necessário
      if (aspectRatio !== null) {
        const ratio = aspectRatio;
        if (resizeHandle.includes('left') || resizeHandle.includes('right')) {
          newHeight = newWidth / ratio;
        } else {
          newWidth = newHeight * ratio;
        }
      }

      // Aplicar limites
      newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
      newHeight = Math.max(minHeight, Math.min(maxHeight, newHeight));

      // Atualizar elemento
      const updatedElement = {
        ...state.resizeElement,
        x: newX,
        y: newY,
        width: newWidth,
        height: newHeight,
      };

      state.resizeElement = updatedElement;
      state.currentPoint = point;

      handlers.onResize?.(updatedElement);
    },
    [snapToGrid, gridSize, minWidth, minHeight, maxWidth, maxHeight, handlers]
  );

  // Finalizar redimensionamento
  const endResize = useCallback(() => {
    const { resizeElement } = resizeState.current;
    if (resizeElement) {
      handlers.onResizeEnd?.(resizeElement);
    }

    resizeState.current = {
      isResizing: false,
      startPoint: null,
      currentPoint: null,
      resizeElement: null,
      resizeHandle: null,
      originalDimensions: null,
      aspectRatio: null,
    };
  }, [handlers]);

  // Verificar se está redimensionando
  const isResizing = useCallback((): boolean => {
    return resizeState.current.isResizing;
  }, []);

  // Obter elemento sendo redimensionado
  const getResizeElement = useCallback(() => {
    return resizeState.current.resizeElement;
  }, []);

  // Obter alça sendo usada
  const getResizeHandle = useCallback(() => {
    return resizeState.current.resizeHandle;
  }, []);

  return {
    startResize,
    updateResize,
    endResize,
    isResizing,
    getResizeElement,
    getResizeHandle,
    findHandleAtPoint,
    drawResizeHandles,
  };
};
