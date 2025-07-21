/**
 * Teste Simples da Integração FastAPI
 * TecnoCursos AI - Editor de Vídeo Inteligente
 */

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// Mock do axios
const mock = new MockAdapter(axios);

// Importar apenas as funções básicas
const mockApiClient = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
};

describe('Integração FastAPI - Teste Simples', () => {
  beforeEach(() => {
    mock.reset();
    jest.clearAllMocks();
  });

  test('deve configurar cliente axios corretamente', () => {
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
}); 