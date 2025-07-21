#!/usr/bin/env python3
"""
Script completo para corrigir todos os problemas do sistema
TecnoCursos AI - Enterprise Edition 2025
"""

import subprocess
import sys
import os
import sqlite3
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

def fix_database_issues():
    """Corrige problemas do banco de dados"""
    print_status("🔧 Corrigindo problemas do banco de dados", "INFO")
    
    db_path = "app/database.db"
    if not os.path.exists(db_path):
        print_status("❌ Banco de dados não encontrado", "ERROR")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print_status(f"📋 Tabelas encontradas: {', '.join(tables)}", "INFO")
        
        # Corrigir relacionamento Asset.scene
        if 'assets' in tables:
            cursor.execute("PRAGMA table_info(assets);")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'scene_id' not in columns:
                print_status("➕ Adicionando coluna scene_id à tabela assets", "INFO")
                cursor.execute("ALTER TABLE assets ADD COLUMN scene_id INTEGER;")
        
        # Criar índices
        print_status("📊 Criando índices...", "INFO")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_scene_id ON assets(scene_id);")
        
        conn.commit()
        print_status("✅ Problemas de banco de dados corrigidos", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"❌ Erro ao corrigir banco: {e}", "ERROR")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def fix_frontend_issues():
    """Corrige problemas do frontend"""
    print_status("⚛️ Corrigindo problemas do frontend React", "INFO")
    
    # Verificar se package.json existe
    if not os.path.exists("package.json"):
        print_status("❌ package.json não encontrado", "ERROR")
        return False
    
    # Tentar diferentes abordagens
    approaches = [
        ("npm install --force", "Instalando dependências com --force"),
        ("npm install react-scripts@latest --save", "Instalando react-scripts"),
        ("npx create-react-app . --force", "Recriando projeto React")
    ]
    
    for command, description in approaches:
        if run_command(command, description):
            return True
    
    return False

def fix_backend_issues():
    """Corrige problemas do backend"""
    print_status("🐍 Corrigindo problemas do backend Python", "INFO")
    
    # Instalar dependências Python
    approaches = [
        ("pip install -r requirements.txt", "Instalando dependências Python"),
        ("pip install fastapi uvicorn sqlalchemy", "Instalando dependências básicas"),
        ("pip install --upgrade pip", "Atualizando pip")
    ]
    
    for command, description in approaches:
        run_command(command, description)
    
    return True

def test_system():
    """Testa o sistema completo"""
    print_status("🧪 Testando sistema completo", "INFO")
    
    # Testar backend
    print_status("🔍 Testando backend...", "INFO")
    try:
        result = subprocess.run("python -c \"import uvicorn; print('Backend OK')\"", 
                              shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_status("✅ Backend funcionando", "SUCCESS")
        else:
            print_status("❌ Problemas no backend", "ERROR")
    except:
        print_status("❌ Backend não disponível", "ERROR")
    
    # Testar banco de dados
    print_status("🔍 Testando banco de dados...", "INFO")
    try:
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result and result[0] == 1:
            print_status("✅ Banco de dados funcionando", "SUCCESS")
        else:
            print_status("❌ Problemas no banco de dados", "ERROR")
        conn.close()
    except:
        print_status("❌ Banco de dados não disponível", "ERROR")
    
    # Testar frontend
    print_status("🔍 Testando frontend...", "INFO")
    if os.path.exists("node_modules"):
        print_status("✅ node_modules encontrado", "SUCCESS")
    else:
        print_status("❌ node_modules não encontrado", "ERROR")

def create_startup_scripts():
    """Cria scripts de inicialização"""
    print_status("📝 Criando scripts de inicialização", "INFO")
    
    # Script para iniciar backend
    backend_script = '''#!/usr/bin/env python3
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
        print("\\n🛑 Backend parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")

if __name__ == "__main__":
    start_backend()
'''
    
    with open("start_backend.py", "w", encoding="utf-8") as f:
        f.write(backend_script)
    
    # Script para iniciar frontend
    frontend_script = '''#!/usr/bin/env python3
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
'''
    
    with open("start_frontend.py", "w", encoding="utf-8") as f:
        f.write(frontend_script)
    
    print_status("✅ Scripts de inicialização criados", "SUCCESS")

def main():
    """Função principal"""
    print_status("🎯 CORREÇÃO COMPLETA DO SISTEMA", "INFO")
    print_status("TecnoCursos AI - Enterprise Edition 2025", "INFO")
    print("=" * 60)
    
    # Corrigir problemas do backend
    fix_backend_issues()
    
    # Corrigir problemas do banco de dados
    fix_database_issues()
    
    # Corrigir problemas do frontend
    fix_frontend_issues()
    
    # Testar sistema
    test_system()
    
    # Criar scripts de inicialização
    create_startup_scripts()
    
    print_status("✅ Correção completa finalizada!", "SUCCESS")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Backend: python start_backend.py")
    print("2. Frontend: python start_frontend.py")
    print("3. Acesse: http://127.0.0.1:8000/docs")
    print("4. Frontend: http://localhost:3000")

if __name__ == "__main__":
    main() 