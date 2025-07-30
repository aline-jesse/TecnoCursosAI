/**
 * Custom Hooks para o Editor de Vídeos
 * Lógica reutilizável para funcionalidades do editor
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Hook para controle de mídia
export const useMediaControls = (videoRef: React.RefObject<HTMLVideoElement>) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(100);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);

  const play = useCallback(async () => {
    if (videoRef.current) {
      try {
        await videoRef.current.play();
        setIsPlaying(true);
      } catch (error) {
        console.error('Erro ao reproduzir:', error);
      }
    }
  }, [videoRef]);

  const pause = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  }, [videoRef]);

  const togglePlayPause = useCallback(() => {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }, [isPlaying, play, pause]);

  const stop = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
      setCurrentTime(0);
      setIsPlaying(false);
    }
  }, [videoRef]);

  const seekTo = useCallback((time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.max(0, Math.min(time, duration));
      setCurrentTime(videoRef.current.currentTime);
    }
  }, [videoRef, duration]);

  const changeVolume = useCallback((newVolume: number) => {
    const clampedVolume = Math.max(0, Math.min(100, newVolume));
    setVolume(clampedVolume);
    if (videoRef.current) {
      videoRef.current.volume = clampedVolume / 100;
      if (clampedVolume === 0) {
        setIsMuted(true);
      } else if (isMuted) {
        setIsMuted(false);
      }
    }
  }, [videoRef, isMuted]);

  const toggleMute = useCallback(() => {
    if (videoRef.current) {
      const newMuted = !isMuted;
      videoRef.current.muted = newMuted;
      setIsMuted(newMuted);
    }
  }, [videoRef, isMuted]);

  const changePlaybackRate = useCallback((rate: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
      setPlaybackRate(rate);
    }
  }, [videoRef]);

  // Event listeners
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => setCurrentTime(video.currentTime);
    const handleDurationChange = () => setDuration(video.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleVolumeChange = () => {
      setVolume(video.volume * 100);
      setIsMuted(video.muted);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('volumechange', handleVolumeChange);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('volumechange', handleVolumeChange);
    };
  }, [videoRef]);

  return {
    isPlaying,
    currentTime,
    duration,
    volume,
    isMuted,
    playbackRate,
    controls: {
      play,
      pause,
      togglePlayPause,
      stop,
      seekTo,
      changeVolume,
      toggleMute,
      changePlaybackRate
    }
  };
};

// Hook para gerenciamento da timeline
export const useTimeline = (projectDuration: number = 300) => {
  const [clips, setClips] = useState<any[]>([]);
  const [selectedClip, setSelectedClip] = useState<string | null>(null);
  const [zoom, setZoom] = useState(100);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const timelineRef = useRef<HTMLDivElement>(null);

  const addClip = useCallback((clipData: any) => {
    const newClip = {
      id: `clip_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      startTime: clipData.startTime || 0,
      endTime: clipData.endTime || clipData.duration || 10,
      layer: clipData.layer || 0,
      ...clipData
    };

    setClips(prev => [...prev, newClip]);
    return newClip.id;
  }, []);

  const removeClip = useCallback((clipId: string) => {
    setClips(prev => prev.filter(clip => clip.id !== clipId));
    if (selectedClip === clipId) {
      setSelectedClip(null);
    }
  }, [selectedClip]);

  const updateClip = useCallback((clipId: string, updates: Partial<any>) => {
    setClips(prev => prev.map(clip => 
      clip.id === clipId ? { ...clip, ...updates } : clip
    ));
  }, []);

  const moveClip = useCallback((clipId: string, newStartTime: number, newLayer?: number) => {
    setClips(prev => prev.map(clip => {
      if (clip.id === clipId) {
        const duration = clip.endTime - clip.startTime;
        const startTime = snapToGrid ? Math.round(newStartTime) : newStartTime;
        return {
          ...clip,
          startTime: Math.max(0, Math.min(startTime, projectDuration - duration)),
          endTime: Math.max(duration, Math.min(startTime + duration, projectDuration)),
          layer: newLayer !== undefined ? newLayer : clip.layer
        };
      }
      return clip;
    }));
  }, [snapToGrid, projectDuration]);

  const duplicateClip = useCallback((clipId: string) => {
    const clip = clips.find(c => c.id === clipId);
    if (clip) {
      const duration = clip.endTime - clip.startTime;
      const newStartTime = clip.endTime;
      
      return addClip({
        ...clip,
        startTime: newStartTime,
        endTime: newStartTime + duration,
        name: `${clip.name} (Cópia)`
      });
    }
  }, [clips, addClip]);

  const splitClip = useCallback((clipId: string, splitTime: number) => {
    const clip = clips.find(c => c.id === clipId);
    if (clip && splitTime > clip.startTime && splitTime < clip.endTime) {
      // Primeiro clipe (antes do corte)
      updateClip(clipId, { endTime: splitTime });
      
      // Segundo clipe (depois do corte)
      return addClip({
        ...clip,
        startTime: splitTime,
        endTime: clip.endTime,
        name: `${clip.name} (Parte 2)`
      });
    }
  }, [clips, updateClip, addClip]);

  const getClipsAtTime = useCallback((time: number, layer?: number) => {
    return clips.filter(clip => 
      time >= clip.startTime && 
      time <= clip.endTime &&
      (layer === undefined || clip.layer === layer)
    );
  }, [clips]);

  const getClipsByLayer = useCallback((layer: number) => {
    return clips.filter(clip => clip.layer === layer);
  }, [clips]);

  const timeToPixels = useCallback((time: number, containerWidth: number = 1000) => {
    return (time / projectDuration) * containerWidth * (zoom / 100);
  }, [projectDuration, zoom]);

  const pixelsToTime = useCallback((pixels: number, containerWidth: number = 1000) => {
    return (pixels / (containerWidth * (zoom / 100))) * projectDuration;
  }, [projectDuration, zoom]);

  return {
    clips,
    selectedClip,
    zoom,
    snapToGrid,
    timelineRef,
    actions: {
      addClip,
      removeClip,
      updateClip,
      moveClip,
      duplicateClip,
      splitClip,
      setSelectedClip,
      setZoom,
      setSnapToGrid
    },
    queries: {
      getClipsAtTime,
      getClipsByLayer,
      timeToPixels,
      pixelsToTime
    }
  };
};

// Hook para upload e processamento de arquivos
export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);

  const uploadFile = useCallback(async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Falha no upload');
      }

      const result = await response.json();
      
      const fileData = {
        id: result.id,
        name: file.name,
        type: file.type,
        size: file.size,
        url: result.url,
        duration: result.duration || 0,
        thumbnail: result.thumbnail,
        uploadedAt: new Date().toISOString()
      };

      setUploadedFiles(prev => [...prev, fileData]);
      return fileData;

    } catch (error) {
      console.error('Erro no upload:', error);
      throw error;
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, []);

  const uploadMultipleFiles = useCallback(async (files: File[]) => {
    const results = [];
    
    for (let i = 0; i < files.length; i++) {
      try {
        const result = await uploadFile(files[i]);
        results.push(result);
      } catch (error) {
        console.error(`Erro no upload do arquivo ${files[i].name}:`, error);
      }
    }

    return results;
  }, [uploadFile]);

  const removeFile = useCallback((fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  }, []);

  return {
    isUploading,
    uploadProgress,
    uploadedFiles,
    actions: {
      uploadFile,
      uploadMultipleFiles,
      removeFile
    }
  };
};

// Hook para exportação de vídeo
export const useVideoExport = () => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportStatus, setExportStatus] = useState<string>('');

  const exportVideo = useCallback(async (projectData: any, settings: any) => {
    setIsExporting(true);
    setExportProgress(0);
    setExportStatus('Iniciando exportação...');

    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project: projectData,
          settings: settings
        })
      });

      if (!response.ok) {
        throw new Error('Falha na exportação');
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('Não foi possível ler a resposta');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = new TextDecoder().decode(value);
        const lines = text.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            
            if (data.progress !== undefined) {
              setExportProgress(data.progress);
            }
            
            if (data.status) {
              setExportStatus(data.status);
            }

            if (data.completed && data.downloadUrl) {
              return data.downloadUrl;
            }
          } catch (e) {
            // Ignorar linhas que não são JSON válido
          }
        }
      }

    } catch (error) {
      console.error('Erro na exportação:', error);
      setExportStatus('Erro na exportação');
      throw error;
    } finally {
      setIsExporting(false);
    }
  }, []);

  const cancelExport = useCallback(async () => {
    try {
      await fetch('/api/export/cancel', { method: 'POST' });
      setIsExporting(false);
      setExportProgress(0);
      setExportStatus('Exportação cancelada');
    } catch (error) {
      console.error('Erro ao cancelar exportação:', error);
    }
  }, []);

  return {
    isExporting,
    exportProgress,
    exportStatus,
    actions: {
      exportVideo,
      cancelExport
    }
  };
};

// Hook para undo/redo
export const useUndoRedo = <T>(initialState: T) => {
  const [history, setHistory] = useState<T[]>([initialState]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const state = history[currentIndex];

  const pushState = useCallback((newState: T) => {
    setHistory(prev => {
      const newHistory = prev.slice(0, currentIndex + 1);
      return [...newHistory, newState];
    });
    setCurrentIndex(prev => prev + 1);
  }, [currentIndex]);

  const undo = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [currentIndex]);

  const redo = useCallback(() => {
    if (currentIndex < history.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  }, [currentIndex, history.length]);

  const canUndo = currentIndex > 0;
  const canRedo = currentIndex < history.length - 1;

  return {
    state,
    canUndo,
    canRedo,
    actions: {
      pushState,
      undo,
      redo
    }
  };
};

// Hook para keyboard shortcuts
export const useKeyboardShortcuts = (callbacks: Record<string, () => void>) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const { ctrlKey, metaKey, shiftKey, altKey, key } = event;
      const modifierKey = ctrlKey || metaKey;

      // Criar string da combinação de teclas
      let shortcut = '';
      if (modifierKey) shortcut += 'ctrl+';
      if (shiftKey) shortcut += 'shift+';
      if (altKey) shortcut += 'alt+';
      shortcut += key.toLowerCase();

      // Executar callback se existir
      if (callbacks[shortcut]) {
        event.preventDefault();
        callbacks[shortcut]();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [callbacks]);
};

// Utilitários
export const formatTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const parseTimeToSeconds = (timeString: string): number => {
  const parts = timeString.split(':').map(Number);
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  } else if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  }
  return 0;
};
