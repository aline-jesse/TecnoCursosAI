import React from 'react';
import './Divider.css';

type DividerOrientation = 'horizontal' | 'vertical';
type DividerVariant = 'solid' | 'dashed' | 'dotted';
type DividerSize = 'small' | 'medium' | 'large';

interface DividerProps {
  orientation?: DividerOrientation;
  className?: string;
  variant?: DividerVariant;
  size?: DividerSize;
  color?: string;
  margin?: string | number;
  width?: string | number;
  label?: React.ReactNode;
  labelPosition?: 'start' | 'center' | 'end';
}

export const Divider: React.FC<DividerProps> = ({
  orientation = 'horizontal',
  className = '',
  variant = 'solid',
  size = 'medium',
  color,
  margin,
  width,
  label,
  labelPosition = 'center',
}) => {
  const style: React.CSSProperties = {
    ...(color && { borderColor: color }),
    ...(margin && {
      margin: typeof margin === 'number' ? `${margin}px` : margin,
    }),
    ...(width && {
      [orientation === 'horizontal' ? 'width' : 'height']:
        typeof width === 'number' ? `${width}px` : width,
    }),
  };

  const dividerClasses = [
    'divider',
    `divider-${orientation}`,
    `divider-${variant}`,
    `divider-${size}`,
    label && 'divider-with-label',
    label && `divider-label-${labelPosition}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  if (label) {
    return (
      <div className={dividerClasses} role="separator" style={style}>
        <span className="divider-label">{label}</span>
      </div>
    );
  }

  return <div className={dividerClasses} role="separator" style={style} />;
};
