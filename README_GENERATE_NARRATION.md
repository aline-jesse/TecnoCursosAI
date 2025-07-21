# 🎤 FUNÇÃO GENERATE_NARRATION - TTS (TEXT-TO-SPEECH)

Sistema completo de conversão de texto em áudio usando modelos TTS da Hugging Face e Google TTS.

## 📋 FUNCIONALIDADES

### ✨ Recursos Principais
- **Múltiplos Provedores**: Bark (Hugging Face), gTTS (Google), Auto-detecção
- **Suporte a Português**: Vozes nativas em português brasileiro
- **Formatos de Saída**: MP3, WAV
- **API REST**: Endpoint integrado para uso via HTTP
- **Função Síncrona/Assíncrona**: Suporte a ambos os paradigmas
- **Validação Robusta**: Verificação de entrada e tratamento de erros
- **Cache Inteligente**: Otimização para modelos pré-carregados

---

## 🚀 INSTALAÇÃO

### 1. Dependências Básicas
```bash
pip install torch transformers torchaudio gtts pydub
```

### 2. GPU Support (Recomendado para Bark)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Configuração Hugging Face (Opcional)
```bash
export HUGGINGFACE_TOKEN="your_token_here"
```

---

## 🎯 USO BÁSICO

### Função Síncrona
```python
from app.utils import generate_narration_sync

# Exemplo simples
result = generate_narration_sync(
    text="Olá! Este é um teste de narração em português.",
    output_path="narracao.mp3"
)

if result['success']:
    print(f"Áudio gerado: {result['audio_path']}")
    print(f"Duração: {result['duration']:.2f}s")
    print(f"Provedor: {result['provider_used']}")
else:
    print(f"Erro: {result['error']}")
```

### Função Assíncrona
```python
import asyncio
from app.utils import generate_narration

async def exemplo_async():
    result = await generate_narration(
        text="Bem-vindos ao curso de IA!",
        output_path="intro_curso.mp3",
        provider="bark",
        voice="v2/pt_speaker_2"
    )
    return result

# Executar
result = asyncio.run(exemplo_async())
```

---

## 🎭 PROVEDORES E VOZES

### gTTS (Google TTS)
- **Velocidade**: 1-3 segundos
- **Qualidade**: Boa para uso geral
- **Configuração**: Sem setup necessário
- **Limitações**: Requer internet

```python
result = generate_narration_sync(
    text="Texto para narração",
    output_path="gtts_audio.mp3",
    provider="gtts"
)
```

### Bark (Hugging Face)
- **Velocidade**: 10-120 segundos (dependendo do hardware)
- **Qualidade**: Excepcional, vozes naturais
- **Configuração**: Requer modelos (~2GB)
- **Offline**: Funciona sem internet após download

#### Vozes Disponíveis em Português:
- `v2/pt_speaker_0` - Masculina neutra
- `v2/pt_speaker_1` - Feminina jovem
- `v2/pt_speaker_2` - Feminina profissional
- `v2/pt_speaker_3` - Masculina grave
- `v2/pt_speaker_4` - Feminina madura
- `v2/pt_speaker_5` a `v2/pt_speaker_9` - Variações

```python
result = generate_narration_sync(
    text="Texto com voz natural",
    output_path="bark_audio.mp3",
    provider="bark",
    voice="v2/pt_speaker_2"
)
```

### Auto-Detecção
```python
result = generate_narration_sync(
    text="Sistema escolhe o melhor provedor",
    output_path="auto_audio.mp3",
    provider="auto"  # Detecta automaticamente
)
```

---

## 🌐 API REST

### Endpoint de Geração
**POST** `/api/tts/generate-narration`

#### Request Body:
```json
{
    "text": "Texto para converter em áudio",
    "provider": "auto",
    "voice": "v2/pt_speaker_1",
    "language": "pt",
    "output_format": "mp3"
}
```

#### Response:
```json
{
    "success": true,
    "message": "Narração gerada com sucesso",
    "audio_path": "temp/narration_a1b2c3d4.mp3",
    "duration": 8.5,
    "provider_used": "bark",
    "filename": "narration_a1b2c3d4.mp3",
    "download_url": "/api/tts/download/narration_a1b2c3d4.mp3",
    "metadata": {
        "voice_used": "v2/pt_speaker_1",
        "model_version": "bark-v2"
    }
}
```

### Download de Arquivo
**GET** `/api/tts/download/{filename}`

#### Exemplo usando cURL:
```bash
# Gerar narração
curl -X POST "http://localhost:8000/api/tts/generate-narration" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Olá! Este é um teste via API.",
    "provider": "gtts"
  }'

# Download do arquivo
curl -O "http://localhost:8000/api/tts/download/narration_a1b2c3d4.mp3"
```

---

## ⚙️ CONFIGURAÇÕES AVANÇADAS

### Parâmetros da Função
```python
generate_narration_sync(
    text: str,                    # Texto a narrar (máx 2000 chars)
    output_path: str,             # Caminho de saída
    voice: Optional[str] = None,  # Voz específica
    provider: str = "auto",       # Provedor ("bark", "gtts", "auto")
    language: str = "pt"          # Idioma
) -> Dict
```

