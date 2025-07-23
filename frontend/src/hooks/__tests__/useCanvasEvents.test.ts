import { renderHook } from '@testing-library/react-hooks';
import { useCanvasEvents } from '../useCanvasEvents';

describe('useCanvasEvents', () => {
  const mockElement = {
    id: 'test-element',
    type: 'text',
    x: 100,
    y: 100,
    width: 200,
    height: 100,
    text: 'Test',
    fontSize: 16,
    fontFamily: 'Arial',
    fill: '#000000',
  };

  const mockHandlers = {
    onElementSelect: jest.fn(),
    onElementUpdate: jest.fn(),
    onSceneUpdate: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should handle mouse down event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new MouseEvent('mousedown', {
      clientX: 150,
      clientY: 150,
    });

    const canvas = document.createElement('canvas');
    canvas.getBoundingClientRect = jest.fn(() => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600,
    }));

    Object.defineProperty(mockEvent, 'target', { value: canvas });
    result.current.handleMouseDown(mockEvent);

    // Verificar se o evento foi processado corretamente
    expect(canvas.getBoundingClientRect).toHaveBeenCalled();
  });

  it('should handle mouse move event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new MouseEvent('mousemove', {
      clientX: 150,
      clientY: 150,
    });

    const canvas = document.createElement('canvas');
    canvas.getBoundingClientRect = jest.fn(() => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600,
    }));

    Object.defineProperty(mockEvent, 'target', { value: canvas });
    result.current.handleMouseMove(mockEvent);

    // Verificar se o evento foi processado corretamente
    expect(canvas.getBoundingClientRect).toHaveBeenCalled();
  });

  it('should handle mouse up event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new MouseEvent('mouseup', {
      clientX: 150,
      clientY: 150,
    });

    const canvas = document.createElement('canvas');
    canvas.getBoundingClientRect = jest.fn(() => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600,
    }));

    Object.defineProperty(mockEvent, 'target', { value: canvas });
    result.current.handleMouseUp(mockEvent);

    // Verificar se o evento foi processado corretamente
    expect(canvas.getBoundingClientRect).toHaveBeenCalled();
  });

  it('should handle wheel event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new WheelEvent('wheel', {
      deltaY: 100,
      clientX: 150,
      clientY: 150,
    });

    const canvas = document.createElement('canvas');
    canvas.getBoundingClientRect = jest.fn(() => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600,
    }));

    Object.defineProperty(mockEvent, 'target', { value: canvas });
    result.current.handleWheel(mockEvent);

    // Verificar se o evento foi processado corretamente
    expect(canvas.getBoundingClientRect).toHaveBeenCalled();
  });

  it('should handle key down event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new KeyboardEvent('keydown', {
      key: 'Delete',
    });

    result.current.handleKeyDown(mockEvent);

    // Verificar se o evento foi processado corretamente
    // Aqui você pode adicionar mais verificações específicas
    // dependendo da implementação do handleKeyDown
  });

  it('should handle key up event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new KeyboardEvent('keyup', {
      key: 'Delete',
    });

    result.current.handleKeyUp(mockEvent);

    // Verificar se o evento foi processado corretamente
    // Aqui você pode adicionar mais verificações específicas
    // dependendo da implementação do handleKeyUp
  });

  it('should handle double click event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new MouseEvent('dblclick', {
      clientX: 150,
      clientY: 150,
    });

    const canvas = document.createElement('canvas');
    canvas.getBoundingClientRect = jest.fn(() => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600,
    }));

    Object.defineProperty(mockEvent, 'target', { value: canvas });
    result.current.handleDoubleClick(mockEvent);

    // Verificar se o evento foi processado corretamente
    expect(canvas.getBoundingClientRect).toHaveBeenCalled();
  });

  it('should handle context menu event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new MouseEvent('contextmenu', {
      clientX: 150,
      clientY: 150,
    });

    const canvas = document.createElement('canvas');
    canvas.getBoundingClientRect = jest.fn(() => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600,
    }));

    Object.defineProperty(mockEvent, 'target', { value: canvas });
    const preventDefault = jest.fn();
    Object.defineProperty(mockEvent, 'preventDefault', {
      value: preventDefault,
    });

    result.current.handleContextMenu(mockEvent);

    // Verificar se o evento foi processado corretamente
    expect(preventDefault).toHaveBeenCalled();
    expect(canvas.getBoundingClientRect).toHaveBeenCalled();
  });

  it('should handle drag events', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new DragEvent('dragenter');
    const preventDefault = jest.fn();
    Object.defineProperty(mockEvent, 'preventDefault', {
      value: preventDefault,
    });

    result.current.handleDragEnter(mockEvent);
    expect(preventDefault).toHaveBeenCalled();

    result.current.handleDragOver(mockEvent);
    expect(preventDefault).toHaveBeenCalledTimes(2);

    result.current.handleDragLeave(mockEvent);
    expect(preventDefault).toHaveBeenCalledTimes(3);
  });

  it('should handle drop event', () => {
    const { result } = renderHook(() => useCanvasEvents(mockHandlers));

    const mockEvent = new DragEvent('drop', {
      clientX: 150,
      clientY: 150,
    });

    const canvas = document.createElement('canvas');
    canvas.getBoundingClientRect = jest.fn(() => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600,
    }));

    Object.defineProperty(mockEvent, 'target', { value: canvas });
    const preventDefault = jest.fn();
    Object.defineProperty(mockEvent, 'preventDefault', {
      value: preventDefault,
    });

    result.current.handleDrop(mockEvent);

    // Verificar se o evento foi processado corretamente
    expect(preventDefault).toHaveBeenCalled();
    expect(canvas.getBoundingClientRect).toHaveBeenCalled();
  });
});
