/**
 * Hook useVideoPreview - Gerenciamento do Sistema de Preview
 * TecnoCursos AI - Sistema de Preview Avançado
 * 
 * Este hook gerencia todo o estado e lógica do sistema de preview,
 * incluindo controles de reprodução, animações, transições e áudio.
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import {
  PreviewState,
  ScenePreviewConfig,
  PreviewPlayerState,
  PreviewQuality,
  TimelineMarker,
  UseVideoPreviewReturn
} from '../types/preview'

/**
 * Hook principal para gerenciar o sistema de preview de vídeo/cena
 * 
 * @param initialScenes - Cenas iniciais para preview
 * @param initialSceneIndex - Índice da cena inicial
 * @returns Objeto com estado, ações e eventos do preview
 */
export const useVideoPreview = (
  initialScenes: ScenePreviewConfig[] = [],
  initialSceneIndex: number = 0
): UseVideoPreviewReturn => {
  
  // Estado principal do preview
  const [state, setState] = useState<PreviewState>({
    scenes: initialScenes,
    currentSceneIndex: Math.max(0, Math.min(initialSceneIndex, initialScenes.length - 1)),
    timeline: {
      currentTime: 0,
      duration: calculateTotalDuration(initialScenes),
      isPlaying: false,
      playbackSpeed: 1,
      loop: false,
      markers: generateSceneMarkers(initialScenes)
    },
    quality: 'medium',
    playerState: 'idle',
    isFullscreen: false,
    showControls: true,
    volume: 1,
    muted: false
  })

  // Refs para controle de intervalos e callbacks
  const playIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const timeUpdateCallbacksRef = useRef<((time: number) => void)[]>([])
  const sceneChangeCallbacksRef = useRef<((sceneIndex: number) => void)[]>([])
  const stateChangeCallbacksRef = useRef<((state: PreviewPlayerState) => void)[]>([])

  /**
   * Calcula a duração total de todas as cenas
   */
  function calculateTotalDuration(scenes: ScenePreviewConfig[]): number {
    return scenes.reduce((total, scene) => total + scene.duration, 0)
  }

  /**
   * Gera marcadores automáticos para as cenas na timeline
   */
  function generateSceneMarkers(scenes: ScenePreviewConfig[]): TimelineMarker[] {
    const markers: TimelineMarker[] = []
    let currentTime = 0

    scenes.forEach((scene, index) => {
      markers.push({
        id: `scene-${scene.id}`,
        time: currentTime,
        label: scene.name || `Cena ${index + 1}`,
        color: '#3b82f6',
        type: 'scene'
      })
      currentTime += scene.duration
    })

    return markers
  }

  /**
   * Atualiza o estado do player e notifica callbacks
   */
  const updatePlayerState = useCallback((newState: PreviewPlayerState) => {
    setState(prev => ({ ...prev, playerState: newState }))
    stateChangeCallbacksRef.current.forEach(callback => callback(newState))
  }, [])

  /**
   * Atualiza o tempo atual e notifica callbacks
   */
  const updateCurrentTime = useCallback((time: number) => {
    setState(prev => ({
      ...prev,
      timeline: { ...prev.timeline, currentTime: time }
    }))
    timeUpdateCallbacksRef.current.forEach(callback => callback(time))
  }, [])

  /**
   * Verifica se deve mudar de cena baseado no tempo atual
   */
  const checkSceneChange = useCallback((currentTime: number, scenes: ScenePreviewConfig[]) => {
    let accumulatedTime = 0
    let newSceneIndex = 0

    for (let i = 0; i < scenes.length; i++) {
      if (currentTime >= accumulatedTime && currentTime < accumulatedTime + scenes[i].duration) {
        newSceneIndex = i
        break
      }
      accumulatedTime += scenes[i].duration
    }

    setState(prev => {
      if (prev.currentSceneIndex !== newSceneIndex) {
        sceneChangeCallbacksRef.current.forEach(callback => callback(newSceneIndex))
        return { ...prev, currentSceneIndex: newSceneIndex }
      }
      return prev
    })
  }, [])

  /**
   * Inicia a reprodução do preview
   */
  const play = useCallback(() => {
    if (state.playerState === 'playing') return

    updatePlayerState('playing')
    
    setState(prev => ({
      ...prev,
      timeline: { ...prev.timeline, isPlaying: true }
    }))

    // Inicia o loop de atualização de tempo
    playIntervalRef.current = setInterval(() => {
      setState(prev => {
        if (!prev.timeline.isPlaying) return prev

        const nextTime = prev.timeline.currentTime + (0.1 * prev.timeline.playbackSpeed)
        
        // Verifica se chegou ao fim
        if (nextTime >= prev.timeline.duration) {
          if (prev.timeline.loop) {
            // Reinicia se loop estiver ativado
            const newTime = 0
            updateCurrentTime(newTime)
            checkSceneChange(newTime, prev.scenes)
            return { ...prev, timeline: { ...prev.timeline, currentTime: newTime } }
          } else {
            // Para a reprodução
            updatePlayerState('idle')
            return {
              ...prev,
              timeline: { 
                ...prev.timeline, 
                isPlaying: false, 
                currentTime: prev.timeline.duration 
              }
            }
          }
        }

        // Atualiza o tempo e verifica mudança de cena
        updateCurrentTime(nextTime)
        checkSceneChange(nextTime, prev.scenes)
        
        return { ...prev, timeline: { ...prev.timeline, currentTime: nextTime } }
      })
    }, 100) // Atualiza a cada 100ms
  }, [state.playerState, updatePlayerState, updateCurrentTime, checkSceneChange])

  /**
   * Pausa a reprodução do preview
   */
  const pause = useCallback(() => {
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current)
      playIntervalRef.current = null
    }

    updatePlayerState('paused')
    setState(prev => ({
      ...prev,
      timeline: { ...prev.timeline, isPlaying: false }
    }))
  }, [updatePlayerState])

  /**
   * Para completamente a reprodução
   */
  const stop = useCallback(() => {
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current)
      playIntervalRef.current = null
    }

    updatePlayerState('idle')
    updateCurrentTime(0)
    setState(prev => ({
      ...prev,
      currentSceneIndex: 0,
      timeline: { ...prev.timeline, isPlaying: false, currentTime: 0 }
    }))
  }, [updatePlayerState, updateCurrentTime])

  /**
   * Navega para um tempo específico na timeline
   */
  const seek = useCallback((time: number) => {
    const clampedTime = Math.max(0, Math.min(time, state.timeline.duration))
    
    updateCurrentTime(clampedTime)
    checkSceneChange(clampedTime, state.scenes)
  }, [state.timeline.duration, state.scenes, updateCurrentTime, checkSceneChange])

  /**
   * Altera a velocidade de reprodução
   */
  const setSpeed = useCallback((speed: number) => {
    setState(prev => ({
      ...prev,
      timeline: { ...prev.timeline, playbackSpeed: Math.max(0.25, Math.min(speed, 4)) }
    }))
  }, [])

  /**
   * Altera o volume global
   */
  const setVolume = useCallback((volume: number) => {
    setState(prev => ({
      ...prev,
      volume: Math.max(0, Math.min(volume, 1)),
      muted: volume === 0
    }))
  }, [])

  /**
   * Altera a qualidade do preview
   */
  const setQuality = useCallback((quality: PreviewQuality) => {
    setState(prev => ({ ...prev, quality }))
  }, [])

  /**
   * Vai para a próxima cena
   */
  const nextScene = useCallback(() => {
    const nextIndex = Math.min(state.currentSceneIndex + 1, state.scenes.length - 1)
    
    // Calcula o tempo inicial da próxima cena
    let sceneStartTime = 0
    for (let i = 0; i < nextIndex; i++) {
      sceneStartTime += state.scenes[i].duration
    }
    
    seek(sceneStartTime)
  }, [state.currentSceneIndex, state.scenes, seek])

  /**
   * Vai para a cena anterior
   */
  const previousScene = useCallback(() => {
    const prevIndex = Math.max(state.currentSceneIndex - 1, 0)
    
    // Calcula o tempo inicial da cena anterior
    let sceneStartTime = 0
    for (let i = 0; i < prevIndex; i++) {
      sceneStartTime += state.scenes[i].duration
    }
    
    seek(sceneStartTime)
  }, [state.currentSceneIndex, state.scenes, seek])

  /**
   * Vai para uma cena específica
   */
  const goToScene = useCallback((index: number) => {
    const clampedIndex = Math.max(0, Math.min(index, state.scenes.length - 1))
    
    // Calcula o tempo inicial da cena
    let sceneStartTime = 0
    for (let i = 0; i < clampedIndex; i++) {
      sceneStartTime += state.scenes[i].duration
    }
    
    seek(sceneStartTime)
  }, [state.scenes, seek])

  /**
   * Adiciona um marcador personalizado na timeline
   */
  const addMarker = useCallback((time: number, label: string) => {
    const newMarker: TimelineMarker = {
      id: `custom-${Date.now()}`,
      time: Math.max(0, Math.min(time, state.timeline.duration)),
      label,
      color: '#10b981',
      type: 'custom'
    }

    setState(prev => ({
      ...prev,
      timeline: {
        ...prev.timeline,
        markers: [...prev.timeline.markers, newMarker].sort((a, b) => a.time - b.time)
      }
    }))
  }, [state.timeline.duration])

  /**
   * Remove um marcador da timeline
   */
  const removeMarker = useCallback((markerId: string) => {
    setState(prev => ({
      ...prev,
      timeline: {
        ...prev.timeline,
        markers: prev.timeline.markers.filter(marker => marker.id !== markerId)
      }
    }))
  }, [])

  /**
   * Atualiza a configuração de uma cena específica
   */
  const updateSceneConfig = useCallback((sceneIndex: number, config: Partial<ScenePreviewConfig>) => {
    setState(prev => {
      const newScenes = [...prev.scenes]
      newScenes[sceneIndex] = { ...newScenes[sceneIndex], ...config }
      
      const newDuration = calculateTotalDuration(newScenes)
      const newMarkers = generateSceneMarkers(newScenes)
      
      return {
        ...prev,
        scenes: newScenes,
        timeline: {
          ...prev.timeline,
          duration: newDuration,
          markers: newMarkers
        }
      }
    })
  }, [])

  /**
   * Alterna modo fullscreen
   */
  const toggleFullscreen = useCallback(() => {
    setState(prev => ({ ...prev, isFullscreen: !prev.isFullscreen }))
  }, [])

  /**
   * Registra callback para eventos de atualização de tempo
   */
  const onTimeUpdate = useCallback((callback: (time: number) => void) => {
    timeUpdateCallbacksRef.current.push(callback)
    
    // Retorna função para remover o callback
    return () => {
      timeUpdateCallbacksRef.current = timeUpdateCallbacksRef.current.filter(cb => cb !== callback)
    }
  }, [])

  /**
   * Registra callback para eventos de mudança de cena
   */
  const onSceneChange = useCallback((callback: (sceneIndex: number) => void) => {
    sceneChangeCallbacksRef.current.push(callback)
    
    // Retorna função para remover o callback
    return () => {
      sceneChangeCallbacksRef.current = sceneChangeCallbacksRef.current.filter(cb => cb !== callback)
    }
  }, [])

  /**
   * Registra callback para eventos de mudança de estado
   */
  const onStateChange = useCallback((callback: (state: PreviewPlayerState) => void) => {
    stateChangeCallbacksRef.current.push(callback)
    
    // Retorna função para remover o callback
    return () => {
      stateChangeCallbacksRef.current = stateChangeCallbacksRef.current.filter(cb => cb !== callback)
    }
  }, [])

  // Cleanup ao desmontar o componente
  useEffect(() => {
    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current)
      }
    }
  }, [])

  // Atualiza quando as cenas mudam externamente
  useEffect(() => {
    setState(prev => ({
      ...prev,
      scenes: initialScenes,
      timeline: {
        ...prev.timeline,
        duration: calculateTotalDuration(initialScenes),
        markers: generateSceneMarkers(initialScenes)
      }
    }))
  }, [initialScenes])

  return {
    state,
    actions: {
      play,
      pause,
      stop,
      seek,
      setSpeed,
      setVolume,
      setQuality,
      nextScene,
      previousScene,
      goToScene,
      addMarker,
      removeMarker,
      updateSceneConfig,
      toggleFullscreen
    },
    events: {
      onTimeUpdate,
      onSceneChange,
      onStateChange
    }
  }
}