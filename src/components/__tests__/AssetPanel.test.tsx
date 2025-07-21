// src/components/__tests__/AssetPanel.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import AssetPanel from '../AssetPanel';

/**
 * Teste de renderização para o componente AssetPanel.
 *
 * Verifica se o componente é renderizado sem erros e se os
 * elementos principais, como o título, estão presentes.
 */
describe('AssetPanel', () => {
  it('should render without crashing', () => {
    render(<AssetPanel />);
    expect(screen.getByText('Asset Library')).toBeInTheDocument();
  });
}); 