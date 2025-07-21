#!/usr/bin/env python3
"""
Script de Inicialização Completa - TecnoCursosAI
Resolve todos os problemas e inicia o sistema completo
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprimir mensagem com status colorido"""
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m", 
        "WARNING": "\033[93m",
        "INFO": "\033[94m"
    }
    color = colors.get(status, colors["INFO"])
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def check_port_available(port):
    """Verificar se porta está disponível"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def find_available_port(start_port=8000):
    """Encontrar porta disponível"""
    port = start_port
    while not check_port_available(port):
        port += 1
    return port

def install_missing_dependencies():
    """Instalar dependências faltantes"""
    print_status("🔧 Verificando e instalando dependências...", "INFO")
    
    # Dependências críticas que podem estar faltando
    critical_deps = [
        "moviepy",
        "gtts", 
        "pydub",
        "redis",
        "transformers",
        "torch"
    ]
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print_status(f"✅ {dep} já instalado", "SUCCESS")
        except ImportError:
            print_status(f"📦 Instalando {dep}...", "WARNING")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print_status(f"✅ {dep} instalado com sucesso", "SUCCESS")
            except subprocess.CalledProcessError:
                print_status(f"⚠️ {dep} falhou, continuando...", "WARNING")

def create_missing_directories():
    """Criar diretórios necessários"""
    print_status("📁 Criando diretórios necessários...", "INFO")
    
    directories = [
        "static/uploads",
        "static/videos",
        "static/audios", 
        "static/thumbnails",
        "logs",
        "cache",
        "temp",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_status(f"✅ {directory}", "SUCCESS")

def setup_database():
    """Configurar banco de dados"""
    print_status("🗄️ Configurando banco de dados...", "INFO")
    
    try:
        # Importar e criar tabelas
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print_status("✅ Banco de dados configurado", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Erro no banco: {e}", "ERROR")
        return False

def start_backend_server(port):
    """Iniciar servidor backend"""
    print_status(f"🚀 Iniciando servidor backend na porta {port}...", "INFO")
    
    try:
        # Usar uvicorn para iniciar o servidor
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ]
        
        process = subprocess.Popen(cmd)
        print_status(f"✅ Servidor backend iniciado em http://localhost:{port}", "SUCCESS")
        return process
    except Exception as e:
        print_status(f"❌ Erro ao iniciar backend: {e}", "ERROR")
        return None

def start_frontend_server(port):
    """Iniciar servidor frontend"""
    print_status(f"🎨 Iniciando servidor frontend na porta {port}...", "INFO")
    
    try:
        # Verificar se package.json existe
        if not Path("package.json").exists():
            print_status("⚠️ package.json não encontrado, pulando frontend", "WARNING")
            return None
        
        # Instalar dependências se necessário
        if not Path("node_modules").exists():
            print_status("📦 Instalando dependências npm...", "INFO")
            subprocess.run(["npm", "install"], check=True)
        
        # Iniciar servidor de desenvolvimento
        cmd = ["npm", "run", "dev"]
        process = subprocess.Popen(cmd, env={**os.environ, "PORT": str(port)})
        print_status(f"✅ Frontend iniciado em http://localhost:{port}", "SUCCESS")
        return process
    except Exception as e:
        print_status(f"❌ Erro ao iniciar frontend: {e}", "ERROR")
        return None

def test_system():
    """Testar sistema"""
    print_status("🧪 Testando sistema...", "INFO")
    
    import requests
    import time
    
    # Aguardar servidor iniciar
    time.sleep(3)
    
    try:
        # Testar endpoint de saúde
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print_status("✅ Backend funcionando", "SUCCESS")
        else:
            print_status("❌ Backend com problemas", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Erro ao testar backend: {e}", "ERROR")
        return False
    
    return True

def show_system_info():
    """Mostrar informações do sistema"""
    print_status("=" * 60, "INFO")
    print_status("🎯 TECNOCURSOS AI - SISTEMA INICIADO", "SUCCESS")
    print_status("=" * 60, "INFO")
    print_status("📋 URLs disponíveis:", "INFO")
    print_status("🏠 Backend API: http://localhost:8000", "INFO")
    print_status("📚 Documentação: http://localhost:8000/docs", "INFO")
    print_status("🎨 Frontend: http://localhost:3000", "INFO")
    print_status("=" * 60, "INFO")
    print_status("🔧 Comandos úteis:", "INFO")
    print_status("• Parar sistema: Ctrl+C", "INFO")
    print_status("• Logs: tail -f logs/app.log", "INFO")
    print_status("• Teste: python test_system_final.py", "INFO")
    print_status("=" * 60, "INFO")

def signal_handler(signum, frame):
    """Handler para Ctrl+C"""
    print_status("\n🛑 Parando sistema...", "WARNING")
    sys.exit(0)

def main():
    """Função principal"""
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print_status("🎯 Iniciando TecnoCursos AI Enterprise Edition 2025...", "INFO")
    print_status("=" * 60, "INFO")
    
    # Verificar Python
    print_status(f"🐍 Python {sys.version.split()[0]} detectado", "SUCCESS")
    
    # Criar diretórios
    create_missing_directories()
    
    # Instalar dependências faltantes
    install_missing_dependencies()
    
    # Configurar banco
    if not setup_database():
        print_status("❌ Falha na configuração do banco", "ERROR")
        return False
    
    # Encontrar portas disponíveis
    backend_port = find_available_port(8000)
    frontend_port = find_available_port(3000)
    
    print_status(f"🔌 Portas: Backend={backend_port}, Frontend={frontend_port}", "INFO")
    
    # Iniciar servidores
    backend_process = start_backend_server(backend_port)
    if not backend_process:
        return False
    
    # Aguardar backend iniciar
    time.sleep(2)
    
    # Testar sistema
    if not test_system():
        print_status("❌ Falha no teste do sistema", "ERROR")
        return False
    
    # Iniciar frontend (opcional)
    frontend_process = start_frontend_server(frontend_port)
    
    # Mostrar informações
    show_system_info()
    
    # Manter sistema rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_status("\n🛑 Parando sistema...", "WARNING")
        
        # Parar processos
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print_status("✅ Sistema parado com sucesso", "SUCCESS")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 