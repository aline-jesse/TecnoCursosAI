#!/usr/bin/env python3
"""
Fix SQLAlchemy compatibility with Python 3.13
Temporary workaround for the TypingOnly inheritance issue
"""

import sys
import os

def apply_sqlalchemy_patch():
    """Aplica patch temporário para SQLAlchemy + Python 3.13"""
    try:
        # Patch para TypingOnly no langhelpers
        import sqlalchemy.util.langhelpers as langhelpers
        
        # Salvar a função original
        original_init_subclass = langhelpers.TypingOnly.__init_subclass__
        
        def patched_init_subclass(cls, **kwargs):
            """Versão corrigida que ignora atributos problemáticos"""
            # Remove atributos problemáticos antes de chamar o original
            for attr in ['__firstlineno__', '__static_attributes__']:
                if hasattr(cls, attr):
                    delattr(cls, attr)
            
            # Chama o método original
            if hasattr(original_init_subclass, '__func__'):
                original_init_subclass.__func__(cls, **kwargs)
            else:
                original_init_subclass(cls, **kwargs)
        
        # Aplicar o patch
        langhelpers.TypingOnly.__init_subclass__ = patched_init_subclass
        
        print("✅ Patch SQLAlchemy aplicado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar patch: {e}")
        return False

def upgrade_sqlalchemy():
    """Tenta atualizar SQLAlchemy para versão compatível"""
    try:
        import subprocess
        print("🔄 Tentando atualizar SQLAlchemy...")
        
        # Tentar instalar versão mais recente
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "sqlalchemy>=2.0.25"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SQLAlchemy atualizado com sucesso")
            return True
        else:
            print(f"⚠️ Erro na atualização: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar SQLAlchemy: {e}")
        return False

def create_simple_database_alternative():
    """Cria alternativa simples sem SQLAlchemy"""
    database_content = '''"""
Banco de dados simplificado para TecnoCursos AI
Versão alternativa sem SQLAlchemy para compatibilidade Python 3.13
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class SimpleDB:
    """Banco de dados simplificado usando sqlite3 puro"""
    
    def __init__(self, db_path: str = "tecnocursos_simple.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Inicializa as tabelas básicas"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    project_id INTEGER,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            
            conn.commit()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Executa query e retorna resultados como lista de dicionários"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do banco"""
        try:
            # Testar conexão
            result = self.execute_query("SELECT 1 as test")
            
            # Contar registros básicos
            users_count = self.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
            projects_count = self.execute_query("SELECT COUNT(*) as count FROM projects")[0]['count']
            
            return {
                "status": "connected",
                "database_type": "sqlite3_simple",
                "users_count": users_count,
                "projects_count": projects_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instância global
simple_db = SimpleDB()

def get_simple_db():
    """Dependency para obter instância do banco simples"""
    return simple_db

class SimpleBase:
    """Base class alternativa para models"""
    pass
'''
    
    with open("backend/app/simple_database.py", "w", encoding="utf-8") as f:
        f.write(database_content)
    
    print("✅ Banco de dados alternativo criado: backend/app/simple_database.py")

def create_compatibility_main():
    """Cria versão do main.py compatível com Python 3.13"""
    main_content = '''#!/usr/bin/env python3
"""
TecnoCursos AI - Versão Compatível Python 3.13
Servidor principal sem dependências problemáticas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
import time
from datetime import datetime
from pathlib import Path

# Usar banco simples ao invés de SQLAlchemy
try:
    from app.simple_database import get_simple_db, simple_db
    database_available = True
except ImportError:
    database_available = False

# Criar aplicação
app = FastAPI(
    title="TecnoCursos AI - Compatible Edition",
    description="Versão compatível com Python 3.13",
    version="2.0.1-compatible"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tempo de início
app.state.start_time = time.time()

@app.get("/")
async def root():
    """Página inicial"""
    return HTMLResponse("""
    <html>
        <head><title>TecnoCursos AI - Compatible</title></head>
        <body>
            <h1>🚀 TecnoCursos AI - Compatible Edition</h1>
            <p>Servidor funcionando com Python 3.13!</p>
            <ul>
                <li><a href="/api/health">Health Check</a></li>
                <li><a href="/docs">Documentação da API</a></li>
                <li><a href="/api/info">Informações do Sistema</a></li>
            </ul>
        </body>
    </html>
    """)

@app.get("/api/health")
async def health_check():
    """Health check compatível"""
    uptime = time.time() - app.state.start_time
    
    status = {
        "status": "healthy",
        "version": "2.0.1-compatible",
        "python_version": "3.13",
        "uptime_seconds": uptime,
        "database_available": database_available,
        "timestamp": datetime.now().isoformat()
    }
    
    if database_available:
        try:
            db_status = simple_db.get_health_status()
            status["database_status"] = db_status
        except Exception as e:
            status["database_error"] = str(e)
    
    return status

@app.get("/api/info")
async def system_info():
    """Informações do sistema"""
    return {
        "name": "TecnoCursos AI - Compatible Edition",
        "version": "2.0.1-compatible",
        "description": "Versão compatível com Python 3.13",
        "python_version": "3.13",
        "features": {
            "basic_api": True,
            "database": database_available,
            "file_upload": False,  # Para implementar
            "video_generation": False  # Para implementar
        },
        "endpoints": {
            "health": "/api/health",
            "info": "/api/info",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_compatible:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
'''
    
    with open("main_compatible.py", "w", encoding="utf-8") as f:
        f.write(main_content)
    
    print("✅ Servidor compatível criado: main_compatible.py")

def main():
    """Função principal"""
    print("🔧 SQLAlchemy + Python 3.13 Compatibility Fix")
    print("=" * 50)
    
    print("\n1. 🔄 Tentando atualizar SQLAlchemy...")
    if upgrade_sqlalchemy():
        print("✅ Tente executar o servidor novamente")
        return True
    
    print("\n2. 🩹 Tentando aplicar patch temporário...")
    if apply_sqlalchemy_patch():
        print("✅ Patch aplicado - teste o servidor")
        return True
    
    print("\n3. 🔀 Criando alternativas compatíveis...")
    create_simple_database_alternative()
    create_compatibility_main()
    
    print("\n✅ Soluções alternativas criadas!")
    print("\n🚀 Para testar:")
    print("   python main_compatible.py")
    print("\n📚 Documentação: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    main() 