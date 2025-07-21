#!/usr/bin/env python3
"""
Script para corrigir problemas do banco de dados
TecnoCursos AI - Enterprise Edition 2025
"""

import subprocess
import sys
import os
import sqlite3
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

def fix_database_relationships():
    """Corrige problemas de relacionamentos no banco de dados"""
    print_status("🔧 Corrigindo problemas de relacionamentos no banco de dados", "INFO")
    
    # Verificar se o banco existe
    db_path = "app/database.db"
    if not os.path.exists(db_path):
        print_status("❌ Banco de dados não encontrado", "ERROR")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print_status(f"📋 Tabelas encontradas: {', '.join(tables)}", "INFO")
        
        # Corrigir relacionamento Asset.scene
        print_status("🔧 Corrigindo relacionamento Asset.scene...", "INFO")
        
        # Verificar se a tabela assets tem a coluna scene_id
        cursor.execute("PRAGMA table_info(assets);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'scene_id' not in columns:
            print_status("➕ Adicionando coluna scene_id à tabela assets", "INFO")
            cursor.execute("ALTER TABLE assets ADD COLUMN scene_id INTEGER;")
        
        # Verificar se a tabela scenes existe
        if 'scenes' not in tables:
            print_status("➕ Criando tabela scenes", "INFO")
            cursor.execute("""
                CREATE TABLE scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        
        # Criar índices para melhorar performance
        print_status("📊 Criando índices...", "INFO")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_scene_id ON assets(scene_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scenes_project_id ON scenes(project_id);")
        
        # Commit das alterações
        conn.commit()
        print_status("✅ Problemas de relacionamento corrigidos", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"❌ Erro ao corrigir banco de dados: {e}", "ERROR")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def recreate_database():
    """Recria o banco de dados do zero"""
    print_status("🔄 Recriando banco de dados...", "INFO")
    
    try:
        # Remover banco antigo
        db_path = "app/database.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print_status("🗑️ Banco de dados antigo removido", "INFO")
        
        # Executar migrações
        print_status("🔄 Executando migrações...", "INFO")
        result = subprocess.run("alembic upgrade head", shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("✅ Banco de dados recriado com sucesso", "SUCCESS")
            return True
        else:
            print_status(f"❌ Erro nas migrações: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Erro ao recriar banco: {e}", "ERROR")
        return False

def test_database_connection():
    """Testa conexão com o banco de dados"""
    print_status("🧪 Testando conexão com banco de dados...", "INFO")
    
    try:
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        
        # Teste básico
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print_status("✅ Conexão com banco de dados OK", "SUCCESS")
            return True
        else:
            print_status("❌ Falha no teste de conexão", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Erro na conexão: {e}", "ERROR")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Função principal"""
    print_status("🎯 CORREÇÃO AUTOMÁTICA DO BANCO DE DADOS", "INFO")
    print_status("TecnoCursos AI - Enterprise Edition 2025", "INFO")
    print("=" * 60)
    
    # Testar conexão atual
    if test_database_connection():
        # Tentar corrigir relacionamentos
        if fix_database_relationships():
            print_status("✅ Correção concluída com sucesso!", "SUCCESS")
        else:
            print_status("🔄 Tentando recriar banco de dados...", "WARNING")
            if recreate_database():
                print_status("✅ Banco de dados recriado com sucesso!", "SUCCESS")
            else:
                print_status("❌ Falha na correção do banco de dados", "ERROR")
    else:
        print_status("🔄 Recriando banco de dados...", "WARNING")
        if recreate_database():
            print_status("✅ Banco de dados recriado com sucesso!", "SUCCESS")
        else:
            print_status("❌ Falha na correção do banco de dados", "ERROR")

if __name__ == "__main__":
    main() 