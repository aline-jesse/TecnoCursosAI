/**
 * Integração Frontend React com Backend FastAPI via Axios
 * TecnoCursos AI - Editor de Vídeo Inteligente
 * 
 * Este serviço implementa todas as integrações necessárias com o backend FastAPI:
 * - Buscar lista de projetos e cenas do usuário (GET)
 * - Fazer upload de arquivo PDF/PPTX (POST /upload)
 * - Salvar/editar cena (POST /scene)
 * - Baixar vídeo final gerado (GET /project/{id}/video)
 * 
 * @author TecnoCursos AI Team
 * @version 2.0.0
 */

import axios from 'axios';
import { config, logger } from '../config/environment';

/**
 * Configuração do cliente Axios para integração com FastAPI
 * 
 * BASE_URL: URL do backend FastAPI (padrão: http://localhost:8000)
 * TIMEOUT: Timeout das requisições em milissegundos
 * RETRY_ATTEMPTS: Número de tentativas em caso de falha
 */
const API_BASE_URL = config.API_BASE_URL || 'http://localhost:8000/api';
const TIMEOUT = 30000; // 30 segundos
const RETRY_ATTEMPTS = 3;

/**
 * Cliente Axios configurado para o backend FastAPI
 * 
 * Configurações:
 * - baseURL: URL base da API
 * - timeout: Timeout das requisições
 * - headers: Headers padrão incluindo Content-Type
 * - withCredentials: Habilita cookies para autenticação
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true, // Habilita cookies para autenticação
});

/**
 * Interceptador de Request - Adiciona token de autenticação
 * 
 * Funcionalidades:
 * - Adiciona token JWT do localStorage aos headers
 * - Log de requisições para debug
 * - Tratamento de erros de request
 */
apiClient.interceptors.request.use(
  (config) => {
    // Adiciona token de autenticação se disponível
    const token = localStorage.getItem('tecnocursos_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log da requisição para debug
    logger.debug('API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data,
      headers: config.headers,
    });

    return config;
  },
  (error) => {
    logger.error('Request Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Interceptador de Response - Tratamento global de erros
 * 
 * Funcionalidades:
 * - Log de respostas para debug
 * - Tratamento de erros 401 (não autorizado)
 * - Tratamento de erros 403 (proibido)
 * - Tratamento de erros 500 (erro interno)
 * - Redirecionamento para login em caso de token expirado
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log da resposta para debug
    logger.debug('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data,
    });

    return response;
  },
  (error) => {
    logger.error('Response Error:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.message,
      data: error.response?.data,
    });

    // Tratamento específico de erros
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      logger.warn('Token expirado, redirecionando para login');
      localStorage.removeItem('tecnocursos_token');
      localStorage.removeItem('tecnocursos_user');
      
      // Redireciona para página de login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403) {
      // Acesso negado
      logger.error('Acesso negado - usuário não tem permissão');
    } else if (error.response?.status === 500) {
      // Erro interno do servidor
      logger.error('Erro interno do servidor');
    }

    return Promise.reject(error);
  }
);

/**
 * Função utilitária para retry automático de requisições
 * 
 * @param {Function} apiCall - Função que faz a chamada da API
 * @param {number} maxRetries - Número máximo de tentativas
 * @param {number} delay - Delay entre tentativas em ms
 * @returns {Promise} Promise com o resultado da API
 */
const withRetry = async (apiCall, maxRetries = RETRY_ATTEMPTS, delay = 1000) => {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      
      // Se não é um erro de rede ou timeout, não tenta novamente
      if (!error.code && error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }

      logger.warn(`Tentativa ${attempt}/${maxRetries} falhou:`, error.message);

      if (attempt < maxRetries) {
        // Aguarda antes da próxima tentativa
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      }
    }
  }

  throw lastError;
};

/**
 * Serviço de Projetos - Gerencia projetos do usuário
 * 
 * Endpoints implementados:
 * - GET /projects - Lista todos os projetos do usuário
 * - GET /projects/{id} - Obtém projeto específico
 * - POST /projects - Cria novo projeto
 * - PUT /projects/{id} - Atualiza projeto
 * - DELETE /projects/{id} - Remove projeto
 */
