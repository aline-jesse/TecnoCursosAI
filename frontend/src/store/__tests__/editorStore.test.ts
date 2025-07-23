import { renderHook, act } from '@testing-library/react';
import { useEditorStore } from '../editorStore';
import { Scene, EditorElement, Asset } from '../../types/editor';

describe('EditorStore', () => {
  beforeEach(() => {
    // Reset do store antes de cada teste
    const { result } = renderHook(() => useEditorStore());
    act(() => {
      result.current.setScenes([]);
      result.current.setAssets([]);
      result.current.setSelectedElementId(null);
      result.current.setCurrentSceneId(null);
    });
  });

  describe('Gerenciamento de Cenas', () => {
    it('deve adicionar uma nova cena', () => {
      const { result } = renderHook(() => useEditorStore());

      const newScene: Scene = {
        id: 'scene-1',
        name: 'Nova Cena',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(newScene);
      });

      expect(result.current.scenes).toHaveLength(1);
      expect(result.current.scenes[0]).toEqual(newScene);
    });

    it('deve atualizar uma cena existente', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena Original',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.updateScene('scene-1', { name: 'Cena Atualizada' });
      });

      expect(result.current.scenes[0].name).toBe('Cena Atualizada');
    });

    it('deve deletar uma cena', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena para Deletar',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.deleteScene('scene-1');
      });

      expect(result.current.scenes).toHaveLength(0);
    });

    it('deve reordenar cenas', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene1: Scene = {
        id: 'scene-1',
        name: 'Cena 1',
        duration: 10,
        elements: [],
        thumbnail: '',
      };
      const scene2: Scene = {
        id: 'scene-2',
        name: 'Cena 2',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(scene1);
        result.current.addScene(scene2);
        result.current.reorderScenes([scene2, scene1]);
      });

      expect(result.current.scenes[0].id).toBe('scene-2');
      expect(result.current.scenes[1].id).toBe('scene-1');
    });
  });

  describe('Gerenciamento de Elementos', () => {
    it('deve adicionar elemento a uma cena', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena Teste',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      const element: EditorElement = {
        id: 'element-1',
        type: 'text',
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Texto Teste',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.addElement('scene-1', element);
      });

      const updatedScene = result.current.scenes.find(s => s.id === 'scene-1');
      expect(updatedScene?.elements).toHaveLength(1);
      expect(updatedScene?.elements[0]).toEqual(element);
    });

    it('deve atualizar elemento existente', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena Teste',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      const element: EditorElement = {
        id: 'element-1',
        type: 'text',
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Texto Original',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.addElement('scene-1', element);
        result.current.updateElement('scene-1', 'element-1', {
          text: 'Texto Atualizado',
        });
      });

      const updatedScene = result.current.scenes.find(s => s.id === 'scene-1');
      expect(updatedScene?.elements[0].text).toBe('Texto Atualizado');
    });

    it('deve deletar elemento', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena Teste',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      const element: EditorElement = {
        id: 'element-1',
        type: 'text',
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Texto Teste',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.addElement('scene-1', element);
        result.current.deleteElement('scene-1', 'element-1');
      });

      const updatedScene = result.current.scenes.find(s => s.id === 'scene-1');
      expect(updatedScene?.elements).toHaveLength(0);
    });
  });

  describe('Gerenciamento de Assets', () => {
    it('deve adicionar novo asset', () => {
      const { result } = renderHook(() => useEditorStore());

      const asset: Asset = {
        id: 'asset-1',
        name: 'Imagem Teste',
        type: 'image',
        src: '/test-image.jpg',
        thumbnail: '/test-thumbnail.jpg',
      };

      act(() => {
        result.current.addAsset(asset);
      });

      expect(result.current.assets).toHaveLength(1);
      expect(result.current.assets[0]).toEqual(asset);
    });

    it('deve deletar asset', () => {
      const { result } = renderHook(() => useEditorStore());

      const asset: Asset = {
        id: 'asset-1',
        name: 'Imagem Teste',
        type: 'image',
        src: '/test-image.jpg',
        thumbnail: '/test-thumbnail.jpg',
      };

      act(() => {
        result.current.addAsset(asset);
        result.current.deleteAsset('asset-1');
      });

      expect(result.current.assets).toHaveLength(0);
    });
  });

  describe('Histórico (Undo/Redo)', () => {
    it('deve permitir desfazer ação', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena Teste',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.undo();
      });

      expect(result.current.scenes).toHaveLength(0);
    });

    it('deve permitir refazer ação', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena Teste',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.undo();
        result.current.redo();
      });

      expect(result.current.scenes).toHaveLength(1);
    });

    it('não deve desfazer quando não há histórico', () => {
      const { result } = renderHook(() => useEditorStore());

      act(() => {
        result.current.undo();
      });

      // Não deve causar erro
      expect(result.current.scenes).toHaveLength(0);
    });
  });

  describe('Estados de Seleção', () => {
    it('deve definir elemento selecionado', () => {
      const { result } = renderHook(() => useEditorStore());

      act(() => {
        result.current.setSelectedElementId('element-1');
      });

      expect(result.current.selectedElementId).toBe('element-1');
    });

    it('deve definir cena atual', () => {
      const { result } = renderHook(() => useEditorStore());

      act(() => {
        result.current.setCurrentSceneId('scene-1');
      });

      expect(result.current.currentSceneId).toBe('scene-1');
    });

    it('deve definir asset arrastado', () => {
      const { result } = renderHook(() => useEditorStore());

      const asset: Asset = {
        id: 'asset-1',
        name: 'Imagem Teste',
        type: 'image',
        src: '/test-image.jpg',
        thumbnail: '/test-thumbnail.jpg',
      };

      act(() => {
        result.current.setDraggedAsset(asset);
      });

      expect(result.current.draggedAsset).toEqual(asset);
    });
  });

  describe('Clipboard', () => {
    it('deve copiar elemento', () => {
      const { result } = renderHook(() => useEditorStore());

      const element: EditorElement = {
        id: 'element-1',
        type: 'text',
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Texto Teste',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };

      act(() => {
        result.current.copyElement('element-1');
      });

      expect(result.current.clipboard).toEqual(element);
    });

    it('deve colar elemento', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene: Scene = {
        id: 'scene-1',
        name: 'Cena Teste',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      const element: EditorElement = {
        id: 'element-1',
        type: 'text',
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Texto Teste',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.copyElement('element-1');
        result.current.pasteElement('scene-1');
      });

      const updatedScene = result.current.scenes.find(s => s.id === 'scene-1');
      expect(updatedScene?.elements).toHaveLength(1);
      expect(updatedScene?.elements[0].id).not.toBe('element-1'); // Novo ID
    });
  });
});
