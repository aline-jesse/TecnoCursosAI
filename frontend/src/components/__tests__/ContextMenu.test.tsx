import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ContextMenu from '../ContextMenu/ContextMenu';

describe('ContextMenu', () => {
  it('should render all context menu items', () => {
    render(<ContextMenu />);
    expect(screen.getByText('Duplicar')).toBeInTheDocument();
    expect(screen.getByText('Deletar')).toBeInTheDocument();
    expect(screen.getByText('Editar')).toBeInTheDocument();
  });

  it('should render as a ul element', () => {
    const { container } = render(<ContextMenu />);
    expect(container.firstChild?.nodeName).toBe('UL');
  });

  it('should have proper styling for menu', () => {
    const { container } = render(<ContextMenu />);
    const menu = container.firstChild;
    expect(menu).toHaveClass('absolute', 'bg-white', 'border', 'rounded', 'shadow-md', 'p-2');
  });

  it('should render 3 menu items', () => {
    render(<ContextMenu />);
    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(3);
  });

  it('should have hover styles on menu items', () => {
    render(<ContextMenu />);
    const items = screen.getAllByRole('listitem');
    items.forEach(item => {
      expect(item).toHaveClass('p-2', 'hover:bg-gray-100', 'cursor-pointer');
    });
  });
});
