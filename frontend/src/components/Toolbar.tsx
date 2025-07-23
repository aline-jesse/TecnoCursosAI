// src/components/Toolbar.tsx
import {
  ArrowDownIcon,
  ArrowUpIcon,
  ArrowUturnLeftIcon,
  ArrowUturnRightIcon,
  ArrowsPointingOutIcon,
  ClipboardDocumentIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  DocumentArrowDownIcon,
  DocumentArrowUpIcon,
  DocumentDuplicateIcon,
  MinusIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import { useEditorStore } from '../store/editorStore';
import './Toolbar.css';

/**
 * Toolbar: Componente com ações para manipular o conteúdo do editor.
 *
 * Funcionalidades:
 * - Histórico (undo/redo)
 * - Copiar/colar elementos
 * - Deletar elementos
 * - Controle de camadas (trazer para frente/enviar para trás)
 * - Alinhamento de elementos
 * - Zoom in/out
 * - Exportar/importar
 * - Configurações
 */
const Toolbar: React.FC = () => {
  const {
    selectedElement,
    currentScene,
    deleteElement,
    bringToFront,
    sendToBack,
    copyElement,
    pasteElement,
    clipboard,
    undo,
    redo,
    history,
    scenes,
    addScene,
  } = useEditorStore();

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const duplicateScene = () => {
    // TODO: Implementar duplicação de cena
  };

  // Verificar se há ações disponíveis
  const canUndo = history.past.length > 0;
  const canRedo = history.future.length > 0;
  const canCopy = selectedElement && currentScene;
  const canPaste = clipboard && currentScene;
  const canDelete = selectedElement && currentScene;
  const canLayer = selectedElement && currentScene;
  const hasScenes = scenes.length > 0;

  // Handlers
  const handleCopy = () => {
    if (canCopy && selectedElement?.id) {
      copyElement(selectedElement.id);
    }
  };

  const handlePaste = () => {
    if (canPaste) {
      pasteElement();
    }
  };

  const handleDelete = () => {
    if (canDelete && selectedElement?.id) {
      deleteElement(selectedElement.id);
    }
  };

  const handleBringToFront = () => {
    if (canLayer && selectedElement?.id) {
      bringToFront(selectedElement.id);
    }
  };

  const handleSendToBack = () => {
    if (canLayer && selectedElement?.id) {
      sendToBack(selectedElement.id);
    }
  };

  const handleDuplicateScene = () => {
    if (currentScene) {
      const newScene = {
        ...currentScene,
        id: `scene-${Date.now()}`,
        name: `${currentScene.name} (Cópia)`,
      };
      addScene(newScene);
    }
  };

  const handleExport = () => {
    // TODO: Implementar exportação
    // eslint-disable-next-line no-console
    console.log('Exportar projeto');
  };

  const handleImport = () => {
    // TODO: Implementar importação
    // eslint-disable-next-line no-console
    console.log('Importar projeto');
  };

  const handleSettings = () => {
    // TODO: Implementar configurações
    // eslint-disable-next-line no-console
    console.log('Abrir configurações');
  };

  return (
    <div className="toolbar">
      {/* Grupo: Histórico */}
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={undo}
          disabled={!canUndo}
          title="Desfazer"
        >
          <ArrowUturnLeftIcon className="w-4 h-4" />
        </button>
        <button
          className="toolbar-btn"
          onClick={redo}
          disabled={!canRedo}
          title="Refazer"
        >
          <ArrowUturnRightIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Separador */}
      <div className="toolbar-separator" />

      {/* Grupo: Edição */}
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={handleCopy}
          disabled={!canCopy}
          title="Copiar elemento"
        >
          <ClipboardDocumentIcon className="w-4 h-4" />
        </button>
        <button
          className="toolbar-btn"
          onClick={handlePaste}
          disabled={!canPaste}
          title="Colar elemento"
        >
          <ClipboardDocumentListIcon className="w-4 h-4" />
        </button>
        <button
          className="toolbar-btn danger"
          onClick={handleDelete}
          disabled={!canDelete}
          title="Deletar elemento"
        >
          <TrashIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Separador */}
      <div className="toolbar-separator" />

      {/* Grupo: Camadas */}
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={handleBringToFront}
          disabled={!canLayer}
          title="Trazer para frente"
        >
          <ArrowUpIcon className="w-4 h-4" />
        </button>
        <button
          className="toolbar-btn"
          onClick={handleSendToBack}
          disabled={!canLayer}
          title="Enviar para trás"
        >
          <ArrowDownIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Separador */}
      <div className="toolbar-separator" />

      {/* Grupo: Cenas */}
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={handleDuplicateScene}
          disabled={!currentScene}
          title="Duplicar cena"
        >
          <DocumentDuplicateIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Separador */}
      <div className="toolbar-separator" />

      {/* Grupo: Zoom */}
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={() => {
            // eslint-disable-next-line no-console
            console.log('Zoom out');
          }}
          title="Diminuir zoom"
        >
          <MinusIcon className="w-4 h-4" />
        </button>
        <span className="zoom-display">100%</span>
        <button
          className="toolbar-btn"
          onClick={() => {
            // eslint-disable-next-line no-console
            console.log('Zoom in');
          }}
          title="Aumentar zoom"
        >
          <PlusIcon className="w-4 h-4" />
        </button>
        <button
          className="toolbar-btn"
          onClick={() => {
            // eslint-disable-next-line no-console
            console.log('Reset zoom');
          }}
          title="Resetar zoom"
        >
          <ArrowsPointingOutIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Separador */}
      <div className="toolbar-separator" />

      {/* Grupo: Arquivo */}
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={handleExport}
          disabled={!hasScenes}
          title="Exportar projeto"
        >
          <DocumentArrowDownIcon className="w-4 h-4" />
        </button>
        <button
          className="toolbar-btn"
          onClick={handleImport}
          title="Importar projeto"
        >
          <DocumentArrowUpIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Separador */}
      <div className="toolbar-separator" />

      {/* Grupo: Configurações */}
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={handleSettings}
          title="Configurações"
        >
          <Cog6ToothIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Status */}
      <div className="toolbar-status">
        <span className="status-text">
          {currentScene ? 'Cena ativa' : 'Nenhuma cena selecionada'}
        </span>
        {selectedElement && (
          <span className="selection-indicator">Elemento selecionado</span>
        )}
      </div>
    </div>
  );
};

export default Toolbar;
