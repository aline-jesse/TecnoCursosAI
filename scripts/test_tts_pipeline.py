"""
Script de Teste - Pipeline TTS Bark
Testa todas as funcionalidades do sistema TTS com Bark e gTTS
"""

import asyncio
import time
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from services.tts_service import (
    tts_service, TTSConfig, TTSProvider, 
    generate_narration, generate_course_narration, test_tts_providers
)
from app.config import get_settings, validate_tts_config

# Configurações
settings = get_settings()

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"🎵 {title}")
    print('='*60)

def print_result(test_name: str, success: bool, details: str = ""):
    """Imprime resultado do teste"""
    status = "✅ SUCESSO" if success else "❌ FALHOU"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

async def test_basic_config():
    """Testa configurações básicas"""
    print_header("TESTE DE CONFIGURAÇÕES")
    
    # Validar configurações
    validation = validate_tts_config()
    print_result(
        "Validação de configurações",
        validation["valid"],
        f"Issues: {validation['issues']}" if validation['issues'] else "Todas válidas"
    )
    
    # Verificar providers disponíveis
    providers = tts_service.get_available_providers()
    print_result(
        "Providers disponíveis",
        len(providers) > 0,
        f"Providers: {', '.join(providers)}"
    )
    
    return validation["valid"]

async def test_gtts_basic():
    """Testa gTTS básico"""
    print_header("TESTE GTTS BÁSICO")
    
    try:
        config = TTSConfig(
            provider=TTSProvider.GTTS,
            language="pt"
        )
        
        result = await tts_service.generate_speech(
            "Este é um teste básico do Google TTS.",
            config,
            "test_gtts.mp3"
        )
        
        print_result(
            "Geração com gTTS",
            result.success,
            f"Arquivo: {result.audio_path}, Duração: {result.duration:.2f}s" if result.success else f"Erro: {result.error}"
        )
        
        return result.success
        
    except Exception as e:
        print_result("Geração com gTTS", False, f"Exceção: {e}")
        return False

async def test_bark_basic():
    """Testa Bark TTS básico"""
    print_header("TESTE BARK TTS BÁSICO")
    
    try:
        config = TTSConfig(
            provider=TTSProvider.BARK,
            voice="pt_speaker_0",
            language="pt"
        )
        
        result = await tts_service.generate_speech(
            "Este é um teste do Bark TTS. A qualidade deve ser superior ao Google TTS.",
            config,
            "test_bark.mp3"
        )
        
        print_result(
            "Geração com Bark",
            result.success,
            f"Arquivo: {result.audio_path}, Duração: {result.duration:.2f}s, Voz: {result.metadata.get('voice') if result.metadata else 'N/A'}" if result.success else f"Erro: {result.error}"
        )
        
        return result.success
        
    except Exception as e:
        print_result("Geração com Bark", False, f"Exceção: {e}")
        return False

async def test_auto_selection():
    """Testa seleção automática de provider"""
    print_header("TESTE SELEÇÃO AUTOMÁTICA")
    
    test_cases = [
        ("Texto curto", "Este é um texto curto para teste."),
        ("Texto médio", "Este é um texto médio para testar a seleção automática de provider. Deve ser suficiente para mostrar a diferença entre os providers disponíveis."),
        ("Texto longo", "Este é um texto muito longo para testar como o sistema escolhe automaticamente o melhor provider baseado no tamanho do conteúdo. " * 10)
    ]
    
    results = []
    
    for name, text in test_cases:
        try:
            config = TTSConfig(provider=TTSProvider.AUTO)
            result = await tts_service.generate_speech(text, config, f"test_auto_{name.lower().replace(' ', '_')}.mp3")
            
            print_result(
                f"Auto-seleção ({name})",
                result.success,
                f"Provider usado: {result.provider_used}, Duração: {result.duration:.2f}s" if result.success else f"Erro: {result.error}"
            )
            
            results.append(result.success)
            
        except Exception as e:
            print_result(f"Auto-seleção ({name})", False, f"Exceção: {e}")
            results.append(False)
    
    return all(results)

async def test_batch_generation():
    """Testa geração em lote"""
    print_header("TESTE GERAÇÃO EM LOTE")
    
    texts = [
        "Primeira parte do curso: Introdução.",
        "Segunda parte do curso: Desenvolvimento.",
        "Terceira parte do curso: Conclusão.",
        "Quarta parte do curso: Exercícios práticos."
    ]
    
    try:
        config = TTSConfig(provider=TTSProvider.AUTO)
        results = await tts_service.generate_batch_speech(texts, config)
        
        successful = sum(1 for r in results if r.success)
        total = len(results)
        
        print_result(
            "Geração em lote",
            successful == total,
            f"Sucessos: {successful}/{total}"
        )
        
        for i, result in enumerate(results):
            if result.success:
                print(f"    ✅ Texto {i+1}: {result.provider_used} - {result.duration:.2f}s")
            else:
                print(f"    ❌ Texto {i+1}: {result.error}")
        
        return successful == total
        
    except Exception as e:
        print_result("Geração em lote", False, f"Exceção: {e}")
        return False

