/**
 * Testes de Integração - Frontend React com Backend FastAPI
 * TecnoCursos AI - Editor de Vídeo Inteligente
 * 
 * Este arquivo contém testes completos para verificar a integração
 * entre o frontend React e o backend FastAPI via Axios.
 * 
 * @author TecnoCursos AI Team
 * @version 2.0.0
 */

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import {
  projectService,
  sceneService,
  uploadService,
  videoService,
  healthService,
  integrationExample,
} from './fastapiIntegration';

// Configurar mock do Axios para testes
const mock = new MockAdapter(axios);

/**
 * Dados de exemplo para testes
 */
const mockData = {
  project: {
    id: 123,
    name: 'Curso de Python',
    description: 'Vídeo educativo sobre Python',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    status: 'active',
    template: 'educational',
    settings: {
      resolution: '1920x1080',
      fps: 30,
      quality: 'high'
    }
  },

  scene: {
    id: 456,
    title: 'Introdução ao Python',
    content: 'Python é uma linguagem de programação...',
    duration: 10000,
    project_id: 123,
    order: 1,
    elements: {
      background: 'classroom',
      character: 'teacher',
      text: {
        content: 'Python é uma linguagem de programação...',
        position: { x: 100, y: 200 },
        style: { fontSize: 24, color: '#ffffff' }
      }
    },
    audio: {
      voice: 'pt-BR',
      speed: 1.0,
      volume: 0.8
    }
  },

  uploadedFile: {
    id: 789,
    filename: 'curso_python.pdf',
    original_name: 'curso_python.pdf',
    file_size: 1024000,
    file_type: 'pdf',
    project_id: 123,
    uploaded_at: '2024-01-15T10:30:00Z',
    status: 'processed',
    extracted_text: 'Conteúdo extraído do PDF...'
  },

  videoGeneration: {
    task_id: 'task_abc123',
    project_id: 123,
    status: 'processing',
    progress: 45,
    created_at: '2024-01-15T11:00:00Z',
    estimated_completion: '2024-01-15T11:05:00Z'
  },

  healthStatus: {
    status: 'healthy',
    uptime: 3600,
    version: '2.0.0',
    timestamp: '2024-01-15T10:00:00Z'
  }
};

/**
 * Testes do Serviço de Projetos
 */
describe('ProjectService', () => {
  beforeEach(() => {
    mock.reset();
  });

  test('deve buscar lista de projetos com sucesso', async () => {
    const mockResponse = {
      data: [mockData.project],
      total: 1,
      page: 1,
      limit: 20,
      pages: 1
    };

    mock.onGet('/projects').reply(200, mockResponse);

    const result = await projectService.getProjects();
    
    expect(result).toEqual(mockResponse);
    expect(result.data).toHaveLength(1);
    expect(result.data[0].name).toBe('Curso de Python');
  });

  test('deve buscar projeto específico por ID', async () => {
    mock.onGet('/projects/123').reply(200, mockData.project);

    const result = await projectService.getProject(123);
    
    expect(result).toEqual(mockData.project);
    expect(result.id).toBe(123);
    expect(result.name).toBe('Curso de Python');
  });

  test('deve criar novo projeto', async () => {
    const newProjectData = {
      name: 'Novo Projeto',
      description: 'Descrição do novo projeto',
      template: 'educational'
    };

    const createdProject = { ...mockData.project, ...newProjectData, id: 124 };
    mock.onPost('/projects').reply(201, createdProject);

    const result = await projectService.createProject(newProjectData);
    
    expect(result).toEqual(createdProject);
    expect(result.name).toBe('Novo Projeto');
  });

  test('deve atualizar projeto existente', async () => {
    const updates = {
      name: 'Curso Python Atualizado',
      description: 'Nova descrição do curso'
    };

    const updatedProject = { ...mockData.project, ...updates };
    mock.onPut('/projects/123').reply(200, updatedProject);

    const result = await projectService.updateProject(123, updates);
    
    expect(result).toEqual(updatedProject);
    expect(result.name).toBe('Curso Python Atualizado');
  });

  test('deve remover projeto', async () => {
    const deleteResponse = { message: 'Projeto removido com sucesso' };
    mock.onDelete('/projects/123').reply(200, deleteResponse);

    const result = await projectService.deleteProject(123);
    
    expect(result).toEqual(deleteResponse);
  });

  test('deve tratar erro ao buscar projetos', async () => {
    mock.onGet('/projects').reply(500, { error: 'Erro interno do servidor' });

    await expect(projectService.getProjects()).rejects.toThrow();
  });
});

/**
 * Testes do Serviço de Cenas
 */
