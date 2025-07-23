import React from 'react';
import './NumberInput.css';

interface NumberInputProps {
  label?: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  className?: string;
  error?: string;
  placeholder?: string;
  required?: boolean;
  name?: string;
  id?: string;
  autoFocus?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  precision?: number;
  unit?: string;
  showControls?: boolean;
}

export const NumberInput: React.FC<NumberInputProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  disabled = false,
  className = '',
  error,
  placeholder,
  required = false,
  name,
  id,
  autoFocus = false,
  onFocus,
  onBlur: onBlurProp,
  precision = 2,
  unit,
  showControls = true,
}) => {
  const [inputValue, setInputValue] = React.useState(value.toString());
  const [isFocused, setIsFocused] = React.useState(false);

  React.useEffect(() => {
    if (!isFocused) {
      setInputValue(formatNumber(value, precision));
    }
  }, [value, precision, isFocused]);

  const formatNumber = (num: number, precision: number): string => {
    return Number(num.toFixed(precision)).toString();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    const numericValue = parseFloat(newValue);
    if (!isNaN(numericValue)) {
      if (min !== undefined && numericValue < min) return;
      if (max !== undefined && numericValue > max) return;
      onChange(numericValue);
    }
  };

  const handleFocus = () => {
    setIsFocused(true);
    onFocus?.();
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    setInputValue(formatNumber(value, precision));
    onBlurProp?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      const newValue = value + step;
      if (max === undefined || newValue <= max) {
        onChange(newValue);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const newValue = value - step;
      if (min === undefined || newValue >= min) {
        onChange(newValue);
      }
    }
  };

  const inputProps = {
    type: 'number',
    className: `number-input-field ${error ? 'error' : ''}`,
    value: inputValue,
    onChange: handleChange,
    onFocus: handleFocus,
    onBlur: handleBlur,
    onKeyDown: handleKeyDown,
    min,
    max,
    step,
    disabled,
    placeholder,
    required,
    name,
    id,
    autoFocus,
  };

  return (
    <div className={`number-input ${className} ${disabled ? 'disabled' : ''}`}>
      {label && (
        <label className="number-input-label" htmlFor={id}>
          {label}
          {required && <span className="number-input-required">*</span>}
        </label>
      )}
      <div className="number-input-container">
        <div className="number-input-controls">
          <input {...inputProps} />
          {unit && <span className="number-input-unit">{unit}</span>}
          {showControls && (
            <div className="number-input-buttons">
              <button
                type="button"
                className="number-input-button"
                onClick={() => onChange(value + step)}
                disabled={disabled || (max !== undefined && value >= max)}
                aria-label="Aumentar"
              >
                ▲
              </button>
              <button
                type="button"
                className="number-input-button"
                onClick={() => onChange(value - step)}
                disabled={disabled || (min !== undefined && value <= min)}
                aria-label="Diminuir"
              >
                ▼
              </button>
            </div>
          )}
        </div>
        {error && <span className="number-input-error">{error}</span>}
      </div>
    </div>
  );
};
