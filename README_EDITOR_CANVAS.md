# 🎨 EditorCanvas - Canvas Interativo Avançado

## 📋 Visão Geral

O **EditorCanvas** é um componente React avançado que implementa um canvas interativo completo usando **Fabric.js**, permitindo edição visual profissional para criação de cenas e vídeos educacionais no TecnoCursos AI.

## ✨ Funcionalidades Implementadas

### 🎯 Canvas Interativo
- Canvas HTML5 com Fabric.js para manipulação avançada de objetos
- Zoom com scroll do mouse (0.1x a 3x)
- Sistema de snap automático para alinhamento preciso
- Guidelines visuais para posicionamento

### 🚀 Drag & Drop
- **Avatares/Personagens**: Arraste da AssetPanel para o canvas
- **Fundos**: Adição automática de backgrounds que se ajustam ao canvas
- **Imagens**: Suporte a imagens com redimensionamento inteligente
- **Detecção automática**: Posicionamento baseado na posição do cursor

### 📝 Textos Editáveis
- **Inserção rápida**: Ctrl+T para adicionar texto instantaneamente
- **Edição inline**: Clique duplo para editar o texto diretamente
- **Formatação completa**: Fonte, tamanho, cor, alinhamento
- **Responsivo**: Textos se adaptam ao conteúdo

### 🔧 Manipulação de Objetos
- **Seleção**: Clique para selecionar objetos
- **Movimentação**: Arrastar e soltar para reposicionar
- **Redimensionamento**: Bordas interativas para ajustar tamanho
- **Rotação**: Controles visuais para rotacionar elementos
- **Duplicação**: Ctrl+D para duplicar objetos
- **Exclusão**: Delete/Backspace para remover elementos

### 📚 Sistema de Camadas
- **Controle Z-Index**: Organização em camadas
- **Mover para frente/trás**: Controles individuais
- **Enviar para topo/fundo**: Posicionamento extremo
- **Lista de objetos**: Visualização de todos os elementos na cena

### ⚙️ Propriedades Editáveis
- **Posição**: Coordenadas X e Y precisas
- **Tamanho**: Largura e altura em pixels
- **Rotação**: Slider de -180° a +180°
- **Opacidade**: Controle de transparência (0-100%)
- **Informações**: Tipo e nome do objeto

### 🔄 Estado Global
- **Sincronização**: Atualização automática do estado da cena
- **Persistência**: Salvamento automático das modificações
- **Histórico**: Preparado para undo/redo (implementação futura)
- **Metadados**: Preservação de informações dos objetos

## 🛠️ Tecnologias Utilizadas

- **React 18**: Framework principal
- **Fabric.js 5.3.0**: Manipulação avançada de canvas
- **UUID**: Identificadores únicos para objetos
- **TailwindCSS**: Estilização moderna e responsiva

## 📦 Estrutura do Componente

```
EditorCanvas.jsx
├── Inicialização do Canvas Fabric.js
├── Sistema de Eventos
├── Manipulação de Objetos
├── Drag & Drop
├── Snap e Guidelines
├── Controles de Camada
├── Painel de Propriedades
└── Interface de Usuário
```

## 🚀 Como Usar

### 1. Adicionar Avatares
1. Na **AssetPanel**, vá para a aba "👥 Avatares"
2. Arraste qualquer avatar para o canvas
3. O avatar será posicionado onde você soltou o mouse
4. Redimensione e posicione conforme necessário

### 2. Inserir Textos
1. Clique no botão "📝 Texto" ou pressione **Ctrl+T**
2. O texto aparecerá no centro do canvas
3. Clique duas vezes para editar o conteúdo
4. Use as propriedades para ajustar formatação

### 3. Adicionar Fundos
1. Na **AssetPanel**, vá para a aba "🖼️ Fundos"
2. Arraste um fundo para o canvas
3. O fundo se ajustará automaticamente ao tamanho do canvas
4. Será posicionado automaticamente atrás de outros elementos

### 4. Manipular Objetos
- **Selecionar**: Clique no objeto
- **Mover**: Arraste o objeto selecionado
- **Redimensionar**: Use as bordas/cantos do objeto
- **Rotacionar**: Use o controle de rotação ou o slider
- **Duplicar**: Pressione **Ctrl+D** com objeto selecionado
- **Excluir**: Pressione **Delete** ou **Backspace**

