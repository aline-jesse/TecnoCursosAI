import { act, renderHook } from '@testing-library/react-hooks';
import { useCanvasFonts } from '../useCanvasFonts';

describe('useCanvasFonts', () => {
  let mockFontFace: FontFace;

  beforeEach(() => {
    mockFontFace = {
      family: 'Test Font',
      load: jest.fn().mockResolvedValue(undefined),
      loaded: Promise.resolve(),
      status: 'loaded',
      style: 'normal',
      weight: '400',
      stretch: 'normal',
      unicodeRange: 'U+0-10FFFF',
      variant: 'normal',
      featureSettings: 'normal',
      variationSettings: 'normal',
      display: 'auto',
    } as unknown as FontFace;

    // Mock document.fonts
    Object.defineProperty(document, 'fonts', {
      value: {
        add: jest.fn(),
        delete: jest.fn(),
        check: jest.fn().mockReturnValue(true),
      },
      writable: true,
    });

    // Mock FontFace constructor
    global.FontFace = jest
      .fn()
      .mockImplementation(() => mockFontFace) as unknown as typeof FontFace;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should load a font', async () => {
    const { result } = renderHook(() => useCanvasFonts());
    const family = 'Test Font';
    const source = 'test-font.woff2';

    let font: FontFace | null = null;
    await act(async () => {
      font = await result.current.loadFont(family, source);
    });

    expect(font).toBe(mockFontFace);
    expect(document.fonts.add).toHaveBeenCalledWith(mockFontFace);
    expect(result.current.isFontCached(source)).toBe(true);
  });

  it('should handle font load error', async () => {
    const { result } = renderHook(() => useCanvasFonts());
    const family = 'Test Font';
    const source = 'invalid-font.woff2';

    // Mock font load error
    mockFontFace.load = jest
      .fn()
      .mockRejectedValue(new Error('Font load error'));

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    let font: FontFace | null = null;
    await act(async () => {
      font = await result.current.loadFont(family, source);
    });

    expect(font).toBeNull();
    expect(consoleSpy).toHaveBeenCalledWith(
      'Erro ao carregar fonte:',
      expect.any(Error)
    );
    expect(result.current.isFontCached(source)).toBe(false);

    consoleSpy.mockRestore();
  });

  it('should preload multiple fonts', async () => {
    const { result } = renderHook(() => useCanvasFonts());
    const fonts = [
      { family: 'Font 1', source: 'font1.woff2' },
      { family: 'Font 2', source: 'font2.woff2' },
      { family: 'Font 3', source: 'font3.woff2' },
    ];

    await act(async () => {
      await result.current.preloadFonts(fonts);
    });

    fonts.forEach(font => {
      expect(result.current.isFontCached(font.source)).toBe(true);
    });
    expect(document.fonts.add).toHaveBeenCalledTimes(fonts.length);
  });

  it('should check if font is loaded', () => {
    const { result } = renderHook(() => useCanvasFonts());
    const family = 'Test Font';

    const isLoaded = result.current.isFontLoaded(family);
    expect(isLoaded).toBe(true);
    expect(document.fonts.check).toHaveBeenCalledWith(`12px "${family}"`);
  });

  it('should clear font cache', async () => {
    const { result } = renderHook(() => useCanvasFonts());
    const family = 'Test Font';
    const source = 'test-font.woff2';

    // Carregar uma fonte
    await act(async () => {
      await result.current.loadFont(family, source);
    });

    // Limpar o cache
    act(() => {
      result.current.clearCache();
    });

    expect(document.fonts.delete).toHaveBeenCalledWith(mockFontFace);
    expect(result.current.isFontCached(source)).toBe(false);
    expect(result.current.getCacheSize()).toBe(0);
  });

  it('should remove specific font from cache', async () => {
    const { result } = renderHook(() => useCanvasFonts());
    const font1 = { family: 'Font 1', source: 'font1.woff2' };
    const font2 = { family: 'Font 2', source: 'font2.woff2' };

    // Carregar duas fontes
    await act(async () => {
      await result.current.loadFont(font1.family, font1.source);
      await result.current.loadFont(font2.family, font2.source);
    });

    // Remover uma fonte específica
    act(() => {
      result.current.removeFromCache(font1.source);
    });

    expect(document.fonts.delete).toHaveBeenCalledTimes(1);
    expect(result.current.isFontCached(font1.source)).toBe(false);
    expect(result.current.isFontCached(font2.source)).toBe(true);
  });

  it('should get loaded fonts', async () => {
    const { result } = renderHook(() => useCanvasFonts());
    const fonts = [
      { family: 'Font 1', source: 'font1.woff2' },
      { family: 'Font 2', source: 'font2.woff2' },
    ];

    // Carregar fontes
    await act(async () => {
      await result.current.preloadFonts(fonts);
    });

    const loadedFonts = result.current.getLoadedFonts();
    expect(loadedFonts).toHaveLength(fonts.length);
    fonts.forEach(font => {
      expect(loadedFonts).toContain(font.source);
    });
  });

  it('should handle errors gracefully when removing fonts', () => {
    const { result } = renderHook(() => useCanvasFonts());
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    // Mock document.fonts.delete para lançar erro
    (document.fonts.delete as jest.Mock).mockImplementation(() => {
      throw new Error('Font removal error');
    });

    act(() => {
      result.current.removeFromCache('test-font.woff2');
    });

    expect(consoleSpy).toHaveBeenCalledWith(
      'Erro ao remover fonte:',
      expect.any(Error)
    );
    consoleSpy.mockRestore();
  });
});
