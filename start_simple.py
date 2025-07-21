#!/usr/bin/env python3
"""
Script de inicialização simples para TecnoCursos AI
Versão simplificada e confiável
"""

import os
import sys
import subprocess
import time
import requests
import socket

def print_banner():
    """Imprime banner do sistema"""
    print("=" * 50)
    print("🚀 TECNOCURSOS AI - INICIALIZAÇÃO SIMPLES")
    print("=" * 50)
    print("📅 Data/Hora:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)

def check_dependencies():
    """Verifica dependências"""
    print("\n📦 Verificando dependências...")
    
    try:
        import requests
        print("✅ requests - OK")
        return True
    except ImportError:
        print("❌ requests - FALTANDO")
        print("💡 Execute: pip install requests")
        return False

def check_files():
    """Verifica arquivos necessários"""
    print("\n📁 Verificando arquivos...")
    
    required_files = [
        'index.html',
        'src/App.jsx', 
        'src/index.css',
        'simple_server.py'
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - OK")
        else:
            print(f"❌ {file_path} - FALTANDO")
            all_ok = False
    
    return all_ok

def kill_process_on_port(port):
    """Mata processo na porta"""
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
                        print(f"🔄 Processo {pid} na porta {port} finalizado")
                        return True
        return False
    except:
        return False

def start_server():
    """Inicia o servidor"""
    print("\n🚀 Iniciando servidor...")
    
    # Tenta liberar porta 8000
    print("🔄 Verificando porta 8000...")
    kill_process_on_port(8000)
    time.sleep(1)
    
    try:
        # Inicia servidor
        print("📡 Iniciando servidor na porta 8000...")
        server_process = subprocess.Popen([sys.executable, "simple_server.py"])
        
        # Aguarda inicialização
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(3)
        
        # Testa conectividade
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor iniciado com sucesso!")
                return True
            else:
                print(f"⚠️  Servidor respondeu com status {response.status_code}")
                return True
        except requests.exceptions.RequestException:
            print("⚠️  Não foi possível conectar ao servidor")
            print("💡 Verifique se não há outro processo usando a porta 8000")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

def run_tests():
    """Executa testes"""
    print("\n🧪 Executando testes...")
    
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
        print("⚠️  Testes demoraram muito")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def open_browser():
    """Abre navegador"""
    try:
        import webbrowser
        url = "http://localhost:8000"
        print(f"\n🌐 Abrindo navegador em {url}")
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"⚠️  Não foi possível abrir navegador: {e}")
        return False

def main():
    """Função principal"""
    print_banner()
    
    # Verificações
    if not check_dependencies():
        return 1
    
    if not check_files():
        print("⚠️  Alguns arquivos estão faltando")
    
    # Inicia servidor
    if not start_server():
        print("\n❌ Falha ao iniciar servidor")
        print("💡 Tente executar manualmente: python simple_server.py")
        return 1
    
    # Executa testes
    run_tests()
    
    # Mostra informações
    print(f"\n🎉 SISTEMA INICIADO!")
    print(f"🌐 URL: http://localhost:8000")
    print(f"🔗 Health: http://localhost:8000/health")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"🔧 API: http://localhost:8000/api/health")
    
    # Abre navegador
    open_browser()
    
    print("\n💡 Pressione Ctrl+C para parar o servidor")
    
    try:
        # Mantém o script rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 