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

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useVideoPreview } from '../hooks/useVideoPreview';
import { AnimatedEditorElement, AnimationType } from '../types/animation';
import {
  EditorElement,
  ImageElement,
  TextElement,
  VideoElement,
} from '../types/editor';
import {
  ExportConfig,
  PreviewQuality,
  VideoPreviewModalProps,
} from '../types/preview';
import {
  PlaybackSpeed,
  PreviewTab,
  Resolution,
  VideoFormat,
  VideoQuality,
} from '../types/video';
import PreviewCanvas from './PreviewCanvas';
import TimelineControls from './TimelineControls';
import './VideoPreviewModal.css';

interface TabConfig {
  id: PreviewTab;
  label: string;
  icon: string;
}

const DEFAULT_EXPORT_CONFIG: ExportConfig = {
  format: 'mp4',
  quality: 'high',
  resolution: { width: 1920, height: 1080 },
  fps: 30,
  includeAudio: true,
};

const TABS: TabConfig[] = [
  { id: 'preview', label: 'Preview', icon: '👀' },
  { id: 'timing', label: 'Timing', icon: '⏱️' },
  { id: 'audio', label: 'Áudio', icon: '🔊' },
  { id: 'transitions', label: 'Transições', icon: '🎬' },
  { id: 'export', label: 'Exportar', icon: '📤' },
];

const PLAYBACK_SPEEDS: PlaybackSpeed[] = [0.5, 0.75, 1, 1.25, 1.5, 2];

const PREVIEW_QUALITIES: PreviewQuality[] = ['low', 'medium', 'high'];

const VIDEO_FORMATS: VideoFormat[] = ['mp4', 'gif', 'webm'];

const VIDEO_QUALITIES: VideoQuality[] = ['low', 'medium', 'high'];

const VIDEO_RESOLUTIONS: Resolution[] = [
  { width: 1280, height: 720, label: 'HD (1280x720)' },
  { width: 1920, height: 1080, label: 'Full HD (1920x1080)' },
  { width: 3840, height: 2160, label: '4K (3840x2160)' },
  { width: 1080, height: 1080, label: 'Square (1080x1080)' },
];

const ANIMATION_TYPES: { value: AnimationType; label: string }[] = [
  { value: 'none', label: 'Sem animação de entrada' },
  { value: 'fadeIn', label: 'Fade In' },
  { value: 'slideInLeft', label: 'Slide In Left' },
  { value: 'slideInRight', label: 'Slide In Right' },
  { value: 'slideInUp', label: 'Slide In Up' },
  { value: 'slideInDown', label: 'Slide In Down' },
  { value: 'zoomIn', label: 'Zoom In' },
  { value: 'bounceIn', label: 'Bounce In' },
  { value: 'rotateIn', label: 'Rotate In' },
];

