import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleOpenEditor = () => {
    navigate('/editor');
  };

  const handleOpenProjects = () => {
    navigate('/projects');
  };

  return (
    <div className='min-h-screen bg-gray-50'>
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
              <span className='text-sm text-gray-700'>
                Bem-vindo, {user?.email || 'Usuário'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main>
        <div className='max-w-7xl mx-auto py-6 sm:px-6 lg:px-8'>
          <div className='px-4 py-6 sm:px-0'>
            <div className='grid grid-cols-1 gap-6 sm:grid-cols-2'>
              {/* Card do Editor */}
              <div className='bg-white overflow-hidden shadow rounded-lg'>
                <div className='px-4 py-5 sm:p-6'>
                  <h3 className='text-lg font-medium text-gray-900'>
                    Editor de Vídeos
                  </h3>
                  <p className='mt-1 text-sm text-gray-500'>
                    Crie e edite vídeos profissionais com nossa ferramenta
                    intuitiva
                  </p>
                  <button
                    onClick={handleOpenEditor}
                    className='mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                  >
                    Abrir Editor
                  </button>
                </div>
              </div>

              {/* Card de Projetos */}
              <div className='bg-white overflow-hidden shadow rounded-lg'>
                <div className='px-4 py-5 sm:p-6'>
                  <h3 className='text-lg font-medium text-gray-900'>
                    Meus Projetos
                  </h3>
                  <p className='mt-1 text-sm text-gray-500'>
                    Gerencie seus projetos e acompanhe o progresso
                  </p>
                  <button
                    onClick={handleOpenProjects}
                    className='mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                  >
                    Painel de Projetos
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
