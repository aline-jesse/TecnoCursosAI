#!/usr/bin/env python3
"""
Script de inicialização para desenvolvimento
Verifica dependências e inicia o servidor
"""

import os
import sys
import subprocess
import time
import requests
import socket
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 ou superior é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = [
        'requests',
        'fastapi',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        print(f"\n📦 Instalando dependências faltantes...")
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
    """Verifica se os arquivos necessários existem"""
    required_files = [
        'index.html',
        'src/App.jsx',
        'src/index.css'
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
        print("   Algumas funcionalidades podem não funcionar corretamente")
    
    return len(missing_files) == 0

def find_available_port(start_port=8000, max_attempts=10):
    """Encontra uma porta disponível"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def check_port_availability(port=8000):
    """Verifica se a porta está disponível"""
    available_port = find_available_port(port)
    if available_port == port:
        print(f"✅ Porta {port} - Disponível")
        return True
    elif available_port:
        print(f"⚠️  Porta {port} - Em uso, usando porta {available_port}")
        return True
    else:
        print(f"❌ Nenhuma porta disponível entre {port} e {port + 10}")
        return False

def kill_process_on_port(port):
    """Tenta matar processo na porta especificada"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        subprocess.run(['taskkill', '/F', '/PID', pid], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"🔄 Processo na porta {port} finalizado")
                        return True
        else:  # Linux/Mac
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"🔄 Processo na porta {port} finalizado")
                return True
    except Exception:
        pass
    return False

def start_server():
    """Inicia o servidor de desenvolvimento"""
    print("\n🚀 Iniciando servidor de desenvolvimento...")
    
    # Encontra porta disponível
    port = find_available_port(8000)
    if port is None:
        print("❌ Nenhuma porta disponível encontrada")
        return False
    
    try:
        # Tenta iniciar o servidor simples
        print(f"📡 Iniciando servidor HTTP na porta {port}...")
        server_process = subprocess.Popen([sys.executable, "simple_server.py"], 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda um pouco para o servidor inicializar
        time.sleep(3)
        
        # Testa se o servidor está respondendo
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor iniciado com sucesso!")
                print(f"\n🌐 URLs disponíveis:")
                print(f"   🎬 Editor: http://localhost:{port}/")
                print(f"   🔗 Health: http://localhost:{port}/health")
                print(f"   📚 Docs: http://localhost:{port}/docs")
                print(f"   🔧 API: http://localhost:{port}/api/health")
                print(f"\n💡 Dicas:")
                print(f"   - Pressione Ctrl+C para parar o servidor")
                print(f"   - Recarregue a página se houver problemas")
                print(f"   - Verifique o console do navegador para logs")
                print(f"   - Teste com: python test_system.py")
                return True
            else:
                print(f"⚠️  Servidor respondeu com status {response.status_code}")
                return True
        except requests.exceptions.RequestException:
            print("⚠️  Não foi possível conectar ao servidor")
            print("   Verifique se não há outro processo usando a porta")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

def run_tests():
    """Executa testes do sistema"""
    print("\n🧪 Executando testes do sistema...")
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Testes passaram!")
            return True
        else:
            print("❌ Alguns testes falharam")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 Verificando ambiente de desenvolvimento...")
    print("=" * 50)
    
    # Verificações
    checks = [
        ("Versão do Python", check_python_version),
        ("Dependências", check_dependencies),
        ("Arquivos", check_files),
        ("Porta 8000", lambda: check_port_availability(8000))
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ Todas as verificações passaram!")
        
        # Tenta liberar porta se necessário
        if not find_available_port(8000):
            print("🔄 Tentando liberar porta 8000...")
            kill_process_on_port(8000)
            time.sleep(2)
        
        if start_server():
            print("\n🎉 Sistema iniciado com sucesso!")
            
            # Pergunta se quer executar testes
            try:
                response = input("\n🧪 Executar testes do sistema? (s/n): ").lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    run_tests()
            except KeyboardInterrupt:
                print("\n👋 Saindo...")
        else:
            print("❌ Falha ao iniciar servidor")
            return 1
    else:
        print("❌ Algumas verificações falharam.")
        print("   Corrija os problemas antes de continuar.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 