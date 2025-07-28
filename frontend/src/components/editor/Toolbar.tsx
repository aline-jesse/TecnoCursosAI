import React from 'react';
import { ToolConfig, ToolType } from '../../types/editor';
import { Divider } from '../common/Divider';
import { IconButton } from '../common/IconButton';
import { Tooltip } from '../common/Tooltip';
import './Toolbar.css';

const TOOLS: ToolConfig[] = [
  {
    id: 'select',
    icon: 'cursor',
    name: 'select',
    label: 'Selecionar',
    shortcut: 'V',
    group: 'selection',
  },
  {
    id: 'hand',
    icon: 'hand',
    name: 'hand',
    label: 'Mover',
    shortcut: 'H',
    group: 'selection',
  },
  { id: 'text', icon: 'text', name: 'text', label: 'Texto', shortcut: 'T', group: 'shapes' },
  {
    id: 'rectangle',
    icon: 'rectangle',
    name: 'rectangle',
    label: 'Retângulo',
    shortcut: 'R',
    group: 'shapes',
  },
  {
    id: 'circle',
    icon: 'circle',
    name: 'circle',
    label: 'Círculo',
    shortcut: 'C',
    group: 'shapes',
  },
  { id: 'line', icon: 'line', name: 'line', label: 'Linha', shortcut: 'L', group: 'shapes' },
  {
    id: 'image',
    icon: 'image',
    name: 'image',
    label: 'Imagem',
    shortcut: 'I',
    group: 'media',
  },
  { id: 'video', icon: 'video', name: 'video', label: 'Vídeo', shortcut: 'V', group: 'media' },
  { id: 'audio', icon: 'audio', name: 'audio', label: 'Áudio', shortcut: 'A', group: 'media' },
];

interface ToolbarProps {
  activeTool: ToolType;
  onToolChange: (tool: ToolType) => void;
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  readOnly?: boolean;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  activeTool,
  onToolChange,
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  zoom,
  onZoomIn,
  onZoomOut,
  onResetZoom,
  readOnly = false,
}) => {
  const renderToolGroup = (group: ToolConfig['group']) => {
    const tools = TOOLS.filter(tool => tool.group === group);
    if (tools.length === 0) return null;

    return (
      <>
        <div className="toolbar-group">
          {tools.map(tool => (
            <Tooltip
              key={tool.id}
              content={`${tool.label} (${tool.shortcut})`}
              position="bottom"
            >
              <IconButton
                icon={tool.icon as any}
                active={activeTool === tool.id}
                onClick={() => onToolChange(tool.id)}
                disabled={
                  readOnly && tool.id !== 'hand' && tool.id !== 'select'
                }
                aria-label={tool.label}
              />
            </Tooltip>
          ))}
        </div>
        <Divider />
      </>
    );
  };

  return (
    <div className="toolbar" role="toolbar" aria-label="Barra de ferramentas">
      {renderToolGroup('selection')}
      {renderToolGroup('shapes')}
      {renderToolGroup('media')}

      <div className="toolbar-group">
        <Tooltip content="Desfazer (Ctrl+Z)" position="bottom">
          <IconButton
            icon="undo"
            onClick={onUndo}
            disabled={!canUndo || readOnly}
            aria-label="Desfazer"
          />
        </Tooltip>
        <Tooltip content="Refazer (Ctrl+Shift+Z)" position="bottom">
          <IconButton
            icon="redo"
            onClick={onRedo}
            disabled={!canRedo || readOnly}
            aria-label="Refazer"
          />
        </Tooltip>
      </div>

      <Divider />

      <div className="toolbar-group">
        <Tooltip content="Diminuir Zoom (Ctrl+-)" position="bottom">
          <IconButton
            icon="zoom-out"
            onClick={onZoomOut}
            disabled={zoom <= 0.1}
            aria-label="Diminuir Zoom"
          />
        </Tooltip>
        <div className="zoom-display" role="status" aria-label="Nível de zoom">
          {Math.round(zoom * 100)}%
        </div>
        <Tooltip content="Aumentar Zoom (Ctrl++)" position="bottom">
          <IconButton
            icon="zoom-in"
            onClick={onZoomIn}
            disabled={zoom >= 5}
            aria-label="Aumentar Zoom"
          />
        </Tooltip>
        <Tooltip content="Resetar Zoom (Ctrl+0)" position="bottom">
          <IconButton
            icon="zoom-reset"
            onClick={onResetZoom}
            disabled={zoom === 1}
            aria-label="Resetar Zoom"
          />
        </Tooltip>
      </div>
    </div>
  );
};
