import { act, renderHook } from '@testing-library/react';
import { useCanvasShapes } from '../useCanvasShapes';

// Mock do canvas
const mockCanvasContext = {
  canvas: document.createElement('canvas'),
  getContextAttributes: jest.fn(() => ({
    alpha: true,
    desynchronized: false,
    colorSpace: 'srgb',
    willReadFrequently: false,
  })),
  save: jest.fn(),
  restore: jest.fn(),
  scale: jest.fn(),
  clearRect: jest.fn(),
  fillRect: jest.fn(),
  fillStyle: '#ffffff',
  strokeStyle: '#000000',
  lineWidth: 1,
  lineCap: 'butt' as CanvasLineCap,
  lineJoin: 'miter' as CanvasLineJoin,
  setLineDash: jest.fn(),
  lineDashOffset: 0,
  shadowColor: 'transparent',
  shadowBlur: 0,
  shadowOffsetX: 0,
  shadowOffsetY: 0,
  globalAlpha: 1,
  globalCompositeOperation: 'source-over' as GlobalCompositeOperation,
  imageSmoothingEnabled: true,
  imageSmoothingQuality: 'high' as ImageSmoothingQuality,
  filter: 'none',
  setTransform: jest.fn(),
  transform: jest.fn(),
  translate: jest.fn(),
  rotate: jest.fn(),
  beginPath: jest.fn(),
  closePath: jest.fn(),
  moveTo: jest.fn(),
  lineTo: jest.fn(),
  arc: jest.fn(),
  arcTo: jest.fn(),
  ellipse: jest.fn(),
  rect: jest.fn(),
  fill: jest.fn(),
  stroke: jest.fn(),
  clip: jest.fn(),
  isPointInPath: jest.fn(),
  isPointInStroke: jest.fn(),
  drawImage: jest.fn(),
  fillText: jest.fn(),
  strokeText: jest.fn(),
  measureText: jest.fn(),
  createLinearGradient: jest.fn(),
  createRadialGradient: jest.fn(),
  createConicGradient: jest.fn(),
  createPattern: jest.fn(),
  createImageData: jest.fn(),
  getImageData: jest.fn(),
  putImageData: jest.fn(),
  getTransform: jest.fn(),
  resetTransform: jest.fn(),
  direction: 'ltr',
  font: '10px sans-serif',
  textAlign: 'start' as CanvasTextAlign,
  textBaseline: 'alphabetic' as CanvasTextBaseline,
} as unknown as CanvasRenderingContext2D;

