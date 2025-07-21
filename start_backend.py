#!/usr/bin/env python3
"""
Script para iniciar o backend
"""
import subprocess
import sys

def start_backend():
    print("🚀 Iniciando backend FastAPI...")
    try:
        subprocess.run("python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload", 
                      shell=True, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")

if __name__ == "__main__":
    start_backend()
