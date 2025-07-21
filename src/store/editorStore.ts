// src/store/editorStore.ts
import { create } from 'zustand';
import { Scene, Asset, EditorElement } from '../types/editor';

/**
 * Interface que define a estrutura do estado global do editor.
 */
interface EditorState {
  scenes: Scene[];
  assets: Asset[];
  selectedElement: EditorElement | null;
  currentSceneId: string | null;

  // Ações para manipular o estado
  addScene: (scene: Scene) => void;
  updateScene: (sceneId: string, updatedScene: Partial<Scene>) => void;
  deleteScene: (sceneId: string) => void;
  reorderScenes: (scenes: Scene[]) => void;

  addAsset: (asset: Asset) => void;
  deleteAsset: (assetId: string) => void;

  setSelectedElement: (element: EditorElement | null) => void;
  updateElement: (sceneId: string, elementId: string, updatedElement: Partial<EditorElement>) => void;

  setCurrentSceneId: (sceneId: string | null) => void;
}

/**
 * Criação do store Zustand para gerenciar o estado global do editor.
 *
 * O store centraliza todas as informações sobre cenas, assets e o estado da interface,
 * permitindo que os componentes acessem e modifiquem o estado de forma consistente.
 */
export const useEditorStore = create<EditorState>((set) => ({
  // Estado inicial
  scenes: [],
  assets: [],
  selectedElement: null,
  currentSceneId: null,

  // Ações para Cenas
  addScene: (scene) => set((state) => ({ scenes: [...state.scenes, scene] })),
  updateScene: (sceneId, updatedScene) =>
    set((state) => ({
      scenes: state.scenes.map((scene) =>
        scene.id === sceneId ? { ...scene, ...updatedScene } : scene
      ),
    })),
  deleteScene: (sceneId) =>
    set((state) => ({
      scenes: state.scenes.filter((scene) => scene.id !== sceneId),
    })),
  reorderScenes: (scenes) => set({ scenes }),

  // Ações para Assets
  addAsset: (asset) => set((state) => ({ assets: [...state.assets, asset] })),
  deleteAsset: (assetId) =>
    set((state) => ({
      assets: state.assets.filter((asset) => asset.id !== assetId),
    })),

  // Ações para Elementos
  setSelectedElement: (element) => set({ selectedElement: element }),
  updateElement: (sceneId, elementId, updatedElement) =>
    set((state) => ({
      scenes: state.scenes.map((scene) =>
        scene.id === sceneId
          ? {
              ...scene,
              elements: scene.elements.map((el) =>
                el.id === elementId ? { ...el, ...updatedElement } : el
              ),
            }
          : scene
      ),
    })),

  // Ação para Cena Atual
  setCurrentSceneId: (sceneId) => set({ currentSceneId: sceneId }),
})); 