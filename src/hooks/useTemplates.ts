/**
 * Hook useTemplates - Gerenciamento de Templates de Cena
 * TecnoCursos AI - Sistema de Templates
 * 
 * Este hook gerencia toda a lógica de templates, incluindo aplicação
 * de templates às cenas e integração com o store do editor.
 */

import { useState, useCallback, useEffect } from 'react'
import { 
  UseTemplatesResult, 
  SceneTemplate, 
  TemplateCategory, 
  TemplateApplicationResult,
  CreateTemplateConfig 
} from '../types/template'
import { 
  SCENE_TEMPLATES, 
  TEMPLATE_CATEGORIES, 
  getTemplatesByCategory, 
  searchTemplates as searchTemplatesData,
  getTemplateById 
} from '../data/sceneTemplates'
import { useEditorStore } from '../store/editorStore'

/**
 * Hook principal para gerenciamento de templates
 */
export const useTemplates = (): UseTemplatesResult => {
  // Estados
  const [templates, setTemplates] = useState<SceneTemplate[]>(SCENE_TEMPLATES)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Store do editor para aplicar templates
  const { addScene, updateScene, scenes } = useEditorStore()

  /**
   * Buscar templates por categoria
   */
  const getTemplatesByCategoryCallback = useCallback((category: TemplateCategory) => {
    return getTemplatesByCategory(category)
  }, [])

  /**
   * Buscar templates por texto
   */
  const searchTemplates = useCallback((query: string) => {
    return searchTemplatesData(query)
  }, [])

  /**
   * Aplicar um template a uma cena
   * Esta é a função principal que converte um template em uma cena real
   */
  const applyTemplate = useCallback((
    template: SceneTemplate, 
    targetSceneId?: string
  ): TemplateApplicationResult => {
    try {
      setLoading(true)
      setError(null)

      console.log(`Aplicando template "${template.name}" ${targetSceneId ? `à cena ${targetSceneId}` : 'como nova cena'}`)

      // Converter elementos do template para elementos de cena
      const sceneElements = template.elements.map(element => {
        const baseElement = {
          ...element,
          id: `${element.id}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          originalTemplateId: element.id,
          editable: 'editable' in element ? element.editable : false
        }

        // Converter elementos específicos baseado no tipo
        switch (element.type) {
          case 'text':
            return {
              ...baseElement,
              type: 'text' as const,
              // Manter todas as propriedades do texto
              content: element.content,
              position: { ...element.position },
              style: { ...element.style }
            }

          case 'image':
            return {
              ...baseElement,
              type: 'image' as const,
              src: element.src,
              position: { ...element.position },
              size: { ...element.size },
              style: { ...element.style }
            }

          case 'avatar':
            return {
              ...baseElement,
              type: 'avatar' as const,
              avatarType: element.avatarType,
              position: { ...element.position },
              size: { ...element.size },
              style: { ...element.style },
              speech: element.speech ? { ...element.speech } : undefined
            }

          case 'effect':
            return {
              ...baseElement,
              type: 'effect' as const,
              effectType: element.effectType,
              position: element.position ? { ...element.position } : undefined,
              properties: { ...element.properties }
            }

          default:
            return baseElement
        }
      })

      // Dados da cena baseados no template
      const sceneData = {
        name: template.name,
        duration: template.duration,
        background: {
          type: template.background.type,
          value: template.background.value,
          overlay: template.background.overlay ? { ...template.background.overlay } : undefined
        },
        elements: sceneElements,
        audio: template.audio ? {
          backgroundMusic: template.audio.backgroundMusic ? { ...template.audio.backgroundMusic } : undefined,
          soundEffects: template.audio.soundEffects ? [...template.audio.soundEffects] : undefined
        } : undefined,
        templateId: template.id,
        templateCategory: template.category,
        createdAt: new Date(),
        updatedAt: new Date()
      }

      let sceneId: string
      const appliedElementIds = sceneElements.map(el => el.id)
      const editableElementIds = sceneElements.filter(el => el.editable).map(el => el.id)

      // Aplicar à cena existente ou criar nova
      if (targetSceneId) {
        // Atualizar cena existente
        updateScene(targetSceneId, sceneData)
        sceneId = targetSceneId
        console.log(`Template aplicado à cena existente: ${targetSceneId}`)
      } else {
        // Criar nova cena
        sceneId = `scene-${Date.now()}`
        const sceneWithId = { ...sceneData, id: sceneId }
        addScene(sceneWithId)
        console.log(`Nova cena criada com template: ${sceneId}`)
      }

      return {
        success: true,
        sceneId,
        appliedElements: appliedElementIds,
        editableElements: editableElementIds,
        message: `Template "${template.name}" aplicado com sucesso! ${editableElementIds.length} elementos podem ser editados.`
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao aplicar template'
      setError(errorMessage)
      console.error('Erro ao aplicar template:', err)
      
      return {
        success: false,
        sceneId: '',
        appliedElements: [],
        editableElements: [],
        message: errorMessage,
        errors: [errorMessage]
      }
    } finally {
      setLoading(false)
    }
  }, [addScene, updateScene])

  /**
   * Criar um novo template baseado em uma cena existente
   */
  const createTemplate = useCallback(async (config: CreateTemplateConfig): Promise<SceneTemplate> => {
    try {
      setLoading(true)
      setError(null)

      // Gerar ID único para o novo template
      const templateId = `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

      // Criar o novo template
      const newTemplate: SceneTemplate = {
        id: templateId,
        name: config.name,
        category: config.category,
        description: config.description,
        thumbnail: `/templates/thumbnails/custom-${templateId}.jpg`, // Seria gerado automaticamente
        duration: config.duration,
        background: { ...config.background },
        elements: config.elements as any[], // Cast necessário devido à tipagem parcial
        tags: [...config.tags],
        difficulty: 'intermediate', // Padrão para templates customizados
        createdAt: new Date(),
        updatedAt: new Date(),
        replaceable: {
          // Identificar automaticamente elementos editáveis
          title: config.elements.find(el => el.type === 'text')?.id,
          avatar: config.elements.find(el => el.type === 'avatar')?.id,
          mainImage: config.elements.find(el => el.type === 'image')?.id
        }
      }

      // Adicionar à lista de templates (em uma implementação real, salvaria no servidor)
      setTemplates(prev => [...prev, newTemplate])

      console.log(`Novo template criado: ${newTemplate.name} (${templateId})`)
      return newTemplate

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar template'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Deletar um template
   */
  const deleteTemplate = useCallback(async (templateId: string): Promise<void> => {
    try {
      setLoading(true)
      setError(null)

      // Verificar se é um template padrão (não pode ser deletado)
      const template = getTemplateById(templateId)
      if (template && !templateId.startsWith('custom-')) {
        throw new Error('Templates padrão não podem ser deletados')
      }

      // Remover da lista
      setTemplates(prev => prev.filter(t => t.id !== templateId))
      
      console.log(`Template deletado: ${templateId}`)

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao deletar template'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Recarregar templates (útil para sincronizar com servidor)
   */
  const refreshTemplates = useCallback(async (): Promise<void> => {
    try {
      setLoading(true)
      setError(null)

      // Em uma implementação real, faria fetch do servidor
      // Por enquanto, apenas reseta para os templates padrão
      setTemplates(SCENE_TEMPLATES)
      
      console.log('Templates recarregados')

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao recarregar templates'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    templates,
    categories: TEMPLATE_CATEGORIES,
    loading,
    error,
    getTemplatesByCategory: getTemplatesByCategoryCallback,
    searchTemplates,
    applyTemplate,
    createTemplate,
    deleteTemplate,
    refreshTemplates
  }
}

/**
 * Hook para gerenciar estado da galeria de templates
 */
export const useTemplateGallery = () => {
  const [isGalleryOpen, setIsGalleryOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<SceneTemplate | null>(null)
  const [currentCategory, setCurrentCategory] = useState<TemplateCategory | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const openGallery = useCallback((category?: TemplateCategory) => {
    if (category) {
      setCurrentCategory(category)
    }
    setIsGalleryOpen(true)
  }, [])

  const closeGallery = useCallback(() => {
    setIsGalleryOpen(false)
    setSelectedTemplate(null)
    setSearchQuery('')
  }, [])

  const selectTemplate = useCallback((template: SceneTemplate) => {
    setSelectedTemplate(template)
  }, [])

  return {
    isGalleryOpen,
    selectedTemplate,
    currentCategory,
    searchQuery,
    setCurrentCategory,
    setSearchQuery,
    openGallery,
    closeGallery,
    selectTemplate
  }
}

export default useTemplates