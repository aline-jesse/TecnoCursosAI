/**
 * EditorCanvas - Componente Unificado do Canvas do Editor
 * Sistema completo de edição com Fabric.js e Zustand
 * Integra funcionalidades de drag & drop, edição inline e controles avançados
 */

import React, { useEffect, useRef, useCallback, useState } from 'react'
import * as fabric from 'fabric'
import { 
  EyeIcon, 
  EyeSlashIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  PhotoIcon,
  SpeakerWaveIcon,
  UserIcon,
  FilmIcon,
  PlusIcon,
  TrashIcon,
  ArrowsPointingOutIcon
} from '@heroicons/react/24/outline'
import { useEditorStore } from '../store/editorStore'
import './EditorCanvas.css'

// Declaração de tipos para Fabric.js
declare global {
  interface Window {
    fabric: typeof fabric
  }
}

interface EditorCanvasProps {
  selectedScene?: any
  assets?: any[]
  width?: number
  height?: number
  backgroundColor?: string
}

/**
 * Custom Hook para gerenciar o estado do canvas
 */
const useCanvasState = (selectedScene: any) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [showGrid, setShowGrid] = useState(true)
  const [showRulers, setShowRulers] = useState(true)
  const [selectedElement, setSelectedElement] = useState<string | null>(null)

  // Resetar estado quando cena muda
  useEffect(() => {
    setIsPlaying(false)
    setCurrentTime(0)
    setSelectedElement(null)
  }, [selectedScene?.id])

  const togglePlayback = useCallback(() => {
    setIsPlaying(prev => !prev)
  }, [])

  const stopPlayback = useCallback(() => {
    setIsPlaying(false)
    setCurrentTime(0)
  }, [])

  const selectElement = useCallback((elementId: string | null) => {
    setSelectedElement(elementId)
  }, [])

  return {
    isPlaying,
    currentTime,
    selectedElement,
    showGrid,
    showRulers,
    togglePlayback,
    stopPlayback,
    selectElement,
    setShowGrid,
    setShowRulers
  }
}

/**
 * Custom Hook para gerenciar elementos da cena
 */
const useSceneElements = (selectedScene: any) => {
  const [elements, setElements] = useState(selectedScene?.elements || [])

  useEffect(() => {
    setElements(selectedScene?.elements || [])
  }, [selectedScene])

  const addElement = useCallback((element: any) => {
    setElements((prev: any[]) => [...prev, { ...element, id: `element-${Date.now()}` }])
  }, [])

  const removeElement = useCallback((elementId: string) => {
    setElements((prev: any[]) => prev.filter(el => el.id !== elementId))
  }, [])

  const updateElement = useCallback((elementId: string, updates: any) => {
    setElements((prev: any[]) => 
      prev.map(el => el.id === elementId ? { ...el, ...updates } : el)
    )
  }, [])

  return {
    elements,
    addElement,
    removeElement,
    updateElement
  }
}

/**
 * Componente para controles do canvas
 */
const CanvasControls = React.memo(({ 
  isPlaying, 
  onTogglePlayback, 
  onStop, 
  zoomLevel, 
  onZoomChange,
  showGrid,
  onToggleGrid,
  showRulers,
  onToggleRulers
}: any) => {
  return (
    <div className="canvas-controls">
      <div className="playback-controls">
        <button
          className="control-btn"
          onClick={onTogglePlayback}
          title={isPlaying ? 'Pausar' : 'Reproduzir'}
        >
          {isPlaying ? <PauseIcon className="w-4 h-4" /> : <PlayIcon className="w-4 h-4" />}
        </button>
        
        <button
          className="control-btn"
          onClick={onStop}
          title="Parar"
        >
          <StopIcon className="w-4 h-4" />
        </button>
      </div>
      
      <div className="view-controls">
        <button
          className={`control-btn ${showGrid ? 'active' : ''}`}
          onClick={onToggleGrid}
          title="Mostrar/Ocultar Grid"
        >
          <ArrowsPointingOutIcon className="w-4 h-4" />
        </button>
        
        <button
          className={`control-btn ${showRulers ? 'active' : ''}`}
          onClick={onToggleRulers}
          title="Mostrar/Ocultar Réguas"
        >
          <Cog6ToothIcon className="w-4 h-4" />
        </button>
      </div>
      
      <div className="zoom-controls">
        <button
          className="control-btn"
          onClick={() => onZoomChange(zoomLevel - 0.1)}
          title="Diminuir Zoom"
        >
          -
        </button>
        
        <span className="zoom-level">{Math.round(zoomLevel * 100)}%</span>
        
        <button
          className="control-btn"
          onClick={() => onZoomChange(zoomLevel + 0.1)}
          title="Aumentar Zoom"
        >
          +
        </button>
      </div>
    </div>
  )
})

