// ============================================================================
// 🎬 TIPOS DO EDITOR DE VÍDEO - TECNOCURSOS AI
// ============================================================================

// ============================================================================
// TIPOS BÁSICOS
// ============================================================================

export interface Position {
  x: number;
  y: number;
}

export interface CanvasElement {
  id: string;
  type: 'text' | 'image' | 'video' | 'audio' | 'shape' | 'character';
  position: Position;
  size: Size;
  rotation: number;
  opacity: number;
  zIndex: number;
  visible: boolean;
  locked: boolean;
  data: ElementData;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface CharacterTemplate {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  category: string;
  tags: string[];
  isPublic: boolean;
  downloads: number;
  rating: number;
  createdAt: string;
  updatedAt: string;
}

export interface Size {
  width: number;
  height: number;
}

export interface Color {
  r: number;
  g: number;
  b: number;
  a: number;
}

export interface Font {
  family: string;
  size: number;
  weight: 'normal' | 'bold' | 'lighter' | 'bolder' | number;
  style: 'normal' | 'italic';
  color: Color;
}

// ============================================================================
// ELEMENTOS DE CENA
// ============================================================================

export interface SceneElement {
  id: string;
  type: 'text' | 'image' | 'video' | 'audio' | 'shape' | 'animation';
  position: Position;
  size: Size;
  rotation: number;
  opacity: number;
  zIndex: number;
  visible: boolean;
  locked: boolean;
  data: ElementData;
  effects: Effect[];
  transitions: Transition[];
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface ElementData {
  // Text Element
  text?: string;
  font?: Font;
  alignment?: 'left' | 'center' | 'right' | 'justify';
  lineHeight?: number;
  letterSpacing?: number;
  backgroundColor?: Color;
  padding?: number;
  
  // Media Elements
  url?: string;
  thumbnail?: string;
  duration?: number;
  volume?: number;
  loop?: boolean;
  muted?: boolean;
  
  // Shape Element
  shapeType?: 'rectangle' | 'circle' | 'triangle' | 'polygon';
  fillColor?: Color;
  strokeColor?: Color;
  strokeWidth?: number;
  
  // Animation Element
  animationType?: 'fade' | 'slide' | 'zoom' | 'rotate' | 'bounce';
  animationDuration?: number;
  animationDelay?: number;
  animationEasing?: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
}

export interface Effect {
  id: string;
  type: 'blur' | 'brightness' | 'contrast' | 'saturation' | 'hue' | 'shadow' | 'glow';
  intensity: number;
  parameters: Record<string, any>;
}

export interface Transition {
  id: string;
  type: 'fade' | 'slide' | 'zoom' | 'wipe' | 'dissolve';
  duration: number;
  direction?: 'left' | 'right' | 'up' | 'down';
  easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
}

// ============================================================================
// CENAS
// ============================================================================

export interface Scene {
  id: string;
  name: string;
  duration: number;
  elements: SceneElement[];
  background: Background;
  transitions: Transition[];
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface Background {
  type: 'color' | 'image' | 'video' | 'gradient';
  color?: Color;
  imageUrl?: string;
  videoUrl?: string;
  gradient?: {
    type: 'linear' | 'radial';
    colors: Color[];
    stops: number[];
    angle?: number;
  };
}

// ============================================================================
// PROJETOS
// ============================================================================

export interface Project {
  id: string;
  name: string;
  description: string;
  scenes: Scene[];
  settings: ProjectSettings;
  metadata: Record<string, any>;
  collaborators: Collaborator[];
  tags: string[];
  status: 'draft' | 'published' | 'archived';
  createdAt: string;
  updatedAt: string;
}

export interface ProjectSettings {
  width: number;
  height: number;
  fps: number;
  duration: number;
  backgroundColor: Color;
  aspectRatio: '16:9' | '9:16' | '1:1' | '4:3' | 'custom';
  quality: 'low' | 'medium' | 'high' | 'ultra';
  format: 'mp4' | 'webm' | 'gif' | 'mov';
  audio: {
    enabled: boolean;
    volume: number;
    fadeIn: number;
    fadeOut: number;
  };
  watermark: {
    enabled: boolean;
    url: string;
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';
    opacity: number;
  };
}

export interface Collaborator {
  id: string;
  email: string;
  name: string;
  role: 'viewer' | 'editor' | 'admin';
  permissions: string[];
  joinedAt: string;
}

// ============================================================================
// ASSETS E BIBLIOTECA
// ============================================================================

export interface Asset {
  id: string;
  name: string;
  type: 'image' | 'video' | 'audio' | 'font' | 'template';
  url: string;
  thumbnail?: string;
  size: number;
  duration?: number;
  metadata: AssetMetadata;
  tags: string[];
  category: string;
  isPublic: boolean;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
}

export interface AssetMetadata {
  format: string;
  size: number;
  width?: number;
  height?: number;
  duration?: number;
  bitrate?: number;
  fps?: number;
  channels?: number;
  sampleRate?: number;
  colorSpace?: string;
  compression?: string;
}

export interface AssetLibrary {
  id: string;
  name: string;
  description: string;
  assets: Asset[];
  categories: AssetCategory[];
  tags: string[];
  isPublic: boolean;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
}

export interface AssetCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  assetCount: number;
}

// ============================================================================
// RENDERIZAÇÃO
// ============================================================================

export interface RenderRequest {
  projectId: string;
  settings: RenderSettings;
  priority: 'low' | 'normal' | 'high';
  callbackUrl?: string;
}

export interface RenderSettings {
  quality: 'low' | 'medium' | 'high' | 'ultra';
  format: 'mp4' | 'webm' | 'gif' | 'mov';
  resolution: string;
  fps: number;
  bitrate?: number;
  audio: {
    enabled: boolean;
    codec: 'aac' | 'mp3' | 'opus';
    bitrate: number;
  };
  watermark?: {
    enabled: boolean;
    url: string;
    position: string;
    opacity: number;
  };
}

export interface RenderStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  estimatedTime: number;
  outputUrl?: string;
  error?: string;
  startedAt: string;
  completedAt?: string;
  settings: RenderSettings;
}

// ============================================================================
// ESTADO DO EDITOR
// ============================================================================

export interface EditorState {
  currentProject: Project | null;
  activeSceneId: string | null;
  selectedElementIds: string[];
  zoom: number;
  pan: Position;
  timeline: TimelineState;
  playback: PlaybackState;
  history: HistoryState;
  loading: LoadingState;
  error: string | null;
  autoSave: boolean;
  collaborators: Collaborator[];
  renderStatus: RenderStatus | null;
}

export interface TimelineState {
  currentTime: number;
  duration: number;
  scale: number;
  snapToGrid: boolean;
  gridSize: number;
  showWaveform: boolean;
  showThumbnails: boolean;
}

export interface PlaybackState {
  isPlaying: boolean;
  isPaused: boolean;
  currentTime: number;
  duration: number;
  speed: number;
  loop: boolean;
  muted: boolean;
  volume: number;
}

export interface HistoryState {
  undoStack: EditorAction[];
  redoStack: EditorAction[];
  maxHistorySize: number;
}

export interface LoadingState {
  projects: boolean;
  assets: boolean;
  save: boolean;
  render: boolean;
  export: boolean;
  import: boolean;
  upload: boolean;
  download: boolean;
}

// ============================================================================
// AÇÕES DO EDITOR
// ============================================================================

export interface EditorAction {
  id: string;
  type: string;
  data: any;
  timestamp: number;
  description: string;
}

export type EditorActionType = 
  | 'ADD_ELEMENT'
  | 'REMOVE_ELEMENT'
  | 'UPDATE_ELEMENT'
  | 'MOVE_ELEMENT'
  | 'RESIZE_ELEMENT'
  | 'ADD_SCENE'
  | 'REMOVE_SCENE'
  | 'UPDATE_SCENE'
  | 'REORDER_SCENES'
  | 'UPDATE_PROJECT'
  | 'IMPORT_ASSET'
  | 'DELETE_ASSET';

// ============================================================================
// CONFIGURAÇÕES DO EDITOR
// ============================================================================

export interface EditorConfig {
  autoSave: boolean;
  autoSaveInterval: number;
  maxUndoSteps: number;
  defaultDuration: number;
  defaultFPS: number;
  supportedFormats: string[];
  maxFileSize: number;
  maxProjectSize: number;
  collaboration: {
    enabled: boolean;
    maxCollaborators: number;
    realTimeSync: boolean;
  };
  rendering: {
    maxConcurrentRenders: number;
    defaultQuality: string;
    defaultFormat: string;
  };
}

// ============================================================================
// EVENTOS DO EDITOR
// ============================================================================

export interface EditorEvent {
  type: string;
  data: any;
  timestamp: number;
  source: 'user' | 'system' | 'collaborator';
}

export type EditorEventType = 
  | 'PROJECT_LOADED'
  | 'PROJECT_SAVED'
  | 'SCENE_ADDED'
  | 'SCENE_REMOVED'
  | 'ELEMENT_ADDED'
  | 'ELEMENT_REMOVED'
  | 'ELEMENT_UPDATED'
  | 'SELECTION_CHANGED'
  | 'ZOOM_CHANGED'
  | 'PLAYBACK_STARTED'
  | 'PLAYBACK_STOPPED'
  | 'RENDER_STARTED'
  | 'RENDER_COMPLETED'
  | 'COLLABORATOR_JOINED'
  | 'COLLABORATOR_LEFT';

// ============================================================================
// UTILITÁRIOS
// ============================================================================

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface ExportOptions {
  format: 'json' | 'zip' | 'project';
  includeAssets: boolean;
  includeRenders: boolean;
  compression: boolean;
}

export interface ImportOptions {
  mergeScenes: boolean;
  overwriteAssets: boolean;
  validateProject: boolean;
}

// ============================================================================
// TIPOS DE WEBSOCKET
// ============================================================================

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  userId?: string;
}

