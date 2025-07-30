import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando TecnoCursos AI Backend na porta 8000...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    try:
        from simple_backend import app
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"Erro: {e}")
        print("Execute: pip install fastapi uvicorn")
