/**
 * Tipos TypeScript para projetos e dashboard
 * TecnoCursos AI - Sistema de Gerenciamento de Projetos
 */

// Status possíveis de um projeto
export enum ProjectStatus {
  DRAFT = 'draft',
  PROCESSING = 'processing', 
  RENDERING = 'rendering',
  COMPLETED = 'completed',
  ERROR = 'error',
  CANCELLED = 'cancelled'
}

// Tipo do projeto baseado no conteúdo
export enum ProjectType {
  VIDEO = 'video',
  PRESENTATION = 'presentation',
  ANIMATION = 'animation',
  TUTORIAL = 'tutorial'
}

// Configurações de qualidade do vídeo
export interface VideoQuality {
  resolution: '720p' | '1080p' | '4K'
  fps: 24 | 30 | 60
  bitrate: number
  format: 'mp4' | 'mov' | 'avi'
}

// Metadados do projeto
export interface ProjectMetadata {
  totalDuration: number
  sceneCount: number
  assetCount: number
  videoQuality: VideoQuality
  createdBy: string
  tags: string[]
}

// Estatísticas de renderização
export interface RenderStats {
  startTime?: Date
  endTime?: Date
  duration?: number
  progress: number
  currentStep: string
  estimatedTimeRemaining?: number
}

// Interface principal do projeto
export interface Project {
  id: string
  name: string
  description?: string
  type: ProjectType
  status: ProjectStatus
  
  // Datas
  createdAt: Date
  updatedAt: Date
  completedAt?: Date
  
  // Metadados
  metadata: ProjectMetadata
  
  // Vídeo gerado
  videoUrl?: string
  thumbnailUrl?: string
  shareableLink?: string
  downloadUrl?: string
  
  // Renderização
  renderStats?: RenderStats
  
  // Configurações
  isPublic: boolean
  allowDownload: boolean
  password?: string
}

// Dados para criação de projeto
export interface CreateProjectDto {
  name: string
  description?: string
  type: ProjectType
  metadata?: Partial<ProjectMetadata>
  isPublic?: boolean
  allowDownload?: boolean
}

// Dados para atualização de projeto
export interface UpdateProjectDto {
  name?: string
  description?: string
  status?: ProjectStatus
  metadata?: Partial<ProjectMetadata>
  isPublic?: boolean
  allowDownload?: boolean
  password?: string
}

// Parâmetros de busca/filtro
export interface ProjectFilters {
  status?: ProjectStatus[]
  type?: ProjectType[]
  dateFrom?: Date
  dateTo?: Date
  search?: string
  tags?: string[]
}

// Parâmetros de paginação
export interface PaginationParams {
  page: number
  limit: number
  sortBy?: keyof Project
  sortOrder?: 'asc' | 'desc'
}

// Resposta paginada da API
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
  hasNext: boolean
  hasPrevious: boolean
}

// Resposta da API para lista de projetos
export interface ProjectListResponse extends PaginatedResponse<Project> {
  statistics: DashboardStats
}

// Dados para compartilhamento
export interface ShareProjectDto {
  projectId: string
  isPublic: boolean
  allowDownload: boolean
  password?: string
  expiresAt?: Date
}

// Link de compartilhamento gerado
export interface ShareLink {
  id: string
  projectId: string
  url: string
  shortUrl: string
  isActive: boolean
  viewCount: number
  downloadCount: number
  createdAt: Date
  expiresAt?: Date
}

// Estatísticas do dashboard
export interface DashboardStats {
  totalProjects: number
  completedProjects: number
  processingProjects: number
  errorProjects: number
  totalVideoTime: number // em minutos
  totalStorageUsed: number // em MB
  projectsThisMonth: number
  mostUsedProjectType: ProjectType
}

// Configurações do usuário para projetos
export interface UserProjectSettings {
  defaultVideoQuality: VideoQuality
  autoSave: boolean
  autoBackup: boolean
  defaultProjectType: ProjectType
  maxConcurrentRenders: number
}

// Eventos de WebSocket para atualizações em tempo real
export interface ProjectEvent {
  type: 'STATUS_CHANGE' | 'PROGRESS_UPDATE' | 'COMPLETED' | 'ERROR'
  projectId: string
  data: {
    status?: ProjectStatus
    progress?: number
    message?: string
    error?: string
  }
  timestamp: Date
}

// Histórico de ações no projeto
export interface ProjectActivity {
  id: string
  projectId: string
  action: 'created' | 'updated' | 'rendered' | 'shared' | 'downloaded' | 'deleted'
  description: string
  userId: string
  metadata?: Record<string, any>
  createdAt: Date
}

// Props para componentes
export interface DashboardProps {
  initialFilters?: ProjectFilters
  showStats?: boolean
  compactMode?: boolean
}

export interface ProjectCardProps {
  project: Project
  onView?: (project: Project) => void
  onDownload?: (project: Project) => void
  onShare?: (project: Project) => void
  onDelete?: (project: Project) => void
  showActions?: boolean
  compactMode?: boolean
}

export interface StatusBadgeProps {
  status: ProjectStatus
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
  animate?: boolean
}

// Hooks personalizados types
export interface UseProjectsOptions {
  filters?: ProjectFilters
  pagination?: PaginationParams
  autoRefresh?: boolean
  refreshInterval?: number
}

export interface UseProjectsResult {
  projects: Project[]
  loading: boolean
  error: string | null
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrevious: boolean
  }
  statistics: DashboardStats
  refetch: () => Promise<void>
  loadMore: () => Promise<void>
  updateProject: (id: string, data: UpdateProjectDto) => Promise<Project>
  deleteProject: (id: string) => Promise<void>
  shareProject: (id: string, data: ShareProjectDto) => Promise<ShareLink>
  downloadProject: (id: string) => Promise<void>
  applyFilters: (filters: ProjectFilters) => void
  clearFilters: () => void
}

// Tipos para formulários
export interface ProjectFormData {
  name: string
  description: string
  type: ProjectType
  isPublic: boolean
  allowDownload: boolean
  videoQuality: VideoQuality
  tags: string[]
}

// Validação de formulário
export interface ProjectFormErrors {
  name?: string
  description?: string
  type?: string
  videoQuality?: {
    resolution?: string
    fps?: string
    bitrate?: string
  }
}