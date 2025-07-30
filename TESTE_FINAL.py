#!/usr/bin/env python3
"""
TESTE FINAL - TecnoCursos AI
Verifica se o servidor está funcionando corretamente
"""

import requests
import json
import time

def test_connection():
    """Testar conexão com o servidor"""
    print("🔍 TESTANDO CONEXÃO...")
    
    url = "http://127.0.0.1:8000"
    
    try:
        print(f"📡 Tentando conectar em: {url}")
        response = requests.get(f"{url}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ CONEXÃO ESTABELECIDA!")
            data = response.json()
            print(f"📊 Status: {data.get('status')}")
            print(f"🔧 Versão: {data.get('version')}")
            print(f"🚀 Servidor: {data.get('server', {})}")
            return True
        else:
            print(f"❌ Status HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERR_CONNECTION_REFUSED - Servidor não está rodando")
        print("🔧 Execute: python server_completo.py")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_login():
    """Testar login"""
    print("\n🔑 TESTANDO LOGIN...")
    
    login_data = {
        "email": "admin@tecnocursos.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ LOGIN FUNCIONANDO!")
            data = response.json()
            print(f"👤 Usuário: {data.get('user', {}).get('name')}")
            return data.get('access_token')
        else:
            print(f"❌ Login falhou: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def main():
    """Função principal"""
    print("🧪 TESTE FINAL - TecnoCursos AI")
    print("="*50)
    
    # Teste 1: Conexão
    if not test_connection():
        print("\n❌ FALHA: Servidor não está respondendo")
        print("🔧 SOLUÇÃO:")
        print("   1. Execute: python server_completo.py")
        print("   2. Ou clique duas vezes em: INICIAR_SISTEMA.bat")
        print("   3. Aguarde alguns segundos e tente novamente")
        return False
    
    # Teste 2: Login
    token = test_login()
    if not token:
        print("\n⚠️ Login com problemas, mas servidor está funcionando")
    
    print("\n" + "="*50)
    print("🎉 TESTE CONCLUÍDO!")
    print("="*50)
    print("🌐 Servidor: http://127.0.0.1:8000")
    print("📚 Documentação: http://127.0.0.1:8000/docs")
    print("🎛️ Dashboard: http://127.0.0.1:8000/dashboard")
    print("🔑 Admin: admin@tecnocursos.com / admin123")
    print("="*50)
    
    return True

if __name__ == "__main__":
    main()
