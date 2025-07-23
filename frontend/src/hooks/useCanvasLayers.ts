import { useCallback, useEffect, useRef } from 'react';

interface Layer {
  canvas: HTMLCanvasElement;
  context: CanvasRenderingContext2D;
  zIndex: number;
}

interface LayerOptions {
  zIndex?: number;
  alpha?: boolean;
  willReadFrequently?: boolean;
}

export const useCanvasLayers = () => {
  const layersRef = useRef<Map<string, Layer>>(new Map());

  // Criar uma nova camada
  const createLayer = useCallback((id: string, options: LayerOptions = {}) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d', {
      alpha: options.alpha !== false,
      willReadFrequently: options.willReadFrequently,
    });

    if (!context) {
      throw new Error(`Não foi possível criar contexto 2D para a camada ${id}`);
    }

    const layer: Layer = {
      canvas,
      context,
      zIndex: options.zIndex || 0,
    };

    layersRef.current.set(id, layer);

    // Configurar estilo do canvas
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.zIndex = layer.zIndex.toString();

    return layer;
  }, []);

  // Destruir uma camada
  const destroyLayer = useCallback((id: string) => {
    const layer = layersRef.current.get(id);
    if (layer) {
      layer.canvas.remove();
      layersRef.current.delete(id);
    }
  }, []);

  // Obter uma camada
  const getLayer = useCallback((id: string) => {
    return layersRef.current.get(id);
  }, []);

  // Obter todas as camadas ordenadas por zIndex
  const getLayers = useCallback(() => {
    return Array.from(layersRef.current.values()).sort(
      (a, b) => a.zIndex - b.zIndex
    );
  }, []);

  // Limpar uma camada
  const clearLayer = useCallback((id: string) => {
    const layer = layersRef.current.get(id);
    if (layer) {
      const { canvas, context } = layer;
      context.clearRect(0, 0, canvas.width, canvas.height);
    }
  }, []);

  // Limpar todas as camadas
  const clearAllLayers = useCallback(() => {
    layersRef.current.forEach(layer => {
      const { canvas, context } = layer;
      context.clearRect(0, 0, canvas.width, canvas.height);
    });
  }, []);

  // Redimensionar todas as camadas
  const resizeLayers = useCallback((width: number, height: number) => {
    layersRef.current.forEach(layer => {
      const { canvas } = layer;
      canvas.width = width;
      canvas.height = height;
    });
  }, []);

  // Atualizar zIndex de uma camada
  const updateLayerZIndex = useCallback((id: string, zIndex: number) => {
    const layer = layersRef.current.get(id);
    if (layer) {
      layer.zIndex = zIndex;
      layer.canvas.style.zIndex = zIndex.toString();
    }
  }, []);

  // Limpar todas as camadas ao desmontar
  useEffect(() => {
    return () => {
      layersRef.current.forEach((_, id) => {
        destroyLayer(id);
      });
    };
  }, [destroyLayer]);

  return {
    createLayer,
    destroyLayer,
    getLayer,
    getLayers,
    clearLayer,
    clearAllLayers,
    resizeLayers,
    updateLayerZIndex,
    layers: layersRef.current,
  };
};
