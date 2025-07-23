import { useCallback, useRef } from 'react';
import { EditorElement } from '../types/editor';

interface Point {
  x: number;
  y: number;
}

interface RotationState {
  isRotating: boolean;
  startAngle: number | null;
  currentAngle: number | null;
  rotateElement: EditorElement | null;
  rotateHandle: Point | null;
  centerPoint: Point | null;
  originalRotation: number | null;
}

interface RotationHandlers {
  onRotateStart?: (element: EditorElement, angle: number) => void;
  onRotate?: (element: EditorElement, angle: number) => void;
  onRotateEnd?: (element: EditorElement, angle: number) => void;
}

interface RotationOptions {
  snapToAngle?: boolean;
  snapAngle?: number;
  handleDistance?: number;
  handleStyle?: {
    fillColor?: string;
    strokeColor?: string;
    strokeWidth?: number;
    radius?: number;
  };
}

export const useCanvasRotation = (
  handlers: RotationHandlers = {},
  options: RotationOptions = {}
) => {
  const {
    snapToAngle = false,
    snapAngle = 15,
    handleDistance = 30,
    handleStyle = {
      fillColor: '#ffffff',
      strokeColor: '#0095ff',
      strokeWidth: 2,
      radius: 6,
    },
  } = options;

  const rotationState = useRef<RotationState>({
    isRotating: false,
    startAngle: null,
    currentAngle: null,
    rotateElement: null,
    rotateHandle: null,
    centerPoint: null,
    originalRotation: null,
  });

  // Calcular ângulo entre dois pontos
  const getAngle = useCallback((center: Point, point: Point): number => {
    return (Math.atan2(point.y - center.y, point.x - center.x) * 180) / Math.PI;
  }, []);

  // Normalizar ângulo para o intervalo [0, 360)
  const normalizeAngle = useCallback((angle: number): number => {
    return ((angle % 360) + 360) % 360;
  }, []);

  // Snap ângulo para o grid
  const snapAngleToGrid = useCallback(
    (angle: number): number => {
      if (!snapToAngle) return angle;
      return Math.round(angle / snapAngle) * snapAngle;
    },
    [snapToAngle, snapAngle]
  );

  // Calcular posição da alça de rotação
  const getRotateHandlePosition = useCallback(
    (element: EditorElement): Point => {
      const centerX = element.x + element.width / 2;
      const centerY = element.y + element.height / 2;
      const rotation = element.rotation || 0;
      const rad = (rotation * Math.PI) / 180;

      return {
        x: centerX + Math.sin(rad) * -handleDistance,
        y: centerY + Math.cos(rad) * -handleDistance,
      };
    },
    [handleDistance]
  );

  // Verificar se ponto está dentro da alça de rotação
  const isPointInRotateHandle = useCallback(
    (point: Point, element: EditorElement): boolean => {
      const handle = getRotateHandlePosition(element);
      const dx = point.x - handle.x;
      const dy = point.y - handle.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      return distance <= handleStyle.radius!;
    },
    [getRotateHandlePosition, handleStyle.radius]
  );

  // Desenhar alça de rotação
  const drawRotateHandle = useCallback(
    (ctx: CanvasRenderingContext2D, element: EditorElement) => {
      const handle = getRotateHandlePosition(element);
      const { fillColor, strokeColor, strokeWidth, radius } = handleStyle;

      ctx.save();
      ctx.beginPath();
      ctx.arc(handle.x, handle.y, radius!, 0, Math.PI * 2);
      ctx.fillStyle = fillColor!;
      ctx.strokeStyle = strokeColor!;
      ctx.lineWidth = strokeWidth!;
      ctx.fill();
      ctx.stroke();

      // Desenhar linha do centro até a alça
      const centerX = element.x + element.width / 2;
      const centerY = element.y + element.height / 2;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(handle.x, handle.y);
      ctx.stroke();

      ctx.restore();
    },
    [getRotateHandlePosition, handleStyle]
  );

  // Iniciar rotação
  const startRotation = useCallback(
    (point: Point, element: EditorElement) => {
      const centerX = element.x + element.width / 2;
      const centerY = element.y + element.height / 2;
      const startAngle = getAngle({ x: centerX, y: centerY }, point);

      rotationState.current = {
        isRotating: true,
        startAngle,
        currentAngle: startAngle,
        rotateElement: element,
        rotateHandle: getRotateHandlePosition(element),
        centerPoint: { x: centerX, y: centerY },
        originalRotation: element.rotation || 0,
      };

      handlers.onRotateStart?.(element, startAngle);
    },
    [getAngle, getRotateHandlePosition, handlers]
  );

  // Atualizar rotação
  const updateRotation = useCallback(
    (point: Point) => {
      const state = rotationState.current;
      if (
        !state.isRotating ||
        !state.rotateElement ||
        !state.centerPoint ||
        state.startAngle === null ||
        state.originalRotation === null
      )
        return;

      const currentAngle = getAngle(state.centerPoint, point);
      const deltaAngle = currentAngle - state.startAngle;
      let newRotation = normalizeAngle(state.originalRotation + deltaAngle);

      // Aplicar snap se necessário
      newRotation = snapAngleToGrid(newRotation);

      // Atualizar elemento
      const updatedElement = {
        ...state.rotateElement,
        rotation: newRotation,
      };

      state.rotateElement = updatedElement;
      state.currentAngle = currentAngle;

      handlers.onRotate?.(updatedElement, newRotation);
    },
    [getAngle, normalizeAngle, snapAngleToGrid, handlers]
  );

  // Finalizar rotação
  const endRotation = useCallback(() => {
    const { rotateElement, currentAngle } = rotationState.current;
    if (rotateElement && currentAngle !== null) {
      handlers.onRotateEnd?.(rotateElement, currentAngle);
    }

    rotationState.current = {
      isRotating: false,
      startAngle: null,
      currentAngle: null,
      rotateElement: null,
      rotateHandle: null,
      centerPoint: null,
      originalRotation: null,
    };
  }, [handlers]);

  // Verificar se está rotacionando
  const isRotating = useCallback((): boolean => {
    return rotationState.current.isRotating;
  }, []);

  // Obter elemento sendo rotacionado
  const getRotateElement = useCallback(() => {
    return rotationState.current.rotateElement;
  }, []);

  // Obter ângulo atual
  const getCurrentAngle = useCallback(() => {
    return rotationState.current.currentAngle;
  }, []);

  return {
    startRotation,
    updateRotation,
    endRotation,
    isRotating,
    getRotateElement,
    getCurrentAngle,
    isPointInRotateHandle,
    drawRotateHandle,
    getRotateHandlePosition,
  };
};
