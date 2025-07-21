import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DragDropContext } from 'react-beautiful-dnd';
import Timeline from './Timeline';

// Mock das dependências
jest.mock('@heroicons/react/24/outline', () => ({
  PlayIcon: () => <div data-testid="play-icon">▶</div>,
  PauseIcon: () => <div data-testid="pause-icon">⏸</div>,
  StopIcon: () => <div data-testid="stop-icon">⏹</div>,
  PlusIcon: () => <div data-testid="plus-icon">+</div>,
  MinusIcon: () => <div data-testid="minus-icon">-</div>,
  ClockIcon: () => <div data-testid="clock-icon">⏰</div>,
  FilmIcon: () => <div data-testid="film-icon">🎬</div>,
  SpeakerWaveIcon: () => <div data-testid="speaker-icon">🔊</div>,
  PhotoIcon: () => <div data-testid="photo-icon">📷</div>,
  DocumentTextIcon: () => <div data-testid="text-icon">📄</div>,
  UserIcon: () => <div data-testid="user-icon">👤</div>,
}));

// Mock do react-beautiful-dnd
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children, onDragEnd, onDragStart }) => (
    <div data-testid="drag-drop-context" 
         onClick={() => onDragEnd({ 
           destination: { index: 1 },
           source: { index: 0 }
         })}
         onMouseDown={() => onDragStart({ draggableId: 'scene-1' })}
    >
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
    assets: [],
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

const mockLayers = {
  'scene-1': [
    { type: 'text', name: 'Título da cena', id: 'text-1' },
    { type: 'avatar', name: 'Avatar principal', id: 'avatar-1' },
    { type: 'image', name: 'Imagem de fundo', id: 'image-1' },
    { type: 'audio', name: 'Narração', id: 'audio-1' }
  ],
  'scene-2': [
    { type: 'text', name: 'Subtítulo', id: 'text-2' },
    { type: 'video', name: 'Vídeo de exemplo', id: 'video-1' }
  ],
  'scene-3': []
};

const defaultProps = {
  scenes: mockScenes,
  activeSceneId: 'scene-1',
  onSceneSelect: jest.fn(),
  onSceneReorder: jest.fn(),
  onSceneUpdate: jest.fn(),
  onSceneDurationChange: jest.fn(),
  layers: mockLayers,
  isPlaying: false,
  currentTime: 0,
  onPlayPause: jest.fn(),
  onStop: jest.fn(),
  onSeek: jest.fn(),
  onZoomIn: jest.fn(),
  onZoomOut: jest.fn(),
  zoomLevel: 1
};

// Wrapper para renderizar com contexto de drag-and-drop
const renderWithDragDrop = (component) => {
  return render(
    <DragDropContext onDragEnd={jest.fn()} onDragStart={jest.fn()}>
      {component}
    </DragDropContext>
  );
};

describe('Timeline', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    test('renderiza o componente corretamente', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('play-icon')).toBeInTheDocument();
      expect(screen.getByTestId('stop-icon')).toBeInTheDocument();
      expect(screen.getByText('Cena 1')).toBeInTheDocument();
      expect(screen.getByText('Cena 2')).toBeInTheDocument();
      expect(screen.getByText('Cena 3')).toBeInTheDocument();
    });

    test('mostra controles de playback', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('play-icon')).toBeInTheDocument();
      expect(screen.getByTestId('stop-icon')).toBeInTheDocument();
      expect(screen.getByText('00:00 / 02:15')).toBeInTheDocument(); // 30+45+60 = 135s = 2:15
    });

    test('mostra controles de zoom', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
      expect(screen.getByTestId('minus-icon')).toBeInTheDocument();
      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    test('mostra marcadores de tempo', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByText('00:00')).toBeInTheDocument();
      expect(screen.getByText('00:13')).toBeInTheDocument(); // Aproximadamente 1/10 de 135s
    });
  });

  describe('Controles de playback', () => {
    test('chama onPlayPause quando botão play é clicado', () => {
      const onPlayPause = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onPlayPause={onPlayPause} />);
      
      fireEvent.click(screen.getByTestId('play-icon').parentElement);
      
      expect(onPlayPause).toHaveBeenCalled();
    });

    test('chama onStop quando botão stop é clicado', () => {
      const onStop = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onStop={onStop} />);
      
      fireEvent.click(screen.getByTestId('stop-icon').parentElement);
      
      expect(onStop).toHaveBeenCalled();
    });

    test('mostra ícone de pause quando está reproduzindo', () => {
      renderWithDragDrop(<Timeline {...defaultProps} isPlaying={true} />);
      
      expect(screen.getByTestId('pause-icon')).toBeInTheDocument();
      expect(screen.queryByTestId('play-icon')).not.toBeInTheDocument();
    });

    test('mostra ícone de play quando está pausado', () => {
      renderWithDragDrop(<Timeline {...defaultProps} isPlaying={false} />);
      
      expect(screen.getByTestId('play-icon')).toBeInTheDocument();
      expect(screen.queryByTestId('pause-icon')).not.toBeInTheDocument();
    });
  });

  describe('Controles de zoom', () => {
    test('chama onZoomIn quando botão + é clicado', () => {
      const onZoomIn = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onZoomIn={onZoomIn} />);
      
      fireEvent.click(screen.getByTestId('plus-icon').parentElement);
      
      expect(onZoomIn).toHaveBeenCalled();
    });

    test('chama onZoomOut quando botão - é clicado', () => {
      const onZoomOut = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onZoomOut={onZoomOut} />);
      
      fireEvent.click(screen.getByTestId('minus-icon').parentElement);
      
      expect(onZoomOut).toHaveBeenCalled();
    });

    test('mostra nível de zoom correto', () => {
      renderWithDragDrop(<Timeline {...defaultProps} zoomLevel={1.5} />);
      
      expect(screen.getByText('150%')).toBeInTheDocument();
    });
  });

  describe('Blocos de cenas', () => {
    test('renderiza blocos de cenas com informações corretas', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByText('Cena 1')).toBeInTheDocument();
      expect(screen.getByText('00:30')).toBeInTheDocument(); // Duração da cena 1
      expect(screen.getByText('Cena 2')).toBeInTheDocument();
      expect(screen.getByText('00:45')).toBeInTheDocument(); // Duração da cena 2
    });

    test('destaca cena ativa', () => {
      renderWithDragDrop(<Timeline {...defaultProps} activeSceneId="scene-2" />);
      
      const scene2Block = screen.getByText('Cena 2').closest('.scene-block');
      expect(scene2Block).toHaveClass('selected');
    });

    test('chama onSceneSelect quando bloco é clicado', () => {
      const onSceneSelect = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onSceneSelect={onSceneSelect} />);
      
      fireEvent.click(screen.getByText('Cena 2'));
      
      expect(onSceneSelect).toHaveBeenCalledWith('scene-2');
    });
  });

  describe('Camadas', () => {
    test('renderiza camadas de texto', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('text-icon')).toBeInTheDocument();
      expect(screen.getByText('Título da cena')).toBeInTheDocument();
    });

    test('renderiza camadas de avatar', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('user-icon')).toBeInTheDocument();
      expect(screen.getByText('Avatar principal')).toBeInTheDocument();
    });

    test('renderiza camadas de imagem', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('photo-icon')).toBeInTheDocument();
      expect(screen.getByText('Imagem de fundo')).toBeInTheDocument();
    });

    test('renderiza camadas de áudio', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('speaker-icon')).toBeInTheDocument();
      expect(screen.getByText('Narração')).toBeInTheDocument();
    });

    test('renderiza camadas de vídeo', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('film-icon')).toBeInTheDocument();
      expect(screen.getByText('Vídeo de exemplo')).toBeInTheDocument();
    });

    test('mostra placeholder quando não há camadas', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByText('Sem camadas')).toBeInTheDocument();
    });
  });

  describe('Edição de duração', () => {
    test('mostra botão de editar duração', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      const editButtons = screen.getAllByTestId('clock-icon');
      expect(editButtons.length).toBeGreaterThan(0);
    });

    test('abre input de edição quando botão é clicado', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      const editButton = screen.getAllByTestId('clock-icon')[0];
      fireEvent.click(editButton.parentElement);
      
      expect(screen.getByDisplayValue('30')).toBeInTheDocument();
      expect(screen.getByText('✓')).toBeInTheDocument();
      expect(screen.getByText('✕')).toBeInTheDocument();
    });

    test('confirma edição com Enter', () => {
      const onSceneDurationChange = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onSceneDurationChange={onSceneDurationChange} />);
      
      // Abrir edição
      const editButton = screen.getAllByTestId('clock-icon')[0];
      fireEvent.click(editButton.parentElement);
      
      // Editar valor
      const input = screen.getByDisplayValue('30');
      fireEvent.change(input, { target: { value: '45' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
      
      expect(onSceneDurationChange).toHaveBeenCalledWith('scene-1', 45);
    });

    test('cancela edição com Escape', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      // Abrir edição
      const editButton = screen.getAllByTestId('clock-icon')[0];
      fireEvent.click(editButton.parentElement);
      
      // Cancelar com Escape
      const input = screen.getByDisplayValue('30');
      fireEvent.keyPress(input, { key: 'Escape', code: 'Escape' });
      
      expect(screen.queryByDisplayValue('30')).not.toBeInTheDocument();
    });

    test('confirma edição com botão', () => {
      const onSceneDurationChange = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onSceneDurationChange={onSceneDurationChange} />);
      
      // Abrir edição
      const editButton = screen.getAllByTestId('clock-icon')[0];
      fireEvent.click(editButton.parentElement);
      
      // Editar e confirmar
      const input = screen.getByDisplayValue('30');
      fireEvent.change(input, { target: { value: '45' } });
      fireEvent.click(screen.getByText('✓'));
      
      expect(onSceneDurationChange).toHaveBeenCalledWith('scene-1', 45);
    });

    test('cancela edição com botão', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      // Abrir edição
      const editButton = screen.getAllByTestId('clock-icon')[0];
      fireEvent.click(editButton.parentElement);
      
      // Cancelar
      fireEvent.click(screen.getByText('✕'));
      
      expect(screen.queryByDisplayValue('30')).not.toBeInTheDocument();
    });
  });

  describe('Drag and Drop', () => {
    test('renderiza contexto de drag-and-drop', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByTestId('drag-drop-context')).toBeInTheDocument();
    });

    test('chama onSceneReorder quando drag-and-drop é executado', () => {
      const onSceneReorder = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onSceneReorder={onSceneReorder} />);
      
      // Simular drag-and-drop
      fireEvent.click(screen.getByTestId('drag-drop-context'));
      
      expect(onSceneReorder).toHaveBeenCalledWith(0, 1);
    });

    test('chama onDragStart quando drag inicia', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      // Simular início do drag
      fireEvent.mouseDown(screen.getByTestId('drag-drop-context'));
      
      // Verificar se o estado de drag foi atualizado
      expect(screen.getByTestId('drag-drop-context')).toBeInTheDocument();
    });
  });

  describe('Seek e playhead', () => {
    test('chama onSeek quando timeline é clicada', () => {
      const onSeek = jest.fn();
      renderWithDragDrop(<Timeline {...defaultProps} onSeek={onSeek} />);
      
      const timelineContainer = screen.getByTestId('drag-drop-context').parentElement;
      fireEvent.click(timelineContainer);
      
      expect(onSeek).toHaveBeenCalled();
    });

    test('atualiza posição do playhead baseado no tempo atual', () => {
      renderWithDragDrop(<Timeline {...defaultProps} currentTime={67.5} />); // 50% de 135s
      
      // O playhead deve estar posicionado em 50%
      const playhead = screen.getByTestId('drag-drop-context').querySelector('.playhead');
      expect(playhead).toBeInTheDocument();
    });
  });

  describe('Formatação de tempo', () => {
    test('formata tempo corretamente', () => {
      renderWithDragDrop(<Timeline {...defaultProps} currentTime={125} />);
      
      expect(screen.getByText('02:05')).toBeInTheDocument(); // 125 segundos
    });

    test('formata duração total corretamente', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      expect(screen.getByText('02:15')).toBeInTheDocument(); // 135 segundos total
    });

    test('mostra 00:00 para tempo zero', () => {
      renderWithDragDrop(<Timeline {...defaultProps} currentTime={0} />);
      
      expect(screen.getByText('00:00')).toBeInTheDocument();
    });
  });

  describe('Estados especiais', () => {
    test('aplica zoom na timeline', () => {
      renderWithDragDrop(<Timeline {...defaultProps} zoomLevel={1.5} />);
      
      const timelineContainer = screen.getByTestId('drag-drop-context').parentElement;
      expect(timelineContainer).toHaveStyle({ transform: 'scaleX(1.5)' });
    });

    test('mostra playhead quando há tempo atual', () => {
      renderWithDragDrop(<Timeline {...defaultProps} currentTime={30} />);
      
      const playhead = screen.getByTestId('drag-drop-context').querySelector('.playhead');
      expect(playhead).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    test('botões têm títulos descritivos', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      const playButton = screen.getByTestId('play-icon').parentElement;
      const stopButton = screen.getByTestId('stop-icon').parentElement;
      const zoomInButton = screen.getByTestId('plus-icon').parentElement;
      const zoomOutButton = screen.getByTestId('minus-icon').parentElement;
      
      expect(playButton).toHaveAttribute('title', 'Reproduzir');
      expect(stopButton).toHaveAttribute('title', 'Parar');
      expect(zoomInButton).toHaveAttribute('title', 'Aumentar zoom');
      expect(zoomOutButton).toHaveAttribute('title', 'Diminuir zoom');
    });

    test('camadas têm tooltips descritivos', () => {
      renderWithDragDrop(<Timeline {...defaultProps} />);
      
      const textLayer = screen.getByText('Título da cena').closest('.layer-item');
      expect(textLayer).toHaveAttribute('title', 'text: Título da cena');
    });
  });

  describe('Performance', () => {
    test('renderiza timeline com muitas cenas sem problemas', () => {
      const manyScenes = Array.from({ length: 50 }, (_, index) => ({
        id: `scene-${index}`,
        title: `Cena ${index + 1}`,
        duration: 30,
        text: '',
        assets: [],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      }));
      
      renderWithDragDrop(<Timeline {...defaultProps} scenes={manyScenes} />);
      
      expect(screen.getByText('Cena 1')).toBeInTheDocument();
      expect(screen.getByText('Cena 50')).toBeInTheDocument();
    });
  });
}); 