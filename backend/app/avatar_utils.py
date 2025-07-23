"""
Utilitários auxiliares para geração de avatares com API Hunyuan3D-2.

Este módulo contém funções especializadas para suporte à geração de avatares 3D
usando a API do Hugging Face Space Hunyuan3D-2 da Tencent.

🔗 API Externa: https://huggingface.co/spaces/tencent/Hunyuan3D-2
"""

import os
import time
import json

# Verificar disponibilidade de bibliotecas opcionais
try:
    from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip, ColorClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️ MoviePy não disponível - instale: pip install moviepy")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL não disponível - instale: pip install pillow")


def detect_language(text: str) -> str:
    """
    Detecta o idioma do texto baseado em palavras-chave comuns.
    
    Args:
        text (str): Texto para analisar
    
    Returns:
        str: Código do idioma detectado ('pt', 'en', 'es', 'fr', etc.)
    """
    # Converter para lowercase para análise
    text_lower = text.lower()
    words = text_lower.split()
    
    # Palavras indicativas por idioma
    language_indicators = {
        'pt': ['que', 'para', 'com', 'uma', 'são', 'não', 'dos', 'mas', 'seu', 'tem', 'como', 'mais', 'este', 'pela'],
        'en': ['the', 'and', 'for', 'are', 'with', 'that', 'this', 'have', 'from', 'they', 'will', 'your', 'all'],
        'es': ['que', 'para', 'con', 'una', 'son', 'del', 'pero', 'sus', 'tiene', 'como', 'más', 'este', 'por'],
        'fr': ['que', 'pour', 'avec', 'une', 'sont', 'des', 'mais', 'ses', 'dans', 'comme', 'plus', 'cette', 'par'],
        'de': ['das', 'und', 'für', 'sind', 'mit', 'dass', 'dies', 'haben', 'von', 'sie', 'wird', 'ihre', 'alle'],
        'it': ['che', 'per', 'con', 'una', 'sono', 'dei', 'ma', 'suo', 'come', 'più', 'questo', 'dalla', 'tutti']
    }
    
    # Calcular scores para cada idioma
    scores = {}
    for lang, indicators in language_indicators.items():
        score = sum(1 for word in words if word in indicators)
        scores[lang] = score
    
    # Retornar idioma com maior score, padrão inglês
    if not scores or max(scores.values()) == 0:
        return 'en'
    
    detected_lang = max(scores, key=scores.get)
    confidence = scores[detected_lang] / len(words) if words else 0
    
    print(f"🗣️ Idioma detectado: {detected_lang} (confiança: {confidence:.2f})")
    return detected_lang


def simulate_avatar_generation(text: str, audio_path: str, output_path: str, start_time: float) -> dict:
    """
    Simula a geração de avatar quando a API não está disponível.
    Cria um vídeo simples com slide e áudio para demonstração.
    
    Args:
        text (str): Texto para exibir
        audio_path (str): Caminho do áudio
        output_path (str): Caminho de saída
        start_time (float): Timestamp de início
    
    Returns:
        dict: Resultado da simulação
    """
    try:
        print("🎭 Gerando vídeo simulado com slide + áudio...")
        
        # Verificar se MoviePy está disponível
        if not MOVIEPY_AVAILABLE:
            print("⚠️ MoviePy não disponível para simulação")
            return {
                'success': False,
                'error': 'MoviePy não instalado. Execute: pip install moviepy'
            }
        
        # Carregar áudio para obter duração
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # Criar background simples
        if PIL_AVAILABLE:
            # Criar imagem de fundo com texto
            img = Image.new('RGB', (1920, 1080), color=(45, 55, 72))  # Azul escuro
            draw = ImageDraw.Draw(img)
            
            # Adicionar gradiente simples
            for y in range(1080):
                alpha = y / 1080
                color = (
                    int(45 + alpha * 20),   # R
                    int(55 + alpha * 30),   # G  
                    int(72 + alpha * 40)    # B
                )
                draw.line([(0, y), (1920, y)], fill=color)
            
            # Adicionar texto centralizado
            try:
                # Tentar usar fonte do sistema
                font = ImageFont.truetype("arial.ttf", 72)
            except:
                font = ImageFont.load_default()
            
            # Quebrar texto em linhas
            words = text.split()
            lines = []
            current_line = []
            max_width = 1600  # Deixar margem
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Desenhar texto centralizado
            y_start = (1080 - len(lines) * 100) // 2
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1920 - text_width) // 2
                y = y_start + i * 100
                
                # Sombra
                draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0))
                # Texto principal
                draw.text((x, y), line, font=font, fill=(255, 255, 255))
            
            # Salvar imagem temporária
            temp_image = "temp_avatar_bg.png"
            img.save(temp_image)
            
            # Criar vídeo clip
            image_clip = ImageClip(temp_image).set_duration(duration)
            
        else:
            # Fallback sem PIL
            print("⚠️ PIL não disponível, usando clip simples")
            # Criar clip de cor sólida
            image_clip = ColorClip(size=(1920, 1080), color=(45, 55, 72)).set_duration(duration)
        
        # Combinar vídeo e áudio
        final_video = CompositeVideoClip([image_clip])
        final_video = final_video.set_audio(audio)
        
        # Salvar vídeo final
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Limpar recursos
        audio.close()
        final_video.close()
        
        # Limpar arquivo temporário
        if PIL_AVAILABLE and os.path.exists("temp_avatar_bg.png"):
            os.remove("temp_avatar_bg.png")
        
        # Coletar métricas
        file_size = os.path.getsize(output_path)
        processing_time = time.time() - start_time
        
        print(f"✅ Vídeo simulado criado: {output_path}")
        print(f"   ⏱️ Duração: {duration:.1f}s")
        print(f"   💾 Tamanho: {file_size/1024/1024:.1f}MB")
        
        return {
            'success': True,
            'video_path': output_path,
            'duration': duration,
            'file_size': file_size,
            'resolution': (1920, 1080),
            'api_used': 'simulation',
            'processing_time': processing_time,
            'queue_time': 0.0,
            'generation_time': processing_time,
            'download_time': 0.0,
            'quality_score': 0.7,  # Score moderado para simulação
            'metadata': {
                'simulated': True,
                'text_length': len(text),
                'method': 'slide_with_audio'
            },
            'error': None
        }
        
    except Exception as e:
        error_msg = f"Erro na simulação: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            'success': False,
            'video_path': None,
            'duration': 0.0,
            'file_size': 0,
            'resolution': (0, 0),
            'api_used': 'simulation',
            'processing_time': time.time() - start_time,
            'queue_time': 0.0,
            'generation_time': 0.0,
            'download_time': 0.0,
            'quality_score': 0.0,
            'metadata': {'error_details': str(e)},
            'error': error_msg
        }


