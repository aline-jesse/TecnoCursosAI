/**
 * Serviço de Cenas/Slides - TecnoCursos AI
 *
 * Gerencia as cenas (slides) de um projeto:
 * - Criar, editar e deletar cenas
 * - Reordenar cenas
 * - Gerenciar assets (imagens, vídeos) das cenas
 * - Configurar tempo e transições
 * - Atualização em lote
 */

import api from './api';
import { API_ENDPOINTS } from '../config/api.config';

class SceneService {
  /**
   * Criar nova cena
   *
   * @param {Object} sceneData - Dados da cena
   * @param {string} sceneData.projectId - ID do projeto
   * @param {string} sceneData.title - Título da cena
   * @param {string} sceneData.content - Conteúdo/texto da cena
   * @param {number} sceneData.duration - Duração em segundos
   * @param {number} sceneData.order - Ordem da cena
   * @param {string} sceneData.transition - Tipo de transição
   * @param {Array} sceneData.assets - Array de assets (imagens, vídeos)
   * @param {Object} sceneData.settings - Configurações adicionais
   * @returns {Promise<Object>} Cena criada
   */
  async createScene(sceneData) {
    try {
      const response = await api.post(API_ENDPOINTS.scenes.create, {
        project_id: sceneData.projectId,
        title: sceneData.title,
        content: sceneData.content,
        duration: sceneData.duration || 5,
        order: sceneData.order || 0,
        transition: sceneData.transition || 'fade',
        assets: sceneData.assets || [],
        settings: sceneData.settings || {},
        narration_text: sceneData.narrationText,
        voice_settings: sceneData.voiceSettings,
      });

      // Limpar cache do projeto
      // clearCache(API_ENDPOINTS.projects.scenes(sceneData.projectId));

      return response.data;
    } catch (error) {
      console.error('Erro ao criar cena:', error);
      throw error;
    }
  }

  /**
   * Atualizar cena existente
   *
   * @param {string} sceneId - ID da cena
   * @param {Object} updates - Dados a atualizar
   * @returns {Promise<Object>} Cena atualizada
   */
  async updateScene(sceneId, updates) {
    try {
      const response = await api.put(
        API_ENDPOINTS.scenes.update(sceneId),
        updates
      );

      // Limpar cache
      if (updates.projectId) {
        // clearCache(API_ENDPOINTS.projects.scenes(updates.projectId));
      }

      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar cena:', error);
      throw error;
    }
  }

  /**
   * Deletar cena
   *
   * @param {string} sceneId - ID da cena
   * @param {string} projectId - ID do projeto (para limpar cache)
   * @returns {Promise<void>}
   */
  async deleteScene(sceneId, projectId) {
    try {
      await api.delete(API_ENDPOINTS.scenes.delete(sceneId));

      // Limpar cache do projeto
      if (projectId) {
        // clearCache(API_ENDPOINTS.projects.scenes(projectId));
      }
    } catch (error) {
      console.error('Erro ao deletar cena:', error);
      throw error;
    }
  }

  /**
   * Reordenar cenas do projeto
   *
   * @param {string} projectId - ID do projeto
   * @param {Array<{id: string, order: number}>} sceneOrder - Nova ordem das cenas
   * @returns {Promise<void>}
   */
  async reorderScenes(projectId, sceneOrder) {
    try {
      await api.post(API_ENDPOINTS.scenes.reorder, {
        project_id: projectId,
        scene_order: sceneOrder,
      });

      // Limpar cache
      // clearCache(API_ENDPOINTS.projects.scenes(projectId));
    } catch (error) {
      console.error('Erro ao reordenar cenas:', error);
      throw error;
    }
  }

  /**
   * Atualizar múltiplas cenas de uma vez
   *
   * @param {Array<{id: string, updates: Object}>} scenesUpdates - Array de atualizações
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Array>} Cenas atualizadas
   */
  async bulkUpdateScenes(scenesUpdates, projectId) {
    try {
      const response = await api.post(API_ENDPOINTS.scenes.bulkUpdate, {
        scenes: scenesUpdates,
        project_id: projectId,
      });

      // Limpar cache
      // clearCache(API_ENDPOINTS.projects.scenes(projectId));

      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar cenas em lote:', error);
      throw error;
    }
  }

