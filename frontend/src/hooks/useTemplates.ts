/**
 * Hook useTemplates - Gerenciamento de Templates de Cena
 * TecnoCursos AI - Sistema de Templates
 *
 * Este hook gerencia toda a lógica de templates, incluindo aplicação
 * de templates às cenas e integração com o store do editor.
 */

import { useCallback, useState } from 'react';
import {
  SCENE_TEMPLATES,
  TEMPLATE_CATEGORIES,
  getTemplateById,
  getTemplatesByCategory,
  searchTemplates as searchTemplatesData,
} from '../data/sceneTemplates';
import { useEditorStore } from '../store/editorStore';
import {
  CharacterElement,
  EditorElement,
  ImageElement,
  Scene,
  SceneBackground,
  TextElement,
} from '../types/editor';
import {
  CreateTemplateConfig,
  SceneTemplate,
  TemplateApplicationResult,
  TemplateCategory,
  UseTemplatesResult,
} from '../types/template';

/**
 * Hook principal para gerenciamento de templates
 */
export const useTemplates = (): UseTemplatesResult => {
  // Estados
  const [templates, setTemplates] = useState<SceneTemplate[]>(SCENE_TEMPLATES);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Store do editor para aplicar templates
  const { addScene, updateScene } = useEditorStore();

  /**
   * Buscar templates por categoria
   */
  const getTemplatesByCategoryCallback = useCallback(
    (category: TemplateCategory) => {
      return getTemplatesByCategory(category);
    },
    []
  );

  /**
   * Buscar templates por texto
   */
  const searchTemplates = useCallback((query: string) => {
    return searchTemplatesData(query);
  }, []);

  /**
   * Aplicar um template a uma cena
   * Esta é a função principal que converte um template em uma cena real
   */
  const applyTemplate = useCallback(
    (
      template: SceneTemplate,
      targetSceneId?: string
    ): TemplateApplicationResult => {
      try {
        setLoading(true);
        setError(null);

        console.log(
          `Aplicando template "${template.name}" ${targetSceneId ? `à cena ${targetSceneId}` : 'como nova cena'}`
        );

        // Converter elementos do template para elementos de cena
        const sceneElements: EditorElement[] = template.elements.map(
          (element): EditorElement => {
            const baseElement = {
              id: `${element.type}-${Date.now()}`,
              x: element.position?.x ?? 0,
              y: element.position?.y ?? 0,
              width: 'size' in element ? element.size.width : 200,
              height: 'size' in element ? element.size.height : 100,
              rotation:
                'style' in element &&
                typeof (element as any).style === 'object' &&
                'rotation' in (element as any).style
                  ? (element as any).style.rotation
                  : 0,
              opacity:
                'style' in element &&
                typeof (element as any).style === 'object' &&
                'opacity' in (element as any).style
                  ? (element as any).style.opacity
                  : 1,
            };

            let newElement: EditorElement;
            let textEl: any, imgEl: any, avatarEl: any;
            switch (element.type) {
              case 'text':
                textEl = element as any;
                newElement = {
                  ...baseElement,
                  type: 'text',
                  text: textEl.text,
                  fontSize: textEl.style.fontSize,
                  fontFamily: textEl.style.fontFamily,
                  fill: textEl.style.color,
                } as TextElement;
                break;
              case 'image':
                imgEl = element as any;
                newElement = {
                  ...baseElement,
                  type: 'image',
                  src: imgEl.src,
                } as ImageElement;
                break;
              case 'avatar': // Mapeando avatar para CharacterElement
                avatarEl = element as any;
                newElement = {
                  ...baseElement,
                  type: 'character',
                  src: avatarEl.src || '/assets/characters/student_1.svg',
                } as CharacterElement;
                break;
              default:
                // Para 'effect', não criamos um elemento visível, então retornamos null
                // e filtramos depois. Ou lançamos um erro se for inesperado.
                console.warn(
                  `Tipo de elemento de template não suportado no canvas: ${element.type}`
                );
                throw new Error(
                  `Tipo de elemento de template não suportado no canvas: ${element.type}`
                );
            }
            return newElement;
          }
        );

        // Dados da cena baseados no template
        const sceneData: Partial<Scene> = {
          name: template.name,
          duration: template.duration,
          elements: sceneElements,
        };

        let sceneId: string;
        const appliedElementIds = sceneElements.map(el => el.id);
        const editableElementIds = appliedElementIds; // Simplificado

        // Aplicar à cena existente ou criar nova
        if (targetSceneId) {
          // Atualizar cena existente
          updateScene({
            ...sceneData,
            id: targetSceneId,
            name: sceneData.name || template.name || 'Cena',
            background:
              sceneData.background &&
              (['color', 'image', 'video'] as Array<string>).indexOf(
                sceneData.background.type
              ) !== -1
                ? (sceneData.background as SceneBackground)
                : { type: 'color', value: '#ffffff' },
            elements: sceneData.elements || [],
          });
          sceneId = targetSceneId;
          console.log(`Template aplicado à cena existente: ${targetSceneId}`);
        } else {
          // Criar nova cena
          sceneId = `scene-${Date.now()}`;
          const newScene: Scene = {
            id: sceneId,
            name: template.name || 'Cena',
            duration: template.duration,
            elements: sceneElements || [],
            background:
              template.background &&
              (['color', 'image', 'video'] as Array<string>).indexOf(
                template.background.type
              ) !== -1
                ? (template.background as SceneBackground)
                : { type: 'color', value: '#ffffff' },
          };
          addScene(newScene);
          console.log(`Nova cena criada com template: ${sceneId}`);
        }

        return {
          success: true,
          sceneId,
          appliedElements: appliedElementIds,
          editableElements: editableElementIds,
          message: `Template "${template.name}" aplicado com sucesso! ${editableElementIds.length} elementos podem ser editados.`,
        };
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : 'Erro desconhecido ao aplicar template';
        setError(errorMessage);
        console.error('Erro ao aplicar template:', err);

        return {
          success: false,
          sceneId: '',
          appliedElements: [],
          editableElements: [],
          message: errorMessage,
          errors: [errorMessage],
        };
      } finally {
        setLoading(false);
      }
    },
    [addScene, updateScene]
  );

  /**
   * Criar um novo template baseado em uma cena existente
   */
  const createTemplate = useCallback(
    async (config: CreateTemplateConfig): Promise<SceneTemplate> => {
      try {
        setLoading(true);
        setError(null);

        // Gerar ID único para o novo template
        const templateId = `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Criar o novo template
        const newTemplate: SceneTemplate = {
          id: templateId,
          name: config.name,
          category: config.category,
          description: config.description,
          thumbnail: `/templates/thumbnails/custom-${templateId}.jpg`, // Seria gerado automaticamente
          duration: config.duration,
          background: { ...config.background },
          elements: config.elements as any[], // Cast necessário devido à tipagem parcial
          tags: [...config.tags],
          difficulty: 'intermediate', // Padrão para templates customizados
          createdAt: new Date(),
          updatedAt: new Date(),
          replaceable: {
            // Identificar automaticamente elementos editáveis
            title: config.elements.find(el => el.type === 'text')?.id,
            avatar: config.elements.find(el => el.type === 'avatar')?.id,
            mainImage: config.elements.find(el => el.type === 'image')?.id,
          },
        };

        // Adicionar à lista de templates (em uma implementação real, salvaria no servidor)
        setTemplates((prev: SceneTemplate[]) => [...prev, newTemplate]);

        console.log(
          `Novo template criado: ${newTemplate.name} (${templateId})`
        );
        return newTemplate;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Erro ao criar template';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * Deletar um template
   */
  const deleteTemplate = useCallback(
    async (templateId: string): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        // Verificar se é um template padrão (não pode ser deletado)
        const template = getTemplateById(templateId);
        if (template && !templateId.startsWith('custom-')) {
          throw new Error('Templates padrão não podem ser deletados');
        }

        // Remover da lista
        setTemplates((prev: SceneTemplate[]) =>
          prev.filter((t: SceneTemplate) => t.id !== templateId)
        );

        console.log(`Template deletado: ${templateId}`);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Erro ao deletar template';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * Recarregar templates (útil para sincronizar com servidor)
   */
  const refreshTemplates = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      // Em uma implementação real, faria fetch do servidor
      // Por enquanto, apenas reseta para os templates padrão
      setTemplates(SCENE_TEMPLATES);

      console.log('Templates recarregados');
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao recarregar templates';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    templates,
    categories: TEMPLATE_CATEGORIES,
    loading,
    error,
    getTemplatesByCategory: getTemplatesByCategoryCallback,
    searchTemplates,
    applyTemplate,
    createTemplate,
    deleteTemplate,
    refreshTemplates,
  };
};

/**
 * Hook para gerenciar estado da galeria de templates
 */
export const useTemplateGallery = () => {
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] =
    useState<SceneTemplate | null>(null);
  const [currentCategory, setCurrentCategory] = useState<
    TemplateCategory | 'all'
  >('all');
  const [searchQuery, setSearchQuery] = useState('');

  const openGallery = useCallback((category?: TemplateCategory) => {
    if (category) {
      setCurrentCategory(category);
    }
    setIsGalleryOpen(true);
  }, []);

  const closeGallery = useCallback(() => {
    setIsGalleryOpen(false);
    setSelectedTemplate(null);
    setSearchQuery('');
  }, []);

  const selectTemplate = useCallback((template: SceneTemplate) => {
    setSelectedTemplate(template);
  }, []);

  return {
    isGalleryOpen,
    selectedTemplate,
    currentCategory,
    searchQuery,
    setCurrentCategory,
    setSearchQuery,
    openGallery,
    closeGallery,
    selectTemplate,
  };
};

export default useTemplates;
