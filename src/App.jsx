import React, { useEffect, useState } from 'react';
import { Editor } from './components/editor/Editor';

/**
 * App - Componente principal do editor de vídeo
 * Layout inspirado no Animaker com organização profissional
 * 
 * Estrutura:
 * - Toolbar fixa no topo
 * - AssetPanel à esquerda (assets e bibliotecas)
 * - EditorCanvas no centro (área de edição)
 * - SceneList à direita (gerenciamento de cenas)
 * - Timeline na parte inferior (controle de tempo)
 */
function App() {
  // Estados principais da aplicação
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking'); // 'checking', 'online', 'offline'
  const [retryCount, setRetryCount] = useState(0);
  const [currentMode, setCurrentMode] = useState('video'); // 'video' ou 'canvas'
  
  // Estados do editor
  const [currentScene, setCurrentScene] = useState(0);
  const [scenes] = useState([
    { id: 1, name: 'Introdução', duration: 5, thumbnail: '🎬' },
    { id: 2, name: 'Desenvolvimento', duration: 10, thumbnail: '📝' },
    { id: 3, name: 'Conclusão', duration: 3, thumbnail: '✅' }
  ]);
  const [timelinePosition, setTimelinePosition] = useState(0);

  // Verificação de conectividade com a API
  const checkApiStatus = async () => {
    try {
      const response = await fetch(`${window.APP_CONFIG?.apiBaseUrl || 'http://localhost:8000'}/api/health`, {
        method: 'GET',
        mode: 'cors',
        timeout: 5000
      });
      
      if (response.ok) {
        setApiStatus('online');
        return true;
      } else {
        setApiStatus('offline');
        return false;
      }
    } catch (error) {
      console.warn('API não disponível:', error.message);
      setApiStatus('offline');
      return false;
    }
  };

  // Inicialização da aplicação
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Verifica status da API
        await checkApiStatus();
        
        // Simula carregamento inicial
        setTimeout(() => {
          setIsLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Erro na inicialização:', error);
        setError('Erro ao inicializar a aplicação');
        setIsLoading(false);
      }
    };

    initializeApp();
  }, []);

  // Retry automático para API
  useEffect(() => {
    if (apiStatus === 'offline' && retryCount < 3) {
      const timer = setTimeout(async () => {
        setRetryCount(prev => prev + 1);
        await checkApiStatus();
      }, 5000 * (retryCount + 1)); // Backoff exponencial

      return () => clearTimeout(timer);
    }
  }, [apiStatus, retryCount]);

  // Handlers do editor
  const handleSceneSelect = (sceneId) => {
    setCurrentScene(sceneId);
    console.log('Cena selecionada:', sceneId);
  };

  const handleAssetSelect = (asset) => {
    console.log('Asset selecionado:', asset);
  };

  // Componente de loading melhorado
  if (isLoading) {
    return React.createElement('div', { 
      className: 'loading',
      style: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        fontFamily: 'Arial, sans-serif',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }
    },
      React.createElement('h1', null, '🚀 TecnoCursos AI - Editor de Vídeo'),
      React.createElement('p', null, 'Inicializando aplicação...'),
      React.createElement('div', { style: { marginTop: '20px' } },
        React.createElement('div', {
          style: {
            width: '40px',
            height: '40px',
            border: '4px solid rgba(255,255,255,0.3)',
            borderTop: '4px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }
        })
      ),
      apiStatus === 'checking' && React.createElement('p', { 
        style: { marginTop: '10px', fontSize: '0.9rem', opacity: 0.8 } 
      }, 'Verificando conectividade...'),
      apiStatus === 'offline' && React.createElement('p', { 
        style: { marginTop: '10px', fontSize: '0.9rem', opacity: 0.8 } 
      }, 'Modo offline - algumas funcionalidades podem estar indisponíveis')
    );
  }

  // Componente de erro melhorado
  if (error) {
    return React.createElement('div', { 
      className: 'error',
      style: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        fontFamily: 'Arial, sans-serif',
        background: '#f44336',
        color: 'white',
        textAlign: 'center',
        padding: '2rem'
      }
    },
      React.createElement('h2', null, '❌ Erro na Aplicação'),
      React.createElement('p', { style: { margin: '1rem 0' } }, error),
      React.createElement('button', {
        onClick: () => window.location.reload(),
        style: {
          padding: '0.75rem 1.5rem',
          background: 'white',
          color: '#f44336',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '1rem',
          marginTop: '1rem'
        }
      }, 'Tentar Novamente')
    );
  }

  // Se o modo atual for canvas, renderizar o Editor de Canvas
  if (currentMode === 'canvas') {
    return React.createElement('div', { 
      className: 'App',
      style: {
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: 'Arial, sans-serif',
        background: '#f8f9fa'
      }
    },
      // Toolbar com seletor de modo
      React.createElement('header', {
        className: 'toolbar',
        style: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '0.75rem 1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          zIndex: 1000
        }
      },
        // Logo e título
        React.createElement('div', { 
          style: { display: 'flex', alignItems: 'center', gap: '1rem' } 
        },
          React.createElement('h1', { 
            style: { margin: 0, fontSize: '1.2rem', fontWeight: 'bold' } 
          }, '🎨 TecnoCursos AI - Editor de Canvas'),
        ),
        // Seletor de modo
        React.createElement('div', { 
          style: { display: 'flex', gap: '0.5rem' } 
        },
          React.createElement('button', {
            onClick: () => setCurrentMode('video'),
            style: {
              padding: '0.5rem 1rem',
              background: currentMode === 'video' ? 'rgba(255,255,255,0.2)' : 'transparent',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.3)',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }
          }, '🎬 Editor de Vídeo'),
          React.createElement('button', {
            onClick: () => setCurrentMode('canvas'),
            style: {
              padding: '0.5rem 1rem',
              background: currentMode === 'canvas' ? 'rgba(255,255,255,0.2)' : 'transparent',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.3)',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }
          }, '🎨 Editor de Canvas')
        )
      ),
      // Editor de Canvas
      React.createElement(Editor)
    );
  }

  // Layout principal do editor de vídeo (modo original)
  return React.createElement('div', { 
    className: 'App',
    style: {
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: 'Arial, sans-serif',
      background: '#f8f9fa'
    }
  },
    // ===== TOOLBAR FIXA NO TOPO =====
    React.createElement('header', {
      className: 'toolbar',
      style: {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '0.75rem 1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        zIndex: 1000
      }
    },
      // Logo e título
      React.createElement('div', { 
        style: { display: 'flex', alignItems: 'center', gap: '1rem' } 
      },
        React.createElement('h1', { 
          style: { margin: 0, fontSize: '1.2rem', fontWeight: 'bold' } 
        }, '🎬 TecnoCursos AI - Editor de Vídeo'),
        React.createElement('div', {
          style: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.8rem',
            padding: '0.25rem 0.5rem',
            borderRadius: '4px',
            background: apiStatus === 'online' ? 'rgba(76, 175, 80, 0.2)' : 'rgba(255, 193, 7, 0.2)',
            border: `1px solid ${apiStatus === 'online' ? '#4CAF50' : '#FFC107'}`
          }
        },
          React.createElement('div', {
            style: {
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: apiStatus === 'online' ? '#4CAF50' : '#FFC107',
              animation: apiStatus === 'checking' ? 'pulse 1s infinite' : 'none'
            }
          }),
          apiStatus === 'online' ? 'Online' : apiStatus === 'offline' ? 'Offline' : 'Verificando...'
        )
      ),
      
      // Botões da toolbar
      React.createElement('div', { 
        style: { display: 'flex', gap: '0.5rem' } 
      },
        React.createElement('button', {
          onClick: () => console.log('Novo projeto'),
          style: {
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '4px',
            background: 'rgba(255,255,255,0.2)',
            color: 'white',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }
        }, '📁 Novo'),
        React.createElement('button', {
          onClick: () => console.log('Salvar projeto'),
          style: {
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '4px',
            background: 'rgba(255,255,255,0.2)',
            color: 'white',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }
        }, '💾 Salvar'),
        React.createElement('button', {
          onClick: () => console.log('Exportar vídeo'),
          style: {
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '4px',
            background: '#4CAF50',
            color: 'white',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: 'bold'
          }
        }, '🎬 Exportar')
      )
    ),
    
    // ===== CONTEÚDO PRINCIPAL =====
    React.createElement('div', { 
      className: 'editor-main',
      style: {
        flex: 1,
        display: 'flex',
        overflow: 'hidden'
      }
    },
      // ===== ASSET PANEL (ESQUERDA) =====
      React.createElement('div', { 
        className: 'asset-panel',
        style: {
          width: '280px',
          background: 'white',
          borderRight: '1px solid #e0e0e0',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }
      },
        // Header do Asset Panel
        React.createElement('div', {
          style: {
            padding: '1rem',
            borderBottom: '1px solid #e0e0e0',
            background: '#f8f9fa'
          }
        },
          React.createElement('h3', { 
            style: { margin: 0, fontSize: '1rem', fontWeight: 'bold' } 
          }, '📚 Biblioteca de Assets')
        ),
        
        // Conteúdo do Asset Panel
        React.createElement('div', {
          style: {
            flex: 1,
            padding: '1rem',
            overflowY: 'auto'
          }
        },
          // Categoria: Imagens
          React.createElement('div', { style: { marginBottom: '1.5rem' } },
            React.createElement('h4', { 
              style: { margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#666' } 
            }, '🖼️ Imagens'),
            React.createElement('div', { 
              style: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' } 
            },
              React.createElement('div', {
                onClick: () => handleAssetSelect({ type: 'image', name: 'Background 1', url: 'bg1.jpg' }),
                style: {
                  padding: '0.5rem',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontSize: '0.8rem'
                }
              }, '🏞️ Background 1'),
              React.createElement('div', {
                onClick: () => handleAssetSelect({ type: 'image', name: 'Background 2', url: 'bg2.jpg' }),
                style: {
                  padding: '0.5rem',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontSize: '0.8rem'
                }
              }, '🏞️ Background 2')
            )
          ),
          
          // Categoria: Áudios
          React.createElement('div', { style: { marginBottom: '1.5rem' } },
            React.createElement('h4', { 
              style: { margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#666' } 
            }, '🎵 Áudios'),
            React.createElement('div', { 
              style: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' } 
            },
              React.createElement('div', {
                onClick: () => handleAssetSelect({ type: 'audio', name: 'Música 1', url: 'music1.mp3' }),
                style: {
                  padding: '0.5rem',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontSize: '0.8rem'
                }
              }, '🎵 Música 1'),
              React.createElement('div', {
                onClick: () => handleAssetSelect({ type: 'audio', name: 'Música 2', url: 'music2.mp3' }),
                style: {
                  padding: '0.5rem',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontSize: '0.8rem'
                }
              }, '🎵 Música 2')
            )
          ),
          
          // Categoria: Vídeos
          React.createElement('div', { style: { marginBottom: '1.5rem' } },
            React.createElement('h4', { 
              style: { margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#666' } 
            }, '🎬 Vídeos'),
            React.createElement('div', { 
              style: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' } 
            },
              React.createElement('div', {
                onClick: () => handleAssetSelect({ type: 'video', name: 'Clipe 1', url: 'clip1.mp4' }),
                style: {
                  padding: '0.5rem',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontSize: '0.8rem'
                }
              }, '🎬 Clipe 1'),
              React.createElement('div', {
                onClick: () => handleAssetSelect({ type: 'video', name: 'Clipe 2', url: 'clip2.mp4' }),
                style: {
                  padding: '0.5rem',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontSize: '0.8rem'
                }
              }, '🎬 Clipe 2')
            )
          )
        )
      ),
      
      // ===== EDITOR CANVAS (CENTRO) =====
      React.createElement('div', { 
        className: 'editor-canvas',
        style: {
          flex: 1,
          background: '#f8f9fa',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }
      },
        // Header do Canvas
        React.createElement('div', {
          style: {
            padding: '1rem',
            borderBottom: '1px solid #e0e0e0',
            background: 'white'
          }
        },
          React.createElement('h3', { 
            style: { margin: 0, fontSize: '1rem', fontWeight: 'bold' } 
          }, '🎨 Área de Edição')
        ),
        
        // Área do Canvas
        React.createElement('div', {
          style: {
            flex: 1,
            margin: '1rem',
            background: 'white',
            border: '2px dashed #e0e0e0',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative'
          }
        },
          React.createElement('div', {
            style: {
              textAlign: 'center',
              color: '#666'
            }
          },
            React.createElement('div', {
              style: {
                fontSize: '3rem',
                marginBottom: '1rem'
              }
            }, '🎬'),
            React.createElement('p', {
              style: {
                margin: 0,
                fontSize: '1.1rem',
                fontWeight: 'bold'
              }
            }, 'Área de Edição'),
            React.createElement('p', {
              style: {
                margin: '0.5rem 0 0 0',
                fontSize: '0.9rem',
                color: '#999'
              }
            }, 'Arraste assets aqui para editar')
          )
        )
      ),
      
      // ===== SCENE LIST (DIREITA) =====
      React.createElement('div', { 
        className: 'scene-list',
        style: {
          width: '280px',
          background: 'white',
          borderLeft: '1px solid #e0e0e0',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }
      },
        // Header do Scene List
        React.createElement('div', {
          style: {
            padding: '1rem',
            borderBottom: '1px solid #e0e0e0',
            background: '#f8f9fa'
          }
        },
          React.createElement('h3', { 
            style: { margin: 0, fontSize: '1rem', fontWeight: 'bold' } 
          }, '📹 Gerenciamento de Cenas')
        ),
        
        // Lista de cenas
        React.createElement('div', {
          style: {
            flex: 1,
            padding: '1rem',
            overflowY: 'auto'
          }
        },
          // Botão adicionar cena
          React.createElement('button', {
            onClick: () => console.log('Adicionar nova cena'),
            style: {
              width: '100%',
              padding: '0.75rem',
              border: '2px dashed #e0e0e0',
              borderRadius: '4px',
              background: 'transparent',
              cursor: 'pointer',
              marginBottom: '1rem',
              fontSize: '0.9rem',
              color: '#666'
            }
          }, '➕ Adicionar Cena'),
          
          // Lista de cenas existentes
          React.createElement('div', {
            style: {
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }
          },
            scenes.map(scene => 
              React.createElement('div', {
                key: scene.id,
                onClick: () => handleSceneSelect(scene.id),
                style: {
                  padding: '0.75rem',
                  border: `1px solid ${currentScene === scene.id ? '#667eea' : '#e0e0e0'}`,
                  borderRadius: '4px',
                  cursor: 'pointer',
                  background: currentScene === scene.id ? '#f0f4ff' : 'white',
                  transition: 'all 0.2s ease'
                }
              },
                React.createElement('div', {
                  style: {
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    marginBottom: '0.25rem'
                  }
                },
                  React.createElement('span', {
                    style: { fontSize: '1.2rem' }
                  }, scene.thumbnail),
                  React.createElement('span', {
                    style: {
                      fontSize: '0.9rem',
                      fontWeight: 'bold',
                      color: currentScene === scene.id ? '#667eea' : '#333'
                    }
                  }, scene.name)
                ),
                React.createElement('div', {
                  style: {
                    fontSize: '0.8rem',
                    color: '#666'
                  }
                }, `${scene.duration}s`)
              )
            )
          )
        )
      )
    ),
    
    // ===== TIMELINE (PARTE INFERIOR) =====
    React.createElement('div', { 
      className: 'timeline',
      style: {
        height: '200px',
        background: 'white',
        borderTop: '1px solid #e0e0e0',
        display: 'flex',
        flexDirection: 'column'
      }
    },
      // Header da Timeline
      React.createElement('div', {
        style: {
          padding: '0.75rem 1rem',
          borderBottom: '1px solid #e0e0e0',
          background: '#f8f9fa',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }
      },
        React.createElement('h3', { 
          style: { margin: 0, fontSize: '1rem', fontWeight: 'bold' } 
        }, '⏱️ Timeline'),
        React.createElement('div', {
          style: {
            display: 'flex',
            gap: '0.5rem'
          }
        },
          React.createElement('button', {
            onClick: () => console.log('Play'),
            style: {
              padding: '0.25rem 0.5rem',
              border: 'none',
              borderRadius: '4px',
              background: '#4CAF50',
              color: 'white',
              cursor: 'pointer',
              fontSize: '0.8rem'
            }
          }, '▶️ Play'),
          React.createElement('button', {
            onClick: () => console.log('Pause'),
            style: {
              padding: '0.25rem 0.5rem',
              border: 'none',
              borderRadius: '4px',
              background: '#FF9800',
              color: 'white',
              cursor: 'pointer',
              fontSize: '0.8rem'
            }
          }, '⏸️ Pause'),
          React.createElement('button', {
            onClick: () => console.log('Stop'),
            style: {
              padding: '0.25rem 0.5rem',
              border: 'none',
              borderRadius: '4px',
              background: '#f44336',
              color: 'white',
              cursor: 'pointer',
              fontSize: '0.8rem'
            }
          }, '⏹️ Stop')
        )
      ),
      
      // Área da Timeline
      React.createElement('div', {
        style: {
          flex: 1,
          padding: '1rem',
          position: 'relative'
        }
      },
        // Linha do tempo
        React.createElement('div', {
          style: {
            height: '60px',
            background: '#f0f0f0',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            position: 'relative',
            marginBottom: '1rem'
          }
        },
          // Marcadores de tempo
          React.createElement('div', {
            style: {
              position: 'absolute',
              top: '0',
              left: '0',
              right: '0',
              height: '20px',
              display: 'flex',
              justifyContent: 'space-between',
              padding: '0 0.5rem',
              fontSize: '0.7rem',
              color: '#666'
            }
          },
            React.createElement('span', null, '0s'),
            React.createElement('span', null, '5s'),
            React.createElement('span', null, '10s'),
            React.createElement('span', null, '15s'),
            React.createElement('span', null, '20s')
          ),
          
          // Cursor da timeline
          React.createElement('div', {
            style: {
              position: 'absolute',
              top: '20px',
              left: `${(timelinePosition / 20) * 100}%`,
              width: '2px',
              height: '40px',
              background: '#667eea',
              zIndex: 10
            }
          })
        ),
        
        // Controles de zoom
        React.createElement('div', {
          style: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }
        },
          React.createElement('span', {
            style: {
              fontSize: '0.8rem',
              color: '#666'
            }
          }, `Posição: ${timelinePosition.toFixed(1)}s`),
          React.createElement('div', {
            style: {
              display: 'flex',
              gap: '0.5rem'
            }
          },
            React.createElement('button', {
              onClick: () => console.log('Zoom out'),
              style: {
                padding: '0.25rem 0.5rem',
                border: '1px solid #e0e0e0',
                borderRadius: '4px',
                background: 'white',
                cursor: 'pointer',
                fontSize: '0.8rem'
              }
            }, '🔍-'),
            React.createElement('button', {
              onClick: () => console.log('Zoom in'),
              style: {
                padding: '0.25rem 0.5rem',
                border: '1px solid #e0e0e0',
                borderRadius: '4px',
                background: 'white',
                cursor: 'pointer',
                fontSize: '0.8rem'
              }
            }, '🔍+')
          )
        )
      )
    )
  );
}

// Exporta o componente App
export default App;

if (typeof module !== 'undefined' && module.exports) {
  module.exports = App;
} else if (typeof window !== 'undefined') {
  window.App = App;
}