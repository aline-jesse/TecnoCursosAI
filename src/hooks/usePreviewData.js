/**
 * Hook para dados de preview
 */

import { useState, useCallback } from 'react';

export const usePreviewData = () => {
  const [previewData, setPreviewData] = useState({
    scenes: [],
    currentScene: 0,
    isPlaying: false,
  });

  const generatePreviewData = useCallback((scenes) => {
    setPreviewData({
      scenes: scenes || [],
      currentScene: 0,
      isPlaying: false,
    });
  }, []);

  return {
    previewData,
    generatePreviewData,
  };
}; 