const VideoPreviewModal: React.FC<VideoPreviewModalProps> = ({
  isOpen,
  scenes,
  initialSceneIndex = 0,
  onClose,
  onExport,
  onRegenerateNarration: _onRegenerateNarration,
}) => {
  // Hook principal do preview
  const { state, actions } = useVideoPreview({
    initialScenes: scenes,
    initialSceneIndex,
  });

  // Estados locais do modal
  const [activeTab, setActiveTab] = useState<PreviewTab>('preview');
  const [isProcessing, setIsProcessing] = useState(false);
  const [exportConfig, setExportConfig] = useState<ExportConfig>(
    DEFAULT_EXPORT_CONFIG
  );

  // Refs para elementos
  const modalRef = useRef<HTMLDivElement>(null);

  // Obter cena atual
  const currentScene = state.scenes[state.currentSceneIndex];

  /**
   * Fechar modal ao clicar fora
   */
  const handleBackdropClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    },
    [onClose]
  );

  /**
   * Fechar modal com ESC
   */
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  /**
   * Salvar alterações
   */
  const handleSave = useCallback(async () => {
    try {
      setIsProcessing(true);
      await actions.updateSceneConfig(state.currentSceneIndex, currentScene);
    } catch (error) {
      console.error('Erro ao salvar:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [state.currentSceneIndex, currentScene, actions]);

  /**
   * Exportar vídeo
   */
  const handleExport = useCallback(async () => {
    try {
      setIsProcessing(true);
      await onExport(exportConfig);
    } catch (error) {
      console.error('Erro ao exportar:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [exportConfig, onExport]);

  /**
   * Atualizar elemento da cena
   */
  const handleElementUpdate = useCallback(
    (elementId: string, updates: Partial<AnimatedEditorElement>) => {
      const updatedElements = currentScene.elements.map(element =>
        element.id === elementId ? { ...element, ...updates } : element
      );

      actions.updateSceneConfig(state.currentSceneIndex, {
        elements: updatedElements,
      });
    },
    [currentScene, actions, state.currentSceneIndex]
  );

  /**
   * Renderizar abas do modal
   */
  const renderTabs = () => (
    <div className="preview-modal-tabs" role="tablist">
      {TABS.map(tab => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
          role="tab"
          aria-selected={activeTab === tab.id}
          aria-controls={`${tab.id}-panel`}
        >
          <span className="tab-icon" aria-hidden="true">
            {tab.icon}
          </span>
          <span className="tab-label">{tab.label}</span>
        </button>
      ))}
    </div>
  );

  /**
   * Renderizar controles de reprodução
   */
  const renderPlaybackControls = () => (
    <div
      className="playback-controls"
      role="group"
      aria-label="Controles de reprodução"
    >
      <button
        onClick={state.timeline.isPlaying ? actions.pause : actions.play}
        className="play-pause-button"
        aria-label={state.timeline.isPlaying ? 'Pausar' : 'Reproduzir'}
      >
        {state.timeline.isPlaying ? '⏸️' : '▶️'}
      </button>

      <button onClick={actions.stop} className="stop-button" aria-label="Parar">
        ⏹️
      </button>

      <div className="time-display" role="timer">
        <span>{Math.round(state.timeline.currentTime)}s</span>
        <span>/</span>
        <span>{Math.round(state.timeline.duration)}s</span>
      </div>

      <div className="speed-control">
        <label htmlFor="speed-select">Velocidade:</label>
        <select
          id="speed-select"
          value={state.timeline.playbackSpeed}
          onChange={e => actions.setSpeed(Number(e.target.value))}
        >
          {PLAYBACK_SPEEDS.map(speed => (
            <option key={speed} value={speed}>
              {speed}x
            </option>
          ))}
        </select>
      </div>

      <div className="quality-control">
        <label htmlFor="quality-select">Qualidade:</label>
        <select
          id="quality-select"
          value={state.quality}
          onChange={e => actions.setQuality(e.target.value as PreviewQuality)}
        >
          {PREVIEW_QUALITIES.map(quality => (
            <option key={quality} value={quality}>
              {quality.charAt(0).toUpperCase() + quality.slice(1)}
            </option>
          ))}
        </select>
      </div>
    </div>
  );

  /**
   * Renderizar configurações de exportação
   */
  const renderExportControls = () => (
    <div className="export-controls">
      <div className="control-group">
        <label htmlFor="format-select">Formato:</label>
        <select
          id="format-select"
          value={exportConfig.format}
          onChange={e =>
            setExportConfig(prev => ({
              ...prev,
              format: e.target.value as VideoFormat,
            }))
          }
        >
          {VIDEO_FORMATS.map(format => (
            <option key={format} value={format}>
              {format.toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      <div className="control-group">
        <label htmlFor="quality-select">Qualidade:</label>
        <select
          id="quality-select"
          value={exportConfig.quality}
          onChange={e =>
            setExportConfig(prev => ({
              ...prev,
              quality: e.target.value as VideoQuality,
            }))
          }
        >
          {VIDEO_QUALITIES.map(quality => (
            <option key={quality} value={quality}>
              {quality === 'high'
                ? 'Alta (lento)'
                : quality === 'medium'
                  ? 'Média (balanceado)'
                  : 'Baixa (rápido)'}
            </option>
          ))}
        </select>
      </div>

      <div className="control-group">
        <label htmlFor="fps-select">FPS:</label>
        <select
          id="fps-select"
          value={exportConfig.fps}
          onChange={e =>
            setExportConfig(prev => ({
              ...prev,
              fps: Number(e.target.value),
            }))
          }
        >
          {[24, 30, 60].map(fps => (
            <option key={fps} value={fps}>
              {fps}
            </option>
          ))}
        </select>
      </div>

      <div className="control-group">
        <label htmlFor="resolution-select">Resolução:</label>
        <select
          id="resolution-select"
          value={`${exportConfig.resolution.width}x${exportConfig.resolution.height}`}
          onChange={e => {
            const [width, height] = e.target.value.split('x').map(Number);
            setExportConfig(prev => ({
              ...prev,
              resolution: { width, height },
            }));
          }}
        >
          {VIDEO_RESOLUTIONS.map(resolution => (
            <option
              key={`${resolution.width}x${resolution.height}`}
              value={`${resolution.width}x${resolution.height}`}
            >
              {resolution.label}
            </option>
          ))}
        </select>
      </div>

      <div className="control-group">
        <label>
          <input
            type="checkbox"
            checked={exportConfig.includeAudio}
            onChange={e =>
              setExportConfig(prev => ({
                ...prev,
                includeAudio: e.target.checked,
              }))
            }
          />
          Incluir Áudio
        </label>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <div
      className="preview-modal-backdrop"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="preview-modal-title"
    >
      <div ref={modalRef} className="preview-modal" role="document">
        {/* Header do modal */}
        <div className="preview-modal-header">
          <h2 id="preview-modal-title">🎬 Preview de Vídeo/Cena</h2>
          <button
            onClick={onClose}
            className="close-button"
            aria-label="Fechar modal"
          >
            ✕
          </button>
        </div>

        {/* Tabs de navegação */}
        {renderTabs()}

        {/* Conteúdo principal */}
        <div
          className="preview-modal-content"
          role="tabpanel"
          aria-labelledby={`${activeTab}-tab`}
        >
          {/* Tab: Preview */}
          {activeTab === 'preview' && (
            <div className="preview-tab">
              <div className="preview-layout">
                {/* Canvas de preview */}
                <div className="preview-canvas-container">
                  <PreviewCanvas
                    scene={currentScene}
                    playerState={state.playerState}
                    currentTime={state.timeline.currentTime}
                    quality={state.quality}
                    isPlaying={state.timeline.isPlaying}
                    onElementSelect={id =>
                      actions.updateSceneConfig(state.currentSceneIndex, {
                        selectedElementId: id,
                      })
                    }
                    onElementUpdate={handleElementUpdate}
                  />

                  {/* Controles de reprodução */}
                  {renderPlaybackControls()}
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
                  </div>
                </div>
              </div>

              {/* Timeline de controles */}
              <div className="timeline-container">
                <TimelineControls
                  config={state.timeline}
                  playerState={state.playerState}
                  onTimeChange={actions.seek}
                  onSpeedChange={actions.setSpeed}
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
                  <label htmlFor="scene-duration">
                    Duração da Cena (segundos):
                  </label>
                  <input
                    id="scene-duration"
                    type="number"
                    min="0.1"
                    max="60"
                    step="0.1"
                    value={currentScene.duration}
                    onChange={e => {
                      const newDuration = parseFloat(e.target.value);
                      if (newDuration > 0) {
                        actions.updateSceneConfig(state.currentSceneIndex, {
                          duration: newDuration,
                        });
                      }
                    }}
                  />
                </div>

                <div className="control-group">
                  <label>Animações dos Elementos:</label>
                  {currentScene.elements.map((element: EditorElement) => {
                    const animatedElement = element as AnimatedEditorElement;
                    return (
                      <div
                        key={element.id}
                        className="element-animation-control"
                      >
                        <span>
                          {element.type} -{' '}
                          {element.type === 'text'
                            ? (element as TextElement).text
                            : element.type === 'image' ||
                                element.type === 'video'
                              ? (element as ImageElement | VideoElement).src
                              : 'Elemento'}
                        </span>
                        <div className="animation-inputs">
                          <select
                            value={animatedElement.animation?.type || 'none'}
                            onChange={e => {
                              handleElementUpdate(element.id, {
                                animation: {
                                  type: e.target.value as AnimationType,
                                  duration:
                                    animatedElement.animation?.duration || 1,
                                },
                              });
                            }}
                          >
                            {ANIMATION_TYPES.map(animation => (
                              <option
                                key={animation.value}
                                value={animation.value}
                              >
                                {animation.label}
                              </option>
                            ))}
                          </select>

                          <input
                            type="number"
                            min="0.1"
                            max="5"
                            step="0.1"
                            value={animatedElement.animation?.duration || 1}
                            onChange={e => {
                              handleElementUpdate(element.id, {
                                animation: {
                                  type:
                                    animatedElement.animation?.type || 'none',
                                  duration: parseFloat(e.target.value),
                                },
                              });
                            }}
                            placeholder="Duração (s)"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Tab: Áudio */}
          {activeTab === 'audio' && (
            <div className="audio-tab">
              <h3>🔊 Configurações de Áudio</h3>
              <div className="no-audio">
                <p>Esta funcionalidade está sendo refatorada.</p>
              </div>
            </div>
          )}

          {/* Tab: Transições */}
          {activeTab === 'transitions' && (
            <div className="transitions-tab">
              <h3>🎬 Configurações de Transição</h3>
              <div className="no-transition">
                <p>Esta funcionalidade está sendo refatorada.</p>
              </div>
            </div>
          )}

          {/* Tab: Exportar */}
          {activeTab === 'export' && (
            <div className="export-tab">
              <h3>📤 Configurações de Exportação</h3>
              {renderExportControls()}
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

            <button onClick={onClose} className="cancel-button">
              ❌ Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPreviewModal;
