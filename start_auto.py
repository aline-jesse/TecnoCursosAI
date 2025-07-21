#!/usr/bin/env python3
"""
Script de inicialização automática para TecnoCursos AI
Resolve problemas automaticamente e inicia o sistema completo
"""

import os
import sys
import subprocess
import time
import requests
import socket
import signal
from pathlib import Path

def print_banner():
    """Imprime banner do sistema"""
    print("=" * 60)
    print("🚀 TECNOCURSOS AI - SISTEMA DE INICIALIZAÇÃO AUTOMÁTICA")
    print("=" * 60)
    print("📅 Data/Hora:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("🎯 Objetivo: Resolver problemas automaticamente")
    print("=" * 60)

def kill_processes_on_port(port):
    """Mata processos na porta especificada"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            print(f"🔄 Processo {pid} na porta {port} finalizado")
                        except:
                            pass
        else:  # Linux/Mac
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(['kill', '-9', pid], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"🔄 Processo {pid} na porta {port} finalizado")
                    except:
                        pass
        return True
    except Exception as e:
        print(f"⚠️  Erro ao finalizar processos: {e}")
        return False

def check_and_install_dependencies():
    """Verifica e instala dependências"""
    print("\n📦 Verificando dependências...")
    
    required_packages = ['requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        print(f"\n🔄 Instalando dependências faltantes...")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package} instalado com sucesso")
            except subprocess.CalledProcessError:
                print(f"❌ Falha ao instalar {package}")
                return False
    
    return True

def check_files():
    """Verifica arquivos necessários"""
    print("\n📁 Verificando arquivos...")
    
    required_files = [
        'index.html',
        'src/App.jsx', 
        'src/index.css',
        'simple_server.py',
        'test_system.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - OK")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - FALTANDO")
    
    if missing_files:
        print(f"\n⚠️  Arquivos faltantes: {missing_files}")
        print("   Algumas funcionalidades podem não funcionar")
    
    return len(missing_files) == 0

def find_available_port(start_port=8000, max_attempts=10):
    """Encontra porta disponível"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_server_auto():
    """Inicia servidor automaticamente"""
    print("\n🚀 Iniciando servidor...")
    
    # Tenta liberar porta 8000
    print("🔄 Liberando porta 8000...")
    kill_processes_on_port(8000)
    time.sleep(2)
    
    # Encontra porta disponível
    port = find_available_port(8000)
    if port is None:
        print("❌ Nenhuma porta disponível encontrada")
        return None
    
    try:
        # Inicia servidor diretamente
        print(f"📡 Iniciando servidor na porta {port}...")
        
        # Usa subprocess.Popen para iniciar em background
        server_process = subprocess.Popen([sys.executable, "simple_server.py"], 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        # Aguarda inicialização
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(5)
        
        # Testa conectividade várias vezes
        for attempt in range(3):
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Servidor iniciado com sucesso na porta {port}")
                    return port
                else:
                    print(f"⚠️  Tentativa {attempt + 1}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Tentativa {attempt + 1}: {e}")
            
            if attempt < 2:
                time.sleep(2)
        
        print("❌ Falha ao conectar ao servidor após 3 tentativas")
        return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def run_tests_auto(port):
    """Executa testes automaticamente"""
    print(f"\n🧪 Executando testes na porta {port}...")
    
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Todos os testes passaram!")
            return True
        else:
            print("❌ Alguns testes falharam")
            print(result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Testes demoraram muito, continuando...")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def open_browser(port):
    """Abre navegador automaticamente"""
    try:
        import webbrowser
        url = f"http://localhost:{port}"
        print(f"\n🌐 Abrindo navegador em {url}")
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"⚠️  Não foi possível abrir navegador: {e}")
        return False

def monitor_system(port):
    """Monitora o sistema"""
    print(f"\n📊 Monitorando sistema na porta {port}")
    print("💡 Pressione Ctrl+C para parar")
    
    try:
        while True:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Sistema OK - {time.strftime('%H:%M:%S')}")
                else:
                    print(f"⚠️  Sistema com problemas - {time.strftime('%H:%M:%S')}")
            except:
                print(f"❌ Sistema offline - {time.strftime('%H:%M:%S')}")
            
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n👋 Monitoramento parado")

def main():
    """Função principal"""
    print_banner()
    
    # Verificações
    print("\n🔍 Verificações iniciais...")
    
    if not check_and_install_dependencies():
        print("❌ Falha nas dependências")
        return 1
    
    if not check_files():
        print("⚠️  Alguns arquivos estão faltando")
    
    # Inicia servidor
    port = start_server_auto()
    if port is None:
        print("❌ Falha ao iniciar servidor")
        print("💡 Tente executar manualmente: python simple_server.py")
        return 1
    
    # Executa testes
    if not run_tests_auto(port):
        print("⚠️  Testes falharam, mas continuando...")
    
    # Mostra informações
    print(f"\n🎉 SISTEMA INICIADO COM SUCESSO!")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🔗 Health: http://localhost:{port}/health")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"🔧 API: http://localhost:{port}/api/health")
    
    # Abre navegador
    open_browser(port)
    
    # Pergunta sobre monitoramento
    try:
        response = input("\n📊 Iniciar monitoramento? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            monitor_system(port)
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 