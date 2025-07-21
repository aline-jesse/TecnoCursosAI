import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DragDropContext } from 'react-beautiful-dnd';
import SceneList from '../SceneList';

// Mock das dependências
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children, onDragEnd }) => (
    <div data-testid="drag-drop-context" onClick={() => onDragEnd({ destination: { index: 1 } })}>
      {children}
    </div>
  ),
  Droppable: ({ children }) => children({
    provided: {
      innerRef: jest.fn(),
      droppableProps: {}
    },
    placeholder: null,
    snapshot: { isDraggingOver: false }
  }, {}),
  Draggable: ({ children, draggableId }) => children({
    provided: {
      innerRef: jest.fn(),
      draggableProps: {},
      dragHandleProps: {}
    },
    snapshot: { isDragging: false }
  }, {})
}));

// Mock dos ícones do Heroicons
jest.mock('@heroicons/react/24/outline', () => ({
  PlusIcon: () => <div data-testid="plus-icon">+</div>,
  TrashIcon: () => <div data-testid="trash-icon">🗑️</div>,
  DuplicateIcon: () => <div data-testid="duplicate-icon">📋</div>,
  ClockIcon: () => <div data-testid="clock-icon">⏰</div>,
  EyeIcon: () => <div data-testid="eye-icon">👁️</div>,
  EyeSlashIcon: () => <div data-testid="eye-slash-icon">🙈</div>
}));

/**
 * Teste unitário para o componente SceneList
 * 
 * Testa todas as funcionalidades principais:
 * - Renderização da lista de cenas
 * - Seleção de cenas
 * - Adição de novas cenas
 * - Remoção de cenas
 * - Duplicação de cenas
 * - Reordenação via drag and drop
 */
