/**
 * Configurações de Ambiente - TecnoCursos AI Editor
 */

// Configurações padrão para desenvolvimento
const defaultConfig = {
  // API Backend
  API_URL: 'http://localhost:8000',
  API_BASE_URL: 'http://localhost:8000/api',
  WS_URL: 'ws://localhost:8000/ws',

  // Upload Configuration
  MAX_FILE_SIZE: 50000000, // 50MB
  CHUNK_SIZE: 1048576, // 1MB
  ALLOWED_FILE_TYPES: [
    '.pdf',
    '.pptx',
    '.docx',
    '.txt',
    '.png',
    '.jpg',
    '.jpeg',
    '.gif',
    '.svg',
    '.mp3',
    '.mp4',
    '.wav',
  ],

  // Canvas Configuration
  CANVAS_WIDTH: 1920,
  CANVAS_HEIGHT: 1080,
  CANVAS_FPS: 30,

  // Authentication
  JWT_STORAGE_KEY: 'tecnocursos_token',
  USER_STORAGE_KEY: 'tecnocursos_user',
  SESSION_TIMEOUT: 3600000, // 1 hora

  // Video Generation
  VIDEO_QUALITY: 'high',
  VIDEO_FORMAT: 'mp4',
  AUDIO_QUALITY: 'high',
  AUDIO_FORMAT: 'mp3',

  // Features Flags
  ENABLE_COLLABORATION: true,
  ENABLE_CLOUD_SAVE: true,
  ENABLE_ANALYTICS: true,
  ENABLE_WEBSOCKET: true,
  ENABLE_DRAG_DROP: true,
  ENABLE_AUTO_SAVE: true,

  // Development
  ENV: 'development',
  DEBUG: true,
  LOG_LEVEL: 'debug',

  // Performance
  LAZY_LOADING: true,
  VIRTUALIZATION: true,
  CACHE_ENABLED: true,
  PREFETCH_ASSETS: true,

  // Editor Configuration
  AUTO_SAVE_INTERVAL: 30000, // 30 segundos
  UNDO_LIMIT: 50,
  ZOOM_MIN: 0.1,
  ZOOM_MAX: 5.0,
  GRID_SIZE: 20,
  SNAP_THRESHOLD: 5,

  // Timeline Configuration
  TIMELINE_ZOOM_LEVELS: [25, 50, 75, 100, 150, 200, 300],
  TIMELINE_SNAP_TO_GRID: true,
  TIMELINE_MAGNETIC_SNAP: true,

  // Templates & Assets
  TEMPLATES_URL: 'http://localhost:8000/api/templates',
  ASSETS_URL: 'http://localhost:8000/static',
  THUMBNAILS_URL: 'http://localhost:8000/static/thumbnails',

  // Error Tracking
  SENTRY_DSN: '',
  ERROR_TRACKING_ENABLED: false,

  // Analytics
  GOOGLE_ANALYTICS_ID: '',
  ANALYTICS_ENABLED: false,

  // Social Features
  ENABLE_COMMENTS: true,
  ENABLE_SHARING: true,
  ENABLE_COLLABORATION_CURSOR: true,

  // Notifications
  ENABLE_PUSH_NOTIFICATIONS: true,
  NOTIFICATION_SOUND: true,

  // Branding
  BRAND_NAME: 'TecnoCursos AI',
  BRAND_LOGO_URL: '/assets/logo.png',
  BRAND_COLOR: '#3b82f6',
  BRAND_SECONDARY_COLOR: '#d946ef',
};

// Configurações específicas para produção
const productionConfig = {
  ...defaultConfig,
  ENV: 'production',
  DEBUG: false,
  LOG_LEVEL: 'error',
  API_URL: process.env.REACT_APP_API_URL || 'https://api.tecnocursos.ai',
  API_BASE_URL:
    process.env.REACT_APP_API_BASE_URL || 'https://api.tecnocursos.ai/api',
  WS_URL: process.env.REACT_APP_WS_URL || 'wss://api.tecnocursos.ai/ws',
  ERROR_TRACKING_ENABLED: true,
  ANALYTICS_ENABLED: true,
};

// Função para obter configuração baseada no ambiente
const getConfig = () => {
  const env = process.env.NODE_ENV || 'development';

  // Se há variáveis de ambiente definidas, usa elas
  const envConfig = {};
  Object.keys(defaultConfig).forEach(key => {
    const envVar = process.env[`REACT_APP_${key}`];
    if (envVar !== undefined) {
      // Converte string para tipo apropriado
      if (envVar === 'true') envConfig[key] = true;
      else if (envVar === 'false') envConfig[key] = false;
      else if (!isNaN(envVar)) envConfig[key] = Number(envVar);
      else envConfig[key] = envVar;
    }
  });

  if (env === 'production') {
    return { ...productionConfig, ...envConfig };
  }

  return { ...defaultConfig, ...envConfig };
};

// Configuração final exportada
export const config = getConfig();

// Utilitários para configuração
export const isProduction = () => config.ENV === 'production';
export const isDevelopment = () => config.ENV === 'development';
export const isDebugEnabled = () => config.DEBUG;

// Validação de configuração
export const validateConfig = () => {
  const required = ['API_URL', 'API_BASE_URL'];
  const missing = required.filter(key => !config[key]);

  if (missing.length > 0) {
    console.error('Configurações obrigatórias não encontradas:', missing);
    return false;
  }

  return true;
};

// Logger baseado na configuração
export const logger = {
  debug: (...args) => {
    if (
      config.DEBUG &&
      (config.LOG_LEVEL === 'debug' || config.LOG_LEVEL === 'info')
    ) {
      console.log('[DEBUG]', ...args);
    }
  },
  info: (...args) => {
    if (config.LOG_LEVEL === 'debug' || config.LOG_LEVEL === 'info') {
      console.info('[INFO]', ...args);
    }
  },
  warn: (...args) => {
    if (config.LOG_LEVEL !== 'error') {
      console.warn('[WARN]', ...args);
    }
  },
  error: (...args) => {
    console.error('[ERROR]', ...args);
  },
};

// Configurações específicas para cada componente
export const canvasConfig = {
  width: config.CANVAS_WIDTH,
  height: config.CANVAS_HEIGHT,
  fps: config.CANVAS_FPS,
  zoom: {
    min: config.ZOOM_MIN,
    max: config.ZOOM_MAX,
    default: 1.0,
  },
  grid: {
    size: config.GRID_SIZE,
    enabled: true,
    snap: config.SNAP_THRESHOLD,
  },
};

export const timelineConfig = {
  zoomLevels: config.TIMELINE_ZOOM_LEVELS,
  snapToGrid: config.TIMELINE_SNAP_TO_GRID,
  magneticSnap: config.TIMELINE_MAGNETIC_SNAP,
  defaultDuration: 5000, // 5 segundos
  minDuration: 100, // 100ms
  maxDuration: 300000, // 5 minutos
};

export const uploadConfig = {
  maxFileSize: config.MAX_FILE_SIZE,
  chunkSize: config.CHUNK_SIZE,
  allowedTypes: config.ALLOWED_FILE_TYPES,
  simultaneousUploads: 3,
  retryAttempts: 3,
};

export default config;
