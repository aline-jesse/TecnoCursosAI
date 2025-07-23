import React from 'react';
import { EditorProvider } from '../../contexts/EditorContext';
import { useEditorStore } from '../../store/editorStore';
import { EditorElement, Scene, ToolType } from '../../types/editor';
import './Editor.css';
import EditorCanvas from './EditorCanvas';
import { Sidebar } from './Sidebar';
import { StatusBar } from './StatusBar';
import { Toolbar } from './Toolbar';

export interface EditorProps {
  initialScene?: Scene;
  onSave?: (scene: Scene) => void;
  onExport?: (data: Scene) => void;
  readOnly?: boolean;
}

export const Editor: React.FC<EditorProps> = ({
  initialScene: _initialScene,
  onSave,
  onExport,
  readOnly = false,
}) => {
  const {
    currentScene: scene,
    selectedElement,
    updateElement,
    deleteElement,
    undo: undoAction,
    redo: redoAction,
    history,
  } = useEditorStore();

  const canvasRef = React.useRef<any>(null); // Usando any temporariamente para resolver o erro de tipo

  const [activeTool, setActiveTool] = React.useState<ToolType>('select');
  const [canUndo, setCanUndo] = React.useState(false);
  const [canRedo, setCanRedo] = React.useState(false);

  React.useEffect(() => {
    setCanUndo(history.past.length > 0);
    setCanRedo(history.future.length > 0);
  }, [history]);

  const handleToolChange = (_tool: ToolType) => {
    setActiveTool(_tool);
  };

  const handleElementSelect = (_element: EditorElement | null) => {
    // TODO: Implementar seleção de elemento usando o store quando disponível
  };

  const handleElementUpdate = (element: EditorElement) => {
    updateElement(element);
  };

  const handleKeyDown = React.useCallback(
    (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'z':
            if (e.shiftKey) {
              redoAction();
            } else {
              undoAction();
            }
            e.preventDefault();
            break;
          case 's':
            if (onSave && scene) {
              onSave(scene);
            }
            e.preventDefault();
            break;
          case 'e':
            if (onExport && scene) {
              onExport(scene);
            }
            e.preventDefault();
            break;
          case '+':
          case '=':
            // TODO: Implementar zoom in quando disponível no store
            e.preventDefault();
            break;
          case '-':
            // TODO: Implementar zoom out quando disponível no store
            e.preventDefault();
            break;
          case '0':
            // TODO: Implementar reset zoom quando disponível no store
            e.preventDefault();
            break;
        }
      } else if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedElement) {
          deleteElement(selectedElement.id);
        }
      }
    },
    [
      selectedElement,
      deleteElement,
      undoAction,
      redoAction,
      onSave,
      onExport,
      scene,
    ]
  );

  React.useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  React.useEffect(() => {
    if (onSave && scene) {
      onSave(scene);
    }
  }, [scene, onSave]);

  React.useEffect(() => {
    if (onExport && scene) {
      onExport(scene);
    }
  }, [scene, onExport]);

  const handleUndo = React.useCallback(() => {
    undoAction();
  }, [undoAction]);

  const handleRedo = React.useCallback(() => {
    redoAction();
  }, [redoAction]);

  const handleZoomIn = React.useCallback(() => {
    // TODO: Implementar zoom in quando disponível no store
  }, []);

  const handleZoomOut = React.useCallback(() => {
    // TODO: Implementar zoom out quando disponível no store
  }, []);

  const handleResetZoom = React.useCallback(() => {
    // TODO: Implementar reset zoom quando disponível no store
  }, []);

  return (
    <EditorProvider
      value={{
        scene,
        selectedElement,
        history: {
          canUndo,
          canRedo,
        },
        tools: {
          activeTool,
        },
        zoom: {
          scale: 1,
        },
        readOnly,
      }}
    >
      <div className="editor">
        <Toolbar
          activeTool={activeTool}
          onToolChange={handleToolChange}
          canUndo={canUndo}
          canRedo={canRedo}
          onUndo={handleUndo}
          onRedo={handleRedo}
          zoom={1}
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onResetZoom={handleResetZoom}
          readOnly={readOnly}
        />
        <div className="editor-main">
          <Sidebar
            selectedElement={selectedElement}
            onElementUpdate={handleElementUpdate}
            readOnly={readOnly}
          />
          <EditorCanvas
            ref={canvasRef}
            width={1920}
            height={1080}
            backgroundColor="#ffffff"
            onElementSelect={handleElementSelect}
            onElementUpdate={handleElementUpdate}
          />
        </div>
        <StatusBar
          zoom={1}
          tool={activeTool}
          selectedElement={selectedElement}
        />
      </div>
    </EditorProvider>
  );
};
