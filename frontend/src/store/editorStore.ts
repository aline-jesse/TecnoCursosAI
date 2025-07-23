// src/store/editorStore.ts
import create from 'zustand';
import {
  Asset,
  EditorElement,
  EditorState,
  History,
  HistoryUpdate,
  Scene,
} from '../types/editor';

const INITIAL_STATE: Partial<EditorState> = {
  scenes: [],
  currentScene: null,
  selectedElement: null,
  clipboard: null,
  history: {
    past: [],
    present: [],
    future: [],
  },
  assets: [],
  zoom: 1,
  isDragging: false,
  isPlaying: false,
  currentTime: 0,
};

// Helper para atualizar o histórico
const updateHistory = (state: EditorState, _update: HistoryUpdate): History => {
  const newPresent = [...state.scenes];

  return {
    past: [...state.history.past, state.history.present],
    present: newPresent,
    future: [],
  };
};

export const useEditorStore = create<EditorState>((set, get) => ({
  ...(INITIAL_STATE as EditorState),

  // Métodos de manipulação de elementos
  addElement: (element: EditorElement) =>
    set(state => {
      if (!state.currentScene) return state;

      const updatedScene = {
        ...state.currentScene,
        elements: [...state.currentScene.elements, element],
      };

      const sceneIndex = state.scenes.findIndex(
        s => s.id === state.currentScene?.id
      );
      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = updatedScene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene: updatedScene,
        history: updateHistory(state, {
          type: 'add',
          payload: element,
          timestamp: Date.now(),
        }),
      };
    }),

  updateElement: (element: EditorElement) =>
    set(state => {
      if (!state.currentScene) return state;

      const elementIndex = state.currentScene.elements.findIndex(
        e => e.id === element.id
      );
      if (elementIndex === -1) return state;

      const updatedElements = [...state.currentScene.elements];
      updatedElements[elementIndex] = element;

      const updatedScene = {
        ...state.currentScene,
        elements: updatedElements,
      };

      const sceneIndex = state.scenes.findIndex(
        s => s.id === state.currentScene?.id
      );
      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = updatedScene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene: updatedScene,
        history: updateHistory(state, {
          type: 'update',
          payload: element,
          timestamp: Date.now(),
        }),
      };
    }),

  deleteElement: (elementId: string) =>
    set(state => {
      if (!state.currentScene) return state;

      const updatedElements = state.currentScene.elements.filter(
        e => e.id !== elementId
      );
      const updatedScene = {
        ...state.currentScene,
        elements: updatedElements,
      };

      const sceneIndex = state.scenes.findIndex(
        s => s.id === state.currentScene?.id
      );
      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = updatedScene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene: updatedScene,
        selectedElement: null,
        history: updateHistory(state, {
          type: 'delete',
          payload: elementId,
          timestamp: Date.now(),
        }),
      };
    }),

  duplicateElement: (elementId: string) =>
    set(state => {
      if (!state.currentScene) return state;

      const element = state.currentScene.elements.find(e => e.id === elementId);
      if (!element) return state;

      const duplicatedElement = {
        ...element,
        id: `${element.id}_copy_${Date.now()}`,
        x: element.x + 20,
        y: element.y + 20,
      };

      const updatedScene = {
        ...state.currentScene,
        elements: [...state.currentScene.elements, duplicatedElement],
      };

      const sceneIndex = state.scenes.findIndex(
        s => s.id === state.currentScene?.id
      );
      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = updatedScene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene: updatedScene,
        history: updateHistory(state, {
          type: 'add',
          payload: duplicatedElement,
          timestamp: Date.now(),
        }),
      };
    }),

  bringToFront: (elementId: string) =>
    set(state => {
      if (!state.currentScene) return state;

      const elements = [...state.currentScene.elements];
      const elementIndex = elements.findIndex(e => e.id === elementId);
      if (elementIndex === -1) return state;

      const element = elements[elementIndex];
      elements.splice(elementIndex, 1);
      elements.push(element);

      const updatedScene = {
        ...state.currentScene,
        elements,
      };

      const sceneIndex = state.scenes.findIndex(
        s => s.id === state.currentScene?.id
      );
      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = updatedScene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene: updatedScene,
        history: updateHistory(state, {
          type: 'reorder',
          payload: { elementId, type: 'front' },
          timestamp: Date.now(),
        }),
      };
    }),

  sendToBack: (elementId: string) =>
    set(state => {
      if (!state.currentScene) return state;

      const elements = [...state.currentScene.elements];
      const elementIndex = elements.findIndex(e => e.id === elementId);
      if (elementIndex === -1) return state;

      const element = elements[elementIndex];
      elements.splice(elementIndex, 1);
      elements.unshift(element);

      const updatedScene = {
        ...state.currentScene,
        elements,
      };

      const sceneIndex = state.scenes.findIndex(
        s => s.id === state.currentScene?.id
      );
      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = updatedScene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene: updatedScene,
        history: updateHistory(state, {
          type: 'reorder',
          payload: { elementId, type: 'back' },
          timestamp: Date.now(),
        }),
      };
    }),

  copyElement: (elementId: string) =>
    set(state => {
      if (!state.currentScene) return state;

      const element = state.currentScene.elements.find(e => e.id === elementId);
      if (!element) return state;

      return {
        ...state,
        clipboard: element,
      };
    }),

  pasteElement: () =>
    set(state => {
      if (!state.clipboard || !state.currentScene) return state;

      const pastedElement = {
        ...state.clipboard,
        id: `${state.clipboard.id}_copy_${Date.now()}`,
        x: state.clipboard.x + 20,
        y: state.clipboard.y + 20,
      };

      const updatedScene = {
        ...state.currentScene,
        elements: [...state.currentScene.elements, pastedElement],
      };

      const sceneIndex = state.scenes.findIndex(
        s => s.id === state.currentScene?.id
      );
      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = updatedScene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene: updatedScene,
        history: updateHistory(state, {
          type: 'add',
          payload: pastedElement,
          timestamp: Date.now(),
        }),
      };
    }),

  // Métodos de manipulação de cenas
  addScene: (scene: Scene) =>
    set(state => ({
      ...state,
      scenes: [...state.scenes, scene],
      currentScene: scene,
      history: updateHistory(state, {
        type: 'add',
        payload: scene,
        timestamp: Date.now(),
      }),
    })),

  updateScene: (scene: Scene) =>
    set(state => {
      const sceneIndex = state.scenes.findIndex(s => s.id === scene.id);
      if (sceneIndex === -1) return state;

      const updatedScenes = [...state.scenes];
      updatedScenes[sceneIndex] = scene;

      return {
        ...state,
        scenes: updatedScenes,
        currentScene:
          scene.id === state.currentScene?.id ? scene : state.currentScene,
        history: updateHistory(state, {
          type: 'update',
          payload: scene,
          timestamp: Date.now(),
        }),
      };
    }),

  deleteScene: (sceneId: string) =>
    set(state => {
      const updatedScenes = state.scenes.filter(s => s.id !== sceneId);
      const currentSceneIndex = state.scenes.findIndex(s => s.id === sceneId);

      return {
        ...state,
        scenes: updatedScenes,
        currentScene:
          state.currentScene?.id === sceneId
            ? updatedScenes[
                Math.min(currentSceneIndex, updatedScenes.length - 1)
              ] || null
            : state.currentScene,
        history: updateHistory(state, {
          type: 'delete',
          payload: sceneId,
          timestamp: Date.now(),
        }),
      };
    }),

  reorderScenes: (sourceIndex: number, targetIndex: number) =>
    set(state => {
      const updatedScenes = [...state.scenes];
      const [movedScene] = updatedScenes.splice(sourceIndex, 1);
      updatedScenes.splice(targetIndex, 0, movedScene);

      return {
        ...state,
        scenes: updatedScenes,
        history: updateHistory(state, {
          type: 'reorder',
          payload: { sourceIndex, targetIndex },
          timestamp: Date.now(),
        }),
      };
    }),

  // Métodos de histórico
  undo: () =>
    set(state => {
      if (state.history.past.length === 0) return state;

      const previous = state.history.past[state.history.past.length - 1];
      const newPast = state.history.past.slice(0, -1);

      return {
        ...state,
        scenes: previous,
        currentScene:
          previous.find(s => s.id === state.currentScene?.id) ||
          previous[0] ||
          null,
        history: {
          past: newPast,
          present: previous,
          future: [state.scenes, ...state.history.future],
        },
      };
    }),

  redo: () =>
    set(state => {
      if (state.history.future.length === 0) return state;

      const next = state.history.future[0];
      const newFuture = state.history.future.slice(1);

      return {
        ...state,
        scenes: next,
        currentScene:
          next.find(s => s.id === state.currentScene?.id) || next[0] || null,
        history: {
          past: [...state.history.past, state.scenes],
          present: next,
          future: newFuture,
        },
      };
    }),

  // Métodos de assets
  addAsset: (asset: Asset) =>
    set(state => ({
      ...state,
      assets: [...state.assets, asset],
    })),

  deleteAsset: (assetId: string) =>
    set(state => ({
      ...state,
      assets: state.assets.filter(a => a.id !== assetId),
    })),

  updateAsset: (asset: Asset) =>
    set(state => {
      const assetIndex = state.assets.findIndex(a => a.id === asset.id);
      if (assetIndex === -1) return state;

      const updatedAssets = [...state.assets];
      updatedAssets[assetIndex] = asset;

      return {
        ...state,
        assets: updatedAssets,
      };
    }),
}));
