#!/usr/bin/env python3
"""
DIAGNÓSTICO RÁPIDO - Por que o sistema está fora do ar?
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def verificar_arquivos():
    """Verificar se os arquivos necessários existem"""
    print("🔍 VERIFICANDO ARQUIVOS...")
    
    arquivos_importantes = [
        "backend/main.py",
        "backend/app/routers/dashboard.py", 
        "backend/app/services/notification_service.py",
        "simple_backend.py",
        "server_completo.py"
    ]
    
    encontrados = []
    for arquivo in arquivos_importantes:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
            encontrados.append(arquivo)
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
    
    return encontrados

def verificar_dependencias():
    """Verificar se as dependências estão instaladas"""
    print("\n📦 VERIFICANDO DEPENDÊNCIAS...")
    
    deps = ["fastapi", "uvicorn", "jinja2"]
    instaladas = []
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
            instaladas.append(dep)
        except ImportError:
            print(f"❌ {dep} - NÃO INSTALADO")
    
    return instaladas

def verificar_portas():
    """Verificar se alguma porta está em uso"""
    print("\n🔌 VERIFICANDO PORTAS...")
    
    portas = [8000, 8001, 3000, 5000]
    
    for porta in portas:
        try:
            response = requests.get(f"http://127.0.0.1:{porta}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Porta {porta} - SERVIDOR ATIVO")
                return porta
        except:
            pass
        
        try:
            response = requests.get(f"http://127.0.0.1:{porta}/", timeout=2)
            if response.status_code == 200:
                print(f"✅ Porta {porta} - SERVIDOR ATIVO")
                return porta
        except:
            pass
        
        print(f"❌ Porta {porta} - INATIVA")
    
    return None

def tentar_iniciar():
    """Tentar iniciar o servidor"""
    print("\n🚀 TENTANDO INICIAR SERVIDOR...")
    
    comandos = [
        "cd backend && uvicorn main:app --host 127.0.0.1 --port 8000",
        "python backend/main.py",
        "uvicorn backend.main:app --host 127.0.0.1 --port 8000",
        "python simple_backend.py"
    ]
    
    for comando in comandos:
        print(f"🔄 Tentando: {comando}")
        try:
            if "cd backend" in comando:
                # Executar em duas partes
                os.chdir("backend")
                resultado = subprocess.run(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"], 
                                         timeout=5, capture_output=True, text=True)
                os.chdir("..")
            else:
                resultado = subprocess.run(comando.split(), timeout=5, capture_output=True, text=True)
            
            print(f"📄 Output: {resultado.stdout[:100]}...")
            if resultado.stderr:
                print(f"🚨 Error: {resultado.stderr[:100]}...")
            
        except subprocess.TimeoutExpired:
            print("⏰ Comando executando em background...")
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return False

def main():
    """Diagnóstico completo"""
    print("🔧 DIAGNÓSTICO: Por que o sistema está fora do ar?")
    print("="*60)
    
    # 1. Verificar arquivos
    arquivos = verificar_arquivos()
    
    # 2. Verificar dependências
    deps = verificar_dependencias()
    
    # 3. Verificar portas
    porta_ativa = verificar_portas()
    
    # 4. Resultado do diagnóstico
    print("\n" + "="*60)
    print("📊 RESULTADO DO DIAGNÓSTICO:")
    print("="*60)
    
    if porta_ativa:
        print(f"✅ SISTEMA ONLINE na porta {porta_ativa}!")
        print(f"🌐 Acesse: http://127.0.0.1:{porta_ativa}")
        return
    
    if not arquivos:
        print("❌ PROBLEMA: Nenhum arquivo de servidor encontrado")
        print("🔧 SOLUÇÃO: Verificar se os arquivos estão no local correto")
        return
    
    if len(deps) < 2:
        print("❌ PROBLEMA: Dependências não instaladas")
        print("🔧 SOLUÇÃO: pip install fastapi uvicorn jinja2")
        return
    
    print("⚠️ PROBLEMA: Servidor não está rodando")
    print("🔧 SOLUÇÕES:")
    print("   1. Execute: python INICIAR_AGORA.py")
    print("   2. Ou: cd backend && uvicorn main:app --host 127.0.0.1 --port 8000")
    print("   3. Ou clique em: INICIAR_SERVIDOR.bat")
    
    # Tentar iniciar automaticamente
    if input("\n❓ Tentar iniciar automaticamente? (s/n): ").lower() == 's':
        tentar_iniciar()

if __name__ == "__main__":
    main()