describe('useCanvasShapes', () => {
  beforeEach(() => {
    // Limpar todos os mocks
    jest.clearAllMocks();
  });

  it('retorna as funções esperadas', () => {
    const { result } = renderHook(() => useCanvasShapes());

    expect(result.current).toHaveProperty('setShapeStyle');
    expect(result.current).toHaveProperty('drawRect');
    expect(result.current).toHaveProperty('drawCircle');
    expect(result.current).toHaveProperty('drawEllipse');
    expect(result.current).toHaveProperty('drawPolygon');
    expect(result.current).toHaveProperty('drawRegularPolygon');
    expect(result.current).toHaveProperty('drawStar');
    expect(result.current).toHaveProperty('drawRoundedRect');
  });

  it('aplica estilo de forma corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const style = {
      color: '#ff0000',
      width: 2,
      cap: 'round' as CanvasLineCap,
      join: 'round' as CanvasLineJoin,
      dash: [5, 5],
      dashOffset: 2.5,
      alpha: 0.5,
    };

    act(() => {
      result.current.setShapeStyle(mockCanvasContext, style);
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.strokeStyle).toBe(style.color);
    expect(mockCanvasContext.lineWidth).toBe(style.width);
    expect(mockCanvasContext.lineCap).toBe(style.cap);
    expect(mockCanvasContext.lineJoin).toBe(style.join);
    expect(mockCanvasContext.setLineDash).toHaveBeenCalledWith(style.dash);
    expect(mockCanvasContext.lineDashOffset).toBe(style.dashOffset);
    expect(mockCanvasContext.globalAlpha).toBe(style.alpha);
  });

  it('desenha retângulo corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const style = {
      fill: '#ff0000',
      stroke: '#000000',
    };

    act(() => {
      result.current.drawRect(mockCanvasContext, 0, 0, 100, 100, style);
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.fillStyle).toBe(style.fill);
    expect(mockCanvasContext.strokeStyle).toBe(style.stroke);
    expect(mockCanvasContext.fillRect).toHaveBeenCalledWith(0, 0, 100, 100);
    expect(mockCanvasContext.strokeRect).toHaveBeenCalledWith(0, 0, 100, 100);
    expect(mockCanvasContext.restore).toHaveBeenCalled();
  });

  it('desenha círculo corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const style = {
      fill: '#ff0000',
      stroke: '#000000',
    };

    act(() => {
      result.current.drawCircle(mockCanvasContext, 50, 50, 25, style);
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.fillStyle).toBe(style.fill);
    expect(mockCanvasContext.strokeStyle).toBe(style.stroke);
    expect(mockCanvasContext.beginPath).toHaveBeenCalled();
    expect(mockCanvasContext.arc).toHaveBeenCalledWith(
      50,
      50,
      25,
      0,
      Math.PI * 2
    );
    expect(mockCanvasContext.fill).toHaveBeenCalled();
    expect(mockCanvasContext.stroke).toHaveBeenCalled();
    expect(mockCanvasContext.restore).toHaveBeenCalled();
  });

  it('desenha elipse corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const style = {
      fill: '#ff0000',
      stroke: '#000000',
    };

    act(() => {
      result.current.drawEllipse(
        mockCanvasContext,
        50,
        50,
        40,
        20,
        Math.PI / 4,
        style
      );
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.fillStyle).toBe(style.fill);
    expect(mockCanvasContext.strokeStyle).toBe(style.stroke);
    expect(mockCanvasContext.beginPath).toHaveBeenCalled();
    expect(mockCanvasContext.ellipse).toHaveBeenCalledWith(
      50,
      50,
      40,
      20,
      Math.PI / 4,
      0,
      Math.PI * 2
    );
    expect(mockCanvasContext.fill).toHaveBeenCalled();
    expect(mockCanvasContext.stroke).toHaveBeenCalled();
    expect(mockCanvasContext.restore).toHaveBeenCalled();
  });

  it('desenha polígono corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const points = [
      { x: 0, y: 0 },
      { x: 100, y: 0 },
      { x: 100, y: 100 },
      { x: 0, y: 100 },
    ];

    const style = {
      fill: '#ff0000',
      stroke: '#000000',
    };

    act(() => {
      result.current.drawPolygon(mockCanvasContext, points, style);
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.fillStyle).toBe(style.fill);
    expect(mockCanvasContext.strokeStyle).toBe(style.stroke);
    expect(mockCanvasContext.beginPath).toHaveBeenCalled();
    expect(mockCanvasContext.moveTo).toHaveBeenCalledWith(
      points[0].x,
      points[0].y
    );
    points.slice(1).forEach(point => {
      expect(mockCanvasContext.lineTo).toHaveBeenCalledWith(point.x, point.y);
    });
    expect(mockCanvasContext.closePath).toHaveBeenCalled();
    expect(mockCanvasContext.fill).toHaveBeenCalled();
    expect(mockCanvasContext.stroke).toHaveBeenCalled();
    expect(mockCanvasContext.restore).toHaveBeenCalled();
  });

  it('desenha polígono regular corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const style = {
      fill: '#ff0000',
      stroke: '#000000',
    };

    act(() => {
      result.current.drawRegularPolygon(
        mockCanvasContext,
        50,
        50,
        25,
        6,
        0,
        style
      );
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.fillStyle).toBe(style.fill);
    expect(mockCanvasContext.strokeStyle).toBe(style.stroke);
    expect(mockCanvasContext.beginPath).toHaveBeenCalled();
    expect(mockCanvasContext.moveTo).toHaveBeenCalled();
    expect(mockCanvasContext.lineTo).toHaveBeenCalledTimes(6);
    expect(mockCanvasContext.closePath).toHaveBeenCalled();
    expect(mockCanvasContext.fill).toHaveBeenCalled();
    expect(mockCanvasContext.stroke).toHaveBeenCalled();
    expect(mockCanvasContext.restore).toHaveBeenCalled();
  });

  it('desenha estrela corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const style = {
      fill: '#ff0000',
      stroke: '#000000',
    };

    act(() => {
      result.current.drawStar(mockCanvasContext, 50, 50, 40, 20, 5, 0, style);
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.fillStyle).toBe(style.fill);
    expect(mockCanvasContext.strokeStyle).toBe(style.stroke);
    expect(mockCanvasContext.beginPath).toHaveBeenCalled();
    expect(mockCanvasContext.moveTo).toHaveBeenCalled();
    expect(mockCanvasContext.lineTo).toHaveBeenCalledTimes(10);
    expect(mockCanvasContext.closePath).toHaveBeenCalled();
    expect(mockCanvasContext.fill).toHaveBeenCalled();
    expect(mockCanvasContext.stroke).toHaveBeenCalled();
    expect(mockCanvasContext.restore).toHaveBeenCalled();
  });

  it('desenha retângulo arredondado corretamente', () => {
    const { result } = renderHook(() => useCanvasShapes());

    const style = {
      fill: '#ff0000',
      stroke: '#000000',
    };

    act(() => {
      result.current.drawRoundedRect(
        mockCanvasContext,
        0,
        0,
        100,
        100,
        10,
        style
      );
    });

    expect(mockCanvasContext.save).toHaveBeenCalled();
    expect(mockCanvasContext.fillStyle).toBe(style.fill);
    expect(mockCanvasContext.strokeStyle).toBe(style.stroke);
    expect(mockCanvasContext.beginPath).toHaveBeenCalled();
    expect(mockCanvasContext.moveTo).toHaveBeenCalled();
    expect(mockCanvasContext.lineTo).toHaveBeenCalled();
    expect(mockCanvasContext.quadraticCurveTo).toHaveBeenCalled();
    expect(mockCanvasContext.closePath).toHaveBeenCalled();
    expect(mockCanvasContext.fill).toHaveBeenCalled();
    expect(mockCanvasContext.stroke).toHaveBeenCalled();
    expect(mockCanvasContext.restore).toHaveBeenCalled();
  });
});
