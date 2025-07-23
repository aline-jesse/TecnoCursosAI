#!/usr/bin/env python3
"""
Script para corrigir automaticamente problemas do frontend React
TecnoCursos AI - Enterprise Edition 2025
"""

import subprocess
import sys
import os
import shutil
import time
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprime status com cores"""
    colors = {
        "SUCCESS": "🟢",
        "ERROR": "🔴", 
        "WARNING": "🟡",
        "INFO": "🔵"
    }
    print(f"{colors.get(status, '🔵')} {message}")

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

def fix_frontend_issues():
    """Corrige problemas do frontend React"""
    print_status("🚀 Iniciando correção automática do frontend React", "INFO")
    
    # 1. Limpar instalação anterior
    print_status("🧹 Limpando instalação anterior...", "INFO")
    run_command("rmdir /s /q node_modules", "Removendo node_modules")
    run_command("del package-lock.json", "Removendo package-lock.json")
    
    # 2. Limpar cache do npm
    print_status("🧹 Limpando cache do npm...", "INFO")
    run_command("npm cache clean --force", "Limpando cache npm")
    
    # 3. Verificar package.json
    print_status("📋 Verificando package.json...", "INFO")
    if not os.path.exists("package.json"):
        print_status("❌ package.json não encontrado", "ERROR")
        return False
    
    # 4. Instalar dependências básicas
    print_status("📦 Instalando dependências básicas...", "INFO")
    run_command("npm install", "Instalando dependências")
    
    # 5. Instalar react-scripts especificamente
    print_status("⚛️ Instalando react-scripts...", "INFO")
    run_command("npm install react-scripts@latest --save", "Instalando react-scripts")
    
    # 6. Verificar se react-scripts está instalado
    print_status("🔍 Verificando instalação...", "INFO")
    result = run_command("npx react-scripts --version", "Verificando versão do react-scripts")
    
    if result:
        print_status("✅ Frontend React corrigido com sucesso!", "SUCCESS")
        return True
    else:
        print_status("❌ Falha na correção do frontend", "ERROR")
        return False

def create_alternative_start_script():
    """Cria script alternativo para iniciar o frontend"""
    script_content = '''#!/usr/bin/env python3
"""
Script alternativo para iniciar o frontend React
"""
import subprocess
import sys
import os

def start_frontend():
    print("🚀 Iniciando frontend React...")
    
    # Verificar se node_modules existe
    if not os.path.exists("node_modules"):
        print("📦 Instalando dependências...")
        subprocess.run("npm install", shell=True)
    
    # Tentar iniciar com diferentes comandos
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
'''
    
    with open("start_frontend.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print_status("📝 Script alternativo criado: start_frontend.py", "SUCCESS")

def main():
    """Função principal"""
    print_status("🎯 CORREÇÃO AUTOMÁTICA DO FRONTEND REACT", "INFO")
    print_status("TecnoCursos AI - Enterprise Edition 2025", "INFO")
    print("=" * 60)
    
    # Corrigir problemas do frontend
    success = fix_frontend_issues()
    
    if success:
        print_status("✅ Correção concluída com sucesso!", "SUCCESS")
        create_alternative_start_script()
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python start_frontend.py")
        print("2. Ou execute: npm start")
        print("3. Acesse: http://localhost:3000")
        
    else:
        print_status("❌ Correção falhou", "ERROR")
        print("\n🔧 SOLUÇÕES ALTERNATIVAS:")
        print("1. Execute: python start_frontend.py")
        print("2. Ou use: npx create-react-app . --force")
        print("3. Ou use: npx next dev")

if __name__ == "__main__":
    main() 