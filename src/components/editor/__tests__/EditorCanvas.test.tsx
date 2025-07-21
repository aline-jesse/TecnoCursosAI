// src/components/editor/__tests__/EditorCanvas.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import EditorCanvas from '../EditorCanvas';
import { useEditorStore } from '../../../store/editorStore';

// Mock do Zustand store
jest.mock('../../../store/editorStore');

/**
 * Teste de renderização para o componente EditorCanvas.
 *
 * Verifica se o canvas é renderizado corretamente, mesmo quando
 * não há cena selecionada.
 */
describe('EditorCanvas', () => {
  it('should render the stage', () => {
    // @ts-ignore
    useEditorStore.mockReturnValue({
      scenes: [],
      currentSceneId: null,
      updateElement: jest.fn(),
    });

    render(<EditorCanvas />);
    // Verifica se o container do canvas está presente
    expect(document.querySelector('.editor-canvas-container')).toBeInTheDocument();
  });
}); 