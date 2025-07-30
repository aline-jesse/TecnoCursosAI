#!/usr/bin/env python3
"""
Script para iniciar o TecnoCursos AI Backend na porta 8000
Resolve o problema de conexão ERR_CONNECTION_REFUSED
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def install_dependencies():
    """Instala dependências necessárias"""
    print("📦 Verificando dependências...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "fastapi", "uvicorn[standard]", "python-multipart"
        ], check=True, capture_output=True)
        print("✅ Dependências instaladas")
    except Exception as e:
        print(f"⚠️ Aviso: {e}")

def start_backend():
    """Inicia o backend na porta 8000"""
    print("🚀 Iniciando TecnoCursos AI Backend...")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("❤️ Health Check: http://localhost:8000/health")
    print("-" * 50)
    
    # Instalar dependências
    install_dependencies()
    
    # Iniciar servidor
    try:
        subprocess.run([sys.executable, "simple_backend.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("\n💡 Tente:")
        print("1. pip install fastapi uvicorn")
        print("2. python simple_backend.py")

if __name__ == "__main__":
    print("🔧 TecnoCursos AI - Correção de Conexão")
    print("="*50)
    print("🎯 Problema: ERR_CONNECTION_REFUSED na porta 8000")
    print("✅ Solução: Iniciando backend na porta correta")
    print("="*50)
    
    start_backend()
