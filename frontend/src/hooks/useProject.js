import { useState, useEffect, useCallback } from 'react';
import { projectService } from '../services/api';

/**
 * Hook personalizado para gerenciar projetos
 * @param {Object} options - Opções de configuração
 * @param {string} options.initialProjectId - ID do projeto inicial (opcional)
 * @param {boolean} options.loadOnMount - Carregar projeto ao montar o componente
 * @returns {Object} - Métodos e estados do projeto
 */
const useProject = (options = {}) => {
  const [project, setProject] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Carrega um projeto específico
   * @param {string} projectId - ID do projeto
   */
  const loadProject = useCallback(async projectId => {
    if (!projectId) return;

    try {
      setLoading(true);
      setError(null);

      // Carregar dados do projeto
      const projectData = await projectService.getProject(projectId);
      setProject(projectData);

      // Carregar cenas do projeto
      const scenesData = await projectService.getProjectScenes(projectId);
      setScenes(scenesData.scenes || []);

      return { project: projectData, scenes: scenesData.scenes || [] };
    } catch (error) {
      console.error('Erro ao carregar projeto:', error);
      setError('Não foi possível carregar o projeto');
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Atualiza as cenas de um projeto
   * @param {string} projectId - ID do projeto
   * @param {Array} updatedScenes - Novas cenas
   */
  const updateScenes = useCallback(async (projectId, updatedScenes) => {
    if (!projectId) return;

    try {
      setLoading(true);
      setError(null);

      // Atualizar cenas no backend
      await projectService.updateProjectScenes(projectId, updatedScenes);

      // Atualizar estado local
      setScenes(updatedScenes);

      return updatedScenes;
    } catch (error) {
      console.error('Erro ao atualizar cenas:', error);
      setError('Não foi possível atualizar as cenas');
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Cria um novo projeto
   * @param {Object} projectData - Dados do projeto
   */
  const createProject = useCallback(async projectData => {
    try {
      setLoading(true);
      setError(null);

      // Criar projeto no backend
      const newProject = await projectService.createProject(projectData);

      // Atualizar estado local
      setProject(newProject);
      setScenes([]);

      return newProject;
    } catch (error) {
      console.error('Erro ao criar projeto:', error);
      setError('Não foi possível criar o projeto');
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  // Carregar projeto inicial se especificado
  useEffect(() => {
    if (options.loadOnMount && options.initialProjectId) {
      loadProject(options.initialProjectId);
    }
  }, [options.loadOnMount, options.initialProjectId, loadProject]);

  return {
    project,
    scenes,
    loading,
    error,
    loadProject,
    updateScenes,
    createProject,
    setScenes,
  };
};

export default useProject;
