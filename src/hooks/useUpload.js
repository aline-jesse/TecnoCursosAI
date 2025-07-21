/**
 * Hook para upload de arquivos
 */

import { useState, useCallback } from 'react';

export const useUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const uploadFile = useCallback(async (file) => {
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Simular upload
      for (let i = 0; i <= 100; i += 10) {
        setUploadProgress(i);
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      return {
        id: Date.now(),
        name: file.name,
        size: file.size,
        type: file.type,
        url: URL.createObjectURL(file),
      };
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, []);

  return {
    uploadFile,
    isUploading,
    uploadProgress,
    error,
  };
};
