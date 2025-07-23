/**
 * Serviço de Arquivos - TecnoCursos AI
 *
 * Gerencia upload, download e manipulação de arquivos:
 * - Upload de PDF/PPTX com progresso
 * - Upload em chunks para arquivos grandes
 * - Listagem e busca de arquivos
 * - Download de arquivos
 * - Extração de texto e metadados
 */

import api from './api';
import { API_ENDPOINTS, ACCEPTED_FILE_TYPES } from '../config/api.config';

class FileService {
  /**
   * Validar arquivo antes do upload
   *
   * @param {File} file - Arquivo a ser validado
   * @param {string} type - Tipo de arquivo esperado (documents, images, videos, audio)
   * @returns {Object} { valid: boolean, error?: string }
   */
  validateFile(file, type = 'documents') {
    const config = ACCEPTED_FILE_TYPES[type];

    if (!config) {
      return { valid: false, error: 'Tipo de arquivo não suportado' };
    }

    // Verificar extensão
    const extension = `.${file.name.split('.').pop().toLowerCase()}`;
    if (!config.extensions.includes(extension)) {
      return {
        valid: false,
        error: `Extensão não permitida. Aceitos: ${config.extensions.join(', ')}`,
      };
    }

    // Verificar tamanho
    if (file.size > config.maxSize) {
      const maxSizeMB = Math.round(config.maxSize / (1024 * 1024));
      return {
        valid: false,
        error: `Arquivo muito grande. Máximo permitido: ${maxSizeMB}MB`,
      };
    }

    // Verificar MIME type
    if (config.mimeTypes && !config.mimeTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'Tipo de arquivo inválido',
      };
    }

