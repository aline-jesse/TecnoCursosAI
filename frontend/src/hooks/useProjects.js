/**
 * Hook personalizado para gerenciar operações de projetos
 * @returns {Object} Métodos e estados relacionados a projetos
 */

import { useState, useCallback } from 'react';

/**
 * Hook personalizado para gerenciar operações de projetos
 * @returns {Object} Métodos e estados relacionados a projetos
 */
export const useProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Busca a lista de projetos do usuário
   * @returns {Promise<void>}
   */
  const fetchProjects = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Simular busca de projetos
      const mockProjects = [
        {
          id: 1,
          name: 'Projeto Demo 1',
          description: 'Projeto de demonstração',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          name: 'Projeto Demo 2',
          description: 'Outro projeto de demonstração',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      setProjects(mockProjects);
    } catch (err) {
      setError(err);
      console.error('Erro ao buscar projetos:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Criar novo projeto
   */
  const createProject = useCallback(async projectData => {
    setLoading(true);
    setError(null);

    try {
      const newProject = {
        id: Date.now(),
        name: projectData.name || 'Novo Projeto',
        description: projectData.description || '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setProjects(prev => [...prev, newProject]);
      return newProject;
    } catch (err) {
      setError(err);
      console.error('Erro ao criar projeto:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Atualizar projeto
   */
  const updateProject = useCallback(async (projectId, updates) => {
    setLoading(true);
    setError(null);

    try {
      setProjects(prev =>
        prev.map(project =>
          project.id === projectId
            ? { ...project, ...updates, updated_at: new Date().toISOString() }
            : project
        )
      );
    } catch (err) {
      setError(err);
      console.error('Erro ao atualizar projeto:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Deletar projeto
   */
  const deleteProject = useCallback(async projectId => {
    setLoading(true);
    setError(null);

    try {
      setProjects(prev => prev.filter(project => project.id !== projectId));
    } catch (err) {
      setError(err);
      console.error('Erro ao deletar projeto:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
  };
};
