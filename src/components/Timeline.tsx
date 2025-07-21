// src/components/Timeline.tsx
import React from 'react';
import { useEditorStore } from '../store/editorStore';
import './Timeline.css';

/**
 * Timeline: Componente para exibir e gerenciar a linha do tempo das cenas.
 *
 * - Exibe blocos representando cada cena.
 * - A largura do bloco é proporcional à duração da cena.
 * - Placeholder para edição de duração e outras interações.
 */
const Timeline: React.FC = () => {
  const { scenes } = useEditorStore();

  // Fator de escala para a largura dos blocos da cena (pixels por segundo)
  const scale = 20;

  return (
    <div className="timeline">
      <div className="timeline-track">
        {scenes.map((scene) => (
          <div
            key={scene.id}
            className="timeline-scene-block"
            style={{ width: `${scene.duration * scale}px` }}
          >
            <span className="scene-block-name">{scene.name}</span>
            <span className="scene-block-duration">{scene.duration}s</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Timeline; 