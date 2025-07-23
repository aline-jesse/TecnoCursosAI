"""
Script de Teste - Geração de Vídeo do Avatar
Demonstra como usar o serviço de geração de vídeos do avatar
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar ao path
sys.path.append(str(Path(__file__).parent))

from services.avatar_video_generator import (
    generate_avatar_video, 
    AvatarVideoGenerator,
    VideoContent,
    AvatarConfig,
    VideoConfig,
    SlideConfig,
    AvatarStyle
)

async def teste_basico():
    """Teste básico da geração de vídeo"""
    print("🎬 Teste Básico - Geração de Vídeo do Avatar")
    print("=" * 50)
    
    # Dados de exemplo
    slides = [
        {
            "title": "Introdução ao Python",
            "content": "Python é uma linguagem de programação poderosa e fácil de aprender. É amplamente utilizada em desenvolvimento web, ciência de dados e automação."
        },
        {
            "title": "Variáveis em Python", 
            "content": "Em Python, você pode criar variáveis simplesmente atribuindo valores a elas. Por exemplo: nome = 'João' ou idade = 25."
        },
        {
            "title": "Estruturas de Controle",
            "content": "Python oferece estruturas como if/else para tomada de decisões e loops for/while para repetição de código."
        }
    ]
    
    textos_narracao = [
        "Olá! Bem-vindos ao nosso curso de Python. Eu sou sua instrutora virtual e vou guiá-los através dos conceitos fundamentais desta linguagem incrível.",
        "Vamos começar aprendendo sobre variáveis. Em Python, criar variáveis é muito simples e intuitivo. Vou mostrar alguns exemplos práticos.",
        "Agora vamos explorar as estruturas de controle. Essas estruturas permitem que nossos programas tomem decisões e executem código repetidamente."
    ]
    
    # Caminho de saída
    output_path = "./video_exemplo_python.mp4"
    
    try:
        print("🎤 Gerando vídeo...")
        resultado = await generate_avatar_video(
            slides=slides,
            audio_texts=textos_narracao,
            output_path=output_path,
            avatar_style="teacher",
            video_quality="1080p"
        )
        
        if resultado["success"]:
            print(f"✅ Vídeo gerado com sucesso!")
            print(f"   📁 Arquivo: {resultado['output_path']}")
            print(f"   ⏱️  Duração: {resultado['duration']:.2f} segundos")
            print(f"   📊 Slides: {resultado['slides_count']}")
            print(f"   📏 Resolução: {resultado['resolution']}")
            print(f"   💾 Tamanho: {resultado['file_size'] / (1024*1024):.1f} MB")
        else:
            print(f"❌ Erro na geração: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

async def teste_personalizado():
    """Teste com configurações personalizadas"""
    print("\n🎨 Teste Personalizado - Avatar Customizado")
    print("=" * 50)
    
    # Criar gerador personalizado
    generator = AvatarVideoGenerator()
    
    # Personalizar avatar
    generator.update_avatar_config(
        style=AvatarStyle.FRIENDLY,
        skin_tone="#f4c2a1",
        hair_color="#654321",
        shirt_color="#2ecc71",
        background_color="#ecf0f1"
    )
    
    # Personalizar vídeo
    generator.update_video_config(
        resolution=(1280, 720),  # HD
        fps=24,
        fade_in_duration=1.0,
        fade_out_duration=1.0
    )
    
    # Personalizar slides
    generator.update_slide_config(
        template="modern",
        title_color="#2c3e50",
        content_color="#34495e",
        accent_color="#e74c3c",
        background_color="#ffffff"
    )
    
    # Conteúdo sobre tecnologia
    slides = [
        {
            "title": "O Futuro da Inteligência Artificial",
            "content": "A IA está revolucionando diversos setores, desde saúde até transporte. Vamos explorar as principais tendências e aplicações."
        },
        {
            "title": "Machine Learning na Prática",
            "content": "Algoritmos de ML permitem que computadores aprendam padrões em dados e façam previsões precisas automaticamente."
        }
    ]
    
    textos_narracao = [
        "Oi pessoal! Hoje vamos falar sobre o futuro da inteligência artificial. É um tema fascinante que está moldando nosso mundo.",
        "Agora vamos mergulhar no machine learning. É incrível como os computadores podem aprender e melhorar sozinhos!"
    ]
    
    content = VideoContent(
        slides=slides,
        audio_texts=textos_narracao
    )
    
    output_path = "./video_ia_personalizado.mp4"
    
    try:
        print("🎨 Gerando vídeo personalizado...")
        resultado = await generator.generate_video(content, output_path)
        
        if resultado["success"]:
            print(f"✅ Vídeo personalizado gerado!")
            print(f"   📁 Arquivo: {resultado['output_path']}")
            print(f"   ⏱️  Duração: {resultado['duration']:.2f} segundos")
        else:
            print(f"❌ Erro: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

async def teste_multiplos_estilos():
    """Teste com diferentes estilos de avatar"""
    print("\n👥 Teste Múltiplos Estilos")
    print("=" * 50)
    
    estilos = ["professional", "friendly", "teacher", "minimal"]
    
    slide_base = {
        "title": "Teste de Estilo",
        "content": "Este é um teste para demonstrar diferentes estilos de avatar disponíveis no sistema."
    }
    
    texto_base = "Olá! Este é um teste de estilo de avatar. Cada vídeo mostra um estilo diferente de apresentador virtual."
    
    for estilo in estilos:
        output_path = f"./video_estilo_{estilo}.mp4"
        
        try:
            print(f"🎭 Gerando estilo: {estilo}")
            resultado = await generate_avatar_video(
                slides=[slide_base],
                audio_texts=[texto_base],
                output_path=output_path,
                avatar_style=estilo,
                video_quality="720p"  # Menor para testes rápidos
            )
            
            if resultado["success"]:
                print(f"   ✅ {estilo}: {resultado['duration']:.1f}s")
            else:
                print(f"   ❌ {estilo}: {resultado['error']}")
                
        except Exception as e:
            print(f"   ❌ {estilo}: Erro - {e}")

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando Dependências")
    print("=" * 30)
    
    dependencias = {
        "PIL": "Pillow",
        "cv2": "opencv-python", 
        "moviepy": "moviepy",
        "numpy": "numpy"
    }
    
    todas_ok = True
    
    for modulo, pacote in dependencias.items():
        try:
            __import__(modulo)
            print(f"   ✅ {pacote}")
        except ImportError:
            print(f"   ❌ {pacote} - FALTANDO")
            todas_ok = False
    
    if not todas_ok:
        print("\n⚠️  Instale as dependências faltantes:")
        print("pip install pillow opencv-python moviepy numpy")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

async def main():
    """Função principal do teste"""
    print("🚀 TecnoCursos AI - Teste do Gerador de Vídeo do Avatar")
    print("=" * 60)
    
    # Verificar dependências
    if not verificar_dependencias():
        return
    
    print("\n")
    
    # Executar testes
    try:
        await teste_basico()
        await teste_personalizado()
        await teste_multiplos_estilos()
        
        print("\n" + "=" * 60)
        print("🎉 Todos os testes concluídos!")
        print("📁 Verifique os arquivos MP4 gerados no diretório atual")
        
    except Exception as e:
        print(f"\n❌ Erro geral nos testes: {e}")

if __name__ == "__main__":
    # Executar testes
    asyncio.run(main()) 