# 📋 Guia de Criação de Templates - TecnoCursos AI

## 🎯 Visão Geral

O sistema de templates permite criar modelos pré-configurados de cenas que podem ser rapidamente aplicados pelo usuário. Este guia explica como criar e customizar templates.

## 🏗️ Estrutura de um Template

### Tipo Base: `SceneTemplate`

```typescript
interface SceneTemplate {
  id: string                    // ID único do template
  name: string                  // Nome exibido na galeria
  category: TemplateCategory    // Categoria do template
  description: string           // Descrição do que o template faz
  thumbnail: string             // URL da imagem de preview
  duration: number              // Duração padrão em segundos
  background: TemplateBackground // Configuração de fundo
  elements: TemplateElement[]   // Elementos inclusos
  audio?: TemplateAudio        // Configurações de áudio (opcional)
  tags: string[]               // Tags para busca
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  createdAt: Date
  updatedAt: Date
  replaceable: {               // Elementos que o usuário pode editar
    title?: string
    subtitle?: string
    mainImage?: string
    avatar?: string
  }
}
```

## 🎨 Elementos Disponíveis

### 1. Elementos de Texto

```typescript
interface TemplateTextElement {
  type: 'text'
  id: string
  content: string              // Texto padrão
  position: { x: number; y: number }
  style: {
    fontSize: number
    fontFamily: string
    color: string
    fontWeight: 'normal' | 'bold' | 'lighter'
    textAlign: 'left' | 'center' | 'right'
    textShadow?: string       // CSS text-shadow
    animation?: string        // Animação CSS
  }
  editable: boolean           // Se o usuário pode editar
}
```

### 2. Elementos de Imagem

```typescript
interface TemplateImageElement {
  type: 'image'
  id: string
  src: string                 // URL ou caminho da imagem
  position: { x: number; y: number }
  size: { width: number; height: number }
  style: {
    opacity: number
    borderRadius: number
    filter?: string          // CSS filters
    animation?: string
  }
  editable: boolean
}
```

### 3. Elementos de Avatar

```typescript
interface TemplateAvatarElement {
  type: 'avatar'
  id: string
  avatarType: 'male' | 'female' | 'robot' | 'custom'
  position: { x: number; y: number }
  size: { width: number; height: number }
  style: {
    animation?: string
    expression?: 'neutral' | 'happy' | 'serious' | 'excited'
  }
  speech?: {
    text: string             // Texto falado pelo avatar
    voice: 'male' | 'female' | 'robotic'
    duration: number         // Duração da fala
  }
  editable: boolean
}
```

### 4. Elementos de Efeito

```typescript
interface TemplateEffectElement {
  type: 'effect'
  id: string
  effectType: 'particles' | 'glow' | 'shake' | 'zoom' | 'fade' | 'slide'
  position?: { x: number; y: number }
  properties: {
    duration: number
    intensity: number
    color?: string
    direction?: 'up' | 'down' | 'left' | 'right'
  }
}
```

## 🖼️ Configuração de Background

```typescript
interface TemplateBackground {
  type: 'color' | 'gradient' | 'image' | 'video'
  value: string              // Cor, CSS gradient, ou URL
  overlay?: {
    color: string
    opacity: number          // 0.0 a 1.0
  }
}
```

**Exemplos:**
```javascript
// Cor sólida
{ type: 'color', value: '#3b82f6' }

// Gradiente
{ 
  type: 'gradient', 
  value: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
}

// Imagem com overlay
{
  type: 'image',
  value: '/backgrounds/corporate.jpg',
  overlay: { color: '#000000', opacity: 0.3 }
}
```

## 🔊 Configuração de Áudio

```typescript
interface TemplateAudio {
  backgroundMusic?: {
    src: string              // URL do arquivo de áudio
    volume: number           // 0.0 a 1.0
    loop: boolean
  }
  soundEffects?: Array<{
    id: string
    src: string
    trigger: 'start' | 'middle' | 'end' | number  // Momento em segundos
    volume: number
  }>
}
```

## 📝 Passo a Passo: Criando um Novo Template

### 1. Definir o Template Base

```javascript
const meuTemplate = {
  id: 'meu-template-customizado',
  name: 'Meu Template Personalizado',
  category: 'educational',  // Ver categorias disponíveis
  description: 'Template para conteúdo educacional interativo',
  thumbnail: '/templates/thumbnails/meu-template.jpg',
  duration: 10,
  // ... resto da configuração
}
```

### 2. Configurar o Background

```javascript
background: {
  type: 'gradient',
  value: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
  overlay: {
    color: '#ffffff',
    opacity: 0.1
  }
}
```

### 3. Adicionar Elementos

