#!/usr/bin/env python3
"""
Script para instalar dependências do frontend React
TecnoCursos AI - Enterprise Edition 2025
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(command, description):
    """Executa um comando e trata erros"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}: {e}")
        print(f"Comando: {command}")
        print(f"Erro: {e.stderr}")
        return False

def clean_node_modules():
    """Remove node_modules e package-lock.json"""
    print("🧹 Limpando instalação anterior...")
    
    # Remover node_modules
    if os.path.exists("node_modules"):
        try:
            shutil.rmtree("node_modules")
            print("✅ node_modules removido")
        except Exception as e:
            print(f"⚠️ Erro ao remover node_modules: {e}")
    
    # Remover package-lock.json
    if os.path.exists("package-lock.json"):
        try:
            os.remove("package-lock.json")
            print("✅ package-lock.json removido")
        except Exception as e:
            print(f"⚠️ Erro ao remover package-lock.json: {e}")

def install_dependencies():
    """Instala as dependências do frontend"""
    print("📦 Instalando dependências do frontend...")
    
    # Limpar cache do npm
    if not run_command("npm cache clean --force", "Limpando cache do npm"):
        return False
    
    # Instalar dependências
    if not run_command("npm install --legacy-peer-deps", "Instalando dependências"):
        return False
    
    return True

def verify_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("🔍 Verificando instalação...")
    
    # Verificar se react-scripts está disponível
    try:
        result = subprocess.run(
            ["npx", "react-scripts", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("✅ react-scripts instalado corretamente")
            return True
        else:
            print("❌ react-scripts não está funcionando")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar react-scripts: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Instalador do Frontend React - TecnoCursos AI")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("package.json"):
        print("❌ package.json não encontrado. Execute este script no diretório raiz do projeto.")
        sys.exit(1)
    
    # Limpar instalação anterior
    clean_node_modules()
    
    # Instalar dependências
    if not install_dependencies():
        print("❌ Falha na instalação das dependências")
        sys.exit(1)
    
    # Verificar instalação
    if not verify_installation():
        print("❌ Falha na verificação da instalação")
        sys.exit(1)
    
    print("\n🎉 Frontend React instalado com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute: npm start")
    print("2. Acesse: http://localhost:3000")
    print("3. Para build: npm run build")

if __name__ == "__main__":
    main() 