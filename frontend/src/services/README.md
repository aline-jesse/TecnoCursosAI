# Integração com Backend FastAPI

## Configuração

1. Copie o arquivo `.env.example` para `.env` e configure as variáveis:
   - `REACT_APP_API_BASE_URL`: URL base do backend
   - `REACT_APP_API_TIMEOUT`: Tempo limite para requisições

## Serviços Disponíveis

### ProjectService

Métodos principais:

- `fetchProjects(token)`: Busca lista de projetos
- `fetchScenes(projectId, token)`: Busca cenas de um projeto
- `uploadFile(file, token)`: Upload de PDF/PPTX
- `saveScenes(projectId, scenes, token)`: Salva dados das cenas
- `generateVideo(projectId, token)`: Gera vídeo final
- `downloadVideo(projectId, token)`: Baixa vídeo gerado

### Exemplo de Uso no Componente

```jsx
import { useProjects } from '../hooks/useProjects';

function ProjectEditor() {
  const {
    projects,
    scenes,
    uploadFile,
    saveScenes,
    generateVideo,
    downloadVideo,
  } = useProjects();

  const handleUpload = async file => {
    try {
      const uploadResponse = await uploadFile(file);
      // Processar resposta
    } catch (error) {
      // Tratar erro
    }
  };

  // Outros métodos similares
}
```

## Requisitos

- Axios para requisições HTTP
- Token de autenticação válido
- Configuração do `.env`

## Tratamento de Erros

Todos os métodos lançam exceções em caso de erro, que devem ser tratadas no componente.

## Considerações

- Sempre verifique o token de autenticação
- Trate os estados de carregamento e erro
- Respeite os timeouts configurados
