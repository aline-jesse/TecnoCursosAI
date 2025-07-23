/**
 * 🔗 TecnoCursos AI - API Service
 * Serviço de integração completo entre Frontend React e Backend FastAPI
 * Enterprise Edition 2025
 */

// ============================================================================
// 🔧 SERVIÇO DE API - TECNOCURSOS AI
// ============================================================================

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Asset, Scene } from '../types/editor';

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  token: string;
  access_token: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
    full_name?: string;
    username?: string;
    is_admin?: boolean;
  };
}

interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

interface ProjectRequest {
  name: string;
  description?: string;
  settings?: any;
}

interface SceneRequest {
  name: string;
  duration: number;
  elements?: Scene['elements'];
}

interface AssetUploadResponse {
  id: string;
  url: string;
  filename: string;
  size: number;
  type: string;
}

interface RenderRequest {
  projectId: string;
  settings?: {
    quality: 'low' | 'medium' | 'high';
    format: 'mp4' | 'webm' | 'gif';
    resolution: string;
  };
}

interface RenderStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  estimatedTime: number;
  outputUrl?: string;
  error?: string;
}

// ============================================================================
// CONFIGURAÇÃO DA API
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  public http: AxiosInstance;

  constructor() {
    this.http = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para adicionar token de autenticação
    this.http.interceptors.request.use(
      config => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      error => {
        return Promise.reject(error);
      }
    );

    // Interceptor para tratamento de erros
    this.http.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          this.handleUnauthorized();
        }
        return Promise.reject(error);
      }
    );
  }

  // ============================================================================
  // MÉTODOS DE AUTENTICAÇÃO
  // ============================================================================

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  private removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  private handleUnauthorized(): void {
    this.removeToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  // ============================================================================
  // ENDPOINTS DE AUTENTICAÇÃO
  // ============================================================================

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response: AxiosResponse<LoginResponse> = await this.http.post(
        '/api/auth/login',
        credentials
      );

      if (response.data) {
        const token = response.data.access_token;
        this.setToken(token);

        // Mapear resposta do backend para o formato esperado pelo frontend
        return {
          token,
          access_token: token,
          user: {
            id: response.data.user.id.toString(),
            email: response.data.user.email,
            name:
              response.data.user.full_name ||
              response.data.user.username ||
              response.data.user.name ||
              'Usuário',
            role: response.data.user.is_admin ? 'admin' : 'user',
          },
        };
      } else {
        throw new Error('Resposta inválida do servidor');
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Email ou senha incorretos');
      }
      throw new Error(error.response?.data?.detail || 'Erro de conexão');
    }
  }

  async register(userData: RegisterRequest): Promise<LoginResponse> {
    try {
      // Mapear dados do frontend para o formato esperado pelo backend
      const registerData = {
        full_name: userData.name,
        email: userData.email,
        password: userData.password,
        username: userData.email.split('@')[0], // Gerar username a partir do email
      };

      const response: AxiosResponse<any> = await this.http.post(
        '/api/auth/register',
        registerData
      );

      if (response.data) {
        const token = response.data.access_token;
        this.setToken(token);

        // Mapear resposta do backend para o formato esperado pelo frontend
        return {
          token,
          access_token: token,
          user: {
            id: response.data.user.id.toString(),
            email: response.data.user.email,
            name:
              response.data.user.full_name ||
              response.data.user.username ||
              response.data.user.name ||
              'Usuário',
            role: response.data.user.is_admin ? 'admin' : 'user',
          },
        };
      } else {
        throw new Error('Resposta inválida do servidor');
      }
    } catch (error: any) {
      if (error.response?.status === 400) {
        throw new Error('Email já está em uso');
      }
      throw new Error(error.response?.data?.detail || 'Erro de conexão');
    }
  }

  async logout(): Promise<void> {
    try {
      await this.http.post('/api/auth/logout');
    } catch {
      // Ignore logout errors
    }
  }

  async getCurrentUser(): Promise<any> {
    try {
      const response: AxiosResponse<ApiResponse<any>> =
        await this.http.get('/api/auth/me');
      return response.data.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Erro ao obter usuário');
    }
  }

  // ============================================================================
  // ENDPOINTS DE PROJETOS
  // ============================================================================

  async getProjects(): Promise<any[]> {
    // Assuming Project type is not defined here, so using any[] for now
    try {
      const response: AxiosResponse<ApiResponse<any[]>> =
        await this.http.get('/api/projects');
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao carregar projetos'
      );
    }
  }

  async getProject(projectId: string): Promise<any> {
    // Assuming Project type is not defined here, so using any
    try {
      const response: AxiosResponse<ApiResponse<any>> = await this.http.get(
        `/api/projects/${projectId}`
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao carregar projeto'
      );
    }
  }

  async createProject(projectData: ProjectRequest): Promise<any> {
    // Assuming Project type is not defined here, so using any
    try {
      const response: AxiosResponse<ApiResponse<any>> = await this.http.post(
        '/api/projects',
        projectData
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Erro ao criar projeto');
    }
  }

  async updateProject(
    projectId: string,
    projectData: Partial<any>
  ): Promise<any> {
    // Assuming Project type is not defined here, so using any
    try {
      const response: AxiosResponse<ApiResponse<any>> = await this.http.put(
        `/api/projects/${projectId}`,
        projectData
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao atualizar projeto'
      );
    }
  }

  async deleteProject(projectId: string): Promise<void> {
    try {
      await this.http.delete(`/api/projects/${projectId}`);
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao deletar projeto'
      );
    }
  }

  // ============================================================================
  // ENDPOINTS DE CENAS
  // ============================================================================

  async getScenes(projectId: string): Promise<Scene[]> {
    try {
      const response: AxiosResponse<ApiResponse<Scene[]>> = await this.http.get(
        `/api/projects/${projectId}/scenes`
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao carregar cenas'
      );
    }
  }

  async createScene(
    projectId: string,
    sceneData: SceneRequest
  ): Promise<Scene> {
    try {
      const response: AxiosResponse<ApiResponse<Scene>> = await this.http.post(
        `/api/projects/${projectId}/scenes`,
        sceneData
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Erro ao criar cena');
    }
  }

  async updateScene(
    projectId: string,
    sceneId: string,
    sceneData: Partial<Scene>
  ): Promise<Scene> {
    try {
      const response: AxiosResponse<ApiResponse<Scene>> = await this.http.put(
        `/api/projects/${projectId}/scenes/${sceneId}`,
        sceneData
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao atualizar cena'
      );
    }
  }

  async deleteScene(projectId: string, sceneId: string): Promise<void> {
    try {
      await this.http.delete(`/api/projects/${projectId}/scenes/${sceneId}`);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Erro ao deletar cena');
    }
  }

  // ============================================================================
  // ENDPOINTS DE ASSETS
  // ============================================================================

  async getAssets(filters?: Record<string, any>): Promise<Asset[]> {
    try {
      const params = filters ? new URLSearchParams(filters).toString() : '';
      const response: AxiosResponse<ApiResponse<Asset[]>> = await this.http.get(
        `/api/assets${params ? `?${params}` : ''}`
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao carregar assets'
      );
    }
  }

  async uploadAsset(file: File, metadata?: any): Promise<AssetUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      if (metadata) {
        formData.append('metadata', JSON.stringify(metadata));
      }

      const response: AxiosResponse<ApiResponse<AssetUploadResponse>> =
        await this.http.post('/api/assets/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao fazer upload do asset'
      );
    }
  }

  async deleteAsset(assetId: string): Promise<void> {
    try {
      await this.http.delete(`/api/assets/${assetId}`);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Erro ao deletar asset');
    }
  }

  // ============================================================================
  // ENDPOINTS DE RENDERIZAÇÃO
  // ============================================================================

  async renderVideo(renderData: RenderRequest): Promise<{ renderId: string }> {
    try {
      const response: AxiosResponse<ApiResponse<{ renderId: string }>> =
        await this.http.post('/api/render', renderData);
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao iniciar renderização'
      );
    }
  }

  async getRenderStatus(renderId: string): Promise<RenderStatus> {
    try {
      const response: AxiosResponse<ApiResponse<RenderStatus>> =
        await this.http.get(`/api/render/${renderId}/status`);
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao obter status da renderização'
      );
    }
  }

  async cancelRender(renderId: string): Promise<void> {
    try {
      await this.http.post(`/api/render/${renderId}/cancel`);
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao cancelar renderização'
      );
    }
  }

  // ============================================================================
  // ENDPOINTS DE EXPORTAÇÃO
  // ============================================================================

  async exportProject(
    projectId: string,
    format: 'json' | 'zip'
  ): Promise<{ downloadUrl: string }> {
    try {
      const response: AxiosResponse<ApiResponse<{ downloadUrl: string }>> =
        await this.http.post(`/api/projects/${projectId}/export`, { format });
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao exportar projeto'
      );
    }
  }

  async importProject(file: File): Promise<any> {
    // Assuming Project type is not defined here, so using any
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response: AxiosResponse<ApiResponse<any>> = await this.http.post(
        '/api/projects/import',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao importar projeto'
      );
    }
  }

  // ============================================================================
  // ENDPOINTS DE COLABORAÇÃO
  // ============================================================================

  async shareProject(
    projectId: string,
    userEmail: string,
    permissions: string[]
  ): Promise<void> {
    try {
      await this.http.post(`/api/projects/${projectId}/share`, {
        userEmail,
        permissions,
      });
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao compartilhar projeto'
      );
    }
  }

  async getCollaborators(projectId: string): Promise<any[]> {
    try {
      const response: AxiosResponse<ApiResponse<any[]>> = await this.http.get(
        `/api/projects/${projectId}/collaborators`
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao obter colaboradores'
      );
    }
  }

  // ============================================================================
  // ENDPOINTS DE TEMPLATES
  // ============================================================================

  async getTemplates(): Promise<any[]> {
    try {
      const response: AxiosResponse<ApiResponse<any[]>> =
        await this.http.get('/api/templates');
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao carregar templates'
      );
    }
  }

  async createProjectFromTemplate(
    templateId: string,
    projectData: ProjectRequest
  ): Promise<any> {
    // Assuming Project type is not defined here, so using any
    try {
      const response: AxiosResponse<ApiResponse<any>> = await this.http.post(
        `/api/templates/${templateId}/create-project`,
        projectData
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao criar projeto do template'
      );
    }
  }

  // ============================================================================
  // ENDPOINTS DE ANÁLISE E MÉTRICAS
  // ============================================================================

  async getProjectAnalytics(projectId: string): Promise<any> {
    try {
      const response: AxiosResponse<ApiResponse<any>> = await this.http.get(
        `/api/projects/${projectId}/analytics`
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao obter analytics do projeto'
      );
    }
  }

  async getUserAnalytics(): Promise<any> {
    try {
      const response: AxiosResponse<ApiResponse<any>> = await this.http.get(
        '/api/analytics/user'
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao obter analytics do usuário'
      );
    }
  }

  // ============================================================================
  // ENDPOINTS DE CONFIGURAÇÕES
  // ============================================================================

  async getUserSettings(): Promise<any> {
    try {
      const response: AxiosResponse<ApiResponse<any>> =
        await this.http.get('/api/user/settings');
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao obter configurações'
      );
    }
  }

  async updateUserSettings(settings: any): Promise<any> {
    try {
      const response: AxiosResponse<ApiResponse<any>> = await this.http.put(
        '/api/user/settings',
        settings
      );
      return response.data.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 'Erro ao atualizar configurações'
      );
    }
  }

  // ============================================================================
  // MÉTODOS DE UTILIDADE
  // ============================================================================

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}