    return { valid: true };
  }

  /**
   * Upload de arquivo único com progresso
   *
   * @param {Object} params - Parâmetros do upload
   * @param {File} params.file - Arquivo a ser enviado
   * @param {string} params.projectId - ID do projeto (opcional)
   * @param {string} params.title - Título do arquivo
   * @param {string} params.description - Descrição do arquivo
   * @param {Function} params.onProgress - Callback de progresso (0-100)
   * @returns {Promise<Object>} Dados do arquivo enviado
   */
  async uploadFile({ file, projectId, title, description, onProgress }) {
    try {
      // Validar arquivo
      const validation = this.validateFile(file, 'documents');
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      // Criar FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_id', projectId);
      formData.append('title', title || file.name);
      if (description) {
        formData.append('description', description);
      }

      // Fazer upload com progresso
      const response = await api.post(API_ENDPOINTS.files.upload, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: onProgress
          ? progressEvent => {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              onProgress(percentCompleted);
            }
          : undefined,
      });

      // Limpar cache de listagem (implementar se necessário)
      // clearCache(API_ENDPOINTS.files.list);

      return response.data;
    } catch (error) {
      console.error('Erro ao fazer upload:', error);
      throw error;
    }
  }

  /**
   * Upload de arquivo grande em chunks
   *
   * @param {Object} params - Parâmetros do upload
   * @param {File} params.file - Arquivo a ser enviado
   * @param {string} params.projectId - ID do projeto
   * @param {Function} params.onProgress - Callback de progresso
   * @param {number} params.chunkSize - Tamanho de cada chunk (padrão: 5MB)
   * @returns {Promise<Object>} Dados do arquivo enviado
   */
  async uploadFileChunked({
    file,
    projectId,
    onProgress,
    chunkSize = 5 * 1024 * 1024,
  }) {
    try {
      const totalChunks = Math.ceil(file.size / chunkSize);
      const uploadId = this.generateUploadId();

      let uploadedBytes = 0;

      // Upload de cada chunk
      for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        const start = chunkIndex * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append('chunk', chunk);
        formData.append('upload_id', uploadId);
        formData.append('chunk_index', chunkIndex);
        formData.append('total_chunks', totalChunks);
        formData.append('filename', file.name);
        formData.append('project_id', projectId);
        formData.append('file_size', file.size);

        await api.post(API_ENDPOINTS.files.uploadChunk, formData);

        uploadedBytes = end;
        if (onProgress) {
          const progress = Math.round((uploadedBytes / file.size) * 100);
          onProgress(progress);
        }
      }

      // Limpar cache (implementar se necessário)
      // clearCache(API_ENDPOINTS.files.list);

      return { upload_id: uploadId, status: 'completed' };
    } catch (error) {
      console.error('Erro no upload em chunks:', error);
      throw error;
    }
  }

  /**
   * Listar arquivos do usuário
   *
   * @param {Object} params - Parâmetros de filtro
   * @param {string} params.projectId - Filtrar por projeto
   * @param {string} params.fileType - Filtrar por tipo (pdf, pptx, etc)
   * @param {string} params.search - Buscar por nome
   * @param {number} params.skip - Paginação
   * @param {number} params.limit - Limite por página
   * @returns {Promise<{data: Array, total: number}>}
   */
  async listFiles({ projectId, fileType, search, skip = 0, limit = 20 } = {}) {
    try {
      const response = await api.get(API_ENDPOINTS.files.list, {
        params: {
          project_id: projectId,
          file_type: fileType,
          search,
          skip,
          limit,
        },
      });

      return {
        data: response.data,
        total: response.headers['x-total-count'] || response.data.length,
      };
    } catch (error) {
      console.error('Erro ao listar arquivos:', error);
      throw error;
    }
  }

  /**
   * Obter detalhes de um arquivo
   *
   * @param {string} fileId - ID do arquivo
   * @returns {Promise<Object>} Dados do arquivo
   */
  async getFile(fileId) {
    try {
      const response = await api.get(API_ENDPOINTS.files.get(fileId));
      return response.data;
    } catch (error) {
      console.error('Erro ao obter arquivo:', error);
      throw error;
    }
  }

  /**
   * Baixar arquivo
   *
   * @param {string} fileId - ID do arquivo
   * @param {string} filename - Nome do arquivo para download
   * @returns {Promise<void>}
   */
  async downloadFile(fileId, filename) {
    try {
      await downloadFile(API_ENDPOINTS.files.download(fileId), filename);
    } catch (error) {
      console.error('Erro ao baixar arquivo:', error);
      throw error;
    }
  }

  /**
   * Deletar arquivo
   *
   * @param {string} fileId - ID do arquivo
   * @returns {Promise<void>}
   */
  async deleteFile(fileId) {
    try {
      await api.delete(API_ENDPOINTS.files.delete(fileId));

      // Limpar cache
      clearCache(API_ENDPOINTS.files.list);
      clearCache(API_ENDPOINTS.files.get(fileId));
    } catch (error) {
      console.error('Erro ao deletar arquivo:', error);
      throw error;
    }
  }

  /**
   * Buscar texto em PDFs
   *
   * @param {string} query - Texto a buscar
   * @param {string} projectId - Limitar busca a um projeto
   * @returns {Promise<Array>} Resultados da busca
   */
  async searchInFiles(query, projectId) {
    try {
      const response = await api.get(API_ENDPOINTS.files.search, {
        params: {
          q: query,
          project_id: projectId,
        },
      });

      return response.data;
    } catch (error) {
      console.error('Erro ao buscar em arquivos:', error);
      throw error;
    }
  }

  /**
   * Upload múltiplo de arquivos
   *
   * @param {Object} params - Parâmetros
   * @param {FileList|Array<File>} params.files - Arquivos a enviar
   * @param {string} params.projectId - ID do projeto
   * @param {Function} params.onProgress - Callback de progresso geral
   * @param {Function} params.onFileComplete - Callback quando um arquivo é concluído
   * @returns {Promise<Object>} Resumo do upload
   */
  async uploadMultipleFiles({ files, projectId, onProgress, onFileComplete }) {
    const fileArray = Array.from(files);
    const results = [];

    for (let i = 0; i < fileArray.length; i++) {
      const file = fileArray[i];

      try {
        const result = await this.uploadFile({
          file,
          projectId,
          onProgress: fileProgress => {
            if (onProgress) {
              const totalProgress =
                (i / fileArray.length) * 100 + fileProgress / fileArray.length;
              onProgress(Math.round(totalProgress));
            }
          },
        });

        results.push({ file: file.name, success: true, data: result });

        if (onFileComplete) {
          onFileComplete(file.name, true, result);
        }
      } catch (error) {
        results.push({ file: file.name, success: false, error: error.message });

        if (onFileComplete) {
          onFileComplete(file.name, false, error);
        }
      }
    }

    const successful = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;

    return {
      results,
      summary: {
        total: fileArray.length,
        successful,
        failed,
      },
    };
  }

  /**
   * Gerar ID único para upload
   * @private
   */
  generateUploadId() {
    return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Exportar instância única do serviço
export default new FileService();
