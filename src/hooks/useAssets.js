import { useState, useCallback, useEffect } from 'react';
import assetService from '../services/assetService';

/**
 * Hook personalizado para gerenciar assets
 * Fornece estado, operações CRUD e sincronização com backend
 */
const useAssets = (projectId) => {
  // Estados do hook
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  /**
   * Carregar assets do projeto
   */
  const loadAssets = useCallback(async () => {
    if (!projectId) return;

    setLoading(true);
    setError(null);

    try {
      const assetsData = await assetService.getAssets(projectId);
      setAssets(assetsData);
    } catch (err) {
      console.error('Erro ao carregar assets:', err);
      setError('Erro ao carregar assets. Tente novamente.');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  /**
   * Adicionar novo asset
   */
  const addAsset = useCallback(async (asset) => {
    if (!projectId) return;

    setLoading(true);
    setError(null);

    try {
      const newAsset = await assetService.addAsset(projectId, asset);
      setAssets(prev => [...prev, newAsset]);
      return newAsset;
    } catch (err) {
      console.error('Erro ao adicionar asset:', err);
      setError('Erro ao adicionar asset. Tente novamente.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  /**
   * Remover asset
   */
  const removeAsset = useCallback(async (assetId) => {
    if (!projectId) return;

    setLoading(true);
    setError(null);

    try {
      const success = await assetService.removeAsset(projectId, assetId);
      if (success) {
        setAssets(prev => prev.filter(asset => asset.id !== assetId));
        
        // Limpar seleção se o asset removido estava selecionado
        if (selectedAsset?.id === assetId) {
          setSelectedAsset(null);
        }
      }
      return success;
    } catch (err) {
      console.error('Erro ao remover asset:', err);
      setError('Erro ao remover asset. Tente novamente.');
      return false;
    } finally {
      setLoading(false);
    }
  }, [projectId, selectedAsset]);

  /**
   * Atualizar asset
   */
  const updateAsset = useCallback(async (assetId, updates) => {
    if (!projectId) return;

    setLoading(true);
    setError(null);

    try {
      const updatedAsset = await assetService.updateAsset(projectId, assetId, updates);
      if (updatedAsset) {
        setAssets(prev => prev.map(asset => 
          asset.id === assetId ? updatedAsset : asset
        ));
        
        // Atualizar seleção se o asset atualizado estava selecionado
        if (selectedAsset?.id === assetId) {
          setSelectedAsset(updatedAsset);
        }
      }
      return updatedAsset;
    } catch (err) {
      console.error('Erro ao atualizar asset:', err);
      setError('Erro ao atualizar asset. Tente novamente.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [projectId, selectedAsset]);

  /**
   * Upload de arquivo
   */
  const uploadFile = useCallback(async (file, type) => {
    if (!projectId || !file) return;

    setLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Simular progresso de upload
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      const newAsset = await assetService.uploadFile(projectId, file, type);
      
      setAssets(prev => [...prev, newAsset]);
      setUploadProgress(100);
      
      setTimeout(() => {
        setUploadProgress(0);
      }, 500);

      return newAsset;
    } catch (err) {
      console.error('Erro no upload:', err);
      setError('Erro no upload do arquivo. Tente novamente.');
      setUploadProgress(0);
      return null;
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  /**
   * Selecionar asset
   */
  const selectAsset = useCallback((asset) => {
    setSelectedAsset(asset);
  }, []);

  /**
   * Limpar seleção
   */
  const clearSelection = useCallback(() => {
    setSelectedAsset(null);
  }, []);

  /**
   * Buscar assets por tipo
   */
  const getAssetsByType = useCallback((type) => {
    return assets.filter(asset => asset.type === type);
  }, [assets]);

  /**
   * Buscar asset por ID
   */
  const getAssetById = useCallback((assetId) => {
    return assets.find(asset => asset.id === assetId);
  }, [assets]);

  /**
   * Duplicar asset
   */
  const duplicateAsset = useCallback(async (assetId) => {
    const asset = getAssetById(assetId);
    if (!asset) return null;

    const duplicatedAsset = {
      ...asset,
      id: undefined, // Será gerado pelo backend
      name: `${asset.name} (Cópia)`,
      createdAt: new Date().toISOString()
    };

    return await addAsset(duplicatedAsset);
  }, [getAssetById, addAsset]);

  /**
   * Buscar estatísticas
   */
  const getStats = useCallback(async () => {
    if (!projectId) return null;

    try {
      return await assetService.getAssetStats(projectId);
    } catch (err) {
      console.error('Erro ao buscar estatísticas:', err);
      // Calcular estatísticas locais
      return {
        total: assets.length,
        byType: {
          character: assets.filter(a => a.type === 'character').length,
          image: assets.filter(a => a.type === 'image').length,
          audio: assets.filter(a => a.type === 'audio').length,
          text: assets.filter(a => a.type === 'text').length
        }
      };
    }
  }, [projectId, assets]);

  /**
   * Validar arquivo
   */
  const validateFile = useCallback((file, type) => {
    return assetService.validateFileType(file, type);
  }, []);

  /**
   * Formatar tamanho do arquivo
   */
  const formatFileSize = useCallback((bytes) => {
    return assetService.formatFileSize(bytes);
  }, []);

  /**
   * Carregar assets quando o projectId mudar
   */
  useEffect(() => {
    if (projectId) {
      loadAssets();
    } else {
      setAssets([]);
      setSelectedAsset(null);
    }
  }, [projectId, loadAssets]);

  /**
   * Limpar erro após 5 segundos
   */
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return {
    // Estado
    assets,
    loading,
    error,
    selectedAsset,
    uploadProgress,
    
    // Operações CRUD
    loadAssets,
    addAsset,
    removeAsset,
    updateAsset,
    uploadFile,
    
    // Seleção
    selectAsset,
    clearSelection,
    
    // Utilitários
    getAssetsByType,
    getAssetById,
    duplicateAsset,
    getStats,
    validateFile,
    formatFileSize
  };
};

export default useAssets; 