### Resposta da Função
```python
{
    'success': bool,              # Status do processamento
    'audio_path': str,            # Caminho do arquivo gerado
    'duration': float,            # Duração em segundos
    'provider_used': str,         # Provedor utilizado
    'error': str,                 # Mensagem de erro (se houver)
    'metadata': Dict              # Informações adicionais
}
```

---

## 🔧 REQUISITOS DE SISTEMA

### Configuração Mínima (gTTS)
- **RAM**: 1GB
- **Internet**: Obrigatória
- **Armazenamento**: 100MB

### Configuração Recomendada (Bark)
- **RAM**: 8GB+
- **VRAM**: 4GB+ (GPU)
- **CPU**: 4+ cores
- **Armazenamento**: 5GB (modelos + cache)

---

## 📊 PERFORMANCE

### Benchmark de Velocidade
| Provedor | Hardware | Tempo (100 caracteres) | Qualidade |
|----------|----------|------------------------|-----------|
| gTTS     | CPU      | 1-3s                   | ⭐⭐⭐     |
| Bark     | CPU      | 30-60s                 | ⭐⭐⭐⭐⭐   |
| Bark     | GPU      | 5-15s                  | ⭐⭐⭐⭐⭐   |

### Otimizações
1. **Cache de Modelos**: Modelos Bark são mantidos em memória
2. **Processamento em Lote**: Multiple textos em uma chamada
3. **GPU Acceleration**: Uso automático de CUDA quando disponível
4. **Compressão**: Arquivos MP3 otimizados

---

## 🚨 TRATAMENTO DE ERROS

### Erros Comuns
```python
# Texto vazio
result = generate_narration_sync("", "output.mp3")
# result['error'] = "Texto não pode estar vazio"

# Texto muito longo
texto_longo = "x" * 5000
result = generate_narration_sync(texto_longo, "output.mp3")
# result['error'] = "Texto muito longo (5000 caracteres). Máximo: 2000."

# Dependências não instaladas
# result['error'] = "Serviço TTS não disponível. Instale as dependências."
```

### Validação de Entrada
```python
def validar_entrada(text: str) -> bool:
    if not text or not text.strip():
        return False
    if len(text) > 2000:
        return False
    return True
```

---

## 🧪 TESTES

### Executar Testes
```bash
# Teste completo
python test_generate_narration.py

# Teste específico via utils.py
python -c "from app.utils import *"
```

### Exemplo de Teste Unitário
```python
import unittest
from app.utils import generate_narration_sync

class TestGenerateNarration(unittest.TestCase):
    
    def test_gtts_basic(self):
        result = generate_narration_sync(
            "Teste", "test.mp3", provider="gtts"
        )
        self.assertTrue(result['success'])
        self.assertIn('.mp3', result['audio_path'])
    
    def test_invalid_text(self):
        result = generate_narration_sync("", "test.mp3")
        self.assertFalse(result['success'])
        self.assertIn("vazio", result['error'])
```

---

## 🔐 SEGURANÇA

### Validações de Entrada
- Limitação de tamanho de texto (2000 caracteres)
- Sanitização de caminhos de arquivo
- Validação de formatos de saída
- Rate limiting via API

### Limpeza de Arquivos
- Arquivos temporários são removidos automaticamente
- Cache de modelos gerenciado inteligentemente
- Logs de auditoria para todas as operações

---

## 📚 EXEMPLOS AVANÇADOS

### Processamento em Lote
```python
textos = [
    "Primeira narração",
    "Segunda narração", 
    "Terceira narração"
]

resultados = []
for i, texto in enumerate(textos):
    result = generate_narration_sync(
        text=texto,
        output_path=f"narração_{i+1}.mp3",
        provider="auto"
    )
    resultados.append(result)
```

### Integração com Frontend
```javascript
// JavaScript para chamada da API
async function gerarNarracao(texto) {
    const response = await fetch('/api/tts/generate-narration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: texto,
            provider: 'auto'
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        // Download automático
        window.open(result.download_url);
    } else {
        console.error('Erro:', result.detail);
    }
}
```

---

## 🆘 TROUBLESHOOTING

### Problema: Bark não funciona
**Solução**:
```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Reinstalar PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Problema: gTTS falha
**Solução**:
```bash
# Verificar conexão
ping google.com

# Atualizar gTTS
pip install --upgrade gtts
```

### Problema: Memória insuficiente
**Solução**:
- Use gTTS para textos longos
- Divida textos em chunks menores
- Configure swap no sistema

---

## 📞 SUPORTE

### Logs de Debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)

result = generate_narration_sync("teste", "debug.mp3")
```

### Informações do Sistema
```python
from app.utils import generate_narration_sync
import torch

print(f"TTS Disponível: {TTS_AVAILABLE}")
print(f"CUDA Disponível: {torch.cuda.is_available()}")
print(f"Dispositivos GPU: {torch.cuda.device_count()}")
```

---

## 🎉 CONCLUSÃO

A função `generate_narration` oferece uma solução completa e robusta para conversão texto-para-áudio, integrando os melhores modelos TTS disponíveis com uma API simples e eficiente.

### Próximos Passos
1. Configurar dependências
2. Testar com textos simples
3. Experimentar diferentes vozes
4. Integrar com sua aplicação
5. Otimizar para produção

**Documentação atualizada em**: Dezembro 2024
**Versão**: 1.0.0 