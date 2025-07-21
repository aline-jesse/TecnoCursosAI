/**
 * Exemplo de Uso - Componente de Integração com Backend FastAPI
 * TecnoCursos AI - Editor de Vídeo Inteligente
 * 
 * Este arquivo demonstra como usar o componente VideoEditorIntegration
 * em um projeto React real, incluindo configuração, customização
 * e integração com outros componentes.
 * 
 * @author TecnoCursos AI Team
 * @version 2.0.0
 */

import React, { useState, useEffect } from 'react';
import VideoEditorIntegration from './VideoEditorIntegration';
import './VideoEditorIntegration.css';

/**
 * Exemplo de App principal que usa o componente de integração
 */
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000/api');

  // Verificar autenticação na inicialização
  useEffect(() => {
    checkAuthentication();
  }, []);

  /**
   * Verificar se o usuário está autenticado
   */
  const checkAuthentication = () => {
    const token = localStorage.getItem('tecnocursos_token');
    const userData = localStorage.getItem('tecnocursos_user');
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    } else {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  /**
   * Função de login
   */
  const handleLogin = async (credentials) => {
    try {
      const response = await fetch(`${backendUrl.replace('/api', '')}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('tecnocursos_token', data.access_token);
        localStorage.setItem('tecnocursos_user', JSON.stringify(data.user));
        setIsAuthenticated(true);
        setUser(data.user);
      } else {
        throw new Error('Credenciais inválidas');
      }
    } catch (error) {
      console.error('Erro no login:', error);
      alert('Erro no login: ' + error.message);
    }
  };

  /**
   * Função de logout
   */
  const handleLogout = () => {
    localStorage.removeItem('tecnocursos_token');
    localStorage.removeItem('tecnocursos_user');
    setIsAuthenticated(false);
    setUser(null);
  };

  /**
   * Componente de login
   */
  const LoginComponent = () => {
    const [credentials, setCredentials] = useState({
      email: '',
      password: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      handleLogin(credentials);
    };

    return (
      <div className="login-container">
        <div className="login-card">
          <h2>🎬 TecnoCursos AI</h2>
          <p>Faça login para acessar o editor de vídeo</p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email:</label>
              <input
                type="email"
                value={credentials.email}
                onChange={(e) => setCredentials({...credentials, email: e.target.value})}
                required
                className="form-control"
              />
            </div>
            
            <div className="form-group">
              <label>Senha:</label>
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                required
                className="form-control"
              />
            </div>
            
            <button type="submit" className="btn btn-primary">
              Entrar
            </button>
          </form>
          
          <div className="login-footer">
            <p>Backend URL: {backendUrl}</p>
            <button 
              onClick={() => setBackendUrl(prompt('Digite a URL do backend:', backendUrl) || backendUrl)}
              className="btn btn-secondary btn-sm"
            >
              Alterar URL
            </button>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Componente de header
   */
  const HeaderComponent = () => {
    return (
      <header className="app-header">
        <div className="header-content">
          <h1>🎬 TecnoCursos AI - Editor de Vídeo</h1>
          
          {user && (
            <div className="user-info">
              <span>Olá, {user.name || user.email}</span>
              <button onClick={handleLogout} className="btn btn-danger btn-sm">
                Sair
              </button>
            </div>
          )}
        </div>
      </header>
    );
  };

  /**
   * Componente de configurações
   */
  const SettingsComponent = () => {
    const [settings, setSettings] = useState({
      autoSave: true,
      notifications: true,
      theme: 'light'
    });

    const handleSettingChange = (key, value) => {
      setSettings({...settings, [key]: value});
      localStorage.setItem('app_settings', JSON.stringify({...settings, [key]: value}));
    };

    return (
      <div className="settings-panel">
        <h3>⚙️ Configurações</h3>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={settings.autoSave}
              onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
            />
            Salvar automaticamente
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={settings.notifications}
              onChange={(e) => handleSettingChange('notifications', e.target.checked)}
            />
            Notificações
          </label>
        </div>
        
        <div className="setting-item">
          <label>Tema:</label>
          <select
            value={settings.theme}
            onChange={(e) => handleSettingChange('theme', e.target.value)}
            className="form-control"
          >
            <option value="light">Claro</option>
            <option value="dark">Escuro</option>
          </select>
        </div>
      </div>
    );
  };

  /**
   * Componente de estatísticas
   */
  const StatsComponent = () => {
    const [stats, setStats] = useState({
      totalProjects: 0,
      totalScenes: 0,
      totalVideos: 0,
      storageUsed: 0
    });

    useEffect(() => {
      // Simular carregamento de estatísticas
      setStats({
        totalProjects: 12,
        totalScenes: 48,
        totalVideos: 8,
        storageUsed: 2.5 // GB
      });
    }, []);

    return (
      <div className="stats-panel">
        <h3>📊 Estatísticas</h3>
        
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{stats.totalProjects}</div>
            <div className="stat-label">Projetos</div>
          </div>
          
          <div className="stat-item">
            <div className="stat-value">{stats.totalScenes}</div>
            <div className="stat-label">Cenas</div>
          </div>
          
          <div className="stat-item">
            <div className="stat-value">{stats.totalVideos}</div>
            <div className="stat-label">Vídeos</div>
          </div>
          
          <div className="stat-item">
            <div className="stat-value">{stats.storageUsed}GB</div>
            <div className="stat-label">Armazenamento</div>
          </div>
        </div>
      </div>
    );
  };

  // Renderização condicional baseada na autenticação
  if (!isAuthenticated) {
    return <LoginComponent />;
  }

  return (
    <div className="app">
      <HeaderComponent />
      
      <div className="app-layout">
        {/* Sidebar com configurações e estatísticas */}
        <aside className="app-sidebar">
          <SettingsComponent />
          <StatsComponent />
        </aside>
        
        {/* Área principal com o editor */}
        <main className="app-main">
          <VideoEditorIntegration />
        </main>
      </div>
    </div>
  );
};

/**
 * Exemplo de uso avançado com customizações
 */
const AdvancedVideoEditor = () => {
  const [customConfig, setCustomConfig] = useState({
    maxFileSize: 50 * 1024 * 1024, // 50MB
    allowedFileTypes: ['.pdf', '.pptx', '.docx'],
    autoProcess: true,
    generateThumbnails: true
  });

  const [theme, setTheme] = useState('light');

  // Customizar configurações do editor
  const handleConfigChange = (key, value) => {
    setCustomConfig({...customConfig, [key]: value});
  };

  // Alternar tema
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.body.className = `theme-${newTheme}`;
  };

  return (
    <div className={`advanced-editor theme-${theme}`}>
      <div className="editor-controls">
        <h2>Editor Avançado</h2>
        
        <div className="control-group">
          <label>Tamanho máximo de arquivo:</label>
          <select
            value={customConfig.maxFileSize / (1024 * 1024)}
            onChange={(e) => handleConfigChange('maxFileSize', e.target.value * 1024 * 1024)}
            className="form-control"
          >
            <option value={10}>10MB</option>
            <option value={25}>25MB</option>
            <option value={50}>50MB</option>
            <option value={100}>100MB</option>
          </select>
        </div>
        
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={customConfig.autoProcess}
              onChange={(e) => handleConfigChange('autoProcess', e.target.checked)}
            />
            Processamento automático
          </label>
        </div>
        
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={customConfig.generateThumbnails}
              onChange={(e) => handleConfigChange('generateThumbnails', e.target.checked)}
            />
            Gerar miniaturas
          </label>
        </div>
        
        <button onClick={toggleTheme} className="btn btn-secondary">
          Alternar Tema
        </button>
      </div>
      
      <VideoEditorIntegration />
    </div>
  );
};

/**
 * Exemplo de integração com sistema de notificações
 */
const VideoEditorWithNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  // Adicionar notificação
  const addNotification = (type, message) => {
    const notification = {
      id: Date.now(),
      type,
      message,
      timestamp: new Date()
    };
    
    setNotifications(prev => [...prev, notification]);
    
    // Remover notificação após 5 segundos
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  // Componente de notificações
  const NotificationComponent = () => {
    return (
      <div className="notifications-container">
        {notifications.map(notification => (
          <div key={notification.id} className={`notification notification-${notification.type}`}>
            <span className="notification-message">{notification.message}</span>
            <button
              onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
              className="notification-close"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    );
  };

  // Wrapper do VideoEditorIntegration com notificações
  const VideoEditorWithNotificationsWrapper = () => {
    // Interceptar eventos do editor para mostrar notificações
    const handleProjectCreated = (project) => {
      addNotification('success', `Projeto "${project.name}" criado com sucesso!`);
    };

    const handleSceneSaved = (scene) => {
      addNotification('success', `Cena "${scene.title}" salva com sucesso!`);
    };

    const handleVideoGenerated = (project) => {
      addNotification('success', `Vídeo do projeto "${project.name}" gerado com sucesso!`);
    };

    const handleError = (error) => {
      addNotification('error', `Erro: ${error.message}`);
    };

    return (
      <div className="video-editor-with-notifications">
        <VideoEditorIntegration />
        
        {/* Aqui você pode adicionar listeners para os eventos do editor */}
        <script>
          {`
            // Exemplo de como interceptar eventos do editor
            document.addEventListener('projectCreated', (e) => {
              handleProjectCreated(e.detail);
            });
            
            document.addEventListener('sceneSaved', (e) => {
              handleSceneSaved(e.detail);
            });
            
            document.addEventListener('videoGenerated', (e) => {
              handleVideoGenerated(e.detail);
            });
            
            document.addEventListener('editorError', (e) => {
              handleError(e.detail);
            });
          `}
        </script>
      </div>
    );
  };

  return (
    <div className="app-with-notifications">
      <NotificationComponent />
      <VideoEditorWithNotificationsWrapper />
    </div>
  );
};

/**
 * Exemplo de uso com roteamento
 */
const VideoEditorWithRouting = () => {
  const [currentPage, setCurrentPage] = useState('editor');

  const pages = {
    editor: <VideoEditorIntegration />,
    advanced: <AdvancedVideoEditor />,
    settings: <div>Configurações</div>,
    help: <div>Ajuda</div>
  };

  return (
    <div className="app-with-routing">
      <nav className="app-navigation">
        <button
          onClick={() => setCurrentPage('editor')}
          className={`nav-button ${currentPage === 'editor' ? 'active' : ''}`}
        >
          Editor
        </button>
        
        <button
          onClick={() => setCurrentPage('advanced')}
          className={`nav-button ${currentPage === 'advanced' ? 'active' : ''}`}
        >
          Editor Avançado
        </button>
        
        <button
          onClick={() => setCurrentPage('settings')}
          className={`nav-button ${currentPage === 'settings' ? 'active' : ''}`}
        >
          Configurações
        </button>
        
        <button
          onClick={() => setCurrentPage('help')}
          className={`nav-button ${currentPage === 'help' ? 'active' : ''}`}
        >
          Ajuda
        </button>
      </nav>
      
      <main className="app-content">
        {pages[currentPage]}
      </main>
    </div>
  );
};

// Exportar todos os exemplos
export {
  App,
  AdvancedVideoEditor,
  VideoEditorWithNotifications,
  VideoEditorWithRouting
};

export default App; 