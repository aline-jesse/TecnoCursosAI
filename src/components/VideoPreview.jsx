/**
 * Componente de Preview de Vídeo - TecnoCursos AI
 */

import React from 'react';
import { FiX, FiPlay, FiPause, FiSkipBack, FiSkipForward } from 'react-icons/fi';

const VideoPreview = ({ scenes, currentScene, onSceneChange, onClose, isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-900">
            Preview do Vídeo
          </h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            <FiX className="h-6 w-6" />
          </button>
        </div>

        {/* Preview Area */}
        <div className="p-6">
          <div className="bg-gray-100 rounded-lg p-8 text-center min-h-[400px] flex items-center justify-center">
            {scenes.length > 0 ? (
              <div className="text-center">
                <h4 className="text-xl font-medium text-gray-900 mb-4">
                  Cena {currentScene + 1} de {scenes.length}
                </h4>
                <p className="text-gray-600">
                  {scenes[currentScene]?.content || 'Conteúdo da cena'}
                </p>
              </div>
            ) : (
              <div className="text-center">
                <h4 className="text-xl font-medium text-gray-900 mb-4">
                  Preview
                </h4>
                <p className="text-gray-600">
                  Nenhuma cena disponível para preview
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Controls */}
        <div className="flex justify-center items-center space-x-4 p-4 border-t">
          <button
            onClick={() => onSceneChange(Math.max(0, currentScene - 1))}
            disabled={currentScene === 0}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:text-gray-300"
          >
            <FiSkipBack className="h-6 w-6" />
          </button>
          
          <button className="p-2 text-gray-600 hover:text-gray-900">
            <FiPlay className="h-6 w-6" />
          </button>
          
          <button
            onClick={() => onSceneChange(Math.min(scenes.length - 1, currentScene + 1))}
            disabled={currentScene === scenes.length - 1}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:text-gray-300"
          >
            <FiSkipForward className="h-6 w-6" />
          </button>
        </div>

        {/* Scene Navigation */}
        {scenes.length > 1 && (
          <div className="p-4 border-t">
            <div className="flex space-x-2 overflow-x-auto">
              {scenes.map((scene, index) => (
                <button
                  key={index}
                  onClick={() => onSceneChange(index)}
                  className={`px-3 py-1 rounded text-sm whitespace-nowrap ${
                    index === currentScene
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Cena {index + 1}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoPreview; 