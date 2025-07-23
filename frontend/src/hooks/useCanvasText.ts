import { useCallback } from 'react';
import { TextElement } from '../types/editor';

export const useCanvasText = () => {
  // Desenhar texto
  const drawText = useCallback(
    (ctx: CanvasRenderingContext2D, element: TextElement) => {
      const { x, y, text, fontSize, fontFamily, fill } = element;

      ctx.font = `${fontSize}px ${fontFamily}`;
      ctx.fillStyle = fill;
      ctx.textBaseline = 'top';
      ctx.fillText(text, x, y);
    },
    []
  );

  // Medir texto
  const measureText = useCallback(
    (ctx: CanvasRenderingContext2D, element: TextElement) => {
      ctx.font = `${element.fontSize}px ${element.fontFamily}`;
      return ctx.measureText(element.text);
    },
    []
  );

  // Obter bounds do texto
  const getTextBounds = useCallback(
    (ctx: CanvasRenderingContext2D, element: TextElement) => {
      const metrics = measureText(ctx, element);
      return {
        x: element.x,
        y: element.y,
        width: metrics.width,
        height: element.fontSize,
      };
    },
    [measureText]
  );

  // Verificar se um ponto está dentro do texto
  const isPointInText = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      element: TextElement,
      x: number,
      y: number
    ): boolean => {
      const bounds = getTextBounds(ctx, element);
      return (
        x >= bounds.x &&
        x <= bounds.x + bounds.width &&
        y >= bounds.y &&
        y <= bounds.y + bounds.height
      );
    },
    [getTextBounds]
  );

  // Quebrar texto em linhas
  const wrapText = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      element: TextElement,
      maxWidth: number
    ): string[] => {
      const words = element.text.split(' ');
      const lines: string[] = [];
      let currentLine = words[0];

      ctx.font = `${element.fontSize}px ${element.fontFamily}`;

      for (let i = 1; i < words.length; i++) {
        const word = words[i];
        const width = ctx.measureText(currentLine + ' ' + word).width;

        if (width < maxWidth) {
          currentLine += ' ' + word;
        } else {
          lines.push(currentLine);
          currentLine = word;
        }
      }

      lines.push(currentLine);
      return lines;
    },
    []
  );

  // Desenhar texto com quebra de linha
  const drawWrappedText = useCallback(
    (ctx: CanvasRenderingContext2D, element: TextElement, maxWidth: number) => {
      const lines = wrapText(ctx, element, maxWidth);
      const lineHeight = element.fontSize * 1.2;

      ctx.font = `${element.fontSize}px ${element.fontFamily}`;
      ctx.fillStyle = element.fill;
      ctx.textBaseline = 'top';

      lines.forEach((line, index) => {
        ctx.fillText(line, element.x, element.y + index * lineHeight);
      });
    },
    [wrapText]
  );

  // Obter posição do cursor
  const getCursorPosition = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      element: TextElement,
      x: number
    ): number => {
      ctx.font = `${element.fontSize}px ${element.fontFamily}`;

      let totalWidth = 0;
      let cursorIndex = element.text.length;

      for (let i = 0; i < element.text.length; i++) {
        const char = element.text[i];
        const charWidth = ctx.measureText(char).width;

        if (x < element.x + totalWidth + charWidth / 2) {
          cursorIndex = i;
          break;
        }

        totalWidth += charWidth;
      }

      return cursorIndex;
    },
    []
  );

  return {
    drawText,
    measureText,
    getTextBounds,
    isPointInText,
    wrapText,
    drawWrappedText,
    getCursorPosition,
  };
};