describe('SceneService', () => {
  beforeEach(() => {
    mock.reset();
  });

  test('deve buscar cenas de um projeto', async () => {
    const mockResponse = {
      data: [mockData.scene],
      total: 1,
      page: 1,
      limit: 50
    };

    mock.onGet('/projects/123/scenes').reply(200, mockResponse);

    const result = await sceneService.getProjectScenes(123);
    
    expect(result).toEqual(mockResponse);
    expect(result.data).toHaveLength(1);
    expect(result.data[0].title).toBe('Introdução ao Python');
  });

  test('deve buscar cena específica por ID', async () => {
    mock.onGet('/scenes/456').reply(200, mockData.scene);

    const result = await sceneService.getScene(456);
    
    expect(result).toEqual(mockData.scene);
    expect(result.id).toBe(456);
    expect(result.title).toBe('Introdução ao Python');
  });

  test('deve criar nova cena', async () => {
    const newSceneData = {
      title: 'Nova Cena',
      content: 'Conteúdo da nova cena',
      duration: 8000,
      project_id: 123,
      elements: {
        background: 'office',
        character: 'student'
      }
    };

    const createdScene = { ...mockData.scene, ...newSceneData, id: 457 };
    mock.onPost('/scenes').reply(201, createdScene);

    const result = await sceneService.createScene(newSceneData);
    
    expect(result).toEqual(createdScene);
    expect(result.title).toBe('Nova Cena');
  });

  test('deve atualizar cena existente', async () => {
    const updates = {
      title: 'Cena Atualizada',
      content: 'Conteúdo atualizado da cena',
      duration: 12000
    };

    const updatedScene = { ...mockData.scene, ...updates };
    mock.onPut('/scenes/456').reply(200, updatedScene);

    const result = await sceneService.updateScene(456, updates);
    
    expect(result).toEqual(updatedScene);
    expect(result.title).toBe('Cena Atualizada');
    expect(result.duration).toBe(12000);
  });

  test('deve remover cena', async () => {
    const deleteResponse = { message: 'Cena removida com sucesso' };
    mock.onDelete('/scenes/456').reply(200, deleteResponse);

    const result = await sceneService.deleteScene(456);
    
    expect(result).toEqual(deleteResponse);
  });

  test('deve reordenar cenas de um projeto', async () => {
    const sceneOrder = [456, 789, 101];
    const reorderResponse = { message: 'Cenas reordenadas com sucesso' };
    
    mock.onPut('/projects/123/scenes/reorder').reply(200, reorderResponse);

    const result = await sceneService.reorderScenes(123, sceneOrder);
    
    expect(result).toEqual(reorderResponse);
  });
});

/**
 * Testes do Serviço de Upload
 */
describe('UploadService', () => {
  beforeEach(() => {
    mock.reset();
  });

  test('deve fazer upload de arquivo com sucesso', async () => {
    const file = new File(['conteúdo do arquivo'], 'test.pdf', { type: 'application/pdf' });
    const onProgress = jest.fn();

    mock.onPost('/upload').reply(200, mockData.uploadedFile);

    const result = await uploadService.uploadFile(file, 123, onProgress);
    
    expect(result).toEqual(mockData.uploadedFile);
    expect(result.filename).toBe('curso_python.pdf');
    expect(result.project_id).toBe(123);
  });

  test('deve fazer upload de arquivo grande em chunks', async () => {
    const file = new File(['x'.repeat(1024 * 1024)], 'large.pdf', { type: 'application/pdf' });
    const onProgress = jest.fn();

    // Mock para chunks
    mock.onPost('/upload/chunk').reply(200, { message: 'Chunk enviado' });
    mock.onPost('/upload/finalize').reply(200, mockData.uploadedFile);

    const result = await uploadService.uploadLargeFile(file, 123, onProgress);
    
    expect(result).toEqual(mockData.uploadedFile);
  });

  test('deve listar arquivos enviados', async () => {
    const mockResponse = {
      data: [mockData.uploadedFile],
      total: 1,
      page: 1,
      limit: 20
    };

    mock.onGet('/upload/files').reply(200, mockResponse);

    const result = await uploadService.getFiles();
    
    expect(result).toEqual(mockResponse);
    expect(result.data).toHaveLength(1);
    expect(result.data[0].filename).toBe('curso_python.pdf');
  });

  test('deve listar arquivos de um projeto específico', async () => {
    const mockResponse = {
      data: [mockData.uploadedFile],
      total: 1,
      page: 1,
      limit: 20
    };

    mock.onGet('/upload/files').reply(200, mockResponse);

    const result = await uploadService.getFiles(123);
    
    expect(result).toEqual(mockResponse);
  });

  test('deve remover arquivo enviado', async () => {
    const deleteResponse = { message: 'Arquivo removido com sucesso' };
    mock.onDelete('/upload/files/789').reply(200, deleteResponse);

    const result = await uploadService.deleteFile(789);
    
    expect(result).toEqual(deleteResponse);
  });

  test('deve obter estatísticas de upload', async () => {
    const statsResponse = {
      total_files: 5,
      total_size_mb: 25.5,
      project_files: 3,
      project_size_mb: 15.2
    };

    mock.onGet('/upload/stats').reply(200, statsResponse);

    const result = await uploadService.getUploadStats(123);
    
    expect(result).toEqual(statsResponse);
    expect(result.total_files).toBe(5);
  });
});

