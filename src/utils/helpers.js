/**
 * Utilitários e Helpers - TecnoCursos AI Editor
 * Funções auxiliares para formatação, validação e manipulação de dados
 */

import { config } from '../config/environment';

/**
 * Formatação de tempo
 */
export const formatTime = (milliseconds, format = 'mm:ss') => {
  const totalSeconds = Math.floor(milliseconds / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const pad = num => num.toString().padStart(2, '0');

  switch (format) {
    case 'hh:mm:ss':
      return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
    case 'mm:ss':
      return `${pad(minutes)}:${pad(seconds)}`;
    case 'ss':
      return `${pad(seconds)}s`;
    case 'human':
      if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
      if (minutes > 0) return `${minutes}m ${seconds}s`;
      return `${seconds}s`;
    default:
      return `${pad(minutes)}:${pad(seconds)}`;
  }
};

/**
 * Formatação de tamanho de arquivo
 */
export const formatFileSize = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Formatação de data
 */
export const formatDate = (date, format = 'relative') => {
  const now = new Date();
  const targetDate = new Date(date);
  const diffMs = now - targetDate;
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  switch (format) {
    case 'relative':
      if (diffMinutes < 1) return 'agora';
      if (diffMinutes < 60) return `${diffMinutes}min atrás`;
      if (diffHours < 24) return `${diffHours}h atrás`;
      if (diffDays < 7) return `${diffDays}d atrás`;
      return targetDate.toLocaleDateString('pt-BR');

    case 'full':
      return targetDate.toLocaleString('pt-BR');

    case 'date':
      return targetDate.toLocaleDateString('pt-BR');

    case 'time':
      return targetDate.toLocaleTimeString('pt-BR');

    default:
      return targetDate.toLocaleDateString('pt-BR');
  }
};

/**
 * Validação de arquivos
 */
export const validateFile = file => {
  const errors = [];

  // Verificar tamanho
  if (file.size > config.MAX_FILE_SIZE) {
    errors.push(
      `Arquivo muito grande. Máximo: ${formatFileSize(config.MAX_FILE_SIZE)}`
    );
  }

  // Verificar tipo
  const extension = '.' + file.name.split('.').pop().toLowerCase();
  if (!config.ALLOWED_FILE_TYPES.includes(extension)) {
    errors.push(
      `Tipo de arquivo não permitido. Tipos aceitos: ${config.ALLOWED_FILE_TYPES.join(', ')}`
    );
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Geração de IDs únicos
 */
export const generateId = (prefix = 'id') => {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 9);
  return `${prefix}_${timestamp}_${random}`;
};

/**
 * Debounce para otimização de performance
 */
export const debounce = (func, wait, immediate) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
};

/**
 * Throttle para limitação de frequência
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Deep clone de objetos
 */
export const deepClone = obj => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const cloned = {};
    Object.keys(obj).forEach(key => {
      cloned[key] = deepClone(obj[key]);
    });
    return cloned;
  }
};

/**
 * Comparação profunda de objetos
 */
export const deepEqual = (a, b) => {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (typeof a !== typeof b) return false;

  if (typeof a === 'object') {
    const aKeys = Object.keys(a);
    const bKeys = Object.keys(b);

    if (aKeys.length !== bKeys.length) return false;

    for (let key of aKeys) {
      if (!bKeys.includes(key)) return false;
      if (!deepEqual(a[key], b[key])) return false;
    }

    return true;
  }

  return false;
};

/**
 * Conversão de coordenadas
 */
export const canvasToScreenCoords = (
  canvasX,
  canvasY,
  zoom,
  panX = 0,
  panY = 0
) => {
  return {
    x: canvasX * zoom + panX,
    y: canvasY * zoom + panY,
  };
};

export const screenToCanvasCoords = (
  screenX,
  screenY,
  zoom,
  panX = 0,
  panY = 0
) => {
  return {
    x: (screenX - panX) / zoom,
    y: (screenY - panY) / zoom,
  };
};

/**
 * Detecção de colisão entre retângulos
 */
export const isRectCollision = (rect1, rect2) => {
  return !(
    rect1.x + rect1.width < rect2.x ||
    rect2.x + rect2.width < rect1.x ||
    rect1.y + rect1.height < rect2.y ||
    rect2.y + rect2.height < rect1.y
  );
};

/**
 * Snap para grid
 */
export const snapToGrid = (value, gridSize = 20) => {
  return Math.round(value / gridSize) * gridSize;
};

/**
 * Cálculo de distância entre pontos
 */
export const distance = (x1, y1, x2, y2) => {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
};

/**
 * Conversão de graus para radianos
 */
export const degreesToRadians = degrees => {
  return degrees * (Math.PI / 180);
};

/**
 * Conversão de radianos para graus
 */
