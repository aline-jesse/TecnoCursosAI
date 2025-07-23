import { EditorElement, Scene } from './editor';

// ============================================================================
// 🎬 TIPOS COMPARTILHADOS - TECNOCURSOS AI
// ============================================================================

// ============================================================================
// FERRAMENTAS
// ============================================================================

export type ToolType =
  | 'select'
  | 'hand'
  | 'text'
  | 'rectangle'
  | 'circle'
  | 'line'
  | 'image'
  | 'video'
  | 'audio';

export interface ToolConfig {
  id: ToolType;
  icon: string;
  label: string;
  shortcut: string;
  group: 'selection' | 'shapes' | 'media' | 'history' | 'zoom';
}

// ============================================================================
// ESTILOS
// ============================================================================

export interface GradientStop {
  offset: number;
  color: string;
  opacity: number;
}

export interface GradientConfig {
  type: 'linear' | 'radial';
  angle?: number;
  stops: GradientStop[];
}

export interface ShadowConfig {
  color: string;
  offsetX: number;
  offsetY: number;
  blur: number;
  spread: number;
  opacity: number;
}

export interface PatternConfig {
  type: 'dots' | 'lines' | 'grid' | 'crosshatch';
  color: string;
  backgroundColor: string;
  size: number;
  spacing: number;
  angle: number;
  opacity: number;
}

// ============================================================================
// EVENTOS
// ============================================================================

export interface CanvasEventHandlers {
  onElementSelect?: (element: EditorElement | null) => void;
  onElementUpdate?: (element: EditorElement) => void;
  onSceneUpdate?: (scene: Scene) => void;
  onZoomChange?: (zoom: number) => void;
  onToolChange?: (tool: ToolType) => void;
  onHistoryChange?: (canUndo: boolean, canRedo: boolean) => void;
}

// ============================================================================
// CONFIGURAÇÕES
// ============================================================================

export interface EditorConfig {
  width: number;
  height: number;
  backgroundColor: string;
  readOnly: boolean;
  showGrid: boolean;
  gridSize: number;
  snapToGrid: boolean;
  showRulers: boolean;
  showGuides: boolean;
  snapToGuides: boolean;
  theme: 'light' | 'dark' | 'auto';
  language: string;
  shortcuts: Record<string, string>;
}

// ============================================================================
// HISTÓRICO
// ============================================================================

export interface HistoryEntry {
  type: 'add' | 'update' | 'delete' | 'reorder';
  payload: any;
  timestamp: number;
  description: string;
}

export interface HistoryState {
  past: HistoryEntry[];
  present: HistoryEntry | null;
  future: HistoryEntry[];
}

// ============================================================================
// EXPORTAÇÃO
// ============================================================================

export interface ExportConfig {
  format: 'png' | 'jpg' | 'svg' | 'pdf';
  quality: number;
  scale: number;
  background: boolean;
  margin: number;
  includeLayers: string[];
}

export interface ExportResult {
  url: string;
  width: number;
  height: number;
  size: number;
  format: string;
  timestamp: number;
}

// ============================================================================
// IMPORTAÇÃO
// ============================================================================

export interface ImportConfig {
  type: 'file' | 'url' | 'clipboard';
  format: string[];
  maxSize: number;
  validateContent: boolean;
  preprocessContent: boolean;
}

export interface ImportResult {
  success: boolean;
  error?: string;
  data?: any;
  format?: string;
  size?: number;
  timestamp: number;
}

// ============================================================================
// MENSAGENS
// ============================================================================

export interface EditorMessage {
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timeout?: number;
  action?: {
    label: string;
    callback: () => void;
  };
}

// ============================================================================
// ATALHOS
// ============================================================================

export interface ShortcutConfig {
  key: string;
  command: string;
  description: string;
  group: string;
  disabled?: boolean;
  when?: string;
}

// ============================================================================
// TEMAS
// ============================================================================

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  border: string;
  success: string;
  warning: string;
  error: string;
}

export interface ThemeConfig {
  name: string;
  colors: ThemeColors;
  spacing: Record<string, string>;
  typography: Record<string, string>;
  shadows: Record<string, string>;
  transitions: Record<string, string>;
  zIndex: Record<string, number>;
}

// ============================================================================
// PLUGINS
// ============================================================================

export interface PluginConfig {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  enabled: boolean;
  settings: Record<string, any>;
}

export interface PluginAPI {
  registerTool: (tool: ToolConfig) => void;
  registerCommand: (command: string, callback: () => void) => void;
  registerShortcut: (shortcut: ShortcutConfig) => void;
  registerTheme: (theme: ThemeConfig) => void;
  getState: () => any;
  dispatch: (action: any) => void;
}

// ============================================================================
// INTERNACIONALIZAÇÃO
// ============================================================================

export interface LocaleConfig {
  code: string;
  name: string;
  direction: 'ltr' | 'rtl';
  messages: Record<string, string>;
  dateFormat: string;
  timeFormat: string;
  numberFormat: {
    decimal: string;
    thousand: string;
    precision: number;
  };
}

// ============================================================================
// ACESSIBILIDADE
// ============================================================================

export interface AccessibilityConfig {
  announcements: boolean;
  highContrast: boolean;
  reducedMotion: boolean;
  screenReader: boolean;
  keyboardNavigation: boolean;
  focusIndicator: boolean;
  textSize: 'normal' | 'large' | 'xlarge';
}

// ============================================================================
// MÉTRICAS
// ============================================================================

export interface EditorMetrics {
  fps: number;
  memory: {
    used: number;
    total: number;
  };
  elements: {
    total: number;
    visible: number;
    selected: number;
  };
  history: {
    undoSize: number;
    redoSize: number;
  };
  performance: {
    renderTime: number;
    updateTime: number;
  };
}

// ============================================================================
// LOGS
// ============================================================================

export interface EditorLogEntry {
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  timestamp: number;
  context?: Record<string, any>;
  stackTrace?: string;
}

export interface EditorLogger {
  debug: (message: string, context?: Record<string, any>) => void;
  info: (message: string, context?: Record<string, any>) => void;
  warning: (message: string, context?: Record<string, any>) => void;
  error: (
    message: string,
    error?: Error,
    context?: Record<string, any>
  ) => void;
  getEntries: (level?: string, limit?: number) => EditorLogEntry[];
  clear: () => void;
}
