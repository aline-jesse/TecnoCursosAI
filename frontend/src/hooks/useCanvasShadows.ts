import { useCallback } from 'react';

interface ShadowConfig {
  color: string;
  blur: number;
  offsetX: number;
  offsetY: number;
}

export const useCanvasShadows = () => {
  // Aplicar sombra
  const setShadow = useCallback(
    (ctx: CanvasRenderingContext2D, config: ShadowConfig) => {
      const { color, blur, offsetX, offsetY } = config;
      ctx.shadowColor = color;
      ctx.shadowBlur = blur;
      ctx.shadowOffsetX = offsetX;
      ctx.shadowOffsetY = offsetY;
    },
    []
  );

  // Limpar sombra
  const clearShadow = useCallback((ctx: CanvasRenderingContext2D) => {
    ctx.shadowColor = 'rgba(0, 0, 0, 0)';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
  }, []);

  // Desenhar retângulo com sombra
  const drawRectWithShadow = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      width: number,
      height: number,
      shadow: ShadowConfig
    ) => {
      ctx.save();
      setShadow(ctx, shadow);
      ctx.fillRect(x, y, width, height);
      ctx.restore();
    },
    [setShadow]
  );

  // Desenhar texto com sombra
  const drawTextWithShadow = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      text: string,
      x: number,
      y: number,
      shadow: ShadowConfig
    ) => {
      ctx.save();
      setShadow(ctx, shadow);
      ctx.fillText(text, x, y);
      ctx.restore();
    },
    [setShadow]
  );

  // Desenhar imagem com sombra
  const drawImageWithShadow = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      image: HTMLImageElement,
      x: number,
      y: number,
      width: number,
      height: number,
      shadow: ShadowConfig
    ) => {
      ctx.save();
      setShadow(ctx, shadow);
      ctx.drawImage(image, x, y, width, height);
      ctx.restore();
    },
    [setShadow]
  );

  // Desenhar caminho com sombra
  const drawPathWithShadow = useCallback(
    (ctx: CanvasRenderingContext2D, path: Path2D, shadow: ShadowConfig) => {
      ctx.save();
      setShadow(ctx, shadow);
      ctx.fill(path);
      ctx.restore();
    },
    [setShadow]
  );

  // Criar sombra interna
  const createInnerShadow = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      width: number,
      height: number,
      shadow: ShadowConfig
    ) => {
      ctx.save();

      // Criar máscara para sombra interna
      ctx.beginPath();
      ctx.rect(x, y, width, height);
      ctx.clip();

      // Desenhar sombra
      ctx.shadowColor = shadow.color;
      ctx.shadowBlur = shadow.blur;
      ctx.shadowOffsetX = shadow.offsetX;
      ctx.shadowOffsetY = shadow.offsetY;

      // Desenhar retângulo maior que o clipping path
      ctx.fillStyle = 'black';
      ctx.fillRect(x - width, y - height, width * 3, height * 3);

      ctx.restore();
    },
    []
  );

  return {
    setShadow,
    clearShadow,
    drawRectWithShadow,
    drawTextWithShadow,
    drawImageWithShadow,
    drawPathWithShadow,
    createInnerShadow,
  };
};
