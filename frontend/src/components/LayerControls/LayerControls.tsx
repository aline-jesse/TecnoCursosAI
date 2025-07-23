import React from 'react';

/**
 * LayerControls
 * Controles de camadas para manipular a ordem dos elementos no canvas.
 * Permite trazer para frente, enviar para trás, avançar e recuar elementos.
 */
const LayerControls: React.FC = () => {
  return (
    <div className="flex flex-col gap-2">
      <button className="btn">Trazer para frente</button>
      <button className="btn">Enviar para trás</button>
      <button className="btn">Avançar</button>
      <button className="btn">Recuar</button>
    </div>
  );
};

export default LayerControls;
