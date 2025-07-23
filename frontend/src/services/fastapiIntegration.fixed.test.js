/**
 * Teste Corrigido da Integração FastAPI
 * TecnoCursos AI - Editor de Vídeo Inteligente
 */

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// Mock do axios
const mock = new MockAdapter(axios);

// Mock do localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock do window.location
delete window.location;
window.location = {
  href: 'http://localhost:3000',
  pathname: '/',
  search: '',
  hash: '',
  reload: jest.fn(),
};

// Mock das dependências
jest.mock('../config/environment', () => ({
  config: {
    API_BASE_URL: 'http://localhost:8000/api',
    DEBUG: true,
    LOG_LEVEL: 'debug',
  },
  logger: {
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  },
}));

// Importar o arquivo de integração
const fastapiIntegration = require('./fastapiIntegration');

describe('Integração FastAPI - Teste Corrigido', () => {
  beforeEach(() => {
    mock.reset();
    jest.clearAllMocks();
  });

  describe('ProjectService', () => {
    test('deve buscar lista de projetos com sucesso', async () => {
      const mockProjects = {
        data: [
          {
            id: 123,
            name: 'Curso de Python',
            description: 'Vídeo educativo sobre Python',
            created_at: '2024-01-15T10:00:00Z',
            updated_at: '2024-01-15T10:00:00Z',
            status: 'active',
            template: 'educational',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
        pages: 1,
      };

      mock.onGet('/projects').reply(200, mockProjects);

      const result = await fastapiIntegration.projectService.getProjects();

      expect(result).toEqual(mockProjects);
      expect(result.data).toHaveLength(1);
      expect(result.data[0].name).toBe('Curso de Python');
    });

    test('deve buscar projeto específico por ID', async () => {
      const mockProject = {
        id: 123,
        name: 'Curso de Python',
        description: 'Vídeo educativo sobre Python',
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:00:00Z',
        status: 'active',
        template: 'educational',
      };

      mock.onGet('/projects/123').reply(200, mockProject);

      const result = await fastapiIntegration.projectService.getProject(123);

      expect(result).toEqual(mockProject);
      expect(result.id).toBe(123);
      expect(result.name).toBe('Curso de Python');
    });

    test('deve criar novo projeto', async () => {
      const newProjectData = {
        name: 'Novo Projeto',
        description: 'Descrição do novo projeto',
        template: 'educational',
      };

      const createdProject = {
        id: 124,
        ...newProjectData,
        created_at: '2024-01-15T11:00:00Z',
        updated_at: '2024-01-15T11:00:00Z',
        status: 'active',
      };

      mock.onPost('/projects').reply(201, createdProject);

      const result =
        await fastapiIntegration.projectService.createProject(newProjectData);

      expect(result).toEqual(createdProject);
      expect(result.name).toBe('Novo Projeto');
    });

    test('deve atualizar projeto existente', async () => {
      const updates = {
        name: 'Curso Python Atualizado',
        description: 'Nova descrição do curso',
      };

      const updatedProject = {
        id: 123,
        ...updates,
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T12:00:00Z',
        status: 'active',
        template: 'educational',
      };

      mock.onPut('/projects/123').reply(200, updatedProject);

      const result = await fastapiIntegration.projectService.updateProject(
        123,
        updates
      );

      expect(result).toEqual(updatedProject);
      expect(result.name).toBe('Curso Python Atualizado');
    });

    test('deve remover projeto', async () => {
      const deleteResponse = { message: 'Projeto removido com sucesso' };
      mock.onDelete('/projects/123').reply(200, deleteResponse);

      const result = await fastapiIntegration.projectService.deleteProject(123);

      expect(result).toEqual(deleteResponse);
    });

    test('deve tratar erro ao buscar projetos', async () => {
      mock.onGet('/projects').reply(500, { error: 'Erro interno do servidor' });

      await expect(
        fastapiIntegration.projectService.getProjects()
      ).rejects.toThrow();
    });
  });

  describe('SceneService', () => {
    test('deve buscar cenas de um projeto', async () => {
      const mockScenes = {
        data: [
          {
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
                style: { fontSize: 24, color: '#ffffff' },
              },
            },
            audio: {
              voice: 'pt-BR',
              speed: 1.0,
              volume: 0.8,
            },
          },
        ],
        total: 1,
        page: 1,
        limit: 50,
      };

      mock.onGet('/projects/123/scenes').reply(200, mockScenes);

      const result =
        await fastapiIntegration.sceneService.getProjectScenes(123);

      expect(result).toEqual(mockScenes);
      expect(result.data).toHaveLength(1);
      expect(result.data[0].title).toBe('Introdução ao Python');
    });

    test('deve criar nova cena', async () => {
      const newSceneData = {
        title: 'Nova Cena',
        content: 'Conteúdo da nova cena',
        duration: 5000,
        project_id: 123,
        order: 2,
        elements: {
          background: 'classroom',
          character: 'teacher',
          text: {
            content: 'Conteúdo da nova cena',
            position: { x: 100, y: 200 },
            style: { fontSize: 24, color: '#ffffff' },
          },
        },
      };

      const createdScene = {
        id: 457,
        ...newSceneData,
        created_at: '2024-01-15T11:30:00Z',
        updated_at: '2024-01-15T11:30:00Z',
      };

      mock.onPost('/scenes').reply(201, createdScene);

      const result =
        await fastapiIntegration.sceneService.createScene(newSceneData);

      expect(result).toEqual(createdScene);
      expect(result.title).toBe('Nova Cena');
    });
  });

  describe('UploadService', () => {
    test('deve fazer upload de arquivo com sucesso', async () => {
      const mockFile = new File(['conteúdo do arquivo'], 'test.pdf', {
        type: 'application/pdf',
      });

      const mockUploadResponse = {
        id: 789,
        filename: 'test.pdf',
        original_name: 'test.pdf',
        file_size: 1024000,
        file_type: 'pdf',
        project_id: 123,
        uploaded_at: '2024-01-15T10:30:00Z',
        status: 'processed',
        extracted_text: 'Conteúdo extraído do PDF...',
      };

      mock.onPost('/upload').reply(200, mockUploadResponse);

      const result = await fastapiIntegration.uploadService.uploadFile(
        mockFile,
        123
      );

      expect(result).toEqual(mockUploadResponse);
      expect(result.filename).toBe('test.pdf');
      expect(result.status).toBe('processed');
    });

    test('deve listar arquivos enviados', async () => {
      const mockFiles = {
        data: [
          {
            id: 789,
            filename: 'test.pdf',
            original_name: 'test.pdf',
            file_size: 1024000,
            file_type: 'pdf',
            project_id: 123,
            uploaded_at: '2024-01-15T10:30:00Z',
            status: 'processed',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
      };

      mock.onGet('/upload/files').reply(200, mockFiles);

      const result = await fastapiIntegration.uploadService.getFiles();

      expect(result).toEqual(mockFiles);
      expect(result.data).toHaveLength(1);
      expect(result.data[0].filename).toBe('test.pdf');
    });
  });

  describe('VideoService', () => {
    test('deve gerar vídeo do projeto', async () => {
      const mockGenerationResponse = {
        task_id: 'task_abc123',
        project_id: 123,
        status: 'processing',
        progress: 0,
        created_at: '2024-01-15T11:00:00Z',
        estimated_completion: '2024-01-15T11:05:00Z',
      };

      mock.onPost('/projects/123/generate').reply(202, mockGenerationResponse);

      const result = await fastapiIntegration.videoService.generateVideo(123);

      expect(result).toEqual(mockGenerationResponse);
      expect(result.task_id).toBe('task_abc123');
      expect(result.status).toBe('processing');
    });

    test('deve verificar status da geração de vídeo', async () => {
      const mockStatusResponse = {
        task_id: 'task_abc123',
        project_id: 123,
        status: 'completed',
        progress: 100,
        created_at: '2024-01-15T11:00:00Z',
        completed_at: '2024-01-15T11:05:00Z',
      };

      mock.onGet('/projects/123/video/status').reply(200, mockStatusResponse);

      const result = await fastapiIntegration.videoService.getGenerationStatus(
        123,
        'task_abc123'
      );

      expect(result).toEqual(mockStatusResponse);
      expect(result.status).toBe('completed');
      expect(result.progress).toBe(100);
    });
  });

  describe('HealthService', () => {
    test('deve verificar saúde geral da API', async () => {
      const mockHealthResponse = {
        status: 'healthy',
        uptime: 3600,
        version: '2.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      mock.onGet('/health').reply(200, mockHealthResponse);

      const result = await fastapiIntegration.healthService.checkHealth();

      expect(result).toEqual(mockHealthResponse);
      expect(result.status).toBe('healthy');
    });

    test('deve verificar saúde específica da API', async () => {
      const mockApiHealthResponse = {
        api_status: 'healthy',
        database_status: 'healthy',
        cache_status: 'healthy',
        timestamp: '2024-01-15T10:00:00Z',
      };

      mock.onGet('/api/health').reply(200, mockApiHealthResponse);

      const result = await fastapiIntegration.healthService.checkApiHealth();

      expect(result).toEqual(mockApiHealthResponse);
      expect(result.api_status).toBe('healthy');
    });
  });

  describe('IntegrationExample', () => {
    test('deve executar fluxo completo de criação de vídeo', async () => {
      // Mock para criação de projeto
      const mockProject = {
        id: 123,
        name: 'Exemplo de Integração',
        description: 'Vídeo criado via integração API',
        template: 'educational',
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:00:00Z',
        status: 'active',
      };

      // Mock para criação de cena
      const mockScene = {
        id: 456,
        title: 'Cena Atualizada',
        content: 'Esta é uma cena atualizada via API',
        duration: 5000,
        project_id: 123,
        order: 1,
        elements: {
          background: 'classroom',
          character: 'teacher',
          text: {
            content: 'Esta é uma cena atualizada via API',
            style: { fontSize: 28, color: '#000000' },
          },
        },
      };

      // Mock para geração de vídeo
      const mockGenerationTask = {
        task_id: 'task_abc123',
        project_id: 123,
        status: 'processing',
        progress: 0,
        created_at: '2024-01-15T11:00:00Z',
      };

      mock.onPost('/projects').reply(201, mockProject);
      mock.onPost('/scenes').reply(201, mockScene);
      mock.onPut('/scenes/456').reply(200, mockScene);
      mock.onPost('/projects/123/generate').reply(202, mockGenerationTask);

      const result =
        await fastapiIntegration.integrationExample.createCompleteVideoWorkflow();

      expect(result).toBeDefined();
      expect(result.project).toEqual(mockProject);
      expect(result.scene).toEqual(mockScene);
      expect(result.generationTask).toEqual(mockGenerationTask);
      expect(result.message).toBe('Fluxo completo executado com sucesso!');
    });
  });
});
