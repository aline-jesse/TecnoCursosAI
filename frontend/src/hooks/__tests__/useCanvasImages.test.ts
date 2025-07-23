import { act, renderHook } from '@testing-library/react-hooks';
import { useCanvasImages } from '../useCanvasImages';

describe('useCanvasImages', () => {
  let mockImage: HTMLImageElement;
  let mockContext: CanvasRenderingContext2D;

  beforeEach(() => {
    mockImage = new Image();
    mockContext = document.createElement('canvas').getContext('2d')!;
    jest.spyOn(mockContext, 'drawImage');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should load and cache an image', async () => {
    const { result } = renderHook(() => useCanvasImages());
    const src = 'test-image.jpg';

    // Mock Image.prototype.onload
    const originalImage = window.Image;
    window.Image = class extends originalImage {
      constructor() {
        super();
        setTimeout(() => {
          this.onload?.();
        }, 0);
      }
    } as any;

    let loadedImage: HTMLImageElement | null = null;
    await act(async () => {
      loadedImage = await result.current.loadImage(src);
    });

    expect(loadedImage).toBeDefined();
    expect(loadedImage?.src).toContain(src);

    // Verificar se a imagem está no cache
    expect(result.current.isImageCached(src)).toBe(true);

    // Restaurar o construtor original de Image
    window.Image = originalImage;
  });

  it('should handle image load error', async () => {
    const { result } = renderHook(() => useCanvasImages());
    const src = 'invalid-image.jpg';

    // Mock Image.prototype.onerror
    const originalImage = window.Image;
    window.Image = class extends originalImage {
      constructor() {
        super();
        setTimeout(() => {
          this.onerror?.();
        }, 0);
      }
    } as any;

    let loadedImage: HTMLImageElement | null = null;
    await act(async () => {
      loadedImage = await result.current.loadImage(src);
    });

    expect(loadedImage).toBeNull();
    expect(result.current.isImageCached(src)).toBe(false);

    // Restaurar o construtor original de Image
    window.Image = originalImage;
  });

  it('should draw image on canvas', () => {
    const { result } = renderHook(() => useCanvasImages());

    act(() => {
      result.current.drawImage(mockContext, mockImage, 0, 0);
    });

    expect(mockContext.drawImage).toHaveBeenCalledWith(mockImage, 0, 0);
  });

  it('should draw image with dimensions', () => {
    const { result } = renderHook(() => useCanvasImages());

    act(() => {
      result.current.drawImage(mockContext, mockImage, 0, 0, 100, 100);
    });

    expect(mockContext.drawImage).toHaveBeenCalledWith(
      mockImage,
      0,
      0,
      100,
      100
    );
  });

  it('should preload multiple images', async () => {
    const { result } = renderHook(() => useCanvasImages());
    const sources = ['image1.jpg', 'image2.jpg', 'image3.jpg'];

    // Mock Image.prototype.onload
    const originalImage = window.Image;
    window.Image = class extends originalImage {
      constructor() {
        super();
        setTimeout(() => {
          this.onload?.();
        }, 0);
      }
    } as any;

    await act(async () => {
      await result.current.preloadImages(sources);
    });

    sources.forEach(src => {
      expect(result.current.isImageCached(src)).toBe(true);
    });

    // Restaurar o construtor original de Image
    window.Image = originalImage;
  });

  it('should clear image cache', () => {
    const { result } = renderHook(() => useCanvasImages());
    const src = 'test-image.jpg';

    // Adicionar uma imagem ao cache
    act(() => {
      result.current.loadImage(src);
    });

    // Limpar o cache
    act(() => {
      result.current.clearCache();
    });

    expect(result.current.isImageCached(src)).toBe(false);
    expect(result.current.getCacheSize()).toBe(0);
  });

  it('should remove specific image from cache', () => {
    const { result } = renderHook(() => useCanvasImages());
    const src1 = 'image1.jpg';
    const src2 = 'image2.jpg';

    // Adicionar imagens ao cache
    act(() => {
      result.current.loadImage(src1);
      result.current.loadImage(src2);
    });

    // Remover uma imagem específica
    act(() => {
      result.current.removeFromCache(src1);
    });

    expect(result.current.isImageCached(src1)).toBe(false);
    expect(result.current.isImageCached(src2)).toBe(true);
  });

  it('should handle drawing errors gracefully', () => {
    const { result } = renderHook(() => useCanvasImages());
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    // Forçar um erro no drawImage
    mockContext.drawImage = jest.fn(() => {
      throw new Error('Draw error');
    });

    act(() => {
      result.current.drawImage(mockContext, mockImage, 0, 0);
    });

    expect(consoleSpy).toHaveBeenCalledWith(
      'Erro ao desenhar imagem:',
      expect.any(Error)
    );
    consoleSpy.mockRestore();
  });
});
