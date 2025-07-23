/**
 * Tipos TypeScript para Sistema de Vídeo
 * TecnoCursos AI - Sistema de Preview Avançado
 */

// Tipos de abas do preview
export type PreviewTab =
  | 'preview'
  | 'timing'
  | 'audio'
  | 'transitions'
  | 'export';

// Velocidades de reprodução
export type PlaybackSpeed = 0.5 | 0.75 | 1 | 1.25 | 1.5 | 2;

// Tipos de animação
export type AnimationType =
  | 'none'
  | 'fadeIn'
  | 'slideInLeft'
  | 'slideInRight'
  | 'slideInUp'
  | 'slideInDown'
  | 'zoomIn'
  | 'bounceIn'
  | 'rotateIn';

// Formatos de vídeo
export type VideoFormat = 'mp4' | 'gif' | 'webm';

// Qualidades de vídeo
export type VideoQuality = 'low' | 'medium' | 'high';

// Resolução de vídeo
export interface Resolution {
  width: number;
  height: number;
  label: string;
}

// Elemento de vídeo
export interface VideoElement {
  id: string;
  type: string;
  text?: string;
  src?: string;
  animationIn?: AnimationType;
  animationDuration?: number;
  [key: string]: any;
}

// Re-exportar tipos necessários
export type { Scene } from './editor';
export type { PreviewQuality } from './preview';
