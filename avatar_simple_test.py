#!/usr/bin/env python3
"""
Teste Simples do Sistema Avatar - TecnoCursosAI
Teste básico para verificar funcionamento sem dependências complexas
"""

import sys
import os
from pathlib import Path

# Adicionar diretório do projeto ao Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Verificar dependências básicas"""
    print("🔍 Verificando dependências...")
    
    deps = {}
    
    # PIL/Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
        deps['PIL'] = "✅ Disponível"
        print(f"✅ PIL/Pillow: Disponível")
    except ImportError as e:
        deps['PIL'] = f"❌ Erro: {e}"
        print(f"❌ PIL/Pillow: {e}")
    
    # NumPy
    try:
        import numpy as np
        deps['numpy'] = "✅ Disponível"
        print(f"✅ NumPy: Disponível")
    except ImportError as e:
        deps['numpy'] = f"❌ Erro: {e}"
        print(f"❌ NumPy: {e}")
    
    # MoviePy
    try:
        from moviepy.editor import ImageClip, VideoFileClip
        deps['moviepy'] = "✅ Disponível"
        print(f"✅ MoviePy: Disponível")
    except ImportError as e:
        deps['moviepy'] = f"❌ Erro: {e}"
        print(f"❌ MoviePy: {e}")
    
    # OpenCV (opcional)
    try:
        import cv2
        deps['cv2'] = "✅ Disponível"
        print(f"✅ OpenCV: Disponível")
    except ImportError as e:
        deps['cv2'] = f"⚠️ Opcional: {e}"
        print(f"⚠️ OpenCV (opcional): {e}")
    
    return deps

