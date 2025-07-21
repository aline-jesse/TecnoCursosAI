/**
 * VideoPreviewModal - Modal de Preview de Vídeo/Cena
 * TecnoCursos AI - Sistema de Preview Avançado
 *
 * Este componente permite ao usuário visualizar e ajustar cenas antes de exportar,
 * incluindo controles de tempo, animação, transição e áudio.
 *
 * Principais funcionalidades:
 * - Preview em tempo real da cena/vídeo
 * - Ajuste fino de tempo, transições, animações e áudio
 * - Exportação customizada
 * - Regeneração de narração IA
 * - Interface responsiva e acessível
 */

import React, { useState, useCallback, useRef, useEffect } from 'react'
import {
  VideoPreviewModalProps,
  ExportConfig,
  ScenePreviewConfig,
  TransitionConfig,
  AudioConfig
} from '../types/preview'
import { useVideoPreview } from '../hooks/useVideoPreview'
import PreviewCanvas from './PreviewCanvas'
import TimelineControls from './TimelineControls'
import './VideoPreviewModal.css'

const VideoPreviewModal: React.FC<VideoPreviewModalProps> = ({
  isOpen,
  scenes,
  initialSceneIndex = 0,
  onClose,
  onExport,
  onSave,
  onRegenerateNarration
}) => {
  // Hook principal do preview
  const { state, actions, events } = useVideoPreview(scenes, initialSceneIndex)
  
  // Estados locais do modal
  const [activeTab, setActiveTab] = useState<'preview' | 'timing' | 'audio' | 'transitions' | 'export'>('preview')
  const [isProcessing, setIsProcessing] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)
  
  // Configurações de export
  const [exportConfig, setExportConfig] = useState<ExportConfig>({
    format: 'mp4',
    quality: 'high',
    fps: 30,
    resolution: { width: 1920, height: 1080 },
    includeAudio: true,
    watermark: {
      enabled: false,
      position: 'bottom-right',
      opacity: 0.5
    }
  })

  // Refs para elementos
  const modalRef = useRef<HTMLDivElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  // Obter cena atual
  const currentScene = state.scenes[state.currentSceneIndex]

  /**
   * Fechar modal ao clicar fora
   */
  const handleBackdropClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }, [onClose])

  /**
   * Fechar modal com ESC
   */
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, onClose])

  /**
   * Salvar alterações
   */
  const handleSave = useCallback(async () => {
    try {
      setIsProcessing(true)
      await onSave(state.scenes)
    } catch (error) {
      console.error('Erro ao salvar:', error)
    } finally {
      setIsProcessing(false)
    }
  }, [state.scenes, onSave])

  /**
   * Exportar vídeo
   */
  const handleExport = useCallback(async () => {
    try {
      setIsProcessing(true)
      await onExport(exportConfig)
      setShowExportDialog(false)
    } catch (error) {
      console.error('Erro ao exportar:', error)
    } finally {
      setIsProcessing(false)
    }
  }, [exportConfig, onExport])

  /**
   * Regenerar narração IA
   */
  const handleRegenerateNarration = useCallback(async (sceneId: string) => {
    const scene = state.scenes.find(s => s.id === sceneId)
    if (!scene || !scene.audio?.text) return

    try {
      setIsProcessing(true)
      const newAudioUrl = await onRegenerateNarration(sceneId, scene.audio.text)

      // Atualiza a configuração da cena com a nova narração
      const sceneIndex = state.scenes.findIndex(s => s.id === sceneId)
      if (sceneIndex !== -1) {
        const updatedScene = {
          ...scene,
          audio: {
            ...scene.audio,
            url: newAudioUrl
          }
        }
        actions.updateScene(sceneId, updatedScene)
      }
    } catch (error) {
      console.error('Erro ao regenerar narração:', error)
    } finally {
      setIsProcessing(false)
    }
  }, [state.scenes, onRegenerateNarration, actions])

  /**
   * Atualizar configurações de áudio
   */
  const handleAudioConfigChange = useCallback((newAudioConfig: Partial<AudioConfig>) => {
    if (!currentScene) return

    const updatedAudio = {
      ...currentScene.audio,
      ...newAudioConfig
    } as AudioConfig

    actions.updateScene(currentScene.id, {
      ...currentScene,
      audio: updatedAudio
    })
  }, [currentScene, actions])

  /**
   * Atualizar configurações de transição
   */
  const handleTransitionConfigChange = useCallback((newTransitionConfig: Partial<TransitionConfig>) => {
    if (!currentScene) return

    const updatedTransition = {
      ...currentScene.transition,
      ...newTransitionConfig
    } as TransitionConfig

    actions.updateScene(currentScene.id, {
      ...currentScene,
      transition: updatedTransition
    })
  }, [currentScene, actions])

  /**
   * Renderizar abas do modal
   */
  const renderTabs = () => (
    <div className="preview-modal-tabs">
      {[
        { id: 'preview', label: '👀 Preview', icon: '👀' },
        { id: 'timing', label: '⏱️ Timing', icon: '⏱️' },
        { id: 'audio', label: '🔊 Áudio', icon: '🔊' },
        { id: 'transitions', label: '🎬 Transições', icon: '🎬' },
        { id: 'export', label: '📤 Exportar', icon: '📤' }
      ].map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id as any)}
          className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
        >
          <span className="tab-icon">{tab.icon}</span>
          <span className="tab-label">{tab.label}</span>
        </button>
      ))}
    </div>
  )

  if (!isOpen) return null

  return (
    <div className="preview-modal-backdrop" onClick={handleBackdropClick}>
      <div ref={modalRef} className="preview-modal">
        {/* Header do modal */}
        <div className="preview-modal-header">
          <h2>🎬 Preview de Vídeo/Cena</h2>
          <button onClick={onClose} className="close-button">
            ✕
          </button>
        </div>

        {/* Tabs de navegação */}
        {renderTabs()}

        {/* Conteúdo principal */}
        <div className="preview-modal-content">
          {/* Tab: Preview */}
          {activeTab === 'preview' && (
            <div className="preview-tab">
              <div className="preview-layout">
                {/* Canvas de preview */}
                <div className="preview-canvas-container">
                  <PreviewCanvas
                    scene={currentScene}
                    playerState={state.playerState}
                    onElementSelect={actions.selectElement}
                    onElementUpdate={actions.updateElement}
                  />
                  
                  {/* Controles de reprodução */}
                  <div className="playback-controls">
                    <button
                      onClick={state.playerState.isPlaying ? actions.pause : actions.play}
                      className="play-pause-button"
                    >
                      {state.playerState.isPlaying ? '⏸️' : '▶️'}
                    </button>
                    
                    <button onClick={actions.stop} className="stop-button">
                      ⏹️
                    </button>
                    
                    <div className="time-display">
                      <span>{Math.round(state.playerState.currentTime)}s</span>
                      <span>/</span>
                      <span>{Math.round(state.playerState.totalDuration)}s</span>
                    </div>
                    
                    <div className="speed-control">
                      <label>Velocidade:</label>
                      <select
                        value={state.playerState.playbackSpeed}
                        onChange={(e) => actions.setSpeed(Number(e.target.value))}
                      >
                        <option value={0.5}>0.5x</option>
                        <option value={0.75}>0.75x</option>
                        <option value={1}>1x</option>
                        <option value={1.25}>1.25x</option>
                        <option value={1.5}>1.5x</option>
                        <option value={2}>2x</option>
                      </select>
                    </div>
                    
                    <div className="quality-control">
                      <label>Qualidade:</label>
                      <select
                        value={state.playerState.quality}
                        onChange={(e) => {
                          // TODO: Implementar mudança de qualidade
                          console.log('Mudar qualidade para:', e.target.value)
                        }}
                      >
                        <option value="low">Baixa</option>
                        <option value="medium">Média</option>
                        <option value="high">Alta</option>
                        <option value="ultra">Ultra</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Informações da cena */}
                <div className="scene-info-panel">
                  <h3>📝 Informações da Cena</h3>
                  <div className="scene-details">
                    <div className="detail-item">
                      <strong>Nome:</strong> {currentScene.name}
                    </div>
                    <div className="detail-item">
                      <strong>Duração:</strong> {currentScene.duration}s
                    </div>
                    <div className="detail-item">
                      <strong>Elementos:</strong> {currentScene.elements.length}
                    </div>
                    <div className="detail-item">
                      <strong>Fundo:</strong> {currentScene.background.type}
                    </div>
                  </div>

                  {/* Informações de áudio */}
                  {currentScene.audio && (
                    <div className="audio-info">
                      <h4>🔊 Áudio</h4>
                      <div className="audio-details">
                        <span>🎵 Tipo: {currentScene.audio.isNarration ? 'Narração' : 'Música'}</span>
                        <span>🔊 Volume: {Math.round(currentScene.audio.volume * 100)}%</span>
                        <span>⏱️ Início: {currentScene.audio.startTime}s</span>
                        {currentScene.audio.endTime && (
                          <span>⏹️ Fim: {currentScene.audio.endTime}s</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Timeline de controles */}
              <div className="timeline-container">
                <TimelineControls
                  config={state.timelineConfig}
                  playerState={state.playerState}
                  onTimeChange={actions.seek}
                  onSpeedChange={actions.setSpeed}
                  onMarkerAdd={actions.addMarker}
                  onMarkerRemove={actions.removeMarker}
                  onSceneSelect={actions.goToScene}
                />
              </div>
            </div>
          )}

          {/* Tab: Timing */}
          {activeTab === 'timing' && (
            <div className="timing-tab">
              <h3>⏱️ Configurações de Tempo</h3>
              
              <div className="timing-controls">
                <div className="control-group">
                  <label>Duração da Cena (segundos):</label>
                  <input
                    type="number"
                    min="0.1"
                    max="60"
                    step="0.1"
                    value={currentScene.duration}
                    onChange={(e) => {
                      const newDuration = parseFloat(e.target.value)
                      if (newDuration > 0) {
                        actions.updateScene(currentScene.id, {
                          ...currentScene,
                          duration: newDuration
                        })
                      }
                    }}
                  />
                </div>

                <div className="control-group">
                  <label>Animações dos Elementos:</label>
                  {currentScene.elements.map((element) => (
                    <div key={element.id} className="element-animation-control">
                      <span>{element.type} - {element.text || element.src || 'Sem nome'}</span>
                      <div className="animation-inputs">
                        <select
                          value={element.animationIn || 'none'}
                          onChange={(e) => {
                            actions.updateElement(element.id, {
                              animationIn: e.target.value as any
                            })
                          }}
                        >
                          <option value="none">Sem animação de entrada</option>
                          <option value="fadeIn">Fade In</option>
                          <option value="slideInLeft">Slide In Left</option>
                          <option value="slideInRight">Slide In Right</option>
                          <option value="slideInUp">Slide In Up</option>
                          <option value="slideInDown">Slide In Down</option>
                          <option value="zoomIn">Zoom In</option>
                          <option value="bounceIn">Bounce In</option>
                          <option value="rotateIn">Rotate In</option>
                        </select>
                        
                        <input
                          type="number"
                          min="0.1"
                          max="5"
                          step="0.1"
                          value={element.animationDuration || 1}
                          onChange={(e) => {
                            actions.updateElement(element.id, {
                              animationDuration: parseFloat(e.target.value)
                            })
                          }}
                          placeholder="Duração (s)"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab: Áudio */}
          {activeTab === 'audio' && (
            <div className="audio-tab">
              <h3>🔊 Configurações de Áudio</h3>
              
              {currentScene.audio ? (
                <div className="audio-controls">
                  {/* Controles de volume */}
                  <div className="control-group">
                    <label>Volume: {Math.round(currentScene.audio.volume * 100)}%</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={currentScene.audio.volume}
                      onChange={(e) => handleAudioConfigChange({
                        volume: parseFloat(e.target.value)
                      })}
                    />
                  </div>

                  {/* Controles de fade */}
                  <div className="control-group">
                    <label>Fade In (segundos):</label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.1"
                      value={currentScene.audio.fadeIn}
                      onChange={(e) => handleAudioConfigChange({
                        fadeIn: parseFloat(e.target.value)
                      })}
                    />
                  </div>

                  <div className="control-group">
                    <label>Fade Out (segundos):</label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.1"
                      value={currentScene.audio.fadeOut}
                      onChange={(e) => handleAudioConfigChange({
                        fadeOut: parseFloat(e.target.value)
                      })}
                    />
                  </div>

                  {/* Controles específicos para narração */}
                  {currentScene.audio.isNarration && currentScene.audio.text && (
                    <div className="audio-section">
                      <h4>Regenerar Narração IA</h4>
                      <div className="narration-controls">
                        <div className="control-group">
                          <label>Texto da Narração:</label>
                          <textarea
                            value={currentScene.audio.text}
                            onChange={(e) => {
                              const newAudio = {
                                ...currentScene.audio!,
                                text: e.target.value
                              }
                              handleAudioConfigChange(newAudio)
                            }}
                            rows={4}
                            placeholder="Digite o texto para narração IA..."
                          />
                        </div>
                        
                        <button
                          onClick={() => handleRegenerateNarration(currentScene.id)}
                          disabled={isProcessing}
                          className="regenerate-button"
                        >
                          {isProcessing ? '🔄 Gerando...' : '🤖 Regenerar Narração IA'}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Botão para trocar áudio */}
                  <div className="audio-section">
                    <h4>Trocar Áudio</h4>
                    <button
                      onClick={() => {
                        // TODO: Implementar seletor de arquivo
                        console.log('Abrir seletor de arquivo de áudio')
                      }}
                      className="change-audio-button"
                    >
                      📁 Escolher Novo Áudio
                    </button>
                  </div>
                </div>
              ) : (
                <div className="no-audio">
                  <p>Esta cena não possui áudio configurado.</p>
                  <button
                    onClick={() => {
                      const newAudio: AudioConfig = {
                        url: '',
                        volume: 1,
                        startTime: 0,
                        fadeIn: 0,
                        fadeOut: 0,
                        isNarration: true,
                        text: 'Digite o texto para narração...'
                      }
                      handleAudioConfigChange(newAudio)
                    }}
                    className="add-audio-button"
                  >
                    ➕ Adicionar Áudio
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Tab: Transições */}
          {activeTab === 'transitions' && (
            <div className="transitions-tab">
              <h3>🎬 Configurações de Transição</h3>
              
              {currentScene.transition ? (
                <div className="transition-controls">
                  <div className="control-group">
                    <label>Tipo de Transição:</label>
                    <select
                      value={currentScene.transition.type}
                      onChange={(e) => handleTransitionConfigChange({
                        type: e.target.value as any
                      })}
                    >
                      <option value="none">Sem transição</option>
                      <option value="fade">Fade</option>
                      <option value="slideLeft">Slide Left</option>
                      <option value="slideRight">Slide Right</option>
                      <option value="slideUp">Slide Up</option>
                      <option value="slideDown">Slide Down</option>
                      <option value="zoom">Zoom</option>
                      <option value="rotate">Rotate</option>
                      <option value="flip">Flip</option>
                    </select>
                  </div>

                  <div className="control-group">
                    <label>Duração (segundos):</label>
                    <input
                      type="number"
                      min="0.1"
                      max="5"
                      step="0.1"
                      value={currentScene.transition.duration}
                      onChange={(e) => handleTransitionConfigChange({
                        duration: parseFloat(e.target.value)
                      })}
                    />
                  </div>

                  <div className="control-group">
                    <label>Easing:</label>
                    <select
                      value={currentScene.transition.easing}
                      onChange={(e) => handleTransitionConfigChange({
                        easing: e.target.value as any
                      })}
                    >
                      <option value="linear">Linear</option>
                      <option value="ease">Ease</option>
                      <option value="ease-in">Ease In</option>
                      <option value="ease-out">Ease Out</option>
                      <option value="ease-in-out">Ease In Out</option>
                    </select>
                  </div>

                  <div className="control-group">
                    <label>Delay (segundos):</label>
                    <input
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      value={currentScene.transition.delay || 0}
                      onChange={(e) => handleTransitionConfigChange({
                        delay: parseFloat(e.target.value)
                      })}
                    />
                  </div>

                  {/* Preview da transição */}
                  <div className="transition-preview">
                    <button
                      onClick={() => {
                        // TODO: Implementar preview da transição
                        console.log('Preview da transição')
                      }}
                      className="preview-transition-button"
                    >
                      👀 Preview da Transição
                    </button>
                  </div>
                </div>
              ) : (
                <div className="no-transition">
                  <p>Esta cena não possui transição configurada.</p>
                  <button
                    onClick={() => {
                      const newTransition: TransitionConfig = {
                        type: 'fade',
                        duration: 1,
                        easing: 'ease-in-out'
                      }
                      handleTransitionConfigChange(newTransition)
                    }}
                    className="add-transition-button"
                  >
                    ➕ Adicionar Transição
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Tab: Exportar */}
          {activeTab === 'export' && (
            <div className="export-tab">
              <h3>📤 Configurações de Exportação</h3>
              
              <div className="export-controls">
                <div className="control-group">
                  <label>Formato:</label>
                  <select
                    value={exportConfig.format}
                    onChange={(e) => setExportConfig(prev => ({
                      ...prev,
                      format: e.target.value as any
                    }))}
                  >
                    <option value="mp4">MP4</option>
                    <option value="webm">WebM</option>
                    <option value="avi">AVI</option>
                    <option value="mov">MOV</option>
                  </select>
                </div>

                <div className="control-group">
                  <label>Qualidade:</label>
                  <select
                    value={exportConfig.quality}
                    onChange={(e) => setExportConfig(prev => ({
                      ...prev,
                      quality: e.target.value as any
                    }))}
                  >
                    <option value="low">Baixa (rápido)</option>
                    <option value="medium">Média (balanceado)</option>
                    <option value="high">Alta (lento)</option>
                    <option value="ultra">Ultra (muito lento)</option>
                  </select>
                </div>

                <div className="control-group">
                  <label>FPS:</label>
                  <select
                    value={exportConfig.fps}
                    onChange={(e) => setExportConfig(prev => ({
                      ...prev,
                      fps: Number(e.target.value)
                    }))}
                  >
                    <option value={24}>24</option>
                    <option value={30}>30</option>
                    <option value={60}>60</option>
                  </select>
                </div>

                <div className="control-group">
                  <label>Resolução:</label>
                  <select
                    value={`${exportConfig.resolution.width}x${exportConfig.resolution.height}`}
                    onChange={(e) => {
                      const [width, height] = e.target.value.split('x').map(Number)
                      setExportConfig(prev => ({
                        ...prev,
                        resolution: { width, height }
                      }))
                    }}
                  >
                    <option value="1280x720">HD (1280x720)</option>
                    <option value="1920x1080">Full HD (1920x1080)</option>
                    <option value="3840x2160">4K (3840x2160)</option>
                    <option value="1080x1080">Square (1080x1080)</option>
                  </select>
                </div>

                <div className="control-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={exportConfig.includeAudio}
                      onChange={(e) => setExportConfig(prev => ({
                        ...prev,
                        includeAudio: e.target.checked
                      }))}
                    />
                    Incluir Áudio
                  </label>
                </div>

                {/* Configurações de marca d'água */}
                <div className="watermark-section">
                  <h4>🏷️ Marca D'Água</h4>
                  
                  <div className="control-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={exportConfig.watermark?.enabled || false}
                        onChange={(e) => setExportConfig(prev => ({
                          ...prev,
                          watermark: {
                            ...prev.watermark!,
                            enabled: e.target.checked
                          }
                        }))}
                      />
                      Ativar marca d'água
                    </label>
                  </div>

                  {exportConfig.watermark?.enabled && (
                    <>
                      <div className="control-group">
                        <label>Texto:</label>
                        <input
                          type="text"
                          value={exportConfig.watermark.text || ''}
                          onChange={(e) => setExportConfig(prev => ({
                            ...prev,
                            watermark: {
                              ...prev.watermark!,
                              text: e.target.value
                            }
                          }))}
                          placeholder="TecnoCursos AI"
                        />
                      </div>

                      <div className="control-group">
                        <label>Posição:</label>
                        <select
                          value={exportConfig.watermark.position}
                          onChange={(e) => setExportConfig(prev => ({
                            ...prev,
                            watermark: {
                              ...prev.watermark!,
                              position: e.target.value as any
                            }
                          }))}
                        >
                          <option value="top-left">Superior Esquerda</option>
                          <option value="top-right">Superior Direita</option>
                          <option value="bottom-left">Inferior Esquerda</option>
                          <option value="bottom-right">Inferior Direita</option>
                          <option value="center">Centro</option>
                        </select>
                      </div>

                      <div className="control-group">
                        <label>Opacidade: {Math.round(exportConfig.watermark.opacity * 100)}%</label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.01"
                          value={exportConfig.watermark.opacity}
                          onChange={(e) => setExportConfig(prev => ({
                            ...prev,
                            watermark: {
                              ...prev.watermark!,
                              opacity: parseFloat(e.target.value)
                            }
                          }))}
                        />
                      </div>
                    </>
                  )}
                </div>

                {/* Botão de exportação */}
                <div className="export-actions">
                  <button
                    onClick={handleExport}
                    disabled={isProcessing}
                    className="export-button"
                  >
                    {isProcessing ? '🔄 Exportando...' : '📤 Exportar Vídeo'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer com ações */}
        <div className="preview-modal-footer">
          <div className="footer-actions">
            <button
              onClick={handleSave}
              disabled={isProcessing}
              className="save-button"
            >
              {isProcessing ? '💾 Salvando...' : '💾 Salvar Alterações'}
            </button>
            
            <button
              onClick={onClose}
              className="cancel-button"
            >
              ❌ Fechar
            </button>
          </div>
        </div>
      </div>

      {/* Elemento de áudio para reprodução */}
      {currentScene.audio && (
        <audio
          ref={audioRef}
          src={currentScene.audio.url}
          /* volume={currentScene.audio.volume} */
          style={{ display: 'none' }}
        />
      )}
    </div>
  )
}

export default VideoPreviewModal