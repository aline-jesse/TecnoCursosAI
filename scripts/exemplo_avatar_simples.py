"""
Exemplo Simples - Geração de Vídeo do Avatar
Demonstra como usar a função principal sem dependências complexas
"""

import asyncio
import os
from pathlib import Path

# Função simplificada que não depende do sistema completo
async def exemplo_simples():
    """Exemplo básico sem dependências do sistema completo"""
    
    print("🎬 TecnoCursos AI - Gerador de Vídeo do Avatar")
    print("=" * 50)
    
    # Verificar se as dependências principais estão disponíveis
    try:
        from PIL import Image, ImageDraw, ImageFont
        from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
        import numpy as np
        print("✅ Dependências principais disponíveis")
    except ImportError as e:
        print(f"❌ Dependências faltando: {e}")
        print("Execute: pip install pillow moviepy numpy opencv-python")
        return
    
    # Slides de exemplo
    slides = [
        {
            "title": "Bem-vindos ao Curso de Python",
            "content": "Python é uma linguagem de programação versátil e poderosa, ideal para iniciantes e profissionais."
        },
        {
            "title": "Variáveis e Tipos de Dados",
            "content": "Em Python, você pode armazenar diferentes tipos de informações em variáveis: números, textos, listas e muito mais."
        },
        {
            "title": "Estruturas de Controle",
            "content": "Use if/else para tomar decisões e loops for/while para repetir ações no seu código Python."
        }
    ]
    
    # Textos para narração
    textos_narracao = [
        "Olá! Seja muito bem-vindo ao nosso curso completo de Python. Eu sou sua instrutora virtual e vou acompanhar você em toda essa jornada de aprendizado.",
        "Agora vamos aprender sobre variáveis em Python. É muito simples: você pode guardar informações como seu nome, idade ou qualquer outro dado.",
        "As estruturas de controle são fundamentais em programação. Elas permitem que seus programas tomem decisões inteligentes e executem tarefas repetitivas."
    ]
    
    try:
        # Tentar importar a função principal
        from services.avatar_video_generator import generate_avatar_video
        
        print("🎤 Gerando vídeo com avatar...")
        
        # Caminho de saída
        output_path = "./meu_video_avatar.mp4"
        
        # Gerar vídeo
        resultado = await generate_avatar_video(
            slides=slides,
            audio_texts=textos_narracao,
            output_path=output_path,
            avatar_style="teacher",  # professional, friendly, teacher, minimal
            video_quality="720p"     # 720p, 1080p, 4k
        )
        
        if resultado["success"]:
            print("\n🎉 SUCESSO! Vídeo gerado com avatar!")
            print(f"📁 Arquivo: {resultado['output_path']}")
            print(f"⏱️  Duração: {resultado['duration']:.1f} segundos")
            print(f"📊 Slides: {resultado['slides_count']}")
            print(f"📏 Resolução: {resultado['resolution']}")
            print(f"💾 Tamanho: {resultado['file_size'] / (1024*1024):.1f} MB")
            
            # Verificar se arquivo foi criado
            if os.path.exists(resultado['output_path']):
                print(f"✅ Arquivo confirmado em: {os.path.abspath(resultado['output_path'])}")
            else:
                print("⚠️  Arquivo não encontrado no local especificado")
                
        else:
            print(f"❌ Erro na geração: {resultado['error']}")
            
    except ImportError:
        print("⚠️  Módulo avatar_video_generator não encontrado")
        print("Execute este script a partir da pasta raiz do projeto")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

async def exemplo_personalizado():
    """Exemplo com avatar personalizado"""
    
    print("\n🎨 Exemplo com Avatar Personalizado")
    print("=" * 40)
    
    try:
        from services.avatar_video_generator import (
            AvatarVideoGenerator, VideoContent, AvatarConfig,
            VideoConfig, SlideConfig, AvatarStyle
        )
        
        # Criar gerador personalizado
        generator = AvatarVideoGenerator()
        
        # Personalizar avatar - estilo amigável
        generator.update_avatar_config(
            style=AvatarStyle.FRIENDLY,
            skin_tone="#f4c2a1",      # Tom de pele mais claro
            hair_color="#654321",     # Cabelo castanho
            shirt_color="#e74c3c",    # Camisa vermelha
            background_color="#ecf0f1" # Fundo cinza claro
        )
        
        # Configurar vídeo HD
        generator.update_video_config(
            resolution=(1280, 720),   # HD
            fps=25,                   # 25 FPS
            fade_in_duration=1.0,     # Fade in de 1 segundo
            fade_out_duration=1.0     # Fade out de 1 segundo
        )
        
        # Configurar slides com cores personalizadas
        generator.update_slide_config(
            title_color="#2c3e50",    # Título azul escuro
            content_color="#34495e",  # Conteúdo cinza escuro
            accent_color="#e74c3c",   # Destaque vermelho
            background_color="#ffffff" # Fundo branco
        )
        
        # Conteúdo sobre JavaScript
        slides = [
            {
                "title": "Introdução ao JavaScript",
                "content": "JavaScript é a linguagem da web! Ela permite criar páginas interativas e aplicações dinâmicas."
            },
            {
                "title": "Funções em JavaScript", 
                "content": "Funções são blocos de código reutilizáveis que executam tarefas específicas. São fundamentais em JS!"
            }
        ]
        
        textos = [
            "Oi, pessoal! Vamos mergulhar no mundo incrível do JavaScript. É a linguagem que dá vida às páginas web!",
            "Agora vamos aprender sobre funções. Elas são como pequenas máquinas que fazem trabalhos específicos no seu código."
        ]
        
        # Criar conteúdo
        content = VideoContent(
            slides=slides,
            audio_texts=textos
        )
        
        print("🎨 Gerando vídeo personalizado...")
        
        # Gerar vídeo
        resultado = await generator.generate_video(
            content=content,
            output_path="./video_js_personalizado.mp4"
        )
        
        if resultado["success"]:
            print("✅ Vídeo personalizado criado com sucesso!")
            print(f"📁 {resultado['output_path']}")
            print(f"⏱️  {resultado['duration']:.1f}s")
        else:
            print(f"❌ Erro: {resultado['error']}")
            
    except ImportError as e:
        print(f"⚠️  Módulo não encontrado: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_estrutura_projeto():
    """Verifica se a estrutura do projeto está correta"""
    print("🔍 Verificando Estrutura do Projeto")
    print("=" * 35)
    
    arquivos_necessarios = [
        "services/avatar_video_generator.py",
        "services/tts_service.py",
        "app/config.py",
        "app/logger.py"
    ]
    
    estrutura_ok = True
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - FALTANDO")
            estrutura_ok = False
    
    if estrutura_ok:
        print("✅ Estrutura do projeto está correta!")
        return True
    else:
        print("⚠️  Execute este script da pasta raiz do projeto TecnoCursosAI")
        return False

async def main():
    """Função principal"""
    print("🚀 TecnoCursos AI - Teste Simples do Avatar")
    print("=" * 50)
    
    # Verificar estrutura
    if not verificar_estrutura_projeto():
        return
    
    print("\n")
    
    # Executar exemplos
    await exemplo_simples()
    await exemplo_personalizado()
    
    print("\n" + "=" * 50)
    print("🎬 Exemplos concluídos!")
    print("📁 Verifique os arquivos .mp4 gerados")
    print("🎥 Abra os vídeos para ver o avatar em ação!")

if __name__ == "__main__":
    # Executar exemplo
    asyncio.run(main()) 