/**
 * Configuração da API - TecnoCursos AI
 *
 * Este arquivo centraliza toda a configuração de endpoints e comportamentos
 * padrão para comunicação com o backend FastAPI.
 *
 * Para configurar o endpoint do backend:
 * 1. Em desenvolvimento: defina REACT_APP_API_URL no arquivo .env.local
 * 2. Em produção: configure a variável de ambiente no servidor
 *
 * Exemplo .env.local:
 * REACT_APP_API_URL=http://localhost:8000
 */

// Configuração de endpoint do backend
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

export const config = {
  // URL base para todas as requisições
  BASE_URL: API_BASE_URL,

  // Endpoints específicos
  ENDPOINTS: {
    PROJECTS: '/projects',
    SCENES: '/scenes',
    UPLOAD: '/upload',
    VIDEO_GENERATION: '/generate-video',
    DOWNLOAD_VIDEO: '/download-video',
  },

  // Configurações padrão do Axios
  AXIOS_CONFIG: {
    timeout: 30000, // 30 segundos
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  },
};

export default config;

// Endpoints da API organizados por módulo
export const API_ENDPOINTS = {
  // Autenticação
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    refresh: '/api/auth/refresh',
    logout: '/api/auth/logout',
    me: '/api/auth/me',
  },

  // Usuários
  users: {
    profile: '/api/users/me',
    update: '/api/users/me',
    stats: '/api/users/me/stats',
  },

  // Projetos
  projects: {
    list: '/api/projects',
    create: '/api/projects',
    get: id => `/api/projects/${id}`,
    update: id => `/api/projects/${id}`,
    delete: id => `/api/projects/${id}`,
    scenes: id => `/api/projects/${id}/scenes`,
  },

  // Upload de arquivos
  files: {
    upload: '/api/files/upload',
    uploadChunk: '/api/files/upload/chunk',
    list: '/api/files',
    get: id => `/api/files/${id}`,
    download: id => `/api/files/${id}/download`,
    delete: id => `/api/files/${id}`,
    search: '/api/files/search',
  },

  // Vídeos
  videos: {
    generate: '/api/videos/generate',
    list: '/api/videos',
    get: id => `/api/videos/${id}`,
    download: id => `/api/videos/${id}/download`,
    status: id => `/api/videos/${id}/status`,
    preview: id => `/api/videos/${id}/preview`,
  },

  // Cenas/Slides
  scenes: {
    create: '/api/scenes',
    update: id => `/api/scenes/${id}`,
    delete: id => `/api/scenes/${id}`,
    reorder: '/api/scenes/reorder',
    bulkUpdate: '/api/scenes/bulk-update',
  },

  // Text-to-Speech
  tts: {
    generate: '/api/tts/generate',
    voices: '/api/tts/voices',
    preview: '/api/tts/preview',
  },

  // WebSocket para atualizações em tempo real
  websocket: {
    url: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  },
};

// Configurações de retry
export const RETRY_CONFIG = {
  // Número máximo de tentativas
  maxRetries: 3,

  // Delay inicial entre tentativas (ms)
  initialDelay: 1000,

  // Fator de multiplicação do delay
  backoffFactor: 2,

  // Códigos HTTP que devem ser retentados
  retryableStatuses: [408, 429, 500, 502, 503, 504],
};

// Configurações de cache
export const CACHE_CONFIG = {
  // Tempo de cache padrão (5 minutos)
  defaultTTL: 5 * 60 * 1000,

  // Tempo de cache para listagens (2 minutos)
  listTTL: 2 * 60 * 1000,

  // Tempo de cache para dados estáticos (30 minutos)
  staticTTL: 30 * 60 * 1000,
};

// Mensagens de erro padrão
export const ERROR_MESSAGES = {
  network: 'Erro de conexão. Verifique sua internet e tente novamente.',
  timeout: 'A requisição demorou muito. Tente novamente.',
  unauthorized: 'Sessão expirada. Faça login novamente.',
  forbidden: 'Você não tem permissão para acessar este recurso.',
  notFound: 'Recurso não encontrado.',
  serverError: 'Erro no servidor. Tente novamente mais tarde.',
  validationError:
    'Dados inválidos. Verifique as informações e tente novamente.',
  uploadError: 'Erro ao fazer upload do arquivo. Tente novamente.',
  default: 'Ocorreu um erro inesperado. Tente novamente.',
};

// Tipos de arquivo aceitos
export const ACCEPTED_FILE_TYPES = {
  documents: {
    mimeTypes: [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/vnd.ms-powerpoint',
    ],
    extensions: ['.pdf', '.pptx', '.ppt'],
    maxSize: 100 * 1024 * 1024, // 100MB
  },
  images: {
    mimeTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    extensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    maxSize: 10 * 1024 * 1024, // 10MB
  },
  videos: {
    mimeTypes: ['video/mp4', 'video/webm', 'video/ogg'],
    extensions: ['.mp4', '.webm', '.ogg'],
    maxSize: 500 * 1024 * 1024, // 500MB
  },
  audio: {
    mimeTypes: ['audio/mpeg', 'audio/wav', 'audio/ogg'],
    extensions: ['.mp3', '.wav', '.ogg'],
    maxSize: 50 * 1024 * 1024, // 50MB
  },
};
