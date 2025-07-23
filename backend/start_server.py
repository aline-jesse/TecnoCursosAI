"""
Script para iniciar o servidor FastAPI diretamente.
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("✅ Aplicação FastAPI importada com sucesso!")
    print(f"   Título: {app.title}")
    print(f"   Versão: {app.version}")
    
    # Tentar importar uvicorn
    try:
        import uvicorn
        print("\n✅ Uvicorn importado com sucesso!")
        print("\n🚀 Iniciando servidor na porta 8001...")
        print("   Acesse: http://localhost:8001")
        print("   Documentação: http://localhost:8001/docs")
        print("\n   Pressione CTRL+C para parar o servidor\n")
        
        # Iniciar o servidor
        uvicorn.run(app, host="0.0.0.0", port=8001)
        
    except ImportError as e:
        print(f"\n❌ Erro ao importar uvicorn: {e}")
        print("\nTentando instalar uvicorn...")
        os.system("pip install uvicorn")
        
except ImportError as e:
    print(f"❌ Erro ao importar a aplicação: {e}")
    print("\nVerifique se você está no diretório correto e se a aplicação está configurada corretamente.")
except Exception as e:
    print(f"❌ Erro inesperado: {e}") 