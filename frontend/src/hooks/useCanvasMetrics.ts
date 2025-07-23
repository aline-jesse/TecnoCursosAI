import { useCallback, useEffect, useRef } from 'react';

interface CanvasMetrics {
  fps: number;
  drawTime: number;
  elementCount: number;
  cacheSize: number;
  memoryUsage: number;
}

interface MetricsOptions {
  sampleSize?: number;
  logInterval?: number;
  logToConsole?: boolean;
  onMetricsUpdate?: (metrics: CanvasMetrics) => void;
}

export const useCanvasMetrics = (options: MetricsOptions = {}) => {
  const {
    sampleSize = 60,
    logInterval = 1000,
    logToConsole = false,
    onMetricsUpdate,
  } = options;

  // Estado das métricas
  const metricsState = useRef({
    frameCount: 0,
    lastFrameTime: 0,
    frameTimes: [] as number[],
    drawTimes: [] as number[],
    elementCounts: [] as number[],
    cacheSizes: [] as number[],
    memoryUsages: [] as number[],
    logTimer: 0,
  });

  // Calcular média de um array
  const calculateAverage = useCallback((arr: number[]) => {
    if (arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  }, []);

  // Registrar frame
  const recordFrame = useCallback(
    (drawTime: number, elementCount: number, cacheSize: number) => {
      const now = performance.now();
      const state = metricsState.current;

      // Calcular tempo do frame
      if (state.lastFrameTime) {
        const frameTime = now - state.lastFrameTime;
        state.frameTimes.push(frameTime);
        if (state.frameTimes.length > sampleSize) {
          state.frameTimes.shift();
        }
      }
      state.lastFrameTime = now;

      // Registrar métricas
      state.frameCount++;
      state.drawTimes.push(drawTime);
      state.elementCounts.push(elementCount);
      state.cacheSizes.push(cacheSize);

      if (state.drawTimes.length > sampleSize) {
        state.drawTimes.shift();
        state.elementCounts.shift();
        state.cacheSizes.shift();
      }

      // Registrar uso de memória
      if ('memory' in performance) {
        state.memoryUsages.push((performance as any).memory.usedJSHeapSize);
        if (state.memoryUsages.length > sampleSize) {
          state.memoryUsages.shift();
        }
      }

      // Calcular e reportar métricas periodicamente
      const timeSinceLastLog = now - state.logTimer;
      if (timeSinceLastLog >= logInterval) {
        const metrics = getMetrics();
        onMetricsUpdate?.(metrics);

        if (logToConsole) {
          console.log('Canvas Metrics:', metrics);
        }

        state.logTimer = now;
      }
    },
    [sampleSize, logInterval, logToConsole, onMetricsUpdate]
  );

  // Obter métricas atuais
  const getMetrics = useCallback((): CanvasMetrics => {
    const state = metricsState.current;

    const fps =
      state.frameTimes.length > 0
        ? 1000 / calculateAverage(state.frameTimes)
        : 0;

    return {
      fps: Math.round(fps * 100) / 100,
      drawTime: calculateAverage(state.drawTimes),
      elementCount: calculateAverage(state.elementCounts),
      cacheSize: calculateAverage(state.cacheSizes),
      memoryUsage: calculateAverage(state.memoryUsages),
    };
  }, [calculateAverage]);

  // Resetar métricas
  const resetMetrics = useCallback(() => {
    metricsState.current = {
      frameCount: 0,
      lastFrameTime: 0,
      frameTimes: [],
      drawTimes: [],
      elementCounts: [],
      cacheSizes: [],
      memoryUsages: [],
      logTimer: 0,
    };
  }, []);

  // Limpar métricas ao desmontar
  useEffect(() => {
    return () => {
      resetMetrics();
    };
  }, [resetMetrics]);

  // Criar objeto de métricas para debug
  const createMetricsDebugObject = useCallback(() => {
    const metrics = getMetrics();
    const state = metricsState.current;

    return {
      ...metrics,
      details: {
        totalFrames: state.frameCount,
        frameTimeHistory: state.frameTimes,
        drawTimeHistory: state.drawTimes,
        elementCountHistory: state.elementCounts,
        cacheSizeHistory: state.cacheSizes,
        memoryUsageHistory: state.memoryUsages,
      },
      stats: {
        fps: {
          min: Math.min(...state.frameTimes.map(t => 1000 / t)),
          max: Math.max(...state.frameTimes.map(t => 1000 / t)),
          avg: metrics.fps,
        },
        drawTime: {
          min: Math.min(...state.drawTimes),
          max: Math.max(...state.drawTimes),
          avg: metrics.drawTime,
        },
        elementCount: {
          min: Math.min(...state.elementCounts),
          max: Math.max(...state.elementCounts),
          avg: metrics.elementCount,
        },
        cacheSize: {
          min: Math.min(...state.cacheSizes),
          max: Math.max(...state.cacheSizes),
          avg: metrics.cacheSize,
        },
        memoryUsage: {
          min: Math.min(...state.memoryUsages),
          max: Math.max(...state.memoryUsages),
          avg: metrics.memoryUsage,
        },
      },
    };
  }, [getMetrics]);

  // Exportar métricas para JSON
  const exportMetrics = useCallback(() => {
    const debugObject = createMetricsDebugObject();
    return JSON.stringify(debugObject, null, 2);
  }, [createMetricsDebugObject]);

  return {
    recordFrame,
    getMetrics,
    resetMetrics,
    createMetricsDebugObject,
    exportMetrics,
  };
};
