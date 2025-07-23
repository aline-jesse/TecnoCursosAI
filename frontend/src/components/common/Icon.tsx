import React from 'react';
import './Icon.css';

export type IconName =
  | 'cursor'
  | 'hand'
  | 'text'
  | 'rectangle'
  | 'circle'
  | 'line'
  | 'image'
  | 'video'
  | 'audio'
  | 'undo'
  | 'redo'
  | 'zoom-in'
  | 'zoom-out'
  | 'zoom-reset'
  | 'chevron-down'
  | 'loading';

interface IconProps {
  name: IconName;
  size?: number;
  className?: string;
}

export const Icon: React.FC<IconProps> = ({
  name,
  size = 24,
  className = '',
}) => {
  return (
    <svg
      className={`icon ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {getPath(name)}
    </svg>
  );
};

const getPath = (name: IconName): React.ReactNode => {
  switch (name) {
    case 'cursor':
      return <path d="M7 2l10 10-3.5 3.5L2 7V2h5z" />;
    case 'hand':
      return <path d="M12 2v7l5 5v6h-4v-6l-5-5V2" />;
    case 'text':
      return (
        <>
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="12" y1="6" x2="12" y2="18" />
        </>
      );
    case 'rectangle':
      return <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />;
    case 'circle':
      return <circle cx="12" cy="12" r="10" />;
    case 'line':
      return <line x1="5" y1="19" x2="19" y2="5" />;
    case 'image':
      return (
        <>
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </>
      );
    case 'video':
      return (
        <>
          <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18" />
          <line x1="7" y1="2" x2="7" y2="22" />
          <line x1="17" y1="2" x2="17" y2="22" />
          <line x1="2" y1="12" x2="22" y2="12" />
          <line x1="2" y1="7" x2="7" y2="7" />
          <line x1="2" y1="17" x2="7" y2="17" />
          <line x1="17" y1="17" x2="22" y2="17" />
          <line x1="17" y1="7" x2="22" y2="7" />
        </>
      );
    case 'audio':
      return (
        <>
          <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
          <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
        </>
      );
    case 'undo':
      return (
        <>
          <path d="M3 7v6h6" />
          <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
        </>
      );
    case 'redo':
      return (
        <>
          <path d="M21 7v6h-6" />
          <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13" />
        </>
      );
    case 'zoom-in':
      return (
        <>
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
          <line x1="11" y1="8" x2="11" y2="14" />
          <line x1="8" y1="11" x2="14" y2="11" />
        </>
      );
    case 'zoom-out':
      return (
        <>
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
          <line x1="8" y1="11" x2="14" y2="11" />
        </>
      );
    case 'zoom-reset':
      return (
        <>
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
          <path d="M8 11h6" />
        </>
      );
    case 'chevron-down':
      return <polyline points="6 9 12 15 18 9" />;
  }
};
