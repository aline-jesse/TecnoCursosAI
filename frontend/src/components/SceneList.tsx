// src/components/SceneList.tsx
import React from 'react';
import { useEditorStore } from '../store/editorStore';
import { Scene } from '../types/editor';
import './SceneList.css';
// Adicionar react-beautiful-dnd se ainda não estiver instalado
// npm install react-beautiful-dnd

import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from '@hello-pangea/dnd';

const SceneList: React.FC = () => {
  const {
    history,
    currentSceneId,
    setCurrentSceneId,
    addScene,
    deleteScene,
    reorderScenes,
    updateScene,
  } = useEditorStore();
  const scenes = history.present;

  const handleAddScene = () => {
    const newScene: Scene = {
      id: `scene-${Date.now()}`,
      name: `Cena ${scenes.length + 1}`,
      duration: 5,
      elements: [],
      thumbnail: 'https://via.placeholder.com/150',
      background: {
        type: 'color',
        value: '#ffffff',
      },
    };
    addScene(newScene);
  };

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) {
      return;
    }
    const items = Array.from(scenes);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    // Atualizar as cenas reordenadas no store
    items.forEach((scene, index) => {
      updateScene(scene.id, { ...scene });
    });
  };

  return (
    <div className='scene-list-panel'>
      <h2>Cenas</h2>
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId='scenes'>
          {provided => (
            <div
              {...provided.droppableProps}
              ref={provided.innerRef}
              className='scene-list'
            >
              {scenes.map((scene, index) => (
                <Draggable key={scene.id} draggableId={scene.id} index={index}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className={`scene-item ${
                        scene.id === currentSceneId ? 'active' : ''
                      } ${snapshot.isDragging ? 'dragging' : ''}`}
                      onClick={() => setCurrentSceneId(scene.id)}
                    >
                      <img
                        src={scene.thumbnail}
                        alt={scene.name}
                        className='scene-thumbnail'
                      />
                      <span className='scene-name'>{scene.name}</span>
                      <button
                        className='delete-scene-btn'
                        onClick={e => {
                          e.stopPropagation();
                          deleteScene(scene.id);
                        }}
                      >
                        ×
                      </button>
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
      <div className='scene-actions'>
        <button onClick={handleAddScene} className='add-scene-btn'>
          Adicionar Cena
        </button>
      </div>
    </div>
  );
};

export default SceneList;
