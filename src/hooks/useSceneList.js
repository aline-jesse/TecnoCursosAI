import { useState, useCallback, useEffect } from 'react';
import sceneListService from '../services/sceneListService';

/**
 * Hook personalizado para gerenciar lista de cenas
 * Integra com o backend através do SceneListService
 * 
 * @param {string} projectId - ID do projeto atual
 * @returns {Object} Estado e métodos para gerenciar cenas
 */
const useSceneList = (projectId) => {
  // Estados principais
  const [scenes, setScenes] = useState([]);
  const [activeSceneId, setActiveSceneId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Estados de operações específicas
  const [isAddingScene, setIsAddingScene] = useState(false);
  const [isRemovingScene, setIsRemovingScene] = useState(false);
  const [isDuplicatingScene, setIsDuplicatingScene] = useState(false);
  const [isReorderingScenes, setIsReorderingScenes] = useState(false);

  /**
   * Limpa erros
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Trata erros de forma centralizada
   * @param {Error} error - Erro capturado
   * @param {string} operation - Operação que falhou
   */
  const handleError = useCallback((error, operation) => {
    console.error(`Erro em ${operation}:`, error);
    setError(`${operation}: ${error.message}`);
  }, []);

  /**
   * Carrega cenas do projeto
   */
  const loadScenes = useCallback(async () => {
    if (!projectId) {
      setScenes([]);
      setActiveSceneId(null);
      return;
    }

    try {
      setIsLoading(true);
      clearError();

      const scenesData = await sceneListService.getScenes(projectId);
      setScenes(scenesData);

      // Seleciona a primeira cena se não há cena ativa
      if (scenesData.length > 0 && !activeSceneId) {
        setActiveSceneId(scenesData[0].id);
      }

      console.log('Cenas carregadas:', scenesData.length);
    } catch (error) {
      handleError(error, 'Carregamento de cenas');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, activeSceneId, clearError, handleError]);

  /**
   * Seleciona uma cena
   * @param {string} sceneId - ID da cena
   */
  const selectScene = useCallback((sceneId) => {
    setActiveSceneId(sceneId);
    console.log('Cena selecionada:', sceneId);
  }, []);

  /**
   * Adiciona uma nova cena
   */
  const addScene = useCallback(async () => {
    if (!projectId) {
      handleError(new Error('Projeto não selecionado'), 'Adição de cena');
      return;
    }

    try {
      setIsAddingScene(true);
      clearError();

      const newSceneData = sceneListService.createDefaultSceneData(scenes.length + 1);
      
      // Valida dados antes de enviar
      const validation = sceneListService.validateSceneData(newSceneData);
      if (!validation.isValid) {
        throw new Error(`Dados inválidos: ${validation.errors.join(', ')}`);
      }

      const newScene = await sceneListService.createScene(projectId, newSceneData);
      
      setScenes(prevScenes => [...prevScenes, newScene]);
      
      // Seleciona a nova cena
      setActiveSceneId(newScene.id);

      console.log('Nova cena criada:', newScene);
    } catch (error) {
      handleError(error, 'Criação de cena');
    } finally {
      setIsAddingScene(false);
    }
  }, [projectId, scenes.length, clearError, handleError]);

  /**
   * Remove uma cena
   * @param {string} sceneId - ID da cena
   */
  const removeScene = useCallback(async (sceneId) => {
    if (!projectId) {
      handleError(new Error('Projeto não selecionado'), 'Remoção de cena');
      return;
    }

    if (scenes.length <= 1) {
      handleError(new Error('Não é possível remover a única cena'), 'Remoção de cena');
      return;
    }

    try {
      setIsRemovingScene(true);
      clearError();

      await sceneListService.deleteScene(projectId, sceneId);
      
      setScenes(prevScenes => prevScenes.filter(scene => scene.id !== sceneId));
      
      // Se a cena removida era a ativa, seleciona a primeira disponível
      if (activeSceneId === sceneId) {
        const remainingScenes = scenes.filter(scene => scene.id !== sceneId);
        if (remainingScenes.length > 0) {
          setActiveSceneId(remainingScenes[0].id);
        } else {
          setActiveSceneId(null);
        }
      }

      console.log('Cena removida:', sceneId);
    } catch (error) {
      handleError(error, 'Remoção de cena');
    } finally {
      setIsRemovingScene(false);
    }
  }, [projectId, scenes, activeSceneId, clearError, handleError]);

  /**
   * Duplica uma cena
   * @param {string} sceneId - ID da cena
   */
  const duplicateScene = useCallback(async (sceneId) => {
    if (!projectId) {
      handleError(new Error('Projeto não selecionado'), 'Duplicação de cena');
      return;
    }

    try {
      setIsDuplicatingScene(true);
      clearError();

      const duplicatedScene = await sceneListService.duplicateScene(projectId, sceneId);
      
      setScenes(prevScenes => [...prevScenes, duplicatedScene]);
      
      // Seleciona a cena duplicada
      setActiveSceneId(duplicatedScene.id);

      console.log('Cena duplicada:', duplicatedScene);
    } catch (error) {
      handleError(error, 'Duplicação de cena');
    } finally {
      setIsDuplicatingScene(false);
    }
  }, [projectId, clearError, handleError]);

  /**
   * Reordena cenas via drag-and-drop
   * @param {number} sourceIndex - Índice de origem
   * @param {number} destinationIndex - Índice de destino
   */
  const reorderScenes = useCallback(async (sourceIndex, destinationIndex) => {
    if (!projectId) {
      handleError(new Error('Projeto não selecionado'), 'Reordenação de cenas');
      return;
    }

    try {
      setIsReorderingScenes(true);
      clearError();

      // Cria nova ordem de cenas
      const sceneIds = scenes.map(scene => scene.id);
      const [movedScene] = sceneIds.splice(sourceIndex, 1);
      sceneIds.splice(destinationIndex, 0, movedScene);

      // Atualiza ordem no backend
      await sceneListService.reorderScenes(projectId, sceneIds);

      // Atualiza ordem local
      const reorderedScenes = [...scenes];
      const [movedSceneData] = reorderedScenes.splice(sourceIndex, 1);
      reorderedScenes.splice(destinationIndex, 0, movedSceneData);
      
      setScenes(reorderedScenes);

      console.log('Cenas reordenadas:', sourceIndex, '->', destinationIndex);
    } catch (error) {
      handleError(error, 'Reordenação de cenas');
    } finally {
      setIsReorderingScenes(false);
    }
  }, [projectId, scenes, clearError, handleError]);

  /**
   * Atualiza uma cena
   * @param {string} sceneId - ID da cena
   * @param {Object} updates - Dados para atualizar
   */
  const updateScene = useCallback(async (sceneId, updates) => {
    if (!projectId) {
      handleError(new Error('Projeto não selecionado'), 'Atualização de cena');
      return;
    }

    try {
      clearError();

      const updatedScene = await sceneListService.updateScene(projectId, sceneId, updates);
      
      setScenes(prevScenes => 
        prevScenes.map(scene => 
          scene.id === sceneId ? updatedScene : scene
        )
      );

      console.log('Cena atualizada:', sceneId, updates);
    } catch (error) {
      handleError(error, 'Atualização de cena');
    }
  }, [projectId, clearError, handleError]);

  /**
   * Obtém cena ativa
   */
  const getActiveScene = useCallback(() => {
    return scenes.find(scene => scene.id === activeSceneId) || null;
  }, [scenes, activeSceneId]);

  /**
   * Obtém índice da cena ativa
   */
  const getActiveSceneIndex = useCallback(() => {
    return scenes.findIndex(scene => scene.id === activeSceneId);
  }, [scenes, activeSceneId]);

  /**
   * Verifica se uma cena está ativa
   * @param {string} sceneId - ID da cena
   */
  const isSceneActive = useCallback((sceneId) => {
    return activeSceneId === sceneId;
  }, [activeSceneId]);

  /**
   * Obtém estatísticas das cenas
   */
  const getScenesStats = useCallback(() => {
    const totalDuration = scenes.reduce((total, scene) => total + (scene.duration || 0), 0);
    const totalAssets = scenes.reduce((total, scene) => total + (scene.assets?.length || 0), 0);
    
    return {
      totalScenes: scenes.length,
      totalDuration,
      totalAssets,
      averageDuration: scenes.length > 0 ? totalDuration / scenes.length : 0,
    };
  }, [scenes]);

  /**
   * Recarrega cenas (útil para sincronização)
   */
  const refreshScenes = useCallback(() => {
    loadScenes();
  }, [loadScenes]);

  // Carrega cenas quando projectId muda
  useEffect(() => {
    loadScenes();
  }, [loadScenes]);

  // Retorna estado e métodos
  return {
    // Estados
    scenes,
    activeSceneId,
    isLoading: isLoading || isAddingScene || isRemovingScene || isDuplicatingScene || isReorderingScenes,
    error,
    
    // Estados específicos
    isAddingScene,
    isRemovingScene,
    isDuplicatingScene,
    isReorderingScenes,
    
    // Métodos principais
    selectScene,
    addScene,
    removeScene,
    duplicateScene,
    reorderScenes,
    updateScene,
    
    // Métodos utilitários
    getActiveScene,
    getActiveSceneIndex,
    isSceneActive,
    getScenesStats,
    refreshScenes,
    clearError,
  };
};

export default useSceneList; 