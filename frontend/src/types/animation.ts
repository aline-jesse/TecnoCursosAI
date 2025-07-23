/**
 * Tipos TypeScript para Animações
 * TecnoCursos AI - Sistema de Preview Avançado
 */

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

// Configuração de animação
export interface AnimationConfig {
  type: AnimationType;
  duration: number;
  delay?: number;
  easing?: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
}

// Elemento animável
export interface AnimatableElement {
  animation?: AnimationConfig;
}

// Estender os tipos do editor
import { EditorElement } from './editor';

export type AnimatedEditorElement = EditorElement & AnimatableElement;
