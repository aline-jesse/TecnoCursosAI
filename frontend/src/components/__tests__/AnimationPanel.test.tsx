import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AnimationPanel from '../AnimationPanel/AnimationPanel';

describe('AnimationPanel', () => {
  it('should render the AnimationPanel component', () => {
    render(<AnimationPanel />);
    expect(screen.getByText('Animações')).toBeInTheDocument();
  });

  it('should display placeholder text when no element is selected', () => {
    render(<AnimationPanel />);
    expect(screen.getByText('Selecione um elemento para animar.')).toBeInTheDocument();
  });

  it('should render as a section element', () => {
    const { container } = render(<AnimationPanel />);
    expect(container.firstChild?.nodeName).toBe('SECTION');
  });

  it('should have proper styling classes', () => {
    const { container } = render(<AnimationPanel />);
    const panel = container.firstChild;
    expect(panel).toHaveClass('p-4', 'bg-white', 'border-t', 'border-gray-200');
  });

  it('should render heading with proper styling', () => {
    render(<AnimationPanel />);
    const heading = screen.getByRole('heading', { level: 2 });
    expect(heading).toHaveClass('text-lg', 'font-bold', 'mb-4');
  });
});
