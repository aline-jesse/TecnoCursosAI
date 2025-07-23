# Integração Frontend React com Backend FastAPI via Axios

## 📋 Visão Geral

Este documento descreve a integração completa entre o frontend React e o backend FastAPI do sistema TecnoCursos AI, implementada através do Axios para comunicação HTTP.

### 🎯 Funcionalidades Implementadas

- ✅ **Buscar lista de projetos e cenas** (GET)
- ✅ **Upload de arquivos PDF/PPTX** (POST /upload)
- ✅ **Salvar/editar cenas** (POST /scene)
- ✅ **Download de vídeos finais** (GET /project/{id}/video)
- ✅ **Tratamento de erros e retry automático**
- ✅ **Interceptadores para autenticação**
- ✅ **Testes completos com mocks**

## 🚀 Configuração Rápida

### 1. Instalação de Dependências

```bash
# Instalar Axios e dependências de teste
npm install axios axios-mock-adapter

# Para desenvolvimento
npm install --save-dev jest @testing-library/react
```

### 2. Configuração da URL do Backend

#### Opção A: Variáveis de Ambiente

Crie um arquivo `.env.local` na raiz do projeto:

```env
# Backend FastAPI
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Configurações de Upload
REACT_APP_MAX_FILE_SIZE=50000000
REACT_APP_CHUNK_SIZE=1048576

# Configurações de Autenticação
REACT_APP_JWT_STORAGE_KEY=tecnocursos_token
REACT_APP_USER_STORAGE_KEY=tecnocursos_user
```

#### Opção B: Configuração Dinâmica

```javascript
// src/config/environment.js
const config = {
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  // ... outras configurações
};
```

#### Opção C: Configuração via localStorage

```javascript
// Configurar via código
localStorage.setItem('api_base_url', 'http://localhost:8000/api');

// Ou via interface do usuário
const setBackendUrl = (url) => {
  localStorage.setItem('api_base_url', url);
  window.location.reload(); // Recarregar para aplicar mudanças
};
```

## 📚 Guia de Uso

### 1. Serviço de Projetos

```javascript
import { projectService } from './services/fastapiIntegration';

// Buscar todos os projetos
const projects = await projectService.getProjects({
  page: 1,
  limit: 20,
  search: 'curso python',
  sort: 'created_at',
  order: 'desc'
});

// Criar novo projeto
const newProject = await projectService.createProject({
  name: 'Curso de Python Avançado',
  description: 'Vídeo educativo sobre Python',
  template: 'educational',
  settings: {
    resolution: '1920x1080',
    fps: 30,
    quality: 'high'
  }
});

// Atualizar projeto
const updatedProject = await projectService.updateProject(123, {
  name: 'Curso Python Atualizado',
  description: 'Nova descrição do curso'
});

// Remover projeto
await projectService.deleteProject(123);
```

### 2. Serviço de Cenas

```javascript
import { sceneService } from './services/fastapiIntegration';

// Buscar cenas de um projeto
const scenes = await sceneService.getProjectScenes(123, {
  page: 1,
  limit: 50,
  sort: 'order'
});

// Criar nova cena
const newScene = await sceneService.createScene({
  title: 'Introdução ao Python',
  content: 'Python é uma linguagem de programação...',
  duration: 10000, // 10 segundos
  project_id: 123,
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
});

// Salvar/editar cena
const updatedScene = await sceneService.updateScene(456, {
  title: 'Introdução Atualizada',
  content: 'Conteúdo atualizado da cena...',
  duration: 12000,
  elements: {
    background: 'office',
    character: 'student',
    text: {
      content: 'Conteúdo atualizado...',
      position: { x: 150, y: 250 },
      style: { fontSize: 28, color: '#000000' }
    }
  }
});

// Reordenar cenas
await sceneService.reorderScenes(123, [456, 789, 101]);
```

### 3. Serviço de Upload

