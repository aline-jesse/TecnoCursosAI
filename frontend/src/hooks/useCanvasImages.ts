import { useCallback, useRef } from 'react';

interface ImageCache {
  [key: string]: HTMLImageElement;
}

export const useCanvasImages = () => {
  const imageCache = useRef<ImageCache>({});

  // Carregar imagem
  const loadImage = useCallback(
    async (src: string): Promise<HTMLImageElement | null> => {
      // Verificar se a imagem já está no cache
      if (imageCache.current[src]) {
        return imageCache.current[src];
      }

      // Carregar nova imagem
      try {
        const image = new Image();
        const loadPromise = new Promise<HTMLImageElement>((resolve, reject) => {
          image.onload = () => resolve(image);
          image.onerror = () =>
            reject(new Error(`Erro ao carregar imagem: ${src}`));
        });

        image.src = src;
        const loadedImage = await loadPromise;
        imageCache.current[src] = loadedImage;

        return loadedImage;
      } catch (error) {
        console.error('Erro ao carregar imagem:', error);
        return null;
      }
    },
    []
  );

  // Desenhar imagem no canvas
  const drawImage = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      image: HTMLImageElement,
      x: number,
      y: number,
      width?: number,
      height?: number
    ) => {
      try {
        if (width !== undefined && height !== undefined) {
          ctx.drawImage(image, x, y, width, height);
        } else {
          ctx.drawImage(image, x, y);
        }
      } catch (error) {
        console.error('Erro ao desenhar imagem:', error);
      }
    },
    []
  );

  // Pré-carregar várias imagens
  const preloadImages = useCallback(
    async (sources: string[]): Promise<void> => {
      try {
        await Promise.all(sources.map(src => loadImage(src)));
      } catch (error) {
        console.error('Erro ao pré-carregar imagens:', error);
      }
    },
    [loadImage]
  );

  // Limpar cache de imagens
  const clearCache = useCallback(() => {
    imageCache.current = {};
  }, []);

  // Verificar se uma imagem está no cache
  const isImageCached = useCallback((src: string): boolean => {
    return src in imageCache.current;
  }, []);

  // Remover uma imagem específica do cache
  const removeFromCache = useCallback((src: string) => {
    delete imageCache.current[src];
  }, []);

  // Obter tamanho do cache
  const getCacheSize = useCallback((): number => {
    return Object.keys(imageCache.current).length;
  }, []);

  return {
    loadImage,
    drawImage,
    preloadImages,
    clearCache,
    isImageCached,
    removeFromCache,
    getCacheSize,
  };
};
