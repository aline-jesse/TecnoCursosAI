import '@testing-library/jest-dom';

// Mock do requestAnimationFrame
global.requestAnimationFrame = callback => {
  return setTimeout(callback, 0);
};

// Mock do cancelAnimationFrame
global.cancelAnimationFrame = id => {
  clearTimeout(id);
};

// Mock do getContext do canvas
const mockContext = {
  clearRect: jest.fn(),
  drawImage: jest.fn(),
  fillRect: jest.fn(),
  fillText: jest.fn(),
  save: jest.fn(),
  restore: jest.fn(),
  translate: jest.fn(),
  rotate: jest.fn(),
  scale: jest.fn(),
  beginPath: jest.fn(),
  arc: jest.fn(),
  fill: jest.fn(),
  stroke: jest.fn(),
  strokeRect: jest.fn(),
  font: '',
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 0,
  globalAlpha: 1,
  textAlign: 'start' as CanvasTextAlign,
  canvas: document.createElement('canvas'),
  getContextAttributes: jest.fn(() => ({
    alpha: true,
    colorSpace: 'srgb',
    desynchronized: false,
    willReadFrequently: false,
  })),
  globalCompositeOperation: 'source-over',
  imageSmoothingEnabled: true,
  imageSmoothingQuality: 'low' as ImageSmoothingQuality,
  lineCap: 'butt' as CanvasLineCap,
  lineDashOffset: 0,
  lineJoin: 'miter' as CanvasLineJoin,
  miterLimit: 10,
  shadowBlur: 0,
  shadowColor: '#000000',
  shadowOffsetX: 0,
  shadowOffsetY: 0,
  direction: 'ltr',
  textBaseline: 'alphabetic' as CanvasTextBaseline,
  clip: jest.fn(),
  createImageData: jest.fn(),
  createLinearGradient: jest.fn(),
  createPattern: jest.fn(),
  createRadialGradient: jest.fn(),
  ellipse: jest.fn(),
  getImageData: jest.fn(),
  getLineDash: jest.fn(() => []),
  getTransform: jest.fn(),
  isPointInPath: jest.fn(),
  isPointInStroke: jest.fn(),
  measureText: jest.fn(() => ({
    width: 0,
    actualBoundingBoxAscent: 0,
    actualBoundingBoxDescent: 0,
    actualBoundingBoxLeft: 0,
    actualBoundingBoxRight: 0,
    fontBoundingBoxAscent: 0,
    fontBoundingBoxDescent: 0,
  })),
  putImageData: jest.fn(),
  quadraticCurveTo: jest.fn(),
  rect: jest.fn(),
  resetTransform: jest.fn(),
  setLineDash: jest.fn(),
  setTransform: jest.fn(),
  strokeText: jest.fn(),
  transform: jest.fn(),
};

// Sobrescrever o tipo original do getContext
declare global {
  interface HTMLCanvasElement {
    getContext(contextId: '2d'): CanvasRenderingContext2D | null;
    getContext(contextId: 'bitmaprenderer'): ImageBitmapRenderingContext | null;
    getContext(contextId: 'webgl' | 'webgl2'): WebGLRenderingContext | null;
    getContext(contextId: string): RenderingContext | null;
  }
}

// Implementar o mock
const getContextMock = jest.fn((contextId: string) => {
  if (contextId === '2d') {
    return mockContext as unknown as CanvasRenderingContext2D;
  }
  if (contextId === 'bitmaprenderer') {
    return {
      canvas: document.createElement('canvas'),
      transferFromImageBitmap: jest.fn(),
    } as unknown as ImageBitmapRenderingContext;
  }
  if (contextId === 'webgl' || contextId === 'webgl2') {
    return null;
  }
  return null;
});

HTMLCanvasElement.prototype.getContext = getContextMock;
