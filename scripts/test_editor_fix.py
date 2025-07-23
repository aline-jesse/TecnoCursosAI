#!/usr/bin/env python3
"""
Script de Teste - Correção da Tela Branca
Testa se o editor está funcionando corretamente após as correções
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def print_banner():
    """Exibe banner do teste"""
    print("=" * 80)
    print("TESTE DE CORREÇÃO - TELA BRANCA")
    print("=" * 80)
    print("Verificando se o editor está funcionando corretamente")
    print("=" * 80)

def check_server():
    """Verifica se o servidor está rodando"""
    print("🔍 Verificando servidor...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor respondendo corretamente")
            return True
        else:
            print(f"⚠️ Servidor retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        return False

def test_editor_page():
    """Testa a página do editor"""
    print("\n🔍 Testando página do editor...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ Página do editor carregada")
            
            # Verificar se contém elementos essenciais
            content = response.text
            
            checks = [
                ("React", "React carregado"),
                ("ReactDOM", "ReactDOM carregado"),
                ("Font Awesome", "Font Awesome carregado"),
                ("TecnoCursos AI", "Título correto"),
                ("Editor de Vídeo", "Subtítulo correto"),
                ("sidebar", "Sidebar presente"),
                ("timeline", "Timeline presente"),
                ("canvas", "Canvas presente"),
                ("upload-area", "Área de upload presente"),
                ("assets-grid", "Grid de assets presente"),
                ("scene-list", "Lista de cenas presente")
            ]
            
            all_passed = True
            for check, description in checks:
                if check.lower() in content.lower():
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description} - NÃO ENCONTRADO")
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ Página retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar página: {e}")
        return False

def test_react_functionality():
    """Testa funcionalidades React"""
    print("\n🔍 Testando funcionalidades React...")
    
    try:
        # Testar se o React está carregado corretamente
        response = requests.get("http://localhost:8000/", timeout=10)
        content = response.text
        
        react_checks = [
            ("react-overlay", "Container React presente"),
            ("createRoot", "React 18 createRoot"),
            ("useState", "Hooks React"),
            ("useEffect", "Hooks React"),
            ("TecnoCursosOverlay", "Componente React"),
            ("progress-container", "Progress bar React"),
            ("dragover", "Drag and drop handlers")
        ]
        
        all_passed = True
        for check, description in react_checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - NÃO ENCONTRADO")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Erro ao testar React: {e}")
        return False

def test_static_files():
    """Testa arquivos estáticos"""
    print("\n🔍 Testando arquivos estáticos...")
    
    static_files = [
        "/favicon.ico",
        "/static/css/style.css",
        "/static/js/app.js"
    ]
    
    all_passed = True
    for file_path in static_files:
        try:
            response = requests.get(f"http://localhost:8000{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {file_path} - OK")
            else:
                print(f"⚠️ {file_path} - Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {file_path} - Erro: {e}")
            all_passed = False
    
    return all_passed

def test_api_endpoints():
    """Testa endpoints da API"""
    print("\n🔍 Testando endpoints da API...")
    
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/status", "Status"),
        ("/api/projects", "Projects"),
        ("/api/videos", "Videos"),
        ("/api/audios", "Audios")
    ]
    
    all_passed = True
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} - OK")
            else:
                print(f"⚠️ {name} - Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name} - Erro: {e}")
            all_passed = False
    
    return all_passed

def generate_test_report():
    """Gera relatório de teste"""
    print("\n" + "=" * 80)
    print("RELATÓRIO DE TESTE - CORREÇÃO TELA BRANCA")
    print("=" * 80)
    
    tests = [
        ("Servidor", check_server),
        ("Página do Editor", test_editor_page),
        ("Funcionalidades React", test_react_functionality),
        ("Arquivos Estáticos", test_static_files),
        ("Endpoints API", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"Resultado: {status}")
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O problema da tela branca foi corrigido")
        print("✅ O editor está funcionando corretamente")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
        print("❌ Ainda há problemas para resolver")
    
    return passed == total

def main():
    """Função principal"""
    print_banner()
    
    # Verificar se o servidor está rodando
    if not check_server():
        print("\n❌ Servidor não está rodando!")
        print("Execute: python simple_server.py")
        return False
    
    # Executar todos os testes
    success = generate_test_report()
    
    if success:
        print("\n🚀 SISTEMA FUNCIONANDO CORRETAMENTE!")
        print("Acesse: http://localhost:8000")
        print("O editor deve carregar sem tela branca")
    else:
        print("\n🔧 PROBLEMAS DETECTADOS")
        print("Verifique os logs acima para identificar os problemas")
    
    return success

if __name__ == "__main__":
    main() 