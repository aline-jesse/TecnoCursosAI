import { renderHook } from '@testing-library/react-hooks';
import { useCanvasShadows } from '../useCanvasShadows';

describe('useCanvasShadows', () => {
  let mockContext: CanvasRenderingContext2D;
  let mockPath: Path2D;
  let mockImage: HTMLImageElement;

  beforeEach(() => {
    mockContext = {
      save: jest.fn(),
      restore: jest.fn(),
      shadowColor: '#000000',
      shadowBlur: 0,
      shadowOffsetX: 0,
      shadowOffsetY: 0,
      fillRect: jest.fn(),
      fillText: jest.fn(),
      drawImage: jest.fn(),
      fill: jest.fn(),
      beginPath: jest.fn(),
      rect: jest.fn(),
      clip: jest.fn(),
      fillStyle: '#000000',
    } as unknown as CanvasRenderingContext2D;

    mockPath = {
      addPath: jest.fn(),
    } as unknown as Path2D;

    mockImage = new Image();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should set shadow', () => {
    const { result } = renderHook(() => useCanvasShadows());

    const config = {
      color: '#000000',
      blur: 10,
      offsetX: 5,
      offsetY: 5,
    };

    result.current.setShadow(mockContext, config);

    expect(mockContext.shadowColor).toBe(config.color);
    expect(mockContext.shadowBlur).toBe(config.blur);
    expect(mockContext.shadowOffsetX).toBe(config.offsetX);
    expect(mockContext.shadowOffsetY).toBe(config.offsetY);
  });

  it('should clear shadow', () => {
    const { result } = renderHook(() => useCanvasShadows());

    result.current.clearShadow(mockContext);

    expect(mockContext.shadowColor).toBe('rgba(0, 0, 0, 0)');
    expect(mockContext.shadowBlur).toBe(0);
    expect(mockContext.shadowOffsetX).toBe(0);
    expect(mockContext.shadowOffsetY).toBe(0);
  });

  it('should draw rectangle with shadow', () => {
    const { result } = renderHook(() => useCanvasShadows());

    const shadow = {
      color: '#000000',
      blur: 10,
      offsetX: 5,
      offsetY: 5,
    };

    result.current.drawRectWithShadow(mockContext, 0, 0, 100, 100, shadow);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.shadowColor).toBe(shadow.color);
    expect(mockContext.shadowBlur).toBe(shadow.blur);
    expect(mockContext.shadowOffsetX).toBe(shadow.offsetX);
    expect(mockContext.shadowOffsetY).toBe(shadow.offsetY);
    expect(mockContext.fillRect).toHaveBeenCalledWith(0, 0, 100, 100);
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw text with shadow', () => {
    const { result } = renderHook(() => useCanvasShadows());

    const shadow = {
      color: '#000000',
      blur: 10,
      offsetX: 5,
      offsetY: 5,
    };

    result.current.drawTextWithShadow(mockContext, 'Test Text', 0, 0, shadow);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.shadowColor).toBe(shadow.color);
    expect(mockContext.shadowBlur).toBe(shadow.blur);
    expect(mockContext.shadowOffsetX).toBe(shadow.offsetX);
    expect(mockContext.shadowOffsetY).toBe(shadow.offsetY);
    expect(mockContext.fillText).toHaveBeenCalledWith('Test Text', 0, 0);
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw image with shadow', () => {
    const { result } = renderHook(() => useCanvasShadows());

    const shadow = {
      color: '#000000',
      blur: 10,
      offsetX: 5,
      offsetY: 5,
    };

    result.current.drawImageWithShadow(
      mockContext,
      mockImage,
      0,
      0,
      100,
      100,
      shadow
    );

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.shadowColor).toBe(shadow.color);
    expect(mockContext.shadowBlur).toBe(shadow.blur);
    expect(mockContext.shadowOffsetX).toBe(shadow.offsetX);
    expect(mockContext.shadowOffsetY).toBe(shadow.offsetY);
    expect(mockContext.drawImage).toHaveBeenCalledWith(
      mockImage,
      0,
      0,
      100,
      100
    );
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw path with shadow', () => {
    const { result } = renderHook(() => useCanvasShadows());

    const shadow = {
      color: '#000000',
      blur: 10,
      offsetX: 5,
      offsetY: 5,
    };

    result.current.drawPathWithShadow(mockContext, mockPath, shadow);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.shadowColor).toBe(shadow.color);
    expect(mockContext.shadowBlur).toBe(shadow.blur);
    expect(mockContext.shadowOffsetX).toBe(shadow.offsetX);
    expect(mockContext.shadowOffsetY).toBe(shadow.offsetY);
    expect(mockContext.fill).toHaveBeenCalledWith(mockPath);
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should create inner shadow', () => {
    const { result } = renderHook(() => useCanvasShadows());

    const shadow = {
      color: '#000000',
      blur: 10,
      offsetX: 5,
      offsetY: 5,
    };

    result.current.createInnerShadow(mockContext, 0, 0, 100, 100, shadow);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.rect).toHaveBeenCalledWith(0, 0, 100, 100);
    expect(mockContext.clip).toHaveBeenCalled();
    expect(mockContext.shadowColor).toBe(shadow.color);
    expect(mockContext.shadowBlur).toBe(shadow.blur);
    expect(mockContext.shadowOffsetX).toBe(shadow.offsetX);
    expect(mockContext.shadowOffsetY).toBe(shadow.offsetY);
    expect(mockContext.fillStyle).toBe('black');
    expect(mockContext.fillRect).toHaveBeenCalledWith(-100, -100, 300, 300);
    expect(mockContext.restore).toHaveBeenCalled();
  });
});
