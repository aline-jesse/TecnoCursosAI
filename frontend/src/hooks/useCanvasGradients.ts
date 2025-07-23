import { useCallback } from 'react';

interface GradientStop {
  offset: number;
  color: string;
}

interface LinearGradientConfig {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  stops: GradientStop[];
}

interface RadialGradientConfig {
  x1: number;
  y1: number;
  r1: number;
  x2: number;
  y2: number;
  r2: number;
  stops: GradientStop[];
}

interface ConicGradientConfig {
  x: number;
  y: number;
  angle: number;
  stops: GradientStop[];
}

export const useCanvasGradients = () => {
  // Criar gradiente linear
  const createLinearGradient = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      config: LinearGradientConfig
    ): CanvasGradient => {
      const { x1, y1, x2, y2, stops } = config;
      const gradient = ctx.createLinearGradient(x1, y1, x2, y2);

      stops.forEach(stop => {
        gradient.addColorStop(stop.offset, stop.color);
      });

      return gradient;
    },
    []
  );

  // Criar gradiente radial
  const createRadialGradient = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      config: RadialGradientConfig
    ): CanvasGradient => {
      const { x1, y1, r1, x2, y2, r2, stops } = config;
      const gradient = ctx.createRadialGradient(x1, y1, r1, x2, y2, r2);

      stops.forEach(stop => {
        gradient.addColorStop(stop.offset, stop.color);
      });

      return gradient;
    },
    []
  );

  // Criar gradiente cônico
  const createConicGradient = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      config: ConicGradientConfig
    ): CanvasGradient => {
      const { x, y, angle, stops } = config;
      const gradient = ctx.createConicGradient(angle, x, y);

      stops.forEach(stop => {
        gradient.addColorStop(stop.offset, stop.color);
      });

      return gradient;
    },
    []
  );

  // Aplicar gradiente como preenchimento
  const fillWithGradient = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      gradient: CanvasGradient,
      x: number,
      y: number,
      width: number,
      height: number
    ) => {
      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, width, height);
    },
    []
  );

  // Aplicar gradiente como contorno
  const strokeWithGradient = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      gradient: CanvasGradient,
      x: number,
      y: number,
      width: number,
      height: number
    ) => {
      ctx.strokeStyle = gradient;
      ctx.strokeRect(x, y, width, height);
    },
    []
  );

  // Criar gradiente de texto
  const createTextGradient = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      text: string,
      x: number,
      y: number,
      gradient: CanvasGradient
    ) => {
      ctx.fillStyle = gradient;
      ctx.fillText(text, x, y);
    },
    []
  );

  return {
    createLinearGradient,
    createRadialGradient,
    createConicGradient,
    fillWithGradient,
    strokeWithGradient,
    createTextGradient,
  };
};
