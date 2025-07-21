/**
 * Componente de Download de Vídeo - TecnoCursos AI
 */

import React from 'react';
import { FiDownload, FiArrowLeft, FiCheck } from 'react-icons/fi';

const VideoDownload = ({ videoUrl, onDownload, onBack }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <FiCheck className="h-8 w-8 text-green-600" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Vídeo Gerado com Sucesso!
          </h2>
          
          <p className="text-gray-600 mb-6">
            Seu vídeo foi gerado e está pronto para download.
          </p>

          <div className="space-y-4">
            <button
              onClick={onDownload}
              className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <FiDownload className="h-5 w-5 mr-2" />
              Baixar Vídeo
            </button>
            
            <button
              onClick={onBack}
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              <FiArrowLeft className="h-5 w-5 mr-2" />
              Voltar aos Projetos
            </button>
          </div>

          {videoUrl && (
            <div className="mt-6 p-4 bg-gray-50 rounded-md">
              <p className="text-sm text-gray-600">
                URL do vídeo: {videoUrl}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoDownload;
