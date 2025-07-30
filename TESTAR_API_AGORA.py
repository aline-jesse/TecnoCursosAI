#!/usr/bin/env python3
"""
Teste Automático da API - TecnoCursos AI
Verifica se o servidor está respondendo corretamente
"""

import requests
import json
import time

def test_api():
    """Testa todos os endpoints da API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testando API TecnoCursosAI...")
    print("="*50)
    
    # Teste 1: Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: OK")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"❌ Health Check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check: Erro de conexão - {e}")
        return False
    
    # Teste 2: Status da API
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ API Status: OK")
        else:
            print(f"❌ API Status: {response.status_code}")
    except Exception as e:
        print(f"❌ API Status: {e}")
    
    # Teste 3: Login
    try:
        login_data = {
            "email": "admin@tecnocursos.com",
            "password": "admin123"
        }
        response = requests.post(
            f"{base_url}/api/auth/login", 
            json=login_data,
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Login: OK")
            token_data = response.json()
            print(f"   Token obtido: {token_data['access_token'][:20]}...")
            
            # Teste 4: Dados do usuário
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            user_response = requests.get(
                f"{base_url}/api/auth/me",
                headers=headers,
                timeout=5
            )
            if user_response.status_code == 200:
                print("✅ Dados do usuário: OK")
            else:
                print(f"⚠️ Dados do usuário: {user_response.status_code}")
        else:
            print(f"❌ Login: {response.status_code}")
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"❌ Login: {e}")
    
    # Teste 5: Documentação
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Documentação: OK")
        else:
            print(f"❌ Documentação: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentação: {e}")
    
    print("="*50)
    print("🎉 Teste concluído!")
    print(f"🌐 Acesse: {base_url}")
    print(f"📚 Docs: {base_url}/docs")
    return True

def wait_for_server():
    """Aguarda o servidor ficar disponível"""
    print("⏳ Aguardando servidor ficar disponível...")
    for i in range(30):  # Aguardar até 30 segundos
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Servidor disponível!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"   Tentativa {i+1}/30...")
    
    print("❌ Servidor não respondeu em 30 segundos")
    return False

if __name__ == "__main__":
    if wait_for_server():
        test_api()
    else:
        print("💡 Inicie o servidor com: python RESOLVER_CONEXAO_AGORA.py")
