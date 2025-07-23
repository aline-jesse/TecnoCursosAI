/**
 * TimelineControls - Controles de Timeline e Tempo
 * TecnoCursos AI - Sistema de Preview
 *
 * Componente para ajustar timing, duração e configurações
 * temporais da cena no sistema de preview.
 */
import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  TimelineControlsProps,
  TimelineMarker,
  PreviewPlayerState,
} from '../types/preview';
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  ForwardIcon,
  BackwardIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

const TimelineControls: React.FC<TimelineControlsProps> = ({
  config,
  playerState,
  onTimeChange,
  onSpeedChange,
  onMarkerAdd,
  onMarkerRemove,
  onSceneSelect,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartX, setDragStartX] = useState(0);
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);
  const [showMarkerDialog, setShowMarkerDialog] = useState(false);
  const [newMarkerTime, setNewMarkerTime] = useState(0);
  const [newMarkerLabel, setNewMarkerLabel] = useState('');

  const timelineRef = useRef<HTMLDivElement>(null);
  const waveformCanvasRef = useRef<HTMLCanvasElement>(null);

  // Opções de velocidade de reprodução
  const speedOptions = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2];

  /**
   * Calcular posição X na timeline baseado no tempo
   */
  const getTimelinePosition = useCallback(
    (time: number): number => {
      if (!timelineRef.current) return 0;
      const timelineWidth = timelineRef.current.offsetWidth;
      return (time / config.duration) * timelineWidth;
    },
    [config.duration]
  );

  /**
   * Calcular tempo baseado na posição X na timeline
   */
  const getTimeFromPosition = useCallback(
    (x: number): number => {
      if (!timelineRef.current) return 0;
      const timelineWidth = timelineRef.current.offsetWidth;
      const ratio = x / timelineWidth;
      return Math.max(0, Math.min(config.duration, ratio * config.duration));
    },
    [config.duration]
  );

  /**
   * Formatar tempo para exibição (MM:SS)
   */
  const formatTime = useCallback((seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  /**
   * Lidar com clique na timeline
   */
  const handleTimelineClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!timelineRef.current) return;

      const rect = timelineRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const newTime = getTimeFromPosition(x);
      onTimeChange(newTime);
    },
    [getTimeFromPosition, onTimeChange]
  );

  /**
   * Iniciar arrastar na timeline
   */
  const handleMouseDown = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      setIsDragging(true);
      setDragStartX(e.clientX);
      handleTimelineClick(e);
    },
    [handleTimelineClick]
  );

  /**
   * Arrastar na timeline
   */
  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!isDragging || !timelineRef.current) return;

      const rect = timelineRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const newTime = getTimeFromPosition(x);
      onTimeChange(newTime);
    },
    [isDragging, getTimeFromPosition, onTimeChange]
  );

  /**
   * Finalizar arrastar
   */
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  /**
   * Sair da timeline
   */
  const handleMouseLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  /**
   * Adicionar marcador duplo clique
   */
  const handleDoubleClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!timelineRef.current) return;

      const rect = timelineRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const time = getTimeFromPosition(x);

      setNewMarkerTime(time);
      setNewMarkerLabel(`Marcador ${config.markers.length + 1}`);
      setShowMarkerDialog(true);
    },
    [getTimeFromPosition, config.markers.length]
  );

  /**
   * Confirmar adição de marcador
   */
  const handleAddMarker = useCallback(() => {
    if (newMarkerLabel.trim()) {
      onMarkerAdd?.(newMarkerTime, newMarkerLabel.trim());
      setShowMarkerDialog(false);
      setNewMarkerLabel('');
    }
  }, [newMarkerLabel, newMarkerTime, onMarkerAdd]);

  /**
   * Cancelar adição de marcador
   */
  const handleCancelMarker = useCallback(() => {
    setShowMarkerDialog(false);
    setNewMarkerLabel('');
  }, []);

  /**
   * Renderizar waveform de áudio (se disponível)
   */
  const renderWaveform = useCallback(
    (
      canvas: HTMLCanvasElement,
      waveformData: number[],
      width: number,
      height: number
    ) => {
      const ctx = canvas.getContext('2d');
      if (!ctx || !waveformData.length) return;

      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = '#3b82f6';

      const barWidth = width / waveformData.length;
      const centerY = height / 2;

      waveformData.forEach((value, index) => {
        const barHeight = Math.abs(value) * centerY;
        const x = index * barWidth;
        const y = centerY - barHeight / 2;

        ctx.fillRect(x, y, Math.max(1, barWidth - 1), barHeight);
      });
    },
    []
  );

  // Efeito para renderizar waveform quando dados de áudio estão disponíveis
  useEffect(() => {
    if (
      config.audio &&
      config.audio.waveformData &&
      waveformCanvasRef.current
    ) {
      renderWaveform(
        waveformCanvasRef.current,
        config.audio.waveformData,
        400,
        40
      );
    }
  }, [config.audio, renderWaveform]);

  return (
    <div className='timeline-controls'>
      {/* Cabeçalho com informações de tempo */}
      <div className='timeline-header'>
        <div className='time-display'>
          <span className='current-time'>{formatTime(config.currentTime)}</span>
          <span className='separator'>/</span>
          <span className='total-time'>{formatTime(config.duration)}</span>
        </div>

        <div className='playback-speed'>
          <button
            onClick={() => setShowSpeedMenu(!showSpeedMenu)}
            className='speed-button'
          >
            {config.playbackSpeed}x{' '}
            <Cog6ToothIcon style={{ width: '1rem', height: '1rem' }} />
          </button>

          {showSpeedMenu && (
            <div className='speed-menu'>
              {speedOptions.map(speed => (
                <button
                  key={speed}
                  onClick={() => {
                    onSpeedChange(speed);
                    setShowSpeedMenu(false);
                  }}
                  className={`speed-option ${config.playbackSpeed === speed ? 'active' : ''}`}
                >
                  {speed}x
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Timeline principal */}
      <div className='timeline-container'>
        <div
          ref={timelineRef}
          className='timeline-track'
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove as any}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseLeave}
          onDoubleClick={handleDoubleClick}
        >
          {/* Fundo da timeline */}
          <div className='timeline-background' />

          {/* Barra de progresso */}
          <div
            className='timeline-progress'
            style={{
              width: `${(config.currentTime / config.duration) * 100}%`,
            }}
          />

          {/* Indicador de posição atual */}
          <div
            className='timeline-cursor'
            style={{
              left: `${(config.currentTime / config.duration) * 100}%`,
            }}
          />

          {/* Marcadores */}
          {config.markers.map(marker => (
            <div
              key={marker.id}
              className='timeline-marker'
              style={{
                left: `${(marker.time / config.duration) * 100}%`,
                backgroundColor: marker.color || '#f59e0b',
              }}
              title={`${marker.label} - ${formatTime(marker.time)}`}
              onClick={e => {
                e.stopPropagation();
                onTimeChange(marker.time);
              }}
              onContextMenu={e => {
                e.preventDefault();
                onMarkerRemove?.(marker.id);
              }}
            >
              <div className='marker-label'>{marker.label}</div>
            </div>
          ))}
        </div>

        {/* Escala de tempo */}
        <div className='timeline-scale'>
          {Array.from(
            { length: Math.ceil(config.duration / 10) + 1 },
            (_, i) => {
              const time = i * 10;
              if (time > config.duration) return null;

              return (
                <div
                  key={i}
                  className='scale-mark'
                  style={{
                    left: `${(time / config.duration) * 100}%`,
                  }}
                >
                  <div className='scale-line' />
                  <div className='scale-label'>{formatTime(time)}</div>
                </div>
              );
            }
          )}
        </div>
      </div>

      {/* Waveform de áudio (se disponível) */}
      {config.audio && config.audio.waveformData && (
        <div className='waveform-container'>
          <canvas
            ref={waveformCanvasRef}
            width={400}
            height={40}
            style={{ width: '100%', height: 40 }}
          />
        </div>
      )}

      {/* Controles de navegação entre cenas */}
      <div className='scene-navigation'>
        <h4>Navegação de Cenas</h4>
        <div className='scene-buttons'>
          <button
            onClick={() =>
              onSceneSelect?.(
                Math.max(0, (playerState.currentSceneIndex ?? 0) - 1)
              )
            }
            disabled={(playerState.currentSceneIndex ?? 0) === 0}
            className='nav-button'
          >
            <BackwardIcon style={{ width: '1rem', height: '1rem' }} />
            Anterior
          </button>

          <span className='scene-indicator'>
            Cena {(playerState.currentSceneIndex ?? 0) + 1}
          </span>

          <button
            onClick={() =>
              onSceneSelect?.((playerState.currentSceneIndex ?? 0) + 1)
            }
            className='nav-button'
          >
            Próxima
            <ForwardIcon style={{ width: '1rem', height: '1rem' }} />
          </button>
        </div>
      </div>

      {/* Dialog para adicionar marcador */}
      {showMarkerDialog && (
        <div className='marker-dialog-overlay'>
          <div className='marker-dialog'>
            <h3>Adicionar Marcador</h3>
            <div className='dialog-content'>
              <label>Tempo: {formatTime(newMarkerTime)}</label>
              <label>
                Nome do Marcador:
                <input
                  type='text'
                  value={newMarkerLabel}
                  onChange={e => setNewMarkerLabel(e.target.value)}
                  placeholder='Digite o nome do marcador'
                  autoFocus
                />
              </label>
            </div>
            <div className='dialog-actions'>
              <button onClick={handleCancelMarker} className='cancel-button'>
                Cancelar
              </button>
              <button onClick={handleAddMarker} className='confirm-button'>
                Adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimelineControls;
