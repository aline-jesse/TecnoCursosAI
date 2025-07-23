// src/types/project.ts

/**
 * Representa o status de um projeto.
 */
export enum ProjectStatus {
  DRAFT = 'draft',
  RENDERING = 'rendering',
  COMPLETED = 'completed',
  ERROR = 'error',
  ARCHIVED = 'archived',
  PROCESSING = 'processing', // Adicionado para consistência
  CANCELLED = 'cancelled', // Adicionado para consistência
}

/**
 * Representa o tipo de um projeto.
 */
export enum ProjectType {
  VIDEO = 'video',
  PRESENTATION = 'presentation',
  ANIMATION = 'animation',
  SOCIAL = 'social',
  TUTORIAL = 'tutorial', // Adicionado para consistência
}

/**
 * Representa estatísticas de renderização.
 */
export interface RenderStats {
  startTime?: Date;
  endTime?: Date;
  durationSeconds?: number;
  status: 'pending' | 'progress' | 'completed' | 'failed';
  progress: number;
  error?: string;
}

/**
 * Representa estatísticas de projetos.
 */
export interface ProjectStatistics {
  totalProjects: number;
  completedProjects: number;
  processingProjects: number;
  errorProjects: number;
  projectsByStatus: Record<ProjectStatus, number>;
  projectsByType: Record<ProjectType, number>;
  averageScenes: number;
  totalDuration: number;
  recentProjects: any[]; // Deveria ser Project[], mas usamos any para evitar problemas com ciclos
}

/**
 * Estrutura principal de um projeto.
 */
export interface Project {
  id: string;
  name: string; // Adicionando a propriedade 'name' que estava faltando
  title: string;
  description?: string;
  status: ProjectStatus;
  type: ProjectType;
  scenes: any[]; // Substituir por `Scene[]` quando definido
  settings: ProjectSettings;
  renderUrl?: string;
  downloadUrl?: string; // Adicionando a propriedade que estava faltando
  thumbnailUrl?: string;
  renderStats?: RenderStats;
  tags?: string[];
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  createdBy: string;
  workspaceId: string;
}

/**
 * Configurações específicas de um projeto.
 */
export interface ProjectSettings {
  resolution: '1080p' | '720p' | '4k';
  aspectRatio: '16:9' | '4:3' | '1:1' | '9:16';
  backgroundColor: string;
  fps: 24 | 30 | 60;
}

/**
 * DTO para criar um novo projeto.
 */
export interface CreateProjectDto
  extends Omit<
    Project,
    | 'id'
    | 'createdAt'
    | 'updatedAt'
    | 'renderStats'
    | 'renderUrl'
    | 'thumbnailUrl'
    | 'completedAt'
    | 'createdBy'
    | 'workspaceId'
  > {
  templateId?: string;
}

/**
 * DTO para atualizar um projeto existente.
 */
export type UpdateProjectDto = Partial<
  Omit<Project, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'workspaceId'>
>;

/**
 * Filtros para buscar projetos.
 */
export interface ProjectFilters {
  status?: ProjectStatus[];
  type?: ProjectType[];
  search?: string;
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
}

/**
 * Parâmetros de paginação para listas.
 */
export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: keyof Project;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Resposta da API para uma lista de projetos.
 */
export interface ProjectListResponse {
  data: Project[];
  total: number;
  page: number;
  limit: number;
  totalPages: number; // Adicionando a propriedade que estava faltando
  hasNext: boolean; // Adicionando a propriedade que estava faltando
  hasPrevious: boolean; // Adicionando a propriedade que estava faltando
  statistics?: DashboardStats;
}

/**
 * Representa um evento de atividade em um projeto (ex: log de auditoria).
 */
export interface ProjectActivity {
  id: string;
  timestamp: Date;
  user: {
    id: string;
    name: string;
    avatarUrl?: string;
  };
  action: string; // Ex: 'element.created', 'scene.deleted'
  details: Record<string, any>;
}

/**
 * Estatísticas para o dashboard.
 */
export interface DashboardStats {
  totalProjects: number;
  completedProjects: number; // Renomeando para consistência
  processingProjects: number; // Adicionando
  errorProjects: number; // Adicionando
  totalVideoTime: number; // Renomeando
  totalStorageUsed: number; // Renomeando
  projectsThisMonth: number; // Adicionando
  mostUsedProjectType: ProjectType; // Adicionando
}

/**
 * DTO para compartilhar um projeto.
 */
export interface ShareProjectDto {
  isPublic: boolean;
  allowDownload: boolean;
  password?: string;
}

/**
 * Props para o componente Dashboard.
 */
export interface DashboardProps {
  projects?: Project[];
  statistics?: DashboardStats;
  loading?: boolean;
  filters?: ProjectFilters;
  initialFilters?: ProjectFilters;
  showStats?: boolean;
  compactMode?: boolean;
  onFilterChange?: (filters: ProjectFilters) => void;
  onProjectSelect?: (project: Project) => void;
  onProjectUpdate?: (id: string, data: UpdateProjectDto) => Promise<void>;
  onProjectDelete?: (id: string) => Promise<void>;
  onProjectShare?: (id: string, data: ShareProjectDto) => Promise<void>;
}

/**
 * Link de compartilhamento gerado.
 */
export interface ShareLink {
  id: string;
  url: string;
  permission: 'view' | 'edit';
  createdAt: Date;
  expiresAt?: Date;
}

/**
 * Representa um evento em tempo real para colaboração.
 */
export interface ProjectEvent {
  type:
    | 'project.updated'
    | 'render.progress'
    | 'render.completed'
    | 'render.failed'
    | 'collaboration.user.joined'
    | 'collaboration.user.left'
    | 'collaboration.element.updated';
  payload: any;
  projectId: string; // ID do projeto relacionado
  source: string; // ID do usuário que originou o evento
}

export interface UseProjectsOptions {
  filters?: ProjectFilters;
  pagination?: PaginationParams;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseProjectsResult {
  projects: Project[];
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  statistics: DashboardStats;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
  updateProject: (id: string, data: UpdateProjectDto) => Promise<Project>;
  deleteProject: (id: string) => Promise<void>;
  shareProject: (id: string, data: ShareProjectDto) => Promise<ShareLink>;
  downloadProject: (id: string) => Promise<void>;
  applyFilters: (filters: ProjectFilters) => void;
  clearFilters: () => void;
}
