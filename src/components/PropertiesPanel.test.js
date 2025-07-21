import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PropertiesPanel from './PropertiesPanel';

// Mock dos ícones do Heroicons
jest.mock('@heroicons/react/24/outline', () => ({
  Cog6ToothIcon: () => <div data-testid="cog-icon">⚙️</div>,
  DocumentTextIcon: () => <div data-testid="text-icon">📄</div>,
  PhotoIcon: () => <div data-testid="photo-icon">📷</div>,
  SpeakerWaveIcon: () => <div data-testid="speaker-icon">🔊</div>,
  UserIcon: () => <div data-testid="user-icon">👤</div>,
  FilmIcon: () => <div data-testid="film-icon">🎬</div>,
  EyeIcon: () => <div data-testid="eye-icon">👁️</div>,
  EyeSlashIcon: () => <div data-testid="eye-slash-icon">🙈</div>,
  LockClosedIcon: () => <div data-testid="lock-closed-icon">🔒</div>,
  LockOpenIcon: () => <div data-testid="lock-open-icon">🔓</div>,
  ArrowsPointingOutIcon: () => <div data-testid="arrows-icon">↔️</div>,
  AdjustmentsHorizontalIcon: () => <div data-testid="adjustments-icon">⚙️</div>,
  SwatchIcon: () => <div data-testid="swatch-icon">🎨</div>,
  FontBoldIcon: () => <div data-testid="bold-icon">B</div>,
  FontItalicIcon: () => <div data-testid="italic-icon">I</div>,
  AlignLeftIcon: () => <div data-testid="align-left-icon">◀</div>,
  AlignCenterIcon: () => <div data-testid="align-center-icon">◀▶</div>,
  AlignRightIcon: () => <div data-testid="align-right-icon">▶</div>,
  ChevronDownIcon: () => <div data-testid="chevron-down-icon">▼</div>,
  ChevronRightIcon: () => <div data-testid="chevron-right-icon">▶</div>
}));

