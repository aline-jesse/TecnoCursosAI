#!/usr/bin/env python3
"""
Script de verificação e status dos serviços TecnoCursos AI
"""

import requests
import subprocess
import time
import sys
import os
from pathlib import Path

def check_service(url, name, timeout=5):
    """Verifica se um serviço está rodando"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name} está rodando em {url}")
            return True
        else:
            print(f"⚠️ {name} respondeu com status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} não está acessível em {url}")
        return False

def check_port(port):
    """Verifica se uma porta está em uso"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def main():
    print("🔍 VERIFICAÇÃO DE STATUS - TECNOCURSOS AI")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Execute este script do diretório raiz do projeto")
        return
    
    # Verificar portas
    print("\n🔌 Verificando portas:")
    backend_port_open = check_port(8001)
    frontend_port_open = check_port(3000)
    
    print(f"🔧 Porta 8001 (Backend): {'Em uso' if backend_port_open else 'Livre'}")
    print(f"🎨 Porta 3000 (Frontend): {'Em uso' if frontend_port_open else 'Livre'}")
    
    # Verificar serviços via HTTP
    print("\n🌐 Verificando serviços:")
    
    # Backend
    backend_running = check_service("http://localhost:8001/", "Backend API")
    if backend_running:
        check_service("http://localhost:8001/docs", "Documentação API")
        check_service("http://localhost:8001/health", "Health Check")
    
    # Frontend  
    frontend_running = check_service("http://localhost:3000/", "Frontend")
    
    # Resumo
    print("\n📊 RESUMO:")
    print("=" * 30)
    
    if backend_running and frontend_running:
        print("🎉 Todos os serviços estão funcionando!")
        print("\n🔗 Links úteis:")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend: http://localhost:8001")
        print("📚 API Docs: http://localhost:8001/docs")
        print("❤️ Health: http://localhost:8001/health")
    elif backend_running:
        print("⚠️ Apenas o backend está rodando")
        print("💡 Inicie o frontend com: cd frontend && npm run dev")
    elif frontend_running:
        print("⚠️ Apenas o frontend está rodando")
        print("💡 Inicie o backend com: cd backend && python run.py")
    else:
        print("❌ Nenhum serviço está rodando")
        print("💡 Execute o script de inicialização: START_ALL_SERVICES.bat")
    
    # Verificar processos
    print("\n🔍 Verificando processos:")
    try:
        # Verificar processos Python
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        python_processes = result.stdout.count('python.exe')
        print(f"🐍 Processos Python ativos: {python_processes}")
        
        # Verificar processos Node
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq node.exe'], 
                              capture_output=True, text=True, shell=True)
        node_processes = result.stdout.count('node.exe')
        print(f"📦 Processos Node ativos: {node_processes}")
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar processos: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Verificação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante verificação: {e}")
        sys.exit(1)