export const projectService = {
  /**
   * Buscar lista de projetos do usuário
   * 
   * @param {Object} params - Parâmetros da consulta
   * @param {number} params.page - Página atual (padrão: 1)
   * @param {number} params.limit - Itens por página (padrão: 20)
   * @param {string} params.search - Termo de busca
   * @param {string} params.sort - Campo para ordenação
   * @param {string} params.order - Direção da ordenação (asc/desc)
   * @returns {Promise<Object>} Lista de projetos com metadados
   * 
   * @example
   * // Buscar todos os projetos
   * const projects = await projectService.getProjects();
   * 
   * // Buscar projetos com paginação
   * const projects = await projectService.getProjects({ 
   *   page: 2, 
   *   limit: 10,
   *   search: 'curso python',
   *   sort: 'created_at',
   *   order: 'desc'
   * });
   */
  async getProjects(params = {}) {
    const { page = 1, limit = 20, search, sort, order } = params;
    
    return withRetry(async () => {
      const response = await apiClient.get('/projects', {
        params: {
          page,
          limit,
          ...(search && { search }),
          ...(sort && { sort }),
          ...(order && { order }),
        },
      });
      
      return response.data;
    });
  },

  /**
   * Obter projeto específico por ID
   * 
   * @param {string|number} projectId - ID do projeto
   * @returns {Promise<Object>} Dados do projeto
   * 
   * @example
   * const project = await projectService.getProject(123);
   * console.log(project.name, project.description);
   */
  async getProject(projectId) {
    return withRetry(async () => {
      const response = await apiClient.get(`/projects/${projectId}`);
      return response.data;
    });
  },

  /**
   * Criar novo projeto
   * 
   * @param {Object} projectData - Dados do projeto
   * @param {string} projectData.name - Nome do projeto
   * @param {string} projectData.description - Descrição do projeto
   * @param {string} projectData.template - Template inicial (opcional)
   * @param {Object} projectData.settings - Configurações do projeto (opcional)
   * @returns {Promise<Object>} Projeto criado
   * 
   * @example
   * const newProject = await projectService.createProject({
   *   name: 'Curso de Python Avançado',
   *   description: 'Vídeo educativo sobre Python',
   *   template: 'educational',
   *   settings: {
   *     resolution: '1920x1080',
   *     fps: 30,
   *     quality: 'high'
   *   }
   * });
   */
  async createProject(projectData) {
    return withRetry(async () => {
      const response = await apiClient.post('/projects', projectData);
      return response.data;
    });
  },

  /**
   * Atualizar projeto existente
   * 
   * @param {string|number} projectId - ID do projeto
   * @param {Object} updates - Dados para atualização
   * @returns {Promise<Object>} Projeto atualizado
   * 
   * @example
   * const updatedProject = await projectService.updateProject(123, {
   *   name: 'Curso Python Atualizado',
   *   description: 'Nova descrição do curso'
   * });
   */
  async updateProject(projectId, updates) {
    return withRetry(async () => {
      const response = await apiClient.put(`/projects/${projectId}`, updates);
      return response.data;
    });
  },

  /**
   * Remover projeto
   * 
   * @param {string|number} projectId - ID do projeto
   * @returns {Promise<Object>} Confirmação da remoção
   * 
   * @example
   * await projectService.deleteProject(123);
   * console.log('Projeto removido com sucesso');
   */
  async deleteProject(projectId) {
    return withRetry(async () => {
      const response = await apiClient.delete(`/projects/${projectId}`);
      return response.data;
    });
  },
};

/**
 * Serviço de Cenas - Gerencia cenas dentro dos projetos
 * 
 * Endpoints implementados:
 * - GET /projects/{id}/scenes - Lista cenas do projeto
 * - GET /scenes/{id} - Obtém cena específica
 * - POST /scenes - Cria nova cena
 * - PUT /scenes/{id} - Atualiza cena
 * - DELETE /scenes/{id} - Remove cena
 */
