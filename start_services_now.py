#!/usr/bin/env python3
"""
TecnoCursos AI - Sistema de Inicialização Completo
Executar tudo de uma vez
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def log_output(process, name):
    """Captura e exibe output dos processos"""
    for line in iter(process.stdout.readline, b''):
        if line:
            print(f"[{name}] {line.decode().strip()}")

def start_backend():
    """Inicia o servidor backend"""
    print("🚀 Iniciando Backend (FastAPI)...")
    
    # Entrar no diretório backend
    os.chdir("backend")
    
    # Comando para iniciar o backend
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001", 
        "--reload"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Thread para capturar output
        thread = threading.Thread(target=log_output, args=(process, "BACKEND"))
        thread.daemon = True
        thread.start()
        
        print("✅ Backend iniciado em http://localhost:8001")
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Inicia o servidor frontend"""
    print("🎨 Iniciando Frontend (React)...")
    
    # Voltar ao diretório raiz e entrar no frontend
    os.chdir("../frontend")
    
    # Comando para iniciar o frontend
    cmd = ["npm", "run", "dev"]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Thread para capturar output
        thread = threading.Thread(target=log_output, args=(process, "FRONTEND"))
        thread.daemon = True
        thread.start()
        
        print("✅ Frontend iniciado em http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        return None

def main():
    """Função principal - inicia tudo"""
    print("=" * 60)
    print("🎯 TECNOCURSOS AI - INICIALIZANDO SISTEMA COMPLETO")
    print("=" * 60)
    
    # Voltar ao diretório raiz
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    processes = []
    
    # 1. Iniciar Backend
    backend_process = start_backend()
    if backend_process:
        processes.append(("Backend", backend_process))
        time.sleep(3)  # Aguardar backend inicializar
    
    # 2. Iniciar Frontend
    frontend_process = start_frontend()
    if frontend_process:
        processes.append(("Frontend", frontend_process))
        time.sleep(2)  # Aguardar frontend inicializar
    
    print("\n" + "=" * 60)
    print("🎉 SISTEMA INICIADO COM SUCESSO!")
    print("=" * 60)
    print("🌐 Frontend: http://localhost:3000")
    print("⚡ Backend:  http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print("📊 Health:   http://localhost:8001/health")
    print("\n💡 Pressione Ctrl+C para parar todos os serviços")
    print("=" * 60)
    
    try:
        # Manter os processos rodando
        while True:
            time.sleep(1)
            
            # Verificar se algum processo parou
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} parou inesperadamente!")
                    
    except KeyboardInterrupt:
        print("\n🛑 Parando todos os serviços...")
        
        # Parar todos os processos
        for name, process in processes:
            try:
                process.terminate()
                print(f"✅ {name} parado")
            except:
                pass
        
        print("✅ Todos os serviços foram parados com sucesso!")

if __name__ == "__main__":
    main()
