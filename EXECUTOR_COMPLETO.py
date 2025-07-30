#!/usr/bin/env python3
"""
EXECUTOR AUTOMÁTICO - TecnoCursos AI
Inicializa todos os serviços automaticamente
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

print("🚀 INICIANDO SISTEMA COMPLETO - TecnoCursos AI")
print("="*70)

def run_command(command, description, shell=True):
    """Executar comando com feedback"""
    print(f"\n▶️ {description}")
    print(f"💻 Comando: {command}")
    
    try:
        if shell:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            if result.stdout:
                print(f"📄 Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ {description} - ERRO")
            if result.stderr:
                print(f"🚨 Error: {result.stderr[:200]}...")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEÇÃO: {str(e)}")
        return False

def check_python():
    """Verificar Python"""
    print("\n🐍 VERIFICANDO PYTHON...")
    result = run_command("python --version", "Verificando versão do Python")
    if not result:
        result = run_command("python3 --version", "Verificando versão do Python3")
    return result

def install_dependencies():
    """Instalar dependências"""
    print("\n📦 INSTALANDO DEPENDÊNCIAS...")
    
    # Pacotes essenciais
    packages = [
        "fastapi",
        "uvicorn[standard]",
        "pyjwt",
        "python-multipart",
        "email-validator",
        "requests",
        "python-dotenv"
    ]
    
    for package in packages:
        run_command(f"pip install {package}", f"Instalando {package}")

def check_files():
    """Verificar arquivos necessários"""
    print("\n📁 VERIFICANDO ARQUIVOS...")
    
    files_to_check = [
        "server_completo.py",
        "config.py", 
        "mocks.py",
        ".env"
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} - Encontrado")
        else:
            print(f"❌ {file} - NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist

def start_server():
    """Iniciar servidor"""
    print("\n🚀 INICIANDO SERVIDOR...")
    
    # Tentar diferentes métodos
    commands = [
        "python server_completo.py",
        "python3 server_completo.py",
        "uvicorn server_completo:app --host 127.0.0.1 --port 8000 --reload"
    ]
    
    for cmd in commands:
        print(f"\n🔄 Tentando: {cmd}")
        try:
            # Usar Popen para não bloquear
            process = subprocess.Popen(
                cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar um pouco para ver se inicia
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ Servidor iniciado com: {cmd}")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Comando falhou: {stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao executar {cmd}: {e}")
    
    return None

def test_server():
    """Testar servidor"""
    print("\n🔍 TESTANDO SERVIDOR...")
    
    import requests
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ SERVIDOR FUNCIONANDO!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🔧 Versão: {data.get('version')}")
            return True
        else:
            print(f"❌ Servidor retornou status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar servidor: {e}")
    
    return False

def main():
    """Função principal"""
    
    # 1. Verificar Python
    if not check_python():
        print("❌ Python não encontrado!")
        return False
    
    # 2. Instalar dependências
    install_dependencies()
    
    # 3. Verificar arquivos
    if not check_files():
        print("⚠️ Alguns arquivos estão faltando, mas continuando...")
    
    # 4. Iniciar servidor
    process = start_server()
    
    if not process:
        print("❌ Falha ao iniciar servidor!")
        return False
    
    # 5. Aguardar e testar
    print("\n⏳ Aguardando servidor inicializar...")
    time.sleep(5)
    
    # 6. Testar servidor
    if test_server():
        print("\n" + "="*70)
        print("🎉 SISTEMA INICIADO COM SUCESSO!")
        print("="*70)
        print("🌐 Acesse: http://127.0.0.1:8000")
        print("📚 Docs: http://127.0.0.1:8000/docs")
        print("🎛️ Dashboard: http://127.0.0.1:8000/dashboard")
        print("🔑 Login: admin@tecnocursos.com / admin123")
        print("="*70)
        
        # Manter o processo vivo
        try:
            print("\n⌨️ Pressione Ctrl+C para parar o servidor")
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            process.terminate()
            process.wait()
            print("✅ Servidor parado.")
        
        return True
    else:
        print("❌ Servidor não respondeu aos testes!")
        if process:
            process.terminate()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ FALHA NA INICIALIZAÇÃO!")
        print("🔧 Tente executar manualmente:")
        print("   python server_completo.py")
        print("   ou")
        print("   uvicorn server_completo:app --host 127.0.0.1 --port 8000")
        sys.exit(1)
    else:
        print("\n✅ SISTEMA FINALIZADO COM SUCESSO!")
        sys.exit(0)
