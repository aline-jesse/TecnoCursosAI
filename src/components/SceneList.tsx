/**
 * SceneList - Componente para listar e gerenciar cenas
 * Permite adicionar, editar, deletar e reordenar cenas
 */

import React, { useState, useCallback } from 'react'
import { useEditorStore } from '../store/editorStore'
import { useTemplates, useTemplateGallery } from '../hooks/useTemplates'
import TemplateGallery from './TemplateGallery'
import { SceneTemplate } from '../types/template'
import { 
  PlusIcon,
  RectangleStackIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline'
import './SceneList.css'
import { VideoPreviewModal } from './VideoPreviewModal';

// Hooks personalizados do store
const useScenes = () => useEditorStore(state => state.scenes)
const useActiveScene = () => useEditorStore(state => state.activeScene)
export const SceneList: React.FC = () => {
  // Estados locais para UI
  const [isAddingScene, setIsAddingScene] = useState(false);
  const [isEditingScene, setIsEditingScene] = useState<string | null>(null);
  const [newSceneName, setNewSceneName] = useState('');
  const [newSceneDuration, setNewSceneDuration] = useState(5);
  const [editSceneName, setEditSceneName] = useState('');
  const [editSceneDuration, setEditSceneDuration] = useState(5);
  const [previewSceneId, setPreviewSceneId] = useState<string | null>(null);
  
  // Hooks da store Zustand
  const scenes = useScenes();
  const activeScene = useActiveScene();
  const { 
    addScene, 
    updateScene, 
    deleteScene, 
    duplicateScene, 
    setActiveScene,
    reorderScenes 
  } = useEditorStore();

  // Hooks de templates
  const { applyTemplate, loading: templateLoading } = useTemplates();
  const {
    isGalleryOpen,
    openGallery,
    closeGallery,
    selectTemplate
  } = useTemplateGallery();

  /**
   * Manipula adição de nova cena
   */
  const handleAddScene = useCallback(() => {
    if (!newSceneName.trim()) return;

    addScene({
      name: newSceneName.trim(),
      duration: newSceneDuration,
      assets: [],
    });

    // Limpa formulário
    setNewSceneName('');
    setNewSceneDuration(5);
    setIsAddingScene(false);
  }, [addScene, newSceneName, newSceneDuration]);

  /**
   * Manipula criação de cena com template
   */
  const handleCreateFromTemplate = useCallback(() => {
    openGallery();
  }, [openGallery]);

  /**
   * Manipula seleção de template na galeria
   */
  const handleSelectTemplate = useCallback((template: SceneTemplate) => {
    try {
      const result = applyTemplate(template);
      
      if (result.success) {
        console.log('Template aplicado com sucesso:', result.message);
        closeGallery();
        
        // Opcional: mostrar notificação de sucesso
        // showNotification(result.message, 'success');
      } else {
        console.error('Erro ao aplicar template:', result.errors);
        // showNotification(result.message || 'Erro ao aplicar template', 'error');
      }
    } catch (error) {
      console.error('Erro inesperado ao aplicar template:', error);
    }
  }, [applyTemplate, closeGallery]);

  /**
   * Manipula edição de cena
   */
  const handleEditScene = useCallback((sceneId: string) => {
    const scene = scenes.find(s => s.id === sceneId);
    if (!scene) return;

    setEditSceneName(scene.name);
    setEditSceneDuration(scene.duration);
    setIsEditingScene(sceneId);
  }, [scenes]);

  /**
   * Salva edição de cena
   */
  const handleSaveEdit = useCallback(() => {
    if (!isEditingScene || !editSceneName.trim()) return;

    updateScene(isEditingScene, {
      name: editSceneName.trim(),
      duration: editSceneDuration,
    });

    setIsEditingScene(null);
    setEditSceneName('');
    setEditSceneDuration(5);
  }, [updateScene, isEditingScene, editSceneName, editSceneDuration]);

  /**
   * Cancela edição de cena
   */
  const handleCancelEdit = useCallback(() => {
    setIsEditingScene(null);
    setEditSceneName('');
    setEditSceneDuration(5);
  }, []);

  /**
   * Manipula duplicação de cena
   */
  const handleDuplicateScene = useCallback((sceneId: string) => {
    duplicateScene(sceneId);
  }, [duplicateScene]);

  /**
   * Manipula exclusão de cena
   */
  const handleDeleteScene = useCallback((sceneId: string) => {
    if (window.confirm('Tem certeza que deseja excluir esta cena?')) {
      deleteScene(sceneId);
    }
  }, [deleteScene]);

  /**
   * Manipula seleção de cena
   */
  const handleSelectScene = useCallback((sceneId: string) => {
    setActiveScene(sceneId);
  }, [setActiveScene]);

  /**
   * Manipula drag & drop para reordenação
   */
  const handleDragStart = useCallback((e: React.DragEvent, index: number) => {
    e.dataTransfer.setData('text/plain', index.toString());
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    const dragIndex = parseInt(e.dataTransfer.getData('text/plain'));
    
    if (dragIndex !== dropIndex) {
      const newScenes = [...scenes];
      const [draggedScene] = newScenes.splice(dragIndex, 1);
      newScenes.splice(dropIndex, 0, draggedScene);
      reorderScenes(newScenes);
    }
  }, [reorderScenes, scenes]);

  // Handler para regenerar narração
  const handleRegenerateNarration = useCallback(async (sceneId: string) => {
    const scene = scenes.find(s => s.id === sceneId);
    if (!scene) return '';
    
    try {
      const response = await fetch('/api/regenerate-narration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: scene.text,
          sceneId
        })
      });
      
      const data = await response.json();
      return data.narrationUrl;
    } catch (error) {
      console.error('Erro ao regenerar narração:', error);
      return '';
    }
  }, [scenes]);

  return (
    <div className="scene-list">
      {/* Header */}
      <div className="scene-list-header">
        <h3>Cenas</h3>
        <div className="header-actions">
          <button 
            className="template-btn"
            onClick={handleCreateFromTemplate}
            title="Criar cena com template"
            disabled={templateLoading}
          >
            <SparklesIcon className="w-4 h-4" />
            Templates
          </button>
          <button 
            className="add-scene-btn"
            onClick={() => setIsAddingScene(true)}
            title="Adicionar cena vazia"
          >
            <PlusIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Formulário de adição */}
      {isAddingScene && (
        <div className="add-scene-form">
          <input
            type="text"
            placeholder="Nome da cena"
            value={newSceneName}
            onChange={(e) => setNewSceneName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddScene()}
            autoFocus
          />
          <input
            type="number"
            placeholder="Duração (s)"
            value={newSceneDuration}
            onChange={(e) => setNewSceneDuration(Number(e.target.value))}
            min="1"
            max="300"
          />
          <div className="form-buttons">
            <button onClick={handleAddScene}>Adicionar</button>
            <button onClick={() => setIsAddingScene(false)}>Cancelar</button>
          </div>
        </div>
      )}

      {/* Lista de cenas */}
      <div className="scenes-container">
        {scenes.length === 0 ? (
          <div className="empty-scenes">
            <p>Nenhuma cena criada</p>
            <p>Crie sua primeira cena para começar</p>
          </div>
        ) : (
          scenes.map((scene, index) => (
            <div
              key={scene.id}
              className={`scene-item ${activeScene?.id === scene.id ? 'active' : ''}`}
              draggable
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, index)}
            >
              {/* Conteúdo da cena */}
              <div 
                className="scene-content"
                onClick={() => handleSelectScene(scene.id)}
              >
                {/* Thumbnail da cena */}
                <div className="scene-thumbnail">
                  {scene.background ? (
                    <img src={scene.background} alt={scene.name} />
                  ) : (
                    <div className="scene-placeholder">
                      {scene.assets.length > 0 ? '📹' : '🎬'}
                    </div>
                  )}
                </div>

                {/* Informações da cena */}
                <div className="scene-info">
                  {isEditingScene === scene.id ? (
                    <div className="edit-form">
                      <input
                        type="text"
                        value={editSceneName}
                        onChange={(e) => setEditSceneName(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSaveEdit()}
                        autoFocus
                      />
                      <input
                        type="number"
                        value={editSceneDuration}
                        onChange={(e) => setEditSceneDuration(Number(e.target.value))}
                        min="1"
                        max="300"
                      />
                    </div>
                  ) : (
                    <>
                      <h4>{scene.name}</h4>
                      <p>{scene.duration}s • {scene.assets.length} assets</p>
                    </>
                  )}
                </div>
              </div>

              {/* Controles da cena */}
              <div className="scene-controls">
                {isEditingScene === scene.id ? (
                  <>
                    <button 
                      className="control-btn save"
                      onClick={handleSaveEdit}
                      title="Salvar"
                    >
                      ✓
                    </button>
                    <button 
                      className="control-btn cancel"
                      onClick={handleCancelEdit}
                      title="Cancelar"
                    >
                      ✕
                    </button>
                  </>
                ) : (
                  <>
                    <button 
                      className="control-btn edit"
                      onClick={() => handleEditScene(scene.id)}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button 
                      className="control-btn duplicate"
                      onClick={() => handleDuplicateScene(scene.id)}
                      title="Duplicar"
                    >
                      📋
                    </button>
                    <button 
                      className="control-btn delete"
                      onClick={() => handleDeleteScene(scene.id)}
                      title="Excluir"
                    >
                      🗑️
                    </button>
                    <button
                      onClick={() => setPreviewSceneId(scene.id)}
                      className="control-btn preview"
                      title="Preview da cena"
                    >
                      <span className="material-icons">preview</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Estatísticas */}
      {scenes.length > 0 && (
        <div className="scene-stats">
          <p>Total: {scenes.length} cena{scenes.length !== 1 ? 's' : ''}</p>
          <p>Duração total: {scenes.reduce((total, scene) => total + scene.duration, 0)}s</p>
        </div>
      )}

      {/* Galeria de Templates */}
      <TemplateGallery 
        isOpen={isGalleryOpen}
        onClose={closeGallery}
        onSelectTemplate={handleSelectTemplate}
        showCategories={true}
      />

      {/* Modal de Preview */}
      {previewSceneId && (
        <VideoPreviewModal
          isOpen={true}
          onClose={() => setPreviewSceneId(null)}
          sceneId={previewSceneId}
          onSave={(config) => {
            // Atualizar configurações da cena
            updateScene(previewSceneId, {
              ...scenes.find(s => s.id === previewSceneId),
              duration: config.duration,
              transition: config.transition,
              animations: config.animations,
              audio: config.audio
            });
            setPreviewSceneId(null);
          }}
          onRegenerateNarration={handleRegenerateNarration}
        />
      )}
    </div>
  );
};

export default SceneList; 