  /**
   * Adicionar asset a uma cena
   *
   * @param {string} sceneId - ID da cena
   * @param {Object} asset - Dados do asset
   * @param {string} asset.type - Tipo do asset (image, video, audio)
   * @param {string} asset.url - URL do asset
   * @param {string} asset.name - Nome do asset
   * @param {Object} asset.position - Posição do asset {x, y, width, height}
   * @param {number} asset.startTime - Tempo de início (para vídeos/áudios)
   * @param {number} asset.endTime - Tempo de fim
   * @returns {Promise<Object>} Cena atualizada
   */
  async addAssetToScene(sceneId, asset) {
    try {
      // Primeiro, obter a cena atual
      const currentScene = await this.getScene(sceneId);

      // Adicionar o novo asset
      const updatedAssets = [...(currentScene.assets || []), asset];

      // Atualizar a cena
      return await this.updateScene(sceneId, { assets: updatedAssets });
    } catch (error) {
      console.error('Erro ao adicionar asset:', error);
      throw error;
    }
  }

  /**
   * Remover asset de uma cena
   *
   * @param {string} sceneId - ID da cena
   * @param {string} assetId - ID do asset a remover
   * @returns {Promise<Object>} Cena atualizada
   */
  async removeAssetFromScene(sceneId, assetId) {
    try {
      // Obter cena atual
      const currentScene = await this.getScene(sceneId);

      // Filtrar assets removendo o especificado
      const updatedAssets = (currentScene.assets || []).filter(
        asset => asset.id !== assetId
      );

      // Atualizar a cena
      return await this.updateScene(sceneId, { assets: updatedAssets });
    } catch (error) {
      console.error('Erro ao remover asset:', error);
      throw error;
    }
  }

  /**
   * Duplicar cena
   *
   * @param {string} sceneId - ID da cena a duplicar
   * @param {string} projectId - ID do projeto
   * @returns {Promise<Object>} Nova cena criada
   */
  async duplicateScene(sceneId, projectId) {
    try {
      // Obter cena original
      const originalScene = await this.getScene(sceneId);

      // Criar cópia com nova ordem
      const sceneCopy = {
        ...originalScene,
        projectId,
        title: `${originalScene.title} (Cópia)`,
        order: originalScene.order + 0.5, // Inserir após a original
      };

      delete sceneCopy.id;
      delete sceneCopy.created_at;
      delete sceneCopy.updated_at;

      return await this.createScene(sceneCopy);
    } catch (error) {
      console.error('Erro ao duplicar cena:', error);
      throw error;
    }
  }

  /**
   * Obter uma cena específica (helper interno)
   * @private
   */
  async getScene(sceneId) {
    // Como não temos endpoint específico, vamos buscar do projeto
    // Esta é uma implementação simplificada
    const response = await api.get(`/api/scenes/${sceneId}`);
    return response.data;
  }

  /**
   * Aplicar template a uma cena
   *
   * @param {string} sceneId - ID da cena
   * @param {Object} template - Template a aplicar
   * @returns {Promise<Object>} Cena atualizada
   */
  async applyTemplate(sceneId, template) {
    try {
      const updates = {
        template_id: template.id,
        settings: {
          ...template.defaultSettings,
          templateName: template.name,
        },
        transition: template.defaultTransition || 'fade',
        duration: template.defaultDuration || 5,
      };

      return await this.updateScene(sceneId, updates);
    } catch (error) {
      console.error('Erro ao aplicar template:', error);
      throw error;
    }
  }

  /**
   * Gerar preview de uma cena
   *
   * @param {string} sceneId - ID da cena
   * @returns {Promise<string>} URL do preview
   */
  async generateScenePreview(sceneId) {
    try {
      const response = await api.post(`/api/scenes/${sceneId}/preview`);
      return response.data.preview_url;
    } catch (error) {
      console.error('Erro ao gerar preview:', error);
      throw error;
    }
  }

  /**
   * Validar dados da cena antes de salvar
   *
   * @param {Object} sceneData - Dados da cena
   * @returns {Object} { valid: boolean, errors?: Array }
   */
  validateSceneData(sceneData) {
    const errors = [];

    // Validar campos obrigatórios
    if (!sceneData.title || sceneData.title.trim().length === 0) {
      errors.push('Título é obrigatório');
    }

    if (!sceneData.projectId) {
      errors.push('ID do projeto é obrigatório');
    }

    // Validar duração
    if (
      sceneData.duration &&
      (sceneData.duration < 1 || sceneData.duration > 300)
    ) {
      errors.push('Duração deve estar entre 1 e 300 segundos');
    }

    // Validar assets
    if (sceneData.assets && Array.isArray(sceneData.assets)) {
      sceneData.assets.forEach((asset, index) => {
        if (!asset.type || !asset.url) {
          errors.push(`Asset ${index + 1} deve ter tipo e URL`);
        }
      });
    }

    return {
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined,
    };
  }
}

// Exportar instância única do serviço
export default new SceneService();
