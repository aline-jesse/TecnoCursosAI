import { useCallback, useRef } from 'react';

interface ZoomConfig {
  minZoom: number;
  maxZoom: number;
  zoomStep: number;
  zoomSpeed: number;
  smoothZoom: boolean;
  zoomDuration: number;
}

interface ZoomState {
  scale: number;
  offsetX: number;
  offsetY: number;
}

export const useCanvasZoom = () => {
  const configRef = useRef<ZoomConfig>({
    minZoom: 0.1,
    maxZoom: 5,
    zoomStep: 0.1,
    zoomSpeed: 1,
    smoothZoom: true,
    zoomDuration: 300,
  });

  const stateRef = useRef<ZoomState>({
    scale: 1,
    offsetX: 0,
    offsetY: 0,
  });

  // Aplicar zoom
  const applyZoom = useCallback(
    (ctx: CanvasRenderingContext2D, scale: number, x: number, y: number) => {
      const { minZoom, maxZoom } = configRef.current;
      const newScale = Math.min(Math.max(scale, minZoom), maxZoom);

      // Calcular novo offset para manter o ponto de zoom fixo
      const state = stateRef.current;
      const factor = newScale / state.scale;

      state.offsetX = x - (x - state.offsetX) * factor;
      state.offsetY = y - (y - state.offsetY) * factor;
      state.scale = newScale;

      // Aplicar transformação
      ctx.setTransform(newScale, 0, 0, newScale, state.offsetX, state.offsetY);
    },
    []
  );

  // Zoom in
  const zoomIn = useCallback(
    (ctx: CanvasRenderingContext2D, x: number, y: number) => {
      const { zoomStep } = configRef.current;
      const { scale } = stateRef.current;
      applyZoom(ctx, scale + zoomStep, x, y);
    },
    [applyZoom]
  );

  // Zoom out
  const zoomOut = useCallback(
    (ctx: CanvasRenderingContext2D, x: number, y: number) => {
      const { zoomStep } = configRef.current;
      const { scale } = stateRef.current;
      applyZoom(ctx, scale - zoomStep, x, y);
    },
    [applyZoom]
  );

  // Zoom para um valor específico
  const zoomTo = useCallback(
    (ctx: CanvasRenderingContext2D, scale: number, x: number, y: number) => {
      applyZoom(ctx, scale, x, y);
    },
    [applyZoom]
  );

  // Zoom para ajustar à tela
  const zoomToFit = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      contentWidth: number,
      contentHeight: number,
      viewportWidth: number,
      viewportHeight: number,
      padding = 20
    ) => {
      const scaleX = (viewportWidth - padding * 2) / contentWidth;
      const scaleY = (viewportHeight - padding * 2) / contentHeight;
      const scale = Math.min(scaleX, scaleY);

      const x = (viewportWidth - contentWidth * scale) / 2;
      const y = (viewportHeight - contentHeight * scale) / 2;

      applyZoom(ctx, scale, x, y);
    },
    [applyZoom]
  );

  // Resetar zoom
  const resetZoom = useCallback((ctx: CanvasRenderingContext2D) => {
    stateRef.current = {
      scale: 1,
      offsetX: 0,
      offsetY: 0,
    };

    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }, []);

  // Atualizar configuração do zoom
  const updateZoomConfig = useCallback((config: Partial<ZoomConfig>) => {
    configRef.current = {
      ...configRef.current,
      ...config,
    };
  }, []);

  // Obter estado atual do zoom
  const getZoomState = useCallback(() => {
    return { ...stateRef.current };
  }, []);

  // Transformar ponto do canvas para coordenadas do mundo
  const canvasToWorld = useCallback((x: number, y: number) => {
    const { scale, offsetX, offsetY } = stateRef.current;
    return {
      x: (x - offsetX) / scale,
      y: (y - offsetY) / scale,
    };
  }, []);

  // Transformar ponto do mundo para coordenadas do canvas
  const worldToCanvas = useCallback((x: number, y: number) => {
    const { scale, offsetX, offsetY } = stateRef.current;
    return {
      x: x * scale + offsetX,
      y: y * scale + offsetY,
    };
  }, []);

  return {
    zoomIn,
    zoomOut,
    zoomTo,
    zoomToFit,
    resetZoom,
    updateZoomConfig,
    getZoomState,
    canvasToWorld,
    worldToCanvas,
  };
};
