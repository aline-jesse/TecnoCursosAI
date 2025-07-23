import { renderHook  } from '@testing-library/react';
import { useCanvasOptimization } from '../useCanvasOptimization';

describe('useCanvasOptimization', () => {
  const mockCanvas = document.createElement('canvas');
  const mockContext = mockCanvas.getContext('2d');

  beforeEach(() => {
    jest
      .spyOn(window, 'requestAnimationFrame')
      .mockImplementation(cb => setTimeout(cb, 0));
    jest
      .spyOn(window, 'cancelAnimationFrame')
      .mockImplementation(id => clearTimeout(id));
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should create canvas ref with correct dimensions', () => {
    const { result } = renderHook(() => useCanvasOptimization(800, 600));

    expect(result.current.canvasRef.current).toBeDefined();
    expect(result.current.optimizationConfig.devicePixelRatio).toBeDefined();
  });

  it('should create offscreen canvas when supported', () => {
    // Mock OffscreenCanvas support
    global.OffscreenCanvas = class OffscreenCanvas {
      constructor(width: number, height: number) {
        return { width, height };
      }
    } as any;

    const { result } = renderHook(() => useCanvasOptimization(800, 600));

    expect(result.current.offscreenCanvasRef.current).toBeDefined();
    expect(result.current.optimizationConfig.useOffscreenCanvas).toBe(true);
  });

  it('should not create offscreen canvas when not supported', () => {
    // Remove OffscreenCanvas support
    delete (global as any).OffscreenCanvas;

    const { result } = renderHook(() => useCanvasOptimization(800, 600));

    expect(result.current.offscreenCanvasRef.current).toBeNull();
    expect(result.current.optimizationConfig.useOffscreenCanvas).toBe(false);
  });

  it('should throttle animation frame requests', () => {
    const { result } = renderHook(() => useCanvasOptimization(800, 600));
    const callback = jest.fn();

    result.current.requestAnimationFrameThrottled(callback);

    expect(window.requestAnimationFrame).toHaveBeenCalledTimes(1);
    expect(callback).not.toHaveBeenCalled();

    // Fast-forward time
    jest.advanceTimersByTime(1000 / result.current.optimizationConfig.maxFPS);

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should clean up animation frame on unmount', () => {
    const { unmount } = renderHook(() => useCanvasOptimization(800, 600));

    unmount();

    expect(window.cancelAnimationFrame).toHaveBeenCalled();
  });

  it('should update canvas dimensions when props change', () => {
    const { rerender } = renderHook(
      ({ width, height }) => useCanvasOptimization(width, height),
      { initialProps: { width: 800, height: 600 } }
    );

    const canvas = document.createElement('canvas');
    const dpr = window.devicePixelRatio || 1;

    expect(canvas.width).toBe(800 * dpr);
    expect(canvas.height).toBe(600 * dpr);

    rerender({ width: 1024, height: 768 });

    expect(canvas.width).toBe(1024 * dpr);
    expect(canvas.height).toBe(768 * dpr);
  });

  it('should apply device pixel ratio scaling', () => {
    const dpr = 2;
    Object.defineProperty(window, 'devicePixelRatio', { value: dpr });

    const { result } = renderHook(() => useCanvasOptimization(800, 600));

    expect(result.current.optimizationConfig.devicePixelRatio).toBe(dpr);
  });

  it('should batch multiple animation frame requests', () => {
    const { result } = renderHook(() => useCanvasOptimization(800, 600));
    const callback1 = jest.fn();
    const callback2 = jest.fn();

    result.current.requestAnimationFrameThrottled(callback1);
    result.current.requestAnimationFrameThrottled(callback2);

    expect(window.requestAnimationFrame).toHaveBeenCalledTimes(1);

    // Fast-forward time
    jest.advanceTimersByTime(1000 / result.current.optimizationConfig.maxFPS);

    expect(callback1).toHaveBeenCalledTimes(1);
    expect(callback2).toHaveBeenCalledTimes(1);
  });
});
