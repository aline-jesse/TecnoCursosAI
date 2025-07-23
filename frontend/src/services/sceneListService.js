/**
 * SceneListService - Serviço para integração com backend FastAPI
 * Gerencia operações CRUD de cenas, projetos e assets
 */

class SceneListService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.token = localStorage.getItem('auth_token') || null;
  }

  /**
   * Atualiza o token de autenticação
   * @param {string} token - Token JWT
   */
  setAuthToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  /**
   * Obtém headers para requisições autenticadas
   * @returns {Object} Headers com autorização
   */
  getAuthHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Faz requisição HTTP com tratamento de erro
   * @param {string} url - URL da requisição
   * @param {Object} options - Opções da requisição
   * @returns {Promise} Resposta da requisição
   */
  async makeRequest(url, options = {}) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getAuthHeaders(),
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error('Erro na requisição:', error);
      throw error;
    }
  }

  // ===== PROJETOS =====

  /**
   * Lista todos os projetos do usuário
   * @returns {Promise<Array>} Lista de projetos
   */
  async getProjects() {
    return this.makeRequest(`${this.baseURL}/api/v1/projects/`);
  }

  /**
   * Obtém um projeto específico
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Object>} Dados do projeto
   */
  async getProject(projectId) {
    return this.makeRequest(`${this.baseURL}/api/v1/projects/${projectId}/`);
  }

  /**
   * Cria um novo projeto
   * @param {Object} projectData - Dados do projeto
   * @returns {Promise<Object>} Projeto criado
   */
  async createProject(projectData) {
    return this.makeRequest(`${this.baseURL}/api/v1/projects/`, {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  /**
   * Atualiza um projeto
   * @param {string} projectId - ID do projeto
   * @param {Object} projectData - Dados atualizados
   * @returns {Promise<Object>} Projeto atualizado
   */
  async updateProject(projectId, projectData) {
    return this.makeRequest(`${this.baseURL}/api/v1/projects/${projectId}/`, {
      method: 'PUT',
      body: JSON.stringify(projectData),
    });
  }

  /**
   * Remove um projeto
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Object>} Confirmação da remoção
   */
  async deleteProject(projectId) {
    return this.makeRequest(`${this.baseURL}/api/v1/projects/${projectId}/`, {
      method: 'DELETE',
    });
  }

  // ===== CENAS =====

  /**
   * Lista cenas de um projeto
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Array>} Lista de cenas
   */
  async getScenes(projectId) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/`
    );
  }

  /**
   * Obtém uma cena específica
   * @param {string} projectId - ID do projeto
   * @param {string} sceneId - ID da cena
   * @returns {Promise<Object>} Dados da cena
   */
  async getScene(projectId, sceneId) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/${sceneId}/`
    );
  }

  /**
   * Cria uma nova cena
   * @param {string} projectId - ID do projeto
   * @param {Object} sceneData - Dados da cena
   * @returns {Promise<Object>} Cena criada
   */
  async createScene(projectId, sceneData) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/`,
      {
        method: 'POST',
        body: JSON.stringify(sceneData),
      }
    );
  }

  /**
   * Atualiza uma cena
   * @param {string} projectId - ID do projeto
   * @param {string} sceneId - ID da cena
   * @param {Object} sceneData - Dados atualizados
   * @returns {Promise<Object>} Cena atualizada
   */
  async updateScene(projectId, sceneId, sceneData) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/${sceneId}/`,
      {
        method: 'PUT',
        body: JSON.stringify(sceneData),
      }
    );
  }

  /**
   * Remove uma cena
   * @param {string} projectId - ID do projeto
   * @param {string} sceneId - ID da cena
   * @returns {Promise<Object>} Confirmação da remoção
   */
  async deleteScene(projectId, sceneId) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/${sceneId}/`,
      {
        method: 'DELETE',
      }
    );
  }

  /**
   * Duplica uma cena
   * @param {string} projectId - ID do projeto
   * @param {string} sceneId - ID da cena
   * @returns {Promise<Object>} Cena duplicada
   */
  async duplicateScene(projectId, sceneId) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/${sceneId}/duplicate/`,
      {
        method: 'POST',
      }
    );
  }

  /**
   * Reordena cenas de um projeto
   * @param {string} projectId - ID do projeto
   * @param {Array} sceneIds - Array com IDs das cenas na nova ordem
   * @returns {Promise<Object>} Confirmação da reordenação
   */
  async reorderScenes(projectId, sceneIds) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/reorder/`,
      {
        method: 'POST',
        body: JSON.stringify({ scene_ids: sceneIds }),
      }
    );
  }

  // ===== ASSETS =====

  /**
   * Lista assets de uma cena
   * @param {string} projectId - ID do projeto
   * @param {string} sceneId - ID da cena
   * @returns {Promise<Array>} Lista de assets
   */
  async getSceneAssets(projectId, sceneId) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/${sceneId}/assets/`
    );
  }

  /**
   * Adiciona asset a uma cena
   * @param {string} projectId - ID do projeto
   * @param {string} sceneId - ID da cena
   * @param {FormData} formData - Dados do asset
   * @returns {Promise<Object>} Asset criado
   */
  async addSceneAsset(projectId, sceneId, formData) {
    const headers = { ...this.getAuthHeaders() };
    delete headers['Content-Type']; // Remove para FormData

    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/${sceneId}/assets/`,
      {
        method: 'POST',
        headers,
        body: formData,
      }
    );
  }

  /**
   * Remove asset de uma cena
   * @param {string} projectId - ID do projeto
   * @param {string} sceneId - ID da cena
   * @param {string} assetId - ID do asset
   * @returns {Promise<Object>} Confirmação da remoção
   */
  async removeSceneAsset(projectId, sceneId, assetId) {
    return this.makeRequest(
      `${this.baseURL}/api/v1/projects/${projectId}/scenes/${sceneId}/assets/${assetId}/`,
      {
        method: 'DELETE',
      }
    );
  }

  // ===== UTILITÁRIOS =====

  /**
   * Formata duração em segundos para MM:SS
   * @param {number} duration - Duração em segundos
   * @returns {string} Duração formatada
   */
  formatDuration(duration) {
    if (!duration || duration <= 0) return '00:00';
    const minutes = Math.floor(duration / 60);
    const seconds = Math.floor(duration % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }

  /**
   * Gera thumbnail para uma cena
   * @param {Object} scene - Objeto da cena
   * @returns {string|null} URL do thumbnail ou null
   */
  getSceneThumbnail(scene) {
    // Se há assets com thumbnails, usa o primeiro
    if (scene.assets && scene.assets.length > 0) {
      const assetWithThumbnail = scene.assets.find(
        asset => asset.thumbnail_url
      );
      if (assetWithThumbnail) {
        return assetWithThumbnail.thumbnail_url;
      }
    }

    // Se há texto na cena, cria thumbnail baseado no texto
    if (scene.text && scene.text.length > 0) {
      const text = scene.text.substring(0, 50);
      return `data:image/svg+xml;base64,${btoa(`
        <svg width="120" height="80" xmlns="http://www.w3.org/2000/svg">
          <rect width="120" height="80" fill="#f3f4f6"/>
          <text x="60" y="45" font-family="Arial" font-size="10" text-anchor="middle" fill="#6b7280">
            ${text}${scene.text.length > 50 ? '...' : ''}
          </text>
        </svg>
      `)}`;
    }

    return null;
  }

  /**
   * Valida dados de uma cena
   * @param {Object} sceneData - Dados da cena
   * @returns {Object} Resultado da validação
   */
  validateSceneData(sceneData) {
    const errors = [];

    if (!sceneData.title && !sceneData.nome) {
      errors.push('Título é obrigatório');
    }

    if (
      sceneData.duration &&
      (sceneData.duration < 0 || sceneData.duration > 3600)
    ) {
      errors.push('Duração deve estar entre 0 e 3600 segundos');
    }

    if (sceneData.order && sceneData.order < 0) {
      errors.push('Ordem deve ser maior ou igual a 0');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Cria dados padrão para nova cena
   * @param {number} order - Ordem da cena
   * @returns {Object} Dados padrão da cena
   */
  createDefaultSceneData(order = 1) {
    return {
      title: `Cena ${order}`,
      duration: 5,
      order,
      text: '',
      type: 'content',
      assets: [],
    };
  }

  // ===== AUTENTICAÇÃO =====

  /**
   * Faz login do usuário
   * @param {string} username - Nome de usuário
   * @param {string} password - Senha
   * @returns {Promise<Object>} Dados do token
   */
  async login(username, password) {
    const response = await this.makeRequest(
      `${this.baseURL}/api/v1/auth/login/`,
      {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      }
    );

    if (response.access_token) {
      this.setAuthToken(response.access_token);
    }

    return response;
  }

  /**
   * Faz logout do usuário
   */
  logout() {
    this.setAuthToken(null);
  }

  /**
   * Verifica se o usuário está autenticado
   * @returns {boolean} True se autenticado
   */
  isAuthenticated() {
    return !!this.token;
  }

  /**
   * Obtém dados do usuário atual
   * @returns {Promise<Object>} Dados do usuário
   */
  async getCurrentUser() {
    return this.makeRequest(`${this.baseURL}/api/v1/auth/me/`);
  }

  // ===== HEALTH CHECK =====

  /**
   * Verifica se o backend está acessível
   * @returns {Promise<boolean>} True se acessível
   */
  async healthCheck() {
    try {
      await this.makeRequest(`${this.baseURL}/health/`);
      return true;
    } catch (error) {
      console.error('Backend não acessível:', error);
      return false;
    }
  }
}

// Exporta instância singleton
const sceneListService = new SceneListService();
export default sceneListService;
