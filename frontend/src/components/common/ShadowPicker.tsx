import React from 'react';
import { ShadowConfig } from '../../types';
import { ColorPicker } from './ColorPicker';
import { NumberInput } from './NumberInput';
import './ShadowPicker.css';

interface ShadowPickerProps {
  value?: ShadowConfig;
  onChange: (value: ShadowConfig) => void;
  disabled?: boolean;
}

const DEFAULT_SHADOW: ShadowConfig = {
  color: '#000000',
  offsetX: 0,
  offsetY: 0,
  blur: 10,
  spread: 0,
  opacity: 0.5,
};

export const ShadowPicker: React.FC<ShadowPickerProps> = ({
  value = DEFAULT_SHADOW,
  onChange,
  disabled = false,
}) => {
  const handleColorChange = (color: string) => {
    onChange({ ...value, color });
  };

  const handleOffsetXChange = (offsetX: number) => {
    onChange({ ...value, offsetX });
  };

  const handleOffsetYChange = (offsetY: number) => {
    onChange({ ...value, offsetY });
  };

  const handleBlurChange = (blur: number) => {
    onChange({ ...value, blur });
  };

  const handleSpreadChange = (spread: number) => {
    onChange({ ...value, spread });
  };

  const handleOpacityChange = (opacity: number) => {
    onChange({ ...value, opacity });
  };

  return (
    <div className="shadow-picker">
      <div
        className="shadow-preview"
        style={{ boxShadow: getShadowStyle(value) }}
      >
        Visualização
      </div>

      <ColorPicker
        label="Cor"
        value={value.color}
        onChange={handleColorChange}
        disabled={disabled}
      />

      <div className="shadow-picker-group">
        <NumberInput
          label="Deslocamento X"
          value={value.offsetX}
          onChange={handleOffsetXChange}
          min={-100}
          max={100}
          step={1}
          disabled={disabled}
        />
        <NumberInput
          label="Deslocamento Y"
          value={value.offsetY}
          onChange={handleOffsetYChange}
          min={-100}
          max={100}
          step={1}
          disabled={disabled}
        />
      </div>

      <div className="shadow-picker-group">
        <NumberInput
          label="Desfoque"
          value={value.blur}
          onChange={handleBlurChange}
          min={0}
          max={100}
          step={1}
          disabled={disabled}
        />
        <NumberInput
          label="Expansão"
          value={value.spread}
          onChange={handleSpreadChange}
          min={-100}
          max={100}
          step={1}
          disabled={disabled}
        />
      </div>

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

const getShadowStyle = (shadow: ShadowConfig): string => {
  const { color, offsetX, offsetY, blur, spread, opacity } = shadow;
  const rgba = hexToRgba(color, opacity);
  return `${offsetX}px ${offsetY}px ${blur}px ${spread}px ${rgba}`;
};

const hexToRgba = (hex: string, opacity: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};
