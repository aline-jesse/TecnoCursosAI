// src/components/__tests__/SceneList.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import SceneList from '../SceneList';
import { useEditorStore } from '../../store/editorStore';

// Mock do Zustand store
jest.mock('../../store/editorStore');

/**
 * Teste de renderização para o componente SceneList.
 *
 * Verifica se o componente renderiza o título e o botão de adicionar cena.
 */
describe('SceneList', () => {
  it('should render the scene list controls', () => {
    // @ts-ignore
    useEditorStore.mockReturnValue({
      scenes: [],
      addScene: jest.fn(),
      deleteScene: jest.fn(),
      setCurrentSceneId: jest.fn(),
      currentSceneId: null,
    });

    render(<SceneList />);
    expect(screen.getByText('Scenes')).toBeInTheDocument();
    expect(screen.getByText('+ Add Scene')).toBeInTheDocument();
  });
}); 