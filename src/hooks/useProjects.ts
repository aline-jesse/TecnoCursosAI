/**
 * Hook personalizado para gerenciamento de projetos
 * TecnoCursos AI - Dashboard de Projetos
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Project,
  ProjectFilters,
  PaginationParams,
  DashboardStats,
  UseProjectsOptions,
  UseProjectsResult,
  UpdateProjectDto,
  ShareProjectDto,
  ShareLink,
  ProjectEvent
} from '../types/project'
import { projectApiService } from '../services/projectApiService'

/**
 * Hook principal para gerenciamento de projetos
 */
export const useProjects = (options: UseProjectsOptions = {}): UseProjectsResult => {
  // Estados
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statistics, setStatistics] = useState<DashboardStats>({
    totalProjects: 0,
    completedProjects: 0,
    processingProjects: 0,
    errorProjects: 0,
    totalVideoTime: 0,
    totalStorageUsed: 0,
    projectsThisMonth: 0,
    mostUsedProjectType: 'video' as any
  })
  
  const [pagination, setPagination] = useState({
    page: options.pagination?.page || 1,
    limit: options.pagination?.limit || 12,
    total: 0,
    totalPages: 0,
    hasNext: false,
    hasPrevious: false
  })

  // Refs para controle
  const filtersRef = useRef<ProjectFilters>(options.filters || {})
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const isLoadingRef = useRef(false)

  /**
   * Carregar projetos da API
   */
  const loadProjects = useCallback(async (
    filters: ProjectFilters = filtersRef.current,
    paginationParams: PaginationParams = {
      page: pagination.page,
      limit: pagination.limit,
      sortBy: options.pagination?.sortBy || 'updatedAt',
      sortOrder: options.pagination?.sortOrder || 'desc'
    },
    append = false
  ) => {
    if (isLoadingRef.current) return
    
    try {
      isLoadingRef.current = true
      setError(null)
      
      if (!append) {
        setLoading(true)
      }

      const response = await projectApiService.getProjects(filters, paginationParams)
      
      if (append) {
        setProjects(prev => [...prev, ...response.data])
      } else {
        setProjects(response.data)
      }
      
      setPagination({
        page: response.page,
        limit: response.limit,
        total: response.total,
        totalPages: response.totalPages,
        hasNext: response.hasNext,
        hasPrevious: response.hasPrevious
      })
      
      // Garantir que as estatísticas estejam completas
      const completeStats: DashboardStats = {
        totalProjects: response.statistics?.totalProjects || response.total || 0,
        completedProjects: response.statistics?.completedProjects || 0,
        processingProjects: response.statistics?.processingProjects || 0,
        errorProjects: response.statistics?.errorProjects || 0,
        totalVideoTime: response.statistics?.totalVideoTime || 0,
        totalStorageUsed: response.statistics?.totalStorageUsed || 0,
        projectsThisMonth: response.statistics?.projectsThisMonth || 0,
        mostUsedProjectType: response.statistics?.mostUsedProjectType || 'video'
      }
      
      setStatistics(completeStats)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar projetos'
      setError(errorMessage)
      console.error('Erro ao carregar projetos:', err)
    } finally {
      setLoading(false)
      isLoadingRef.current = false
    }
  }, [pagination.page, pagination.limit, options.pagination])

  /**
   * Recarregar projetos (refresh)
   */
  const refetch = useCallback(async () => {
    await loadProjects(filtersRef.current, { 
      page: 1, 
      limit: pagination.limit,
      sortBy: options.pagination?.sortBy || 'updatedAt',
      sortOrder: options.pagination?.sortOrder || 'desc'
    })
    setPagination(prev => ({ ...prev, page: 1 }))
  }, [loadProjects, pagination.limit, options.pagination])

  /**
   * Carregar mais projetos (paginação)
   */
  const loadMore = useCallback(async () => {
    if (!pagination.hasNext || loading) return
    
    await loadProjects(
      filtersRef.current,
      { 
        page: pagination.page + 1, 
        limit: pagination.limit,
        sortBy: options.pagination?.sortBy || 'updatedAt',
        sortOrder: options.pagination?.sortOrder || 'desc'
      },
      true
    )
  }, [loadProjects, pagination, loading, options.pagination])

  /**
   * Atualizar projeto
   */
  const updateProject = useCallback(async (id: string, data: UpdateProjectDto) => {
    try {
      const updatedProject = await projectApiService.updateProject(id, data)
      
      setProjects(prev => 
        prev.map(project => 
          project.id === id ? updatedProject : project
        )
      )
      
      return updatedProject
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar projeto'
      setError(errorMessage)
      throw err
    }
  }, [])

  /**
   * Excluir projeto
   */
  const deleteProject = useCallback(async (id: string) => {
    try {
      await projectApiService.deleteProject(id)
      
      setProjects(prev => prev.filter(project => project.id !== id))
      
      // Atualizar estatísticas
      setStatistics(prev => ({
        ...prev,
        totalProjects: prev.totalProjects - 1
      }))
      
      setPagination(prev => ({
        ...prev,
        total: prev.total - 1
      }))
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao excluir projeto'
      setError(errorMessage)
      throw err
    }
  }, [])

  /**
   * Compartilhar projeto
   */
  const shareProject = useCallback(async (id: string, data: ShareProjectDto): Promise<ShareLink> => {
    try {
      const shareLink = await projectApiService.shareProject(id, data)
      
      // Atualizar projeto com informações de compartilhamento
      setProjects(prev =>
        prev.map(project =>
          project.id === id
            ? { ...project, shareableLink: shareLink.url }
            : project
        )
      )
      
      return shareLink
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao compartilhar projeto'
      setError(errorMessage)
      throw err
    }
  }, [])

  /**
   * Baixar vídeo do projeto
   */
  const downloadProject = useCallback(async (id: string) => {
    try {
      const blob = await projectApiService.downloadVideo(id)
      
      // Criar URL temporária e fazer download
      const url = URL.createObjectURL(blob)
      const project = projects.find(p => p.id === id)
      const fileName = `${project?.name || 'projeto'}.mp4`
      
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao baixar projeto'
      setError(errorMessage)
      throw err
    }
  }, [projects])

  /**
   * Aplicar novos filtros
   */
  const applyFilters = useCallback((newFilters: ProjectFilters) => {
    filtersRef.current = newFilters
    setPagination(prev => ({ ...prev, page: 1 }))
    loadProjects(newFilters, { page: 1, limit: pagination.limit })
  }, [loadProjects, pagination.limit])

  /**
   * Limpar filtros
   */
  const clearFilters = useCallback(() => {
    filtersRef.current = {}
    setPagination(prev => ({ ...prev, page: 1 }))
    loadProjects({}, { page: 1, limit: pagination.limit })
  }, [loadProjects, pagination.limit])

  /**
   * Handler para eventos WebSocket
   */
  const handleProjectEvent = useCallback((event: ProjectEvent) => {
    setProjects(prev => 
      prev.map(project => {
        if (project.id === event.projectId) {
          const updatedProject = { ...project }
          
          // Atualizar status
          if (event.data.status) {
            updatedProject.status = event.data.status
          }
          
          // Atualizar progresso de renderização
          if (event.data.progress !== undefined) {
            updatedProject.renderStats = {
              ...updatedProject.renderStats,
              progress: event.data.progress,
              currentStep: event.data.message || updatedProject.renderStats?.currentStep || ''
            }
          }
          
          // Marcar como concluído
          if (event.type === 'COMPLETED') {
            updatedProject.completedAt = new Date()
            if (updatedProject.renderStats) {
              updatedProject.renderStats.endTime = new Date()
            }
          }
          
          return updatedProject
        }
        return project
      })
    )
  }, [])

  // Efeito para carregar projetos inicialmente
  useEffect(() => {
    loadProjects()
  }, []) // Só executa uma vez na montagem

  // Efeito para configurar auto-refresh
  useEffect(() => {
    if (options.autoRefresh && options.refreshInterval) {
      refreshIntervalRef.current = setInterval(() => {
        refetch()
      }, options.refreshInterval)
      
      return () => {
        if (refreshIntervalRef.current) {
          clearInterval(refreshIntervalRef.current)
        }
      }
    }
  }, [options.autoRefresh, options.refreshInterval, refetch])

  // Efeito para configurar WebSocket listeners
  useEffect(() => {
    projectApiService.addEventListener('*', handleProjectEvent)
    
    return () => {
      projectApiService.removeEventListener('*', handleProjectEvent)
    }
  }, [handleProjectEvent])

  // Cleanup
  useEffect(() => {
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
      }
    }
  }, [])

  return {
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
    downloadProject,
    applyFilters,
    clearFilters
  }
}