```javascript
elements: [
  // Título principal
  {
    type: 'text',
    id: 'main-title',
    content: 'TÍTULO EDITÁVEL',
    position: { x: 960, y: 300 },  // Centro horizontal
    style: {
      fontSize: 64,
      fontFamily: 'Arial Black',
      color: '#ffffff',
      fontWeight: 'bold',
      textAlign: 'center',
      textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
      animation: 'fadeInUp'
    },
    editable: true  // Usuário pode editar este texto
  },

  // Avatar interativo
  {
    type: 'avatar',
    id: 'instructor-avatar',
    avatarType: 'female',
    position: { x: 200, y: 400 },
    size: { width: 300, height: 400 },
    style: {
      expression: 'happy',
      animation: 'wave'
    },
    speech: {
      text: 'Olá! Vamos aprender algo novo hoje!',
      voice: 'female',
      duration: 4
    },
    editable: true
  },

  // Efeito visual
  {
    type: 'effect',
    id: 'sparkle-effect',
    effectType: 'particles',
    properties: {
      duration: 10,
      intensity: 0.7,
      color: '#ffd700'
    }
  }
]
```

### 4. Definir Elementos Editáveis

```javascript
replaceable: {
  title: 'main-title',      // ID do elemento de título
  avatar: 'instructor-avatar', // ID do avatar
  // subtitle: 'subtitle-id',  // Opcional
  // mainImage: 'image-id'     // Opcional
}
```

### 5. Adicionar Tags e Metadados

```javascript
tags: ['educação', 'interativo', 'avatar', 'aprendizado'],
difficulty: 'intermediate',
createdAt: new Date(),
updatedAt: new Date()
```

## 📂 Adicionando o Template ao Sistema

### Opção 1: Template Pré-definido (Recomendado)

Adicione seu template ao arquivo `src/data/sceneTemplates.ts`:

```javascript
export const SCENE_TEMPLATES: SceneTemplate[] = [
  // ... templates existentes
  
  // Seu novo template
  {
    id: 'meu-template-customizado',
    name: 'Meu Template Personalizado',
    // ... configuração completa
  }
]
```

### Opção 2: Template Dinâmico

Use o hook `useTemplates` para criar templates em runtime:

```javascript
const { createTemplate } = useTemplates()

const criarMeuTemplate = async () => {
  const config = {
    name: 'Template Dinâmico',
    category: 'educational',
    description: 'Criado dinamicamente',
    elements: [/* seus elementos */],
    background: {/* configuração */},
    duration: 8,
    tags: ['dinâmico']
  }
  
  const novoTemplate = await createTemplate(config)
  console.log('Template criado:', novoTemplate.id)
}
```

## 🎭 Categorias de Templates

| Categoria | Descrição | Uso Típico |
|-----------|-----------|------------|
| `opening` | Abertura de vídeo | Introduções, boas-vindas |
| `alert` | Avisos importantes | Alertas, avisos, atenção |
| `checklist` | Listas e checklists | Passos, itens, tarefas |
| `comparison` | Comparações | Antes/depois, vs, diferenças |
| `testimonial` | Depoimentos | Reviews, opiniões, feedback |
| `call-to-action` | Chamadas para ação | Inscreva-se, compre, clique |
| `closing` | Encerramento | Agradecimentos, fim |
| `transition` | Transições | Entre seções, mudanças |
| `educational` | Educacional | Ensino, explicações |
| `promotional` | Promocional | Vendas, marketing |

## 🎨 Guia de Posicionamento

### Sistema de Coordenadas
- **Origem (0,0)**: Canto superior esquerdo
- **Canvas padrão**: 1920x1080 pixels (16:9)
- **Centro**: x: 960, y: 540

### Posições Comuns
```javascript
// Posições de texto
const positions = {
  titleTop: { x: 960, y: 200 },        // Título no topo
  titleCenter: { x: 960, y: 400 },     // Título centralizado
  subtitleBelow: { x: 960, y: 500 },   // Subtítulo abaixo do título
  
  // Posições de avatar
  leftAvatar: { x: 200, y: 400 },      // Avatar à esquerda
  rightAvatar: { x: 1400, y: 400 },    // Avatar à direita
  centerAvatar: { x: 960, y: 500 },    // Avatar centralizado
  
  // Posições de imagem
  backgroundImage: { x: 0, y: 0 },     // Imagem de fundo
  centerImage: { x: 960, y: 540 }      // Imagem centralizada
}
```

## 🎬 Animações Disponíveis

### Animações de Entrada
- `fadeIn` - Aparece gradualmente
- `fadeInUp` - Aparece de baixo para cima
- `fadeInDown` - Aparece de cima para baixo
- `slideInLeft` - Desliza da esquerda
- `slideInRight` - Desliza da direita
- `bounceIn` - Aparece com efeito de bounce
- `zoomIn` - Aparece com zoom

### Animações Contínuas
- `pulse` - Pulsa continuamente
- `bounce` - Pula continuamente
- `shake` - Balança
- `wave` - Acena (para avatares)
- `float` - Flutua suavemente

## 🎤 Configuração de Fala do Avatar

```javascript
speech: {
  text: 'O que o avatar vai falar',
  voice: 'female',    // 'male', 'female', 'robotic'
  duration: 5         // Duração em segundos
}
```

