import { useState, useCallback } from 'react';
import { ScenePreviewConfig } from '../types/preview';

/**
 * Hook personalizado para integração do sistema de preview
 * Facilita o uso do VideoPreviewModal em outros componentes
 */
export function usePreviewIntegration({
  onExport,
  onSave,
  onRegenerateNarration,
}: {
  onExport?: (config: any) => Promise<void>;
  onSave?: (scenes: any[]) => Promise<void>;
  onRegenerateNarration?: (sceneId: string, text: string) => Promise<string>;
} = {}) {
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [previewScenes, setPreviewScenes] = useState<ScenePreviewConfig[]>([]);
  const [initialSceneIndex, setInitialSceneIndex] = useState(0);

  /**
   * Abre o preview com as cenas fornecidas
   */
  const openPreview = useCallback((scenes: any[], sceneIndex = 0) => {
    // Converter cenas do formato interno para o formato de preview
    const convertedScenes: ScenePreviewConfig[] = scenes.map(scene => ({
      scene,
      playerState: 'paused',
      onElementSelect: () => {},
      onElementUpdate: () => {},
    }));

    setPreviewScenes(convertedScenes);
    setInitialSceneIndex(
      Math.max(0, Math.min(sceneIndex, convertedScenes.length - 1))
    );
    setIsPreviewOpen(true);
  }, []);

  /**
   * Fecha o preview
   */
  const closePreview = useCallback(() => {
    setIsPreviewOpen(false);
    setPreviewScenes([]);
    setInitialSceneIndex(0);
  }, []);

  /**
   * Abre o preview para uma cena específica
   */
  const openScenePreview = useCallback(
    (scene: any, allScenes?: any[]) => {
      const scenes = allScenes || [scene];
      const sceneIndex = allScenes
        ? allScenes.findIndex(s => s.id === scene.id)
        : 0;
      openPreview(scenes, sceneIndex);
    },
    [openPreview]
  );

  /**
   * Handler padrão para salvar mudanças
   */
  const createSaveHandler = useCallback(
    (onSceneUpdate: (sceneId: string, updates: any) => void) => {
      return (updatedScenes: ScenePreviewConfig[]) => {
        updatedScenes.forEach(sceneConfig => {
          onSceneUpdate(sceneConfig.scene.id, {
            duration: sceneConfig.scene.duration,
            transition: (sceneConfig.scene as any).transition,
            audio: (sceneConfig.scene as any).audio,
            elements: (sceneConfig.scene as any).elements || [],
            background: (sceneConfig.scene as any).background,
          });
        });
        closePreview();
      };
    },
    [closePreview]
  );

  /**
   * Handler padrão para exportar vídeo
   */
  const createExportHandler = useCallback(
    (apiEndpoint = '/api/export-video') => {
      return async (config: any) => {
        try {
          const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(config),
          });

          if (response.ok) {
            const result = await response.json();
            console.log('Vídeo exportado com sucesso:', result);
            return result;
          } else {
            throw new Error('Erro na exportação');
          }
        } catch (error) {
          console.error('Erro ao exportar vídeo:', error);
          throw error;
        }
      };
    },
    []
  );

  /**
   * Handler padrão para regenerar narração
   */
  const createNarrationHandler = useCallback(
    (apiEndpoint = '/api/regenerate-narration') => {
      return async (sceneId: string) => {
        const scene = previewScenes.find(s => (s as any).id === sceneId);
        if (!scene) return '';

        try {
          const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: (scene as any).text || '',
              sceneId,
            }),
          });

          const data = await response.json();
          return data.narrationUrl || '';
        } catch (error) {
          console.error('Erro ao regenerar narração:', error);
          return '';
        }
      };
    },
    [previewScenes]
  );

  // Passar handlers reais para o modal
  return {
    isPreviewOpen,
    previewScenes,
    initialSceneIndex,
    openScenePreview,
    closePreview,
    createSaveHandler: (updateScene: any) => async (scenes: any[]) => {
      if (onSave) await onSave(scenes);
      if (updateScene) updateScene(scenes);
    },
    createExportHandler: () => async (config: any) => {
      if (onExport) await onExport(config);
    },
    createNarrationHandler: () => async (sceneId: string, text: string) => {
      if (onRegenerateNarration)
        return await onRegenerateNarration(sceneId, text);
      return '';
    },
  };
}

export default usePreviewIntegration;
