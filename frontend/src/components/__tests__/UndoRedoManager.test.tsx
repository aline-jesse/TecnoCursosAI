import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import UndoRedoManager from '../UndoRedoManager/UndoRedoManager';

describe('UndoRedoManager', () => {
  it('should render undo and redo buttons', () => {
    render(<UndoRedoManager />);
    expect(screen.getByText('Desfazer')).toBeInTheDocument();
    expect(screen.getByText('Refazer')).toBeInTheDocument();
  });

  it('should have proper flex layout', () => {
    const { container } = render(<UndoRedoManager />);
    const manager = container.firstChild;
    expect(manager).toHaveClass('flex', 'gap-2');
  });

  it('should render 2 buttons', () => {
    render(<UndoRedoManager />);
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(2);
  });

  it('should have btn class on all buttons', () => {
    render(<UndoRedoManager />);
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveClass('btn');
    });
  });

  it('should render buttons in correct order', () => {
    render(<UndoRedoManager />);
    const buttons = screen.getAllByRole('button');
    expect(buttons[0]).toHaveTextContent('Desfazer');
    expect(buttons[1]).toHaveTextContent('Refazer');
  });
});
