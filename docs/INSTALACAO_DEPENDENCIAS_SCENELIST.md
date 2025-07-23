# Instalação de Dependências - SceneList

## Dependências Necessárias

O componente SceneList utiliza as seguintes dependências que já estão instaladas no projeto:

### Dependências Principais

```bash
# React e dependências básicas
npm install react react-dom

# Drag and Drop
npm install react-beautiful-dnd

# Ícones
npm install @heroicons/react

# Testes
npm install @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Verificação de Instalação

Para verificar se todas as dependências estão instaladas corretamente:

```bash
# Verificar dependências instaladas
npm list react-beautiful-dnd
npm list @heroicons/react
npm list @testing-library/react
```

### Versões Recomendadas

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-beautiful-dnd": "^13.1.1",
    "@heroicons/react": "^2.0.18"
  },
  "devDependencies": {
    "@testing-library/react": "^13.3.0",
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/user-event": "^13.5.0"
  }
}
```

## Configuração do TypeScript (Opcional)

Se estiver usando TypeScript, adicione os tipos:

```bash
npm install --save-dev @types/react-beautiful-dnd
```

## Configuração do ESLint (Opcional)

Para melhor suporte ao ESLint com react-beautiful-dnd:

```bash
npm install --save-dev eslint-plugin-react-hooks
```

Adicione ao `.eslintrc.js`:

```javascript
module.exports = {
  plugins: ['react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn'
  }
};
```

## Verificação de Funcionamento

Após a instalação, execute os testes para verificar se tudo está funcionando:

```bash
# Executar testes do SceneList
npm test -- SceneList.test.js

# Executar todos os testes
npm test
```

## Solução de Problemas

### Erro: "react-beautiful-dnd not found"
```bash
npm install react-beautiful-dnd
```

### Erro: "@heroicons/react not found"
```bash
npm install @heroicons/react
```

### Erro: "Cannot resolve module"
```bash
# Limpar cache do npm
npm cache clean --force

# Reinstalar dependências
rm -rf node_modules package-lock.json
npm install
```

### Erro de TypeScript
Se estiver usando TypeScript e encontrar erros de tipos:

```bash
npm install --save-dev @types/react-beautiful-dnd
```

## Estrutura de Arquivos

Após a instalação, você deve ter:

```
src/
├── components/
│   ├── SceneList.jsx          # Componente principal
│   ├── SceneList.css          # Estilos
│   └── SceneList.test.js      # Testes
├── App.jsx                    # Exemplo de uso
└── index.js                   # Ponto de entrada
```

## Comandos Úteis

```bash
# Instalar todas as dependências
npm install

# Executar em modo desenvolvimento
npm start

# Executar testes
npm test

# Build para produção
npm run build
```

## Notas Importantes

1. **react-beautiful-dnd**: Biblioteca essencial para drag-and-drop
2. **@heroicons/react**: Fornece ícones SVG otimizados
3. **@testing-library**: Para testes unitários e de integração
4. **CSS**: Estilos customizados para melhor UX

## Próximos Passos

Após a instalação bem-sucedida:

1. Execute `npm start` para ver o componente em ação
2. Execute `npm test` para verificar se os testes passam
3. Integre o componente no seu editor de vídeos
4. Personalize os estilos conforme necessário

## Suporte

Se encontrar problemas:

1. Verifique se todas as dependências estão instaladas
2. Confirme se as versões são compatíveis
3. Execute `npm audit` para verificar vulnerabilidades
4. Consulte a documentação oficial das bibliotecas 