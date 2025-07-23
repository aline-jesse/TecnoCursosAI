#!/usr/bin/env python3
"""
Script de teste para verificar o sistema reorganizado do TecnoCursos AI
"""

import sys
import os
import requests
import time
import subprocess
import logging
from pathlib import Path
from threading import Thread


def setup_logging():
    """Configurar logging para os testes"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def test_imports():
    """Testar se os imports básicos funcionam"""
    logger = logging.getLogger(__name__)
    
    try:
        # Adicionar path do backend
        backend_path = Path(__file__).parent.parent.parent.parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Testar imports básicos
        from app.core.config import get_settings
        from app.core.database import Base, create_database
        from app.models.base import User, Project
        from app.schemas.base import HealthCheck, SystemStatus
        
        logger.info("✅ Imports básicos funcionando")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos imports: {e}")
        return False


def test_database():
    """Testar criação do banco de dados"""
    logger = logging.getLogger(__name__)
    
    try:
        backend_path = Path(__file__).parent.parent.parent.parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from app.core.database import create_database, check_database_health_sync
        
        # Criar banco de dados
        create_database()
        
        # Verificar saúde
        if check_database_health_sync():
            logger.info("✅ Banco de dados funcionando")
            return True
        else:
            logger.error("❌ Banco de dados com problemas")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no banco de dados: {e}")
        return False


def start_server_background():
    """Iniciar servidor em background para testes"""
    backend_path = Path(__file__).parent.parent.parent.parent / "backend"
    os.chdir(backend_path)
    
    # Configurar ambiente de teste
    os.environ["DEBUG"] = "true"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"
    
    # Iniciar servidor
    subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "localhost",
        "--port", "8001",  # Porta diferente para teste
        "--log-level", "error"  # Reduzir logs
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def test_api_endpoints():
    """Testar endpoints da API"""
    logger = logging.getLogger(__name__)
    
    # Iniciar servidor em background
    server_thread = Thread(target=start_server_background, daemon=True)
    server_thread.start()
    
    # Aguardar servidor inicializar
    time.sleep(5)
    
    base_url = "http://localhost:8001"
    
    tests = [
        ("/", "Página inicial"),
        ("/api/health", "Health check"),
        ("/api/status", "Status do sistema"),
        ("/docs", "Documentação"),
    ]
    
    results = []
    
    for endpoint, description in tests:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {description}: OK")
                results.append(True)
            else:
                logger.warning(f"⚠️ {description}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            logger.error(f"❌ {description}: Erro - {e}")
            results.append(False)
    
    return all(results)


def test_configuration():
    """Testar sistema de configuração"""
    logger = logging.getLogger(__name__)
    
    try:
        backend_path = Path(__file__).parent.parent.parent.parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from app.core.config import get_settings, get_database_url, is_development
        
        settings = get_settings()
        
        # Verificar configurações básicas
        assert settings.app_name == "TecnoCursos AI"
        assert settings.version == "2.0.0"
        assert isinstance(get_database_url(), str)
        assert isinstance(is_development(), bool)
        
        logger.info("✅ Sistema de configuração funcionando")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nas configurações: {e}")
        return False


def test_directory_structure():
    """Testar se a estrutura de diretórios está correta"""
    logger = logging.getLogger(__name__)
    
    base_path = Path(__file__).parent.parent.parent.parent
    
    required_dirs = [
        "backend/app/core",
        "backend/app/models", 
        "backend/app/schemas",
        "backend/app/routers",
        "tools/scripts/dev",
        "tools/scripts/prod",
        "tools/scripts/testing",
        "docs",
        "infrastructure",
    ]
    
    missing_dirs = []
    
    for directory in required_dirs:
        dir_path = base_path / directory
        if not dir_path.exists():
            missing_dirs.append(directory)
    
    if missing_dirs:
        logger.error(f"❌ Diretórios faltando: {missing_dirs}")
        return False
    else:
        logger.info("✅ Estrutura de diretórios OK")
        return True


def test_dependencies():
    """Testar se as dependências estão disponíveis"""
    logger = logging.getLogger(__name__)
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "pydantic",
        "requests",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Pacotes faltando: {missing_packages}")
        logger.info("💡 Execute: pip install -r backend/requirements.txt")
        return False
    else:
        logger.info("✅ Dependências principais OK")
        return True


def main():
    """Função principal de teste"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🧪 Testando Sistema Reorganizado - TecnoCursos AI v2.0")
    logger.info("=" * 60)
    
    tests = [
        ("Estrutura de diretórios", test_directory_structure),
        ("Dependências", test_dependencies),
        ("Imports básicos", test_imports),
        ("Sistema de configuração", test_configuration),
        ("Banco de dados", test_database),
        ("Endpoints da API", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_function in tests:
        logger.info(f"\n🔍 Testando: {test_name}")
        try:
            result = test_function()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RELATÓRIO FINAL DOS TESTES")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Taxa de Sucesso: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 TODOS OS TESTES PASSARAM!")
        logger.info("✅ Sistema reorganizado está funcionando perfeitamente!")
        return 0
    else:
        logger.warning("⚠️ Alguns testes falharam")
        logger.info("💡 Verifique os logs acima para mais detalhes")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 