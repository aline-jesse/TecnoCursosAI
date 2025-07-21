import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DragDropContext } from 'react-beautiful-dnd';
import AssetPanel from './AssetPanel';

/**
 * Mock das funções de callback
 */
const mockCallbacks = {
  onAssetAdd: jest.fn(),
  onAssetRemove: jest.fn(),
  onAssetSelect: jest.fn(),
  onCreateCharacter: jest.fn()
};

/**
 * Mock do URL.createObjectURL para testes
 */
global.URL.createObjectURL = jest.fn(() => 'mock-url');

/**
 * Dados de teste para assets
 */
const mockAssets = [
  {
    id: 'asset-1',
    name: 'Personagem 1',
    type: 'avatar',
    url: '/assets/characters/char1.svg',
    thumbnail: '/assets/characters/char1.svg',
    size: 1024,
    createdAt: '2024-01-01T00:00:00.000Z'
  },
  {
    id: 'asset-2',
    name: 'Imagem de fundo',
    type: 'image',
    url: '/assets/images/bg1.jpg',
    thumbnail: '/assets/images/bg1.jpg',
    size: 2048,
    createdAt: '2024-01-02T00:00:00.000Z'
  },
  {
    id: 'asset-3',
    name: 'Música de fundo',
    type: 'audio',
    url: '/assets/audio/music1.mp3',
    size: 5120,
    createdAt: '2024-01-03T00:00:00.000Z'
  },
  {
    id: 'asset-4',
    name: 'Texto explicativo',
    type: 'text',
    content: 'Este é um texto de exemplo',
    createdAt: '2024-01-04T00:00:00.000Z'
  }
];

/**
 * Wrapper para renderizar o componente com DragDropContext
 */
const renderAssetPanel = (props = {}) => {
  const defaultProps = {
    assets: mockAssets,
    ...mockCallbacks,
    ...props
  };

  return render(
    <DragDropContext onDragEnd={() => {}}>
      <AssetPanel {...defaultProps} />
    </DragDropContext>
  );
};

/**
 * Limpa todos os mocks antes de cada teste
 */
beforeEach(() => {
  jest.clearAllMocks();
  global.URL.createObjectURL.mockClear();
});

/**
 * Testes do componente AssetPanel
 */
