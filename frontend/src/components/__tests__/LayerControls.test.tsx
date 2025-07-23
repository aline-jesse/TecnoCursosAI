import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LayerControls from '../LayerControls/LayerControls';

describe('LayerControls', () => {
  it('should render all layer control buttons', () => {
    render(<LayerControls />);
    expect(screen.getByText('Trazer para frente')).toBeInTheDocument();
    expect(screen.getByText('Enviar para trás')).toBeInTheDocument();
    expect(screen.getByText('Avançar')).toBeInTheDocument();
    expect(screen.getByText('Recuar')).toBeInTheDocument();
  });

  it('should have proper flex layout', () => {
    const { container } = render(<LayerControls />);
    const controls = container.firstChild;
    expect(controls).toHaveClass('flex', 'flex-col', 'gap-2');
  });

  it('should render 4 buttons', () => {
    render(<LayerControls />);
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(4);
  });

  it('should have btn class on all buttons', () => {
    render(<LayerControls />);
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveClass('btn');
    });
  });
});
