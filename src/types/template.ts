/**
 * Tipos TypeScript para Sistema de Templates de Cena
 * TecnoCursos AI - Editor de Vídeo
 */

// Tipos básicos de elementos que podem ser inseridos em um template
export interface TemplateTextElement {
  type: 'text'
  id: string
  content: string
  position: { x: number; y: number }
  style: {
    fontSize: number
    fontFamily: string
    color: string
    fontWeight: 'normal' | 'bold' | 'lighter'
    textAlign: 'left' | 'center' | 'right'
    textShadow?: string
    animation?: string
  }
  editable: boolean // Se o usuário pode editar este elemento
}

export interface TemplateImageElement {
  type: 'image'
  id: string
  src: string // URL da imagem ou caminho
  position: { x: number; y: number }
  size: { width: number; height: number }
  style: {
    opacity: number
    borderRadius: number
    filter?: string // CSS filters como blur, brightness, etc
    animation?: string
  }
  editable: boolean
}

export interface TemplateAvatarElement {
  type: 'avatar'
  id: string
  avatarType: 'male' | 'female' | 'robot' | 'custom'
  position: { x: number; y: number }
  size: { width: number; height: number }
  style: {
    animation?: string
    expression?: 'neutral' | 'happy' | 'serious' | 'excited'
  }
  speech?: {
    text: string
    voice: 'male' | 'female' | 'robotic'
    duration: number
  }
  editable: boolean
}

export interface TemplateEffectElement {
  type: 'effect'
  id: string
  effectType: 'particles' | 'glow' | 'shake' | 'zoom' | 'fade' | 'slide'
  position?: { x: number; y: number }
  properties: {
    duration: number
    intensity: number
    color?: string
    direction?: 'up' | 'down' | 'left' | 'right'
  }
}

// União de todos os tipos de elementos
export type TemplateElement = TemplateTextElement | TemplateImageElement | TemplateAvatarElement | TemplateEffectElement

// Configuração de background do template
export interface TemplateBackground {
  type: 'color' | 'gradient' | 'image' | 'video'
  value: string // Cor, URL da imagem/vídeo, ou CSS gradient
  overlay?: {
    color: string
    opacity: number
  }
}

// Configuração de áudio do template
export interface TemplateAudio {
  backgroundMusic?: {
    src: string
    volume: number
    loop: boolean
  }
  soundEffects?: Array<{
    id: string
    src: string
    trigger: 'start' | 'middle' | 'end' | number // Momento em segundos
    volume: number
  }>
}

// Definição completa de um template
export interface SceneTemplate {
  id: string
  name: string
  category: TemplateCategory
  description: string
  thumbnail: string // URL da imagem de preview
  
  // Configurações da cena
  duration: number // Duração em segundos
  background: TemplateBackground
  elements: TemplateElement[]
  audio?: TemplateAudio
  
  // Metadados
  tags: string[]
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  createdAt: Date
  updatedAt: Date
  
  // Configurações de aplicação
  replaceable: {
    // IDs de elementos que devem ser substituídos por conteúdo do usuário
    title?: string // ID do elemento de título principal
    subtitle?: string // ID do elemento de subtítulo
    mainImage?: string // ID da imagem principal
    avatar?: string // ID do avatar
  }
}

// Categorias de templates
export type TemplateCategory = 
  | 'opening' // Abertura de vídeo
  | 'alert' // Alertas e avisos importantes
  | 'checklist' // Listas e checklists
  | 'comparison' // Comparações e vs
  | 'testimonial' // Depoimentos e reviews
  | 'call-to-action' // Chamadas para ação
  | 'closing' // Encerramento de vídeo
  | 'transition' // Transições entre seções
  | 'educational' // Conteúdo educacional
  | 'promotional' // Conteúdo promocional

// Props do componente de galeria de templates
export interface TemplateGalleryProps {
  isOpen: boolean
  onClose: () => void
  onSelectTemplate: (template: SceneTemplate) => void
  category?: TemplateCategory
  searchTerm?: string
  showCategories?: boolean
}

// Props do componente de preview de template
export interface TemplatePreviewProps {
  template: SceneTemplate
  isSelected?: boolean
  onClick: (template: SceneTemplate) => void
  showDetails?: boolean
}

// Configuração para criação de novo template
export interface CreateTemplateConfig {
  name: string
  category: TemplateCategory
  description: string
  basedOnScene?: string // ID de cena existente para usar como base
  elements: Partial<TemplateElement>[]
  background: TemplateBackground
  duration: number
  tags: string[]
}

// Resultado da aplicação de um template
export interface TemplateApplicationResult {
  success: boolean
  sceneId: string
  appliedElements: string[] // IDs dos elementos aplicados
  editableElements: string[] // IDs dos elementos que o usuário pode editar
  message?: string
  errors?: string[]
}

// Hook personalizado para gerenciar templates
export interface UseTemplatesResult {
  templates: SceneTemplate[]
  categories: TemplateCategory[]
  loading: boolean
  error: string | null
  
  // Métodos
  getTemplatesByCategory: (category: TemplateCategory) => SceneTemplate[]
  searchTemplates: (query: string) => SceneTemplate[]
  applyTemplate: (template: SceneTemplate, targetSceneId?: string) => TemplateApplicationResult
  createTemplate: (config: CreateTemplateConfig) => Promise<SceneTemplate>
  deleteTemplate: (templateId: string) => Promise<void>
  refreshTemplates: () => Promise<void>
}

// Estados do sistema de templates
export interface TemplateSystemState {
  isGalleryOpen: boolean
  selectedTemplate: SceneTemplate | null
  previewMode: boolean
  currentCategory: TemplateCategory | 'all'
  searchQuery: string
}

export default SceneTemplate