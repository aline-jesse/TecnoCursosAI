/**
 * Componente ProjectDashboard
 * Dashboard principal para gerenciamento de projetos
 * TecnoCursos AI - Sistema de Gerenciamento de Projetos
 */

import {
  ArrowPathIcon,
  ChartBarIcon,
  DocumentArrowDownIcon,
  FunnelIcon,
  ListBulletIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  Squares2X2Icon,
} from '@heroicons/react/24/outline';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useProjects } from '../hooks/useProjects';
import {
  DashboardProps,
  Project,
  ProjectFilters,
  ProjectStatistics,
  ProjectStatus,
  ProjectType,
  ShareProjectDto,
} from '../types/project';
import { ProjectCard, ProjectCardCompact } from './ProjectCard';
import './ProjectDashboard.css';
import { StatusBadge } from './StatusBadge';

interface StatItem {
  label: string;
  value: number;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  color: 'blue' | 'green' | 'yellow' | 'red';
}

interface DashboardStatsProps {
  statistics: ProjectStatistics;
}

/**
 * Componente de estatísticas do dashboard
 */
const DashboardStats: React.FC<DashboardStatsProps> = ({ statistics }) => {
  const stats: StatItem[] = [
    {
      label: 'Total de Projetos',
      value: statistics.totalProjects,
      icon: Squares2X2Icon,
      color: 'blue',
    },
    {
      label: 'Concluídos',
      value: statistics.completedProjects,
      icon: ChartBarIcon,
      color: 'green',
    },
    {
      label: 'Em Processo',
      value: statistics.processingProjects,
      icon: ArrowPathIcon,
      color: 'yellow',
    },
    {
      label: 'Com Erro',
      value: statistics.errorProjects,
      icon: DocumentArrowDownIcon,
      color: 'red',
    },
  ];

  return (
    <div className="dashboard-stats">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div key={index} className="stat-card">
            <div className="stat-card-content">
              <div className="stat-card-info">
                <p className="stat-card-label">{stat.label}</p>
                <p className="stat-card-value">{stat.value}</p>
              </div>
              <div className={`stat-card-icon bg-${stat.color}-100`}>
                <Icon className={`w-6 h-6 text-${stat.color}-600`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

/**
 * Componente de filtros
 */
interface FiltersPanelProps {
  filters: ProjectFilters;
  onFiltersChange: (filters: ProjectFilters) => void;
  onClearFilters: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

const FiltersPanel: React.FC<FiltersPanelProps> = ({
  filters,
  onFiltersChange,
  onClearFilters,
  isOpen,
  onToggle,
}) => {
  const handleStatusChange = (status: ProjectStatus, checked: boolean) => {
    const newStatuses = checked
      ? [...(filters.status || []), status]
      : (filters.status || []).filter(s => s !== status);

    onFiltersChange({ ...filters, status: newStatuses });
  };

  const handleTypeChange = (type: ProjectType, checked: boolean) => {
    const newTypes = checked
      ? [...(filters.type || []), type]
      : (filters.type || []).filter(t => t !== type);

    onFiltersChange({ ...filters, type: newTypes });
  };

  if (!isOpen) return null;

  return (
    <div className="filters-panel">
      <div className="filters-grid">
        {/* Filtro por Status */}
        <div className="filter-section">
          <h4>Status</h4>
          <div className="filter-options">
            {Object.values(ProjectStatus).map(status => (
              <label key={status} className="filter-option">
                <input
                  type="checkbox"
                  checked={filters.status?.includes(status) || false}
                  onChange={e => handleStatusChange(status, e.target.checked)}
                />
                <span>
                  <StatusBadge status={status} size="sm" />
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Filtro por Tipo */}
        <div className="filter-section">
          <h4>Tipo de Projeto</h4>
          <div className="filter-options">
            {Object.values(ProjectType).map(type => (
              <label key={type} className="filter-option">
                <input
                  type="checkbox"
                  checked={filters.type?.includes(type) || false}
                  onChange={e => handleTypeChange(type, e.target.checked)}
                />
                <span>{type}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Filtro por Data */}
        <div className="filter-section">
          <h4>Período</h4>
          <div className="filter-date">
            <div>
              <label>De:</label>
              <input
                type="date"
                value={
                  filters.dateFrom
                    ? filters.dateFrom.toISOString().split('T')[0]
                    : ''
                }
                onChange={e =>
                  onFiltersChange({
                    ...filters,
                    dateFrom: e.target.value
                      ? new Date(e.target.value)
                      : undefined,
                  })
                }
              />
            </div>
            <div>
              <label>Até:</label>
              <input
                type="date"
                value={
                  filters.dateTo
                    ? filters.dateTo.toISOString().split('T')[0]
                    : ''
                }
                onChange={e =>
                  onFiltersChange({
                    ...filters,
                    dateTo: e.target.value
                      ? new Date(e.target.value)
                      : undefined,
                  })
                }
              />
            </div>
          </div>
        </div>
      </div>

      {/* Ações dos filtros */}
      <div className="filters-actions">
        <button onClick={onClearFilters}>Limpar Filtros</button>
      </div>
    </div>
  );
};

interface ShareModalProps {
  project: Project;
  onShare: (id: string, data: ShareProjectDto) => void;
  onClose: () => void;
}

/**
 * Modal de compartilhamento
 */
const ShareModal: React.FC<ShareModalProps> = ({
  project,
  onShare,
  onClose,
}) => {
  const [isPublic, setIsPublic] = useState(true);
  const [allowDownload, setAllowDownload] = useState(true);
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onShare(project.id, {
      isPublic,
      allowDownload,
      password: password || undefined,
    });
  };

  return (
    <div className="share-modal-overlay">
      <div className="share-modal">
        <h3 className="share-modal-title">Compartilhar Projeto</h3>

        <form onSubmit={handleSubmit} className="share-form">
          <div className="share-option">
            <input
              type="checkbox"
              checked={isPublic}
              onChange={e => setIsPublic(e.target.checked)}
            />
            <span>Tornar público</span>
          </div>

          <div className="share-option">
            <input
              type="checkbox"
              checked={allowDownload}
              onChange={e => setAllowDownload(e.target.checked)}
            />
            <span>Permitir download</span>
          </div>

          <div className="share-password">
            <label>Senha (opcional)</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Digite uma senha"
            />
          </div>

          <div className="share-actions">
            <button type="button" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit">Compartilhar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

/**
 * Componente principal ProjectDashboard
 */
export const ProjectDashboard: React.FC<DashboardProps> = ({
  initialFilters = {},
  showStats = true,
  compactMode = false,
}) => {
  // Estados locais
  const [searchTerm, setSearchTerm] = useState('');
  const [localFilters, setLocalFilters] =
    useState<ProjectFilters>(initialFilters);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [showShareModal, setShowShareModal] = useState(false);

  // Hook de projetos
  const {
    projects,
    loading,
    error,
    pagination,
    statistics,
    refetch,
    loadMore,
    updateProject,
    deleteProject,
    shareProject,
    applyFilters,
    clearFilters,
  } = useProjects({
    filters: { ...localFilters, search: searchTerm },
    pagination: { page: 1, limit: 12, sortBy: 'updatedAt', sortOrder: 'desc' },
    autoRefresh: true,
    refreshInterval: 30000, // 30 segundos
  });

  // Aplicar filtros com debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      applyFilters({ ...localFilters, search: searchTerm });
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, localFilters, applyFilters]);

  // Handlers
  const handleProjectView = useCallback((project: Project) => {
    window.open(`/projects/${project.id}`, '_blank');
  }, []);

  const handleProjectDownload = useCallback(async (project: Project) => {
    if (project.status !== ProjectStatus.COMPLETED || !project.downloadUrl) {
      alert('O projeto ainda não foi finalizado ou não possui vídeo gerado.');
      return;
    }

    try {
      const response = await fetch(project.downloadUrl);
      const blob = await response.blob();

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.name}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erro ao baixar projeto:', error);
      alert('Erro ao baixar o projeto. Tente novamente.');
    }
  }, []);

  const handleProjectShare = useCallback((project: Project) => {
    setSelectedProject(project);
    setShowShareModal(true);
  }, []);

  const handleShareSubmit = useCallback(
    async (id: string, shareData: ShareProjectDto) => {
      try {
        const shareLink = await shareProject(id, shareData);
        await navigator.clipboard.writeText(shareLink.url);
        alert('Link de compartilhamento copiado para a área de transferência!');
        setShowShareModal(false);
        setSelectedProject(null);
      } catch (error) {
        console.error('Erro ao compartilhar projeto:', error);
        alert('Erro ao compartilhar projeto. Tente novamente.');
      }
    },
    [shareProject]
  );

  const handleProjectDelete = useCallback(
    async (project: Project) => {
      try {
        await deleteProject(project.id);
        alert('Projeto excluído com sucesso!');
      } catch (error) {
        console.error('Erro ao excluir projeto:', error);
        alert('Erro ao excluir projeto. Tente novamente.');
      }
    },
    [deleteProject]
  );

  const handleFiltersChange = useCallback((newFilters: ProjectFilters) => {
    setLocalFilters(newFilters);
  }, []);

  const handleClearFilters = useCallback(() => {
    setLocalFilters({});
    setSearchTerm('');
    clearFilters();
  }, [clearFilters]);

  // Contadores para filtros aplicados
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (localFilters.status?.length) count++;
    if (localFilters.type?.length) count++;
    if (localFilters.dateFrom || localFilters.dateTo) count++;
    if (searchTerm) count++;
    return count;
  }, [localFilters, searchTerm]);

  if (error) {
    return (
      <div className="error-state">
        <div className="error-icon">❌</div>
        <h3 className="error-title">Erro ao carregar projetos</h3>
        <p className="error-text">{error}</p>
        <button onClick={refetch}>Tentar Novamente</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Estatísticas */}
      {showStats && <DashboardStats statistics={statistics} />}

      {/* Header com controles */}
      <div className="dashboard-controls">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* Busca */}
          <div className="search-bar">
            <MagnifyingGlassIcon className="search-bar-icon" />
            <input
              type="text"
              placeholder="Buscar projetos..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Filtros */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`filters-button ${showFilters ? 'active' : ''}`}
          >
            <div className="flex items-center gap-2">
              <FunnelIcon className="w-4 h-4" />
              <span>Filtros</span>
              {activeFiltersCount > 0 && (
                <span className="filters-count">{activeFiltersCount}</span>
              )}
            </div>
          </button>
        </div>

        {/* Controles do lado direito */}
        <div className="flex items-center gap-2">
          {/* View mode toggle */}
          <div className="view-mode">
            <button
              onClick={() => setViewMode('grid')}
              className={viewMode === 'grid' ? 'active' : ''}
            >
              <Squares2X2Icon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={viewMode === 'list' ? 'active' : ''}
            >
              <ListBulletIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Refresh */}
          <button
            onClick={refetch}
            disabled={loading}
            className="filters-button"
          >
            <ArrowPathIcon
              className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
            />
          </button>

          {/* Novo projeto */}
          <button
            onClick={() => window.open('/projects/new', '_blank')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <PlusIcon className="w-4 h-4" />
            <span className="hidden sm:inline">Novo Projeto</span>
          </button>
        </div>
      </div>

      {/* Painel de filtros */}
      <FiltersPanel
        filters={localFilters}
        onFiltersChange={handleFiltersChange}
        onClearFilters={handleClearFilters}
        isOpen={showFilters}
        onToggle={() => setShowFilters(!showFilters)}
      />

      {/* Lista de projetos */}
      {loading && projects.length === 0 ? (
        <div className="loading-state">
          <ArrowPathIcon className="loading-spinner" />
          <p className="loading-text">Carregando projetos...</p>
        </div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📁</div>
          <h3 className="empty-state-title">Nenhum projeto encontrado</h3>
          <p className="empty-state-text">
            {activeFiltersCount > 0 ? 'Tente ajustar os filtros ou' : 'Comece'}{' '}
            criando seu primeiro projeto
          </p>
          <button
            onClick={() => window.open('/projects/new', '_blank')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Criar Projeto
          </button>
        </div>
      ) : (
        <div>
          {/* Grid de projetos */}
          <div
            className={viewMode === 'grid' ? 'projects-grid' : 'projects-list'}
          >
            {projects.map(project =>
              viewMode === 'grid' ? (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onView={handleProjectView}
                  onDownload={handleProjectDownload}
                  onShare={handleProjectShare}
                  onDelete={handleProjectDelete}
                  compactMode={compactMode}
                />
              ) : (
                <ProjectCardCompact
                  key={project.id}
                  project={project}
                  onView={handleProjectView}
                  onDownload={handleProjectDownload}
                  onShare={handleProjectShare}
                  onDelete={handleProjectDelete}
                />
              )
            )}
          </div>

          {/* Botão carregar mais */}
          {pagination.hasNext && (
            <div className="load-more">
              <button onClick={loadMore} disabled={loading}>
                {loading ? 'Carregando...' : 'Carregar Mais'}
              </button>
            </div>
          )}

          {/* Informações de paginação */}
          <div className="pagination-info">
            Mostrando {projects.length} de {pagination.total} projetos
          </div>
        </div>
      )}

      {/* Modal de compartilhamento */}
      {showShareModal && selectedProject && (
        <ShareModal
          project={selectedProject}
          onShare={handleShareSubmit}
          onClose={() => {
            setShowShareModal(false);
            setSelectedProject(null);
          }}
        />
      )}
    </div>
  );
};

export default ProjectDashboard;
