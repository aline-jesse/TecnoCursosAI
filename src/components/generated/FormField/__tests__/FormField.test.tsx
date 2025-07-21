// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import FormField from '../FormField';

describe('FormField Component', () => {
  test('renderiza o componente corretamente', () => {
    render(<FormField />);
    expect(screen.getByText('FormField')).toBeInTheDocument();
  });

  test('aplica classes CSS corretas', () => {
    render(<FormField />);
    const container = screen.getByText('FormField').parentElement;
    expect(container).toHaveClass('formfield-container');
  });
});
