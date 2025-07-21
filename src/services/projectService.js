/**
 * Serviço para gerenciamento de projetos
 */
const projectService = {
  /**
   * Busca todos os projetos do usuário
   * @param {Object} options - Opções de busca
   * @param {number} options.page - Página atual
   * @param {number} options.limit - Limite de itens por página
   * @param {string} options.sortBy - Campo para ordenação
   * @param {string} options.sortOrder - Ordem (asc, desc)
   * @returns {Promise<Object>} - Lista de projetos e metadados
   */
  async getProjects(options = {}) {
    try {
      const defaultOptions = {
        page: 1,
        limit: 10,
        sortBy: 'updatedAt',
        sortOrder: 'desc',
      };

      const mergedOptions = { ...defaultOptions, ...options };

      const response = await api.get('/api/projects', {
        params: {
          page: mergedOptions.page,
          limit: mergedOptions.limit,
          sort_by: mergedOptions.sortBy,
          sort_order: mergedOptions.sortOrder,
        },
      });

      return response.data;
    } catch (error) {
      console.error('Erro ao buscar projetos:', error);
      throw error;
    }
  },

  /**
   * Busca um projeto específico
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Object>} - Dados do projeto
   */
  async getProject(projectId) {
    try {
      const response = await api.get(`/api/projects/${projectId}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar projeto:', error);
      throw error;
    }
  },

  /**
   * Busca as cenas de um projeto
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Object>} - Lista de cenas
   */
  async getProjectScenes(projectId) {
    try {
      const response = await api.get(`/api/projects/${projectId}/scenes`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar cenas:', error);
      throw error;
    }
  },

  /**
   * Cria um novo projeto
   * @param {Object} projectData - Dados do projeto
   * @param {string} projectData.title - Título do projeto
   * @param {string} projectData.description - Descrição do projeto
   * @returns {Promise<Object>} - Projeto criado
   */
  async createProject(projectData) {
    try {
      const response = await api.post('/api/projects', projectData);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar projeto:', error);
      throw error;
    }
  },

  /**
   * Atualiza um projeto existente
   * @param {string} projectId - ID do projeto
   * @param {Object} projectData - Dados para atualização
   * @returns {Promise<Object>} - Projeto atualizado
   */
  async updateProject(projectId, projectData) {
    try {
      const response = await api.put(`/api/projects/${projectId}`, projectData);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar projeto:', error);
      throw error;
    }
  },

  /**
   * Atualiza as cenas de um projeto
   * @param {string} projectId - ID do projeto
   * @param {Array} scenes - Lista de cenas
   * @returns {Promise<Object>} - Cenas atualizadas
   */
  async updateProjectScenes(projectId, scenes) {
    try {
      const response = await api.put(`/api/projects/${projectId}/scenes`, {
        scenes,
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar cenas:', error);
      throw error;
    }
  },

  /**
   * Exclui um projeto
   * @param {string} projectId - ID do projeto
   * @returns {Promise<boolean>} - Sucesso da operação
   */
  async deleteProject(projectId) {
    try {
      await api.delete(`/api/projects/${projectId}`);
      return true;
    } catch (error) {
      console.error('Erro ao excluir projeto:', error);
      throw error;
    }
  },

  /**
   * Duplica um projeto existente
   * @param {string} projectId - ID do projeto a ser duplicado
   * @param {Object} options - Opções de duplicação
   * @param {string} options.title - Novo título para o projeto duplicado
   * @returns {Promise<Object>} - Novo projeto
   */
  async duplicateProject(projectId, options = {}) {
    try {
      const response = await api.post(
        `/api/projects/${projectId}/duplicate`,
        options
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao duplicar projeto:', error);
      throw error;
    }
  },
};

export default projectService;
