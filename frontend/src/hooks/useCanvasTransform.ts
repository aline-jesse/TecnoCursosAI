import { useCallback, useRef } from 'react';

interface Transform {
  translate?: { x: number; y: number };
  scale?: number;
  rotate?: number;
}

interface Point {
  x: number;
  y: number;
}

export const useCanvasTransform = () => {
  const transformRef = useRef<Transform>({
    translate: { x: 0, y: 0 },
    scale: 1,
    rotate: 0,
  });

  // Aplicar transformação ao contexto
  const setTransform = useCallback(
    (ctx: CanvasRenderingContext2D, transform: Transform) => {
      const { translate, scale, rotate } = transform;

      ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset transform

      if (translate) {
        ctx.translate(translate.x, translate.y);
      }

      if (scale) {
        ctx.scale(scale, scale);
      }

      if (rotate) {
        ctx.rotate((rotate * Math.PI) / 180);
      }
    },
    []
  );

  // Resetar transformação
  const resetTransform = useCallback((ctx: CanvasRenderingContext2D) => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    transformRef.current = {
      translate: { x: 0, y: 0 },
      scale: 1,
      rotate: 0,
    };
  }, []);

  // Executar operação com transformação temporária
  const withTransform = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      transform: Transform,
      callback: () => void
    ) => {
      ctx.save();
      setTransform(ctx, transform);
      callback();
      ctx.restore();
    },
    [setTransform]
  );

  // Transformar ponto do canvas para coordenadas do mundo
  const transformPoint = useCallback((point: Point): Point => {
    const { translate, scale, rotate } = transformRef.current;
    const rad = ((rotate || 0) * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    const s = scale || 1;
    const tx = translate?.x || 0;
    const ty = translate?.y || 0;

    return {
      x: point.x * cos * s - point.y * sin * s + tx,
      y: point.x * sin * s + point.y * cos * s + ty,
    };
  }, []);

  // Transformar ponto do mundo para coordenadas do canvas
  const inverseTransformPoint = useCallback((point: Point): Point => {
    const { translate, scale, rotate } = transformRef.current;
    const rad = ((rotate || 0) * Math.PI) / 180;
    const cos = Math.cos(-rad);
    const sin = Math.sin(-rad);
    const s = 1 / (scale || 1);
    const tx = -(translate?.x || 0);
    const ty = -(translate?.y || 0);

    const px = point.x + tx;
    const py = point.y + ty;

    return {
      x: (px * cos - py * sin) * s,
      y: (px * sin + py * cos) * s,
    };
  }, []);

  return {
    setTransform,
    resetTransform,
    withTransform,
    transformPoint,
    inverseTransformPoint,
    currentTransform: transformRef.current,
  };
};
