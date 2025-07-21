#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração da Função: create_video_from_text_and_audio

Este script demonstra como usar a nova função implementada no utils.py
para criar vídeos a partir de texto e áudio sincronizados.

Funcionalidades demonstradas:
- Criação de slide com texto formatado
- Sincronização com áudio
- Geração de vídeo MP4 final
- Validação de arquivos criados

Autor: TecnoCursos AI
Data: 17/01/2025
"""

import os
import sys
import time

# Adicionar o diretório app ao path para importar utils
sys.path.append('app')

try:
    from app.utils import create_video_from_text_and_audio
    print("✅ Função create_video_from_text_and_audio importada com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar função: {e}")
    sys.exit(1)

def demonstrar_funcao():
    """
    Demonstra o uso da função create_video_from_text_and_audio
    com diferentes tipos de conteúdo e configurações.
    """
    print("🎬 DEMONSTRAÇÃO: create_video_from_text_and_audio")
    print("=" * 70)
    
    # Lista de exemplos para testar
    exemplos = [
        {
            "nome": "Introdução Técnica",
            "texto": """
            🚀 TecnoCursos AI - Plataforma de Ensino

            Bem-vindos à nova era do aprendizado!
            
            ✓ Inteligência Artificial aplicada
            ✓ Conteúdo personalizado
            ✓ Metodologia inovadora
            
            Prepare-se para transformar seu futuro!
            """,
            "audio": "app/static/audios/intro_tecnica.wav",
            "saida": "videos/demo_intro_tecnica.mp4"
        },
        {
            "nome": "Curso Python",
            "texto": """
            🐍 CURSO DE PYTHON

            Módulo 1: Fundamentos
            
            • Variáveis e tipos de dados
            • Estruturas de controle
            • Funções e módulos
            • Programação orientada a objetos
            
            Vamos começar a programar juntos!
            """,
            "audio": "app/static/audios/curso_python.wav",
            "saida": "videos/demo_curso_python.mp4"
        },
        {
            "nome": "Resumo Executivo",
            "texto": """
            📊 RELATÓRIO EXECUTIVO - Q1 2025

            Principais Métricas:
            ▲ 150% crescimento em usuários
            ▲ 89% satisfação do cliente
            ▲ 200+ cursos disponíveis
            
            Meta para Q2: Expansão internacional
            """,
            "audio": "app/static/audios/relatorio_exec.wav",
            "saida": "videos/demo_relatorio_exec.mp4"
        }
    ]
    
    # Resultados dos testes
    resultados = []
    
    for i, exemplo in enumerate(exemplos, 1):
        print(f"\n🎯 TESTE {i}: {exemplo['nome']}")
        print("-" * 50)
        
        # Criar áudio de teste se não existir
        if not os.path.exists(exemplo['audio']):
            print(f"🎵 Criando áudio de teste: {exemplo['nome']}")
            criar_audio_teste(exemplo['texto'][:100], exemplo['audio'])
        
        # Garantir que o diretório de saída existe
        os.makedirs(os.path.dirname(exemplo['saida']), exist_ok=True)
        
        # Executar a função
        print(f"🚀 Executando criação de vídeo...")
        inicio = time.time()
        
        resultado = create_video_from_text_and_audio(
            text=exemplo['texto'],
            audio_path=exemplo['audio'],
            output_path=exemplo['saida']
        )
        
        fim = time.time()
        tempo_execucao = fim - inicio
        
        # Validar resultado
        if resultado['success']:
            tamanho_mb = resultado['file_size'] / 1024 / 1024
            print(f"✅ Sucesso! Vídeo criado em {tempo_execucao:.2f}s")
            print(f"📁 Arquivo: {resultado['output_path']}")
            print(f"⏱️ Duração: {resultado['duration']:.2f}s")
            print(f"📐 Resolução: {resultado['resolution']}")
            print(f"💾 Tamanho: {tamanho_mb:.2f} MB")
            
            # Verificar se arquivo realmente existe
            if os.path.exists(resultado['output_path']):
                print(f"✅ Arquivo confirmado no sistema")
            else:
                print(f"⚠️ Arquivo não encontrado no caminho especificado")
        else:
            print(f"❌ Erro: {resultado['error']}")
        
        # Salvar resultado para resumo
        resultados.append({
            'nome': exemplo['nome'],
            'sucesso': resultado['success'],
            'tempo': tempo_execucao,
            'tamanho_mb': resultado['file_size'] / 1024 / 1024 if resultado['success'] else 0,
            'duracao': resultado['duration'] if resultado['success'] else 0
        })
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    
    sucessos = sum(1 for r in resultados if r['sucesso'])
    tempo_total = sum(r['tempo'] for r in resultados)
    tamanho_total = sum(r['tamanho_mb'] for r in resultados)
    
    print(f"✅ Sucessos: {sucessos}/{len(resultados)}")
    print(f"⏱️ Tempo total: {tempo_total:.2f}s")
    print(f"💾 Tamanho total: {tamanho_total:.2f} MB")
    print(f"📈 Taxa de sucesso: {(sucessos/len(resultados)*100):.1f}%")
    
    # Detalhes por teste
    print(f"\n📋 DETALHES POR TESTE:")
    for resultado in resultados:
        status = "✅" if resultado['sucesso'] else "❌"
        print(f"{status} {resultado['nome']: <20} | "
              f"{resultado['tempo']:5.2f}s | "
              f"{resultado['tamanho_mb']:5.2f}MB | "
              f"{resultado['duracao']:5.2f}s")
    
    return sucessos == len(resultados)


def criar_audio_teste(texto_base: str, caminho_audio: str):
    """
    Cria um arquivo de áudio de teste usando gTTS.
    
    Args:
        texto_base (str): Texto para gerar o áudio
        caminho_audio (str): Caminho onde salvar o áudio
    """
    try:
        from gtts import gTTS
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(caminho_audio), exist_ok=True)
        
        # Criar áudio
        tts = gTTS(text=texto_base, lang='pt', slow=False)
        tts.save(caminho_audio)
        
        print(f"✅ Áudio criado: {caminho_audio}")
        
    except ImportError:
        print("⚠️ gTTS não disponível - criando áudio silencioso")
        criar_audio_silencioso(caminho_audio, duracao=5.0)
    except Exception as e:
        print(f"⚠️ Erro ao criar áudio: {e}")
        criar_audio_silencioso(caminho_audio, duracao=5.0)


def criar_audio_silencioso(caminho_audio: str, duracao: float = 5.0):
    """
    Cria um arquivo de áudio silencioso para teste.
    
    Args:
        caminho_audio (str): Caminho onde salvar
        duracao (float): Duração em segundos
    """
    try:
        import wave
        import numpy as np
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(caminho_audio), exist_ok=True)
        
        # Configurações de áudio
        sample_rate = 44100
        frames = int(duracao * sample_rate)
        
        # Gerar silêncio (zeros)
        audio_data = np.zeros(frames, dtype=np.int16)
        
        # Salvar como WAV
        with wave.open(caminho_audio, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print(f"✅ Áudio silencioso criado: {caminho_audio} ({duracao}s)")
        
    except Exception as e:
        print(f"❌ Erro ao criar áudio silencioso: {e}")


def validar_dependencias():
    """
    Valida se todas as dependências necessárias estão disponíveis.
    """
    print("🔍 VALIDANDO DEPENDÊNCIAS")
    print("-" * 30)
    
    dependencias = {
        'moviepy': False,
        'PIL': False,
        'numpy': False,
        'gtts': False
    }
    
    # MoviePy
    try:
        import moviepy
        dependencias['moviepy'] = True
        print("✅ MoviePy: Disponível")
    except ImportError:
        print("❌ MoviePy: Não disponível - pip install moviepy")
    
    # PIL (Pillow)
    try:
        from PIL import Image
        dependencias['PIL'] = True
        print("✅ PIL/Pillow: Disponível")
    except ImportError:
        print("❌ PIL/Pillow: Não disponível - pip install pillow")
    
    # NumPy
    try:
        import numpy
        dependencias['numpy'] = True
        print("✅ NumPy: Disponível")
    except ImportError:
        print("❌ NumPy: Não disponível - pip install numpy")
    
    # gTTS (opcional)
    try:
        import gtts
        dependencias['gtts'] = True
        print("✅ gTTS: Disponível")
    except ImportError:
        print("⚠️ gTTS: Não disponível (opcional) - pip install gtts")
    
    # Verificar dependências críticas
    criticas = ['moviepy', 'PIL']
    criticas_ok = all(dependencias[dep] for dep in criticas)
    
    print(f"\n🎯 Dependências críticas: {'✅ OK' if criticas_ok else '❌ FALTANDO'}")
    
    if not criticas_ok:
        print("\n💡 INSTALAR DEPENDÊNCIAS:")
        print("pip install moviepy pillow numpy gtts")
        return False
    
    return True


if __name__ == '__main__':
    """
    Script principal de demonstração.
    """
    print("🎬 DEMO: Criador de Vídeo a partir de Texto e Áudio")
    print("=" * 70)
    print("📝 Função: create_video_from_text_and_audio()")
    print("📍 Localização: app/utils.py")
    print("🎯 Objetivo: Criar vídeos sincronizados com slides de texto")
    print()
    
    # Validar dependências
    if not validar_dependencias():
        print("\n❌ Dependências insuficientes. Instale os pacotes necessários.")
        sys.exit(1)
    
    # Executar demonstração
    try:
        sucesso = demonstrar_funcao()
        
        if sucesso:
            print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("🔗 Verifique os vídeos criados no diretório 'videos/'")
        else:
            print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
            
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("📚 Para usar a função em seu código:")
    print()
    print("```python")
    print("from app.utils import create_video_from_text_and_audio")
    print()
    print("resultado = create_video_from_text_and_audio(")
    print("    text='Seu texto aqui',")
    print("    audio_path='caminho/para/audio.wav',")
    print("    output_path='video_saida.mp4'")
    print(")")
    print()
    print("if resultado['success']:")
    print("    print(f'Vídeo criado: {resultado[\"output_path\"]}')")
    print("```")
    print("=" * 70) 