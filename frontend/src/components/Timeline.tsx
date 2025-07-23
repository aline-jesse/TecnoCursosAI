// src/components/Timeline.tsx
import React, { useState, useCallback } from 'react';
import { useEditorStore } from '../store/editorStore';
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  BackwardIcon,
  ForwardIcon,
  SpeakerWaveIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';
import './Timeline.css';

/**
 * Timeline: Exibe as cenas em uma linha do tempo horizontal.
 *
 * Funcionalidades:
 * - Renderiza blocos para cada cena com duração proporcional
 * - Controles de reprodução (play, pause, stop, next, previous)
 * - Indicador de tempo atual
 * - Controles de volume e configurações
 * - Destaca a cena atualmente selecionada
 * - Permite clicar em uma cena para selecioná-la
 */
const Timeline: React.FC = () => {
  const { history, currentSceneId, setCurrentSceneId, updateScene } =
    useEditorStore();
  const scenes = history.present;

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showAudio, setShowAudio] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  // Calcular duração total
  const totalDuration = scenes.reduce(
    (total, scene) => total + scene.duration,
    0
  );

  // Calcular tempo atual baseado na cena selecionada
  const getCurrentTimeInTimeline = useCallback(() => {
    if (!currentSceneId) return 0;

    const currentSceneIndex = scenes.findIndex(
      scene => scene.id === currentSceneId
    );
    if (currentSceneIndex === -1) return 0;

    return scenes
      .slice(0, currentSceneIndex)
      .reduce((total, scene) => total + scene.duration, 0);
  }, [scenes, currentSceneId]);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _getCurrentTimeInTimeline = getCurrentTimeInTimeline;

  // Controles de reprodução
  const handlePlay = useCallback(() => {
    setIsPlaying(true);
    // TODO: Implementar reprodução real
  }, []);

  const handlePause = useCallback(() => {
    setIsPlaying(false);
    // TODO: Implementar pausa real
  }, []);

  const handleStop = useCallback(() => {
    setIsPlaying(false);
    setCurrentTime(0);
    // TODO: Implementar parada real
  }, []);

  const handlePrevious = useCallback(() => {
    const currentIndex = scenes.findIndex(scene => scene.id === currentSceneId);
    if (currentIndex > 0) {
      setCurrentSceneId(scenes[currentIndex - 1].id);
    }
  }, [scenes, currentSceneId, setCurrentSceneId]);

  const handleNext = useCallback(() => {
    const currentIndex = scenes.findIndex(scene => scene.id === currentSceneId);
    if (currentIndex < scenes.length - 1) {
      setCurrentSceneId(scenes[currentIndex + 1].id);
    }
  }, [scenes, currentSceneId, setCurrentSceneId]);

  // Formatar tempo
  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  // Calcular posição do bloco baseado na duração
  const getBlockWidth = useCallback(
    (duration: number) => {
      const totalWidth = 100; // 100% do container
      return (duration / totalDuration) * totalWidth;
    },
    [totalDuration]
  );

  // Calcular posição do bloco baseado no tempo acumulado
  const getBlockPosition = useCallback(
    (sceneIndex: number) => {
      const previousScenesDuration = scenes
        .slice(0, sceneIndex)
        .reduce((total, scene) => total + scene.duration, 0);
      return (previousScenesDuration / totalDuration) * 100;
    },
    [scenes, totalDuration]
  );

  // Editar duração da cena
  const handleDurationChange = useCallback(
    (sceneId: string, newDuration: number) => {
      if (newDuration >= 1 && newDuration <= 60) {
        const scene = scenes.find(s => s.id === sceneId);
        if (scene) {
          updateScene({ ...scene, duration: newDuration });
        }
      }
    },
    [updateScene, scenes]
  );

  return (
    <div className='timeline-container'>
      {/* Controles de reprodução */}
      <div className='timeline-controls'>
        <div className='playback-controls'>
          <button
            className='control-btn'
            onClick={handlePrevious}
            disabled={!currentSceneId}
            title='Cena anterior'
          >
            <BackwardIcon className='w-4 h-4' />
          </button>

          <button
            className='control-btn primary'
            onClick={isPlaying ? handlePause : handlePlay}
            title={isPlaying ? 'Pausar' : 'Reproduzir'}
          >
            {isPlaying ? (
              <PauseIcon className='w-5 h-5' />
            ) : (
              <PlayIcon className='w-5 h-5' />
            )}
          </button>

          <button className='control-btn' onClick={handleStop} title='Parar'>
            <StopIcon className='w-4 h-4' />
          </button>

          <button
            className='control-btn'
            onClick={handleNext}
            disabled={!currentSceneId}
            title='Próxima cena'
          >
            <ForwardIcon className='w-4 h-4' />
          </button>
        </div>

        {/* Indicador de tempo */}
        <div className='time-display'>
          <span className='current-time'>{formatTime(currentTime)}</span>
          <span className='time-separator'>/</span>
          <span className='total-time'>{formatTime(totalDuration)}</span>
        </div>

        {/* Controles adicionais */}
        <div className='additional-controls'>
          <button
            className={`control-btn ${showAudio ? 'active' : ''}`}
            onClick={() => setShowAudio(!showAudio)}
            title={showAudio ? 'Ocultar áudio' : 'Mostrar áudio'}
          >
            <SpeakerWaveIcon className='w-4 h-4' />
          </button>

          <button
            className={`control-btn ${showSettings ? 'active' : ''}`}
            onClick={() => setShowSettings(!showSettings)}
            title='Configurações'
          >
            <Cog6ToothIcon className='w-4 h-4' />
          </button>
        </div>
      </div>

      {/* Timeline principal */}
      <div className='timeline-main'>
        <div className='timeline-track'>
          {/* Blocos das cenas */}
          {scenes.map((scene, index) => (
            <div
              key={scene.id}
              className={`timeline-block ${scene.id === currentSceneId ? 'active' : ''}`}
              style={{
                width: `${getBlockWidth(scene.duration)}%`,
                left: `${getBlockPosition(index)}%`,
              }}
              onClick={() => setCurrentSceneId(scene.id)}
              title={`${scene.name} (${scene.duration}s)`}
            >
              <div className='block-header'>
                <span className='block-title'>{scene.name}</span>
                <span className='block-duration'>{scene.duration}s</span>
              </div>

              <div className='block-content'>
                {scene.thumbnail && (
                  <img
                    src={scene.thumbnail}
                    alt={scene.name}
                    className='block-thumbnail'
                  />
                )}

                <div className='block-info'>
                  <span className='element-count'>
                    {scene.elements.length} elementos
                  </span>
                </div>
              </div>

              {/* Controle de duração inline */}
              <div className='duration-control'>
                <input
                  type='number'
                  min='1'
                  max='60'
                  value={scene.duration}
                  onChange={e =>
                    handleDurationChange(
                      scene.id,
                      parseInt(e.target.value) || 1
                    )
                  }
                  className='duration-input'
                  onClick={e => e.stopPropagation()}
                />
                <span className='duration-unit'>s</span>
              </div>
            </div>
          ))}

          {/* Indicador de tempo atual */}
          <div
            className='time-indicator'
            style={{
              left: `${(currentTime / totalDuration) * 100}%`,
            }}
          />
        </div>

        {/* Faixa de áudio (se habilitada) */}
        {showAudio && (
          <div className='audio-track'>
            <div className='audio-track-label'>
              <SpeakerWaveIcon className='w-3 h-3' />
              <span>Áudio</span>
            </div>
            <div className='audio-track-content'>
              {/* TODO: Implementar visualização de áudio */}
              <div className='audio-waveform'>
                {Array.from({ length: 20 }, (_, i) => (
                  <div
                    key={i}
                    className='audio-bar'
                    style={{
                      height: `${Math.random() * 60 + 20}%`,
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Configurações (se habilitadas) */}
      {showSettings && (
        <div className='timeline-settings'>
          <div className='setting-group'>
            <label htmlFor='volume'>Volume:</label>
            <input
              id='volume'
              type='range'
              min='0'
              max='1'
              step='0.1'
              value={volume}
              onChange={e => setVolume(parseFloat(e.target.value))}
              className='volume-slider'
            />
            <span className='volume-value'>{Math.round(volume * 100)}%</span>
          </div>

          <div className='setting-group'>
            <label htmlFor='playback-speed'>Velocidade:</label>
            <select
              id='playback-speed'
              className='speed-select'
              defaultValue='1'
            >
              <option value='0.5'>0.5x</option>
              <option value='0.75'>0.75x</option>
              <option value='1'>1x</option>
              <option value='1.25'>1.25x</option>
              <option value='1.5'>1.5x</option>
              <option value='2'>2x</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default Timeline;
