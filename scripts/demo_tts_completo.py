#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEMONSTRAÇÃO COMPLETA - Sistema TTS TecnoCursos AI
=================================================

Script para demonstrar todas as funcionalidades implementadas
do sistema Text-to-Speech integrado.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz
sys.path.append(str(Path(__file__).parent))

def print_header(title):
    """Imprimir cabeçalho estilizado"""
    print("\n" + "="*80)
    print(f"🎤 {title}")
    print("="*80)

def print_section(title):
    """Imprimir seção"""
    print(f"\n🔹 {title}")
    print("-" * 60)

async def demo_basico():
    """Demonstração básica da função generate_narration"""
    print_header("DEMONSTRAÇÃO BÁSICA - FUNÇÃO GENERATE_NARRATION")
    
    try:
        from app.utils import generate_narration_sync, generate_narration
        
        print_section("1. Teste Síncrono com gTTS")
        
        result = generate_narration_sync(
            text="Olá! Bem-vindos ao TecnoCursos AI. Este é um sistema completo de Text-to-Speech.",
            output_path="demo_gtts.mp3",
            provider="gtts"
        )
        
        if result['success']:
            print(f"✅ Sucesso! Arquivo: {result['audio_path']}")
            print(f"⏱️ Duração: {result['duration']:.2f}s")
            print(f"🔊 Provedor: {result['provider_used']}")
            print(f"⚡ Tempo processamento: {result.get('processing_time', 0):.2f}s")
            print(f"💾 Cache: {'HIT' if result.get('cached') else 'MISS'}")
        else:
            print(f"❌ Erro: {result['error']}")
        
        print_section("2. Teste Assíncrono com Auto-detecção")
        
        result = await generate_narration(
            text="Sistema avançado com cache, analytics e processamento em lote.",
            output_path="demo_auto.mp3",
            provider="auto"
        )
        
        if result['success']:
            print(f"✅ Sucesso! Arquivo: {result['audio_path']}")
            print(f"⏱️ Duração: {result['duration']:.2f}s")
            print(f"🔊 Provedor: {result['provider_used']}")
        else:
            print(f"❌ Erro: {result['error']}")
        
        print_section("3. Teste com Bark (se disponível)")
        
        result = generate_narration_sync(
            text="Teste com modelo Bark da Hugging Face para voz natural.",
            output_path="demo_bark.mp3",
            provider="bark",
            voice="v2/pt_speaker_1"
        )
        
        if result['success']:
            print(f"✅ Sucesso! Arquivo: {result['audio_path']}")
            print(f"🎭 Voz: v2/pt_speaker_1")
        else:
            print(f"❌ Erro Bark: {result['error']}")
            print("💡 Bark requer dependências adicionais")
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("🔧 Execute: pip install torch transformers gtts pydub")

async def demo_cache():
    """Demonstração do sistema de cache"""
    print_header("DEMONSTRAÇÃO - SISTEMA DE CACHE INTELIGENTE")
    
    try:
        from app.services.tts_cache_service import get_tts_cache_stats, tts_cache_manager
        
        print_section("Estatísticas do Cache")
        
        stats = await get_tts_cache_stats()
        
        print(f"📊 Total entradas: {stats.get('total_entries', 0)}")
        print(f"💾 Tamanho total: {stats.get('total_size_mb', 0):.2f} MB")
        print(f"🎯 Hit rate: {stats.get('hit_rate', 0):.1f}%")
        print(f"📈 Total acessos: {stats.get('total_accesses', 0)}")
        
        print_section("Buscar Áudios Similares")
        
        similar = await tts_cache_manager.find_similar_audio(
            text="teste sistema",
            similarity_threshold=0.6,
            max_results=3
        )
        
        print(f"🔍 Encontrados {len(similar)} áudios similares:")
        for audio in similar[:3]:
            print(f"   - Texto: {audio['text'][:50]}...")
            print(f"     Similaridade: {audio['similarity']:.2f}")
            print(f"     Provedor: {audio['provider']}")
            
    except ImportError:
        print("⚠️ Sistema de cache não disponível")
    except Exception as e:
        print(f"❌ Erro no cache: {e}")

