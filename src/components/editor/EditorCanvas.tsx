// src/components/editor/EditorCanvas.tsx
import React from 'react';
import { Stage, Layer, Text, Image as KonvaImage } from 'react-konva';
import { useEditorStore } from '../../store/editorStore';
import { EditorElement } from '../../types/editor';
import './EditorCanvas.css';
import useImage from 'use-image';

/**
 * Componente para renderizar um único elemento no canvas.
 * Lida com a renderização de diferentes tipos de elementos (texto, imagem).
 */
const CanvasElement: React.FC<{ element: EditorElement }> = ({ element }) => {
  const [img] = useImage(element.type === 'image' ? element.src : '');

  switch (element.type) {
    case 'text':
      return <Text {...element} />;
    case 'image':
      return <KonvaImage image={img} {...element} draggable />;
    case 'character':
      // Placeholder para renderização de personagem
      return <KonvaImage image={img} {...element} draggable />;
    default:
      return null;
  }
};

/**
 * EditorCanvas: A área principal de edição drag-and-drop.
 *
 * - Usa Konva.js para renderizar o canvas.
 * - Exibe os elementos da cena atual.
 * - Permite arrastar e soltar elementos.
 */
const EditorCanvas: React.FC = () => {
  const { scenes, currentSceneId, updateElement } = useEditorStore();
  const currentScene = scenes.find((s) => s.id === currentSceneId);

  const handleDragEnd = (e: any, elementId: string) => {
    if (!currentSceneId) return;
    const { x, y } = e.target.position();
    updateElement(currentSceneId, elementId, { x, y });
  };

  return (
    <div className="editor-canvas-container">
      <Stage width={window.innerWidth - 500} height={window.innerHeight - 150}>
        <Layer>
          {currentScene?.elements.map((element) => (
            <CanvasElement
              key={element.id}
              element={element}
              // onDragEnd={(e) => handleDragEnd(e, element.id)}
            />
          ))}
        </Layer>
      </Stage>
    </div>
  );
};

export default EditorCanvas; 