/**
 * Hook simplificado para um projeto específico
 */
export const useProject = (projectId: string) => {
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadProject = useCallback(async () => {
    if (!projectId) return
    
    try {
      setLoading(true)
      setError(null)
      
      const projectData = await projectApiService.getProject(projectId)
      setProject(projectData)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar projeto'
      setError(errorMessage)
      console.error('Erro ao carregar projeto:', err)
    } finally {
      setLoading(false)
    }
  }, [projectId])

  const updateProject = useCallback(async (data: UpdateProjectDto) => {
    if (!projectId) return
    
    try {
      const updatedProject = await projectApiService.updateProject(projectId, data)
      setProject(updatedProject)
      return updatedProject
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar projeto'
      setError(errorMessage)
      throw err
    }
  }, [projectId])

  useEffect(() => {
    loadProject()
  }, [loadProject])

  // Listener para eventos WebSocket específicos do projeto
  useEffect(() => {
    if (!projectId) return

    const handleEvent = (event: ProjectEvent) => {
      setProject(prev => {
        if (!prev || prev.id !== event.projectId) return prev
        
        return {
          ...prev,
          ...(event.data.status && { status: event.data.status }),
          ...(event.data.progress !== undefined && {
            renderStats: {
              ...prev.renderStats,
              progress: event.data.progress,
              currentStep: event.data.message || prev.renderStats?.currentStep || ''
            }
          }),
          ...(event.type === 'COMPLETED' && { completedAt: new Date() })
        }
      })
    }

    projectApiService.addEventListener(projectId, handleEvent)
    
    return () => {
      projectApiService.removeEventListener(projectId, handleEvent)
    }
  }, [projectId])

  return {
    project,
    loading,
    error,
    refetch: loadProject,
    updateProject
  }
}

export default useProjects