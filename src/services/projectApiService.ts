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
  ProjectEvent
} from '../types/project'

/**
 * Classe principal do serviço de API
 */
class ProjectApiService {
  private baseUrl: string
  private wsConnection: WebSocket | null = null
  private eventListeners: Map<string, Function[]> = new Map()

  constructor() {
    // Configuração da URL base da API
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'
    
    // Inicializar conexão WebSocket para updates em tempo real
    this.initializeWebSocket()
  }

  /**
   * Configuração de headers padrão para requisições
   */
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('authToken')
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    }
  }

  /**
   * Wrapper para requisições HTTP com tratamento de erro
   */
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(
          errorData?.detail || 
          errorData?.message || 
          `HTTP ${response.status}: ${response.statusText}`
        )
      }

      return await response.json()
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error)
      throw error
    }
  }

  /**
   * Buscar lista de projetos com filtros e paginação
   */
  async getProjects(
    filters: ProjectFilters = {},
    pagination: PaginationParams = { page: 1, limit: 12 }
  ): Promise<ProjectListResponse> {
    const queryParams = new URLSearchParams()
    
    // Parâmetros de paginação
    queryParams.append('page', pagination.page.toString())
    queryParams.append('limit', pagination.limit.toString())
    
    if (pagination.sortBy) {
      queryParams.append('sort_by', pagination.sortBy.toString())
      queryParams.append('sort_order', pagination.sortOrder || 'desc')
    }

    // Filtros
    if (filters.status?.length) {
      filters.status.forEach(status => queryParams.append('status', status))
    }
    
    if (filters.type?.length) {
      filters.type.forEach(type => queryParams.append('type', type))
    }
    
    if (filters.search) {
      queryParams.append('search', filters.search)
    }
    
    if (filters.dateFrom) {
      queryParams.append('date_from', filters.dateFrom.toISOString())
    }
    
    if (filters.dateTo) {
      queryParams.append('date_to', filters.dateTo.toISOString())
    }

    if (filters.tags?.length) {
      filters.tags.forEach(tag => queryParams.append('tags', tag))
    }

    const response = await this.request<ProjectListResponse>(
      `/projects?${queryParams.toString()}`
    )

    // Converter strings de data para objetos Date
    response.data = response.data.map(this.transformProjectDates)
    
    return response
  }

  /**
   * Buscar um projeto específico por ID
   */
  async getProject(id: string): Promise<Project> {
    const project = await this.request<Project>(`/projects/${id}`)
    return this.transformProjectDates(project)
  }

  /**
   * Criar novo projeto
   */
  async createProject(data: CreateProjectDto): Promise<Project> {
    const project = await this.request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(data)
    })
    
    return this.transformProjectDates(project)
  }

  /**
   * Atualizar projeto existente
   */
  async updateProject(id: string, data: UpdateProjectDto): Promise<Project> {
    const project = await this.request<Project>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
    
    return this.transformProjectDates(project)
  }

  /**
   * Excluir projeto
   */
  async deleteProject(id: string): Promise<void> {
    await this.request(`/projects/${id}`, {
      method: 'DELETE'
    })
  }

  /**
   * Duplicar projeto
   */
  async duplicateProject(id: string, newName?: string): Promise<Project> {
    const project = await this.request<Project>(`/projects/${id}/duplicate`, {
      method: 'POST',
      body: JSON.stringify({ name: newName })
    })
    
    return this.transformProjectDates(project)
  }

  /**
   * Iniciar renderização de vídeo
   */
  async startRendering(id: string, quality?: any): Promise<Project> {
    const project = await this.request<Project>(`/projects/${id}/render`, {
      method: 'POST',
      body: JSON.stringify({ quality })
    })
    
    return this.transformProjectDates(project)
  }

  /**
   * Cancelar renderização
   */
  async cancelRendering(id: string): Promise<Project> {
    const project = await this.request<Project>(`/projects/${id}/render/cancel`, {
      method: 'POST'
    })
    
    return this.transformProjectDates(project)
  }

  /**
   * Baixar vídeo gerado
   */
  async downloadVideo(id: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/projects/${id}/download`, {
      headers: this.getHeaders()
    })
    
    if (!response.ok) {
      throw new Error(`Erro ao baixar vídeo: ${response.statusText}`)
    }
    
    return await response.blob()
  }

  /**
   * Obter URL de download direto
   */
  async getDownloadUrl(id: string): Promise<string> {
    const response = await this.request<{ downloadUrl: string }>(
      `/projects/${id}/download-url`
    )
    
    return response.downloadUrl
  }

  /**
   * Compartilhar projeto
   */
  async shareProject(id: string, data: ShareProjectDto): Promise<ShareLink> {
    const shareLink = await this.request<ShareLink>(`/projects/${id}/share`, {
      method: 'POST',
      body: JSON.stringify(data)
    })
    
    return {
      ...shareLink,
      createdAt: new Date(shareLink.createdAt),
      ...(shareLink.expiresAt && { expiresAt: new Date(shareLink.expiresAt) })
    }
  }

  /**
   * Obter links de compartilhamento de um projeto
   */
  async getShareLinks(id: string): Promise<ShareLink[]> {
    const links = await this.request<ShareLink[]>(`/projects/${id}/shares`)
    
    return links.map(link => ({
      ...link,
      createdAt: new Date(link.createdAt),
      ...(link.expiresAt && { expiresAt: new Date(link.expiresAt) })
    }))
  }

  /**
   * Revogar link de compartilhamento
   */
  async revokeShareLink(projectId: string, linkId: string): Promise<void> {
    await this.request(`/projects/${projectId}/shares/${linkId}`, {
      method: 'DELETE'
    })
  }

  /**
   * Obter estatísticas do dashboard
   */
  async getDashboardStats(): Promise<DashboardStats> {
    return await this.request<DashboardStats>('/dashboard/stats')
  }

  /**
   * Obter histórico de atividades de um projeto
   */
  async getProjectActivity(id: string): Promise<ProjectActivity[]> {
    const activities = await this.request<ProjectActivity[]>(
      `/projects/${id}/activity`
    )
    
    return activities.map(activity => ({
      ...activity,
      createdAt: new Date(activity.createdAt)
    }))
  }

  /**
   * Exportar projeto para diferentes formatos
   */
  async exportProject(
    id: string, 
    format: 'json' | 'zip' | 'pdf'
  ): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/projects/${id}/export?format=${format}`,
      { headers: this.getHeaders() }
    )
    
    if (!response.ok) {
      throw new Error(`Erro ao exportar projeto: ${response.statusText}`)
    }
    
    return await response.blob()
  }

  /**
   * Obter thumbnail do projeto
   */
  async getProjectThumbnail(id: string): Promise<string> {
    const response = await this.request<{ thumbnailUrl: string }>(
      `/projects/${id}/thumbnail`
    )
    
    return response.thumbnailUrl
  }

  /**
   * Gerar preview do projeto
   */
  async generatePreview(id: string): Promise<{ previewUrl: string }> {
    return await this.request<{ previewUrl: string }>(
      `/projects/${id}/preview`,
      { method: 'POST' }
    )
  }

  /**
   * Utilitário para transformar strings de data em objetos Date
   */
  private transformProjectDates(project: any): Project {
    return {
      ...project,
      createdAt: new Date(project.createdAt),
      updatedAt: new Date(project.updatedAt),
      ...(project.completedAt && { completedAt: new Date(project.completedAt) }),
      ...(project.renderStats?.startTime && {
        renderStats: {
          ...project.renderStats,
          startTime: new Date(project.renderStats.startTime),
          ...(project.renderStats.endTime && {
            endTime: new Date(project.renderStats.endTime)
          })
        }
      })
    }
  }

  /**
   * Inicializar conexão WebSocket para updates em tempo real
   */
  private initializeWebSocket(): void {
    try {
      const wsUrl = (process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws')
      const token = localStorage.getItem('authToken')
      
      this.wsConnection = new WebSocket(`${wsUrl}/projects${token ? `?token=${token}` : ''}`)
      
      this.wsConnection.onopen = () => {
        console.log('WebSocket conectado para updates de projetos')
      }
      
      this.wsConnection.onmessage = (event) => {
        try {
          const projectEvent: ProjectEvent = JSON.parse(event.data)
          this.handleProjectEvent(projectEvent)
        } catch (error) {
          console.error('Erro ao processar mensagem WebSocket:', error)
        }
      }
      
      this.wsConnection.onclose = () => {
        console.log('WebSocket desconectado. Tentando reconectar...')
        // Reconectar após 5 segundos
        setTimeout(() => this.initializeWebSocket(), 5000)
      }
      
      this.wsConnection.onerror = (error) => {
        console.error('Erro WebSocket:', error)
      }
    } catch (error) {
      console.error('Erro ao inicializar WebSocket:', error)
    }
  }

  /**
   * Processar eventos de projeto via WebSocket
   */
  private handleProjectEvent(event: ProjectEvent): void {
    const listenersForProject = this.eventListeners.get(event.projectId)
    const listenersForAll = this.eventListeners.get('*')
    
    const allCallbacks = [
      ...(listenersForProject || []),
      ...(listenersForAll || [])
    ]
    
    allCallbacks.forEach(callback => {
      try {
        callback(event)
      } catch (error) {
        console.error('Erro ao executar callback de evento:', error)
      }
    })
  }

  /**
   * Adicionar listener para eventos de projeto
   */
  addEventListener(projectId: string | '*', callback: (event: ProjectEvent) => void): void {
    const currentListeners = this.eventListeners.get(projectId) || []
    currentListeners.push(callback)
    this.eventListeners.set(projectId, currentListeners)
  }

  /**
   * Remover listener de eventos
   */
  removeEventListener(projectId: string | '*', callback: (event: ProjectEvent) => void): void {
    const currentListeners = this.eventListeners.get(projectId) || []
    const index = currentListeners.indexOf(callback)
    if (index > -1) {
      currentListeners.splice(index, 1)
      this.eventListeners.set(projectId, currentListeners)
    }
  }

  /**
   * Fechar conexão WebSocket
   */
  disconnect(): void {
    if (this.wsConnection) {
      this.wsConnection.close()
      this.wsConnection = null
    }
    this.eventListeners.clear()
  }
}

// Instância singleton do serviço
export const projectApiService = new ProjectApiService()
export default projectApiService