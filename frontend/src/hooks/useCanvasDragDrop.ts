import { useCallback, useRef } from 'react';

interface Point {
  x: number;
  y: number;
}

interface DragState {
  isDragging: boolean;
  startPoint: Point | null;
  currentPoint: Point | null;
  draggedElement: any;
  dragData: any;
  dropTarget: EventTarget | null;
  dragCount: number;
  dropCount: number;
}

interface DragHandlers {
  onDragStart?: (point: Point, event: DragEvent) => void;
  onDrag?: (point: Point, event: DragEvent) => void;
  onDragEnd?: (point: Point | null, event: DragEvent) => void;
  onDragEnter?: (event: DragEvent) => void;
  onDragLeave?: (event: DragEvent) => void;
  onDragOver?: (point: Point, event: DragEvent) => void;
  onDrop?: (point: Point, event: DragEvent) => void;
}

interface DragOptions {
  acceptTypes?: string[];
  dropEffect?: 'none' | 'copy' | 'link' | 'move';
  dragImage?: HTMLImageElement;
  dragImageOffset?: Point;
  preventDefaultDrop?: boolean;
}

export const useCanvasDragDrop = (
  handlers: DragHandlers = {},
  options: DragOptions = {}
) => {
  const {
    acceptTypes = [],
    dropEffect = 'move',
    dragImage,
    dragImageOffset = { x: 0, y: 0 },
    preventDefaultDrop = true,
  } = options;

  const dragState = useRef<DragState>({
    isDragging: false,
    startPoint: null,
    currentPoint: null,
    draggedElement: null,
    dragData: null,
    dropTarget: null,
    dragCount: 0,
    dropCount: 0,
  });

  // Converter coordenadas do mouse para coordenadas do canvas
  const getCanvasPoint = useCallback(
    (event: DragEvent, canvas: HTMLCanvasElement): Point => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;

      return {
        x: (event.clientX - rect.left) * scaleX,
        y: (event.clientY - rect.top) * scaleY,
      };
    },
    []
  );

  // Verificar se tipo é aceito
  const isTypeAccepted = useCallback(
    (type: string): boolean => {
      if (acceptTypes.length === 0) return true;
      return acceptTypes.some(acceptType =>
        type.toLowerCase().includes(acceptType.toLowerCase())
      );
    },
    [acceptTypes]
  );

  // Handler para dragstart
  const handleDragStart = useCallback(
    (event: DragEvent) => {
      const canvas = event.currentTarget as HTMLCanvasElement;
      const point = getCanvasPoint(event, canvas);

      dragState.current = {
        ...dragState.current,
        isDragging: true,
        startPoint: point,
        currentPoint: point,
        draggedElement: event.target,
        dragCount: dragState.current.dragCount + 1,
      };

      // Configurar imagem de arrastar
      if (dragImage) {
        event.dataTransfer?.setDragImage(
          dragImage,
          dragImageOffset.x,
          dragImageOffset.y
        );
      }

      // Configurar efeito de arrastar
      event.dataTransfer!.effectAllowed = dropEffect;

      handlers.onDragStart?.(point, event);
    },
    [getCanvasPoint, dragImage, dragImageOffset, dropEffect, handlers]
  );

  // Handler para drag
  const handleDrag = useCallback(
    (event: DragEvent) => {
      if (!dragState.current.isDragging) return;

      const canvas = event.currentTarget as HTMLCanvasElement;
      const point = getCanvasPoint(event, canvas);

      dragState.current.currentPoint = point;
      handlers.onDrag?.(point, event);
    },
    [getCanvasPoint, handlers]
  );

  // Handler para dragend
  const handleDragEnd = useCallback(
    (event: DragEvent) => {
      if (!dragState.current.isDragging) return;

      const canvas = event.currentTarget as HTMLCanvasElement;
      const point = dragState.current.currentPoint;

      dragState.current = {
        ...dragState.current,
        isDragging: false,
        draggedElement: null,
        dragData: null,
      };

      handlers.onDragEnd?.(point, event);
    },
    [handlers]
  );

  // Handler para dragenter
  const handleDragEnter = useCallback(
    (event: DragEvent) => {
      const types = Array.from(event.dataTransfer?.types || []);
      if (!types.some(isTypeAccepted)) return;

      dragState.current.dropTarget = event.target;
      handlers.onDragEnter?.(event);
    },
    [isTypeAccepted, handlers]
  );

  // Handler para dragleave
  const handleDragLeave = useCallback(
    (event: DragEvent) => {
      if (event.target === dragState.current.dropTarget) {
        dragState.current.dropTarget = null;
        handlers.onDragLeave?.(event);
      }
    },
    [handlers]
  );

  // Handler para dragover
  const handleDragOver = useCallback(
    (event: DragEvent) => {
      const types = Array.from(event.dataTransfer?.types || []);
      if (!types.some(isTypeAccepted)) return;

      event.preventDefault();
      event.dataTransfer!.dropEffect = dropEffect;

      const canvas = event.currentTarget as HTMLCanvasElement;
      const point = getCanvasPoint(event, canvas);

      handlers.onDragOver?.(point, event);
    },
    [getCanvasPoint, isTypeAccepted, dropEffect, handlers]
  );

  // Handler para drop
  const handleDrop = useCallback(
    (event: DragEvent) => {
      if (preventDefaultDrop) {
        event.preventDefault();
      }

      const types = Array.from(event.dataTransfer?.types || []);
      if (!types.some(isTypeAccepted)) return;

      const canvas = event.currentTarget as HTMLCanvasElement;
      const point = getCanvasPoint(event, canvas);

      dragState.current = {
        ...dragState.current,
        dropCount: dragState.current.dropCount + 1,
        dropTarget: null,
      };

      handlers.onDrop?.(point, event);
    },
    [getCanvasPoint, isTypeAccepted, preventDefaultDrop, handlers]
  );

  // Iniciar operação de arrastar
  const startDrag = useCallback(
    (
      element: HTMLElement,
      data: any,
      options: {
        image?: HTMLImageElement;
        imageOffset?: Point;
        effect?: DragOptions['dropEffect'];
      } = {}
    ) => {
      const {
        image = dragImage,
        imageOffset = dragImageOffset,
        effect = dropEffect,
      } = options;

      const dragEvent = new DragEvent('dragstart', {
        bubbles: true,
        cancelable: true,
      });

      Object.defineProperty(dragEvent, 'dataTransfer', {
        value: new DataTransfer(),
      });

      if (image) {
        dragEvent.dataTransfer?.setDragImage(
          image,
          imageOffset.x,
          imageOffset.y
        );
      }

      dragEvent.dataTransfer!.effectAllowed = effect;
      dragState.current.dragData = data;

      element.dispatchEvent(dragEvent);
    },
    [dragImage, dragImageOffset, dropEffect]
  );

  // Verificar se está arrastando
  const isDragging = useCallback((): boolean => {
    return dragState.current.isDragging;
  }, []);

  // Obter dados do arrasto
  const getDragData = useCallback(() => {
    return dragState.current.dragData;
  }, []);

  // Obter elemento arrastado
  const getDraggedElement = useCallback(() => {
    return dragState.current.draggedElement;
  }, []);

  // Obter contagem de operações
  const getDragCount = useCallback((): number => {
    return dragState.current.dragCount;
  }, []);

  const getDropCount = useCallback((): number => {
    return dragState.current.dropCount;
  }, []);

  // Limpar estado
  const clearDragState = useCallback(() => {
    dragState.current = {
      isDragging: false,
      startPoint: null,
      currentPoint: null,
      draggedElement: null,
      dragData: null,
      dropTarget: null,
      dragCount: 0,
      dropCount: 0,
    };
  }, []);

  return {
    handleDragStart,
    handleDrag,
    handleDragEnd,
    handleDragEnter,
    handleDragLeave,
    handleDragOver,
    handleDrop,
    startDrag,
    isDragging,
    getDragData,
    getDraggedElement,
    getDragCount,
    getDropCount,
    clearDragState,
  };
};
