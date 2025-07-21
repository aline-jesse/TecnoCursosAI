// src/components/SceneList.tsx
import React from 'react';
import { useEditorStore } from '../store/editorStore';
import './SceneList.css';

/**
 * SceneList: Componente para gerenciar a lista de cenas.
 *
 * - Exibe a lista de cenas do projeto.
 * - Permite adicionar, deletar e selecionar cenas.
 * - A reordenação (drag-and-drop) pode ser adicionada no futuro.
 */
const SceneList: React.FC = () => {
  const { scenes, addScene, deleteScene, setCurrentSceneId, currentSceneId } = useEditorStore();

  const handleAddScene = () => {
    const newScene = {
      id: `scene-${Date.now()}`,
      name: `Scene ${scenes.length + 1}`,
      duration: 5, // 5 segundos
      elements: [],
      thumbnail: `https://via.placeholder.com/150/f0f0f0/000000?text=Scene+${scenes.length + 1}`,
    };
    addScene(newScene);
    setCurrentSceneId(newScene.id);
  };

  return (
    <div className="scene-list">
      <h2>Scenes</h2>
      <div className="scenes-container">
        {scenes.map((scene, index) => (
          <div
            key={scene.id}
            className={`scene-item ${scene.id === currentSceneId ? 'active' : ''}`}
            onClick={() => setCurrentSceneId(scene.id)}
          >
            <span className="scene-index">{index + 1}</span>
            <img src={scene.thumbnail} alt={scene.name} className="scene-thumbnail" />
            <span className="scene-name">{scene.name}</span>
            <button
              className="delete-scene-btn"
              onClick={(e) => {
                e.stopPropagation();
                deleteScene(scene.id);
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>
      <button className="add-scene-btn" onClick={handleAddScene}>
        + Add Scene
      </button>
    </div>
  );
};

export default SceneList; 