#!/usr/bin/env python3
"""
Script de diagnóstico para problemas do servidor TecnoCursos AI
"""

import os
import sys
import subprocess
import socket
import time
import requests
import logging
from pathlib import Path


def setup_logging():
    """Configurar logging para diagnóstico"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def check_port_availability(port=8000):
    """Verificar se a porta está disponível"""
    logger = logging.getLogger(__name__)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            logger.warning(f"⚠️ Porta {port} já está em uso")
            return False
        else:
            logger.info(f"✅ Porta {port} está disponível")
            return True


def find_processes_on_port(port=8000):
    """Encontrar processos usando a porta"""
    logger = logging.getLogger(__name__)
    
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run([
                'netstat', '-ano', '|', 'findstr', f':{port}'
            ], capture_output=True, text=True, shell=True)
        else:  # Linux/Mac
            result = subprocess.run([
                'lsof', '-i', f':{port}'
            ], capture_output=True, text=True)
        
        if result.stdout:
            logger.info(f"🔍 Processos na porta {port}:")
            logger.info(result.stdout)
        else:
            logger.info(f"ℹ️ Nenhum processo encontrado na porta {port}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar processos: {e}")


def test_python_imports():
    """Testar imports críticos"""
    logger = logging.getLogger(__name__)
    
    # Adicionar path do backend
    backend_path = Path(__file__).parent.parent.parent.parent / "backend"
    sys.path.insert(0, str(backend_path))
    
    imports_to_test = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
    ]
    
    failed_imports = []
    
    for module, description in imports_to_test:
        try:
            __import__(module)
            logger.info(f"✅ {description}: OK")
        except ImportError as e:
            logger.error(f"❌ {description}: FALHOU - {e}")
            failed_imports.append(module)
    
    # Testar imports da aplicação
    try:
        from app.core.config import get_settings
        from app.core.database import Base
        from app.main import app
        logger.info("✅ Imports da aplicação: OK")
    except Exception as e:
        logger.error(f"❌ Imports da aplicação: FALHOU - {e}")
        failed_imports.append("app")
    
    return len(failed_imports) == 0


def check_database():
    """Verificar banco de dados"""
    logger = logging.getLogger(__name__)
    
    try:
        backend_path = Path(__file__).parent.parent.parent.parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from app.core.database import create_database, check_database_health_sync
        
        # Criar diretório de dados se não existir
        data_dir = backend_path / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Tentar criar banco
        create_database()
        
        # Verificar saúde
        if check_database_health_sync():
            logger.info("✅ Banco de dados: OK")
            return True
        else:
            logger.error("❌ Banco de dados: Problemas de conexão")
            return False
            
    except Exception as e:
        logger.error(f"❌ Banco de dados: ERRO - {e}")
        return False


def try_start_server():
    """Tentar iniciar o servidor e capturar erros"""
    logger = logging.getLogger(__name__)
    
    backend_path = Path(__file__).parent.parent.parent.parent / "backend"
    os.chdir(backend_path)
    
    logger.info("🚀 Tentando iniciar servidor...")
    
    try:
        # Configurar ambiente
        os.environ["DEBUG"] = "true"
        os.environ["ENVIRONMENT"] = "development"
        
        # Tentar iniciar servidor
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "localhost",
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguardar um pouco para capturar erros iniciais
        time.sleep(3)
        
        # Verificar se processo ainda está rodando
        if process.poll() is None:
            logger.info("✅ Servidor iniciou sem erros aparentes")
            
            # Testar conectividade
            time.sleep(2)
            try:
                response = requests.get("http://localhost:8000/api/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Health check: OK")
                    logger.info("🎉 Servidor funcionando corretamente!")
                else:
                    logger.warning(f"⚠️ Health check retornou: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Erro ao testar conectividade: {e}")
            
            # Encerrar processo de teste
            process.terminate()
            return True
            
        else:
            # Processo terminou, capturar erro
            stdout, stderr = process.communicate()
            logger.error("❌ Servidor falhou ao iniciar")
            if stdout:
                logger.error(f"STDOUT: {stdout}")
            if stderr:
                logger.error(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao tentar iniciar servidor: {e}")
        return False


def check_dependencies():
    """Verificar se dependências estão instaladas"""
    logger = logging.getLogger(__name__)
    
    backend_path = Path(__file__).parent.parent.parent.parent / "backend"
    requirements_file = backend_path / "requirements.txt"
    
    if not requirements_file.exists():
        logger.error(f"❌ Arquivo requirements.txt não encontrado em {requirements_file}")
        return False
    
    try:
        # Verificar se pip list mostra as dependências principais
        result = subprocess.run([
            sys.executable, "-m", "pip", "list"
        ], capture_output=True, text=True)
        
        installed_packages = result.stdout.lower()
        
        required_packages = ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]
        missing_packages = []
        
        for package in required_packages:
            if package not in installed_packages:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Pacotes faltando: {missing_packages}")
            logger.info("💡 Execute:")
            logger.info(f"   cd {backend_path}")
            logger.info(f"   pip install -r requirements.txt")
            return False
        else:
            logger.info("✅ Dependências principais instaladas")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar dependências: {e}")
        return False


def provide_solutions():
    """Fornecer soluções para problemas comuns"""
    logger = logging.getLogger(__name__)
    
    logger.info("\n" + "="*60)
    logger.info("🔧 SOLUÇÕES PARA PROBLEMAS COMUNS")
    logger.info("="*60)
    
    backend_path = Path(__file__).parent.parent.parent.parent / "backend"
    
    logger.info("\n1️⃣ INSTALAÇÃO DE DEPENDÊNCIAS:")
    logger.info(f"   cd {backend_path}")
    logger.info("   pip install -r requirements.txt")
    
    logger.info("\n2️⃣ INICIALIZAÇÃO MANUAL:")
    logger.info(f"   cd {backend_path}")
    logger.info("   python -m uvicorn app.main:app --reload --host localhost --port 8000")
    
    logger.info("\n3️⃣ INICIALIZAÇÃO COM SCRIPT:")
    logger.info("   python tools/scripts/dev/start_development.py")
    
    logger.info("\n4️⃣ VERIFICAR CONFLITOS DE PORTA:")
    logger.info("   Use porta alternativa: --port 8001")
    
    logger.info("\n5️⃣ MODO DEBUG:")
    logger.info("   export DEBUG=true")
    logger.info("   export LOG_LEVEL=DEBUG")
    
    logger.info("\n6️⃣ VERIFICAR LOGS:")
    logger.info("   Verifique logs/tecnocursos.log para mais detalhes")


def main():
    """Função principal de diagnóstico"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🔍 DIAGNÓSTICO DO SERVIDOR TECNOCURSOS AI")
    logger.info("="*60)
    
    # Lista de verificações
    checks = [
        ("Disponibilidade da porta 8000", lambda: check_port_availability(8000)),
        ("Dependências instaladas", check_dependencies),
        ("Imports Python", test_python_imports), 
        ("Banco de dados", check_database),
        ("Inicialização do servidor", try_start_server),
    ]
    
    results = []
    
    for check_name, check_function in checks:
        logger.info(f"\n🔍 Verificando: {check_name}")
        try:
            result = check_function()
            results.append((check_name, result))
            
            if not result:
                # Se uma verificação falhar, mostrar processos na porta
                if "porta" in check_name.lower():
                    find_processes_on_port(8000)
                    
        except Exception as e:
            logger.error(f"❌ Erro inesperado em {check_name}: {e}")
            results.append((check_name, False))
    
    # Relatório final
    logger.info("\n" + "="*60)
    logger.info("📊 RELATÓRIO DE DIAGNÓSTICO")
    logger.info("="*60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ OK" if result else "❌ FALHOU"
        logger.info(f"{check_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Taxa de Sucesso: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 TUDO FUNCIONANDO!")
        logger.info("✅ Acesse: http://localhost:8000")
    else:
        logger.warning("⚠️ Problemas encontrados")
        provide_solutions()


if __name__ == "__main__":
    main() 