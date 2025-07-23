# Testes do EditorCanvas

Este diretório contém os testes unitários para o componente `EditorCanvas` usando React Testing Library e Jest.

## Estrutura dos Testes

### `EditorCanvas.test.jsx`
Testes principais que cobrem:

- **Renderização**: Verifica se o componente renderiza corretamente
- **Funcionalidades de Controle**: Testa botões de adicionar texto, deletar, etc.
- **Drag and Drop**: Verifica funcionalidade de arrastar assets para o canvas
- **Interações do Mouse**: Testa eventos de mouse (click, drag, double-click)
- **Integração com Assets**: Verifica se assets são processados corretamente
- **Estados e Props**: Testa mudanças de props e estados
- **Acessibilidade**: Verifica atributos de acessibilidade

## Como Executar os Testes

### Executar todos os testes do EditorCanvas:
```bash
npm test
```

### Executar em modo watch (desenvolvimento):
```bash
npm run test:watch
```

### Executar com cobertura de código:
```bash
npm run test:coverage
```

### Executar testes específicos:
```bash
npm test -- --testNamePattern="deve adicionar texto"
```

## Mocks e Configuração

### Canvas Mock
O canvas é mockado para evitar erros em ambiente de teste:
- `getContext('2d')` retorna um objeto com métodos mockados
- `getBoundingClientRect()` retorna coordenadas fixas
- Eventos de mouse são simulados

### Assets Mock
```javascript
const mockAssets = [
  { id: 'avatar1', type: 'avatar', url: '/test-avatar.svg', name: 'Avatar Teste' },
  { id: 'img1', type: 'image', url: '/test-image.jpg', name: 'Imagem Teste' },
];
```

### Cena Mock
```javascript
const mockScene = {
  id: 'scene1',
  name: 'Cena Teste',
  width: 800,
  height: 600,
  background: '#ffffff',
  objects: [],
};
```

## Padrões de Teste

### 1. Renderização Básica
```javascript
test('deve renderizar o canvas sem erros', () => {
  renderEditorCanvas();
  const canvas = screen.getByRole('img', { hidden: true });
  expect(canvas).toBeInTheDocument();
});
```

### 2. Teste de Funcionalidade
```javascript
test('deve adicionar texto quando botão for clicado', async () => {
  renderEditorCanvas();
  const addTextButton = screen.getByText('Adicionar Texto');
  fireEvent.click(addTextButton);
  
  await waitFor(() => {
    expect(mockUpdateScene).toHaveBeenCalledWith(
      expect.objectContaining({
        objects: expect.arrayContaining([
          expect.objectContaining({
            type: 'text',
            text: 'Novo texto',
          }),
        ]),
      })
    );
  });
});
```

### 3. Teste de Drag and Drop
```javascript
test('deve aceitar drop de assets no canvas', async () => {
  renderEditorCanvas();
  const canvas = screen.getByRole('img', { hidden: true });
  
  const dropEvent = new Event('drop', { bubbles: true });
  dropEvent.dataTransfer = {
    getData: jest.fn((key) => {
      if (key === 'assetId') return 'avatar1';
      if (key === 'assetType') return 'avatar';
      return '';
    }),
  };
  
  fireEvent(canvas, dropEvent);
  
  await waitFor(() => {
    expect(mockUpdateScene).toHaveBeenCalledWith(
      expect.objectContaining({
        objects: expect.arrayContaining([
          expect.objectContaining({
            type: 'avatar',
            assetId: 'avatar1',
          }),
        ]),
      })
    );
  });
});
```

## Cobertura de Testes

Os testes cobrem:

- ✅ Renderização do componente
- ✅ Botões de controle (adicionar, deletar, ordenar)
- ✅ Drag and drop de assets
- ✅ Eventos de mouse
- ✅ Estados disabled/enabled
- ✅ Mudanças de props
- ✅ Acessibilidade básica

## Próximos Passos

Para expandir a cobertura de testes:

1. **Testes de Integração**: Testar interação com store global (Zustand)
2. **Testes de Performance**: Verificar renderização com muitos objetos
3. **Testes de Edge Cases**: Cenários extremos (muitos assets, objetos sobrepostos)
4. **Testes de Acessibilidade**: Verificar navegação por teclado completa
5. **Testes de Responsividade**: Verificar comportamento em diferentes tamanhos

## Troubleshooting

### Erro: "Canvas is not supported in this environment"
- Verifique se o mock do canvas está configurado em `setupTests.js`

### Erro: "getBoundingClientRect is not a function"
- Certifique-se de que o mock do `getBoundingClientRect` está ativo

### Testes falhando por timing
- Use `waitFor()` para operações assíncronas
- Aumente o timeout se necessário: `jest.setTimeout(10000)` 