# AssetPanel - Painel de Gerenciamento de Assets

O `AssetPanel` é um componente React avançado para gerenciamento de assets em editores de vídeo, com funcionalidades completas de drag and drop, upload de arquivos, criação de personagens e organização por categorias.

## 🚀 Funcionalidades

### ✅ Implementadas
- **Lista de personagens/avatares** com miniaturas
- **Botões para adicionar texto**, upload de imagem, upload de áudio/música
- **Drag and drop** para arrastar assets para o EditorCanvas
- **Função para criar novo personagem** (simulado no MVP)
- **Recebe via props**: lista de assets, função para adicionar/remover asset
- **Código comentado em português**
- **Testes unitários completos**
- **Interface responsiva e moderna**

### 🎯 Características Técnicas
- **React Beautiful DnD** para drag and drop
- **Categorização por tipos**: personagens, imagens, áudio, texto
- **Busca em tempo real** com filtros
- **Upload de múltiplos arquivos** com preview
- **Modal para criação de personagens**
- **Estatísticas de assets** no footer
- **Animações suaves** e feedback visual

## 📦 Instalação

O componente já está integrado ao projeto. Dependências necessárias:

```bash
npm install react-beautiful-dnd
```

## 🎨 Uso Básico

```jsx
import AssetPanel from './components/AssetPanel';

function App() {
  const [assets, setAssets] = useState([]);

  const handleAssetAdd = (newAsset) => {
    setAssets(prev => [...prev, newAsset]);
  };

  const handleAssetRemove = (assetId) => {
    setAssets(prev => prev.filter(asset => asset.id !== assetId));
  };

  const handleAssetSelect = (asset) => {
    console.log('Asset selecionado:', asset);
  };

  const handleCreateCharacter = (newCharacter) => {
    setAssets(prev => [...prev, newCharacter]);
    console.log('Novo personagem criado:', newCharacter);
  };

  return (
    <AssetPanel
      assets={assets}
      onAssetAdd={handleAssetAdd}
      onAssetRemove={handleAssetRemove}
      onAssetSelect={handleAssetSelect}
      onCreateCharacter={handleCreateCharacter}
    />
  );
}
```

## 🔧 Props

| Prop | Tipo | Obrigatório | Descrição |
|------|------|-------------|-----------|
| `assets` | `Array` | ✅ | Lista de assets disponíveis |
| `onAssetAdd` | `Function` | ✅ | Callback chamado quando um asset é adicionado |
| `onAssetRemove` | `Function` | ✅ | Callback chamado quando um asset é removido |
| `onAssetSelect` | `Function` | ❌ | Callback chamado quando um asset é selecionado |
| `onCreateCharacter` | `Function` | ❌ | Callback chamado quando um novo personagem é criado |
| `className` | `String` | ❌ | Classes CSS adicionais |

## 📋 Estrutura de Asset

```javascript
const asset = {
  id: 'asset-123',
  name: 'Nome do Asset',
  type: 'avatar', // 'avatar', 'image', 'audio', 'text', 'video'
  url: '/path/to/asset',
  thumbnail: '/path/to/thumbnail', // opcional
  size: 1024, // em bytes
  content: 'Conteúdo do texto', // apenas para type: 'text'
  style: { // apenas para type: 'text'
    fontSize: '16px',
    color: '#000000',
    fontFamily: 'Arial'
  },
  properties: { // apenas para type: 'avatar'
    gender: 'neutral',
    age: 'adult',
    style: 'professional'
  },
  createdAt: '2024-01-01T00:00:00.000Z'
};
```

## 🎮 Funcionalidades Detalhadas

### 1. Categorização por Abas
- **👤 Personagens**: Avatares e personagens customizados
- **🖼️ Imagens**: Imagens de fundo, elementos visuais
- **🎵 Áudio**: Músicas, narrações, efeitos sonoros
- **📝 Texto**: Elementos de texto editáveis

### 2. Busca e Filtros
```javascript
// Busca em tempo real
const searchTerm = 'personagem'; // Filtra por nome
const activeTab = 'characters'; // Filtra por categoria
```

### 3. Upload de Arquivos
```javascript
// Suporta múltiplos tipos
const supportedTypes = {
  image: ['image/*'],
  audio: ['audio/*'],
  video: ['video/*']
};
```

### 4. Criação de Personagens
```javascript
// Modal interativo para criar personagens
const newCharacter = {
  id: `character-${Date.now()}`,
  name: 'Nome do Personagem',
  type: 'avatar',
  url: '/assets/characters/default-avatar.svg',
  properties: {
    gender: 'neutral',
    age: 'adult',
    style: 'professional'
  }
};
```

### 5. Drag and Drop
```javascript
// Integração com react-beautiful-dnd
<Draggable draggableId={asset.id} index={index}>
  {(provided, snapshot) => (
    <div
      ref={provided.innerRef}
      {...provided.draggableProps}
      {...provided.dragHandleProps}
    >
      {/* Conteúdo do asset */}
    </div>
  )}
</Draggable>
```

## 🧪 Testes

O componente inclui testes unitários completos:

```bash
npm test AssetPanel.test.js
```

### Cobertura de Testes
- ✅ Renderização correta
- ✅ Filtros por categoria
- ✅ Busca em tempo real
- ✅ Adição/remoção de assets
- ✅ Criação de personagens
- ✅ Upload de arquivos
- ✅ Drag and drop
- ✅ Estados vazios
- ✅ Acessibilidade

## 🎨 Estilização

O componente usa CSS customizado com:

- **Gradientes modernos**
- **Animações suaves**
- **Responsividade completa**
- **Scrollbar personalizada**
- **Efeitos hover**
- **Estados de loading**

### Classes CSS Principais
```css
.asset-panel          /* Container principal */
.asset-panel-header   /* Header com título e busca */
.category-tabs        /* Abas de categorias */
.asset-list           /* Lista de assets */
.asset-item           /* Item individual */
.asset-thumbnail      /* Thumbnail do asset */
.modal-overlay        /* Modal para criar personagem */
```

## 🔄 Integração com EditorCanvas

Para integrar com o EditorCanvas, use o sistema de drag and drop:

```jsx
// No EditorCanvas
<Droppable droppableId="editor-canvas">
  {(provided, snapshot) => (
    <div
      ref={provided.innerRef}
      {...provided.droppableProps}
      className={`editor-canvas ${snapshot.isDraggingOver ? 'drag-over' : ''}`}
    >
      {/* Conteúdo do editor */}
      {provided.placeholder}
    </div>
  )}
</Droppable>
```

## 📱 Responsividade

O componente é totalmente responsivo:

```css
@media (max-width: 768px) {
  .asset-panel {
    width: 100%;
    max-width: 320px;
  }
  
  .assets-grid {
    grid-template-columns: 1fr;
  }
  
  .category-tabs {
    flex-wrap: wrap;
  }
}
```

## 🚀 Melhorias Futuras

- [ ] **Integração com IA** para geração automática de personagens
- [ ] **Upload em lote** com progress bar
- [ ] **Preview de áudio/vídeo** inline
- [ ] **Edição inline** de textos
- [ ] **Templates de personagens** pré-definidos
- [ ] **Sincronização com backend** para persistência
- [ ] **Compressão automática** de imagens
- [ ] **Validação de tipos** de arquivo

## 📄 Licença

Este componente faz parte do projeto TecnoCursos AI e segue as mesmas diretrizes de licenciamento.

## 🤝 Contribuição

Para contribuir com melhorias no AssetPanel:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Faça commit com mensagem semântica
6. Abra um Pull Request

---

**Desenvolvido com ❤️ para o TecnoCursos AI** 