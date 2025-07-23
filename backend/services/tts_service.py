"""
Serviço de Text-to-Speech (TTS) - TecnoCursos AI
Suporte a múltiplos modelos: Bark (Hugging Face), gTTS (Google)
Pipeline robusto para geração de narração de alta qualidade
"""

import os
import asyncio
import tempfile
import torch
from pathlib import Path
from typing import Dict, List, Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum
import numpy as np
import scipy.io.wavfile as wavfile
from pydub import AudioSegment
import logging
from backend.app.logger import logger
from backend.app.config import settings

# Imports condicionais para evitar erros se não instalados
try:
    from transformers import AutoProcessor, BarkModel
    from gtts import gTTS
    import torchaudio
    BARK_AVAILABLE = True
except ImportError as e:
    BARK_AVAILABLE = False
    print(f"⚠️ Algumas dependências TTS não disponíveis: {e}")

logger = logging.getLogger(__name__)

class TTSProvider(Enum):
    """Provedores de TTS disponíveis"""
    BARK = "bark"
    GTTS = "gtts"
    AUTO = "auto"

@dataclass
class TTSConfig:
    """Configurações para TTS"""
    provider: TTSProvider = TTSProvider.AUTO
    language: str = "pt"
    voice: Optional[str] = None
    speed: float = 1.0
    pitch: float = 1.0
    output_format: str = "mp3"
    sample_rate: int = 22050
    max_length: int = 1000  # Máximo de caracteres por segmento

