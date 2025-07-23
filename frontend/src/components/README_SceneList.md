# 🎬 SceneList Component

## 📋 Visão Geral

O `SceneList` é um componente React para gerenciar uma lista de cenas em um editor de vídeos. Ele oferece funcionalidades completas de CRUD (Create, Read, Update, Delete) com drag-and-drop para reordenação.

## ✨ Funcionalidades

### 🎯 Principais
- **Lista vertical de cenas** com miniaturas
- **Drag-and-drop** para reordenação
- **Adicionar/remover/duplicar** cenas
- **Seleção de cena** para edição
- **Miniaturas automáticas** baseadas em assets ou texto
- **Formatação de duração** (MM:SS)
- **Estado global** controlado via props

### 🎨 Interface
- **Design responsivo** com TailwindCSS
- **Animações suaves** de hover e drag
- **Feedback visual** para cena ativa
- **Botões de ação** que aparecem no hover
- **Estatísticas** no footer (total de cenas, duração)

## 🚀 Como Usar

### Importação
```jsx
import SceneList from './components/SceneList';
```

### Uso Básico
```jsx
<SceneList
  scenes={scenes}
  activeSceneId={activeSceneId}
  onSceneSelect={handleSceneSelect}
  onSceneAdd={handleSceneAdd}
  onSceneRemove={handleSceneRemove}
  onSceneDuplicate={handleSceneDuplicate}
  onScenesReorder={handleScenesReorder}
/>
```

### Exemplo Completo
```jsx
import React, { useState, useCallback } from 'react';
import SceneList from './components/SceneList';

function VideoEditor() {
  const [scenes, setScenes] = useState([
    {
      id: 'scene-1',
      name: 'Introdução',
      ordem: 1,
      duracao: 10,
      texto: 'Bem-vindo ao curso!',
      assets: []
    }
  ]);
  
  const [activeSceneId, setActiveSceneId] = useState('scene-1');

  const handleSceneSelect = useCallback((sceneId) => {
    setActiveSceneId(sceneId);
  }, []);

  const handleSceneAdd = useCallback(() => {
    const newScene = {
      id: `scene-${Date.now()}`,
      name: `Cena ${scenes.length + 1}`,
      ordem: scenes.length + 1,
      duracao: 5,
      texto: '',
      assets: []
    };
    setScenes(prev => [...prev, newScene]);
  }, [scenes.length]);

  const handleSceneRemove = useCallback((sceneId) => {
    setScenes(prev => prev.filter(scene => scene.id !== sceneId));
  }, []);

  const handleSceneDuplicate = useCallback((sceneId) => {
    const sceneToDuplicate = scenes.find(s => s.id === sceneId);
    if (!sceneToDuplicate) return;

    const duplicatedScene = {
      ...sceneToDuplicate,
      id: `scene-${Date.now()}`,
      name: `${sceneToDuplicate.name} (Cópia)`,
      ordem: scenes.length + 1
    };
    setScenes(prev => [...prev, duplicatedScene]);
  }, [scenes]);

  const handleScenesReorder = useCallback((sourceIndex, destinationIndex) => {
    setScenes(prev => {
      const reordered = [...prev];
      const [moved] = reordered.splice(sourceIndex, 1);
      reordered.splice(destinationIndex, 0, moved);
      return reordered.map((scene, index) => ({
        ...scene,
        ordem: index + 1
      }));
    });
  }, []);

  return (
    <SceneList
      scenes={scenes}
      activeSceneId={activeSceneId}
      onSceneSelect={handleSceneSelect}
      onSceneAdd={handleSceneAdd}
      onSceneRemove={handleSceneRemove}
      onSceneDuplicate={handleSceneDuplicate}
      onScenesReorder={handleScenesReorder}
    />
  );
}
```

## 📊 Props