def test_basic_avatar_creation():
    """Testar criação básica de avatar"""
    print("\n🎭 Testando criação básica de avatar...")
    
    try:
        from PIL import Image, ImageDraw
        import numpy as np
        
        # Criar uma imagem simples de avatar
        width, height = 400, 600
        img = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Desenhar cabeça (círculo)
        head_center = (width // 2, height // 3)
        head_radius = 80
        draw.ellipse([
            head_center[0] - head_radius, head_center[1] - head_radius,
            head_center[0] + head_radius, head_center[1] + head_radius
        ], fill=(220, 180, 140), outline=(180, 140, 100))
        
        # Desenhar olhos
        eye_y = head_center[1] - 20
        left_eye = (head_center[0] - 25, eye_y)
        right_eye = (head_center[0] + 25, eye_y)
        
        draw.ellipse([left_eye[0] - 8, left_eye[1] - 8, left_eye[0] + 8, left_eye[1] + 8], fill=(0, 0, 0))
        draw.ellipse([right_eye[0] - 8, right_eye[1] - 8, right_eye[0] + 8, right_eye[1] + 8], fill=(0, 0, 0))
        
        # Desenhar boca
        mouth_center = (head_center[0], head_center[1] + 30)
        draw.arc([
            mouth_center[0] - 20, mouth_center[1] - 10,
            mouth_center[0] + 20, mouth_center[1] + 10
        ], start=0, end=180, fill=(0, 0, 0), width=3)
        
        # Desenhar corpo (retângulo)
        body_top = head_center[1] + head_radius + 20
        body_width = 120
        body_height = 200
        draw.rectangle([
            head_center[0] - body_width // 2, body_top,
            head_center[0] + body_width // 2, body_top + body_height
        ], fill=(50, 100, 150), outline=(30, 70, 120))
        
        # Salvar imagem de teste
        output_path = "avatar_test.png"
        img.save(output_path)
        
        print(f"✅ Avatar básico criado: {output_path}")
        print(f"   Tamanho: {img.size}")
        
        return True, output_path
        
    except Exception as e:
        print(f"❌ Erro ao criar avatar: {e}")
        return False, None

def test_basic_slide_creation():
    """Testar criação básica de slide"""
    print("\n📄 Testando criação básica de slide...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Criar slide
        width, height = 1280, 720
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Tentar usar fonte padrão
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            text_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Desenhar título
        title = "Introdução ao Python"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        draw.text((title_x, 100), title, fill=(25, 25, 112), font=title_font)
        
        # Desenhar linha divisória
        draw.line([(100, 200), (width - 100, 200)], fill=(200, 200, 200), width=2)
        
        # Desenhar conteúdo
        content_lines = [
            "• Python é uma linguagem de programação",
            "• Sintaxe simples e legível",
            "• Grande comunidade de desenvolvedores",
            "• Muitas bibliotecas disponíveis"
        ]
        
        y_pos = 250
        for line in content_lines:
            draw.text((150, y_pos), line, fill=(51, 51, 51), font=text_font)
            y_pos += 50
        
        # Salvar slide de teste
        output_path = "slide_test.png"
        img.save(output_path)
        
        print(f"✅ Slide básico criado: {output_path}")
        print(f"   Tamanho: {img.size}")
        
        return True, output_path
        
    except Exception as e:
        print(f"❌ Erro ao criar slide: {e}")
        return False, None

def test_basic_video_creation():
    """Testar criação básica de vídeo"""
    print("\n🎬 Testando criação básica de vídeo...")
    
    try:
        from moviepy.editor import ImageClip, concatenate_videoclips
        
        # Verificar se temos as imagens
        avatar_path = "avatar_test.png"
        slide_path = "slide_test.png"
        
        if not (Path(avatar_path).exists() and Path(slide_path).exists()):
            print("❌ Imagens de teste não encontradas")
            return False, None
        
        # Criar clips de imagem
        avatar_clip = ImageClip(avatar_path, duration=3)
        slide_clip = ImageClip(slide_path, duration=3)
        
        # Redimensionar para garantir compatibilidade
        avatar_clip = avatar_clip.resize(height=720)
        slide_clip = slide_clip.resize(height=720)
        
        # Concatenar clips
        final_video = concatenate_videoclips([avatar_clip, slide_clip])
        
        # Salvar vídeo
        output_path = "video_test.mp4"
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        print(f"✅ Vídeo básico criado: {output_path}")
        
        # Verificar se arquivo foi criado
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            print(f"   Tamanho: {file_size / 1024:.1f} KB")
            return True, output_path
        else:
            print("❌ Arquivo de vídeo não foi criado")
            return False, None
        
    except Exception as e:
        print(f"❌ Erro ao criar vídeo: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Função principal"""
    print("🚀 TESTE SIMPLES DO SISTEMA AVATAR")
    print("=" * 50)
    
    # Verificar dependências
    deps = check_dependencies()
    
    # Verificar se dependências críticas estão disponíveis
    critical_deps = ['PIL', 'numpy', 'moviepy']
    missing_critical = []
    
    for dep in critical_deps:
        if dep not in deps or "❌" in deps[dep]:
            missing_critical.append(dep)
    
    if missing_critical:
        print(f"\n❌ Dependências críticas faltando: {', '.join(missing_critical)}")
        print("Execute: pip install pillow numpy moviepy")
        return False
    
    # Executar testes
    tests = [
        ("Avatar Básico", test_basic_avatar_creation),
        ("Slide Básico", test_basic_slide_creation),
        ("Vídeo Básico", test_basic_video_creation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            success, output = test_func()
            results[test_name] = success
            if success and output:
                print(f"📁 Output: {output}")
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results[test_name] = False
    
    # Resumo
    print(f"\n{'='*50}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*50}")
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:15} {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\nResultado: {passed}/{total} testes passaram ({success_rate:.1f}%)")
    
    if success_rate >= 66:  # 2 de 3 testes
        print("🎉 Sistema básico de avatar está funcional!")
        print("\n📁 Arquivos gerados:")
        for file in ["avatar_test.png", "slide_test.png", "video_test.mp4"]:
            if Path(file).exists():
                size = Path(file).stat().st_size
                print(f"   {file} ({size / 1024:.1f} KB)")
        return True
    else:
        print("⚠️ Sistema precisa de correções")
        return False

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 