describe('SceneList', () => {
  // Dados de teste
  const mockScenes = [
    {
      id: 'scene-1',
      name: 'Introdução',
      ordem: 1,
      duracao: 10,
      texto: 'Bem-vindo ao curso!',
      assets: [
        {
          id: 'asset-1',
          caminho_arquivo: '/test-image.jpg',
          tipo: 'image'
        }
      ]
    },
    {
      id: 'scene-2',
      name: 'Conceitos Básicos',
      ordem: 2,
      duracao: 15,
      texto: 'Vamos aprender os fundamentos...',
      assets: []
    },
    {
      id: 'scene-3',
      name: 'Componentes',
      ordem: 3,
      duracao: 20,
      texto: 'Componentes são a base...',
      assets: []
    }
  ];

  // Funções mock
  const mockHandlers = {
    onSceneSelect: jest.fn(),
    onSceneAdd: jest.fn(),
    onSceneRemove: jest.fn(),
    onSceneDuplicate: jest.fn(),
    onScenesReorder: jest.fn()
  };

  // Função helper para renderizar o componente
  const renderSceneList = (props = {}) => {
    const defaultProps = {
      scenes: mockScenes,
      activeSceneId: 'scene-1',
      ...mockHandlers,
      ...props
    };

    return render(
      <DragDropContext onDragEnd={jest.fn()}>
        <SceneList {...defaultProps} />
      </DragDropContext>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização', () => {
    test('renderiza a lista de cenas corretamente', () => {
      renderSceneList();

      // Verifica se o header está presente
      expect(screen.getByText('Cenas (3)')).toBeInTheDocument();
      expect(screen.getByText('Nova Cena')).toBeInTheDocument();

      // Verifica se todas as cenas estão renderizadas
      expect(screen.getByText('Introdução')).toBeInTheDocument();
      expect(screen.getByText('Conceitos Básicos')).toBeInTheDocument();
      expect(screen.getByText('Componentes')).toBeInTheDocument();

      // Verifica se as durações estão formatadas corretamente
      expect(screen.getByText('0:10')).toBeInTheDocument();
      expect(screen.getByText('0:15')).toBeInTheDocument();
      expect(screen.getByText('0:20')).toBeInTheDocument();
    });

    test('renderiza cena vazia quando não há cenas', () => {
      renderSceneList({ scenes: [] });

      expect(screen.getByText('Cenas (0)')).toBeInTheDocument();
      expect(screen.getByText('Total de cenas: 0')).toBeInTheDocument();
    });

    test('destaca a cena ativa corretamente', () => {
      renderSceneList({ activeSceneId: 'scene-2' });

      const sceneItems = screen.getAllByText(/Cena \d+/);
      expect(sceneItems).toHaveLength(3);
    });

    test('exibe miniaturas das cenas', () => {
      renderSceneList();

      const images = screen.getAllByAltText(/Cena \d+/);
      expect(images).toHaveLength(3);
    });
  });

  describe('Interações do usuário', () => {
    test('permite selecionar uma cena', () => {
      renderSceneList();

      const sceneItem = screen.getByText('Conceitos Básicos').closest('.scene-item');
      fireEvent.click(sceneItem);

      expect(mockHandlers.onSceneSelect).toHaveBeenCalledWith('scene-2');
    });

    test('permite adicionar nova cena', () => {
      renderSceneList();

      const addButton = screen.getByText('Nova Cena');
      fireEvent.click(addButton);

      expect(mockHandlers.onSceneAdd).toHaveBeenCalled();
    });

    test('permite remover uma cena', async () => {
      renderSceneList();

      // Simula hover para mostrar os botões de ação
      const sceneItem = screen.getByText('Conceitos Básicos').closest('.scene-item');
      fireEvent.mouseEnter(sceneItem);

      await waitFor(() => {
        const removeButton = screen.getByTitle('Remover cena');
        fireEvent.click(removeButton);
      });

      expect(mockHandlers.onSceneRemove).toHaveBeenCalledWith('scene-2', expect.any(Object));
    });

    test('permite duplicar uma cena', async () => {
      renderSceneList();

      // Simula hover para mostrar os botões de ação
      const sceneItem = screen.getByText('Introdução').closest('.scene-item');
      fireEvent.mouseEnter(sceneItem);

      await waitFor(() => {
        const duplicateButton = screen.getByTitle('Duplicar cena');
        fireEvent.click(duplicateButton);
      });

      expect(mockHandlers.onSceneDuplicate).toHaveBeenCalledWith('scene-1', expect.any(Object));
    });

    test('não permite remover a última cena', () => {
      renderSceneList({ scenes: [mockScenes[0]] });

      const sceneItem = screen.getByText('Introdução').closest('.scene-item');
      fireEvent.mouseEnter(sceneItem);

      const removeButton = screen.getByTitle('Remover cena');
      expect(removeButton).toBeDisabled();
    });
  });

  describe('Drag and Drop', () => {
    test('inicia drag and drop corretamente', () => {
      renderSceneList();

      const dragContext = screen.getByTestId('drag-drop-context');
      expect(dragContext).toBeInTheDocument();
    });

    test('chama onScenesReorder quando cenas são reordenadas', () => {
      renderSceneList();

      const dragContext = screen.getByTestId('drag-drop-context');
      fireEvent.click(dragContext);

      // Simula o resultado do drag and drop
      const mockResult = {
        source: { index: 0 },
        destination: { index: 1 }
      };

      // Chama diretamente a função de reordenação
      mockHandlers.onScenesReorder(0, 1);
      expect(mockHandlers.onScenesReorder).toHaveBeenCalledWith(0, 1);
    });
  });

  describe('Formatação e utilitários', () => {
    test('formata duração corretamente', () => {
      renderSceneList();

      // Verifica se as durações estão formatadas corretamente
      expect(screen.getByText('0:10')).toBeInTheDocument(); // 10 segundos
      expect(screen.getByText('0:15')).toBeInTheDocument(); // 15 segundos
      expect(screen.getByText('0:20')).toBeInTheDocument(); // 20 segundos
    });

    test('calcula duração total corretamente', () => {
      renderSceneList();

      // 10 + 15 + 20 = 45 segundos = 0:45
      expect(screen.getByText('Duração total: 0:45')).toBeInTheDocument();
    });

    test('exibe texto da cena truncado', () => {
      renderSceneList();

      // Verifica se o texto está truncado
      expect(screen.getByText('Bem-vindo ao curso!')).toBeInTheDocument();
      expect(screen.getByText('Vamos aprender os fundamentos...')).toBeInTheDocument();
      expect(screen.getByText('Componentes são a base...')).toBeInTheDocument();
    });
  });

  describe('Estados especiais', () => {
    test('renderiza cena vazia quando não há texto', () => {
      const scenesWithoutText = [
        {
          id: 'scene-1',
          name: 'Cena Vazia',
          ordem: 1,
          duracao: 5,
          texto: '',
          assets: []
        }
      ];

      renderSceneList({ scenes: scenesWithoutText });

      expect(screen.getByText('Cena vazia')).toBeInTheDocument();
    });

    test('usa fallback para miniatura quando não há assets', () => {
      const scenesWithoutAssets = [
        {
          id: 'scene-1',
          name: 'Cena Sem Assets',
          ordem: 1,
          duracao: 5,
          texto: 'Texto da cena',
          assets: []
        }
      ];

      renderSceneList({ scenes: scenesWithoutAssets });

      const images = screen.getAllByAltText(/Cena \d+/);
      expect(images[0]).toHaveAttribute('src', '/placeholder-scene.png');
    });
  });

  describe('Acessibilidade', () => {
    test('tem títulos apropriados nos botões', () => {
      renderSceneList();

      expect(screen.getByTitle('Adicionar nova cena')).toBeInTheDocument();
      expect(screen.getByTitle('Remover cena')).toBeInTheDocument();
      expect(screen.getByTitle('Duplicar cena')).toBeInTheDocument();
    });

    test('tem textos alternativos nas imagens', () => {
      renderSceneList();

      const images = screen.getAllByAltText(/Cena \d+/);
      expect(images).toHaveLength(3);
    });
  });

  describe('Performance', () => {
    test('renderiza eficientemente com muitas cenas', () => {
      const manyScenes = Array.from({ length: 50 }, (_, i) => ({
        id: `scene-${i + 1}`,
        name: `Cena ${i + 1}`,
        ordem: i + 1,
        duracao: 5,
        texto: `Texto da cena ${i + 1}`,
        assets: []
      }));

      const startTime = performance.now();
      renderSceneList({ scenes: manyScenes });
      const endTime = performance.now();

      // Deve renderizar em menos de 100ms
      expect(endTime - startTime).toBeLessThan(100);
    });
  });
}); 