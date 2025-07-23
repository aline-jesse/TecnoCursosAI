// src/data/initialData.ts
import { Asset, Scene } from '../types/editor';

export const initialScenes: Scene[] = [
  {
    id: 'scene-1',
    name: 'Cena Inicial',
    duration: 10,
    elements: [],
    background: { type: 'color', value: '#ffffff' },
  },
];

export const initialAssets: Asset[] = [
  {
    id: 'asset-1',
    name: 'Asset Exemplo',
    type: 'image',
    src: '',
    thumbnail: '',
  },
];
