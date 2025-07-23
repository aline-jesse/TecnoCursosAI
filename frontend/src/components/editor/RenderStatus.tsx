/**
 * Componente RenderStatus - Simplificado
 * Status de renderização de vídeo
 * TecnoCursos AI - Dashboard de Projetos
 */

import React, { useEffect, useState } from 'react';
import { useEditorStore } from '../../store/editorStore';

interface RenderStatusProps {
  onClose: () => void;
}

export function RenderStatus({ onClose }: RenderStatusProps) {
  const [progress, setProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(120);

  // Simular progresso para demonstração
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + Math.random() * 10;
      });
      setEstimatedTime(prev => Math.max(prev - 5, 0));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleCancel = () => {
    onClose();
  };

  const handleDownload = () => {
    alert('Download iniciado!');
    onClose();
  };

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
      <div className='bg-white rounded-lg p-6 w-full max-w-md'>
        <h3 className='text-lg font-semibold mb-4 text-center'>
          Renderizando Vídeo
        </h3>

        {/* Barra de progresso */}
        <div className='mb-4'>
          <div className='flex justify-between text-sm text-gray-600 mb-2'>
            <span>Progresso</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className='w-full bg-gray-200 rounded-full h-2'>
            <div
              className='bg-blue-600 h-2 rounded-full transition-all duration-500'
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
        </div>

        {/* Informações */}
        <div className='text-sm text-gray-600 text-center mb-6'>
          {progress < 100 ? (
            <>
              <p>Tempo estimado: {Math.ceil(estimatedTime / 60)} minutos</p>
              <p className='mt-1'>Processando cenas e efeitos...</p>
            </>
          ) : (
            <p className='text-green-600 font-semibold'>
              ✅ Renderização concluída!
            </p>
          )}
        </div>

        {/* Ações */}
        <div className='flex justify-end gap-3'>
          {progress < 100 ? (
            <button
              onClick={handleCancel}
              className='px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors'
            >
              Cancelar
            </button>
          ) : (
            <>
              <button
                onClick={handleDownload}
                className='px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors'
              >
                Baixar Vídeo
              </button>
              <button
                onClick={onClose}
                className='px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors'
              >
                Fechar
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
