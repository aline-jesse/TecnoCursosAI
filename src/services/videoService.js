/**
 * Serviço para processamento de vídeos
 */
const videoService = {
  /**
   * Gera um vídeo a partir das cenas do projeto
   * @param {string} projectId - ID do projeto
   * @param {Object} options - Opções de geração
   * @param {string} options.quality - Qualidade do vídeo (720p, 1080p, 4K)
   * @param {string} options.format - Formato do vídeo (mp4, webm)
   * @param {function} options.onProgress - Callback para progresso
   * @returns {Promise<Object>} - Informações do vídeo gerado
   */
  async generateVideo(projectId, options = {}) {
    try {
      const defaultOptions = {
        quality: process.env.REACT_APP_DEFAULT_VIDEO_QUALITY || '1080p',
        format: 'mp4',
        onProgress: null,
      };

      const mergedOptions = { ...defaultOptions, ...options };

      // Iniciar geração do vídeo
      const response = await api.post(
        `/api/projects/${projectId}/generate-video`,
        {
          quality: mergedOptions.quality,
          format: mergedOptions.format,
        }
      );

      // Se a geração é assíncrona, iniciar polling para verificar status
      if (response.data.status === 'processing') {
        return this.pollVideoStatus(
          response.data.video_id,
          mergedOptions.onProgress
        );
      }

      return response.data;
    } catch (error) {
      console.error('Erro ao gerar vídeo:', error);
      throw error;
    }
  },

  /**
   * Verifica o status de geração do vídeo periodicamente
   * @param {string} videoId - ID do vídeo
   * @param {function} onProgress - Callback para progresso
   * @returns {Promise<Object>} - Informações do vídeo gerado
   */
  async pollVideoStatus(videoId, onProgress) {
    return new Promise((resolve, reject) => {
      const checkStatus = async () => {
        try {
          const response = await api.get(`/api/videos/${videoId}/status`);
          const { status, progress, video } = response.data;

          // Notificar progresso
          if (onProgress && typeof onProgress === 'function') {
            onProgress(progress);
          }

          if (status === 'completed') {
            resolve(video);
            return;
          }

          if (status === 'failed') {
            reject(new Error('Falha ao gerar vídeo'));
            return;
          }

          // Continuar verificando a cada 2 segundos
          setTimeout(checkStatus, 2000);
        } catch (error) {
          reject(error);
        }
      };

      // Iniciar verificação
      checkStatus();
    });
  },

  /**
   * Obtém informações de um vídeo
   * @param {string} videoId - ID do vídeo
   * @returns {Promise<Object>} - Informações do vídeo
   */
  async getVideoInfo(videoId) {
    try {
      const response = await api.get(`/api/videos/${videoId}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao obter informações do vídeo:', error);
      throw error;
    }
  },

  /**
   * Baixa um vídeo
   * @param {string} videoId - ID do vídeo
   * @param {string} filename - Nome do arquivo para download
   * @returns {Promise<boolean>} - Sucesso do download
   */
  async downloadVideo(videoId, filename) {
    try {
      const response = await api.get(`/api/videos/${videoId}/download`, {
        responseType: 'blob',
      });

      // Criar URL do blob e iniciar download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || `video_${videoId}.mp4`);
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

export default videoService;
