/**
 * Hook useVideoPreview - Gerenciamento do Sistema de Preview
 * TecnoCursos AI - Sistema de Preview Avançado
 * 
 * Este hook gerencia todo o estado e lógica do sistema de preview,
 * incluindo controles de reprodução, animações, transições e áudio.
 */
import { useState, useCallback, useEffect, useRef } from 'react';
import { useStore } from '../store/editorStore';
import { 
  PreviewPlayerState, 
  ScenePreviewConfig, 
  AnimationConfig, 
  AudioConfig 
} from '../types/preview';

export const useVideoPreview = (sceneId: string) => {
  // Estados do player
  const [playerState, setPlayerState] = useState<PreviewPlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 1,
    isMuted: false
  });

  // Referência para o elemento de áudio
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  // Estado da configuração da cena
  const [config, setConfig] = useState<ScenePreviewConfig>({
    id: sceneId,
    duration: 0,
    transition: 'fade',
    animations: {},
    audio: {
      narrationVolume: 1,
      musicVolume: 0.3
    },
    elements: []
  });

  // Busca dados da cena do store global
  const scene = useStore(state => state.scenes.find(s => s.id === sceneId));

  // Inicializa configuração quando a cena muda
  useEffect(() => {
    if (scene) {
      setConfig(prevConfig => ({
        ...prevConfig,
        duration: scene.duration || 5,
        elements: scene.elements.map(elem => ({
          id: elem.id,
          type: elem.type,
          animation: {
            type: 'fade',
            duration: 1,
            delay: 0,
            easing: 'ease-in-out'
          }
        }))
      }));
    }
  }, [scene]);

  // Controles de reprodução
  const play = useCallback(() => {
    setPlayerState(prev => ({ ...prev, isPlaying: true }));
    audioRef.current?.play();
  }, []);

  const pause = useCallback(() => {
    setPlayerState(prev => ({ ...prev, isPlaying: false }));
    audioRef.current?.pause();
  }, []);

  const seek = useCallback((time: number) => {
    setPlayerState(prev => ({ ...prev, currentTime: time }));
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  }, []);

  // Controles de áudio
  const setVolume = useCallback((volume: number) => {
    setPlayerState(prev => ({ ...prev, volume }));
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, []);

  const toggleMute = useCallback(() => {
    setPlayerState(prev => {
      const isMuted = !prev.isMuted;
      if (audioRef.current) {
        audioRef.current.muted = isMuted;
      }
      return { ...prev, isMuted };
    });
  }, []);

  // Atualização de configurações
  const updateAnimation = useCallback((elementId: string, animation: AnimationConfig) => {
    setConfig(prev => ({
      ...prev,
      animations: {
        ...prev.animations,
        [elementId]: animation
      }
    }));
  }, []);

  const updateTransition = useCallback((type: TransitionType) => {
    setConfig(prev => ({
      ...prev,
      transition: type
    }));
  }, []);

  const updateAudio = useCallback((audio: Partial<AudioConfig>) => {
    setConfig(prev => ({
      ...prev,
      audio: {
        ...prev.audio,
        ...audio
      }
    }));
  }, []);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      audioRef.current?.pause();
    };
  }, []);

  return {
    playerState,
    config,
    controls: {
      play,
      pause,
      seek,
      setVolume,
      toggleMute
    },
    updateAnimation,
    updateTransition,
    updateAudio
  };
};