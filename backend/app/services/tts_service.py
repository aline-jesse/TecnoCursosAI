import os
from typing import Optional
import soundfile as sf

def get_default_tts_model() -> str:
    """Obtém o modelo TTS padrão da variável de ambiente ou retorna 'coqui'."""
    return os.getenv("TTS_MODEL", "coqui")

# Função plugável para TTS (Bark/Coqui)
def generate_tts_narration(text: str, output_path: str, model: Optional[str] = None, voice: Optional[str] = None) -> str:
    """
    Gera narração TTS para o texto fornecido usando modelo Hugging Face (Bark ou Coqui).
    Salva o áudio em output_path e retorna o caminho.
    Parâmetros:
        text: Texto a ser narrado.
        output_path: Caminho do arquivo de saída.
        model: Modelo TTS ('bark' ou 'coqui'). Se None, usa padrão.
        voice: Voz a ser utilizada (opcional).
    """
    model = model or get_default_tts_model()
    if model == "bark":
        try:
            from bark import generate_audio
            audio_array = generate_audio(text, voice_preset=voice or "v2/pt_speaker_0")
            sf.write(output_path, audio_array, 24000)
            return output_path
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar TTS com Bark: {e}")
    elif model == "coqui":
        try:
            from TTS.api import TTS
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)
            tts.tts_to_file(text=text, file_path=output_path)
            return output_path
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar TTS com Coqui: {e}")
    else:
        raise ValueError(f"Modelo TTS não suportado: {model}")
