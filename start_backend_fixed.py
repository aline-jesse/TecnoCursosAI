#!/usr/bin/env python3
"""
Inicializador Backend Corrigido - TecnoCursos AI
Inicia o backend com health check funcionando
"""

import subprocess
import sys
import time
import threading
import requests
from pathlib import Path

def install_dependencies():
    """Instala dependências necessárias"""
    print("📦 Instalando dependências...")
    
    deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "jinja2==3.1.2",
        "aiofiles==23.2.1",
        "requests==2.31.0"
    ]
    
    for dep in deps:
        try:
            print(f"   Instalando {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"   ⚠️ Falha ao instalar {dep}")

def start_backend():
    """Inicia o servidor backend"""
    print("🚀 Iniciando Backend TecnoCursos AI...")
    
    # Entrar no diretório backend
    backend_dir = Path("backend")
    if backend_dir.exists():
        import os
        os.chdir(backend_dir)
    
    # Comando para iniciar o backend
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8001",
        "--reload"
    ]
    
    try:
        print("📍 Executando comando:")
        print(f"   {' '.join(cmd)}")
        
        # Iniciar processo
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("✅ Backend iniciado!")
        print("📍 URL: http://localhost:8001")
        print("❤️ Health: http://localhost:8001/health")
        print("📚 Docs: http://localhost:8001/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def monitor_output(process):
    """Monitora output do processo"""
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"[BACKEND] {line.rstrip()}")

def wait_for_backend():
    """Aguarda backend ficar disponível"""
    print("\n⏳ Aguardando backend ficar disponível...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend está respondendo!")
                return True
        except:
            pass
        
        time.sleep(1)
        print(f"   Tentativa {attempt + 1}/{max_attempts}...")
    
    print("❌ Backend não respondeu no tempo esperado")
    return False

def test_health_check():
    """Testa se o health check está funcionando"""
    print("\n🧪 Testando health check...")
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check funcionando!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Serviço: {data.get('service', 'unknown')}")
            return True
        else:
            print(f"❌ Health check retornou erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🎯 INICIALIZADOR BACKEND CORRIGIDO - TECNOCURSOS AI")
    print("=" * 60)
    
    # Instalar dependências
    install_dependencies()
    
    # Iniciar backend
    backend_process = start_backend()
    
    if not backend_process:
        print("❌ Falha ao iniciar backend")
        return
    
    # Monitor output em thread separada
    monitor_thread = threading.Thread(
        target=monitor_output, 
        args=(backend_process,), 
        daemon=True
    )
    monitor_thread.start()
    
    # Aguardar backend ficar disponível
    if wait_for_backend():
        # Testar health check
        test_health_check()
        
        print("\n" + "=" * 60)
        print("🎉 BACKEND INICIADO COM SUCESSO!")
        print("=" * 60)
        print("🌐 URLs disponíveis:")
        print("   • Backend: http://localhost:8001")
        print("   • Health: http://localhost:8001/health")
        print("   • API Docs: http://localhost:8001/docs")
        print("   • Status: http://localhost:8001/api/status")
        print("\n💡 Pressione Ctrl+C para parar o servidor")
        print("=" * 60)
        
        try:
            # Manter rodando
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando backend...")
            backend_process.terminate()
            print("✅ Backend parado!")
    
    else:
        print("❌ Backend não iniciou corretamente")
        backend_process.terminate()

if __name__ == "__main__":
    main()
