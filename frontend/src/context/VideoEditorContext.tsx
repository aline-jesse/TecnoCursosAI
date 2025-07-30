/**
 * Context Provider para Video Editor
 * Gerencia estado global do editor de vídeo com integração ao backend
 */

import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { videoEditorAPI, useVideoEditorAPI } from '@/lib/videoEditorAPI';
import { toast } from 'sonner';

// Tipos
interface VideoEditorState {
  // Projeto atual
  currentProject: VideoProject | null;
  projectModified: boolean;
  
  // Timeline
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  volume: number;
  zoom: number;
  
  // Seleção
  selectedClips: string[];
  selectedClip: VideoClip | null;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  
  // Media Library
  mediaFiles: MediaFile[];
  uploadProgress: { [fileId: string]: number };
  
  // Export
  exportInProgress: boolean;
  exportProgress: number;
  exportId: string | null;
  
  // History (Undo/Redo)
  history: VideoProject[];
  historyIndex: number;
  maxHistorySize: number;
}

interface MediaFile {
  id: string;
  filename: string;
  url: string;
  thumbnail?: string;
  size: number;
  duration: number;
  width?: number;
  height?: number;
  mime_type: string;
  uploaded_at: string;
}

type VideoEditorAction =
  | { type: 'SET_PROJECT'; payload: VideoProject }
  | { type: 'UPDATE_PROJECT'; payload: Partial<VideoProject> }
  | { type: 'SET_PROJECT_MODIFIED'; payload: boolean }
  | { type: 'SET_CURRENT_TIME'; payload: number }
  | { type: 'SET_DURATION'; payload: number }
  | { type: 'SET_PLAYING'; payload: boolean }
  | { type: 'SET_VOLUME'; payload: number }
  | { type: 'SET_ZOOM'; payload: number }
  | { type: 'SELECT_CLIPS'; payload: string[] }
  | { type: 'SELECT_CLIP'; payload: VideoClip | null }
  | { type: 'ADD_CLIP'; payload: VideoClip }
  | { type: 'UPDATE_CLIP'; payload: { id: string; updates: Partial<VideoClip> } }
  | { type: 'DELETE_CLIP'; payload: string }
  | { type: 'MOVE_CLIP'; payload: { id: string; layer: number; startTime: number } }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_MEDIA_FILE'; payload: MediaFile }
  | { type: 'SET_MEDIA_FILES'; payload: MediaFile[] }
  | { type: 'SET_UPLOAD_PROGRESS'; payload: { fileId: string; progress: number } }
  | { type: 'SET_EXPORT_PROGRESS'; payload: { inProgress: boolean; progress: number; exportId?: string } }
  | { type: 'SAVE_TO_HISTORY' }
  | { type: 'UNDO' }
  | { type: 'REDO' }
  | { type: 'RESET_STATE' };

const initialState: VideoEditorState = {
  currentProject: null,
  projectModified: false,
  currentTime: 0,
  duration: 300, // 5 minutos default
  isPlaying: false,
  volume: 100,
  zoom: 1,
  selectedClips: [],
  selectedClip: null,
  isLoading: false,
  error: null,
  mediaFiles: [],
  uploadProgress: {},
  exportInProgress: false,
  exportProgress: 0,
  exportId: null,
  history: [],
  historyIndex: -1,
  maxHistorySize: 50,
};

