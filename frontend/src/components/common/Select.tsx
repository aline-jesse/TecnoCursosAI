import React from 'react';
import './Select.css';

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
  description?: string;
  icon?: string;
}

interface SelectProps {
  label?: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
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
}

export const Select: React.FC<SelectProps> = ({
  label,
  value,
  options,
  onChange,
  disabled = false,
  className = '',
  error,
  placeholder,
  required = false,
  name,
  id,
  autoFocus = false,
  onFocus,
  onBlur,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value);
  };

  const selectProps = {
    className: `select-input ${error ? 'error' : ''}`,
    value,
    onChange: handleChange,
    disabled,
    required,
    name,
    id,
    autoFocus,
    onFocus,
    onBlur,
  };

  return (
    <div className={`select ${className} ${disabled ? 'disabled' : ''}`}>
      {label && (
        <label className="select-label" htmlFor={id}>
          {label}
          {required && <span className="select-required">*</span>}
        </label>
      )}
      <select {...selectProps}>
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map(option => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
            title={option.description}
          >
            {option.icon && (
              <span className="select-option-icon">{option.icon}</span>
            )}
            {option.label}
          </option>
        ))}
      </select>
      {error && <span className="select-error">{error}</span>}
    </div>
  );
};
