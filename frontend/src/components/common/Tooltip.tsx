import React from 'react';
import './Tooltip.css';

type TooltipPosition = 'top' | 'right' | 'bottom' | 'left';
type TooltipTrigger = 'hover' | 'click' | 'focus';
type TooltipSize = 'small' | 'medium' | 'large';

interface TooltipProps {
  content: React.ReactNode;
  position?: TooltipPosition;
  delay?: number;
  children: React.ReactNode;
  className?: string;
  trigger?: TooltipTrigger;
  size?: TooltipSize;
  maxWidth?: string | number;
  disabled?: boolean;
  arrow?: boolean;
  interactive?: boolean;
  onShow?: () => void;
  onHide?: () => void;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  position = 'top',
  delay = 200,
  children,
  className = '',
  trigger = 'hover',
  size = 'medium',
  maxWidth,
  disabled = false,
  arrow = true,
  interactive = false,
  onShow,
  onHide,
}) => {
  const [visible, setVisible] = React.useState(false);
  const timeoutRef = React.useRef<number>();
  const tooltipRef = React.useRef<HTMLDivElement>(null);

  const showTooltip = () => {
    if (disabled) return;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = window.setTimeout(() => {
      setVisible(true);
      onShow?.();
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setVisible(false);
    onHide?.();
  };

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  React.useEffect(() => {
    if (disabled && visible) {
      hideTooltip();
    }
  }, [disabled]);

  const handleClick = () => {
    if (trigger === 'click') {
      if (visible) {
        hideTooltip();
      } else {
        showTooltip();
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape' && visible) {
      hideTooltip();
    }
  };

  const tooltipClasses = [
    'tooltip',
    `tooltip-${position}`,
    `tooltip-${size}`,
    arrow && 'tooltip-arrow',
    interactive && 'tooltip-interactive',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const containerProps = {
    className: 'tooltip-container',
    ref: tooltipRef,
    onClick: trigger === 'click' ? handleClick : undefined,
    onKeyDown: handleKeyDown,
    ...(trigger === 'hover' && {
      onMouseEnter: showTooltip,
      onMouseLeave: hideTooltip,
    }),
    ...(trigger === 'focus' && {
      onFocus: showTooltip,
      onBlur: hideTooltip,
    }),
    tabIndex: trigger === 'focus' ? 0 : undefined,
    role: 'tooltip',
    'aria-describedby': visible ? 'tooltip' : undefined,
  };

  const tooltipStyle: React.CSSProperties = {
    ...(maxWidth && {
      maxWidth: typeof maxWidth === 'number' ? `${maxWidth}px` : maxWidth,
    }),
  };

  return (
    <div {...containerProps}>
      {children}
      {visible && (
        <div
          id="tooltip"
          className={tooltipClasses}
          style={tooltipStyle}
          role="tooltip"
        >
          {content}
        </div>
      )}
    </div>
  );
};