function videoEditorReducer(state: VideoEditorState, action: VideoEditorAction): VideoEditorState {
  switch (action.type) {
    case 'SET_PROJECT':
      return {
        ...state,
        currentProject: action.payload,
        projectModified: false,
        duration: action.payload.settings.duration,
        history: [action.payload],
        historyIndex: 0,
      };

    case 'UPDATE_PROJECT':
      if (!state.currentProject) return state;
      
      const updatedProject = { ...state.currentProject, ...action.payload };
      return {
        ...state,
        currentProject: updatedProject,
        projectModified: true,
      };

    case 'SET_PROJECT_MODIFIED':
      return { ...state, projectModified: action.payload };

    case 'SET_CURRENT_TIME':
      return { ...state, currentTime: Math.max(0, Math.min(action.payload, state.duration)) };

    case 'SET_DURATION':
      return { ...state, duration: action.payload };

    case 'SET_PLAYING':
      return { ...state, isPlaying: action.payload };

    case 'SET_VOLUME':
      return { ...state, volume: Math.max(0, Math.min(action.payload, 100)) };

    case 'SET_ZOOM':
      return { ...state, zoom: Math.max(0.1, Math.min(action.payload, 10)) };

    case 'SELECT_CLIPS':
      return { ...state, selectedClips: action.payload };

    case 'SELECT_CLIP':
      return { 
        ...state, 
        selectedClip: action.payload,
        selectedClips: action.payload ? [action.payload.id] : [],
      };

    case 'ADD_CLIP':
      if (!state.currentProject) return state;
      
      const newProject = {
        ...state.currentProject,
        clips: [...state.currentProject.clips, action.payload],
      };
      
      return {
        ...state,
        currentProject: newProject,
        projectModified: true,
      };

    case 'UPDATE_CLIP':
      if (!state.currentProject) return state;
      
      const updatedClips = state.currentProject.clips.map(clip =>
        clip.id === action.payload.id ? { ...clip, ...action.payload.updates } : clip
      );
      
      const projectWithUpdatedClip = {
        ...state.currentProject,
        clips: updatedClips,
      };
      
      return {
        ...state,
        currentProject: projectWithUpdatedClip,
        projectModified: true,
        selectedClip: state.selectedClip?.id === action.payload.id 
          ? { ...state.selectedClip, ...action.payload.updates }
          : state.selectedClip,
      };

    case 'DELETE_CLIP':
      if (!state.currentProject) return state;
      
      const filteredClips = state.currentProject.clips.filter(clip => clip.id !== action.payload);
      
      return {
        ...state,
        currentProject: {
          ...state.currentProject,
          clips: filteredClips,
        },
        projectModified: true,
        selectedClips: state.selectedClips.filter(id => id !== action.payload),
        selectedClip: state.selectedClip?.id === action.payload ? null : state.selectedClip,
      };

    case 'MOVE_CLIP':
      if (!state.currentProject) return state;
      
      const movedClips = state.currentProject.clips.map(clip =>
        clip.id === action.payload.id
          ? { ...clip, layer: action.payload.layer, start_time: action.payload.startTime }
          : clip
      );
      
      return {
        ...state,
        currentProject: {
          ...state.currentProject,
          clips: movedClips,
        },
        projectModified: true,
      };

    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload };

    case 'ADD_MEDIA_FILE':
      return {
        ...state,
        mediaFiles: [...state.mediaFiles, action.payload],
      };

    case 'SET_MEDIA_FILES':
      return { ...state, mediaFiles: action.payload };

    case 'SET_UPLOAD_PROGRESS':
      return {
        ...state,
        uploadProgress: {
          ...state.uploadProgress,
          [action.payload.fileId]: action.payload.progress,
        },
      };

    case 'SET_EXPORT_PROGRESS':
      return {
        ...state,
        exportInProgress: action.payload.inProgress,
        exportProgress: action.payload.progress,
        exportId: action.payload.exportId || state.exportId,
      };

    case 'SAVE_TO_HISTORY':
      if (!state.currentProject) return state;
      
      const newHistory = state.history.slice(0, state.historyIndex + 1);
      newHistory.push({ ...state.currentProject });
      
      // Limitar tamanho do histórico
      if (newHistory.length > state.maxHistorySize) {
        newHistory.shift();
      }
      
      return {
        ...state,
        history: newHistory,
        historyIndex: newHistory.length - 1,
      };

    case 'UNDO':
      if (state.historyIndex <= 0) return state;
      
      const prevIndex = state.historyIndex - 1;
      const prevProject = state.history[prevIndex];
      
      return {
        ...state,
        currentProject: prevProject,
        historyIndex: prevIndex,
        projectModified: true,
      };

    case 'REDO':
      if (state.historyIndex >= state.history.length - 1) return state;
      
      const nextIndex = state.historyIndex + 1;
      const nextProject = state.history[nextIndex];
      
      return {
        ...state,
        currentProject: nextProject,
        historyIndex: nextIndex,
        projectModified: true,
      };

    case 'RESET_STATE':
      return initialState;

    default:
      return state;
  }
}

// Context
const VideoEditorContext = createContext<{
  state: VideoEditorState;
  dispatch: React.Dispatch<VideoEditorAction>;
  actions: {
    // Projeto
    createProject: (name: string, settings?: Partial<ProjectSettings>) => Promise<void>;
    loadProject: (projectId: string) => Promise<void>;
    saveProject: () => Promise<void>;
    exportProject: (settings: ExportSettings) => Promise<void>;
    
    // Timeline
    play: () => void;
    pause: () => void;
    stop: () => void;
    seek: (time: number) => void;
    setVolume: (volume: number) => void;
    setZoom: (zoom: number) => void;
    
    // Clipes
    addClip: (clip: Omit<VideoClip, 'id'>) => void;
    updateClip: (id: string, updates: Partial<VideoClip>) => void;
    deleteClip: (id: string) => void;
    selectClip: (clip: VideoClip | null) => void;
    moveClip: (id: string, layer: number, startTime: number) => void;
    duplicateClip: (id: string) => void;
    splitClip: (id: string, time: number) => void;
    
    // Mídia
    uploadFile: (file: File) => Promise<void>;
    loadMediaFiles: () => Promise<void>;
    
    // História
    undo: () => void;
    redo: () => void;
    saveToHistory: () => void;
    
    // Utilitários
    clearError: () => void;
    resetEditor: () => void;
  };
} | null>(null);

