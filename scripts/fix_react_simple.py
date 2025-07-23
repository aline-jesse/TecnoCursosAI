#!/usr/bin/env python3
"""
Script Simples para Corrigir React - TecnoCursosAI
"""

import os
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 Corrigindo React App...")
    
    # 1. Limpar node_modules se existir
    if Path("node_modules").exists():
        print("🧹 Removendo node_modules...")
        try:
            shutil.rmtree("node_modules")
        except:
            print("⚠️ Não foi possível remover completamente node_modules")
    
    # 2. Remover package-lock.json se existir
    if Path("package-lock.json").exists():
        os.remove("package-lock.json")
    
    # 3. Instalar dependências
    print("📦 Instalando dependências...")
    try:
        subprocess.run(["npm", "install"], check=True, shell=True)
        print("✅ Dependências instaladas!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False
    
    # 4. Testar se funciona
    print("🧪 Testando React...")
    try:
        # Tentar iniciar o servidor
        process = subprocess.Popen(
            ["npm", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        # Aguardar um pouco
        import time
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ React iniciado com sucesso!")
            process.terminate()
            return True
        else:
            print("❌ Falha ao iniciar React")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 React corrigido com sucesso!")
        print("Execute: npm start")
    else:
        print("\n❌ Falha na correção do React") 