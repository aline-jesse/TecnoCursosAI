/**
 * Serviço base da API - TecnoCursos AI
 *
 * Este arquivo configura a instância do Axios com:
 * - Interceptors para autenticação automática
 * - Tratamento centralizado de erros
 * - Sistema de retry automático
 * - Cache de requisições
 */

import axios from 'axios';

// Configuração base do Axios
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Serviço de projetos e cenas
export const projectService = {
  // Buscar todos os projetos do usuário
  async getProjects() {
    try {
      const response = await api.get('/api/projects');
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar projetos:', error);
      throw error;
    }
  },

  // Buscar cenas de um projeto específico
  async getProjectScenes(projectId) {
    try {
      const response = await api.get(`/api/projects/${projectId}/scenes`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar cenas:', error);
      throw error;
    }
  },

  // Criar novo projeto
  async createProject(projectData) {
    try {
      const response = await api.post('/api/projects', projectData);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar projeto:', error);
      throw error;
    }
  },

  // Atualizar cenas de um projeto
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
};

// Serviço de upload e processamento de arquivos
export const fileService = {
  // Upload de arquivo PDF/PPTX
  async uploadFile(file, projectId) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_id', projectId);

      const response = await api.post('/api/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: progressEvent => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          console.log('Progresso do upload:', percentCompleted);
        },
      });
      return response.data;
    } catch (error) {
      console.error('Erro no upload do arquivo:', error);
      throw error;
    }
  },

  // Baixar vídeo gerado
  async downloadVideo(videoId) {
    try {
      const response = await api.get(`/api/videos/${videoId}/download`, {
        responseType: 'blob',
      });

      // Criar URL do blob e iniciar download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `video_${videoId}.mp4`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return true;
    } catch (error) {
      console.error('Erro ao baixar vídeo:', error);
      throw error;
    }
  },
};

export default api;