export const radiansToDegrees = radians => {
  return radians * (180 / Math.PI);
};

/**
 * Cálculo de ângulo entre dois pontos
 */
export const angleBetween = (x1, y1, x2, y2) => {
  return Math.atan2(y2 - y1, x2 - x1);
};

/**
 * Limitação de valor entre min e max
 */
export const clamp = (value, min, max) => {
  return Math.min(Math.max(value, min), max);
};

/**
 * Interpolação linear
 */
export const lerp = (start, end, factor) => {
  return start + (end - start) * factor;
};

/**
 * Formatação de texto
 */
export const truncateText = (text, maxLength = 50, suffix = '...') => {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength - suffix.length) + suffix;
};

export const capitalizeFirst = str => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const camelToKebab = str => {
  return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
};

export const kebabToCamel = str => {
  return str.replace(/-([a-z])/g, g => g[1].toUpperCase());
};

/**
 * Validação de URL
 */
export const isValidUrl = string => {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
};

/**
 * Extração de extensão de arquivo
 */
export const getFileExtension = filename => {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
};

/**
 * Geração de cores aleatórias
 */
export const randomColor = () => {
  return '#' + Math.floor(Math.random() * 16777215).toString(16);
};

export const randomColorFromPalette = (
  palette = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
) => {
  return palette[Math.floor(Math.random() * palette.length)];
};

/**
 * Conversão de cores
 */
export const hexToRgb = hex => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
};

export const rgbToHex = (r, g, b) => {
  return (
    '#' +
    [r, g, b]
      .map(x => {
        const hex = x.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
      })
      .join('')
  );
};

/**
 * Manipulação de localStorage com fallback
 */
export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn('Erro ao ler localStorage:', error);
      return defaultValue;
    }
  },

  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.warn('Erro ao escrever localStorage:', error);
      return false;
    }
  },

  remove: key => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.warn('Erro ao remover localStorage:', error);
      return false;
    }
  },
};

/**
 * Download de arquivo
 */
export const downloadFile = (
  data,
  filename,
  mimeType = 'application/octet-stream'
) => {
  const blob = new Blob([data], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Cópia para clipboard
 */
export const copyToClipboard = async text => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    // Fallback para navegadores mais antigos
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      return true;
    } catch (err) {
      console.warn('Erro ao copiar para clipboard:', err);
      return false;
    } finally {
      document.body.removeChild(textArea);
    }
  }
};

/**
 * Detecção de dispositivo
 */
export const device = {
  isMobile: () =>
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    ),
  isTablet: () => /iPad|Android|Tablet/i.test(navigator.userAgent),
  isDesktop: () => !device.isMobile() && !device.isTablet(),
  isTouchDevice: () => 'ontouchstart' in window || navigator.maxTouchPoints > 0,
  getOS: () => {
    const userAgent = navigator.userAgent;
    if (/Windows/i.test(userAgent)) return 'Windows';
    if (/Macintosh|Mac OS X/i.test(userAgent)) return 'macOS';
    if (/Linux/i.test(userAgent)) return 'Linux';
    if (/Android/i.test(userAgent)) return 'Android';
    if (/iPhone|iPad|iPod/i.test(userAgent)) return 'iOS';
    return 'Unknown';
  },
};

/**
 * Utilitários de array
 */
export const arrayUtils = {
  shuffle: array => {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  },

  unique: array => [...new Set(array)],

  chunk: (array, size) => {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  },

  groupBy: (array, key) => {
    return array.reduce((groups, item) => {
      const group = item[key];
      groups[group] = groups[group] || [];
      groups[group].push(item);
      return groups;
    }, {});
  },
};

/**
 * Performance helpers
 */
export const performance = {
  measure: (name, fn) => {
    const start = Date.now();
    const result = fn();
    const end = Date.now();
    console.log(`${name}: ${end - start}ms`);
    return result;
  },

  measureAsync: async (name, asyncFn) => {
    const start = Date.now();
    const result = await asyncFn();
    const end = Date.now();
    console.log(`${name}: ${end - start}ms`);
    return result;
  },
};

// Exportar todas as funções
export default {
  formatTime,
  formatFileSize,
  formatDate,
  validateFile,
  generateId,
  debounce,
  throttle,
  deepClone,
  deepEqual,
  canvasToScreenCoords,
  screenToCanvasCoords,
  isRectCollision,
  snapToGrid,
  distance,
  degreesToRadians,
  radiansToDegrees,
  angleBetween,
  clamp,
  lerp,
  truncateText,
  capitalizeFirst,
  camelToKebab,
  kebabToCamel,
  isValidUrl,
  getFileExtension,
  randomColor,
  randomColorFromPalette,
  hexToRgb,
  rgbToHex,
  storage,
  downloadFile,
  copyToClipboard,
  device,
  arrayUtils,
  performance,
};
