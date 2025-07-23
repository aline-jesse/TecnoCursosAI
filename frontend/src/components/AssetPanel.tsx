// src/components/AssetPanel.tsx
import React, { useState, useCallback } from 'react';
import { useEditorStore } from '../store/editorStore';
import { Asset, AssetType } from '../types/editor';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  PhotoIcon,
  UserIcon,
  SpeakerWaveIcon,
  DocumentPlusIcon,
  FolderPlusIcon,
} from '@heroicons/react/24/outline';
import './AssetPanel.css';

/**
 * AssetPanel: Componente para gerenciar e exibir assets.
 *
 * Funcionalidades:
 * - Exibe uma lista de assets organizados por categorias (personagens, imagens, áudio)
 * - Permite o upload de novos assets (imagens, áudio)
 * - Permite arrastar assets para o canvas
 * - Busca e filtros por categoria
 * - Interface moderna e responsiva
 */
const AssetPanel: React.FC = () => {
  const { assets, addAsset, setDraggedAsset } = useEditorStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<AssetType | 'all'>(
    'all'
  );
  const [isUploading, setIsUploading] = useState(false);

  // Categorias disponíveis
  const categories = [
    { id: 'all', label: 'Todos', icon: DocumentPlusIcon },
    { id: 'character', label: 'Personagens', icon: UserIcon },
    { id: 'image', label: 'Imagens', icon: PhotoIcon },
    { id: 'audio', label: 'Áudio', icon: SpeakerWaveIcon },
  ];

  // Filtrar assets baseado na busca e categoria
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === 'all' || asset.type === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Determinar tipo de asset baseado na extensão do arquivo
  const getAssetType = (fileName: string): AssetType => {
    const extension = fileName.toLowerCase().split('.').pop();
    if (['mp3', 'wav', 'ogg', 'm4a'].includes(extension || '')) {
      return 'audio';
    }
    if (
      ['svg', 'png', 'jpg', 'jpeg', 'gif', 'webp'].includes(extension || '')
    ) {
      return 'image';
    }
    return 'image'; // padrão
  };

  // Upload de arquivo
  const handleUpload = useCallback(
    (input: React.ChangeEvent<HTMLInputElement> | FileList) => {
      let files: File[];

      if (input instanceof FileList) {
        files = Array.from(input);
      } else {
        if (!input.target.files || input.target.files.length === 0) return;
        files = Array.from(input.target.files);
      }

      setIsUploading(true);
      try {
        for (const file of files) {
          const assetType = getAssetType(file.name);
          const newAsset: Asset = {
            id: `asset-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            name: file.name.replace(/\.[^/.]+$/, ''), // Remove extensão
            type: assetType,
            src: URL.createObjectURL(file),
            thumbnail:
              assetType === 'image' ? URL.createObjectURL(file) : undefined,
          };
          addAsset(newAsset);
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Erro ao fazer upload:', error);
      } finally {
        setIsUploading(false);
      }
    },
    [addAsset]
  );

  // Drag and drop para upload
  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const files = Array.from(event.dataTransfer.files);

      if (files.length > 0) {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = 'image/*,audio/*,.svg';
        input.files = event.dataTransfer.files as FileList;

        // Simular evento de change para upload
        const { files } = event.dataTransfer;
        if (files.length > 0) {
          handleUpload(files);
        }
      }
    },
    [handleUpload]
  );

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  // Iniciar drag de asset
  const handleDragStart = (e: React.DragEvent, asset: Asset) => {
    setDraggedAsset(asset);
    e.dataTransfer.setData('text/plain', asset.id);
    e.dataTransfer.effectAllowed = 'copy';
  };

  // Gerar thumbnail para áudio
  const getAudioThumbnail = () => {
    return (
      <div className='audio-thumbnail'>
        <SpeakerWaveIcon className='w-8 h-8 text-blue-500' />
      </div>
    );
  };

  return (
    <div className='asset-panel'>
      {/* Header */}
      <div className='asset-panel-header'>
        <h2 className='asset-panel-title'>Biblioteca de Assets</h2>
        <button
          className='new-asset-btn'
          onClick={() => document.getElementById('upload-input')?.click()}
          disabled={isUploading}
        >
          <PlusIcon className='w-4 h-4' />
          {isUploading ? 'Enviando...' : 'Novo Asset'}
        </button>
      </div>

      {/* Busca */}
      <div className='asset-search'>
        <div className='search-input-wrapper'>
          <MagnifyingGlassIcon className='search-icon' />
          <input
            type='text'
            placeholder='Buscar assets...'
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className='search-input'
          />
        </div>
      </div>

      {/* Categorias */}
      <div className='asset-categories'>
        {categories.map(category => {
          const Icon = category.icon;
          return (
            <button
              key={category.id}
              className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
              onClick={() =>
                setSelectedCategory(category.id as AssetType | 'all')
              }
            >
              <Icon className='w-4 h-4' />
              <span>{category.label}</span>
            </button>
          );
        })}
      </div>

      {/* Área de upload */}
      <div
        className='upload-area'
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <input
          id='upload-input'
          type='file'
          multiple
          accept='image/*,audio/*,.svg'
          onChange={handleUpload}
          style={{ display: 'none' }}
        />
        <div className='upload-content'>
          <FolderPlusIcon className='upload-icon' />
          <p>Arraste arquivos aqui ou clique para selecionar</p>
          <span className='upload-hint'>Suporta: PNG, JPG, SVG, MP3, WAV</span>
        </div>
      </div>

      {/* Lista de assets */}
      <div className='asset-list-container'>
        <div className='asset-list'>
          {filteredAssets.length === 0 ? (
            <div className='empty-state'>
              <PhotoIcon className='empty-icon' />
              <p>Nenhum asset encontrado</p>
              <span>Tente fazer upload de alguns arquivos</span>
            </div>
          ) : (
            filteredAssets.map(asset => (
              <div
                key={asset.id}
                className='asset-item'
                draggable
                onDragStart={e => handleDragStart(e, asset)}
                title={asset.name}
              >
                <div className='asset-thumbnail'>
                  {asset.type === 'audio' ? (
                    getAudioThumbnail()
                  ) : (
                    <img
                      src={asset.thumbnail || asset.src}
                      alt={asset.name}
                      onError={e => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                      }}
                    />
                  )}
                  <div className='asset-type-badge'>
                    {asset.type === 'character' && (
                      <UserIcon className='w-3 h-3' />
                    )}
                    {asset.type === 'image' && (
                      <PhotoIcon className='w-3 h-3' />
                    )}
                    {asset.type === 'audio' && (
                      <SpeakerWaveIcon className='w-3 h-3' />
                    )}
                  </div>
                </div>
                <div className='asset-info'>
                  <span className='asset-name'>{asset.name}</span>
                  <span className='asset-type'>{asset.type}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Estatísticas */}
      <div className='asset-stats'>
        <span>
          {filteredAssets.length} de {assets.length} assets
        </span>
      </div>
    </div>
  );
};

export default AssetPanel;
