/**
 * TimelineControls - Controles de Timeline e Tempo
 * TecnoCursos AI - Sistema de Preview
 * 
 * Componente para ajustar timing, duração e configurações
 * temporais da cena no sistema de preview.
 */
import React from 'react';
import { PreviewPlayerState } from '../types/preview';

interface TimelineControlsProps {
  playerState: PreviewPlayerState;
  controls: {
    play: () => void;
    pause: () => void;
    seek: (time: number) => void;
    setVolume: (volume: number) => void;
    toggleMute: () => void;
  };
}

export const TimelineControls: React.FC<TimelineControlsProps> = ({
  playerState,
  controls
}) => {
  // Formatar tempo para exibição (mm:ss)
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Controles de reprodução */}
      <div className="flex items-center gap-4">
        <button
          onClick={playerState.isPlaying ? controls.pause : controls.play}
          className="w-10 h-10 flex items-center justify-center bg-blue-500 text-white rounded-full hover:bg-blue-600"
        >
          {playerState.isPlaying ? (
            <span className="material-icons">pause</span>
          ) : (
            <span className="material-icons">play_arrow</span>
          )}
        </button>

        {/* Tempo atual / Duração */}
        <div className="text-sm font-mono">
          {formatTime(playerState.currentTime)} / {formatTime(playerState.duration)}
        </div>

        {/* Controle de volume */}
        <div className="flex items-center gap-2">
          <button
            onClick={controls.toggleMute}
            className="text-gray-600 hover:text-gray-800"
          >
            {playerState.isMuted ? (
              <span className="material-icons">volume_off</span>
            ) : (
              <span className="material-icons">volume_up</span>
            )}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={playerState.isMuted ? 0 : playerState.volume}
            onChange={(e) => controls.setVolume(parseFloat(e.target.value))}
            className="w-24"
          />
        </div>
      </div>

      {/* Timeline */}
      <div className="flex items-center gap-2">
        <input
          type="range"
          min="0"
          max={playerState.duration}
          step="0.1"
          value={playerState.currentTime}
          onChange={(e) => controls.seek(parseFloat(e.target.value))}
          className="flex-1"
        />
      </div>
    </div>
  );
};