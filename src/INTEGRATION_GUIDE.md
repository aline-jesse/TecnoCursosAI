# Guia de Integração React + FastAPI - TecnoCursos AI

Este guia explica como configurar e usar a integração completa entre o frontend React e o backend FastAPI.

## 📋 Índice

1. [Configuração Inicial](#configuração-inicial)
2. [Arquitetura da Integração](#arquitetura-da-integração)
3. [Serviços Disponíveis](#serviços-disponíveis)
4. [Hooks Customizados](#hooks-customizados)
5. [Fluxo de Trabalho](#fluxo-de-trabalho)
6. [Tratamento de Erros](#tratamento-de-erros)
7. [Exemplos de Uso](#exemplos-de-uso)

## 🚀 Configuração Inicial

### 1. Instalar Dependências

```bash
# Instalar Axios e outras dependências necessárias
npm install axios react-toastify react-icons

# Para TypeScript (opcional)
npm install --save-dev @types/axios
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env.local` na raiz do projeto React:

```env
# URL do backend FastAPI
REACT_APP_API_URL=http://localhost:8000

# URL do WebSocket (opcional)
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 3. Configurar Notificações

No seu componente principal (`App.jsx`):

```jsx
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <>
      {/* Seus componentes */}
      <ToastContainer />
    </>
  );
}
```

## 🏗️ Arquitetura da Integração

### Estrutura de Pastas

```
src/
├── config/
│   └── api.config.js       # Configurações da API
├── services/
│   ├── api.js              # Instância Axios configurada
│   ├── projectService.js   # Serviço de projetos
│   ├── fileService.js      # Serviço de arquivos
│   ├── sceneService.js     # Serviço de cenas
│   └── videoService.js     # Serviço de vídeos
├── hooks/
│   ├── useProjects.js      # Hook de projetos
│   ├── useFileUpload.js    # Hook de upload
│   ├── useVideoGeneration.js # Hook de vídeos
│   └── useNotification.js  # Hook de notificações
└── components/
    └── ProjectWorkflow.jsx # Componente exemplo
```

### Fluxo de Dados

```
Componente React
    ↓
Hook Customizado (gerencia estado e lógica)
    ↓
Serviço (faz chamadas à API)
    ↓
API Base (Axios com interceptors)
    ↓
Backend FastAPI
```

## 📦 Serviços Disponíveis

### 1. ProjectService

Gerencia operações de projetos:

```javascript
import projectService from '../services/projectService';

// Listar projetos
const { data, total } = await projectService.listProjects({
  skip: 0,
  limit: 20,
  status: 'active',
  search: 'curso',
});

// Criar projeto
const newProject = await projectService.createProject({
  name: 'Novo Curso',
  description: 'Descrição do curso',
  tags: 'programação, web',
});

// Atualizar projeto
const updated = await projectService.updateProject(projectId, {
  name: 'Nome Atualizado',
});

// Deletar projeto
await projectService.deleteProject(projectId);
```

### 2. FileService

Gerencia upload e manipulação de arquivos:

```javascript
import fileService from '../services/fileService';

// Upload simples
const result = await fileService.uploadFile({
  file: fileObject,
  projectId: '123',
  onProgress: progress => console.log(`${progress}%`),
});

// Upload múltiplo
const results = await fileService.uploadMultipleFiles({
  files: fileList,
  projectId: '123',
  onProgress: totalProgress => console.log(`Total: ${totalProgress}%`),
  onFileComplete: (filename, success, data) => {
    console.log(`${filename}: ${success ? 'sucesso' : 'falhou'}`);
  },
});

// Upload em chunks (arquivos grandes)
const largeFileResult = await fileService.uploadFileChunked({
  file: largeFile,
  projectId: '123',
  onProgress: progress => console.log(`Chunk progress: ${progress}%`),
});
```

### 3. SceneService

Gerencia cenas/slides:

```javascript
import sceneService from '../services/sceneService';

// Criar cena
const newScene = await sceneService.createScene({
  projectId: '123',
  title: 'Introdução',
  content: 'Conteúdo da cena',
  duration: 10,
  assets: [
    {
      type: 'image',
      url: '/path/to/image.jpg',
      position: { x: 0, y: 0, width: 100, height: 100 },
    },
  ],
});

// Atualizar cena
await sceneService.updateScene(sceneId, {
  content: 'Novo conteúdo',
});

// Reordenar cenas
await sceneService.reorderScenes(projectId, [
  { id: 'scene1', order: 0 },
  { id: 'scene2', order: 1 },
]);
```

### 4. VideoService

Gerencia geração e download de vídeos:

```javascript
import videoService from '../services/videoService';

// Gerar vídeo
const { videoId, taskId } = await videoService.generateVideo({
  projectId: '123',
  settings: {
    resolution: '1080p',
    fps: 30,
    format: 'mp4',
  },
  audioSettings: {
    includeNarration: true,
    voiceType: 'pt-br',
  },
});

// Monitorar progresso
const monitor = videoService.monitorProgress(videoId, status => {
  console.log(`Progresso: ${status.progress}%`);
  console.log(`Status: ${status.status}`);
  console.log(`Etapa: ${status.currentStep}`);
});

// Parar monitoramento
monitor.stop();

// Baixar vídeo
await videoService.downloadVideo(videoId, 'meu-video.mp4');
```

## 🪝 Hooks Customizados

### 1. useProjects

Hook para gerenciar projetos com estado e loading automático:

```jsx
import { useProjects } from '../hooks/useProjects';

function MyComponent() {
  const {
    projects,
    selectedProject,
    loading,
    error,
    createProject,
    selectProject,
    deleteProject,
  } = useProjects();

  // Criar projeto
  const handleCreate = async () => {
    try {
      const newProject = await createProject({
        name: 'Novo Projeto',
        description: 'Descrição',
      });
      console.log('Projeto criado:', newProject);
    } catch (error) {
      console.error('Erro:', error);
    }
  };

  return (
    <div>
      {loading && <p>Carregando...</p>}
      {error && <p>Erro: {error}</p>}

      {projects.map(project => (
        <div key={project.id} onClick={() => selectProject(project)}>
          {project.name}
        </div>
      ))}
    </div>
  );
}
```

### 2. useFileUpload

Hook para upload de arquivos com progresso:

```jsx
import { useFileUpload } from '../hooks/useFileUpload';

function UploadComponent({ projectId }) {
  const {
    uploading,
    uploadProgress,
    totalProgress,
    uploadFile,
    uploadMultipleFiles,
  } = useFileUpload(projectId);

  const handleUpload = async event => {
    const files = event.target.files;

    if (files.length === 1) {
      await uploadFile(files[0]);
    } else {
      await uploadMultipleFiles(files);
    }
  };

  return (
    <div>
      <input
        type='file'
        multiple
        onChange={handleUpload}
        disabled={uploading}
      />

      {uploading && (
        <div>
          <p>Progresso Total: {totalProgress}%</p>

          {Object.entries(uploadProgress).map(([id, info]) => (
            <div key={id}>
              {info.name}: {info.progress}% ({info.status})
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 3. useVideoGeneration

Hook para geração de vídeos:

```jsx
import { useVideoGeneration } from '../hooks/useVideoGeneration';

function VideoGenerator({ projectId }) {
  const {
    generating,
    generationProgress,
    videos,
    generateVideo,
    downloadVideo,
  } = useVideoGeneration(projectId);

  const handleGenerate = async () => {
    await generateVideo({
      resolution: '1080p',
      includeNarration: true,
      voiceType: 'pt-br',
    });
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={generating}>
        {generating ? 'Gerando...' : 'Gerar Vídeo'}
      </button>

      {generating && (
        <div>
          <p>{generationProgress.currentStep}</p>
          <progress value={generationProgress.progress} max='100' />
        </div>
      )}

      {videos.map(video => (
        <div key={video.id}>
          <p>
            Vídeo #{video.id} - {video.status}
          </p>
          {video.status === 'completed' && (
            <button onClick={() => downloadVideo(video.id)}>Baixar</button>
          )}
        </div>
      ))}
    </div>
  );
}
```

## 🔄 Fluxo de Trabalho

### Fluxo Completo de Criação de Vídeo

1. **Criar/Selecionar Projeto**

   ```jsx
   const { createProject, selectProject } = useProjects();
   const project = await createProject({ name: 'Meu Curso' });
   selectProject(project);
   ```

2. **Upload de Arquivo PDF/PPTX**

   ```jsx
   const { uploadFile } = useFileUpload(project.id);
   await uploadFile(file);
   ```

3. **Editar Cenas (Opcional)**

   ```jsx
   await sceneService.updateScene(sceneId, {
     content: 'Novo conteúdo',
     duration: 15,
   });
   ```

4. **Gerar Vídeo**

   ```jsx
   const { generateVideo } = useVideoGeneration(project.id);
   await generateVideo({
     resolution: '1080p',
     includeNarration: true,
   });
   ```

5. **Baixar Vídeo**
   ```jsx
   const { downloadVideo } = useVideoGeneration(project.id);
   await downloadVideo(videoId, 'curso-completo.mp4');
   ```

## ⚠️ Tratamento de Erros

### Erros Automáticos

A integração trata automaticamente:

- **401 Unauthorized**: Renova token automaticamente
- **429 Too Many Requests**: Retry com backoff exponencial
- **5xx Server Errors**: Retry automático até 3 vezes

### Tratamento Manual

```jsx
try {
  await projectService.createProject(data);
} catch (error) {
  if (error.status === 400) {
    // Erro de validação
    console.error('Dados inválidos:', error.data);
  } else if (error.code === 'NETWORK_ERROR') {
    // Erro de rede
    console.error('Sem conexão');
  } else {
    // Outros erros
    console.error('Erro:', error.message);
  }
}
```

## 💡 Exemplos de Uso

### Componente de Upload com Drag & Drop

```jsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFileUpload } from '../hooks/useFileUpload';

function DropzoneUpload({ projectId }) {
  const { uploadMultipleFiles, uploading } = useFileUpload(projectId);

  const onDrop = useCallback(
    async acceptedFiles => {
      await uploadMultipleFiles({ files: acceptedFiles });
    },
    [uploadMultipleFiles]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-powerpoint': ['.ppt', '.pptx'],
    },
    disabled: uploading,
  });

  return (
    <div {...getRootProps()} className='dropzone'>
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Solte os arquivos aqui...</p>
      ) : (
        <p>Arraste arquivos ou clique para selecionar</p>
      )}
    </div>
  );
}
```

### Monitoramento em Tempo Real com WebSocket

```jsx
import { useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api.config';

function RealtimeMonitor({ projectId }) {
  useEffect(() => {
    const ws = new WebSocket(API_ENDPOINTS.websocket.url);

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          type: 'subscribe',
          projectId,
        })
      );
    };

    ws.onmessage = event => {
      const data = JSON.parse(event.data);
      console.log('Update:', data);
    };

    return () => ws.close();
  }, [projectId]);

  return <div>Monitorando projeto...</div>;
}
```

## 🔧 Configurações Avançadas

### Cache Personalizado

```javascript
// Desabilitar cache para uma requisição específica
api.get('/api/data', { cache: false });

// Cache com TTL customizado
api.get('/api/data', { cacheTTL: 10000 }); // 10 segundos

// Limpar cache
import { clearCache } from '../services/api';
clearCache('/api/projects'); // Limpar cache específico
clearCache(); // Limpar todo o cache
```

### Timeout Customizado

```javascript
// Para operações longas
api.post('/api/long-operation', data, {
  timeout: 120000, // 2 minutos
});
```

## 📝 Notas Importantes

1. **Autenticação**: Os tokens são gerenciados automaticamente. Apenas faça login uma vez.
2. **Progresso**: Todos os uploads e downloads suportam callbacks de progresso.
3. **Retry**: Erros de rede e servidor são retentados automaticamente.
4. **Cache**: Requisições GET são cacheadas por padrão para melhor performance.
5. **Notificações**: Sucessos e erros são notificados automaticamente via toast.

## 🆘 Suporte

Para problemas ou dúvidas:

1. Verifique os logs do console do navegador
2. Confirme que o backend está rodando em `http://localhost:8000`
3. Verifique as variáveis de ambiente no `.env.local`
4. Teste os endpoints diretamente em `http://localhost:8000/docs`
