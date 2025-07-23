#!/usr/bin/env python3
"""
Script de Teste Completo - TecnoCursos AI Enterprise Edition
Testa todas as funcionalidades do sistema
"""

import requests
import json
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_health_endpoint():
    """Testa o endpoint de health"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Health check: OK")
            logger.info(f"   Status: {data.get('data', {}).get('status', 'unknown')}")
            logger.info(f"   Uptime: {data.get('data', {}).get('uptime', 0):.2f}s")
            return True
        else:
            logger.error(f"❌ Health check: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health check: {e}")
        return False

def test_api_endpoints():
    """Testa endpoints da API"""
    endpoints = [
        ("/api/health", "API Health"),
        ("/api/status", "API Status"),
        ("/api/projects", "Projects"),
        ("/api/videos", "Videos"),
        ("/api/audios", "Audios")
    ]
    
    results = []
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {name}: OK")
                results.append(True)
            else:
                logger.warning(f"⚠️ {name}: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            logger.error(f"❌ {name}: {e}")
            results.append(False)
    
    return results

def test_static_files():
    """Testa arquivos estáticos"""
    files = [
        ("/", "Home Page"),
        ("/favicon.ico", "Favicon"),
        ("/static/css/style.css", "CSS"),
        ("/static/js/app.js", "JavaScript")
    ]
    
    results = []
    for file_path, name in files:
        try:
            response = requests.get(f"http://localhost:8000{file_path}", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {name}: OK")
                results.append(True)
            else:
                logger.warning(f"⚠️ {name}: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            logger.error(f"❌ {name}: {e}")
            results.append(False)
    
    return results

def test_upload_system():
    """Testa sistema de upload"""
    try:
        # Testar endpoint de lista de uploads
        response = requests.get("http://localhost:8000/api/upload/files", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Upload system: OK")
            return True
        else:
            logger.warning(f"⚠️ Upload system: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Upload system: {e}")
        return False

def test_background_processor():
    """Testa processador em background"""
    try:
        # Testar endpoint de estatísticas
        response = requests.get("http://localhost:8000/api/background/stats", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Background processor: OK")
            return True
        else:
            logger.warning(f"⚠️ Background processor: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Background processor: {e}")
        return False

def test_file_structure():
    """Testa estrutura de arquivos"""
    required_files = [
        "simple_server.py",
        "upload_handler.py",
        "background_processor.py",
        "index.html",
        "config.json"
    ]
    
    required_dirs = [
        "uploads",
        "static",
        "cache",
        "logs"
    ]
    
    results = []
    
    # Verificar arquivos
    for file in required_files:
        if Path(file).exists():
            logger.info(f"✅ File {file}: OK")
            results.append(True)
        else:
            logger.error(f"❌ File {file}: Missing")
            results.append(False)
    
    # Verificar diretórios
    for directory in required_dirs:
        if Path(directory).exists():
            logger.info(f"✅ Directory {directory}: OK")
            results.append(True)
        else:
            logger.error(f"❌ Directory {directory}: Missing")
            results.append(False)
    
    return results

def generate_test_report(results):
    """Gera relatório de teste"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system": "TecnoCursos AI Enterprise Edition",
        "version": "2.1.1",
        "tests": {
            "health_check": results.get("health", False),
            "api_endpoints": results.get("api", []),
            "static_files": results.get("static", []),
            "upload_system": results.get("upload", False),
            "background_processor": results.get("background", False),
            "file_structure": results.get("files", [])
        },
        "summary": {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
    }
    
    # Calcular estatísticas
    for test_type, test_results in report["tests"].items():
        if isinstance(test_results, list):
            report["summary"]["total_tests"] += len(test_results)
            report["summary"]["passed_tests"] += sum(1 for r in test_results if r)
            report["summary"]["failed_tests"] += sum(1 for r in test_results if not r)
        else:
            report["summary"]["total_tests"] += 1
            if test_results:
                report["summary"]["passed_tests"] += 1
            else:
                report["summary"]["failed_tests"] += 1
    
    return report

def main():
    """Função principal"""
    print("=" * 80)
    print("TESTE COMPLETO DO SISTEMA - TECNOCURSOS AI")
    print("=" * 80)
    
    results = {}
    
    # Testar health check
    logger.info("Testando health check...")
    results["health"] = test_health_endpoint()
    
    # Testar endpoints da API
    logger.info("Testando endpoints da API...")
    results["api"] = test_api_endpoints()
    
    # Testar arquivos estáticos
    logger.info("Testando arquivos estáticos...")
    results["static"] = test_static_files()
    
    # Testar sistema de upload
    logger.info("Testando sistema de upload...")
    results["upload"] = test_upload_system()
    
    # Testar processador em background
    logger.info("Testando processador em background...")
    results["background"] = test_background_processor()
    
    # Testar estrutura de arquivos
    logger.info("Testando estrutura de arquivos...")
    results["files"] = test_file_structure()
    
    # Gerar relatório
    report = generate_test_report(results)
    
    # Salvar relatório
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Exibir resumo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"Total de testes: {report['summary']['total_tests']}")
    print(f"Testes aprovados: {report['summary']['passed_tests']}")
    print(f"Testes falharam: {report['summary']['failed_tests']}")
    
    success_rate = (report['summary']['passed_tests'] / report['summary']['total_tests']) * 100
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
    elif success_rate >= 70:
        print("✅ SISTEMA FUNCIONANDO BEM!")
    elif success_rate >= 50:
        print("⚠️ SISTEMA COM PROBLEMAS MENORES!")
    else:
        print("❌ SISTEMA COM PROBLEMAS CRÍTICOS!")
    
    print("=" * 80)
    print("Relatório salvo em: test_results.json")

if __name__ == "__main__":
    main() 