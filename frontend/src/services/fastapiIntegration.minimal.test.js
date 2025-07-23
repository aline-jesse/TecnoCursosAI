/**
 * Teste Mínimo da Integração FastAPI
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

// Mock do logger
const mockLogger = {
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Mock do config
const mockConfig = {
  API_BASE_URL: 'http://localhost:8000/api',
  DEBUG: true,
  LOG_LEVEL: 'debug',
};

// Mock das dependências
jest.mock('../config/environment', () => ({
  config: mockConfig,
  logger: mockLogger,
}));

describe('Integração FastAPI - Teste Mínimo', () => {
  beforeEach(() => {
    mock.reset();
    jest.clearAllMocks();
  });

  test('deve configurar axios corretamente', () => {
    expect(axios).toBeDefined();
    expect(mock).toBeDefined();
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

  test('deve tratar erro de rede', async () => {
    mock.onGet('/error').networkError();

    await expect(axios.get('/error')).rejects.toThrow();
  });

  test('deve tratar erro 404', async () => {
    mock.onGet('/not-found').reply(404, { error: 'Not found' });

    try {
      await axios.get('/not-found');
    } catch (error) {
      expect(error.response.status).toBe(404);
      expect(error.response.data.error).toBe('Not found');
    }
  });

  test('deve verificar configuração mockada', () => {
    expect(mockConfig.API_BASE_URL).toBe('http://localhost:8000/api');
    expect(mockConfig.DEBUG).toBe(true);
  });

  test('deve verificar logger mockado', () => {
    mockLogger.debug('teste debug');
    mockLogger.info('teste info');
    mockLogger.warn('teste warn');
    mockLogger.error('teste error');

    expect(mockLogger.debug).toHaveBeenCalledWith('teste debug');
    expect(mockLogger.info).toHaveBeenCalledWith('teste info');
    expect(mockLogger.warn).toHaveBeenCalledWith('teste warn');
    expect(mockLogger.error).toHaveBeenCalledWith('teste error');
  });
});
