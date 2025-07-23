import React from 'react';
import './FontPicker.css';
import { Select } from './Select';

interface FontPickerProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const FONTS = [
  { value: 'Arial', label: 'Arial' },
  { value: 'Helvetica', label: 'Helvetica' },
  { value: 'Times New Roman', label: 'Times New Roman' },
  { value: 'Georgia', label: 'Georgia' },
  { value: 'Verdana', label: 'Verdana' },
  { value: 'Roboto', label: 'Roboto' },
  { value: 'Open Sans', label: 'Open Sans' },
  { value: 'Lato', label: 'Lato' },
  { value: 'Montserrat', label: 'Montserrat' },
  { value: 'Source Sans Pro', label: 'Source Sans Pro' },
];

export const FontPicker: React.FC<FontPickerProps> = ({
  label,
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <Select
      label={label}
      value={value}
      options={FONTS}
      onChange={onChange}
      disabled={disabled}
    />
  );
};
