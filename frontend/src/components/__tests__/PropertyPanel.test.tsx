import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PropertyPanel from '../PropertyPanel/PropertyPanel';

describe('PropertyPanel', () => {
  it('should render the PropertyPanel component', () => {
    render(<PropertyPanel />);
    expect(screen.getByText('Propriedades')).toBeInTheDocument();
  });

  it('should display placeholder text when no element is selected', () => {
    render(<PropertyPanel />);
    expect(screen.getByText('Selecione um elemento para editar suas propriedades.')).toBeInTheDocument();
  });

  it('should have proper styling classes', () => {
    const { container } = render(<PropertyPanel />);
    const panel = container.firstChild;
    expect(panel).toHaveClass('w-72', 'p-4', 'bg-white', 'border-l', 'border-gray-200', 'h-full');
  });

  it('should render as an aside element', () => {
    const { container } = render(<PropertyPanel />);
    expect(container.firstChild?.nodeName).toBe('ASIDE');
  });
});
