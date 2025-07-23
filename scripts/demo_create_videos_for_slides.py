#!/usr/bin/env python3
"""
🎬 DEMONSTRAÇÃO: create_videos_for_slides
==========================================

Este script demonstra o uso da nova função create_videos_for_slides()
que foi implementada no arquivo app/utils.py. Esta função permite criar
múltiplos vídeos automaticamente a partir de listas de textos e áudios.

Autor: Sistema TecnoCursos AI
Data: 2025
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório principal ao path do Python
sys.path.append(str(Path(__file__).parent))

try:
    from app.utils import create_videos_for_slides, batch_create_videos_info, validate_batch_creation_params
    print("✅ Funções importadas com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar funções: {e}")
    print("🔧 Verifique se as dependências estão instaladas: pip install moviepy pillow")
    sys.exit(1)

def demo_create_videos_for_slides():
    """
    Demonstra o uso da função create_videos_for_slides com dados de exemplo.
    
    Esta função cria um exemplo prático de como usar a nova funcionalidade
    para gerar múltiplos vídeos a partir de listas de textos e áudios.
    """
    print("\n" + "="*60)
    print("🎬 DEMONSTRAÇÃO: create_videos_for_slides")
    print("="*60)
    
    # Dados de exemplo para demonstração
    slides_text_list = [
        "Bem-vindos ao TecnoCursos AI! Nesta aula vamos aprender sobre inteligência artificial e suas aplicações no mundo moderno. A IA está transformando diversos setores da economia.",
        
        "Python é uma das linguagens mais populares para machine learning. Suas bibliotecas como TensorFlow, PyTorch e Scikit-learn facilitam o desenvolvimento de modelos de IA.",
        
        "Obrigado por assistir esta apresentação! Continue estudando e praticando para se tornar um especialista em tecnologia. O futuro é dos que se preparam hoje!",
    ]
    
    # Caminhos de exemplo para arquivos de áudio (você precisaria ter estes arquivos)
    audios_path_list = [
        "app/static/audios/intro_tecnica.wav",    # Áudio para slide 1
        "app/static/audios/curso_python.wav",     # Áudio para slide 2  
        "app/static/audios/relatorio_exec.wav",   # Áudio para slide 3
    ]
    
    # Pasta onde os vídeos serão salvos
    output_folder = "videos/demo_slides_output"
    
    print(f"📝 Preparando para processar {len(slides_text_list)} slides:")
    for i, (text, audio) in enumerate(zip(slides_text_list, audios_path_list), 1):
        print(f"   {i}. Texto: {text[:50]}...")
        print(f"      Áudio: {audio}")
    
    print(f"\n📁 Pasta de output: {output_folder}")
    
    # Verificar se os arquivos de áudio existem
    print("\n🔍 Verificando arquivos de áudio...")
    missing_files = []
    for audio_path in audios_path_list:
        if os.path.exists(audio_path):
            print(f"   ✅ {audio_path}")
        else:
            print(f"   ❌ {audio_path} (não encontrado)")
            missing_files.append(audio_path)
    
    if missing_files:
        print(f"\n⚠️ AVISO: {len(missing_files)} arquivos de áudio não foram encontrados.")
        print("💡 Para executar a demonstração completa, certifique-se de ter os arquivos de áudio.")
        print("🎵 Você pode usar arquivos de áudio existentes ou gerar novos com TTS.")
        
        # Pergunta se o usuário quer continuar mesmo assim
        choice = input("\n❓ Deseja continuar mesmo assim? (s/n): ").lower()
        if choice != 's':
            print("❌ Demonstração cancelada pelo usuário.")
            return
    
    print("\n📊 Calculando informações de processamento...")
    
    # Obter informações sobre o processamento em lote
    batch_info = batch_create_videos_info(
        slides_count=len(slides_text_list),
        template="modern",
        resolution="hd"
    )
    
    print(f"⏱️ Tempo estimado: {batch_info['estimated_time_minutes']} minutos")
    print(f"💾 Espaço estimado: {batch_info['estimated_disk_space_mb']} MB")
    print(f"🧠 RAM recomendada: {batch_info['recommended_memory_mb']} MB")
    
    print("\n💡 Dicas de otimização:")
    for tip in batch_info['processing_tips']:
        print(f"   {tip}")
    
    # Validar parâmetros antes do processamento
    print("\n🔍 Validando parâmetros...")
    validation_result = validate_batch_creation_params(
        slides_text_list=slides_text_list,
        audios_path_list=audios_path_list,
        output_folder=output_folder
    )
    
    if validation_result['errors']:
        print("❌ Erros encontrados:")
        for error in validation_result['errors']:
            print(f"   • {error}")
    
    if validation_result['warnings']:
        print("⚠️ Avisos:")
        for warning in validation_result['warnings']:
            print(f"   • {warning}")
    
    print(f"\n📋 Resumo da validação:")
    summary = validation_result['summary']
    print(f"   📄 Total de slides: {summary['total_slides']}")
    print(f"   🎵 Total de áudios: {summary['total_audios']}")
    print(f"   ❌ Erros: {summary['errors_count']}")
    print(f"   ⚠️ Avisos: {summary['warnings_count']}")
    
    # Decidir se continuar com o processamento
    if not validation_result['is_valid']:
        print("\n❌ Não é possível continuar devido aos erros de validação.")
        return
    
    print("\n🚀 Iniciando processamento dos vídeos...")
    
    try:
        # Executar a função principal
        generated_videos = create_videos_for_slides(
            slides_text_list=slides_text_list,
            audios_path_list=audios_path_list,
            output_folder=output_folder,
            template="modern",        # Template moderno e profissional
            resolution="hd",          # Resolução HD (720p)
            animations=True,          # Ativar animações
            background_style="gradient"  # Fundo gradiente
        )
        
        # Exibir resultados
        print(f"\n🎉 Processamento concluído com sucesso!")
        print(f"✅ {len(generated_videos)} vídeos foram criados:")
        
        total_size = 0
        for i, video_path in enumerate(generated_videos, 1):
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                total_size += file_size
                size_mb = file_size / 1024 / 1024
                print(f"   {i}. {os.path.basename(video_path)} ({size_mb:.2f} MB)")
            else:
                print(f"   {i}. {os.path.basename(video_path)} (arquivo não encontrado)")
        
        print(f"\n💾 Tamanho total: {total_size / 1024 / 1024:.2f} MB")
        print(f"📁 Pasta: {output_folder}")
        
    except Exception as e:
        print(f"\n❌ Erro durante o processamento: {e}")
        print("\n💡 Dicas para resolver:")
        print("1. Verifique se todos os arquivos de áudio existem")
        print("2. Certifique-se de ter permissões de escrita na pasta de output")
        print("3. Instale as dependências: pip install moviepy pillow")
        print("4. Verifique se há espaço suficiente em disco")

def create_sample_audio_files():
    """
    Cria arquivos de áudio de exemplo usando TTS para a demonstração.
    
    Esta função pode ser usada para gerar os arquivos de áudio necessários
    para a demonstração caso eles não existam.
    """
    print("\n🎵 Criando arquivos de áudio de exemplo...")
    
    try:
        from app.utils import create_tts_audio_file
        
        # Textos para gerar áudios
        audio_texts = [
            "Bem-vindos ao TecnoCursos AI! Hoje vamos aprender sobre inteligência artificial.",
            "Python é uma linguagem muito popular para machine learning e ciência de dados.",
            "Obrigado por assistir! Continue estudando e praticando para se tornar um especialista."
        ]
        
        # Caminhos dos arquivos de áudio
        audio_paths = [
            "app/static/audios/demo_slide_1.wav",
            "app/static/audios/demo_slide_2.wav", 
            "app/static/audios/demo_slide_3.wav"
        ]
        
        # Criar pasta de áudios se não existir
        os.makedirs("app/static/audios", exist_ok=True)
        
        # Gerar cada arquivo de áudio
        for i, (text, path) in enumerate(zip(audio_texts, audio_paths), 1):
            print(f"   🎤 Gerando áudio {i}/3: {os.path.basename(path)}")
            
            # Usar TTS para criar arquivo de áudio
            result = create_tts_audio_file(
                text=text,
                output_path=path,
                provider="gtts",
                language="pt-br"
            )
            
            if result.get('success'):
                print(f"   ✅ Criado: {path}")
            else:
                print(f"   ❌ Erro: {result.get('error', 'Desconhecido')}")
        
        print("✅ Arquivos de áudio de exemplo criados!")
        return audio_paths
        
    except ImportError:
        print("⚠️ TTS não disponível - usando arquivos existentes")
        return None
    except Exception as e:
        print(f"❌ Erro ao criar arquivos de áudio: {e}")
        return None

def main():
    """
    Função principal que executa a demonstração completa.
    """
    print("🎬 DEMONSTRAÇÃO: create_videos_for_slides")
    print("==========================================")
    print("Esta demonstração mostra como usar a nova função para criar")
    print("múltiplos vídeos automaticamente a partir de textos e áudios.")
    
    # Verificar se os arquivos de áudio existem
    audio_files = [
        "app/static/audios/intro_tecnica.wav",
        "app/static/audios/curso_python.wav", 
        "app/static/audios/relatorio_exec.wav"
    ]
    
    missing_count = sum(1 for f in audio_files if not os.path.exists(f))
    
    if missing_count > 0:
        print(f"\n⚠️ {missing_count} arquivos de áudio não encontrados.")
        choice = input("🎵 Deseja criar arquivos de exemplo com TTS? (s/n): ").lower()
        
        if choice == 's':
            created_files = create_sample_audio_files()
            if created_files:
                print("✅ Arquivos criados! Continuando com a demonstração...")
            else:
                print("❌ Não foi possível criar arquivos. Usando demonstração limitada.")
    
    # Executar demonstração principal
    demo_create_videos_for_slides()
    
    print("\n" + "="*60)
    print("📚 INFORMAÇÕES ADICIONAIS")
    print("="*60)
    print("📖 Função implementada: create_videos_for_slides()")
    print("📁 Localização: app/utils.py")
    print("🔧 Dependências: moviepy, pillow")
    
    print("\n💡 Exemplo de uso programático:")
    print("```python")
    print("from app.utils import create_videos_for_slides")
    print("")
    print("videos = create_videos_for_slides(")
    print("    slides_text_list=['Texto 1', 'Texto 2'],")
    print("    audios_path_list=['audio1.wav', 'audio2.wav'],")
    print("    output_folder='meus_videos',")
    print("    template='modern',")
    print("    resolution='hd'")
    print(")")
    print("```")
    
    print(f"\n🏁 Demonstração concluída!")

if __name__ == "__main__":
    main() 