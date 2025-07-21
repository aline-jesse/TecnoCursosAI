import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Toolbar from '../Toolbar';

/**
 * Mock das funções de callback para testar as ações
 */
const mockCallbacks = {
  onUndo: jest.fn(),
  onRedo: jest.fn(),
  onDuplicateScene: jest.fn(),
  onDeleteScene: jest.fn(),
  onCopyElement: jest.fn(),
  onPasteElement: jest.fn(),
  onAlignLeft: jest.fn(),
  onAlignCenter: jest.fn(),
  onAlignRight: jest.fn(),
  onAlignTop: jest.fn(),
  onAlignMiddle: jest.fn(),
  onAlignBottom: jest.fn(),
  onDistributeHorizontally: jest.fn(),
  onDistributeVertically: jest.fn()
};

/**
 * Configuração padrão das props para os testes
 */
const defaultProps = {
  ...mockCallbacks,
  canUndo: false,
  canRedo: false,
  canDuplicate: true,
  canDelete: true,
  canCopy: false,
  canPaste: false,
  canAlign: false,
  canDistribute: false
};

/**
 * Função helper para limpar os mocks entre os testes
 */
const clearMocks = () => {
  Object.values(mockCallbacks).forEach(mock => mock.mockClear());
};

describe('Toolbar Component', () => {
  beforeEach(() => {
    clearMocks();
  });

  /**
   * Teste de renderização básica
   */
  describe('Renderização', () => {
    test('renderiza o componente Toolbar corretamente', () => {
      render(<Toolbar {...defaultProps} />);
      
      // Verifica se o título da toolbar está presente
      expect(screen.getByText('Ferramentas')).toBeInTheDocument();
      
      // Verifica se as seções estão presentes
      expect(screen.getByText('Histórico')).toBeInTheDocument();
      expect(screen.getByText('Cenas')).toBeInTheDocument();
      expect(screen.getByText('Elementos')).toBeInTheDocument();
      expect(screen.getByText('Alinhar Horizontal')).toBeInTheDocument();
      expect(screen.getByText('Alinhar Vertical')).toBeInTheDocument();
      expect(screen.getByText('Distribuir')).toBeInTheDocument();
    });

    test('renderiza todos os botões da toolbar', () => {
      render(<Toolbar {...defaultProps} />);
      
      // Botões de histórico
      expect(screen.getByTitle('Desfazer (Ctrl+Z)')).toBeInTheDocument();
      expect(screen.getByTitle('Refazer (Ctrl+Y)')).toBeInTheDocument();
      
      // Botões de cena
      expect(screen.getByTitle('Duplicar Cena')).toBeInTheDocument();
      expect(screen.getByTitle('Deletar Cena')).toBeInTheDocument();
      
      // Botões de elementos
      expect(screen.getByTitle('Copiar Elemento (Ctrl+C)')).toBeInTheDocument();
      expect(screen.getByTitle('Colar Elemento (Ctrl+V)')).toBeInTheDocument();
      
      // Botões de alinhamento horizontal
      expect(screen.getByTitle('Alinhar à Esquerda')).toBeInTheDocument();
      expect(screen.getByTitle('Alinhar ao Centro')).toBeInTheDocument();
      expect(screen.getByTitle('Alinhar à Direita')).toBeInTheDocument();
      
      // Botões de alinhamento vertical
      expect(screen.getByTitle('Alinhar ao Topo')).toBeInTheDocument();
      expect(screen.getByTitle('Alinhar ao Meio')).toBeInTheDocument();
      expect(screen.getByTitle('Alinhar à Base')).toBeInTheDocument();
      
      // Botões de distribuição
      expect(screen.getByTitle('Distribuir Horizontalmente')).toBeInTheDocument();
      expect(screen.getByTitle('Distribuir Verticalmente')).toBeInTheDocument();
    });
  });

  /**
   * Teste de estados de habilitação dos botões
   */
  describe('Estados de Habilitação', () => {
    test('botões de histórico são desabilitados quando canUndo e canRedo são false', () => {
      render(<Toolbar {...defaultProps} canUndo={false} canRedo={false} />);
      
      const undoButton = screen.getByTitle('Desfazer (Ctrl+Z)');
      const redoButton = screen.getByTitle('Refazer (Ctrl+Y)');
      
      expect(undoButton).toBeDisabled();
      expect(redoButton).toBeDisabled();
    });

    test('botões de histórico são habilitados quando canUndo e canRedo são true', () => {
      render(<Toolbar {...defaultProps} canUndo={true} canRedo={true} />);
      
      const undoButton = screen.getByTitle('Desfazer (Ctrl+Z)');
      const redoButton = screen.getByTitle('Refazer (Ctrl+Y)');
      
      expect(undoButton).not.toBeDisabled();
      expect(redoButton).not.toBeDisabled();
    });

    test('botões de cena são habilitados quando canDuplicate e canDelete são true', () => {
      render(<Toolbar {...defaultProps} canDuplicate={true} canDelete={true} />);
      
      const duplicateButton = screen.getByTitle('Duplicar Cena');
      const deleteButton = screen.getByTitle('Deletar Cena');
      
      expect(duplicateButton).not.toBeDisabled();
      expect(deleteButton).not.toBeDisabled();
    });

    test('botões de elementos são desabilitados quando canCopy e canPaste são false', () => {
      render(<Toolbar {...defaultProps} canCopy={false} canPaste={false} />);
      
      const copyButton = screen.getByTitle('Copiar Elemento (Ctrl+C)');
      const pasteButton = screen.getByTitle('Colar Elemento (Ctrl+V)');
      
      expect(copyButton).toBeDisabled();
      expect(pasteButton).toBeDisabled();
    });

    test('botões de alinhamento são desabilitados quando canAlign é false', () => {
      render(<Toolbar {...defaultProps} canAlign={false} />);
      
      const alignLeftButton = screen.getByTitle('Alinhar à Esquerda');
      const alignCenterButton = screen.getByTitle('Alinhar ao Centro');
      const alignRightButton = screen.getByTitle('Alinhar à Direita');
      
      expect(alignLeftButton).toBeDisabled();
      expect(alignCenterButton).toBeDisabled();
      expect(alignRightButton).toBeDisabled();
    });

    test('botões de distribuição são desabilitados quando canDistribute é false', () => {
      render(<Toolbar {...defaultProps} canDistribute={false} />);
      
      const distributeHButton = screen.getByTitle('Distribuir Horizontalmente');
      const distributeVButton = screen.getByTitle('Distribuir Verticalmente');
      
      expect(distributeHButton).toBeDisabled();
      expect(distributeVButton).toBeDisabled();
    });
  });

  /**
   * Teste de execução de ações
   */
  describe('Execução de Ações', () => {
    test('chama onUndo quando botão desfazer é clicado', () => {
      render(<Toolbar {...defaultProps} canUndo={true} />);
      
      const undoButton = screen.getByTitle('Desfazer (Ctrl+Z)');
      fireEvent.click(undoButton);
      
      expect(mockCallbacks.onUndo).toHaveBeenCalledTimes(1);
    });

    test('chama onRedo quando botão refazer é clicado', () => {
      render(<Toolbar {...defaultProps} canRedo={true} />);
      
      const redoButton = screen.getByTitle('Refazer (Ctrl+Y)');
      fireEvent.click(redoButton);
      
      expect(mockCallbacks.onRedo).toHaveBeenCalledTimes(1);
    });

    test('chama onDuplicateScene quando botão duplicar cena é clicado', () => {
      render(<Toolbar {...defaultProps} canDuplicate={true} />);
      
      const duplicateButton = screen.getByTitle('Duplicar Cena');
      fireEvent.click(duplicateButton);
      
      expect(mockCallbacks.onDuplicateScene).toHaveBeenCalledTimes(1);
    });

    test('chama onDeleteScene quando botão deletar cena é clicado', () => {
      render(<Toolbar {...defaultProps} canDelete={true} />);
      
      const deleteButton = screen.getByTitle('Deletar Cena');
      fireEvent.click(deleteButton);
      
      expect(mockCallbacks.onDeleteScene).toHaveBeenCalledTimes(1);
    });

    test('chama onCopyElement quando botão copiar elemento é clicado', () => {
      render(<Toolbar {...defaultProps} canCopy={true} />);
      
      const copyButton = screen.getByTitle('Copiar Elemento (Ctrl+C)');
      fireEvent.click(copyButton);
      
      expect(mockCallbacks.onCopyElement).toHaveBeenCalledTimes(1);
    });

    test('chama onPasteElement quando botão colar elemento é clicado', () => {
      render(<Toolbar {...defaultProps} canPaste={true} />);
      
      const pasteButton = screen.getByTitle('Colar Elemento (Ctrl+V)');
      fireEvent.click(pasteButton);
      
      expect(mockCallbacks.onPasteElement).toHaveBeenCalledTimes(1);
    });

    test('chama funções de alinhamento quando botões são clicados', () => {
      render(<Toolbar {...defaultProps} canAlign={true} />);
      
      const alignLeftButton = screen.getByTitle('Alinhar à Esquerda');
      const alignCenterButton = screen.getByTitle('Alinhar ao Centro');
      const alignRightButton = screen.getByTitle('Alinhar à Direita');
      
      fireEvent.click(alignLeftButton);
      fireEvent.click(alignCenterButton);
      fireEvent.click(alignRightButton);
      
      expect(mockCallbacks.onAlignLeft).toHaveBeenCalledTimes(1);
      expect(mockCallbacks.onAlignCenter).toHaveBeenCalledTimes(1);
      expect(mockCallbacks.onAlignRight).toHaveBeenCalledTimes(1);
    });

    test('chama funções de alinhamento vertical quando botões são clicados', () => {
      render(<Toolbar {...defaultProps} canAlign={true} />);
      
      const alignTopButton = screen.getByTitle('Alinhar ao Topo');
      const alignMiddleButton = screen.getByTitle('Alinhar ao Meio');
      const alignBottomButton = screen.getByTitle('Alinhar à Base');
      
      fireEvent.click(alignTopButton);
      fireEvent.click(alignMiddleButton);
      fireEvent.click(alignBottomButton);
      
      expect(mockCallbacks.onAlignTop).toHaveBeenCalledTimes(1);
      expect(mockCallbacks.onAlignMiddle).toHaveBeenCalledTimes(1);
      expect(mockCallbacks.onAlignBottom).toHaveBeenCalledTimes(1);
    });

    test('chama funções de distribuição quando botões são clicados', () => {
      render(<Toolbar {...defaultProps} canDistribute={true} />);
      
      const distributeHButton = screen.getByTitle('Distribuir Horizontalmente');
      const distributeVButton = screen.getByTitle('Distribuir Verticalmente');
      
      fireEvent.click(distributeHButton);
      fireEvent.click(distributeVButton);
      
      expect(mockCallbacks.onDistributeHorizontally).toHaveBeenCalledTimes(1);
      expect(mockCallbacks.onDistributeVertically).toHaveBeenCalledTimes(1);
    });
  });

  /**
   * Teste de feedback visual
   */
  describe('Feedback Visual', () => {
    test('botões não executam ações quando desabilitados', () => {
      render(<Toolbar {...defaultProps} canUndo={false} />);
      
      const undoButton = screen.getByTitle('Desfazer (Ctrl+Z)');
      fireEvent.click(undoButton);
      
      expect(mockCallbacks.onUndo).not.toHaveBeenCalled();
    });

    test('botão de deletar tem classe danger', () => {
      render(<Toolbar {...defaultProps} />);
      
      const deleteButton = screen.getByTitle('Deletar Cena');
      expect(deleteButton).toHaveClass('toolbar-btn', 'danger');
    });

    test('botões desabilitados têm opacidade reduzida', () => {
      render(<Toolbar {...defaultProps} canUndo={false} />);
      
      const undoButton = screen.getByTitle('Desfazer (Ctrl+Z)');
      expect(undoButton).toHaveClass('toolbar-btn', 'disabled');
    });
  });

  /**
   * Teste de acessibilidade
   */
  describe('Acessibilidade', () => {
    test('todos os botões têm atributos title', () => {
      render(<Toolbar {...defaultProps} />);
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAttribute('title');
      });
    });

    test('botões desabilitados têm atributo disabled', () => {
      render(<Toolbar {...defaultProps} canUndo={false} canRedo={false} />);
      
      const undoButton = screen.getByTitle('Desfazer (Ctrl+Z)');
      const redoButton = screen.getByTitle('Refazer (Ctrl+Y)');
      
      expect(undoButton).toHaveAttribute('disabled');
      expect(redoButton).toHaveAttribute('disabled');
    });
  });

  /**
   * Teste de integração
   */
  describe('Integração', () => {
    test('todas as seções são renderizadas corretamente', () => {
      render(<Toolbar {...defaultProps} />);
      
      // Verifica se todas as seções estão presentes
      const sections = [
        'Histórico',
        'Cenas', 
        'Elementos',
        'Alinhar Horizontal',
        'Alinhar Vertical',
        'Distribuir'
      ];
      
      sections.forEach(section => {
        expect(screen.getByText(section)).toBeInTheDocument();
      });
    });

    test('componente funciona sem props opcionais', () => {
      render(<Toolbar />);
      
      // Verifica se o componente renderiza sem erros
      expect(screen.getByText('Ferramentas')).toBeInTheDocument();
    });
  });
}); 