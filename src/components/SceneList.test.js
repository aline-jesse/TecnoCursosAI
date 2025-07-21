import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DragDropContext } from 'react-beautiful-dnd';
import SceneList from './SceneList';

// Mock das dependências
jest.mock('@heroicons/react/24/outline', () => ({
  PlusIcon: () => <div data-testid="plus-icon">+</div>,
  TrashIcon: () => <div data-testid="trash-icon">🗑</div>,
  DocumentDuplicateIcon: () => <div data-testid="duplicate-icon">📋</div>,
  PlayIcon: () => <div data-testid="play-icon">▶</div>,
  ClockIcon: () => <div data-testid="clock-icon">⏰</div>,
  PhotoIcon: () => <div data-testid="photo-icon">📷</div>,
  PencilIcon: () => <div data-testid="pencil-icon">✏️</div>,
}));

// Mock do react-beautiful-dnd
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children, onDragEnd }) => (
    <div data-testid="drag-drop-context" onClick={() => onDragEnd({ 
      destination: { index: 1 },
      source: { index: 0 }
    })}>
      {children}
    </div>
  ),
  Droppable: ({ children }) => children({
    provided: {
      innerRef: jest.fn(),
      droppableProps: {},
    },
    placeholder: null,
    snapshot: { isDraggingOver: false },
  }, {}),
  Draggable: ({ children, draggableId }) => children({
    provided: {
      innerRef: jest.fn(),
      draggableProps: {},
      dragHandleProps: {},
    },
    snapshot: { isDragging: false },
  }, {}),
}));

