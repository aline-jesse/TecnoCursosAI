import { renderHook  } from '@testing-library/react';
import { useCanvasPatterns } from '../useCanvasPatterns';

describe('useCanvasPatterns', () => {
  let mockContext: CanvasRenderingContext2D;
  let mockPattern: CanvasPattern;
  let mockImage: HTMLImageElement;
  let mockPath: Path2D;

  beforeEach(() => {
    mockPattern = {
      setTransform: jest.fn(),
    } as unknown as CanvasPattern;

    mockContext = {
      createPattern: jest.fn().mockReturnValue(mockPattern),
      save: jest.fn(),
      restore: jest.fn(),
      fillStyle: '#000000',
      strokeStyle: '#000000',
      fillRect: jest.fn(),
      fill: jest.fn(),
      beginPath: jest.fn(),
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      arc: jest.fn(),
      stroke: jest.fn(),
    } as unknown as CanvasRenderingContext2D;

    mockImage = new Image();
    mockPath = new Path2D();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should create pattern', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const config = {
      image: mockImage,
      repetition: 'repeat' as const,
      transform: new DOMMatrix(),
    };

    const pattern = result.current.createPattern(mockContext, config);

    expect(mockContext.createPattern).toHaveBeenCalledWith(mockImage, 'repeat');
    expect(mockPattern.setTransform).toHaveBeenCalledWith(config.transform);
    expect(pattern).toBe(mockPattern);
  });

  it('should return cached pattern', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const config = {
      image: mockImage,
      repetition: 'repeat' as const,
    };

    // Criar padrão pela primeira vez
    const pattern1 = result.current.createPattern(mockContext, config);
    expect(mockContext.createPattern).toHaveBeenCalledTimes(1);

    // Obter o mesmo padrão do cache
    const pattern2 = result.current.createPattern(mockContext, config);
    expect(mockContext.createPattern).toHaveBeenCalledTimes(1);
    expect(pattern2).toBe(pattern1);
  });

  it('should draw rect with pattern', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    result.current.drawRectWithPattern(
      mockContext,
      0,
      0,
      100,
      100,
      mockPattern
    );

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.fillStyle).toBe(mockPattern);
    expect(mockContext.fillRect).toHaveBeenCalledWith(0, 0, 100, 100);
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw path with pattern', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    result.current.drawPathWithPattern(mockContext, mockPath, mockPattern);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.fillStyle).toBe(mockPattern);
    expect(mockContext.fill).toHaveBeenCalledWith(mockPath);
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should create checker pattern', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const pattern = result.current.createCheckerPattern(
      mockContext,
      10,
      '#000000',
      '#ffffff'
    );

    expect(pattern).toBe(mockPattern);
    expect(mockContext.createPattern).toHaveBeenCalled();
  });

  it('should create line pattern', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const pattern = result.current.createLinePattern(
      mockContext,
      10,
      '#000000',
      45
    );

    expect(pattern).toBe(mockPattern);
    expect(mockContext.createPattern).toHaveBeenCalled();
  });

  it('should create dot pattern', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const pattern = result.current.createDotPattern(
      mockContext,
      20,
      5,
      '#000000'
    );

    expect(pattern).toBe(mockPattern);
    expect(mockContext.createPattern).toHaveBeenCalled();
  });

  it('should clear pattern cache', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const config = {
      image: mockImage,
      repetition: 'repeat' as const,
    };

    // Criar um padrão
    result.current.createPattern(mockContext, config);
    expect(result.current.isImageCached(mockImage.src)).toBe(true);

    // Limpar cache
    result.current.clearCache();
    expect(result.current.isImageCached(mockImage.src)).toBe(false);
  });

  it('should remove pattern from cache', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const config = {
      image: mockImage,
      repetition: 'repeat' as const,
    };

    // Criar um padrão
    result.current.createPattern(mockContext, config);
    expect(result.current.isImageCached(mockImage.src)).toBe(true);

    // Remover do cache
    result.current.removeFromCache(mockImage.src);
    expect(result.current.isImageCached(mockImage.src)).toBe(false);
  });

  it('should get cache size', () => {
    const { result } = renderHook(() => useCanvasPatterns());

    const config1 = {
      image: mockImage,
      repetition: 'repeat' as const,
    };

    const config2 = {
      image: new Image(),
      repetition: 'repeat' as const,
    };

    // Criar dois padrões
    result.current.createPattern(mockContext, config1);
    result.current.createPattern(mockContext, config2);

    expect(result.current.getCacheSize()).toBe(2);
  });
});
