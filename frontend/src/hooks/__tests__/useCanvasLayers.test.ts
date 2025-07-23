import { act, renderHook } from '@testing-library/react-hooks';
import { useCanvasLayers } from '../useCanvasLayers';

describe('useCanvasLayers', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('should create a new layer', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      const layer = result.current.createLayer('test', { zIndex: 1 });
      expect(layer).toBeDefined();
      expect(layer.canvas).toBeInstanceOf(HTMLCanvasElement);
      expect(layer.context).toBeInstanceOf(CanvasRenderingContext2D);
      expect(layer.zIndex).toBe(1);
    });
  });

  it('should destroy a layer', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      result.current.createLayer('test');
      result.current.destroyLayer('test');
      expect(result.current.getLayer('test')).toBeUndefined();
    });
  });

  it('should get a layer', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      const layer = result.current.createLayer('test');
      const retrievedLayer = result.current.getLayer('test');
      expect(retrievedLayer).toBe(layer);
    });
  });

  it('should get all layers sorted by zIndex', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      result.current.createLayer('layer1', { zIndex: 2 });
      result.current.createLayer('layer2', { zIndex: 1 });
      result.current.createLayer('layer3', { zIndex: 3 });

      const layers = result.current.getLayers();
      expect(layers.length).toBe(3);
      expect(layers[0].zIndex).toBe(1);
      expect(layers[1].zIndex).toBe(2);
      expect(layers[2].zIndex).toBe(3);
    });
  });

  it('should clear a layer', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      const layer = result.current.createLayer('test');
      const clearRectSpy = jest.spyOn(layer.context, 'clearRect');
      result.current.clearLayer('test');
      expect(clearRectSpy).toHaveBeenCalled();
    });
  });

  it('should clear all layers', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      const layer1 = result.current.createLayer('layer1');
      const layer2 = result.current.createLayer('layer2');
      const clearRectSpy1 = jest.spyOn(layer1.context, 'clearRect');
      const clearRectSpy2 = jest.spyOn(layer2.context, 'clearRect');

      result.current.clearAllLayers();
      expect(clearRectSpy1).toHaveBeenCalled();
      expect(clearRectSpy2).toHaveBeenCalled();
    });
  });

  it('should resize all layers', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      const layer1 = result.current.createLayer('layer1');
      const layer2 = result.current.createLayer('layer2');

      result.current.resizeLayers(800, 600);
      expect(layer1.canvas.width).toBe(800);
      expect(layer1.canvas.height).toBe(600);
      expect(layer2.canvas.width).toBe(800);
      expect(layer2.canvas.height).toBe(600);
    });
  });

  it('should update layer zIndex', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      const layer = result.current.createLayer('test', { zIndex: 1 });
      result.current.updateLayerZIndex('test', 2);
      expect(layer.zIndex).toBe(2);
      expect(layer.canvas.style.zIndex).toBe('2');
    });
  });

  it('should handle layer options', () => {
    const { result } = renderHook(() => useCanvasLayers());

    act(() => {
      const layer = result.current.createLayer('test', {
        zIndex: 1,
        alpha: true,
        willReadFrequently: true,
      });

      expect(layer.zIndex).toBe(1);
      expect(layer.canvas.style.zIndex).toBe('1');
    });
  });

  it('should clean up layers on unmount', () => {
    const { result, unmount } = renderHook(() => useCanvasLayers());

    act(() => {
      result.current.createLayer('layer1');
      result.current.createLayer('layer2');
    });

    const removeSpy = jest.spyOn(HTMLCanvasElement.prototype, 'remove');
    unmount();

    expect(removeSpy).toHaveBeenCalledTimes(2);
  });
});
