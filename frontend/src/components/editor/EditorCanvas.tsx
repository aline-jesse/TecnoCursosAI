// src/components/editor/EditorCanvas.tsx
import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react';
import { useCanvasEvents } from '../../hooks/useCanvasEvents';
import { useCanvasFonts } from '../../hooks/useCanvasFonts';
import { useCanvasImages } from '../../hooks/useCanvasImages';
import { useCanvasLayers } from '../../hooks/useCanvasLayers';
import { useCanvasOptimization } from '../../hooks/useCanvasOptimization';
import { useCanvasTransform } from '../../hooks/useCanvasTransform';
import { useEditorStore } from '../../store/editorStore';
import {
  AudioElement,
  CanvasRef,
  CharacterElement,
  EditorCanvasProps,
  EditorElement,
  ImageElement,
  Scene,
  ShapeElement,
  TextElement,
  VideoElement,
} from '../../types/editor';
import './EditorCanvas.css';

type FabricEventHandler = (e: fabric.IEvent) => void;
type FabricObject = fabric.Object & { data?: { id: string } };

interface CanvasOptions extends fabric.ICanvasOptions {
  width: number;
  height: number;
  backgroundColor: string;
}

const EditorCanvas = forwardRef<CanvasRef, EditorCanvasProps>((props, ref) => {
  const {
    width = 1920,
    height = 1080,
    backgroundColor = '#ffffff',
    onElementSelect,
    onElementUpdate,
    onSceneUpdate,
    readOnly = false,
  } = props;

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<fabric.Canvas | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  const {
    scenes,
    currentScene,
    selectedElement,
    clipboard,
    addElement,
    updateElement,
    deleteElement,
    duplicateElement,
    bringToFront,
    sendToBack,
    copyElement,
    pasteElement,
    updateScene,
    zoom,
    isDragging,
    isPlaying,
    currentTime,
  } = useEditorStore();

  // Hooks personalizados para funcionalidades do canvas
  const { canvasRef: optimizedCanvasRef, optimizationConfig } =
    useCanvasOptimization(width, height);
  const { layers, contexts, createLayer, destroyLayer } = useCanvasLayers();
  const {
    setTransform,
    resetTransform,
    withTransform,
    transformPoint,
    inverseTransformPoint,
  } = useCanvasTransform();
  const { handleMouseDown, handleMouseMove, handleMouseUp, handleWheel } =
    useCanvasEvents({
      onElementSelect,
      onElementUpdate,
      onSceneUpdate,
    });
  const { loadImage, drawImage, clearCache } = useCanvasImages();
  const { loadFont, preloadFonts } = useCanvasFonts();

  const initializeCanvas = useCallback(() => {
    if (!canvasRef.current || isInitialized) return;

    const options: CanvasOptions = {
      width,
      height,
      backgroundColor,
      selection: !readOnly,
      preserveObjectStacking: true,
      renderOnAddRemove: true,
      skipTargetFind: readOnly,
      selectable: !readOnly,
      evented: !readOnly,
      fireRightClick: true,
      fireMiddleClick: true,
      stopContextMenu: true,
      enableRetinaScaling: true,
      imageSmoothingEnabled: true,
    };

    const canvas = new fabric.Canvas(canvasRef.current, options);
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
    canvas.on('mouse:wheel', handleWheel);

    // Criar camadas
    createLayer('background', { zIndex: 0 });
    createLayer('main', { zIndex: 1 });
    createLayer('overlay', { zIndex: 2 });

    setIsInitialized(true);

    return () => {
      canvas.dispose();
      destroyLayer('background');
      destroyLayer('main');
      destroyLayer('overlay');
      clearCache();
      setIsInitialized(false);
    };
  }, [width, height, backgroundColor, readOnly, isInitialized]);

  // Inicialização do canvas
  useEffect(() => {
    return initializeCanvas();
  }, [initializeCanvas]);

  // Atualizar opções do canvas quando readOnly muda
  useEffect(() => {
    if (!fabricCanvasRef.current) return;

    const canvas = fabricCanvasRef.current;
    canvas.selection = !readOnly;
    canvas.skipTargetFind = readOnly;
    canvas.selectable = !readOnly;
    canvas.evented = !readOnly;

    canvas.getObjects().forEach(obj => {
      obj.selectable = !readOnly;
      obj.evented = !readOnly;
    });

    canvas.renderAll();
  }, [readOnly]);

  // Renderização dos elementos
  useEffect(() => {
    if (!currentScene || !fabricCanvasRef.current || !isInitialized) return;

    const canvas = fabricCanvasRef.current;
    canvas.clear();

    // Renderizar fundo
    if (currentScene.background) {
      renderBackground(currentScene.background);
    }

    // Renderizar elementos
    currentScene.elements.forEach(element => {
      renderElement(element);
    });

    canvas.renderAll();
  }, [currentScene, zoom, isInitialized]);

  // Renderização do fundo
  const renderBackground = useCallback(
    (background: Scene['background']) => {
      if (!fabricCanvasRef.current || !contexts.background) return;

      const ctx = contexts.background;
      ctx.clearRect(0, 0, width, height);

      switch (background.type) {
        case 'color':
          ctx.fillStyle = background.value;
          ctx.fillRect(0, 0, width, height);
          break;
        case 'image':
          loadImage(background.value).then(image => {
            if (image) {
              drawImage(ctx, image, 0, 0, width, height);
            }
          });
          break;
        case 'video':
          // TODO: Implementar renderização de vídeo como fundo
          break;
      }
    },
    [width, height, contexts.background, loadImage, drawImage]
  );

  // Renderização de elementos
  const renderElement = useCallback(
    (element: EditorElement) => {
      if (!fabricCanvasRef.current) return;

      const canvas = fabricCanvasRef.current;
      const commonProps = {
        left: element.x,
        top: element.y,
        width: element.width,
        height: element.height,
        angle: element.rotation,
        scaleX: element.scaleX,
        scaleY: element.scaleY,
        opacity: element.opacity,
        selectable: !readOnly,
        evented: !readOnly,
        data: { id: element.id },
      };

      switch (element.type) {
        case 'text':
          renderTextElement(canvas, element as TextElement, commonProps);
          break;
        case 'image':
        case 'character':
          renderImageElement(
            canvas,
            element as ImageElement | CharacterElement,
            commonProps
          );
          break;
        case 'video':
          renderVideoElement(canvas, element as VideoElement, commonProps);
          break;
        case 'audio':
          renderAudioElement(canvas, element as AudioElement, commonProps);
          break;
        case 'shape':
          renderShapeElement(canvas, element as ShapeElement, commonProps);
          break;
      }
    },
    [readOnly]
  );

  // Renderização de elementos específicos
  const renderTextElement = useCallback(
    (
      canvas: fabric.Canvas,
      element: TextElement,
      commonProps: fabric.IObjectOptions
    ) => {
      const text = new fabric.Text(element.text, {
        ...commonProps,
        fontSize: element.fontSize,
        fontFamily: element.fontFamily,
        fill: element.fill,
      });

      canvas.add(text);
    },
    []
  );

  const renderImageElement = useCallback(
    (
      canvas: fabric.Canvas,
      element: ImageElement | CharacterElement,
      commonProps: fabric.IObjectOptions
    ) => {
      loadImage(element.src).then(img => {
        if (!img) return;

        const image = new fabric.Image(img, commonProps);
        canvas.add(image);
      });
    },
    [loadImage]
  );

  const renderVideoElement = useCallback(
    (
      canvas: fabric.Canvas,
      element: VideoElement,
      commonProps: fabric.IObjectOptions
    ) => {
      // TODO: Implementar renderização de vídeo
    },
    []
  );

  const renderAudioElement = useCallback(
    (
      canvas: fabric.Canvas,
      element: AudioElement,
      commonProps: fabric.IObjectOptions
    ) => {
      // TODO: Implementar visualização de áudio (waveform)
    },
    []
  );

  const renderShapeElement = useCallback(
    (
      canvas: fabric.Canvas,
      element: ShapeElement,
      commonProps: fabric.IObjectOptions
    ) => {
      let shape: fabric.Object | null = null;

      switch (element.shapeType) {
        case 'rectangle':
          shape = new fabric.Rect({
            ...commonProps,
            fill: element.fill,
            stroke: element.stroke,
            strokeWidth: element.strokeWidth,
          });
          break;
        case 'circle':
          shape = new fabric.Circle({
            ...commonProps,
            radius: Math.min(element.width, element.height) / 2,
            fill: element.fill,
            stroke: element.stroke,
            strokeWidth: element.strokeWidth,
          });
          break;
      }

      if (shape) {
        canvas.add(shape);
      }
    },
    []
  );

  // Handlers de eventos do canvas
  const handleSelectionCreated: FabricEventHandler = useCallback(
    e => {
      if (readOnly) return;

      const activeObject = e.target as FabricObject;
      if (!activeObject) return;

      const element = currentScene?.elements.find(
        el => el.id === activeObject.data?.id
      );
      if (element) {
        onElementSelect?.(element);
      }
    },
    [currentScene, onElementSelect, readOnly]
  );

  const handleSelectionUpdated: FabricEventHandler = useCallback(
    e => {
      if (readOnly) return;

      const activeObject = e.target as FabricObject;
      if (!activeObject) return;

      const element = currentScene?.elements.find(
        el => el.id === activeObject.data?.id
      );
      if (element) {
        onElementSelect?.(element);
      }
    },
    [currentScene, onElementSelect, readOnly]
  );

  const handleSelectionCleared = useCallback(() => {
    if (!readOnly) {
      onElementSelect?.(null);
    }
  }, [onElementSelect, readOnly]);

  const handleObjectModified: FabricEventHandler = useCallback(
    e => {
      if (readOnly) return;

      const activeObject = e.target as FabricObject;
      if (!activeObject || !currentScene) return;

      const element = currentScene.elements.find(
        el => el.id === activeObject.data?.id
      );
      if (!element) return;

      const updatedElement = {
        ...element,
        x: activeObject.left || 0,
        y: activeObject.top || 0,
        width: activeObject.getScaledWidth(),
        height: activeObject.getScaledHeight(),
        rotation: activeObject.angle || 0,
        scaleX: activeObject.scaleX || 1,
        scaleY: activeObject.scaleY || 1,
        opacity: activeObject.opacity || 1,
      };

      updateElement(updatedElement);
      onElementUpdate?.(updatedElement);
    },
    [currentScene, updateElement, onElementUpdate, readOnly]
  );

  const handleObjectMoving: FabricEventHandler = useCallback(
    e => {
      if (readOnly) return;
      // Implementar lógica de snapping e guias aqui
    },
    [readOnly]
  );

  const handleObjectScaling: FabricEventHandler = useCallback(
    e => {
      if (readOnly) return;
      // Implementar lógica de restrições de proporção aqui
    },
    [readOnly]
  );

  const handleObjectRotating: FabricEventHandler = useCallback(
    e => {
      if (readOnly) return;
      // Implementar lógica de snapping de rotação aqui
    },
    [readOnly]
  );

  // Expor métodos do canvas via ref
  useImperativeHandle(ref, () => ({
    getContext: () => canvasRef.current?.getContext('2d') || null,
    getElement: () => canvasRef.current,
    redraw: () => {
      if (fabricCanvasRef.current) {
        fabricCanvasRef.current.renderAll();
      }
    },
    resetTransform: () => {
      if (fabricCanvasRef.current) {
        fabricCanvasRef.current.setViewportTransform([1, 0, 0, 1, 0, 0]);
      }
    },
    zoomTo: (scale: number) => {
      if (fabricCanvasRef.current) {
        fabricCanvasRef.current.setZoom(scale);
      }
    },
    rotateTo: (angle: number) => {
      if (fabricCanvasRef.current) {
        fabricCanvasRef.current.getObjects().forEach(obj => {
          obj.rotate(angle);
        });
        fabricCanvasRef.current.renderAll();
      }
    },
    panTo: (x: number, y: number) => {
      if (fabricCanvasRef.current) {
        fabricCanvasRef.current.absolutePan(new fabric.Point(x, y));
      }
    },
  }));

  return (
    <div className="editor-canvas-container">
      <div className="canvas-controls">
        <div className="control-group">
          <button
            className="control-btn"
            onClick={() => selectedElement && bringToFront(selectedElement.id)}
            disabled={!selectedElement || readOnly}
            aria-label="Trazer para frente"
          >
            Trazer para frente
          </button>
          <button
            className="control-btn"
            onClick={() => selectedElement && sendToBack(selectedElement.id)}
            disabled={!selectedElement || readOnly}
            aria-label="Enviar para trás"
          >
            Enviar para trás
          </button>
          <button
            className="control-btn"
            onClick={() => selectedElement && copyElement(selectedElement.id)}
            disabled={!selectedElement || readOnly}
            aria-label="Copiar"
          >
            Copiar
          </button>
          <button
            className="control-btn"
            onClick={pasteElement}
            disabled={!clipboard || readOnly}
            aria-label="Colar"
          >
            Colar
          </button>
          <button
            className="control-btn danger"
            onClick={() => selectedElement && deleteElement(selectedElement.id)}
            disabled={!selectedElement || readOnly}
            aria-label="Excluir"
          >
            Excluir
          </button>
        </div>
      </div>
      <div className="canvas-wrapper">
        <canvas
          ref={canvasRef}
          className="editor-canvas"
          aria-label="Editor de Canvas"
          role="application"
        />
      </div>
    </div>
  );
});

EditorCanvas.displayName = 'EditorCanvas';

export default EditorCanvas;
