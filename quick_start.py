#!/usr/bin/env python3
"""
Quick Start - TecnoCursos AI
Inicialização rápida com logs visíveis
"""

def quick_start():
    print("🚀 TecnoCursos AI - Quick Start")
    print("="*50)
    
    # Teste básico de importação
    try:
        print("📦 Importando aplicação...")
        from app.main import app
        print("✅ Aplicação carregada com sucesso!")
        
        # Mostrar informações básicas
        print(f"📋 Título: {app.title}")
        print(f"📋 Versão: {app.version}")
        print(f"📋 Rotas disponíveis: {len(app.routes)}")
        
        return app
    except Exception as e:
        print(f"❌ Erro ao carregar aplicação: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_development_server(app):
    """Iniciar servidor de desenvolvimento"""
    print("\n🌐 Iniciando servidor de desenvolvimento...")
    
    try:
        import uvicorn
        
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False
        )
        
        server = uvicorn.Server(config)
        
        print("🌟 Servidor iniciando em: http://127.0.0.1:8000")
        print("📚 Documentação API: http://127.0.0.1:8000/docs")
        print("❤️ Health Check: http://127.0.0.1:8000/api/health")
        print("\n⌨️ Pressione Ctrl+C para parar o servidor")
        print("="*50)
        
        # Iniciar servidor
        server.run()
        
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Carregar aplicação
    app = quick_start()
    
    if app:
        # Iniciar servidor
        start_development_server(app)
    else:
        print("❌ Não foi possível iniciar o servidor")
        exit(1) 