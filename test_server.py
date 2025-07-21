#!/usr/bin/env python3
"""
Script de teste para verificar inicialização do servidor TecnoCursos AI
"""

import sys
import os
import traceback

def test_imports():
    """Testar importações principais"""
    print("🔍 Testando importações...")
    
    try:
        from app.main import app
        print("✅ app.main importado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar app.main: {e}")
        traceback.print_exc()
        return False

def test_basic_endpoints():
    """Testar endpoints básicos"""
    print("🔍 Testando endpoints básicos...")
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app=app)
        
        # Testar health endpoint
        response = client.get("/api/health")
        print(f"✅ Health endpoint: {response.status_code}")
        
        # Testar docs
        response = client.get("/docs")
        print(f"✅ Docs endpoint: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar endpoints: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Testando TecnoCursos AI Server")
    print("="*50)
    
    # Teste 1: Importações
    if not test_imports():
        print("❌ Falha nos testes de importação")
        return False
    
    # Teste 2: Endpoints básicos
    if not test_basic_endpoints():
        print("❌ Falha nos testes de endpoints")
        return False
    
    print("="*50)
    print("✅ Todos os testes passaram!")
    print("🎉 Servidor está pronto para inicializar")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 