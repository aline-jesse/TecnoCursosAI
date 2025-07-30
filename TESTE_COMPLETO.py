#!/usr/bin/env python3
"""
TESTE AUTOMATICO COMPLETO - TecnoCursos AI
Verifica se a implementação está funcionando
"""

import requests
import json
import time
import threading
import subprocess
import sys

def wait_for_server(max_attempts=30):
    """Aguarda servidor ficar disponível"""
    print("⏳ Aguardando servidor...")
    
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Servidor disponível!")
                return True
        except:
            pass
        
        print(f"   Tentativa {i+1}/{max_attempts}...")
        time.sleep(1)
    
    print("❌ Servidor não respondeu")
    return False

def test_all_endpoints():
    """Testa todos os endpoints da API"""
    base_url = "http://localhost:8000"
    results = []
    
    print("\n🧪 TESTANDO TODOS OS ENDPOINTS")
    print("="*50)
    
    # Teste 1: Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: OK")
            results.append("✅ Health Check")
        else:
            print(f"❌ Health Check: {response.status_code}")
            results.append("❌ Health Check")
    except Exception as e:
        print(f"❌ Health Check: {e}")
        results.append("❌ Health Check")
    
    # Teste 2: Página Principal
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Página Principal: OK")
            results.append("✅ Página Principal")
        else:
            print(f"❌ Página Principal: {response.status_code}")
            results.append("❌ Página Principal")
    except Exception as e:
        print(f"❌ Página Principal: {e}")
        results.append("❌ Página Principal")
    
    # Teste 3: Status da API
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ API Status: OK")
            results.append("✅ API Status")
        else:
            print(f"❌ API Status: {response.status_code}")
            results.append("❌ API Status")
    except Exception as e:
        print(f"❌ API Status: {e}")
        results.append("❌ API Status")
    
    # Teste 4: Login Admin
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
            token_data = response.json()
            token = token_data.get('access_token')
            print("✅ Login Admin: OK")
            results.append("✅ Login Admin")
            
            # Teste 5: Dados do Usuário
            headers = {"Authorization": f"Bearer {token}"}
            user_response = requests.get(
                f"{base_url}/api/auth/me",
                headers=headers,
                timeout=5
            )
            if user_response.status_code == 200:
                print("✅ Dados do Usuário: OK")
                results.append("✅ Dados do Usuário")
            else:
                print(f"❌ Dados do Usuário: {user_response.status_code}")
                results.append("❌ Dados do Usuário")
        else:
            print(f"❌ Login Admin: {response.status_code}")
            results.append("❌ Login Admin")
    except Exception as e:
        print(f"❌ Login Admin: {e}")
        results.append("❌ Login Admin")
    
    # Teste 6: Login Usuário
    try:
        login_data = {
            "email": "user@tecnocursos.com",
            "password": "user123"
        }
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Login Usuário: OK")
            results.append("✅ Login Usuário")
        else:
            print(f"❌ Login Usuário: {response.status_code}")
            results.append("❌ Login Usuário")
    except Exception as e:
        print(f"❌ Login Usuário: {e}")
        results.append("❌ Login Usuário")
    
    # Teste 7: Documentação
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Documentação: OK")
            results.append("✅ Documentação")
        else:
            print(f"❌ Documentação: {response.status_code}")
            results.append("❌ Documentação")
    except Exception as e:
        print(f"❌ Documentação: {e}")
        results.append("❌ Documentação")
    
    return results

def generate_report(results):
    """Gera relatório final"""
    print("\n" + "="*50)
    print("📊 RELATÓRIO FINAL DE TESTES")
    print("="*50)
    
    total = len(results)
    success = len([r for r in results if r.startswith("✅")])
    failed = total - success
    
    print(f"📈 Total de testes: {total}")
    print(f"✅ Sucessos: {success}")
    print(f"❌ Falhas: {failed}")
    print(f"📊 Taxa de sucesso: {(success/total)*100:.1f}%")
    
    print("\n📋 Detalhes:")
    for result in results:
        print(f"   {result}")
    
    if success == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 TecnoCursos AI está funcionando perfeitamente!")
    elif success >= total * 0.8:
        print("\n⚠️ Maioria dos testes passou")
        print("🔧 Algumas funcionalidades podem precisar de ajuste")
    else:
        print("\n❌ Muitos testes falharam")
        print("🚨 Verifique se o servidor está rodando")
    
    print("\n📍 URLs importantes:")
    print("   - Backend: http://localhost:8000")
    print("   - Documentação: http://localhost:8000/docs")
    print("   - Health: http://localhost:8000/health")
    
    print("\n🔑 Credenciais de teste:")
    print("   - admin@tecnocursos.com / admin123")
    print("   - user@tecnocursos.com / user123")

def main():
    """Função principal de teste"""
    print("🧪 TECNOCURSOS AI - TESTE AUTOMÁTICO COMPLETO")
    print("="*60)
    
    # Aguardar servidor
    if not wait_for_server():
        print("💡 Execute: python AUTO_IMPLEMENTAR.py")
        return
    
    # Executar testes
    results = test_all_endpoints()
    
    # Gerar relatório
    generate_report(results)

if __name__ == "__main__":
    main()
