import { renderHook  } from '@testing-library/react';
import { useCanvasLines } from '../useCanvasLines';

describe('useCanvasLines', () => {
  let mockContext: CanvasRenderingContext2D;

  beforeEach(() => {
    mockContext = {
      strokeStyle: '#000000',
      lineWidth: 1,
      lineCap: 'butt',
      lineJoin: 'miter',
      setLineDash: jest.fn(),
      lineDashOffset: 0,
      save: jest.fn(),
      restore: jest.fn(),
      beginPath: jest.fn(),
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      stroke: jest.fn(),
    } as unknown as CanvasRenderingContext2D;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should set line style', () => {
    const { result } = renderHook(() => useCanvasLines());

    const style = {
      color: '#ff0000',
      width: 2,
      cap: 'round' as CanvasLineCap,
      join: 'bevel' as CanvasLineJoin,
      dash: [5, 5],
      dashOffset: 2,
    };

    result.current.setLineStyle(mockContext, style);

    expect(mockContext.strokeStyle).toBe(style.color);
    expect(mockContext.lineWidth).toBe(style.width);
    expect(mockContext.lineCap).toBe(style.cap);
    expect(mockContext.lineJoin).toBe(style.join);
    expect(mockContext.setLineDash).toHaveBeenCalledWith(style.dash);
    expect(mockContext.lineDashOffset).toBe(style.dashOffset);
  });

  it('should draw line', () => {
    const { result } = renderHook(() => useCanvasLines());

    const style = {
      color: '#ff0000',
      width: 2,
    };

    result.current.drawLine(mockContext, 0, 0, 100, 100, style);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.lineTo).toHaveBeenCalledWith(100, 100);
    expect(mockContext.stroke).toHaveBeenCalled();
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw polyline', () => {
    const { result } = renderHook(() => useCanvasLines());

    const points = [
      { x: 0, y: 0 },
      { x: 50, y: 50 },
      { x: 100, y: 0 },
    ];

    const style = {
      color: '#ff0000',
      width: 2,
    };

    result.current.drawPolyline(mockContext, points, style);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.lineTo).toHaveBeenCalledTimes(2);
    expect(mockContext.stroke).toHaveBeenCalled();
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw curve', () => {
    const { result } = renderHook(() => useCanvasLines());

    const points = [
      { x: 0, y: 0 },
      { x: 50, y: 50 },
      { x: 100, y: 0 },
    ];

    const style = {
      color: '#ff0000',
      width: 2,
    };

    result.current.drawCurve(mockContext, points, style);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.stroke).toHaveBeenCalled();
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw arrow line', () => {
    const { result } = renderHook(() => useCanvasLines());

    const style = {
      color: '#ff0000',
      width: 2,
    };

    result.current.drawArrowLine(mockContext, 0, 0, 100, 100, style);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.lineTo).toHaveBeenCalledWith(100, 100);
    expect(mockContext.stroke).toHaveBeenCalled();
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw dashed line', () => {
    const { result } = renderHook(() => useCanvasLines());

    const style = {
      color: '#ff0000',
      width: 2,
    };

    result.current.drawDashedLine(mockContext, 0, 0, 100, 100, style);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.lineTo).toHaveBeenCalledWith(100, 100);
    expect(mockContext.stroke).toHaveBeenCalled();
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should draw grid', () => {
    const { result } = renderHook(() => useCanvasLines());

    const style = {
      color: '#ff0000',
      width: 1,
    };

    result.current.drawGrid(mockContext, 100, 100, 20, style);

    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalled();
    expect(mockContext.lineTo).toHaveBeenCalled();
    expect(mockContext.stroke).toHaveBeenCalled();
    expect(mockContext.restore).toHaveBeenCalled();
  });

  it('should handle empty points array in polyline', () => {
    const { result } = renderHook(() => useCanvasLines());

    const style = {
      color: '#ff0000',
      width: 2,
    };

    result.current.drawPolyline(mockContext, [], style);

    expect(mockContext.beginPath).not.toHaveBeenCalled();
    expect(mockContext.stroke).not.toHaveBeenCalled();
  });

  it('should handle single point in polyline', () => {
    const { result } = renderHook(() => useCanvasLines());

    const points = [{ x: 0, y: 0 }];
    const style = {
      color: '#ff0000',
      width: 2,
    };

    result.current.drawPolyline(mockContext, points, style);

    expect(mockContext.beginPath).toHaveBeenCalled();
    expect(mockContext.moveTo).toHaveBeenCalledWith(0, 0);
    expect(mockContext.lineTo).not.toHaveBeenCalled();
    expect(mockContext.stroke).toHaveBeenCalled();
  });
});
