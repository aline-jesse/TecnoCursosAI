#!/usr/bin/env python3
"""
INICIALIZADOR RÁPIDO - TecnoCursos AI
Detecta e inicia o servidor automaticamente
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def encontrar_servidor():
    """Encontrar arquivo do servidor"""
    possibilidades = [
        "backend/main.py",
        "main.py", 
        "server.py",
        "app.py",
        "backend/app/main.py"
    ]
    
    for arquivo in possibilidades:
        if os.path.exists(arquivo):
            print(f"✅ Servidor encontrado: {arquivo}")
            return arquivo
    
    return None

def instalar_dependencias():
    """Instalar dependências básicas"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "jinja2", "python-multipart"], 
                      check=True, capture_output=True)
        print("✅ Dependências instaladas")
        return True
    except:
        print("❌ Erro ao instalar dependências")
        return False

def iniciar_servidor(arquivo_servidor):
    """Iniciar servidor"""
    print(f"🚀 Iniciando servidor: {arquivo_servidor}")
    
    # Comandos possíveis
    comandos = []
    
    if "backend/" in arquivo_servidor:
        # Se está na pasta backend
        comandos.extend([
            f"cd backend && uvicorn main:app --host 127.0.0.1 --port 8000 --reload",
            f"cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000",
            f"cd backend && python main.py"
        ])
    else:
        comandos.extend([
            f"uvicorn {arquivo_servidor.replace('.py', '').replace('/', '.')}:app --host 127.0.0.1 --port 8000 --reload",
            f"python {arquivo_servidor}"
        ])
    
    for comando in comandos:
        print(f"🔄 Tentando: {comando}")
        try:
            # Dividir comando se contém &&
            if " && " in comando:
                partes = comando.split(" && ")
                if len(partes) == 2:
                    os.chdir(partes[0].replace("cd ", ""))
                    processo = subprocess.Popen(partes[1].split(), shell=True)
                else:
                    processo = subprocess.Popen(comando, shell=True)
            else:
                processo = subprocess.Popen(comando, shell=True)
            
            # Aguardar um pouco
            time.sleep(3)
            
            # Verificar se o processo ainda está rodando
            if processo.poll() is None:
                print(f"✅ Servidor iniciado com: {comando}")
                return processo
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return None

def testar_conexao():
    """Testar se servidor está respondendo"""
    print("🔍 Testando conexão...")
    
    urls = [
        "http://127.0.0.1:8000/health",
        "http://127.0.0.1:8000/",
        "http://localhost:8000/health",
        "http://localhost:8000/"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Servidor respondendo em: {url}")
                return True
        except:
            continue
    
    print("❌ Servidor não está respondendo")
    return False

def main():
    """Função principal"""
    print("🚀 INICIALIZADOR RÁPIDO - TecnoCursos AI")
    print("="*50)
    
    # 1. Encontrar servidor
    servidor = encontrar_servidor()
    if not servidor:
        print("❌ Nenhum arquivo de servidor encontrado!")
        return False
    
    # 2. Instalar dependências
    if not instalar_dependencias():
        print("⚠️ Continuando sem instalar dependências...")
    
    # 3. Iniciar servidor
    processo = iniciar_servidor(servidor)
    if not processo:
        print("❌ Falha ao iniciar servidor!")
        return False
    
    # 4. Aguardar inicialização
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(5)
    
    # 5. Testar conexão
    if testar_conexao():
        print("\n" + "="*50)
        print("🎉 SERVIDOR ONLINE!")
        print("="*50)
        print("🌐 Acesse: http://127.0.0.1:8000")
        print("📚 Docs: http://127.0.0.1:8000/docs")
        print("❤️ Health: http://127.0.0.1:8000/health")
        print("="*50)
        
        try:
            print("\n⌨️ Pressione Ctrl+C para parar")
            processo.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            processo.terminate()
            print("✅ Servidor parado")
        
        return True
    else:
        print("❌ Servidor não respondeu aos testes")
        if processo:
            processo.terminate()
        return False

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        print("\n🔧 SOLUÇÕES MANUAIS:")
        print("1. cd backend && uvicorn main:app --host 127.0.0.1 --port 8000")
        print("2. python backend/main.py")
        print("3. Verificar se as dependências estão instaladas")
        sys.exit(1)
