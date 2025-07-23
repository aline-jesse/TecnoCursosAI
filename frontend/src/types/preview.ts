/**
 * Tipos TypeScript para Sistema de Preview de Vídeo/Cena
 * TecnoCursos AI - Sistema de Preview Avançado
 */

import { Scene } from './editor';

// Estado geral do player
export type PreviewPlayerState =
  | 'playing'
  | 'paused'
  | 'idle'
  | 'loading'
  | 'error';

// Qualidade do preview
export type PreviewQuality = 'low' | 'medium' | 'high' | '4k';

/**
 * Marcador na timeline.
 */
export interface Marker {
  id: string;
  time: number; // em segundos
  label: string;
  color?: string;
  type: 'scene' | 'audio' | 'custom';
}

/**
 * Configuração da timeline.
 */
export interface TimelineState {
  duration: number; // em segundos
  currentTime: number;
  isPlaying: boolean;
  playbackSpeed: number;
  loop: boolean;
  markers: Marker[];
}

/**
 * Estado completo do sistema de preview.
 */
export interface PreviewState {
  scenes: Scene[];
  currentSceneIndex: number;
  timeline: TimelineState;
  playerState: PreviewPlayerState;
  volume: number;
  muted: boolean;
  quality: PreviewQuality;
  isFullscreen: boolean;
  error?: string;
}

/**
 * Ações que podem ser executadas no preview.
 */
export interface PreviewActions {
  play: () => void;
  pause: () => void;
  stop: () => void;
  seek: (time: number) => void;
  setSpeed: (speed: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setQuality: (quality: PreviewQuality) => void;
  nextScene: () => void;
  previousScene: () => void;
  goToScene: (index: number) => void;
  addMarker: (time: number, label: string) => void;
  removeMarker: (markerId: string) => void;
  updateSceneConfig: (sceneIndex: number, config: Partial<Scene>) => void;
  toggleFullscreen: () => void;
  setScenes: (scenes: Scene[]) => void;
}

/**
 * Eventos que podem ser emitidos pelo sistema de preview.
 */
export interface PreviewEvents {
  onTimeUpdate: (callback: (time: number) => void) => () => void;
  onSceneChange: (callback: (sceneIndex: number) => void) => () => void;
  onPlayStateChange: (
    callback: (state: PreviewPlayerState) => void
  ) => () => void;
  onReady: (callback: () => void) => () => void;
  onError: (callback: (error: string) => void) => () => void;
}

/**
 * Configuração inicial para o hook useVideoPreview.
 */
export interface VideoPreviewOptions {
  initialScenes?: Scene[];
  initialSceneIndex?: number;
  initialTime?: number;
  autoplay?: boolean;
  loop?: boolean;
  volume?: number;
  quality?: PreviewQuality;
}

// ============================================================================
// Tipos para Componentes
// ============================================================================

export interface AudioConfig {
  url?: string;
  narrationUrl?: string;
  volume: number;
  narrationVolume: number;
  musicVolume: number;
  startTime: number;
  endTime?: number;
  isNarration: boolean;
  text?: string; // Para narração IA
  fadeIn: number;
  fadeOut: number;
  needsRegeneration?: boolean;
}

export interface TransitionConfig {
  type: 'fade' | 'slide' | 'zoom' | 'none';
  duration: number; // em segundos
  easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
  delay?: number;
}

export interface ScenePreviewConfig {
  scene: Scene;
  playerState: PreviewPlayerState;
  onElementSelect: (elementId: string) => void;
  onElementUpdate: (elementId: string, props: any) => void;
}

export interface PreviewCanvasProps {
  scene: Scene;
  currentTime: number;
  quality: PreviewQuality;
  isPlaying: boolean;
  playerState: PreviewPlayerState;
  onElementSelect: (elementId: string) => void;
  onElementUpdate: (elementId: string, props: any) => void;
  onRender?: (canvas: HTMLCanvasElement) => void;
  onError?: (error: string) => void;
}

export interface PreviewSceneElement {
  id: string;
  type: string;
  [key: string]: any;
}

export interface VideoPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  scenes: Scene[];
  initialSceneIndex?: number;
  onExport: (config: ExportConfig) => void;
  onSave?: (scenes: Scene[]) => Promise<void>;
  onRegenerateNarration: (sceneId: string, text: string) => Promise<string>;
}

export interface ExportConfig {
  format: 'mp4' | 'gif' | 'webm';
  quality: 'low' | 'medium' | 'high';
  resolution: { width: number; height: number };
  fps: number;
  includeAudio: boolean;
  watermark?: {
    enabled: boolean;
    text?: string;
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
    opacity: number;
  };
}

export interface TimelineControlsProps {
  config: TimelineState & { audio?: { waveformData?: any } };
  playerState: PreviewPlayerState & { currentSceneIndex?: number };
  onTimeChange: (time: number) => void;
  onSpeedChange: (speed: number) => void;
  onMarkerAdd?: (time: number, label: string) => void;
  onMarkerRemove?: (markerId: string) => void;
  onSceneSelect?: (sceneIndex: number) => void;
}

export type TimelineMarker = Marker;
