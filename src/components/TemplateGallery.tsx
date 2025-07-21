/**
 * TemplateGallery - Galeria Visual de Templates de Cena
 * TecnoCursos AI - Sistema de Templates
 * 
 * Este componente exibe uma galeria interativa de templates,
 * permitindo preview, filtragem e seleção de templates.
 */

import React, { useState, useMemo, useEffect } from 'react'
import { 
  XMarkIcon, 
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  CheckIcon
} from '@heroicons/react/24/outline'
import { TemplateGalleryProps, SceneTemplate, TemplateCategory } from '../types/template'
import { SCENE_TEMPLATES, TEMPLATE_CATEGORIES, CATEGORY_NAMES, searchTemplates } from '../data/sceneTemplates'
import TemplatePreview from './TemplatePreview'
import './TemplateGallery.css'

/**
 * Componente principal da galeria de templates
 */
const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  isOpen,
  onClose,
  onSelectTemplate,
  category: initialCategory,
  searchTerm: initialSearchTerm = '',
  showCategories = true
}) => {
  // Estados locais
  const [selectedCategory, setSelectedCategory] = useState<TemplateCategory | 'all'>(initialCategory || 'all')
  const [searchQuery, setSearchQuery] = useState(initialSearchTerm)
  const [previewTemplate, setPreviewTemplate] = useState<SceneTemplate | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<SceneTemplate | null>(null)

  // Filtrar templates baseado na categoria e busca
  const filteredTemplates = useMemo(() => {
    let templates = SCENE_TEMPLATES

    // Filtrar por categoria
    if (selectedCategory !== 'all') {
      templates = templates.filter(template => template.category === selectedCategory)
    }

    // Filtrar por busca
    if (searchQuery.trim()) {
      templates = searchTemplates(searchQuery)
      if (selectedCategory !== 'all') {
        templates = templates.filter(template => template.category === selectedCategory)
      }
    }

    return templates
  }, [selectedCategory, searchQuery])

  // Resetar busca quando categoria muda
  useEffect(() => {
    if (initialCategory) {
      setSelectedCategory(initialCategory)
    }
  }, [initialCategory])

  // Handler para seleção de template
  const handleSelectTemplate = (template: SceneTemplate) => {
    setSelectedTemplate(template)
  }

  // Handler para aplicar template selecionado
  const handleApplyTemplate = () => {
    if (selectedTemplate) {
      onSelectTemplate(selectedTemplate)
      onClose()
    }
  }

  // Handler para preview de template
  const handlePreviewTemplate = (template: SceneTemplate) => {
    setPreviewTemplate(template)
  }

  // Não renderiza se não estiver aberto
  if (!isOpen) return null

  return (
    <div className="template-gallery-overlay">
      <div className="template-gallery-modal">
        {/* Header da Galeria */}
        <div className="gallery-header">
          <div className="header-left">
            <h2>Galeria de Templates</h2>
            <p>Escolha um template para começar rapidamente</p>
          </div>
          
          <div className="header-right">
            <button 
              className="close-btn"
              onClick={onClose}
              title="Fechar galeria"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Filtros e Busca */}
        <div className="gallery-filters">
          <div className="search-container">
            <MagnifyingGlassIcon className="w-5 h-5 search-icon" />
            <input
              type="text"
              placeholder="Buscar templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          {showCategories && (
            <div className="category-filters">
              <FunnelIcon className="w-5 h-5 filter-icon" />
              <select 
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value as TemplateCategory | 'all')}
                className="category-select"
              >
                <option value="all">Todas as categorias</option>
                {TEMPLATE_CATEGORIES.map(cat => (
                  <option key={cat} value={cat}>
                    {CATEGORY_NAMES[cat]}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Contador de resultados */}
        <div className="results-info">
          <span>{filteredTemplates.length} template(s) encontrado(s)</span>
          {selectedCategory !== 'all' && (
            <span className="category-tag">
              {CATEGORY_NAMES[selectedCategory as TemplateCategory]}
            </span>
          )}
        </div>

        {/* Grid de Templates */}
        <div className="templates-grid">
          {filteredTemplates.length > 0 ? (
            filteredTemplates.map(template => (
              <div key={template.id} className="template-card-container">
                <TemplatePreview
                  template={template}
                  isSelected={selectedTemplate?.id === template.id}
                  onClick={handleSelectTemplate}
                  showDetails={true}
                />
                
                {/* Botões de ação do template */}
                <div className="template-actions">
                  <button
                    className="preview-btn"
                    onClick={() => handlePreviewTemplate(template)}
                    title="Visualizar template"
                  >
                    <EyeIcon className="w-4 h-4" />
                    Preview
                  </button>
                  
                  {selectedTemplate?.id === template.id && (
                    <button
                      className="select-btn selected"
                      onClick={handleApplyTemplate}
                      title="Aplicar template"
                    >
                      <CheckIcon className="w-4 h-4" />
                      Usar Template
                    </button>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="no-templates">
              <div className="no-templates-content">
                <h3>Nenhum template encontrado</h3>
                <p>
                  {searchQuery 
                    ? `Nenhum template corresponde à busca "${searchQuery}"`
                    : 'Nenhum template disponível nesta categoria'
                  }
                </p>
                <button 
                  className="clear-filters-btn"
                  onClick={() => {
                    setSearchQuery('')
                    setSelectedCategory('all')
                  }}
                >
                  Limpar Filtros
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer com ações */}
        <div className="gallery-footer">
          <div className="footer-info">
            {selectedTemplate && (
              <span>Template selecionado: <strong>{selectedTemplate.name}</strong></span>
            )}
          </div>
          
          <div className="footer-actions">
            <button 
              className="cancel-btn"
              onClick={onClose}
            >
              Cancelar
            </button>
            
            <button 
              className={`apply-btn ${!selectedTemplate ? 'disabled' : ''}`}
              onClick={handleApplyTemplate}
              disabled={!selectedTemplate}
            >
              Aplicar Template
            </button>
          </div>
        </div>
      </div>

      {/* Modal de Preview */}
      {previewTemplate && (
        <div className="preview-overlay" onClick={() => setPreviewTemplate(null)}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <h3>{previewTemplate.name}</h3>
              <button 
                className="close-preview-btn"
                onClick={() => setPreviewTemplate(null)}
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="preview-content">
              <div className="preview-thumbnail">
                <img 
                  src={previewTemplate.thumbnail} 
                  alt={previewTemplate.name}
                  onError={(e) => {
                    // Fallback para imagem padrão se thumbnail não existir
                    (e.target as HTMLImageElement).src = '/templates/default-thumbnail.jpg'
                  }}
                />
              </div>
              
              <div className="preview-details">
                <p className="template-description">
                  {previewTemplate.description}
                </p>
                
                <div className="template-metadata">
                  <div className="metadata-item">
                    <strong>Categoria:</strong> {CATEGORY_NAMES[previewTemplate.category]}
                  </div>
                  <div className="metadata-item">
                    <strong>Duração:</strong> {previewTemplate.duration}s
                  </div>
                  <div className="metadata-item">
                    <strong>Dificuldade:</strong> 
                    <span className={`difficulty ${previewTemplate.difficulty}`}>
                      {previewTemplate.difficulty === 'beginner' ? 'Iniciante' :
                       previewTemplate.difficulty === 'intermediate' ? 'Intermediário' : 'Avançado'}
                    </span>
                  </div>
                </div>
                
                <div className="template-tags">
                  {previewTemplate.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
                
                <div className="elements-count">
                  <strong>Elementos inclusos:</strong>
                  <ul>
                    <li>{previewTemplate.elements.filter(el => el.type === 'text').length} textos</li>
                    <li>{previewTemplate.elements.filter(el => el.type === 'image').length} imagens</li>
                    <li>{previewTemplate.elements.filter(el => el.type === 'avatar').length} avatares</li>
                    <li>{previewTemplate.elements.filter(el => el.type === 'effect').length} efeitos</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="preview-actions">
              <button 
                className="use-template-btn"
                onClick={() => {
                  setSelectedTemplate(previewTemplate)
                  setPreviewTemplate(null)
                }}
              >
                Usar Este Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateGallery