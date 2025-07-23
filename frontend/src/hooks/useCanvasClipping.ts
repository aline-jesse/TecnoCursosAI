import { useCallback } from 'react';

interface ClipConfig {
  x: number;
  y: number;
  width: number;
  height: number;
  radius?: number;
}

export const useCanvasClipping = () => {
  // Criar área de recorte retangular
  const clipRect = useCallback(
    (ctx: CanvasRenderingContext2D, config: ClipConfig) => {
      const { x, y, width, height } = config;
      ctx.beginPath();
      ctx.rect(x, y, width, height);
      ctx.clip();
    },
    []
  );

  // Criar área de recorte circular
  const clipCircle = useCallback(
    (ctx: CanvasRenderingContext2D, x: number, y: number, radius: number) => {
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.clip();
    },
    []
  );

  // Criar área de recorte com cantos arredondados
  const clipRoundedRect = useCallback(
    (ctx: CanvasRenderingContext2D, config: ClipConfig) => {
      const { x, y, width, height, radius = 0 } = config;

      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + width - radius, y);
      ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
      ctx.lineTo(x + width, y + height - radius);
      ctx.quadraticCurveTo(
        x + width,
        y + height,
        x + width - radius,
        y + height
      );
      ctx.lineTo(x + radius, y + height);
      ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.closePath();
      ctx.clip();
    },
    []
  );

  // Criar área de recorte com caminho personalizado
  const clipPath = useCallback(
    (ctx: CanvasRenderingContext2D, path: Path2D) => {
      ctx.clip(path);
    },
    []
  );

  // Criar área de recorte com polígono
  const clipPolygon = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      points: Array<{ x: number; y: number }>
    ) => {
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);

      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
      }

      ctx.closePath();
      ctx.clip();
    },
    []
  );

  // Criar área de recorte com texto
  const clipText = useCallback(
    (ctx: CanvasRenderingContext2D, text: string, x: number, y: number) => {
      ctx.beginPath();
      ctx.fillText(text, x, y);
      ctx.clip();
    },
    []
  );

  // Salvar estado do clipping
  const saveClipState = useCallback((ctx: CanvasRenderingContext2D) => {
    ctx.save();
  }, []);

  // Restaurar estado do clipping
  const restoreClipState = useCallback((ctx: CanvasRenderingContext2D) => {
    ctx.restore();
  }, []);

  return {
    clipRect,
    clipCircle,
    clipRoundedRect,
    clipPath,
    clipPolygon,
    clipText,
    saveClipState,
    restoreClipState,
  };
};
