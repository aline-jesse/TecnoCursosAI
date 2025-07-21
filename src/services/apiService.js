/**
 * Serviço de API - TecnoCursos AI Editor
 * Integração completa com backend FastAPI
 */

import axios from 'axios';
import { config, logger } from '../config/environment';

// Configuração do cliente axios
const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptador de request para adicionar token de autenticação
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('tecnocursos_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    logger.debug('API Request:', {
      method: config.method,
      url: config.url,
      data: config.data,
    });

    return config;
  },
  error => {
    logger.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Interceptador de response para tratar erros globalmente
api.interceptors.response.use(
  response => {
    logger.debug('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data,
    });
    return response;
  },
  error => {
    logger.error('Response error:', error);

    if (error.response?.status === 401) {
      // Token expirado, redirecionar para login
      localStorage.removeItem('tecnocursos_token');
      localStorage.removeItem('tecnocursos_user');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

/**
 * Serviços de Autenticação
 */
export const authService = {
  // Login do usuário
  async login(credentials) {
    const response = await api.post('/auth/login', credentials);

    if (response.data.access_token) {
      localStorage.setItem('tecnocursos_token', response.data.access_token);
      localStorage.setItem(
        'tecnocursos_user',
        JSON.stringify(response.data.user)
      );
    }

    return response.data;
  },

  // Registro de novo usuário
  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // Logout
  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      logger.warn('Logout error:', error);
    } finally {
      localStorage.removeItem('tecnocursos_token');
      localStorage.removeItem('tecnocursos_user');
    }
  },

  // Obter perfil do usuário
  async getProfile() {
    const response = await api.get('/users/me');
    return response.data;
  },

  // Verificar se usuário está autenticado
  isAuthenticated() {
    return !!localStorage.getItem('tecnocursos_token');
  },

  // Obter usuário atual do localStorage
  getCurrentUser() {
    const user = localStorage.getItem('tecnocursos_user');
    return user ? JSON.parse(user) : null;
  },
};

/**
 * Serviços de Projetos
 */
export const projectService = {
  // Listar projetos do usuário
  async getProjects(page = 1, limit = 20) {
    const response = await api.get('/projects', {
      params: { page, limit },
    });
    return response.data;
  },

  // Obter projeto específico
  async getProject(projectId) {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  // Criar novo projeto
  async createProject(projectData) {
    const response = await api.post('/projects', projectData);
    return response.data;
  },

  // Atualizar projeto
  async updateProject(projectId, updates) {
    const response = await api.put(`/projects/${projectId}`, updates);
    return response.data;
  },

  // Deletar projeto
  async deleteProject(projectId) {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },
};

/**
 * Serviços de Upload e Arquivos
 */
export const fileService = {
  // Upload de arquivo
  async uploadFile(file, projectId = null, onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (projectId) {
      formData.append('project_id', projectId);
    }

    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: progressEvent => {
        if (onProgress) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  // Upload em chunks para arquivos grandes
  async uploadFileChunks(file, projectId = null, onProgress = null) {
    const chunkSize = config.CHUNK_SIZE;
    const totalChunks = Math.ceil(file.size / chunkSize);
    const uploadId = `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, file.size);
      const chunk = file.slice(start, end);

      const formData = new FormData();
      formData.append('chunk', chunk);
      formData.append('chunk_number', i);
      formData.append('total_chunks', totalChunks);
      formData.append('upload_id', uploadId);
      formData.append('filename', file.name);
      if (projectId) {
        formData.append('project_id', projectId);
      }

      await api.post('/files/upload-chunk', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (onProgress) {
        const progress = Math.round(((i + 1) / totalChunks) * 100);
        onProgress(progress);
      }
    }

    // Finalizar upload
    const response = await api.post('/files/finalize-upload', {
      upload_id: uploadId,
      project_id: projectId,
    });

    return response.data;
  },

  // Listar arquivos
  async getFiles(projectId = null, page = 1, limit = 20) {
    const params = { page, limit };
    if (projectId) {
      params.project_id = projectId;
    }

    const response = await api.get('/files', { params });
    return response.data;
  },

  // Obter arquivo específico
  async getFile(fileId) {
    const response = await api.get(`/files/${fileId}`);
    return response.data;
  },

  // Deletar arquivo
  async deleteFile(fileId) {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  },

  // Gerar narração de texto
  async generateNarration(text, voice = 'pt-BR', projectId = null) {
    const response = await api.post('/tts/generate', {
      text,
      voice,
      project_id: projectId,
    });
    return response.data;
  },
};

/**
 * Serviços de Vídeo
 */
export const videoService = {
  // Gerar vídeo a partir de projeto
  async generateVideo(projectId, options = {}) {
    const response = await api.post('/video/generate', {
      project_id: projectId,
      ...options,
    });
    return response.data;
  },

  // Obter status de geração de vídeo
  async getGenerationStatus(taskId) {
    const response = await api.get(`/video/status/${taskId}`);
    return response.data;
  },

  // Listar vídeos gerados
  async getVideos(projectId = null, page = 1, limit = 20) {
    const params = { page, limit };
    if (projectId) {
      params.project_id = projectId;
    }

    const response = await api.get('/video/list', { params });
    return response.data;
  },

  // Download de vídeo
  async downloadVideo(videoId) {
    const response = await api.get(`/video/download/${videoId}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

/**
 * Serviços de Templates e Assets
 */
export const assetService = {
  // Listar templates
  async getTemplates(category = null, page = 1, limit = 20) {
    const params = { page, limit };
    if (category) {
      params.category = category;
    }

    const response = await api.get('/templates', { params });
    return response.data;
  },

  // Obter template específico
  async getTemplate(templateId) {
    const response = await api.get(`/templates/${templateId}`);
    return response.data;
  },

  // Listar personagens/avatares
  async getCharacters(page = 1, limit = 20) {
    const response = await api.get('/assets/characters', {
      params: { page, limit },
    });
    return response.data;
  },

  // Listar backgrounds
  async getBackgrounds(page = 1, limit = 20) {
    const response = await api.get('/assets/backgrounds', {
      params: { page, limit },
    });
    return response.data;
  },

  // Listar elementos gráficos
  async getElements(category = null, page = 1, limit = 20) {
    const params = { page, limit };
    if (category) {
      params.category = category;
    }

    const response = await api.get('/assets/elements', { params });
    return response.data;
  },
};

/**
 * Serviços de Análise e Métricas
 */
export const analyticsService = {
  // Obter estatísticas do dashboard
  async getDashboardStats() {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },

  // Registrar evento de uso
  async trackEvent(eventName, eventData = {}) {
    try {
      await api.post('/analytics/track', {
        event: eventName,
        data: eventData,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.warn('Analytics tracking failed:', error);
    }
  },
};

/**
 * Serviços de Sistema
 */
export const systemService = {
  // Health check da API
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  // Obter informações do sistema
  async getSystemInfo() {
    const response = await api.get('/system/info');
    return response.data;
  },
};

/**
 * Utilitários para manipulação de erros
 */
export const handleApiError = error => {
  if (error.response) {
    // Erro de resposta do servidor
    const { status, data } = error.response;

    switch (status) {
      case 400:
        return {
          message: data.detail || 'Dados inválidos',
          type: 'validation',
        };
      case 401:
        return { message: 'Não autorizado', type: 'auth' };
      case 403:
        return { message: 'Acesso negado', type: 'permission' };
      case 404:
        return { message: 'Recurso não encontrado', type: 'notfound' };
      case 429:
        return {
          message: 'Muitas tentativas. Tente novamente em alguns minutos.',
          type: 'ratelimit',
        };
      case 500:
        return { message: 'Erro interno do servidor', type: 'server' };
      default:
        return { message: data.detail || 'Erro desconhecido', type: 'unknown' };
    }
  } else if (error.request) {
    // Erro de rede
    return { message: 'Erro de conexão com o servidor', type: 'network' };
  } else {
    // Erro de configuração
    return { message: 'Erro na configuração da requisição', type: 'config' };
  }
};

/**
 * Hook para retry automático
 */
export const withRetry = async (apiCall, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      if (i === maxRetries - 1) throw error;

      logger.warn(
        `API call failed, retrying in ${delay}ms... (${i + 1}/${maxRetries})`
      );
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2; // Exponential backoff
    }
  }
};

// Exportar cliente axios para uso direto se necessário
export { api };

// Exportar tudo como default
export default {
  auth: authService,
  projects: projectService,
  files: fileService,
  videos: videoService,
  assets: assetService,
  analytics: analyticsService,
  system: systemService,
  handleApiError,
  withRetry,
  api,
};
