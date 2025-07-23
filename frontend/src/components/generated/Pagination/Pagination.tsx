// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

import React from 'react';
import './Pagination.css';

import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  showPageNumbers: boolean;
}

/**
 * Componente Pagination
 * Gerado automaticamente pelo sistema de code generation
 */
const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  showPageNumbers,
}: PaginationProps) => {
  return (
    <div className='pagination-container'>
      <h3>Pagination</h3>
      {/* Conteúdo do componente */}
    </div>
  );
};

export default Pagination;
