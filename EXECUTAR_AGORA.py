#!/usr/bin/env python3
"""
INICIALIZADOR FINAL - TecnoCursos AI
Inicia backend e frontend automaticamente
"""

import subprocess
import sys
import time
import threading
import webbrowser
import os
from pathlib import Path

def start_backend():
    """Inicia o backend"""
    print("🚀 Iniciando Backend...")
    
    try:
        # Instalar dependências se necessário
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "fastapi", "uvicorn", "python-multipart"
        ], check=False, capture_output=True)
        
        # Iniciar backend
        process = subprocess.Popen([
            sys.executable, "simple_backend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Backend iniciado na porta 8000")
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Inicia o frontend"""
    print("🎨 Iniciando Frontend...")
    
    try:
        process = subprocess.Popen([
            sys.executable, "simple_frontend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Frontend iniciado na porta 3000")
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        return None

def open_browser():
    """Abre o navegador"""
    time.sleep(3)  # Aguardar serviços iniciarem
    
    try:
        print("🌐 Abrindo navegador...")
        webbrowser.open("http://localhost:3000")
        time.sleep(1)
        webbrowser.open("http://localhost:8001")
        print("✅ Navegador aberto!")
    except:
        print("ℹ️ Abra manualmente: http://localhost:3000")

def main():
    """Função principal"""
    print("=" * 60)
    print("🎯 TECNOCURSOS AI - INICIALIZADOR AUTOMÁTICO")
    print("=" * 60)
    print()
    
    processes = []
    
    # Iniciar backend
    backend_process = start_backend()
    if backend_process:
        processes.append(("Backend", backend_process))
        time.sleep(2)
    
    # Iniciar frontend
    frontend_process = start_frontend()
    if frontend_process:
        processes.append(("Frontend", frontend_process))
        time.sleep(2)
    
    # Abrir navegador
    threading.Thread(target=open_browser, daemon=True).start()
    
    print()
    print("=" * 60)
    print("🎉 SISTEMA TECNOCURSOS AI INICIADO!")
    print("=" * 60)
    print("🌐 Frontend: http://localhost:3000")
    print("⚡ Backend:  http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print("❤️ Health:   http://localhost:8001/health")
    print()
    print("💡 Pressione Ctrl+C para parar todos os serviços")
    print("=" * 60)
    
    try:
        # Manter rodando
        while True:
            time.sleep(1)
            
            # Verificar se processos ainda estão rodando
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️ {name} parou inesperadamente!")
                    
    except KeyboardInterrupt:
        print("\n🛑 Parando todos os serviços...")
        
        for name, process in processes:
            try:
                process.terminate()
                print(f"✅ {name} parado")
            except:
                pass
        
        print("✅ Todos os serviços foram parados!")

if __name__ == "__main__":
    main()
