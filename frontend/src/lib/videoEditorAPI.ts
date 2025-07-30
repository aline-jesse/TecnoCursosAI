/**
 * API Client para Video Editor
 * Gerencia comunicação com backend de processamento de vídeo
 */

interface UploadResponse {
  success: boolean;
  data: {
    id: string;
    filename: string;
    url: string;
    thumbnail?: string;
    size: number;
    duration: number;
    width?: number;
    height?: number;
    mime_type: string;
    uploaded_at: string;
  };
}

interface ProjectResponse {
  success: boolean;
  project: VideoProject;
}

interface ExportResponse {
  success: boolean;
  export_id: string;
}

interface ExportStatus {
  success: boolean;
  status: {
    status: 'starting' | 'processing_video' | 'processing_audio' | 'encoding' | 'completed' | 'error' | 'cancelled';
    progress: number;
    user_id: string;
    started_at: string;
    output_path?: string;
    error?: string;
  };
}

class VideoEditorAPI {
  private baseUrl: string;
  private token: string | null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.token = this.getAuthToken();
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}/api/video-editor${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  private async uploadRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const url = `${this.baseUrl}/api/video-editor${endpoint}`;
    
    const headers: HeadersInit = {};
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Upload de mídia
  async uploadMedia(file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      if (onProgress) {
        // Simular progresso para demonstração
        const interval = setInterval(() => {
          onProgress(Math.random() * 100);
        }, 100);
        
        const result = await this.uploadRequest<UploadResponse>('/upload', formData);
        clearInterval(interval);
        onProgress(100);
        return result;
      }

      return await this.uploadRequest<UploadResponse>('/upload', formData);
    } catch (error) {
      console.error('Erro no upload:', error);
      throw error;
    }
  }

  // Gerenciamento de projetos
  async createProject(project: Omit<VideoProject, 'id' | 'created_at' | 'updated_at'>): Promise<ProjectResponse> {
    return this.request<ProjectResponse>('/projects', {
      method: 'POST',
      body: JSON.stringify(project),
    });
  }

  async getProject(projectId: string): Promise<ProjectResponse> {
    return this.request<ProjectResponse>(`/projects/${projectId}`);
  }

  async updateProject(projectId: string, project: VideoProject): Promise<ProjectResponse> {
    return this.request<ProjectResponse>(`/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(project),
    });
  }

  async listProjects(): Promise<{ success: boolean; projects: VideoProject[] }> {
    return this.request<{ success: boolean; projects: VideoProject[] }>('/projects');
  }

  // Exportação de vídeo
  async exportProject(
    projectId: string,
    exportSettings: ExportSettings
  ): Promise<ExportResponse> {
    return this.request<ExportResponse>(`/projects/${projectId}/export`, {
      method: 'POST',
      body: JSON.stringify(exportSettings),
    });
  }

  async getExportStatus(exportId: string): Promise<ExportStatus> {
    return this.request<ExportStatus>(`/exports/${exportId}/status`);
  }

  async downloadExport(exportId: string): Promise<Blob> {
    const url = `${this.baseUrl}/api/video-editor/exports/${exportId}/download`;
    
    const headers: HeadersInit = {};
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, { headers });
    
    if (!response.ok) {
      throw new Error(`Erro no download: ${response.statusText}`);
    }

    return response.blob();
  }

  async cancelExport(exportId: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(`/exports/${exportId}/cancel`, {
      method: 'POST',
    });
  }

  // Monitoramento de exportação com polling
  async monitorExport(
    exportId: string,
    onProgress: (status: ExportStatus['status']) => void,
    onComplete: (downloadUrl: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    const pollInterval = 2000; // 2 segundos
    let isCompleted = false;

    const poll = async () => {
      try {
        const statusResponse = await this.getExportStatus(exportId);
        const status = statusResponse.status;

        onProgress(status);

        if (status.status === 'completed') {
          isCompleted = true;
          const downloadUrl = `${this.baseUrl}/api/video-editor/exports/${exportId}/download`;
          onComplete(downloadUrl);
        } else if (status.status === 'error') {
          isCompleted = true;
          onError(status.error || 'Erro desconhecido na exportação');
        } else if (status.status === 'cancelled') {
          isCompleted = true;
          onError('Exportação cancelada');
        } else {
          // Continuar polling se ainda está processando
          setTimeout(poll, pollInterval);
        }
      } catch (error) {
        isCompleted = true;
        onError(error instanceof Error ? error.message : 'Erro na comunicação');
      }
    };

    poll();
  }

  // Utilitários
  getFileUrl(filename: string): string {
    return `${this.baseUrl}/api/files/${filename}`;
  }

  getThumbnailUrl(thumbnailPath: string): string {
    return `${this.baseUrl}${thumbnailPath}`;
  }

  // Validação de arquivos no frontend
  validateFile(file: File): { valid: boolean; error?: string } {
    const maxSize = 500 * 1024 * 1024; // 500MB
    const allowedTypes = [
      'video/mp4',
      'video/quicktime',
      'video/x-msvideo',
      'audio/mpeg',
      'audio/wav',
      'audio/ogg',
      'image/jpeg',
      'image/png',
      'image/gif'
    ];

    if (file.size > maxSize) {
      return {
        valid: false,
        error: `Arquivo muito grande. Máximo permitido: ${maxSize / (1024 * 1024)}MB`
      };
    }

    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `Tipo de arquivo não suportado: ${file.type}`
      };
    }

    return { valid: true };
  }

  // Estimativas de tempo baseadas em tamanho
  estimateProcessingTime(fileSize: number, duration: number): number {
    // Estimativa simples: 1 segundo de processamento para cada 10 segundos de vídeo
    // + tempo baseado no tamanho do arquivo
    const durationFactor = duration * 0.1;
    const sizeFactor = (fileSize / (1024 * 1024)) * 0.1; // MB to seconds
    
    return Math.max(5, durationFactor + sizeFactor); // Mínimo 5 segundos
  }

  // Formatação de tempo para UI
  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  // WebSocket para atualizações em tempo real (opcional)
  connectWebSocket(onMessage: (data: any) => void): WebSocket | null {
    if (!this.token) return null;

    try {
      const wsUrl = `${this.baseUrl.replace('http', 'ws')}/api/video-editor/ws?token=${this.token}`;
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Erro ao parsear mensagem WebSocket:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('Erro WebSocket:', error);
      };

      return ws;
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
      return null;
    }
  }
}

// Instância singleton do cliente API
export const videoEditorAPI = new VideoEditorAPI();

// Hook personalizado para facilitar uso no React
export function useVideoEditorAPI() {
  return {
    api: videoEditorAPI,
    uploadMedia: videoEditorAPI.uploadMedia.bind(videoEditorAPI),
    createProject: videoEditorAPI.createProject.bind(videoEditorAPI),
    getProject: videoEditorAPI.getProject.bind(videoEditorAPI),
    updateProject: videoEditorAPI.updateProject.bind(videoEditorAPI),
    listProjects: videoEditorAPI.listProjects.bind(videoEditorAPI),
    exportProject: videoEditorAPI.exportProject.bind(videoEditorAPI),
    getExportStatus: videoEditorAPI.getExportStatus.bind(videoEditorAPI),
    downloadExport: videoEditorAPI.downloadExport.bind(videoEditorAPI),
    cancelExport: videoEditorAPI.cancelExport.bind(videoEditorAPI),
    monitorExport: videoEditorAPI.monitorExport.bind(videoEditorAPI),
    validateFile: videoEditorAPI.validateFile.bind(videoEditorAPI),
    formatDuration: videoEditorAPI.formatDuration.bind(videoEditorAPI),
  };
}

export default videoEditorAPI;