### 5. Organizar Camadas
1. Selecione um objeto
2. Use os botões no painel de propriedades:
   - "⬆️ Frente": Move uma camada para frente
   - "⬇️ Trás": Move uma camada para trás
   - "⏫ Topo": Move para a camada superior
   - "⏬ Fundo": Move para a camada inferior

## ⌨️ Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl + T` | Adicionar texto |
| `Ctrl + D` | Duplicar objeto selecionado |
| `Delete` | Excluir objeto selecionado |
| `Backspace` | Excluir objeto selecionado |
| `Scroll` | Zoom in/out no canvas |

## 🎛️ Controles Principais

### Toolbar Superior
- **📝 Texto**: Adiciona novo texto editável
- **🧲 Snap**: Liga/desliga alinhamento automático
- **📋 Duplicar**: Duplica objeto selecionado
- **🗑️ Excluir**: Remove objeto selecionado

### Painel de Propriedades
- **Posição**: Coordenadas X e Y
- **Tamanho**: Largura e altura
- **Rotação**: Controle de ângulo
- **Opacidade**: Nível de transparência
- **Camadas**: Controles de sobreposição

### Painel de Objetos
- Lista todos os elementos na cena
- Mostra hierarquia de camadas
- Permite seleção rápida de objetos

## 🔧 Configurações Avançadas

### Snap e Alinhamento
- **Threshold**: 10 pixels para snap automático
- **Bordas**: Snap nas bordas do canvas
- **Objetos**: Snap entre objetos na cena
- **Toggle**: Botão para ativar/desativar

### Zoom
- **Mínimo**: 0.1x (10%)
- **Máximo**: 3x (300%)
- **Método**: Scroll do mouse
- **Centro**: Zoom baseado na posição do cursor

### Performance
- **Renderização**: Otimizada com Fabric.js
- **Estados**: Atualizações inteligentes
- **Memória**: Cleanup automático de recursos

## 🐛 Resolução de Problemas

### Canvas não carrega
- Verifique se o Fabric.js foi instalado corretamente
- Confirme que o canvas DOM está disponível
- Verifique erros no console do navegador

### Drag & Drop não funciona
- Confirme que o AssetPanel está configurado corretamente
- Verifique se os dados estão sendo transferidos
- Certifique-se que preventDefault está sendo chamado

### Objetos não se movem
- Verifique se o objeto está selecionado
- Confirme que selectable está como true
- Verifique se não há overlays interferindo

### Performance lenta
- Reduza o número de objetos na cena
- Desative snap temporariamente
- Verifique o nível de zoom

## 📝 Estrutura de Dados

### Objeto Canvas
```javascript
{
  objectId: "uuid-v4",
  objectType: "avatar|text|image|background",
  name: "Nome do objeto",
  left: 100,
  top: 50,
  width: 200,
  height: 300,
  scaleX: 1,
  scaleY: 1,
  angle: 0,
  opacity: 1,
  metadata: { /* dados específicos */ }
}
```

### Estado da Cena
```javascript
{
  id: "scene-id",
  canvasData: { /* dados do Fabric.js */ },
  objects: [ /* lista de objetos */ ],
  lastModified: "2024-01-15T10:30:00Z"
}
```

## 🔄 Atualizações Futuras

### Planejadas
- [ ] Sistema de Undo/Redo
- [ ] Histórico de alterações
- [ ] Animações e transições
- [ ] Filtros e efeitos visuais
- [ ] Templates de cena
- [ ] Exportação de imagens
- [ ] Colaboração em tempo real

### Em Consideração
- [ ] Camadas aninhadas
- [ ] Grupos de objetos
- [ ] Máscaras e recortes
- [ ] Efeitos de sombreamento
- [ ] Gradientes personalizados

## 🤝 Contribuição

Para contribuir com melhorias:

1. Documente novas funcionalidades
2. Mantenha compatibilidade com API existente
3. Teste em diferentes navegadores
4. Siga os padrões de código estabelecidos
5. Atualize a documentação

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique este README primeiro
- Consulte a documentação do Fabric.js
- Abra uma issue com detalhes específicos
- Inclua capturas de tela quando relevante

---

**TecnoCursos AI** - Sistema Revolucionário de Geração de Vídeos Educacionais 🚀 