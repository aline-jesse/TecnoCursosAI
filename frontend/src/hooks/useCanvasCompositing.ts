import { useCallback } from 'react';

type GlobalCompositeOperation =
  | 'source-over'
  | 'source-in'
  | 'source-out'
  | 'source-atop'
  | 'destination-over'
  | 'destination-in'
  | 'destination-out'
  | 'destination-atop'
  | 'lighter'
  | 'copy'
  | 'xor'
  | 'multiply'
  | 'screen'
  | 'overlay'
  | 'darken'
  | 'lighten'
  | 'color-dodge'
  | 'color-burn'
  | 'hard-light'
  | 'soft-light'
  | 'difference'
  | 'exclusion'
  | 'hue'
  | 'saturation'
  | 'color'
  | 'luminosity';

interface CompositingOptions {
  operation?: GlobalCompositeOperation;
  opacity?: number;
}

const DEFAULT_OPTIONS: Required<CompositingOptions> = {
  operation: 'source-over',
  opacity: 1,
};

export const useCanvasCompositing = () => {
  const setCompositing = useCallback(
    (ctx: CanvasRenderingContext2D, options: CompositingOptions = {}) => {
      const { operation, opacity } = { ...DEFAULT_OPTIONS, ...options };
      ctx.globalCompositeOperation = operation;
      ctx.globalAlpha = opacity;
    },
    []
  );

  const clearCompositing = useCallback((ctx: CanvasRenderingContext2D) => {
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
  }, []);

  const withCompositing = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      callback: () => void,
      options: CompositingOptions = {}
    ) => {
      ctx.save();
      setCompositing(ctx, options);
      callback();
      ctx.restore();
    },
    [setCompositing]
  );

  const drawImageWithCompositing = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      image: CanvasImageSource,
      x: number,
      y: number,
      width?: number,
      height?: number,
      options: CompositingOptions = {}
    ) => {
      withCompositing(
        ctx,
        () => {
          if (width !== undefined && height !== undefined) {
            ctx.drawImage(image, x, y, width, height);
          } else {
            ctx.drawImage(image, x, y);
          }
        },
        options
      );
    },
    [withCompositing]
  );

  const drawRectWithCompositing = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      width: number,
      height: number,
      options: CompositingOptions = {}
    ) => {
      withCompositing(
        ctx,
        () => {
          ctx.fillRect(x, y, width, height);
        },
        options
      );
    },
    [withCompositing]
  );

  const drawPathWithCompositing = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      path: Path2D,
      options: CompositingOptions = {}
    ) => {
      withCompositing(
        ctx,
        () => {
          ctx.fill(path);
        },
        options
      );
    },
    [withCompositing]
  );

  const blendLayers = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      layers: Array<{
        canvas: HTMLCanvasElement;
        options?: CompositingOptions;
      }>
    ) => {
      layers.forEach(({ canvas, options = {} }) => {
        drawImageWithCompositing(
          ctx,
          canvas,
          0,
          0,
          undefined,
          undefined,
          options
        );
      });
    },
    [drawImageWithCompositing]
  );

  const createMask = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      mask: HTMLCanvasElement | ((ctx: CanvasRenderingContext2D) => void),
      content: HTMLCanvasElement | ((ctx: CanvasRenderingContext2D) => void)
    ) => {
      // Desenhar máscara
      withCompositing(
        ctx,
        () => {
          if (mask instanceof HTMLCanvasElement) {
            ctx.drawImage(mask, 0, 0);
          } else {
            mask(ctx);
          }
        },
        { operation: 'destination-in' }
      );

      // Desenhar conteúdo
      withCompositing(ctx, () => {
        if (content instanceof HTMLCanvasElement) {
          ctx.drawImage(content, 0, 0);
        } else {
          content(ctx);
        }
      });
    },
    [withCompositing]
  );

  const createLightingEffect = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      radius: number,
      color: string
    ) => {
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      gradient.addColorStop(0, color);
      gradient.addColorStop(1, 'transparent');

      withCompositing(
        ctx,
        () => {
          ctx.fillStyle = gradient;
          ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
        },
        { operation: 'lighter' }
      );
    },
    [withCompositing]
  );

  const createShadowEffect = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      blur: number,
      color: string
    ) => {
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, blur);
      gradient.addColorStop(0, color);
      gradient.addColorStop(1, 'transparent');

      withCompositing(
        ctx,
        () => {
          ctx.fillStyle = gradient;
          ctx.fillRect(x - blur, y - blur, blur * 2, blur * 2);
        },
        { operation: 'destination-over' }
      );
    },
    [withCompositing]
  );

  const createGlowEffect = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      radius: number,
      color: string,
      intensity = 0.5
    ) => {
      const steps = 5;
      const stepRadius = radius / steps;

      for (let i = 0; i < steps; i++) {
        const currentRadius = stepRadius * (i + 1);
        const alpha = (1 - i / steps) * intensity;

        withCompositing(
          ctx,
          () => {
            const gradient = ctx.createRadialGradient(
              x,
              y,
              0,
              x,
              y,
              currentRadius
            );
            gradient.addColorStop(
              0,
              `${color}${Math.round(alpha * 255)
                .toString(16)
                .padStart(2, '0')}`
            );
            gradient.addColorStop(1, `${color}00`);

            ctx.fillStyle = gradient;
            ctx.fillRect(
              x - currentRadius,
              y - currentRadius,
              currentRadius * 2,
              currentRadius * 2
            );
          },
          { operation: 'lighter' }
        );
      }
    },
    [withCompositing]
  );

  return {
    setCompositing,
    clearCompositing,
    withCompositing,
    drawImageWithCompositing,
    drawRectWithCompositing,
    drawPathWithCompositing,
    blendLayers,
    createMask,
    createLightingEffect,
    createShadowEffect,
    createGlowEffect,
  };
};
