// ============================================================================
// 🎨 TIPOS DO CANVAS - TECNOCURSOS AI
// ============================================================================

// ============================================================================
// TIPOS BÁSICOS
// ============================================================================

export interface Point {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface Bounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Transform {
  translate?: Point;
  scale?: number;
  rotate?: number;
}

// ============================================================================
// ESTILOS
// ============================================================================

export interface LineStyle {
  color: string;
  width: number;
  cap?: CanvasLineCap;
  join?: CanvasLineJoin;
  dash?: number[];
  dashOffset?: number;
}

export interface FillStyle {
  color?: string;
  gradient?: CanvasGradient;
  pattern?: CanvasPattern;
  opacity?: number;
}

export interface ShadowStyle {
  color: string;
  blur: number;
  offsetX: number;
  offsetY: number;
}

// ============================================================================
// GRADIENTES
// ============================================================================

export interface GradientStop {
  offset: number;
  color: string;
}

export interface LinearGradientConfig {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  stops: GradientStop[];
}

export interface RadialGradientConfig {
  x1: number;
  y1: number;
  r1: number;
  x2: number;
  y2: number;
  r2: number;
  stops: GradientStop[];
}

export interface ConicGradientConfig {
  x: number;
  y: number;
  angle: number;
  stops: GradientStop[];
}

// ============================================================================
// PADRÕES
// ============================================================================

export interface PatternConfig {
  image: HTMLImageElement;
  repetition?: 'repeat' | 'repeat-x' | 'repeat-y' | 'no-repeat';
  transform?: DOMMatrix;
}

// ============================================================================
// CLIPPING
// ============================================================================

export interface ClipConfig {
  x: number;
  y: number;
  width: number;
  height: number;
  radius?: number;
}

// ============================================================================
// ANIMAÇÃO
// ============================================================================

export interface AnimationConfig {
  duration: number;
  easing?: (t: number) => number;
  onUpdate?: (progress: number) => void;
  onComplete?: () => void;
}

export interface TransformAnimationConfig extends AnimationConfig {
  startTransform: DOMMatrix;
  endTransform: DOMMatrix;
}

// ============================================================================
// CAMADAS
// ============================================================================

export interface Layer {
  canvas: HTMLCanvasElement;
  context: CanvasRenderingContext2D;
  zIndex: number;
}

export interface LayerOptions {
  zIndex?: number;
  alpha?: boolean;
  willReadFrequently?: boolean;
}

// ============================================================================
// OTIMIZAÇÃO
// ============================================================================

export interface OptimizationConfig {
  devicePixelRatio: number;
  useOffscreenCanvas: boolean;
  batchDrawing: boolean;
  imageCaching: boolean;
  maxFPS: number;
}

// ============================================================================
// EVENTOS
// ============================================================================

export interface CanvasEventHandlers {
  onElementSelect?: (element: any | null) => void;
  onElementUpdate?: (element: any) => void;
  onSceneUpdate?: (scene: any) => void;
}

// ============================================================================
// HISTÓRICO
// ============================================================================

export interface HistoryState {
  past: any[];
  present: any[];
  future: any[];
}

export interface HistoryUpdate {
  type: 'add' | 'update' | 'delete' | 'reorder';
  payload: any;
  timestamp: number;
}

// ============================================================================
// CACHE
// ============================================================================

export interface ImageCache {
  [key: string]: HTMLImageElement;
}

export interface FontCache {
  [key: string]: FontFace;
}

export interface PatternCache {
  [key: string]: CanvasPattern | null;
}

// ============================================================================
// REFS
// ============================================================================

export interface CanvasRef {
  getContext: () => CanvasRenderingContext2D | null;
  getElement: () => HTMLCanvasElement | null;
  redraw: () => void;
  resetTransform: () => void;
  zoomTo: (scale: number) => void;
  rotateTo: (angle: number) => void;
  panTo: (x: number, y: number) => void;
}

// ============================================================================
// PROPS
// ============================================================================

export interface CanvasProps {
  width: number;
  height: number;
  backgroundColor?: string;
  onElementSelect?: (element: any | null) => void;
  onElementUpdate?: (element: any) => void;
  onSceneUpdate?: (scene: any) => void;
}
