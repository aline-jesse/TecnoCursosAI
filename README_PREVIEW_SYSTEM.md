# 🎬 Sistema de Preview de Vídeo - TecnoCursos AI

## Visão Geral

O sistema de preview implementado no TecnoCursos AI oferece uma visualização em tempo real do resultado final do vídeo, simulando todas as animações, efeitos e elementos que serão incluídos no vídeo final. Este sistema utiliza Canvas API para renderização de alta performance e oferece controles profissionais de reprodução.

## 🚀 Funcionalidades Principais

### 1. **Preview em Tempo Real**
- Renderização em tempo real usando Canvas API
- Animações suaves e fluidas (60 FPS)
- Simulação precisa do resultado final
- Suporte a múltiplos tipos de elementos

### 2. **Tipos de Elementos Suportados**
- **Texto**: Com formatação completa, sombras e animações
- **Imagens**: Com transformações e efeitos
- **Formas**: Retângulos, círculos e outras formas geométricas
- **Avatares**: Com expressões faciais e animações
- **Backgrounds**: Cores sólidas, gradientes e imagens

### 3. **Sistema de Animações**
- **Posição**: Movimento suave entre pontos
- **Escala**: Zoom in/out com easing
- **Rotação**: Rotação 2D com controle de ângulo
- **Easing**: Múltiplas funções de easing (linear, ease-in, ease-out, ease-in-out)

### 4. **Controles Profissionais**
- **Play/Pause**: Controle de reprodução
- **Stop**: Parar e voltar ao início
- **Seek**: Navegação por timeline
- **Velocidade**: 0.25x a 2x
- **Volume**: Controle de áudio
- **Fullscreen**: Modo tela cheia
- **Export**: Exportar frames como PNG

## 🏗️ Arquitetura do Sistema

### Componentes Principais

#### 1. **VideoPreview.jsx**
```javascript
// Componente principal do preview
<VideoPreview
  scenes={previewScenes}
  currentScene={currentPreviewScene}
  onSceneChange={handlePreviewSceneChange}
  onClose={handleClosePreview}
  isVisible={showPreview}
/>
```

**Funcionalidades:**
- Renderização do canvas
- Controles de reprodução
- Timeline interativo
- Sistema de animações
- Exportação de frames

#### 2. **usePreviewData.js**
```javascript
// Hook para gerenciar dados de preview
const { previewData, generatePreviewData } = usePreviewData();
```

**Funcionalidades:**
- Geração de dados de exemplo
- Conversão de cenas para formato de preview
- Gerenciamento de estado
- Estruturação de animações

### Estrutura de Dados

#### Cena de Preview
```javascript
{
  id: 'scene-1',
  title: 'Introdução',
  duration: 5000, // 5 segundos
  background: {
    type: 'gradient',
    colors: ['#667eea', '#764ba2']
  },
  elements: [
    {
      id: 'title-1',
      type: 'text',
      content: 'Bem-vindo ao TecnoCursos AI',
      position: { x: 400, y: 200 },
      style: {
        fontFamily: 'Arial',
        fontSize: 48,
        color: '#ffffff',
        textAlign: 'center',
        fontWeight: 'bold',
        shadow: {
          enabled: true,
          color: '#000000',
          blur: 4,
          offsetX: 2,
          offsetY: 2
        }
      },
      animation: {
        position: {
          start: { x: 400, y: 100 },
          end: { x: 400, y: 200 },
          duration: 2000,
          easing: 'ease-out'
        },
        scale: {
          start: 0.8,
          end: 1,
          duration: 1500,
          easing: 'ease-out'
        }
      }
    }
  ]
}
```

## 🎨 Sistema de Animações

### Tipos de Animação

#### 1. **Animação de Posição**
```javascript
animation: {
  position: {
    start: { x: 0, y: 0 },
    end: { x: 400, y: 200 },
    duration: 2000,
    easing: 'ease-out'
  }
}
```

#### 2. **Animação de Escala**
```javascript
animation: {
  scale: {
    start: 0.5,
    end: 1.2,
    duration: 1500,
    easing: 'ease-out'
  }
}
```

#### 3. **Animação de Rotação**
```javascript
animation: {
  rotation: {
    start: -15,
    end: 0,
    duration: 1000,
    easing: 'ease-out'
  }
}
```

### Funções de Easing

- **linear**: Movimento constante
- **ease-in**: Aceleração gradual
- **ease-out**: Desaceleração gradual
- **ease-in-out**: Aceleração e desaceleração

## 🎯 Como o Preview Simula o Resultado Final

### 1. **Renderização em Tempo Real**
O preview utiliza Canvas API para renderizar cada frame em tempo real, calculando:
- Posição atual de cada elemento
- Transformações aplicadas (escala, rotação)
- Efeitos visuais (sombras, bordas)
- Transições entre cenas

### 2. **Sincronização de Tempo**
```javascript
// Cálculo de tempo para animações
const elapsedTime = currentTime - sceneStartTime;
const progress = Math.min(elapsedTime / animationDuration, 1);
const easedProgress = applyEasing(progress, easing);
```

### 3. **Interpolação de Valores**
```javascript
// Interpolação linear para posição
const currentX = startX + (endX - startX) * easedProgress;
const currentY = startY + (endY - startY) * easedProgress;
```

