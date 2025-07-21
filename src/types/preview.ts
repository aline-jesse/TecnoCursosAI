/**
 * Tipos TypeScript para Sistema de Preview de Vídeo/Cena
 * TecnoCursos AI - Sistema de Preview Avançado
 */

// Tipos de transições disponíveis entre cenas
export type TransitionType =
  | 'fade'        // Dissolve suave
  | 'slideLeft'   // Deslizar para esquerda
  | 'slideRight'  // Deslizar para direita
  | 'slideUp'     // Deslizar para cima
  | 'slideDown'   // Deslizar para baixo
  | 'zoom'        // Zoom in/out
  | 'rotate'      // Rotação
  | 'flip'        // Virar/espelhar
  | 'none'        // Sem transição

// Tipos de animação para elementos
export type AnimationType =
  | 'fadeIn'
  | 'fadeOut'
  | 'slideInLeft'
  | 'slideInRight'
  | 'slideInUp'
  | 'slideInDown'
  | 'zoomIn'
  | 'zoomOut'
  | 'bounceIn'
  | 'rotateIn'
  | 'none'

// Configuração de transição entre cenas
export interface TransitionConfig {
  type: TransitionType
  duration: number // em segundos
  easing: 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'linear'
  delay?: number
}

// Configuração de áudio da cena
export interface AudioConfig {
  url: string
  volume: number // 0 a 1
  isNarration: boolean // true para narração IA, false para música
  text?: string // texto para narração IA
  startTime: number // tempo de início em segundos
  endTime?: number // tempo de fim em segundos (opcional)
  fadeIn: number // duração do fade in em segundos
  fadeOut: number // duração do fade out em segundos
  waveformData?: number[] // dados para renderizar waveform
}

// Configuração de timeline
export interface TimelineConfig {
  duration: number // duração total em segundos
  currentTime: number
  playbackSpeed: number // 0.5x, 1x, 1.5x, 2x etc
  markers: TimelineMarker[]
  audio?: AudioConfig // configuração de áudio global
}

// Marcador na timeline
export interface TimelineMarker {
  id: string
  time: number // posição em segundos
  label: string
  type: 'scene' | 'transition' | 'audio' | 'custom'
  color?: string
}

// Elemento de cena (texto, imagem, etc)
export interface SceneElement {
  id: string
  type: 'text' | 'image' | 'shape' | 'video' | 'audio' | 'avatar'
  x: number
  y: number
  width: number
  height: number
  rotation: number
  opacity: number
  visible: boolean
  locked: boolean
  
  // Propriedades específicas por tipo
  text?: string
  fontSize?: number
  fontFamily?: string
  fontColor?: string
  backgroundColor?: string
  borderColor?: string
  borderWidth?: number
  src?: string // para imagens e vídeos
  
  // Animações
  animationIn?: AnimationType
  animationOut?: AnimationType
  animationDuration?: number
  animationDelay?: number
}

// Configuração completa de uma cena para preview
export interface ScenePreviewConfig {
  id: string
  name: string
  duration: number // em segundos
  background: {
    type: 'color' | 'image' | 'video'
    value: string // cor hex ou URL
  }
  elements: SceneElement[]
  audio?: AudioConfig
  transition?: TransitionConfig
  thumbnail?: string // URL da miniatura
}

// Estado do player de preview
export interface PreviewPlayerState {
  isPlaying: boolean
  currentTime: number
  totalDuration: number
  currentSceneIndex: number
  playbackSpeed: number
  volume: number
  isMuted: boolean
  isLooping: boolean
  quality: 'low' | 'medium' | 'high' | 'ultra'
}

// Configuração de exportação
export interface ExportConfig {
  format: 'mp4' | 'webm' | 'avi' | 'mov'
  quality: 'low' | 'medium' | 'high' | 'ultra'
  fps: number // frames por segundo
  resolution: {
    width: number
    height: number
  }
  includeAudio: boolean
  startTime?: number // tempo de início para exportação parcial
  endTime?: number // tempo de fim para exportação parcial
  watermark?: {
    enabled: boolean
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center'
    text?: string
    image?: string
    opacity: number
  }
}

// Props do componente VideoPreviewModal
export interface VideoPreviewModalProps {
  isOpen: boolean
  scenes: ScenePreviewConfig[]
  initialSceneIndex?: number
  onClose: () => void
  onSave: (scenes: ScenePreviewConfig[]) => Promise<void>
  onExport: (config: ExportConfig) => Promise<void>
  onRegenerateNarration: (sceneId: string, text: string) => Promise<string>
}

// Props do componente PreviewCanvas
export interface PreviewCanvasProps {
  scene: ScenePreviewConfig
  playerState: PreviewPlayerState
  width?: number
  height?: number
  onElementSelect?: (elementId: string | null) => void
  onElementUpdate?: (elementId: string, updates: Partial<SceneElement>) => void
}

// Props do componente TimelineControls
export interface TimelineControlsProps {
  config: TimelineConfig
  playerState: PreviewPlayerState
  onTimeChange: (time: number) => void
  onSpeedChange: (speed: number) => void
  onMarkerAdd: (time: number, label: string) => void
  onMarkerRemove: (markerId: string) => void
  onSceneSelect: (sceneIndex: number) => void
}

// Resposta do hook useVideoPreview
export interface UseVideoPreviewReturn {
  state: {
    scenes: ScenePreviewConfig[]
    currentSceneIndex: number
    playerState: PreviewPlayerState
    timelineConfig: TimelineConfig
    selectedElementId: string | null
  }
  actions: {
    play: () => void
    pause: () => void
    stop: () => void
    seek: (time: number) => void
    nextScene: () => void
    previousScene: () => void
    goToScene: (index: number) => void
    setSpeed: (speed: number) => void
    setVolume: (volume: number) => void
    toggleMute: () => void
    addMarker: (time: number, label: string) => void
    removeMarker: (markerId: string) => void
    updateScene: (sceneId: string, updates: Partial<ScenePreviewConfig>) => void
    selectElement: (elementId: string | null) => void
    updateElement: (elementId: string, updates: Partial<SceneElement>) => void
  }
  events: {
    onTimeUpdate: (callback: (time: number) => void) => void
    onSceneChange: (callback: (sceneIndex: number) => void) => void
    onPlayStateChange: (callback: (isPlaying: boolean) => void) => void
  }
}

// Tipos para estados de processo
export type ProcessState = 'idle' | 'loading' | 'processing' | 'success' | 'error'

// Interface para notificações do sistema de preview
export interface PreviewNotification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  duration?: number
  action?: {
    label: string
    callback: () => void
  }
}