# 🚀 Guia de Uso - SceneList Component

## Instalação Rápida

```bash
# Instalar dependências
npm install react react-dom react-beautiful-dnd @heroicons/react tailwindcss

# Configurar TailwindCSS
npx tailwindcss init -p
```

## Uso Básico

```jsx
import SceneList from './components/SceneList';
import useSceneList from './hooks/useSceneList';

function MyComponent() {
  const {
    scenes,
    activeSceneId,
    selectScene,
    addScene,
    removeScene,
    duplicateScene,
    reorderScenes
  } = useSceneList('project-id');

  return (
    <SceneList
      scenes={scenes}
      activeSceneId={activeSceneId}
      onSceneSelect={selectScene}
      onSceneAdd={addScene}
      onSceneRemove={removeScene}
      onSceneDuplicate={duplicateScene}
      onSceneReorder={reorderScenes}
    />
  );
}
```

## Funcionalidades

- ✅ **Adicionar cena**: Clique no botão +
- ✅ **Selecionar cena**: Clique na cena desejada
- ✅ **Remover cena**: Clique no botão 🗑 (cena ativa)
- ✅ **Duplicar cena**: Clique no botão 📋 (cena ativa)
- ✅ **Reordenar**: Arraste e solte as cenas

## Configuração Backend

```javascript
// Configurar URL do backend
process.env.REACT_APP_API_URL = 'http://localhost:8000';

// Configurar token de autenticação
sceneListService.setAuthToken('your-jwt-token');
```

## Testes

```bash
# Executar testes unitários
npm test

# Executar testes de integração
python test_scene_list_backend.py
```

## Suporte

- 📚 Documentação: INSTALACAO_DEPENDENCIAS_SCENELIST.md
- 🧪 Testes: src/components/SceneList.test.js
- 🔧 Exemplo: src/App.jsx
