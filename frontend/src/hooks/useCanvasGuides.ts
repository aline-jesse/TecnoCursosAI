import { useCallback, useRef } from 'react';
import { EditorElement } from '../types/editor';

interface Point {
  x: number;
  y: number;
}

interface Guide {
  position: number;
  type: 'horizontal' | 'vertical';
  isTemporary?: boolean;
}

interface GuidesState {
  horizontalGuides: number[];
  verticalGuides: number[];
  temporaryGuides: Guide[];
  activeGuides: Guide[];
  snapDistance: number;
  isVisible: boolean;
}

interface GuideStyle {
  color?: string;
  width?: number;
  opacity?: number;
  dashPattern?: number[];
}

interface GuidesHandlers {
  onGuideAdd?: (guide: Guide) => void;
  onGuideRemove?: (guide: Guide) => void;
  onGuideMove?: (guide: Guide, position: number) => void;
  onSnap?: (element: EditorElement, guides: Guide[]) => void;
}

interface GuidesOptions {
  snapDistance?: number;
  showCenterGuides?: boolean;
  showDistanceLabels?: boolean;
  showAngleGuides?: boolean;
}

export const useCanvasGuides = (
  handlers: GuidesHandlers = {},
  options: GuidesOptions = {},
  style: GuideStyle = {}
) => {
  const {
    snapDistance = 5,
    showCenterGuides = true,
    showDistanceLabels = true,
    showAngleGuides = true,
  } = options;

  const {
    color = '#0095ff',
    width = 1,
    opacity = 0.5,
    dashPattern = [5, 5],
  } = style;

  const guidesState = useRef<GuidesState>({
    horizontalGuides: [],
    verticalGuides: [],
    temporaryGuides: [],
    activeGuides: [],
    snapDistance,
    isVisible: true,
  });

  // Adicionar guia
  const addGuide = useCallback(
    (guide: Guide) => {
      const { horizontalGuides, verticalGuides } = guidesState.current;

      if (guide.type === 'horizontal') {
        if (!horizontalGuides.includes(guide.position)) {
          guidesState.current.horizontalGuides = [
            ...horizontalGuides,
            guide.position,
          ].sort((a, b) => a - b);
        }
      } else {
        if (!verticalGuides.includes(guide.position)) {
          guidesState.current.verticalGuides = [
            ...verticalGuides,
            guide.position,
          ].sort((a, b) => a - b);
        }
      }

      handlers.onGuideAdd?.(guide);
    },
    [handlers]
  );

  // Remover guia
  const removeGuide = useCallback(
    (guide: Guide) => {
      const { horizontalGuides, verticalGuides } = guidesState.current;

      if (guide.type === 'horizontal') {
        guidesState.current.horizontalGuides = horizontalGuides.filter(
          pos => pos !== guide.position
        );
      } else {
        guidesState.current.verticalGuides = verticalGuides.filter(
          pos => pos !== guide.position
        );
      }

      handlers.onGuideRemove?.(guide);
    },
    [handlers]
  );

  // Mover guia
  const moveGuide = useCallback(
    (guide: Guide, newPosition: number) => {
      const { horizontalGuides, verticalGuides } = guidesState.current;

      if (guide.type === 'horizontal') {
        const index = horizontalGuides.indexOf(guide.position);
        if (index !== -1) {
          const newGuides = [...horizontalGuides];
          newGuides[index] = newPosition;
          guidesState.current.horizontalGuides = newGuides.sort(
            (a, b) => a - b
          );
        }
      } else {
        const index = verticalGuides.indexOf(guide.position);
        if (index !== -1) {
          const newGuides = [...verticalGuides];
          newGuides[index] = newPosition;
          guidesState.current.verticalGuides = newGuides.sort((a, b) => a - b);
        }
      }

      handlers.onGuideMove?.(guide, newPosition);
    },
    [handlers]
  );

  // Adicionar guia temporária
  const addTemporaryGuide = useCallback((guide: Guide) => {
    guidesState.current.temporaryGuides = [
      ...guidesState.current.temporaryGuides,
      { ...guide, isTemporary: true },
    ];
  }, []);

  // Limpar guias temporárias
  const clearTemporaryGuides = useCallback(() => {
    guidesState.current.temporaryGuides = [];
  }, []);

  // Encontrar guias próximas
  const findNearbyGuides = useCallback((element: EditorElement): Guide[] => {
    const { horizontalGuides, verticalGuides, temporaryGuides, snapDistance } =
      guidesState.current;

    const nearbyGuides: Guide[] = [];

    // Pontos do elemento
    const elementPoints = {
      left: element.x,
      center: element.x + element.width / 2,
      right: element.x + element.width,
      top: element.y,
      middle: element.y + element.height / 2,
      bottom: element.y + element.height,
    };

    // Verificar guias horizontais
    [
      ...horizontalGuides,
      ...temporaryGuides
        .filter(g => g.type === 'horizontal')
        .map(g => g.position),
    ].forEach(position => {
      if (
        Math.abs(position - elementPoints.top) <= snapDistance ||
        Math.abs(position - elementPoints.middle) <= snapDistance ||
        Math.abs(position - elementPoints.bottom) <= snapDistance
      ) {
        nearbyGuides.push({
          position,
          type: 'horizontal',
        });
      }
    });

    // Verificar guias verticais
    [
      ...verticalGuides,
      ...temporaryGuides
        .filter(g => g.type === 'vertical')
        .map(g => g.position),
    ].forEach(position => {
      if (
        Math.abs(position - elementPoints.left) <= snapDistance ||
        Math.abs(position - elementPoints.center) <= snapDistance ||
        Math.abs(position - elementPoints.right) <= snapDistance
      ) {
        nearbyGuides.push({
          position,
          type: 'vertical',
        });
      }
    });

    return nearbyGuides;
  }, []);

  // Snap elemento para guias
  const snapElementToGuides = useCallback(
    (element: EditorElement): EditorElement => {
      const nearbyGuides = findNearbyGuides(element);
      if (nearbyGuides.length === 0) return element;

      let newX = element.x;
      let newY = element.y;

      // Pontos do elemento
      const elementPoints = {
        left: element.x,
        center: element.x + element.width / 2,
        right: element.x + element.width,
        top: element.y,
        middle: element.y + element.height / 2,
        bottom: element.y + element.height,
      };

      // Snap para guias horizontais
      nearbyGuides
        .filter(guide => guide.type === 'horizontal')
        .forEach(guide => {
          const { position } = guide;
          const topDiff = Math.abs(position - elementPoints.top);
          const middleDiff = Math.abs(position - elementPoints.middle);
          const bottomDiff = Math.abs(position - elementPoints.bottom);

          if (topDiff <= guidesState.current.snapDistance) {
            newY = position;
          } else if (middleDiff <= guidesState.current.snapDistance) {
            newY = position - element.height / 2;
          } else if (bottomDiff <= guidesState.current.snapDistance) {
            newY = position - element.height;
          }
        });

      // Snap para guias verticais
      nearbyGuides
        .filter(guide => guide.type === 'vertical')
        .forEach(guide => {
          const { position } = guide;
          const leftDiff = Math.abs(position - elementPoints.left);
          const centerDiff = Math.abs(position - elementPoints.center);
          const rightDiff = Math.abs(position - elementPoints.right);

          if (leftDiff <= guidesState.current.snapDistance) {
            newX = position;
          } else if (centerDiff <= guidesState.current.snapDistance) {
            newX = position - element.width / 2;
          } else if (rightDiff <= guidesState.current.snapDistance) {
            newX = position - element.width;
          }
        });

      const snappedElement = {
        ...element,
        x: newX,
        y: newY,
      };

      handlers.onSnap?.(snappedElement, nearbyGuides);
      guidesState.current.activeGuides = nearbyGuides;

      return snappedElement;
    },
    [findNearbyGuides, handlers]
  );

  // Desenhar guias
  const drawGuides = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      if (!guidesState.current.isVisible) return;

      const {
        horizontalGuides,
        verticalGuides,
        temporaryGuides,
        activeGuides,
      } = guidesState.current;

      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.globalAlpha = opacity;
      ctx.setLineDash(dashPattern);

      // Desenhar guias horizontais
      [
        ...horizontalGuides,
        ...temporaryGuides
          .filter(g => g.type === 'horizontal')
          .map(g => g.position),
      ].forEach(position => {
        const isActive = activeGuides.some(
          g => g.type === 'horizontal' && g.position === position
        );

        if (isActive) {
          ctx.strokeStyle = '#00ff00';
          ctx.lineWidth = width * 2;
        }

        ctx.beginPath();
        ctx.moveTo(0, position);
        ctx.lineTo(width, position);
        ctx.stroke();

        if (isActive) {
          ctx.strokeStyle = color;
          ctx.lineWidth = width;
        }
      });

      // Desenhar guias verticais
      [
        ...verticalGuides,
        ...temporaryGuides
          .filter(g => g.type === 'vertical')
          .map(g => g.position),
      ].forEach(position => {
        const isActive = activeGuides.some(
          g => g.type === 'vertical' && g.position === position
        );

        if (isActive) {
          ctx.strokeStyle = '#00ff00';
          ctx.lineWidth = width * 2;
        }

        ctx.beginPath();
        ctx.moveTo(position, 0);
        ctx.lineTo(position, height);
        ctx.stroke();

        if (isActive) {
          ctx.strokeStyle = color;
          ctx.lineWidth = width;
        }
      });

      ctx.restore();
    },
    [color, width, opacity, dashPattern]
  );

  // Mostrar/ocultar guias
  const setGuidesVisible = useCallback((visible: boolean) => {
    guidesState.current.isVisible = visible;
  }, []);

  // Definir distância de snap
  const setSnapDistance = useCallback((distance: number) => {
    guidesState.current.snapDistance = distance;
  }, []);

  // Limpar todas as guias
  const clearGuides = useCallback(() => {
    guidesState.current.horizontalGuides = [];
    guidesState.current.verticalGuides = [];
    guidesState.current.temporaryGuides = [];
    guidesState.current.activeGuides = [];
  }, []);

  // Obter estado das guias
  const getGuidesState = useCallback(() => {
    return { ...guidesState.current };
  }, []);

  return {
    addGuide,
    removeGuide,
    moveGuide,
    addTemporaryGuide,
    clearTemporaryGuides,
    snapElementToGuides,
    drawGuides,
    setGuidesVisible,
    setSnapDistance,
    clearGuides,
    getGuidesState,
  };
};
