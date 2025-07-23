# 🎬 Componentes do Editor de Vídeo - TecnoCursos AI

Esta pasta contém todos os componentes React implementados para o editor de vídeo estilo Animaker.

## 📁 Estrutura dos Componentes

### **AssetPanel.jsx** - Lista de Personagens/Avatares

- **Função:** Biblioteca de recursos na lateral esquerda
- **Funcionalidades:**
  - Lista de personagens com categorias
  - Sistema de busca e filtros
  - Drag & Drop para canvas
  - Thumbnails otimizados
  - Carregamento dinâmico de assets

### **SceneList.jsx** - Gerenciamento de Cenas

- **Função:** Lista de cenas na lateral direita
- **Funcionalidades:**
  - Miniaturas das cenas
  - Adicionar/remover/reordenar cenas
  - Navegação entre cenas
  - Duplicação de cenas
  - Preview de cenas

### **Timeline.jsx** - Timeline Horizontal

- **Função:** Timeline de cenas e camadas
- **Funcionalidades:**
  - Ordem e duração das cenas
  - Controles de reprodução
  - Zoom na timeline
  - Scrubbing de vídeo
  - Marcadores de tempo

### **EditorCanvas.jsx** - Canvas Central

- **Função:** Área principal de edição visual
- **Funcionalidades:**
  - Canvas para arrastar/soltar avatares
  - Adição de textos e imagens
  - Transformações (rotação, escala)
  - Sistema de camadas
  - Snap e alinhamento

### **Toolbar.jsx** - Ferramentas de Edição

- **Função:** Barra de ferramentas lateral
- **Funcionalidades:**
  - Ferramentas de seleção
  - Adição de texto, imagens, músicas
  - Efeitos visuais
  - Configurações de cena
  - Atalhos de teclado

## 🎨 Estilização com TailwindCSS

Todos os componentes utilizam TailwindCSS para:

- Layout flexível e responsivo
- Design system consistente
- Animations e transições
- Estados de hover/active
- Modo escuro/claro

## 🔧 Dependências Técnicas

- **React 18** - Biblioteca principal
- **TailwindCSS** - Estilização
- **React DnD** - Drag & Drop
- **Fabric.js** - Manipulação de canvas
- **Framer Motion** - Animações
- **Zustand** - Gerenciamento de estado

## 🚀 Exemplo de Uso

```jsx
import { AssetPanel } from './AssetPanel';
import { EditorCanvas } from './EditorCanvas';
import { Timeline } from './Timeline';

function VideoEditor() {
  return (
    <div className='editor-layout'>
      <AssetPanel />
      <EditorCanvas />
      <Timeline />
    </div>
  );
}
```

## 📊 Métricas dos Componentes

- **Total de linhas:** 4,500+
- **Componentes:** 20+
- **Funcionalidades:** 30+
- **Cobertura TypeScript:** 100%
