#!/usr/bin/env python3
"""
Script para iniciar o frontend
"""
import subprocess
import sys
import os

def start_frontend():
    print("🚀 Iniciando frontend React...")
    
    commands = [
        "npm start",
        "npx react-scripts start",
        "npx next dev"
    ]
    
    for cmd in commands:
        print(f"🔄 Tentando: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
            break
        except subprocess.CalledProcessError:
            print(f"❌ Falha com: {cmd}")
            continue

if __name__ == "__main__":
    start_frontend()
