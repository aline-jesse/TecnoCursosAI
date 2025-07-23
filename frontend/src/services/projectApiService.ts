/**
 * Serviço de API para gerenciamento de projetos
 * Integração completa com FastAPI backend
 * TecnoCursos AI - Dashboard de Projetos
 */

import {
  Project,
  CreateProjectDto,
  UpdateProjectDto,
  ProjectFilters,
  PaginationParams,
  ProjectListResponse,
  ShareProjectDto,
  ShareLink,
  DashboardStats,
  ProjectActivity,
  ProjectEvent,
  ProjectStatus,
  ProjectType,
} from '../types/project';
import { apiService } from './apiService'; // Importando a instância centralizada

/**
 * Classe principal do serviço de API
 */
class ProjectApiService {
  private baseUrl = '/projects';
  private wsConnection: WebSocket | null = null;
  private eventListeners: Map<string, Function[]> = new Map();

  constructor() {
    this.initializeWebSocket();
  }

  /**
   * Buscar lista de projetos com filtros e paginação
   */
  async getProjects(
    filters: ProjectFilters = {},
    pagination: PaginationParams = { page: 1, limit: 12 }
  ): Promise<ProjectListResponse> {
    const queryParams = new URLSearchParams();

    // Parâmetros de paginação
    queryParams.append('page', pagination.page.toString());
    queryParams.append('limit', pagination.limit.toString());

    if (pagination.sortBy) {
      queryParams.append('sort_by', pagination.sortBy.toString());
      queryParams.append('sort_order', pagination.sortOrder || 'desc');
    }

    // Filtros
    if (filters.status?.length) {
      filters.status.forEach((status: ProjectStatus) =>
        queryParams.append('status', status)
      );
    }

    if (filters.type?.length) {
      filters.type.forEach((type: ProjectType) =>
        queryParams.append('type', type)
      );
    }

    if (filters.search) {
      queryParams.append('search', filters.search);
    }

    if (filters.dateFrom) {
      queryParams.append('date_from', filters.dateFrom.toISOString());
    }

    if (filters.dateTo) {
      queryParams.append('date_to', filters.dateTo.toISOString());
    }

    if (filters.tags?.length) {
      filters.tags.forEach((tag: string) => queryParams.append('tags', tag));
    }

    const response = await apiService.http.get<ProjectListResponse>(
      `${this.baseUrl}?${queryParams.toString()}`
    );

    // Converter strings de data para objetos Date
    const projectList = response.data;
    projectList.data = projectList.data.map(this.transformProjectDates);
    return projectList;
  }

  /**
   * Buscar um projeto específico por ID
   */
  async getProject(id: string): Promise<Project> {
    const response = await apiService.http.get<Project>(
      `${this.baseUrl}/${id}`
    );
    const project = response.data;
    return this.transformProjectDates(project);
  }

  /**
   * Criar novo projeto
   */
  async createProject(data: CreateProjectDto): Promise<Project> {
    const response = await apiService.http.post<Project>(this.baseUrl, data);
    const project = response.data;
    return this.transformProjectDates(project);
  }

  /**
   * Atualizar projeto existente
   */
  async updateProject(id: string, data: UpdateProjectDto): Promise<Project> {
    const response = await apiService.http.put<Project>(
      `${this.baseUrl}/${id}`,
      data
    );
    const project = response.data;
    return this.transformProjectDates(project);
  }