def get_video_duration(video_path: str) -> float:
    """
    Obtém a duração de um vídeo em segundos.
    
    Args:
        video_path (str): Caminho do arquivo de vídeo
    
    Returns:
        float: Duração em segundos
    """
    try:
        if MOVIEPY_AVAILABLE:
            with VideoFileClip(video_path) as clip:
                return clip.duration
        else:
            # Fallback: tentar obter do tamanho do arquivo (estimativa grosseira)
            file_size = os.path.getsize(video_path)
            # Estimar ~1MB por segundo para vídeos HD
            estimated_duration = file_size / (1024 * 1024)
            return max(1.0, estimated_duration)  # Mínimo 1 segundo
            
    except Exception as e:
        print(f"⚠️ Erro ao obter duração do vídeo: {e}")
        return 0.0


def get_video_resolution(video_path: str) -> tuple:
    """
    Obtém a resolução de um vídeo.
    
    Args:
        video_path (str): Caminho do arquivo de vídeo
    
    Returns:
        tuple: (largura, altura)
    """
    try:
        if MOVIEPY_AVAILABLE:
            with VideoFileClip(video_path) as clip:
                return (clip.w, clip.h)
        else:
            # Fallback: retornar resolução padrão HD
            return (1920, 1080)
            
    except Exception as e:
        print(f"⚠️ Erro ao obter resolução do vídeo: {e}")
        return (1920, 1080)  # Padrão HD


def calculate_quality_score(file_size: int, duration: float, resolution: tuple, generation_time: float) -> float:
    """
    Calcula um score de qualidade baseado nas métricas do vídeo.
    
    Args:
        file_size (int): Tamanho do arquivo em bytes
        duration (float): Duração em segundos
        resolution (tuple): (largura, altura)
        generation_time (float): Tempo de processamento
    
    Returns:
        float: Score de qualidade entre 0.0 e 1.0
    """
    try:
        score = 0.0
        
        # Fator de resolução (peso: 30%)
        width, height = resolution
        pixels = width * height
        
        if pixels >= 1920 * 1080:  # Full HD ou superior
            resolution_score = 1.0
        elif pixels >= 1280 * 720:  # HD
            resolution_score = 0.8
        elif pixels >= 854 * 480:   # SD
            resolution_score = 0.6
        else:
            resolution_score = 0.4
        
        score += resolution_score * 0.3
        
        # Fator de bitrate estimado (peso: 25%)
        if duration > 0:
            bitrate_mbps = (file_size * 8) / (duration * 1024 * 1024)  # Mbps
            
            if bitrate_mbps >= 5.0:      # Alta qualidade
                bitrate_score = 1.0
            elif bitrate_mbps >= 2.0:    # Boa qualidade
                bitrate_score = 0.8
            elif bitrate_mbps >= 1.0:    # Qualidade média
                bitrate_score = 0.6
            else:                        # Baixa qualidade
                bitrate_score = 0.4
        else:
            bitrate_score = 0.5
        
        score += bitrate_score * 0.25
        
        # Fator de eficiência do processamento (peso: 20%)
        if generation_time > 0:
            efficiency = duration / generation_time  # Razão duração/tempo_processamento
            
            if efficiency >= 0.1:       # Processamento rápido
                efficiency_score = 1.0
            elif efficiency >= 0.05:    # Processamento médio
                efficiency_score = 0.8
            elif efficiency >= 0.02:    # Processamento lento
                efficiency_score = 0.6
            else:                       # Muito lento
                efficiency_score = 0.4
        else:
            efficiency_score = 0.5
        
        score += efficiency_score * 0.2
        
        # Fator de tamanho do arquivo (peso: 15%)
        size_mb = file_size / (1024 * 1024)
        
        if duration > 0:
            size_per_second = size_mb / duration
            
            if 0.5 <= size_per_second <= 2.0:  # Tamanho otimizado
                size_score = 1.0
            elif 0.3 <= size_per_second < 0.5 or 2.0 < size_per_second <= 3.0:
                size_score = 0.8
            else:
                size_score = 0.6
        else:
            size_score = 0.5
        
        score += size_score * 0.15
        
        # Fator base de existência do arquivo (peso: 10%)
        if file_size > 0:
            existence_score = 1.0
        else:
            existence_score = 0.0
        
        score += existence_score * 0.1
        
        # Garantir que o score esteja entre 0.0 e 1.0
        score = max(0.0, min(1.0, score))
        
        return round(score, 3)
        
    except Exception as e:
        print(f"⚠️ Erro ao calcular score de qualidade: {e}")
        return 0.5  # Score neutro em caso de erro 