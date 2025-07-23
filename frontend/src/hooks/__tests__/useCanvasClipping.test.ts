import { renderHook } from '@testing-library/react-hooks';
import { useCanvasClipping } from '../useCanvasClipping';

describe('useCanvasClipping', () => {
  let mockContext: CanvasRenderingContext2D;
  let mockPath: Path2D;

  beforeEach(() => {
    mockContext = {
      beginPath: jest.fn(),
      rect: jest.fn(),
      arc: jest.fn(),
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      quadraticCurveTo: jest.fn(),
      closePath: jest.fn(),
      clip: jest.fn(),
      fillText: jest.fn(),
      save: jest.fn(),
      restore: jest.fn(),
    } as unknown as CanvasRenderingContext2D;

    mockPath = new Path2D();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should create rectangular clip', () => {
    const { result } = renderHook(() => useCanvasClipping());

    const config = {
      x: 0,
      y: 0,
      width: 100,
      height: 100,
    };

    result.current.clipRect(mockContext, config);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.rect).toHaveBeenCalledWith(0, 0, 100, 100);
    expect(mockContext.clip).toHaveBeenCalled();
  });

  it('should create circular clip', () => {
    const { result } = renderHook(() => useCanvasClipping());

    result.current.clipCircle(mockContext, 50, 50, 25);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.arc).toHaveBeenCalledWith(50, 50, 25, 0, Math.PI * 2);
    expect(mockContext.clip).toHaveBeenCalled();
  });

  it('should create rounded rectangle clip', () => {
    const { result } = renderHook(() => useCanvasClipping());

    const config = {
      x: 0,
      y: 0,
      width: 100,
      height: 100,
      radius: 10,
    };

    result.current.clipRoundedRect(mockContext, config);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(10, 0);
    expect(mockContext.quadraticCurveTo).toHaveBeenCalled();
    expect(mockContext.closePath).toHaveBeenCalled();
    expect(mockContext.clip).toHaveBeenCalled();
  });

  it('should create path clip', () => {
    const { result } = renderHook(() => useCanvasClipping());

    result.current.clipPath(mockContext, mockPath);

    expect(mockContext.clip).toHaveBeenCalledWith(mockPath);
  });

  it('should create polygon clip', () => {
    const { result } = renderHook(() => useCanvasClipping());

    const points = [
      { x: 0, y: 0 },
      { x: 100, y: 0 },
      { x: 100, y: 100 },
      { x: 0, y: 100 },
    ];

    result.current.clipPolygon(mockContext, points);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.lineTo).toHaveBeenCalledTimes(3);
    expect(mockContext.closePath).toHaveBeenCalled();
    expect(mockContext.clip).toHaveBeenCalled();
  });

  it('should create text clip', () => {
    const { result } = renderHook(() => useCanvasClipping());

    result.current.clipText(mockContext, 'Test Text', 0, 0);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.fillText).toHaveBeenCalledWith('Test Text', 0, 0);
    expect(mockContext.clip).toHaveBeenCalled();
  });

  it('should save clip state', () => {
    const { result } = renderHook(() => useCanvasClipping());

    result.current.saveClipState(mockContext);

    expect(mockContext.save).toHaveBeenCalled();
  });

  it('should restore clip state', () => {
    const { result } = renderHook(() => useCanvasClipping());

    result.current.restoreClipState(mockContext);

    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should handle rounded rectangle clip with no radius', () => {
    const { result } = renderHook(() => useCanvasClipping());

    const config = {
      x: 0,
      y: 0,
      width: 100,
      height: 100,
    };

    result.current.clipRoundedRect(mockContext, config);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.quadraticCurveTo).not.toHaveBeenCalled();
    expect(mockContext.closePath).toHaveBeenCalled();
    expect(mockContext.clip).toHaveBeenCalled();
  });

  it('should handle polygon clip with less than 3 points', () => {
    const { result } = renderHook(() => useCanvasClipping());

    const points = [
      { x: 0, y: 0 },
      { x: 100, y: 0 },
    ];

    result.current.clipPolygon(mockContext, points);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.lineTo).toHaveBeenCalledTimes(1);
    expect(mockContext.closePath).toHaveBeenCalled();
    expect(mockContext.clip).toHaveBeenCalled();
  });
});
