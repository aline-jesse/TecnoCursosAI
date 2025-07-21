/**
 * VideoScrubber - Componente de Scrubber de Vídeo Avançado
 * TecnoCursos AI - Sistema de Preview
 * 
 * Inspirado no react-video-scrubber, este componente permite navegar
 * frame a frame pelo vídeo usando canvas para renderização otimizada.
 */
import React, { useRef, useEffect, useState, useCallback } from 'react';

interface VideoScrubberProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  duration: number;
  currentTime: number;
  onTimeChange: (time: number) => void;
  onScrubStart?: () => void;
  onScrubEnd?: () => void;
  frameRate?: number;
  thumbnailCount?: number;
}

export const VideoScrubber: React.FC<VideoScrubberProps> = ({
  videoRef,
  duration,
  currentTime,
  onTimeChange,
  onScrubStart,
  onScrubEnd,
  frameRate = 30,
  thumbnailCount = 10
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [thumbnails, setThumbnails] = useState<string[]>([]);

  // Gerar thumbnails do vídeo
  const generateThumbnails = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const thumbs: string[] = [];
    const interval = duration / thumbnailCount;

    for (let i = 0; i < thumbnailCount; i++) {
      const time = i * interval;
      
      // Aguardar vídeo carregar o frame específico
      await new Promise<void>((resolve) => {
        const handleSeeked = () => {
          video.removeEventListener('seeked', handleSeeked);
          
          // Desenhar frame no canvas
          canvas.width = 120;
          canvas.height = 68;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          // Converter para base64 e adicionar à lista
          thumbs.push(canvas.toDataURL('image/jpeg', 0.7));
          resolve();
        };
        
        video.addEventListener('seeked', handleSeeked);
        video.currentTime = time;
      });
    }

    setThumbnails(thumbs);
  }, [duration, thumbnailCount, videoRef]);

  // Gerar thumbnails quando vídeo carregar
  useEffect(() => {
    if (videoRef.current && duration > 0) {
      generateThumbnails();
    }
  }, [generateThumbnails, duration]);

  // Calcular posição do playhead
  const playheadPosition = (currentTime / duration) * 100;

  // Handler para click/drag na timeline
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!containerRef.current) return;

    setIsDragging(true);
    onScrubStart?.();

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = Math.max(0, Math.min(duration, percentage * duration));
    
    onTimeChange(newTime);
  }, [duration, onTimeChange, onScrubStart]);

  // Handler para movimento do mouse
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    const newTime = percentage * duration;
    
    onTimeChange(newTime);
  }, [isDragging, duration, onTimeChange]);

  // Handler para soltar o mouse
  const handleMouseUp = useCallback(() => {
    if (isDragging) {
      setIsDragging(false);
      onScrubEnd?.();
    }
  }, [isDragging, onScrubEnd]);

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
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-scrubber">
      {/* Timeline com thumbnails */}
      <div 
        ref={containerRef}
        className="scrubber-timeline"
        onMouseDown={handleMouseDown}
      >
        {/* Thumbnails de fundo */}
        <div className="thumbnails-container">
          {thumbnails.map((thumb, index) => (
            <div
              key={index}
              className="thumbnail-frame"
              style={{
                left: `${(index / (thumbnailCount - 1)) * 100}%`,
                backgroundImage: `url(${thumb})`
              }}
            />
          ))}
        </div>

        {/* Barra de progresso */}
        <div className="progress-track">
          <div 
            className="progress-fill"
            style={{ width: `${playheadPosition}%` }}
          />
        </div>

        {/* Playhead */}
        <div 
          className="playhead"
          style={{ left: `${playheadPosition}%` }}
        >
          <div className="playhead-handle" />
          <div className="time-tooltip">
            {formatTime(currentTime)}
          </div>
        </div>

        {/* Marcadores de tempo */}
        <div className="time-markers">
          {Array.from({ length: 11 }, (_, i) => {
            const time = (i / 10) * duration;
            return (
              <div
                key={i}
                className="time-marker"
                style={{ left: `${i * 10}%` }}
              >
                <div className="marker-line" />
                <span className="marker-label">{formatTime(time)}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Canvas oculto para gerar thumbnails */}
      <canvas
        ref={canvasRef}
        style={{ display: 'none' }}
      />

      {/* Controles de frame */}
      <div className="frame-controls">
        <button
          onClick={() => onTimeChange(Math.max(0, currentTime - 1/frameRate))}
          className="frame-btn"
          title="Frame anterior"
        >
          ⏮
        </button>
        <span className="frame-info">
          Frame: {Math.floor(currentTime * frameRate)}
        </span>
        <button
          onClick={() => onTimeChange(Math.min(duration, currentTime + 1/frameRate))}
          className="frame-btn"
          title="Próximo frame"
        >
          ⏭
        </button>
      </div>
    </div>
  );
}; 