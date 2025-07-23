/**
 * EditorCanvas - Componente Unificado do Canvas do Editor
 * Sistema completo de edição com Fabric.js e Zustand
 * Integra funcionalidades de drag & drop, edição inline e controles avançados
 */

import React, { useEffect, useRef, useCallback, useState } from 'react';
import * as fabric from 'fabric';
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
  ArrowsPointingOutIcon,
  MagnifyingGlassIcon,
  MinusIcon,
  ArrowPathIcon,
  Square2StackIcon,
} from '@heroicons/react/24/outline';
import { useEditorStore } from '../store/editorStore';
import { EditorElement, ElementType } from '../types/editor';
import './EditorCanvas.css';

// Tipos para Fabric.js
// TODO: Refatorar para tipos mais estritos conforme documentação do fabric.js
type FabricEventAny = any; // Usar 'any' para compatibilidade de build
type FabricImage = fabric.Image;

// Declaração de tipos para Fabric.js
declare global {
  interface Window {
    fabric: typeof fabric;
  }
}

interface EditorCanvasProps {
  width?: number;
  height?: number;
  backgroundColor?: string;
}

/**
 * Custom Hook para gerenciar o estado do canvas
 */
const useCanvasState = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [showGrid, setShowGrid] = useState(true);
  const [showRulers, setShowRulers] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [isDragging, setIsDragging] = useState(false);

  const togglePlayback = useCallback(() => {
    setIsPlaying(prev => !prev);
  }, []);

  const stopPlayback = useCallback(() => {
    setIsPlaying(false);
    setCurrentTime(0);
  }, []);

  const zoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev * 1.2, 3));
  }, []);

  const zoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev / 1.2, 0.1));
  }, []);

  const resetZoom = useCallback(() => {
    setZoom(1);
  }, []);

  return {
    isPlaying,
    currentTime,
    showGrid,
    showRulers,
    zoom,
    isDragging,
    togglePlayback,
    stopPlayback,
    setShowGrid,
    setShowRulers,
    setZoom,
    zoomIn,
    zoomOut,
    resetZoom,
    setIsDragging,
  };
};

/**
 * EditorCanvas Component
 */
