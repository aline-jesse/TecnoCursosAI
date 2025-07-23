import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Project {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  scenes: number;
}

const ProjectList = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      // TODO: Implementar chamada real à API
      const response = await fetch('/api/projects');
      const data = await response.json();
      setProjects(data);
    } catch (err) {
      setError('Erro ao carregar projetos');
      console.error('Erro ao carregar projetos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenProject = (projectId: string) => {
    navigate(`/editor/${projectId}`);
  };

  const handleCreateProject = () => {
    navigate('/editor');
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
        <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600'></div>
      </div>
    );
  }

  return (
    <div className='min-h-screen bg-gray-50'>
      <header className='bg-white shadow'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex justify-between items-center py-6'>
            <div className='flex items-center'>
              <button
                onClick={handleBack}
                className='mr-4 text-gray-600 hover:text-gray-900'
              >
                ← Voltar
              </button>
              <h1 className='text-2xl font-bold text-gray-900'>
                Meus Projetos
              </h1>
            </div>
            <button
              onClick={handleCreateProject}
              className='px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700'
            >
              Novo Projeto
            </button>
          </div>
        </div>
      </header>

      <main className='max-w-7xl mx-auto py-6 sm:px-6 lg:px-8'>
        {error && (
          <div className='mb-4 p-4 bg-red-100 text-red-700 rounded-md'>
            {error}
          </div>
        )}

        <div className='bg-white shadow overflow-hidden sm:rounded-md'>
          <ul className='divide-y divide-gray-200'>
            {projects.map(project => (
              <li key={project.id}>
                <div
                  className='px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer'
                  onClick={() => handleOpenProject(project.id)}
                >
                  <div className='flex items-center justify-between'>
                    <div className='flex-1'>
                      <h3 className='text-lg font-medium text-indigo-600'>
                        {project.name}
                      </h3>
                      <p className='mt-1 text-sm text-gray-500'>
                        {project.scenes} cenas • Última atualização:{' '}
                        {new Date(project.updatedAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className='ml-4'>
                      <span className='text-gray-400'>→</span>
                    </div>
                  </div>
                </div>
              </li>
            ))}

            {projects.length === 0 && !loading && (
              <li className='px-4 py-8 text-center text-gray-500'>
                Nenhum projeto encontrado. Crie um novo projeto para começar!
              </li>
            )}
          </ul>
        </div>
      </main>
    </div>
  );
};

export default ProjectList;
