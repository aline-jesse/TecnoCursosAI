#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema está funcionando
"""

import requests
import time
import sys
import socket
from datetime import datetime

def find_server_port(start_port=8000, max_attempts=10):
    """Encontra a porta onde o servidor está rodando"""
    for port in range(start_port, start_port + max_attempts):
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                return port
        except requests.exceptions.RequestException:
            continue
    return None

def test_server_health(port):
    """Testa se o servidor está respondendo"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check - OK")
            return True
        else:
            print(f"❌ Health check - Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check - Erro: {e}")
        return False

def test_api_endpoints(port):
    """Testa endpoints da API"""
    endpoints = [
        ("/api/health", "Health API"),
        ("/api/status", "Status API"),
        ("/api/projects", "Projects API"),
        ("/api/videos", "Videos API"),
        ("/api/audios", "Audios API")
    ]
    
    all_ok = True
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:{port}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} - OK")
            else:
                print(f"❌ {name} - Status {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} - Erro: {e}")
            all_ok = False
    
    return all_ok

def test_static_files(port):
    """Testa arquivos estáticos"""
    files = [
        ("/", "Index HTML"),
        ("/src/App.jsx", "App Component"),
        ("/src/index.css", "CSS Styles"),
        ("/static/favicon.ico", "Favicon")
    ]
    
    all_ok = True
    for file_path, name in files:
        try:
            response = requests.get(f"http://localhost:{port}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} - OK")
            else:
                print(f"❌ {name} - Status {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} - Erro: {e}")
            all_ok = False
    
    return all_ok

def test_frontend_functionality(port):
    """Testa funcionalidades do frontend"""
    try:
        # Testa se o React está carregado
        response = requests.get(f"http://localhost:{port}/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "React" in content and "App" in content:
                print("✅ Frontend React - OK")
                return True
            else:
                print("❌ Frontend React - React não encontrado")
                return False
        else:
            print(f"❌ Frontend React - Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend React - Erro: {e}")
        return False

def test_cors_support(port):
    """Testa suporte a CORS"""
    try:
        response = requests.options(f"http://localhost:{port}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ CORS Support - OK")
            return True
        else:
            print(f"❌ CORS Support - Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS Support - Erro: {e}")
        return False

def test_error_handling(port):
    """Testa tratamento de erros"""
    try:
        # Testa endpoint inexistente
        response = requests.get(f"http://localhost:{port}/api/nonexistent", timeout=5)
        if response.status_code == 404:
            print("✅ Error Handling - OK")
            return True
        else:
            print(f"❌ Error Handling - Status inesperado {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error Handling - Erro: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 Testando Sistema TecnoCursos AI")
    print("=" * 50)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Encontra porta do servidor
    print("🔍 Procurando servidor...")
    port = find_server_port()
    if port is None:
        print("❌ Servidor não encontrado!")
        print("💡 Execute: python simple_server.py")
        return 1
    
    print(f"✅ Servidor encontrado na porta {port}")
    print()
    
    # Aguarda um pouco para garantir que o servidor está pronto
    time.sleep(1)
    
    # Testes
    tests = [
        ("Servidor Health", lambda: test_server_health(port)),
        ("API Endpoints", lambda: test_api_endpoints(port)),
        ("Arquivos Estáticos", lambda: test_static_files(port)),
        ("Frontend React", lambda: test_frontend_functionality(port)),
        ("CORS Support", lambda: test_cors_support(port)),
        ("Error Handling", lambda: test_error_handling(port))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testando: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Taxa de Sucesso: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema funcionando corretamente")
        print(f"🌐 Acesse: http://localhost:{port}")
        print("\n🚀 Próximos passos:")
        print("   - Abra o navegador em http://localhost:{port}")
        print("   - Teste as funcionalidades do editor")
        print("   - Verifique o console para logs")
        return 0
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam")
        print("🔧 Verifique os logs e tente novamente")
        print("\n💡 Dicas:")
        print("   - Verifique se o servidor está rodando")
        print("   - Confirme se todos os arquivos existem")
        print("   - Teste manualmente no navegador")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 