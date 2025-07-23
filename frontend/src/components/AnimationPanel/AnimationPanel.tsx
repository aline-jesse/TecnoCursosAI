import React from 'react';

/**
 * AnimationPanel
 * Painel para configuração de animações de entrada, saída e efeitos nos elementos.
 */
const AnimationPanel: React.FC = () => {
  return (
    <section className="p-4 bg-white border-t border-gray-200">
      <h2 className="text-lg font-bold mb-4">Animações</h2>
      {/* Campos para seleção de animações */}
      <div className="text-gray-500">Selecione um elemento para animar.</div>
    </section>
  );
};

export default AnimationPanel;
