// src/types/editor.ts

/**
 * Define os tipos de elementos que podem ser adicionados ao canvas.
 */
export type ElementType = 'text' | 'image' | 'character';

/**
 * Propriedades base para todos os elementos do editor.
 */
export interface BaseElement {
  id: string;
  type: ElementType;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  opacity: number;
}

/**
 * Propriedades específicas para elementos de texto.
 */
export interface TextElement extends BaseElement {
  type: 'text';
  text: string;
  fontSize: number;
  fontFamily: string;
  fill: string;
}

/**
 * Propriedades específicas para elementos de imagem.
 */
export interface ImageElement extends BaseElement {
  type: 'image';
  src: string;
}

/**
 * Propriedades específicas para elementos de personagem.
 */
export interface CharacterElement extends BaseElement {
  type: 'character';
  src: string; // URL para o SVG ou imagem do personagem
}

/**
 * União de todos os tipos de elementos possíveis no editor.
 */
export type EditorElement = TextElement | ImageElement | CharacterElement;

/**
 * Define a estrutura de uma cena no vídeo.
 */
export interface Scene {
  id: string;
  name: string;
  duration: number; // em segundos
  elements: EditorElement[];
  thumbnail: string; // URL para a miniatura da cena
}

/**
 * Define os tipos de assets disponíveis no painel.
 */
export type AssetType = 'character' | 'image' | 'audio';

/**
 * Define a estrutura de um asset na biblioteca.
 */
export interface Asset {
  id: string;
  name: string;
  type: AssetType;
  src: string; // URL para o recurso (imagem, svg, áudio)
  thumbnail?: string; // URL para a miniatura do asset
} 