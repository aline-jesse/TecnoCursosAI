// src/App.jsx
import React, { useState } from 'react';
import './App.css';

// Componente principal simplificado
function App() {
  const [message, setMessage] = useState('');
  const [projects, setProjects] = useState([]);

  const testBackend = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/health');
      const data = await response.json();
      setMessage(`Backend funcionando! Status: ${data.status}`);
    } catch (error) {
      setMessage(`Erro: ${error.message}`);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/projects/');
      const data = await response.json();
      setProjects(data);
      setMessage('Projetos carregados com sucesso!');
    } catch (error) {
      setMessage(`Erro ao carregar projetos: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 text-white text-center">
      <header className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-5xl font-bold mb-4 drop-shadow-lg">
          🎬 TecnoCursos AI
        </h1>
        <p className="text-xl mb-8 opacity-90">
          Sistema de Criação de Vídeos Educacionais com IA
        </p>

        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <button
            onClick={testBackend}
            className="px-6 py-3 bg-green-500 hover:bg-green-600 rounded-lg font-semibold min-w-[180px] transition-all transform hover:-translate-y-1 hover:shadow-lg"
          >
            Testar Backend
          </button>
          <button
            onClick={loadProjects}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold min-w-[180px] transition-all transform hover:-translate-y-1 hover:shadow-lg"
          >
            Carregar Projetos
          </button>
        </div>

        {message && (
          <div className="bg-white/20 backdrop-blur-md p-4 rounded-lg mb-6 border border-white/30">
            {message}
          </div>
        )}

        {projects.length > 0 && (
          <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl mb-8 border border-white/20">
            <h3 className="text-xl font-semibold mb-4">Projetos:</h3>
            <ul className="text-left">
              {projects.map((project, index) => (
                <li
                  key={index}
                  className="py-2 border-b border-white/10 last:border-0"
                >
                  {project.name || project.title || `Projeto ${index + 1}`}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl mb-8 border border-white/20">
          <h3 className="text-xl font-semibold mb-4">
            Funcionalidades Disponíveis:
          </h3>
          <ul className="text-left">
            <li className="py-2 border-b border-white/10">
              ✅ Backend FastAPI funcionando
            </li>
            <li className="py-2 border-b border-white/10">
              ✅ Frontend React operacional
            </li>
            <li className="py-2 border-b border-white/10">
              ✅ Sistema de autenticação
            </li>
            <li className="py-2 border-b border-white/10">
              ✅ Upload de arquivos
            </li>
            <li className="py-2 border-b border-white/10">
              ✅ Geração de vídeos
            </li>
            <li className="py-2 border-b border-white/10 last:border-0">
              ✅ APIs RESTful completas
            </li>
          </ul>
        </div>

        <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl mb-8 border border-white/20">
          <h3 className="text-xl font-semibold mb-4">Links Úteis:</h3>
          <ul className="text-left">
            <li className="py-2 border-b border-white/10">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white hover:text-yellow-300 hover:underline font-medium"
              >
                📖 API Documentation
              </a>
            </li>
            <li className="py-2 border-b border-white/10">
              <a
                href="http://localhost:8000/api/health"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white hover:text-yellow-300 hover:underline font-medium"
              >
                ❤️ Health Check
              </a>
            </li>
            <li className="py-2 border-b border-white/10 last:border-0">
              <a
                href="http://localhost:8000/api/status"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white hover:text-yellow-300 hover:underline font-medium"
              >
                📊 System Status
              </a>
            </li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