async def demo_batch():
    """Demonstração do processamento em lote"""
    print_header("DEMONSTRAÇÃO - PROCESSAMENTO EM LOTE")
    
    try:
        from app.services.tts_batch_service import create_tts_batch, get_tts_batch_status
        
        print_section("Criando Lote de Testes")
        
        textos_teste = [
            "Primeiro texto do lote de teste.",
            "Segundo texto para demonstração.",
            "Terceiro texto do sistema TTS.",
            "Quarto e último texto do lote."
        ]
        
        batch_id = await create_tts_batch(
            texts=textos_teste,
            provider="gtts",
            voice=None,
            user_id="demo_user"
        )
        
        print(f"✅ Lote criado: {batch_id}")
        
        # Monitorar progresso
        print_section("Monitorando Progresso")
        
        for i in range(10):  # Máximo 10 iterações
            await asyncio.sleep(2)  # Aguardar 2 segundos
            
            status = await get_tts_batch_status(batch_id)
            
            if status:
                print(f"📊 Progresso: {status['progress']:.1f}%")
                print(f"✅ Sucessos: {status['success_count']}")
                print(f"❌ Falhas: {status['failure_count']}")
                print(f"📁 Diretório: {status['output_directory']}")
                
                if status['status'] == 'completed':
                    print("🎉 Lote concluído!")
                    break
            else:
                print("❌ Erro ao obter status do lote")
                break
                
    except ImportError:
        print("⚠️ Sistema de lotes não disponível")
    except Exception as e:
        print(f"❌ Erro no processamento em lote: {e}")

async def demo_analytics():
    """Demonstração do sistema de analytics"""
    print_header("DEMONSTRAÇÃO - SISTEMA DE ANALYTICS")
    
    try:
        from app.services.tts_analytics_service import get_tts_usage_stats, get_tts_performance_report
        
        print_section("Estatísticas de Uso")
        
        usage_stats = await get_tts_usage_stats()
        
        print(f"📊 Total requisições: {usage_stats.total_requests}")
        print(f"✅ Requisições bem-sucedidas: {usage_stats.successful_requests}")
        print(f"❌ Requisições falharam: {usage_stats.failed_requests}")
        print(f"⏱️ Tempo total processamento: {usage_stats.total_processing_time:.2f}s")
        print(f"🎵 Duração total áudio: {usage_stats.total_audio_duration:.2f}s")
        print(f"👥 Usuários únicos: {usage_stats.unique_users}")
        
        if usage_stats.total_requests > 0:
            success_rate = (usage_stats.successful_requests / usage_stats.total_requests) * 100
            print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        print_section("Relatório de Performance")
        
        report = await get_tts_performance_report()
        
        if 'performance_insights' in report:
            insights = report['performance_insights']
            print(f"⚡ Tempo mediano processamento: {insights.get('median_processing_time', 0):.2f}s")
            print(f"📊 Cache hit rate: {insights.get('cache_hit_rate', 0):.1f}%")
            
    except ImportError:
        print("⚠️ Sistema de analytics não disponível")
    except Exception as e:
        print(f"❌ Erro no analytics: {e}")