@dataclass
class AudioResult:
    """Resultado da geração de áudio"""
    success: bool
    audio_path: Optional[str] = None
    duration: float = 0.0
    provider_used: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class BarkTTSEngine:
    """Engine TTS usando Bark (Hugging Face)"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "suno/bark"
        self.loaded = False
        
        # Vozes disponíveis para português
        self.portuguese_voices = [
            "v2/pt_speaker_0",
            "v2/pt_speaker_1", 
            "v2/pt_speaker_2",
            "v2/pt_speaker_3",
            "v2/pt_speaker_4",
            "v2/pt_speaker_5",
            "v2/pt_speaker_6",
            "v2/pt_speaker_7",
            "v2/pt_speaker_8",
            "v2/pt_speaker_9"
        ]
    
    async def load_model(self) -> bool:
        """Carrega o modelo Bark"""
        if self.loaded:
            return True
            
        try:
            logger.info("Carregando modelo Bark TTS...")
            
            # Carregar processor e model
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = BarkModel.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Mover para device
            self.model = self.model.to(self.device)
            
            # Otimizações para performance
            if self.device == "cuda":
                self.model = torch.compile(self.model)
            
            self.loaded = True
            logger.info(f"✅ Modelo Bark carregado em {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo Bark: {e}")
            return False
    
    def _split_text(self, text: str, max_length: int = 200) -> List[str]:
        """Divide texto em segmentos menores para o Bark"""
        if len(text) <= max_length:
            return [text]
        
        # Dividir por sentenças primeiro
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_segment + sentence) <= max_length:
                current_segment += sentence + ". "
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence + ". "
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    async def generate_audio(self, text: str, config: TTSConfig, output_path: str) -> AudioResult:
        """Gera áudio usando Bark"""
        if not self.loaded:
            success = await self.load_model()
            if not success:
                return AudioResult(
                    success=False,
                    error="Falha ao carregar modelo Bark"
                )
        
        try:
            # Escolher voz
            voice_preset = config.voice or self.portuguese_voices[0]
            if voice_preset not in self.portuguese_voices:
                voice_preset = self.portuguese_voices[0]
            
            # Dividir texto em segmentos
            text_segments = self._split_text(text, config.max_length)
            audio_segments = []
            
            logger.info(f"Gerando {len(text_segments)} segmentos de áudio com Bark...")
            
            for i, segment in enumerate(text_segments):
                logger.info(f"Processando segmento {i+1}/{len(text_segments)}")
                
                # Preparar texto para o modelo
                inputs = self.processor(segment, voice_preset=voice_preset)
                
                # Gerar áudio
                with torch.no_grad():
                    audio_array = self.model.generate(**inputs.to(self.device))
                
                # Converter para numpy
                audio_np = audio_array.cpu().numpy().squeeze()
                
                # Normalizar áudio
                audio_np = audio_np / np.max(np.abs(audio_np))
                audio_segments.append(audio_np)
            
            # Concatenar segmentos
            final_audio = np.concatenate(audio_segments)
            
            # Salvar como WAV temporário
            temp_wav = output_path.replace('.mp3', '.wav')
            wavfile.write(temp_wav, config.sample_rate, (final_audio * 32767).astype(np.int16))
            
            # Converter para MP3 se necessário
            if config.output_format == "mp3":
                audio_segment = AudioSegment.from_wav(temp_wav)
                audio_segment.export(output_path, format="mp3", bitrate="128k")
                os.remove(temp_wav)  # Remover WAV temporário
            else:
                os.rename(temp_wav, output_path)
            
            # Calcular duração
            duration = len(final_audio) / config.sample_rate
            
            logger.info(f"✅ Áudio gerado com Bark: {duration:.2f}s")
            
            return AudioResult(
                success=True,
                audio_path=output_path,
                duration=duration,
                provider_used="bark",
                metadata={
                    "voice": voice_preset,
                    "segments": len(text_segments),
                    "sample_rate": config.sample_rate,
                    "device": self.device
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na geração Bark: {e}")
            return AudioResult(
                success=False,
                error=str(e),
                provider_used="bark"
            )

class GTTSEngine:
    """Engine TTS usando Google TTS (fallback)"""
    
    def __init__(self):
        self.supported_languages = ['pt', 'en', 'es', 'fr', 'de', 'it']
    
    async def generate_audio(self, text: str, config: TTSConfig, output_path: str) -> AudioResult:
        """Gera áudio usando gTTS"""
        try:
            logger.info("Gerando áudio com gTTS...")
            
            # Verificar idioma
            lang = config.language if config.language in self.supported_languages else 'pt'
            
            # Criar TTS
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Salvar arquivo
            tts.save(output_path)
            
            # Calcular duração aproximada
            duration = len(text) / 150.0  # ~150 caracteres por segundo
            
            logger.info(f"✅ Áudio gerado com gTTS: {duration:.2f}s")
            
            return AudioResult(
                success=True,
                audio_path=output_path,
                duration=duration,
                provider_used="gtts",
                metadata={
                    "language": lang,
                    "text_length": len(text)
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na geração gTTS: {e}")
            return AudioResult(
                success=False,
                error=str(e),
                provider_used="gtts"
            )

class TTSService:
    """Serviço principal de TTS com múltiplos providers"""
    
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "tecnocursos_tts"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Inicializar engines
        self.bark_engine = BarkTTSEngine() if BARK_AVAILABLE else None
        self.gtts_engine = GTTSEngine()
        
        # Cache de configurações
        self._model_loaded = False
    
    def get_available_providers(self) -> List[str]:
        """Retorna providers disponíveis"""
        providers = ["gtts"]
        if BARK_AVAILABLE and self.bark_engine:
            providers.insert(0, "bark")  # Bark como primeira opção
        return providers
    
    def get_recommended_provider(self, text_length: int) -> TTSProvider:
        """Recomenda provider baseado no tamanho do texto"""
        if not BARK_AVAILABLE:
            return TTSProvider.GTTS
        
        # Para textos curtos (< 500 chars), usar Bark
        # Para textos longos, usar gTTS (mais rápido)
        if text_length < 500:
            return TTSProvider.BARK
        else:
            return TTSProvider.GTTS
    
    async def generate_speech(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
        output_filename: Optional[str] = None
    ) -> AudioResult:
        """Gera áudio a partir de texto"""
        
        # Configuração padrão
        if config is None:
            config = TTSConfig()
        
        # Auto-selecionar provider se necessário
        if config.provider == TTSProvider.AUTO:
            config.provider = self.get_recommended_provider(len(text))
        
        # Gerar nome do arquivo se não fornecido
        if output_filename is None:
            output_filename = f"tts_{hash(text) % 1000000}.{config.output_format}"
        
        output_path = str(self.temp_dir / output_filename)
        
        # Validar texto
        if not text or len(text.strip()) == 0:
            return AudioResult(
                success=False,
                error="Texto vazio fornecido"
            )
        
        # Limitar tamanho do texto
        if len(text) > 5000:  # Limite de 5000 caracteres
            text = text[:5000] + "..."
            logger.warning("Texto truncado para 5000 caracteres")
        
        logger.info(f"Gerando TTS: {len(text)} chars, provider: {config.provider.value}")
        
        try:
            # Tentar com provider preferido
            if config.provider == TTSProvider.BARK and self.bark_engine:
                result = await self.bark_engine.generate_audio(text, config, output_path)
                if result.success:
                    return result
                else:
                    logger.warning(f"Bark falhou: {result.error}, tentando gTTS...")
                    config.provider = TTSProvider.GTTS
            
            # Fallback para gTTS
            if config.provider == TTSProvider.GTTS:
                return await self.gtts_engine.generate_audio(text, config, output_path)
            
            return AudioResult(
                success=False,
                error="Nenhum provider TTS disponível"
            )
            
        except Exception as e:
            logger.error(f"Erro geral no TTS: {e}")
            return AudioResult(
                success=False,
                error=str(e)
            )
    
    async def generate_batch_speech(
        self,
        texts: List[str],
        config: Optional[TTSConfig] = None
    ) -> List[AudioResult]:
        """Gera múltiplos áudios em lote"""
        results = []
        
        for i, text in enumerate(texts):
            filename = f"batch_{i}_{hash(text) % 100000}.mp3"
            result = await self.generate_speech(text, config, filename)
            results.append(result)
        
        return results
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """Limpa arquivos temporários antigos"""
        try:
            current_time = asyncio.get_event_loop().time()
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Arquivo temporário removido: {file_path.name}")
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {e}")

# Instância global do serviço TTS
tts_service = TTSService()

# Funções de conveniência
async def generate_narration(
    text: str,
    voice: str = "pt_speaker_0",
    provider: str = "auto",
    output_path: Optional[str] = None
) -> AudioResult:
    """Função de conveniência para gerar narração"""
    config = TTSConfig(
        provider=TTSProvider(provider),
        voice=voice,
        language="pt"
    )
    
    return await tts_service.generate_speech(text, config, output_path)

async def generate_course_narration(
    course_sections: List[Dict],
    voice: str = "pt_speaker_0"
) -> List[AudioResult]:
    """Gera narração para seções de curso"""
    config = TTSConfig(
        provider=TTSProvider.AUTO,
        voice=voice,
        language="pt"
    )
    
    texts = []
    for section in course_sections:
        # Combinar título e conteúdo
        narration_text = ""
        if section.get("title"):
            narration_text += f"{section['title']}. "
        if section.get("content"):
            narration_text += section["content"]
        
        texts.append(narration_text)
    
    return await tts_service.generate_batch_speech(texts, config)

async def test_tts_providers() -> Dict[str, bool]:
    """Testa todos os providers TTS disponíveis"""
    test_text = "Este é um teste do sistema de síntese de voz."
    results = {}
    
    for provider in ["bark", "gtts"]:
        try:
            config = TTSConfig(provider=TTSProvider(provider))
            result = await tts_service.generate_speech(test_text, config)
            results[provider] = result.success
            
            if result.success and result.audio_path:
                # Limpar arquivo de teste
                Path(result.audio_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Erro testando {provider}: {e}")
            results[provider] = False
    
    return results

if __name__ == "__main__":
    # Teste básico
    async def main():
        print("🎵 Testando TTS Service...")
        
        # Testar providers
        providers = await test_tts_providers()
        print(f"Providers disponíveis: {providers}")
        
        # Teste de geração
        result = await generate_narration(
            "Olá! Este é um teste do sistema de narração TecnoCursos AI.",
            provider="auto"
        )
        
        if result.success:
            print(f"✅ TTS gerado: {result.audio_path}")
            print(f"   Provider: {result.provider_used}")
            print(f"   Duração: {result.duration:.2f}s")
        else:
            print(f"❌ Erro: {result.error}")
    
    asyncio.run(main()) 