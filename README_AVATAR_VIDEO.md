# 🎭 Gerador de Vídeo do Avatar - TecnoCursos AI

Sistema completo para geração de vídeos educacionais com avatar animado, áudio TTS sincronizado e slides personalizados usando MoviePy.

## ✨ Funcionalidades

- 🎭 **Avatar Animado**: Personagem virtual com animações de fala sincronizadas
- 🎤 **TTS Avançado**: Narração usando Bark AI ou Google TTS
- 📄 **Slides Dinâmicos**: Slides customizáveis com diferentes templates
- 🎬 **Vídeo HD/4K**: Exportação em diferentes qualidades
- 🎨 **Personalização Total**: Cores, estilos e configurações ajustáveis

## 🚀 Instalação

### Dependências Principais

```bash
pip install moviepy pillow opencv-python numpy pydub
```

### Dependências Opcionais (TTS Avançado)

```bash
pip install transformers torch torchaudio gtts
```

## 📋 Uso Básico

### Exemplo Simples

```python
import asyncio
from services.avatar_video_generator import generate_avatar_video

async def criar_video():
    # Dados dos slides
    slides = [
        {
            "title": "Introdução ao Python",
            "content": "Python é uma linguagem poderosa e fácil de aprender."
        },
        {
            "title": "Variáveis",
            "content": "Em Python, criar variáveis é muito simples."
        }
    ]
    
    # Textos para narração
    textos = [
        "Bem-vindos ao curso de Python!",
        "Vamos aprender sobre variáveis em Python."
    ]
    
    # Gerar vídeo
    resultado = await generate_avatar_video(
        slides=slides,
        audio_texts=textos,
        output_path="./meu_video.mp4",
        avatar_style="teacher",
        video_quality="1080p"
    )
    
    if resultado["success"]:
        print(f"✅ Vídeo criado: {resultado['output_path']}")
    else:
        print(f"❌ Erro: {resultado['error']}")

# Executar
asyncio.run(criar_video())
```

## 🎨 Personalização Avançada

### Avatar Personalizado

```python
from services.avatar_video_generator import (
    AvatarVideoGenerator, VideoContent, AvatarStyle
)

async def video_personalizado():
    # Criar gerador
    generator = AvatarVideoGenerator()
    
    # Personalizar avatar
    generator.update_avatar_config(
        style=AvatarStyle.FRIENDLY,
        skin_tone="#f4c2a1",      # Tom de pele
        hair_color="#654321",     # Cor do cabelo
        shirt_color="#e74c3c",    # Cor da camisa
        enable_animation=True     # Animações
    )
    
    # Configurar vídeo
    generator.update_video_config(
        resolution=(1920, 1080),  # Full HD
        fps=30,                   # 30 FPS
        fade_in_duration=1.0      # Fade in
    )
    
    # Configurar slides
    generator.update_slide_config(
        title_color="#2c3e50",    # Cor do título
        content_color="#34495e",  # Cor do conteúdo
        accent_color="#e74c3c"    # Cor de destaque
    )
    
    # Criar conteúdo
    content = VideoContent(
        slides=[{"title": "Meu Slide", "content": "Conteúdo aqui"}],
        audio_texts=["Texto para narração"]
    )
    
    # Gerar vídeo
    resultado = await generator.generate_video(
        content=content,
        output_path="./video_personalizado.mp4"
    )
    
    return resultado
```

## 🎭 Estilos de Avatar

| Estilo | Descrição | Uso Recomendado |
|--------|-----------|-----------------|
| `professional` | Aparência formal e corporativa | Treinamentos empresariais |
| `friendly` | Visual caloroso e acessível | Cursos gerais |
| `teacher` | Otimizado para educação | Aulas e tutoriais |
| `minimal` | Design simples e clean | Apresentações técnicas |

## 📺 Qualidades de Vídeo

| Qualidade | Resolução | Uso Recomendado |
|-----------|-----------|-----------------|
| `720p` | 1280x720 | Testes rápidos, baixa largura de banda |
| `1080p` | 1920x1080 | Qualidade padrão para web |
| `4k` | 3840x2160 | Máxima qualidade, apresentações profissionais |

## 🎤 Configurações de TTS

### Providers Disponíveis

- **`auto`**: Seleção automática do melhor provider
- **`bark`**: TTS avançado com vozes naturais (requer transformers)
- **`gtts`**: Google TTS rápido e confiável

### Vozes Disponíveis (Bark)

- `pt_speaker_0` a `pt_speaker_9`: Vozes em português
- Diferentes tons e estilos de fala

## 🛠️ Configurações Detalhadas

### Avatar Config

