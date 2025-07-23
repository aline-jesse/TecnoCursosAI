# Instalação de Dependências - AssetPanel

Este documento contém as instruções completas para instalar todas as dependências necessárias para o componente AssetPanel.

## 📦 Dependências Principais

### React e Dependências Core
```bash
npm install react react-dom
npm install @heroicons/react
npm install react-beautiful-dnd
```

### Styling e UI
```bash
npm install tailwindcss
npm install @tailwindcss/forms
npm install autoprefixer
npm install postcss
```

### Testing
```bash
npm install --save-dev @testing-library/react
npm install --save-dev @testing-library/jest-dom
npm install --save-dev @testing-library/user-event
npm install --save-dev jest
npm install --save-dev jest-environment-jsdom
```

### Build Tools
```bash
npm install --save-dev @babel/core
npm install --save-dev @babel/preset-react
npm install --save-dev @babel/preset-env
npm install --save-dev babel-loader
```

## 🔧 Configuração do TailwindCSS

### 1. Inicializar TailwindCSS
```bash
npx tailwindcss init -p
```

### 2. Configurar tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### 3. Configurar CSS principal
```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## 🧪 Configuração do Jest

### 1. Configurar jest.config.js
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/__mocks__/fileMock.js'
  },
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
  },
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx}'
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
  ]
};
```

### 2. Configurar setupTests.js
```javascript
// src/setupTests.js
import '@testing-library/jest-dom';

// Mock do react-beautiful-dnd
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children }) => <div>{children}</div>,
  Droppable: ({ children }) => children({ innerRef: jest.fn(), droppableProps: {} }, {}),
  Draggable: ({ children }) => children({ innerRef: jest.fn(), draggableProps: {}, dragHandleProps: {} }, { isDragging: false }),
}));

// Mock do @heroicons/react
jest.mock('@heroicons/react/24/outline', () => ({
  PlusIcon: () => <div data-testid="plus-icon">+</div>,
  PhotoIcon: () => <div data-testid="photo-icon">📷</div>,
  MusicalNoteIcon: () => <div data-testid="music-icon">🎵</div>,
  DocumentTextIcon: () => <div data-testid="text-icon">📄</div>,
  UserIcon: () => <div data-testid="user-icon">👤</div>,
  TrashIcon: () => <div data-testid="trash-icon">🗑️</div>,
  CogIcon: () => <div data-testid="cog-icon">⚙️</div>,
}));

// Mock do File API
global.URL.createObjectURL = jest.fn(() => 'mock-url');
```

### 3. Configurar Babel
```javascript
// .babelrc
{
  "presets": [
    "@babel/preset-env",
    ["@babel/preset-react", { "runtime": "automatic" }]
  ]
}
```

## 📁 Estrutura de Arquivos

```
src/
├── components/
│   ├── AssetPanel.jsx
│   └── AssetPanel.test.js
├── services/
│   └── assetService.js
├── hooks/
│   └── useAssets.js
├── App.jsx
├── index.js
└── index.css
```

## 🚀 Scripts do package.json

```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "test:coverage": "npm test -- --coverage --watchAll=false",
    "test:ci": "npm test -- --watchAll=false --coverage --ci"
  }
}
```

## 🔍 Verificação da Instalação

### 1. Verificar se todas as dependências estão instaladas
```bash
npm list react react-dom @heroicons/react react-beautiful-dnd tailwindcss
```

### 2. Executar testes
```bash
npm test
```

### 3. Verificar build
```bash
npm run build
```

## 🐛 Solução de Problemas

### Erro: "react-beautiful-dnd not found"
```bash
npm install react-beautiful-dnd@latest
```

### Erro: "@heroicons/react not found"
```bash
npm install @heroicons/react@latest
```

### Erro: "TailwindCSS not working"
```bash
# Verificar se o CSS está importado
# Em src/index.js deve ter: import './index.css'
```

### Erro: "Jest tests failing"
```bash
# Limpar cache do Jest
npm test -- --clearCache
```

## 📋 Checklist de Instalação

- [ ] React e React-DOM instalados
- [ ] @heroicons/react instalado
- [ ] react-beautiful-dnd instalado
- [ ] TailwindCSS configurado
- [ ] Jest configurado
- [ ] @testing-library instalado
- [ ] Babel configurado
- [ ] Scripts do package.json configurados
- [ ] Testes executando sem erros
- [ ] Build funcionando

## 🔗 Links Úteis

- [React Beautiful DnD](https://github.com/atlassian/react-beautiful-dnd)
- [Heroicons](https://heroicons.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [Testing Library](https://testing-library.com/)
- [Jest](https://jestjs.io/)

## 📝 Notas Importantes

1. **Versões**: Certifique-se de usar versões compatíveis
2. **Node.js**: Requer Node.js 14+ 
3. **npm**: Use npm 6+ ou yarn
4. **TypeScript**: Opcional, mas recomendado para projetos maiores
5. **ESLint**: Recomendado para linting

## 🎯 Próximos Passos

Após a instalação bem-sucedida:

1. Importe o AssetPanel no seu App.jsx
2. Configure o useAssets hook
3. Configure o assetService
4. Execute os testes para verificar funcionamento
5. Personalize o styling conforme necessário 