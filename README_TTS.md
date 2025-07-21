# 🎵 TTS Pipeline Bark - TecnoCursos AI

Sistema avançado de Text-to-Speech (TTS) com suporte ao Bark da Suno AI via Hugging Face, integrando perfeitamente com o processamento de PDFs e PPTXs para geração automática de narração.

## ✨ Funcionalidades

### 🤖 **Modelos TTS Suportados**
- **Bark TTS (Suno AI)** - Qualidade superior, vozes naturais
- **Google TTS (gTTS)** - Fallback rápido e confiável
- **Seleção Automática** - Escolhe o melhor modelo automaticamente

### 🎭 **Vozes Disponíveis (Português)**
- `pt_speaker_0` - Voz masculina neutra
- `pt_speaker_1` - Voz feminina suave  
- `pt_speaker_2` - Voz masculina jovem
- `pt_speaker_3` - Voz feminina profissional
- `pt_speaker_4` - Voz masculina grave
- `pt_speaker_5` - Voz feminina clara
- `pt_speaker_6` - Voz masculina amigável
- `pt_speaker_7` - Voz feminina energética
- `pt_speaker_8` - Voz masculina calma
- `pt_speaker_9` - Voz feminina doce

### 🚀 **Recursos Avançados**
- ✅ Geração de áudio em lote
- ✅ Cache inteligente de modelos
- ✅ Otimização automática (CPU/GPU)
- ✅ API RESTful completa
- ✅ Integração com processamento de documentos
- ✅ Limpeza automática de arquivos temporários
- ✅ Fallback automático entre modelos

## 📦 Instalação

### 1. **Instalação Básica (CPU)**
```bash
# Instalar dependências básicas
pip install gtts pydub scipy numpy

# Para funcionalidade completa
pip install torch torchvision torchaudio transformers
```

### 2. **Instalação com GPU (Recomendado)**
```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Transformers e dependências
pip install transformers accelerate

# Dependências de áudio
pip install gtts pydub scipy soundfile librosa
```

### 3. **Verificação da Instalação**
```bash
python test_tts_pipeline.py
```

## ⚙️ Configuração

### 1. **Arquivo .env**
```bash
# Copiar configurações de exemplo
cp env.example .env

# Editar configurações TTS
nano .env
```

### 2. **Configurações Principais**
```env
# Provider TTS (auto, bark, gtts)
TTS_PROVIDER=auto

# Configurações Bark
BARK_DEVICE=auto  # auto, cpu, cuda
BARK_VOICE_PRESET=pt_speaker_0
BARK_ENABLE_COMPILE=true

# Configurações de performance
TTS_MAX_CONCURRENT_JOBS=3
TTS_CACHE_DIR=./cache/tts
```

### 3. **Configurações por Ambiente**

#### 🛠️ **Desenvolvimento**
```env
TTS_PROVIDER=auto
BARK_DEVICE=cpu
DEBUG=true
```

#### 🚀 **Produção**
```env
TTS_PROVIDER=bark
BARK_DEVICE=cuda
BARK_ENABLE_COMPILE=true
TTS_MAX_CONCURRENT_JOBS=1
```

#### 💻 **Servidor Limitado**
```env
TTS_PROVIDER=gtts
# Usar apenas Google TTS
```

## 📚 Uso da API

### 1. **Status do Sistema**
```bash
GET /api/tts/status
```

**Resposta:**
```json
{
  "available_providers": ["bark", "gtts"],
  "available_voices": ["pt_speaker_0", "pt_speaker_1", ...],
  "config": {...},
  "system_status": {
    "config_valid": true,
    "provider_tests": {"bark": true, "gtts": true}
  }
}
```

### 2. **Gerar Áudio Simples**
```bash
POST /api/tts/generate
Content-Type: application/json

{
  "text": "Olá! Este é um teste do TTS Bark.",
  "provider": "auto",
  "voice": "pt_speaker_0",
  "language": "pt"
}
```

**Resposta:**
```json
{
  "success": true,
  "audio_url": "/api/tts/download/audio_123.mp3",
  "duration": 3.5,
  "provider_used": "bark",
  "file_size": 56832
}
```

### 3. **Gerar Áudio em Lote**
```bash
POST /api/tts/generate-batch
Content-Type: application/json

{
  "texts": [
    "Primeira parte do curso.",
    "Segunda parte do curso.",
    "Terceira parte do curso."
  ],
  "provider": "bark",
  "voice": "pt_speaker_1"
}
```

### 4. **Narração de Curso**
```bash
POST /api/tts/generate-course
Content-Type: application/json

{
  "sections": [
    {
      "title": "Introdução ao Python",
      "content": "Python é uma linguagem...",
      "notes": "Enfatizar simplicidade"
    },
    {
      "title": "Variáveis",
      "content": "Variáveis armazenam dados..."
    }
  ],
  "voice": "pt_speaker_0"
}
```

### 5. **Testar Sistema**
```bash
POST /api/tts/test
```

## 🐍 Uso Programático

### 1. **Importar Serviço**
```python
from services.tts_service import tts_service, TTSConfig, TTSProvider
```

### 2. **Gerar Áudio Simples**
```python
import asyncio
from services.tts_service import generate_narration

async def exemplo_basico():
    result = await generate_narration(
        text="Olá! Este é um teste.",
        voice="pt_speaker_0",
        provider="auto"
    )
    
    if result.success:
        print(f"Áudio gerado: {result.audio_path}")
        print(f"Duração: {result.duration:.2f}s")
        print(f"Provider: {result.provider_used}")
    else:
        print(f"Erro: {result.error}")

# Executar
asyncio.run(exemplo_basico())
```

