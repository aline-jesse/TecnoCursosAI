import { useCallback, useEffect, useRef } from 'react';

interface CachedImage {
  image: HTMLImageElement;
  timestamp: number;
  lastUsed: number;
}

interface ImageCacheOptions {
  maxSize?: number; // Número máximo de imagens em cache
  maxAge?: number; // Tempo máximo em ms que uma imagem pode ficar em cache
  cleanupInterval?: number; // Intervalo em ms para limpar o cache
}

const DEFAULT_OPTIONS: Required<ImageCacheOptions> = {
  maxSize: 100,
  maxAge: 5 * 60 * 1000, // 5 minutos
  cleanupInterval: 60 * 1000, // 1 minuto
};

export const useImageCache = (options: ImageCacheOptions = {}) => {
  const { maxSize, maxAge, cleanupInterval } = {
    ...DEFAULT_OPTIONS,
    ...options,
  };

  const cache = useRef<Map<string, CachedImage>>(new Map());
  const cleanupTimer = useRef<number>();

  const loadImage = useCallback((src: string): Promise<HTMLImageElement> => {
    // Verificar se a imagem já está em cache
    const cached = cache.current.get(src);
    if (cached) {
      cached.lastUsed = Date.now();
      return Promise.resolve(cached.image);
    }

    // Carregar nova imagem
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';

      img.onload = () => {
        cache.current.set(src, {
          image: img,
          timestamp: Date.now(),
          lastUsed: Date.now(),
        });
        resolve(img);
      };

      img.onerror = () => {
        reject(new Error(`Failed to load image: ${src}`));
      };

      img.src = src;
    });
  }, []);

  const preloadImages = useCallback(
    (srcs: string[]): Promise<HTMLImageElement[]> => {
      return Promise.all(srcs.map(loadImage));
    },
    [loadImage]
  );

  const cleanup = useCallback(() => {
    const now = Date.now();

    // Remover imagens antigas
    for (const [src, { timestamp, lastUsed }] of cache.current.entries()) {
      if (now - timestamp > maxAge || now - lastUsed > maxAge) {
        cache.current.delete(src);
      }
    }

    // Remover imagens excedentes (mais antigas primeiro)
    if (cache.current.size > maxSize) {
      const sortedEntries = Array.from(cache.current.entries()).sort(
        ([, a], [, b]) => a.lastUsed - b.lastUsed
      );

      const toRemove = sortedEntries.slice(0, cache.current.size - maxSize);
      toRemove.forEach(([src]) => cache.current.delete(src));
    }
  }, [maxAge, maxSize]);

  const clearCache = useCallback(() => {
    cache.current.clear();
  }, []);

  const getCacheSize = useCallback(() => {
    return cache.current.size;
  }, []);

  const getCacheInfo = useCallback(() => {
    return Array.from(cache.current.entries()).map(
      ([src, { timestamp, lastUsed }]) => ({
        src,
        timestamp,
        lastUsed,
        age: Date.now() - timestamp,
        timeSinceLastUse: Date.now() - lastUsed,
      })
    );
  }, []);

  useEffect(() => {
    // Iniciar timer de limpeza
    cleanupTimer.current = window.setInterval(cleanup, cleanupInterval);

    return () => {
      if (cleanupTimer.current) {
        clearInterval(cleanupTimer.current);
      }
    };
  }, [cleanup, cleanupInterval]);

  return {
    loadImage,
    preloadImages,
    clearCache,
    getCacheSize,
    getCacheInfo,
  };
};
