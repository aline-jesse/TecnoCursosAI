// src/components/Toolbar.tsx
import React from 'react';
import {
  FaUndo,
  FaRedo,
  FaCopy,
  FaTrash,
  FaAlignLeft,
  FaAlignCenter,
  FaAlignRight,
} from 'react-icons/fa';
import './Toolbar.css';

/**
 * Toolbar: Barra de ferramentas com ações rápidas para o editor.
 *
 * - Ações de desfazer e refazer (placeholders).
 * - Ações de copiar, colar e deletar (placeholders).
 * - Controles de alinhamento de texto (placeholders).
 */
const Toolbar: React.FC = () => {
  return (
    <div className="toolbar">
      <div className="toolbar-group">
        <button className="toolbar-button" title="Undo">
          <FaUndo />
        </button>
        <button className="toolbar-button" title="Redo">
          <FaRedo />
        </button>
      </div>
      <div className="toolbar-group">
        <button className="toolbar-button" title="Copy">
          <FaCopy />
        </button>
        <button className="toolbar-button" title="Delete">
          <FaTrash />
        </button>
      </div>
      <div className="toolbar-group">
        <button className="toolbar-button" title="Align Left">
          <FaAlignLeft />
        </button>
        <button className="toolbar-button" title="Align Center">
          <FaAlignCenter />
        </button>
        <button className="toolbar-button" title="Align Right">
          <FaAlignRight />
        </button>
      </div>
    </div>
  );
};

export default Toolbar; 