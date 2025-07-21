/**
 * Componente ProjectCard
 * Card individual para cada projeto na dashboard
 * TecnoCursos AI - Dashboard de Projetos
 */

import React, { useState, useCallback } from 'react'
import {
  EyeIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  TrashIcon,
  PlayIcon,
  DocumentDuplicateIcon,
  ClockIcon,
  FilmIcon,
  PhotoIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline'
import { Project, ProjectCardProps, ProjectStatus, ProjectType } from '../types/project'
import { StatusBadge, StatusBadgeWithProgress } from './StatusBadge'
import { formatDistanceToNow, format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

/**
 * Utilitário para formatar duração em minutos/segundos
 */
const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes === 0) {
    return `${remainingSeconds}s`
  }
  
  return `${minutes}m ${remainingSeconds}s`
}

/**
 * Utilitário para formatar tamanho de arquivo
 */
const formatFileSize = (bytes: number): string => {
  const mb = bytes / (1024 * 1024)
  if (mb < 1000) {
    return `${Math.round(mb)} MB`
  }
  return `${(mb / 1024).toFixed(1)} GB`
}

/**
 * Ícones para tipos de projeto
 */
const PROJECT_TYPE_ICONS = {
  [ProjectType.VIDEO]: FilmIcon,
  [ProjectType.PRESENTATION]: PhotoIcon,
  [ProjectType.ANIMATION]: PlayIcon,
  [ProjectType.TUTORIAL]: EyeIcon
}

/**
 * Componente principal ProjectCard
 */