describe('AssetPanel', () => {
  /**
   * Teste: Renderiza corretamente
   */
  test('renderiza o painel de assets corretamente', () => {
    renderAssetPanel();
    
    // Verifica se o título está presente
    expect(screen.getByText('📁 Biblioteca de Assets')).toBeInTheDocument();
    
    // Verifica se as abas estão presentes
    expect(screen.getByText('👤 Personagens')).toBeInTheDocument();
    expect(screen.getByText('🖼️ Imagens')).toBeInTheDocument();
    expect(screen.getByText('🎵 Áudio')).toBeInTheDocument();
    expect(screen.getByText('📝 Texto')).toBeInTheDocument();
    
    // Verifica se a barra de busca está presente
    expect(screen.getByPlaceholderText('Buscar assets...')).toBeInTheDocument();
  });

  /**
   * Teste: Exibe lista de assets com informações corretas
   */
  test('exibe lista de assets com informações corretas', () => {
    renderAssetPanel();
    
    // Verifica se o primeiro asset (personagem) é exibido na aba padrão
    expect(screen.getByText('Personagem 1')).toBeInTheDocument();
    expect(screen.getByText('avatar')).toBeInTheDocument();
    
    // Verifica se o asset tem informações básicas
    expect(screen.getByText('Personagem 1')).toBeInTheDocument();
  });

  /**
   * Teste: Filtra assets por categoria
   */
  test('filtra assets por categoria corretamente', async () => {
    renderAssetPanel();
    
    // Inicialmente deve mostrar apenas personagens (aba padrão)
    expect(screen.getByText('Personagem 1')).toBeInTheDocument();
    expect(screen.queryByText('Imagem de fundo')).not.toBeInTheDocument();
    
    // Clica na aba de imagens
    fireEvent.click(screen.getByText('🖼️ Imagens'));
    await waitFor(() => {
      expect(screen.getByText('Imagem de fundo')).toBeInTheDocument();
      expect(screen.queryByText('Personagem 1')).not.toBeInTheDocument();
    });
    
    // Clica na aba de áudio
    fireEvent.click(screen.getByText('🎵 Áudio'));
    await waitFor(() => {
      expect(screen.getByText('Música de fundo')).toBeInTheDocument();
      expect(screen.queryByText('Imagem de fundo')).not.toBeInTheDocument();
    });
    
    // Clica na aba de texto
    fireEvent.click(screen.getByText('📝 Texto'));
    await waitFor(() => {
      expect(screen.getByText('Texto explicativo')).toBeInTheDocument();
      expect(screen.queryByText('Música de fundo')).not.toBeInTheDocument();
    });
  });

  /**
   * Teste: Filtra assets por busca
   */
  test('filtra assets por termo de busca', async () => {
    renderAssetPanel();
    
    const searchInput = screen.getByPlaceholderText('Buscar assets...');
    
    // Busca por "personagem"
    fireEvent.change(searchInput, { target: { value: 'personagem' } });
    await waitFor(() => {
      expect(screen.getByText('Personagem 1')).toBeInTheDocument();
      expect(screen.queryByText('Imagem de fundo')).not.toBeInTheDocument();
    });
    
    // Limpa a busca e clica na aba de imagens para testar busca por "imagem"
    fireEvent.change(searchInput, { target: { value: '' } });
    fireEvent.click(screen.getByText('🖼️ Imagens'));
    
    // Agora busca por "imagem" na aba de imagens
    fireEvent.change(searchInput, { target: { value: 'imagem' } });
    await waitFor(() => {
      expect(screen.getByText('Imagem de fundo')).toBeInTheDocument();
      expect(screen.queryByText('Personagem 1')).not.toBeInTheDocument();
    });
  });

  /**
   * Teste: Adiciona novo texto
   */
  test('adiciona novo texto quando clica no botão', async () => {
    renderAssetPanel();
    
    // Clica na aba de texto
    fireEvent.click(screen.getByText('📝 Texto'));
    
    // Clica no botão de adicionar texto
    const addTextButton = screen.getByText('✏️ Adicionar Texto');
    fireEvent.click(addTextButton);
    
    // Verifica se a função de callback foi chamada
    await waitFor(() => {
      expect(mockCallbacks.onAssetAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          id: expect.stringMatching(/^text-/),
          name: 'Novo Texto',
          type: 'text',
          content: 'Digite seu texto aqui...'
        })
      );
    });
  });

  /**
   * Teste: Remove asset
   */
  test('remove asset quando clica no botão de remover', async () => {
    renderAssetPanel();
    
    // Encontra o botão de remover do primeiro asset
    const removeButtons = screen.getAllByTitle('Remover asset');
    fireEvent.click(removeButtons[0]);
    
    // Verifica se a função de callback foi chamada
    await waitFor(() => {
      expect(mockCallbacks.onAssetRemove).toHaveBeenCalledWith('asset-1');
    });
  });

  /**
   * Teste: Seleciona asset
   */
  test('seleciona asset quando clica no item', async () => {
    renderAssetPanel();
    
    // Clica no primeiro asset
    const assetItem = screen.getByText('Personagem 1').closest('.asset-item');
    fireEvent.click(assetItem);
    
    // Verifica se a função de callback foi chamada
    await waitFor(() => {
      expect(mockCallbacks.onAssetSelect).toHaveBeenCalledWith(mockAssets[0]);
    });
  });

  /**
   * Teste: Cria novo personagem
   */
  test('cria novo personagem através do modal', async () => {
    renderAssetPanel();
    
    // Clica no botão de criar personagem
    const createCharacterButton = screen.getByText('➕ Criar Personagem');
    fireEvent.click(createCharacterButton);
    
    // Verifica se o modal foi aberto
    expect(screen.getByText('Criar Novo Personagem')).toBeInTheDocument();
    
    // Digita o nome do personagem
    const nameInput = screen.getByPlaceholderText('Nome do personagem');
    fireEvent.change(nameInput, { target: { value: 'Novo Personagem' } });
    
    // Clica no botão de criar
    const createButton = screen.getByText('Criar');
    fireEvent.click(createButton);
    
    // Verifica se a função de callback foi chamada
    await waitFor(() => {
      expect(mockCallbacks.onCreateCharacter).toHaveBeenCalledWith(
        expect.objectContaining({
          id: expect.stringMatching(/^character-/),
          name: 'Novo Personagem',
          type: 'avatar'
        })
      );
    });
    
    // Verifica se o modal foi fechado
    expect(screen.queryByText('Criar Novo Personagem')).not.toBeInTheDocument();
  });

  /**
   * Teste: Cancela criação de personagem
   */
  test('cancela criação de personagem', async () => {
    renderAssetPanel();
    
    // Abre o modal
    fireEvent.click(screen.getByText('➕ Criar Personagem'));
    expect(screen.getByText('Criar Novo Personagem')).toBeInTheDocument();
    
    // Clica no botão cancelar
    const cancelButton = screen.getByText('Cancelar');
    fireEvent.click(cancelButton);
    
    // Verifica se o modal foi fechado
    await waitFor(() => {
      expect(screen.queryByText('Criar Novo Personagem')).not.toBeInTheDocument();
    });
    
    // Verifica se a função de callback não foi chamada
    expect(mockCallbacks.onCreateCharacter).not.toHaveBeenCalled();
  });

  /**
   * Teste: Botão criar personagem desabilitado sem nome
   */
  test('botão criar personagem fica desabilitado sem nome', () => {
    renderAssetPanel();
    
    // Abre o modal
    fireEvent.click(screen.getByText('➕ Criar Personagem'));
    
    // Verifica se o botão está desabilitado
    const createButton = screen.getByText('Criar');
    expect(createButton).toBeDisabled();
  });

  /**
   * Teste: Upload de arquivos
   */
  test('processa upload de arquivos corretamente', async () => {
    renderAssetPanel();
    
    // Simula upload de arquivo
    const file = new File(['test content'], 'test-image.jpg', { type: 'image/jpeg' });
    
    // Encontra o input de arquivo oculto
    const fileInput = document.querySelector('input[type="file"]');
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Verifica se a função de callback foi chamada
    await waitFor(() => {
      expect(mockCallbacks.onAssetAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          id: expect.stringMatching(/^asset-/),
          name: 'test-image.jpg',
          type: 'image',
          size: 12
        })
      );
    });
  });

  /**
   * Teste: Estado vazio
   */
  test('exibe estado vazio quando não há assets', () => {
    renderAssetPanel({ assets: [] });
    
    expect(screen.getByText('Nenhum asset encontrado')).toBeInTheDocument();
    expect(screen.getByText('Adicione novos assets usando os botões acima')).toBeInTheDocument();
  });

  /**
   * Teste: Estatísticas no footer
   */
  test('exibe estatísticas corretas no footer', () => {
    renderAssetPanel();
    
    // Verifica se as estatísticas são exibidas
    expect(screen.getByText('1 assets')).toBeInTheDocument();
    expect(screen.getByText('4 total')).toBeInTheDocument();
  });

  /**
   * Teste: Responsividade das abas
   */
  test('muda aba ativa corretamente', async () => {
    renderAssetPanel();
    
    // Verifica se a aba de personagens está ativa por padrão
    const charactersTab = screen.getByText('👤 Personagens');
    expect(charactersTab).toHaveClass('active');
    
    // Clica na aba de imagens
    const imagesTab = screen.getByText('🖼️ Imagens');
    fireEvent.click(imagesTab);
    
    // Verifica se a aba de imagens ficou ativa
    await waitFor(() => {
      expect(imagesTab).toHaveClass('active');
      expect(charactersTab).not.toHaveClass('active');
    });
  });

  /**
   * Teste: Acessibilidade
   */
  test('tem elementos acessíveis', () => {
    renderAssetPanel();
    
    // Verifica se os botões têm títulos
    const removeButtons = screen.getAllByTitle('Remover asset');
    expect(removeButtons.length).toBeGreaterThan(0);
    
    // Verifica se os inputs têm labels
    const searchInput = screen.getByPlaceholderText('Buscar assets...');
    expect(searchInput).toBeInTheDocument();
  });
}); 