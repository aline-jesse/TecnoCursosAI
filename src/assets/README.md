# 🎨 Assets - TecnoCursos AI Video Editor

Esta pasta contém todos os recursos visuais e de mídia utilizados no editor de vídeo.

## 📁 Estrutura dos Assets

### **Characters** - Personagens e Avatares

```
/characters/
├── teacher_1.png      - Professor masculino
├── teacher_2.png      - Professora feminina
├── student_1.png      - Estudante jovem
├── student_2.png      - Estudante adulto
├── scientist_1.png    - Cientista masculino
├── doctor_1.png       - Médica feminina
└── business_1.png     - Profissional de negócios
```

### **Backgrounds** - Fundos e Cenários

```
/backgrounds/
├── classroom_1.jpg    - Sala de aula moderna
├── lab_1.jpg          - Laboratório científico
├── office_1.jpg       - Escritório corporativo
├── library_1.jpg      - Biblioteca acadêmica
├── hospital_1.jpg     - Ambiente hospitalar
└── home_1.jpg         - Ambiente doméstico
```

### **Elements** - Elementos Gráficos

```
/elements/
├── chart_pie.png      - Gráfico de pizza
├── chart_bar.png      - Gráfico de barras
├── chart_line.png     - Gráfico de linha
├── text_box.png       - Caixa de texto
├── arrow.png          - Seta direcional
├── star.png           - Estrela decorativa
└── checkmark.png      - Check mark
```

### **Icons** - Ícones da Interface

```
/icons/
├── play.svg           - Botão play
├── pause.svg          - Botão pause
├── stop.svg           - Botão stop
├── zoom_in.svg        - Zoom in
├── zoom_out.svg       - Zoom out
├── select.svg         - Ferramenta seleção
├── text.svg           - Ferramenta texto
└── image.svg          - Ferramenta imagem
```

### **Scenes** - Miniaturas de Cenas

```
/scenes/
├── scene_1.jpg        - Thumbnail cena 1
├── scene_2.jpg        - Thumbnail cena 2
├── scene_3.jpg        - Thumbnail cena 3
└── scene_default.jpg  - Thumbnail padrão
```

## 🎯 Especificações Técnicas

### **Formatos Suportados**

- **Imagens:** PNG, JPG, SVG, WebP
- **Vídeos:** MP4, WebM, GIF
- **Áudios:** MP3, WAV, OGG

### **Dimensões Recomendadas**

- **Personagens:** 150x200px (PNG com transparência)
- **Fundos:** 1280x720px (JPG otimizado)
- **Elementos:** 64x64px ou 128x128px (PNG)
- **Ícones:** 24x24px (SVG vetorial)
- **Thumbnails:** 160x90px (JPG)

### **Otimização**

- Compressão automática para web
- Lazy loading implementado
- Fallbacks para assets não encontrados
- Cache inteligente de assets

## 🚀 Como Adicionar Novos Assets

### 1. **Personagens**

```javascript
// Adicionar ao mockAssets em AssetPanel.jsx
{
  id: 13,
  name: 'Novo Personagem',
  thumbnail: '/assets/characters/novo_personagem.png',
  category: 'characters'
}
```

### 2. **Fundos**

```javascript
// Adicionar à categoria backgrounds
{
  id: 14,
  name: 'Novo Fundo',
  thumbnail: '/assets/backgrounds/novo_fundo.jpg',
  category: 'backgrounds'
}
```

### 3. **Elementos**

```javascript
// Adicionar à categoria elements
{
  id: 15,
  name: 'Novo Elemento',
  thumbnail: '/assets/elements/novo_elemento.png',
  category: 'elements'
}
```

## 📊 Estatísticas dos Assets

- **Total de Assets:** 25+ elementos
- **Tamanho Total:** ~2MB (otimizado)
- **Formatos:** PNG, JPG, SVG
- **Compatibilidade:** 100% navegadores modernos

## 🔧 Ferramentas de Geração

Para criar novos assets, recomendamos:

- **Personagens:** Adobe Illustrator, Figma
- **Fundos:** Unsplash, Adobe Stock
- **Ícones:** Heroicons, Feather Icons
- **Elementos:** Canva, Adobe Illustrator

## 📝 Convenções de Nomenclatura

```
categoria_numero.extensão
professor_1.png
sala_aula_1.jpg
icone_play.svg
```

## 🎨 Paleta de Cores

### **Cores Principais**

- **Azul:** #3B82F6 (Botões primários)
- **Verde:** #10B981 (Sucesso)
- **Vermelho:** #EF4444 (Alertas)
- **Cinza:** #6B7280 (Texto secundário)

### **Cores de Fundo**

- **Branco:** #FFFFFF (Canvas)
- **Cinza Claro:** #F8FAFC (Painéis)
- **Cinza Escuro:** #1F2937 (Timeline)
