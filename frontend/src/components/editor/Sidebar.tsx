import React from 'react';
import { EditorElement, TextElement } from '../../types';
import { Accordion } from '../common/Accordion';
import { ColorPicker } from '../common/ColorPicker';
import { FontPicker } from '../common/FontPicker';
import { GradientPicker } from '../common/GradientPicker';
import { NumberInput } from '../common/NumberInput';
import { PatternPicker } from '../common/PatternPicker';
import { Select } from '../common/Select';
import { ShadowPicker } from '../common/ShadowPicker';
import { TextInput } from '../common/TextInput';
import './Sidebar.css';

interface SidebarProps {
  selectedElement: EditorElement | null;
  onElementUpdate: (element: EditorElement) => void;
  readOnly?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  selectedElement,
  onElementUpdate,
  readOnly = false,
}) => {
  if (!selectedElement) {
    return (
      <div className="sidebar">
        <div className="sidebar-empty">
          Selecione um elemento para editar suas propriedades
        </div>
      </div>
    );
  }

  const handleChange = <T extends keyof EditorElement>(
    property: T,
    value: EditorElement[T]
  ) => {
    if (readOnly) return;
    onElementUpdate({
      ...selectedElement,
      [property]: value,
    });
  };

  const isTextElement = (element: EditorElement): element is TextElement => {
    return element.type === 'text';
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>{selectedElement.type}</h3>
      </div>

      <div className="sidebar-content">
        <Accordion title="Posição e Tamanho" defaultOpen>
          <div className="property-group">
            <NumberInput
              label="X"
              value={selectedElement.x}
              onChange={value => handleChange('x', value)}
              min={0}
              step={1}
              disabled={readOnly}
            />
            <NumberInput
              label="Y"
              value={selectedElement.y}
              onChange={value => handleChange('y', value)}
              min={0}
              step={1}
              disabled={readOnly}
            />
          </div>
          <div className="property-group">
            <NumberInput
              label="Largura"
              value={selectedElement.width}
              onChange={value => handleChange('width', value)}
              min={1}
              step={1}
              disabled={readOnly}
            />
            <NumberInput
              label="Altura"
              value={selectedElement.height}
              onChange={value => handleChange('height', value)}
              min={1}
              step={1}
              disabled={readOnly}
            />
          </div>
          <div className="property-group">
            <NumberInput
              label="Rotação"
              value={selectedElement.rotation || 0}
              onChange={value => handleChange('rotation', value)}
              min={-360}
              max={360}
              step={1}
              disabled={readOnly}
            />
          </div>
        </Accordion>

        {isTextElement(selectedElement) && (
          <Accordion title="Texto" defaultOpen>
            <TextInput
              label="Conteúdo"
              value={selectedElement.text}
              onChange={value => handleChange('text', value)}
              multiline
              disabled={readOnly}
            />
            <FontPicker
              label="Fonte"
              value={selectedElement.fontFamily}
              onChange={value => handleChange('fontFamily', value)}
              disabled={readOnly}
            />
            <NumberInput
              label="Tamanho"
              value={selectedElement.fontSize}
              onChange={value => handleChange('fontSize', value)}
              min={1}
              step={1}
              disabled={readOnly}
            />
            <Select
              label="Alinhamento"
              value={selectedElement.textAlign || 'left'}
              options={[
                { value: 'left', label: 'Esquerda' },
                { value: 'center', label: 'Centro' },
                { value: 'right', label: 'Direita' },
              ]}
              onChange={value => handleChange('textAlign', value)}
              disabled={readOnly}
            />
          </Accordion>
        )}

        <Accordion title="Estilo" defaultOpen>
          <ColorPicker
            label="Cor de Preenchimento"
            value={selectedElement.fill || '#000000'}
            onChange={value => handleChange('fill', value)}
            disabled={readOnly}
          />
          <ColorPicker
            label="Cor da Borda"
            value={selectedElement.stroke || 'transparent'}
            onChange={value => handleChange('stroke', value)}
            disabled={readOnly}
          />
          <NumberInput
            label="Espessura da Borda"
            value={selectedElement.strokeWidth || 0}
            onChange={value => handleChange('strokeWidth', value)}
            min={0}
            step={1}
            disabled={readOnly}
          />
          <NumberInput
            label="Opacidade"
            value={selectedElement.opacity || 1}
            onChange={value => handleChange('opacity', value)}
            min={0}
            max={1}
            step={0.1}
            disabled={readOnly}
          />
        </Accordion>

        <Accordion title="Gradiente">
          <GradientPicker
            value={selectedElement.gradient}
            onChange={value => handleChange('gradient', value)}
            disabled={readOnly}
          />
        </Accordion>

        <Accordion title="Sombra">
          <ShadowPicker
            value={selectedElement.shadow}
            onChange={value => handleChange('shadow', value)}
            disabled={readOnly}
          />
        </Accordion>

        <Accordion title="Padrão">
          <PatternPicker
            value={selectedElement.pattern}
            onChange={value => handleChange('pattern', value)}
            disabled={readOnly}
          />
        </Accordion>
      </div>
    </div>
  );
};