export interface CollaborationMessage {
  type: 'cursor_move' | 'selection_change' | 'element_update' | 'scene_change';
  data: any;
  userId: string;
  timestamp: number;
}

// ============================================================================
// TIPOS DE ANÁLISE
// ============================================================================

export interface ProjectAnalytics {
  projectId: string;
  totalScenes: number;
  totalElements: number;
  totalDuration: number;
  assetUsage: Record<string, number>;
  elementTypes: Record<string, number>;
  renderHistory: RenderStatus[];
  collaborationStats: {
    totalCollaborators: number;
    activeCollaborators: number;
    totalEdits: number;
  };
  performance: {
    averageLoadTime: number;
    averageRenderTime: number;
    memoryUsage: number;
  };
}

// ============================================================================
// TIPOS DE TEMPLATE
// ============================================================================

export interface Template {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  category: string;
  tags: string[];
  project: Partial<Project>;
  settings: {
    width: number;
    height: number;
    fps: number;
    duration: number;
  };
  isPublic: boolean;
  downloads: number;
  rating: number;
  createdAt: string;
  updatedAt: string;
}

// ============================================================================
// TIPOS DE NOTIFICAÇÃO
// ============================================================================

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  data?: any;
  timestamp: number;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}

// ============================================================================
// TIPOS DE CONFIGURAÇÃO DO USUÁRIO
// ============================================================================

export interface UserSettings {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
  };
  editor: {
    autoSave: boolean;
    autoSaveInterval: number;
    defaultDuration: number;
    defaultFPS: number;
    showGrid: boolean;
    snapToGrid: boolean;
    gridSize: number;
  };
  rendering: {
    defaultQuality: string;
    defaultFormat: string;
    maxConcurrentRenders: number;
  };
  collaboration: {
    showCursors: boolean;
    showNames: boolean;
    autoAcceptInvites: boolean;
  };
}
