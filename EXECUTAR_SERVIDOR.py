#!/usr/bin/env python3
"""
EXECUTOR ALTERNATIVO - TecnoCursos AI
Para contornar problemas com terminais
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser

def executar_servidor():
    """Executar servidor em thread separada"""
    try:
        # Tentar importar e executar o servidor
        import simple_backend
        print("✅ Módulo simple_backend carregado")
        
        # Executar o servidor
        if hasattr(simple_backend, 'app'):
            import uvicorn
            print("🚀 Iniciando servidor uvicorn...")
            uvicorn.run(
                simple_backend.app,
                host="127.0.0.1", 
                port=8000,
                log_level="info"
            )
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("🔧 Tente: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 EXECUTOR ALTERNATIVO - TecnoCursos AI")
    print("="*50)
    
    # Verificar se o arquivo existe
    if not os.path.exists("simple_backend.py"):
        print("❌ Arquivo simple_backend.py não encontrado!")
        return
    
    print("✅ Arquivo encontrado: simple_backend.py")
    
    # Executar servidor em thread
    servidor_thread = threading.Thread(target=executar_servidor)
    servidor_thread.daemon = True
    servidor_thread.start()
    
    # Aguardar um pouco
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    # Abrir navegador
    print("🌐 Abrindo navegador...")
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except:
        print("⚠️ Não foi possível abrir o navegador automaticamente")
    
    print("\n" + "="*50)
    print("🎉 SERVIDOR ATIVO!")
    print("="*50)
    print("🌐 Dashboard: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("❤️ Health: http://127.0.0.1:8000/health")
    print("🔑 Login: admin@tecnocursos.com / admin123")
    print("="*50)
    
    # Manter o programa rodando
    try:
        print("\n⌨️ Pressione Ctrl+C para parar")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        print("✅ Servidor parado")

if __name__ == "__main__":
    main()
