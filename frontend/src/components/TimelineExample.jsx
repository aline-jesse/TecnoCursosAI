/**
 * TimelineExample.jsx - Exemplo de Uso do Timeline Avançado
 *
 * Este componente demonstra como usar o Timeline.jsx com dados reais
 * e todas as funcionalidades implementadas.
 *
 * Funcionalidades demonstradas:
 * - Integração com dados de projeto
 * - Gerenciamento de estado de cenas
 * - Controle de camadas
 * - Callbacks de eventos
 * - Interface completa de edição
 */

import React, { useState, useEffect } from 'react';
import Timeline from './Timeline';
import { projectService } from '../services/api';

const TimelineExample = ({ projectId }) => {
  // Estados principais
  const [scenes, setScenes] = useState([]);
  const [selectedScene, setSelectedScene] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Carregar cenas do projeto
  useEffect(() => {
    loadProjectScenes();
  }, [projectId]);

  /**
   * Carregar cenas do projeto
   */
  const loadProjectScenes = async () => {
    try {
      setLoading(true);
      const projectData = await projectService.getProject(projectId);
      setScenes(projectData.scenes || []);
      setError(null);
    } catch (err) {
      console.error('❌ Erro ao carregar cenas:', err);
      setError('Erro ao carregar cenas do projeto');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Atualizar cenas quando houver mudanças
   */
  const handleSceneUpdate = async updatedScenes => {
    try {
      // Atualizar no backend
      await projectService.updateProjectScenes(projectId, updatedScenes);

      // Atualizar estado local
      setScenes(updatedScenes);

      console.log('✅ Cenas atualizadas com sucesso');
    } catch (err) {
      console.error('❌ Erro ao atualizar cenas:', err);
      // Reverter em caso de erro
      loadProjectScenes();
    }
  };

  /**
   * Selecionar uma cena
   */
  const handleSceneSelect = scene => {
    setSelectedScene(scene);
    console.log('🎯 Cena selecionada:', scene.title);

    // Aqui você pode integrar com o EditorCanvas
    // updateEditorCanvas(scene);
  };

  /**
   * Atualizar camadas (elementos)
   */
  const handleLayerUpdate = (elementId, type, value) => {
    console.log('🎨 Camada atualizada:', { elementId, type, value });

    // Atualizar elemento específico
    const updatedScenes = scenes.map(scene => {
      if (scene.elements) {
        const updatedElements = scene.elements.map(element => {
          if (element.id === elementId) {
            return {
              ...element,
              [type === 'visibility'
                ? 'visible'
                : type === 'lock'
                  ? 'locked'
                  : 'order']: value,
            };
          }
          return element;
        });
        return { ...scene, elements: updatedElements };
      }
      return scene;
    });

    setScenes(updatedScenes);

    // Notificar outros componentes sobre a mudança
    // updateElementInCanvas(elementId, type, value);
  };

  /**
   * Adicionar nova cena
   */
  const addNewScene = () => {
    const newScene = {
      id: `scene-${Date.now()}`,
      title: `Cena ${scenes.length + 1}`,
      duration: 10,
      elements: [],
    };

    const updatedScenes = [...scenes, newScene];
    handleSceneUpdate(updatedScenes);
  };

  /**
   * Remover cena selecionada
   */
  const removeSelectedScene = () => {
    if (!selectedScene) return;

    const updatedScenes = scenes.filter(scene => scene.id !== selectedScene.id);
    handleSceneUpdate(updatedScenes);
    setSelectedScene(null);
  };

  // Estados de loading e erro
  if (loading) {
    return (
      <div className='flex items-center justify-center h-64'>
        <div className='text-center'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto'></div>
          <p className='mt-4 text-gray-600'>Carregando timeline...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='flex items-center justify-center h-64'>
        <div className='text-center'>
          <div className='text-red-500 text-4xl mb-4'>⚠️</div>
          <p className='text-red-600 font-medium'>{error}</p>
          <button
            onClick={loadProjectScenes}
            className='mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600'
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {/* Cabeçalho com controles */}
      <div className='bg-white rounded-lg shadow p-4'>
        <div className='flex items-center justify-between'>
          <div>
            <h2 className='text-xl font-bold text-gray-900'>Editor de Vídeo</h2>
            <p className='text-sm text-gray-600'>
              Projeto: {projectId} • {scenes.length} cenas
            </p>
          </div>

          <div className='flex space-x-2'>
            <button
              onClick={addNewScene}
              className='px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors'
            >
              ➕ Nova Cena
            </button>

            {selectedScene && (
              <button
                onClick={removeSelectedScene}
                className='px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors'
              >
                🗑️ Remover Cena
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Timeline */}
      <Timeline
        projectId={projectId}
        scenes={scenes}
        onSceneUpdate={handleSceneUpdate}
        onSceneSelect={handleSceneSelect}
        selectedSceneId={selectedScene?.id}
        onLayerUpdate={handleLayerUpdate}
      />

      {/* Informações da cena selecionada */}
      {selectedScene && (
        <div className='bg-white rounded-lg shadow p-4'>
          <h3 className='text-lg font-semibold text-gray-900 mb-2'>
            Cena Selecionada: {selectedScene.title}
          </h3>

          <div className='grid grid-cols-2 gap-4 text-sm'>
            <div>
              <span className='font-medium text-gray-700'>ID:</span>
              <span className='ml-2 text-gray-600'>{selectedScene.id}</span>
            </div>

            <div>
              <span className='font-medium text-gray-700'>Duração:</span>
              <span className='ml-2 text-gray-600'>
                {selectedScene.duration}s
              </span>
            </div>

            <div>
              <span className='font-medium text-gray-700'>Elementos:</span>
              <span className='ml-2 text-gray-600'>
                {selectedScene.elements?.length || 0}
              </span>
            </div>

            <div>
              <span className='font-medium text-gray-700'>Tipo:</span>
              <span className='ml-2 text-gray-600'>
                {selectedScene.type || 'Padrão'}
              </span>
            </div>
          </div>

          {/* Lista de elementos da cena */}
          {selectedScene.elements && selectedScene.elements.length > 0 && (
            <div className='mt-4'>
              <h4 className='font-medium text-gray-700 mb-2'>Elementos:</h4>
              <div className='space-y-1'>
                {selectedScene.elements.map((element, index) => (
                  <div
                    key={element.id}
                    className='flex items-center justify-between p-2 bg-gray-50 rounded text-sm'
                  >
                    <span className='font-medium'>#{index + 1}</span>
                    <span className='flex-1 mx-2'>
                      {element.name || `Elemento ${index + 1}`}
                    </span>
                    <span className='text-gray-500'>{element.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Estado vazio */}
      {scenes.length === 0 && (
        <div className='bg-white rounded-lg shadow p-8 text-center'>
          <div className='text-6xl mb-4'>🎬</div>
          <h3 className='text-xl font-semibold text-gray-900 mb-2'>
            Nenhuma cena criada
          </h3>
          <p className='text-gray-600 mb-4'>
            Comece criando sua primeira cena para editar o vídeo
          </p>
          <button
            onClick={addNewScene}
            className='px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors'
          >
            ➕ Criar Primeira Cena
          </button>
        </div>
      )}
    </div>
  );
};

export default TimelineExample;
