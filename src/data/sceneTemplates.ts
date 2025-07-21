/**
 * Templates de Cena Pré-definidos
 * TecnoCursos AI - Sistema de Templates
 * 
 * Este arquivo contém todos os templates prontos para uso.
 * Para adicionar um novo template, siga o padrão dos existentes.
 */

import { SceneTemplate, TemplateCategory } from '../types/template'

/**
 * COMO ADICIONAR UM NOVO TEMPLATE:
 * 
 * 1. Defina os elementos (texto, imagem, avatar, efeitos)
 * 2. Configure o background (cor, gradiente ou imagem)
 * 3. Defina a duração da cena
 * 4. Especifique quais elementos são editáveis pelo usuário
 * 5. Adicione tags relevantes para busca
 * 6. Crie uma thumbnail representativa (400x300px recomendado)
 * 7. Adicione o template ao array SCENE_TEMPLATES
 */

export const SCENE_TEMPLATES: SceneTemplate[] = [
  // ==================== TEMPLATES DE ABERTURA ====================
  {
    id: 'opening-corporate',
    name: 'Abertura Corporativa',
    category: 'opening' as TemplateCategory,
    description: 'Template profissional para abertura de vídeos corporativos',
    thumbnail: '/templates/thumbnails/opening-corporate.jpg',
    duration: 8,
    background: {
      type: 'gradient',
      value: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      overlay: {
        color: '#000000',
        opacity: 0.3
      }
    },
    elements: [
      {
        type: 'text',
        id: 'main-title',
        content: 'SEU TÍTULO AQUI',
        position: { x: 960, y: 400 },
        style: {
          fontSize: 72,
          fontFamily: 'Arial Black',
          color: '#FFFFFF',
          fontWeight: 'bold',
          textAlign: 'center',
          textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
          animation: 'fadeInUp'
        },
        editable: true
      },
      {
        type: 'text',
        id: 'subtitle',
        content: 'Subtítulo ou descrição aqui',
        position: { x: 960, y: 500 },
        style: {
          fontSize: 28,
          fontFamily: 'Arial',
          color: '#E0E0E0',
          fontWeight: 'normal',
          textAlign: 'center',
          animation: 'fadeInUp'
        },
        editable: true
      },
      {
        type: 'effect',
        id: 'particles-effect',
        effectType: 'particles',
        properties: {
          duration: 8,
          intensity: 0.6,
          color: '#FFFFFF'
        }
      }
    ],
    audio: {
      backgroundMusic: {
        src: '/audio/corporate-intro.mp3',
        volume: 0.3,
        loop: false
      }
    },
    tags: ['abertura', 'corporativo', 'profissional', 'negócios'],
    difficulty: 'beginner',
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    replaceable: {
      title: 'main-title',
      subtitle: 'subtitle'
    }
  },

  {
    id: 'opening-creative',
    name: 'Abertura Criativa',
    category: 'opening' as TemplateCategory,
    description: 'Template colorido e dinâmico para conteúdo criativo',
    thumbnail: '/templates/thumbnails/opening-creative.jpg',
    duration: 6,
    background: {
      type: 'gradient',
      value: 'linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4)'
    },
    elements: [
      {
        type: 'text',
        id: 'creative-title',
        content: 'SEJA CRIATIVO!',
        position: { x: 960, y: 350 },
        style: {
          fontSize: 80,
          fontFamily: 'Comic Sans MS',
          color: '#FFFFFF',
          fontWeight: 'bold',
          textAlign: 'center',
          textShadow: '3px 3px 0px #FF1744',
          animation: 'bounce'
        },
        editable: true
      },
      {
        type: 'avatar',
        id: 'creative-avatar',
        avatarType: 'robot',
        position: { x: 200, y: 400 },
        size: { width: 200, height: 300 },
        style: {
          animation: 'wave',
          expression: 'excited'
        },
        speech: {
          text: 'Olá! Vamos começar algo incrível!',
          voice: 'robotic',
          duration: 3
        },
        editable: true
      },
      {
        type: 'effect',
        id: 'glow-effect',
        effectType: 'glow',
        properties: {
          duration: 6,
          intensity: 0.8,
          color: '#FFD700'
        }
      }
    ],
    tags: ['criativo', 'colorido', 'divertido', 'avatar'],
    difficulty: 'intermediate',
    createdAt: new Date('2024-01-02'),
    updatedAt: new Date('2024-01-02'),
    replaceable: {
      title: 'creative-title',
      avatar: 'creative-avatar'
    }
  },

  // ==================== TEMPLATES DE ALERTA ====================
  {
    id: 'alert-warning',
    name: 'Alerta de Aviso',
    category: 'alert' as TemplateCategory,
    description: 'Template para avisos importantes e alertas',
    thumbnail: '/templates/thumbnails/alert-warning.jpg',
    duration: 5,
    background: {
      type: 'gradient',
      value: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)',
      overlay: {
        color: '#FF5722',
        opacity: 0.1
      }
    },
    elements: [
      {
        type: 'image',
        id: 'warning-icon',
        src: '/icons/warning-triangle.svg',
        position: { x: 860, y: 200 },
        size: { width: 200, height: 200 },
        style: {
          opacity: 1,
          borderRadius: 0,
          animation: 'pulse'
        },
        editable: false
      },
      {
        type: 'text',
        id: 'alert-title',
        content: 'ATENÇÃO!',
        position: { x: 960, y: 450 },
        style: {
          fontSize: 64,
          fontFamily: 'Arial Black',
          color: '#D32F2F',
          fontWeight: 'bold',
          textAlign: 'center',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
        },
        editable: true
      },
      {
        type: 'text',
        id: 'alert-message',
        content: 'Sua mensagem importante aqui',
        position: { x: 960, y: 550 },
        style: {
          fontSize: 32,
          fontFamily: 'Arial',
          color: '#424242',
          fontWeight: 'normal',
          textAlign: 'center'
        },
        editable: true
      },
      {
        type: 'effect',
        id: 'shake-effect',
        effectType: 'shake',
        properties: {
          duration: 1,
          intensity: 0.5,
          direction: 'up'
        }
      }
    ],
    audio: {
      soundEffects: [
        {
          id: 'alert-sound',
          src: '/audio/alert-beep.mp3',
          trigger: 'start',
          volume: 0.7
        }
      ]
    },
    tags: ['alerta', 'aviso', 'atenção', 'importante'],
    difficulty: 'beginner',
    createdAt: new Date('2024-01-03'),
    updatedAt: new Date('2024-01-03'),
    replaceable: {
      title: 'alert-title',
      subtitle: 'alert-message'
    }
  },

  // ==================== TEMPLATES DE CHECKLIST ====================
  {
    id: 'checklist-steps',
    name: 'Lista de Passos',
    category: 'checklist' as TemplateCategory,
    description: 'Template para apresentar lista de passos ou itens',
    thumbnail: '/templates/thumbnails/checklist-steps.jpg',
    duration: 10,
    background: {
      type: 'color',
      value: '#F8F9FA'
    },
    elements: [
      {
        type: 'text',
        id: 'checklist-title',
        content: 'PASSOS IMPORTANTES',
        position: { x: 960, y: 150 },
        style: {
          fontSize: 48,
          fontFamily: 'Arial Black',
          color: '#2E7D32',
          fontWeight: 'bold',
          textAlign: 'center'
        },
        editable: true
      },
      {
        type: 'text',
        id: 'step-1',
        content: '✓ Primeiro passo aqui',
        position: { x: 480, y: 300 },
        style: {
          fontSize: 36,
          fontFamily: 'Arial',
          color: '#424242',
          fontWeight: 'normal',
          textAlign: 'left',
          animation: 'slideInLeft'
        },
        editable: true
      },
      {
        type: 'text',
        id: 'step-2',
        content: '✓ Segundo passo aqui',
        position: { x: 480, y: 380 },
        style: {
          fontSize: 36,
          fontFamily: 'Arial',
          color: '#424242',
          fontWeight: 'normal',
          textAlign: 'left',
          animation: 'slideInLeft'
        },
        editable: true
      },
      {
        type: 'text',
        id: 'step-3',
        content: '✓ Terceiro passo aqui',
        position: { x: 480, y: 460 },
        style: {
          fontSize: 36,
          fontFamily: 'Arial',
          color: '#424242',
          fontWeight: 'normal',
          textAlign: 'left',
          animation: 'slideInLeft'
        },
        editable: true
      },
      {
        type: 'avatar',
        id: 'checklist-avatar',
        avatarType: 'female',
        position: { x: 1400, y: 300 },
        size: { width: 300, height: 400 },
        style: {
          expression: 'happy'
        },
        speech: {
          text: 'Siga estes passos para ter sucesso!',
          voice: 'female',
          duration: 4
        },
        editable: true
      }
    ],
    tags: ['checklist', 'passos', 'lista', 'organização'],
    difficulty: 'intermediate',
    createdAt: new Date('2024-01-04'),
    updatedAt: new Date('2024-01-04'),
    replaceable: {
      title: 'checklist-title',
      avatar: 'checklist-avatar'
    }
  },

  // ==================== TEMPLATES DE ENCERRAMENTO ====================
  {
    id: 'closing-thankyou',
    name: 'Agradecimento',
    category: 'closing' as TemplateCategory,
    description: 'Template de encerramento com agradecimento',
    thumbnail: '/templates/thumbnails/closing-thankyou.jpg',
    duration: 6,
    background: {
      type: 'gradient',
      value: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    elements: [
      {
        type: 'text',
        id: 'thank-you-title',
        content: 'OBRIGADO!',
        position: { x: 960, y: 350 },
        style: {
          fontSize: 80,
          fontFamily: 'Arial Black',
          color: '#FFFFFF',
          fontWeight: 'bold',
          textAlign: 'center',
          textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
          animation: 'fadeIn'
        },
        editable: true
      },
      {
        type: 'text',
        id: 'subscribe-message',
        content: 'Inscreva-se e ative o sininho!',
        position: { x: 960, y: 450 },
        style: {
          fontSize: 32,
          fontFamily: 'Arial',
          color: '#E0E0E0',
          fontWeight: 'normal',
          textAlign: 'center',
          animation: 'fadeIn'
        },
        editable: true
      },
      {
        type: 'effect',
        id: 'confetti-effect',
        effectType: 'particles',
        properties: {
          duration: 6,
          intensity: 1.0,
          color: '#FFD700'
        }
      }
    ],
    audio: {
      backgroundMusic: {
        src: '/audio/thank-you-music.mp3',
        volume: 0.4,
        loop: false
      }
    },
    tags: ['encerramento', 'obrigado', 'fim', 'inscrever'],
    difficulty: 'beginner',
    createdAt: new Date('2024-01-05'),
    updatedAt: new Date('2024-01-05'),
    replaceable: {
      title: 'thank-you-title',
      subtitle: 'subscribe-message'
    }
  },

  // ==================== TEMPLATES DE CALL TO ACTION ====================
  {
    id: 'cta-subscribe',
    name: 'Call to Action - Inscrição',
    category: 'call-to-action' as TemplateCategory,
    description: 'Template para incentivar inscrições e engajamento',
    thumbnail: '/templates/thumbnails/cta-subscribe.jpg',
    duration: 8,
    background: {
      type: 'gradient',
      value: 'linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%)'
    },
    elements: [
      {
        type: 'text',
        id: 'cta-title',
        content: 'GOSTOU DO CONTEÚDO?',
        position: { x: 960, y: 250 },
        style: {
          fontSize: 56,
          fontFamily: 'Arial Black',
          color: '#FFFFFF',
          fontWeight: 'bold',
          textAlign: 'center',
          textShadow: '2px 2px 4px rgba(0,0,0,0.5)'
        },
        editable: true
      },
      {
        type: 'text',
        id: 'cta-action',
        content: '👍 CURTA | 🔔 INSCREVA-SE | 💬 COMENTE',
        position: { x: 960, y: 450 },
        style: {
          fontSize: 40,
          fontFamily: 'Arial',
          color: '#FFFFFF',
          fontWeight: 'bold',
          textAlign: 'center',
          animation: 'pulse'
        },
        editable: true
      },
      {
        type: 'avatar',
        id: 'cta-avatar',
        avatarType: 'male',
        position: { x: 1400, y: 350 },
        size: { width: 250, height: 350 },
        style: {
          animation: 'point',
          expression: 'excited'
        },
        speech: {
          text: 'Não esqueça de curtir e se inscrever!',
          voice: 'male',
          duration: 4
        },
        editable: true
      },
      {
        type: 'effect',
        id: 'zoom-effect',
        effectType: 'zoom',
        properties: {
          duration: 2,
          intensity: 1.2,
          direction: 'up'
        }
      }
    ],
    tags: ['cta', 'inscrever', 'curtir', 'engajamento'],
    difficulty: 'intermediate',
    createdAt: new Date('2024-01-06'),
    updatedAt: new Date('2024-01-06'),
    replaceable: {
      title: 'cta-title',
      subtitle: 'cta-action',
      avatar: 'cta-avatar'
    }
  }
]