| Prop | Tipo | Obrigatório | Descrição |
|------|------|-------------|-----------|
| `scenes` | `Array<Scene>` | ✅ | Lista de cenas |
| `activeSceneId` | `string` | ✅ | ID da cena atualmente selecionada |
| `onSceneSelect` | `function` | ✅ | Callback quando uma cena é selecionada |
| `onSceneAdd` | `function` | ✅ | Callback para adicionar nova cena |
| `onSceneRemove` | `function` | ✅ | Callback para remover cena |
| `onSceneDuplicate` | `function` | ✅ | Callback para duplicar cena |
| `onScenesReorder` | `function` | ✅ | Callback para reordenar cenas |
| `className` | `string` | ❌ | Classes CSS adicionais |

## 📝 Estrutura de Dados

### Scene Object
```typescript
interface Scene {
  id: string;
  name: string;
  ordem: number;
  duracao: number;
  texto?: string;
  assets?: Asset[];
}
```

### Asset Object
```typescript
interface Asset {
  id: string;
  caminho_arquivo?: string;
  tipo: 'image' | 'video' | 'audio' | 'text';
}
```

## 🎨 Estilos

O componente usa TailwindCSS para estilização. Principais classes:

- **Container**: `bg-gray-50 border-r border-gray-200 w-80 flex flex-col`
- **Header**: `p-4 border-b border-gray-200 bg-white`
- **Scene Item**: `bg-white rounded-lg border-2 cursor-pointer`
- **Active Scene**: `border-blue-500 shadow-lg`
- **Hover Effects**: `hover:border-gray-300 transition-all duration-200`

## 🔧 Funcionalidades Internas

### Geração de Miniatura
```jsx
const getSceneThumbnail = useCallback((scene) => {
  // Prioridade: assets > texto > fallback
  if (scene.assets?.length > 0) {
    return scene.assets[0].caminho_arquivo;
  }
  if (scene.texto) {
    return `data:text/plain;base64,${btoa(scene.texto.substring(0, 50))}`;
  }
  return '/placeholder-scene.png';
}, []);
```

### Formatação de Duração
```jsx
const formatDuration = useCallback((duration) => {
  const minutes = Math.floor(duration / 60);
  const seconds = Math.floor(duration % 60);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}, []);
```

### Drag and Drop
```jsx
const handleDragEnd = useCallback((result) => {
  if (!result.destination) return;
  
  const sourceIndex = result.source.index;
  const destinationIndex = result.destination.index;
  
  if (sourceIndex !== destinationIndex) {
    onScenesReorder(sourceIndex, destinationIndex);
  }
}, [onScenesReorder]);
```

## 🧪 Testes

O componente inclui testes unitários completos:

```bash
# Executar testes
npm test SceneList

# Executar em modo watch
npm test SceneList -- --watch
```

### Cobertura de Testes
- ✅ Renderização da lista
- ✅ Seleção de cenas
- ✅ Adição de cenas
- ✅ Remoção de cenas
- ✅ Duplicação de cenas
- ✅ Drag and drop
- ✅ Formatação de duração
- ✅ Estados especiais
- ✅ Acessibilidade
- ✅ Performance

## 🐛 Solução de Problemas

### Erro: "react-beautiful-dnd not found"
```bash
npm install react-beautiful-dnd
```

### Erro: "Cannot resolve @heroicons/react"
```bash
npm install @heroicons/react
```

### Drag and drop não funciona
Verifique se o `DragDropContext` está envolvendo o componente:
```jsx
import { DragDropContext } from 'react-beautiful-dnd';

<DragDropContext onDragEnd={handleDragEnd}>
  <SceneList {...props} />
</DragDropContext>
```

### Miniaturas não aparecem
Certifique-se de que:
1. O arquivo `/public/placeholder-scene.png` existe
2. Os assets têm `caminho_arquivo` válido
3. As imagens são acessíveis

## 🔄 Changelog

### v1.0.0
- ✅ Implementação inicial
- ✅ Drag and drop funcional
- ✅ CRUD completo
- ✅ Testes unitários
- ✅ Documentação completa

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a documentação
- Verifique os testes para exemplos de uso

---

**Desenvolvido com ❤️ para o TecnoCursos AI** 