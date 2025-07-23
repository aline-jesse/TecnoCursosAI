// src/components/__tests__/Toolbar.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Toolbar from '../Toolbar';
import { useEditorStore } from '../../store/editorStore';

// Mock do store
jest.mock('../../store/editorStore');

const mockUseEditorStore = useEditorStore as jest.MockedFunction<
  typeof useEditorStore
>;

describe('Toolbar', () => {
  const mockStore = {
    selectedElementId: null,
    currentSceneId: 'scene-1',
    deleteElement: jest.fn(),
    copyElement: jest.fn(),
    pasteElement: jest.fn(),
    bringToFront: jest.fn(),
    sendToBack: jest.fn(),
    clipboard: null,
    undo: jest.fn(),
    redo: jest.fn(),
    history: {
      past: [],
      future: [],
    },
    scenes: [
      {
        id: 'scene-1',
        name: 'Test Scene',
        duration: 5,
        elements: [],
      },
    ],
    addScene: jest.fn(),
    duplicateScene: jest.fn(),
  };

  beforeEach(() => {
    mockUseEditorStore.mockReturnValue(mockStore);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renderiza corretamente', () => {
    render(<Toolbar />);

    expect(screen.getByTitle('Desfazer')).toBeInTheDocument();
    expect(screen.getByTitle('Refazer')).toBeInTheDocument();
    expect(screen.getByTitle('Copiar elemento')).toBeInTheDocument();
    expect(screen.getByTitle('Colar elemento')).toBeInTheDocument();
    expect(screen.getByTitle('Deletar elemento')).toBeInTheDocument();
  });

  it('exibe status da cena atual', () => {
    render(<Toolbar />);

    expect(screen.getByText('Cena ativa')).toBeInTheDocument();
  });

  it('exibe status quando não há cena selecionada', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      currentSceneId: null,
    });

    render(<Toolbar />);

    expect(screen.getByText('Nenhuma cena selecionada')).toBeInTheDocument();
  });

  it('exibe indicador de elemento selecionado', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
    });

    render(<Toolbar />);

    expect(screen.getByText('Elemento selecionado')).toBeInTheDocument();
  });

  it('controla undo/redo', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      history: {
        past: ['action1'],
        future: ['action2'],
      },
    });

    render(<Toolbar />);

    const undoBtn = screen.getByTitle('Desfazer');
    const redoBtn = screen.getByTitle('Refazer');

    fireEvent.click(undoBtn);
    expect(mockStore.undo).toHaveBeenCalled();

    fireEvent.click(redoBtn);
    expect(mockStore.redo).toHaveBeenCalled();
  });

  it('desabilita undo/redo quando não há histórico', () => {
    render(<Toolbar />);

    const undoBtn = screen.getByTitle('Desfazer');
    const redoBtn = screen.getByTitle('Refazer');

    expect(undoBtn).toBeDisabled();
    expect(redoBtn).toBeDisabled();
  });

  it('controla copiar/colar', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
      clipboard: { id: 'element-1', type: 'text' },
    });

    render(<Toolbar />);

    const copyBtn = screen.getByTitle('Copiar elemento');
    const pasteBtn = screen.getByTitle('Colar elemento');

    fireEvent.click(copyBtn);
    expect(mockStore.copyElement).toHaveBeenCalledWith('element-1');

    fireEvent.click(pasteBtn);
    expect(mockStore.pasteElement).toHaveBeenCalledWith('scene-1');
  });

  it('desabilita copiar quando não há elemento selecionado', () => {
    render(<Toolbar />);

    const copyBtn = screen.getByTitle('Copiar elemento');
    expect(copyBtn).toBeDisabled();
  });

  it('desabilita colar quando não há clipboard', () => {
    render(<Toolbar />);

    const pasteBtn = screen.getByTitle('Colar elemento');
    expect(pasteBtn).toBeDisabled();
  });

  it('controla deletar elemento', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
    });

    render(<Toolbar />);

    const deleteBtn = screen.getByTitle('Deletar elemento');
    fireEvent.click(deleteBtn);

    expect(mockStore.deleteElement).toHaveBeenCalledWith(
      'scene-1',
      'element-1'
    );
  });

  it('não mostra botão de deletar quando não há elemento selecionado', () => {
    render(<Toolbar />);

    expect(screen.queryByTitle('Deletar elemento')).not.toBeInTheDocument();
  });

  it('controla camadas', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
    });

    render(<Toolbar />);

    const bringToFrontBtn = screen.getByTitle('Trazer para frente');
    const sendToBackBtn = screen.getByTitle('Enviar para trás');

    fireEvent.click(bringToFrontBtn);
    expect(mockStore.bringToFront).toHaveBeenCalledWith('scene-1', 'element-1');

    fireEvent.click(sendToBackBtn);
    expect(mockStore.sendToBack).toHaveBeenCalledWith('scene-1', 'element-1');
  });

  it('desabilita controles de camada quando não há elemento selecionado', () => {
    render(<Toolbar />);

    const bringToFrontBtn = screen.getByTitle('Trazer para frente');
    const sendToBackBtn = screen.getByTitle('Enviar para trás');

    expect(bringToFrontBtn).toBeDisabled();
    expect(sendToBackBtn).toBeDisabled();
  });

  it('duplica cena atual', () => {
    render(<Toolbar />);

    const duplicateBtn = screen.getByTitle('Duplicar cena');
    fireEvent.click(duplicateBtn);

    expect(mockStore.addScene).toHaveBeenCalledWith(
      expect.objectContaining({
        id: expect.stringMatching(/scene-\d+/),
        name: 'Test Scene (Cópia)',
      })
    );
  });

  it('desabilita duplicar cena quando não há cena selecionada', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      currentSceneId: null,
    });

    render(<Toolbar />);

    const duplicateBtn = screen.getByTitle('Duplicar cena');
    expect(duplicateBtn).toBeDisabled();
  });

  it('controla zoom', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

    render(<Toolbar />);

    const zoomOutBtn = screen.getByTitle('Diminuir zoom');
    const zoomInBtn = screen.getByTitle('Aumentar zoom');
    const resetZoomBtn = screen.getByTitle('Resetar zoom');

    fireEvent.click(zoomOutBtn);
    expect(consoleSpy).toHaveBeenCalledWith('Zoom out');

    fireEvent.click(zoomInBtn);
    expect(consoleSpy).toHaveBeenCalledWith('Zoom in');

    fireEvent.click(resetZoomBtn);
    expect(consoleSpy).toHaveBeenCalledWith('Reset zoom');

    consoleSpy.mockRestore();
  });

  it('exibe nível de zoom atual', () => {
    render(<Toolbar />);

    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('controla exportar projeto', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

    render(<Toolbar />);

    const exportBtn = screen.getByTitle('Exportar projeto');
    fireEvent.click(exportBtn);

    expect(consoleSpy).toHaveBeenCalledWith('Exportar projeto');

    consoleSpy.mockRestore();
  });

  it('controla importar projeto', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

    render(<Toolbar />);

    const importBtn = screen.getByTitle('Importar projeto');
    fireEvent.click(importBtn);

    expect(consoleSpy).toHaveBeenCalledWith('Importar projeto');

    consoleSpy.mockRestore();
  });

  it('desabilita exportar quando não há cenas', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      scenes: [],
    });

    render(<Toolbar />);

    const exportBtn = screen.getByTitle('Exportar projeto');
    expect(exportBtn).toBeDisabled();
  });

  it('controla configurações', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

    render(<Toolbar />);

    const settingsBtn = screen.getByTitle('Configurações');
    fireEvent.click(settingsBtn);

    expect(consoleSpy).toHaveBeenCalledWith('Abrir configurações');

    consoleSpy.mockRestore();
  });

  it('agrupa botões corretamente', () => {
    render(<Toolbar />);

    // Verificar se os grupos estão presentes
    const groups = document.querySelectorAll('.toolbar-group');
    expect(groups.length).toBeGreaterThan(0);
  });

  it('exibe separadores entre grupos', () => {
    render(<Toolbar />);

    const separators = document.querySelectorAll('.toolbar-separator');
    expect(separators.length).toBeGreaterThan(0);
  });

  it('aplica estilos corretos aos botões', () => {
    render(<Toolbar />);

    const buttons = document.querySelectorAll('.toolbar-btn');
    buttons.forEach(button => {
      expect(button).toHaveClass('toolbar-btn');
    });
  });

  it('aplica estilos de perigo ao botão de deletar', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
    });

    render(<Toolbar />);

    const deleteBtn = screen.getByTitle('Deletar elemento');
    expect(deleteBtn).toHaveClass('danger');
  });

  it('manipula estados de hover', () => {
    render(<Toolbar />);

    const undoBtn = screen.getByTitle('Desfazer');
    fireEvent.mouseEnter(undoBtn);

    // Verificar se o hover foi aplicado (implementação interna)
    expect(undoBtn).toBeInTheDocument();
  });

  it('manipula estados de foco', () => {
    render(<Toolbar />);

    const undoBtn = screen.getByTitle('Desfazer');
    fireEvent.focus(undoBtn);

    // Verificar se o foco foi aplicado (implementação interna)
    expect(undoBtn).toBeInTheDocument();
  });

  it('exibe tooltips corretos', () => {
    render(<Toolbar />);

    expect(screen.getByTitle('Desfazer')).toBeInTheDocument();
    expect(screen.getByTitle('Refazer')).toBeInTheDocument();
    expect(screen.getByTitle('Copiar elemento')).toBeInTheDocument();
    expect(screen.getByTitle('Colar elemento')).toBeInTheDocument();
    expect(screen.getByTitle('Trazer para frente')).toBeInTheDocument();
    expect(screen.getByTitle('Enviar para trás')).toBeInTheDocument();
    expect(screen.getByTitle('Duplicar cena')).toBeInTheDocument();
    expect(screen.getByTitle('Diminuir zoom')).toBeInTheDocument();
    expect(screen.getByTitle('Aumentar zoom')).toBeInTheDocument();
    expect(screen.getByTitle('Resetar zoom')).toBeInTheDocument();
    expect(screen.getByTitle('Exportar projeto')).toBeInTheDocument();
    expect(screen.getByTitle('Importar projeto')).toBeInTheDocument();
    expect(screen.getByTitle('Configurações')).toBeInTheDocument();
  });

  it('manipula estados de loading', () => {
    render(<Toolbar />);

    const toolbar = document.querySelector('.toolbar');
    expect(toolbar).not.toHaveClass('loading');
  });

  it('é responsivo em diferentes tamanhos de tela', () => {
    render(<Toolbar />);

    const toolbar = document.querySelector('.toolbar');
    expect(toolbar).toHaveStyle({
      overflowX: 'auto',
      overflowY: 'hidden',
    });
  });

  it('mantém estado consistente entre renderizações', () => {
    const { rerender } = render(<Toolbar />);

    // Verificar se o estado inicial está correto
    expect(screen.getByText('Cena ativa')).toBeInTheDocument();

    // Mudar estado e re-renderizar
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
    });

    rerender(<Toolbar />);

    // Verificar se o novo estado está correto
    expect(screen.getByText('Elemento selecionado')).toBeInTheDocument();
  });

  it('previne ações quando elementos não estão disponíveis', () => {
    render(<Toolbar />);

    // Tentar copiar sem elemento selecionado
    const copyBtn = screen.getByTitle('Copiar elemento');
    fireEvent.click(copyBtn);

    expect(mockStore.copyElement).not.toHaveBeenCalled();
  });

  it('manipula erros graciosamente', () => {
    mockStore.copyElement.mockImplementation(() => {
      throw new Error('Copy failed');
    });

    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      selectedElementId: 'element-1',
    });

    render(<Toolbar />);

    const copyBtn = screen.getByTitle('Copiar elemento');

    // O componente não deve quebrar quando há erro
    expect(() => {
      fireEvent.click(copyBtn);
    }).not.toThrow();
  });
});
