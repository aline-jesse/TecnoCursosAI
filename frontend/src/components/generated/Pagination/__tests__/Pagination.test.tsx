// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Pagination from '../Pagination';

describe('Pagination Component', () => {
  test('renderiza o componente corretamente', () => {
    render(<Pagination />);
    expect(screen.getByText('Pagination')).toBeInTheDocument();
  });

  test('aplica classes CSS corretas', () => {
    render(<Pagination />);
    const container = screen.getByText('Pagination').parentElement;
    expect(container).toHaveClass('pagination-container');
  });
});
