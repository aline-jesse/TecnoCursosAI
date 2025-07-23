#!/usr/bin/env python3
"""
Teste simples do editor sem dependências complexas
"""

import os
import sys
from pathlib import Path

# Definir variáveis de ambiente necessárias
os.environ.setdefault('DATABASE_URL', 'sqlite:///./tecnocursos.db')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-development')
os.environ.setdefault('ALLOWED_EXTENSIONS', '["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "pdf", "pptx"]')
os.environ.setdefault('OPENAI_API_KEY', '')
os.environ.setdefault('DEBUG', 'True')

# Agora importar a aplicação
try:
    from app.main import app
    print("✅ Aplicação importada com sucesso!")
    
    # Testar import do router do editor
    from app.routers.video_editor_advanced import router
    print("✅ Router do editor importado com sucesso!")
    
    print("\n📋 Rotas disponíveis no editor:")
    for route in router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"  {methods:10} {route.path}")
    
    print("\n🚀 Para iniciar o servidor:")
    print("python -m uvicorn app.main:app --reload --port 8000")
    
except Exception as e:
    print(f"❌ Erro ao importar: {e}")
    print("\n💡 Soluções:")
    print("1. Verifique se está na pasta correta (TecnoCursosAI)")
    print("2. Instale as dependências: pip install -r requirements.txt")
    print("3. Verifique as configurações em app/config.py")

if __name__ == "__main__":
    import uvicorn
    print("\n🔄 Iniciando servidor de teste...")
    
    # Criar diretórios necessários
    for dir_name in ['data/autosave', 'data/collaboration', 'data/ai_features', 'uploads', 'static/videos']:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="localhost", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")