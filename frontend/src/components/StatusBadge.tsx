/**
 * Componente StatusBadge
 * Badges coloridas para status dos projetos
 * TecnoCursos AI - Dashboard de Projetos
 */

import React from 'react';
import { ProjectStatus } from '../types/project';

/**
 * Props para o componente StatusBadge.
 */
export interface StatusBadgeProps {
  status: ProjectStatus;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  animate?: boolean;
}

/**
 * Configuração de cores e ícones para cada status
 */
const STATUS_CONFIG: { [key in ProjectStatus]: any } = {
  [ProjectStatus.DRAFT]: {
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    icon: '📝',
    label: 'Rascunho',
    pulse: false,
  },
  [ProjectStatus.PROCESSING]: {
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
    icon: '⚙️',
    label: 'Processando',
    pulse: true,
  },
  [ProjectStatus.RENDERING]: {
    color: 'yellow',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-300',
    icon: '🎬',
    label: 'Renderizando',
    pulse: true,
  },
  [ProjectStatus.COMPLETED]: {
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
    icon: '✅',
    label: 'Concluído',
    pulse: false,
  },
  [ProjectStatus.ERROR]: {
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
    icon: '❌',
    label: 'Erro',
    pulse: false,
  },
  [ProjectStatus.CANCELLED]: {
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600',
    borderColor: 'border-gray-300',
    icon: '⛔',
    label: 'Cancelado',
    pulse: false,
  },
  [ProjectStatus.ARCHIVED]: {
    color: 'gray',
    bgColor: 'bg-gray-50',
    textColor: 'text-gray-500',
    borderColor: 'border-gray-200',
    icon: '📦',
    label: 'Arquivado',
    pulse: false,
  },
};

/**
 * Configuração de tamanhos
 */
const SIZE_CONFIG = {
  sm: {
    padding: 'px-2 py-1',
    fontSize: 'text-xs',
    iconSize: 'text-xs',
    height: 'h-5',
  },
  md: {
    padding: 'px-3 py-1.5',
    fontSize: 'text-sm',
    iconSize: 'text-sm',
    height: 'h-6',
  },
  lg: {
    padding: 'px-4 py-2',
    fontSize: 'text-base',
    iconSize: 'text-base',
    height: 'h-8',
  },
};

/**
 * Componente StatusBadge
 */
export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showText = true,
  animate = true,
}) => {
  const statusConfig = STATUS_CONFIG[status];
  const sizeConfig = SIZE_CONFIG[size];

  if (!statusConfig) {
    console.warn(`Status desconhecido: ${status}`);
    return null;
  }

  const shouldAnimate = animate && statusConfig.pulse;

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full border font-medium
        ${statusConfig.bgColor} 
        ${statusConfig.textColor} 
        ${statusConfig.borderColor}
        ${sizeConfig.padding} 
        ${sizeConfig.fontSize}
        ${sizeConfig.height}
        ${shouldAnimate ? 'animate-pulse' : ''}
        transition-all duration-200
      `}
      title={`Status: ${statusConfig.label}`}
    >
      {/* Ícone do status */}
      <span
        className={`${sizeConfig.iconSize} leading-none`}
        aria-hidden='true'
      >
        {statusConfig.icon}
      </span>

      {/* Texto do status (opcional) */}
      {showText && (
        <span className='leading-none font-medium'>{statusConfig.label}</span>
      )}

      {/* Indicador de progresso para status em andamento */}
      {shouldAnimate && (
        <span
          className='w-2 h-2 rounded-full bg-current opacity-60 animate-ping'
          aria-hidden='true'
        />
      )}
    </span>
  );
};

/**
 * Componente StatusBadge com progresso (para renderização)
 */
interface StatusBadgeWithProgressProps extends StatusBadgeProps {
  progress?: number;
  showProgress?: boolean;
}

export const StatusBadgeWithProgress: React.FC<
  StatusBadgeWithProgressProps
> = ({ status, progress = 0, showProgress = false, ...props }) => {
  const isProcessing =
    status === ProjectStatus.PROCESSING || status === ProjectStatus.RENDERING;

  if (!showProgress || !isProcessing || progress === 0) {
    return <StatusBadge status={status} {...props} />;
  }

  const statusConfig = STATUS_CONFIG[status];
  const sizeConfig = SIZE_CONFIG[props.size || 'md'];

  return (
    <div className='flex items-center gap-2'>
      {/* Badge principal */}
      <StatusBadge status={status} {...props} />

      {/* Barra de progresso */}
      <div className='flex items-center gap-1 min-w-0'>
        <div
          className={`
            flex-1 bg-gray-200 rounded-full overflow-hidden
            ${props.size === 'sm' ? 'h-1' : props.size === 'lg' ? 'h-2' : 'h-1.5'}
          `}
          title={`Progresso: ${Math.round(progress)}%`}
        >
          <div
            className={`
              h-full transition-all duration-300 ease-out rounded-full
              ${statusConfig.color === 'blue' ? 'bg-blue-500' : 'bg-yellow-500'}
            `}
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>

        {/* Porcentagem */}
        <span
          className={`
            ${sizeConfig.fontSize} font-mono font-medium text-gray-600 whitespace-nowrap
          `}
        >
          {Math.round(progress)}%
        </span>
      </div>
    </div>
  );
};

/**
 * Componente para múltiplos status (estatísticas)
 */
interface StatusSummaryProps {
  counts: Partial<Record<ProjectStatus, number>>;
  total: number;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusSummary: React.FC<StatusSummaryProps> = ({
  counts,
  total,
  size = 'md',
}) => {
  const nonZeroCounts = Object.entries(counts).filter(
    ([_, count]) => count && count > 0
  );

  if (nonZeroCounts.length === 0) {
    return <span className='text-gray-500 text-sm'>Nenhum projeto</span>;
  }

  return (
    <div className='flex items-center gap-2 flex-wrap'>
      {nonZeroCounts.map(([status, count]) => (
        <div key={status} className='flex items-center gap-1'>
          <StatusBadge
            status={status as ProjectStatus}
            size={size}
            showText={false}
            animate={false}
          />
          <span className='text-sm font-medium text-gray-700'>{count}</span>
        </div>
      ))}

      {total > 0 && (
        <span className='text-sm text-gray-500 ml-2'>Total: {total}</span>
      )}
    </div>
  );
};

/**
 * Hook para obter configuração de status
 */
export const useStatusConfig = (status: ProjectStatus) => {
  return STATUS_CONFIG[status] || STATUS_CONFIG[ProjectStatus.DRAFT];
};

/**
 * Utilitário para obter cor do status
 */
export const getStatusColor = (status: ProjectStatus): string => {
  return STATUS_CONFIG[status]?.color || 'gray';
};

/**
 * Utilitário para verificar se status está em progresso
 */
export const isStatusInProgress = (status: ProjectStatus): boolean => {
  return (
    status === ProjectStatus.PROCESSING || status === ProjectStatus.RENDERING
  );
};

/**
 * Utilitário para verificar se status é final
 */
export const isStatusFinal = (status: ProjectStatus): boolean => {
  return (
    status === ProjectStatus.COMPLETED ||
    status === ProjectStatus.ERROR ||
    status === ProjectStatus.CANCELLED
  );
};

export default StatusBadge;
