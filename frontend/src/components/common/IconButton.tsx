import React from 'react';
import { Icon } from './Icon';
import './IconButton.css';

type IconButtonSize = 'small' | 'medium' | 'large';
type IconButtonVariant =
  | 'default'
  | 'primary'
  | 'secondary'
  | 'danger'
  | 'ghost';

interface IconButtonProps {
  icon: string;
  active?: boolean;
  disabled?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onMouseEnter?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onMouseLeave?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  title?: string;
  className?: string;
  size?: IconButtonSize;
  variant?: IconButtonVariant;
  loading?: boolean;
  badge?: React.ReactNode;
  ariaLabel?: string;
  tabIndex?: number;
  name?: string;
  id?: string;
  form?: string;
  type?: 'button' | 'submit' | 'reset';
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      icon,
      active = false,
      disabled = false,
      onClick,
      onMouseEnter,
      onMouseLeave,
      title,
      className = '',
      size = 'medium',
      variant = 'default',
      loading = false,
      badge,
      ariaLabel,
      tabIndex,
      name,
      id,
      form,
      type = 'button',
    },
    ref
  ) => {
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!disabled && !loading && onClick) {
        onClick(e);
      }
    };

    const buttonClasses = [
      'icon-button',
      `icon-button-${size}`,
      `icon-button-${variant}`,
      active && 'active',
      loading && 'loading',
      disabled && 'disabled',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <button
        ref={ref}
        className={buttonClasses}
        onClick={handleClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        disabled={disabled || loading}
        title={title}
        type={type}
        aria-label={ariaLabel || title}
        aria-disabled={disabled || loading}
        aria-busy={loading}
        tabIndex={tabIndex}
        name={name}
        id={id}
        form={form}
      >
        {loading ? (
          <div className="icon-button-spinner">
            <Icon name="loading" className="spin" />
          </div>
        ) : (
          <Icon
            name={icon}
            size={size === 'small' ? 16 : size === 'large' ? 24 : 20}
          />
        )}
        {badge && <span className="icon-button-badge">{badge}</span>}
      </button>
    );
  }
);
