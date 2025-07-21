#!/usr/bin/env python3
"""
Script de inicialização do TecnoCursos AI Server
"""

import sys
import os
import uvicorn

def main():
    """Inicializar servidor TecnoCursos AI"""
    print("🚀 Iniciando TecnoCursos AI Server...")
    print("="*50)
    
    # Importar a aplicação
    try:
        from app.main import app
        print("✅ Aplicação FastAPI carregada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar aplicação: {e}")
        return False
    
    # Configurações do servidor
    config = {
        "app": "app.main:app",
        "host": "localhost",
        "port": 8000,
        "reload": False,
        "log_level": "info",
        "access_log": True,
        "timeout_keep_alive": 30
    }
    
    print("📋 Configurações do servidor:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    print("\n🌐 Servidor será acessível em:")
    print(f"   • Frontend: http://localhost:8000")
    print(f"   • API Docs: http://localhost:8000/docs")
    print(f"   • Health Check: http://localhost:8000/api/health")
    
    print("\n🚀 Iniciando servidor...")
    print("="*50)
    
    try:
        # Iniciar servidor com uvicorn
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n👋 Servidor finalizado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no servidor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