export const sceneService = {
  /**
   * Buscar lista de cenas de um projeto
   * 
   * @param {string|number} projectId - ID do projeto
   * @param {Object} params - Parâmetros da consulta
   * @returns {Promise<Object>} Lista de cenas
   * 
   * @example
   * const scenes = await sceneService.getProjectScenes(123);
   * scenes.forEach(scene => console.log(scene.title));
   */
  async getProjectScenes(projectId, params = {}) {
    const { page = 1, limit = 50, sort = 'order' } = params;
    
    return withRetry(async () => {
      const response = await apiClient.get(`/projects/${projectId}/scenes`, {
        params: { page, limit, sort },
      });
      
      return response.data;
    });
  },

  /**
   * Obter cena específica por ID
   * 
   * @param {string|number} sceneId - ID da cena
   * @returns {Promise<Object>} Dados da cena
   * 
   * @example
   * const scene = await sceneService.getScene(456);
   * console.log(scene.title, scene.duration);
   */
  async getScene(sceneId) {
    return withRetry(async () => {
      const response = await apiClient.get(`/scenes/${sceneId}`);
      return response.data;
    });
  },

  /**
   * Criar nova cena
   * 
   * @param {Object} sceneData - Dados da cena
   * @param {string} sceneData.title - Título da cena
   * @param {string} sceneData.content - Conteúdo da cena (texto/narração)
   * @param {number} sceneData.duration - Duração em milissegundos
   * @param {string|number} sceneData.project_id - ID do projeto
   * @param {Object} sceneData.elements - Elementos visuais da cena
   * @param {Object} sceneData.audio - Configurações de áudio
   * @returns {Promise<Object>} Cena criada
   * 
   * @example
   * const newScene = await sceneService.createScene({
   *   title: 'Introdução ao Python',
   *   content: 'Python é uma linguagem de programação...',
   *   duration: 10000, // 10 segundos
   *   project_id: 123,
   *   elements: {
   *     background: 'classroom',
   *     character: 'teacher',
   *     text: {
   *       content: 'Python é uma linguagem...',
   *       position: { x: 100, y: 200 },
   *       style: { fontSize: 24, color: '#ffffff' }
   *     }
   *   },
   *   audio: {
   *     voice: 'pt-BR',
   *     speed: 1.0,
   *     volume: 0.8
   *   }
   * });
   */
  async createScene(sceneData) {
    return withRetry(async () => {
      const response = await apiClient.post('/scenes', sceneData);
      return response.data;
    });
  },

  /**
   * Salvar/editar cena existente
   * 
   * @param {string|number} sceneId - ID da cena
   * @param {Object} updates - Dados para atualização
   * @returns {Promise<Object>} Cena atualizada
   * 
   * @example
   * // Salvar alterações em uma cena
   * const updatedScene = await sceneService.updateScene(456, {
   *   title: 'Introdução Atualizada',
   *   content: 'Conteúdo atualizado da cena...',
   *   duration: 12000, // 12 segundos
   *   elements: {
   *     // Novos elementos visuais
   *     background: 'office',
   *     character: 'student',
   *     text: {
   *       content: 'Conteúdo atualizado...',
   *       position: { x: 150, y: 250 },
   *       style: { fontSize: 28, color: '#000000' }
   *     }
   *   }
   * });
   */
  async updateScene(sceneId, updates) {
    return withRetry(async () => {
      const response = await apiClient.put(`/scenes/${sceneId}`, updates);
      return response.data;
    });
  },

  /**
   * Remover cena
   * 
   * @param {string|number} sceneId - ID da cena
   * @returns {Promise<Object>} Confirmação da remoção
   * 
   * @example
   * await sceneService.deleteScene(456);
   * console.log('Cena removida com sucesso');
   */
  async deleteScene(sceneId) {
    return withRetry(async () => {
      const response = await apiClient.delete(`/scenes/${sceneId}`);
      return response.data;
    });
  },

  /**
   * Reordenar cenas de um projeto
   * 
   * @param {string|number} projectId - ID do projeto
   * @param {Array} sceneOrder - Array com IDs das cenas na nova ordem
   * @returns {Promise<Object>} Confirmação da reordenação
   * 
   * @example
   * await sceneService.reorderScenes(123, [456, 789, 101]);
   * console.log('Cenas reordenadas com sucesso');
   */
  async reorderScenes(projectId, sceneOrder) {
    return withRetry(async () => {
      const response = await apiClient.put(`/projects/${projectId}/scenes/reorder`, {
        scene_order: sceneOrder,
      });
      
      return response.data;
    });
  },
};

/**
 * Serviço de Upload - Gerencia upload de arquivos
 * 
 * Endpoints implementados:
 * - POST /upload - Upload de arquivo
 * - GET /upload/files - Lista arquivos enviados
 * - DELETE /upload/files/{id} - Remove arquivo
 * - GET /upload/stats - Estatísticas de upload
 */
