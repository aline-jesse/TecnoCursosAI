import React, { useState } from 'react'
import EditorCanvas from '../EditorCanvas'
import { EditorControls } from './EditorControls'
import './Editor.css'

export const Editor: React.FC = () => {
  const [showControls, setShowControls] = useState(true)

  return (
    <div className="editor-container">
      <div className="editor-header">
        <h1>🎨 Editor de Canvas - TecnoCursos AI</h1>
        <div className="header-controls">
          <button
            onClick={() => setShowControls(!showControls)}
            className="toggle-controls-btn"
          >
            {showControls ? '👁️ Ocultar Controles' : '⚙️ Mostrar Controles'}
          </button>
        </div>
      </div>
      
      <div className="editor-main">
        <div className="editor-canvas-area">
          <EditorCanvas />
        </div>
        
        {showControls && (
          <div className="editor-controls-area">
            <EditorControls />
          </div>
        )}
      </div>
      
      <div className="editor-footer">
        <div className="footer-info">
          <span>🖱️ Clique e arraste para mover objetos</span>
          <span>🔍 Use a roda do mouse para zoom</span>
          <span>⌨️ Delete para remover objetos selecionados</span>
        </div>
        <div className="footer-status">
          <span>✅ Pronto para editar</span>
        </div>
      </div>
    </div>
  )
} 