export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onView,
  onDownload,
  onShare,
  onDelete,
  showActions = true,
  compactMode = false
}) => {
  // Estados locais
  const [showDropdown, setShowDropdown] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [imageError, setImageError] = useState(false)

  // Handlers
  const handleView = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    onView?.(project)
  }, [onView, project])

  const handleDownload = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (project.status !== ProjectStatus.COMPLETED || !project.downloadUrl) {
      return
    }
    
    try {
      setIsLoading(true)
      await onDownload?.(project)
    } catch (error) {
      console.error('Erro ao baixar projeto:', error)
    } finally {
      setIsLoading(false)
    }
  }, [onDownload, project])

  const handleShare = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onShare?.(project)
    setShowDropdown(false)
  }, [onShare, project])

  const handleDelete = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (window.confirm(`Tem certeza que deseja excluir o projeto "${project.name}"?`)) {
      onDelete?.(project)
    }
    setShowDropdown(false)
  }, [onDelete, project])

  // Ícone do tipo de projeto
  const TypeIcon = PROJECT_TYPE_ICONS[project.type] || FilmIcon

  // Verificar se pode baixar
  const canDownload = project.status === ProjectStatus.COMPLETED && project.downloadUrl

  // Thumbnail ou placeholder
  const thumbnailUrl = project.thumbnailUrl || '/placeholder-project.jpg'

  return (
    <div className={`
      group relative bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md 
      transition-all duration-200 overflow-hidden cursor-pointer
      ${compactMode ? 'h-32' : 'h-80'}
    `}>
      {/* Thumbnail/Preview */}
      <div className={`
        relative overflow-hidden
        ${compactMode ? 'h-16' : 'h-48'}
      `}>
        {!imageError ? (
          <img
            src={thumbnailUrl}
            alt={project.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <TypeIcon className="w-8 h-8 text-gray-400" />
          </div>
        )}
        
        {/* Overlay com play button */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 flex items-center justify-center">
          <button
            onClick={handleView}
            className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-white bg-opacity-90 rounded-full p-3 hover:bg-opacity-100"
          >
            <EyeIcon className="w-5 h-5 text-gray-700" />
          </button>
        </div>

        {/* Status Badge */}
        <div className="absolute top-2 left-2">
          {project.renderStats && (project.status === ProjectStatus.PROCESSING || project.status === ProjectStatus.RENDERING) ? (
            <StatusBadgeWithProgress
              status={project.status}
              progress={project.renderStats.progress}
              showProgress={true}
              size="sm"
            />
          ) : (
            <StatusBadge 
              status={project.status}
              size="sm"
              showText={!compactMode}
            />
          )}
        </div>

        {/* Menu dropdown */}
        {showActions && (
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div className="relative">
              <button
                onClick={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setShowDropdown(!showDropdown)
                }}
                className="bg-white bg-opacity-90 hover:bg-opacity-100 rounded-full p-2 transition-all duration-200"
              >
                <EllipsisVerticalIcon className="w-4 h-4 text-gray-700" />
              </button>

              {/* Dropdown menu */}
              {showDropdown && (
                <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                  <button
                    onClick={handleView}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <EyeIcon className="w-4 h-4" />
                    Ver detalhes
                  </button>
                  
                  {canDownload && (
                    <button
                      onClick={handleDownload}
                      disabled={isLoading}
                      className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 disabled:opacity-50"
                    >
                      <ArrowDownTrayIcon className="w-4 h-4" />
                      {isLoading ? 'Baixando...' : 'Baixar vídeo'}
                    </button>
                  )}
                  
                  <button
                    onClick={handleShare}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <ShareIcon className="w-4 h-4" />
                    Compartilhar
                  </button>
                  
                  <button
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <DocumentDuplicateIcon className="w-4 h-4" />
                    Duplicar
                  </button>
                  
                  <div className="border-t border-gray-100 my-1" />
                  
                  <button
                    onClick={handleDelete}
                    className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                  >
                    <TrashIcon className="w-4 h-4" />
                    Excluir
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Conteúdo do card */}
      <div className={`p-4 ${compactMode ? 'py-2' : ''}`}>
        {/* Título e descrição */}
        <div className="mb-2">
          <h3 className={`font-semibold text-gray-900 line-clamp-2 ${compactMode ? 'text-sm' : 'text-base'}`}>
            {project.name}
          </h3>
          
          {!compactMode && project.description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {project.description}
            </p>
          )}
        </div>

        {/* Metadados */}
        {!compactMode && (
          <div className="space-y-2 mb-3">
            {/* Tipo e duração */}
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <TypeIcon className="w-4 h-4" />
                <span className="capitalize">{project.type}</span>
              </div>
              
              {project.metadata.totalDuration && (
                <div className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  <span>{formatDuration(project.metadata.totalDuration)}</span>
                </div>
              )}
            </div>

            {/* Estatísticas */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{project.metadata.sceneCount} cenas</span>
              <span>{project.metadata.assetCount} assets</span>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between">
          {/* Data de atualização */}
          <span className="text-xs text-gray-500" title={format(project.updatedAt, 'PPpp', { locale: ptBR })}>
            {formatDistanceToNow(project.updatedAt, { 
              addSuffix: true, 
              locale: ptBR 
            })}
          </span>

          {/* Ações rápidas */}
          {showActions && !compactMode && (
            <div className="flex items-center gap-1">
              {canDownload && (
                <button
                  onClick={handleDownload}
                  disabled={isLoading}
                  className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors duration-200 disabled:opacity-50"
                  title="Baixar vídeo"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                </button>
              )}
              
              <button
                onClick={handleShare}
                className="p-1.5 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors duration-200"
                title="Compartilhar"
              >
                <ShareIcon className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Barra de progresso (se renderizando) */}
        {project.renderStats && (project.status === ProjectStatus.PROCESSING || project.status === ProjectStatus.RENDERING) && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
              <span>{project.renderStats.currentStep}</span>
              <span>{Math.round(project.renderStats.progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${project.renderStats.progress}%` }}
              />
            </div>
            {project.renderStats.estimatedTimeRemaining && (
              <p className="text-xs text-gray-500 mt-1">
                Tempo restante: ~{Math.ceil(project.renderStats.estimatedTimeRemaining / 60)} min
              </p>
            )}
          </div>
        )}
      </div>

      {/* Click overlay para navegação */}
      <div 
        className="absolute inset-0 z-0"
        onClick={handleView}
      />
    </div>
  )
}

/**
 * Componente de card simplificado para listas
 */
export const ProjectCardCompact: React.FC<ProjectCardProps> = (props) => {
  return <ProjectCard {...props} compactMode={true} />
}

export default ProjectCard