import React from 'react';
import { PatternConfig } from '../../types';
import { ColorPicker } from './ColorPicker';
import { NumberInput } from './NumberInput';
import './PatternPicker.css';
import { Select } from './Select';

interface PatternPickerProps {
  value?: PatternConfig;
  onChange: (value: PatternConfig) => void;
  disabled?: boolean;
}

const DEFAULT_PATTERN: PatternConfig = {
  type: 'dots',
  color: '#000000',
  backgroundColor: '#ffffff',
  size: 10,
  spacing: 20,
  angle: 0,
  opacity: 1,
};

export const PatternPicker: React.FC<PatternPickerProps> = ({
  value = DEFAULT_PATTERN,
  onChange,
  disabled = false,
}) => {
  const handleTypeChange = (type: PatternConfig['type']) => {
    onChange({ ...value, type });
  };

  const handleColorChange = (color: string) => {
    onChange({ ...value, color });
  };

  const handleBackgroundColorChange = (backgroundColor: string) => {
    onChange({ ...value, backgroundColor });
  };

  const handleSizeChange = (size: number) => {
    onChange({ ...value, size });
  };

  const handleSpacingChange = (spacing: number) => {
    onChange({ ...value, spacing });
  };

  const handleAngleChange = (angle: number) => {
    onChange({ ...value, angle });
  };

  const handleOpacityChange = (opacity: number) => {
    onChange({ ...value, opacity });
  };

  return (
    <div className="pattern-picker">
      <Select
        label="Tipo"
        value={value.type}
        options={[
          { value: 'dots', label: 'Pontos' },
          { value: 'lines', label: 'Linhas' },
          { value: 'grid', label: 'Grade' },
          { value: 'crosshatch', label: 'Hachurado' },
        ]}
        onChange={handleTypeChange}
        disabled={disabled}
      />

      <div
        className="pattern-preview"
        style={{ background: getPatternStyle(value) }}
      />

      <ColorPicker
        label="Cor"
        value={value.color}
        onChange={handleColorChange}
        disabled={disabled}
      />

      <ColorPicker
        label="Cor de Fundo"
        value={value.backgroundColor}
        onChange={handleBackgroundColorChange}
        disabled={disabled}
      />

      <NumberInput
        label="Tamanho"
        value={value.size}
        onChange={handleSizeChange}
        min={1}
        max={100}
        step={1}
        disabled={disabled}
      />

      <NumberInput
        label="Espaçamento"
        value={value.spacing}
        onChange={handleSpacingChange}
        min={1}
        max={100}
        step={1}
        disabled={disabled}
      />

      <NumberInput
        label="Ângulo"
        value={value.angle}
        onChange={handleAngleChange}
        min={0}
        max={360}
        step={1}
        disabled={disabled}
      />

      <NumberInput
        label="Opacidade"
        value={value.opacity}
        onChange={handleOpacityChange}
        min={0}
        max={1}
        step={0.01}
        disabled={disabled}
      />
    </div>
  );
};

const getPatternStyle = (pattern: PatternConfig): string => {
  const { type, color, backgroundColor, size, spacing, angle, opacity } =
    pattern;

  const styles: Record<PatternConfig['type'], string> = {
    dots: `radial-gradient(circle ${size}px at center, ${color} ${size / 2}px, transparent ${size / 2}px)`,
    lines: `repeating-linear-gradient(${angle}deg, ${color}, ${color} ${size}px, transparent ${size}px, transparent ${spacing}px)`,
    grid: `repeating-linear-gradient(${angle}deg, ${color}, ${color} ${size}px, transparent ${size}px, transparent ${spacing}px), repeating-linear-gradient(${angle + 90}deg, ${color}, ${color} ${size}px, transparent ${size}px, transparent ${spacing}px)`,
    crosshatch: `repeating-linear-gradient(${angle}deg, ${color}, ${color} ${size}px, transparent ${size}px, transparent ${spacing}px), repeating-linear-gradient(${angle + 45}deg, ${color}, ${color} ${size}px, transparent ${size}px, transparent ${spacing}px)`,
  };

  return `${backgroundColor} ${styles[type]}`;
};
