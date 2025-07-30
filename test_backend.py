#!/usr/bin/env python3
"""
Teste do Health Check - TecnoCursos AI
Verifica se o backend está respondendo corretamente
"""

import requests
import json
import time

def test_health_endpoint():
    """Testa o endpoint de health"""
    url = "http://localhost:8001/health"
    
    try:
        print("🔍 Testando endpoint de health...")
        print(f"📍 URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Health check respondeu com sucesso!")
            
            data = response.json()
            print("\n📊 Status do Sistema:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Serviço: {data.get('service', 'unknown')}")
            print(f"   Versão: {data.get('version', 'unknown')}")
            print(f"   Porta: {data.get('port', 'unknown')}")
            print(f"   Ambiente: {data.get('environment', 'unknown')}")
            
            # Mostrar componentes
            components = data.get('components', {})
            print("\n🧩 Componentes:")
            for comp, status in components.items():
                emoji = "✅" if status in ["online", "active", "available"] else "⚠️"
                print(f"   {emoji} {comp}: {status}")
            
            # Mostrar features
            features = data.get('features', {})
            print("\n🚀 Funcionalidades:")
            for feature, enabled in features.items():
                emoji = "✅" if enabled else "❌"
                print(f"   {emoji} {feature}")
            
            return True
            
        else:
            print(f"❌ Health check falhou! Status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao backend!")
        print("💡 Certifique-se de que o backend está rodando na porta 8001")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout ao tentar conectar!")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_api_status():
    """Testa o endpoint de status da API"""
    url = "http://localhost:8001/api/status"
    
    try:
        print(f"\n🔍 Testando endpoint de status da API...")
        print(f"📍 URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API status respondeu com sucesso!")
            
            data = response.json()
            print(f"\n📊 Status da API:")
            print(f"   Versão: {data.get('api_version', 'unknown')}")
            print(f"   Status: {data.get('status', 'unknown')}")
            
            endpoints = data.get('endpoints', {})
            print("\n📍 Endpoints disponíveis:")
            for endpoint, path in endpoints.items():
                print(f"   • {endpoint}: {path}")
            
            return True
            
        else:
            print(f"❌ API status falhou! Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API status: {e}")
        return False

def test_main_page():
    """Testa a página principal"""
    url = "http://localhost:8001/"
    
    try:
        print(f"\n🔍 Testando página principal...")
        print(f"📍 URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Página principal respondeu com sucesso!")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            return True
        else:
            print(f"❌ Página principal falhou! Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar página principal: {e}")
        return False

def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🧪 TESTE COMPLETO DO BACKEND TECNOCURSOS AI")
    print("=" * 60)
    
    results = []
    
    # Testar health check
    results.append(test_health_endpoint())
    
    # Testar API status
    results.append(test_api_status())
    
    # Testar página principal
    results.append(test_main_page())
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📋 RESULTADO DOS TESTES")
    print("=" * 60)
    
    if all(results):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Backend está funcionando corretamente")
        print("\n🌐 URLs para acessar:")
        print("   • Frontend: http://localhost:3000")
        print("   • Backend: http://localhost:8001")
        print("   • Health: http://localhost:8001/health")
        print("   • API Docs: http://localhost:8001/docs")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️ Verifique se o backend está rodando corretamente")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
