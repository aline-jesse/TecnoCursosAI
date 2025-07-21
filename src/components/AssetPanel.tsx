/**
 * AssetPanel - Componente para gerenciar assets
 * Permite visualizar, filtrar, adicionar e remover assets
 */

import React, { useState, useCallback, useRef } from 'react';
import { useAssets, useEditor } from '../store/editorStore';
import './AssetPanel.css';

/**
 * AssetPanel - Componente para gerenciar assets
 * Permite visualizar, filtrar, adicionar e remover assets
 */
const AssetPanel: React.FC = () => {
  // Estados locais para UI
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<'all' | 'image' | 'video' | 'audio' | 'text'>('all');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Hooks da store Zustand
  const assets = useAssets();
  const { addAsset, deleteAsset } = useEditor();

  /**
   * Filtra assets baseado na busca e tipo
   */
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         asset.tags?.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = selectedType === 'all' || asset.type === selectedType;
    return matchesSearch && matchesType;
  });

  /**
   * Manipula upload de arquivo
   */
  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Simula progresso de upload
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            if (prev >= 100) {
              clearInterval(progressInterval);
              return 100;
            }
            return prev + 10;
          });
        }, 100);

        // Determina tipo do asset baseado na extensão
        const fileType = getAssetType(file);
        
        // Cria URL temporária para o arquivo
        const fileUrl = URL.createObjectURL(file);
        
        // Cria thumbnail se for imagem
        let thumbnail = undefined;
        if (fileType === 'image') {
          thumbnail = fileUrl;
        }

        // Adiciona asset à store
        addAsset({
          name: file.name,
          type: fileType,
          url: fileUrl,
          thumbnail,
          size: file.size,
          tags: [fileType, file.name.split('.').pop() || ''],
        });

        // Aguarda um pouco para simular upload
        await new Promise(resolve => setTimeout(resolve, 500));
        clearInterval(progressInterval);
      }
    } catch (error) {
      console.error('Erro no upload:', error);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, [addAsset]);

  /**
   * Determina o tipo do asset baseado na extensão do arquivo
   */
  const getAssetType = (file: File): 'image' | 'video' | 'audio' | 'text' => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
    const videoExtensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'];
    const audioExtensions = ['mp3', 'wav', 'ogg', 'aac', 'flac'];
    const textExtensions = ['txt', 'md', 'json', 'xml', 'html', 'css', 'js'];
    
    if (imageExtensions.includes(extension || '')) return 'image';
    if (videoExtensions.includes(extension || '')) return 'video';
    if (audioExtensions.includes(extension || '')) return 'audio';
    if (textExtensions.includes(extension || '')) return 'text';
    
    return 'text'; // Padrão
  };

  /**
   * Manipula drag & drop de arquivos
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.currentTarget.classList.remove('drag-over');
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    // Simula upload dos arquivos
    files.forEach(file => {
      const fileType = getAssetType(file);
      const fileUrl = URL.createObjectURL(file);
      
      addAsset({
        name: file.name,
        type: fileType,
        url: fileUrl,
        thumbnail: fileType === 'image' ? fileUrl : undefined,
        size: file.size,
        tags: [fileType, file.name.split('.').pop() || ''],
      });
    });
  }, [addAsset]);

  /**
   * Manipula remoção de asset
   */
  const handleDeleteAsset = useCallback((assetId: string) => {
    if (window.confirm('Tem certeza que deseja excluir este asset?')) {
      deleteAsset(assetId);
    }
  }, [deleteAsset]);

  /**
   * Abre seletor de arquivo
   */
  const handleSelectFiles = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="asset-panel">
      {/* Header */}
      <div className="asset-panel-header">
        <h3>Assets</h3>
        <button 
          className="upload-btn"
          onClick={handleSelectFiles}
          disabled={isUploading}
          title="Adicionar assets"
        >
          {isUploading ? '⏳' : '📁'}
        </button>
      </div>

      {/* Input de arquivo oculto */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,video/*,audio/*,.txt,.md,.json,.xml,.html,.css,.js"
        onChange={handleFileUpload}
        style={{ display: 'none' }}
      />

      {/* Área de upload */}
      <div 
        className="upload-area"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="upload-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p>Enviando... {uploadProgress}%</p>
          </div>
        ) : (
          <div className="upload-hint">
            <p>Arraste arquivos aqui ou clique para selecionar</p>
            <p>Suporta: imagens, vídeos, áudios e textos</p>
          </div>
        )}
      </div>

      {/* Filtros */}
      <div className="asset-filters">
        <input
          type="text"
          placeholder="Buscar assets..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value as any)}
          className="type-filter"
        >
          <option value="all">Todos os tipos</option>
          <option value="image">Imagens</option>
          <option value="video">Vídeos</option>
          <option value="audio">Áudios</option>
          <option value="text">Textos</option>
        </select>
      </div>

      {/* Lista de assets */}
      <div className="assets-container">
        {filteredAssets.length === 0 ? (
          <div className="empty-assets">
            <p>Nenhum asset encontrado</p>
            <p>Adicione alguns assets para começar</p>
          </div>
        ) : (
          <div className="assets-grid">
            {filteredAssets.map((asset) => (
              <div
                key={asset.id}
                className="asset-item"
                draggable
                onDragStart={(e) => {
                  e.dataTransfer.setData('text/plain', asset.id);
                }}
              >
                {/* Thumbnail do asset */}
                <div className="asset-thumbnail">
                  {asset.thumbnail ? (
                    <img src={asset.thumbnail} alt={asset.name} />
                  ) : (
                    <div className="asset-placeholder">
                      {asset.type === 'image' && '🖼️'}
                      {asset.type === 'video' && '🎥'}
                      {asset.type === 'audio' && '🎵'}
                      {asset.type === 'text' && '📝'}
                    </div>
                  )}
                </div>

                {/* Informações do asset */}
                <div className="asset-info">
                  <h4 className="asset-name">{asset.name}</h4>
                  <p className="asset-type">{asset.type}</p>
                  {asset.size && (
                    <p className="asset-size">
                      {(asset.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  )}
                </div>

                {/* Tags do asset */}
                {asset.tags && asset.tags.length > 0 && (
                  <div className="asset-tags">
                    {asset.tags.slice(0, 3).map((tag: string, index: number) => (
                      <span key={index} className="tag">
                        {tag}
                      </span>
                    ))}
                    {asset.tags.length > 3 && (
                      <span className="tag more">+{asset.tags.length - 3}</span>
                    )}
                  </div>
                )}

                {/* Controles do asset */}
                <div className="asset-controls">
                  <button
                    className="control-btn preview"
                    onClick={() => window.open(asset.url, '_blank')}
                    title="Visualizar"
                  >
                    👁️
                  </button>
                  <button
                    className="control-btn delete"
                    onClick={() => handleDeleteAsset(asset.id)}
                    title="Excluir"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Estatísticas */}
      {assets.length > 0 && (
        <div className="asset-stats">
          <p>Total: {assets.length} asset{assets.length !== 1 ? 's' : ''}</p>
          <p>Filtrados: {filteredAssets.length}</p>
        </div>
      )}
    </div>
  );
};

export default AssetPanel; 