// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Modal from '../Modal';

describe('Modal Component', () => {
  test('renderiza o componente corretamente', () => {
    render(<Modal />);
    expect(screen.getByText('Modal')).toBeInTheDocument();
  });

  test('aplica classes CSS corretas', () => {
    render(<Modal />);
    const container = screen.getByText('Modal').parentElement;
    expect(container).toHaveClass('modal-container');
  });
});