/**
 * Componente principal EditorCanvas Unificado
 */
const EditorCanvas: React.FC<EditorCanvasProps> = ({
  selectedScene,
  assets = [],
  width = 1920,
  height = 1080,
  backgroundColor = '#ffffff'
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const {
    canvas,
    setCanvas,
    currentTool,
    canvasWidth,
    canvasHeight,
    zoom,
    setCanvasSize,
    setBackgroundColor,
    setZoom,
    addObject,
    removeObject,
    updateObject,
    selectObject,
    clearCanvas,
    exportCanvas
  } = useEditorStore()

  // Custom hooks para gerenciar estado
  const canvasState = useCanvasState(selectedScene)
  const { elements, addElement, removeElement, updateElement } = useSceneElements(selectedScene)

  // Inicializar canvas Fabric.js
  const initializeCanvas = useCallback(() => {
    if (!canvasRef.current) return

    const fabricCanvas = new fabric.Canvas(canvasRef.current, {
      width: canvasWidth,
      height: canvasHeight,
      backgroundColor,
      selection: true,
      preserveObjectStacking: true,
      renderOnAddRemove: true,
      skipTargetFind: false,
      stopContextMenu: true,
      fireRightClick: true,
      fireMiddleClick: true,
      enableRetinaScaling: true,
      allowTouchScrolling: true
    })

    // Configurar eventos do canvas
    fabricCanvas.on('mouse:wheel', (opt) => {
      const delta = opt.e.deltaY
      let zoomLevel = fabricCanvas.getZoom()
      zoomLevel *= 0.999 ** delta
      
      if (zoomLevel > 20) zoomLevel = 20
      if (zoomLevel < 0.01) zoomLevel = 0.01
      
      fabricCanvas.zoomToPoint(new fabric.Point(opt.e.offsetX, opt.e.offsetY), zoomLevel)
      setZoom(zoomLevel)
      opt.e.preventDefault()
      opt.e.stopPropagation()
    })

    // Pan com middle mouse button
    fabricCanvas.on('mouse:down', (opt) => {
      if ((opt.e as any).button === 1) {
        ;(fabricCanvas as any).isDragging = true
        fabricCanvas.selection = false
        const pointer = fabricCanvas.getPointer(opt.e)
        ;(fabricCanvas as any).lastPosX = pointer.x
        ;(fabricCanvas as any).lastPosY = pointer.y
      }
    })

    fabricCanvas.on('mouse:move', (opt) => {
      if ((fabricCanvas as any).isDragging) {
        const vpt = fabricCanvas.viewportTransform
        if (vpt) {
          const pointer = fabricCanvas.getPointer(opt.e)
          vpt[4] += pointer.x - (fabricCanvas as any).lastPosX
          vpt[5] += pointer.y - (fabricCanvas as any).lastPosY
          fabricCanvas.requestRenderAll()
          ;(fabricCanvas as any).lastPosX = pointer.x
          ;(fabricCanvas as any).lastPosY = pointer.y
        }
      }
    })

    fabricCanvas.on('mouse:up', () => {
      ;(fabricCanvas as any).isDragging = false
      fabricCanvas.selection = true
    })

    setCanvas(fabricCanvas)
    return fabricCanvas
  }, [canvasWidth, canvasHeight, backgroundColor, setCanvas, setZoom])

  // Efeito para inicializar canvas
  useEffect(() => {
    const fabricCanvas = initializeCanvas()
    
    return () => {
      if (fabricCanvas) {
        fabricCanvas.dispose()
      }
    }
  }, [initializeCanvas])

  // Efeito para atualizar tamanho do canvas
  useEffect(() => {
    if (canvas) {
      setCanvasSize(width, height)
    }
  }, [width, height, canvas, setCanvasSize])

  // Efeito para atualizar cor de fundo
  useEffect(() => {
    if (canvas) {
      setBackgroundColor(backgroundColor)
    }
  }, [backgroundColor, canvas, setBackgroundColor])

  // Efeito para atualizar ferramenta atual
  useEffect(() => {
    if (!canvas) return

    switch (currentTool) {
      case 'select':
        canvas.isDrawingMode = false
        canvas.selection = true
        break
      case 'text':
        canvas.isDrawingMode = false
        canvas.selection = true
        break
      case 'draw':
        canvas.isDrawingMode = true
        canvas.freeDrawingBrush = new fabric.PencilBrush(canvas)
        canvas.freeDrawingBrush.color = '#000000'
        canvas.freeDrawingBrush.width = 2
        break
      case 'eraser':
        canvas.isDrawingMode = true
        canvas.freeDrawingBrush = new fabric.PencilBrush(canvas)
        canvas.freeDrawingBrush.color = 'rgba(255,255,255,1)'
        canvas.freeDrawingBrush.width = 20
        break
      default:
        canvas.isDrawingMode = false
        canvas.selection = true
    }
  }, [currentTool, canvas])

  // Funções para adicionar objetos
  const addText = useCallback(() => {
    if (!canvas) return

    const text = new fabric.IText('Texto Editável', {
      left: 100,
      top: 100,
      fontFamily: 'Arial',
      fontSize: 20,
      fill: '#000000',
      selectable: true,
      editable: true
    })

    canvas.add(text)
    canvas.setActiveObject(text)
    canvas.renderAll()
  }, [canvas])

  const addRectangle = useCallback(() => {
    if (!canvas) return

    const rect = new fabric.Rect({
      left: 100,
      top: 100,
      width: 100,
      height: 100,
      fill: '#ff0000',
      stroke: '#000000',
      strokeWidth: 2,
      selectable: true
    })

    canvas.add(rect)
    canvas.setActiveObject(rect)
    canvas.renderAll()
  }, [canvas])

  const addCircle = useCallback(() => {
    if (!canvas) return

    const circle = new fabric.Circle({
      left: 100,
      top: 100,
      radius: 50,
      fill: '#00ff00',
      stroke: '#000000',
      strokeWidth: 2,
      selectable: true
    })

    canvas.add(circle)
    canvas.setActiveObject(circle)
    canvas.renderAll()
  }, [canvas])

  const addImage = useCallback((url: string) => {
    if (!canvas) return

    fabric.Image.fromURL(url).then((img) => {
      img.scaleToWidth(200)
      canvas.add(img)
      canvas.setActiveObject(img)
      canvas.renderAll()
    })
  }, [canvas])

  // Manipula drag & drop de assets
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.currentTarget.classList.add('drag-over')
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.currentTarget.classList.remove('drag-over')
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.currentTarget.classList.remove('drag-over')
    
    const assetId = e.dataTransfer.getData('text/plain')
    const asset = assets.find(a => a.id === assetId)
    
    if (asset && selectedScene && canvas) {
      // Calcula posição do drop
      const rect = e.currentTarget.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      
      // Adiciona asset ao canvas baseado no tipo
      if (asset.type === 'image' && asset.url) {
        addImage(asset.url)
      } else if (asset.type === 'text') {
        addText()
      }
      
      console.log(`Asset ${asset.name} adicionado à cena na posição (${x}, ${y})`)
    }
  }, [assets, selectedScene, canvas, addImage, addText])

  // Renderiza mensagem se não há cena ativa
  if (!selectedScene) {
    return (
      <div className="editor-canvas empty">
        <div className="empty-state">
          <h3>Nenhuma cena selecionada</h3>
          <p>Selecione uma cena para começar a editar</p>
        </div>
      </div>
    )
  }

  return (
    <div className="editor-canvas-container">
      {/* Header da cena com controles */}
      <div className="canvas-header">
        <div className="scene-info">
          <h3>Editando: {selectedScene.title || selectedScene.name}</h3>
          <span>Duração: {selectedScene.duration || 30}s</span>
        </div>
        
        <CanvasControls
          isPlaying={canvasState.isPlaying}
          onTogglePlayback={canvasState.togglePlayback}
          onStop={canvasState.stopPlayback}
          zoomLevel={zoom}
          onZoomChange={setZoom}
          showGrid={canvasState.showGrid}
          onToggleGrid={canvasState.setShowGrid}
          showRulers={canvasState.showRulers}
          onToggleRulers={canvasState.setShowRulers}
        />
      </div>

      {/* Toolbar do canvas */}
      <div className="canvas-toolbar">
        <button onClick={addText} className="tool-button">
          <DocumentTextIcon className="w-4 h-4" /> Texto
        </button>
        <button onClick={addRectangle} className="tool-button">
          ⬜ Retângulo
        </button>
        <button onClick={addCircle} className="tool-button">
          ⭕ Círculo
        </button>
        <button onClick={clearCanvas} className="tool-button">
          <TrashIcon className="w-4 h-4" /> Limpar
        </button>
        <button onClick={exportCanvas} className="tool-button">
          💾 Exportar
        </button>
      </div>
      
      {/* Wrapper do canvas */}
      <div 
        className="canvas-wrapper"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <canvas
          ref={canvasRef}
          className={`editor-canvas ${canvasState.showGrid ? 'show-grid' : ''} ${canvasState.showRulers ? 'show-rulers' : ''}`}
          style={{
            border: '1px solid #ccc',
            cursor: currentTool === 'select' ? 'default' : 'crosshair'
          }}
        />
      </div>
      
      {/* Info do canvas */}
      <div className="canvas-info">
        <span>Ferramenta: {currentTool}</span>
        <span>Tamanho: {canvasWidth} x {canvasHeight}</span>
        <span>Zoom: {Math.round(zoom * 100)}%</span>
      </div>
    </div>
  )
}

export default EditorCanvas 