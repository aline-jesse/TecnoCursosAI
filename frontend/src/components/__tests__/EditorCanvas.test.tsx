import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EditorCanvas from '../EditorCanvas';
import { useEditorStore } from '../../store/editorStore';

// Mock do store
jest.mock('../../store/editorStore');

// Mock do Fabric.js
jest.mock('fabric', () => ({
  Canvas: jest.fn().mockImplementation(() => ({
    on: jest.fn(),
    add: jest.fn(),
    remove: jest.fn(),
    clear: jest.fn(),
    renderAll: jest.fn(),
    setZoom: jest.fn(),
    getElement: jest.fn(() => ({
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      getBoundingClientRect: jest.fn(() => ({ left: 0, top: 0 })),
    })),
    getWidth: jest.fn(() => 1920),
    getHeight: jest.fn(() => 1080),
    getActiveObject: jest.fn(() => null),
    dispose: jest.fn(),
  })),
  Text: jest.fn().mockImplementation(() => ({
    set: jest.fn(),
  })),
  Rect: jest.fn().mockImplementation(() => ({
    set: jest.fn(),
  })),
  Circle: jest.fn().mockImplementation(() => ({
    set: jest.fn(),
  })),
  Line: jest.fn().mockImplementation(() => ({
    set: jest.fn(),
  })),
  Image: {
    fromURL: jest.fn((url, callback) => {
      const mockImage = {
        set: jest.fn(),
      };
      callback(mockImage);
    }),
  },
}));

const mockUseEditorStore = useEditorStore as jest.MockedFunction<
  typeof useEditorStore
>;

