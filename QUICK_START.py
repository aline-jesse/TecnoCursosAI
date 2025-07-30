#!/usr/bin/env python3
import os
import sys

# Executar direto
try:
    import uvicorn
    print("🚀 Iniciando TecnoCursos AI...")
    uvicorn.run("simple_backend:app", host="127.0.0.1", port=8000, reload=True)
except ImportError:
    print("Instalando uvicorn...")
    os.system("pip install uvicorn fastapi")
    import uvicorn
    uvicorn.run("simple_backend:app", host="127.0.0.1", port=8000, reload=True)
except Exception as e:
    print(f"Erro: {e}")
    print("Execute: python simple_backend.py")
