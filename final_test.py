#!/usr/bin/env python3
"""
TecnoCursos AI - Teste Final Completo
Inicia servidor com todas as correções aplicadas
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def kill_existing_servers():
    """Mata processos existentes do uvicorn"""
    try:
        # Windows
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, text=True)
        time.sleep(2)
    except:
        pass

def main():
    print("=== TecnoCursos AI - Inicializacao Final ===")
    
    # Matar servidores existentes
    print("Parando servidores existentes...")
    kill_existing_servers()
    
    # Configurar ambiente
    os.environ['DATABASE_URL'] = 'sqlite:///./tecnocursos.db'
    os.environ['SECRET_KEY'] = 'tecnocursos-final-key'
    os.environ['DEBUG'] = 'True'
    
    # Criar diretórios
    directories = [
        'data/autosave', 'data/collaboration', 'data/ai_features',
        'uploads', 'static/videos', 'static/audios', 'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Diretorios criados")
    
    # Testar importacao
    try:
        from app.main import app
        print("✓ App importada com sucesso")
        
        # Testar router do editor
        from app.routers.video_editor_advanced import router
        print(f"✓ Router carregado com {len(router.routes)} rotas")
        
        # Verificar se os endpoints de teste existem
        test_endpoints = []
        for route in router.routes:
            if hasattr(route, 'path'):
                if 'test' in route.path:
                    test_endpoints.append(route.path)
        
        if test_endpoints:
            print(f"✓ Endpoints de teste encontrados: {len(test_endpoints)}")
            for endpoint in test_endpoints:
                print(f"  - {endpoint}")
        else:
            print("! Nenhum endpoint de teste encontrado")
        
    except Exception as e:
        print(f"✗ Erro ao importar: {e}")
        return
    
    print()
    print("=== INICIANDO SERVIDOR ===")
    print("URL Principal: http://localhost:8000")
    print("Editor Teste: http://localhost:8000/test_editor.html")
    print("Editor Completo: http://localhost:8000/editor_integrated.html")
    print("Documentacao: http://localhost:8000/docs")
    print()
    print("Pressione Ctrl+C para parar")
    print("-" * 50)
    
    try:
        # Usar uvicorn diretamente
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="localhost",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuario")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()