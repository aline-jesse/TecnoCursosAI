import { useCallback } from 'react';
import { ShapeElement } from '../types/editor';

export const useCanvasShapes = () => {
  // Desenhar retângulo
  const drawRectangle = useCallback(
    (ctx: CanvasRenderingContext2D, element: ShapeElement) => {
      const { x, y, width, height, fill, stroke, strokeWidth } = element;

      ctx.beginPath();
      ctx.fillStyle = fill;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = strokeWidth;
      ctx.rect(x, y, width, height);
      ctx.fill();
      ctx.stroke();
    },
    []
  );

  // Desenhar círculo
  const drawCircle = useCallback(
    (ctx: CanvasRenderingContext2D, element: ShapeElement) => {
      const { x, y, width, height, fill, stroke, strokeWidth } = element;
      const radius = Math.min(width, height) / 2;

      ctx.beginPath();
      ctx.fillStyle = fill;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = strokeWidth;
      ctx.arc(x + radius, y + radius, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    },
    []
  );

  // Desenhar forma com base no tipo
  const drawShape = useCallback(
    (ctx: CanvasRenderingContext2D, element: ShapeElement) => {
      switch (element.shapeType) {
        case 'rectangle':
          drawRectangle(ctx, element);
          break;
        case 'circle':
          drawCircle(ctx, element);
          break;
      }
    },
    [drawRectangle, drawCircle]
  );

  // Verificar se um ponto está dentro da forma
  const isPointInShape = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      element: ShapeElement,
      x: number,
      y: number
    ): boolean => {
      ctx.beginPath();

      switch (element.shapeType) {
        case 'rectangle':
          ctx.rect(element.x, element.y, element.width, element.height);
          break;
        case 'circle':
          const radius = Math.min(element.width, element.height) / 2;
          ctx.arc(
            element.x + radius,
            element.y + radius,
            radius,
            0,
            Math.PI * 2
          );
          break;
      }

      return ctx.isPointInPath(x, y);
    },
    []
  );

  // Obter bounds da forma
  const getShapeBounds = useCallback((element: ShapeElement) => {
    return {
      x: element.x,
      y: element.y,
      width: element.width,
      height: element.height,
    };
  }, []);

  return {
    drawShape,
    isPointInShape,
    getShapeBounds,
  };
};
