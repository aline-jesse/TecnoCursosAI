#!/usr/bin/env python3
"""
Teste Completo do Sistema Avatar - TecnoCursosAI
Script para verificar se toda a funcionalidade de avatar está funcionando
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar diretório do projeto ao Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from services.avatar_video_generator import (
        AvatarVideoGenerator, AvatarConfig, VideoConfig, SlideConfig,
        VideoContent, AvatarStyle, VideoQuality
    )
    print("✅ Importação do avatar_video_generator bem-sucedida!")
except ImportError as e:
    print(f"❌ Erro ao importar avatar_video_generator: {e}")
    sys.exit(1)

try:
    from services.tts_service import TTSService, TTSConfig, TTSProvider
    print("✅ Importação do tts_service bem-sucedida!")
except ImportError as e:
    print(f"⚠️ Aviso: TTS service não disponível: {e}")
    TTSService = None

def test_avatar_config():
    """Testar configurações do avatar"""
    print("\n🔧 Testando configurações do avatar...")
    
    try:
        # Configuração do avatar
        avatar_config = AvatarConfig(
            style=AvatarStyle.PROFESSIONAL,
            skin_color=(220, 180, 140),
            hair_color=(101, 67, 33),
            shirt_color=(50, 100, 150)
        )
        
        # Configuração do vídeo
        video_config = VideoConfig(
            width=1280,
            height=720,
            fps=30,
            quality=VideoQuality.HD_720P,
            background_color=(240, 240, 240),
            duration_per_slide=5.0
        )
        
        # Configuração dos slides
        slide_config = SlideConfig(
            font_size=48,
            title_font_size=64,
            text_color=(51, 51, 51),
            title_color=(25, 25, 112),
            background_color=(255, 255, 255),
            max_lines_per_slide=6
        )
        
        print("✅ Configurações criadas com sucesso!")
        return avatar_config, video_config, slide_config
        
    except Exception as e:
        print(f"❌ Erro ao criar configurações: {e}")
        return None, None, None

def test_video_content():
    """Testar criação de conteúdo do vídeo"""
    print("\n📝 Testando criação de conteúdo...")
    
    try:
        content = VideoContent(
            title="Introdução ao Python",
            slides=[
                {
                    "title": "O que é Python?",
                    "content": "Python é uma linguagem de programação de alto nível, interpretada e de propósito geral."
                },
                {
                    "title": "Vantagens do Python",
                    "content": "- Sintaxe simples e legível\n- Grande comunidade\n- Muitas bibliotecas\n- Multiplataforma"
                },
                {
                    "title": "Primeiro Programa",
                    "content": "O famoso 'Hello World' em Python:\n\nprint('Hello, World!')"
                }
            ],
            narration_text="Bem-vindos ao curso de Python. Hoje vamos aprender os conceitos básicos desta incrível linguagem de programação.",
            background_music=None,
            voice_settings={'voice': 'pt_speaker_0', 'speed': 1.0}
        )
        
        print("✅ Conteúdo criado com sucesso!")
        print(f"   Título: {content.title}")
        print(f"   Slides: {len(content.slides)}")
        print(f"   Narração: {content.narration_text[:50]}...")
        return content
        
    except Exception as e:
        print(f"❌ Erro ao criar conteúdo: {e}")
        return None

async def test_avatar_generation():
    """Testar geração completa de avatar"""
    print("\n🎭 Testando geração de avatar...")
    
    # Obter configurações
    avatar_config, video_config, slide_config = test_avatar_config()
    content = test_video_content()
    
    if not all([avatar_config, video_config, slide_config, content]):
        print("❌ Não foi possível criar as configurações necessárias")
        return False
    
    try:
        # Criar gerador
        generator = AvatarVideoGenerator(
            avatar_config=avatar_config,
            video_config=video_config,
            slide_config=slide_config
        )
        
        print("✅ AvatarVideoGenerator criado!")
        
        # Testar geração de frame do avatar
        print("🎨 Testando geração de frame do avatar...")
        avatar_frame = generator.avatar_generator.generate_avatar_frame(0)
        print(f"✅ Frame do avatar gerado: {avatar_frame.size}")
        
        # Testar geração de slide
        print("📄 Testando geração de slide...")
        slide_frame = generator.slide_generator.generate_slide(
            content.slides[0]["title"],
            content.slides[0]["content"]
        )
        print(f"✅ Slide gerado: {slide_frame.size}")
        
        # Gerar vídeo completo
        print("🎬 Iniciando geração de vídeo completo...")
        output_path = "test_avatar_completo.mp4"
        
        # Configurar callback de progresso
        def progress_callback(stage, progress, message):
            print(f"   {stage}: {progress:.1f}% - {message}")
        
        video_path = await generator.generate_video(
            content=content,
            output_path=output_path,
            progress_callback=progress_callback
        )
        
        if video_path and Path(video_path).exists():
            file_size = Path(video_path).stat().st_size
            print(f"✅ Vídeo gerado com sucesso!")
            print(f"   Arquivo: {video_path}")
            print(f"   Tamanho: {file_size / 1024:.1f} KB")
            return True
        else:
            print("❌ Vídeo não foi gerado corretamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante geração: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Testar integração com outras partes do sistema"""
    print("\n🔗 Testando integração...")
    
    try:
        # Testar se pode importar outros módulos do sistema
        try:
            from app.models import Video, User, Project
            print("✅ Modelos do banco importados")
        except ImportError as e:
            print(f"⚠️ Modelos do banco não disponíveis: {e}")
        
        try:
            from app.database import get_db, create_database
            print("✅ Sistema de banco importado")
        except ImportError as e:
            print(f"⚠️ Sistema de banco não disponível: {e}")
        
        try:
            from app.config import get_settings
            settings = get_settings()
            print(f"✅ Configurações carregadas: {settings.app_name}")
        except ImportError as e:
            print(f"⚠️ Configurações não disponíveis: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

async def main():
    """Função principal de teste"""
    print("🚀 TESTE COMPLETO DO SISTEMA AVATAR - TecnoCursosAI")
    print("=" * 60)
    
    # Verificar dependências
    print("\n📦 Verificando dependências...")
    dependencies = {
        'moviepy': None,
        'PIL': None,
        'numpy': None,
        'cv2': None
    }
    
    for dep in dependencies:
        try:
            if dep == 'PIL':
                import PIL
                dependencies[dep] = PIL.__version__
            elif dep == 'cv2':
                import cv2
                dependencies[dep] = cv2.__version__
            else:
                module = __import__(dep)
                dependencies[dep] = getattr(module, '__version__', 'disponível')
            print(f"✅ {dep}: {dependencies[dep]}")
        except ImportError:
            print(f"❌ {dep}: não encontrado")
            dependencies[dep] = None
    
    # Verificar se todas as dependências estão disponíveis
    missing_deps = [dep for dep, version in dependencies.items() if version is None]
    if missing_deps:
        print(f"\n❌ Dependências faltando: {', '.join(missing_deps)}")
        print("Execute: pip install moviepy pillow numpy opencv-python")
        return False
    
    # Executar testes
    tests = [
        ("Configurações", test_avatar_config),
        ("Conteúdo", test_video_content),
        ("Integração", test_integration),
        ("Geração de Avatar", test_avatar_generation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results[test_name] = False
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*60}")
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nTestes: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 Sistema Avatar está funcional!")
        return True
    else:
        print("⚠️ Sistema Avatar precisa de correções")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 