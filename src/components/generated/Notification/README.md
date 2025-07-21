// Este arquivo foi gerado automaticamente por scripts/codegen/generateComponents.js
// Não edite manualmente - use o sistema de geração

# Notification

Sistema de notificações

## Props

- `message` (string): Mensagem da notificação
- `type` ('success' | 'error' | 'warning' | 'info'): Tipo da notificação
- `onClose` (() => void): Callback para fechar
- `autoClose` (boolean): Fechar automaticamente

## Uso

```tsx
import Notification from './Notification';

<Notification message={value} type={value} onClose={value} autoClose={value} />
```

## Testes

Execute os testes com:

```bash
npm test -- --testPathPattern=Notification.test.tsx
```

---

*Este componente foi gerado automaticamente pelo sistema de code generation.*