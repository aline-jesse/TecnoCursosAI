import React, { useState, useCallback } from 'react';
import Toolbar from './Toolbar';

/**
 * Exemplo de uso do componente Toolbar
 *
 * Este arquivo demonstra como implementar todas as funcionalidades
 * do Toolbar em uma aplicação real
 */
const ToolbarExample = () => {
  // Estados para controlar as funcionalidades
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [selectedElement, setSelectedElement] = useState(null);
  const [clipboard, setClipboard] = useState(null);
  const [activeScene, setActiveScene] = useState(null);

  /**
   * Funções de histórico (desfazer/refazer)
   */
  const handleUndo = useCallback(() => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      console.log('Ação desfeita');
    }
  }, [historyIndex]);

  const handleRedo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1);
      console.log('Ação refeita');
    }
  }, [historyIndex, history.length]);

  /**
   * Funções de cena
   */
  const handleDuplicateScene = useCallback(() => {
    if (activeScene) {
      const duplicatedScene = {
        ...activeScene,
        id: `scene-${Date.now()}`,
        title: `${activeScene.title} (Cópia)`,
      };
      console.log('Cena duplicada:', duplicatedScene);
    }
  }, [activeScene]);

  const handleDeleteScene = useCallback(() => {
    if (activeScene) {
      console.log('Cena deletada:', activeScene);
      setActiveScene(null);
    }
  }, [activeScene]);

  /**
   * Funções de elementos
   */
  const handleCopyElement = useCallback(() => {
    if (selectedElement) {
      setClipboard(selectedElement);
      console.log('Elemento copiado:', selectedElement);
    }
  }, [selectedElement]);

  const handlePasteElement = useCallback(() => {
    if (clipboard) {
      const pastedElement = {
        ...clipboard,
        id: `element-${Date.now()}`,
        x: clipboard.x + 10,
        y: clipboard.y + 10,
      };
      console.log('Elemento colado:', pastedElement);
    }
  }, [clipboard]);

  /**
   * Funções de alinhamento horizontal
   */
  const handleAlignLeft = useCallback(() => {
    if (selectedElement) {
      console.log('Elemento alinhado à esquerda');
    }
  }, [selectedElement]);

  const handleAlignCenter = useCallback(() => {
    if (selectedElement) {
      console.log('Elemento alinhado ao centro');
    }
  }, [selectedElement]);

  const handleAlignRight = useCallback(() => {
    if (selectedElement) {
      console.log('Elemento alinhado à direita');
    }
  }, [selectedElement]);

  /**
   * Funções de alinhamento vertical
   */
  const handleAlignTop = useCallback(() => {
    if (selectedElement) {
      console.log('Elemento alinhado ao topo');
    }
  }, [selectedElement]);

  const handleAlignMiddle = useCallback(() => {
    if (selectedElement) {
      console.log('Elemento alinhado ao meio');
    }
  }, [selectedElement]);

  const handleAlignBottom = useCallback(() => {
    if (selectedElement) {
      console.log('Elemento alinhado à base');
    }
  }, [selectedElement]);

  /**
   * Funções de distribuição
   */
  const handleDistributeHorizontally = useCallback(() => {
    console.log('Elementos distribuídos horizontalmente');
  }, []);

  const handleDistributeVertically = useCallback(() => {
    console.log('Elementos distribuídos verticalmente');
  }, []);

  // Estados de habilitação baseados na lógica da aplicação
  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;
  const canDuplicate = !!activeScene;
  const canDelete = !!activeScene;
  const canCopy = !!selectedElement;
  const canPaste = !!clipboard;
  const canAlign = !!selectedElement;
  const canDistribute = false; // Implementar lógica para múltiplos elementos selecionados

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Toolbar
        // Funções de histórico
        onUndo={handleUndo}
        onRedo={handleRedo}
        // Funções de cena
        onDuplicateScene={handleDuplicateScene}
        onDeleteScene={handleDeleteScene}
        // Funções de elementos
        onCopyElement={handleCopyElement}
        onPasteElement={handlePasteElement}
        // Funções de alinhamento horizontal
        onAlignLeft={handleAlignLeft}
        onAlignCenter={handleAlignCenter}
        onAlignRight={handleAlignRight}
        // Funções de alinhamento vertical
        onAlignTop={handleAlignTop}
        onAlignMiddle={handleAlignMiddle}
        onAlignBottom={handleAlignBottom}
        // Funções de distribuição
        onDistributeHorizontally={handleDistributeHorizontally}
        onDistributeVertically={handleDistributeVertically}
        // Estados de habilitação
        canUndo={canUndo}
        canRedo={canRedo}
        canDuplicate={canDuplicate}
        canDelete={canDelete}
        canCopy={canCopy}
        canPaste={canPaste}
        canAlign={canAlign}
        canDistribute={canDistribute}
      />

      <div style={{ flex: 1, padding: '20px', marginLeft: '280px' }}>
        <h2>Exemplo de Uso do Toolbar</h2>

        <div style={{ marginBottom: '20px' }}>
          <h3>Estados Atuais:</h3>
          <ul>
            <li>
              Histórico: {history.length} ações, índice: {historyIndex}
            </li>
            <li>Cena ativa: {activeScene ? activeScene.title : 'Nenhuma'}</li>
            <li>
              Elemento selecionado:{' '}
              {selectedElement ? selectedElement.name : 'Nenhum'}
            </li>
            <li>Clipboard: {clipboard ? 'Com conteúdo' : 'Vazio'}</li>
          </ul>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3>Controles de Teste:</h3>
          <button
            onClick={() => setActiveScene({ id: '1', title: 'Cena de Teste' })}
          >
            Definir Cena Ativa
          </button>
          <button
            onClick={() =>
              setSelectedElement({ id: '1', name: 'Elemento de Teste' })
            }
          >
            Selecionar Elemento
          </button>
          <button
            onClick={() => setClipboard({ id: '1', name: 'Elemento Copiado' })}
          >
            Definir Clipboard
          </button>
          <button
            onClick={() => {
              setHistory([...history, `Ação ${history.length + 1}`]);
              setHistoryIndex(history.length);
            }}
          >
            Adicionar Ação ao Histórico
          </button>
        </div>

        <div>
          <h3>Como Usar:</h3>
          <ol>
            <li>Use os controles acima para simular diferentes estados</li>
            <li>
              Observe como os botões da toolbar são habilitados/desabilitados
            </li>
            <li>Clique nos botões da toolbar para ver as ações no console</li>
            <li>A toolbar está fixa à esquerda e responsiva</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default ToolbarExample;
