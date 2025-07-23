import React from 'react';
import './TextInput.css';

interface TextInputProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  multiline?: boolean;
  rows?: number;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  error?: string;
  maxLength?: number;
  autoFocus?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  onKeyPress?: (
    e: React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
}

export const TextInput: React.FC<TextInputProps> = ({
  label,
  value,
  onChange,
  multiline = false,
  rows = 3,
  placeholder,
  disabled = false,
  className = '',
  error,
  maxLength,
  autoFocus = false,
  onFocus,
  onBlur,
  onKeyPress,
}) => {
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    onChange(e.target.value);
  };

  const inputProps = {
    className: `text-input-${multiline ? 'textarea' : 'field'} ${error ? 'error' : ''}`,
    value,
    onChange: handleChange,
    placeholder,
    disabled,
    maxLength,
    autoFocus,
    onFocus,
    onBlur,
    onKeyPress,
  };

  return (
    <div className={`text-input ${className} ${disabled ? 'disabled' : ''}`}>
      {label && <label className="text-input-label">{label}</label>}
      {multiline ? (
        <textarea {...inputProps} rows={rows} />
      ) : (
        <input type="text" {...inputProps} />
      )}
      {error && <span className="text-input-error">{error}</span>}
    </div>
  );
};
