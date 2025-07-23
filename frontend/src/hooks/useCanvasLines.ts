import { useCallback } from 'react';

interface LineStyle {
  color: string;
  width: number;
  cap?: CanvasLineCap;
  join?: CanvasLineJoin;
  dash?: number[];
  dashOffset?: number;
}

interface Point {
  x: number;
  y: number;
}

export const useCanvasLines = () => {
  // Aplicar estilo de linha
  const setLineStyle = useCallback(
    (ctx: CanvasRenderingContext2D, style: LineStyle) => {
      const {
        color,
        width,
        cap = 'butt',
        join = 'miter',
        dash = [],
        dashOffset = 0,
      } = style;

      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.lineCap = cap;
      ctx.lineJoin = join;
      ctx.setLineDash(dash);
      ctx.lineDashOffset = dashOffset;
    },
    []
  );

  // Desenhar linha reta
  const drawLine = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x1: number,
      y1: number,
      x2: number,
      y2: number,
      style: LineStyle
    ) => {
      ctx.save();
      setLineStyle(ctx, style);

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      ctx.restore();
    },
    [setLineStyle]
  );

  // Desenhar linha com múltiplos segmentos
  const drawPolyline = useCallback(
    (ctx: CanvasRenderingContext2D, points: Point[], style: LineStyle) => {
      if (points.length < 2) return;

      ctx.save();
      setLineStyle(ctx, style);

      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);

      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
      }

      ctx.stroke();
      ctx.restore();
    },
    [setLineStyle]
  );

  // Desenhar linha curva
  const drawCurve = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      points: Point[],
      style: LineStyle,
      tension = 0.5
    ) => {
      if (points.length < 2) return;

      ctx.save();
      setLineStyle(ctx, style);

      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);

      if (points.length === 2) {
        ctx.lineTo(points[1].x, points[1].y);
      } else {
        for (let i = 0; i < points.length - 1; i++) {
          const p0 = points[Math.max(0, i - 1)];
          const p1 = points[i];
          const p2 = points[i + 1];
          const p3 = points[Math.min(points.length - 1, i + 2)];

          const cp1x = p1.x + (p2.x - p0.x) * tension;
          const cp1y = p1.y + (p2.y - p0.y) * tension;
          const cp2x = p2.x - (p3.x - p1.x) * tension;
          const cp2y = p2.y - (p3.y - p1.y) * tension;

          ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
        }
      }

      ctx.stroke();
      ctx.restore();
    },
    [setLineStyle]
  );

  // Desenhar linha com setas
  const drawArrowLine = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x1: number,
      y1: number,
      x2: number,
      y2: number,
      style: LineStyle,
      arrowSize = 10
    ) => {
      ctx.save();
      setLineStyle(ctx, style);

      // Desenhar linha principal
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      // Calcular ângulo da linha
      const angle = Math.atan2(y2 - y1, x2 - x1);

      // Desenhar ponta da seta
      ctx.beginPath();
      ctx.moveTo(x2, y2);
      ctx.lineTo(
        x2 - arrowSize * Math.cos(angle - Math.PI / 6),
        y2 - arrowSize * Math.sin(angle - Math.PI / 6)
      );
      ctx.moveTo(x2, y2);
      ctx.lineTo(
        x2 - arrowSize * Math.cos(angle + Math.PI / 6),
        y2 - arrowSize * Math.sin(angle + Math.PI / 6)
      );
      ctx.stroke();

      ctx.restore();
    },
    [setLineStyle]
  );

  // Desenhar linha pontilhada
  const drawDashedLine = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x1: number,
      y1: number,
      x2: number,
      y2: number,
      style: LineStyle,
      dashPattern: number[] = [5, 5]
    ) => {
      drawLine(ctx, x1, y1, x2, y2, {
        ...style,
        dash: dashPattern,
      });
    },
    [drawLine]
  );

  // Desenhar grade
  const drawGrid = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      width: number,
      height: number,
      cellSize: number,
      style: LineStyle
    ) => {
      ctx.save();
      setLineStyle(ctx, style);

      // Linhas verticais
      for (let x = 0; x <= width; x += cellSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }

      // Linhas horizontais
      for (let y = 0; y <= height; y += cellSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      ctx.restore();
    },
    [setLineStyle]
  );

  return {
    drawLine,
    drawPolyline,
    drawCurve,
    drawArrowLine,
    drawDashedLine,
    drawGrid,
  };
};
