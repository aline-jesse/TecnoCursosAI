/**
 * TemplatePreview - Componente de Preview Individual de Template
 * TecnoCursos AI - Sistema de Templates
 *
 * Exibe uma prévia visual de um template individual com informações
 * básicas e estado de seleção.
 */

import React from 'react';
import {
  ClockIcon,
  TagIcon,
  SparklesIcon,
  UserIcon,
  PhotoIcon,
  ChatBubbleLeftRightIcon,
  StarIcon,
} from '@heroicons/react/24/outline';
import { TemplatePreviewProps } from '../types/template';
import { CATEGORY_NAMES } from '../data/sceneTemplates';
import './TemplatePreview.css';

/**
 * Componente de prévia de template individual
 */
const TemplatePreview: React.FC<TemplatePreviewProps> = ({
  template,
  isSelected = false,
  onClick,
  showDetails = true,
}) => {
  // Handler para clique no template
  const handleClick = () => {
    onClick(template);
  };

  // Contar elementos por tipo para exibir informações
  const elementCounts = {
    text: template.elements.filter(el => el.type === 'text').length,
    image: template.elements.filter(el => el.type === 'image').length,
    avatar: template.elements.filter(el => el.type === 'avatar').length,
    effect: template.elements.filter(el => el.type === 'effect').length,
  };

  // Determinar cor da categoria
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      opening: '#4CAF50',
      alert: '#FF5722',
      checklist: '#2196F3',
      comparison: '#FF9800',
      testimonial: '#9C27B0',
      'call-to-action': '#F44336',
      closing: '#607D8B',
      transition: '#795548',
      educational: '#3F51B5',
      promotional: '#E91E63',
    };
    return colors[category] || '#9E9E9E';
  };

  // Determinar ícone da dificuldade
  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return '⭐';
      case 'intermediate':
        return '⭐⭐';
      case 'advanced':
        return '⭐⭐⭐';
      default:
        return '⭐';
    }
  };

  return (
    <div
      className={`template-preview ${isSelected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      {/* Thumbnail do template */}
      <div className='template-thumbnail'>
        <img
          src={template.thumbnail}
          alt={template.name}
          onError={e => {
            // Fallback para imagem padrão
            (e.target as HTMLImageElement).src =
              '/templates/default-thumbnail.jpg';
          }}
        />

        {/* Overlay com categoria e duração */}
        <div className='thumbnail-overlay'>
          <div
            className='category-badge'
            style={{ backgroundColor: getCategoryColor(template.category) }}
          >
            {CATEGORY_NAMES[template.category]}
          </div>

          <div className='duration-badge'>
            <ClockIcon className='w-4 h-4' />
            {template.duration}s
          </div>
        </div>

        {/* Indicador de seleção */}
        {isSelected && (
          <div className='selection-indicator'>
            <div className='selection-check'>✓</div>
          </div>
        )}
      </div>

      {/* Informações do template */}
      <div className='template-info'>
        <h3 className='template-name'>{template.name}</h3>

        {showDetails && (
          <>
            <p className='template-description'>{template.description}</p>

            {/* Metadados */}
            <div className='template-metadata'>
              {/* Dificuldade */}
              <div className='metadata-item'>
                <StarIcon className='w-4 h-4' />
                <span className={`difficulty ${template.difficulty}`}>
                  {getDifficultyIcon(template.difficulty)}
                  {template.difficulty === 'beginner'
                    ? 'Iniciante'
                    : template.difficulty === 'intermediate'
                      ? 'Intermediário'
                      : 'Avançado'}
                </span>
              </div>

              {/* Elementos inclusos */}
              <div className='elements-summary'>
                {elementCounts.text > 0 && (
                  <div className='element-count' title='Textos'>
                    <ChatBubbleLeftRightIcon className='w-4 h-4' />
                    {elementCounts.text}
                  </div>
                )}

                {elementCounts.image > 0 && (
                  <div className='element-count' title='Imagens'>
                    <PhotoIcon className='w-4 h-4' />
                    {elementCounts.image}
                  </div>
                )}

                {elementCounts.avatar > 0 && (
                  <div className='element-count' title='Avatares'>
                    <UserIcon className='w-4 h-4' />
                    {elementCounts.avatar}
                  </div>
                )}

                {elementCounts.effect > 0 && (
                  <div className='element-count' title='Efeitos'>
                    <SparklesIcon className='w-4 h-4' />
                    {elementCounts.effect}
                  </div>
                )}
              </div>
            </div>

            {/* Tags principais (máximo 3) */}
            {template.tags.length > 0 && (
              <div className='template-tags'>
                <TagIcon className='w-4 h-4' />
                <div className='tags-list'>
                  {template.tags.slice(0, 3).map(tag => (
                    <span key={tag} className='tag'>
                      {tag}
                    </span>
                  ))}
                  {template.tags.length > 3 && (
                    <span className='more-tags'>
                      +{template.tags.length - 3}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Indicadores especiais */}
            <div className='template-features'>
              {template.audio?.backgroundMusic && (
                <div
                  className='feature-indicator'
                  title='Inclui música de fundo'
                >
                  🎵
                </div>
              )}

              {template.audio?.soundEffects &&
                template.audio.soundEffects.length > 0 && (
                  <div
                    className='feature-indicator'
                    title='Inclui efeitos sonoros'
                  >
                    🔊
                  </div>
                )}

              {template.elements.some(
                el => el.type === 'avatar' && el.speech
              ) && (
                <div className='feature-indicator' title='Avatar com fala'>
                  💬
                </div>
              )}

              {template.elements.some(el => el.type === 'effect') && (
                <div
                  className='feature-indicator'
                  title='Inclui efeitos visuais'
                >
                  ✨
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Estado de hover */}
      <div className='template-hover-overlay'>
        <div className='hover-content'>
          <p>Clique para selecionar</p>
          {!isSelected && (
            <div className='preview-hint'>👁️ Preview disponível</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplatePreview;