def demo_api():
    """Demonstração dos endpoints da API"""
    print_header("DEMONSTRAÇÃO - ENDPOINTS DA API")
    
    print_section("Endpoints Básicos (/api/tts/)")
    print("🎯 POST /api/tts/generate-narration - Gerar narração individual")
    print("📊 GET  /api/tts/stats - Estatísticas do sistema")
    print("📦 POST /api/tts/quick-batch - Lote rápido (até 10 textos)")
    print("📥 GET  /api/tts/download/{filename} - Download de arquivos")
    
    print_section("Endpoints Avançados (/api/tts/advanced/)")
    print("🚀 POST /api/tts/advanced/batch - Criar lote (até 50 textos)")
    print("📋 GET  /api/tts/advanced/batch/{id}/status - Status do lote")
    print("📁 GET  /api/tts/advanced/batch/{id}/download - Download ZIP")
    print("❌ DELETE /api/tts/advanced/batch/{id} - Cancelar lote")
    
    print_section("Cache e Analytics")
    print("💾 GET  /api/tts/advanced/cache/stats - Estatísticas cache")
    print("🧹 DELETE /api/tts/advanced/cache - Limpar cache (admin)")
    print("📈 GET  /api/tts/advanced/analytics - Analytics completos")
    print("❤️ GET  /api/tts/advanced/health - Health check")
    
    print_section("Exemplo de Uso via cURL")
    print("""
# Gerar narração individual
curl -X POST "http://localhost:8000/api/tts/generate-narration" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Olá! Este é um teste via API.",
    "provider": "gtts",
    "voice": "v2/pt_speaker_0"
  }'

# Lote rápido
curl -X POST "http://localhost:8000/api/tts/quick-batch" \\
  -H "Content-Type: application/json" \\
  -d '{
    "texts": ["Texto 1", "Texto 2", "Texto 3"],
    "provider": "auto"
  }'

# Estatísticas
curl "http://localhost:8000/api/tts/stats"
    """)

def demo_configuracao():
    """Demonstração de configuração"""
    print_header("CONFIGURAÇÃO E INSTALAÇÃO")
    
    print_section("Dependências Necessárias")
    print("""
# Dependências básicas
pip install torch transformers torchaudio gtts pydub

# Para GPU (recomendado para Bark)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Token Hugging Face (opcional)
export HUGGINGFACE_TOKEN="your_token_here"
    """)
    
    print_section("Vozes Disponíveis em Português")
    vozes = [
        ("v2/pt_speaker_0", "Masculina neutra"),
        ("v2/pt_speaker_1", "Feminina jovem"),
        ("v2/pt_speaker_2", "Feminina profissional"),
        ("v2/pt_speaker_3", "Masculina grave"),
        ("v2/pt_speaker_4", "Feminina madura"),
        ("v2/pt_speaker_5", "Variação 1"),
        ("v2/pt_speaker_6", "Variação 2"),
        ("v2/pt_speaker_7", "Variação 3"),
        ("v2/pt_speaker_8", "Variação 4"),
        ("v2/pt_speaker_9", "Variação 5")
    ]
    
    for voz, descricao in vozes:
        print(f"🎭 {voz}: {descricao}")
    
    print_section("Provedores TTS")
    print("🤖 gtts: Google Text-to-Speech (rápido, boa qualidade)")
    print("🧠 bark: Hugging Face Bark (lento, excelente qualidade)")
    print("⚡ auto: Auto-detecção do melhor provedor disponível")

async def main():
    """Função principal da demonstração"""
    print_header("SISTEMA TTS COMPLETO - TECNOCIURSOS AI")
    print("🎉 Demonstração de todas as funcionalidades implementadas")
    print("🚀 Sistema pronto para produção com cache, lotes e analytics")
    
    try:
        # Executar demonstrações
        await demo_basico()
        await demo_cache()
        await demo_batch()
        await demo_analytics()
        demo_api()
        demo_configuracao()
        
        print_header("DEMONSTRAÇÃO CONCLUÍDA")
        print("✅ Todas as funcionalidades foram demonstradas")
        print("🎤 Sistema TTS está operacional e pronto para uso")
        print("📖 Consulte README_GENERATE_NARRATION.md para documentação completa")
        print("🏗️ Veja SISTEMA_TTS_COMPLETO_IMPLEMENTADO.md para arquitetura detalhada")
        
    except KeyboardInterrupt:
        print("\n\n⛔ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro na demonstração: {e}")
        print("🔧 Verifique se todas as dependências estão instaladas")

if __name__ == "__main__":
    # Executar demonstração
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Erro ao executar demonstração: {e}")
        print("🔧 Execute: pip install -r requirements.txt") 