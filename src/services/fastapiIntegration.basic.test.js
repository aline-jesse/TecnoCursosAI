/**
 * Teste Básico da Integração FastAPI
 * TecnoCursos AI - Editor de Vídeo Inteligente
 */

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// Mock do axios
const mock = new MockAdapter(axios);

// Configuração básica do cliente
const API_BASE_URL = 'http://localhost:8000/api';
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

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

describe('Integração FastAPI - Teste Básico', () => {
  beforeEach(() => {
    mock.reset();
    jest.clearAllMocks();
  });

  test('deve configurar cliente axios com baseURL', () => {
    expect(apiClient.defaults.baseURL).toBe(API_BASE_URL);
    expect(apiClient.defaults.timeout).toBe(30000);
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
  });

  test('deve fazer requisição GET para projetos', async () => {
    const mockProjects = {
      data: [
        {
          id: 1,
          name: 'Curso de Python',
          description: 'Vídeo educativo sobre Python',
          created_at: '2024-01-15T10:00:00Z',
        }
      ],
      total: 1,
      page: 1,
      limit: 20
    };

    mock.onGet('/projects').reply(200, mockProjects);

    const response = await apiClient.get('/projects');
    
    expect(response.status).toBe(200);
    expect(response.data).toEqual(mockProjects);
    expect(response.data.data).toHaveLength(1);
    expect(response.data.data[0].name).toBe('Curso de Python');
  });

  test('deve fazer requisição POST para criar projeto', async () => {
    const newProject = {
      name: 'Novo Projeto',
      description: 'Descrição do novo projeto',
      template: 'educational'
    };

    const createdProject = {
      id: 2,
      ...newProject,
      created_at: '2024-01-15T11:00:00Z',
      updated_at: '2024-01-15T11:00:00Z'
    };

    mock.onPost('/projects', newProject).reply(201, createdProject);

    const response = await apiClient.post('/projects', newProject);
    
    expect(response.status).toBe(201);
    expect(response.data).toEqual(createdProject);
    expect(response.data.name).toBe('Novo Projeto');
  });

  test('deve fazer requisição GET para cenas de um projeto', async () => {
    const mockScenes = {
      data: [
        {
          id: 1,
          title: 'Introdução ao Python',
          content: 'Python é uma linguagem de programação...',
          duration: 10000,
          project_id: 1,
          order: 1
        }
      ],
      total: 1,
      page: 1,
      limit: 50
    };

    mock.onGet('/projects/1/scenes').reply(200, mockScenes);

    const response = await apiClient.get('/projects/1/scenes');
    
    expect(response.status).toBe(200);
    expect(response.data).toEqual(mockScenes);
    expect(response.data.data).toHaveLength(1);
    expect(response.data.data[0].title).toBe('Introdução ao Python');
  });

  test('deve fazer upload de arquivo', async () => {
    const mockFile = new File(['conteúdo do arquivo'], 'test.pdf', {
      type: 'application/pdf'
    });

    const mockUploadResponse = {
      id: 1,
      filename: 'test.pdf',
      original_name: 'test.pdf',
      file_size: 1024,
      file_type: 'pdf',
      status: 'uploaded'
    };

    mock.onPost('/upload').reply(200, mockUploadResponse);

    const formData = new FormData();
    formData.append('file', mockFile);

    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    expect(response.status).toBe(200);
    expect(response.data).toEqual(mockUploadResponse);
    expect(response.data.filename).toBe('test.pdf');
  });

  test('deve tratar erro 401 (não autorizado)', async () => {
    mock.onGet('/projects').reply(401, { error: 'Unauthorized' });

    try {
      await apiClient.get('/projects');
    } catch (error) {
      expect(error.response.status).toBe(401);
      expect(error.response.data.error).toBe('Unauthorized');
    }
  });

  test('deve tratar erro 500 (erro interno)', async () => {
    mock.onGet('/projects').reply(500, { error: 'Internal Server Error' });

    try {
      await apiClient.get('/projects');
    } catch (error) {
      expect(error.response.status).toBe(500);
      expect(error.response.data.error).toBe('Internal Server Error');
    }
  });

  test('deve verificar saúde da API', async () => {
    const mockHealth = {
      status: 'healthy',
      uptime: 3600,
      version: '2.0.0',
      timestamp: '2024-01-15T10:00:00Z'
    };

    mock.onGet('/health').reply(200, mockHealth);

    const response = await apiClient.get('/health');
    
    expect(response.status).toBe(200);
    expect(response.data).toEqual(mockHealth);
    expect(response.data.status).toBe('healthy');
  });
}); 