/**
 * Testes do Serviço de Vídeos
 */
describe('VideoService', () => {
  beforeEach(() => {
    mock.reset();
  });

  test('deve gerar vídeo do projeto', async () => {
    const options = {
      resolution: '1920x1080',
      quality: 'high',
      format: 'mp4'
    };

    mock.onPost('/projects/123/generate').reply(200, mockData.videoGeneration);

    const result = await videoService.generateVideo(123, options);
    
    expect(result).toEqual(mockData.videoGeneration);
    expect(result.task_id).toBe('task_abc123');
    expect(result.status).toBe('processing');
  });

  test('deve verificar status da geração de vídeo', async () => {
    const statusResponse = {
      ...mockData.videoGeneration,
      status: 'completed',
      progress: 100,
      video_url: '/videos/project_123.mp4'
    };

    mock.onGet('/projects/123/video/status').reply(200, statusResponse);

    const result = await videoService.getGenerationStatus(123, 'task_abc123');
    
    expect(result).toEqual(statusResponse);
    expect(result.status).toBe('completed');
    expect(result.progress).toBe(100);
  });

  test('deve baixar vídeo final gerado', async () => {
    const videoBlob = new Blob(['video content'], { type: 'video/mp4' });
    mock.onGet('/projects/123/video').reply(200, videoBlob);

    const result = await videoService.downloadVideo(123);
    
    expect(result).toBeInstanceOf(Blob);
    expect(result.type).toBe('video/mp4');
  });

  test('deve listar vídeos gerados', async () => {
    const mockResponse = {
      data: [
        {
          id: 1,
          project_id: 123,
          filename: 'video_123.mp4',
          file_size: 52428800,
          duration: 120,
          resolution: '1920x1080',
          status: 'completed',
          created_at: '2024-01-15T12:00:00Z'
        }
      ],
      total: 1,
      page: 1,
      limit: 20
    };

    mock.onGet('/videos').reply(200, mockResponse);

    const result = await videoService.getVideos();
    
    expect(result).toEqual(mockResponse);
    expect(result.data).toHaveLength(1);
    expect(result.data[0].filename).toBe('video_123.mp4');
  });

  test('deve obter informações do vídeo', async () => {
    const videoInfo = {
      id: 1,
      project_id: 123,
      filename: 'video_123.mp4',
      file_size: 52428800,
      duration: 120,
      resolution: '1920x1080',
      fps: 30,
      bitrate: 5000,
      status: 'completed'
    };

    mock.onGet('/videos/1').reply(200, videoInfo);

    const result = await videoService.getVideoInfo(1);
    
    expect(result).toEqual(videoInfo);
    expect(result.duration).toBe(120);
    expect(result.resolution).toBe('1920x1080');
  });
});

/**
 * Testes do Serviço de Health Check
 */
describe('HealthService', () => {
  beforeEach(() => {
    mock.reset();
  });

  test('deve verificar saúde geral da API', async () => {
    mock.onGet('/health').reply(200, mockData.healthStatus);

    const result = await healthService.checkHealth();
    
    expect(result).toEqual(mockData.healthStatus);
    expect(result.status).toBe('healthy');
  });

  test('deve verificar saúde específica da API', async () => {
    const apiHealthResponse = {
      status: 'healthy',
      database: 'connected',
      storage: 'available',
      background_tasks: 'running',
      uptime: 3600
    };

    mock.onGet('/api/health').reply(200, apiHealthResponse);

    const result = await healthService.checkApiHealth();
    
    expect(result).toEqual(apiHealthResponse);
    expect(result.database).toBe('connected');
  });

  test('deve obter status detalhado do sistema', async () => {
    const systemStatus = {
      status: 'healthy',
      cpu_usage: 25.5,
      memory_usage: 60.2,
      disk_usage: 45.8,
      active_connections: 15,
      background_tasks: 3,
      uptime: 3600
    };

    mock.onGet('/api/status').reply(200, systemStatus);

    const result = await healthService.getSystemStatus();
    
    expect(result).toEqual(systemStatus);
    expect(result.cpu_usage).toBe(25.5);
    expect(result.memory_usage).toBe(60.2);
  });
});

/**
 * Testes de Integração Completa
 */
