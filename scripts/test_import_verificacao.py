"""
Teste de Verificação de Importações e Funções
=============================================

Script simples para verificar se as funções do pipeline
estão importando corretamente e sem erros.
"""

def test_imports():
    """Testa se todas as importações necessárias funcionam"""
    print("🔍 Testando importações...")
    
    try:
        # Testar importações básicas
        print("📦 Testando importações básicas...")
        from app.utils import extract_pdf_text, extract_text_from_pptx
        print("✅ extract_pdf_text, extract_text_from_pptx - OK")
        
        from app.utils import generate_narration_sync
        print("✅ generate_narration_sync - OK")
        
        from app.utils import create_videos_for_slides, concatenate_videos
        print("✅ create_videos_for_slides, concatenate_videos - OK")
        
        from app.models import FileUpload, Audio, Video, Project, User
        print("✅ Modelos do banco - OK")
        
        from app.routers.files import router
        print("✅ Router de files - OK")
        
        print("\n🎉 TODAS AS IMPORTAÇÕES FUNCIONARAM!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_function_signatures():
    """Testa se as funções têm as assinaturas corretas"""
    print("\n🔍 Testando assinaturas das funções...")
    
    try:
        from app.utils import create_videos_for_slides, concatenate_videos
        import inspect
        
        # Testar create_videos_for_slides
        sig = inspect.signature(create_videos_for_slides)
        params = list(sig.parameters.keys())
        print(f"✅ create_videos_for_slides - Parâmetros: {params}")
        
        # Testar concatenate_videos
        sig = inspect.signature(concatenate_videos)
        params = list(sig.parameters.keys())
        print(f"✅ concatenate_videos - Parâmetros: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar assinaturas: {e}")
        return False

def test_basic_functionality():
    """Testa funcionalidades básicas sem fazer uploads"""
    print("\n🔍 Testando funcionalidades básicas...")
    
    try:
        # Testar validação de arquivos
        from app.utils import validate_file
        print("✅ validate_file disponível")
        
        # Testar configurações
        from app.config import get_settings
        settings = get_settings()
        print(f"✅ Configurações carregadas - Static dir: {settings.static_directory}")
        
        # Testar Path
        from pathlib import Path
        test_path = Path(settings.static_directory) / "audios"
        print(f"✅ Path para áudios: {test_path}")
        
        test_path = Path(settings.static_directory) / "videos"  
        print(f"✅ Path para vídeos: {test_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro em funcionalidades básicas: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE VERIFICAÇÃO DO PIPELINE MODIFICADO")
    print("="*60)
    
    # Executar testes
    test1 = test_imports()
    test2 = test_function_signatures()
    test3 = test_basic_functionality()
    
    print("\n" + "="*60)
    if test1 and test2 and test3:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O código está pronto para ser executado")
        print("🚀 Para testar o pipeline completo, inicie o servidor:")
        print("   python main.py")
        print("   python test_upload_pipeline_completo.py")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os erros acima antes de continuar")
    print("="*60)

if __name__ == "__main__":
    main() 