async def test_course_narration():
    """Testa narração de curso completo"""
    print_header("TESTE NARRAÇÃO DE CURSO")
    
    course_sections = [
        {
            "title": "Introdução ao Python",
            "content": "Python é uma linguagem de programação de alto nível, interpretada e de propósito geral."
        },
        {
            "title": "Variáveis e Tipos de Dados",
            "content": "Em Python, podemos criar variáveis para armazenar diferentes tipos de dados como números, textos e listas."
        },
        {
            "title": "Estruturas de Controle",
            "content": "As estruturas de controle como if, for e while nos permitem controlar o fluxo de execução do programa."
        }
    ]
    
    try:
        results = await generate_course_narration(course_sections, voice="pt_speaker_0")
        
        successful = sum(1 for r in results if r.success)
        total = len(results)
        
        print_result(
            "Narração de curso",
            successful == total,
            f"Sucessos: {successful}/{total}"
        )
        
        for i, result in enumerate(results):
            if result.success:
                print(f"    ✅ Seção {i+1}: {result.provider_used} - {result.duration:.2f}s")
            else:
                print(f"    ❌ Seção {i+1}: {result.error}")
        
        return successful == total
        
    except Exception as e:
        print_result("Narração de curso", False, f"Exceção: {e}")
        return False

async def test_different_voices():
    """Testa diferentes vozes do Bark"""
    print_header("TESTE DIFERENTES VOZES")
    
    voices = ["pt_speaker_0", "pt_speaker_1", "pt_speaker_2"]
    text = "Este é um teste com diferentes vozes do Bark TTS."
    
    results = []
    
    for voice in voices:
        try:
            config = TTSConfig(
                provider=TTSProvider.BARK,
                voice=voice
            )
            
            result = await tts_service.generate_speech(text, config, f"test_voice_{voice}.mp3")
            
            print_result(
                f"Voz {voice}",
                result.success,
                f"Duração: {result.duration:.2f}s" if result.success else f"Erro: {result.error}"
            )
            
            results.append(result.success)
            
        except Exception as e:
            print_result(f"Voz {voice}", False, f"Exceção: {e}")
            results.append(False)
    
    return all(results)

async def test_performance():
    """Testa performance do sistema"""
    print_header("TESTE DE PERFORMANCE")
    
    text = "Este é um teste de performance para medir o tempo de geração de áudio."
    
    # Teste gTTS
    try:
        start_time = time.time()
        config = TTSConfig(provider=TTSProvider.GTTS)
        result_gtts = await tts_service.generate_speech(text, config, "perf_gtts.mp3")
        gtts_time = time.time() - start_time
        
        print_result(
            "Performance gTTS",
            result_gtts.success,
            f"Tempo: {gtts_time:.2f}s"
        )
    except Exception as e:
        gtts_time = 999
        print_result("Performance gTTS", False, f"Erro: {e}")
    
    # Teste Bark
    try:
        start_time = time.time()
        config = TTSConfig(provider=TTSProvider.BARK)
        result_bark = await tts_service.generate_speech(text, config, "perf_bark.mp3")
        bark_time = time.time() - start_time
        
        print_result(
            "Performance Bark",
            result_bark.success,
            f"Tempo: {bark_time:.2f}s"
        )
    except Exception as e:
        bark_time = 999
        print_result("Performance Bark", False, f"Erro: {e}")
    
    # Comparação
    if gtts_time < 999 and bark_time < 999:
        faster = "gTTS" if gtts_time < bark_time else "Bark"
        ratio = max(gtts_time, bark_time) / min(gtts_time, bark_time)
        print(f"    🏃 {faster} foi {ratio:.1f}x mais rápido")
    
    return True

async def test_cleanup():
    """Testa limpeza de arquivos temporários"""
    print_header("TESTE LIMPEZA")
    
    try:
        # Contar arquivos antes
        temp_files_before = len(list(tts_service.temp_dir.glob("*")))
        
        # Executar limpeza
        await tts_service.cleanup_temp_files(max_age_hours=0)  # Limpar tudo
        
        # Contar arquivos depois
        temp_files_after = len(list(tts_service.temp_dir.glob("*")))
        
        print_result(
            "Limpeza de arquivos",
            temp_files_after <= temp_files_before,
            f"Antes: {temp_files_before}, Depois: {temp_files_after}"
        )
        
        return True
        
    except Exception as e:
        print_result("Limpeza de arquivos", False, f"Exceção: {e}")
        return False

async def run_all_tests():
    """Executa todos os testes"""
    print_header("INICIANDO TESTES DO PIPELINE TTS BARK")
    
    start_time = time.time()
    
    tests = [
        ("Configurações", test_basic_config),
        ("gTTS Básico", test_gtts_basic),
        ("Bark Básico", test_bark_basic),
        ("Seleção Automática", test_auto_selection),
        ("Geração em Lote", test_batch_generation),
        ("Narração de Curso", test_course_narration),
        ("Diferentes Vozes", test_different_voices),
        ("Performance", test_performance),
        ("Limpeza", test_cleanup),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Executando: {test_name}")
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    total_time = time.time() - start_time
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   Sucessos: {successful}/{total}")
    print(f"   Taxa de sucesso: {(successful/total)*100:.1f}%")
    print(f"   Tempo total: {total_time:.2f}s")
    
    if successful == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Pipeline TTS está funcionando perfeitamente.")
    else:
        print(f"\n⚠️ {total - successful} testes falharam. Verifique as configurações e dependências.")
    
    return successful == total

if __name__ == "__main__":
    print("🚀 Iniciando testes do Pipeline TTS Bark...")
    
    # Verificar dependências básicas
    try:
        import torch
        import transformers
        print(f"✅ PyTorch {torch.__version__}")
        print(f"✅ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("   Execute: pip install torch transformers")
        sys.exit(1)
    
    # Executar testes
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testes interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1) 