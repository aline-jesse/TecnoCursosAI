import React, { useEffect, useRef, useCallback } from 'react'
import * as fabric from 'fabric'
import { useEditorStore } from '../../store/editorStore'
import './EditorCanvas.css'

interface EditorCanvasProps {
  width?: number
  height?: number
  backgroundColor?: string
}

export const EditorCanvas: React.FC<EditorCanvasProps> = ({
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
    setZoom
  } = useEditorStore()

  // Inicializar canvas
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
    fabricCanvas.on('mouse:down', (e) => {
      console.log('Mouse down:', e)
    })

    fabricCanvas.on('mouse:up', (e) => {
      console.log('Mouse up:', e)
    })

    fabricCanvas.on('mouse:move', (e) => {
      console.log('Mouse move:', e)
    })

    fabricCanvas.on('object:added', (e) => {
      console.log('Object added:', e)
    })

    fabricCanvas.on('object:removed', (e) => {
      console.log('Object removed:', e)
    })

    fabricCanvas.on('object:modified', (e) => {
      console.log('Object modified:', e)
    })

    fabricCanvas.on('selection:created', (e) => {
      console.log('Selection created:', e)
    })

    fabricCanvas.on('selection:cleared', (e) => {
      console.log('Selection cleared:', e)
    })

    // Configurar zoom com scroll
    fabricCanvas.on('mouse:wheel', (opt) => {
      const delta = opt.e.deltaY
      let zoom = fabricCanvas.getZoom()
      zoom *= 0.999 ** delta
      
      if (zoom > 20) zoom = 20
      if (zoom < 0.01) zoom = 0.01
      
      fabricCanvas.zoomToPoint({ x: opt.e.offsetX, y: opt.e.offsetY }, zoom)
      setZoom(zoom)
      opt.e.preventDefault()
      opt.e.stopPropagation()
    })

    // Configurar pan com middle mouse button
    fabricCanvas.on('mouse:down', (opt) => {
      if (opt.e.button === 1) { // Middle mouse button
        fabricCanvas.isDragging = true
        fabricCanvas.selection = false
        fabricCanvas.getPointer(opt.e)
        fabricCanvas.lastPosX = fabricCanvas.getPointer(opt.e).x
        fabricCanvas.lastPosY = fabricCanvas.getPointer(opt.e).y
      }
    })

    fabricCanvas.on('mouse:move', (opt) => {
      if (fabricCanvas.isDragging) {
        const vpt = fabricCanvas.viewportTransform
        if (vpt) {
          vpt[4] += fabricCanvas.getPointer(opt.e).x - fabricCanvas.lastPosX
          vpt[5] += fabricCanvas.getPointer(opt.e).y - fabricCanvas.lastPosY
          fabricCanvas.requestRenderAll()
          fabricCanvas.lastPosX = fabricCanvas.getPointer(opt.e).x
          fabricCanvas.lastPosY = fabricCanvas.getPointer(opt.e).y
        }
      }
    })

    fabricCanvas.on('mouse:up', () => {
      fabricCanvas.isDragging = false
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

    fabric.Image.fromURL(url, (img) => {
      img.scaleToWidth(200)
      canvas.add(img)
      canvas.setActiveObject(img)
      canvas.renderAll()
    })
  }, [canvas])

  // Funções de controle
  const clearCanvas = useCallback(() => {
    if (canvas) {
      canvas.clear()
      canvas.backgroundColor = backgroundColor
      canvas.renderAll()
    }
  }, [canvas, backgroundColor])

  const exportCanvas = useCallback(() => {
    if (canvas) {
      const dataURL = canvas.toDataURL({
        format: 'png',
        quality: 1
      })
      
      const link = document.createElement('a')
      link.download = 'canvas-export.png'
      link.href = dataURL
      link.click()
    }
  }, [canvas])

  return (
    <div className="editor-canvas-container">
      <div className="canvas-toolbar">
        <button onClick={addText} className="tool-button">
          📝 Texto
        </button>
        <button onClick={addRectangle} className="tool-button">
          ⬜ Retângulo
        </button>
        <button onClick={addCircle} className="tool-button">
          ⭕ Círculo
        </button>
        <button onClick={clearCanvas} className="tool-button">
          🗑️ Limpar
        </button>
        <button onClick={exportCanvas} className="tool-button">
          💾 Exportar
        </button>
        <div className="zoom-controls">
          <button onClick={() => setZoom(zoom * 1.2)}>🔍+</button>
          <span>{Math.round(zoom * 100)}%</span>
          <button onClick={() => setZoom(zoom / 1.2)}>🔍-</button>
        </div>
      </div>
      
      <div className="canvas-wrapper">
        <canvas
          ref={canvasRef}
          className="editor-canvas"
          style={{
            border: '1px solid #ccc',
            cursor: currentTool === 'select' ? 'default' : 'crosshair'
          }}
        />
      </div>
      
      <div className="canvas-info">
        <span>Ferramenta: {currentTool}</span>
        <span>Tamanho: {canvasWidth} x {canvasHeight}</span>
        <span>Zoom: {Math.round(zoom * 100)}%</span>
      </div>
    </div>
  )
} 