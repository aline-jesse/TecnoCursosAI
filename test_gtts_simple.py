"""
Teste Simples - TTS com gTTS apenas
Verifica se o sistema TTS básico está funcionando sem dependências do Bark
"""

import asyncio
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Testa imports básicos"""
    try:
        print("🔍 Testando imports...")
        
        # Testar gTTS
        from gtts import gTTS
        print("✅ gTTS importado com sucesso")
        
        # Testar pydub
        try:
            import pydub
            print("✅ pydub disponível")
        except ImportError:
            print("⚠️ pydub não disponível (não é crítico)")
        
        # Testar configurações
        from app.config import get_settings, validate_tts_config
        print("✅ Configurações carregadas")
        
        # Testar validação
        validation = validate_tts_config()
        if validation["valid"]:
            print("✅ Configurações TTS válidas")
        else:
            print(f"⚠️ Problemas na configuração: {validation['issues']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_gtts_basic():
    """Testa gTTS básico"""
    try:
        print("\n🎵 Testando gTTS básico...")
        
        from gtts import gTTS
        import tempfile
        import os
        
        # Texto de teste
        text = "Este é um teste básico do Google TTS no TecnoCursos AI."
        
        # Criar TTS
        tts = gTTS(text=text, lang='pt', slow=False)
        
        # Salvar em arquivo temporário
        temp_dir = Path(tempfile.gettempdir())
        audio_file = temp_dir / "test_gtts_basic.mp3"
        
        tts.save(str(audio_file))
        
        # Verificar se arquivo foi criado
        if audio_file.exists():
            file_size = audio_file.stat().st_size
            print(f"✅ Áudio gerado: {audio_file}")
            print(f"   Tamanho: {file_size} bytes")
            
            # Limpar arquivo
            audio_file.unlink()
            print("✅ Arquivo temporário removido")
            
            return True
        else:
            print("❌ Arquivo de áudio não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste gTTS: {e}")
        return False

async def test_tts_service_gtts():
    """Testa serviço TTS apenas com gTTS"""
    try:
        print("\n🔧 Testando serviço TTS (somente gTTS)...")
        
        # Importar com fallback
        try:
            from services.tts_service import GTTSEngine, TTSConfig
            print("✅ Serviço TTS importado")
        except ImportError as e:
            print(f"❌ Erro ao importar serviço TTS: {e}")
            return False
        
        # Criar engine gTTS
        engine = GTTSEngine()
        
        # Configurar
        config = TTSConfig(
            language="pt",
            output_format="mp3"
        )
        
        # Gerar áudio
        text = "Teste do serviço TTS com Google TTS."
        temp_file = "test_service_gtts.mp3"
        
        result = await engine.generate_audio(text, config, temp_file)
        
        if result.success:
            print(f"✅ Áudio gerado pelo serviço")
            print(f"   Provider: {result.provider_used}")
            print(f"   Duração: {result.duration:.2f}s")
            
            # Limpar arquivo
            if Path(temp_file).exists():
                Path(temp_file).unlink()
                print("✅ Arquivo limpo")
            
            return True
        else:
            print(f"❌ Erro no serviço: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste do serviço: {e}")
        return False

def test_config():
    """Testa configurações"""
    try:
        print("\n⚙️ Testando configurações...")
        
        from app.config import get_settings, get_tts_config
        
        settings = get_settings()
        print(f"✅ Provider TTS: {getattr(settings, 'tts_provider', 'auto')}")
        print(f"✅ Idioma gTTS: {getattr(settings, 'gtts_language', 'pt')}")
        
        tts_config = get_tts_config()
        print(f"✅ Configuração TTS carregada: {len(tts_config)} seções")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

async def run_simple_tests():
    """Executa testes simples"""
    print("🚀 Iniciando testes simples TTS (apenas gTTS)")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("gTTS Básico", test_gtts_basic),
        ("Configurações", test_config),
        ("Serviço TTS", test_tts_service_gtts),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    successful = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            successful += 1
    
    total = len(results)
    print(f"\n🎯 Resultado: {successful}/{total} testes passaram")
    
    if successful == total:
        print("🎉 TODOS OS TESTES BÁSICOS PASSARAM!")
        print("\n📝 Próximos passos:")
        print("1. Instalar PyTorch para Bark TTS:")
        print("   pip install torch transformers")
        print("2. Executar teste completo:")
        print("   python test_tts_pipeline.py")
        print("3. Iniciar servidor:")
        print("   python app/main.py")
        print("4. Testar API TTS:")
        print("   curl http://localhost:8000/api/tts/status")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        print("\n🔧 Possíveis soluções:")
        print("1. Instalar dependências básicas:")
        print("   pip install gtts pydub")
        print("2. Verificar configurações em .env")
        print("3. Verificar logs para mais detalhes")
    
    return successful == total

if __name__ == "__main__":
    print("🎵 Teste Simples TTS - TecnoCursos AI")
    print("Testando apenas funcionalidades básicas com gTTS\n")
    
    # Verificar dependências críticas
    try:
        import gtts
        print(f"✅ gTTS versão: {gtts.__version__ if hasattr(gtts, '__version__') else 'desconhecida'}")
    except ImportError:
        print("❌ gTTS não instalado. Execute:")
        print("   pip install gtts")
        sys.exit(1)
    
    # Executar testes
    try:
        result = asyncio.run(run_simple_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1) 