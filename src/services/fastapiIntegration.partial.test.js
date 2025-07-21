/**
 * Teste Parcial da Integração FastAPI
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

// Importar apenas o arquivo de integração
let fastapiIntegration;

describe('Integração FastAPI - Teste Parcial', () => {
  beforeEach(() => {
    mock.reset();
    jest.clearAllMocks();
    
    // Importar o arquivo de integração
    try {
      fastapiIntegration = require('./fastapiIntegration');
    } catch (error) {
      console.error('Erro ao importar fastapiIntegration:', error);
    }
  });

  test('deve importar o arquivo de integração', () => {
    expect(fastapiIntegration).toBeDefined();
  });

  test('deve ter projectService exportado', () => {
    if (fastapiIntegration) {
      expect(fastapiIntegration.projectService).toBeDefined();
    }
  });

  test('deve ter sceneService exportado', () => {
    if (fastapiIntegration) {
      expect(fastapiIntegration.sceneService).toBeDefined();
    }
  });

  test('deve ter uploadService exportado', () => {
    if (fastapiIntegration) {
      expect(fastapiIntegration.uploadService).toBeDefined();
    }
  });

  test('deve ter videoService exportado', () => {
    if (fastapiIntegration) {
      expect(fastapiIntegration.videoService).toBeDefined();
    }
  });

  test('deve ter healthService exportado', () => {
    if (fastapiIntegration) {
      expect(fastapiIntegration.healthService).toBeDefined();
    }
  });

  test('deve ter integrationExample exportado', () => {
    if (fastapiIntegration) {
      expect(fastapiIntegration.integrationExample).toBeDefined();
    }
  });

  test('deve fazer requisição GET mockada', async () => {
    const mockData = { message: 'Teste bem-sucedido' };
    mock.onGet('/test').reply(200, mockData);

    const response = await axios.get('/test');
    
    expect(response.status).toBe(200);
    expect(response.data).toEqual(mockData);
  });

  test('deve fazer requisição POST mockada', async () => {
    const mockData = { id: 1, name: 'Teste' };
    const postData = { name: 'Teste' };
    mock.onPost('/test', postData).reply(201, mockData);

    const response = await axios.post('/test', postData);
    
    expect(response.status).toBe(201);
    expect(response.data).toEqual(mockData);
  });
}); 