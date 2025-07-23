import React from 'react';

/**
 * ContextMenu
 * Menu de contexto exibido ao clicar com o botão direito no canvas.
 * Permite ações rápidas como duplicar, deletar, editar, etc.
 */
const ContextMenu: React.FC = () => {
  return (
    <ul className="absolute bg-white border rounded shadow-md p-2">
      <li className="p-2 hover:bg-gray-100 cursor-pointer">Duplicar</li>
      <li className="p-2 hover:bg-gray-100 cursor-pointer">Deletar</li>
      <li className="p-2 hover:bg-gray-100 cursor-pointer">Editar</li>
    </ul>
  );
};

export default ContextMenu;
