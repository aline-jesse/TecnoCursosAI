# Componente Toolbar

## Visão Geral

O componente `Toolbar` é uma barra de ferramentas vertical fixa à esquerda da tela, projetada para o editor de vídeos TecnoCursos AI. Ele fornece acesso rápido às principais ferramentas de edição, organizadas em seções lógicas.

## Funcionalidades Implementadas

### 🔄 Histórico
- **Desfazer (Ctrl+Z)**: Reverte a última ação realizada
- **Refazer (Ctrl+Y)**: Repete a última ação desfeita

### 🎬 Cenas
- **Duplicar Cena**: Cria uma cópia da cena atual
- **Deletar Cena**: Remove a cena selecionada

### 📋 Elementos
- **Copiar Elemento (Ctrl+C)**: Copia o elemento selecionado para a área de transferência
- **Colar Elemento (Ctrl+V)**: Cola o elemento da área de transferência

### ↔️ Alinhamento Horizontal
- **Alinhar à Esquerda**: Alinha elementos à borda esquerda
- **Alinhar ao Centro**: Centraliza elementos horizontalmente
- **Alinhar à Direita**: Alinha elementos à borda direita

### ↕️ Alinhamento Vertical
- **Alinhar ao Topo**: Alinha elementos à borda superior
- **Alinhar ao Meio**: Centraliza elementos verticalmente
- **Alinhar à Base**: Alinha elementos à borda inferior

### 📐 Distribuição
- **Distribuir Horizontalmente**: Distribui elementos uniformemente no eixo X
- **Distribuir Verticalmente**: Distribui elementos uniformemente no eixo Y

## Props

### Funções de Callback

| Prop | Tipo | Descrição |
|------|------|-----------|
| `onUndo` | `function` | Chamada quando o botão desfazer é clicado |
| `onRedo` | `function` | Chamada quando o botão refazer é clicado |
| `onDuplicateScene` | `function` | Chamada quando o botão duplicar cena é clicado |
| `onDeleteScene` | `function` | Chamada quando o botão deletar cena é clicado |
| `onCopyElement` | `function` | Chamada quando o botão copiar elemento é clicado |
| `onPasteElement` | `function` | Chamada quando o botão colar elemento é clicado |
| `onAlignLeft` | `function` | Chamada quando o botão alinhar à esquerda é clicado |
| `onAlignCenter` | `function` | Chamada quando o botão alinhar ao centro é clicado |
| `onAlignRight` | `function` | Chamada quando o botão alinhar à direita é clicado |
| `onAlignTop` | `function` | Chamada quando o botão alinhar ao topo é clicado |
| `onAlignMiddle` | `function` | Chamada quando o botão alinhar ao meio é clicado |
| `onAlignBottom` | `function` | Chamada quando o botão alinhar à base é clicado |
| `onDistributeHorizontally` | `function` | Chamada quando o botão distribuir horizontalmente é clicado |
| `onDistributeVertically` | `function` | Chamada quando o botão distribuir verticalmente é clicado |

### Estados de Habilitação

| Prop | Tipo | Padrão | Descrição |
|------|------|--------|-----------|
| `canUndo` | `boolean` | `false` | Habilita/desabilita o botão desfazer |
| `canRedo` | `boolean` | `false` | Habilita/desabilita o botão refazer |
| `canDuplicate` | `boolean` | `true` | Habilita/desabilita o botão duplicar cena |
| `canDelete` | `boolean` | `true` | Habilita/desabilita o botão deletar cena |
| `canCopy` | `boolean` | `false` | Habilita/desabilita o botão copiar elemento |
| `canPaste` | `boolean` | `false` | Habilita/desabilita o botão colar elemento |
| `canAlign` | `boolean` | `false` | Habilita/desabilita os botões de alinhamento |
| `canDistribute` | `boolean` | `false` | Habilita/desabilita os botões de distribuição |

## Exemplo de Uso

