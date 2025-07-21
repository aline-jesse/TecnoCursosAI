/**
 * Verifica se um valor é nulo ou indefinido
 * @param {*} value - Valor a ser verificado
 * @returns {boolean} - Se o valor é nulo ou indefinido
 */
export const isNullOrUndefined = value => {
  return value === null || value === undefined;
};

/**
 * Verifica se um valor é vazio (string vazia, array vazio, objeto vazio)
 * @param {*} value - Valor a ser verificado
 * @returns {boolean} - Se o valor é vazio
 */
export const isEmpty = value => {
  if (isNullOrUndefined(value)) return true;

  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;

  return false;
};

/**
 * Verifica se um arquivo é do tipo permitido
 * @param {File} file - Arquivo a ser verificado
 * @param {Array} allowedTypes - Tipos MIME permitidos
 * @returns {boolean} - Se o arquivo é de um tipo permitido
 */
export const isValidFileType = (file, allowedTypes = []) => {
  if (!file || !file.type) return false;

  // Se não houver tipos permitidos especificados, usar padrões
  if (allowedTypes.length === 0) {
    allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    ];
  }

  return allowedTypes.includes(file.type);
};

/**
 * Verifica se um arquivo está dentro do tamanho permitido
 * @param {File} file - Arquivo a ser verificado
 * @param {number} maxSizeMB - Tamanho máximo em MB
 * @returns {boolean} - Se o arquivo está dentro do tamanho permitido
 */
export const isValidFileSize = (file, maxSizeMB = 50) => {
  if (!file || !file.size) return false;

  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
};

/**
 * Verifica se uma string é um email válido
 * @param {string} email - Email a ser verificado
 * @returns {boolean} - Se o email é válido
 */
export const isValidEmail = email => {
  if (!email) return false;

  // Regex para validação de email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Verifica se uma string é uma URL válida
 * @param {string} url - URL a ser verificada
 * @returns {boolean} - Se a URL é válida
 */
export const isValidUrl = url => {
  if (!url) return false;

  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Verifica se um valor é um número
 * @param {*} value - Valor a ser verificado
 * @returns {boolean} - Se o valor é um número
 */
export const isNumber = value => {
  if (isNullOrUndefined(value)) return false;
  return !isNaN(Number(value));
};

/**
 * Verifica se um valor é um número inteiro
 * @param {*} value - Valor a ser verificado
 * @returns {boolean} - Se o valor é um número inteiro
 */
export const isInteger = value => {
  if (!isNumber(value)) return false;
  return Number.isInteger(Number(value));
};

/**
 * Verifica se um valor está dentro de um intervalo
 * @param {number} value - Valor a ser verificado
 * @param {number} min - Valor mínimo
 * @param {number} max - Valor máximo
 * @returns {boolean} - Se o valor está dentro do intervalo
 */
export const isInRange = (value, min, max) => {
  if (!isNumber(value)) return false;

  const numValue = Number(value);
  return numValue >= min && numValue <= max;
};
