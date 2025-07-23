"""
Demo Básico - Gerador de Avatar com MoviePy
Versão simplificada que demonstra as funcionalidades principais
"""

import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip
    MOVIEPY_OK = True
except ImportError:
    print("❌ MoviePy não está disponível. Execute: pip install moviepy==1.0.3")
    MOVIEPY_OK = False

def criar_avatar_simples(width=400, height=600, cor_pele="#fdbcb4", cor_camisa="#4a90e2"):
    """Cria um avatar simples usando PIL"""
    
    # Criar imagem
    avatar = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(avatar)
    
    # Cabeça (círculo)
    head_center = (width // 2, height // 3)
    head_radius = 80
    
    # Desenhar cabeça
    draw.ellipse(
        [head_center[0] - head_radius, head_center[1] - head_radius,
         head_center[0] + head_radius, head_center[1] + head_radius],
        fill=cor_pele,
        outline="#d4a574",
        width=2
    )
    
    # Corpo (retângulo)
    body_top = head_center[1] + head_radius - 20
    body_width = 120
    body_height = 200
    
    draw.rectangle(
        [head_center[0] - body_width//2, body_top,
         head_center[0] + body_width//2, body_top + body_height],
        fill=cor_camisa,
        outline="#2c3e50",
        width=2
    )
    
    # Cabelo
    hair_points = [
        (head_center[0] - head_radius + 10, head_center[1] - head_radius + 20),
        (head_center[0], head_center[1] - head_radius - 10),
        (head_center[0] + head_radius - 10, head_center[1] - head_radius + 20)
    ]
    draw.polygon(hair_points, fill="#8b4513")
    
    # Olhos
    eye_y = head_center[1] - 20
    left_eye = (head_center[0] - 25, eye_y)
    right_eye = (head_center[0] + 25, eye_y)
    
    # Desenhar olhos
    for eye_pos in [left_eye, right_eye]:
        # Branco do olho
        draw.ellipse([eye_pos[0] - 8, eye_pos[1] - 6,
                     eye_pos[0] + 8, eye_pos[1] + 6],
                    fill="white", outline="black")
        # Pupila
        draw.ellipse([eye_pos[0] - 3, eye_pos[1] - 3,
                     eye_pos[0] + 3, eye_pos[1] + 3],
                    fill="black")
    
    # Nariz
    nose_center = (head_center[0], head_center[1] + 5)
    draw.line([nose_center[0], nose_center[1], 
              nose_center[0], nose_center[1] + 10], 
             fill="#d4a574", width=2)
    
    # Boca
    mouth_center = (head_center[0], head_center[1] + 30)
    draw.arc([mouth_center[0] - 15, mouth_center[1] - 5,
             mouth_center[0] + 15, mouth_center[1] + 10],
            0, 180, fill="black", width=2)
    
    return avatar

def criar_slide_simples(titulo, conteudo, width=1280, height=720):
    """Cria um slide simples"""
    
    # Criar slide
    slide = Image.new('RGB', (width, height), "#ffffff")
    draw = ImageDraw.Draw(slide)
    
    try:
        # Tentar carregar fonte
        font_titulo = ImageFont.truetype("arial.ttf", 36)
        font_conteudo = ImageFont.truetype("arial.ttf", 24)
    except:
        # Usar fonte padrão se não encontrar arial
        font_titulo = ImageFont.load_default()
        font_conteudo = ImageFont.load_default()
    
    # Área de conteúdo (lado direito)
    content_x = width // 2 + 50
    content_width = width // 2 - 100
    
    # Título
    draw.text((content_x, 100), titulo, font=font_titulo, fill="#2c3e50")
    
    # Conteúdo (quebrar em linhas)
    words = conteudo.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font_conteudo)
        if bbox[2] - bbox[0] <= content_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Desenhar linhas de conteúdo
    y_pos = 180
    for line in lines[:8]:  # Máximo 8 linhas
        draw.text((content_x, y_pos), line, font=font_conteudo, fill="#34495e")
        y_pos += 40
    
    # Linha de separação
    draw.line([(content_x - 30, 80), (content_x - 30, height - 80)], 
             fill="#3498db", width=3)
    
    return slide

def demo_basico():
    """Demonstração básica sem TTS"""
    
    print("🎬 Demo Básico - Gerador de Avatar")
    print("=" * 40)
    
    if not MOVIEPY_OK:
        return
    
    try:
        # Criar diretório temporário
        temp_dir = Path(tempfile.gettempdir()) / "demo_avatar"
        temp_dir.mkdir(exist_ok=True)
        
        print("🎭 Criando avatar...")
        
        # Criar avatar
        avatar = criar_avatar_simples()
        avatar_path = temp_dir / "avatar.png"
        avatar.save(str(avatar_path))
        
        print("📄 Criando slide...")
        
        # Criar slide
        slide = criar_slide_simples(
            "Bem-vindos ao TecnoCursos AI",
            "Esta é uma demonstração do nosso gerador de vídeos com avatar virtual. "
            "O sistema combina slides educacionais com um apresentador animado para "
            "criar experiências de aprendizado envolventes e profissionais."
        )
        slide_path = temp_dir / "slide.png"
        slide.save(str(slide_path))
        
        print("🎬 Criando vídeo...")
        
        # Criar clips
        duracao = 5  # 5 segundos
        
        # Slide como fundo
        slide_clip = ImageClip(str(slide_path), duration=duracao)
        
        # Avatar no lado esquerdo
        avatar_clip = ImageClip(str(avatar_path), duration=duracao)
        avatar_clip = avatar_clip.set_position((50, 60))  # Posição x, y
        
        # Combinar clips
        video_final = CompositeVideoClip([slide_clip, avatar_clip])
        
        # Caminho de saída
        output_path = "./demo_avatar_basico.mp4"
        
        print("💾 Exportando vídeo...")
        
        # Exportar vídeo
        video_final.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Limpar
        video_final.close()
        
        print(f"✅ Demo concluído!")
        print(f"📁 Arquivo: {os.path.abspath(output_path)}")
        print(f"⏱️  Duração: {duracao} segundos")
        print(f"📏 Resolução: 1280x720")
        
        # Verificar arquivo
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"💾 Tamanho: {file_size / (1024*1024):.1f} MB")
            print("🎥 Abra o arquivo para ver o resultado!")
        else:
            print("⚠️  Arquivo não foi criado")
        
    except Exception as e:
        print(f"❌ Erro na criação do demo: {e}")

