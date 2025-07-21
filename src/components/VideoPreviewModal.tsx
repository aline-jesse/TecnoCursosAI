/**
 * VideoPreviewModal - Modal de Preview de Vídeo/Cena
 * TecnoCursos AI - Sistema de Preview Avançado
 * 
 * Este componente permite ao usuário visualizar e ajustar cenas antes de exportar,
 * incluindo controles de tempo, animação, transição e áudio.
 */
import React, { useState, useCallback, useRef } from 'react';
import { useVideoPreview } from '../hooks/useVideoPreview';
import { VideoPreviewModalProps, TransitionType } from '../types/preview';
import PreviewCanvas from './PreviewCanvas';
import { VideoScrubber } from './VideoScrubber';
import { AudioControls } from './AudioControls';
import './VideoScrubber.css';

// Opções de transição disponíveis
const transitionOptions: TransitionType[] = [
  'fade',
  'slideLeft',
  'slideRight',
  'slideUp',
  'slideDown',
  'zoom',
  'none'
];

export const VideoPreviewModal: React.FC<VideoPreviewModalProps> = ({
  isOpen,
  onClose,
  sceneId,
  onSave,
  onRegenerateNarration
}) => {
  // Hook de preview
  const {
    playerState,
    config,
    controls,
    updateAnimation,
    updateTransition,
    updateAudio
  } = useVideoPreview(sceneId);

  // Estados locais
  const [activeTab, setActiveTab] = useState<'preview' | 'audio' | 'transitions'>('preview');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Referências
  const videoRef = useRef<HTMLVideoElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  // Handler para regenerar narração
  const handleRegenerateNarration = useCallback(async () => {
    setIsRegenerating(true);
    try {
      const newNarrationUrl = await onRegenerateNarration(sceneId);
      updateAudio({
        narrationUrl: newNarrationUrl,
        needsRegeneration: false
      });
    } catch (error) {
      console.error('Erro ao regenerar narração:', error);
    } finally {
      setIsRegenerating(false);
    }
  }, [sceneId, onRegenerateNarration, updateAudio]);

  // Handler para salvar alterações
  const handleSave = useCallback(() => {
    onSave(config);
    onClose();
  }, [config, onSave, onClose]);

  // Handler para fullscreen
  const handleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      modalRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  // Handler para teclas de atalho
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case ' ':
        e.preventDefault();
        playerState.isPlaying ? controls.pause() : controls.play();
        break;
      case 'Escape':
        if (isFullscreen) {
          handleFullscreen();
        } else {
          onClose();
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        controls.seek(Math.max(0, playerState.currentTime - 5));
        break;
      case 'ArrowRight':
        e.preventDefault();
        controls.seek(Math.min(playerState.duration, playerState.currentTime + 5));
        break;
      case 'f':
      case 'F':
        e.preventDefault();
        handleFullscreen();
        break;
    }
  }, [playerState, controls, isFullscreen, handleFullscreen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${isFullscreen ? 'bg-black' : ''}`}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <div 
        ref={modalRef}
        className={`bg-white rounded-lg shadow-xl ${isFullscreen ? 'w-full h-full rounded-none' : 'w-[95vw] max-w-7xl h-[90vh]'} flex flex-col`}
      >
        {/* Cabeçalho */}
        <div className="p-4 border-b flex justify-between items-center bg-gray-50">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold">🎬 Preview da Cena</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('preview')}
                className={`px-3 py-1 rounded text-sm ${activeTab === 'preview' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
              >
                Preview
              </button>
              <button
                onClick={() => setActiveTab('audio')}
                className={`px-3 py-1 rounded text-sm ${activeTab === 'audio' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
              >
                Áudio
              </button>
              <button
                onClick={() => setActiveTab('transitions')}
                className={`px-3 py-1 rounded text-sm ${activeTab === 'transitions' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
              >
                Transições
              </button>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleFullscreen}
              className="p-2 text-gray-500 hover:text-gray-700"
              title="Tela cheia (F)"
            >
              {isFullscreen ? '🗗' : '⛶'}
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700"
              title="Fechar (ESC)"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Área principal */}
        <div className="flex-1 flex gap-4 p-4 overflow-hidden">
          {/* Área de preview */}
          <div className="flex-1 flex flex-col">
            <div className="flex-1 bg-gray-900 rounded-lg overflow-hidden relative">
              <PreviewCanvas
                config={config}
                playerState={playerState}
              />
              
              {/* Overlay de controles rápidos */}
              <div className="absolute bottom-4 left-4 right-4">
                <div className="bg-black bg-opacity-50 rounded-lg p-3">
                  <div className="flex items-center justify-between text-white text-sm mb-2">
                    <span>{Math.floor(playerState.currentTime)}s / {Math.floor(playerState.duration)}s</span>
                    <span>FPS: 30 | 1920x1080</span>
                  </div>
                  
                  {/* Scrubber avançado */}
                  <VideoScrubber
                    videoRef={videoRef}
                    duration={playerState.duration}
                    currentTime={playerState.currentTime}
                    onTimeChange={controls.seek}
                    onScrubStart={controls.pause}
                    onScrubEnd={controls.play}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Painel de controles */}
          <div className="w-96 bg-gray-50 rounded-lg flex flex-col overflow-hidden">
            {activeTab === 'preview' && (
              <div className="p-4 space-y-4 overflow-y-auto">
                <h3 className="font-medium">⚙️ Configurações de Preview</h3>
                
                {/* Controles básicos */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium">Duração da Cena</label>
                  <input
                    type="range"
                    min="1"
                    max="30"
                    step="0.5"
                    value={config.duration}
                    onChange={(e) => updateAudio({ ...config.audio })}
                    className="w-full"
                  />
                  <span className="text-sm text-gray-600">{config.duration}s</span>
                </div>

                {/* Elementos da cena */}
                <div>
                  <h4 className="font-medium mb-2">📋 Elementos</h4>
                  <div className="space-y-2">
                    {config.elements.map((element, index) => (
                      <div key={element.id} className="p-2 bg-white rounded border">
                        <div className="flex justify-between items-center">
                          <span className="text-sm">{element.type}</span>
                          <select
                            value={config.animations[element.id]?.type || 'fade'}
                            onChange={(e) => updateAnimation(element.id, {
                              ...config.animations[element.id],
                              type: e.target.value as any
                            })}
                            className="text-sm border rounded px-1"
                          >
                            <option value="fade">Fade</option>
                            <option value="slide">Slide</option>
                            <option value="zoom">Zoom</option>
                            <option value="none">Nenhuma</option>
                          </select>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'audio' && (
              <div className="flex-1 overflow-y-auto">
                <AudioControls
                  audioConfig={config.audio}
                  onUpdateAudio={updateAudio}
                  onRegenerateNarration={handleRegenerateNarration}
                  isRegenerating={isRegenerating}
                />
              </div>
            )}

            {activeTab === 'transitions' && (
              <div className="p-4 space-y-4 overflow-y-auto">
                <h3 className="font-medium">🔄 Transições</h3>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Tipo de Transição</label>
                  <select
                    value={config.transition}
                    onChange={(e) => updateTransition(e.target.value as TransitionType)}
                    className="w-full p-2 border rounded"
                  >
                    {transitionOptions.map(option => (
                      <option key={option} value={option}>
                        {option.charAt(0).toUpperCase() + option.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Preview da transição */}
                <div className="bg-white p-3 rounded border">
                  <h4 className="text-sm font-medium mb-2">Preview da Transição</h4>
                  <div className="h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded flex items-center justify-center text-white text-sm">
                    {config.transition}
                  </div>
                </div>
              </div>
            )}

            {/* Botões de ação */}
            <div className="p-4 border-t bg-white">
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  className="flex-1 py-2 px-4 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                >
                  💾 Salvar
                </button>
                <button
                  onClick={onClose}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Vídeo oculto para análise */}
        <video
          ref={videoRef}
          style={{ display: 'none' }}
          src={config.audio.narrationUrl}
          crossOrigin="anonymous"
        />
      </div>
    </div>
  );
};