// Dados de teste
const mockScenes = [
  {
    id: 'scene-1',
    title: 'Cena 1',
    duration: 30,
    text: 'Texto da cena 1',
    assets: [
      { id: 'asset-1', thumbnail_url: 'http://example.com/thumb1.jpg' }
    ],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 'scene-2',
    title: 'Cena 2',
    duration: 45,
    text: 'Texto da cena 2',
    assets: [],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 'scene-3',
    title: 'Cena 3',
    duration: 60,
    text: '',
    assets: [],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
];

const defaultProps = {
  scenes: mockScenes,
  activeSceneId: 'scene-1',
  onSceneSelect: jest.fn(),
  onSceneAdd: jest.fn(),
  onSceneRemove: jest.fn(),
  onSceneDuplicate: jest.fn(),
  onSceneReorder: jest.fn(),
  onSceneUpdate: jest.fn(),
  isLoading: false,
  error: null,
};

// Wrapper para renderizar com contexto de drag-and-drop
const renderWithDragDrop = (component) => {
  return render(
    <DragDropContext onDragEnd={jest.fn()}>
      {component}
    </DragDropContext>
  );
};

describe('SceneList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    test('renderiza o componente corretamente', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByText('Cenas')).toBeInTheDocument();
      expect(screen.getByText('Cena 1')).toBeInTheDocument();
      expect(screen.getByText('Cena 2')).toBeInTheDocument();
      expect(screen.getByText('Cena 3')).toBeInTheDocument();
    });

    test('mostra botões de ação quando há cena ativa', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
      expect(screen.getByTestId('duplicate-icon')).toBeInTheDocument();
      expect(screen.getByTestId('trash-icon')).toBeInTheDocument();
    });

    test('não mostra botões de ação quando não há cena ativa', () => {
      renderWithDragDrop(<SceneList {...defaultProps} activeSceneId={null} />);
      
      expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
      expect(screen.queryByTestId('duplicate-icon')).not.toBeInTheDocument();
      expect(screen.queryByTestId('trash-icon')).not.toBeInTheDocument();
    });

    test('mostra números das cenas corretamente', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    test('formata duração corretamente', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByText('00:30')).toBeInTheDocument(); // 30 segundos
      expect(screen.getByText('00:45')).toBeInTheDocument(); // 45 segundos
      expect(screen.getByText('01:00')).toBeInTheDocument(); // 60 segundos
    });

    test('mostra contador de elementos', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByText('1 elementos')).toBeInTheDocument(); // Cena 1 tem 1 asset
      expect(screen.getByText('0 elementos')).toBeInTheDocument(); // Cenas 2 e 3 não têm assets
    });
  });

  describe('Estados de carregamento e erro', () => {
    test('mostra indicador de carregamento', () => {
      renderWithDragDrop(<SceneList {...defaultProps} isLoading={true} />);
      
      expect(screen.getByText('Carregando cenas...')).toBeInTheDocument();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    test('mostra mensagem de erro', () => {
      const errorMessage = 'Erro ao carregar cenas';
      renderWithDragDrop(<SceneList {...defaultProps} error={errorMessage} />);
      
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
      expect(screen.getByText('Tentar Novamente')).toBeInTheDocument();
    });

    test('mostra estado vazio quando não há cenas', () => {
      renderWithDragDrop(<SceneList {...defaultProps} scenes={[]} />);
      
      expect(screen.getByText('Nenhuma cena criada')).toBeInTheDocument();
      expect(screen.getByText('Clique no botão + para adicionar uma cena')).toBeInTheDocument();
    });
  });

  describe('Interações do usuário', () => {
    test('chama onSceneSelect quando uma cena é clicada', () => {
      const onSceneSelect = jest.fn();
      renderWithDragDrop(<SceneList {...defaultProps} onSceneSelect={onSceneSelect} />);
      
      fireEvent.click(screen.getByText('Cena 2'));
      
      expect(onSceneSelect).toHaveBeenCalledWith('scene-2');
    });

    test('chama onSceneAdd quando botão de adicionar é clicado', () => {
      const onSceneAdd = jest.fn();
      renderWithDragDrop(<SceneList {...defaultProps} onSceneAdd={onSceneAdd} />);
      
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      expect(onSceneAdd).toHaveBeenCalled();
    });

    test('chama onSceneRemove quando botão de remover é clicado', () => {
      const onSceneRemove = jest.fn();
      renderWithDragDrop(<SceneList {...defaultProps} onSceneRemove={onSceneRemove} />);
      
      fireEvent.click(screen.getByTestId('trash-icon').parentElement);
      
      expect(onSceneRemove).toHaveBeenCalledWith('scene-1');
    });

    test('chama onSceneDuplicate quando botão de duplicar é clicado', () => {
      const onSceneDuplicate = jest.fn();
      renderWithDragDrop(<SceneList {...defaultProps} onSceneDuplicate={onSceneDuplicate} />);
      
      fireEvent.click(screen.getByTestId('duplicate-icon').parentElement);
      
      expect(onSceneDuplicate).toHaveBeenCalledWith('scene-1');
    });

    test('desabilita botão de remover quando só há uma cena', () => {
      const singleScene = [mockScenes[0]];
      renderWithDragDrop(<SceneList {...defaultProps} scenes={singleScene} />);
      
      const removeButton = screen.getByTestId('trash-icon').parentElement;
      expect(removeButton).toBeDisabled();
    });
  });

  describe('Formulário de criação de cena', () => {
    test('mostra formulário quando botão de adicionar é clicado', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      expect(screen.getByPlaceholderText('Nome da nova cena')).toBeInTheDocument();
      expect(screen.getByText('Criar')).toBeInTheDocument();
      expect(screen.getByText('Cancelar')).toBeInTheDocument();
    });

    test('cria nova cena quando formulário é submetido', () => {
      const onSceneAdd = jest.fn();
      renderWithDragDrop(<SceneList {...defaultProps} onSceneAdd={onSceneAdd} />);
      
      // Abrir formulário
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      // Preencher nome da cena
      const input = screen.getByPlaceholderText('Nome da nova cena');
      fireEvent.change(input, { target: { value: 'Nova Cena' } });
      
      // Submeter formulário
      fireEvent.click(screen.getByText('Criar'));
      
      expect(onSceneAdd).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Nova Cena',
        duration: 30,
        text: '',
        assets: []
      }));
    });

    test('cancela criação quando botão cancelar é clicado', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      // Abrir formulário
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      // Cancelar
      fireEvent.click(screen.getByText('Cancelar'));
      
      expect(screen.queryByPlaceholderText('Nome da nova cena')).not.toBeInTheDocument();
    });

    test('submete formulário com Enter', () => {
      const onSceneAdd = jest.fn();
      renderWithDragDrop(<SceneList {...defaultProps} onSceneAdd={onSceneAdd} />);
      
      // Abrir formulário
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      // Preencher e submeter com Enter
      const input = screen.getByPlaceholderText('Nome da nova cena');
      fireEvent.change(input, { target: { value: 'Nova Cena' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
      
      expect(onSceneAdd).toHaveBeenCalled();
    });

    test('cancela formulário com Escape', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      // Abrir formulário
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      // Cancelar com Escape
      const input = screen.getByPlaceholderText('Nome da nova cena');
      fireEvent.keyPress(input, { key: 'Escape', code: 'Escape' });
      
      expect(screen.queryByPlaceholderText('Nome da nova cena')).not.toBeInTheDocument();
    });

    test('desabilita botão criar quando nome está vazio', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      // Abrir formulário
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      const createButton = screen.getByText('Criar');
      expect(createButton).toBeDisabled();
    });
  });

  describe('Drag and Drop', () => {
    test('renderiza contexto de drag-and-drop', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByTestId('drag-drop-context')).toBeInTheDocument();
    });

    test('chama onSceneReorder quando drag-and-drop é executado', () => {
      const onSceneReorder = jest.fn();
      renderWithDragDrop(<SceneList {...defaultProps} onSceneReorder={onSceneReorder} />);
      
      // Simular drag-and-drop
      fireEvent.click(screen.getByTestId('drag-drop-context'));
      
      expect(onSceneReorder).toHaveBeenCalledWith(0, 1);
    });
  });

  describe('Renderização de miniaturas', () => {
    test('renderiza miniatura de imagem quando asset tem thumbnail', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      const thumbnail = screen.getByAltText('Miniatura de Cena 1');
      expect(thumbnail).toBeInTheDocument();
      expect(thumbnail.src).toBe('http://example.com/thumb1.jpg');
    });

    test('renderiza ícone de texto quando cena tem texto', () => {
      const scenesWithText = [
        {
          ...mockScenes[0],
          assets: [],
          text: 'Texto longo da cena que deve ser truncado'
        }
      ];
      
      renderWithDragDrop(<SceneList {...defaultProps} scenes={scenesWithText} />);
      
      expect(screen.getByTestId('pencil-icon')).toBeInTheDocument();
      expect(screen.getByText('Texto longo da cena...')).toBeInTheDocument();
    });

    test('renderiza placeholder quando cena está vazia', () => {
      const emptyScene = [mockScenes[2]]; // Cena 3 está vazia
      
      renderWithDragDrop(<SceneList {...defaultProps} scenes={emptyScene} />);
      
      expect(screen.getByTestId('photo-icon')).toBeInTheDocument();
      expect(screen.getByText('Vazia')).toBeInTheDocument();
    });
  });

  describe('Formatação de duração', () => {
    test('formata duração corretamente', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByText('00:30')).toBeInTheDocument(); // 30 segundos
      expect(screen.getByText('00:45')).toBeInTheDocument(); // 45 segundos
      expect(screen.getByText('01:00')).toBeInTheDocument(); // 60 segundos
    });

    test('mostra 00:00 para duração zero ou negativa', () => {
      const scenesWithZeroDuration = [
        { ...mockScenes[0], duration: 0 },
        { ...mockScenes[1], duration: -5 }
      ];
      
      renderWithDragDrop(<SceneList {...defaultProps} scenes={scenesWithZeroDuration} />);
      
      expect(screen.getAllByText('00:00')).toHaveLength(2);
    });

    test('formata duração longa corretamente', () => {
      const scenesWithLongDuration = [
        { ...mockScenes[0], duration: 125 }, // 2:05
        { ...mockScenes[1], duration: 3661 } // 1:01:01
      ];
      
      renderWithDragDrop(<SceneList {...defaultProps} scenes={scenesWithLongDuration} />);
      
      expect(screen.getByText('02:05')).toBeInTheDocument();
      expect(screen.getByText('61:01')).toBeInTheDocument();
    });
  });

  describe('Estados especiais', () => {
    test('destaca cena ativa', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      const activeScene = screen.getByText('Cena 1').closest('.scene-item');
      expect(activeScene).toHaveClass('active');
    });

    test('mostra indicador de cena ativa', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      expect(screen.getByTestId('play-icon')).toBeInTheDocument();
    });

    test('não mostra indicador quando não há cena ativa', () => {
      renderWithDragDrop(<SceneList {...defaultProps} activeSceneId={null} />);
      
      expect(screen.queryByTestId('play-icon')).not.toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    test('botões têm títulos descritivos', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      const addButton = screen.getByTestId('plus-icon').parentElement;
      const duplicateButton = screen.getByTestId('duplicate-icon').parentElement;
      const removeButton = screen.getByTestId('trash-icon').parentElement;
      
      expect(addButton).toHaveAttribute('title', 'Adicionar nova cena');
      expect(duplicateButton).toHaveAttribute('title', 'Duplicar cena');
      expect(removeButton).toHaveAttribute('title', 'Remover cena');
    });

    test('imagens têm alt text descritivo', () => {
      renderWithDragDrop(<SceneList {...defaultProps} />);
      
      const thumbnail = screen.getByAltText('Miniatura de Cena 1');
      expect(thumbnail).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    test('renderiza lista grande sem problemas', () => {
      const largeScenesList = Array.from({ length: 100 }, (_, index) => ({
        id: `scene-${index}`,
        title: `Cena ${index + 1}`,
        duration: 30,
        text: '',
        assets: [],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      }));
      
      renderWithDragDrop(<SceneList {...defaultProps} scenes={largeScenesList} />);
      
      expect(screen.getByText('Cena 1')).toBeInTheDocument();
      expect(screen.getByText('Cena 100')).toBeInTheDocument();
    });
  });
}); 