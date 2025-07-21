# 🎬 Timeline Avançado - TecnoCursos AI

## 📋 Visão Geral

O componente **Timeline.jsx** foi completamente reescrito para oferecer uma experiência de edição de vídeo profissional, similar aos editores de vídeo comerciais como Adobe Premiere Pro ou DaVinci Resolve.

## ✨ Funcionalidades Implementadas

### 🎯 **Blocos Visuais para Cenas**
- ✅ **Indicação visual da ordem** - Número sequencial (#1, #2, #3...)
- ✅ **Nome da cena** - Título personalizado ou "Cena X"
- ✅ **Duração editável** - Controle numérico em segundos
- ✅ **Posicionamento proporcional** - Baseado na duração total
- ✅ **Destaque visual** - Cena selecionada com borda azul

### 🔄 **Drag & Drop para Reordenação**
- ✅ **Arrastar cenas** - Reordenar por drag & drop
- ✅ **Feedback visual** - Destaque durante arrasto
- ✅ **Validação** - Prevenção de drops inválidos
- ✅ **Persistência** - Salva automaticamente no backend
- ✅ **Rollback** - Reverte em caso de erro

### 🎨 **Gerenciamento de Camadas (Layers)**
- ✅ **Expandir/colapsar** - Botão para mostrar camadas
- ✅ **Visibilidade** - Mostrar/ocultar camadas (👁️/👁️‍🗨️)
- ✅ **Travamento** - Travar/destravar camadas (🔒/🔓)
- ✅ **Ordem das camadas** - Mover para frente/trás (⬆️/⬇️)
- ✅ **Estados visuais** - Diferenciação por estado

### 🎛️ **Controles Avançados**
- ✅ **Zoom na timeline** - 50% a 300% de zoom
- ✅ **Scroll horizontal** - Navegação em projetos longos
- ✅ **Régua de tempo** - Marcadores a cada 5 segundos
- ✅ **Duração total** - Cálculo automático
- ✅ **Contador de cenas** - Número total de cenas

## 🚀 Como Usar

### **1. Props do Componente**

```jsx
<Timeline
  projectId="projeto-123"
  scenes={arrayDeCenas}
  onSceneUpdate={(scenes) => console.log('Cenas atualizadas:', scenes)}
  onSceneSelect={(scene) => console.log('Cena selecionada:', scene)}
  selectedSceneId="cena-456"
  onLayerUpdate={(elementId, type, value) => console.log('Camada atualizada:', elementId, type, value)}
/>
```

### **2. Estrutura de Dados**

```javascript
// Exemplo de cena
const scene = {
  id: "cena-123",
  title: "Introdução",
  duration: 10, // segundos
  elements: [
    {
      id: "elemento-1",
      name: "Texto Principal",
      type: "text",
      order: 0,
      // ... outras propriedades
    },
    {
      id: "elemento-2", 
      name: "Imagem de Fundo",
      type: "image",
      order: 1,
      // ... outras propriedades
    }
  ]
};
```

### **3. Interações Principais**

#### **Selecionar Cena**
```jsx
// Clique em qualquer bloco de cena
// A cena será destacada e o callback onSceneSelect será chamado
```

#### **Editar Duração**
```jsx
// Clique no campo numérico de duração
// Digite o novo valor em segundos
// A mudança é salva automaticamente
```

#### **Reordenar Cenas**
```jsx
// Arraste um bloco de cena para nova posição
// Solte para confirmar a reordenação
// A ordem é salva automaticamente
```

#### **Gerenciar Camadas**
```jsx
// Clique no ícone 📁 para expandir camadas
// Use os controles de cada camada:
// - 👁️/👁️‍🗨️: Mostrar/ocultar
// - 🔒/🔓: Travar/destravar  
// - ⬆️/⬇️: Mover para frente/trás
```

## 🎨 Interface Visual

### **Blocos de Cena**
```
┌─────────────────────────────────────┐
│ #1 Introdução          10s    📁   │
│ ┌─────────────────────────────────┐ │
│ │ 👁️ Texto Principal    ⬇️ ⬆️ 🔓 │ │
│ │ 👁️‍🗨️ Imagem Fundo    ⬇️ ⬆️ 🔒 │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### **Estados Visuais**
- **Selecionada**: Borda azul, sombra
- **Arrastando**: Opacidade reduzida, escala menor
- **Drop target**: Borda verde, fundo verde claro
- **Camada oculta**: Opacidade reduzida
- **Camada travada**: Borda vermelha à esquerda

## 🔧 Funcionalidades Técnicas

### **Cálculo de Posicionamento**
```javascript
// Posição baseada na duração acumulada
const previousDuration = scenes.slice(0, index).reduce((total, s) => total + s.duration, 0);
const position = (previousDuration * 100) / totalDuration;
const width = (scene.duration * 100) / totalDuration;
```

### **Gerenciamento de Estado**
```javascript
// Estados principais
const [timelineScenes, setTimelineScenes] = useState(scenes);
const [isDragging, setIsDragging] = useState(false);
const [draggedScene, setDraggedScene] = useState(null);
const [expandedSceneId, setExpandedSceneId] = useState(null);
const [layerStates, setLayerStates] = useState({});
const [zoom, setZoom] = useState(1);
```

### **Callbacks de Eventos**
```javascript
// Atualização de cena
onSceneUpdate: (scenes) => void

// Seleção de cena  
onSceneSelect: (scene) => void

// Atualização de camada
onLayerUpdate: (elementId, type, value) => void
// type: 'visibility' | 'lock' | 'order'
// value: boolean | number
```

## 🎯 Casos de Uso

### **1. Edição de Vídeo Educacional**
```jsx
// Timeline para curso de programação
<Timeline
  scenes={[
    { id: "intro", title: "Introdução", duration: 15 },
    { id: "conceitos", title: "Conceitos Básicos", duration: 30 },
    { id: "exemplos", title: "Exemplos Práticos", duration: 45 }
  ]}
  onSceneSelect={(scene) => setActiveScene(scene)}
/>
```

### **2. Gerenciamento de Camadas**
```jsx
// Controle de elementos por cena
onLayerUpdate={(elementId, type, value) => {
  if (type === 'visibility') {
    // Mostrar/ocultar elemento no canvas
    updateElementVisibility(elementId, value);
  } else if (type === 'lock') {
    // Travar/destravar edição do elemento
    updateElementLock(elementId, value);
  }
}}
```

### **3. Reordenação Automática**
```jsx
// Reordenar cenas e atualizar backend
onSceneUpdate={(scenes) => {
  // Salvar nova ordem no banco de dados
  saveProjectScenes(projectId, scenes);
  
  // Atualizar preview do vídeo
  updateVideoPreview(scenes);
}}
```

## 🔍 Recursos Avançados

### **Zoom e Navegação**
- **Zoom**: 50% a 300% com controles +/- 
- **Scroll**: Navegação horizontal automática
- **Régua**: Marcadores de tempo a cada 5s
- **Indicador**: Barra de progresso do scroll

### **Performance**
- **Renderização otimizada**: Apenas cenas visíveis
- **Debounce**: Atualizações em lote
- **Memoização**: Evita re-renders desnecessários
- **Lazy loading**: Carrega camadas sob demanda

### **Acessibilidade**
- **Teclado**: Navegação por Tab
- **Screen readers**: Labels descritivos
- **Contraste**: Cores com contraste adequado
- **Foco**: Indicadores visuais de foco

## 🛠️ Personalização

### **Estilos Customizados**
```css
/* Personalizar aparência dos blocos */
.timeline-scene {
  @apply bg-white border-2 rounded-lg p-3;
}

.timeline-scene.selected {
  @apply ring-2 ring-blue-500 shadow-lg;
}

.timeline-layer {
  @apply flex items-center justify-between p-2 rounded text-xs;
}
```

### **Temas**
```javascript
// Suporte a temas claro/escuro
const theme = {
  light: {
    background: 'bg-white',
    border: 'border-gray-200',
    text: 'text-gray-900'
  },
  dark: {
    background: 'bg-gray-800', 
    border: 'border-gray-600',
    text: 'text-gray-100'
  }
};
```

## 🎉 Benefícios

### **Para o Usuário**
- ✅ **Interface intuitiva** - Similar a editores profissionais
- ✅ **Feedback visual** - Estados claros e responsivos
- ✅ **Produtividade** - Drag & drop rápido
- ✅ **Controle granular** - Gerenciamento de camadas
- ✅ **Flexibilidade** - Zoom e navegação

### **Para o Desenvolvedor**
- ✅ **Código limpo** - Bem documentado e estruturado
- ✅ **Reutilizável** - Props flexíveis
- ✅ **Testável** - Funções puras e isoladas
- ✅ **Manutenível** - Separação de responsabilidades
- ✅ **Extensível** - Fácil adição de funcionalidades

---

## 🏆 Conclusão

O componente **Timeline.jsx** agora oferece uma experiência de edição de vídeo **enterprise-grade** com:

- **Interface profissional** similar a editores comerciais
- **Funcionalidades completas** de timeline e camadas
- **Performance otimizada** para projetos complexos
- **Acessibilidade** e usabilidade excepcionais
- **Código limpo** e bem documentado

**O TecnoCursos AI agora possui um editor de vídeo de nível profissional! 🚀** 