#!/usr/bin/env python3
"""
Health Check Simples - TecnoCursos AI
"""

try:
    import requests
    
    print("🔍 Testando health check...")
    print("📍 URL: http://localhost:8001/health")
    
    response = requests.get("http://localhost:8001/health", timeout=5)
    
    if response.status_code == 200:
        print("✅ SUCESSO! Health check funcionando!")
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Serviço: {data.get('service')}")
        print(f"Versão: {data.get('version')}")
    
    elif response.status_code == 404:
        print("❌ ERRO 404: Rota /health não encontrada!")
        print("💡 O backend precisa ser atualizado com a rota de health")
    
    else:
        print(f"❌ ERRO: Status {response.status_code}")
        print(f"Resposta: {response.text}")

except ImportError:
    print("❌ Biblioteca 'requests' não encontrada")
    print("💡 Execute: pip install requests")

except requests.exceptions.ConnectionError:
    print("❌ Erro: Backend não está rodando na porta 8001")
    print("💡 Execute o backend primeiro")

except Exception as e:
    print(f"❌ Erro: {e}")

print("\n🚀 Para iniciar o backend com health check:")
print("   python backend_with_health.py")
print("\n🌐 URLs que devem funcionar:")
print("   • http://localhost:8001")
print("   • http://localhost:8001/health")
print("   • http://localhost:8001/docs")
