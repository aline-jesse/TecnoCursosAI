import React from 'react';
import { GradientConfig, GradientStop } from '../../types';
import { ColorPicker } from './ColorPicker';
import './GradientPicker.css';
import { NumberInput } from './NumberInput';
import { Select } from './Select';

interface GradientPickerProps {
  value?: GradientConfig;
  onChange: (value: GradientConfig) => void;
  disabled?: boolean;
}

const DEFAULT_GRADIENT: GradientConfig = {
  type: 'linear',
  angle: 0,
  stops: [
    { offset: 0, color: '#000000', opacity: 1 },
    { offset: 1, color: '#ffffff', opacity: 1 },
  ],
};

export const GradientPicker: React.FC<GradientPickerProps> = ({
  value = DEFAULT_GRADIENT,
  onChange,
  disabled = false,
}) => {
  const handleTypeChange = (type: GradientConfig['type']) => {
    onChange({ ...value, type });
  };

  const handleAngleChange = (angle: number) => {
    onChange({ ...value, angle });
  };

  const handleStopChange = (index: number, stop: Partial<GradientStop>) => {
    const newStops = [...value.stops];
    newStops[index] = { ...newStops[index], ...stop };
    onChange({ ...value, stops: newStops });
  };

  const addStop = () => {
    const lastStop = value.stops[value.stops.length - 1];
    const newStop: GradientStop = {
      offset: Math.min(lastStop.offset + 0.1, 1),
      color: lastStop.color,
      opacity: lastStop.opacity,
    };
    onChange({ ...value, stops: [...value.stops, newStop] });
  };

  const removeStop = (index: number) => {
    if (value.stops.length <= 2) return;
    const newStops = value.stops.filter((_, i) => i !== index);
    onChange({ ...value, stops: newStops });
  };

  return (
    <div className="gradient-picker">
      <div className="gradient-picker-header">
        <Select
          label="Tipo"
          value={value.type}
          options={[
            { value: 'linear', label: 'Linear' },
            { value: 'radial', label: 'Radial' },
          ]}
          onChange={handleTypeChange}
          disabled={disabled}
        />
        {value.type === 'linear' && (
          <NumberInput
            label="Ângulo"
            value={value.angle || 0}
            onChange={handleAngleChange}
            min={0}
            max={360}
            step={1}
            disabled={disabled}
          />
        )}
      </div>

      <div
        className="gradient-preview"
        style={{ background: getGradientStyle(value) }}
      />

      <div className="gradient-stops">
        {value.stops.map((stop, index) => (
          <div key={index} className="gradient-stop">
            <NumberInput
              label="Posição"
              value={stop.offset}
              onChange={offset => handleStopChange(index, { offset })}
              min={0}
              max={1}
              step={0.01}
              disabled={disabled}
            />
            <ColorPicker
              label="Cor"
              value={stop.color}
              onChange={color => handleStopChange(index, { color })}
              disabled={disabled}
            />
            <NumberInput
              label="Opacidade"
              value={stop.opacity}
              onChange={opacity => handleStopChange(index, { opacity })}
              min={0}
              max={1}
              step={0.01}
              disabled={disabled}
            />
            {value.stops.length > 2 && (
              <button
                className="gradient-stop-remove"
                onClick={() => removeStop(index)}
                disabled={disabled}
                aria-label="Remover parada"
              >
                ✕
              </button>
            )}
          </div>
        ))}
        {value.stops.length < 5 && (
          <button
            className="gradient-stop-add"
            onClick={addStop}
            disabled={disabled}
            aria-label="Adicionar parada"
          >
            +
          </button>
        )}
      </div>
    </div>
  );
};

const getGradientStyle = (gradient: GradientConfig): string => {
  const stops = gradient.stops
    .map(stop => `${stop.color} ${stop.offset * 100}%`)
    .join(', ');

  if (gradient.type === 'linear') {
    return `linear-gradient(${gradient.angle}deg, ${stops})`;
  } else {
    return `radial-gradient(circle at center, ${stops})`;
  }
};
