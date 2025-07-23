// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

# DataTable

Componente de tabela de dados com paginação e ordenação

## Props

- `data` (any[]): Dados para exibir na tabela
- `columns` (Column[]): Configuração das colunas
- `onRowClick` ((row: any) => void): Callback para clique na linha
- `loading` (boolean): Estado de carregamento

## Uso

```tsx
import DataTable from './DataTable';

<DataTable data={value} columns={value} onRowClick={value} loading={value} />
```

## Testes

Execute os testes com:

```bash
npm test -- --testPathPattern=DataTable.test.tsx
```

---

*Este componente foi gerado automaticamente pelo sistema de code generation.*