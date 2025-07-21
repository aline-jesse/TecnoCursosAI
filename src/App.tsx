/**
 * App - Aplicação Principal do Editor de Vídeo TecnoCursos AI
 * Sistema unificado com Zustand, Fabric.js e componentes TypeScript
 */

import React, { useEffect, useState } from 'react'
import EditorCanvas from './components/EditorCanvas'
import AssetPanel from './components/AssetPanel'
import SceneList from './components/SceneList'
import Timeline from './components/Timeline'
import ProjectDashboard from './components/ProjectDashboard'
import { useEditorStore } from './store/editorStore'
import './App.css'
import './components/ProjectDashboard.css'

/**
 * Componente de status da API
 */
const ApiStatus: React.FC<{ status: string }> = ({ status }) => {
  const statusIcons = {
    checking: '🔄',
    online: '🟢', 
    offline: '🔴'
  }
  
  const statusTexts = {
    checking: 'Verificando conexão...',
    online: 'API Online',
    offline: 'API Offline'
  }

  return (
    <div className={`api-status ${status}`}>
      <span>{statusIcons[status as keyof typeof statusIcons]} {statusTexts[status as keyof typeof statusTexts]}</span>
    </div>
  )
}

/**
 * Componente principal da aplicação
 */
const App: React.FC = () => {
  // Estados da aplicação
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [currentMode, setCurrentMode] = useState<'dashboard' | 'canvas' | 'video'>('dashboard')

  // Store Zustand
  const { scenes, assets, activeScene } = useEditorStore()

  // Verificação de status da API
  const checkApiStatus = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/health`, {
        method: 'GET',
        mode: 'cors',
        signal: AbortSignal.timeout(5000)
      })
      
      if (response.ok) {
        setApiStatus('online')
        return true
      } else {
        setApiStatus('offline')
        return false
      }
    } catch (error) {
      console.warn('API não disponível:', error)
      setApiStatus('offline')
      return false
    }
  }

  // Inicialização da aplicação
  useEffect(() => {
    const initializeApp = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Verifica status da API
        await checkApiStatus()

        // Simula carregamento inicial
        await new Promise(resolve => setTimeout(resolve, 1000))

        setIsLoading(false)
      } catch (err) {
        console.error('Erro na inicialização:', err)
        setError('Erro ao inicializar aplicação')
        setIsLoading(false)
      }
    }

    initializeApp()
  }, [])

  // Verificação periódica do status da API
  useEffect(() => {
    const interval = setInterval(checkApiStatus, 30000) // Verifica a cada 30s
    return () => clearInterval(interval)
  }, [])

  // Renderiza tela de carregamento
  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h2>TecnoCursos AI</h2>
          <p>Carregando editor de vídeo...</p>
        </div>
      </div>
    )
  }

  // Renderiza tela de erro
  if (error) {
    return (
      <div className="app-error">
        <div className="error-container">
          <h2>❌ Erro</h2>
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="retry-button"
          >
            🔄 Tentar Novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      {/* Header da aplicação */}
      <header className="app-header">
        <div className="header-left">
          <h1 className="app-title">
            🎬 TecnoCursos AI
          </h1>
          <span className="app-subtitle">Editor de Vídeo Inteligente</span>
        </div>
        
        <div className="header-center">
          <div className="mode-selector">
            <button
              className={`mode-btn ${currentMode === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentMode('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              className={`mode-btn ${currentMode === 'canvas' ? 'active' : ''}`}
              onClick={() => setCurrentMode('canvas')}
            >
              🎨 Canvas
            </button>
            <button
              className={`mode-btn ${currentMode === 'video' ? 'active' : ''}`}
              onClick={() => setCurrentMode('video')}
            >
              🎥 Vídeo
            </button>
          </div>
        </div>

        <div className="header-right">
          <ApiStatus status={apiStatus} />
          <div className="project-info">
            <span>Projeto: Novo Vídeo</span>
            <span>{scenes.length} cenas • {assets.length} assets</span>
          </div>
        </div>
      </header>

      {/* Layout principal */}
      <main className="app-main">
        {currentMode === 'dashboard' ? (
          /* Dashboard Mode - Layout completo */
          <section className="dashboard-container">
            <div className="dashboard-content">
              <ProjectDashboard 
                showStats={true}
                compactMode={false}
              />
            </div>
          </section>
        ) : (
          /* Editor Mode - Layout com sidebars */
          <>
            {/* Painel lateral esquerdo - Assets */}
            <aside className="sidebar sidebar-left">
              <AssetPanel />
            </aside>

            {/* Área central - Canvas/Editor */}
            <section className="main-content">
              <div className="editor-container">
                {currentMode === 'canvas' ? (
                  <EditorCanvas 
                    selectedScene={activeScene}
                    assets={assets}
                    width={1920}
                    height={1080}
                    backgroundColor="#ffffff"
                  />
                ) : (
                  <div className="video-editor-placeholder">
                    <h3>🎥 Editor de Vídeo</h3>
                    <p>Funcionalidade em desenvolvimento</p>
                  </div>
                )}
              </div>
            </section>

            {/* Painel lateral direito - Cenas */}
            <aside className="sidebar sidebar-right">
              <SceneList />
            </aside>
          </>
        )}
      </main>

      {/* Timeline inferior - apenas para modo editor */}
      {currentMode !== 'dashboard' && (
        <footer className="app-footer">
          <Timeline />
        </footer>
      )}
    </div>
  )
}

export default App