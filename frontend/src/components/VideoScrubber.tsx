/**
 * VideoScrubber - Componente de Scrubber de Vídeo Avançado
 * TecnoCursos AI - Sistema de Preview
 *
 * Inspirado no react-video-scrubber, este componente permite navegar
 * frame a frame pelo vídeo usando canvas para renderização otimizada.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import './VideoScrubber.css';

interface Thumbnail {
  url: string;
  time: number;
}

interface VideoScrubberProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  duration: number;
  currentTime: number;
  onTimeChange: (time: number) => void;
  onScrubStart?: () => void;
  onScrubEnd?: () => void;
  frameRate?: number;
  thumbnailCount?: number;
  disabled?: boolean;
  ariaLabel?: string;
  className?: string;
}

interface TimeMarker {
  time: number;
  label: string;
  position: number;
}

export const VideoScrubber: React.FC<VideoScrubberProps> = ({
  videoRef,
  duration,
  currentTime,
  onTimeChange,
  onScrubStart,
  onScrubEnd,
  frameRate = 30,
  thumbnailCount = 10,
  disabled = false,
  ariaLabel = 'Controle de tempo do vídeo',
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [thumbnails, setThumbnails] = useState<Thumbnail[]>([]);
  const [isGeneratingThumbnails, setIsGeneratingThumbnails] = useState(false);

  // Gerar thumbnails do vídeo
  const generateThumbnails = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || isGeneratingThumbnails)
      return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    setIsGeneratingThumbnails(true);
    const thumbs: Thumbnail[] = [];
    const interval = duration / thumbnailCount;

    try {
      for (let i = 0; i < thumbnailCount; i++) {
        const time = i * interval;

        // Aguardar vídeo carregar o frame específico
        await new Promise<void>((resolve, reject) => {
          const handleSeeked = () => {
            video.removeEventListener('seeked', handleSeeked);
            video.removeEventListener('error', handleError);

            // Desenhar frame no canvas
            canvas.width = 120;
            canvas.height = 68;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Converter para base64 e adicionar à lista
            thumbs.push({
              url: canvas.toDataURL('image/jpeg', 0.7),
              time,
            });
            resolve();
          };

          const handleError = () => {
            video.removeEventListener('seeked', handleSeeked);
            video.removeEventListener('error', handleError);
            reject(new Error('Erro ao gerar thumbnail'));
          };

          video.addEventListener('seeked', handleSeeked);
          video.addEventListener('error', handleError);
          video.currentTime = time;
        });
      }

      setThumbnails(thumbs);
    } catch (error) {
      console.error('Erro ao gerar thumbnails:', error);
    } finally {
      setIsGeneratingThumbnails(false);
    }
  }, [duration, thumbnailCount, videoRef, isGeneratingThumbnails]);

  // Gerar thumbnails quando vídeo carregar
  useEffect(() => {
    if (videoRef.current && duration > 0) {
      generateThumbnails();
    }
  }, [generateThumbnails, duration]);

  // Calcular posição do playhead
  const playheadPosition = (currentTime / duration) * 100;

  // Handler para click/drag na timeline
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (!containerRef.current || disabled) return;

      setIsDragging(true);
      onScrubStart?.();

      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = x / rect.width;
      const newTime = Math.max(0, Math.min(duration, percentage * duration));

      onTimeChange(newTime);
    },
    [duration, onTimeChange, onScrubStart, disabled]
  );

  // Handler para movimento do mouse
  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !containerRef.current || disabled) return;

      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = Math.max(0, Math.min(1, x / rect.width));
      const newTime = percentage * duration;

      onTimeChange(newTime);
    },
    [isDragging, duration, onTimeChange, disabled]
  );

  // Handler para soltar o mouse
  const handleMouseUp = useCallback(() => {
    if (isDragging) {
      setIsDragging(false);
      onScrubEnd?.();
    }
  }, [isDragging, onScrubEnd]);

  // Handler para teclas
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (disabled) return;

      const step = e.shiftKey ? 10 : 1;
      let newTime = currentTime;

      switch (e.key) {
        case 'ArrowLeft':
          newTime = Math.max(0, currentTime - step);
          break;
        case 'ArrowRight':
          newTime = Math.min(duration, currentTime + step);
          break;
        case 'Home':
          newTime = 0;
          break;
        case 'End':
          newTime = duration;
          break;
        default:
          return;
      }

      e.preventDefault();
      onTimeChange(newTime);
    },
    [currentTime, duration, onTimeChange, disabled]
  );

  // Adicionar/remover event listeners
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  // Formatar tempo para exibição
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Gerar marcadores de tempo
  const timeMarkers = Array.from<unknown, TimeMarker>(
    { length: 11 },
    (_, i) => {
      const time = (i / 10) * duration;
      return {
        time,
        label: formatTime(time),
        position: i * 10,
      };
    }
  );

  return (
    <div className={`video-scrubber ${className}`}>
      {/* Timeline com thumbnails */}
      <div
        ref={containerRef}
        className={`scrubber-timeline ${disabled ? 'disabled' : ''}`}
        onMouseDown={handleMouseDown}
        onKeyDown={handleKeyDown}
        role="slider"
        aria-label={ariaLabel}
        aria-valuemin={0}
        aria-valuemax={duration}
        aria-valuenow={currentTime}
        aria-valuetext={`${formatTime(currentTime)} de ${formatTime(duration)}`}
        tabIndex={disabled ? -1 : 0}
      >
        {/* Thumbnails de fundo */}
        <div className="thumbnails-container">
          {thumbnails.map((thumb, index) => (
            <div
              key={index}
              className="thumbnail-frame"
              style={{
                left: `${(index / (thumbnailCount - 1)) * 100}%`,
                backgroundImage: `url(${thumb.url})`,
              }}
              role="presentation"
            />
          ))}
        </div>

        {/* Barra de progresso */}
        <div className="progress-track" role="presentation">
          <div
            className="progress-fill"
            style={{ width: `${playheadPosition}%` }}
          />
        </div>

        {/* Playhead */}
        <div
          className="playhead"
          style={{ left: `${playheadPosition}%` }}
          role="presentation"
        >
          <div className="playhead-handle" />
          <div className="time-tooltip" role="tooltip">
            {formatTime(currentTime)}
          </div>
        </div>

        {/* Marcadores de tempo */}
        <div className="time-markers" role="presentation">
          {timeMarkers.map(marker => (
            <div
              key={marker.position}
              className="time-marker"
              style={{ left: `${marker.position}%` }}
            >
              <div className="marker-line" />
              <span className="marker-label">{marker.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Canvas oculto para gerar thumbnails */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Controles de frame */}
      <div className="frame-controls">
        <button
          onClick={() => onTimeChange(Math.max(0, currentTime - 1 / frameRate))}
          className="frame-btn"
          title="Frame anterior"
          disabled={disabled || currentTime <= 0}
          aria-label="Frame anterior"
        >
          ⏮
        </button>
        <span className="frame-info" role="status">
          Frame: {Math.floor(currentTime * frameRate)}
        </span>
        <button
          onClick={() =>
            onTimeChange(Math.min(duration, currentTime + 1 / frameRate))
          }
          className="frame-btn"
          title="Próximo frame"
          disabled={disabled || currentTime >= duration}
          aria-label="Próximo frame"
        >
          ⏭
        </button>
      </div>
    </div>
  );
};