```javascript
import { uploadService } from './services/fastapiIntegration';

// Upload simples
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];

const uploadedFile = await uploadService.uploadFile(file, 123, (progress) => {
  console.log(`Upload: ${progress}%`);
});

// Upload de arquivo grande em chunks
const largeFile = fileInput.files[0];
const uploadedFile = await uploadService.uploadLargeFile(
  largeFile, 
  123, 
  (progress) => console.log(`Progresso: ${progress}%`),
  { chunkSize: 1024 * 1024 } // 1MB por chunk
);

// Listar arquivos enviados
const files = await uploadService.getFiles(123, {
  page: 1,
  limit: 20,
  type: 'pdf'
});

// Obter estatísticas
const stats = await uploadService.getUploadStats(123);
console.log(`Total de arquivos: ${stats.total_files}`);
console.log(`Espaço usado: ${stats.total_size_mb}MB`);
```

### 4. Serviço de Vídeos

```javascript
import { videoService } from './services/fastapiIntegration';

// Gerar vídeo do projeto
const generationTask = await videoService.generateVideo(123, {
  resolution: '1920x1080',
  quality: 'high',
  format: 'mp4',
  includeAudio: true,
  audioQuality: 'high',
  watermark: false,
  subtitles: true,
  language: 'pt-BR'
});

// Monitorar progresso da geração
const checkProgress = async () => {
  const status = await videoService.getGenerationStatus(123, generationTask.task_id);
  
  if (status.status === 'completed') {
    // Download do vídeo final
    const videoBlob = await videoService.downloadVideo(123);
    const videoUrl = URL.createObjectURL(videoBlob);
    
    // Criar link de download
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = 'meu_video.mp4';
    link.click();
  } else if (status.status === 'failed') {
    console.error('Erro na geração do vídeo:', status.error);
  } else {
    console.log(`Progresso: ${status.progress}%`);
    setTimeout(checkProgress, 2000); // Verificar novamente em 2 segundos
  }
};

checkProgress();

// Listar vídeos gerados
const videos = await videoService.getVideos({
  page: 1,
  limit: 10,
  project_id: 123,
  status: 'completed'
});
```

### 5. Serviço de Health Check

```javascript
import { healthService } from './services/fastapiIntegration';

// Verificar saúde geral da API
const health = await healthService.checkHealth();
console.log(`API Status: ${health.status}`);

// Verificar saúde específica da API
const apiHealth = await healthService.checkApiHealth();
console.log(`Database: ${apiHealth.database}`);
console.log(`Storage: ${apiHealth.storage}`);

// Obter status detalhado do sistema
const systemStatus = await healthService.getSystemStatus();
console.log(`CPU Usage: ${systemStatus.cpu_usage}%`);
console.log(`Memory Usage: ${systemStatus.memory_usage}%`);
```

## 🔧 Exemplo de Integração Completa

```javascript
import { 
  projectService, 
  sceneService, 
  uploadService, 
  videoService 
} from './services/fastapiIntegration';

/**
 * Exemplo: Fluxo completo de criação de vídeo
 */
const createCompleteVideo = async () => {
  try {
    // 1. Criar novo projeto
    const project = await projectService.createProject({
      name: 'Tutorial Python',
      description: 'Curso básico de Python',
      template: 'educational'
    });

    // 2. Fazer upload de arquivo PDF
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    const uploadedFile = await uploadService.uploadFile(file, project.id);

    // 3. Criar cenas baseadas no arquivo
    const scene1 = await sceneService.createScene({
      title: 'Introdução',
      content: 'Bem-vindo ao curso de Python!',
      duration: 5000,
      project_id: project.id,
      elements: {
        background: 'classroom',
        character: 'teacher',
        text: {
          content: 'Bem-vindo ao curso de Python!',
          position: { x: 100, y: 200 },
          style: { fontSize: 24, color: '#ffffff' }
        }
      }
    });

    // 4. Salvar alterações na cena
    await sceneService.updateScene(scene1.id, {
      title: 'Introdução Atualizada',
      content: 'Bem-vindo ao curso completo de Python!',
      elements: {
        text: {
          content: 'Bem-vindo ao curso completo de Python!',
          style: { fontSize: 28, color: '#000000' }
        }
      }
    });

    // 5. Gerar vídeo final
    const generationTask = await videoService.generateVideo(project.id, {
      resolution: '1920x1080',
      quality: 'high',
      includeAudio: true
    });

    // 6. Monitorar progresso da geração
    const checkProgress = async () => {
      const status = await videoService.getGenerationStatus(project.id, generationTask.task_id);
      
      if (status.status === 'completed') {
        // 7. Download do vídeo final
        const videoBlob = await videoService.downloadVideo(project.id);
        const videoUrl = URL.createObjectURL(videoBlob);
        
        // Criar link de download
        const link = document.createElement('a');
        link.href = videoUrl;
        link.download = `${project.name}.mp4`;
        link.click();
        
        console.log('Vídeo gerado com sucesso!');
      } else if (status.status === 'failed') {
        console.error('Erro na geração do vídeo:', status.error);
      } else {
        console.log(`Progresso: ${status.progress}%`);
        setTimeout(checkProgress, 2000);
      }
    };

    checkProgress();

  } catch (error) {
    console.error('Erro no fluxo de criação:', error);
  }
};
```

