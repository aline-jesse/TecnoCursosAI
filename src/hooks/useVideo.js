import { useState, useCallback } from 'react';
import videoService from '../services/videoService';

/**
 * Hook personalizado para gerenciar vídeos
 * @param {Object} options - Opções de configuração
 * @param {string} options.projectId - ID do projeto (opcional)
 * @param {Function} options.onProgress - Callback para progresso
 * @returns {Object} - Métodos e estados do vídeo
 */
const useVideo = (options = {}) => {
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [video, setVideo] = useState(null);

  /**
   * Gera um vídeo para o projeto
   * @param {string} projectId - ID do projeto (opcional, sobrescreve o da configuração)
   * @param {Object} videoOptions - Opções de geração
   */
  const generateVideo = useCallback(
    async (projectId = null, videoOptions = {}) => {
      const targetProjectId = projectId || options.projectId;

      if (!targetProjectId) {
        setError('ID do projeto não especificado');
        return;
      }

      try {
        setGenerating(true);
        setProgress(0);
        setError(null);
        setVideo(null);

        // Configurar callback de progresso
        const handleProgress = progressValue => {
          setProgress(progressValue);
          if (options.onProgress) options.onProgress(progressValue);
        };

        // Iniciar geração de vídeo
        const generatedVideo = await videoService.generateVideo(
          targetProjectId,
          {
            ...videoOptions,
            onProgress: handleProgress,
          }
        );

        setVideo(generatedVideo);
        return generatedVideo;
      } catch (error) {
        console.error('Erro ao gerar vídeo:', error);
        setError(error.message || 'Erro ao gerar vídeo');
        throw error;
      } finally {
        setGenerating(false);
      }
    },
    [options]
  );

  /**
   * Baixa um vídeo
   * @param {string} videoId - ID do vídeo (opcional, usa o vídeo atual se não especificado)
   * @param {string} filename - Nome do arquivo para download
   */
  const downloadVideo = useCallback(
    async (videoId = null, filename = null) => {
      const targetVideoId = videoId || (video ? video.id : null);

      if (!targetVideoId) {
        setError('ID do vídeo não especificado');
        return;
      }

      try {
        setError(null);
        await videoService.downloadVideo(targetVideoId, filename);
        return true;
      } catch (error) {
        console.error('Erro ao baixar vídeo:', error);
        setError(error.message || 'Erro ao baixar vídeo');
        throw error;
      }
    },
    [video]
  );

  /**
   * Reseta o estado do vídeo
   */
  const reset = useCallback(() => {
    setGenerating(false);
    setProgress(0);
    setError(null);
    setVideo(null);
  }, []);

  return {
    generateVideo,
    downloadVideo,
    reset,
    generating,
    progress,
    error,
    video,
  };
};

export default useVideo;
