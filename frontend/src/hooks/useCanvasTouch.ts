import { useCallback, useRef } from 'react';

interface Point {
  x: number;
  y: number;
}

interface TouchState {
  isActive: boolean;
  startPoint: Point | null;
  lastPoint: Point | null;
  currentPoint: Point | null;
  startDistance: number | null;
  lastDistance: number | null;
  startAngle: number | null;
  lastAngle: number | null;
  touchCount: number;
  startTime: number;
}

interface TouchHandlers {
  onTouchStart?: (point: Point, event: TouchEvent) => void;
  onTouchMove?: (point: Point, event: TouchEvent) => void;
  onTouchEnd?: (point: Point | null, event: TouchEvent) => void;
  onPinchStart?: (
    center: Point,
    distance: number,
    angle: number,
    event: TouchEvent
  ) => void;
  onPinchMove?: (
    center: Point,
    distance: number,
    angle: number,
    event: TouchEvent
  ) => void;
  onPinchEnd?: (center: Point | null, event: TouchEvent) => void;
  onRotateStart?: (center: Point, angle: number, event: TouchEvent) => void;
  onRotateMove?: (center: Point, angle: number, event: TouchEvent) => void;
  onRotateEnd?: (center: Point | null, event: TouchEvent) => void;
  onPan?: (deltaX: number, deltaY: number, event: TouchEvent) => void;
  onSwipe?: (
    direction: 'left' | 'right' | 'up' | 'down',
    velocity: number,
    event: TouchEvent
  ) => void;
}

export const useCanvasTouch = (handlers: TouchHandlers = {}) => {
  const touchState = useRef<TouchState>({
    isActive: false,
    startPoint: null,
    lastPoint: null,
    currentPoint: null,
    startDistance: null,
    lastDistance: null,
    startAngle: null,
    lastAngle: null,
    touchCount: 0,
    startTime: 0,
  });

  // Converter coordenadas do toque para coordenadas do canvas
  const getTouchPoint = useCallback(
    (touch: Touch, canvas: HTMLCanvasElement): Point => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;

      return {
        x: (touch.clientX - rect.left) * scaleX,
        y: (touch.clientY - rect.top) * scaleY,
      };
    },
    []
  );

  // Calcular centro entre dois pontos
  const getCenter = useCallback((p1: Point, p2: Point): Point => {
    return {
      x: (p1.x + p2.x) / 2,
      y: (p1.y + p2.y) / 2,
    };
  }, []);

  // Calcular distância entre dois pontos
  const getDistance = useCallback((p1: Point, p2: Point): number => {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy);
  }, []);

  // Calcular ângulo entre dois pontos
  const getAngle = useCallback((p1: Point, p2: Point): number => {
    return (Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180) / Math.PI;
  }, []);

  // Handler para touchstart
  const handleTouchStart = useCallback(
    (event: TouchEvent) => {
      const canvas = event.currentTarget as HTMLCanvasElement;
      const touch = event.touches[0];
      const point = getTouchPoint(touch, canvas);

      touchState.current = {
        ...touchState.current,
        isActive: true,
        startPoint: point,
        lastPoint: point,
        currentPoint: point,
        touchCount: event.touches.length,
        startTime: performance.now(),
      };

      if (event.touches.length === 2) {
        const touch2 = event.touches[1];
        const point2 = getTouchPoint(touch2, canvas);
        const center = getCenter(point, point2);
        const distance = getDistance(point, point2);
        const angle = getAngle(point, point2);

        touchState.current.startDistance = distance;
        touchState.current.lastDistance = distance;
        touchState.current.startAngle = angle;
        touchState.current.lastAngle = angle;

        handlers.onPinchStart?.(center, distance, angle, event);
        handlers.onRotateStart?.(center, angle, event);
      } else {
        handlers.onTouchStart?.(point, event);
      }

      event.preventDefault();
    },
    [getTouchPoint, getCenter, getDistance, getAngle, handlers]
  );

  // Handler para touchmove
  const handleTouchMove = useCallback(
    (event: TouchEvent) => {
      if (!touchState.current.isActive) return;

      const canvas = event.currentTarget as HTMLCanvasElement;
      const touch = event.touches[0];
      const point = getTouchPoint(touch, canvas);

      touchState.current.currentPoint = point;

      if (event.touches.length === 2) {
        const touch2 = event.touches[1];
        const point2 = getTouchPoint(touch2, canvas);
        const center = getCenter(point, point2);
        const distance = getDistance(point, point2);
        const angle = getAngle(point, point2);

        // Pinch
        if (touchState.current.lastDistance !== null) {
          handlers.onPinchMove?.(center, distance, angle, event);
        }

        // Rotate
        if (touchState.current.lastAngle !== null) {
          handlers.onRotateMove?.(center, angle, event);
        }

        touchState.current.lastDistance = distance;
        touchState.current.lastAngle = angle;
      } else if (touchState.current.lastPoint) {
        // Pan
        const deltaX = point.x - touchState.current.lastPoint.x;
        const deltaY = point.y - touchState.current.lastPoint.y;
        handlers.onPan?.(deltaX, deltaY, event);
        handlers.onTouchMove?.(point, event);
      }

      touchState.current.lastPoint = point;
      event.preventDefault();
    },
    [getTouchPoint, getCenter, getDistance, getAngle, handlers]
  );

  // Handler para touchend
  const handleTouchEnd = useCallback(
    (event: TouchEvent) => {
      if (!touchState.current.isActive) return;

      const remainingTouches = event.touches.length;

      if (remainingTouches === 0) {
        // Detectar swipe
        if (
          touchState.current.startPoint &&
          touchState.current.currentPoint &&
          touchState.current.lastPoint
        ) {
          const deltaX =
            touchState.current.currentPoint.x - touchState.current.startPoint.x;
          const deltaY =
            touchState.current.currentPoint.y - touchState.current.startPoint.y;
          const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
          const time = performance.now() - touchState.current.startTime;
          const velocity = distance / time;

          if (velocity > 0.5) {
            // Velocidade mínima para considerar um swipe
            const absX = Math.abs(deltaX);
            const absY = Math.abs(deltaY);

            if (absX > absY) {
              handlers.onSwipe?.(
                deltaX > 0 ? 'right' : 'left',
                velocity,
                event
              );
            } else {
              handlers.onSwipe?.(deltaY > 0 ? 'down' : 'up', velocity, event);
            }
          }
        }

        handlers.onTouchEnd?.(touchState.current.currentPoint, event);
        handlers.onPinchEnd?.(touchState.current.currentPoint, event);
        handlers.onRotateEnd?.(touchState.current.currentPoint, event);

        touchState.current = {
          isActive: false,
          startPoint: null,
          lastPoint: null,
          currentPoint: null,
          startDistance: null,
          lastDistance: null,
          startAngle: null,
          lastAngle: null,
          touchCount: 0,
          startTime: 0,
        };
      } else {
        touchState.current.touchCount = remainingTouches;
      }

      event.preventDefault();
    },
    [handlers]
  );

  return {
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd,
    getTouchPoint,
    getCenter,
    getDistance,
    getAngle,
  };
};
