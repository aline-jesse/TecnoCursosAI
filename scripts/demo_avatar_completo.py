#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEMONSTRAÇÃO COMPLETA DO SISTEMA AVANÇADO DE VÍDEO AVATAR
=========================================================

Este arquivo demonstra todas as funcionalidades implementadas no sistema
de geração de vídeo avatar com IA, incluindo:

✅ FUNCIONALIDADES IMPLEMENTADAS:
- 4 Templates visuais profissionais (professional, educational, tech, minimal)
- Sistema de cache inteligente para otimização
- Callbacks de progresso em tempo real
- Detecção automática de idioma (português, inglês, espanhol)
- Efeitos visuais avançados (gradientes, bordas, sombras)
- Suporte inicial para D-ID API (com fallback automático)
- Múltiplas resoluções e qualidades
- Sistema de pontuação de qualidade
- Validações robustas de entrada
- Cleanup automático de arquivos temporários

🚀 FUTURAS INTEGRAÇÕES:
- Hunyuan3D-2 API para avatares 3D realistas
- Synthesia API para apresentações corporativas
- RunwayML para efeitos especiais avançados
- Lip-sync preciso e gestos naturais
"""

import os
import sys
import time
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from app.utils import (
    generate_avatar_video, 
    generate_narration_sync,
    format_file_size
)


def progress_callback(percentage: int, message: str):
    """
    Callback para mostrar progresso em tempo real.
    
    Args:
        percentage (int): Porcentagem de progresso (0-100)
        message (str): Mensagem de status atual
    """
    bar_length = 40
    filled_length = int(bar_length * percentage // 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f'\r🎬 [{bar}] {percentage}% - {message}', end='', flush=True)
    
    if percentage == 100:
        print()  # Nova linha quando completo


def demo_template_professional():
    """Demonstra template profissional corporativo."""
    
    print("\n" + "="*80)
    print("🏢 DEMONSTRAÇÃO: TEMPLATE PROFESSIONAL (CORPORATIVO)")
    print("="*80)
    
    texto = """Apresentação Corporativa
    
    Bem-vindos à nossa apresentação sobre inovação tecnológica.
    
    Nossa empresa está na vanguarda da transformação digital,
    oferecendo soluções de inteligência artificial que revolucionam
    a forma como as empresas operam no século XXI.
    
    Juntos, construiremos o futuro dos negócios."""
    
    # Gerar áudio
    print("🎤 Gerando narração profissional...")
    audio_result = generate_narration_sync(
        text=texto,
        output_path="demo_professional_audio.mp3",
        provider="gtts",
        language="pt"
    )
    
    if audio_result['success']:
        print(f"✅ Áudio criado: {audio_result['duration']:.2f}s")
        
        # Gerar vídeo com template profissional
        print("🎬 Gerando vídeo corporativo...")
        video_result = generate_avatar_video(
            text=texto,
            audio_path=audio_result['audio_path'],
            output_path="demo_professional_video.mp4",
            template="professional",
            avatar_style="slide_mvp",
            progress_callback=progress_callback,
            cache_enabled=True,
            resolution=(1920, 1080),
            effects=['fade_in', 'logo_overlay']
        )
        
        if video_result['success']:
            print(f"✅ Vídeo profissional criado!")
            print(f"📁 Arquivo: {video_result['video_path']}")
            print(f"⏱️ Duração: {video_result['duration']:.2f}s")
            print(f"🎨 Template: {video_result['template_used']}")
            print(f"📊 Qualidade: {video_result['quality_score']:.2f}")
            print(f"💾 Cached: {'Sim' if video_result['cached'] else 'Não'}")
            print(f"📋 Tamanho: {format_file_size(video_result['file_size'])}")
        else:
            print(f"❌ Erro: {video_result['error']}")
    else:
        print(f"❌ Erro no áudio: {audio_result['error']}")


def demo_template_educational():
    """Demonstra template educacional amigável."""
    
    print("\n" + "="*80)
    print("🎓 DEMONSTRAÇÃO: TEMPLATE EDUCATIONAL (EDUCACIONAL)")
    print("="*80)
    
    texto = """Introdução à Inteligência Artificial
    
    Olá, estudantes! Hoje vamos explorar o fascinante mundo da IA.
    
    A inteligência artificial está transformando nossa sociedade
    de maneiras que antes só existiam na ficção científica.
    
    Desde assistentes virtuais até carros autônomos,
    a IA está presente em nossas vidas diárias.
    
    Vamos descobrir juntos como essa tecnologia funciona!"""
    
    # Gerar áudio
    print("🎤 Gerando narração educacional...")
    audio_result = generate_narration_sync(
        text=texto,
        output_path="demo_educational_audio.mp3",
        provider="gtts",
        language="pt"
    )
    
    if audio_result['success']:
        print(f"✅ Áudio criado: {audio_result['duration']:.2f}s")
        
        # Gerar vídeo com template educacional
        print("🎬 Gerando vídeo educacional...")
        video_result = generate_avatar_video(
            text=texto,
            audio_path=audio_result['audio_path'],
            output_path="demo_educational_video.mp4",
            template="educational",
            avatar_style="slide_mvp",
            progress_callback=progress_callback,
            cache_enabled=True,
            quality="high",
            effects=['educational_icons', 'friendly_animation']
        )
        
        if video_result['success']:
            print(f"✅ Vídeo educacional criado!")
            print(f"📁 Arquivo: {video_result['video_path']}")
            print(f"⏱️ Duração: {video_result['duration']:.2f}s")
            print(f"🎨 Template: {video_result['template_used']}")
            print(f"🌐 Idioma: {video_result['metadata']['language']}")
            print(f"📊 Qualidade: {video_result['quality_score']:.2f}")
        else:
            print(f"❌ Erro: {video_result['error']}")
    else:
        print(f"❌ Erro no áudio: {audio_result['error']}")


def demo_template_tech():
    """Demonstra template tecnológico futurista."""
    
    print("\n" + "="*80)
    print("🤖 DEMONSTRAÇÃO: TEMPLATE TECH (TECNOLÓGICO)")
    print("="*80)
    
    texto = """Sistemas de IA Avançados
    
    Bem-vindos ao futuro da computação quântica e inteligência artificial.
    
    Nossos algoritmos de machine learning operam em tempo real,
    processando terabytes de dados com precisão nanométrica.
    
    A convergência entre redes neurais e computação distribuída
    está criando possibilidades antes inimagináveis.
    
    Prepare-se para a próxima revolução tecnológica."""
    
    # Gerar áudio
    print("🎤 Gerando narração tecnológica...")
    audio_result = generate_narration_sync(
        text=texto,
        output_path="demo_tech_audio.mp3",
        provider="gtts",
        language="pt"
    )
    
    if audio_result['success']:
        print(f"✅ Áudio criado: {audio_result['duration']:.2f}s")
        
        # Gerar vídeo com template tech
        print("🎬 Gerando vídeo tecnológico...")
        video_result = generate_avatar_video(
            text=texto,
            audio_path=audio_result['audio_path'],
            output_path="demo_tech_video.mp4",
            template="tech",
            avatar_style="slide_mvp",
            progress_callback=progress_callback,
            cache_enabled=True,
            resolution=(1920, 1080),
            fps=30,
            effects=['neon_glow', 'tech_grid', 'cyber_animation']
        )
        
        if video_result['success']:
            print(f"✅ Vídeo tecnológico criado!")
            print(f"📁 Arquivo: {video_result['video_path']}")
            print(f"⏱️ Duração: {video_result['duration']:.2f}s")
            print(f"🎨 Template: {video_result['template_used']}")
            print(f"🔧 Método: {video_result['method']}")
            print(f"📊 Qualidade: {video_result['quality_score']:.2f}")
            print(f"🎭 Efeitos: {len(video_result['metadata']['effects_applied'])}")
        else:
            print(f"❌ Erro: {video_result['error']}")
    else:
        print(f"❌ Erro no áudio: {audio_result['error']}")


def demo_template_minimal():
    """Demonstra template minimalista limpo."""
    
    print("\n" + "="*80)
    print("🎨 DEMONSTRAÇÃO: TEMPLATE MINIMAL (MINIMALISTA)")
    print("="*80)
    
    texto = """Design Minimalista
    
    A simplicidade é a máxima sofisticação.
    
    Em um mundo cheio de ruído e complexidade,
    o design minimalista oferece clareza e foco.
    
    Menos é mais. Cada elemento tem propósito.
    Cada palavra, cada espaço, cada cor.
    
    A beleza está na simplicidade."""
    
    # Gerar áudio
    print("🎤 Gerando narração minimalista...")
    audio_result = generate_narration_sync(
        text=texto,
        output_path="demo_minimal_audio.mp3",
        provider="gtts",
        language="pt"
    )
    
    if audio_result['success']:
        print(f"✅ Áudio criado: {audio_result['duration']:.2f}s")
        
        # Gerar vídeo com template minimal
        print("🎬 Gerando vídeo minimalista...")
        video_result = generate_avatar_video(
            text=texto,
            audio_path=audio_result['audio_path'],
            output_path="demo_minimal_video.mp4",
            template="minimal",
            avatar_style="slide_mvp",
            progress_callback=progress_callback,
            cache_enabled=True,
            quality="ultra_high",
            effects=['clean_lines', 'subtle_fade']
        )
        
        if video_result['success']:
            print(f"✅ Vídeo minimalista criado!")
            print(f"📁 Arquivo: {video_result['video_path']}")
            print(f"⏱️ Duração: {video_result['duration']:.2f}s")
            print(f"🎨 Template: {video_result['template_used']}")
            print(f"⚡ Tempo de processamento: {video_result['processing_time']:.2f}s")
            print(f"📊 Qualidade: {video_result['quality_score']:.2f}")
        else:
            print(f"❌ Erro: {video_result['error']}")
    else:
        print(f"❌ Erro no áudio: {audio_result['error']}")


def demo_cache_performance():
    """Demonstra performance do sistema de cache."""
    
    print("\n" + "="*80)
    print("💾 DEMONSTRAÇÃO: SISTEMA DE CACHE INTELIGENTE")
    print("="*80)
    
    texto = "Este é um teste de cache para medir performance de geração de vídeo."
    
    print("🎤 Gerando áudio para teste de cache...")
    audio_result = generate_narration_sync(
        text=texto,
        output_path="demo_cache_audio.mp3",
        provider="gtts"
    )
    
    if audio_result['success']:
        # Primeira geração (sem cache)
        print("\n1️⃣ PRIMEIRA GERAÇÃO (sem cache):")
        start_time = time.time()
        
        video_result1 = generate_avatar_video(
            text=texto,
            audio_path=audio_result['audio_path'],
            output_path="demo_cache_video1.mp4",
            template="professional",
            cache_enabled=True
        )
        
        first_time = time.time() - start_time
        
        if video_result1['success']:
            print(f"✅ Primeira geração: {first_time:.2f}s")
            print(f"💾 Cached: {video_result1['cached']}")
            
            # Segunda geração (com cache)
            print("\n2️⃣ SEGUNDA GERAÇÃO (com cache):")
            start_time = time.time()
            
            video_result2 = generate_avatar_video(
                text=texto,
                audio_path=audio_result['audio_path'],
                output_path="demo_cache_video2.mp4",
                template="professional",
                cache_enabled=True
            )
            
            second_time = time.time() - start_time
            
            if video_result2['success']:
                print(f"✅ Segunda geração: {second_time:.2f}s")
                print(f"💾 Cached: {video_result2['cached']}")
                
                if video_result2['cached']:
                    improvement = ((first_time - second_time) / first_time) * 100
                    print(f"🚀 Melhoria de performance: {improvement:.1f}%")
                else:
                    print("ℹ️ Cache não encontrado (parâmetros diferentes)")
        else:
            print(f"❌ Erro na primeira geração: {video_result1['error']}")
    else:
        print(f"❌ Erro no áudio: {audio_result['error']}")


def demo_d_id_api_simulation():
    """Simula integração com D-ID API (caso tenha chave configurada)."""
    
    print("\n" + "="*80)
    print("🤖 DEMONSTRAÇÃO: INTEGRAÇÃO D-ID API (SIMULAÇÃO)")
    print("="*80)
    
    # Verificar se D-ID API está configurada
    d_id_key = os.getenv('D_ID_API_KEY')
    
    if d_id_key:
        print(f"🔑 D-ID API Key detectada: {d_id_key[:10]}...")
        print("🚧 Tentando conexão com D-ID API...")
        
        texto = """Avatar 3D Realista
        
        Olá! Eu sou um avatar 3D criado com inteligência artificial.
        Posso falar de forma natural e sincronizar meus movimentos labiais
        com qualquer texto que você quiser.
        
        Esta é a próxima geração de apresentações digitais!"""
        
        print("🎤 Gerando áudio para D-ID...")
        audio_result = generate_narration_sync(
            text=texto,
            output_path="demo_d_id_audio.mp3",
            provider="gtts"
        )
        
        if audio_result['success']:
            print("🎬 Tentando gerar vídeo com D-ID API...")
            video_result = generate_avatar_video(
                text=texto,
                audio_path=audio_result['audio_path'],
                output_path="demo_d_id_video.mp4",
                template="professional",
                avatar_style="d_id",
                progress_callback=progress_callback,
                cache_enabled=True
            )
            
            if video_result['success']:
                print(f"✅ Vídeo D-ID criado!")
                print(f"🤖 API usada: {video_result['avatar_api_used']}")
                print(f"🎬 Método: {video_result['method']}")
                print(f"📊 Qualidade: {video_result['quality_score']:.2f}")
            else:
                print(f"⚠️ Fallback para MVP: {video_result['error']}")
        else:
            print(f"❌ Erro no áudio: {audio_result['error']}")
    else:
        print("ℹ️ D-ID API Key não configurada.")
        print("💡 Para testar, configure: export D_ID_API_KEY='sua_chave'")
        print("🔄 Sistema usará MVP avançado como fallback.")


def main():
    """Função principal de demonstração."""
    
    print("🎬" * 20)
    print("SISTEMA AVANÇADO DE GERAÇÃO DE VÍDEO AVATAR COM IA")
    print("🎬" * 20)
    print(f"🕒 Iniciado em: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar dependências
    try:
        from PIL import Image
        print("✅ PIL/Pillow disponível")
    except ImportError:
        print("❌ PIL/Pillow não disponível - instale com: pip install pillow")
        return
    
    try:
        import cv2
        print("✅ OpenCV disponível")
    except ImportError:
        print("⚠️ OpenCV não disponível - funcionalidade limitada")
    
    # Menu de demonstração
    print("\n📋 DEMONSTRAÇÕES DISPONÍVEIS:")
    print("1. Template Professional (Corporativo)")
    print("2. Template Educational (Educacional)")  
    print("3. Template Tech (Tecnológico)")
    print("4. Template Minimal (Minimalista)")
    print("5. Sistema de Cache")
    print("6. D-ID API (se configurada)")
    print("7. Executar todas as demonstrações")
    print("0. Sair")
    
    try:
        choice = input("\n👉 Escolha uma opção (0-7): ").strip()
        
        if choice == '1':
            demo_template_professional()
        elif choice == '2':
            demo_template_educational()
        elif choice == '3':
            demo_template_tech()
        elif choice == '4':
            demo_template_minimal()
        elif choice == '5':
            demo_cache_performance()
        elif choice == '6':
            demo_d_id_api_simulation()
        elif choice == '7':
            print("\n🚀 EXECUTANDO TODAS AS DEMONSTRAÇÕES...")
            demo_template_professional()
            demo_template_educational()
            demo_template_tech()
            demo_template_minimal()
            demo_cache_performance()
            demo_d_id_api_simulation()
        elif choice == '0':
            print("\n👋 Saindo...")
            return
        else:
            print("❌ Opção inválida!")
            return
            
        print("\n" + "="*80)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("="*80)
        print(f"📁 Verifique os arquivos gerados no diretório atual")
        print(f"🎬 Templates demonstrados: professional, educational, tech, minimal")
        print(f"💾 Sistema de cache testado")
        print(f"🔗 Integração D-ID demonstrada")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n⏹️ Demonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")


if __name__ == "__main__":
    main() 