const EditorCanvas: React.FC<EditorCanvasProps> = ({
  width = 1920,
  height = 1080,
  backgroundColor = '#ffffff',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<fabric.Canvas | null>(null);

  const {
    scenes,
    currentSceneId,
    selectedElementId,
    draggedAsset,
    addElement,
    updateElement,
    deleteElement,
    setSelectedElementId,
    setDraggedAsset,
    canvasWidth,
    canvasHeight,
    setCanvasSize,
  } = useEditorStore();

  const canvasState = useCanvasState();
  const currentScene = scenes.find(scene => scene.id === currentSceneId);

  // Inicializar Fabric.js Canvas
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = new fabric.Canvas(canvasRef.current, {
      width,
      height,
      backgroundColor,
      selection: true,
      preserveObjectStacking: true,
      renderOnAddRemove: true,
      skipTargetFind: false,
      selectable: true,
      evented: true,
      fireRightClick: true,
      fireMiddleClick: true,
      stopContextMenu: true,
      enableRetinaScaling: true,
      imageSmoothingEnabled: true,
      imageSmoothingQuality: 'high',
    });

    fabricCanvasRef.current = canvas;

    // Configurar eventos do canvas
    canvas.on('selection:created', handleSelectionCreated);
    canvas.on('selection:updated', handleSelectionUpdated);
    canvas.on('selection:cleared', handleSelectionCleared);
    canvas.on('object:modified', handleObjectModified);
    canvas.on('object:moving', handleObjectMoving);
    canvas.on('object:scaling', handleObjectScaling);
    canvas.on('object:rotating', handleObjectRotating);
    canvas.on('mouse:down', handleMouseDown);
    canvas.on('mouse:up', handleMouseUp);
    canvas.on('mouse:move', handleMouseMove);

    // Configurar grid
    if (canvasState.showGrid) {
      drawGrid(canvas);
    }

    // Configurar regras
    if (canvasState.showRulers) {
      drawRulers(canvas);
    }

    setCanvasSize(width, height);

    return () => {
      canvas.dispose();
    };
  }, [width, height, backgroundColor]);

  // Atualizar elementos quando a cena muda
  useEffect(() => {
    if (!fabricCanvasRef.current || !currentScene) return;

    const canvas = fabricCanvasRef.current;
    canvas.clear();

    // Adicionar elementos da cena atual
    currentScene.elements.forEach(element => {
      addFabricObject(element);
    });

    // Redesenhar grid e regras
    if (canvasState.showGrid) {
      drawGrid(canvas);
    }
    if (canvasState.showRulers) {
      drawRulers(canvas);
    }
  }, [currentScene, canvasState.showGrid, canvasState.showRulers]);

  // Atualizar zoom
  useEffect(() => {
    if (!fabricCanvasRef.current) return;

    const canvas = fabricCanvasRef.current;
    canvas.setZoom(canvasState.zoom);
    canvas.renderAll();
  }, [canvasState.zoom]);

  // Handlers de eventos do canvas
  const handleSelectionCreated = useCallback(
    (e: FabricEventAny) => {
      const activeObject = e.selected?.[0];
      if (activeObject && 'id' in activeObject) {
        setSelectedElementId(activeObject.id as string);
      }
    },
    [setSelectedElementId]
  );

  const handleSelectionUpdated = useCallback(
    (e: FabricEventAny) => {
      const activeObject = e.selected?.[0];
      if (activeObject && 'id' in activeObject) {
        setSelectedElementId(activeObject.id as string);
      }
    },
    [setSelectedElementId]
  );

  const handleSelectionCleared = useCallback(() => {
    setSelectedElementId(null);
  }, [setSelectedElementId]);

  const handleObjectModified = useCallback(
    (e: FabricEventAny) => {
      if (!currentSceneId) return;

      const fabricObject = e.target;
      if (!fabricObject || !('id' in fabricObject)) return;

      const elementId = fabricObject.id as string;

      const updatedElement: Partial<EditorElement> = {
        x: fabricObject.left || 0,
        y: fabricObject.top || 0,
        width: fabricObject.width || 0,
        height: fabricObject.height || 0,
        rotation: fabricObject.angle || 0,
        opacity: fabricObject.opacity || 1,
      };

      updateElement(updatedElement);
    },
    [currentSceneId, updateElement]
  );

  const handleObjectMoving = useCallback(() => {
    canvasState.setIsDragging(true);
  }, [canvasState]);

  const handleObjectScaling = useCallback(() => {
    // Atualizar em tempo real durante o redimensionamento
  }, []);

  const handleObjectRotating = useCallback(() => {
    // Atualizar em tempo real durante a rotação
  }, []);

  const handleMouseDown = useCallback(() => {
    // Implementar lógica de mouse down se necessário
  }, []);

  const handleMouseUp = useCallback(() => {
    canvasState.setIsDragging(false);
  }, [canvasState]);

  const handleMouseMove = useCallback(() => {
    // Implementar lógica de mouse move se necessário
  }, []);

  // Adicionar objeto Fabric.js baseado no elemento
  const addFabricObject = useCallback((element: EditorElement) => {
    if (!fabricCanvasRef.current) return;

    const canvas = fabricCanvasRef.current;
    let fabricObject: fabric.Object | null = null;

    switch (element.type) {
      case 'text':
        fabricObject = new fabric.Text(element.text, {
          left: element.x,
          top: element.y,
          fontSize: element.fontSize,
          fontFamily: element.fontFamily,
          fill: element.fill,
          width: element.width,
          height: element.height,
          angle: element.rotation,
          opacity: element.opacity,
          id: element.id,
          selectable: true,
          evented: true,
        });
        break;

      case 'image':
        // @ts-expect-error
        fabric.Image.fromURL(element.src, (img: any) => {
          img.set({
            left: element.x,
            top: element.y,
            width: element.width,
            height: element.height,
            angle: element.rotation,
            opacity: element.opacity,
            id: element.id,
            selectable: true,
            evented: true,
          });
          canvas.add(img);
          canvas.renderAll();
        });
        return;

      case 'character':
        // @ts-expect-error
        fabric.Image.fromURL(element.src, (img: any) => {
          img.set({
            left: element.x,
            top: element.y,
            width: element.width,
            height: element.height,
            angle: element.rotation,
            opacity: element.opacity,
            id: element.id,
            selectable: true,
            evented: true,
          });
          canvas.add(img);
          canvas.renderAll();
        });
        return;

      case 'shape':
        switch (element.shapeType) {
          case 'rectangle':
            fabricObject = new fabric.Rect({
              left: element.x,
              top: element.y,
              width: element.width,
              height: element.height,
              fill: element.fill,
              stroke: element.stroke,
              strokeWidth: element.strokeWidth,
              angle: element.rotation,
              opacity: element.opacity,
              id: element.id,
              selectable: true,
              evented: true,
            });
            break;
          case 'circle':
            fabricObject = new fabric.Circle({
              left: element.x,
              top: element.y,
              radius: element.width / 2,
              fill: element.fill,
              stroke: element.stroke,
              strokeWidth: element.strokeWidth,
              angle: element.rotation,
              opacity: element.opacity,
              id: element.id,
              selectable: true,
              evented: true,
            });
            break;
        }
        break;
    }

    if (fabricObject) {
      canvas.add(fabricObject);
      canvas.renderAll();
    }
  }, []);

  // Desenhar grid
  const drawGrid = useCallback((canvas: fabric.Canvas) => {
    const gridSize = 20;
    const width = canvas.getWidth();
    const height = canvas.getHeight();

    // Remover grid anterior
    canvas.getObjects().forEach(obj => {
      if ('id' in obj && obj.id === 'grid') {
        canvas.remove(obj);
      }
    });

    // Desenhar linhas verticais
    for (let i = 0; i <= width; i += gridSize) {
      const line = new fabric.Line([i, 0, i, height], {
        stroke: '#e5e7eb',
        strokeWidth: 1,
        selectable: false,
        evented: false,
        id: 'grid',
      });
      canvas.add(line);
    }

    // Desenhar linhas horizontais
    for (let i = 0; i <= height; i += gridSize) {
      const line = new fabric.Line([0, i, width, i], {
        stroke: '#e5e7eb',
        strokeWidth: 1,
        selectable: false,
        evented: false,
        id: 'grid',
      });
      canvas.add(line);
    }

    canvas.renderAll();
  }, []);

  // Desenhar regras
  const drawRulers = useCallback((canvas: fabric.Canvas) => {
    // Implementar regras se necessário
  }, []);

  // Adicionar elemento quando asset é arrastado
  useEffect(() => {
    if (!draggedAsset || !currentSceneId || !fabricCanvasRef.current) return;

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();

      if (!fabricCanvasRef.current) return;

      const canvas = fabricCanvasRef.current;
      const rect = canvas.getElement().getBoundingClientRect();
      const x = (e.clientX - rect.left) / canvasState.zoom;
      const y = (e.clientY - rect.top) / canvasState.zoom;

      const newElement: EditorElement = {
        id: `element-${Date.now()}`,
        type: draggedAsset.type === 'character' ? 'character' : 'image',
        x,
        y,
        width: 200,
        height: 200,
        rotation: 0,
        opacity: 1,
        src: draggedAsset.src,
      };

      addElement(newElement);
      setDraggedAsset(null);
    };

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    const canvasElement = fabricCanvasRef.current.getElement();
    canvasElement.addEventListener('drop', handleDrop);
    canvasElement.addEventListener('dragover', handleDragOver);

    return () => {
      canvasElement.removeEventListener('drop', handleDrop);
      canvasElement.removeEventListener('dragover', handleDragOver);
    };
  }, [
    draggedAsset,
    currentSceneId,
    addElement,
    setDraggedAsset,
    canvasState.zoom,
  ]);

  // Adicionar texto
  const addText = useCallback(() => {
    if (!currentSceneId) return;

    const newElement: EditorElement = {
      id: `text-${Date.now()}`,
      type: 'text',
      x: 100,
      y: 100,
      width: 200,
      height: 50,
      rotation: 0,
      opacity: 1,
      text: 'Novo texto',
      fontSize: 24,
      fontFamily: 'Arial',
      fill: '#000000',
    };

    addElement(newElement);
  }, [currentSceneId, addElement]);

  // Adicionar forma
  const addShape = useCallback(
    (shapeType: 'rectangle' | 'circle') => {
      if (!currentSceneId) return;

      const newElement: EditorElement = {
        id: `shape-${Date.now()}`,
        type: 'shape',
        x: 100,
        y: 100,
        width: 100,
        height: 100,
        rotation: 0,
        opacity: 1,
        shapeType,
        fill: '#3b82f6',
        stroke: '#1d4ed8',
        strokeWidth: 2,
      };

      addElement(newElement);
    },
    [currentSceneId, addElement]
  );

  // Deletar elemento selecionado
  const deleteSelectedElement = useCallback(() => {
    if (!currentSceneId || !selectedElementId) return;

    deleteElement(selectedElementId);

    if (fabricCanvasRef.current) {
      const canvas = fabricCanvasRef.current;
      const activeObject = canvas.getActiveObject();
      if (activeObject) {
        canvas.remove(activeObject);
        canvas.renderAll();
      }
    }
  }, [currentSceneId, selectedElementId, deleteElement]);

  return (
    <div className='editor-canvas-container'>
      {/* Controles do canvas */}
      <div className='canvas-controls'>
        <div className='control-group'>
          <button
            className='control-btn'
            onClick={addText}
            title='Adicionar texto'
          >
            <DocumentTextIcon className='w-4 h-4' />
          </button>
          <button
            className='control-btn'
            onClick={() => addShape('rectangle')}
            title='Adicionar retângulo'
          >
            <Square2StackIcon className='w-4 h-4' />
          </button>
          <button
            className='control-btn'
            onClick={() => addShape('circle')}
            title='Adicionar círculo'
          >
            <ArrowsPointingOutIcon className='w-4 h-4' />
          </button>
        </div>

        <div className='control-group'>
          <button
            className='control-btn'
            onClick={canvasState.zoomOut}
            title='Diminuir zoom'
          >
            <MinusIcon className='w-4 h-4' />
          </button>
          <span className='zoom-display'>
            {Math.round(canvasState.zoom * 100)}%
          </span>
          <button
            className='control-btn'
            onClick={canvasState.zoomIn}
            title='Aumentar zoom'
          >
            <MagnifyingGlassIcon className='w-4 h-4' />
          </button>
          <button
            className='control-btn'
            onClick={canvasState.resetZoom}
            title='Resetar zoom'
          >
            <ArrowPathIcon className='w-4 h-4' />
          </button>
        </div>

        <div className='control-group'>
          <button
            className={`control-btn ${canvasState.showGrid ? 'active' : ''}`}
            onClick={() => canvasState.setShowGrid(!canvasState.showGrid)}
            title='Mostrar/ocultar grid'
          >
            <Cog6ToothIcon className='w-4 h-4' />
          </button>
          <button
            className={`control-btn ${canvasState.showRulers ? 'active' : ''}`}
            onClick={() => canvasState.setShowRulers(!canvasState.showRulers)}
            title='Mostrar/ocultar regras'
          >
            <ArrowsPointingOutIcon className='w-4 h-4' />
          </button>
        </div>

        {selectedElementId && (
          <div className='control-group'>
            <button
              className='control-btn danger'
              onClick={deleteSelectedElement}
              title='Deletar elemento'
            >
              <TrashIcon className='w-4 h-4' />
            </button>
          </div>
        )}
      </div>

      {/* Canvas */}
      <div className='canvas-wrapper'>
        <canvas
          ref={canvasRef}
          className='editor-canvas'
          style={{
            transform: `scale(${canvasState.zoom})`,
            transformOrigin: 'top left',
          }}
        />

        {/* Overlay de informações */}
        <div className='canvas-overlay'>
          <div className='canvas-info'>
            {currentScene ? (
              <>
                <span className='scene-name'>{currentScene.name}</span>
                <span className='scene-duration'>{currentScene.duration}s</span>
              </>
            ) : (
              <span className='no-scene'>Nenhuma cena selecionada</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditorCanvas;
