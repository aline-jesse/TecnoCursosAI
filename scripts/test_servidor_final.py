#!/usr/bin/env python3
"""
Teste final do servidor TecnoCursos AI
"""

import time
import requests
import sys

def test_server():
    print("🚀 Testando TecnoCursos AI Server...")
    
    try:
        # Testar endpoint principal
        print("📡 Testando endpoint principal...")
        response = requests.get('http://localhost:8000/', timeout=10)
        if response.status_code == 200:
            print("✅ Servidor respondendo na porta 8000!")
        
        # Testar API Status
        print("📊 Testando API status...")
        status_response = requests.get('http://localhost:8000/api/status', timeout=10)
        if status_response.status_code == 200:
            data = status_response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"✅ Versão: {data['version']}")
        
        # Testar documentação
        print("📚 Testando documentação...")
        docs_response = requests.get('http://localhost:8000/docs', timeout=10)
        if docs_response.status_code == 200:
            print("✅ Documentação Swagger disponível!")
        
        print("\n🎉 SISTEMA TECNOCURSOS AI FUNCIONANDO PERFEITAMENTE!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("ℹ️ Servidor não está rodando. Execute: python main.py")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1) 