#!/usr/bin/env python3
"""
Inicializador Automático - TecnoCursos AI Backend
Resolve automaticamente o erro ERR_CONNECTION_REFUSED
"""

import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

def install_dependencies():
    """Instala todas as dependências necessárias"""
    print("📦 Instalando dependências...")
    dependencies = [
        "fastapi",
        "uvicorn[standard]", 
        "python-multipart",
        "pyjwt",
        "pydantic[email]",
        "email-validator"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep, "--quiet"
            ], check=True)
            print(f"✅ {dep} instalado")
        except Exception as e:
            print(f"⚠️ Aviso ao instalar {dep}: {e}")

def check_port_available(port):
    """Verifica se a porta está disponível"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except:
        return False

def kill_process_on_port(port):
    """Mata processo rodando na porta"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run([
                'netstat', '-ano'
            ], capture_output=True, check=True)
            subprocess.run([
                'for', '/f', '"tokens=5"', '%a', 'in', 
                f'(\'netstat -ano ^| findstr :{port}\')', 'do', 
                'taskkill', '/F', '/PID', '%a'
            ], shell=True, capture_output=True)
        else:  # Linux/Mac
            subprocess.run([
                'lsof', f'-ti:{port}', '|', 'xargs', 'kill', '-9'
            ], shell=True, capture_output=True)
        print(f"🔄 Porta {port} liberada")
    except:
        pass

def start_server():
    """Inicia o servidor backend"""
    print("🚀 TecnoCursos AI - Iniciador Automático")
    print("="*50)
    print("🎯 Objetivo: Resolver ERR_CONNECTION_REFUSED")
    print("="*50)
    
    # Instalar dependências
    install_dependencies()
    
    # Verificar/liberar porta 8000
    if not check_port_available(8000):
        print("🔄 Liberando porta 8000...")
        kill_process_on_port(8000)
        time.sleep(2)
    
    print("\n🌐 Iniciando servidor...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("❤️ Health: http://localhost:8000/health")
    print("\n🔑 Credenciais de teste:")
    print("Email: admin@tecnocursos.com")
    print("Senha: admin123")
    print("\n⚠️ Para parar: Ctrl+C")
    print("="*50)
    
    # Aguardar um pouco antes de abrir o navegador
    import threading
    def open_browser():
        time.sleep(3)
        try:
            webbrowser.open('http://localhost:8000')
            print("🌐 Navegador aberto automaticamente")
        except:
            pass
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor
    try:
        subprocess.run([sys.executable, "simple_backend.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Tente executar manualmente:")
        print("python simple_backend.py")

if __name__ == "__main__":
    start_server()
