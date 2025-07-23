import React from 'react';
import './Accordion.css';
import { Icon } from './Icon';

interface AccordionProps {
  title: string | React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
  onChange?: (isOpen: boolean) => void;
  id?: string;
  headerClassName?: string;
  contentClassName?: string;
  icon?: React.ReactNode;
  expandIcon?: string;
  collapseIcon?: string;
  animationDuration?: number;
}

export const Accordion: React.FC<AccordionProps> = ({
  title,
  defaultOpen = false,
  children,
  className = '',
  disabled = false,
  onChange,
  id,
  headerClassName = '',
  contentClassName = '',
  icon,
  expandIcon = 'chevron-down',
  collapseIcon = 'chevron-down',
  animationDuration = 300,
}) => {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);
  const contentRef = React.useRef<HTMLDivElement>(null);

  const toggleAccordion = () => {
    if (!disabled) {
      const newState = !isOpen;
      setIsOpen(newState);
      onChange?.(newState);
    }
  };

  React.useEffect(() => {
    if (contentRef.current) {
      const content = contentRef.current;
      if (isOpen) {
        content.style.height = '0';
        content.style.opacity = '0';
        requestAnimationFrame(() => {
          content.style.height = `${content.scrollHeight}px`;
          content.style.opacity = '1';
        });
      } else {
        content.style.height = `${content.scrollHeight}px`;
        requestAnimationFrame(() => {
          content.style.height = '0';
          content.style.opacity = '0';
        });
      }
    }
  }, [isOpen]);

  return (
    <div
      className={`accordion ${className} ${disabled ? 'disabled' : ''}`}
      id={id}
    >
      <button
        className={`accordion-header ${headerClassName} ${isOpen ? 'open' : ''}`}
        onClick={toggleAccordion}
        type="button"
        disabled={disabled}
        aria-expanded={isOpen}
        aria-controls={`${id}-content`}
      >
        {icon && <span className="accordion-icon-custom">{icon}</span>}
        <span className="accordion-title">
          {typeof title === 'string' ? title : title}
        </span>
        <Icon
          name={isOpen ? collapseIcon : expandIcon}
          className={`accordion-icon ${isOpen ? 'open' : ''}`}
        />
      </button>
      <div
        ref={contentRef}
        className={`accordion-content ${contentClassName}`}
        id={`${id}-content`}
        role="region"
        aria-labelledby={id}
        style={{
          transition: `height ${animationDuration}ms ease-in-out, opacity ${animationDuration}ms ease-in-out`,
          height: isOpen ? 'auto' : '0',
          opacity: isOpen ? '1' : '0',
          overflow: 'hidden',
        }}
      >
        <div className="accordion-content-inner">{children}</div>
      </div>
    </div>
  );
};