**Dicas para Fala:**
- Mantenha textos entre 10-50 palavras
- Use pontuação para pausas naturais
- Teste a duração com diferentes vozes
- Considere a sincronia com outros elementos

## 🖼️ Criando Thumbnails

### Especificações
- **Dimensões**: 400x300 pixels (4:3)
- **Formato**: JPG ou PNG
- **Qualidade**: Alta qualidade, otimizado para web
- **Local**: `/public/templates/thumbnails/`

### Dicas de Design
1. **Represente visualmente** o template
2. **Use cores vibrantes** que se destaquem
3. **Inclua elementos chave** do template
4. **Mantenha texto legível** mesmo em tamanho pequeno
5. **Use mockups** para mostrar o resultado final

### Ferramentas Recomendadas
- **Design**: Figma, Canva, Photoshop
- **Otimização**: TinyPNG, ImageOptim
- **Mockups**: Smartmockups, Placeit

## 🔍 Testando seu Template

### 1. Validação Básica
```javascript
// Verificar se todos os campos obrigatórios estão preenchidos
const validarTemplate = (template) => {
  const required = ['id', 'name', 'category', 'description', 'elements']
  return required.every(field => template[field])
}
```

### 2. Teste de Aplicação
```javascript
const { applyTemplate } = useTemplates()

const testarTemplate = async () => {
  try {
    const resultado = await applyTemplate(meuTemplate)
    if (resultado.success) {
      console.log('✅ Template aplicado com sucesso!')
      console.log('Elementos editáveis:', resultado.editableElements)
    }
  } catch (error) {
    console.error('❌ Erro ao aplicar template:', error)
  }
}
```

### 3. Checklist de Qualidade

- [ ] **ID único** e descritivo
- [ ] **Nome claro** e não ambíguo
- [ ] **Descrição informativa** do propósito
- [ ] **Categoria correta** selecionada
- [ ] **Thumbnail** representativa e de qualidade
- [ ] **Elementos posicionados** corretamente
- [ ] **Textos editáveis** marcados como `editable: true`
- [ ] **Durações realistas** para fala e animações
- [ ] **Tags relevantes** para facilitar busca
- [ ] **Testado** em diferentes resoluções

## 🚀 Dicas Avançadas

### 1. Responsividade
```javascript
// Use posições relativas quando possível
position: { 
  x: canvasWidth * 0.5,    // 50% da largura
  y: canvasHeight * 0.3    // 30% da altura
}
```

### 2. Elementos Condicionais
```javascript
// Adicione elementos baseado em condições
if (incluirAvatar) {
  elements.push(avatarElement)
}
```

### 3. Variações de Template
```javascript
// Crie variações do mesmo template
const criarVariacoes = (templateBase) => {
  return ['blue', 'red', 'green'].map(color => ({
    ...templateBase,
    id: `${templateBase.id}-${color}`,
    name: `${templateBase.name} (${color})`,
    background: { ...templateBase.background, value: colors[color] }
  }))
}
```

### 4. Templates Baseados em Dados
```javascript
// Template que se adapta aos dados fornecidos
const criarTemplateComDados = (dados) => {
  return {
    // ... configuração base
    elements: dados.items.map((item, index) => ({
      type: 'text',
      id: `item-${index}`,
      content: item.texto,
      position: { x: 100, y: 200 + (index * 50) }
    }))
  }
}
```

## 🐛 Solução de Problemas

### Problema: Template não aparece na galeria
- ✅ Verificar se foi adicionado ao array `SCENE_TEMPLATES`
- ✅ Verificar se o ID é único
- ✅ Validar estrutura do objeto

### Problema: Elementos não ficam editáveis
- ✅ Definir `editable: true` no elemento
- ✅ Adicionar ID do elemento em `replaceable`
- ✅ Verificar se o ID corresponde exatamente

### Problema: Thumbnail não carrega
- ✅ Verificar caminho do arquivo
- ✅ Confirmar que o arquivo existe
- ✅ Adicionar fallback para imagem padrão

### Problema: Animações não funcionam
- ✅ Verificar nome da animação CSS
- ✅ Confirmar que os keyframes existem
- ✅ Testar duração e timing

## 📚 Recursos Adicionais

### Arquivos de Referência
- `src/types/template.ts` - Definições de tipos
- `src/data/sceneTemplates.ts` - Templates existentes
- `src/hooks/useTemplates.ts` - Hook de gerenciamento
- `src/components/TemplateGallery.tsx` - Interface da galeria

### Exemplos Completos
Consulte os templates existentes no código para exemplos completos e funcionais.

---

## ✨ Conclusão

Com este guia, você pode criar templates profissionais e reutilizáveis para o TecnoCursos AI. Lembre-se de sempre testar seus templates antes de disponibilizá-los aos usuários e manter a documentação atualizada.

**Dúvidas?** Consulte o código fonte ou crie uma issue no repositório do projeto.

**Happy templating! 🎨✨**