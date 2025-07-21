import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import VideoPreviewModal from '../VideoPreviewModal'
import { ScenePreviewConfig } from '../../types/preview'
import userEvent from '@testing-library/user-event'

describe('VideoPreviewModal', () => {
  const scenes: ScenePreviewConfig[] = [
    {
      id: '1',
      name: 'Cena Teste',
      duration: 5,
      background: { type: 'color', value: '#fff' },
      elements: [],
      audio: { url: '', volume: 1, isNarration: true, text: 'Texto de teste', fadeIn: 0, fadeOut: 0, startTime: 0 },
      transition: { type: 'fade', duration: 1, easing: 'ease-in-out' },
      thumbnail: ''
    }
  ]

  it('renderiza corretamente o modal de preview', () => {
    render(
      <VideoPreviewModal
        isOpen={true}
        scenes={scenes}
        initialSceneIndex={0}
        onClose={() => {}}
        onSave={() => {}}
        onExport={() => {}}
        onRegenerateNarration={async () => ''}
      />
    )
    expect(screen.getByText('Preview')).toBeInTheDocument()
    expect(screen.getByText('Cena Teste')).toBeInTheDocument()
  })

  it('permite ajustar a duração da cena', async () => {
    render(
      <VideoPreviewModal
        isOpen={true}
        scenes={scenes}
        initialSceneIndex={0}
        onClose={() => {}}
        onSave={() => {}}
        onExport={() => {}}
        onRegenerateNarration={async () => ''}
      />
    )
    const timingTab = screen.getByRole('button', { name: /Timing/i })
    userEvent.click(timingTab)
    const input = screen.getByRole('spinbutton')
    userEvent.clear(input)
    userEvent.type(input, '8')
    expect(input).toHaveValue(8)
  })

  it('chama a função de exportação ao clicar em exportar', async () => {
    const onExport = jest.fn()
    render(
      <VideoPreviewModal
        isOpen={true}
        scenes={scenes}
        initialSceneIndex={0}
        onClose={() => {}}
        onSave={() => {}}
        onExport={onExport}
        onRegenerateNarration={async () => ''}
      />
    )
    const exportTab = screen.getByRole('button', { name: /Export/i })
    userEvent.click(exportTab)
    const exportBtn = screen.getByRole('button', { name: /Exportar Vídeo/i })
    userEvent.click(exportBtn)
    expect(onExport).toHaveBeenCalled()
  })

  it('chama a função de narração IA ao clicar em regenerar', async () => {
    const onRegenerateNarration = jest.fn().mockResolvedValue('url-novo-audio')
    render(
      <VideoPreviewModal
        isOpen={true}
        scenes={scenes}
        initialSceneIndex={0}
        onClose={() => {}}
        onSave={() => {}}
        onExport={() => {}}
        onRegenerateNarration={onRegenerateNarration}
      />
    )
    const audioTab = screen.getByRole('button', { name: /Áudio/i })
    userEvent.click(audioTab)
    const regenBtn = screen.getByRole('button', { name: /Regenerar Narração/i })
    userEvent.click(regenBtn)
    expect(onRegenerateNarration).toHaveBeenCalled()
  })

  it('permite ajustar o volume do áudio', async () => {
    render(
      <VideoPreviewModal
        isOpen={true}
        scenes={scenes}
        initialSceneIndex={0}
        onClose={() => {}}
        onSave={() => {}}
        onExport={() => {}}
        onRegenerateNarration={async () => ''}
      />
    )
    const audioTab = screen.getByRole('button', { name: /Áudio/i })
    userEvent.click(audioTab)
    const volumeSlider = screen.getByRole('slider')
    userEvent.type(volumeSlider, '{arrowleft}')
    expect(volumeSlider).toHaveValue('1') // valor inicial
  })
}) 