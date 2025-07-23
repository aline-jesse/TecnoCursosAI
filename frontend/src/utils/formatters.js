/**
 * Formata um número para exibição com casas decimais
 * @param {number} value - Valor a ser formatado
 * @param {number} decimals - Número de casas decimais
 * @returns {string} - Valor formatado
 */
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined) return '-';
  return Number(value).toFixed(decimals);
};

/**
 * Formata bytes para exibição em KB, MB, GB, etc.
 * @param {number} bytes - Tamanho em bytes
 * @param {number} decimals - Número de casas decimais
 * @returns {string} - Tamanho formatado
 */
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  if (!bytes) return '-';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
};

/**
 * Formata segundos para exibição em formato de tempo (MM:SS ou HH:MM:SS)
 * @param {number} seconds - Tempo em segundos
 * @param {boolean} showHours - Se deve mostrar horas mesmo que seja zero
 * @returns {string} - Tempo formatado
 */
export const formatTime = (seconds, showHours = false) => {
  if (seconds === null || seconds === undefined) return '--:--';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  // Formatar com padding de zero
  const paddedMinutes = String(minutes).padStart(2, '0');
  const paddedSeconds = String(secs).padStart(2, '0');

  if (hours > 0 || showHours) {
    const paddedHours = String(hours).padStart(2, '0');
    return `${paddedHours}:${paddedMinutes}:${paddedSeconds}`;
  }

  return `${paddedMinutes}:${paddedSeconds}`;
};

/**
 * Formata uma data para exibição
 * @param {string|Date} date - Data a ser formatada
 * @param {Object} options - Opções de formatação
 * @returns {string} - Data formatada
 */
export const formatDate = (date, options = {}) => {
  if (!date) return '-';

  const defaultOptions = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  };

  const mergedOptions = { ...defaultOptions, ...options };

  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('pt-BR', mergedOptions);
  } catch (error) {
    console.error('Erro ao formatar data:', error);
    return String(date);
  }
};

/**
 * Trunca um texto para um tamanho máximo
 * @param {string} text - Texto a ser truncado
 * @param {number} maxLength - Tamanho máximo
 * @param {string} suffix - Sufixo a ser adicionado
 * @returns {string} - Texto truncado
 */
export const truncateText = (text, maxLength = 50, suffix = '...') => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength - suffix.length)}${suffix}`;
};

/**
 * Formata um nome de arquivo para exibição
 * @param {string} filename - Nome do arquivo
 * @param {number} maxLength - Tamanho máximo
 * @returns {string} - Nome formatado
 */
export const formatFilename = (filename, maxLength = 20) => {
  if (!filename) return '';

  // Se o nome do arquivo for menor que o tamanho máximo, retorna o nome completo
  if (filename.length <= maxLength) return filename;

  // Divide o nome do arquivo em nome e extensão
  const lastDotIndex = filename.lastIndexOf('.');
  const name =
    lastDotIndex > 0 ? filename.substring(0, lastDotIndex) : filename;
  const extension = lastDotIndex > 0 ? filename.substring(lastDotIndex) : '';

  // Calcula o tamanho disponível para o nome (considerando extensão e '...')
  const availableLength = maxLength - extension.length - 3;

  // Trunca o nome e adiciona a extensão
  return `${name.substring(0, availableLength)}...${extension}`;
};
