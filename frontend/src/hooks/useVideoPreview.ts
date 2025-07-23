/**
 * Hook useVideoPreview - Gerenciamento do Sistema de Preview
 * TecnoCursos AI - Sistema de Preview Avançado
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import {
  PreviewState,
  PreviewActions,
  PreviewEvents,
  PreviewQuality,
  PreviewPlayerState,
  Marker,
  VideoPreviewOptions,
} from '../types/preview';
import { Scene } from '../types/editor';

/**
 * Função para criar o estado inicial do preview.
 */
const createInitialState = (
  options: VideoPreviewOptions = {}
): PreviewState => {
  const {
    initialScenes = [],
    initialSceneIndex = 0,
    initialTime = 0,
    autoplay = false,
    loop = false,
    volume = 1,
    quality = 'high',
  } = options;

  const totalDuration = initialScenes.reduce(
    (acc, scene) => acc + scene.duration,
    0
  );

  const markers: Marker[] = [];
  let currentTime = 0;
  initialScenes.forEach((scene, index) => {
    markers.push({
      id: `scene-marker-${scene.id}`,
      time: currentTime,
      label: scene.name || `Cena ${index + 1}`,
      type: 'scene',
      color: '#3b82f6',
    });
    currentTime += scene.duration;
  });

  return {
    scenes: initialScenes,
    currentSceneIndex: initialSceneIndex,
    playerState: autoplay ? 'playing' : 'idle',
    timeline: {
      duration: totalDuration,
      currentTime: initialTime,
      isPlaying: autoplay,
      playbackSpeed: 1,
      loop,
      markers,
    },
    volume,
    muted: volume === 0,
    quality,
    isFullscreen: false,
  };
};

/**
 * Hook principal para gerenciar o sistema de preview de vídeo/cena
 */
