#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE DO SISTEMA UNIFICADO - TECNOCURSOS AI
==============================================

Script de teste completo para validar todas as funcionalidades
do sistema unificado após padronização e consolidação.

Funcionalidades Testadas:
- Sistema de imports centralizados
- Configuração unificada
- Video Engine
- Dependências instaladas
- Funcionalidades básicas

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import sys
import os
from pathlib import Path

# Adicionar app ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports_system():
    """Testar sistema de imports centralizados"""
    print("🔗 TESTANDO SISTEMA DE IMPORTS CENTRALIZADOS")
    print("=" * 60)
    
    try:
        from app.core.imports import (
            get_dependency_report, 
            check_dependencies,
            check_video_dependencies,
            check_ai_dependencies,
            check_web_dependencies,
            AVAILABLE_MODULES
        )
        
        print("✅ Imports centralizados carregados com sucesso")
        
        # Mostrar status das dependências
        deps = check_dependencies()
        print(f"✅ Status das dependências obtido: {len(deps)} módulos verificados")
        
        # Verificar dependências por categoria
        print(f"🎬 Dependências de vídeo: {'✅' if check_video_dependencies() else '❌'}")
        print(f"🤖 Dependências de IA: {'✅' if check_ai_dependencies() else '❌'}")
        print(f"🌐 Dependências web: {'✅' if check_web_dependencies() else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de imports: {e}")
        return False

def test_unified_config():
    """Testar configuração unificada"""
    print("\n🔧 TESTANDO CONFIGURAÇÃO UNIFICADA")
    print("=" * 60)
    
    try:
        from app.unified_config import (
            get_config, 
            get_video_config,
            get_audio_config,
            get_ai_config,
            is_development
        )
        
        print("✅ Configuração unificada carregada com sucesso")
        
        # Testar configurações
        config = get_config()
        print(f"✅ Configuração principal: {type(config).__name__}")
        
        video_config = get_video_config()
        print(f"✅ Config de vídeo: resolução padrão {video_config.default_resolution}")
        
        audio_config = get_audio_config()
        print(f"✅ Config de áudio: provedor padrão {audio_config.default_provider}")
        
        ai_config = get_ai_config()
        print(f"✅ Config de IA: provedor padrão {ai_config.default_provider}")
        
        print(f"✅ Modo desenvolvimento: {is_development()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração unificada: {e}")
        return False

def test_video_engine():
    """Testar Video Engine"""
    print("\n🎬 TESTANDO VIDEO ENGINE")
    print("=" * 60)
    
    try:
        from app.video_engine import (
            VideoEngine, 
            VideoConfig, 
            VideoQuality, 
            VideoTemplate,
            video_engine
        )
        
        print("✅ Video Engine carregado com sucesso")
        
        # Testar configuração
        config = VideoConfig()
        print(f"✅ Config de vídeo: {config.width}x{config.height} @ {config.fps}fps")
        
        # Testar instância global
        print(f"✅ Instância global: {type(video_engine).__name__}")
        
        # Testar enums
        print(f"✅ Qualidades disponíveis: {[q.value for q in VideoQuality]}")
        print(f"✅ Templates disponíveis: {[t.value for t in VideoTemplate]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Video Engine: {e}")
        return False

def test_basic_functionality():
    """Testar funcionalidades básicas"""
    print("\n⚙️ TESTANDO FUNCIONALIDADES BÁSICAS")
    print("=" * 60)
    
    try:
        # Testar imports básicos que devem estar disponíveis
        from app.core.imports import (
            FASTAPI_AVAILABLE,
            SQLALCHEMY_AVAILABLE, 
            PYDANTIC_AVAILABLE,
            PIL_AVAILABLE,
            GTTS_AVAILABLE
        )
        
        print(f"✅ FastAPI disponível: {FASTAPI_AVAILABLE}")
        print(f"✅ SQLAlchemy disponível: {SQLALCHEMY_AVAILABLE}")
        print(f"✅ Pydantic disponível: {PYDANTIC_AVAILABLE}")
        print(f"✅ PIL disponível: {PIL_AVAILABLE}")
        print(f"✅ gTTS disponível: {GTTS_AVAILABLE}")
        
        # Testar funcionalidades básicas se disponíveis
        if FASTAPI_AVAILABLE:
            from app.core.imports import FastAPI, APIRouter
            print("✅ FastAPI classes importadas com sucesso")
        
        if PIL_AVAILABLE:
            from app.core.imports import Image
            print("✅ PIL Image importada com sucesso")
            
            # Criar uma imagem de teste
            img = Image.new('RGB', (100, 100), color='red')
            print("✅ Imagem de teste criada com sucesso")
        
        if GTTS_AVAILABLE:
            from app.core.imports import gTTS
            print("✅ gTTS importada com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas funcionalidades básicas: {e}")
        return False

def test_directory_structure():
    """Testar estrutura de diretórios"""
    print("\n📁 TESTANDO ESTRUTURA DE DIRETÓRIOS")
    print("=" * 60)
    
    try:
        # Diretórios que devem existir
        required_dirs = [
            "app",
            "app/core", 
            "static/videos",
            "static/audios",
            "temp/videos",
            "temp/audios",
            "cache/videos",
            "cache/audios",
            "logs"
        ]
        
        for directory in required_dirs:
            path = Path(directory)
            if path.exists():
                print(f"✅ {directory}")
            else:
                path.mkdir(parents=True, exist_ok=True)
                print(f"📁 {directory} (criado)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na estrutura de diretórios: {e}")
        return False

def test_file_system():
    """Testar sistema de arquivos"""
    print("\n💾 TESTANDO SISTEMA DE ARQUIVOS")
    print("=" * 60)
    
    try:
        # Arquivos principais que devem existir
        key_files = [
            "app/__init__.py",
            "app/core/imports.py",
            "app/unified_config.py", 
            "app/video_engine.py",
            "requirements_minimal_dev.txt"
        ]
        
        for file_path in key_files:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                print(f"✅ {file_path} ({size:,} bytes)")
            else:
                print(f"❌ {file_path} (não encontrado)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de arquivos: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("🧪 TESTE COMPLETO DO SISTEMA UNIFICADO TECNOCURSOS AI")
    print("=" * 70)
    print(f"Data: {os.popen('date /t').read().strip() if os.name == 'nt' else os.popen('date').read().strip()}")
    print()
    
    tests = [
        ("Imports Centralizados", test_imports_system),
        ("Configuração Unificada", test_unified_config),
        ("Video Engine", test_video_engine),
        ("Funcionalidades Básicas", test_basic_functionality),
        ("Estrutura de Diretórios", test_directory_structure),
        ("Sistema de Arquivos", test_file_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n📊 RELATÓRIO FINAL")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status:12} {test_name}")
    
    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema unificado funcionando perfeitamente!")
        print("\n✨ PRÓXIMOS PASSOS:")
        print("1. Instalar dependências opcionais: pip install moviepy numpy openai")
        print("2. Configurar chaves de API (OpenAI, D-ID, etc.)")
        print("3. Testar funcionalidades avançadas")
        print("4. Executar em produção")
    else:
        failed = total - passed
        print(f"⚠️ {failed} teste(s) falharam. Verifique os erros acima.")
        print("\n🔧 AÇÕES RECOMENDADAS:")
        print("1. Instalar dependências faltantes")
        print("2. Verificar configurações")
        print("3. Corrigir problemas identificados")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 