// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Notification from '../Notification';

describe('Notification Component', () => {
  test('renderiza o componente corretamente', () => {
    render(<Notification />);
    expect(screen.getByText('Notification')).toBeInTheDocument();
  });

  test('aplica classes CSS corretas', () => {
    render(<Notification />);
    const container = screen.getByText('Notification').parentElement;
    expect(container).toHaveClass('notification-container');
  });
});
