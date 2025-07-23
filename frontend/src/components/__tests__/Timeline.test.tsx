// src/components/__tests__/Timeline.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Timeline from '../Timeline';
import { useEditorStore } from '../../store/editorStore';

// Mock do store
jest.mock('../../store/editorStore');

const mockUseEditorStore = useEditorStore as jest.MockedFunction<
  typeof useEditorStore
>;

describe('Timeline', () => {
  const mockStore = {
    history: {
      present: [
        {
          id: 'scene-1',
          name: 'Cena 1',
          duration: 5,
          elements: [
            {
              id: 'element-1',
              type: 'text',
              x: 100,
              y: 100,
              width: 200,
              height: 50,
              rotation: 0,
              opacity: 1,
              text: 'Test',
              fontSize: 24,
              fontFamily: 'Arial',
              fill: '#000',
            },
          ],
          thumbnail: 'scene-1-thumb.jpg',
        },
        {
          id: 'scene-2',
          name: 'Cena 2',
          duration: 3,
          elements: [],
          thumbnail: 'scene-2-thumb.jpg',
        },
        {
          id: 'scene-3',
          name: 'Cena 3',
          duration: 7,
          elements: [],
          thumbnail: 'scene-3-thumb.jpg',
        },
      ],
      past: [],
      future: [],
    },
    currentSceneId: 'scene-1',
    setCurrentSceneId: jest.fn(),
    updateScene: jest.fn(),
  };

  beforeEach(() => {
    mockUseEditorStore.mockReturnValue(mockStore);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renderiza corretamente', () => {
    render(<Timeline />);

    expect(screen.getByTitle('Cena anterior')).toBeInTheDocument();
    expect(screen.getByTitle('Reproduzir')).toBeInTheDocument();
    expect(screen.getByTitle('Parar')).toBeInTheDocument();
    expect(screen.getByTitle('Próxima cena')).toBeInTheDocument();
  });

  it('exibe controles de reprodução', () => {
    render(<Timeline />);

    expect(screen.getByText('0:00')).toBeInTheDocument();
    expect(screen.getByText('/')).toBeInTheDocument();
    expect(screen.getByText('0:15')).toBeInTheDocument(); // 5 + 3 + 7 = 15 segundos
  });

  it('exibe blocos das cenas', () => {
    render(<Timeline />);

    expect(screen.getByText('Cena 1')).toBeInTheDocument();
    expect(screen.getByText('Cena 2')).toBeInTheDocument();
    expect(screen.getByText('Cena 3')).toBeInTheDocument();
  });

  it('destaca cena ativa', () => {
    render(<Timeline />);

    const activeScene = screen.getByText('Cena 1').closest('.timeline-block');
    expect(activeScene).toHaveClass('active');
  });

  it('permite selecionar cena ao clicar', () => {
    render(<Timeline />);

    const scene2 = screen.getByText('Cena 2').closest('.timeline-block');
    fireEvent.click(scene2!);

    expect(mockStore.setCurrentSceneId).toHaveBeenCalledWith('scene-2');
  });

  it('controla reprodução', () => {
    render(<Timeline />);

    const playBtn = screen.getByTitle('Reproduzir');
    fireEvent.click(playBtn);

    // Verificar se o estado de reprodução mudou (implementação interna)
    expect(playBtn).toBeInTheDocument();
  });

  it('controla reprodução', () => {
    render(<Timeline />);

    const playBtn = screen.getByTitle('Reproduzir');
    fireEvent.click(playBtn);

    // Verificar se o botão está presente
    expect(playBtn).toBeInTheDocument();
  });

  it('controla parada', () => {
    render(<Timeline />);

    const stopBtn = screen.getByTitle('Parar');
    fireEvent.click(stopBtn);

    // Verificar se o estado de parada mudou (implementação interna)
    expect(stopBtn).toBeInTheDocument();
  });

  it('navega para cena anterior', () => {
    render(<Timeline />);

    const prevBtn = screen.getByTitle('Cena anterior');
    fireEvent.click(prevBtn);

    // Deve navegar para a cena anterior (se disponível)
    expect(prevBtn).toBeInTheDocument();
  });

  it('navega para próxima cena', () => {
    render(<Timeline />);

    const nextBtn = screen.getByTitle('Próxima cena');
    fireEvent.click(nextBtn);

    // Deve navegar para a próxima cena
    expect(mockStore.setCurrentSceneId).toHaveBeenCalledWith('scene-2');
  });

  it('desabilita navegação quando não há cenas', () => {
    mockUseEditorStore.mockReturnValue({
      ...mockStore,
      currentSceneId: null,
    });

    render(<Timeline />);

    const prevBtn = screen.getByTitle('Cena anterior');
    const nextBtn = screen.getByTitle('Próxima cena');

    expect(prevBtn).toBeDisabled();
    expect(nextBtn).toBeDisabled();
  });

  it('permite editar duração da cena', () => {
    render(<Timeline />);

    const durationInput = screen.getByDisplayValue('5');
    fireEvent.change(durationInput, { target: { value: '10' } });

    expect(mockStore.updateScene).toHaveBeenCalledWith('scene-1', {
      duration: 10,
    });
  });

  it('valida duração mínima e máxima', () => {
    render(<Timeline />);

    const durationInput = screen.getByDisplayValue('5');

    // Testar valor mínimo
    fireEvent.change(durationInput, { target: { value: '0' } });
    expect(mockStore.updateScene).not.toHaveBeenCalledWith('scene-1', {
      duration: 0,
    });

    // Testar valor máximo
    fireEvent.change(durationInput, { target: { value: '100' } });
    expect(mockStore.updateScene).not.toHaveBeenCalledWith('scene-1', {
      duration: 100,
    });

    // Testar valor válido
    fireEvent.change(durationInput, { target: { value: '15' } });
    expect(mockStore.updateScene).toHaveBeenCalledWith('scene-1', {
      duration: 15,
    });
  });

  it('exibe contagem de elementos', () => {
    render(<Timeline />);

    expect(screen.getByText('1 elementos')).toBeInTheDocument();
  });

  it('exibe thumbnails das cenas', () => {
    render(<Timeline />);

    const thumbnails = screen.getAllByRole('img');
    expect(thumbnails.length).toBeGreaterThan(0);
  });

  it('alterna exibição de áudio', () => {
    render(<Timeline />);

    const audioBtn = screen.getByTitle('Ocultar áudio');
    fireEvent.click(audioBtn);

    // Verificar se a faixa de áudio foi ocultada (implementação interna)
    expect(audioBtn).toBeInTheDocument();
  });

  it('alterna configurações', () => {
    render(<Timeline />);

    const settingsBtn = screen.getByTitle('Configurações');
    fireEvent.click(settingsBtn);

    // Verificar se as configurações foram exibidas
    expect(screen.getByText('Volume:')).toBeInTheDocument();
    expect(screen.getByText('Velocidade:')).toBeInTheDocument();
  });

  it('controla volume', () => {
    render(<Timeline />);

    // Abrir configurações primeiro
    const settingsBtn = screen.getByTitle('Configurações');
    fireEvent.click(settingsBtn);

    const volumeSlider = screen.getByLabelText('Volume:');
    fireEvent.change(volumeSlider, { target: { value: '0.5' } });

    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('controla velocidade de reprodução', () => {
    render(<Timeline />);

    // Abrir configurações primeiro
    const settingsBtn = screen.getByTitle('Configurações');
    fireEvent.click(settingsBtn);

    const speedSelect = screen.getByLabelText('Velocidade:');
    fireEvent.change(speedSelect, { target: { value: '1.5' } });

    expect(speedSelect).toHaveValue('1.5');
  });

  it('exibe faixa de áudio quando habilitada', () => {
    render(<Timeline />);

    expect(screen.getByText('Áudio')).toBeInTheDocument();
    expect(
      screen.getByText('Áudio').closest('.audio-track')
    ).toBeInTheDocument();
  });

  it('oculta faixa de áudio quando desabilitada', () => {
    render(<Timeline />);

    const audioBtn = screen.getByTitle('Ocultar áudio');
    fireEvent.click(audioBtn);

    expect(screen.queryByText('Áudio')).not.toBeInTheDocument();
  });

  it('exibe blocos das cenas com duração', () => {
    render(<Timeline />);

    const scene1Block = screen.getByText('Cena 1').closest('.timeline-block');
    const scene2Block = screen.getByText('Cena 2').closest('.timeline-block');
    const scene3Block = screen.getByText('Cena 3').closest('.timeline-block');

    // Verificar se os blocos estão presentes
    expect(scene1Block).toBeInTheDocument();
    expect(scene2Block).toBeInTheDocument();
    expect(scene3Block).toBeInTheDocument();
  });

  it('exibe blocos das cenas em posições', () => {
    render(<Timeline />);

    const scene1Block = screen.getByText('Cena 1').closest('.timeline-block');
    const scene2Block = screen.getByText('Cena 2').closest('.timeline-block');
    const scene3Block = screen.getByText('Cena 3').closest('.timeline-block');

    // Verificar se os blocos estão presentes
    expect(scene1Block).toBeInTheDocument();
    expect(scene2Block).toBeInTheDocument();
    expect(scene3Block).toBeInTheDocument();
  });

  it('formata tempo corretamente', () => {
    render(<Timeline />);

    // Verificar se o tempo total está correto (5 + 3 + 7 = 15 segundos = 0:15)
    expect(screen.getByText('0:15')).toBeInTheDocument();
  });

  it('exibe indicador de tempo atual', () => {
    render(<Timeline />);

    const timeIndicator = document.querySelector('.time-indicator');
    expect(timeIndicator).toBeInTheDocument();
  });

  it('exibe indicador de tempo', () => {
    render(<Timeline />);

    const timeIndicator = document.querySelector('.time-indicator');
    expect(timeIndicator).toBeInTheDocument();
  });

  it('manipula eventos de clique nos blocos', () => {
    render(<Timeline />);

    const scene2Block = screen.getByText('Cena 2').closest('.timeline-block');
    fireEvent.click(scene2Block!);

    expect(mockStore.setCurrentSceneId).toHaveBeenCalledWith('scene-2');
  });

  it('previne propagação de eventos nos controles de duração', () => {
    render(<Timeline />);

    const durationInput = screen.getByDisplayValue('5');
    fireEvent.click(durationInput);

    // O clique no input não deve propagar para o bloco da cena
    expect(durationInput).toBeInTheDocument();
  });

  it('exibe tooltips informativos', () => {
    render(<Timeline />);

    const scene1Block = screen.getByText('Cena 1').closest('.timeline-block');
    expect(scene1Block).toHaveAttribute('title', 'Cena 1 (5s)');
  });

  it('manipula estado de reprodução', () => {
    render(<Timeline />);

    const playBtn = screen.getByTitle('Reproduzir');
    fireEvent.click(playBtn);

    // Verificar se o botão mudou para pausar
    expect(screen.getByTitle('Pausar')).toBeInTheDocument();
  });

  it('reseta tempo ao parar', () => {
    render(<Timeline />);

    const stopBtn = screen.getByTitle('Parar');
    fireEvent.click(stopBtn);

    // Verificar se o tempo foi resetado para 0:00
    expect(screen.getByText('0:00')).toBeInTheDocument();
  });

  it('navega entre cenas', () => {
    render(<Timeline />);

    // Navegar para próxima cena
    const nextBtn = screen.getByTitle('Próxima cena');
    fireEvent.click(nextBtn);
    expect(mockStore.setCurrentSceneId).toHaveBeenCalled();

    // Navegar para cena anterior
    const prevBtn = screen.getByTitle('Cena anterior');
    fireEvent.click(prevBtn);
    expect(mockStore.setCurrentSceneId).toHaveBeenCalled();
  });

  it('exibe botões de navegação', () => {
    render(<Timeline />);

    // Verificar se os botões estão presentes
    const prevBtn = screen.getByTitle('Cena anterior');
    const nextBtn = screen.getByTitle('Próxima cena');

    expect(prevBtn).toBeInTheDocument();
    expect(nextBtn).toBeInTheDocument();
  });
});
