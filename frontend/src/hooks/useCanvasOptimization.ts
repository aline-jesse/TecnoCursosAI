import { useCallback, useEffect, useRef } from 'react';

interface CanvasOptimizationConfig {
  devicePixelRatio: number;
  useOffscreenCanvas: boolean;
  batchDrawing: boolean;
  imageCaching: boolean;
  maxFPS: number;
}

export const useCanvasOptimization = (width: number, height: number) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const offscreenCanvasRef = useRef<OffscreenCanvas | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastFrameTimeRef = useRef<number>(0);

  const optimizationConfig: CanvasOptimizationConfig = {
    devicePixelRatio: window.devicePixelRatio || 1,
    useOffscreenCanvas: 'OffscreenCanvas' in window,
    batchDrawing: true,
    imageCaching: true,
    maxFPS: 60,
  };

  // Configurar canvas com devicePixelRatio
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = optimizationConfig.devicePixelRatio;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.scale(dpr, dpr);
    }

    // Criar offscreen canvas se suportado
    if (optimizationConfig.useOffscreenCanvas) {
      offscreenCanvasRef.current = new OffscreenCanvas(
        width * dpr,
        height * dpr
      );
    }
  }, [width, height, optimizationConfig.devicePixelRatio]);

  // Função para limitar FPS
  const requestAnimationFrameThrottled = useCallback(
    (callback: FrameRequestCallback) => {
      const currentTime = performance.now();
      const timeUntilNextFrame = Math.max(
        0,
        1000 / optimizationConfig.maxFPS -
          (currentTime - lastFrameTimeRef.current)
      );

      if (timeUntilNextFrame === 0) {
        lastFrameTimeRef.current = currentTime;
        animationFrameRef.current = requestAnimationFrame(callback);
      } else {
        setTimeout(() => {
          lastFrameTimeRef.current = performance.now();
          animationFrameRef.current = requestAnimationFrame(callback);
        }, timeUntilNextFrame);
      }
    },
    [optimizationConfig.maxFPS]
  );

  // Limpar animationFrame ao desmontar
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    canvasRef,
    offscreenCanvasRef,
    optimizationConfig,
    requestAnimationFrameThrottled,
  };
};
