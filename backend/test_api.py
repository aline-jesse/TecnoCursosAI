"""
Script para testar a API de forma isolada.
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== TESTE DA API TECNOCURSOS ===\n")

# Testar importação básica
try:
    from app.main import app
    print("✅ App importada com sucesso!")
    print(f"   Título: {app.title}")
    print(f"   Versão: {app.version}")
except Exception as e:
    print(f"❌ Erro ao importar app: {e}")
    sys.exit(1)

# Listar endpoints disponíveis
print("\n📍 Endpoints disponíveis:")
for route in app.routes:
    if hasattr(route, 'methods'):
        for method in route.methods:
            print(f"   {method} {route.path}")

# Tentar fazer uma requisição local
print("\n🔍 Testando endpoint de saúde...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.json()}")
except Exception as e:
    print(f"❌ Erro ao testar endpoint: {e}")

print("\n✅ Teste concluído!") 