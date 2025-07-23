// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import DataTable from '../DataTable';

describe('DataTable Component', () => {
  test('renderiza o componente corretamente', () => {
    render(<DataTable />);
    expect(screen.getByText('DataTable')).toBeInTheDocument();
  });

  test('aplica classes CSS corretas', () => {
    render(<DataTable />);
    const container = screen.getByText('DataTable').parentElement;
    expect(container).toHaveClass('datatable-container');
  });
});
