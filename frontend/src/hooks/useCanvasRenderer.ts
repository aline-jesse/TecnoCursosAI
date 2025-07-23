import { useCallback, useEffect, useRef } from 'react';
import { EditorElement } from '../types/editor';

interface RenderOptions {
  skipCache?: boolean;
  forceRedraw?: boolean;
  updateLayers?: string[];
  quality?: 'low' | 'medium' | 'high';
}

interface RenderState {
  isRendering: boolean;
  lastRenderTime: number;
  frameCount: number;
  renderQueue: Array<() => void>;
}

interface ElementCache {
  [key: string]: {
    image?: HTMLImageElement;
    pattern?: CanvasPattern;
    gradient?: CanvasGradient;
    path?: Path2D;
    lastUpdate: number;
  };
}

interface RenderHandlers {
  onBeforeRender?: () => void;
  onAfterRender?: () => void;
  onRenderError?: (error: Error) => void;
}

interface RenderMetrics {
  fps: number;
  renderTime: number;
  elementCount: number;
  cacheSize: number;
}

export const useCanvasRenderer = (handlers: RenderHandlers = {}) => {
  const renderState = useRef<RenderState>({
    isRendering: false,
    lastRenderTime: 0,
    frameCount: 0,
    renderQueue: [],
  });

  const elementCache = useRef<ElementCache>({});
  const metricsInterval = useRef<number | null>(null);
  const metrics = useRef<RenderMetrics>({
    fps: 0,
    renderTime: 0,
    elementCount: 0,
    cacheSize: 0,
  });

  // Limpar cache
  const clearCache = useCallback(() => {
    elementCache.current = {};
  }, []);

  // Verificar se elemento está em cache
  const isElementCached = useCallback((element: EditorElement): boolean => {
    const cacheKey = `${element.id}-${element.type}`;
    return !!elementCache.current[cacheKey];
  }, []);

  // Obter elemento do cache
  const getCachedElement = useCallback((element: EditorElement) => {
    const cacheKey = `${element.id}-${element.type}`;
    return elementCache.current[cacheKey];
  }, []);

  // Adicionar elemento ao cache
  const cacheElement = useCallback(
    (element: EditorElement, cacheData: Partial<ElementCache[string]>) => {
      const cacheKey = `${element.id}-${element.type}`;
      elementCache.current[cacheKey] = {
        ...cacheData,
        lastUpdate: Date.now(),
      };
    },
    []
  );

  // Renderizar elemento
  const renderElement = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      element: EditorElement,
      options: RenderOptions = {}
    ) => {
      const { skipCache = false, quality = 'high' } = options;

      // Configurar qualidade de renderização
      ctx.imageSmoothingEnabled = quality !== 'low';
      ctx.imageSmoothingQuality = quality;

      // Verificar cache
      if (!skipCache && isElementCached(element)) {
        const cached = getCachedElement(element);
        if (cached.image) {
          ctx.drawImage(
            cached.image,
            element.x,
            element.y,
            element.width,
            element.height
          );
          return;
        }
      }

      // Renderizar elemento baseado no tipo
      ctx.save();
      ctx.translate(element.x, element.y);
      if (element.rotation) {
        ctx.rotate((element.rotation * Math.PI) / 180);
      }
      if (element.scaleX || element.scaleY) {
        ctx.scale(element.scaleX || 1, element.scaleY || 1);
      }
      if (element.opacity !== undefined) {
        ctx.globalAlpha = element.opacity;
      }

      switch (element.type) {
        case 'text':
          ctx.font = `${element.fontSize}px ${element.fontFamily}`;
          ctx.fillStyle = element.fill;
          ctx.textAlign = 'left';
          ctx.textBaseline = 'top';
          ctx.fillText(element.text, 0, 0);
          break;

        case 'image':
        case 'character':
          const img = new Image();
          img.src = element.src;
          img.onload = () => {
            ctx.drawImage(img, 0, 0, element.width, element.height);
            if (!skipCache) {
              cacheElement(element, { image: img });
            }
          };
          break;

        case 'shape':
          ctx.fillStyle = element.fill;
          ctx.strokeStyle = element.stroke;
          ctx.lineWidth = element.strokeWidth;

          if (element.shapeType === 'rectangle') {
            ctx.beginPath();
            ctx.rect(0, 0, element.width, element.height);
            ctx.fill();
            ctx.stroke();
          } else if (element.shapeType === 'circle') {
            ctx.beginPath();
            ctx.arc(
              element.width / 2,
              element.height / 2,
              Math.min(element.width, element.height) / 2,
              0,
              Math.PI * 2
            );
            ctx.fill();
            ctx.stroke();
          }
          break;

        case 'video':
          // Implementar renderização de vídeo
          break;

        case 'audio':
          // Implementar visualização de áudio
          break;
      }

      ctx.restore();
    },
    [isElementCached, getCachedElement, cacheElement]
  );

  // Renderizar lista de elementos
  const renderElements = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      elements: EditorElement[],
      options: RenderOptions = {}
    ) => {
      const startTime = performance.now();

      try {
        handlers.onBeforeRender?.();

        // Limpar canvas
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        // Renderizar elementos
        elements.forEach(element => {
          renderElement(ctx, element, options);
        });

        // Atualizar métricas
        const endTime = performance.now();
        metrics.current = {
          ...metrics.current,
          renderTime: endTime - startTime,
          elementCount: elements.length,
          cacheSize: Object.keys(elementCache.current).length,
        };

        handlers.onAfterRender?.();
      } catch (error) {
        handlers.onRenderError?.(error as Error);
      }

      // Atualizar estado de renderização
      renderState.current.lastRenderTime = performance.now() - startTime;
      renderState.current.frameCount++;
    },
    [renderElement, handlers]
  );

  // Agendar renderização
  const scheduleRender = useCallback((renderCallback: () => void) => {
    renderState.current.renderQueue.push(renderCallback);

    if (!renderState.current.isRendering) {
      const processQueue = () => {
        if (renderState.current.renderQueue.length > 0) {
          renderState.current.isRendering = true;
          const nextRender = renderState.current.renderQueue.shift();
          nextRender?.();
          requestAnimationFrame(processQueue);
        } else {
          renderState.current.isRendering = false;
        }
      };

      requestAnimationFrame(processQueue);
    }
  }, []);

  // Atualizar métricas periodicamente
  useEffect(() => {
    metricsInterval.current = window.setInterval(() => {
      const now = performance.now();
      const elapsed = now - renderState.current.lastRenderTime;
      metrics.current.fps = 1000 / elapsed;
    }, 1000);

    return () => {
      if (metricsInterval.current !== null) {
        clearInterval(metricsInterval.current);
      }
    };
  }, []);

  // Limpar estado ao desmontar
  useEffect(() => {
    return () => {
      renderState.current.renderQueue = [];
      renderState.current.isRendering = false;
      clearCache();
    };
  }, [clearCache]);

  return {
    renderElement,
    renderElements,
    scheduleRender,
    clearCache,
    getRenderState: () => ({
      lastRenderTime: renderState.current.lastRenderTime,
      frameCount: renderState.current.frameCount,
      queueLength: renderState.current.renderQueue.length,
      isRendering: renderState.current.isRendering,
    }),
    getMetrics: () => ({ ...metrics.current }),
  };
};
