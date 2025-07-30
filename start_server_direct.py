import os
import subprocess
import sys
import time

def main():
    print("🚀 TecnoCursos AI - Iniciador Automático")
    print("="*60)
    
    # Verificar diretório
    print(f"📁 Diretório: {os.getcwd()}")
    
    # Instalar dependências
    print("📦 Instalando dependências...")
    deps = ["fastapi", "uvicorn[standard]", "python-multipart", "pyjwt"]
    
    for dep in deps:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep, "--quiet"
            ], check=True, timeout=30)
            print(f"✅ {dep}")
        except Exception as e:
            print(f"⚠️ {dep}: {str(e)[:50]}")
    
    print("\n🌐 Iniciando servidor...")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("❤️ Health: http://localhost:8000/health")
    print("\n🔑 Credenciais de teste:")
    print("Email: admin@tecnocursos.com")
    print("Senha: admin123")
    print("\n" + "="*60)
    
    # Tentar importar e executar
    try:
        import uvicorn
        print("✅ uvicorn importado")
        
        # Importar app
        sys.path.insert(0, os.getcwd())
        from simple_backend import app
        print("✅ App importada")
        
        # Iniciar servidor
        print("🚀 Iniciando servidor na porta 8000...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False
        )
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Execute: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print("💡 Verifique se o arquivo simple_backend.py existe")

if __name__ == "__main__":
    main()
