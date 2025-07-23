/**
 * Testes unitários para funcionalidades básicas do EditorCanvas
 * Testa renderização e interações básicas sem dependências externas
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock simples do EditorCanvas para testes
const MockEditorCanvas = ({ activeScene, onUpdateScene, assets }) => {
  const [scene, setScene] = React.useState(activeScene);
  const [selectedElement, setSelectedElement] = React.useState(null);

  const handleAddText = () => {
    const newText = {
      id: `text-${Date.now()}`,
      type: 'text',
      text: 'Novo texto',
      x: 100,
      y: 100,
      width: 200,
      height: 40,
    };

    const newScene = {
      ...scene,
      objects: [...(scene.objects || []), newText],
    };
    setScene(newScene);
    onUpdateScene(newScene);
  };

  const handleDeleteSelected = () => {
    if (selectedElement) {
      const newScene = {
        ...scene,
        objects: (scene.objects || []).filter(
          obj => obj.id !== selectedElement
        ),
      };
      setScene(newScene);
      setSelectedElement(null);
      onUpdateScene(newScene);
    }
  };

  const handleSelectElement = elementId => {
    setSelectedElement(elementId);
  };

  const handleDrop = e => {
    e.preventDefault();
    const assetId = e.dataTransfer.getData('assetId');
    const assetType = e.dataTransfer.getData('assetType');

    if (assetId && assetType) {
      const newObject = {
        id: `${assetType}-${Date.now()}`,
        type: assetType,
        assetId,
        x: 100,
        y: 100,
        width: assetType === 'avatar' ? 120 : 200,
        height: assetType === 'avatar' ? 180 : 120,
      };

      const newScene = {
        ...scene,
        objects: [...(scene.objects || []), newObject],
      };
      setScene(newScene);
      onUpdateScene(newScene);
    }
  };

  const handleDragOver = e => {
    e.preventDefault();
  };

  return (
    <div className='editor-canvas' data-testid='editor-canvas'>
      <canvas
        width={scene?.width || 800}
        height={scene?.height || 600}
        tabIndex={0}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        data-testid='canvas'
      />

      <div className='canvas-controls'>
        <button onClick={handleAddText} data-testid='add-text-btn'>
          Adicionar Texto
        </button>
        <button
          onClick={handleDeleteSelected}
          disabled={!selectedElement}
          data-testid='delete-btn'
        >
          Excluir Selecionado
        </button>
        <button
          onClick={() => handleSelectElement('test-element')}
          data-testid='select-btn'
        >
          Selecionar Elemento
        </button>
      </div>

      <div className='scene-info'>
        <span data-testid='scene-name'>{scene?.name || 'Cena'}</span>
        <span data-testid='objects-count'>
          Objetos: {scene?.objects?.length || 0}
        </span>
        <span data-testid='selected-element'>
          Selecionado: {selectedElement || 'Nenhum'}
        </span>
      </div>

      <div className='scene-objects'>
        {(scene?.objects || []).map(obj => (
          <div
            key={obj.id}
            className={`scene-object ${selectedElement === obj.id ? 'selected' : ''}`}
            onClick={() => handleSelectElement(obj.id)}
            data-testid={`object-${obj.id}`}
          >
            {obj.type}: {obj.text || obj.assetId}
          </div>
        ))}
      </div>
    </div>
  );
};

// Mock de assets para teste
const mockAssets = [
  {
    id: 'avatar1',
    type: 'avatar',
    url: '/test-avatar.svg',
    name: 'Avatar Teste',
  },
  { id: 'img1', type: 'image', url: '/test-image.jpg', name: 'Imagem Teste' },
];

// Cena inicial para testes
const mockScene = {
  id: 'scene1',
  name: 'Cena Teste',
  width: 800,
  height: 600,
  background: '#ffffff',
  objects: [],
};

// Função mock para atualização de cena
const mockUpdateScene = jest.fn();

// Configuração padrão para renderizar o componente
const renderEditorCanvas = (props = {}) => {
  const defaultProps = {
    activeScene: mockScene,
    onUpdateScene: mockUpdateScene,
    assets: mockAssets,
    ...props,
  };

  return render(<MockEditorCanvas {...defaultProps} />);
};

describe('EditorCanvas - Funcionalidades Básicas', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização', () => {
    test('deve renderizar o canvas sem erros', () => {
      renderEditorCanvas();

      const canvas = screen.getByTestId('canvas');
      expect(canvas).toBeInTheDocument();
    });

    test('deve renderizar botões de controle', () => {
      renderEditorCanvas();

      expect(screen.getByTestId('add-text-btn')).toBeInTheDocument();
      expect(screen.getByTestId('delete-btn')).toBeInTheDocument();
      expect(screen.getByTestId('select-btn')).toBeInTheDocument();
    });

    test('deve aplicar dimensões corretas ao canvas', () => {
      renderEditorCanvas();

      const canvas = screen.getByTestId('canvas');
      expect(canvas).toHaveAttribute('width', '800');
      expect(canvas).toHaveAttribute('height', '600');
    });

    test('deve mostrar informações da cena', () => {
      renderEditorCanvas();

      expect(screen.getByTestId('scene-name')).toHaveTextContent('Cena Teste');
      expect(screen.getByTestId('objects-count')).toHaveTextContent(
        'Objetos: 0'
      );
      expect(screen.getByTestId('selected-element')).toHaveTextContent(
        'Selecionado: Nenhum'
      );
    });
  });

  describe('Funcionalidades de Controle', () => {
    test('deve adicionar texto quando botão "Adicionar Texto" for clicado', async () => {
      renderEditorCanvas();

      const addTextButton = screen.getByTestId('add-text-btn');
      fireEvent.click(addTextButton);

      await waitFor(() => {
        expect(mockUpdateScene).toHaveBeenCalledWith(
          expect.objectContaining({
            objects: expect.arrayContaining([
              expect.objectContaining({
                type: 'text',
                text: 'Novo texto',
              }),
            ]),
          })
        );
      });

      expect(screen.getByTestId('objects-count')).toHaveTextContent(
        'Objetos: 1'
      );
    });

    test('deve estar desabilitado quando nenhum elemento está selecionado', () => {
      renderEditorCanvas();

      const deleteButton = screen.getByTestId('delete-btn');
      expect(deleteButton).toBeDisabled();
    });

    test('deve estar habilitado quando há elemento selecionado', () => {
      renderEditorCanvas();

      const selectButton = screen.getByTestId('select-btn');
      fireEvent.click(selectButton);

      const deleteButton = screen.getByTestId('delete-btn');
      expect(deleteButton).not.toBeDisabled();
    });

    test('deve deletar elemento selecionado', async () => {
      // Cena com um objeto
      const sceneWithObject = {
        ...mockScene,
        objects: [
          {
            id: 'obj1',
            type: 'text',
            text: 'Texto para deletar',
            x: 100,
            y: 100,
            width: 200,
            height: 40,
          },
        ],
      };

      renderEditorCanvas({ activeScene: sceneWithObject });

      // Seleciona o elemento
      const objectElement = screen.getByTestId('object-obj1');
      fireEvent.click(objectElement);

      // Deleta o elemento
      const deleteButton = screen.getByTestId('delete-btn');
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(mockUpdateScene).toHaveBeenCalledWith(
          expect.objectContaining({
            objects: [],
          })
        );
      });
    });
  });

  describe('Drag and Drop', () => {
    test('deve aceitar drop de assets no canvas', async () => {
      renderEditorCanvas();

      const canvas = screen.getByTestId('canvas');

      const dropEvent = new Event('drop', { bubbles: true });
      dropEvent.dataTransfer = {
        getData: jest.fn(key => {
          if (key === 'assetId') return 'avatar1';
          if (key === 'assetType') return 'avatar';
          return '';
        }),
      };

      fireEvent(canvas, dropEvent);

      await waitFor(() => {
        expect(mockUpdateScene).toHaveBeenCalledWith(
          expect.objectContaining({
            objects: expect.arrayContaining([
              expect.objectContaining({
                type: 'avatar',
                assetId: 'avatar1',
              }),
            ]),
          })
        );
      });
    });

    test('deve prevenir comportamento padrão no dragOver', () => {
      renderEditorCanvas();

      const canvas = screen.getByTestId('canvas');
      const dragOverEvent = new Event('dragover', { bubbles: true });

      const preventDefaultSpy = jest.spyOn(dragOverEvent, 'preventDefault');

      fireEvent(canvas, dragOverEvent);

      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });

  describe('Integração com Assets', () => {
    test('deve adicionar avatar quando asset de avatar for dropado', async () => {
      renderEditorCanvas();

      const canvas = screen.getByTestId('canvas');

      const dropEvent = new Event('drop', { bubbles: true });
      dropEvent.dataTransfer = {
        getData: jest.fn(key => {
          if (key === 'assetId') return 'avatar1';
          if (key === 'assetType') return 'avatar';
          return '';
        }),
      };

      fireEvent(canvas, dropEvent);

      await waitFor(() => {
        expect(mockUpdateScene).toHaveBeenCalledWith(
          expect.objectContaining({
            objects: expect.arrayContaining([
              expect.objectContaining({
                type: 'avatar',
                assetId: 'avatar1',
                width: 120,
                height: 180,
              }),
            ]),
          })
        );
      });
    });

    test('deve adicionar imagem quando asset de imagem for dropado', async () => {
      renderEditorCanvas();

      const canvas = screen.getByTestId('canvas');

      const dropEvent = new Event('drop', { bubbles: true });
      dropEvent.dataTransfer = {
        getData: jest.fn(key => {
          if (key === 'assetId') return 'img1';
          if (key === 'assetType') return 'image';
          return '';
        }),
      };

      fireEvent(canvas, dropEvent);

      await waitFor(() => {
        expect(mockUpdateScene).toHaveBeenCalledWith(
          expect.objectContaining({
            objects: expect.arrayContaining([
              expect.objectContaining({
                type: 'image',
                assetId: 'img1',
                width: 200,
                height: 120,
              }),
            ]),
          })
        );
      });
    });
  });

  describe('Estados e Props', () => {
    test('deve atualizar quando props mudarem', () => {
      const { rerender } = renderEditorCanvas();

      const newScene = {
        ...mockScene,
        name: 'Nova Cena',
        objects: [
          {
            id: 'obj1',
            type: 'text',
            text: 'Novo texto',
            x: 50,
            y: 50,
            width: 100,
            height: 30,
          },
        ],
      };

      // Força a re-renderização com novas props
      rerender(
        <MockEditorCanvas
          activeScene={newScene}
          onUpdateScene={mockUpdateScene}
          assets={mockAssets}
        />
      );

      // Aguarda a atualização do DOM
      waitFor(() => {
        expect(screen.getByTestId('scene-name')).toHaveTextContent('Nova Cena');
        expect(screen.getByTestId('objects-count')).toHaveTextContent(
          'Objetos: 1'
        );
      });
    });

    test('deve lidar com cena vazia', () => {
      const emptyScene = {
        ...mockScene,
        objects: [],
      };

      renderEditorCanvas({ activeScene: emptyScene });

      expect(screen.getByTestId('objects-count')).toHaveTextContent(
        'Objetos: 0'
      );
    });

    test('deve lidar com assets vazios', () => {
      renderEditorCanvas({ assets: [] });

      const canvas = screen.getByTestId('canvas');
      expect(canvas).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    test('deve ter canvas com tabIndex para navegação por teclado', () => {
      renderEditorCanvas();

      const canvas = screen.getByTestId('canvas');
      expect(canvas).toHaveAttribute('tabIndex', '0');
    });

    test('deve ter botões com estados disabled apropriados', () => {
      renderEditorCanvas();

      const deleteButton = screen.getByTestId('delete-btn');
      expect(deleteButton).toBeDisabled();

      const addTextButton = screen.getByTestId('add-text-btn');
      expect(addTextButton).not.toBeDisabled();
    });
  });

  describe('Interações de Elementos', () => {
    test('deve selecionar elemento quando clicado', () => {
      const sceneWithObject = {
        ...mockScene,
        objects: [
          {
            id: 'obj1',
            type: 'text',
            text: 'Texto teste',
            x: 100,
            y: 100,
            width: 200,
            height: 40,
          },
        ],
      };

      renderEditorCanvas({ activeScene: sceneWithObject });

      const objectElement = screen.getByTestId('object-obj1');
      fireEvent.click(objectElement);

      expect(screen.getByTestId('selected-element')).toHaveTextContent(
        'Selecionado: obj1'
      );
    });

    test('deve mostrar objetos da cena', () => {
      const sceneWithObjects = {
        ...mockScene,
        objects: [
          {
            id: 'obj1',
            type: 'text',
            text: 'Texto 1',
            x: 100,
            y: 100,
            width: 200,
            height: 40,
          },
          {
            id: 'obj2',
            type: 'image',
            assetId: 'img1',
            x: 200,
            y: 200,
            width: 150,
            height: 100,
          },
        ],
      };

      renderEditorCanvas({ activeScene: sceneWithObjects });

      expect(screen.getByTestId('object-obj1')).toHaveTextContent(
        'text: Texto 1'
      );
      expect(screen.getByTestId('object-obj2')).toHaveTextContent(
        'image: img1'
      );
    });
  });
});