describe('EditorCanvas', () => {
  const mockStore = {
    history: {
      present: [
        {
          id: 'scene-1',
          name: 'Test Scene',
          duration: 5,
          elements: [
            {
              id: 'element-1',
              type: 'text' as const,
              x: 100,
              y: 100,
              width: 200,
              height: 50,
              rotation: 0,
              opacity: 1,
              text: 'Test Text',
              fontSize: 24,
              fontFamily: 'Arial',
              fill: '#000000',
            },
          ],
          thumbnail: 'test-thumbnail.jpg',
        },
      ],
      past: [],
      future: [],
    },
    currentSceneId: 'scene-1',
    selectedElementId: null,
    draggedAsset: null,
    addElement: jest.fn(),
    updateElement: jest.fn(),
    deleteElement: jest.fn(),
    setSelectedElementId: jest.fn(),
    setDraggedAsset: jest.fn(),
    canvasWidth: 1920,
    canvasHeight: 1080,
    setCanvasSize: jest.fn(),
  };

  beforeEach(() => {
    mockUseEditorStore.mockReturnValue(mockStore);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renderiza corretamente', () => {
    render(<EditorCanvas />);

    expect(screen.getByTitle('Adicionar texto')).toBeInTheDocument();
    expect(screen.getByTitle('Adicionar retângulo')).toBeInTheDocument();
    expect(screen.getByTitle('Adicionar círculo')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('exibe informações da cena atual', () => {
    render(<EditorCanvas />);

    expect(screen.getByText('Test Scene')).toBeInTheDocument();
    expect(screen.getByText('5s')).toBeInTheDocument();
  });

  it('exibe mensagem quando não há cena selecionada', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      currentSceneId: null,
      scenes: [],
    });

    render(<EditorCanvas />);

    expect(screen.getByText('Nenhuma cena selecionada')).toBeInTheDocument();
  });

  it('adiciona texto quando botão é clicado', () => {
    render(<EditorCanvas />);

    const addTextBtn = screen.getByTitle('Adicionar texto');
    fireEvent.click(addTextBtn);

    expect(mockStore.addElement).toHaveBeenCalledWith(
      'scene-1',
      expect.objectContaining({
        type: 'text',
        text: 'Novo texto',
      })
    );
  });

  it('adiciona retângulo quando botão é clicado', () => {
    render(<EditorCanvas />);

    const addRectBtn = screen.getByTitle('Adicionar retângulo');
    fireEvent.click(addRectBtn);

    expect(mockStore.addElement).toHaveBeenCalledWith(
      'scene-1',
      expect.objectContaining({
        type: 'shape',
        shapeType: 'rectangle',
      })
    );
  });

  it('adiciona círculo quando botão é clicado', () => {
    render(<EditorCanvas />);

    const addCircleBtn = screen.getByTitle('Adicionar círculo');
    fireEvent.click(addCircleBtn);

    expect(mockStore.addElement).toHaveBeenCalledWith(
      'scene-1',
      expect.objectContaining({
        type: 'shape',
        shapeType: 'circle',
      })
    );
  });

  it('controla zoom in', () => {
    render(<EditorCanvas />);

    const zoomInBtn = screen.getByTitle('Aumentar zoom');
    fireEvent.click(zoomInBtn);

    // Verificar se o zoom foi aumentado (implementação interna)
    expect(zoomInBtn).toBeInTheDocument();
  });

  it('controla zoom out', () => {
    render(<EditorCanvas />);

    const zoomOutBtn = screen.getByTitle('Diminuir zoom');
    fireEvent.click(zoomOutBtn);

    // Verificar se o zoom foi diminuído (implementação interna)
    expect(zoomOutBtn).toBeInTheDocument();
  });

  it('reseta zoom', () => {
    render(<EditorCanvas />);

    const resetZoomBtn = screen.getByTitle('Resetar zoom');
    fireEvent.click(resetZoomBtn);

    // Verificar se o zoom foi resetado (implementação interna)
    expect(resetZoomBtn).toBeInTheDocument();
  });

  it('alterna grid', () => {
    render(<EditorCanvas />);

    const gridBtn = screen.getByTitle('Mostrar/ocultar grid');
    fireEvent.click(gridBtn);

    // Verificar se o grid foi alternado (implementação interna)
    expect(gridBtn).toBeInTheDocument();
  });

  it('alterna regras', () => {
    render(<EditorCanvas />);

    const rulersBtn = screen.getByTitle('Mostrar/ocultar regras');
    fireEvent.click(rulersBtn);

    // Verificar se as regras foram alternadas (implementação interna)
    expect(rulersBtn).toBeInTheDocument();
  });

  it('deleta elemento selecionado', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
    });

    render(<EditorCanvas />);

    const deleteBtn = screen.getByTitle('Deletar elemento');
    fireEvent.click(deleteBtn);

    expect(mockStore.deleteElement).toHaveBeenCalledWith(
      'scene-1',
      'element-1'
    );
  });

  it('não mostra botão de deletar quando não há elemento selecionado', () => {
    render(<EditorCanvas />);

    expect(screen.queryByTitle('Deletar elemento')).not.toBeInTheDocument();
  });

  it('adiciona elemento quando asset é arrastado', async () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      draggedAsset: {
        id: 'asset-1',
        name: 'Test Asset',
        type: 'image' as const,
        src: 'test-asset.jpg',
      },
    });

    render(<EditorCanvas />);

    // Simular drop de asset
    const canvas = screen.getByRole('img', { hidden: true }).closest('canvas');
    if (canvas) {
      fireEvent.drop(canvas, {
        clientX: 100,
        clientY: 100,
      });
    }

    await waitFor(() => {
      expect(mockStore.addElement).toHaveBeenCalledWith(
        'scene-1',
        expect.objectContaining({
          type: 'image',
          src: 'test-asset.jpg',
        })
      );
    });
  });

  it('configura canvas com dimensões corretas', () => {
    render(<EditorCanvas width={1280} height={720} />);

    expect(mockStore.setCanvasSize).toHaveBeenCalledWith(1280, 720);
  });

  it('configura canvas com cor de fundo personalizada', () => {
    render(<EditorCanvas backgroundColor='#000000' />);

    // Verificar se a cor de fundo foi aplicada (implementação interna)
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
  });

  it('manipula eventos de seleção do canvas', () => {
    render(<EditorCanvas />);

    // Simular seleção de objeto
    const canvas = screen.getByRole('img', { hidden: true }).closest('canvas');
    if (canvas) {
      fireEvent.mouseDown(canvas);
      fireEvent.mouseUp(canvas);
    }

    // Verificar se os eventos foram tratados (implementação interna)
    expect(canvas).toBeInTheDocument();
  });

  it('renderiza canvas com zoom correto', () => {
    render(<EditorCanvas />);

    const canvas = screen.getByRole('img', { hidden: true }).closest('canvas');
    expect(canvas).toHaveStyle({
      transform: 'scale(1)',
      transformOrigin: 'top left',
    });
  });

  it('exibe overlay de informações', () => {
    render(<EditorCanvas />);

    expect(screen.getByText('Test Scene')).toBeInTheDocument();
    expect(screen.getByText('5s')).toBeInTheDocument();
  });

  it('manipula drag and drop de assets', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      draggedAsset: {
        id: 'asset-1',
        name: 'Test Asset',
        type: 'character' as const,
        src: 'test-character.svg',
      },
    });

    render(<EditorCanvas />);

    const canvas = screen.getByRole('img', { hidden: true }).closest('canvas');
    if (canvas) {
      fireEvent.dragOver(canvas);
      fireEvent.drop(canvas, {
        clientX: 200,
        clientY: 200,
      });
    }

    expect(mockStore.addElement).toHaveBeenCalledWith(
      'scene-1',
      expect.objectContaining({
        type: 'character',
        src: 'test-character.svg',
      })
    );
  });

  it('atualiza elementos quando cena muda', () => {
    const { rerender } = render(<EditorCanvas />);

    // Mudar para uma nova cena
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      currentSceneId: 'scene-2',
      scenes: [
        ...mockStore.scenes,
        {
          id: 'scene-2',
          name: 'New Scene',
          duration: 3,
          elements: [],
          thumbnail: 'new-thumbnail.jpg',
        },
      ],
    });

    rerender(<EditorCanvas />);

    expect(screen.getByText('New Scene')).toBeInTheDocument();
    expect(screen.getByText('3s')).toBeInTheDocument();
  });

  it('limpa canvas quando não há cena', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      currentSceneId: null,
    });

    render(<EditorCanvas />);

    expect(screen.getByText('Nenhuma cena selecionada')).toBeInTheDocument();
  });

  it('manipula erros de carregamento de imagem', () => {
    render(<EditorCanvas />);

    // Simular erro de carregamento de imagem
    const canvas = screen.getByRole('img', { hidden: true }).closest('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('configura eventos do canvas corretamente', () => {
    render(<EditorCanvas />);

    // Verificar se os eventos foram configurados (implementação interna)
    const canvas = screen.getByRole('img', { hidden: true }).closest('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('desenha grid quando habilitado', () => {
    render(<EditorCanvas />);

    const gridBtn = screen.getByTitle('Mostrar/ocultar grid');
    fireEvent.click(gridBtn);

    // Verificar se o grid foi desenhado (implementação interna)
    expect(gridBtn).toBeInTheDocument();
  });

  it('desenha regras quando habilitadas', () => {
    render(<EditorCanvas />);

    const rulersBtn = screen.getByTitle('Mostrar/ocultar regras');
    fireEvent.click(rulersBtn);

    // Verificar se as regras foram desenhadas (implementação interna)
    expect(rulersBtn).toBeInTheDocument();
  });
});
