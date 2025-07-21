#!/usr/bin/env python3
"""
Teste simples para a função concatenate_videos.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

def test_import():
    """Testa se a função pode ser importada."""
    try:
        from app.utils import concatenate_videos
        print("✅ Função concatenate_videos importada com sucesso!")
        print(f"📋 Nome da função: {concatenate_videos.__name__}")
        print(f"📝 Tem documentação: {'Sim' if concatenate_videos.__doc__ else 'Não'}")
        
        # Verificar se é chamável
        if callable(concatenate_videos):
            print("✅ Função é chamável")
        else:
            print("❌ Função não é chamável")
            
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_basic_usage():
    """Teste básico de uso da função."""
    try:
        from app.utils import concatenate_videos
        
        # Lista de vídeos fictícios para teste
        test_videos = [
            "videos/video1.mp4",  # Não existe
            "videos/video2.mp4",  # Não existe
            "videos/video3.mp4"   # Não existe
        ]
        
        output_path = "videos/teste_concatenacao.mp4"
        
        print("\n🧪 TESTE BÁSICO DE USO")
        print("-" * 40)
        print("📝 Testando com vídeos inexistentes (deve retornar erro)...")
        
        # Chamar a função (deve falhar graciosamente)
        result = concatenate_videos(test_videos, output_path)
        
        print("📊 Resultado do teste:")
        print(f"   Success: {result.get('success', 'N/A')}")
        print(f"   Error: {result.get('error', 'N/A')}")
        print(f"   Videos processed: {result.get('videos_processed', 'N/A')}")
        print(f"   Videos skipped: {result.get('videos_skipped', 'N/A')}")
        
        if not result.get('success', False):
            print("✅ Teste passou - função tratou erro corretamente")
            return True
        else:
            print("⚠️ Resultado inesperado - deveria ter falhado com vídeos inexistentes")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    print("🎬 TESTE DA FUNÇÃO CONCATENATE_VIDEOS")
    print("=" * 50)
    
    # Teste 1: Importação
    print("\n📦 TESTE 1: Importação da função")
    import_ok = test_import()
    
    if import_ok:
        # Teste 2: Uso básico
        print("\n📦 TESTE 2: Uso básico da função")
        usage_ok = test_basic_usage()
        
        if usage_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
        else:
            print("\n⚠️ Alguns testes falharam")
    else:
        print("\n❌ Não foi possível importar a função")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído") 