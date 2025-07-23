import React, { useState, useEffect } from 'react';

/**
 * App - Componente principal da aplicação
 * Integra todos os componentes do editor de vídeo
 */
function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState('editor');

  useEffect(() => {
    // Simula carregamento inicial
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  }, []);

  if (isLoading) {
    return (
      <div
        className='loading'
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          fontFamily: 'Arial, sans-serif',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }}
      >
        <h1>🚀 TecnoCursos AI - Editor de Vídeo</h1>
        <p>Carregando aplicação...</p>
        <div style={{ marginTop: '20px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              border: '4px solid rgba(255,255,255,0.3)',
              borderTop: '4px solid white',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }}
          ></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className='error'
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          fontFamily: 'Arial, sans-serif',
          background: '#f44336',
          color: 'white',
        }}
      >
        <h2>❌ Erro</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div
      className='App'
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: 'Arial, sans-serif',
      }}
    >
      {/* Header */}
      <header
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h1 style={{ margin: 0 }}>🎬 TecnoCursos AI - Editor de Vídeo</h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            onClick={() => setCurrentView('editor')}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '4px',
              background: currentView === 'editor' ? 'white' : 'transparent',
              color: currentView === 'editor' ? '#667eea' : 'white',
              cursor: 'pointer',
            }}
          >
            Editor
          </button>
          <button
            onClick={() => setCurrentView('preview')}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '4px',
              background: currentView === 'preview' ? 'white' : 'transparent',
              color: currentView === 'preview' ? '#667eea' : 'white',
              cursor: 'pointer',
            }}
          >
            Preview
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div
        className='editor-container'
        style={{
          flex: 1,
          display: 'flex',
          background: '#f5f5f5',
        }}
      >
        {/* Sidebar */}
        <div
          className='editor-sidebar'
          style={{
            width: '300px',
            background: 'white',
            borderRight: '1px solid #e0e0e0',
            padding: '1rem',
          }}
        >
          <div className='scene-list' style={{ marginBottom: '2rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>📹 Cenas</h3>
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
              }}
            >
              <div
                style={{
                  padding: '0.5rem',
                  background: '#f0f0f0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Cena 1 - Introdução
              </div>
              <div
                style={{
                  padding: '0.5rem',
                  background: '#f0f0f0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Cena 2 - Desenvolvimento
              </div>
              <div
                style={{
                  padding: '0.5rem',
                  background: '#f0f0f0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Cena 3 - Conclusão
              </div>
            </div>
          </div>

          <div className='asset-panel'>
            <h3 style={{ margin: '0 0 1rem 0' }}>🎨 Assets</h3>
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
              }}
            >
              <div
                style={{
                  padding: '0.5rem',
                  background: '#e3f2fd',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                🎵 Áudio 1
              </div>
              <div
                style={{
                  padding: '0.5rem',
                  background: '#e8f5e8',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                🖼️ Imagem 1
              </div>
              <div
                style={{
                  padding: '0.5rem',
                  background: '#fff3e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                📹 Vídeo 1
              </div>
            </div>
          </div>
        </div>

        {/* Main Editor Area */}
        <div
          className='editor-main'
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div
            className='editor-canvas'
            style={{
              flex: 1,
              background: 'white',
              margin: '1rem',
              borderRadius: '8px',
              padding: '2rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <h2 style={{ margin: '0 0 1rem 0' }}>🎬 Editor Canvas</h2>
            <p style={{ textAlign: 'center', color: '#666' }}>
              Área de edição de vídeo com IA
              <br />
              Arraste e solte elementos aqui
            </p>
            <div
              style={{
                marginTop: '2rem',
                padding: '2rem',
                border: '2px dashed #ccc',
                borderRadius: '8px',
                textAlign: 'center',
                color: '#999',
              }}
            >
              📁 Arraste arquivos aqui
            </div>
          </div>

          <div
            className='editor-timeline'
            style={{
              height: '150px',
              background: 'white',
              margin: '0 1rem 1rem 1rem',
              borderRadius: '8px',
              padding: '1rem',
              border: '1px solid #e0e0e0',
            }}
          >
            <h3 style={{ margin: '0 0 1rem 0' }}>⏱️ Timeline</h3>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                style={{
                  padding: '0.5rem 1rem',
                  border: 'none',
                  borderRadius: '4px',
                  background: '#667eea',
                  color: 'white',
                  cursor: 'pointer',
                }}
              >
                ▶️ Play
              </button>
              <button
                style={{
                  padding: '0.5rem 1rem',
                  border: 'none',
                  borderRadius: '4px',
                  background: '#f44336',
                  color: 'white',
                  cursor: 'pointer',
                }}
              >
                ⏹️ Stop
              </button>
              <button
                style={{
                  padding: '0.5rem 1rem',
                  border: 'none',
                  borderRadius: '4px',
                  background: '#4caf50',
                  color: 'white',
                  cursor: 'pointer',
                }}
              >
                💾 Salvar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
