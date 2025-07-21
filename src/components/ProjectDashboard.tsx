/**
 * Componente ProjectDashboard
 * Dashboard principal para gerenciamento de projetos
 * TecnoCursos AI - Sistema de Gerenciamento de Projetos
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
import {
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  Squares2X2Icon,
  ListBulletIcon,
  ChartBarIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline'
import { 
  DashboardProps,
  ProjectFilters,
  ProjectStatus,
  ProjectType,
  Project,
  ShareProjectDto
} from '../types/project'
import { useProjects } from '../hooks/useProjects'
import { ProjectCard, ProjectCardCompact } from './ProjectCard'
import { StatusBadge, StatusSummary } from './StatusBadge'

/**
 * Componente de estatísticas do dashboard
 */
const DashboardStats: React.FC<{ statistics: any }> = ({ statistics }) => {
  const stats = [
    {
      label: 'Total de Projetos',
      value: statistics.totalProjects,
      icon: Squares2X2Icon,
      color: 'blue'
    },
    {
      label: 'Concluídos',
      value: statistics.completedProjects,
      icon: ChartBarIcon,
      color: 'green'
    },
    {
      label: 'Em Processo',
      value: statistics.processingProjects,
      icon: ArrowPathIcon,
      color: 'yellow'
    },
    {
      label: 'Com Erro',
      value: statistics.errorProjects,
      icon: DocumentArrowDownIcon,
      color: 'red'
    }
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <div key={index} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`p-2 rounded-lg bg-${stat.color}-100`}>
                <Icon className={`w-6 h-6 text-${stat.color}-600`} />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

/**
 * Componente de filtros
 */
interface FiltersPanelProps {
  filters: ProjectFilters
  onFiltersChange: (filters: ProjectFilters) => void
  onClearFilters: () => void
  isOpen: boolean
  onToggle: () => void
}

const FiltersPanel: React.FC<FiltersPanelProps> = ({
  filters,
  onFiltersChange,
  onClearFilters,
  isOpen,
  onToggle
}) => {
  const handleStatusChange = (status: ProjectStatus, checked: boolean) => {
    const newStatuses = checked
      ? [...(filters.status || []), status]
      : (filters.status || []).filter(s => s !== status)
    
    onFiltersChange({ ...filters, status: newStatuses })
  }

  const handleTypeChange = (type: ProjectType, checked: boolean) => {
    const newTypes = checked
      ? [...(filters.type || []), type]
      : (filters.type || []).filter(t => t !== type)
    
    onFiltersChange({ ...filters, type: newTypes })
  }

  if (!isOpen) return null

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Filtro por Status */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Status</h4>
          <div className="space-y-2">
            {Object.values(ProjectStatus).map(status => (
              <label key={status} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.status?.includes(status) || false}
                  onChange={(e) => handleStatusChange(status, e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2">
                  <StatusBadge status={status} size="sm" />
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Filtro por Tipo */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Tipo de Projeto</h4>
          <div className="space-y-2">
            {Object.values(ProjectType).map(type => (
              <label key={type} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.type?.includes(type) || false}
                  onChange={(e) => handleTypeChange(type, e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700 capitalize">
                  {type}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Filtro por Data */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Período</h4>
          <div className="space-y-2">
            <div>
              <label className="block text-sm text-gray-600 mb-1">De:</label>
              <input
                type="date"
                value={filters.dateFrom ? filters.dateFrom.toISOString().split('T')[0] : ''}
                onChange={(e) => onFiltersChange({
                  ...filters,
                  dateFrom: e.target.value ? new Date(e.target.value) : undefined
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Até:</label>
              <input
                type="date"
                value={filters.dateTo ? filters.dateTo.toISOString().split('T')[0] : ''}
                onChange={(e) => onFiltersChange({
                  ...filters,
                  dateTo: e.target.value ? new Date(e.target.value) : undefined
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Ações dos filtros */}
      <div className="flex justify-end mt-4 pt-4 border-t border-gray-200">
        <button
          onClick={onClearFilters}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          Limpar Filtros
        </button>
      </div>
    </div>
  )
}

/**
 * Componente principal ProjectDashboard
 */
export const ProjectDashboard: React.FC<DashboardProps> = ({
  initialFilters = {},
  showStats = true,
  compactMode = false
}) => {
  // Estados locais
  const [searchTerm, setSearchTerm] = useState('')
  const [localFilters, setLocalFilters] = useState<ProjectFilters>(initialFilters)
  const [showFilters, setShowFilters] = useState(false)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [showShareModal, setShowShareModal] = useState(false)

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
    clearFilters
  } = useProjects({
    filters: { ...localFilters, search: searchTerm },
    pagination: { page: 1, limit: 12, sortBy: 'updatedAt', sortOrder: 'desc' },
    autoRefresh: true,
    refreshInterval: 30000 // 30 segundos
  })

  // Aplicar filtros com debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      applyFilters({ ...localFilters, search: searchTerm })
    }, 500)

    return () => clearTimeout(timer)
  }, [searchTerm, localFilters, applyFilters])

  // Handlers
  const handleProjectView = useCallback((project: Project) => {
    // Navegar para página de detalhes do projeto
    window.open(`/projects/${project.id}`, '_blank')
  }, [])

  const handleProjectDownload = useCallback(async (project: Project) => {
    if (project.status !== ProjectStatus.COMPLETED || !project.downloadUrl) {
      alert('O projeto ainda não foi finalizado ou não possui vídeo gerado.')
      return
    }

    try {
      // Usar o serviço para baixar o vídeo
      const response = await fetch(project.downloadUrl)
      const blob = await response.blob()
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${project.name}.mp4`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Erro ao baixar projeto:', error)
      alert('Erro ao baixar o projeto. Tente novamente.')
    }
  }, [])

  const handleProjectShare = useCallback((project: Project) => {
    setSelectedProject(project)
    setShowShareModal(true)
  }, [])

  const handleShareSubmit = useCallback(async (shareData: ShareProjectDto) => {
    if (!selectedProject) return

    try {
      const shareLink = await shareProject(selectedProject.id, shareData)
      
      // Copiar link para clipboard
      await navigator.clipboard.writeText(shareLink.url)
      alert('Link de compartilhamento copiado para a área de transferência!')
      
      setShowShareModal(false)
      setSelectedProject(null)
    } catch (error) {
      console.error('Erro ao compartilhar projeto:', error)
      alert('Erro ao compartilhar projeto. Tente novamente.')
    }
  }, [selectedProject, shareProject])

  const handleProjectDelete = useCallback(async (project: Project) => {
    try {
      await deleteProject(project.id)
      alert('Projeto excluído com sucesso!')
    } catch (error) {
      console.error('Erro ao excluir projeto:', error)
      alert('Erro ao excluir projeto. Tente novamente.')
    }
  }, [deleteProject])

  const handleFiltersChange = useCallback((newFilters: ProjectFilters) => {
    setLocalFilters(newFilters)
  }, [])

  const handleClearFilters = useCallback(() => {
    setLocalFilters({})
    setSearchTerm('')
    clearFilters()
  }, [clearFilters])

  // Contadores para filtros aplicados
  const activeFiltersCount = useMemo(() => {
    let count = 0
    if (localFilters.status?.length) count++
    if (localFilters.type?.length) count++
    if (localFilters.dateFrom || localFilters.dateTo) count++
    if (searchTerm) count++
    return count
  }, [localFilters, searchTerm])

  if (error) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-lg mb-2">❌</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Erro ao carregar projetos</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Estatísticas */}
      {showStats && <DashboardStats statistics={statistics} />}

      {/* Header com controles */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* Busca */}
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar projetos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Filtros */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`
              relative px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors
              ${showFilters ? 'bg-gray-50 border-gray-400' : 'bg-white'}
            `}
          >
            <div className="flex items-center gap-2">
              <FunnelIcon className="w-4 h-4" />
              <span className="text-sm">Filtros</span>
              {activeFiltersCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {activeFiltersCount}
                </span>
              )}
            </div>
          </button>
        </div>

        {/* Controles do lado direito */}
        <div className="flex items-center gap-2">
          {/* View mode toggle */}
          <div className="flex border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-gray-100' : 'bg-white'} hover:bg-gray-50 transition-colors`}
            >
              <Squares2X2Icon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 ${viewMode === 'list' ? 'bg-gray-100' : 'bg-white'} hover:bg-gray-50 transition-colors border-l border-gray-300`}
            >
              <ListBulletIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Refresh */}
          <button
            onClick={refetch}
            disabled={loading}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <ArrowPathIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
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
        <div className="min-h-96 flex items-center justify-center">
          <div className="text-center">
            <ArrowPathIcon className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Carregando projetos...</p>
          </div>
        </div>
      ) : projects.length === 0 ? (
        <div className="min-h-96 flex items-center justify-center">
          <div className="text-center">
            <div className="text-gray-400 text-6xl mb-4">📁</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Nenhum projeto encontrado</h3>
            <p className="text-gray-600 mb-4">
              {activeFiltersCount > 0 ? 'Tente ajustar os filtros ou' : 'Comece'} criando seu primeiro projeto
            </p>
            <button
              onClick={() => window.open('/projects/new', '_blank')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Criar Projeto
            </button>
          </div>
        </div>
      ) : (
        <div>
          {/* Grid de projetos */}
          <div className={
            viewMode === 'grid'
              ? `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6`
              : `space-y-4`
          }>
            {projects.map(project => (
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
            ))}
          </div>

          {/* Botão carregar mais */}
          {pagination.hasNext && (
            <div className="flex justify-center mt-8">
              <button
                onClick={loadMore}
                disabled={loading}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                {loading ? 'Carregando...' : 'Carregar Mais'}
              </button>
            </div>
          )}

          {/* Informações de paginação */}
          <div className="flex justify-center mt-4 text-sm text-gray-600">
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
            setShowShareModal(false)
            setSelectedProject(null)
          }}
        />
      )}
    </div>
  )
}

/**
 * Modal de compartilhamento (componente simplificado)
 */
const ShareModal: React.FC<{
  project: Project
  onShare: (data: ShareProjectDto) => void
  onClose: () => void
}> = ({ project, onShare, onClose }) => {
  const [isPublic, setIsPublic] = useState(true)
  const [allowDownload, setAllowDownload] = useState(true)
  const [password, setPassword] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onShare({
      projectId: project.id,
      isPublic,
      allowDownload,
      password: password || undefined
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Compartilhar Projeto</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm">Tornar público</span>
            </label>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={allowDownload}
                onChange={(e) => setAllowDownload(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm">Permitir download</span>
            </label>
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">
              Senha (opcional)
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite uma senha"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Compartilhar
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProjectDashboard