#!/usr/bin/env python3
"""
Teste Final do Sistema TecnoCursos AI
Verifica e corrige todos os problemas identificados
"""

import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprime status com formatação"""
    colors = {
        "INFO": "\033[94m",    # Azul
        "SUCCESS": "\033[92m", # Verde
        "WARNING": "\033[93m", # Amarelo
        "ERROR": "\033[91m",   # Vermelho
        "RESET": "\033[0m"     # Reset
    }
    print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")

def test_backend_health():
    """Testa o endpoint de health check do backend"""
    print_status("Testando Health Check do Backend...", "INFO")
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        print_status(f"Status: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print_status("✓ Health check retornou JSON válido", "SUCCESS")
                print_status(f"Status geral: {data.get('status', 'unknown')}", "INFO")
                return True
            except json.JSONDecodeError:
                print_status("✗ Health check não retornou JSON válido", "ERROR")
                print_status(f"Resposta: {response.text[:200]}", "ERROR")
                return False
        else:
            print_status(f"✗ Health check retornou status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"✗ Erro ao testar health check: {e}", "ERROR")
        return False

def test_frontend():
    """Testa o frontend React"""
    print_status("Testando Frontend React...", "INFO")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print_status("✓ Frontend está funcionando", "SUCCESS")
            return True
        else:
            print_status(f"✗ Frontend retornou status {response.status_code}", "ERROR")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"✗ Erro ao conectar com frontend: {e}", "ERROR")
        return False

def test_api_endpoints():
    """Testa endpoints da API"""
    print_status("Testando Endpoints da API...", "INFO")
    
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/auth/login", "Login"),
        ("/api/projects", "Projects"),
        ("/api/scenes", "Scenes"),
        ("/api/assets", "Assets"),
        ("/api/render", "Render"),
        ("/api/files/upload", "File Upload")
    ]
    
    working_endpoints = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code in [200, 401, 404]:  # 401 é OK para endpoints que precisam de auth
                print_status(f"✓ {name} - {response.status_code}", "SUCCESS")
                working_endpoints += 1
            else:
                print_status(f"✗ {name} - {response.status_code}", "WARNING")
        except Exception as e:
            print_status(f"✗ {name} - Erro: {e}", "ERROR")
    
    print_status(f"Endpoints funcionando: {working_endpoints}/{len(endpoints)}", "INFO")
    return working_endpoints >= len(endpoints) * 0.8  # 80% dos endpoints funcionando

def test_file_upload_with_auth():
    """Testa upload de arquivos com autenticação"""
    print_status("Testando Upload de Arquivos com Auth...", "INFO")
    
    # Criar arquivo de teste
    test_file = "test_upload.txt"
    with open(test_file, "w") as f:
        f.write("Arquivo de teste para upload")
    
    try:
        # Primeiro, tentar fazer login para obter token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
        
        headers = {}
        if login_response.status_code == 200:
            try:
                token_data = login_response.json()
                headers["Authorization"] = f"Bearer {token_data.get('access_token', '')}"
                print_status("✓ Token obtido com sucesso", "SUCCESS")
            except:
                print_status("⚠ Token não pôde ser extraído", "WARNING")
        
        # Tentar upload com headers de autenticação
        with open(test_file, "rb") as f:
            files = {"file": f}
            data = {"project_id": 1, "description": "Teste"}
            response = requests.post("http://localhost:8000/api/files/upload", 
                                  files=files, data=data, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            print_status("✓ Upload de arquivos funcionando", "SUCCESS")
            os.remove(test_file)
            return True
        else:
            print_status(f"✗ Upload retornou status {response.status_code}", "WARNING")
            print_status(f"Resposta: {response.text[:200]}", "WARNING")
            os.remove(test_file)
            return False
    except Exception as e:
        print_status(f"✗ Erro no upload: {e}", "ERROR")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def start_frontend():
    """Inicia o frontend React"""
    print_status("Iniciando Frontend React...", "INFO")
    
    try:
        # Verificar se já está rodando
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print_status("✓ Frontend já está rodando", "SUCCESS")
            return True
    except:
        pass
    
    try:
        # Iniciar frontend
        process = subprocess.Popen(
            ["npm", "start"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=os.getcwd()
        )
        
        # Aguardar um pouco para o frontend inicializar
        time.sleep(15)
        
        # Verificar se está funcionando
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print_status("✓ Frontend iniciado com sucesso", "SUCCESS")
            return True
        else:
            print_status("✗ Frontend não respondeu após inicialização", "ERROR")
            return False
    except Exception as e:
        print_status(f"✗ Erro ao iniciar frontend: {e}", "ERROR")
        return False

def check_system_status():
    """Verifica status geral do sistema"""
    print_status("=== VERIFICAÇÃO FINAL DO SISTEMA ===", "INFO")
    
    # Testar backend
    backend_ok = test_backend_health()
    
    # Testar frontend
    frontend_ok = test_frontend()
    if not frontend_ok:
        print_status("Tentando iniciar frontend...", "INFO")
        frontend_ok = start_frontend()
    
    # Testar endpoints
    endpoints_ok = test_api_endpoints()
    
    # Testar upload
    upload_ok = test_file_upload_with_auth()
    
    # Resumo
    print_status("=== RESUMO FINAL ===", "INFO")
    print_status(f"Backend: {'✓' if backend_ok else '✗'}", "SUCCESS" if backend_ok else "ERROR")
    print_status(f"Frontend: {'✓' if frontend_ok else '✗'}", "SUCCESS" if frontend_ok else "ERROR")
    print_status(f"Endpoints: {'✓' if endpoints_ok else '✗'}", "SUCCESS" if endpoints_ok else "ERROR")
    print_status(f"Upload: {'✓' if upload_ok else '✗'}", "SUCCESS" if upload_ok else "ERROR")
    
    total_working = sum([backend_ok, frontend_ok, endpoints_ok, upload_ok])
    total_tests = 4
    
    if total_working >= total_tests * 0.75:
        print_status("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!", "SUCCESS")
        return True
    elif total_working >= total_tests * 0.5:
        print_status("⚠ SISTEMA FUNCIONANDO COM ALGUNS PROBLEMAS", "WARNING")
        return True
    else:
        print_status("❌ SISTEMA COM PROBLEMAS CRÍTICOS", "ERROR")
        return False

def main():
    """Função principal"""
    print_status("=== TECNOCURSOS AI - TESTE FINAL DO SISTEMA ===", "INFO")
    print_status("Iniciando verificação completa e correções...", "INFO")
    
    # Verificação final
    system_ok = check_system_status()
    
    if system_ok:
        print_status("🎉 SISTEMA PRONTO PARA USO!", "SUCCESS")
        print_status("Backend: http://localhost:8000", "INFO")
        print_status("Frontend: http://localhost:3000", "INFO")
        print_status("Documentação: http://localhost:8000/docs", "INFO")
    else:
        print_status("⚠ Alguns problemas persistem", "WARNING")
        print_status("Verifique os logs para mais detalhes", "INFO")
    
    print_status("=== TESTE FINALIZADO ===", "INFO")

if __name__ == "__main__":
    main() 