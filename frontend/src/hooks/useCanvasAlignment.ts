import { useCallback, useRef } from 'react';
import { EditorElement } from '../types/editor';

interface Point {
  x: number;
  y: number;
}

interface AlignmentGuide {
  type: 'horizontal' | 'vertical';
  position: number;
  elements: EditorElement[];
}

interface Distribution {
  type: 'horizontal' | 'vertical';
  elements: EditorElement[];
  spacing: number;
}

interface AlignmentState {
  activeGuides: AlignmentGuide[];
  snapDistance: number;
  isEnabled: boolean;
}

interface AlignmentHandlers {
  onAlign?: (elements: EditorElement[], type: string) => void;
  onDistribute?: (elements: EditorElement[], type: string) => void;
  onGuideShow?: (guide: AlignmentGuide) => void;
  onGuideHide?: (guide: AlignmentGuide) => void;
}

interface AlignmentOptions {
  snapDistance?: number;
  showGuides?: boolean;
  guideStyle?: {
    color?: string;
    width?: number;
    opacity?: number;
    dashPattern?: number[];
  };
}

export const useCanvasAlignment = (
  handlers: AlignmentHandlers = {},
  options: AlignmentOptions = {}
) => {
  const {
    snapDistance = 5,
    showGuides = true,
    guideStyle = {
      color: '#0095ff',
      width: 1,
      opacity: 0.5,
      dashPattern: [5, 5],
    },
  } = options;

  const alignmentState = useRef<AlignmentState>({
    activeGuides: [],
    snapDistance,
    isEnabled: true,
  });

  // Calcular limites do elemento
  const getElementBounds = useCallback((element: EditorElement) => {
    return {
      left: element.x,
      right: element.x + element.width,
      top: element.y,
      bottom: element.y + element.height,
      centerX: element.x + element.width / 2,
      centerY: element.y + element.height / 2,
      width: element.width,
      height: element.height,
    };
  }, []);

  // Encontrar guias de alinhamento
  const findAlignmentGuides = useCallback(
    (
      targetElement: EditorElement,
      otherElements: EditorElement[]
    ): AlignmentGuide[] => {
      const guides: AlignmentGuide[] = [];
      const targetBounds = getElementBounds(targetElement);

      otherElements.forEach(element => {
        const bounds = getElementBounds(element);

        // Guias horizontais
        const horizontalGuides = [
          { pos: bounds.top, type: 'top' },
          { pos: bounds.centerY, type: 'center' },
          { pos: bounds.bottom, type: 'bottom' },
        ];

        horizontalGuides.forEach(({ pos, type }) => {
          const distances = [
            Math.abs(pos - targetBounds.top),
            Math.abs(pos - targetBounds.centerY),
            Math.abs(pos - targetBounds.bottom),
          ];

          const minDistance = Math.min(...distances);
          if (minDistance <= alignmentState.current.snapDistance) {
            guides.push({
              type: 'horizontal',
              position: pos,
              elements: [targetElement, element],
            });
          }
        });

        // Guias verticais
        const verticalGuides = [
          { pos: bounds.left, type: 'left' },
          { pos: bounds.centerX, type: 'center' },
          { pos: bounds.right, type: 'right' },
        ];

        verticalGuides.forEach(({ pos, type }) => {
          const distances = [
            Math.abs(pos - targetBounds.left),
            Math.abs(pos - targetBounds.centerX),
            Math.abs(pos - targetBounds.right),
          ];

          const minDistance = Math.min(...distances);
          if (minDistance <= alignmentState.current.snapDistance) {
            guides.push({
              type: 'vertical',
              position: pos,
              elements: [targetElement, element],
            });
          }
        });
      });

      return guides;
    },
    [getElementBounds]
  );

  // Alinhar elementos
  const alignElements = useCallback(
    (
      elements: EditorElement[],
      alignment: 'left' | 'center' | 'right' | 'top' | 'middle' | 'bottom'
    ): EditorElement[] => {
      if (elements.length < 2) return elements;

      const bounds = elements.map(getElementBounds);
      const updatedElements = [...elements];

      switch (alignment) {
        case 'left': {
          const leftmost = Math.min(...bounds.map(b => b.left));
          updatedElements.forEach((element, i) => {
            element.x = leftmost;
          });
          break;
        }
        case 'center': {
          const center =
            bounds.reduce((sum, b) => sum + b.centerX, 0) / bounds.length;
          updatedElements.forEach((element, i) => {
            element.x = center - element.width / 2;
          });
          break;
        }
        case 'right': {
          const rightmost = Math.max(...bounds.map(b => b.right));
          updatedElements.forEach((element, i) => {
            element.x = rightmost - element.width;
          });
          break;
        }
        case 'top': {
          const topmost = Math.min(...bounds.map(b => b.top));
          updatedElements.forEach((element, i) => {
            element.y = topmost;
          });
          break;
        }
        case 'middle': {
          const middle =
            bounds.reduce((sum, b) => sum + b.centerY, 0) / bounds.length;
          updatedElements.forEach((element, i) => {
            element.y = middle - element.height / 2;
          });
          break;
        }
        case 'bottom': {
          const bottommost = Math.max(...bounds.map(b => b.bottom));
          updatedElements.forEach((element, i) => {
            element.y = bottommost - element.height;
          });
          break;
        }
      }

      handlers.onAlign?.(updatedElements, alignment);
      return updatedElements;
    },
    [getElementBounds, handlers]
  );

  // Distribuir elementos
  const distributeElements = useCallback(
    (
      elements: EditorElement[],
      distribution: 'horizontal' | 'vertical'
    ): EditorElement[] => {
      if (elements.length < 3) return elements;

      const bounds = elements.map(getElementBounds);
      const updatedElements = [...elements];

      if (distribution === 'horizontal') {
        // Ordenar por posição x
        const sorted = updatedElements
          .map((element, index) => ({ element, bounds: bounds[index] }))
          .sort((a, b) => a.bounds.centerX - b.bounds.centerX);

        const totalWidth =
          sorted[sorted.length - 1].bounds.right - sorted[0].bounds.left;
        const totalGaps = sorted.length - 1;
        const spacing =
          (totalWidth -
            sorted.reduce((sum, { bounds }) => sum + bounds.width, 0)) /
          totalGaps;

        let currentX = sorted[0].bounds.left;
        sorted.forEach(({ element, bounds }, i) => {
          element.x = currentX;
          currentX += bounds.width + spacing;
        });
      } else {
        // Ordenar por posição y
        const sorted = updatedElements
          .map((element, index) => ({ element, bounds: bounds[index] }))
          .sort((a, b) => a.bounds.centerY - b.bounds.centerY);

        const totalHeight =
          sorted[sorted.length - 1].bounds.bottom - sorted[0].bounds.top;
        const totalGaps = sorted.length - 1;
        const spacing =
          (totalHeight -
            sorted.reduce((sum, { bounds }) => sum + bounds.height, 0)) /
          totalGaps;

        let currentY = sorted[0].bounds.top;
        sorted.forEach(({ element, bounds }, i) => {
          element.y = currentY;
          currentY += bounds.height + spacing;
        });
      }

      handlers.onDistribute?.(updatedElements, distribution);
      return updatedElements;
    },
    [getElementBounds, handlers]
  );

  // Desenhar guias de alinhamento
  const drawAlignmentGuides = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      if (!showGuides || !alignmentState.current.isEnabled) return;

      const { activeGuides } = alignmentState.current;
      const { color, width: lineWidth, opacity, dashPattern } = guideStyle;

      ctx.save();
      ctx.strokeStyle = color!;
      ctx.lineWidth = lineWidth!;
      ctx.globalAlpha = opacity!;
      ctx.setLineDash(dashPattern!);

      activeGuides.forEach(guide => {
        ctx.beginPath();
        if (guide.type === 'horizontal') {
          ctx.moveTo(0, guide.position);
          ctx.lineTo(width, guide.position);
        } else {
          ctx.moveTo(guide.position, 0);
          ctx.lineTo(guide.position, height);
        }
        ctx.stroke();
      });

      ctx.restore();
    },
    [showGuides, guideStyle]
  );

  // Ativar/desativar alinhamento
  const setAlignmentEnabled = useCallback((enabled: boolean) => {
    alignmentState.current.isEnabled = enabled;
  }, []);

  // Definir distância de snap
  const setSnapDistance = useCallback((distance: number) => {
    alignmentState.current.snapDistance = distance;
  }, []);

  // Limpar guias ativas
  const clearActiveGuides = useCallback(() => {
    alignmentState.current.activeGuides.forEach(guide => {
      handlers.onGuideHide?.(guide);
    });
    alignmentState.current.activeGuides = [];
  }, [handlers]);

  return {
    alignElements,
    distributeElements,
    findAlignmentGuides,
    drawAlignmentGuides,
    setAlignmentEnabled,
    setSnapDistance,
    clearActiveGuides,
  };
};
