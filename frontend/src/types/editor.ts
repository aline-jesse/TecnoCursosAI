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

// ============================================================================
// ELEMENTOS DO EDITOR
// ============================================================================

export interface BaseElement {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation?: number;
  scaleX?: number;
  scaleY?: number;
  opacity?: number;
  zIndex?: number;
  content?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  gradient?: GradientConfig;
  shadow?: ShadowConfig;
  pattern?: PatternConfig;
}

export interface TextElement extends BaseElement {
  type: 'text';
  text: string;
  content?: string; // Para compatibilidade
  fontSize: number;
  fontFamily: string;
  fill: string;
  textAlign?: 'left' | 'center' | 'right';
  textBaseline?: 'top' | 'middle' | 'bottom';
  textDecoration?: 'none' | 'underline' | 'line-through';
  fontWeight?: 'normal' | 'bold';
  fontStyle?: 'normal' | 'italic';
  lineHeight?: number;
  letterSpacing?: number;
  wordSpacing?: number;
  textTransform?: 'none' | 'uppercase' | 'lowercase' | 'capitalize';
}

export interface ImageElement extends BaseElement {
  type: 'image';
  src: string;
  objectFit?: 'contain' | 'cover' | 'fill' | 'none';
  objectPosition?: string;
  filter?: string;
  clipPath?: string;
}

export interface CharacterElement extends BaseElement {
  type: 'character';
  src: string;
  animation?: string;
  pose?: string;
  expression?: string;
  direction?: 'left' | 'right';
}

export interface VideoElement extends BaseElement {
  type: 'video';
  src: string;
  currentTime?: number;
  duration?: number;
  volume?: number;
  muted?: boolean;
  loop?: boolean;
  autoplay?: boolean;
  playbackRate?: number;
  filter?: string;
}

export interface AudioElement extends BaseElement {
  type: 'audio';
  src: string;
  content?: string; // Para compatibilidade
  currentTime?: number;
  duration?: number;
  volume?: number;
  muted?: boolean;
  loop?: boolean;
  autoplay?: boolean;
  playbackRate?: number;
  visualizer?: 'none' | 'waveform' | 'frequency';
}

export interface ShapeElement extends BaseElement {
  type: 'shape';
  shapeType: 'rectangle' | 'circle';
  fill: string;
  stroke: string;
  strokeWidth: number;
  content?: string; // Para compatibilidade
  cornerRadius?: number;
  dashArray?: number[];
  lineCap?: 'butt' | 'round' | 'square';
  lineJoin?: 'miter' | 'round' | 'bevel';
}

export type EditorElement =
  | TextElement
  | ImageElement
  | CharacterElement
  | VideoElement
  | AudioElement
  | ShapeElement;

// ============================================================================
// CENAS E FUNDO
// ============================================================================

export interface SceneBackground {
  type: 'color' | 'image' | 'video' | 'gradient';
  value: string;
}

export interface Scene {
  id: string;
  name: string;
  background: SceneBackground;
  elements: EditorElement[];
  duration?: number;
  thumbnail?: string;
  selectedElementId?: string;
  transitions?: {
    in?: string;
    out?: string;
  };
}

// ============================================================================
// ASSETS
// ============================================================================

export type AssetType = 'image' | 'character' | 'audio' | 'video';

export type ToolType = 
  | 'select' 
  | 'hand'
  | 'text' 
  | 'rectangle' 
  | 'circle' 
  | 'line' 
  | 'image' 
  | 'video' 
  | 'audio'
  | 'draw'
  | 'erase';

export interface ToolConfig {
  id: string;
  name: string;
  icon: string;
}

export interface Asset {
  id: string;
  type: AssetType;
  name: string;
  src: string;
  thumbnail?: string;
  metadata?: {
    width?: number;
    height?: number;
    duration?: number;
    format?: string;
  };
}

// ============================================================================
// HISTÓRICO E ESTADO
// ============================================================================

export interface History {
  past: Scene[][];
  present: Scene[];
  future: Scene[][];
}

export interface HistoryUpdate {
  type: 'add' | 'update' | 'delete' | 'reorder';
  payload: any;
  timestamp: number;
}

export interface EditorState {
  scenes: Scene[];
  currentScene: Scene | null;
  currentSceneId: string | null;
  selectedElement: EditorElement | null;
  selectedElementId: string | null;
  draggedAsset: Asset | null;
  clipboard: EditorElement | null;
  history: History;
  assets: Asset[];
  zoom: number;
  isDragging: boolean;
  isPlaying: boolean;
  currentTime: number;
  canvasWidth: number;
  canvasHeight: number;

  // Scene ID management
  setCurrentSceneId: (sceneId: string | null) => void;
  
  // Element selection management
  setSelectedElementId: (id: string | null) => void;

  // Canvas management
  setCanvasSize: (width: number, height: number) => void;

  // Project management
  loadProject: (projectId: string) => Promise<void>;
  saveProject: (projectId?: string) => Promise<any>;

  // Métodos de manipulação de elementos
  addElement: (element: EditorElement) => void;
  updateElement: (element: EditorElement) => void;
  deleteElement: (elementId: string) => void;
  duplicateElement: (elementId: string) => void;
  bringToFront: (elementId: string) => void;
  sendToBack: (elementId: string) => void;
  copyElement: (elementId: string) => void;
  pasteElement: () => void;

  // Métodos de manipulação de cenas
  addScene: (scene: Scene) => void;
  updateScene: (scene: Scene) => void;
  deleteScene: (sceneId: string) => void;
  reorderScenes: (sourceIndex: number, targetIndex: number) => void;

  // Métodos de histórico
  undo: () => void;
  redo: () => void;

  // Métodos de assets
  addAsset: (asset: Asset) => void;
  deleteAsset: (assetId: string) => void;
  updateAsset: (asset: Asset) => void;
  setDraggedAsset: (asset: Asset | null) => void;
}

// ============================================================================
// PROPS E REFS
// ============================================================================

export interface EditorCanvasProps {
  width: number;
  height: number;
  backgroundColor?: string;
  onElementSelect?: (element: EditorElement | null) => void;
  onElementUpdate?: (element: EditorElement) => void;
  onSceneUpdate?: (scene: Scene) => void;
  readOnly?: boolean;
}

export interface CanvasRef {
  getContext: () => CanvasRenderingContext2D | null;
  getElement: () => HTMLCanvasElement | null;
  redraw: () => void;
  resetTransform: () => void;
  zoomTo: (scale: number) => void;
  rotateTo: (angle: number) => void;
  panTo: (x: number, y: number) => void;
}

export interface CanvasObject {
  element: EditorElement;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  transform: {
    rotation: number;
    scaleX: number;
    scaleY: number;
    opacity: number;
  };
}

// ============================================================================
// FABRIC.JS TYPES
// ============================================================================

// Fabric.js types - usando any para compatibilidade
export interface FabricObject extends Record<string, any> {
  data?: {
    id: string;
  };
}

export interface FabricEvent extends Record<string, any> {
  target: FabricObject;
}

export interface FabricCanvas extends Record<string, any> {
  selection: boolean;
  skipTargetFind: boolean;
  selectable: boolean;
  evented: boolean;
}

export interface FabricCanvasOptions extends Record<string, any> {
  width: number;
  height: number;
  backgroundColor: string;
  selection: boolean;
  skipTargetFind: boolean;
  selectable: boolean;
  evented: boolean;
}

export interface FabricPoint extends Record<string, any> {
  x: number;
  y: number;
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
