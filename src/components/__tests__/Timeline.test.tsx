// src/components/__tests__/Timeline.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import Timeline from '../Timeline';
import { useEditorStore } from '../../store/editorStore';

// Mock do Zustand store
jest.mock('../../store/editorStore');

/**
 * Teste de renderização para o componente Timeline.
 *
 * Verifica se o contêiner da timeline é renderizado corretamente.
 */
describe('Timeline', () => {
  it('should render the timeline track', () => {
    // @ts-ignore
    useEditorStore.mockReturnValue({
      scenes: [],
    });

    render(<Timeline />);
    expect(document.querySelector('.timeline-track')).toBeInTheDocument();
  });
}); 