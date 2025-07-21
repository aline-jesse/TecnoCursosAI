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
  | 'none';       // Sem transição

// Estado do player de preview
export interface PreviewPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
}

// Configurações de animação para elementos da cena
export interface AnimationConfig {
  type: 'fade' | 'slide' | 'zoom' | 'none';
  duration: number;
  delay: number;
  easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
}

// Configurações de áudio para a cena
export interface AudioConfig {
  narrationUrl?: string;
  backgroundMusicUrl?: string;
  narrationVolume: number;
  musicVolume: number;
  needsRegeneration?: boolean;
}

// Configurações completas de preview da cena
export interface ScenePreviewConfig {
  id: string;
  duration: number;
  transition: TransitionType;
  animations: Record<string, AnimationConfig>;
  audio: AudioConfig;
  elements: Array<{
    id: string;
    type: string;
    animation?: AnimationConfig;
  }>;
}

// Props para o modal de preview
export interface VideoPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  sceneId: string;
  onSave: (config: ScenePreviewConfig) => void;
  onRegenerateNarration: (sceneId: string) => Promise<string>;
}