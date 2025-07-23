import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import EditorCanvas from '../components/editor/EditorCanvas';
import ScenePreview from '../components/editor/ScenePreview';
import { useEditorStore } from '../store/editorStore';

interface EditorProps {
  projectId?: string;
}

const Editor: React.FC<EditorProps> = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const {
    scenes,
    currentSceneId,
    setCurrentSceneId,
    loadProject,
    saveProject,
  } = useEditorStore();

  useEffect(() => {
    if (projectId) {
      loadProject(projectId);
    }
  }, [projectId, loadProject]);

  const handleSave = async () => {
    try {
      await saveProject();
      // Mostrar feedback de sucesso
    } catch (error) {
      console.error('Erro ao salvar projeto:', error);
      // Mostrar feedback de erro
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  return (
    <div className='min-h-screen bg-gray-100'>
      {/* Header */}
      <header className='bg-white shadow'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex justify-between items-center py-4'>
            <div className='flex items-center'>
              <button
                onClick={handleBack}
                className='mr-4 text-gray-600 hover:text-gray-900'
              >
                ← Voltar
              </button>
              <h1 className='text-xl font-semibold text-gray-900'>
                Editor de Vídeo
              </h1>
            </div>
            <button
              onClick={handleSave}
              className='px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700'
            >
              Salvar Projeto
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className='max-w-7xl mx-auto py-6 sm:px-6 lg:px-8'>
        <div className='flex gap-6'>
          {/* Editor Canvas */}
          <div className='flex-1 bg-white rounded-lg shadow overflow-hidden'>
            <EditorCanvas width={1280} height={720} backgroundColor='#f0f0f0' />
          </div>

          {/* Scene List */}
          <div className='w-64 bg-white p-4 rounded-lg shadow'>
            <h3 className='text-lg font-medium mb-4'>Cenas</h3>
            <div className='space-y-4'>
              {scenes.map((scene, index) => (
                <div
                  key={scene.id}
                  className={`cursor-pointer p-2 rounded ${
                    scene.id === currentSceneId
                      ? 'bg-indigo-100 border-indigo-500'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setCurrentSceneId(scene.id)}
                >
                  <ScenePreview scene={scene} />
                  <p className='mt-2 text-sm text-gray-600'>Cena {index + 1}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Editor;