export const uploadService = {
  /**
   * Fazer upload de arquivo PDF/PPTX
   * 
   * @param {File} file - Arquivo para upload
   * @param {string|number} projectId - ID do projeto (opcional)
   * @param {Function} onProgress - Callback para progresso (opcional)
   * @param {Object} options - Opções adicionais
   * @returns {Promise<Object>} Dados do arquivo enviado
   * 
   * @example
   * // Upload simples
   * const fileInput = document.getElementById('file-input');
   * const file = fileInput.files[0];
   * 
   * const uploadedFile = await uploadService.uploadFile(file, 123, (progress) => {
   *   console.log(`Upload: ${progress}%`);
   * });
   * 
   * console.log('Arquivo enviado:', uploadedFile.filename);
   * 
   * // Upload com opções
   * const uploadedFile = await uploadService.uploadFile(file, 123, null, {
   *   autoProcess: true,
   *   extractText: true,
   *   generateThumbnails: true
   * });
   */
  async uploadFile(file, projectId = null, onProgress = null, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    if (projectId) {
      formData.append('project_id', projectId);
    }
    
    // Adiciona opções ao formData
    Object.keys(options).forEach(key => {
      formData.append(key, options[key]);
    });

    return withRetry(async () => {
      const response = await apiClient.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(progress);
          }
        },
      });
      
      return response.data;
    });
  },

  /**
   * Upload em chunks para arquivos grandes
   * 
   * @param {File} file - Arquivo para upload
   * @param {string|number} projectId - ID do projeto (opcional)
   * @param {Function} onProgress - Callback para progresso
   * @param {Object} options - Opções de upload
   * @returns {Promise<Object>} Dados do arquivo enviado
   * 
   * @example
   * const uploadedFile = await uploadService.uploadLargeFile(
   *   largeFile, 
   *   123, 
   *   (progress) => console.log(`Progresso: ${progress}%`),
   *   { chunkSize: 1024 * 1024 } // 1MB por chunk
   * );
   */
  async uploadLargeFile(file, projectId = null, onProgress = null, options = {}) {
    const chunkSize = options.chunkSize || 1024 * 1024; // 1MB padrão
    const totalChunks = Math.ceil(file.size / chunkSize);
    const uploadId = `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    logger.info(`Iniciando upload em chunks: ${totalChunks} chunks de ${chunkSize} bytes`);

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

      try {
        await apiClient.post('/upload/chunk', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Calcula progresso
        const progress = Math.round(((i + 1) * 100) / totalChunks);
        if (onProgress) {
          onProgress(progress);
        }

        logger.debug(`Chunk ${i + 1}/${totalChunks} enviado (${progress}%)`);
      } catch (error) {
        logger.error(`Erro ao enviar chunk ${i + 1}:`, error);
        throw error;
      }
    }

    // Finaliza upload
    const finalizeResponse = await apiClient.post('/upload/finalize', {
      upload_id: uploadId,
      filename: file.name,
      project_id: projectId,
    });

    return finalizeResponse.data;
  },

  /**
   * Listar arquivos enviados
   * 
   * @param {string|number} projectId - ID do projeto (opcional)
   * @param {Object} params - Parâmetros da consulta
   * @returns {Promise<Object>} Lista de arquivos
   * 
   * @example
   * // Listar todos os arquivos
   * const files = await uploadService.getFiles();
   * 
   * // Listar arquivos de um projeto
   * const projectFiles = await uploadService.getFiles(123, {
   *   page: 1,
   *   limit: 20,
   *   type: 'pdf'
   * });
   */
  async getFiles(projectId = null, params = {}) {
    const { page = 1, limit = 20, type, sort = 'uploaded_at' } = params;
    
    return withRetry(async () => {
      const response = await apiClient.get('/upload/files', {
        params: {
          page,
          limit,
          ...(projectId && { project_id: projectId }),
          ...(type && { type }),
          sort,
        },
      });
      
      return response.data;
    });
  },

  /**
   * Remover arquivo enviado
   * 
   * @param {string|number} fileId - ID do arquivo
   * @returns {Promise<Object>} Confirmação da remoção
   * 
   * @example
   * await uploadService.deleteFile(789);
   * console.log('Arquivo removido com sucesso');
   */
  async deleteFile(fileId) {
    return withRetry(async () => {
      const response = await apiClient.delete(`/upload/files/${fileId}`);
      return response.data;
    });
  },

  /**
   * Obter estatísticas de upload
   * 
   * @param {string|number} projectId - ID do projeto (opcional)
   * @returns {Promise<Object>} Estatísticas de upload
   * 
   * @example
   * const stats = await uploadService.getUploadStats(123);
   * console.log(`Total de arquivos: ${stats.total_files}`);
   * console.log(`Espaço usado: ${stats.total_size_mb}MB`);
   */
  async getUploadStats(projectId = null) {
    return withRetry(async () => {
      const response = await apiClient.get('/upload/stats', {
        params: projectId ? { project_id: projectId } : {},
      });
      
      return response.data;
    });
  },
};

/**
 * Serviço de Vídeos - Gerencia geração e download de vídeos
 * 
 * Endpoints implementados:
 * - POST /projects/{id}/generate - Gerar vídeo do projeto
 * - GET /projects/{id}/video - Download do vídeo final
 * - GET /projects/{id}/video/status - Status da geração
 * - GET /videos - Lista vídeos gerados
 */
export const videoService = {
  /**
   * Gerar vídeo do projeto
   * 
   * @param {string|number} projectId - ID do projeto
   * @param {Object} options - Opções de geração
   * @returns {Promise<Object>} Dados da tarefa de geração
   * 
   * @example
   * // Gerar vídeo com configurações padrão
   * const generationTask = await videoService.generateVideo(123);
   * console.log('Tarefa iniciada:', generationTask.task_id);
   * 
   * // Gerar vídeo com opções personalizadas
   * const generationTask = await videoService.generateVideo(123, {
   *   resolution: '1920x1080',
   *   fps: 30,
   *   quality: 'high',
   *   format: 'mp4',
   *   includeAudio: true,
   *   audioQuality: 'high',
   *   watermark: false,
   *   subtitles: true,
   *   language: 'pt-BR'
   * });
   */
  async generateVideo(projectId, options = {}) {
    const defaultOptions = {
      resolution: '1920x1080',
      fps: 30,
      quality: 'high',
      format: 'mp4',
      includeAudio: true,
      audioQuality: 'high',
      watermark: false,
      subtitles: false,
      language: 'pt-BR',
    };

    const generationOptions = { ...defaultOptions, ...options };

    return withRetry(async () => {
      const response = await apiClient.post(`/projects/${projectId}/generate`, generationOptions);
      return response.data;
    });
  },

  /**
   * Verificar status da geração de vídeo
   * 
   * @param {string|number} projectId - ID do projeto
   * @param {string} taskId - ID da tarefa de geração
   * @returns {Promise<Object>} Status da geração
   * 
   * @example
   * const status = await videoService.getGenerationStatus(123, 'task_abc123');
   * console.log(`Status: ${status.status}, Progresso: ${status.progress}%`);
   * 
   * if (status.status === 'completed') {
   *   console.log('Vídeo gerado com sucesso!');
   * }
   */
  async getGenerationStatus(projectId, taskId) {
    return withRetry(async () => {
      const response = await apiClient.get(`/projects/${projectId}/video/status`, {
        params: { task_id: taskId },
      });
      
      return response.data;
    });
  },

  /**
   * Baixar vídeo final gerado
   * 
   * @param {string|number} projectId - ID do projeto
   * @param {Object} options - Opções de download
   * @returns {Promise<Blob>} Arquivo de vídeo
   * 
   * @example
   * // Download simples
   * const videoBlob = await videoService.downloadVideo(123);
   * 
   * // Criar URL para download
   * const videoUrl = URL.createObjectURL(videoBlob);
   * const link = document.createElement('a');
   * link.href = videoUrl;
   * link.download = 'meu_video.mp4';
   * link.click();
   * 
   * // Download com opções
   * const videoBlob = await videoService.downloadVideo(123, {
   *   quality: 'high',
   *   format: 'mp4',
   *   includeSubtitles: true
   * });
   */
  async downloadVideo(projectId, options = {}) {
    return withRetry(async () => {
      const response = await apiClient.get(`/projects/${projectId}/video`, {
        params: options,
        responseType: 'blob', // Importante para download de arquivo
      });
      
      return response.data;
    });
  },

  /**
   * Listar vídeos gerados
   * 
   * @param {Object} params - Parâmetros da consulta
   * @returns {Promise<Object>} Lista de vídeos
   * 
   * @example
   * // Listar todos os vídeos
   * const videos = await videoService.getVideos();
   * 
   * // Listar vídeos com filtros
   * const videos = await videoService.getVideos({
   *   page: 1,
   *   limit: 10,
   *   project_id: 123,
   *   status: 'completed'
   * });
   */
  async getVideos(params = {}) {
    const { page = 1, limit = 20, project_id, status, sort = 'created_at' } = params;
    
    return withRetry(async () => {
      const response = await apiClient.get('/videos', {
        params: {
          page,
          limit,
          ...(project_id && { project_id }),
          ...(status && { status }),
          sort,
        },
      });
      
      return response.data;
    });
  },

  /**
   * Obter informações do vídeo
   * 
   * @param {string|number} videoId - ID do vídeo
   * @returns {Promise<Object>} Informações do vídeo
   * 
   * @example
   * const videoInfo = await videoService.getVideoInfo(456);
   * console.log(`Duração: ${videoInfo.duration}s`);
   * console.log(`Tamanho: ${videoInfo.file_size_mb}MB`);
   * console.log(`Resolução: ${videoInfo.resolution}`);
   */
  async getVideoInfo(videoId) {
    return withRetry(async () => {
      const response = await apiClient.get(`/videos/${videoId}`);
      return response.data;
    });
  },
};

/**
 * Serviço de Health Check - Verifica status da API
 * 
 * Endpoints implementados:
 * - GET /health - Health check geral
 * - GET /api/health - Health check da API
 * - GET /api/status - Status detalhado do sistema
 */
export const healthService = {
  /**
   * Verificar saúde geral da API
   * 
   * @returns {Promise<Object>} Status de saúde da API
   * 
   * @example
   * const health = await healthService.checkHealth();
   * console.log(`API Status: ${health.status}`);
   * console.log(`Uptime: ${health.uptime}s`);
   */
  async checkHealth() {
    return withRetry(async () => {
      const response = await apiClient.get('/health');
      return response.data;
    });
  },

  /**
   * Verificar saúde específica da API
   * 
   * @returns {Promise<Object>} Status detalhado da API
   * 
   * @example
   * const apiHealth = await healthService.checkApiHealth();
   * console.log(`Database: ${apiHealth.database}`);
   * console.log(`Storage: ${apiHealth.storage}`);
   * console.log(`Background Tasks: ${apiHealth.background_tasks}`);
   */
  async checkApiHealth() {
    return withRetry(async () => {
      const response = await apiClient.get('/api/health');
      return response.data;
    });
  },

  /**
   * Obter status detalhado do sistema
   * 
   * @returns {Promise<Object>} Status completo do sistema
   * 
   * @example
   * const systemStatus = await healthService.getSystemStatus();
   * console.log(`CPU Usage: ${systemStatus.cpu_usage}%`);
   * console.log(`Memory Usage: ${systemStatus.memory_usage}%`);
   * console.log(`Disk Usage: ${systemStatus.disk_usage}%`);
   */
  async getSystemStatus() {
    return withRetry(async () => {
      const response = await apiClient.get('/api/status');
      return response.data;
    });
  },
};

/**
 * Configuração da URL do Backend
 * 
 * Para configurar a URL do backend, você pode:
 * 
 * 1. Usar variáveis de ambiente:
 *    - REACT_APP_API_BASE_URL=http://localhost:8000/api
 * 
 * 2. Modificar diretamente no arquivo de configuração:
 *    - src/config/environment.js
 * 
 * 3. Usar configuração dinâmica:
 *    - Configurar via localStorage ou sessionStorage
 * 
 * @example
 * // Configurar via variável de ambiente
 * // .env.local
 * REACT_APP_API_BASE_URL=http://localhost:8000/api
 * 
 * // Configurar via localStorage
 * localStorage.setItem('api_base_url', 'http://localhost:8000/api');
 * 
 * // Configurar via código
 * import { config } from '../config/environment';
 * config.API_BASE_URL = 'http://localhost:8000/api';
 */

/**
 * Exemplo de integração completa
 * 
 * Este exemplo demonstra como usar todos os serviços
 * para criar um fluxo completo de edição de vídeo.
 */
export const integrationExample = {
  /**
   * Exemplo: Criar projeto, adicionar cenas e gerar vídeo
   * 
   * @example
   * // 1. Criar novo projeto
   * const project = await projectService.createProject({
   *   name: 'Tutorial Python',
   *   description: 'Curso básico de Python',
   *   template: 'educational'
   * });
   * 
   * // 2. Fazer upload de arquivo PDF
   * const fileInput = document.getElementById('file-input');
   * const file = fileInput.files[0];
   * const uploadedFile = await uploadService.uploadFile(file, project.id);
   * 
   * // 3. Criar cenas baseadas no arquivo
   * const scene1 = await sceneService.createScene({
   *   title: 'Introdução',
   *   content: 'Bem-vindo ao curso de Python!',
   *   duration: 5000,
   *   project_id: project.id,
   *   elements: {
   *     background: 'classroom',
   *     character: 'teacher',
   *     text: {
   *       content: 'Bem-vindo ao curso de Python!',
   *       position: { x: 100, y: 200 },
   *       style: { fontSize: 24, color: '#ffffff' }
   *     }
   *   }
   * });
   * 
   * // 4. Salvar alterações na cena
   * await sceneService.updateScene(scene1.id, {
   *   title: 'Introdução Atualizada',
   *   content: 'Bem-vindo ao curso completo de Python!',
   *   elements: {
   *     text: {
   *       content: 'Bem-vindo ao curso completo de Python!',
   *       style: { fontSize: 28, color: '#000000' }
   *     }
   *   }
   * });
   * 
   * // 5. Gerar vídeo final
   * const generationTask = await videoService.generateVideo(project.id, {
   *   resolution: '1920x1080',
   *   quality: 'high',
   *   includeAudio: true
   * });
   * 
   * // 6. Monitorar progresso da geração
   * const checkProgress = async () => {
   *   const status = await videoService.getGenerationStatus(project.id, generationTask.task_id);
   *   
   *   if (status.status === 'completed') {
   *     // 7. Download do vídeo final
   *     const videoBlob = await videoService.downloadVideo(project.id);
   *     const videoUrl = URL.createObjectURL(videoBlob);
   *     
   *     // Criar link de download
   *     const link = document.createElement('a');
   *     link.href = videoUrl;
   *     link.download = `${project.name}.mp4`;
   *     link.click();
   *   } else if (status.status === 'failed') {
   *     console.error('Erro na geração do vídeo:', status.error);
   *   } else {
   *     console.log(`Progresso: ${status.progress}%`);
   *     setTimeout(checkProgress, 2000); // Verificar novamente em 2 segundos
   *   }
   * };
   * 
   * checkProgress();
   */
  async createCompleteVideoWorkflow() {
    try {
      // 1. Criar projeto
      const project = await projectService.createProject({
        name: 'Exemplo de Integração',
        description: 'Vídeo criado via integração API',
        template: 'educational'
      });

      // 2. Criar cena
      const scene = await sceneService.createScene({
        title: 'Cena de Exemplo',
        content: 'Esta é uma cena criada via API',
        duration: 5000,
        project_id: project.id,
        elements: {
          background: 'classroom',
          character: 'teacher',
          text: {
            content: 'Esta é uma cena criada via API',
            position: { x: 100, y: 200 },
            style: { fontSize: 24, color: '#ffffff' }
          }
        }
      });

      // 3. Atualizar cena
      await sceneService.updateScene(scene.id, {
        title: 'Cena Atualizada',
        content: 'Esta é uma cena atualizada via API',
        elements: {
          text: {
            content: 'Esta é uma cena atualizada via API',
            style: { fontSize: 28, color: '#000000' }
          }
        }
      });

      // 4. Gerar vídeo
      const generationTask = await videoService.generateVideo(project.id);

      return {
        project,
        scene,
        generationTask,
        message: 'Fluxo completo executado com sucesso!'
      };

    } catch (error) {
      logger.error('Erro no fluxo de exemplo:', error);
      throw error;
    }
  }
};

/**
 * Exporta todos os serviços para uso no frontend
 */
export default {
  projectService,
  sceneService,
  uploadService,
  videoService,
  healthService,
  integrationExample,
  
  // Configurações
  API_BASE_URL,
  apiClient,
  
  // Utilitários
  withRetry,
}; 