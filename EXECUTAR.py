#!/usr/bin/env python3
"""
EXECUTAR AGORA - TecnoCursos AI
Servidor Backend na porta 8000
"""

if __name__ == "__main__":
    try:
        print("🚀 TecnoCursos AI - Iniciando...")
        
        # Importar diretamente
        import uvicorn
        
        # Executar servidor
        uvicorn.run(
            "simple_backend:app",
            host="127.0.0.1", 
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError:
        print("❌ Instale: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Erro: {e}")
