/**
 * Hooks personalizados para o Editor - TecnoCursos AI
 * Gerenciamento de estado, API calls e funcionalidades específicas
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
import apiService from '../services/apiService';
import websocketService from '../services/websocketService';
import {
  config,
  logger,
  canvasConfig,
  timelineConfig,
} from '../config/environment';

/**
 * Hook principal para gerenciamento do estado do editor
 */
export const useEditor = () => {
  // Estados principais
  const [currentProject, setCurrentProject] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [selectedElements, setSelectedElements] = useState([]);
  const [canvasZoom, setCanvasZoom] = useState(1);
  const [timelineZoom, setTimelineZoom] = useState(100);
  const [playhead, setPlayhead] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [undoStack, setUndoStack] = useState([]);
  const [redoStack, setRedoStack] = useState([]);
  const [clipboard, setClipboard] = useState(null);

  // Estado de carregamento e erros
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState('saved'); // 'saving', 'saved', 'error'

  // Refs para auto-save e performance
  const saveTimeoutRef = useRef(null);
  const lastSaveRef = useRef(null);

  /**
   * Carregar projeto
   */
  const loadProject = useCallback(async projectId => {
    setIsLoading(true);
    setError(null);

    try {
      const project = await apiService.projects.getProject(projectId);
      setCurrentProject(project);

      // Carregar cenas do projeto
      if (project.scenes) {
        setScenes(project.scenes);
      }

      logger.info('Projeto carregado:', project);
    } catch (error) {
      const apiError = apiService.handleApiError(error);
      setError(apiError.message);
      logger.error('Erro ao carregar projeto:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Salvar projeto (auto-save)
   */
  const saveProject = useCallback(
    async (immediate = false) => {
      if (!currentProject) return;

      // Cancelar save anterior se existir
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }

      const doSave = async () => {
        setSaveStatus('saving');

        try {
          const projectData = {
            ...currentProject,
            scenes,
            updated_at: new Date().toISOString(),
          };

          await apiService.projects.updateProject(
            currentProject.id,
            projectData
          );
          setSaveStatus('saved');
          lastSaveRef.current = Date.now();

          logger.info('Projeto salvo automaticamente');
        } catch (error) {
          setSaveStatus('error');
          logger.error('Erro ao salvar projeto:', error);
        }
      };

      if (immediate) {
        await doSave();
      } else {
        // Auto-save com delay
        saveTimeoutRef.current = setTimeout(doSave, config.AUTO_SAVE_INTERVAL);
      }
    },
    [currentProject, scenes]
  );

  /**
   * Adicionar à pilha de undo
   */
  const addToUndoStack = useCallback(action => {
    setUndoStack(prev => {
      const newStack = [...prev, action];
      if (newStack.length > config.UNDO_LIMIT) {
        newStack.shift();
      }
      return newStack;
    });
    setRedoStack([]); // Limpar redo stack
  }, []);

  /**
   * Operações de Undo/Redo
   */
  const undo = useCallback(() => {
    if (undoStack.length === 0) return;

    const action = undoStack[undoStack.length - 1];
    setUndoStack(prev => prev.slice(0, -1));
    setRedoStack(prev => [...prev, action]);

    // Aplicar undo baseado no tipo de ação
    switch (action.type) {
      case 'add_scene':
        setScenes(prev => prev.filter(s => s.id !== action.data.id));
        break;
      case 'delete_scene':
        setScenes(prev => [...prev, action.data]);
        break;
      case 'move_element':
        // Reverter movimento
        updateElement(action.data.id, {
          x: action.data.oldPosition.x,
          y: action.data.oldPosition.y,
        });
        break;
      default:
        logger.warn('Tipo de ação undo não implementada:', action.type);
    }
  }, [undoStack]);

  const redo = useCallback(() => {
    if (redoStack.length === 0) return;

    const action = redoStack[redoStack.length - 1];
    setRedoStack(prev => prev.slice(0, -1));
    setUndoStack(prev => [...prev, action]);

    // Aplicar redo baseado no tipo de ação
    switch (action.type) {
      case 'add_scene':
        setScenes(prev => [...prev, action.data]);
        break;
      case 'delete_scene':
        setScenes(prev => prev.filter(s => s.id !== action.data.id));
        break;
      case 'move_element':
        updateElement(action.data.id, {
          x: action.data.newPosition.x,
          y: action.data.newPosition.y,
        });
        break;
      default:
        logger.warn('Tipo de ação redo não implementada:', action.type);
    }
  }, [redoStack]);

  /**
   * Operações com cenas
   */
  const addScene = useCallback(
    (sceneData = {}) => {
      const newScene = {
        id: `scene_${Date.now()}`,
        title: sceneData.title || `Cena ${scenes.length + 1}`,
        duration: sceneData.duration || timelineConfig.defaultDuration,
        elements: sceneData.elements || [],
        background: sceneData.background || null,
        created_at: new Date().toISOString(),
        ...sceneData,
      };

      setScenes(prev => [...prev, newScene]);
      addToUndoStack({ type: 'add_scene', data: newScene });
      saveProject();

      return newScene;
    },
    [scenes, addToUndoStack, saveProject]
  );

  const deleteScene = useCallback(
    sceneId => {
      const sceneToDelete = scenes.find(s => s.id === sceneId);
      if (!sceneToDelete) return;

      setScenes(prev => prev.filter(s => s.id !== sceneId));
      addToUndoStack({ type: 'delete_scene', data: sceneToDelete });
      saveProject();
    },
    [scenes, addToUndoStack, saveProject]
  );

  const duplicateScene = useCallback(
    sceneId => {
      const sceneToDuplicate = scenes.find(s => s.id === sceneId);
      if (!sceneToDuplicate) return;

      const newScene = {
        ...sceneToDuplicate,
        id: `scene_${Date.now()}`,
        title: `${sceneToDuplicate.title} (Cópia)`,
        elements: sceneToDuplicate.elements.map(el => ({
          ...el,
          id: `element_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        })),
      };

      setScenes(prev => [...prev, newScene]);
      addToUndoStack({ type: 'add_scene', data: newScene });
      saveProject();

      return newScene;
    },
    [scenes, addToUndoStack, saveProject]
  );

  /**
   * Operações com elementos
   */
  const addElement = useCallback(
    (sceneId, elementData) => {
      const newElement = {
        id: `element_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: elementData.type || 'text',
        x: elementData.x || 0,
        y: elementData.y || 0,
        width: elementData.width || 100,
        height: elementData.height || 100,
        rotation: elementData.rotation || 0,
        opacity: elementData.opacity || 1,
        zIndex: elementData.zIndex || 0,
        created_at: new Date().toISOString(),
        ...elementData,
      };

      setScenes(prev =>
        prev.map(scene =>
          scene.id === sceneId
            ? { ...scene, elements: [...scene.elements, newElement] }
            : scene
        )
      );

      addToUndoStack({
        type: 'add_element',
        data: { sceneId, element: newElement },
      });
      saveProject();

      return newElement;
    },
    [addToUndoStack, saveProject]
  );

  const updateElement = useCallback(
    (elementId, updates) => {
      setScenes(prev =>
        prev.map(scene => ({
          ...scene,
          elements: scene.elements.map(element =>
            element.id === elementId
              ? { ...element, ...updates, updated_at: new Date().toISOString() }
              : element
          ),
        }))
      );
      saveProject();
    },
    [saveProject]
  );

  const deleteElement = useCallback(
    elementId => {
      let deletedElement = null;
      let sceneId = null;

      setScenes(prev =>
        prev.map(scene => {
          const elementIndex = scene.elements.findIndex(
            el => el.id === elementId
          );
          if (elementIndex > -1) {
            deletedElement = scene.elements[elementIndex];
            sceneId = scene.id;
            return {
              ...scene,
              elements: scene.elements.filter(el => el.id !== elementId),
            };
          }
          return scene;
        })
      );

      if (deletedElement) {
        addToUndoStack({
          type: 'delete_element',
          data: { sceneId, element: deletedElement },
        });
        saveProject();
      }
    },
    [addToUndoStack, saveProject]
  );

  /**
   * Operações de seleção
   */
  const selectElement = useCallback((elementId, multiSelect = false) => {
    if (multiSelect) {
      setSelectedElements(prev =>
        prev.includes(elementId)
          ? prev.filter(id => id !== elementId)
          : [...prev, elementId]
      );
    } else {
      setSelectedElements([elementId]);
    }
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedElements([]);
  }, []);

  /**
   * Operações de clipboard
   */
  const copyElements = useCallback(() => {
    if (selectedElements.length === 0) return;

    const elementsToCopy = [];
    scenes.forEach(scene => {
      scene.elements.forEach(element => {
        if (selectedElements.includes(element.id)) {
          elementsToCopy.push(element);
        }
      });
    });

    setClipboard(elementsToCopy);
    logger.info(`${elementsToCopy.length} elementos copiados`);
  }, [selectedElements, scenes]);

  const pasteElements = useCallback(
    targetSceneId => {
      if (!clipboard || clipboard.length === 0) return;

      const pastedElements = clipboard.map(element => ({
        ...element,
        id: `element_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        x: element.x + 20, // Offset para não sobrepor
        y: element.y + 20,
      }));

      setScenes(prev =>
        prev.map(scene =>
          scene.id === targetSceneId
            ? { ...scene, elements: [...scene.elements, ...pastedElements] }
            : scene
        )
      );

      addToUndoStack({
        type: 'paste_elements',
        data: { sceneId: targetSceneId, elements: pastedElements },
      });
      saveProject();

      return pastedElements;
    },
    [clipboard, addToUndoStack, saveProject]
  );

  /**
   * Controles de timeline
   */
  const play = useCallback(() => {
    setIsPlaying(true);
    // Implementar lógica de play
  }, []);

  const pause = useCallback(() => {
    setIsPlaying(false);
  }, []);

  const stop = useCallback(() => {
    setIsPlaying(false);
    setPlayhead(0);
  }, []);

  /**
   * Configurar shortcuts de teclado
   */
  useHotkeys('ctrl+z, cmd+z', undo, { enableOnTags: ['INPUT', 'TEXTAREA'] });
  useHotkeys('ctrl+y, cmd+y, ctrl+shift+z', redo, {
    enableOnTags: ['INPUT', 'TEXTAREA'],
  });
  useHotkeys('ctrl+c, cmd+c', copyElements);
  useHotkeys('ctrl+v, cmd+v', () => {
    if (scenes.length > 0) {
      pasteElements(scenes[0].id); // Colar na primeira cena por padrão
    }
  });
  useHotkeys('delete, backspace', () => {
    selectedElements.forEach(deleteElement);
  });
  useHotkeys('space', e => {
    e.preventDefault();
    isPlaying ? pause() : play();
  });

  // Auto-save quando houver mudanças
  useEffect(() => {
    if (currentProject && scenes.length > 0) {
      saveProject();
    }
  }, [scenes, currentProject, saveProject]);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  return {
    // Estado
    currentProject,
    scenes,
    selectedElements,
    canvasZoom,
    timelineZoom,
    playhead,
    isPlaying,
    isLoading,
    error,
    saveStatus,
    undoStack,
    redoStack,
    clipboard,

    // Ações de projeto
    loadProject,
    saveProject,

    // Ações de undo/redo
    undo,
    redo,
    canUndo: undoStack.length > 0,
    canRedo: redoStack.length > 0,

    // Ações de cenas
    addScene,
    deleteScene,
    duplicateScene,

    // Ações de elementos
    addElement,
    updateElement,
    deleteElement,

    // Ações de seleção
    selectElement,
    clearSelection,

    // Ações de clipboard
    copyElements,
    pasteElements,

    // Controles de timeline
    play,
    pause,
    stop,
    setPlayhead,

    // Controles de zoom
    setCanvasZoom,
    setTimelineZoom,
  };
};
