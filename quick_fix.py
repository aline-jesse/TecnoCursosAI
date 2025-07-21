#!/usr/bin/env python3
"""
Quick fix para o TecnoCursos AI Editor
Remove variáveis de ambiente problemáticas e inicia o servidor
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=== TecnoCursos AI - Quick Fix ===")
    
    # Remover variáveis de ambiente problemáticas
    problematic_vars = [
        'ALLOWED_EXTENSIONS',
        'CORS_ORIGINS', 
        'CORS_ALLOW_METHODS',
        'CORS_ALLOW_HEADERS'
    ]
    
    for var in problematic_vars:
        if var in os.environ:
            del os.environ[var]
            print(f"Removida variável problemática: {var}")
    
    # Definir apenas as essenciais
    os.environ['DATABASE_URL'] = 'sqlite:///./tecnocursos.db'
    os.environ['SECRET_KEY'] = 'tecnocursos-development-key'
    os.environ['DEBUG'] = 'True'
    
    print("Configurações básicas definidas")
    
    # Criar diretórios
    directories = [
        'data/autosave', 'data/collaboration', 'data/ai_features',
        'uploads', 'static/videos', 'static/audios', 'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Diretórios criados")
    
    # Testar import
    try:
        from app.main import app
        print("✓ App importada com sucesso")
        
        # Iniciar servidor diretamente
        import uvicorn
        print("\nIniciando servidor...")
        print("URL: http://localhost:8000")
        print("Editor: http://localhost:8000/test_editor.html")
        print("Press Ctrl+C to stop")
        print("-" * 40)
        
        uvicorn.run(
            app,
            host="localhost",
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        print(f"Erro: {e}")
        print("\nIniciando servidor via subprocess...")
        
        # Fallback: usar subprocess
        try:
            subprocess.run([
                sys.executable, '-m', 'uvicorn', 'app.main:app',
                '--host', 'localhost', '--port', '8000'
            ])
        except KeyboardInterrupt:
            print("\nServidor parado")

if __name__ == "__main__":
    main()