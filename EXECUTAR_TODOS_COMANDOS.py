#!/usr/bin/env python3
import subprocess
import sys
import os
import time

def executar_tudo():
    print("🚀 EXECUTANDO TODOS OS COMANDOS NECESSÁRIOS")
    print("="*60)
    
    # 1. Verificar Python
    print("[1/6] Verificando Python...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        print("❌ Python não encontrado!")
        return
    
    # 2. Instalar dependências
    print("\n[2/6] Instalando dependências...")
    deps = ["fastapi", "uvicorn", "python-multipart", "pyjwt"]
    for dep in deps:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep, "--quiet", "--user"], check=True)
            print(f"✅ {dep}")
        except:
            print(f"⚠️ {dep}")
    
    # 3. Verificar arquivos
    print("\n[3/6] Verificando arquivos...")
    if os.path.exists("simple_backend.py"):
        print("✅ simple_backend.py encontrado")
    else:
        print("❌ simple_backend.py não encontrado!")
        return
    
    # 4. Liberar porta
    print("\n[4/6] Liberando porta 8000...")
    try:
        if os.name == 'nt':
            subprocess.run('for /f "tokens=5" %a in (\'netstat -ano | findstr :8000\') do taskkill /F /PID %a 2>nul', shell=True)
        print("✅ Porta liberada")
    except:
        print("⚠️ Não foi possível liberar porta")
    
    # 5. Abrir navegadores
    print("\n[5/6] Preparando navegadores...")
    import webbrowser
    try:
        # Aguardar um pouco antes de abrir
        def abrir_navegadores():
            time.sleep(3)
            webbrowser.open("http://localhost:8000")
            time.sleep(1)
            webbrowser.open("http://localhost:8000/docs")
        
        import threading
        browser_thread = threading.Thread(target=abrir_navegadores, daemon=True)
        browser_thread.start()
        print("✅ Navegadores programados para abrir")
    except:
        print("⚠️ Não foi possível programar navegadores")
    
    # 6. Iniciar servidor
    print("\n[6/6] Iniciando servidor...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("❤️ Health: http://localhost:8000/health")
    print("🔑 Login: admin@tecnocursos.com / admin123")
    print("="*60)
    print("⚠️ Pressione Ctrl+C para parar o servidor")
    print("="*60)
    
    try:
        # Importar e executar
        import uvicorn
        from simple_backend import app
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("💡 Tente executar manualmente: python simple_backend.py")

if __name__ == "__main__":
    executar_tudo()
