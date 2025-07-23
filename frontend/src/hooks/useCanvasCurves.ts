import { useCallback } from 'react';

interface Point {
  x: number;
  y: number;
}

interface CurveStyle {
  strokeStyle?: string | CanvasGradient | CanvasPattern;
  lineWidth?: number;
  lineCap?: CanvasLineCap;
  lineJoin?: CanvasLineJoin;
  lineDash?: number[];
  opacity?: number;
}

const DEFAULT_STYLE: Required<CurveStyle> = {
  strokeStyle: '#000000',
  lineWidth: 1,
  lineCap: 'butt',
  lineJoin: 'miter',
  lineDash: [],
  opacity: 1,
};

export const useCanvasCurves = () => {
  const setCurveStyle = useCallback(
    (ctx: CanvasRenderingContext2D, style: CurveStyle = {}) => {
      const { strokeStyle, lineWidth, lineCap, lineJoin, lineDash, opacity } = {
        ...DEFAULT_STYLE,
        ...style,
      };

      ctx.strokeStyle = strokeStyle;
      ctx.lineWidth = lineWidth;
      ctx.lineCap = lineCap;
      ctx.lineJoin = lineJoin;
      ctx.setLineDash(lineDash);
      ctx.globalAlpha = opacity;
    },
    []
  );

  const drawBezierCurve = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      start: Point,
      control1: Point,
      control2: Point,
      end: Point,
      style: CurveStyle = {}
    ) => {
      ctx.save();
      setCurveStyle(ctx, style);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.bezierCurveTo(
        control1.x,
        control1.y,
        control2.x,
        control2.y,
        end.x,
        end.y
      );
      ctx.stroke();
      ctx.restore();
    },
    [setCurveStyle]
  );

  const drawQuadraticCurve = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      start: Point,
      control: Point,
      end: Point,
      style: CurveStyle = {}
    ) => {
      ctx.save();
      setCurveStyle(ctx, style);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.quadraticCurveTo(control.x, control.y, end.x, end.y);
      ctx.stroke();
      ctx.restore();
    },
    [setCurveStyle]
  );

  const drawSmoothCurve = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      points: Point[],
      tension = 0.5,
      style: CurveStyle = {}
    ) => {
      if (points.length < 2) return;

      ctx.save();
      setCurveStyle(ctx, style);
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);

      for (let i = 0; i < points.length - 1; i++) {
        const current = points[i];
        const next = points[i + 1];
        const prev = points[i - 1] || current;
        const after = points[i + 2] || next;

        const controlPoint1 = {
          x: current.x + ((next.x - prev.x) * tension) / 2,
          y: current.y + ((next.y - prev.y) * tension) / 2,
        };

        const controlPoint2 = {
          x: next.x - ((after.x - current.x) * tension) / 2,
          y: next.y - ((after.y - current.y) * tension) / 2,
        };

        ctx.bezierCurveTo(
          controlPoint1.x,
          controlPoint1.y,
          controlPoint2.x,
          controlPoint2.y,
          next.x,
          next.y
        );
      }

      ctx.stroke();
      ctx.restore();
    },
    [setCurveStyle]
  );

  const drawCatmullRomSpline = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      points: Point[],
      alpha = 0.5,
      style: CurveStyle = {}
    ) => {
      if (points.length < 2) return;

      ctx.save();
      setCurveStyle(ctx, style);
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);

      for (let i = 0; i < points.length - 1; i++) {
        const p0 = points[Math.max(0, i - 1)];
        const p1 = points[i];
        const p2 = points[i + 1];
        const p3 = points[Math.min(points.length - 1, i + 2)];

        const d1 = Math.sqrt(
          Math.pow(p1.x - p0.x, 2) + Math.pow(p1.y - p0.y, 2)
        );
        const d2 = Math.sqrt(
          Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2)
        );
        const d3 = Math.sqrt(
          Math.pow(p3.x - p2.x, 2) + Math.pow(p3.y - p2.y, 2)
        );

        const d1a = Math.pow(d1, alpha);
        const d2a = Math.pow(d2, alpha);
        const d3a = Math.pow(d3, alpha);

        const controlPoint1 = {
          x: p1.x + (d2a / (d1a + d2a)) * (p2.x - p0.x),
          y: p1.y + (d2a / (d1a + d2a)) * (p2.y - p0.y),
        };

        const controlPoint2 = {
          x: p2.x - (d2a / (d2a + d3a)) * (p3.x - p1.x),
          y: p2.y - (d2a / (d2a + d3a)) * (p3.y - p1.y),
        };

        ctx.bezierCurveTo(
          controlPoint1.x,
          controlPoint1.y,
          controlPoint2.x,
          controlPoint2.y,
          p2.x,
          p2.y
        );
      }

      ctx.stroke();
      ctx.restore();
    },
    [setCurveStyle]
  );

  const drawHermiteCurve = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      start: Point,
      end: Point,
      tangent1: Point,
      tangent2: Point,
      style: CurveStyle = {}
    ) => {
      ctx.save();
      setCurveStyle(ctx, style);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);

      const steps = 100;
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        const t2 = t * t;
        const t3 = t2 * t;
        const h1 = 2 * t3 - 3 * t2 + 1;
        const h2 = -2 * t3 + 3 * t2;
        const h3 = t3 - 2 * t2 + t;
        const h4 = t3 - t2;

        const x = h1 * start.x + h2 * end.x + h3 * tangent1.x + h4 * tangent2.x;
        const y = h1 * start.y + h2 * end.y + h3 * tangent1.y + h4 * tangent2.y;

        ctx.lineTo(x, y);
      }

      ctx.stroke();
      ctx.restore();
    },
    [setCurveStyle]
  );

  return {
    setCurveStyle,
    drawBezierCurve,
    drawQuadraticCurve,
    drawSmoothCurve,
    drawCatmullRomSpline,
    drawHermiteCurve,
  };
};
