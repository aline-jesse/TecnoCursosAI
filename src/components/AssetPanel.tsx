// src/components/AssetPanel.tsx
import React from 'react';
import { useEditorStore } from '../store/editorStore';
import './AssetPanel.css';

/**
 * AssetPanel: Componente para gerenciar e exibir assets.
 *
 * - Exibe uma lista de assets (personagens, imagens).
 * - Permite o upload de novos assets.
 * - Botão para adicionar novos tipos de assets (placeholder).
 */
const AssetPanel: React.FC = () => {
  const { assets, addAsset } = useEditorStore();

  const handleUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      const newAsset = {
        id: `asset-${Date.now()}`,
        name: file.name,
        type: 'image' as const,
        src: URL.createObjectURL(file),
      };
      addAsset(newAsset);
    }
  };

  return (
    <div className="asset-panel">
      <h2>Asset Library</h2>
      <div className="asset-list">
        {assets.map((asset) => (
          <div key={asset.id} className="asset-item">
            {asset.thumbnail ? (
              <img src={asset.thumbnail} alt={asset.name} width="50" />
            ) : (
              <img src={asset.src} alt={asset.name} width="50" />
            )}
            <span>{asset.name}</span>
          </div>
        ))}
      </div>
      <div className="asset-actions">
        <input type="file" id="upload" onChange={handleUpload} style={{ display: 'none' }} />
        <label htmlFor="upload" className="button">
          Upload Image
        </label>
        <button className="button">New Asset</button>
      </div>
    </div>
  );
};

export default AssetPanel; 