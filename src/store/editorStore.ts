/**
 * Store Zustand para Gerenciamento de Estado Global do Editor
 * TecnoCursos AI - Editor State Management
 * 
 * Este store gerencia:
 * - Lista de cenas (scenes)
 * - Cena ativa (activeScene)
 * - Assets globais (assets)
 * - Seleção atual (selection)
 * - Funções CRUD para cenas e assets
 * - Sincronização de estado
 */

import { create } from 'zustand'
import * as fabric from 'fabric'
import { ScenePreviewConfig } from '../types/preview';

// Declaração de tipos para Fabric.js
declare global {
  interface Window {
    fabric: typeof fabric;
  }
}

// Tipos para o editor
export interface CanvasObject {
  id: string
  type: 'text' | 'image' | 'shape' | 'video' | 'audio'
  fabricObject: fabric.Object
  properties: {
    left: number
    top: number
    width: number
    height: number
    angle: number
    scaleX: number
    scaleY: number
    fill?: string
    stroke?: string
    fontSize?: number
    fontFamily?: string
    text?: string
    src?: string
  }
}

export interface EditorState {
  // Canvas
  canvas: fabric.Canvas | null
  canvasObjects: CanvasObject[]
  selectedObject: CanvasObject | null
  
  // Editor state
  isDrawing: boolean
  isSelecting: boolean
  currentTool: 'select' | 'text' | 'image' | 'shape' | 'draw' | 'eraser'
  
  // Canvas properties
  canvasWidth: number
  canvasHeight: number
  backgroundColor: string
  zoom: number
  
  // History
  history: CanvasObject[][]
  historyIndex: number

  // Scenes and Assets
  scenes: any[]
  assets: any[]
  activeScene: any | null
  selection: { type: string; id?: string; sceneId?: string }
  
  // Preview
  previewConfig: Record<string, ScenePreviewConfig>;
  updatePreviewConfig: (sceneId: string, config: ScenePreviewConfig) => void;

  // Actions
  setCanvas: (canvas: fabric.Canvas) => void
  addObject: (object: CanvasObject) => void
  removeObject: (id: string) => void
  updateObject: (id: string, properties: Partial<CanvasObject['properties']>) => void
  selectObject: (object: CanvasObject | null) => void
  setCurrentTool: (tool: EditorState['currentTool']) => void
  setCanvasSize: (width: number, height: number) => void
  setBackgroundColor: (color: string) => void
  setZoom: (zoom: number) => void
  undo: () => void
  redo: () => void
  saveToHistory: () => void
  clearCanvas: () => void
  exportCanvas: () => string

  // Scene and Asset Actions
  addScene: (scene: any) => void
  updateScene: (id: string, updates: any) => void
  deleteScene: (id: string) => void
  duplicateScene: (id: string) => void
  setActiveScene: (id: string) => void
  reorderScenes: (scenes: any[]) => void
  addAsset: (asset: any) => void
  deleteAsset: (id: string) => void
  addAssetToScene: (assetId: string, sceneId: string) => void
  removeAssetFromScene: (assetId: string, sceneId: string) => void
  setSelection: (selection: { type: string; id?: string; sceneId?: string }) => void
}

// Seletores para facilitar o uso
export const useScenes = () => useEditorStore(state => state.scenes || [])
export const useAssets = () => useEditorStore(state => state.assets || [])
export const useActiveScene = () => useEditorStore(state => state.activeScene)
export const useSelection = () => useEditorStore(state => state.selection || { type: 'none' })
export const useEditor = () => useEditorStore(state => ({
  addScene: state.addScene,
  updateScene: state.updateScene,
  deleteScene: state.deleteScene,
  duplicateScene: state.duplicateScene,
  setActiveScene: state.setActiveScene,
  reorderScenes: state.reorderScenes,
  addAsset: state.addAsset,
  deleteAsset: state.deleteAsset,
  addAssetToScene: state.addAssetToScene,
  removeAssetFromScene: state.removeAssetFromScene,
  setSelection: state.setSelection
}))

