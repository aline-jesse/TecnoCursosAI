// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

# FormField

Campo de formulário com validação

## Props

- `label` (string): Rótulo do campo
- `value` (string): Valor do campo
- `onChange` ((value: string) => void): Callback de mudança
- `error` (string): Mensagem de erro
- `type` ('text' | 'email' | 'password'): Tipo do campo

## Uso

```tsx
import FormField from './FormField';

<FormField label={value} value={value} onChange={value} error={value} type={value} />
```

## Testes

Execute os testes com:

```bash
npm test -- --testPathPattern=FormField.test.tsx
```

---

*Este componente foi gerado automaticamente pelo sistema de code generation.*