describe('PropertiesPanel', () => {
  const mockSelectedElement = {
    id: 'element-1',
    type: 'text',
    name: 'Título da cena',
    x: 100,
    y: 50,
    width: 200,
    height: 100,
    content: 'Texto de exemplo'
  };

  const defaultProps = {
    selectedElement: null,
    onPropertyChange: jest.fn(),
    onReset: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    test('deve renderizar o painel quando nenhum elemento está selecionado', () => {
      render(<PropertiesPanel {...defaultProps} />);
      
      expect(screen.getByText('Propriedades')).toBeInTheDocument();
      expect(screen.getByText('Selecione um elemento para editar suas propriedades')).toBeInTheDocument();
      expect(screen.getByTestId('cog-icon')).toBeInTheDocument();
    });

    test('deve renderizar informações do elemento quando selecionado', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByText('Propriedades')).toBeInTheDocument();
      expect(screen.getByText('Título da cena')).toBeInTheDocument();
      expect(screen.getByTestId('text-icon')).toBeInTheDocument();
    });

    test('deve renderizar o botão de reset', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByText('Resetar')).toBeInTheDocument();
    });
  });

  describe('Seções do painel', () => {
    test('deve renderizar todas as seções quando elemento está selecionado', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByText('Posição')).toBeInTheDocument();
      expect(screen.getByText('Tamanho')).toBeInTheDocument();
      expect(screen.getByText('Texto')).toBeInTheDocument();
      expect(screen.getByText('Cores')).toBeInTheDocument();
      expect(screen.getByText('Efeitos')).toBeInTheDocument();
      expect(screen.getByText('Visibilidade')).toBeInTheDocument();
    });

    test('deve expandir/colapsar seções ao clicar', async () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const positionSection = screen.getByText('Posição').closest('button');
      const sizeSection = screen.getByText('Tamanho').closest('button');
      
      // Seções devem estar expandidas por padrão
      expect(screen.getByDisplayValue('100')).toBeInTheDocument(); // X position
      expect(screen.getByDisplayValue('50')).toBeInTheDocument();  // Y position
      
      // Clicar para colapsar
      fireEvent.click(positionSection);
      
      await waitFor(() => {
        expect(screen.queryByDisplayValue('100')).not.toBeInTheDocument();
      });
      
      // Clicar para expandir novamente
      fireEvent.click(positionSection);
      
      await waitFor(() => {
        expect(screen.getByDisplayValue('100')).toBeInTheDocument();
      });
    });
  });

  describe('Propriedades de posição', () => {
    test('deve renderizar inputs de posição X e Y', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const xInput = screen.getByDisplayValue('100');
      const yInput = screen.getByDisplayValue('50');
      
      expect(xInput).toBeInTheDocument();
      expect(yInput).toBeInTheDocument();
      expect(xInput.getAttribute('type')).toBe('number');
      expect(yInput.getAttribute('type')).toBe('number');
    });

    test('deve chamar onPropertyChange ao alterar posição', () => {
      const mockOnPropertyChange = jest.fn();
      render(
        <PropertiesPanel 
          {...defaultProps} 
          selectedElement={mockSelectedElement}
          onPropertyChange={mockOnPropertyChange}
        />
      );
      
      const xInput = screen.getByDisplayValue('100');
      fireEvent.change(xInput, { target: { value: '150' } });
      
      expect(mockOnPropertyChange).toHaveBeenCalledWith('element-1', 'position.x', 150);
    });
  });

  describe('Propriedades de tamanho', () => {
    test('deve renderizar inputs de largura e altura', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const widthInput = screen.getByDisplayValue('200');
      const heightInput = screen.getByDisplayValue('100');
      
      expect(widthInput).toBeInTheDocument();
      expect(heightInput).toBeInTheDocument();
    });

    test('deve chamar onPropertyChange ao alterar tamanho', () => {
      const mockOnPropertyChange = jest.fn();
      render(
        <PropertiesPanel 
          {...defaultProps} 
          selectedElement={mockSelectedElement}
          onPropertyChange={mockOnPropertyChange}
        />
      );
      
      const widthInput = screen.getByDisplayValue('200');
      fireEvent.change(widthInput, { target: { value: '250' } });
      
      expect(mockOnPropertyChange).toHaveBeenCalledWith('element-1', 'size.width', 250);
    });
  });

  describe('Propriedades de texto', () => {
    test('deve renderizar controles de texto para elementos do tipo text', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByText('Tamanho:')).toBeInTheDocument();
      expect(screen.getByText('Peso:')).toBeInTheDocument();
      expect(screen.getByTestId('bold-icon')).toBeInTheDocument();
      expect(screen.getByTestId('italic-icon')).toBeInTheDocument();
    });

    test('deve renderizar botões de alinhamento', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByTestId('align-left-icon')).toBeInTheDocument();
      expect(screen.getByTestId('align-center-icon')).toBeInTheDocument();
      expect(screen.getByTestId('align-right-icon')).toBeInTheDocument();
    });

    test('deve chamar onPropertyChange ao alterar propriedades de texto', () => {
      const mockOnPropertyChange = jest.fn();
      render(
        <PropertiesPanel 
          {...defaultProps} 
          selectedElement={mockSelectedElement}
          onPropertyChange={mockOnPropertyChange}
        />
      );
      
      const fontSizeSelect = screen.getByDisplayValue('16px');
      fireEvent.change(fontSizeSelect, { target: { value: '24' } });
      
      expect(mockOnPropertyChange).toHaveBeenCalledWith('element-1', 'style.fontSize', 24);
    });
  });

  describe('Propriedades de cor', () => {
    test('deve renderizar inputs de cor', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByText('Cor do texto:')).toBeInTheDocument();
      expect(screen.getByText('Cor de fundo:')).toBeInTheDocument();
    });

    test('deve renderizar cores predefinidas', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      // Verificar se há botões de cor predefinida
      const colorButtons = screen.getAllByRole('button').filter(button => 
        button.style.backgroundColor
      );
      expect(colorButtons.length).toBeGreaterThan(0);
    });

    test('deve chamar onPropertyChange ao alterar cor', () => {
      const mockOnPropertyChange = jest.fn();
      render(
        <PropertiesPanel 
          {...defaultProps} 
          selectedElement={mockSelectedElement}
          onPropertyChange={mockOnPropertyChange}
        />
      );
      
      const colorInput = screen.getByDisplayValue('#000000');
      fireEvent.change(colorInput, { target: { value: '#ff0000' } });
      
      expect(mockOnPropertyChange).toHaveBeenCalledWith('element-1', 'style.color', '#ff0000');
    });
  });

  describe('Propriedades de efeitos', () => {
    test('deve renderizar controles de opacidade e rotação', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByText('Opacidade:')).toBeInTheDocument();
      expect(screen.getByText('Rotação:')).toBeInTheDocument();
      expect(screen.getByText('Z-Index:')).toBeInTheDocument();
    });

    test('deve renderizar sliders de range', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const opacitySlider = screen.getByRole('slider', { name: /opacidade/i });
      const rotationSlider = screen.getByRole('slider', { name: /rotação/i });
      
      expect(opacitySlider).toBeInTheDocument();
      expect(rotationSlider).toBeInTheDocument();
    });

    test('deve chamar onPropertyChange ao alterar efeitos', () => {
      const mockOnPropertyChange = jest.fn();
      render(
        <PropertiesPanel 
          {...defaultProps} 
          selectedElement={mockSelectedElement}
          onPropertyChange={mockOnPropertyChange}
        />
      );
      
      const opacitySlider = screen.getByRole('slider', { name: /opacidade/i });
      fireEvent.change(opacitySlider, { target: { value: '50' } });
      
      expect(mockOnPropertyChange).toHaveBeenCalledWith('element-1', 'style.opacity', 0.5);
    });
  });

  describe('Propriedades de visibilidade', () => {
    test('deve renderizar botões de visibilidade e bloqueio', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByText('Visível')).toBeInTheDocument();
      expect(screen.getByText('Desbloqueado')).toBeInTheDocument();
    });

    test('deve chamar onPropertyChange ao alterar visibilidade', () => {
      const mockOnPropertyChange = jest.fn();
      render(
        <PropertiesPanel 
          {...defaultProps} 
          selectedElement={mockSelectedElement}
          onPropertyChange={mockOnPropertyChange}
        />
      );
      
      const visibilityButton = screen.getByText('Visível');
      fireEvent.click(visibilityButton);
      
      expect(mockOnPropertyChange).toHaveBeenCalledWith('element-1', 'visibility.visible', false);
    });
  });

  describe('Propriedades específicas por tipo', () => {
    test('deve renderizar propriedades específicas para elementos de imagem', () => {
      const imageElement = { ...mockSelectedElement, type: 'image' };
      render(<PropertiesPanel {...defaultProps} selectedElement={imageElement} />);
      
      expect(screen.getByText('Imagem')).toBeInTheDocument();
      expect(screen.getByText('URL:')).toBeInTheDocument();
      expect(screen.getByText('Alt:')).toBeInTheDocument();
    });

    test('deve renderizar propriedades específicas para elementos de áudio', () => {
      const audioElement = { ...mockSelectedElement, type: 'audio' };
      render(<PropertiesPanel {...defaultProps} selectedElement={audioElement} />);
      
      expect(screen.getByText('Áudio')).toBeInTheDocument();
      expect(screen.getByText('Volume:')).toBeInTheDocument();
      expect(screen.getByText('Loop:')).toBeInTheDocument();
    });

    test('deve renderizar propriedades específicas para elementos de vídeo', () => {
      const videoElement = { ...mockSelectedElement, type: 'video' };
      render(<PropertiesPanel {...defaultProps} selectedElement={videoElement} />);
      
      expect(screen.getByText('Vídeo')).toBeInTheDocument();
      expect(screen.getByText('Autoplay:')).toBeInTheDocument();
      expect(screen.getByText('Muted:')).toBeInTheDocument();
    });
  });

  describe('Interações do usuário', () => {
    test('deve chamar onReset ao clicar no botão resetar', () => {
      const mockOnReset = jest.fn();
      render(
        <PropertiesPanel 
          {...defaultProps} 
          selectedElement={mockSelectedElement}
          onReset={mockOnReset}
        />
      );
      
      const resetButton = screen.getByText('Resetar');
      fireEvent.click(resetButton);
      
      expect(mockOnReset).toHaveBeenCalledWith('element-1');
    });

    test('deve aplicar estilos ativos aos botões quando selecionados', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const boldButton = screen.getByTestId('bold-icon').closest('button');
      fireEvent.click(boldButton);
      
      expect(boldButton).toHaveClass('active');
    });

    test('deve mostrar valores corretos nos sliders', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const opacitySlider = screen.getByRole('slider', { name: /opacidade/i });
      expect(opacitySlider.value).toBe('100'); // 100% por padrão
      
      const rotationSlider = screen.getByRole('slider', { name: /rotação/i });
      expect(rotationSlider.value).toBe('0'); // 0° por padrão
    });
  });

  describe('Acessibilidade', () => {
    test('deve ter títulos descritivos para todos os botões', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAttribute('title');
      });
    });

    test('deve ter labels apropriados para inputs', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByLabelText('X:')).toBeInTheDocument();
      expect(screen.getByLabelText('Y:')).toBeInTheDocument();
      expect(screen.getByLabelText('Largura:')).toBeInTheDocument();
      expect(screen.getByLabelText('Altura:')).toBeInTheDocument();
    });

    test('deve ter roles apropriados para elementos interativos', () => {
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      expect(screen.getByRole('slider', { name: /opacidade/i })).toBeInTheDocument();
      expect(screen.getByRole('slider', { name: /rotação/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /resetar/i })).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    test('deve renderizar rapidamente com muitos elementos', () => {
      const startTime = performance.now();
      
      render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      expect(renderTime).toBeLessThan(100); // Deve renderizar em menos de 100ms
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const initialRenderCount = screen.getAllByRole('button').length;
      
      // Re-render com as mesmas props
      rerender(<PropertiesPanel {...defaultProps} selectedElement={mockSelectedElement} />);
      
      const finalRenderCount = screen.getAllByRole('button').length;
      expect(finalRenderCount).toBe(initialRenderCount);
    });
  });

  describe('Tratamento de erros', () => {
    test('deve lidar graciosamente com elementos inválidos', () => {
      const invalidElement = { id: 'invalid', type: 'invalid' };
      
      expect(() => {
        render(<PropertiesPanel {...defaultProps} selectedElement={invalidElement} />);
      }).not.toThrow();
    });

    test('deve lidar com valores undefined/null', () => {
      const elementWithNullValues = {
        ...mockSelectedElement,
        x: null,
        y: undefined,
        width: null,
        height: undefined
      };
      
      expect(() => {
        render(<PropertiesPanel {...defaultProps} selectedElement={elementWithNullValues} />);
      }).not.toThrow();
    });
  });
}); 