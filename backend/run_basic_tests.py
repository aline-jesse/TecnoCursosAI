"""
Script para executar testes básicos sem depender do pytest.
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Testa se os módulos principais podem ser importados."""
    print("\n=== Testando imports básicos ===")
    try:
        # Testar imports básicos
        from app.main import app
        print("✅ Importou app.main")
        
        from app.database import get_db
        print("✅ Importou app.database")
        
        from app.models import User, Project, Video
        print("✅ Importou app.models")
        
        from app.schemas import UserCreate, UserResponse
        print("✅ Importou app.schemas")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_app_startup():
    """Testa se a aplicação pode ser inicializada."""
    print("\n=== Testando inicialização da aplicação ===")
    try:
        from app.main import app
        
        # Verificar se a aplicação tem rotas
        routes = [route.path for route in app.routes]
        print(f"✅ Aplicação inicializada com {len(routes)} rotas")
        
        # Listar algumas rotas
        print("\nAlgumas rotas disponíveis:")
        for route in routes[:10]:  # Mostrar apenas as primeiras 10
            print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar aplicação: {e}")
        return False

def test_database_connection():
    """Testa se a conexão com banco de dados pode ser estabelecida."""
    print("\n=== Testando conexão com banco de dados ===")
    try:
        from app.database import engine
        
        # Testar conexão
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Conexão com banco de dados funcionou")
            return True
            
    except Exception as e:
        print(f"⚠️ Conexão com banco falhou (pode ser esperado): {e}")
        return False

def test_fastapi_server():
    """Testa se o servidor FastAPI pode ser iniciado."""
    print("\n=== Testando servidor FastAPI ===")
    try:
        from app.main import app
        print("✅ FastAPI app importado com sucesso")
        print(f"   Título: {app.title}")
        print(f"   Versão: {app.version}")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar FastAPI app: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=== EXECUTANDO TESTES BÁSICOS ===")
    print("=" * 50)
    
    results = []
    
    # Executar testes
    results.append(("Imports básicos", test_basic_imports()))
    results.append(("Inicialização da app", test_app_startup()))
    results.append(("Conexão com banco", test_database_connection()))
    results.append(("Servidor FastAPI", test_fastapi_server()))
    
    # Resumo
    print("\n" + "=" * 50)
    print("=== RESUMO DOS TESTES ===")
    print("=" * 50)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️ {total - passed} testes falharam")

if __name__ == "__main__":
    main() 