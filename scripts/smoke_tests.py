#!/usr/bin/env python3
"""
SMOKE TESTS - TECNOCURSOS AI
============================
Testes rápidos para validação de deploy e funcionalidade essencial
"""

import asyncio
import aiohttp
import json
import time
import sys
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import argparse

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmokeTestRunner:
    """Runner para testes de smoke"""
    
    def __init__(self, environment: str = "staging"):
        self.environment = environment
        self.start_time = time.time()
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []
        
        # URLs baseadas no ambiente
        self.base_urls = {
            "production": "https://api.tecnocursos.ai",
            "staging": "https://staging-api.tecnocursos.ai", 
            "development": "http://localhost:8000"
        }
        self.base_url = self.base_urls.get(environment, "http://localhost:8000")
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "TecnoCursos-SmokeTest/1.0"
        }
        
        # Token de autenticação (será preenchido durante login)
        self.auth_token = None
    
    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Teste: Endpoint de health básico"""
        test_name = "Health Endpoint"
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validações básicas
                        assert "status" in data
                        assert data["status"] == "healthy"
                        assert duration < 2.0  # Deve responder em menos de 2s
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": "Health endpoint respondendo corretamente"
                        }
                    else:
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_database_connectivity(self) -> Dict[str, Any]:
        """Teste: Conectividade com banco de dados"""
        test_name = "Database Connectivity"
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/health/database",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validações
                        assert "status" in data
                        assert data["status"] == "healthy"
                        assert duration < 5.0  # Deve responder em menos de 5s
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": "Banco de dados acessível"
                        }
                    else:
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_user_registration(self) -> Dict[str, Any]:
        """Teste: Registro de usuário"""
        test_name = "User Registration"
        try:
            test_email = f"smoketest_{int(time.time())}@test.com"
            test_data = {
                "name": "Smoke Test User",
                "email": test_email,
                "password": "SmokeTest123!",
                "confirm_password": "SmokeTest123!"
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json=test_data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        
                        # Validações
                        assert "id" in data or "user_id" in data
                        assert "email" in data or test_email in str(data)
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": f"Usuário criado: {test_email}"
                        }
                    else:
                        response_text = await response.text()
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_user_login(self) -> Dict[str, Any]:
        """Teste: Login de usuário e obtenção de token"""
        test_name = "User Login"
        try:
            # Usar credenciais de teste ou criar usuário temporário
            login_data = {
                "username": "admin@tecnocursos.ai",  # Usuário padrão
                "password": "admin123"
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data=login_data,  # Form data para OAuth2
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validações
                        assert "access_token" in data
                        assert "token_type" in data
                        
                        # Armazenar token para próximos testes
                        self.auth_token = data["access_token"]
                        self.headers["Authorization"] = f"Bearer {self.auth_token}"
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": "Login realizado com sucesso"
                        }
                    else:
                        response_text = await response.text()
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_project_creation(self) -> Dict[str, Any]:
        """Teste: Criação de projeto"""
        test_name = "Project Creation"
        try:
            if not self.auth_token:
                return {
                    "test": test_name,
                    "status": "SKIP",
                    "error": "Sem token de autenticação"
                }
            
            project_data = {
                "name": f"Smoke Test Project {int(time.time())}",
                "description": "Projeto criado durante smoke test",
                "type": "video"
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/v1/projects",
                    json=project_data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        
                        # Validações
                        assert "id" in data
                        assert "name" in data
                        assert data["name"] == project_data["name"]
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": f"Projeto criado: ID {data['id']}"
                        }
                    else:
                        response_text = await response.text()
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_file_upload_endpoint(self) -> Dict[str, Any]:
        """Teste: Endpoint de upload de arquivo"""
        test_name = "File Upload Endpoint"
        try:
            if not self.auth_token:
                return {
                    "test": test_name,
                    "status": "SKIP",
                    "error": "Sem token de autenticação"
                }
            
            # Criar arquivo de teste pequeno
            test_content = "Conteúdo de teste para smoke test"
            
            async with aiohttp.ClientSession() as session:
                # Preparar dados multipart
                data = aiohttp.FormData()
                data.add_field('file', 
                             test_content,
                             filename='smoke_test.txt',
                             content_type='text/plain')
                data.add_field('type', 'document')
                
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/v1/files/upload",
                    data=data,
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        
                        # Validações básicas
                        assert "file_id" in data or "id" in data
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": "Upload realizado com sucesso"
                        }
                    else:
                        response_text = await response.text()
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_tts_endpoint(self) -> Dict[str, Any]:
        """Teste: Endpoint de TTS"""
        test_name = "TTS Endpoint"
        try:
            if not self.auth_token:
                return {
                    "test": test_name,
                    "status": "SKIP",
                    "error": "Sem token de autenticação"
                }
            
            tts_data = {
                "text": "Este é um teste de síntese de voz",
                "voice": "nova",
                "speed": 1.0
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/v1/tts/synthesize",
                    json=tts_data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status in [200, 201]:
                        # Para TTS, pode retornar JSON com URL ou dados binários
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            data = await response.json()
                            assert "audio_url" in data or "task_id" in data
                        else:
                            # Áudio direto
                            audio_data = await response.read()
                            assert len(audio_data) > 0
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": "TTS processado com sucesso"
                        }
                    else:
                        response_text = await response.text()
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_api_versioning(self) -> Dict[str, Any]:
        """Teste: Versionamento da API"""
        test_name = "API Versioning"
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/api/version",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validações
                        assert "version" in data
                        assert "api_version" in data or "v1" in str(data)
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "duration": duration,
                            "details": f"API Version: {data.get('version', 'unknown')}"
                        }
                    else:
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "duration": duration,
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os smoke tests"""
        logger.info(f"Iniciando smoke tests para ambiente: {self.environment}")
        
        # Lista de testes para executar
        tests = [
            self.test_health_endpoint(),
            self.test_database_connectivity(),
            self.test_api_versioning(),
            self.test_user_registration(),
            self.test_user_login(),
            self.test_project_creation(),
            self.test_file_upload_endpoint(),
            self.test_tts_endpoint(),
        ]
        
        # Executar testes em sequência (alguns dependem de outros)
        results = []
        for test_coro in tests:
            try:
                result = await test_coro
                results.append(result)
                
                if result["status"] == "PASS":
                    self.passed_tests += 1
                    logger.info(f"✅ {result['test']}: PASS")
                elif result["status"] == "SKIP":
                    logger.warning(f"⏭️  {result['test']}: SKIP - {result.get('error', '')}")
                else:
                    self.failed_tests += 1
                    logger.error(f"❌ {result['test']}: FAIL - {result.get('error', '')}")
                
            except Exception as e:
                self.failed_tests += 1
                error_result = {
                    "test": "Unknown Test",
                    "status": "FAIL",
                    "error": str(e)
                }
                results.append(error_result)
                logger.error(f"❌ Erro inesperado: {e}")
        
        # Compilar resultado final
        total_duration = time.time() - self.start_time
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        final_result = {
            "summary": {
                "environment": self.environment,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration": total_duration,
                "total_tests": total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "success_rate": round(success_rate, 2),
                "status": "PASS" if self.failed_tests == 0 else "FAIL"
            },
            "tests": results
        }
        
        return final_result
    
    def save_results(self, results: Dict[str, Any], output_file: Optional[str] = None):
        """Salva resultados em arquivo"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"smoke_test_{self.environment}_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados salvos em: {output_path}")

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Smoke Tests TecnoCursos AI")
    parser.add_argument(
        "--environment",
        choices=["production", "staging", "development"],
        default="staging",
        help="Ambiente a ser testado"
    )
    parser.add_argument(
        "--output",
        help="Arquivo de saída para os resultados"
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Para na primeira falha"
    )
    
    args = parser.parse_args()
    
    runner = SmokeTestRunner(args.environment)
    results = await runner.run_all_tests()
    
    # Exibir resumo
    summary = results["summary"]
    print(f"\n{'='*60}")
    print(f"SMOKE TESTS - {summary['environment'].upper()}")
    print(f"{'='*60}")
    print(f"Testes executados: {summary['total_tests']}")
    print(f"Sucessos: {summary['passed']}")
    print(f"Falhas: {summary['failed']}")
    print(f"Taxa de sucesso: {summary['success_rate']}%")
    print(f"Duração: {summary['duration']:.2f}s")
    print(f"Status: {summary['status']}")
    print(f"{'='*60}")
    
    # Salvar resultados se solicitado
    if args.output:
        runner.save_results(results, args.output)
    
    # Exit code baseado no resultado
    if summary["status"] == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 