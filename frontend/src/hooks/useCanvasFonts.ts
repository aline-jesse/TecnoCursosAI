import { useCallback, useRef } from 'react';

interface FontCache {
  [key: string]: FontFace;
}

export const useCanvasFonts = () => {
  const fontCache = useRef<FontCache>({});

  // Carregar fonte
  const loadFont = useCallback(
    async (
      family: string,
      source: string | ArrayBuffer
    ): Promise<FontFace | null> => {
      // Verificar se a fonte já está no cache
      const cacheKey = typeof source === 'string' ? source : family;
      if (fontCache.current[cacheKey]) {
        return fontCache.current[cacheKey];
      }

      // Carregar nova fonte
      try {
        const font = new FontFace(family, source);
        await font.load();
        document.fonts.add(font);
        fontCache.current[cacheKey] = font;
        return font;
      } catch (error) {
        console.error('Erro ao carregar fonte:', error);
        return null;
      }
    },
    []
  );

  // Pré-carregar várias fontes
  const preloadFonts = useCallback(
    async (
      fonts: Array<{ family: string; source: string | ArrayBuffer }>
    ): Promise<void> => {
      try {
        await Promise.all(
          fonts.map(font => loadFont(font.family, font.source))
        );
      } catch (error) {
        console.error('Erro ao pré-carregar fontes:', error);
      }
    },
    [loadFont]
  );

  // Verificar se uma fonte está carregada
  const isFontLoaded = useCallback((family: string): boolean => {
    return document.fonts.check(`12px "${family}"`);
  }, []);

  // Verificar se uma fonte está no cache
  const isFontCached = useCallback((key: string): boolean => {
    return key in fontCache.current;
  }, []);

  // Limpar cache de fontes
  const clearCache = useCallback(() => {
    Object.values(fontCache.current).forEach(font => {
      try {
        document.fonts.delete(font);
      } catch (error) {
        console.error('Erro ao remover fonte:', error);
      }
    });
    fontCache.current = {};
  }, []);

  // Remover uma fonte específica do cache
  const removeFromCache = useCallback((key: string) => {
    const font = fontCache.current[key];
    if (font) {
      try {
        document.fonts.delete(font);
        delete fontCache.current[key];
      } catch (error) {
        console.error('Erro ao remover fonte:', error);
      }
    }
  }, []);

  // Obter tamanho do cache
  const getCacheSize = useCallback((): number => {
    return Object.keys(fontCache.current).length;
  }, []);

  // Obter lista de fontes carregadas
  const getLoadedFonts = useCallback((): string[] => {
    return Object.keys(fontCache.current);
  }, []);

  return {
    loadFont,
    preloadFonts,
    isFontLoaded,
    isFontCached,
    clearCache,
    removeFromCache,
    getCacheSize,
    getLoadedFonts,
  };
};
