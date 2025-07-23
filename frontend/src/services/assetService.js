/**
 * AssetService - Serviço para gerenciamento de assets
 * Fornece métodos para CRUD de assets, upload de arquivos e integração com backend
 */

class AssetService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.token = localStorage.getItem('authToken') || 'demo-token';
  }

  /**
   * Configurar headers para requisições
   */
  getHeaders() {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.token}`,
    };
  }

  /**
   * Buscar todos os assets do projeto
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Array>} Lista de assets
   */
  async getAssets(projectId) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/projects/${projectId}/assets`,
        {
          method: 'GET',
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao buscar assets: ${response.status}`);
      }

      const data = await response.json();
      return data.assets || [];
    } catch (error) {
      console.error('Erro ao buscar assets:', error);
      // Retornar dados mock para demo
      return this.getMockAssets();
    }
  }

  /**
   * Adicionar novo asset
   * @param {string} projectId - ID do projeto
   * @param {Object} asset - Dados do asset
   * @returns {Promise<Object>} Asset criado
   */
  async addAsset(projectId, asset) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/projects/${projectId}/assets`,
        {
          method: 'POST',
          headers: this.getHeaders(),
          body: JSON.stringify(asset),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao adicionar asset: ${response.status}`);
      }

      const data = await response.json();
      return data.asset;
    } catch (error) {
      console.error('Erro ao adicionar asset:', error);
      // Simular criação local
      return {
        ...asset,
        id:
          asset.id ||
          `asset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        createdAt: new Date().toISOString(),
      };
    }
  }

  /**
   * Remover asset
   * @param {string} projectId - ID do projeto
   * @param {string} assetId - ID do asset
   * @returns {Promise<boolean>} Sucesso da operação
   */
  async removeAsset(projectId, assetId) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/projects/${projectId}/assets/${assetId}`,
        {
          method: 'DELETE',
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao remover asset: ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Erro ao remover asset:', error);
      return false;
    }
  }

  /**
   * Atualizar asset
   * @param {string} projectId - ID do projeto
   * @param {string} assetId - ID do asset
   * @param {Object} updates - Dados para atualizar
   * @returns {Promise<Object>} Asset atualizado
   */
  async updateAsset(projectId, assetId, updates) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/projects/${projectId}/assets/${assetId}`,
        {
          method: 'PUT',
          headers: this.getHeaders(),
          body: JSON.stringify(updates),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao atualizar asset: ${response.status}`);
      }

      const data = await response.json();
      return data.asset;
    } catch (error) {
      console.error('Erro ao atualizar asset:', error);
      return null;
    }
  }

  /**
   * Upload de arquivo
   * @param {string} projectId - ID do projeto
   * @param {File} file - Arquivo para upload
   * @param {string} type - Tipo do asset
   * @returns {Promise<Object>} Asset criado
   */
  async uploadFile(projectId, file, type) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const response = await fetch(
        `${this.baseURL}/api/projects/${projectId}/assets/upload`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Erro no upload: ${response.status}`);
      }

      const data = await response.json();
      return data.asset;
    } catch (error) {
      console.error('Erro no upload:', error);
      // Simular upload local
      return {
        id: `asset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: file.name,
        type,
        url: URL.createObjectURL(file),
        thumbnail: type === 'image' ? URL.createObjectURL(file) : null,
        size: file.size,
        createdAt: new Date().toISOString(),
        metadata: {
          fileType: file.type,
          lastModified: file.lastModified,
        },
      };
    }
  }

  /**
   * Buscar assets por tipo
   * @param {string} projectId - ID do projeto
   * @param {string} type - Tipo do asset
   * @returns {Promise<Array>} Lista de assets filtrados
   */
  async getAssetsByType(projectId, type) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/projects/${projectId}/assets?type=${type}`,
        {
          method: 'GET',
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao buscar assets por tipo: ${response.status}`);
      }

      const data = await response.json();
      return data.assets || [];
    } catch (error) {
      console.error('Erro ao buscar assets por tipo:', error);
      const allAssets = this.getMockAssets();
      return allAssets.filter(asset => asset.type === type);
    }
  }

  /**
   * Buscar estatísticas de assets
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Object>} Estatísticas dos assets
   */
  async getAssetStats(projectId) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/projects/${projectId}/assets/stats`,
        {
          method: 'GET',
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao buscar estatísticas: ${response.status}`);
      }

      const data = await response.json();
      return data.stats;
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
      const assets = this.getMockAssets();
      return {
        total: assets.length,
        byType: {
          character: assets.filter(a => a.type === 'character').length,
          image: assets.filter(a => a.type === 'image').length,
          audio: assets.filter(a => a.type === 'audio').length,
          text: assets.filter(a => a.type === 'text').length,
        },
      };
    }
  }

  /**
   * Dados mock para demonstração
   * @returns {Array} Lista de assets mock
   */
  getMockAssets() {
    return [
      {
        id: 'character_1',
        name: 'Professor João',
        type: 'character',
        thumbnail: `data:image/svg+xml;base64,${btoa(`
          <svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="20" r="12" fill="#4F46E5"/>
            <rect x="18" y="35" width="24" height="20" rx="12" fill="#4F46E5"/>
            <circle cx="30" cy="15" r="3" fill="white"/>
            <rect x="25" y="25" width="10" height="2" fill="white"/>
          </svg>
        `)}`,
        createdAt: '2024-01-15T10:30:00Z',
        metadata: {
          isCustom: true,
          category: 'character',
        },
      },
      {
        id: 'character_2',
        name: 'Estudante Maria',
        type: 'character',
        thumbnail: `data:image/svg+xml;base64,${btoa(`
          <svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="20" r="12" fill="#EC4899"/>
            <rect x="18" y="35" width="24" height="20" rx="12" fill="#EC4899"/>
            <circle cx="30" cy="15" r="3" fill="white"/>
            <rect x="25" y="25" width="10" height="2" fill="white"/>
          </svg>
        `)}`,
        createdAt: '2024-01-16T14:20:00Z',
        metadata: {
          isCustom: true,
          category: 'character',
        },
      },
      {
        id: 'text_1',
        name: 'Título Principal',
        type: 'text',
        content: 'Título do Vídeo',
        thumbnail: `data:image/svg+xml;base64,${btoa(`
          <svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="15" width="40" height="30" fill="#F3F4F6" stroke="#D1D5DB" stroke-width="2"/>
            <text x="30" y="35" text-anchor="middle" font-family="Arial" font-size="12" fill="#374151">T</text>
          </svg>
        `)}`,
        createdAt: '2024-01-17T09:15:00Z',
        metadata: {
          category: 'text',
          fontSize: 24,
          fontFamily: 'Arial',
          color: '#000000',
        },
      },
      {
        id: 'text_2',
        name: 'Subtítulo',
        type: 'text',
        content: 'Subtítulo explicativo',
        thumbnail: `data:image/svg+xml;base64,${btoa(`
          <svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="15" width="40" height="30" fill="#F3F4F6" stroke="#D1D5DB" stroke-width="2"/>
            <text x="30" y="35" text-anchor="middle" font-family="Arial" font-size="10" fill="#374151">S</text>
          </svg>
        `)}`,
        createdAt: '2024-01-17T09:16:00Z',
        metadata: {
          category: 'text',
          fontSize: 16,
          fontFamily: 'Arial',
          color: '#666666',
        },
      },
    ];
  }

  /**
   * Validar tipo de arquivo
   * @param {File} file - Arquivo para validar
   * @param {string} type - Tipo esperado
   * @returns {boolean} Se o arquivo é válido
   */
  validateFileType(file, type) {
    const validTypes = {
      image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
      audio: ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3'],
      video: ['video/mp4', 'video/webm', 'video/ogg'],
    };

    return validTypes[type]?.includes(file.type) || false;
  }

  /**
   * Formatar tamanho do arquivo
   * @param {number} bytes - Tamanho em bytes
   * @returns {string} Tamanho formatado
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  }

  /**
   * Gerar thumbnail para arquivo
   * @param {File} file - Arquivo para gerar thumbnail
   * @returns {Promise<string>} URL do thumbnail
   */
  async generateThumbnail(file) {
    return new Promise(resolve => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.readAsDataURL(file);
      } else {
        // Thumbnail padrão para não-imagens
        resolve(null);
      }
    });
  }
}

// Instância singleton do serviço
const assetService = new AssetService();

export default assetService;
