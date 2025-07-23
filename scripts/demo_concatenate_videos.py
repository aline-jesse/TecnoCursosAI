#!/usr/bin/env python3
"""
Demonstração da função concatenate_videos()
Este script mostra como usar a nova função para concatenar múltiplos vídeos.

Autor: TecnoCursos AI
Data: 2025
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(str(Path(__file__).parent))

from app.utils import concatenate_videos

def main():
    """
    Demonstração completa da função concatenate_videos.
    """
    
    print("🎬 DEMONSTRAÇÃO: CONCATENAÇÃO DE VÍDEOS")
    print("="*60)
    
    # === EXEMPLO 1: Concatenação básica ===
    print("\n📹 EXEMPLO 1: Concatenação Básica")
    print("-" * 40)
    
    # Lista de vídeos para concatenar (ajuste os caminhos conforme necessário)
    video_list_basic = [
        "videos/demo_curso_python.mp4",
        "videos/demo_intro_tecnica.mp4", 
        "videos/demo_relatorio_exec.mp4"
    ]
    
    # Caminho de saída
    output_basic = "videos/apresentacao_concatenada_demo.mp4"
    
    print(f"📝 Vídeos a concatenar:")
    for i, video in enumerate(video_list_basic, 1):
        status = "✅" if os.path.exists(video) else "❌ (não encontrado)"
        print(f"   {i}. {video} {status}")
    
    print(f"\n📁 Arquivo de saída: {output_basic}")
    
    # Executar concatenação
    try:
        result = concatenate_videos(video_list_basic, output_basic)
        
        if result["success"]:
            print("\n🎉 CONCATENAÇÃO BEM-SUCEDIDA!")
            print(f"   📹 Vídeos processados: {result['videos_processed']}")
            print(f"   ⏱️ Duração total: {result['total_duration']:.2f}s")
            print(f"   💾 Tamanho: {result['file_size'] / (1024*1024):.2f} MB")
            print(f"   🕒 Tempo de processamento: {result['processing_time']:.2f}s")
            print(f"   📁 Arquivo criado: {result['output_path']}")
        else:
            print(f"\n❌ ERRO: {result['error']}")
            
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {str(e)}")
    
    # === EXEMPLO 2: Concatenação com vídeos de teste ===
    print("\n\n📹 EXEMPLO 2: Criando Vídeos de Teste e Concatenando")
    print("-" * 50)
    
    # Criar alguns vídeos de teste se MoviePy estiver disponível
    try:
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
        
        print("🔧 Criando vídeos de teste...")
        
        # Criar pasta para vídeos de teste
        test_videos_dir = "temp_test_videos"
        os.makedirs(test_videos_dir, exist_ok=True)
        
        test_videos = []
        
        # Criar 3 vídeos de teste simples
        for i in range(1, 4):
            print(f"   📝 Criando vídeo teste {i}/3...")
            
            # Clip de cor de fundo
            color_clip = ColorClip(
                size=(640, 480), 
                color=(50*i, 100, 150), 
                duration=3.0
            )
            
            # Texto sobreposto
            text_clip = TextClip(
                f"Vídeo Teste {i}\nDuração: 3 segundos",
                fontsize=50,
                color='white',
                font='Arial'
            ).set_position('center').set_duration(3.0)
            
            # Combinar
            final_clip = CompositeVideoClip([color_clip, text_clip])
            
            # Salvar
            test_video_path = f"{test_videos_dir}/teste_{i}.mp4"
            final_clip.write_videofile(test_video_path, verbose=False, logger=None)
            
            test_videos.append(test_video_path)
            
            # Limpar recursos
            color_clip.close()
            text_clip.close()
            final_clip.close()
            
            print(f"   ✅ Vídeo criado: {test_video_path}")
        
        # Concatenar os vídeos de teste
        output_test = f"{test_videos_dir}/concatenado_final.mp4"
        
        print(f"\n🔧 Concatenando {len(test_videos)} vídeos de teste...")
        
        result_test = concatenate_videos(test_videos, output_test)
        
        if result_test["success"]:
            print("\n🎉 CONCATENAÇÃO DE TESTE BEM-SUCEDIDA!")
            print(f"   📹 Vídeos processados: {result_test['videos_processed']}")
            print(f"   ⏱️ Duração total: {result_test['total_duration']:.2f}s")
            print(f"   💾 Tamanho: {result_test['file_size'] / (1024*1024):.2f} MB")
            print(f"   📁 Arquivo criado: {result_test['output_path']}")
            
            # Limpeza opcional
            print(f"\n🧹 Para limpar os arquivos de teste, delete a pasta: {test_videos_dir}")
        else:
            print(f"\n❌ ERRO NO TESTE: {result_test['error']}")
            
    except ImportError:
        print("⚠️ MoviePy não disponível - pulando criação de vídeos de teste")
    except Exception as e:
        print(f"⚠️ Erro ao criar vídeos de teste: {str(e)}")
    
    # === EXEMPLO 3: Tratamento de erros ===
    print("\n\n📹 EXEMPLO 3: Demonstrando Tratamento de Erros")
    print("-" * 50)
    
    # Lista com vídeos que não existem
    video_list_error = [
        "videos/inexistente1.mp4",
        "videos/inexistente2.mp4",
        "videos/arquivo_corrompido.mp4"
    ]
    
    output_error = "videos/teste_erro.mp4"
    
    print("🔧 Tentando concatenar vídeos inexistentes...")
    
    result_error = concatenate_videos(video_list_error, output_error)
    
    if not result_error["success"]:
        print("✅ Tratamento de erro funcionou corretamente!")
        print(f"   ❌ Erro detectado: {result_error['error']}")
        print(f"   📊 Vídeos processados: {result_error['videos_processed']}")
        print(f"   📊 Vídeos ignorados: {result_error['videos_skipped']}")
        print(f"   📋 Detalhes: {len(result_error['details']['invalid_videos'])} vídeos inválidos")
    
    print("\n" + "="*60)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print("="*60)
    print("\n💡 Como usar a função concatenate_videos:")
    print("   1. Prepare uma lista com caminhos dos vídeos")
    print("   2. Defina o caminho de saída do vídeo final") 
    print("   3. Chame: result = concatenate_videos(lista_videos, saida)")
    print("   4. Verifique result['success'] para confirmar sucesso")
    print("\n📚 Consulte a documentação da função para mais detalhes!")

if __name__ == "__main__":
    main() 