### 3. **Configuração Avançada**
```python
from services.tts_service import TTSConfig, TTSProvider, tts_service

# Configurar TTS
config = TTSConfig(
    provider=TTSProvider.BARK,
    voice="pt_speaker_1",
    language="pt",
    output_format="mp3",
    sample_rate=22050
)

# Gerar áudio
result = await tts_service.generate_speech(
    "Texto para converter",
    config,
    "meu_audio.mp3"
)
```

### 4. **Narração de Curso Completo**
```python
from services.tts_service import generate_course_narration

course_sections = [
    {
        "title": "Introdução",
        "content": "Bem-vindos ao curso...",
        "notes": "Tom entusiasmado"
    },
    {
        "title": "Conceitos Básicos", 
        "content": "Vamos começar com..."
    }
]

results = await generate_course_narration(
    course_sections,
    voice="pt_speaker_0"
)

for i, result in enumerate(results):
    if result.success:
        print(f"Seção {i+1}: {result.audio_path}")
```

## 🔧 Integração com File Processor

O TTS é automaticamente integrado no processamento de arquivos:

### 1. **PDF → Curso com Narração**
```python
# O file_processor automaticamente usa TTS avançado
from services.file_processor import FileProcessor

processor = FileProcessor()
result = await processor.process_file("pdf_file_id")

print(f"TTS usado: {result['tts_provider']}")
```

### 2. **PPTX → Apresentação Narrada**
```python
# Slides são automaticamente narrados
result = await processor._process_presentation(file_upload, db)

print(f"Slides processados: {result['slides_count']}")
print(f"Narração: {result['tts_provider']}")
```

## 🛠️ Troubleshooting

### 1. **Erro: "No module named 'torch'"**
```bash
# Instalar PyTorch
pip install torch torchvision torchaudio
```

### 2. **Erro: "CUDA out of memory"**
```env
# Configurar para usar CPU
BARK_DEVICE=cpu

# Ou reduzir jobs concorrentes
TTS_MAX_CONCURRENT_JOBS=1
```

### 3. **Bark muito lento**
```env
# Ativar compilação (requer PyTorch 2.0+)
BARK_ENABLE_COMPILE=true

# Usar GPU se disponível
BARK_DEVICE=cuda
```

### 4. **Fallback para gTTS**
```bash
# Verificar logs para entender por que Bark falhou
tail -f logs/app.log | grep TTS
```

### 5. **Limpar cache**
```bash
# Via API
DELETE /api/tts/cleanup

# Ou manual
rm -rf ./cache/tts/*
```

## 📊 Performance

### 1. **Benchmarks Típicos**

| Modelo | Tempo (10s áudio) | Qualidade | GPU Memory |
|--------|-------------------|-----------|------------|
| Bark   | 15-30s           | Excelente | 2-4GB      |
| gTTS   | 1-3s             | Boa       | 0MB        |

### 2. **Otimizações**

#### **CPU**
```env
BARK_DEVICE=cpu
BARK_ENABLE_COMPILE=false
TTS_MAX_CONCURRENT_JOBS=2
```

#### **GPU (RTX 3080+)**
```env
BARK_DEVICE=cuda
BARK_ENABLE_COMPILE=true
TTS_MAX_CONCURRENT_JOBS=1
```

#### **Servidor de Produção**
```env
TTS_PROVIDER=bark
BARK_DEVICE=cuda
TTS_CACHE_DIR=/var/cache/tts
TTS_CLEANUP_INTERVAL_HOURS=12
```

## 🔍 Monitoramento

### 1. **Logs**
```bash
# Seguir logs TTS
tail -f logs/app.log | grep "TTS\|Bark\|gTTS"
```

### 2. **Métricas via API**
```bash
# Status detalhado
curl http://localhost:8000/api/tts/status

# Teste de providers
curl -X POST http://localhost:8000/api/tts/test
```

### 3. **Cache Usage**
```bash
# Verificar tamanho do cache
du -sh ./cache/tts/
du -sh ./cache/huggingface/
```

## 🔒 Segurança

### 1. **Limitações de Texto**
```env
# Máximo de caracteres por request
TTS_MAX_TEXT_LENGTH=1000

# Rate limiting
TTS_RATE_LIMIT_PER_MINUTE=10
```

### 2. **Validação de Entrada**
- Sanitização automática de texto
- Bloqueio de conteúdo suspeito
- Limitação de tamanho de arquivo

## 🆘 Suporte

### 1. **Teste Completo**
```bash
python test_tts_pipeline.py
```

### 2. **Verificar Configuração**
```bash
python -c "from app.config import validate_tts_config; print(validate_tts_config())"
```

### 3. **Status dos Modelos**
```bash
curl http://localhost:8000/api/tts/status | jq .system_status
```

---

## 🎯 Próximos Passos

- [ ] Suporte a mais idiomas
- [ ] Vozes customizadas
- [ ] WebSocket para progresso em tempo real
- [ ] Integração com Azure/AWS TTS
- [ ] Cache distribuído
- [ ] Métricas avançadas

---

## 📄 Licença

Este módulo TTS faz parte do TecnoCursos AI e segue a mesma licença do projeto principal.

Para dúvidas ou suporte, consulte a documentação principal ou abra uma issue no GitHub. 