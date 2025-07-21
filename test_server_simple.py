#!/usr/bin/env python3
"""
Servidor de teste simples para TecnoCursos AI
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Criar aplicação simples
app = FastAPI(
    title="TecnoCursos AI - Teste",
    description="Servidor de teste simples",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "TecnoCursos AI funcionando!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Sistema funcionando"}

@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "API funcionando"
    }

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste...")
    print("📚 Documentação: http://127.0.0.1:8000/docs")
    print("🔍 Health Check: http://127.0.0.1:8000/health")
    print("🌐 API Health: http://127.0.0.1:8000/api/health")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True) 