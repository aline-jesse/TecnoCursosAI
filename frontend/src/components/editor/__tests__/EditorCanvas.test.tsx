import { fireEvent, render, screen } from '@testing-library/react';
import { useEditorStore } from '../../../store/editorStore';
import EditorCanvas from '../EditorCanvas';

// Mock do useEditorStore
jest.mock('../../../store/editorStore', () => ({
  useEditorStore: jest.fn(),
}));

// Mock do canvas
const mockCanvas = {
  getContext: jest.fn(() => ({
    save: jest.fn(),
    restore: jest.fn(),
    scale: jest.fn(),
    clearRect: jest.fn(),
    fillRect: jest.fn(),
    fillStyle: '#ffffff',
    strokeStyle: '#000000',
    lineWidth: 1,
    lineCap: 'butt',
    lineJoin: 'miter',
    setLineDash: jest.fn(),
    lineDashOffset: 0,
    shadowColor: 'transparent',
    shadowBlur: 0,
    shadowOffsetX: 0,
    shadowOffsetY: 0,
    globalAlpha: 1,
    globalCompositeOperation: 'source-over',
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
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
    fill: jest.fn(),
    stroke: jest.fn(),
    clip: jest.fn(),
    drawImage: jest.fn(),
    fillText: jest.fn(),
    strokeText: jest.fn(),
    measureText: jest.fn(),
    createLinearGradient: jest.fn(),
    createRadialGradient: jest.fn(),
    createPattern: jest.fn(),
    createImageData: jest.fn(),
    getImageData: jest.fn(),
    putImageData: jest.fn(),
    isPointInPath: jest.fn(),
    isPointInStroke: jest.fn(),
  })),
  style: {},
  width: 800,
  height: 600,
  getBoundingClientRect: jest.fn(() => ({
    left: 0,
    top: 0,
    width: 800,
    height: 600,
  })),
};

// Mock do window.devicePixelRatio
Object.defineProperty(window, 'devicePixelRatio', {
  value: 1,
  writable: true,
});

// Mock do requestAnimationFrame
global.requestAnimationFrame = jest.fn(callback => setTimeout(callback, 0));
global.cancelAnimationFrame = jest.fn();

describe('EditorCanvas', () => {
  beforeEach(() => {
    // Limpar todos os mocks
    jest.clearAllMocks();

    // Mock do createElement para canvas
    const createElement = document.createElement.bind(document);
    document.createElement = jest.fn(tagName => {
      if (tagName === 'canvas') {
        return mockCanvas;
      }
      return createElement(tagName);
    });

    // Mock do estado inicial do editor
    (useEditorStore as jest.Mock).mockImplementation(() => ({
      scenes: [],
      currentScene: null,
      selectedElement: null,
      updateScene: jest.fn(),
      addElement: jest.fn(),
      updateElement: jest.fn(),
      deleteElement: jest.fn(),
      setSelectedElement: jest.fn(),
    }));
  });

  it('renderiza corretamente com props padrão', () => {
    render(<EditorCanvas width={800} height={600} backgroundColor='#ffffff' />);

    const canvas = screen.getByRole('presentation');
    expect(canvas).toBeInTheDocument();
    expect(canvas).toHaveStyle({
      width: '800px',
      height: '600px',
    });
  });

  it('configura o canvas com o devicePixelRatio correto', () => {
    window.devicePixelRatio = 2;

    render(<EditorCanvas width={800} height={600} backgroundColor='#ffffff' />);

    expect(mockCanvas.width).toBe(1600);
    expect(mockCanvas.height).toBe(1200);
    expect(mockCanvas.style.width).toBe('800px');
    expect(mockCanvas.style.height).toBe('600px');
    expect(mockCanvas.getContext).toHaveBeenCalledWith('2d');
    expect(mockCanvas.getContext().scale).toHaveBeenCalledWith(2, 2);
  });

  it('responde a eventos do mouse corretamente', () => {
    const onElementSelect = jest.fn();
    const onElementUpdate = jest.fn();

    render(
      <EditorCanvas
        width={800}
        height={600}
        backgroundColor='#ffffff'
        onElementSelect={onElementSelect}
        onElementUpdate={onElementUpdate}
      />
    );

    const canvas = screen.getByRole('presentation');

    // Simular mousedown
    fireEvent.mouseDown(canvas, {
      clientX: 100,
      clientY: 100,
    });

    // Simular mousemove
    fireEvent.mouseMove(canvas, {
      clientX: 150,
      clientY: 150,
    });

    // Simular mouseup
    fireEvent.mouseUp(canvas);

    // Verificar se os handlers foram chamados
    expect(onElementSelect).toHaveBeenCalled();
  });

  it('aplica transformações corretamente', () => {
    render(<EditorCanvas width={800} height={600} backgroundColor='#ffffff' />);

    const canvas = screen.getByRole('presentation');

    // Simular zoom
    fireEvent.wheel(canvas, {
      deltaY: -100,
      ctrlKey: true,
    });

    // Simular rotação
    fireEvent.wheel(canvas, {
      deltaY: 100,
      shiftKey: true,
    });

    // Verificar se as transformações foram aplicadas
    expect(mockCanvas.getContext().scale).toHaveBeenCalled();
    expect(mockCanvas.getContext().rotate).toHaveBeenCalled();
  });

  it('renderiza elementos da cena corretamente', () => {
    const mockScene = {
      id: '1',
      elements: [
        {
          id: '1',
          type: 'text',
          x: 100,
          y: 100,
          width: 200,
          height: 50,
          text: 'Test Text',
          fontSize: 24,
          fontFamily: 'Arial',
          fill: '#000000',
        },
        {
          id: '2',
          type: 'image',
          x: 300,
          y: 100,
          width: 200,
          height: 200,
          src: 'test.jpg',
        },
      ],
    };

    (useEditorStore as jest.Mock).mockImplementation(() => ({
      scenes: [mockScene],
      currentScene: mockScene,
      selectedElement: null,
      updateScene: jest.fn(),
      addElement: jest.fn(),
      updateElement: jest.fn(),
      deleteElement: jest.fn(),
      setSelectedElement: jest.fn(),
    }));

    render(<EditorCanvas width={800} height={600} backgroundColor='#ffffff' />);

    // Verificar se os elementos foram renderizados
    expect(mockCanvas.getContext().fillText).toHaveBeenCalled();
    expect(mockCanvas.getContext().drawImage).toHaveBeenCalled();
  });

  it('limpa o canvas ao desmontar', () => {
    const { unmount } = render(
      <EditorCanvas width={800} height={600} backgroundColor='#ffffff' />
    );

    unmount();

    expect(mockCanvas.getContext().clearRect).toHaveBeenCalledWith(
      0,
      0,
      800,
      600
    );
  });
});