  /**
   * Excluir projeto
   */
  async deleteProject(id: string): Promise<void> {
    await apiService.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Duplicar projeto
   */
  async duplicateProject(id: string, newName?: string): Promise<Project> {
    const response = await apiService.http.post<Project>(
      `${this.baseUrl}/${id}/duplicate`,
      { name: newName }
    );
    const project = response.data;
    return this.transformProjectDates(project);
  }

  /**
   * Iniciar renderização de vídeo
   */
  async startRendering(id: string, quality?: any): Promise<Project> {
    const response = await apiService.http.post<Project>(
      `${this.baseUrl}/${id}/render`,
      { quality }
    );
    const project = response.data;
    return this.transformProjectDates(project);
  }

  /**
   * Cancelar renderização
   */
  async cancelRendering(id: string): Promise<Project> {
    const response = await apiService.http.post<Project>(
      `${this.baseUrl}/${id}/render/cancel`
    );
    const project = response.data;
    return this.transformProjectDates(project);
  }

  /**
   * Baixar vídeo gerado
   */
  async downloadVideo(id: string): Promise<Blob> {
    const response = await apiService.http.get<Blob>(
      `${this.baseUrl}/${id}/download`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  }

  /**
   * Obter URL de download direto
   */
  async getDownloadUrl(id: string): Promise<string> {
    const response = await apiService.http.get<{ downloadUrl: string }>(
      `${this.baseUrl}/${id}/download-url`
    );
    return response.data.downloadUrl;
  }

  /**
   * Compartilhar projeto
   */
  async shareProject(id: string, data: ShareProjectDto): Promise<ShareLink> {
    const response = await apiService.http.post<ShareLink>(
      `${this.baseUrl}/${id}/share`,
      data
    );
    const shareLink = response.data;
    return {
      ...shareLink,
      createdAt: new Date(shareLink.createdAt),
      ...(shareLink.expiresAt && { expiresAt: new Date(shareLink.expiresAt) }),
    };
  }

  /**
   * Obter links de compartilhamento de um projeto
   */
  async getShareLinks(id: string): Promise<ShareLink[]> {
    const response = await apiService.http.get<ShareLink[]>(
      `${this.baseUrl}/${id}/shares`
    );
    const links = response.data;
    return links.map((link: ShareLink) => ({
      ...link,
      createdAt: new Date(link.createdAt),
      ...(link.expiresAt && { expiresAt: new Date(link.expiresAt) }),
    }));
  }

  /**
   * Revogar link de compartilhamento
   */
  async revokeShareLink(projectId: string, linkId: string): Promise<void> {
    await apiService.http.delete<void>(
      `${this.baseUrl}/${projectId}/shares/${linkId}`
    );
  }

  /**
   * Obter estatísticas do dashboard
   */
  async getDashboardStats(): Promise<DashboardStats> {
    const response =
      await apiService.http.get<DashboardStats>('/dashboard/stats');
    return response.data;
  }

  /**
   * Obter histórico de atividades de um projeto
   */
  async getProjectActivity(id: string): Promise<ProjectActivity[]> {
    const response = await apiService.http.get<ProjectActivity[]>(
      `${this.baseUrl}/${id}/activity`
    );
    const activities = response.data;
    return activities.map((activity: ProjectActivity) => ({
      ...activity,
      timestamp: new Date(activity.timestamp),
    }));
  }

  /**
   * Exportar projeto para diferentes formatos
   */
  async exportProject(
    id: string,
    format: 'json' | 'zip' | 'pdf'
  ): Promise<Blob> {
    const response = await apiService.http.get<Blob>(
      `${this.baseUrl}/${id}/export?format=${format}`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  /**
   * Obter thumbnail do projeto
   */
  async getProjectThumbnail(id: string): Promise<string> {
    const response = await apiService.http.get<{ thumbnailUrl: string }>(
      `${this.baseUrl}/${id}/thumbnail`
    );
    return response.data.thumbnailUrl;
  }

  /**
   * Gerar preview do projeto
   */
  async generatePreview(id: string): Promise<{ previewUrl: string }> {
    const response = await apiService.http.post<{ previewUrl: string }>(
      `${this.baseUrl}/${id}/preview`
    );
    return response.data;
  }

  /**
   * Utilitário para transformar strings de data em objetos Date
   */
  private transformProjectDates(project: any): Project {
    return {
      ...project,
      createdAt: new Date(project.createdAt),
      updatedAt: new Date(project.updatedAt),
      ...(project.completedAt && {
        completedAt: new Date(project.completedAt),
      }),
      ...(project.renderStats?.startTime && {
        renderStats: {
          ...project.renderStats,
          startTime: new Date(project.renderStats.startTime),
          ...(project.renderStats.endTime && {
            endTime: new Date(project.renderStats.endTime),
          }),
        },
      }),
    };
  }

  /**
   * Inicializar conexão WebSocket para updates em tempo real
   */
  private initializeWebSocket(): void {
    try {
      const wsUrl =
        process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/projects';
      const token = localStorage.getItem('authToken');

      this.wsConnection = new WebSocket(
        `${wsUrl}${token ? `?token=${token}` : ''}`
      );

      this.wsConnection.onopen = () => {
        console.log('WebSocket conectado para updates de projetos');
      };

      this.wsConnection.onmessage = event => {
        try {
          const projectEvent: ProjectEvent = JSON.parse(event.data);
          this.handleProjectEvent(projectEvent);
        } catch (error) {
          console.error('Erro ao processar mensagem WebSocket:', error);
        }
      };

      this.wsConnection.onclose = () => {
        console.log('WebSocket desconectado. Tentando reconectar...');
        // Reconectar após 5 segundos
        setTimeout(() => this.initializeWebSocket(), 5000);
      };

      this.wsConnection.onerror = error => {
        console.error('Erro WebSocket:', error);
      };
    } catch (error) {
      console.error('Erro ao inicializar WebSocket:', error);
    }
  }

  /**
   * Processar eventos de projeto via WebSocket
   */
  private handleProjectEvent(event: ProjectEvent): void {
    const listenersForProject = this.eventListeners.get(event.projectId);
    const listenersForAll = this.eventListeners.get('*');

    const allCallbacks = [
      ...(listenersForProject || []),
      ...(listenersForAll || []),
    ];

    allCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('Erro ao executar callback de evento:', error);
      }
    });
  }

  /**
   * Adicionar listener para eventos de projeto
   */
  addEventListener(
    projectId: string | '*',
    callback: (event: ProjectEvent) => void
  ): () => void {
    const currentListeners = this.eventListeners.get(projectId) || [];
    currentListeners.push(callback);
    this.eventListeners.set(projectId, currentListeners);

    // Retorna uma função de cleanup
    return () => this.removeEventListener(projectId, callback);
  }

  /**
   * Remover listener de eventos
   */
  removeEventListener(
    projectId: string | '*',
    callback: (event: ProjectEvent) => void
  ): void {
    const currentListeners = this.eventListeners.get(projectId) || [];
    const index = currentListeners.indexOf(callback);
    if (index > -1) {
      currentListeners.splice(index, 1);
      this.eventListeners.set(projectId, currentListeners);
    }
  }

  /**
   * Fechar conexão WebSocket
   */
  disconnect(): void {
    if (this.wsConnection) {
      this.wsConnection.close();
      this.wsConnection = null;
    }
    this.eventListeners.clear();
  }
}

// Instância singleton do serviço
export const projectApiService = new ProjectApiService();
export default projectApiService;