```jsx
import React, { useState, useCallback } from 'react';
import Toolbar from './components/Toolbar';

const App = () => {
  const [selectedElement, setSelectedElement] = useState(null);
  const [activeScene, setActiveScene] = useState(null);
  const [clipboard, setClipboard] = useState(null);

  const handleUndo = useCallback(() => {
    console.log('Ação desfeita');
  }, []);

  const handleRedo = useCallback(() => {
    console.log('Ação refeita');
  }, []);

  const handleDuplicateScene = useCallback(() => {
    console.log('Cena duplicada');
  }, []);

  const handleDeleteScene = useCallback(() => {
    console.log('Cena deletada');
  }, []);

  const handleCopyElement = useCallback(() => {
    if (selectedElement) {
      setClipboard(selectedElement);
      console.log('Elemento copiado');
    }
  }, [selectedElement]);

  const handlePasteElement = useCallback(() => {
    if (clipboard) {
      console.log('Elemento colado');
    }
  }, [clipboard]);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Toolbar 
        // Funções de callback
        onUndo={handleUndo}
        onRedo={handleRedo}
        onDuplicateScene={handleDuplicateScene}
        onDeleteScene={handleDeleteScene}
        onCopyElement={handleCopyElement}
        onPasteElement={handlePasteElement}
        
        // Estados de habilitação
        canUndo={false}
        canRedo={false}
        canDuplicate={!!activeScene}
        canDelete={!!activeScene}
        canCopy={!!selectedElement}
        canPaste={!!clipboard}
        canAlign={!!selectedElement}
        canDistribute={false}
      />
      
      <div style={{ flex: 1, marginLeft: '280px' }}>
        {/* Conteúdo principal da aplicação */}
      </div>
    </div>
  );
};
```

## Características de Design

### Layout
- **Posição**: Fixa à esquerda da tela
- **Largura**: 280px (240px em tablets, 200px em mobile)
- **Altura**: 100vh (altura total da viewport)
- **Scroll**: Automático quando necessário

### Estilo Visual
- **Tema**: Escuro com gradientes
- **Cores**: Tons de cinza e azul
- **Ícones**: Heroicons (24px outline)
- **Feedback**: Hover effects e estados ativos
- **Tooltips**: Informações detalhadas nos botões

### Responsividade
- **Desktop**: 280px de largura
- **Tablet**: 240px de largura
- **Mobile**: 200px de largura, layout adaptado

## Acessibilidade

### Atributos
- Todos os botões têm `title` com descrição detalhada
- Botões desabilitados têm `disabled` attribute
- Foco visual com outline azul

### Navegação
- Suporte a navegação por teclado
- Atalhos de teclado mencionados nos tooltips
- Estados de foco bem definidos

## Testes

O componente inclui testes unitários abrangentes:

```bash
npm test -- --testPathPattern=Toolbar.test.jsx
```

### Cobertura de Testes
- ✅ Renderização básica
- ✅ Estados de habilitação
- ✅ Execução de ações
- ✅ Feedback visual
- ✅ Acessibilidade
- ✅ Integração

## Dependências

- **React**: ^18.2.0
- **@heroicons/react**: ^2.0.18
- **@testing-library/react**: ^13.3.0
- **@testing-library/jest-dom**: ^5.16.4

## Estrutura de Arquivos

```
src/components/
├── Toolbar.jsx          # Componente principal
├── Toolbar.css          # Estilos
├── ToolbarExample.jsx   # Exemplo de uso
├── __tests__/
│   └── Toolbar.test.jsx # Testes unitários
└── README_Toolbar.md    # Esta documentação
```

## Contribuição

Para contribuir com o componente Toolbar:

1. Siga o padrão de código existente
2. Adicione testes para novas funcionalidades
3. Atualize a documentação
4. Mantenha a responsividade
5. Teste em diferentes dispositivos

## Changelog

### v1.0.0
- ✅ Implementação inicial do componente
- ✅ Todas as funcionalidades básicas
- ✅ Testes unitários completos
- ✅ Documentação detalhada
- ✅ Exemplo de uso
- ✅ Design responsivo
- ✅ Acessibilidade implementada 