// src/components/__tests__/AssetPanel.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AssetPanel from '../AssetPanel';
import { useEditorStore } from '../../store/editorStore';

// Mock do store
jest.mock('../../store/editorStore');

const mockUseEditorStore = useEditorStore as jest.MockedFunction<
  typeof useEditorStore
>;

describe('AssetPanel', () => {
  const mockStore = {
    assets: [
      {
        id: 'asset-1',
        name: 'Test Image',
        type: 'image' as const,
        src: 'test-image.jpg',
        thumbnail: 'test-thumbnail.jpg',
      },
      {
        id: 'asset-2',
        name: 'Test Audio',
        type: 'audio' as const,
        src: 'test-audio.mp3',
      },
      {
        id: 'asset-3',
        name: 'Test Character',
        type: 'character' as const,
        src: 'test-character.svg',
      },
    ],
    addAsset: jest.fn(),
    setDraggedAsset: jest.fn(),
  };

  beforeEach(() => {
    mockUseEditorStore.mockReturnValue(mockStore);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renderiza corretamente', () => {
    render(<AssetPanel />);

    expect(screen.getByText('Biblioteca de Assets')).toBeInTheDocument();
    expect(screen.getByText('Novo Asset')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Buscar assets...')).toBeInTheDocument();
  });

  it('exibe as categorias corretamente', () => {
    render(<AssetPanel />);

    expect(screen.getByText('Todos')).toBeInTheDocument();
    expect(screen.getByText('Personagens')).toBeInTheDocument();
    expect(screen.getByText('Imagens')).toBeInTheDocument();
    expect(screen.getByText('Áudio')).toBeInTheDocument();
  });

  it('filtra assets por categoria', () => {
    render(<AssetPanel />);

    // Clicar na categoria "Imagens"
    fireEvent.click(screen.getByText('Imagens'));

    // Deve mostrar apenas o asset de imagem
    expect(screen.getByText('Test Image')).toBeInTheDocument();
    expect(screen.queryByText('Test Audio')).not.toBeInTheDocument();
    expect(screen.queryByText('Test Character')).not.toBeInTheDocument();
  });

  it('filtra assets por busca', () => {
    render(<AssetPanel />);

    const searchInput = screen.getByPlaceholderText('Buscar assets...');
    fireEvent.change(searchInput, { target: { value: 'Audio' } });

    expect(screen.getByText('Test Audio')).toBeInTheDocument();
    expect(screen.queryByText('Test Image')).not.toBeInTheDocument();
    expect(screen.queryByText('Test Character')).not.toBeInTheDocument();
  });

  it('exibe estado vazio quando não há assets', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      assets: [],
    });

    render(<AssetPanel />);

    expect(screen.getByText('Nenhum asset encontrado')).toBeInTheDocument();
    expect(
      screen.getByText('Tente fazer upload de alguns arquivos')
    ).toBeInTheDocument();
  });

  it('permite upload de arquivos', async () => {
    render(<AssetPanel />);

    const file = new File(['test'], 'test-image.png', { type: 'image/png' });
    const input = screen.getByDisplayValue('');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(mockStore.addAsset).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'test-image',
          type: 'image',
        })
      );
    });
  });

  it('permite drag and drop de arquivos', async () => {
    render(<AssetPanel />);

    const file = new File(['test'], 'test-audio.mp3', { type: 'audio/mp3' });
    const uploadArea = screen
      .getByText('Arraste arquivos aqui ou clique para selecionar')
      .closest('div');

    fireEvent.dragOver(uploadArea!);
    fireEvent.drop(uploadArea!, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(mockStore.addAsset).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'test-audio',
          type: 'audio',
        })
      );
    });
  });

  it('inicia drag de asset', () => {
    render(<AssetPanel />);

    const assetItem = screen
      .getByText('Test Image')
      .closest('[draggable="true"]');

    fireEvent.dragStart(assetItem!);

    expect(mockStore.setDraggedAsset).toHaveBeenCalledWith(mockStore.assets[0]);
  });

  it('exibe estatísticas corretas', () => {
    render(<AssetPanel />);

    expect(screen.getByText('3 de 3 assets')).toBeInTheDocument();
  });

  it('filtra estatísticas quando há busca ativa', () => {
    render(<AssetPanel />);

    const searchInput = screen.getByPlaceholderText('Buscar assets...');
    fireEvent.change(searchInput, { target: { value: 'Audio' } });

    expect(screen.getByText('1 de 3 assets')).toBeInTheDocument();
  });

  it('determina tipo de asset baseado na extensão', async () => {
    render(<AssetPanel />);

    const imageFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const audioFile = new File(['test'], 'test.mp3', { type: 'audio/mp3' });
    const svgFile = new File(['test'], 'test.svg', { type: 'image/svg+xml' });

    const input = screen.getByDisplayValue('');

    // Testar imagem
    fireEvent.change(input, { target: { files: [imageFile] } });
    await waitFor(() => {
      expect(mockStore.addAsset).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'image' })
      );
    });

    // Testar áudio
    fireEvent.change(input, { target: { files: [audioFile] } });
    await waitFor(() => {
      expect(mockStore.addAsset).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'audio' })
      );
    });

    // Testar SVG
    fireEvent.change(input, { target: { files: [svgFile] } });
    await waitFor(() => {
      expect(mockStore.addAsset).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'image' })
      );
    });
  });

  it('exibe thumbnail para assets de áudio', () => {
    render(<AssetPanel />);

    const audioAsset = screen.getByText('Test Audio').closest('.asset-item');
    expect(audioAsset).toHaveClass('asset-item');

    // Verificar se o ícone de áudio está presente
    const audioIcon = audioAsset!.querySelector('.audio-thumbnail');
    expect(audioIcon).toBeInTheDocument();
  });

  it('exibe badges de tipo para cada asset', () => {
    render(<AssetPanel />);

    const assetItems = screen.getAllByRole('img', { hidden: true });
    expect(assetItems.length).toBeGreaterThan(0);

    // Verificar se os badges estão presentes
    const badges = document.querySelectorAll('.asset-type-badge');
    expect(badges.length).toBe(3);
  });

  it('trata erros de upload graciosamente', async () => {
    const consoleSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    mockStore.addAsset.mockImplementation(() => {
      throw new Error('Upload failed');
    });

    render(<AssetPanel />);

    const file = new File(['test'], 'test.png', { type: 'image/png' });
    const input = screen.getByDisplayValue('');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        'Erro ao fazer upload:',
        expect.any(Error)
      );
    });

    consoleSpy.mockRestore();
  });

  it('desabilita botão durante upload', async () => {
    render(<AssetPanel />);

    const newAssetBtn = screen.getByText('Novo Asset');
    expect(newAssetBtn).not.toBeDisabled();

    // Simular upload em andamento
    const file = new File(['test'], 'test.png', { type: 'image/png' });
    const input = screen.getByDisplayValue('');

    fireEvent.change(input, { target: { files: [file] } });

    // O botão deve estar desabilitado durante o upload
    await waitFor(() => {
      expect(newAssetBtn).toBeDisabled();
    });
  });
});
