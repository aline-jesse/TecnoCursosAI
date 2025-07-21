/**
 * Componente de Integração com Backend FastAPI
 * TecnoCursos AI - Editor de Vídeo Inteligente
 * 
 * Este componente demonstra a integração completa entre o frontend React
 * e o backend FastAPI, incluindo todas as funcionalidades solicitadas:
 * - Buscar lista de projetos e cenas
 * - Upload de arquivos PDF/PPTX
 * - Salvar/editar cenas
 * - Download de vídeos finais
 * 
 * @author TecnoCursos AI Team
 * @version 2.0.0
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  projectService,
  sceneService,
  uploadService,
  videoService,
  healthService,
} from '../services/fastapiIntegration';

/**
 * Componente principal de integração
 */
const VideoEditorIntegration = () => {
  // Estados do componente
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [currentScene, setCurrentScene] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);

  /**
   * Verificar saúde do sistema na inicialização
   */
  useEffect(() => {
    checkSystemHealth();
  }, []);

  /**
   * Verificar saúde do backend
   */
  const checkSystemHealth = async () => {
    try {
      setLoading(true);
      const health = await healthService.checkHealth();
      setSystemHealth(health);
      console.log('Sistema saudável:', health);
    } catch (error) {
      console.error('Erro ao verificar saúde do sistema:', error);
      setError('Backend não está acessível. Verifique se o servidor está rodando.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Buscar lista de projetos do usuário
   */
  const loadProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await projectService.getProjects({
        page: 1,
        limit: 20,
        sort: 'created_at',
        order: 'desc'
      });
      
      setProjects(response.data || []);
      console.log('Projetos carregados:', response.data);
    } catch (error) {
      console.error('Erro ao carregar projetos:', error);
      setError('Erro ao carregar projetos. Tente novamente.');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Carregar projetos na inicialização
   */
  useEffect(() => {
    if (systemHealth?.status === 'healthy') {
      loadProjects();
    }
  }, [systemHealth, loadProjects]);

  /**
   * Buscar cenas de um projeto
   */
  const loadProjectScenes = useCallback(async (projectId) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await sceneService.getProjectScenes(projectId, {
        page: 1,
        limit: 50,
        sort: 'order'
      });
      
      setScenes(response.data || []);
      console.log('Cenas carregadas:', response.data);
    } catch (error) {
      console.error('Erro ao carregar cenas:', error);
      setError('Erro ao carregar cenas. Tente novamente.');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Selecionar projeto e carregar suas cenas
   */
  const selectProject = useCallback(async (project) => {
    setCurrentProject(project);
    setCurrentScene(null);
    await loadProjectScenes(project.id);
  }, [loadProjectScenes]);

  /**
   * Criar novo projeto
   */
  const createNewProject = async (projectData) => {
    try {
      setLoading(true);
      setError(null);
      
      const newProject = await projectService.createProject({
        name: projectData.name || 'Novo Projeto',
        description: projectData.description || 'Descrição do projeto',
        template: projectData.template || 'educational',
        settings: {
          resolution: '1920x1080',
          fps: 30,
          quality: 'high'
        }
      });
      
      console.log('Projeto criado:', newProject);
      
      // Recarregar lista de projetos
      await loadProjects();
      
      // Selecionar o novo projeto
      await selectProject(newProject);
      
      return newProject;
    } catch (error) {
      console.error('Erro ao criar projeto:', error);
      setError('Erro ao criar projeto. Tente novamente.');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Upload de arquivo PDF/PPTX
   */
  const handleFileUpload = async (file, projectId = null) => {
    try {
      setLoading(true);
      setError(null);
      setUploadProgress(0);
      
      // Validar arquivo
      const allowedTypes = ['.pdf', '.pptx', '.docx'];
      const fileExtension = file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(`.${fileExtension}`)) {
        throw new Error('Tipo de arquivo não permitido. Use PDF, PPTX ou DOCX.');
      }
      
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        throw new Error('Arquivo muito grande. Máximo 50MB.');
      }
      
      // Fazer upload
      const uploadedFile = await uploadService.uploadFile(
        file,
        projectId || currentProject?.id,
        (progress) => {
          setUploadProgress(progress);
          console.log(`Upload progresso: ${progress}%`);
        },
        {
          autoProcess: true,
          extractText: true,
          generateThumbnails: true
        }
      );
      
      console.log('Arquivo enviado:', uploadedFile);
      
      // Se não há projeto selecionado, criar um novo
      if (!projectId && !currentProject) {
        const newProject = await createNewProject({
          name: `Projeto - ${file.name}`,
          description: `Projeto criado a partir do arquivo ${file.name}`,
          template: 'educational'
        });
        
        // Recarregar cenas do novo projeto
        await loadProjectScenes(newProject.id);
      } else {
        // Recarregar cenas do projeto atual
        await loadProjectScenes(currentProject.id);
      }
      
      return uploadedFile;
    } catch (error) {
      console.error('Erro no upload:', error);
      setError(error.message || 'Erro no upload. Tente novamente.');
      throw error;
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  /**
   * Criar nova cena
   */
  const createNewScene = async (sceneData) => {
    try {
      setLoading(true);
      setError(null);
      
      if (!currentProject) {
        throw new Error('Nenhum projeto selecionado.');
      }
      
      const newScene = await sceneService.createScene({
        title: sceneData.title || 'Nova Cena',
        content: sceneData.content || 'Conteúdo da cena...',
        duration: sceneData.duration || 5000, // 5 segundos
        project_id: currentProject.id,
        elements: {
          background: sceneData.background || 'classroom',
          character: sceneData.character || 'teacher',
          text: {
            content: sceneData.content || 'Conteúdo da cena...',
            position: { x: 100, y: 200 },
            style: { 
              fontSize: 24, 
              color: '#ffffff',
              fontFamily: 'Arial, sans-serif'
            }
          }
        },
        audio: {
          voice: 'pt-BR',
          speed: 1.0,
          volume: 0.8
        }
      });
      
      console.log('Cena criada:', newScene);
      
      // Recarregar cenas
      await loadProjectScenes(currentProject.id);
      
      // Selecionar a nova cena
      setCurrentScene(newScene);
      
      return newScene;
    } catch (error) {
      console.error('Erro ao criar cena:', error);
      setError('Erro ao criar cena. Tente novamente.');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Salvar/editar cena atual
   */
  const saveCurrentScene = async (updates) => {
    try {
      setLoading(true);
      setError(null);
      
      if (!currentScene) {
        throw new Error('Nenhuma cena selecionada.');
      }
      
      const updatedScene = await sceneService.updateScene(currentScene.id, {
        ...currentScene,
        ...updates,
        elements: {
          ...currentScene.elements,
          ...updates.elements
        }
      });
      
      console.log('Cena atualizada:', updatedScene);
      
      // Atualizar cena atual
      setCurrentScene(updatedScene);
      
      // Atualizar lista de cenas
      await loadProjectScenes(currentProject.id);
      
      return updatedScene;
    } catch (error) {
      console.error('Erro ao salvar cena:', error);
      setError('Erro ao salvar cena. Tente novamente.');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Selecionar cena para edição
   */
  const selectScene = useCallback((scene) => {
    setCurrentScene(scene);
    console.log('Cena selecionada:', scene);
  }, []);

  /**
   * Gerar vídeo do projeto atual
   */
  const generateVideo = async (options = {}) => {
    try {
      setLoading(true);
      setError(null);
      setGenerationProgress(0);
      
      if (!currentProject) {
        throw new Error('Nenhum projeto selecionado.');
      }
      
      // Gerar vídeo
      const generationTask = await videoService.generateVideo(currentProject.id, {
        resolution: '1920x1080',
        quality: 'high',
        format: 'mp4',
        includeAudio: true,
        audioQuality: 'high',
        watermark: false,
        subtitles: true,
        language: 'pt-BR',
        ...options
      });
      
      console.log('Geração iniciada:', generationTask);
      
      // Monitorar progresso
      const checkProgress = async () => {
        try {
          const status = await videoService.getGenerationStatus(
            currentProject.id, 
            generationTask.task_id
          );
          
          setGenerationProgress(status.progress || 0);
          
          if (status.status === 'completed') {
            console.log('Vídeo gerado com sucesso!');
            
            // Download do vídeo
            const videoBlob = await videoService.downloadVideo(currentProject.id);
            const videoUrl = URL.createObjectURL(videoBlob);
            
            // Criar link de download
            const link = document.createElement('a');
            link.href = videoUrl;
            link.download = `${currentProject.name}.mp4`;
            link.click();
            
            // Limpar URL
            URL.revokeObjectURL(videoUrl);
            
            setGenerationProgress(100);
            setLoading(false);
            
          } else if (status.status === 'failed') {
            console.error('Erro na geração:', status.error);
            setError(`Erro na geração do vídeo: ${status.error}`);
            setLoading(false);
            
          } else {
            // Continuar monitorando
            setTimeout(checkProgress, 2000);
          }
        } catch (error) {
          console.error('Erro ao verificar progresso:', error);
          setError('Erro ao verificar progresso da geração.');
          setLoading(false);
        }
      };
      
      // Iniciar monitoramento
      checkProgress();
      
    } catch (error) {
      console.error('Erro ao gerar vídeo:', error);
      setError('Erro ao gerar vídeo. Tente novamente.');
      setLoading(false);
    }
  };

  /**
   * Remover projeto
   */
  const deleteProject = async (projectId) => {
    try {
      setLoading(true);
      setError(null);
      
      await projectService.deleteProject(projectId);
      
      console.log('Projeto removido:', projectId);
      
      // Recarregar projetos
      await loadProjects();
      
      // Limpar seleção se o projeto removido era o atual
      if (currentProject?.id === projectId) {
        setCurrentProject(null);
        setCurrentScene(null);
        setScenes([]);
      }
      
    } catch (error) {
      console.error('Erro ao remover projeto:', error);
      setError('Erro ao remover projeto. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Remover cena
   */
  const deleteScene = async (sceneId) => {
    try {
      setLoading(true);
      setError(null);
      
      await sceneService.deleteScene(sceneId);
      
      console.log('Cena removida:', sceneId);
      
      // Recarregar cenas
      await loadProjectScenes(currentProject.id);
      
      // Limpar seleção se a cena removida era a atual
      if (currentScene?.id === sceneId) {
        setCurrentScene(null);
      }
      
    } catch (error) {
      console.error('Erro ao remover cena:', error);
      setError('Erro ao remover cena. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Componente de upload de arquivo
   */
  const FileUploadComponent = () => {
    const [dragActive, setDragActive] = useState(false);
    
    const handleDrag = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === 'dragenter' || e.type === 'dragover') {
        setDragActive(true);
      } else if (e.type === 'dragleave') {
        setDragActive(false);
      }
    };
    
    const handleDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileUpload(e.dataTransfer.files[0]);
      }
    };
    
    const handleFileInput = (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileUpload(e.target.files[0]);
      }
    };
    
    return (
      <div className="file-upload-container">
        <h3>Upload de Arquivo</h3>
        <div
          className={`file-upload-area ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".pdf,.pptx,.docx"
            onChange={handleFileInput}
            style={{ display: 'none' }}
            id="file-input"
          />
          <label htmlFor="file-input" className="file-upload-label">
            <div className="upload-icon">📁</div>
            <p>Arraste um arquivo PDF, PPTX ou DOCX aqui</p>
            <p>ou clique para selecionar</p>
          </label>
        </div>
        
        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p>Upload: {uploadProgress}%</p>
          </div>
        )}
      </div>
    );
  };

  /**
   * Componente de lista de projetos
   */
  const ProjectListComponent = () => {
    return (
      <div className="project-list-container">
        <h3>Projetos</h3>
        <button 
          onClick={() => createNewProject({ name: 'Novo Projeto' })}
          disabled={loading}
          className="btn btn-primary"
        >
          + Novo Projeto
        </button>
        
        <div className="project-list">
          {projects.map(project => (
            <div 
              key={project.id} 
              className={`project-item ${currentProject?.id === project.id ? 'active' : ''}`}
              onClick={() => selectProject(project)}
            >
              <h4>{project.name}</h4>
              <p>{project.description}</p>
              <div className="project-meta">
                <span>Criado: {new Date(project.created_at).toLocaleDateString()}</span>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteProject(project.id);
                  }}
                  className="btn btn-danger btn-sm"
                >
                  Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  /**
   * Componente de lista de cenas
   */
  const SceneListComponent = () => {
    return (
      <div className="scene-list-container">
        <h3>Cenas do Projeto</h3>
        {currentProject && (
          <button 
            onClick={() => createNewScene({ title: 'Nova Cena' })}
            disabled={loading}
            className="btn btn-primary"
          >
            + Nova Cena
          </button>
        )}
        
        <div className="scene-list">
          {scenes.map(scene => (
            <div 
              key={scene.id} 
              className={`scene-item ${currentScene?.id === scene.id ? 'active' : ''}`}
              onClick={() => selectScene(scene)}
            >
              <h4>{scene.title}</h4>
              <p>{scene.content?.substring(0, 100)}...</p>
              <div className="scene-meta">
                <span>Duração: {scene.duration / 1000}s</span>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteScene(scene.id);
                  }}
                  className="btn btn-danger btn-sm"
                >
                  Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  /**
   * Componente de edição de cena
   */
  const SceneEditorComponent = () => {
    const [sceneData, setSceneData] = useState({});
    
    useEffect(() => {
      if (currentScene) {
        setSceneData({
          title: currentScene.title || '',
          content: currentScene.content || '',
          duration: currentScene.duration || 5000,
          background: currentScene.elements?.background || 'classroom',
          character: currentScene.elements?.character || 'teacher'
        });
      }
    }, [currentScene]);
    
    const handleSave = async () => {
      try {
        await saveCurrentScene({
          title: sceneData.title,
          content: sceneData.content,
          duration: parseInt(sceneData.duration),
          elements: {
            background: sceneData.background,
            character: sceneData.character,
            text: {
              content: sceneData.content,
              position: { x: 100, y: 200 },
              style: { fontSize: 24, color: '#ffffff' }
            }
          }
        });
        
        alert('Cena salva com sucesso!');
      } catch (error) {
        alert('Erro ao salvar cena: ' + error.message);
      }
    };
    
    if (!currentScene) {
      return <div className="scene-editor">Selecione uma cena para editar</div>;
    }
    
    return (
      <div className="scene-editor">
        <h3>Editor de Cena</h3>
        
        <div className="form-group">
          <label>Título:</label>
          <input
            type="text"
            value={sceneData.title || ''}
            onChange={(e) => setSceneData({...sceneData, title: e.target.value})}
            className="form-control"
          />
        </div>
        
        <div className="form-group">
          <label>Conteúdo:</label>
          <textarea
            value={sceneData.content || ''}
            onChange={(e) => setSceneData({...sceneData, content: e.target.value})}
            className="form-control"
            rows="4"
          />
        </div>
        
        <div className="form-group">
          <label>Duração (ms):</label>
          <input
            type="number"
            value={sceneData.duration || 5000}
            onChange={(e) => setSceneData({...sceneData, duration: e.target.value})}
            className="form-control"
            min="1000"
            max="300000"
          />
        </div>
        
        <div className="form-group">
          <label>Background:</label>
          <select
            value={sceneData.background || 'classroom'}
            onChange={(e) => setSceneData({...sceneData, background: e.target.value})}
            className="form-control"
          >
            <option value="classroom">Sala de Aula</option>
            <option value="office">Escritório</option>
            <option value="studio">Estúdio</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Personagem:</label>
          <select
            value={sceneData.character || 'teacher'}
            onChange={(e) => setSceneData({...sceneData, character: e.target.value})}
            className="form-control"
          >
            <option value="teacher">Professor</option>
            <option value="student">Estudante</option>
            <option value="presenter">Apresentador</option>
          </select>
        </div>
        
        <button 
          onClick={handleSave}
          disabled={loading}
          className="btn btn-success"
        >
          Salvar Cena
        </button>
      </div>
    );
  };

  /**
   * Componente de geração de vídeo
   */
  const VideoGenerationComponent = () => {
    return (
      <div className="video-generation-container">
        <h3>Geração de Vídeo</h3>
        
        {currentProject && (
          <div className="generation-controls">
            <button 
              onClick={() => generateVideo()}
              disabled={loading}
              className="btn btn-primary"
            >
              Gerar Vídeo
            </button>
            
            {generationProgress > 0 && generationProgress < 100 && (
              <div className="generation-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${generationProgress}%` }}
                  ></div>
                </div>
                <p>Geração: {generationProgress}%</p>
              </div>
            )}
          </div>
        )}
        
        {!currentProject && (
          <p>Selecione um projeto para gerar vídeo</p>
        )}
      </div>
    );
  };

  /**
   * Componente de status do sistema
   */
  const SystemStatusComponent = () => {
    return (
      <div className="system-status">
        <h3>Status do Sistema</h3>
        
        {systemHealth ? (
          <div className="status-info">
            <p>Status: <span className="status-healthy">✅ Saudável</span></p>
            <p>Uptime: {Math.floor(systemHealth.uptime / 3600)}h {(systemHealth.uptime % 3600) / 60}m</p>
            <p>Versão: {systemHealth.version}</p>
          </div>
        ) : (
          <p>Status: <span className="status-error">❌ Indisponível</span></p>
        )}
        
        <button 
          onClick={checkSystemHealth}
          disabled={loading}
          className="btn btn-secondary"
        >
          Verificar Status
        </button>
      </div>
    );
  };

  // Renderização do componente
  return (
    <div className="video-editor-integration">
      <h2>🎬 TecnoCursos AI - Editor de Vídeo</h2>
      
      {/* Status do Sistema */}
      <SystemStatusComponent />
      
      {/* Mensagens de Erro */}
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => setError(null)}>Fechar</button>
        </div>
      )}
      
      {/* Loading */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Carregando...</p>
        </div>
      )}
      
      <div className="editor-layout">
        {/* Coluna Esquerda - Upload e Projetos */}
        <div className="left-column">
          <FileUploadComponent />
          <ProjectListComponent />
        </div>
        
        {/* Coluna Central - Cenas */}
        <div className="center-column">
          <SceneListComponent />
        </div>
        
        {/* Coluna Direita - Editor e Geração */}
        <div className="right-column">
          <SceneEditorComponent />
          <VideoGenerationComponent />
        </div>
      </div>
      
      {/* Informações do Projeto Atual */}
      {currentProject && (
        <div className="current-project-info">
          <h3>Projeto Atual: {currentProject.name}</h3>
          <p>{currentProject.description}</p>
          <p>Cenas: {scenes.length}</p>
          {currentScene && (
            <p>Cena Selecionada: {currentScene.title}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoEditorIntegration; 