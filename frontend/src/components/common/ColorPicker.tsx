import React from 'react';
import './ColorPicker.css';

interface ColorPickerProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  className?: string;
  error?: string;
  required?: boolean;
  name?: string;
  id?: string;
  autoFocus?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  showAlpha?: boolean;
  presetColors?: string[];
}

export const ColorPicker: React.FC<ColorPickerProps> = ({
  label,
  value,
  onChange,
  disabled = false,
  className = '',
  error,
  required = false,
  name,
  id,
  autoFocus = false,
  onFocus,
  onBlur,
  showAlpha = false,
  presetColors = [],
}) => {
  const [isValid, setIsValid] = React.useState(true);

  const validateColor = (color: string): boolean => {
    const hexRegex = /^#[0-9A-Fa-f]{6}$/;
    const hexaRegex = /^#[0-9A-Fa-f]{8}$/;
    return showAlpha ? hexaRegex.test(color) : hexRegex.test(color);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    const valid = validateColor(newValue);
    setIsValid(valid);
    if (valid) {
      onChange(newValue);
    }
  };

  const handlePresetClick = (color: string) => {
    if (!disabled) {
      onChange(color);
    }
  };

  const inputProps = {
    name,
    id,
    disabled,
    autoFocus,
    onFocus,
    onBlur,
  };

  return (
    <div className={`color-picker ${className} ${disabled ? 'disabled' : ''}`}>
      {label && (
        <label className="color-picker-label" htmlFor={id}>
          {label}
          {required && <span className="color-picker-required">*</span>}
        </label>
      )}
      <div className="color-picker-container">
        <div className="color-picker-controls">
          <div
            className="color-preview"
            style={{ backgroundColor: value }}
            title={value}
          />
          <input
            type="color"
            className="color-input"
            value={value}
            onChange={handleChange}
            {...inputProps}
          />
          <input
            type="text"
            className={`color-text ${!isValid || error ? 'error' : ''}`}
            value={value}
            onChange={handleChange}
            pattern={showAlpha ? '^#[0-9A-Fa-f]{8}$' : '^#[0-9A-Fa-f]{6}$'}
            title={`Cor em formato hexadecimal (${showAlpha ? '#RRGGBBAA' : '#RRGGBB'})`}
            {...inputProps}
          />
        </div>
        {presetColors.length > 0 && (
          <div className="color-presets">
            {presetColors.map((color, index) => (
              <button
                key={index}
                type="button"
                className="color-preset"
                style={{ backgroundColor: color }}
                onClick={() => handlePresetClick(color)}
                disabled={disabled}
                title={color}
              />
            ))}
          </div>
        )}
        {(error || !isValid) && (
          <span className="color-picker-error">
            {error ||
              `Formato inválido. Use ${showAlpha ? '#RRGGBBAA' : '#RRGGBB'}`}
          </span>
        )}
      </div>
    </div>
  );
};