## 🧪 Testes

### Executar Testes

```bash
# Executar todos os testes
npm test

# Executar testes específicos
npm test -- --testNamePattern="ProjectService"

# Executar testes com coverage
npm test -- --coverage
```

### Exemplo de Teste

```javascript
import { projectService } from './services/fastapiIntegration';
import MockAdapter from 'axios-mock-adapter';
import axios from 'axios';

const mock = new MockAdapter(axios);

describe('ProjectService', () => {
  test('deve buscar lista de projetos com sucesso', async () => {
    const mockResponse = {
      data: [{ id: 123, name: 'Curso de Python' }],
      total: 1,
      page: 1,
      limit: 20
    };

    mock.onGet('/projects').reply(200, mockResponse);

    const result = await projectService.getProjects();
    
    expect(result).toEqual(mockResponse);
    expect(result.data).toHaveLength(1);
    expect(result.data[0].name).toBe('Curso de Python');
  });
});
```

## 🔒 Autenticação

### Configuração de Token JWT

```javascript
// O serviço automaticamente adiciona o token JWT aos headers
// Certifique-se de que o token está armazenado no localStorage

// Login
const login = async (credentials) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  
  const data = await response.json();
  
  if (data.access_token) {
    localStorage.setItem('tecnocursos_token', data.access_token);
    localStorage.setItem('tecnocursos_user', JSON.stringify(data.user));
  }
};

// Logout
const logout = () => {
  localStorage.removeItem('tecnocursos_token');
  localStorage.removeItem('tecnocursos_user');
  window.location.href = '/login';
};
```

### Interceptadores Automáticos

O serviço inclui interceptadores que:

1. **Adicionam token automaticamente** aos headers de todas as requisições
2. **Tratam erros 401** redirecionando para login
3. **Fazem retry automático** em caso de falhas de rede
4. **Logam requisições** para debug

## 🚨 Tratamento de Erros

### Tipos de Erro

```javascript
try {
  const projects = await projectService.getProjects();
} catch (error) {
  if (error.response?.status === 401) {
    // Token expirado - redirecionar para login
    window.location.href = '/login';
  } else if (error.response?.status === 403) {
    // Acesso negado
    console.error('Acesso negado');
  } else if (error.response?.status === 500) {
    // Erro interno do servidor
    console.error('Erro interno do servidor');
  } else {
    // Outros erros
    console.error('Erro:', error.message);
  }
}
```

### Retry Automático

O serviço faz retry automático em caso de:
- Erros de rede
- Timeouts
- Erros 5xx (exceto 500)

```javascript
// Configuração de retry
const withRetry = async (apiCall, maxRetries = 3, delay = 1000) => {
  // Implementação automática de retry
};
```

## 📊 Monitoramento e Logs

### Logs Automáticos

```javascript
// Logs são gerados automaticamente para:
// - Requisições (método, URL, dados)
// - Respostas (status, dados)
// - Erros (detalhes completos)
// - Progresso de upload
// - Status de geração de vídeo
```

### Métricas de Performance

```javascript
// Timeout configurado
const TIMEOUT = 30000; // 30 segundos

// Retry attempts
const RETRY_ATTEMPTS = 3;

// Chunk size para upload
const CHUNK_SIZE = 1024 * 1024; // 1MB
```

## 🔧 Configuração Avançada

### Personalizar Configurações