// ============================================================================
// INSTÂNCIA GLOBAL
// ============================================================================

export const apiService = new ApiService();

// ============================================================================
// HOOKS PARA REACT
// ============================================================================

export const useApiService = () => {
  return apiService;
};

// ============================================================================
// EXPORTAÇÕES PARA COMPATIBILIDADE
// ============================================================================

export const userService = {
  getCurrentUser: () => apiService.getCurrentUser(),
  updateSettings: (settings: any) => apiService.updateUserSettings(settings),
  getSettings: () => apiService.getUserSettings(),
};

export const authService = {
  login: (credentials: LoginRequest) => apiService.login(credentials),
  register: (userData: RegisterRequest) => apiService.register(userData),
  logout: () => apiService.logout(),
  isAuthenticated: () => apiService.isAuthenticated(),
};

// ============================================================================
// VIDEO EDITOR SERVICE
// ============================================================================

class VideoEditorService {
  private apiService: ApiService;

  constructor() {
    this.apiService = new ApiService();
  }

  async getAssetCategories(): Promise<any[]> {
    try {
      const response = await this.apiService.http.get('/api/assets/categories');
      return response.data.data || [];
    } catch (error) {
      console.error('Erro ao buscar categorias de assets:', error);
      return [];
    }
  }

  async uploadAsset(file: File): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.apiService.http.post(
        '/api/assets/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data.data;
    } catch (error) {
      throw new Error('Erro ao fazer upload do asset');
    }
  }

  async deleteAsset(assetId: string): Promise<void> {
    try {
      await this.apiService.http.delete(`/api/assets/${assetId}`);
    } catch (error) {
      throw new Error('Erro ao deletar asset');
    }
  }

  async renderVideo(renderData: RenderRequest): Promise<{ renderId: string }> {
    try {
      const response = await this.apiService.http.post(
        '/api/render',
        renderData
      );
      return response.data.data;
    } catch (error) {
      throw new Error('Erro ao iniciar renderização');
    }
  }
}

export default apiService;
