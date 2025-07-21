// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

# Pagination

Componente de paginação

## Props

- `currentPage` (number): Página atual
- `totalPages` (number): Total de páginas
- `onPageChange` ((page: number) => void): Callback de mudança de página
- `showPageNumbers` (boolean): Mostrar números das páginas

## Uso

```tsx
import Pagination from './Pagination';

<Pagination currentPage={value} totalPages={value} onPageChange={value} showPageNumbers={value} />
```

## Testes

Execute os testes com:

```bash
npm test -- --testPathPattern=Pagination.test.tsx
```

---

*Este componente foi gerado automaticamente pelo sistema de code generation.*