### 4. **Renderização de Elementos**
```javascript
// Renderização de texto com animações
const renderText = (ctx, element, style) => {
  ctx.font = `${style.fontWeight} ${style.fontSize}px ${style.fontFamily}`;
  ctx.fillStyle = style.color;
  ctx.textAlign = style.textAlign;
  
  // Aplicar sombra se configurada
  if (style.shadow?.enabled) {
    ctx.shadowColor = style.shadow.color;
    ctx.shadowBlur = style.shadow.blur;
    ctx.shadowOffsetX = style.shadow.offsetX;
    ctx.shadowOffsetY = style.shadow.offsetY;
  }
  
  ctx.fillText(element.content, 0, 0);
};
```

## 🎮 Controles de Interface

### Timeline Interativo
- **Slider**: Navegação visual pelo tempo
- **Display de Tempo**: Formato MM:SS
- **Marcadores**: Indicadores de cenas
- **Seek**: Clique direto para posição

### Controles de Reprodução
- **Play/Pause**: Alternar reprodução
- **Stop**: Parar e resetar
- **Skip**: Avançar/voltar 5 segundos
- **Velocidade**: 0.25x, 0.5x, 1x, 1.5x, 2x

### Controles Avançados
- **Fullscreen**: Modo tela cheia
- **Export**: Salvar frame atual
- **Volume**: Controle de áudio
- **FPS**: Indicador de performance

## 📊 Performance e Otimização

### 1. **RequestAnimationFrame**
```javascript
const animate = useCallback(() => {
  if (!isPlaying) return;
  
  // Renderizar frame atual
  renderCurrentFrame();
  
  // Atualizar tempo
  setCurrentTime(prev => prev + frameTime);
  
  // Continuar animação
  animationRef.current = requestAnimationFrame(animate);
}, [isPlaying, currentTime]);
```

### 2. **Cache de Imagens**
```javascript
const imageCache = new Map();

const loadImage = (url) => {
  if (imageCache.has(url)) {
    return imageCache.get(url);
  }
  
  const img = new Image();
  img.onload = () => imageCache.set(url, img);
  img.src = url;
  return img;
};
```

### 3. **Otimização de Canvas**
```javascript
// Configurações de alta performance
canvas.width = 1920;
canvas.height = 1080;
ctx.imageSmoothingEnabled = true;
ctx.imageSmoothingQuality = 'high';
```

## 🔧 Integração com o Sistema

### 1. **No App.jsx**
```javascript
// Estados do preview
const [showPreview, setShowPreview] = useState(false);
const [previewScenes, setPreviewScenes] = useState([]);
const [currentPreviewScene, setCurrentPreviewScene] = useState(0);

// Função para abrir preview
const handleOpenPreview = (scenes = []) => {
  generatePreviewData(scenes);
  setPreviewScenes(previewData.scenes);
  setShowPreview(true);
};
```

### 2. **No ProjectWorkflow.jsx**
```javascript
// Botão de preview
<button
  onClick={() => onOpenPreview && onOpenPreview(scenes)}
  disabled={scenes.length === 0}
  className="preview-btn"
>
  <FiEye className="mr-2" />
  Preview
</button>
```

## 🎨 Estilos e Design

### Tema Escuro Profissional
- **Background**: Gradiente escuro (#1a1a1a)
- **Controles**: Semi-transparentes com hover effects
- **Timeline**: Slider customizado com gradiente azul
- **Animações**: Transições suaves e responsivas

### Responsividade
- **Desktop**: Layout completo com controles laterais
- **Tablet**: Controles reorganizados
- **Mobile**: Interface simplificada

## 🚀 Próximas Melhorias

### 1. **Recursos Planejados**
- [ ] Suporte a áudio em tempo real
- [ ] Efeitos de transição entre cenas
- [ ] Templates pré-definidos
- [ ] Exportação de vídeo direto
- [ ] Compartilhamento de preview

### 2. **Otimizações**
- [ ] WebGL para renderização 3D
- [ ] Compressão de frames
- [ ] Cache inteligente
- [ ] Lazy loading de assets

### 3. **Funcionalidades Avançadas**
- [ ] Editor de animações visual
- [ ] Keyframes customizados
- [ ] Efeitos de partículas
- [ ] Integração com IA para sugestões

## 📝 Exemplo de Uso

```javascript
// Abrir preview com cenas existentes
const handlePreviewClick = () => {
  const projectScenes = [
    {
      id: 'scene-1',
      title: 'Introdução',
      content: 'Bem-vindo ao curso!',
      duration: 5000
    },
    {
      id: 'scene-2', 
      title: 'Conteúdo Principal',
      content: 'Aqui está o conteúdo...',
      duration: 8000
    }
  ];
  
  onOpenPreview(projectScenes);
};
```

## 🎯 Benefícios do Sistema

### 1. **Feedback Imediato**
- Visualização instantânea das mudanças
- Preview antes da geração final
- Correção rápida de problemas

### 2. **Experiência Profissional**
- Interface similar a editores profissionais
- Controles intuitivos e responsivos
- Performance otimizada

### 3. **Integração Perfeita**
- Funciona com o sistema existente
- Dados reais do projeto
- Exportação direta para vídeo

---

**🎬 O sistema de preview do TecnoCursos AI oferece uma experiência completa de visualização, permitindo que os usuários vejam exatamente como seu vídeo final será antes mesmo de gerá-lo. Com animações suaves, controles profissionais e interface intuitiva, é a ferramenta perfeita para criar vídeos de alta qualidade.** 