```javascript
// src/config/environment.js
export const config = {
  // API Configuration
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  
  // Upload Configuration
  MAX_FILE_SIZE: 50000000, // 50MB
  CHUNK_SIZE: 1048576, // 1MB
  ALLOWED_FILE_TYPES: ['.pdf', '.pptx', '.docx', '.txt', '.jpg', '.png', '.mp4'],
  
  // Authentication
  JWT_STORAGE_KEY: 'tecnocursos_token',
  USER_STORAGE_KEY: 'tecnocursos_user',
  
  // Development
  DEBUG: process.env.NODE_ENV === 'development',
  LOG_LEVEL: 'debug'
};
```

### Configuração de CORS

No backend FastAPI, certifique-se de configurar CORS:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de CORS

**Sintoma:** Erro "CORS policy" no console do navegador

**Solução:**
```python
# No backend FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. Token não encontrado

**Sintoma:** Erro 401 em todas as requisições

**Solução:**
```javascript
// Verificar se o token existe
const token = localStorage.getItem('tecnocursos_token');
if (!token) {
  // Redirecionar para login
  window.location.href = '/login';
}
```

#### 3. Upload falha

**Sintoma:** Upload de arquivos não funciona

**Solução:**
```javascript
// Verificar tamanho do arquivo
const maxSize = 50000000; // 50MB
if (file.size > maxSize) {
  alert('Arquivo muito grande');
  return;
}

// Verificar tipo do arquivo
const allowedTypes = ['.pdf', '.pptx', '.docx'];
const fileExtension = file.name.split('.').pop().toLowerCase();
if (!allowedTypes.includes(`.${fileExtension}`)) {
  alert('Tipo de arquivo não permitido');
  return;
}
```

#### 4. Timeout em requisições

**Sintoma:** Requisições demoram muito ou falham

**Solução:**
```javascript
// Aumentar timeout
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 segundos
});
```

#### 5. Erro de rede

**Sintoma:** "Network Error" ou "ERR_NETWORK"

**Solução:**
```javascript
// Verificar se o backend está rodando
const checkBackendHealth = async () => {
  try {
    const response = await fetch('http://localhost:8000/health');
    if (response.ok) {
      console.log('Backend está funcionando');
    }
  } catch (error) {
    console.error('Backend não está acessível:', error);
  }
};
```

## 📈 Performance

### Otimizações Implementadas

1. **Retry automático** para falhas de rede
2. **Upload em chunks** para arquivos grandes
3. **Progress tracking** para uploads
4. **Timeout configurável** para requisições
5. **Interceptadores otimizados** para logs e autenticação

### Métricas Recomendadas

```javascript
// Monitorar performance
const performanceMetrics = {
  requestTime: 0,
  uploadSpeed: 0,
  errorRate: 0,
  successRate: 0
};

// Exemplo de monitoramento
const startTime = Date.now();
try {
  const result = await projectService.getProjects();
  const endTime = Date.now();
  performanceMetrics.requestTime = endTime - startTime;
  performanceMetrics.successRate++;
} catch (error) {
  performanceMetrics.errorRate++;
}
```

## 🔄 Versionamento

### Histórico de Versões

- **v2.0.0** - Integração completa com FastAPI
- **v1.5.0** - Adicionado retry automático
- **v1.0.0** - Versão inicial com Axios

### Migração de Versões

```javascript
// Migração de v1 para v2
// Antes
import { apiService } from './services/apiService';

// Depois
import { projectService, sceneService, uploadService, videoService } from './services/fastapiIntegration';
```

## 📞 Suporte

### Recursos de Ajuda

1. **Documentação da API:** `http://localhost:8000/docs`
2. **Health Check:** `http://localhost:8000/health`
3. **Logs do Backend:** Verificar console do servidor
4. **Logs do Frontend:** Verificar console do navegador

### Contato

- **Email:** suporte@tecnocursos.ai
- **GitHub:** [Issues do projeto](https://github.com/tecnocursos/ai-editor/issues)
- **Documentação:** [Wiki do projeto](https://github.com/tecnocursos/ai-editor/wiki)

---

**Última atualização:** Janeiro 2025  
**Versão:** 2.0.0  
**Autor:** TecnoCursos AI Team 