import React, { useState } from 'react'
import { useEditorStore } from '../../store/editorStore'
import './EditorControls.css'

export const EditorControls: React.FC = () => {
  const {
    currentTool,
    setCurrentTool,
    selectedObject,
    updateObject,
    undo,
    redo,
    clearCanvas,
    exportCanvas,
    canvasWidth,
    canvasHeight,
    setCanvasSize,
    backgroundColor,
    setBackgroundColor,
    zoom,
    setZoom
  } = useEditorStore()

  const [showProperties, setShowProperties] = useState(false)
  const [showCanvasSettings, setShowCanvasSettings] = useState(false)

  const tools = [
    { id: 'select', label: 'Selecionar', icon: '👆' },
    { id: 'text', label: 'Texto', icon: '📝' },
    { id: 'image', label: 'Imagem', icon: '🖼️' },
    { id: 'shape', label: 'Forma', icon: '⬜' },
    { id: 'draw', label: 'Desenhar', icon: '✏️' },
    { id: 'eraser', label: 'Apagar', icon: '🧽' }
  ] as const

  const canvasSizes = [
    { name: 'HD (1280x720)', width: 1280, height: 720 },
    { name: 'Full HD (1920x1080)', width: 1920, height: 1080 },
    { name: '4K (3840x2160)', width: 3840, height: 2160 },
    { name: 'Instagram (1080x1080)', width: 1080, height: 1080 },
    { name: 'Facebook (1200x630)', width: 1200, height: 630 },
    { name: 'Twitter (1200x675)', width: 1200, height: 675 }
  ]

  const colors = [
    '#000000', '#ffffff', '#ff0000', '#00ff00', '#0000ff',
    '#ffff00', '#ff00ff', '#00ffff', '#ffa500', '#800080',
    '#008000', '#800000', '#000080', '#808080', '#c0c0c0'
  ]

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const url = e.target?.result as string
        // Aqui você pode adicionar a imagem ao canvas
        console.log('Imagem carregada:', url)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleExport = () => {
    const dataURL = exportCanvas()
    if (dataURL) {
      const link = document.createElement('a')
      link.download = `canvas-export-${Date.now()}.png`
      link.href = dataURL
      link.click()
    }
  }

  return (
    <div className="editor-controls">
      {/* Barra de ferramentas principal */}
      <div className="controls-section">
        <h3>🛠️ Ferramentas</h3>
        <div className="tools-grid">
          {tools.map((tool) => (
            <button
              key={tool.id}
              className={`tool-button ${currentTool === tool.id ? 'active' : ''}`}
              onClick={() => setCurrentTool(tool.id)}
              data-tool={tool.id}
            >
              <span className="tool-icon">{tool.icon}</span>
              <span className="tool-label">{tool.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Controles de ação */}
      <div className="controls-section">
        <h3>⚡ Ações</h3>
        <div className="action-buttons">
          <button onClick={undo} className="action-button">
            ↩️ Desfazer
          </button>
          <button onClick={redo} className="action-button">
            ↪️ Refazer
          </button>
          <button onClick={clearCanvas} className="action-button danger">
            🗑️ Limpar
          </button>
          <button onClick={handleExport} className="action-button primary">
            💾 Exportar
          </button>
        </div>
      </div>

      {/* Configurações do canvas */}
      <div className="controls-section">
        <h3>⚙️ Configurações</h3>
        <div className="settings-grid">
          <button
            onClick={() => setShowCanvasSettings(!showCanvasSettings)}
            className="settings-toggle"
          >
            📐 Tamanho do Canvas
          </button>
          
          {showCanvasSettings && (
            <div className="settings-panel">
              <div className="size-presets">
                {canvasSizes.map((size) => (
                  <button
                    key={size.name}
                    onClick={() => setCanvasSize(size.width, size.height)}
                    className={`size-preset ${
                      canvasWidth === size.width && canvasHeight === size.height ? 'active' : ''
                    }`}
                  >
                    {size.name}
                  </button>
                ))}
              </div>
              
              <div className="custom-size">
                <label>
                  Largura:
                  <input
                    type="number"
                    value={canvasWidth}
                    onChange={(e) => setCanvasSize(Number(e.target.value), canvasHeight)}
                    min="100"
                    max="4000"
                  />
                </label>
                <label>
                  Altura:
                  <input
                    type="number"
                    value={canvasHeight}
                    onChange={(e) => setCanvasSize(canvasWidth, Number(e.target.value))}
                    min="100"
                    max="4000"
                  />
                </label>
              </div>
            </div>
          )}

          <div className="background-color">
            <label>Cor de Fundo:</label>
            <div className="color-picker">
              <input
                type="color"
                value={backgroundColor}
                onChange={(e) => setBackgroundColor(e.target.value)}
                className="color-input"
              />
              <div className="color-presets">
                {colors.map((color) => (
                  <button
                    key={color}
                    onClick={() => setBackgroundColor(color)}
                    className="color-preset"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="zoom-control">
            <label>Zoom: {Math.round(zoom * 100)}%</label>
            <input
              type="range"
              min="0.1"
              max="3"
              step="0.1"
              value={zoom}
              onChange={(e) => setZoom(Number(e.target.value))}
              className="zoom-slider"
            />
            <div className="zoom-buttons">
              <button onClick={() => setZoom(zoom * 0.9)}>🔍-</button>
              <button onClick={() => setZoom(1)}>100%</button>
              <button onClick={() => setZoom(zoom * 1.1)}>🔍+</button>
            </div>
          </div>
        </div>
      </div>

      {/* Propriedades do objeto selecionado */}
      {selectedObject && (
        <div className="controls-section">
          <h3>📋 Propriedades</h3>
          <div className="properties-panel">
            <div className="property-group">
              <label>Posição X:</label>
              <input
                type="number"
                value={selectedObject.properties.left}
                onChange={(e) => updateObject(selectedObject.id, { left: Number(e.target.value) })}
              />
            </div>
            
            <div className="property-group">
              <label>Posição Y:</label>
              <input
                type="number"
                value={selectedObject.properties.top}
                onChange={(e) => updateObject(selectedObject.id, { top: Number(e.target.value) })}
              />
            </div>
            
            <div className="property-group">
              <label>Largura:</label>
              <input
                type="number"
                value={selectedObject.properties.width}
                onChange={(e) => updateObject(selectedObject.id, { width: Number(e.target.value) })}
              />
            </div>
            
            <div className="property-group">
              <label>Altura:</label>
              <input
                type="number"
                value={selectedObject.properties.height}
                onChange={(e) => updateObject(selectedObject.id, { height: Number(e.target.value) })}
              />
            </div>
            
            <div className="property-group">
              <label>Rotação:</label>
              <input
                type="number"
                value={selectedObject.properties.angle}
                onChange={(e) => updateObject(selectedObject.id, { angle: Number(e.target.value) })}
                min="0"
                max="360"
              />
            </div>

            {selectedObject.type === 'text' && (
              <>
                <div className="property-group">
                  <label>Texto:</label>
                  <input
                    type="text"
                    value={selectedObject.properties.text || ''}
                    onChange={(e) => updateObject(selectedObject.id, { text: e.target.value })}
                  />
                </div>
                
                <div className="property-group">
                  <label>Tamanho da Fonte:</label>
                  <input
                    type="number"
                    value={selectedObject.properties.fontSize || 20}
                    onChange={(e) => updateObject(selectedObject.id, { fontSize: Number(e.target.value) })}
                    min="8"
                    max="200"
                  />
                </div>
                
                <div className="property-group">
                  <label>Cor do Texto:</label>
                  <input
                    type="color"
                    value={selectedObject.properties.fill || '#000000'}
                    onChange={(e) => updateObject(selectedObject.id, { fill: e.target.value })}
                  />
                </div>
              </>
            )}

            {selectedObject.type === 'shape' && (
              <>
                <div className="property-group">
                  <label>Cor de Preenchimento:</label>
                  <input
                    type="color"
                    value={selectedObject.properties.fill || '#ff0000'}
                    onChange={(e) => updateObject(selectedObject.id, { fill: e.target.value })}
                  />
                </div>
                
                <div className="property-group">
                  <label>Cor da Borda:</label>
                  <input
                    type="color"
                    value={selectedObject.properties.stroke || '#000000'}
                    onChange={(e) => updateObject(selectedObject.id, { stroke: e.target.value })}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Upload de arquivos */}
      <div className="controls-section">
        <h3>📁 Arquivos</h3>
        <div className="file-upload">
          <label className="upload-button">
            📤 Carregar Imagem
            <input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>
    </div>
  )
} 