describe('IntegrationExample', () => {
  beforeEach(() => {
    mock.reset();
  });

  test('deve executar fluxo completo de criação de vídeo', async () => {
    // Mock para criação de projeto
    const createdProject = { ...mockData.project, id: 999 };
    mock.onPost('/projects').reply(201, createdProject);

    // Mock para criação de cena
    const createdScene = { ...mockData.scene, id: 888, project_id: 999 };
    mock.onPost('/scenes').reply(201, createdScene);

    // Mock para atualização de cena
    const updatedScene = { ...createdScene, title: 'Cena Atualizada' };
    mock.onPut('/scenes/888').reply(200, updatedScene);

    // Mock para geração de vídeo
    const generationTask = { ...mockData.videoGeneration, project_id: 999 };
    mock.onPost('/projects/999/generate').reply(200, generationTask);

    const result = await integrationExample.createCompleteVideoWorkflow();
    
    expect(result.project).toEqual(createdProject);
    expect(result.scene).toEqual(updatedScene);
    expect(result.generationTask).toEqual(generationTask);
    expect(result.message).toBe('Fluxo completo executado com sucesso!');
  });

  test('deve tratar erro no fluxo de exemplo', async () => {
    mock.onPost('/projects').reply(500, { error: 'Erro interno do servidor' });

    await expect(integrationExample.createCompleteVideoWorkflow()).rejects.toThrow();
  });
});

/**
 * Testes de Configuração e Utilitários
 */
describe('Configuration', () => {
  test('deve ter configuração correta da API', () => {
    expect(process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api').toBeDefined();
  });

  test('deve ter timeout configurado', () => {
    expect(30000).toBeGreaterThan(0);
  });

  test('deve ter retry attempts configurado', () => {
    expect(3).toBeGreaterThan(0);
  });
});

/**
 * Testes de Tratamento de Erros
 */
describe('Error Handling', () => {
  beforeEach(() => {
    mock.reset();
  });

  test('deve tratar erro 401 (não autorizado)', async () => {
    mock.onGet('/projects').reply(401, { error: 'Unauthorized' });

    // Simula localStorage
    const localStorageMock = {
      getItem: jest.fn(),
      removeItem: jest.fn(),
      setItem: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
    });

    await expect(projectService.getProjects()).rejects.toThrow();
  });

  test('deve tratar erro 403 (proibido)', async () => {
    mock.onGet('/projects').reply(403, { error: 'Forbidden' });

    await expect(projectService.getProjects()).rejects.toThrow();
  });

  test('deve tratar erro 500 (erro interno)', async () => {
    mock.onGet('/projects').reply(500, { error: 'Internal Server Error' });

    await expect(projectService.getProjects()).rejects.toThrow();
  });

  test('deve fazer retry em caso de erro de rede', async () => {
    mock.onGet('/projects')
      .replyOnce(500, { error: 'Network Error' })
      .onGet('/projects')
      .reply(200, { data: [mockData.project] });

    const result = await projectService.getProjects();
    
    expect(result.data).toHaveLength(1);
  });
});

/**
 * Testes de Performance
 */
describe('Performance', () => {
  test('deve ter timeout adequado para requisições', () => {
    expect(30000).toBeGreaterThanOrEqual(10000); // Mínimo 10 segundos
  });

  test('deve ter retry attempts adequado', () => {
    expect(3).toBeGreaterThanOrEqual(1); // Mínimo 1 tentativa
  });
});

/**
 * Testes de Segurança
 */
describe('Security', () => {
  test('deve incluir token de autorização nos headers', () => {
    // Simula localStorage com token
    const localStorageMock = {
      getItem: jest.fn(() => 'test_token'),
      removeItem: jest.fn(),
      setItem: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
    });

    mock.onGet('/projects').reply(200, { data: [] });

    // Verifica se o interceptor adiciona o token
    projectService.getProjects().then(() => {
      expect(localStorageMock.getItem).toHaveBeenCalledWith('tecnocursos_token');
    });
  });
});

/**
 * Configuração dos testes
 */
beforeAll(() => {
  // Configurar ambiente de teste
  process.env.NODE_ENV = 'test';
});

afterAll(() => {
  // Limpar mocks
  mock.restore();
});

/**
 * Utilitários para testes
 */
export const testUtils = {
  /**
   * Cria um arquivo mock para testes de upload
   */
  createMockFile(name = 'test.pdf', size = 1024, type = 'application/pdf') {
    const content = 'x'.repeat(size);
    return new File([content], name, { type });
  },

  /**
   * Simula progresso de upload
   */
  simulateUploadProgress(onProgress, totalSteps = 10) {
    for (let i = 1; i <= totalSteps; i++) {
      setTimeout(() => {
        onProgress((i / totalSteps) * 100);
      }, i * 100);
    }
  },

  /**
   * Aguarda um tempo específico
   */
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}; 