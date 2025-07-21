/**
 * Hook personalizado para upload de arquivos
 *
 * Gerencia uploads com:
 * - Progresso individual e total
 * - Upload múltiplo
 * - Validação de arquivos
 * - Tratamento de erros
 * - Preview de arquivos
 */

import { useState, useCallback, useRef } from 'react';
import fileService from '../services/fileService';
import { useNotification } from './useNotification';

export const useFileUpload = projectId => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [errors, setErrors] = useState([]);
  const [totalProgress, setTotalProgress] = useState(0);

  const { showSuccess, showError, showWarning } = useNotification();
  const abortControllerRef = useRef(null);

  /**
   * Fazer upload de arquivo único
   */
  const uploadFile = useCallback(
    async (file, options = {}) => {
      const fileId = `${file.name}_${Date.now()}`;

      try {
        setUploading(true);
        setErrors([]);

        // Validar arquivo
        const validation = fileService.validateFile(file);
        if (!validation.valid) {
          throw new Error(validation.error);
        }

        // Inicializar progresso
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { name: file.name, progress: 0, status: 'uploading' },
        }));

        // Fazer upload
        const result = await fileService.uploadFile({
          file,
          projectId: options.projectId || projectId,
          title: options.title,
          description: options.description,
          onProgress: progress => {
            setUploadProgress(prev => ({
              ...prev,
              [fileId]: { ...prev[fileId], progress },
            }));
            setTotalProgress(progress);
          },
        });

        // Atualizar status de sucesso
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { ...prev[fileId], progress: 100, status: 'completed' },
        }));

        setUploadedFiles(prev => [...prev, result]);
        showSuccess(`Arquivo "${file.name}" enviado com sucesso!`);

        return result;
      } catch (error) {
        // Atualizar status de erro
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { ...prev[fileId], status: 'error', error: error.message },
        }));

        setErrors(prev => [...prev, { file: file.name, error: error.message }]);
        showError(`Erro ao enviar "${file.name}": ${error.message}`);
        throw error;
      } finally {
        setUploading(false);
        setTotalProgress(0);
      }
    },
    [projectId, showSuccess, showError]
  );

  /**
   * Upload múltiplo de arquivos
   */
  const uploadMultipleFiles = useCallback(
    async (files, options = {}) => {
      setUploading(true);
      setErrors([]);
      setUploadedFiles([]);
      setUploadProgress({});

      try {
        const result = await fileService.uploadMultipleFiles({
          files,
          projectId: options.projectId || projectId,
          onProgress: setTotalProgress,
          onFileComplete: (filename, success, data) => {
            if (success) {
              setUploadedFiles(prev => [...prev, data]);
            }
          },
        });

        // Mostrar resumo
        if (result.summary.successful > 0) {
          showSuccess(
            `${result.summary.successful} arquivo(s) enviado(s) com sucesso!`
          );
        }

        if (result.summary.failed > 0) {
          showWarning(`${result.summary.failed} arquivo(s) falharam no envio.`);
        }

        return result;
      } catch (error) {
        showError('Erro durante o upload múltiplo');
        throw error;
      } finally {
        setUploading(false);
        setTotalProgress(0);
      }
    },
    [projectId, showSuccess, showError, showWarning]
  );

  /**
   * Upload de arquivo grande em chunks
   */
  const uploadLargeFile = useCallback(
    async (file, options = {}) => {
      const fileId = `${file.name}_${Date.now()}`;

      try {
        setUploading(true);
        setErrors([]);

        // Verificar se o arquivo é grande (> 50MB)
        const isLarge = file.size > 50 * 1024 * 1024;

        if (!isLarge) {
          // Se não for grande, usar upload normal
          return await uploadFile(file, options);
        }

        // Inicializar progresso
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { name: file.name, progress: 0, status: 'uploading' },
        }));

        // Upload em chunks
        const result = await fileService.uploadFileChunked({
          file,
          projectId: options.projectId || projectId,
          onProgress: progress => {
            setUploadProgress(prev => ({
              ...prev,
              [fileId]: { ...prev[fileId], progress },
            }));
            setTotalProgress(progress);
          },
        });

        // Atualizar status
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { ...prev[fileId], progress: 100, status: 'completed' },
        }));

        showSuccess(`Arquivo grande "${file.name}" enviado com sucesso!`);
        return result;
      } catch (error) {
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { ...prev[fileId], status: 'error', error: error.message },
        }));

        showError(`Erro ao enviar arquivo grande: ${error.message}`);
        throw error;
      } finally {
        setUploading(false);
        setTotalProgress(0);
      }
    },
    [projectId, uploadFile, showSuccess, showError]
  );

  /**
   * Cancelar upload em andamento
   */
  const cancelUpload = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setUploading(false);
      setTotalProgress(0);
      showWarning('Upload cancelado');
    }
  }, [showWarning]);

  /**
   * Limpar estado de upload
   */
  const clearUploadState = useCallback(() => {
    setUploadProgress({});
    setUploadedFiles([]);
    setErrors([]);
    setTotalProgress(0);
  }, []);

  /**
   * Verificar se pode fazer upload
   */
  const canUpload = useCallback(file => {
    const validation = fileService.validateFile(file);
    return validation.valid;
  }, []);

  /**
   * Obter preview de arquivo
   */
  const getFilePreview = useCallback(file => {
    if (file.type.startsWith('image/')) {
      return URL.createObjectURL(file);
    }

    // Ícones por tipo de arquivo
    const icons = {
      'application/pdf': '📄',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        '📊',
      'application/vnd.ms-powerpoint': '📊',
    };

    return icons[file.type] || '📎';
  }, []);

  return {
    // Estados
    uploading,
    uploadProgress,
    uploadedFiles,
    errors,
    totalProgress,

    // Ações
    uploadFile,
    uploadMultipleFiles,
    uploadLargeFile,
    cancelUpload,
    clearUploadState,

    // Helpers
    canUpload,
    getFilePreview,
    hasErrors: errors.length > 0,
    isUploading: uploading,
    completedCount: uploadedFiles.length,
  };
};
