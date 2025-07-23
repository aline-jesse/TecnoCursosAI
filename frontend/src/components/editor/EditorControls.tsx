import {
  DocumentTextIcon,
  EyeIcon,
  EyeSlashIcon,
  PhotoIcon,
  SpeakerWaveIcon,
  TrashIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import React, { useState } from 'react';
import './EditorControls.css';

type ElementType = 'text' | 'image' | 'audio' | 'avatar';
type TabType = 'elements' | 'layers' | 'settings';
type CanvasSize = '1920x1080' | '1280x720' | '800x600' | '1080x1080';

interface ElementTypeConfig {
  id: ElementType;
  label: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  color: string;
}

interface Layer {
  id: string;
  name: string;
  visible: boolean;
  locked: boolean;
}

interface EditorControlsProps {
  onAddElement?: (type: ElementType) => void;
  onToggleLayer?: (layerId: string) => void;
  onDeleteSelected?: () => void;
  onCanvasSizeChange?: (size: CanvasSize) => void;
  onBackgroundColorChange?: (color: string) => void;
  onSnapToGridChange?: (enabled: boolean) => void;
  onShowRulersChange?: (enabled: boolean) => void;
}

interface TabButtonProps {
  tab: TabType;
  label: string;
  isActive: boolean;
  onClick: (tab: TabType) => void;
}

const elementTypes: ElementTypeConfig[] = [
  { id: 'text', label: 'Texto', icon: DocumentTextIcon, color: '#3b82f6' },
  { id: 'image', label: 'Imagem', icon: PhotoIcon, color: '#10b981' },
  { id: 'audio', label: 'Áudio', icon: SpeakerWaveIcon, color: '#f59e0b' },
  { id: 'avatar', label: 'Avatar', icon: UserIcon, color: '#8b5cf6' },
];

const mockLayers: Layer[] = [
  { id: 'layer-1', name: 'Fundo', visible: true, locked: false },
  { id: 'layer-2', name: 'Texto Principal', visible: true, locked: false },
  { id: 'layer-3', name: 'Avatar', visible: false, locked: true },
];

const TabButton: React.FC<TabButtonProps> = ({
  tab,
  label,
  isActive,
  onClick,
}) => (
  <button
    onClick={() => onClick(tab)}
    className={`tab-button ${isActive ? 'active' : ''}`}
    aria-pressed={isActive}
  >
    {label}
  </button>
);

export const EditorControls: React.FC<EditorControlsProps> = ({
  onAddElement,
  onToggleLayer,
  onDeleteSelected,
  onCanvasSizeChange,
  onBackgroundColorChange,
  onSnapToGridChange,
  onShowRulersChange,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('elements');
  const [canvasSize, setCanvasSize] = useState<CanvasSize>('1920x1080');
  const [backgroundColor, setBackgroundColor] = useState('#ffffff');
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [showRulers, setShowRulers] = useState(true);

  const handleAddElement = (elementType: ElementType) => {
    onAddElement?.(elementType);
  };

  const handleCanvasSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSize = e.target.value as CanvasSize;
    setCanvasSize(newSize);
    onCanvasSizeChange?.(newSize);
  };

  const handleBackgroundColorChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newColor = e.target.value;
    setBackgroundColor(newColor);
    onBackgroundColorChange?.(newColor);
  };

  const handleSnapToGridChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = e.target.checked;
    setSnapToGrid(enabled);
    onSnapToGridChange?.(enabled);
  };

  const handleShowRulersChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = e.target.checked;
    setShowRulers(enabled);
    onShowRulersChange?.(enabled);
  };

  return (
    <div className="editor-controls">
      {/* Header com tabs */}
      <div className="controls-header">
        <h3>🎛️ Controles do Editor</h3>

        <div className="tab-buttons">
          <TabButton
            tab="elements"
            label="Elementos"
            isActive={activeTab === 'elements'}
            onClick={setActiveTab}
          />
          <TabButton
            tab="layers"
            label="Camadas"
            isActive={activeTab === 'layers'}
            onClick={setActiveTab}
          />
          <TabButton
            tab="settings"
            label="Config"
            isActive={activeTab === 'settings'}
            onClick={setActiveTab}
          />
        </div>
      </div>

      {/* Conteúdo dos tabs */}
      <div className="controls-content">
        {/* Tab: Elementos */}
        {activeTab === 'elements' && (
          <div className="elements-tab">
            <h4>Adicionar Elementos</h4>

            <div className="element-grid">
              {elementTypes.map(element => {
                const IconComponent = element.icon;
                return (
                  <button
                    key={element.id}
                    onClick={() => handleAddElement(element.id)}
                    className="element-button"
                    style={
                      {
                        '--element-color': element.color,
                      } as React.CSSProperties
                    }
                  >
                    <IconComponent className="element-icon" />
                    {element.label}
                  </button>
                );
              })}
            </div>

            <div className="delete-button-container">
              <button onClick={onDeleteSelected} className="delete-button">
                <TrashIcon className="delete-icon" />
                Excluir Selecionado
              </button>
            </div>
          </div>
        )}

        {/* Tab: Camadas */}
        {activeTab === 'layers' && (
          <div className="layers-tab">
            <h4>Gerenciar Camadas</h4>

            <div className="layers-list">
              {mockLayers.map(layer => (
                <div key={layer.id} className="layer-item">
                  <span className="layer-name">{layer.name}</span>

                  <div className="layer-actions">
                    <button
                      onClick={() => onToggleLayer?.(layer.id)}
                      className={`visibility-button ${layer.visible ? 'visible' : ''}`}
                      title={
                        layer.visible ? 'Ocultar camada' : 'Mostrar camada'
                      }
                    >
                      {layer.visible ? (
                        <EyeIcon className="visibility-icon" />
                      ) : (
                        <EyeSlashIcon className="visibility-icon" />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab: Configurações */}
        {activeTab === 'settings' && (
          <div className="settings-tab">
            <h4>Configurações</h4>

            <div className="settings-list">
              {/* Canvas Size */}
              <div className="setting-group">
                <label htmlFor="canvas-size">Tamanho do Canvas</label>
                <select
                  id="canvas-size"
                  value={canvasSize}
                  onChange={handleCanvasSizeChange}
                >
                  <option value="1920x1080">1920x1080 (Full HD)</option>
                  <option value="1280x720">1280x720 (HD)</option>
                  <option value="800x600">800x600 (4:3)</option>
                  <option value="1080x1080">1080x1080 (Quadrado)</option>
                </select>
              </div>

              {/* Background Color */}
              <div className="setting-group">
                <label htmlFor="background-color">Cor de Fundo</label>
                <input
                  id="background-color"
                  type="color"
                  value={backgroundColor}
                  onChange={handleBackgroundColorChange}
                />
              </div>

              {/* Snap to Grid */}
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={snapToGrid}
                    onChange={handleSnapToGridChange}
                  />
                  Snap to Grid
                </label>
              </div>

              {/* Show Rulers */}
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={showRulers}
                    onChange={handleShowRulersChange}
                  />
                  Mostrar Réguas
                </label>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EditorControls;
