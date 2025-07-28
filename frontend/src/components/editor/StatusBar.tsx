import React from 'react';
import { EditorElement, ToolType } from '../../types';
import './StatusBar.css';

interface StatusBarProps {
  zoom: number;
  tool: ToolType;
  selectedElement: EditorElement | null;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  zoom,
  tool,
  selectedElement,
}) => {
  const formatTool = (tool: ToolType): string => {
    const toolLabels: Record<ToolType, string> = {
      select: 'Selecionar',
      hand: 'Mover',
      text: 'Texto',
      rectangle: 'Retângulo',
      circle: 'Círculo',
      line: 'Linha',
      draw: 'Desenhar',
      erase: 'Apagar',
      image: 'Imagem',
      video: 'Vídeo',
      audio: 'Áudio',
    };
    return toolLabels[tool] || tool;
  };

  const getElementInfo = (element: EditorElement): string => {
    if (!element) return '';

    const typeLabels: Record<EditorElement['type'], string> = {
      text: 'Texto',
      image: 'Imagem',
      character: 'Personagem',
      video: 'Vídeo',
      audio: 'Áudio',
      shape: 'Forma',
    };

    const type = typeLabels[element.type] || element.type;
    const position = `(${Math.round(element.x)}, ${Math.round(element.y)})`;
    const size = `${Math.round(element.width)}×${Math.round(element.height)}`;

    let additionalInfo = '';
    switch (element.type) {
      case 'text':
        additionalInfo = ` "${element.text.substring(0, 20)}${element.text.length > 20 ? '...' : ''}"`;
        break;
      case 'image':
      case 'character':
      case 'video':
      case 'audio':
        additionalInfo = ` "${element.src.split('/').pop()}"`;
        break;
      case 'shape':
        additionalInfo = ` (${element.shapeType})`;
        break;
    }

    return `${type} ${position} ${size}${additionalInfo}`;
  };

  return (
    <div className="status-bar" role="status" aria-live="polite">
      <div className="status-item">
        <span className="status-label">Zoom:</span>
        <span
          className="status-value"
          aria-label={`Zoom ${Math.round(zoom * 100)}%`}
        >
          {Math.round(zoom * 100)}%
        </span>
      </div>

      <div className="status-item">
        <span className="status-label">Ferramenta:</span>
        <span
          className="status-value"
          aria-label={`Ferramenta atual: ${formatTool(tool)}`}
        >
          {formatTool(tool)}
        </span>
      </div>

      {selectedElement && (
        <div className="status-item">
          <span className="status-label">Selecionado:</span>
          <span
            className="status-value"
            aria-label={`Elemento selecionado: ${getElementInfo(selectedElement)}`}
          >
            {getElementInfo(selectedElement)}
          </span>
        </div>
      )}
    </div>
  );
};
