/**
 * AudioControls - Controles Avançados de Áudio
 * TecnoCursos AI - Sistema de Preview
 *
 * Inspirado no react-modal-video, este componente oferece controles
 * completos de áudio incluindo equalizer, narração e música de fundo.
 */
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { AudioConfig } from '../types/preview';
import './AudioControls.css';

interface AudioControlsProps {
  audioConfig: AudioConfig;
  onUpdateAudio: (updates: Partial<AudioConfig>) => void;
  onRegenerateNarration: () => Promise<void>;
  isRegenerating?: boolean;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  audioConfig,
  onUpdateAudio,
  onRegenerateNarration,
  isRegenerating = false,
}) => {
  // Estados locais
  const [showEqualizer, setShowEqualizer] = useState(false);
  const [voiceSettings, setVoiceSettings] = useState({
    speed: 1.0,
    pitch: 0,
    emphasis: 'medium' as 'low' | 'medium' | 'high',
    voice: 'female' as 'male' | 'female' | 'neutral',
  });
  const [audioAnalyzer, setAudioAnalyzer] = useState<AnalyserNode | null>(null);
  const [frequencyData, setFrequencyData] = useState<Uint8Array | null>(null);

  // Referências
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  // Configurar analisador de áudio
  useEffect(() => {
    if (audioConfig.narrationUrl) {
      const audio = new Audio(audioConfig.narrationUrl);
      const audioContext = new (window.AudioContext ||
        (window as any).webkitAudioContext)();
      const source = audioContext.createMediaElementSource(audio);
      const analyzer = audioContext.createAnalyser();

      analyzer.fftSize = 256;
      source.connect(analyzer);
      analyzer.connect(audioContext.destination);

      setAudioAnalyzer(analyzer);
      setFrequencyData(new Uint8Array(analyzer.frequencyBinCount));
    }
  }, [audioConfig.narrationUrl]);

  // Animação do visualizador
  const drawAudioVisualizer = useCallback(() => {
    if (!canvasRef.current || !audioAnalyzer || !frequencyData) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    audioAnalyzer.getByteFrequencyData(frequencyData);

    // Limpar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Desenhar barras de frequência
    const barWidth = canvas.width / frequencyData.length;
    for (let i = 0; i < frequencyData.length; i++) {
      const barHeight = (frequencyData[i] / 255) * canvas.height;
      const hue = (i / frequencyData.length) * 360;

      ctx.fillStyle = `hsla(${hue}, 70%, 50%, 0.8)`;
      ctx.fillRect(
        i * barWidth,
        canvas.height - barHeight,
        barWidth - 1,
        barHeight
      );
    }

    animationFrameRef.current = requestAnimationFrame(drawAudioVisualizer);
  }, [audioAnalyzer, frequencyData]);

  useEffect(() => {
    if (showEqualizer && audioAnalyzer) {
      drawAudioVisualizer();
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [showEqualizer, drawAudioVisualizer, audioAnalyzer]);

  // Handlers
  const handleVolumeChange = useCallback(
    (type: 'narration' | 'music', value: number) => {
      if (type === 'narration') {
        onUpdateAudio({ narrationVolume: value });
      } else {
        onUpdateAudio({ musicVolume: value });
      }
    },
    [onUpdateAudio]
  );

  const handleVoiceSettingsChange = useCallback(
    (setting: string, value: any) => {
      setVoiceSettings(prev => ({ ...prev, [setting]: value }));
    },
    []
  );

  const handleRegenerateWithSettings = useCallback(async () => {
    // Aqui você pode usar os voiceSettings para personalizar a regeneração
    await onRegenerateNarration();
  }, [onRegenerateNarration]);

  return (
    <div className='audio-controls'>
      {/* Cabeçalho */}
      <div className='audio-header'>
        <h3>🎵 Controles de Áudio</h3>
        <button
          onClick={() => setShowEqualizer(!showEqualizer)}
          className={`equalizer-toggle ${showEqualizer ? 'active' : ''}`}
        >
          📊 Equalizer
        </button>
      </div>

      {/* Visualizador de áudio */}
      {showEqualizer && (
        <div className='audio-visualizer'>
          <canvas
            ref={canvasRef}
            width={300}
            height={80}
            className='visualizer-canvas'
          />
        </div>
      )}

      {/* Controles de volume */}
      <div className='volume-section'>
        <div className='volume-control'>
          <label>🎤 Narração</label>
          <div className='volume-slider-container'>
            <input
              type='range'
              min='0'
              max='1'
              step='0.05'
              value={audioConfig.narrationVolume}
              onChange={e =>
                handleVolumeChange('narration', parseFloat(e.target.value))
              }
              className='volume-slider'
            />
            <span className='volume-value'>
              {Math.round(audioConfig.narrationVolume * 100)}%
            </span>
          </div>
        </div>

        <div className='volume-control'>
          <label>🎶 Música de Fundo</label>
          <div className='volume-slider-container'>
            <input
              type='range'
              min='0'
              max='1'
              step='0.05'
              value={audioConfig.musicVolume}
              onChange={e =>
                handleVolumeChange('music', parseFloat(e.target.value))
              }
              className='volume-slider'
            />
            <span className='volume-value'>
              {Math.round(audioConfig.musicVolume * 100)}%
            </span>
          </div>
        </div>
      </div>

      {/* Configurações de voz */}
      <div className='voice-settings'>
        <h4>🗣️ Configurações de Voz</h4>

        <div className='voice-setting'>
          <label>Tipo de Voz:</label>
          <select
            value={voiceSettings.voice}
            onChange={e => handleVoiceSettingsChange('voice', e.target.value)}
            className='voice-select'
          >
            <option value='female'>Feminina</option>
            <option value='male'>Masculina</option>
            <option value='neutral'>Neutra</option>
          </select>
        </div>

        <div className='voice-setting'>
          <label>Velocidade:</label>
          <div className='speed-control'>
            <input
              type='range'
              min='0.5'
              max='2.0'
              step='0.1'
              value={voiceSettings.speed}
              onChange={e =>
                handleVoiceSettingsChange('speed', parseFloat(e.target.value))
              }
              className='speed-slider'
            />
            <span>{voiceSettings.speed}x</span>
          </div>
        </div>

        <div className='voice-setting'>
          <label>Tom:</label>
          <div className='pitch-control'>
            <input
              type='range'
              min='-10'
              max='10'
              step='1'
              value={voiceSettings.pitch}
              onChange={e =>
                handleVoiceSettingsChange('pitch', parseInt(e.target.value))
              }
              className='pitch-slider'
            />
            <span>
              {voiceSettings.pitch > 0 ? '+' : ''}
              {voiceSettings.pitch}
            </span>
          </div>
        </div>

        <div className='voice-setting'>
          <label>Ênfase:</label>
          <div className='emphasis-buttons'>
            {['low', 'medium', 'high'].map(level => (
              <button
                key={level}
                onClick={() => handleVoiceSettingsChange('emphasis', level)}
                className={`emphasis-btn ${voiceSettings.emphasis === level ? 'active' : ''}`}
              >
                {level === 'low'
                  ? 'Baixa'
                  : level === 'medium'
                    ? 'Média'
                    : 'Alta'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Botão de regenerar narração */}
      <div className='regeneration-section'>
        <button
          onClick={handleRegenerateWithSettings}
          disabled={isRegenerating}
          className={`regenerate-btn ${isRegenerating ? 'loading' : ''}`}
        >
          {isRegenerating ? (
            <>
              <div className='spinner' />
              Gerando...
            </>
          ) : (
            <>🔄 Regenerar Narração IA</>
          )}
        </button>

        {audioConfig.needsRegeneration && (
          <div className='regeneration-warning'>
            ⚠️ O texto foi modificado. Recomendamos regenerar a narração.
          </div>
        )}
      </div>

      {/* Presets de áudio */}
      <div className='audio-presets'>
        <h4>🎯 Presets Rápidos</h4>
        <div className='preset-buttons'>
          <button
            onClick={() => {
              onUpdateAudio({ narrationVolume: 1, musicVolume: 0.2 });
              setVoiceSettings({
                speed: 1.0,
                pitch: 0,
                emphasis: 'medium',
                voice: 'female',
              });
            }}
            className='preset-btn'
          >
            🎓 Educacional
          </button>
          <button
            onClick={() => {
              onUpdateAudio({ narrationVolume: 0.9, musicVolume: 0.4 });
              setVoiceSettings({
                speed: 1.1,
                pitch: 2,
                emphasis: 'high',
                voice: 'male',
              });
            }}
            className='preset-btn'
          >
            💼 Corporativo
          </button>
          <button
            onClick={() => {
              onUpdateAudio({ narrationVolume: 0.8, musicVolume: 0.6 });
              setVoiceSettings({
                speed: 0.9,
                pitch: -1,
                emphasis: 'low',
                voice: 'neutral',
              });
            }}
            className='preset-btn'
          >
            🎵 Musical
          </button>
        </div>
      </div>
    </div>
  );
};