/**
 * Categorias disponíveis de templates
 */
export const TEMPLATE_CATEGORIES: TemplateCategory[] = [
  'opening',
  'alert',
  'checklist',
  'comparison',
  'testimonial',
  'call-to-action',
  'closing',
  'transition',
  'educational',
  'promotional'
]

/**
 * Mapeamento de categorias para nomes em português
 */
export const CATEGORY_NAMES: Record<TemplateCategory, string> = {
  opening: 'Abertura',
  alert: 'Alerta',
  checklist: 'Lista/Checklist',
  comparison: 'Comparação',
  testimonial: 'Depoimento',
  'call-to-action': 'Call to Action',
  closing: 'Encerramento',
  transition: 'Transição',
  educational: 'Educacional',
  promotional: 'Promocional'
}

/**
 * Função utilitária para buscar templates por categoria
 */
export const getTemplatesByCategory = (category: TemplateCategory): SceneTemplate[] => {
  return SCENE_TEMPLATES.filter(template => template.category === category)
}

/**
 * Função utilitária para buscar templates por texto
 */
export const searchTemplates = (query: string): SceneTemplate[] => {
  const lowerQuery = query.toLowerCase()
  return SCENE_TEMPLATES.filter(template => 
    template.name.toLowerCase().includes(lowerQuery) ||
    template.description.toLowerCase().includes(lowerQuery) ||
    template.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
  )
}

/**
 * Função para obter um template por ID
 */
export const getTemplateById = (id: string): SceneTemplate | null => {
  return SCENE_TEMPLATES.find(template => template.id === id) || null
}

export default SCENE_TEMPLATES