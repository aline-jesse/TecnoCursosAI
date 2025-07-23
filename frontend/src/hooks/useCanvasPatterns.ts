import { useCallback, useRef } from 'react';

interface PatternCache {
  [key: string]: CanvasPattern | null;
}

interface PatternConfig {
  image: HTMLImageElement;
  repetition?: 'repeat' | 'repeat-x' | 'repeat-y' | 'no-repeat';
  transform?: DOMMatrix;
}

export const useCanvasPatterns = () => {
  const patternCache = useRef<PatternCache>({});

  // Criar padrão
  const createPattern = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      config: PatternConfig
    ): CanvasPattern | null => {
      const { image, repetition = 'repeat', transform } = config;
      const cacheKey = `${image.src}_${repetition}`;

      // Verificar cache
      if (patternCache.current[cacheKey]) {
        return patternCache.current[cacheKey];
      }

      // Criar novo padrão
      const pattern = ctx.createPattern(image, repetition);
      if (pattern && transform) {
        pattern.setTransform(transform);
      }

      patternCache.current[cacheKey] = pattern;
      return pattern;
    },
    []
  );

  // Desenhar retângulo com padrão
  const drawRectWithPattern = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      width: number,
      height: number,
      pattern: CanvasPattern
    ) => {
      ctx.save();
      ctx.fillStyle = pattern;
      ctx.fillRect(x, y, width, height);
      ctx.restore();
    },
    []
  );

  // Desenhar caminho com padrão
  const drawPathWithPattern = useCallback(
    (ctx: CanvasRenderingContext2D, path: Path2D, pattern: CanvasPattern) => {
      ctx.save();
      ctx.fillStyle = pattern;
      ctx.fill(path);
      ctx.restore();
    },
    []
  );

  // Criar padrão xadrez
  const createCheckerPattern = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      size: number,
      color1: string,
      color2: string
    ): CanvasPattern | null => {
      // Criar canvas temporário para o padrão
      const patternCanvas = document.createElement('canvas');
      patternCanvas.width = size * 2;
      patternCanvas.height = size * 2;

      const patternCtx = patternCanvas.getContext('2d');
      if (!patternCtx) return null;

      // Desenhar quadrados
      patternCtx.fillStyle = color1;
      patternCtx.fillRect(0, 0, size * 2, size * 2);

      patternCtx.fillStyle = color2;
      patternCtx.fillRect(0, 0, size, size);
      patternCtx.fillRect(size, size, size, size);

      // Criar e retornar padrão
      return ctx.createPattern(patternCanvas, 'repeat');
    },
    []
  );

  // Criar padrão de linhas
  const createLinePattern = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      size: number,
      color: string,
      angle = 45
    ): CanvasPattern | null => {
      // Criar canvas temporário para o padrão
      const patternCanvas = document.createElement('canvas');
      patternCanvas.width = size * 2;
      patternCanvas.height = size * 2;

      const patternCtx = patternCanvas.getContext('2d');
      if (!patternCtx) return null;

      // Configurar linha
      patternCtx.strokeStyle = color;
      patternCtx.lineWidth = 1;

      // Desenhar linha
      patternCtx.save();
      patternCtx.translate(size, size);
      patternCtx.rotate((angle * Math.PI) / 180);
      patternCtx.beginPath();
      patternCtx.moveTo(-size * 2, 0);
      patternCtx.lineTo(size * 2, 0);
      patternCtx.stroke();
      patternCtx.restore();

      // Criar e retornar padrão
      return ctx.createPattern(patternCanvas, 'repeat');
    },
    []
  );

  // Criar padrão de pontos
  const createDotPattern = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      size: number,
      dotSize: number,
      color: string
    ): CanvasPattern | null => {
      // Criar canvas temporário para o padrão
      const patternCanvas = document.createElement('canvas');
      patternCanvas.width = size;
      patternCanvas.height = size;

      const patternCtx = patternCanvas.getContext('2d');
      if (!patternCtx) return null;

      // Desenhar ponto
      patternCtx.fillStyle = color;
      patternCtx.beginPath();
      patternCtx.arc(size / 2, size / 2, dotSize / 2, 0, Math.PI * 2);
      patternCtx.fill();

      // Criar e retornar padrão
      return ctx.createPattern(patternCanvas, 'repeat');
    },
    []
  );

  // Limpar cache
  const clearCache = useCallback(() => {
    patternCache.current = {};
  }, []);

  return {
    createPattern,
    drawRectWithPattern,
    drawPathWithPattern,
    createCheckerPattern,
    createLinePattern,
    createDotPattern,
    clearCache,
  };
};
