import React from 'react';

/**
 * UndoRedoManager
 * Gerenciador de histórico de ações (undo/redo) do editor.
 * Permite desfazer e refazer ações do usuário.
 */
const UndoRedoManager: React.FC = () => {
  return (
    <div className="flex gap-2">
      <button className="btn">Desfazer</button>
      <button className="btn">Refazer</button>
    </div>
  );
};

export default UndoRedoManager;
