/**
 * Componente de Workflow de Projetos - TecnoCursos AI
 */

import React, { useState } from 'react';
import {
  FiPlus,
  FiUpload,
  FiPlay,
  FiDownload,
  FiLogOut,
  FiUser,
  FiEdit3,
} from 'react-icons/fi';

const ProjectWorkflow = ({
  user,
  projects,
  onLogout,
  onFileUpload,
  onCreateProject,
  onUpdateProject,
  onDeleteProject,
  onGenerateVideo,
  onOpenPreview,
  isGenerating,
  isUploading,
  uploadProgress,
  videoUrl,
  videoError,
  onOpenEditor, // Nova prop para abrir o editor
}) => {
  const [selectedProject, setSelectedProject] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) return;

    try {
      await onCreateProject({ name: newProjectName });
      setNewProjectName('');
      setShowCreateModal(false);
    } catch (error) {
      console.error('Erro ao criar projeto:', error);
    }
  };

  const handleGenerateVideo = async () => {
    if (!selectedProject) return;

    try {
      await onGenerateVideo(selectedProject);
    } catch (error) {
      console.error('Erro ao gerar vídeo:', error);
    }
  };

  const handleOpenEditor = () => {
    if (onOpenEditor) {
      onOpenEditor();
    }
  };

  return (
    <div className='min-h-screen bg-gray-50'>
      {/* Header */}
      <header className='bg-white shadow'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex justify-between items-center py-6'>
            <div className='flex items-center'>
              <div className='h-10 w-10 bg-indigo-600 rounded-full flex items-center justify-center'>
                <span className='text-white text-xl font-bold'>TC</span>
              </div>
              <h1 className='ml-3 text-2xl font-bold text-gray-900'>
                TecnoCursos AI
              </h1>
            </div>

            <div className='flex items-center space-x-4'>
              <div className='flex items-center'>
                <FiUser className='h-5 w-5 text-gray-400' />
                <span className='ml-2 text-sm text-gray-700'>
                  {user?.email || 'Usuário'}
                </span>
              </div>
              <button
                onClick={onLogout}
                className='flex items-center px-3 py-2 text-sm text-gray-700 hover:text-gray-900'
              >
                <FiLogOut className='h-4 w-4 mr-2' />
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'>
        <div className='grid grid-cols-1 lg:grid-cols-3 gap-8'>
          {/* Sidebar - Lista de Projetos */}
          <div className='lg:col-span-1'>
            <div className='bg-white rounded-lg shadow p-6'>
              <div className='flex justify-between items-center mb-6'>
                <h2 className='text-lg font-semibold text-gray-900'>
                  Meus Projetos
                </h2>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className='flex items-center px-3 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700'
                >
                  <FiPlus className='h-4 w-4 mr-2' />
                  Novo Projeto
                </button>
              </div>

              <div className='space-y-3'>
                {projects.map(project => (
                  <div
                    key={project.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedProject?.id === project.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedProject(project)}
                  >
                    <h3 className='font-medium text-gray-900'>
                      {project.name}
                    </h3>
                    <p className='text-sm text-gray-500 mt-1'>
                      {project.description || 'Sem descrição'}
                    </p>
                    <p className='text-xs text-gray-400 mt-2'>
                      Criado em{' '}
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Area - Detalhes do Projeto */}
          <div className='lg:col-span-2'>
            {selectedProject ? (
              <div className='bg-white rounded-lg shadow p-6'>
                <div className='flex justify-between items-center mb-6'>
                  <h2 className='text-xl font-semibold text-gray-900'>
                    {selectedProject.name}
                  </h2>
                  <div className='flex space-x-3'>
                    <button
                      onClick={handleOpenEditor}
                      className='flex items-center px-4 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700'
                    >
                      <FiEdit3 className='h-4 w-4 mr-2' />
                      Abrir Editor
                    </button>
                    <button
                      onClick={() => onOpenPreview([])}
                      className='flex items-center px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700'
                    >
                      <FiPlay className='h-4 w-4 mr-2' />
                      Preview
                    </button>
                    <button
                      onClick={handleGenerateVideo}
                      disabled={isGenerating}
                      className='flex items-center px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50'
                    >
                      {isGenerating ? (
                        <>
                          <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2'></div>
                          Gerando...
                        </>
                      ) : (
                        <>
                          <FiPlay className='h-4 w-4 mr-2' />
                          Gerar Vídeo
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Upload Area */}
                <div className='border-2 border-dashed border-gray-300 rounded-lg p-8 text-center'>
                  <FiUpload className='mx-auto h-12 w-12 text-gray-400' />
                  <h3 className='mt-2 text-sm font-medium text-gray-900'>
                    Upload de Arquivo
                  </h3>
                  <p className='mt-1 text-sm text-gray-500'>
                    Arraste um arquivo PDF ou PPTX aqui, ou clique para
                    selecionar
                  </p>
                  <div className='mt-6'>
                    <input
                      type='file'
                      accept='.pdf,.pptx,.ppt'
                      onChange={e => {
                        const file = e.target.files[0];
                        if (file) onFileUpload(file);
                      }}
                      className='hidden'
                      id='file-upload'
                    />
                    <label
                      htmlFor='file-upload'
                      className='cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50'
                    >
                      Selecionar Arquivo
                    </label>
                  </div>

                  {isUploading && (
                    <div className='mt-4'>
                      <div className='w-full bg-gray-200 rounded-full h-2'>
                        <div
                          className='bg-blue-600 h-2 rounded-full transition-all'
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                      <p className='text-sm text-gray-600 mt-2'>
                        Upload em progresso: {uploadProgress}%
                      </p>
                    </div>
                  )}
                </div>

                {/* Video URL */}
                {videoUrl && (
                  <div className='mt-6 p-4 bg-green-50 border border-green-200 rounded-lg'>
                    <h4 className='text-sm font-medium text-green-800'>
                      Vídeo Gerado com Sucesso!
                    </h4>
                    <p className='text-sm text-green-600 mt-1'>
                      URL: {videoUrl}
                    </p>
                    <button
                      onClick={() => window.open(videoUrl, '_blank')}
                      className='mt-2 flex items-center px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700'
                    >
                      <FiDownload className='h-4 w-4 mr-1' />
                      Baixar Vídeo
                    </button>
                  </div>
                )}

                {/* Error */}
                {videoError && (
                  <div className='mt-6 p-4 bg-red-50 border border-red-200 rounded-lg'>
                    <h4 className='text-sm font-medium text-red-800'>
                      Erro na Geração do Vídeo
                    </h4>
                    <p className='text-sm text-red-600 mt-1'>{videoError}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className='bg-white rounded-lg shadow p-12 text-center'>
                <FiPlus className='mx-auto h-12 w-12 text-gray-400' />
                <h3 className='mt-2 text-sm font-medium text-gray-900'>
                  Nenhum projeto selecionado
                </h3>
                <p className='mt-1 text-sm text-gray-500'>
                  Selecione um projeto da lista ou crie um novo para começar
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className='fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50'>
          <div className='relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white'>
            <div className='mt-3'>
              <h3 className='text-lg font-medium text-gray-900 mb-4'>
                Criar Novo Projeto
              </h3>
              <input
                type='text'
                placeholder='Nome do projeto'
                value={newProjectName}
                onChange={e => setNewProjectName(e.target.value)}
                className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
              />
              <div className='flex justify-end space-x-3 mt-6'>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className='px-4 py-2 text-sm text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300'
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateProject}
                  className='px-4 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700'
                >
                  Criar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectWorkflow;
