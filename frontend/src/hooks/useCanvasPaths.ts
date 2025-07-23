import { useCallback } from 'react';

interface Point {
  x: number;
  y: number;
}

interface PathStyle {
  fillStyle?: string | CanvasGradient | CanvasPattern;
  strokeStyle?: string | CanvasGradient | CanvasPattern;
  lineWidth?: number;
  lineCap?: CanvasLineCap;
  lineJoin?: CanvasLineJoin;
  lineDash?: number[];
  opacity?: number;
  fillRule?: 'nonzero' | 'evenodd';
}

const DEFAULT_STYLE: Required<PathStyle> = {
  fillStyle: '#000000',
  strokeStyle: '#000000',
  lineWidth: 1,
  lineCap: 'butt',
  lineJoin: 'miter',
  lineDash: [],
  opacity: 1,
  fillRule: 'nonzero',
};

export const useCanvasPaths = () => {
  const setPathStyle = useCallback(
    (ctx: CanvasRenderingContext2D, style: PathStyle = {}) => {
      const {
        fillStyle,
        strokeStyle,
        lineWidth,
        lineCap,
        lineJoin,
        lineDash,
        opacity,
      } = { ...DEFAULT_STYLE, ...style };

      ctx.fillStyle = fillStyle;
      ctx.strokeStyle = strokeStyle;
      ctx.lineWidth = lineWidth;
      ctx.lineCap = lineCap;
      ctx.lineJoin = lineJoin;
      ctx.setLineDash(lineDash);
      ctx.globalAlpha = opacity;
    },
    []
  );

  const createPath = useCallback((commands: string) => {
    return new Path2D(commands);
  }, []);

  const drawPath = useCallback(
    (ctx: CanvasRenderingContext2D, path: Path2D, style: PathStyle = {}) => {
      const { fillRule } = { ...DEFAULT_STYLE, ...style };

      ctx.save();
      setPathStyle(ctx, style);

      if (style.fillStyle) {
        ctx.fill(path, fillRule);
      }
      if (style.strokeStyle) {
        ctx.stroke(path);
      }

      ctx.restore();
    },
    [setPathStyle]
  );

  const isPointInPath = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      path: Path2D,
      x: number,
      y: number,
      fillRule: 'nonzero' | 'evenodd' = 'nonzero'
    ) => {
      return ctx.isPointInPath(path, x, y, fillRule);
    },
    []
  );

  const isPointInStroke = useCallback(
    (ctx: CanvasRenderingContext2D, path: Path2D, x: number, y: number) => {
      return ctx.isPointInStroke(path, x, y);
    },
    []
  );

  const combinePaths = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      paths: Array<{ path: Path2D; operation: GlobalCompositeOperation }>,
      style: PathStyle = {}
    ) => {
      ctx.save();
      setPathStyle(ctx, style);

      const resultPath = new Path2D();

      paths.forEach(({ path, operation }) => {
        ctx.globalCompositeOperation = operation;
        ctx.fill(path);
      });

      ctx.restore();
      return resultPath;
    },
    [setPathStyle]
  );

  const createRoundedRectPath = useCallback(
    (
      x: number,
      y: number,
      width: number,
      height: number,
      radius: number | { tl: number; tr: number; br: number; bl: number }
    ) => {
      const path = new Path2D();
      const r =
        typeof radius === 'number'
          ? { tl: radius, tr: radius, br: radius, bl: radius }
          : radius;

      path.moveTo(x + r.tl, y);
      path.lineTo(x + width - r.tr, y);
      path.quadraticCurveTo(x + width, y, x + width, y + r.tr);
      path.lineTo(x + width, y + height - r.br);
      path.quadraticCurveTo(
        x + width,
        y + height,
        x + width - r.br,
        y + height
      );
      path.lineTo(x + r.bl, y + height);
      path.quadraticCurveTo(x, y + height, x, y + height - r.bl);
      path.lineTo(x, y + r.tl);
      path.quadraticCurveTo(x, y, x + r.tl, y);
      path.closePath();

      return path;
    },
    []
  );

  const createStarPath = useCallback(
    (
      x: number,
      y: number,
      outerRadius: number,
      innerRadius: number,
      points: number,
      rotation = 0
    ) => {
      const path = new Path2D();
      const angle = Math.PI / points;

      path.moveTo(
        x + outerRadius * Math.cos(rotation),
        y + outerRadius * Math.sin(rotation)
      );

      for (let i = 1; i < points * 2; i++) {
        const radius = i % 2 === 0 ? outerRadius : innerRadius;
        const currentAngle = angle * i + rotation;
        path.lineTo(
          x + radius * Math.cos(currentAngle),
          y + radius * Math.sin(currentAngle)
        );
      }

      path.closePath();
      return path;
    },
    []
  );

  const createRegularPolygonPath = useCallback(
    (x: number, y: number, radius: number, sides: number, rotation = 0) => {
      const path = new Path2D();
      const angle = (Math.PI * 2) / sides;

      path.moveTo(
        x + radius * Math.cos(rotation),
        y + radius * Math.sin(rotation)
      );

      for (let i = 1; i < sides; i++) {
        const currentAngle = angle * i + rotation;
        path.lineTo(
          x + radius * Math.cos(currentAngle),
          y + radius * Math.sin(currentAngle)
        );
      }

      path.closePath();
      return path;
    },
    []
  );

  return {
    setPathStyle,
    createPath,
    drawPath,
    isPointInPath,
    isPointInStroke,
    combinePaths,
    createRoundedRectPath,
    createStarPath,
    createRegularPolygonPath,
  };
};