export const useEditorStore = create<EditorState>((set, get) => ({
  // Initial state
  canvas: null,
  canvasObjects: [],
  selectedObject: null,
  isDrawing: false,
  isSelecting: false,
  currentTool: 'select',
  canvasWidth: 1920,
  canvasHeight: 1080,
  backgroundColor: '#ffffff',
  zoom: 1,
  history: [],
  historyIndex: -1,

  // Scenes and Assets initial state
  scenes: [
    { id: 'scene-1', name: 'Cena 1', duration: 30, assets: [], background: '#ffffff' },
    { id: 'scene-2', name: 'Cena 2', duration: 45, assets: [], background: '#f0f0f0' }
  ],
  assets: [
    { id: 'asset-1', name: 'Imagem Exemplo', type: 'image', url: '/placeholder-image.jpg', thumbnail: '/placeholder-image.jpg', size: 1024000 }
  ],
  activeScene: null,
  selection: { type: 'none' },

  // Preview
  previewConfig: {},
  
  updatePreviewConfig: (sceneId, config) => set((state) => ({
    previewConfig: {
      ...state.previewConfig,
      [sceneId]: config
    }
  })),

  // Actions
  setCanvas: (canvas) => {
    set({ canvas })
    // Configurar eventos do canvas
    if (canvas) {
      canvas.on('selection:created', (e) => {
        const selected = e.selected?.[0]
        if (selected) {
          const obj = get().canvasObjects.find(o => o.fabricObject === selected)
          set({ selectedObject: obj || null })
        }
      })

      canvas.on('selection:cleared', () => {
        set({ selectedObject: null })
      })

      canvas.on('object:modified', () => {
        get().saveToHistory()
      })
    }
  },

  addObject: (object) => {
    set((state) => {
      const { canvasObjects } = state
      return {
        canvasObjects: [...canvasObjects, object],
        selectedObject: object
      }
    })
    
    const { canvas } = get()
    if (canvas) {
      canvas.add(object.fabricObject)
      canvas.setActiveObject(object.fabricObject)
      canvas.renderAll()
    }
    
    get().saveToHistory()
  },

  removeObject: (id) => {
    set((state) => {
      const { canvasObjects, canvas, selectedObject } = state
      const object = canvasObjects.find(o => o.id === id)
      if (object && canvas) {
        canvas.remove(object.fabricObject)
        canvas.renderAll()
      }
      
      return {
        canvasObjects: canvasObjects.filter(o => o.id !== id),
        selectedObject: selectedObject?.id === id ? null : selectedObject
      }
    })
    
    get().saveToHistory()
  },

  updateObject: (id, properties) => {
    set((state) => {
      const { canvasObjects, canvas, selectedObject } = state
      const objectIndex = canvasObjects.findIndex(o => o.id === id)
      if (objectIndex === -1) return state

      const updatedObjects = [...canvasObjects]
      updatedObjects[objectIndex] = {
        ...updatedObjects[objectIndex],
        properties: { ...updatedObjects[objectIndex].properties, ...properties }
      }

      // Atualizar objeto Fabric
      const { fabricObject } = updatedObjects[objectIndex]
      Object.entries(properties).forEach(([key, value]) => {
        if (fabricObject && key in fabricObject) {
          ;(fabricObject as any)[key] = value
        }
      })

      if (canvas) {
        canvas.renderAll()
      }

      return {
        canvasObjects: updatedObjects,
        selectedObject: selectedObject?.id === id ? updatedObjects[objectIndex] : selectedObject
      }
    })
  },

  selectObject: (object) => {
    set({ selectedObject: object })
    
    const { canvas } = get()
    if (canvas && object) {
      canvas.setActiveObject(object.fabricObject)
      canvas.renderAll()
    } else if (canvas) {
      canvas.discardActiveObject()
      canvas.renderAll()
    }
  },

  setCurrentTool: (tool) => {
    set({ currentTool: tool })
    
    const { canvas } = get()
    if (canvas) {
      canvas.isDrawingMode = tool === 'draw'
      canvas.freeDrawingBrush = tool === 'draw' ? new fabric.PencilBrush(canvas) : undefined
      
      if (tool === 'eraser') {
        canvas.isDrawingMode = true
        canvas.freeDrawingBrush = new fabric.PencilBrush(canvas)
        canvas.freeDrawingBrush.color = 'rgba(255,255,255,1)'
        canvas.freeDrawingBrush.width = 20
      }
    }
  },

  setCanvasSize: (width, height) => {
    set({ canvasWidth: width, canvasHeight: height })
    
    const { canvas } = get()
    if (canvas) {
      canvas.setDimensions({ width, height })
      canvas.renderAll()
    }
  },

  setBackgroundColor: (color) => {
    set({ backgroundColor: color })
    
    const { canvas } = get()
    if (canvas) {
      canvas.backgroundColor = color
      canvas.renderAll()
    }
  },

  setZoom: (zoom) => {
    set({ zoom })
    
    const { canvas } = get()
    if (canvas) {
      const vpt = canvas.viewportTransform
      if (vpt) {
        vpt[0] = zoom
        vpt[3] = zoom
        canvas.setViewportTransform(vpt)
        canvas.renderAll()
      }
    }
  },

  undo: () => {
    const { history, historyIndex } = get()
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1
      const previousState = history[newIndex]
      
      set(() => ({
        canvasObjects: previousState,
        historyIndex: newIndex
      }))
      
      // Restaurar objetos no canvas
      const { canvas } = get()
      if (canvas) {
        canvas.clear()
        previousState.forEach(obj => {
          canvas.add(obj.fabricObject)
        })
        canvas.renderAll()
      }
    }
  },

  redo: () => {
    const { history, historyIndex } = get()
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1
      const nextState = history[newIndex]
      
      set(() => ({
        canvasObjects: nextState,
        historyIndex: newIndex
      }))
      
      // Restaurar objetos no canvas
      const { canvas } = get()
      if (canvas) {
        canvas.clear()
        nextState.forEach(obj => {
          canvas.add(obj.fabricObject)
        })
        canvas.renderAll()
      }
    }
  },

  saveToHistory: () => {
    const { canvasObjects, history, historyIndex } = get()
    const newHistory = history.slice(0, historyIndex + 1)
    newHistory.push([...canvasObjects])
    
    set({
      history: newHistory,
      historyIndex: newHistory.length - 1
    })
  },

  clearCanvas: () => {
    set({ canvasObjects: [], selectedObject: null })
    
    const { canvas } = get()
    if (canvas) {
      canvas.clear()
      canvas.renderAll()
    }
    
    get().saveToHistory()
  },

  exportCanvas: () => {
    const { canvas } = get()
    if (canvas) {
      return canvas.toDataURL({
        format: 'png',
        quality: 1,
        multiplier: 1
      })
    }
    return ''
  },

  // Scene and Asset Actions Implementation
  addScene: (scene) => {
    set(state => ({
      scenes: [...state.scenes, { ...scene, id: `scene-${Date.now()}` }]
    }))
  },

  updateScene: (id, updates) => {
    set(state => ({
      scenes: state.scenes.map(scene => 
        scene.id === id ? { ...scene, ...updates } : scene
      )
    }))
  },

  deleteScene: (id) => {
    set(state => ({
      scenes: state.scenes.filter(scene => scene.id !== id),
      activeScene: state.activeScene?.id === id ? null : state.activeScene
    }))
  },

  duplicateScene: (id) => {
    set(state => {
      const scene = state.scenes.find(s => s.id === id)
      if (!scene) return state
      
      const duplicate = {
        ...scene,
        id: `scene-${Date.now()}`,
        name: `${scene.name} (Cópia)`
      }
      
      return {
        scenes: [...state.scenes, duplicate]
      }
    })
  },

  setActiveScene: (id) => {
    set(state => ({
      activeScene: state.scenes.find(scene => scene.id === id) || null
    }))
  },

  reorderScenes: (scenes) => {
    set({ scenes })
  },

  addAsset: (asset) => {
    set(state => ({
      assets: [...state.assets, { ...asset, id: `asset-${Date.now()}` }]
    }))
  },

  deleteAsset: (id) => {
    set(state => ({
      assets: state.assets.filter(asset => asset.id !== id)
    }))
  },

  addAssetToScene: (assetId, sceneId) => {
    set(state => ({
      scenes: state.scenes.map(scene => {
        if (scene.id === sceneId) {
          const asset = state.assets.find(a => a.id === assetId)
          if (asset && !scene.assets.find((a: any) => a.id === assetId)) {
            return {
              ...scene,
              assets: [...scene.assets, asset]
            }
          }
        }
        return scene
      })
    }))
  },

  removeAssetFromScene: (assetId, sceneId) => {
    set(state => ({
      scenes: state.scenes.map(scene => {
        if (scene.id === sceneId) {
          return {
            ...scene,
            assets: scene.assets.filter((asset: any) => asset.id !== assetId)
          }
        }
        return scene
      })
    }))
  },

  setSelection: (selection) => {
    set({ selection })
  }
}))
