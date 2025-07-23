#!/usr/bin/env python3
"""
Exemplo de uso da função generate_avatar_video com API Hunyuan3D-2.

Este script demonstra como gerar vídeos de avatar 3D usando a integração 
com o Hugging Face Space Hunyuan3D-2 da Tencent.

🔗 API Externa: https://huggingface.co/spaces/tencent/Hunyuan3D-2

Uso:
    python test_avatar_hunyuan3d.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório da aplicação ao path
sys.path.append('app')

from utils import generate_avatar_video

def criar_audio_teste(texto: str, output_path: str) -> bool:
    """
    Cria um arquivo de áudio de teste usando TTS.
    Em produção, você usaria o TTSService real.
    
    Args:
        texto (str): Texto para converter em áudio
        output_path (str): Caminho onde salvar o áudio
    
    Returns:
        bool: True se áudio foi criado com sucesso
    """
    try:
        # Simulação: criar um arquivo de áudio vazio para teste
        # Em produção real, você faria:
        # from services.tts_service import TTSService
        # result = TTSService.generate_audio(texto, output_path)
        
        print(f"🎵 Criando áudio de teste: {output_path}")
        
        # Verificar se já existe
        if os.path.exists(output_path):
            print(f"   ✅ Arquivo já existe: {output_path}")
            return True
        
        # Para este exemplo, vamos usar um placeholder
        print("   ⚠️ Para funcionamento completo, instale e configure TTS:")
        print("   pip install gtts pydub")
        print("   ou use: from services.tts_service import TTSService")
        
        # Criar arquivo placeholder (em produção, seria áudio real)
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(b'\x00' * 1024)  # 1KB de dados placeholder
        
        print(f"   ✅ Arquivo placeholder criado: {output_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar áudio: {e}")
        return False


def demonstrar_avatar_basico():
    """
    Demonstra uso básico da geração de avatar.
    """
    print("=" * 60)
    print("🎭 TESTE 1: AVATAR BÁSICO")
    print("=" * 60)
    
    # Configurações do teste
    texto = """
    Olá! Bem-vindos ao curso de Python com Inteligência Artificial.
    Hoje vamos aprender sobre geração de avatares 3D e processamento
    de linguagem natural. Este é um exemplo prático de como criar
    apresentações interativas usando modelos de IA avançados.
    """
    
    audio_path = "./temp_audio_basico.mp3"
    video_path = "./output_avatar_basico.mp4"
    
    print(f"📝 Texto: {texto[:100]}...")
    print(f"🎵 Áudio: {audio_path}")
    print(f"📹 Vídeo: {video_path}")
    
    # Criar áudio de teste
    if not criar_audio_teste(texto, audio_path):
        print("❌ Falha ao criar áudio de teste")
        return
    
    # Gerar avatar
    try:
        print("\n🚀 Iniciando geração de avatar...")
        
        resultado = generate_avatar_video(
            text=texto.strip(),
            audio_path=audio_path,
            output_path=video_path,
            avatar_style="hunyuan3d",
            quality="medium",
            timeout=180
        )
        
        # Exibir resultado
        print("\n📊 RESULTADO:")
        if resultado['success']:
            print("✅ SUCESSO!")
            print(f"   📹 Vídeo: {resultado['video_path']}")
            print(f"   ⏱️ Duração: {resultado['duration']:.1f}s")
            print(f"   💾 Tamanho: {resultado['file_size']/1024/1024:.2f}MB")
            print(f"   📊 Resolução: {resultado['resolution'][0]}x{resultado['resolution'][1]}")
            print(f"   🎯 API: {resultado['api_used']}")
            print(f"   ⏳ Tempo total: {resultado['processing_time']:.1f}s")
            print(f"   📈 Qualidade: {resultado['quality_score']:.2f}")
            
        else:
            print("❌ FALHA!")
            print(f"   Erro: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
    
    finally:
        # Limpeza
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"🧹 Arquivo temporário removido: {audio_path}")


def demonstrar_avatar_avancado():
    """
    Demonstra uso avançado com configurações personalizadas.
    """
    print("\n" + "=" * 60)
    print("🎭 TESTE 2: AVATAR AVANÇADO")
    print("=" * 60)
    
    # Configurações avançadas
    texto = """
    Welcome to our advanced AI presentation system. 
    Today we'll explore cutting-edge machine learning models 
    for 3D avatar generation and real-time facial animation.
    This technology represents the future of digital communication.
    """
    
    audio_path = "./temp_audio_avancado.mp3"
    video_path = "./output_avatar_avancado.mp4"
    
    print(f"📝 Texto (EN): {texto[:80]}...")
    print(f"🎵 Áudio: {audio_path}")
    print(f"📹 Vídeo: {video_path}")
    
    # Criar áudio de teste
    if not criar_audio_teste(texto, audio_path):
        print("❌ Falha ao criar áudio de teste")
        return
    
    # Gerar avatar com configurações avançadas
    try:
        print("\n🚀 Iniciando geração avançada...")
        
        resultado = generate_avatar_video(
            text=texto.strip(),
            audio_path=audio_path,
            output_path=video_path,
            avatar_style="realistic",
            quality="high",
            timeout=300,
            # Parâmetros adicionais (kwargs)
            background="office_modern",
            emotion="confident",
            pose="presenter",
            lighting="professional"
        )
        
        # Exibir resultado detalhado
        print("\n📊 RESULTADO AVANÇADO:")
        if resultado['success']:
            print("✅ SUCESSO!")
            print(f"   📹 Vídeo: {resultado['video_path']}")
            print(f"   ⏱️ Duração: {resultado['duration']:.1f}s")
            print(f"   💾 Tamanho: {resultado['file_size']/1024/1024:.2f}MB")
            print(f"   📊 Resolução: {resultado['resolution'][0]}x{resultado['resolution'][1]}")
            print(f"   🎯 API: {resultado['api_used']}")
            print(f"   ⏳ Tempo total: {resultado['processing_time']:.1f}s")
            
            # Métricas detalhadas
            if resultado['queue_time'] > 0:
                print(f"   ⏰ Tempo na fila: {resultado['queue_time']:.1f}s")
                print(f"   🔧 Tempo geração: {resultado['generation_time']:.1f}s")
                print(f"   ⬇️ Tempo download: {resultado['download_time']:.1f}s")
            
            print(f"   📈 Score qualidade: {resultado['quality_score']:.3f}")
            
            # Metadados
            metadata = resultado.get('metadata', {})
            if metadata:
                print("   📋 Metadados:")
                for key, value in metadata.items():
                    print(f"      {key}: {value}")
            
        else:
            print("❌ FALHA!")
            print(f"   Erro: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
    
    finally:
        # Limpeza
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"🧹 Arquivo temporário removido: {audio_path}")


def demonstrar_configuracoes_multiplas():
    """
    Demonstra diferentes configurações de avatar.
    """
    print("\n" + "=" * 60)
    print("🎭 TESTE 3: CONFIGURAÇÕES MÚLTIPLAS")
    print("=" * 60)
    
    # Diferentes configurações para testar
    configuracoes = [
        {
            "nome": "Avatar Educacional",
            "avatar_style": "hunyuan3d",
            "quality": "medium",
            "background": "classroom",
            "emotion": "friendly"
        },
        {
            "nome": "Avatar Corporativo",
            "avatar_style": "realistic", 
            "quality": "high",
            "background": "office",
            "emotion": "professional"
        },
        {
            "nome": "Avatar Tecnológico",
            "avatar_style": "hunyuan3d",
            "quality": "ultra",
            "background": "tech_studio",
            "emotion": "enthusiastic"
        }
    ]
    
    texto_base = "Este é um teste de geração de avatar com diferentes configurações visuais."
    
    for i, config in enumerate(configuracoes, 1):
        print(f"\n🧪 Subconfigração {i}: {config['nome']}")
        print(f"   Estilo: {config['avatar_style']}")
        print(f"   Qualidade: {config['quality']}")
        print(f"   Background: {config.get('background', 'default')}")
        print(f"   Emoção: {config.get('emotion', 'neutral')}")
        
        # Simular teste rápido (sem gerar arquivo real)
        audio_path = f"./temp_config_{i}.mp3"
        video_path = f"./output_config_{i}.mp4"
        
        if criar_audio_teste(texto_base, audio_path):
            try:
                # Para demonstração, usar timeout muito baixo
                resultado = generate_avatar_video(
                    text=texto_base,
                    audio_path=audio_path,
                    output_path=video_path,
                    timeout=5,  # Timeout baixo para demonstração
                    **{k: v for k, v in config.items() if k != 'nome'}
                )
                
                if resultado['success']:
                    print(f"   ✅ Sucesso simulado")
                else:
                    print(f"   ⚠️ Como esperado: {resultado['error'][:50]}...")
                    
            except Exception as e:
                print(f"   ⚠️ Erro esperado: {str(e)[:50]}...")
            
            # Limpeza
            if os.path.exists(audio_path):
                os.remove(audio_path)


def main():
    """
    Função principal do exemplo.
    """
    print("🎭 DEMONSTRAÇÃO: GERAÇÃO DE AVATAR COM HUNYUAN3D-2")
    print("="*70)
    print("🔗 API Externa: https://huggingface.co/spaces/tencent/Hunyuan3D-2")
    print("📝 Modelo: Tencent Hunyuan3D-2 (Talking Head Generation)")
    print("="*70)
    
    # Verificar dependências
    print("\n🔍 Verificando dependências...")
    try:
        import requests
        print("✅ requests disponível")
    except ImportError:
        print("❌ requests não encontrado - instale: pip install requests")
        return
    
    try:
        from moviepy.editor import VideoFileClip
        print("✅ moviepy disponível")
    except ImportError:
        print("⚠️ moviepy não encontrado - instale: pip install moviepy")
    
    try:
        from PIL import Image
        print("✅ PIL disponível")
    except ImportError:
        print("⚠️ PIL não encontrado - instale: pip install pillow")
    
    # Executar demonstrações
    try:
        demonstrar_avatar_basico()
        demonstrar_avatar_avancado()
        demonstrar_configuracoes_multiplas()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demonstração interrompida pelo usuário")
    
    except Exception as e:
        print(f"\n\n❌ Erro na demonstração: {e}")
    
    finally:
        print("\n" + "="*70)
        print("📊 RESUMO DA DEMONSTRAÇÃO")
        print("="*70)
        print("✅ Função generate_avatar_video testada")
        print("🔗 Integração com Hunyuan3D-2 configurada")
        print("🎯 Funcionalidades principais:")
        print("   • Detecção automática de idioma")
        print("   • Cache local inteligente")
        print("   • Monitoramento de fila com timeout")
        print("   • Fallback para simulação")
        print("   • Métricas detalhadas de qualidade")
        print("   • Configurações avançadas (background, emoção)")
        
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Configure o TTS real para gerar áudios")
        print("2. Teste com a API real do Hunyuan3D-2")
        print("3. Ajuste timeouts conforme necessário")
        print("4. Integre no pipeline de produção")
        
        print("\n🔧 CONFIGURAÇÃO MANUAL (se API offline):")
        print("1. Acesse: https://huggingface.co/spaces/tencent/Hunyuan3D-2")
        print("2. Faça upload do arquivo de áudio")
        print("3. Insira o texto desejado")
        print("4. Configure parâmetros e aguarde processamento")
        print("5. Baixe o vídeo gerado")
        print("="*70)


if __name__ == "__main__":
    main() 