```python
avatar_config = {
    "style": AvatarStyle.TEACHER,
    "skin_tone": "#fdbcb4",        # Hex color
    "hair_color": "#8b4513",       # Hex color  
    "shirt_color": "#4a90e2",      # Hex color
    "background_color": "#f0f0f0", # Hex color
    "enable_animation": True,      # Animações
    "enable_gestures": True,       # Gestos
    "eye_blink": True,             # Piscar olhos
    "mouth_animation": True        # Animação boca
}
```

### Video Config

```python
video_config = {
    "resolution": (1920, 1080),    # Largura x Altura
    "fps": 30,                     # Frames por segundo
    "codec": "libx264",            # Codec de vídeo
    "audio_codec": "aac",          # Codec de áudio
    "bitrate": "2000k",            # Taxa de bits
    "fade_in_duration": 0.5,       # Fade in (segundos)
    "fade_out_duration": 0.5       # Fade out (segundos)
}
```

### Slide Config

```python
slide_config = {
    "template": "modern",          # Template do slide
    "font_family": "Arial",        # Família da fonte
    "title_size": 48,              # Tamanho título
    "content_size": 32,            # Tamanho conteúdo
    "title_color": "#2c3e50",      # Cor título
    "content_color": "#34495e",    # Cor conteúdo
    "background_color": "#ffffff", # Cor fundo
    "accent_color": "#3498db",     # Cor destaque
    "show_slide_numbers": True     # Mostrar números
}
```

## 🔧 Executando os Exemplos

### Exemplo Básico

```bash
python exemplo_avatar_simples.py
```

### Teste Completo

```bash
python test_avatar_video.py
```

## 📁 Estrutura de Arquivos

```
TecnoCursosAI/
├── services/
│   ├── avatar_video_generator.py  # Gerador principal
│   └── tts_service.py            # Serviço TTS
├── exemplo_avatar_simples.py     # Exemplo básico
├── test_avatar_video.py          # Testes completos
└── README_AVATAR_VIDEO.md        # Esta documentação
```

## 🎯 Fluxo de Processamento

1. **📄 Preparação**: Análise dos slides e textos de entrada
2. **🎤 TTS**: Geração do áudio usando Bark ou Google TTS
3. **🎭 Avatar**: Criação dos frames animados sincronizados
4. **📺 Slides**: Renderização dos slides com layout personalizado
5. **🎬 Composição**: Combinação de avatar, slides e áudio
6. **💾 Export**: Renderização final do vídeo MP4

## 📊 Resultados

### Informações Retornadas

```python
resultado = {
    "success": True,               # Status da geração
    "output_path": "video.mp4",    # Caminho do arquivo
    "duration": 45.2,              # Duração em segundos
    "slides_count": 3,             # Número de slides
    "resolution": "1920x1080",     # Resolução final
    "fps": 30,                     # FPS final
    "file_size": 15728640          # Tamanho em bytes
}
```

## ⚡ Performance

### Tempos Estimados (Full HD, 30fps)

- **1 slide (~15s)**: 30-60 segundos
- **5 slides (~2min)**: 2-5 minutos  
- **10 slides (~5min)**: 5-15 minutos

### Fatores que Afetam Performance

- Resolução do vídeo
- Duração do áudio
- Complexidade dos slides
- Provider TTS usado
- Hardware disponível

## 🚨 Troubleshooting

### Erros Comuns

#### ImportError: MoviePy

```bash
pip install moviepy
```

#### Erro de Codec

```bash
# No Ubuntu/Debian
sudo apt install ffmpeg

# No Windows (via chocolatey)
choco install ffmpeg

# No macOS
brew install ffmpeg
```

#### TTS não funciona

```bash
# Para Bark TTS
pip install transformers torch

# Para Google TTS
pip install gtts
```

#### Erro de memória

- Use resolução menor (720p)
- Reduza FPS para 24
- Processe slides em lotes menores

### Logs de Debug

Para debugar problemas, ative logs detalhados:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🌟 Exemplos Avançados

### Vídeo com Música de Fundo

```python
generator.update_video_config(
    background_music="./musica_fundo.mp3",
    music_volume=0.1  # 10% do volume
)
```

### Avatar com Gestos

```python
generator.update_avatar_config(
    enable_gestures=True,
    style=AvatarStyle.TEACHER
)
```

### Slides com Templates

```python
generator.update_slide_config(
    template="minimal",  # ou "classic", "modern"
    accent_color="#ff6b6b"
)
```

## 🔮 Futuras Melhorias

- [ ] Múltiplos avatares na mesma cena
- [ ] Gestos mais complexos
- [ ] Sincronização labial avançada
- [ ] Templates de slides adicionais
- [ ] Suporte a vídeos de fundo
- [ ] Integração com IA generativa

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação acima
2. Execute os exemplos fornecidos
3. Consulte os logs de erro
4. Abra uma issue no repositório

---

**TecnoCursos AI** - Transformando educação com tecnologia! 🚀 