/**
 * Configuração de testes para React Testing Library e Jest
 * Inclui mocks necessários para canvas e eventos
 */

// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock para react-konva
jest.mock('react-konva', () => ({
  Stage: ({ children, ...props }) => (
    <div data-testid='stage' {...props}>
      {children}
    </div>
  ),
  Layer: ({ children, ...props }) => (
    <div data-testid='layer' {...props}>
      {children}
    </div>
  ),
  Text: ({ children, ...props }) => (
    <div data-testid='text' {...props}>
      {children}
    </div>
  ),
  Image: ({ children, ...props }) => (
    <div data-testid='image' {...props}>
      {children}
    </div>
  ),
  Transformer: ({ children, ...props }) => (
    <div data-testid='transformer' {...props}>
      {children}
    </div>
  ),
}));

// Mock para use-image
jest.mock('use-image', () => () => [null, 'loaded']);

// Mock para fabric.js
global.fabric = {
  Canvas: jest.fn(),
  IText: jest.fn(),
  Rect: jest.fn(),
  Circle: jest.fn(),
  Image: {
    fromURL: jest.fn(() => Promise.resolve({})),
  },
  PencilBrush: jest.fn(),
};

// Mock para window.Image
global.Image = jest.fn(() => ({
  src: '',
  onload: jest.fn(),
  width: 100,
  height: 100,
}));

// Mock do canvas para testes
class MockCanvas {
  constructor() {
    this.width = 800;
    this.height = 600;
    this.style = {};
  }

  getContext(type) {
    if (type === '2d') {
      return {
        clearRect: jest.fn(),
        save: jest.fn(),
        restore: jest.fn(),
        translate: jest.fn(),
        rotate: jest.fn(),
        fillStyle: '',
        strokeStyle: '',
        lineWidth: 0,
        strokeRect: jest.fn(),
        fillRect: jest.fn(),
        beginPath: jest.fn(),
        arc: jest.fn(),
        fill: jest.fn(),
        stroke: jest.fn(),
        font: '',
        textBaseline: '',
        fillText: jest.fn(),
        drawImage: jest.fn(),
      };
    }
    return null;
  }

  getBoundingClientRect() {
    return {
      left: 0,
      top: 0,
      width: this.width,
      height: this.height,
    };
  }
}

// Mock global do canvas
global.HTMLCanvasElement.prototype.getContext = jest.fn(type => {
  if (type === '2d') {
    return {
      clearRect: jest.fn(),
      save: jest.fn(),
      restore: jest.fn(),
      translate: jest.fn(),
      rotate: jest.fn(),
      fillStyle: '',
      strokeStyle: '',
      lineWidth: 0,
      strokeRect: jest.fn(),
      fillRect: jest.fn(),
      beginPath: jest.fn(),
      arc: jest.fn(),
      fill: jest.fn(),
      stroke: jest.fn(),
      font: '',
      textBaseline: '',
      fillText: jest.fn(),
      drawImage: jest.fn(),
    };
  }
  return null;
});

// Mock do getBoundingClientRect
global.Element.prototype.getBoundingClientRect = jest.fn(() => ({
  left: 0,
  top: 0,
  width: 800,
  height: 600,
}));

// Mock do Image para carregamento de imagens
global.Image = class {
  constructor() {
    this.src = '';
    this.onload = null;
    this.onerror = null;
  }
};

// Mock do window.URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-url');

// Mock do window.URL.revokeObjectURL
global.URL.revokeObjectURL = jest.fn();

// Mock do console para suprimir warnings em testes
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Mock do ResizeObserver para evitar warnings
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock do IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock do matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock do requestAnimationFrame
global.requestAnimationFrame = jest.fn(callback => setTimeout(callback, 0));

// Mock do cancelAnimationFrame
global.cancelAnimationFrame = jest.fn(id => clearTimeout(id));
