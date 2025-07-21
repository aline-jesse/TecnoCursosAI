# Integração Zustand para Estado Global do Editor

Este documento explica como usar a store Zustand implementada para gerenciar o estado global do editor de vídeo.

## 📦 Instalação

O Zustand já foi instalado via npm:

```bash
npm install zustand
```

## 🏗️ Estrutura da Store

### Interfaces Principais

```typescript
interface Asset {
  id: string;
  name: string;
  type: 'image' | 'video' | 'audio' | 'text';
  url: string;
  thumbnail?: string;
  duration?: number;
  size?: number;
  createdAt: Date;
  tags?: string[];
}

interface Scene {
  id: string;
  name: string;
  duration: number;
  assets: Asset[];
  background?: string;
  transitions?: {
    in: string;
    out: string;
  };
  createdAt: Date;
  updatedAt: Date;
}

interface Selection {
  type: 'scene' | 'asset' | 'none';
  id?: string;
  sceneId?: string;
}

interface PlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
}
```

## 🎯 Hooks Disponíveis

### Hooks Principais

```typescript
// Hook completo da store
const { scenes, assets, addScene, addAsset, ... } = useEditor();

// Hooks específicos
const scenes = useScenes();
const activeScene = useActiveScene();
const assets = useAssets();
const selection = useSelection();
const playerState = usePlayerState();
const isLoading = useLoading();
const error = useError();
```

### Hooks Especializados

```typescript
// Assets filtrados por tipo
const imageAssets = useAssetsByType('image');
const videoAssets = useAssetsByType('video');

// Cena ativa com assets
const activeSceneWithAssets = useActiveSceneWithAssets();
```

## 📝 Como Adicionar Cenas

### Método 1: Usando o hook completo

```typescript
import { useEditor } from '../store/editorStore';

const MyComponent = () => {
  const { addScene } = useEditor();

  const handleAddScene = () => {
    addScene({
      name: 'Nova Cena',
      duration: 10, // em segundos
      assets: [],
    });
  };

  return <button onClick={handleAddScene}>Adicionar Cena</button>;
};
```

### Método 2: Usando hook específico

```typescript
import { useScenes } from '../store/editorStore';

const SceneList = () => {
  const scenes = useScenes();
  
  return (
    <div>
      {scenes.map(scene => (
        <div key={scene.id}>{scene.name}</div>
      ))}
    </div>
  );
};
```

## 🎨 Como Adicionar Assets

### Upload de Arquivo

```typescript
import { useEditor } from '../store/editorStore';

const AssetUploader = () => {
  const { addAsset } = useEditor();

  const handleFileUpload = (file: File) => {
    const fileUrl = URL.createObjectURL(file);
    
    addAsset({
      name: file.name,
      type: getAssetType(file), // função para determinar tipo
      url: fileUrl,
      thumbnail: file.type.startsWith('image/') ? fileUrl : undefined,
      size: file.size,
      tags: [file.type.split('/')[0], file.name.split('.').pop() || ''],
    });
  };

  return <input type="file" onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])} />;
};
```

### Adicionar Asset a uma Cena

```typescript
const { addAssetToScene } = useEditor();

const handleAddToScene = (assetId: string, sceneId: string) => {
  addAssetToScene(assetId, sceneId);
};
```

## ✏️ Como Editar Cenas e Assets

### Editar Cena

```typescript
const { updateScene } = useEditor();

const handleEditScene = (sceneId: string) => {
  updateScene(sceneId, {
    name: 'Novo Nome',
    duration: 15,
    background: 'https://example.com/background.jpg',
  });
};
```

### Editar Asset

```typescript
const { updateAsset } = useEditor();

const handleEditAsset = (assetId: string) => {
  updateAsset(assetId, {
    name: 'Novo Nome do Asset',
    tags: ['novo', 'tag'],
  });
};
```

## 🗑️ Como Remover Cenas e Assets

### Remover Cena

```typescript
const { deleteScene } = useEditor();

const handleDeleteScene = (sceneId: string) => {
  if (window.confirm('Tem certeza que deseja excluir esta cena?')) {
    deleteScene(sceneId);
  }
};
```

### Remover Asset

```typescript
const { deleteAsset } = useEditor();

const handleDeleteAsset = (assetId: string) => {
  if (window.confirm('Tem certeza que deseja excluir este asset?')) {
    deleteAsset(assetId);
  }
};
```

### Remover Asset de uma Cena

```typescript
const { removeAssetFromScene } = useEditor();

const handleRemoveFromScene = (assetId: string, sceneId: string) => {
  removeAssetFromScene(assetId, sceneId);
};
```

## 🎮 Controles do Player

### Reprodução

```typescript
const { play, pause, seek, setVolume, toggleMute } = useEditor();

// Reproduzir
play();

// Pausar
pause();

// Buscar tempo específico (em segundos)
seek(30.5);

// Controlar volume (0-1)
setVolume(0.8);

// Alternar mute
toggleMute();
```

### Estado do Player

```typescript
const playerState = usePlayerState();

// playerState contém:
// - isPlaying: boolean
// - currentTime: number
// - duration: number
// - volume: number
// - isMuted: boolean
```

## 🎯 Gerenciamento de Seleção

### Definir Seleção

```typescript
const { setSelection, clearSelection } = useEditor();

// Selecionar cena
setSelection({
  type: 'scene',
  id: 'scene-123',
  sceneId: 'scene-123',
});

// Selecionar asset
setSelection({
  type: 'asset',
  id: 'asset-456',
  sceneId: 'scene-123',
});

// Limpar seleção
clearSelection();
```