export const useVideoPreview = (
  options: VideoPreviewOptions = {}
): {
  state: PreviewState;
  actions: PreviewActions;
  events: PreviewEvents;
} => {
  const [state, setState] = useState<PreviewState>(() =>
    createInitialState(options)
  );

  const playIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const timeUpdateCallbacksRef = useRef<Set<(time: number) => void>>(new Set());
  const sceneChangeCallbacksRef = useRef<Set<(sceneIndex: number) => void>>(
    new Set()
  );
  const stateChangeCallbacksRef = useRef<
    Set<(state: PreviewPlayerState) => void>
  >(new Set());
  const readyCallbacksRef = useRef<Set<() => void>>(new Set());
  const errorCallbacksRef = useRef<Set<(error: string) => void>>(new Set());

  const updatePlayerState = useCallback((newState: PreviewPlayerState) => {
    setState(prev => {
      if (prev.playerState === newState) return prev;
      stateChangeCallbacksRef.current.forEach(cb => cb(newState));
      return { ...prev, playerState: newState };
    });
  }, []);

  const updateCurrentTime = useCallback((time: number) => {
    setState(prev => {
      // Evita re-renders desnecessários
      if (Math.abs(prev.timeline.currentTime - time) < 0.01) return prev;
      timeUpdateCallbacksRef.current.forEach(cb => cb(time));
      return { ...prev, timeline: { ...prev.timeline, currentTime: time } };
    });
  }, []);

  const checkSceneChange = useCallback(
    (currentTime: number, scenes: Scene[]) => {
      let accumulatedTime = 0;
      let newSceneIndex = -1;

      for (let i = 0; i < scenes.length; i++) {
        accumulatedTime += scenes[i].duration;
        if (currentTime < accumulatedTime) {
          newSceneIndex = i;
          break;
        }
      }
      // Caso esteja exatamente no final
      if (
        newSceneIndex === -1 &&
        currentTime >= state.timeline.duration - 0.01
      ) {
        newSceneIndex = scenes.length - 1;
      }

      setState(prev => {
        if (prev.currentSceneIndex !== newSceneIndex && newSceneIndex !== -1) {
          sceneChangeCallbacksRef.current.forEach(cb => cb(newSceneIndex));
          return { ...prev, currentSceneIndex: newSceneIndex };
        }
        return prev;
      });
    },
    [state.timeline.duration]
  );

  const play = useCallback(() => {
    if (state.playerState === 'playing' || state.scenes.length === 0) return;

    updatePlayerState('playing');
    setState(prev => ({
      ...prev,
      timeline: { ...prev.timeline, isPlaying: true },
    }));

    playIntervalRef.current = setInterval(() => {
      setState(prev => {
        if (!prev.timeline.isPlaying) return prev;

        const nextTime =
          prev.timeline.currentTime + 0.1 * prev.timeline.playbackSpeed;

        if (nextTime >= prev.timeline.duration) {
          if (prev.timeline.loop) {
            const newTime = 0;
            updateCurrentTime(newTime);
            checkSceneChange(newTime, prev.scenes);
            return {
              ...prev,
              timeline: { ...prev.timeline, currentTime: newTime },
            };
          } else {
            updatePlayerState('idle');
            // Garante que o tempo não ultrapasse a duração
            const finalTime = prev.timeline.duration;
            updateCurrentTime(finalTime);
            if (playIntervalRef.current) clearInterval(playIntervalRef.current);
            return {
              ...prev,
              timeline: {
                ...prev.timeline,
                isPlaying: false,
                currentTime: finalTime,
              },
            };
          }
        } else {
          updateCurrentTime(nextTime);
          checkSceneChange(nextTime, prev.scenes);
          return {
            ...prev,
            timeline: { ...prev.timeline, currentTime: nextTime },
          };
        }
      });
    }, 100);
  }, [
    state.playerState,
    state.scenes,
    updatePlayerState,
    updateCurrentTime,
    checkSceneChange,
  ]);

  const pause = useCallback(() => {
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current);
      playIntervalRef.current = null;
    }
    updatePlayerState('paused');
    setState(prev => ({
      ...prev,
      timeline: { ...prev.timeline, isPlaying: false },
    }));
  }, [updatePlayerState]);

  const stop = useCallback(() => {
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current);
      playIntervalRef.current = null;
    }
    updatePlayerState('idle');
    updateCurrentTime(0);
    checkSceneChange(0, state.scenes);
    setState(prev => ({
      ...prev,
      timeline: { ...prev.timeline, isPlaying: false, currentTime: 0 },
    }));
  }, [updatePlayerState, updateCurrentTime, checkSceneChange, state.scenes]);

  const seek = useCallback(
    (time: number) => {
      const clampedTime = Math.max(0, Math.min(time, state.timeline.duration));
      updateCurrentTime(clampedTime);
      checkSceneChange(clampedTime, state.scenes);
    },
    [state.timeline.duration, state.scenes, updateCurrentTime, checkSceneChange]
  );

  const setSpeed = useCallback((speed: number) => {
    setState(prev => ({
      ...prev,
      timeline: {
        ...prev.timeline,
        playbackSpeed: Math.max(0.25, Math.min(speed, 4)),
      },
    }));
  }, []);

  const setVolume = useCallback((volume: number) => {
    const newVolume = Math.max(0, Math.min(volume, 1));
    setState(prev => ({
      ...prev,
      volume: newVolume,
      muted: newVolume === 0,
    }));
  }, []);

  const toggleMute = useCallback(() => {
    setState(prev => ({ ...prev, muted: !prev.muted }));
  }, []);

  const setQuality = useCallback((quality: PreviewQuality) => {
    setState(prev => ({ ...prev, quality }));
  }, []);

  const goToScene = useCallback(
    (index: number) => {
      const clampedIndex = Math.max(
        0,
        Math.min(index, state.scenes.length - 1)
      );
      if (clampedIndex === state.currentSceneIndex) return;

      const sceneStartTime = state.scenes
        .slice(0, clampedIndex)
        .reduce((acc, scene) => acc + scene.duration, 0);

      seek(sceneStartTime);
    },
    [state.scenes, state.currentSceneIndex, seek]
  );

  const nextScene = useCallback(() => {
    goToScene(state.currentSceneIndex + 1);
  }, [state.currentSceneIndex, goToScene]);

  const previousScene = useCallback(() => {
    goToScene(state.currentSceneIndex - 1);
  }, [state.currentSceneIndex, goToScene]);

  const addMarker = useCallback(
    (time: number, label: string) => {
      const newMarker: Marker = {
        id: `custom-${Date.now()}`,
        time: Math.max(0, Math.min(time, state.timeline.duration)),
        label,
        color: '#10b981',
        type: 'custom',
      };

      setState(prev => ({
        ...prev,
        timeline: {
          ...prev.timeline,
          markers: [...prev.timeline.markers, newMarker].sort(
            (a, b) => a.time - b.time
          ),
        },
      }));
    },
    [state.timeline.duration]
  );

  const removeMarker = useCallback((markerId: string) => {
    setState(prev => ({
      ...prev,
      timeline: {
        ...prev.timeline,
        markers: prev.timeline.markers.filter(marker => marker.id !== markerId),
      },
    }));
  }, []);

  const updateSceneConfig = useCallback(
    (sceneIndex: number, config: Partial<Scene>) => {
      setState(prev => {
        const newScenes = [...prev.scenes];
        if (!newScenes[sceneIndex]) return prev;
        newScenes[sceneIndex] = { ...newScenes[sceneIndex], ...config };

        // Recalcula duração e marcadores se a duração da cena mudar
        if (config.duration !== undefined) {
          const newDuration = newScenes.reduce(
            (acc, scene) => acc + scene.duration,
            0
          );
          let currentTime = 0;
          const newMarkers: Marker[] = newScenes.map((scene, index) => {
            const markerTime = currentTime;
            currentTime += scene.duration;
            return {
              id: `scene-marker-${scene.id}`,
              time: markerTime,
              label: scene.name || `Cena ${index + 1}`,
              type: 'scene',
              color: '#3b82f6',
            };
          });

          return {
            ...prev,
            scenes: newScenes,
            timeline: {
              ...prev.timeline,
              duration: newDuration,
              markers: newMarkers,
            },
          };
        }

        return { ...prev, scenes: newScenes };
      });
    },
    []
  );

  const setScenes = useCallback(
    (scenes: Scene[]) => {
      setState(createInitialState({ ...options, initialScenes: scenes }));
    },
    [options]
  );

  const toggleFullscreen = useCallback(() => {
    setState(prev => ({ ...prev, isFullscreen: !prev.isFullscreen }));
  }, []);

  const createEventSubscriber = <T>(ref: React.MutableRefObject<Set<T>>) =>
    useCallback(
      (callback: T) => {
        ref.current.add(callback);
        return () => ref.current.delete(callback);
      },
      [ref]
    );

  const onTimeUpdate = createEventSubscriber(timeUpdateCallbacksRef);
  const onSceneChange = createEventSubscriber(sceneChangeCallbacksRef);
  const onPlayStateChange = createEventSubscriber(stateChangeCallbacksRef);
  const onReady = createEventSubscriber(readyCallbacksRef);
  const onError = createEventSubscriber(errorCallbacksRef);

  useEffect(() => {
    // Carregamento inicial das cenas
    setScenes(options.initialScenes || []);
  }, [options.initialScenes, setScenes]);

  useEffect(() => {
    // Efeito para notificar que o player está pronto
    if (state.scenes.length > 0) {
      readyCallbacksRef.current.forEach(cb => cb());
    }
  }, [state.scenes]);

  useEffect(() => {
    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    };
  }, []);

  return {
    state,
    actions: {
      play,
      pause,
      stop,
      seek,
      setSpeed,
      setVolume,
      toggleMute,
      setQuality,
      nextScene,
      previousScene,
      goToScene,
      addMarker,
      removeMarker,
      updateSceneConfig,
      toggleFullscreen,
      setScenes,
    },
    events: {
      onTimeUpdate,
      onSceneChange,
      onPlayStateChange,
      onReady,
      onError,
    },
  };
};
