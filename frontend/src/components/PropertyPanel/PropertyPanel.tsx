import React from 'react';

/**
 * PropertyPanel
 * Painel lateral para edição de propriedades do elemento selecionado no editor de vídeo.
 * Permite editar posição, tamanho, cor, fonte, animações, etc.
 */
const PropertyPanel: React.FC = () => {
  return (
    <aside className="w-72 p-4 bg-white border-l border-gray-200 h-full">
      <h2 className="text-lg font-bold mb-4">Propriedades</h2>
      {/* Campos de edição de propriedades aqui */}
      <div className="text-gray-500">Selecione um elemento para editar suas propriedades.</div>
    </aside>
  );
};

export default PropertyPanel;