### Verificar Seleção

```typescript
const selection = useSelection();

if (selection.type === 'scene') {
  console.log('Cena selecionada:', selection.id);
} else if (selection.type === 'asset') {
  console.log('Asset selecionado:', selection.id);
}
```

## 🔄 Estados de Loading e Erro

### Loading

```typescript
const { setLoading } = useEditor();
const isLoading = useLoading();

// Ativar loading
setLoading(true);

// Desativar loading
setLoading(false);
```

### Erro

```typescript
const { setError } = useEditor();
const error = useError();

// Definir erro
setError('Erro de upload');

// Limpar erro
setError(null);
```

## 📊 Exemplos de Uso nos Componentes

### EditorCanvas

```typescript
import { useActiveScene, useSelection, useEditor } from '../store/editorStore';

const EditorCanvas = () => {
  const activeScene = useActiveScene();
  const selection = useSelection();
  const { setSelection, addAssetToScene } = useEditor();

  const handleAssetClick = (assetId: string) => {
    setSelection({
      type: 'asset',
      id: assetId,
      sceneId: activeScene?.id,
    });
  };

  const handleDrop = (assetId: string) => {
    if (activeScene) {
      addAssetToScene(assetId, activeScene.id);
    }
  };

  return (
    <div>
      {activeScene?.assets.map(asset => (
        <div key={asset.id} onClick={() => handleAssetClick(asset.id)}>
          {asset.name}
        </div>
      ))}
    </div>
  );
};
```

### SceneList

```typescript
import { useScenes, useActiveScene, useEditor } from '../store/editorStore';

const SceneList = () => {
  const scenes = useScenes();
  const activeScene = useActiveScene();
  const { addScene, setActiveScene, deleteScene } = useEditor();

  const handleAddScene = () => {
    addScene({
      name: 'Nova Cena',
      duration: 10,
      assets: [],
    });
  };

  const handleSelectScene = (sceneId: string) => {
    setActiveScene(sceneId);
  };

  return (
    <div>
      <button onClick={handleAddScene}>Adicionar Cena</button>
      {scenes.map(scene => (
        <div 
          key={scene.id}
          className={activeScene?.id === scene.id ? 'active' : ''}
          onClick={() => handleSelectScene(scene.id)}
        >
          {scene.name}
        </div>
      ))}
    </div>
  );
};
```

### AssetPanel

```typescript
import { useAssets, useEditor } from '../store/editorStore';

const AssetPanel = () => {
  const assets = useAssets();
  const { addAsset, deleteAsset } = useEditor();

  const handleFileUpload = (file: File) => {
    const fileUrl = URL.createObjectURL(file);
    
    addAsset({
      name: file.name,
      type: getAssetType(file),
      url: fileUrl,
      size: file.size,
    });
  };

  const handleDeleteAsset = (assetId: string) => {
    deleteAsset(assetId);
  };

  return (
    <div>
      <input type="file" onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])} />
      {assets.map(asset => (
        <div key={asset.id}>
          {asset.name}
          <button onClick={() => handleDeleteAsset(asset.id)}>Excluir</button>
        </div>
      ))}
    </div>
  );
};
```

## 🧪 Testes

Execute os testes da store:

```bash
npm test src/store/editorStore.test.ts
```

Os testes cobrem:
- ✅ Adicionar, editar e deletar cenas
- ✅ Adicionar, editar e deletar assets
- ✅ Gerenciamento de seleção
- ✅ Controles do player
- ✅ Estados de loading e erro

## 🔧 Middlewares

A store utiliza os seguintes middlewares:

### DevTools
Para debugging no desenvolvimento:
```typescript
devtools({
  name: 'editor-store',
})
```

### Persist
Para persistência no localStorage:
```typescript
persist({
  name: 'editor-store',
  partialize: (state) => ({
    scenes: state.scenes,
    assets: state.assets,
    playerState: state.playerState,
  }),
})
```

## 📈 Performance

### Otimizações Implementadas

1. **Seletores Específicos**: Use hooks específicos em vez do hook completo quando possível
2. **Imutabilidade**: Todas as atualizações são imutáveis
3. **Persistência Seletiva**: Apenas dados essenciais são persistidos
4. **Hooks Personalizados**: Hooks otimizados para casos de uso específicos

### Boas Práticas

```typescript
// ✅ Bom - Use hooks específicos
const scenes = useScenes();
const activeScene = useActiveScene();

// ❌ Evite - Use hook completo quando não necessário
const { scenes, activeScene } = useEditor();

// ✅ Bom - Use callbacks para funções
const handleAddScene = useCallback(() => {
  addScene({ name: 'Nova Cena', duration: 10, assets: [] });
}, [addScene]);

// ❌ Evite - Funções inline
<button onClick={() => addScene({ name: 'Nova Cena', duration: 10, assets: [] })}>
```

## 🚀 Próximos Passos

1. **Sincronização com Backend**: Implementar `syncState()` para sincronizar com APIs
2. **Histórico de Undo/Redo**: Adicionar middleware para histórico de ações
3. **Validação**: Implementar validação de dados na store
4. **Performance**: Adicionar memoização para seletores complexos
5. **Testes**: Expandir cobertura de testes para casos edge

## 📚 Recursos Adicionais

- [Documentação oficial do Zustand](https://github.com/pmndrs/zustand)
- [Guia de middlewares](https://github.com/pmndrs/zustand#middleware)
- [Padrões de performance](https://github.com/pmndrs/zustand#performance)

---

**Commit**: `feat: integrar Zustand para estado global`

**Status**: ✅ Implementação completa e funcional 