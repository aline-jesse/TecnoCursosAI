// src/components/__tests__/Toolbar.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import Toolbar from '../Toolbar';

/**
 * Teste de renderização para o componente Toolbar.
 *
 * Verifica se a barra de ferramentas é renderizada com os botões principais.
 */
describe('Toolbar', () => {
  it('should render the toolbar buttons', () => {
    render(<Toolbar />);
    expect(screen.getByTitle('Undo')).toBeInTheDocument();
    expect(screen.getByTitle('Redo')).toBeInTheDocument();
    expect(screen.getByTitle('Copy')).toBeInTheDocument();
    expect(screen.getByTitle('Delete')).toBeInTheDocument();
    expect(screen.getByTitle('Align Left')).toBeInTheDocument();
    expect(screen.getByTitle('Align Center')).toBeInTheDocument();
    expect(screen.getByTitle('Align Right')).toBeInTheDocument();
  });
}); 