// Provider
export function VideoEditorProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(videoEditorReducer, initialState);
  const api = useVideoEditorAPI();

  // Auto-save periódico
  useEffect(() => {
    if (state.projectModified && state.currentProject?.id) {
      const timer = setTimeout(() => {
        saveProject();
      }, 30000); // Auto-save a cada 30 segundos

      return () => clearTimeout(timer);
    }
  }, [state.projectModified, state.currentProject]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyboard = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'z':
            e.preventDefault();
            if (e.shiftKey) {
              actions.redo();
            } else {
              actions.undo();
            }
            break;
          case 's':
            e.preventDefault();
            actions.saveProject();
            break;
          case ' ':
            e.preventDefault();
            if (state.isPlaying) {
              actions.pause();
            } else {
              actions.play();
            }
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyboard);
    return () => window.removeEventListener('keydown', handleKeyboard);
  }, [state.isPlaying]);

  // Ações
  const createProject = useCallback(async (name: string, settings?: Partial<ProjectSettings>) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const defaultSettings: ProjectSettings = {
        resolution: { width: 1920, height: 1080 },
        frame_rate: 30,
        duration: 300,
        background_color: '#000000',
        audio_sample_rate: 44100,
        ...settings,
      };

      const newProject: Omit<VideoProject, 'id' | 'created_at' | 'updated_at'> = {
        name,
        clips: [],
        settings: defaultSettings,
      };

      const response = await api.createProject(newProject);
      dispatch({ type: 'SET_PROJECT', payload: response.project });
      
      toast.success(`Projeto "${name}" criado com sucesso!`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao criar projeto';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [api]);

  const loadProject = useCallback(async (projectId: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const response = await api.getProject(projectId);
      dispatch({ type: 'SET_PROJECT', payload: response.project });
      
      toast.success('Projeto carregado com sucesso!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao carregar projeto';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [api]);

  const saveProject = useCallback(async () => {
    if (!state.currentProject?.id) return;
    
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await api.updateProject(state.currentProject.id, state.currentProject);
      dispatch({ type: 'SET_PROJECT_MODIFIED', payload: false });
      
      toast.success('Projeto salvo com sucesso!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao salvar projeto';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [state.currentProject, api]);

  const exportProject = useCallback(async (settings: ExportSettings) => {
    if (!state.currentProject?.id) return;
    
    dispatch({ type: 'SET_EXPORT_PROGRESS', payload: { inProgress: true, progress: 0 } });
    
    try {
      const response = await api.exportProject(state.currentProject.id, settings);
      const exportId = response.export_id;
      
      dispatch({ type: 'SET_EXPORT_PROGRESS', payload: { inProgress: true, progress: 0, exportId } });
      
      // Monitorar progresso da exportação
      api.monitorExport(
        exportId,
        (status) => {
          dispatch({ type: 'SET_EXPORT_PROGRESS', payload: { inProgress: true, progress: status.progress } });
        },
        (downloadUrl) => {
          dispatch({ type: 'SET_EXPORT_PROGRESS', payload: { inProgress: false, progress: 100 } });
          toast.success('Exportação concluída! Iniciando download...');
          
          // Iniciar download automaticamente
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.download = `${state.currentProject?.name || 'video'}_export.${settings.format}`;
          link.click();
        },
        (error) => {
          dispatch({ type: 'SET_EXPORT_PROGRESS', payload: { inProgress: false, progress: 0 } });
          dispatch({ type: 'SET_ERROR', payload: error });
          toast.error(`Erro na exportação: ${error}`);
        }
      );
      
      toast.success('Exportação iniciada!');
    } catch (error) {
      dispatch({ type: 'SET_EXPORT_PROGRESS', payload: { inProgress: false, progress: 0 } });
      const errorMessage = error instanceof Error ? error.message : 'Erro ao iniciar exportação';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    }
  }, [state.currentProject, api]);

  const uploadFile = useCallback(async (file: File) => {
    const validation = api.validateFile(file);
    if (!validation.valid) {
      toast.error(validation.error);
      return;
    }
    
    const fileId = `upload_${Date.now()}_${Math.random()}`;
    
    try {
      dispatch({ type: 'SET_UPLOAD_PROGRESS', payload: { fileId, progress: 0 } });
      
      const response = await api.uploadMedia(file, (progress) => {
        dispatch({ type: 'SET_UPLOAD_PROGRESS', payload: { fileId, progress } });
      });
      
      dispatch({ type: 'ADD_MEDIA_FILE', payload: response.data });
      toast.success(`Arquivo "${file.name}" enviado com sucesso!`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro no upload';
      toast.error(errorMessage);
    } finally {
      // Remove progresso após 2 segundos
      setTimeout(() => {
        dispatch({ type: 'SET_UPLOAD_PROGRESS', payload: { fileId, progress: -1 } });
      }, 2000);
    }
  }, [api]);

  const addClip = useCallback((clipData: Omit<VideoClip, 'id'>) => {
    const clip: VideoClip = {
      ...clipData,
      id: `clip_${Date.now()}_${Math.random()}`,
    };
    
    dispatch({ type: 'SAVE_TO_HISTORY' });
    dispatch({ type: 'ADD_CLIP', payload: clip });
  }, []);

  const duplicateClip = useCallback((id: string) => {
    if (!state.currentProject) return;
    
    const clip = state.currentProject.clips.find(c => c.id === id);
    if (!clip) return;
    
    const duplicatedClip: VideoClip = {
      ...clip,
      id: `clip_${Date.now()}_${Math.random()}`,
      start_time: clip.end_time,
      end_time: clip.end_time + (clip.end_time - clip.start_time),
    };
    
    dispatch({ type: 'SAVE_TO_HISTORY' });
    dispatch({ type: 'ADD_CLIP', payload: duplicatedClip });
  }, [state.currentProject]);

  const splitClip = useCallback((id: string, time: number) => {
    if (!state.currentProject) return;
    
    const clip = state.currentProject.clips.find(c => c.id === id);
    if (!clip || time <= clip.start_time || time >= clip.end_time) return;
    
    const firstPart: VideoClip = {
      ...clip,
      end_time: time,
    };
    
    const secondPart: VideoClip = {
      ...clip,
      id: `clip_${Date.now()}_${Math.random()}`,
      start_time: time,
    };
    
    dispatch({ type: 'SAVE_TO_HISTORY' });
    dispatch({ type: 'UPDATE_CLIP', payload: { id, updates: firstPart } });
    dispatch({ type: 'ADD_CLIP', payload: secondPart });
  }, [state.currentProject]);

  // Objeto de ações
  const actions = {
    createProject,
    loadProject,
    saveProject,
    exportProject,
    
    play: () => dispatch({ type: 'SET_PLAYING', payload: true }),
    pause: () => dispatch({ type: 'SET_PLAYING', payload: false }),
    stop: () => {
      dispatch({ type: 'SET_PLAYING', payload: false });
      dispatch({ type: 'SET_CURRENT_TIME', payload: 0 });
    },
    seek: (time: number) => dispatch({ type: 'SET_CURRENT_TIME', payload: time }),
    setVolume: (volume: number) => dispatch({ type: 'SET_VOLUME', payload: volume }),
    setZoom: (zoom: number) => dispatch({ type: 'SET_ZOOM', payload: zoom }),
    
    addClip,
    updateClip: (id: string, updates: Partial<VideoClip>) => {
      dispatch({ type: 'SAVE_TO_HISTORY' });
      dispatch({ type: 'UPDATE_CLIP', payload: { id, updates } });
    },
    deleteClip: (id: string) => {
      dispatch({ type: 'SAVE_TO_HISTORY' });
      dispatch({ type: 'DELETE_CLIP', payload: id });
    },
    selectClip: (clip: VideoClip | null) => dispatch({ type: 'SELECT_CLIP', payload: clip }),
    moveClip: (id: string, layer: number, startTime: number) => {
      dispatch({ type: 'SAVE_TO_HISTORY' });
      dispatch({ type: 'MOVE_CLIP', payload: { id, layer, startTime } });
    },
    duplicateClip,
    splitClip,
    
    uploadFile,
    loadMediaFiles: async () => {
      try {
        const response = await api.listProjects();
        // Implementar quando tiver endpoint para listar mídia
      } catch (error) {
        console.error('Erro ao carregar mídia:', error);
      }
    },
    
    undo: () => dispatch({ type: 'UNDO' }),
    redo: () => dispatch({ type: 'REDO' }),
    saveToHistory: () => dispatch({ type: 'SAVE_TO_HISTORY' }),
    
    clearError: () => dispatch({ type: 'SET_ERROR', payload: null }),
    resetEditor: () => dispatch({ type: 'RESET_STATE' }),
  };

  return (
    <VideoEditorContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </VideoEditorContext.Provider>
  );
}

// Hook para usar o context
export function useVideoEditor() {
  const context = useContext(VideoEditorContext);
  if (!context) {
    throw new Error('useVideoEditor deve ser usado dentro de VideoEditorProvider');
  }
  return context;
}

export default VideoEditorContext;
