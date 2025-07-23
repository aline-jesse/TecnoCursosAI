import { renderHook } from '@testing-library/react-hooks';
import { useCanvasGradients } from '../useCanvasGradients';

describe('useCanvasGradients', () => {
  let mockContext: CanvasRenderingContext2D;
  let mockGradient: CanvasGradient;

  beforeEach(() => {
    mockGradient = {
      addColorStop: jest.fn(),
    } as unknown as CanvasGradient;

    mockContext = {
      createLinearGradient: jest.fn().mockReturnValue(mockGradient),
      createRadialGradient: jest.fn().mockReturnValue(mockGradient),
      createConicGradient: jest.fn().mockReturnValue(mockGradient),
      fillStyle: '#000000',
      strokeStyle: '#000000',
      fillRect: jest.fn(),
      strokeRect: jest.fn(),
      fillText: jest.fn(),
    } as unknown as CanvasRenderingContext2D;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should create linear gradient', () => {
    const { result } = renderHook(() => useCanvasGradients());

    const config = {
      x1: 0,
      y1: 0,
      x2: 100,
      y2: 100,
      stops: [
        { offset: 0, color: '#000000' },
        { offset: 1, color: '#ffffff' },
      ],
    };

    const gradient = result.current.createLinearGradient(mockContext, config);

    expect(mockContext.createLinearGradient).toHaveBeenCalledWith(
      0,
      0,
      100,
      100
    );
    expect(mockGradient.addColorStop).toHaveBeenCalledTimes(2);
    expect(mockGradient.addColorStop).toHaveBeenCalledWith(0, '#000000');
    expect(mockGradient.addColorStop).toHaveBeenCalledWith(1, '#ffffff');
    expect(gradient).toBe(mockGradient);
  });

  it('should create radial gradient', () => {
    const { result } = renderHook(() => useCanvasGradients());

    const config = {
      x1: 50,
      y1: 50,
      r1: 10,
      x2: 50,
      y2: 50,
      r2: 50,
      stops: [
        { offset: 0, color: '#000000' },
        { offset: 1, color: '#ffffff' },
      ],
    };

    const gradient = result.current.createRadialGradient(mockContext, config);

    expect(mockContext.createRadialGradient).toHaveBeenCalledWith(
      50,
      50,
      10,
      50,
      50,
      50
    );
    expect(mockGradient.addColorStop).toHaveBeenCalledTimes(2);
    expect(mockGradient.addColorStop).toHaveBeenCalledWith(0, '#000000');
    expect(mockGradient.addColorStop).toHaveBeenCalledWith(1, '#ffffff');
    expect(gradient).toBe(mockGradient);
  });

  it('should create conic gradient', () => {
    const { result } = renderHook(() => useCanvasGradients());

    const config = {
      x: 50,
      y: 50,
      angle: Math.PI / 4,
      stops: [
        { offset: 0, color: '#000000' },
        { offset: 1, color: '#ffffff' },
      ],
    };

    const gradient = result.current.createConicGradient(mockContext, config);

    expect(mockContext.createConicGradient).toHaveBeenCalledWith(
      Math.PI / 4,
      50,
      50
    );
    expect(mockGradient.addColorStop).toHaveBeenCalledTimes(2);
    expect(mockGradient.addColorStop).toHaveBeenCalledWith(0, '#000000');
    expect(mockGradient.addColorStop).toHaveBeenCalledWith(1, '#ffffff');
    expect(gradient).toBe(mockGradient);
  });

  it('should fill with gradient', () => {
    const { result } = renderHook(() => useCanvasGradients());

    result.current.fillWithGradient(mockContext, mockGradient, 0, 0, 100, 100);

    expect(mockContext.fillStyle).toBe(mockGradient);
    expect(mockContext.fillRect).toHaveBeenCalledWith(0, 0, 100, 100);
  });

  it('should stroke with gradient', () => {
    const { result } = renderHook(() => useCanvasGradients());

    result.current.strokeWithGradient(
      mockContext,
      mockGradient,
      0,
      0,
      100,
      100
    );

    expect(mockContext.strokeStyle).toBe(mockGradient);
    expect(mockContext.strokeRect).toHaveBeenCalledWith(0, 0, 100, 100);
  });

  it('should create text gradient', () => {
    const { result } = renderHook(() => useCanvasGradients());

    result.current.createTextGradient(
      mockContext,
      'Test Text',
      0,
      0,
      mockGradient
    );

    expect(mockContext.fillStyle).toBe(mockGradient);
    expect(mockContext.fillText).toHaveBeenCalledWith('Test Text', 0, 0);
  });
});
