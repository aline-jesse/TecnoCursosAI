import { renderHook, act } from '@testing-library/react';
import { useEditorStore } from '../useEditorStore';

describe('useEditorStore Hook', () => {
  beforeEach(() => {
    // Reset do store antes de cada teste
    const { result } = renderHook(() => useEditorStore());
    act(() => {
      result.current.setScenes([]);
      result.current.setAssets([]);
    });
  });

  describe('Inicialização', () => {
    it('deve inicializar com estado vazio', () => {
      const { result } = renderHook(() => useEditorStore());

      expect(result.current.scenes).toEqual([]);
      expect(result.current.assets).toEqual([]);
      expect(result.current.selectedElementId).toBeNull();
      expect(result.current.currentSceneId).toBeNull();
      expect(result.current.draggedAsset).toBeNull();
      expect(result.current.clipboard).toBeNull();
    });

    it('deve ter histórico inicializado', () => {
      const { result } = renderHook(() => useEditorStore());

      expect(result.current.history).toBeDefined();
      expect(result.current.history.past).toEqual([]);
      expect(result.current.history.present).toEqual([]);
      expect(result.current.history.future).toEqual([]);
    });
  });

  describe('Gerenciamento de Estado', () => {
    it('deve atualizar estado de forma imutável', () => {
      const { result } = renderHook(() => useEditorStore());

      const initialScenes = result.current.scenes;

      act(() => {
        result.current.setScenes([
          {
            id: 'scene-1',
            name: 'Test',
            duration: 10,
            elements: [],
            thumbnail: '',
          },
        ]);
      });

      expect(result.current.scenes).not.toBe(initialScenes);
      expect(result.current.scenes).toHaveLength(1);
    });

    it('deve manter referências estáveis para funções', () => {
      const { result, rerender } = renderHook(() => useEditorStore());

      const initialAddScene = result.current.addScene;

      rerender();

      expect(result.current.addScene).toBe(initialAddScene);
    });
  });

  describe('Integração com Histórico', () => {
    it('deve registrar ações no histórico', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene = {
        id: 'scene-1',
        name: 'Test',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(scene);
      });

      expect(result.current.history.past).toHaveLength(1);
      expect(result.current.history.present).toHaveLength(1);
      expect(result.current.history.future).toHaveLength(0);
    });

    it('deve permitir navegação no histórico', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene1 = {
        id: 'scene-1',
        name: 'Scene 1',
        duration: 10,
        elements: [],
        thumbnail: '',
      };
      const scene2 = {
        id: 'scene-2',
        name: 'Scene 2',
        duration: 10,
        elements: [],
        thumbnail: '',
      };

      act(() => {
        result.current.addScene(scene1);
        result.current.addScene(scene2);
      });

      expect(result.current.scenes).toHaveLength(2);

      act(() => {
        result.current.undo();
      });

      expect(result.current.scenes).toHaveLength(1);
      expect(result.current.scenes[0].id).toBe('scene-1');

      act(() => {
        result.current.redo();
      });

      expect(result.current.scenes).toHaveLength(2);
      expect(result.current.scenes[1].id).toBe('scene-2');
    });
  });

  describe('Operações de Elementos', () => {
    it('deve adicionar elemento com histórico', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene = {
        id: 'scene-1',
        name: 'Test',
        duration: 10,
        elements: [],
        thumbnail: '',
      };
      const element = {
        id: 'element-1',
        type: 'text' as const,
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Test',
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

    it('deve atualizar elemento preservando outros', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene = {
        id: 'scene-1',
        name: 'Test',
        duration: 10,
        elements: [],
        thumbnail: '',
      };
      const element1 = {
        id: 'element-1',
        type: 'text' as const,
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Element 1',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };
      const element2 = {
        id: 'element-2',
        type: 'text' as const,
        x: 200,
        y: 200,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Element 2',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.addElement('scene-1', element1);
        result.current.addElement('scene-1', element2);
        result.current.updateElement('scene-1', 'element-1', {
          text: 'Updated Element 1',
        });
      });

      const updatedScene = result.current.scenes.find(s => s.id === 'scene-1');
      expect(updatedScene?.elements).toHaveLength(2);
      expect(updatedScene?.elements[0].text).toBe('Updated Element 1');
      expect(updatedScene?.elements[1].text).toBe('Element 2');
    });
  });

  describe('Operações de Assets', () => {
    it('deve gerenciar assets sem afetar histórico', () => {
      const { result } = renderHook(() => useEditorStore());

      const asset = {
        id: 'asset-1',
        name: 'Test Asset',
        type: 'image' as const,
        src: '/test.jpg',
        thumbnail: '/test-thumb.jpg',
      };

      act(() => {
        result.current.addAsset(asset);
      });

      expect(result.current.assets).toHaveLength(1);
      expect(result.current.assets[0]).toEqual(asset);
      expect(result.current.history.past).toHaveLength(0); // Assets não afetam histórico
    });

    it('deve permitir múltiplos assets', () => {
      const { result } = renderHook(() => useEditorStore());

      const asset1 = {
        id: 'asset-1',
        name: 'Asset 1',
        type: 'image' as const,
        src: '/1.jpg',
        thumbnail: '/1-thumb.jpg',
      };
      const asset2 = {
        id: 'asset-2',
        name: 'Asset 2',
        type: 'character' as const,
        src: '/2.jpg',
        thumbnail: '/2-thumb.jpg',
      };

      act(() => {
        result.current.addAsset(asset1);
        result.current.addAsset(asset2);
      });

      expect(result.current.assets).toHaveLength(2);
      expect(result.current.assets[0]).toEqual(asset1);
      expect(result.current.assets[1]).toEqual(asset2);
    });
  });

  describe('Estados de UI', () => {
    it('deve gerenciar seleção de elementos', () => {
      const { result } = renderHook(() => useEditorStore());

      act(() => {
        result.current.setSelectedElementId('element-1');
      });

      expect(result.current.selectedElementId).toBe('element-1');

      act(() => {
        result.current.setSelectedElementId(null);
      });

      expect(result.current.selectedElementId).toBeNull();
    });

    it('deve gerenciar cena atual', () => {
      const { result } = renderHook(() => useEditorStore());

      act(() => {
        result.current.setCurrentSceneId('scene-1');
      });

      expect(result.current.currentSceneId).toBe('scene-1');
    });

    it('deve gerenciar asset arrastado', () => {
      const { result } = renderHook(() => useEditorStore());

      const asset = {
        id: 'asset-1',
        name: 'Test',
        type: 'image' as const,
        src: '/test.jpg',
        thumbnail: '/test-thumb.jpg',
      };

      act(() => {
        result.current.setDraggedAsset(asset);
      });

      expect(result.current.draggedAsset).toEqual(asset);

      act(() => {
        result.current.setDraggedAsset(null);
      });

      expect(result.current.draggedAsset).toBeNull();
    });
  });

  describe('Clipboard', () => {
    it('deve copiar e colar elementos', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene = {
        id: 'scene-1',
        name: 'Test',
        duration: 10,
        elements: [],
        thumbnail: '',
      };
      const element = {
        id: 'element-1',
        type: 'text' as const,
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: 'Test Element',
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      };

      act(() => {
        result.current.addScene(scene);
        result.current.addElement('scene-1', element);
        result.current.copyElement('element-1');
      });

      expect(result.current.clipboard).toEqual(element);

      act(() => {
        result.current.pasteElement('scene-1');
      });

      const updatedScene = result.current.scenes.find(s => s.id === 'scene-1');
      expect(updatedScene?.elements).toHaveLength(2);
      expect(updatedScene?.elements[1].text).toBe('Test Element');
      expect(updatedScene?.elements[1].id).not.toBe('element-1'); // Novo ID
    });
  });

  describe('Performance', () => {
    it('deve lidar com muitas cenas eficientemente', () => {
      const { result } = renderHook(() => useEditorStore());

      const scenes = Array.from({ length: 100 }, (_, i) => ({
        id: `scene-${i}`,
        name: `Scene ${i}`,
        duration: 10,
        elements: [],
        thumbnail: '',
      }));

      act(() => {
        result.current.setScenes(scenes);
      });

      expect(result.current.scenes).toHaveLength(100);
    });

    it('deve lidar com muitos elementos eficientemente', () => {
      const { result } = renderHook(() => useEditorStore());

      const scene = {
        id: 'scene-1',
        name: 'Test',
        duration: 10,
        elements: [],
        thumbnail: '',
      };
      const elements = Array.from({ length: 50 }, (_, i) => ({
        id: `element-${i}`,
        type: 'text' as const,
        x: i * 10,
        y: i * 10,
        width: 100,
        height: 50,
        rotation: 0,
        opacity: 1,
        text: `Element ${i}`,
        fontSize: 16,
        fontFamily: 'Arial',
        fill: '#000000',
      }));

      act(() => {
        result.current.addScene(scene);
        elements.forEach(element => {
          result.current.addElement('scene-1', element);
        });
      });

      const updatedScene = result.current.scenes.find(s => s.id === 'scene-1');
      expect(updatedScene?.elements).toHaveLength(50);
    });
  });
});
