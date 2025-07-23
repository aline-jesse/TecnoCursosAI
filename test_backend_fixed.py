#!/usr/bin/env python3
"""
Teste do Backend TecnoCursos AI - Após Correções
Verifica se o backend principal pode ser importado e inicializado
"""

import sys
import os

# Adicionar diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Testa as importações principais"""
    try:
        print("🔍 Testando importações...")
        
        # Testar importação da aplicação
        from app.main import app
        print("✅ Aplicação FastAPI importada com sucesso")
        
        # Testar banco de dados
        from app.database import get_db, Base
        print("✅ Database importado com sucesso")
        
        # Testar schemas
        from app.schemas import UserCreate, HealthCheck
        print("✅ Schemas importados com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_app_creation():
    """Testa a criação da aplicação"""
    try:
        print("\n🚀 Testando criação da aplicação...")
        
        from app.main import app
        
        # Verificar se app foi criado
        if app is None:
            raise Exception("App é None")
            
        print(f"✅ Aplicação criada: {app.title}")
        print(f"✅ Versão: {app.version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação da aplicação: {e}")
        return False

def test_health_endpoint():
    """Testa o endpoint de health check"""
    try:
        print("\n❤️ Testando endpoint de health...")
        
        from fastapi.testclient import TestClient
        from app.main import app
        
        with TestClient(app) as client:
            response = client.get("/api/health")
            
            if response.status_code == 200:
                print("✅ Health check funcionando")
                health_data = response.json()
                print(f"✅ Status: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check falhou: {response.status_code}")
                return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def main():
    """Função principal do teste"""
    print("🧪 TecnoCursos AI - Teste do Backend (Pós-Correções)")
    print("=" * 55)
    
    tests = [
        ("Importações", test_imports),
        ("Criação da App", test_app_creation),
        ("Health Endpoint", test_health_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
    
    print("\n" + "=" * 55)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Backend principal está funcionando!")
        return True
    else:
        print("⚠️ Alguns testes falharam")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 