def demo_multiplos_estilos():
    """Demo com diferentes estilos de avatar"""
    
    print("\n🎨 Demo - Múltiplos Estilos de Avatar")
    print("=" * 40)
    
    if not MOVIEPY_OK:
        return
    
    estilos = [
        {"nome": "Profissional", "pele": "#fdbcb4", "camisa": "#2c3e50"},
        {"nome": "Amigável", "pele": "#f4c2a1", "camisa": "#e74c3c"},
        {"nome": "Professor", "pele": "#d4a574", "camisa": "#27ae60"},
        {"nome": "Minimalista", "pele": "#e8d5b7", "camisa": "#95a5a6"}
    ]
    
    try:
        temp_dir = Path(tempfile.gettempdir()) / "demo_estilos"
        temp_dir.mkdir(exist_ok=True)
        
        for i, estilo in enumerate(estilos):
            print(f"🎭 Criando avatar {estilo['nome']}...")
            
            # Criar avatar com cores específicas
            avatar = criar_avatar_simples(
                cor_pele=estilo['pele'],
                cor_camisa=estilo['camisa']
            )
            
            # Criar slide
            slide = criar_slide_simples(
                f"Avatar {estilo['nome']}",
                f"Este é o estilo {estilo['nome'].lower()} do nosso avatar virtual. "
                f"Cada estilo tem cores e características específicas para diferentes "
                f"tipos de conteúdo educacional."
            )
            
            # Salvar imagens
            avatar_path = temp_dir / f"avatar_{i}.png"
            slide_path = temp_dir / f"slide_{i}.png"
            avatar.save(str(avatar_path))
            slide.save(str(slide_path))
            
            # Criar vídeo individual
            slide_clip = ImageClip(str(slide_path), duration=3)
            avatar_clip = ImageClip(str(avatar_path), duration=3)
            avatar_clip = avatar_clip.set_position((50, 60))
            
            video_clip = CompositeVideoClip([slide_clip, avatar_clip])
            
            output_path = f"./demo_avatar_{estilo['nome'].lower()}.mp4"
            
            video_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            video_clip.close()
            
            print(f"   ✅ {estilo['nome']}: {output_path}")
        
        print("🎉 Todos os estilos criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na criação dos estilos: {e}")

def verificar_sistema():
    """Verifica se o sistema está pronto"""
    
    print("🔍 Verificação do Sistema")
    print("=" * 25)
    
    dependencias = [
        ("PIL", "Pillow"),
        ("numpy", "numpy"),
        ("moviepy", "moviepy")
    ]
    
    todas_ok = True
    
    for modulo, nome in dependencias:
        try:
            __import__(modulo)
            print(f"   ✅ {nome}")
        except ImportError:
            print(f"   ❌ {nome} - FALTANDO")
            todas_ok = False
    
    if todas_ok:
        print("✅ Sistema pronto para demonstração!")
        return True
    else:
        print("\n⚠️  Instale as dependências:")
        print("pip install pillow numpy moviepy==1.0.3")
        return False

def main():
    """Função principal"""
    
    print("🚀 TecnoCursos AI - Demo do Gerador de Avatar")
    print("=" * 50)
    
    # Verificar sistema
    if not verificar_sistema():
        return
    
    print("\n")
    
    # Executar demos
    demo_basico()
    demo_multiplos_estilos()
    
    print("\n" + "=" * 50)
    print("🎬 Demonstrações concluídas!")
    print("📁 Verifique os arquivos .mp4 gerados")
    print("🎥 Cada vídeo mostra um estilo diferente de avatar")

if __name__ == "__main__":
    main() 