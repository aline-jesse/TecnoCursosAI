#!/usr/bin/env python3
"""
STRESS TESTING - TECNOCURSOS AI
===============================
Testes de stress para detectar limites do sistema e pontos de falha
"""

import asyncio
import aiohttp
import psutil
import time
import json
import gc
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import resource
import signal
import sys

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor de recursos do sistema"""
    
    def __init__(self):
        self.monitoring = False
        self.stats = []
        self.start_time = None
        
    def start_monitoring(self):
        """Inicia monitoramento de recursos"""
        self.monitoring = True
        self.start_time = time.time()
        
        def monitor_loop():
            while self.monitoring:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Informações de processo Python atual
                    process = psutil.Process()
                    process_memory = process.memory_info()
                    
                    stat = {
                        "timestamp": time.time(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_available_gb": memory.available / (1024**3),
                        "memory_used_gb": memory.used / (1024**3),
                        "disk_percent": disk.percent,
                        "process_memory_rss_mb": process_memory.rss / (1024**2),
                        "process_memory_vms_mb": process_memory.vms / (1024**2),
                        "open_files": len(process.open_files()),
                        "connections": len(process.connections()),
                        "threads": process.num_threads()
                    }
                    
                    self.stats.append(stat)
                    
                    # Limitar histórico para evitar memory leak
                    if len(self.stats) > 1000:
                        self.stats = self.stats[-500:]
                        
                except Exception as e:
                    logger.error(f"Erro no monitoramento: {e}")
                    
                time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoramento de sistema iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoramento de sistema parado")
    
    def get_peak_usage(self) -> Dict[str, Any]:
        """Retorna picos de uso de recursos"""
        if not self.stats:
            return {}
        
        peak_cpu = max(stat["cpu_percent"] for stat in self.stats)
        peak_memory = max(stat["memory_percent"] for stat in self.stats)
        peak_process_memory = max(stat["process_memory_rss_mb"] for stat in self.stats)
        peak_connections = max(stat["connections"] for stat in self.stats)
        peak_threads = max(stat["threads"] for stat in self.stats)
        
        return {
            "peak_cpu_percent": peak_cpu,
            "peak_memory_percent": peak_memory,
            "peak_process_memory_mb": peak_process_memory,
            "peak_connections": peak_connections,
            "peak_threads": peak_threads,
            "monitoring_duration": time.time() - self.start_time if self.start_time else 0
        }

class StressTestRunner:
    """Runner principal para testes de stress"""
    
    def __init__(self, base_url: str, environment: str = "staging"):
        self.base_url = base_url
        self.environment = environment
        self.monitor = SystemMonitor()
        self.results = []
        self.auth_tokens = []
        self.active_sessions = []
        self.errors = []
        
        # Configurar limites de sistema
        try:
            # Aumentar limite de file descriptors
            resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
        except Exception as e:
            logger.warning(f"Não foi possível ajustar limites: {e}")
    
    async def create_auth_session(self, session_id: int) -> Optional[str]:
        """Cria sessão autenticada"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=1000)
            ) as session:
                # Registrar usuário
                user_data = {
                    "name": f"Stress Test User {session_id}",
                    "email": f"stress_{session_id}_{int(time.time())}@test.com",
                    "password": "StressTest123!",
                    "confirm_password": "StressTest123!"
                }
                
                async with session.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json=user_data
                ) as response:
                    if response.status not in [200, 201]:
                        # Tentar login com admin se registro falhar
                        login_data = {
                            "username": "admin@tecnocursos.ai",
                            "password": "admin123"
                        }
                        
                        async with session.post(
                            f"{self.base_url}/api/v1/auth/login",
                            data=login_data
                        ) as login_response:
                            if login_response.status == 200:
                                data = await login_response.json()
                                return data.get("access_token")
                            return None
                
                # Login com usuário registrado
                login_data = {
                    "username": user_data["email"],
                    "password": user_data["password"]
                }
                
                async with session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data=login_data
                ) as login_response:
                    if login_response.status == 200:
                        data = await login_response.json()
                        return data.get("access_token")
                    
        except Exception as e:
            logger.error(f"Erro criando sessão {session_id}: {e}")
        
        return None
    
    async def stress_endpoints(self, token: str, requests_per_endpoint: int = 100) -> Dict[str, Any]:
        """Testa endpoints sob stress"""
        endpoints = [
            {"method": "GET", "url": "/health", "weight": 20},
            {"method": "GET", "url": "/api/v1/projects", "weight": 15},
            {"method": "GET", "url": "/api/v1/scenes", "weight": 15},
            {"method": "GET", "url": "/api/v1/assets", "weight": 10},
            {"method": "POST", "url": "/api/v1/projects", "weight": 5, "data": {
                "name": f"Stress Project {time.time()}",
                "description": "Stress test project",
                "type": "video"
            }},
            {"method": "POST", "url": "/api/v1/tts/synthesize", "weight": 3, "data": {
                "text": "Teste de stress TTS",
                "voice": "nova",
                "speed": 1.0
            }}
        ]
        
        headers = {"Authorization": f"Bearer {token}"}
        results = {"success": 0, "errors": 0, "response_times": []}
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            connector=aiohttp.TCPConnector(limit=100)
        ) as session:
            
            tasks = []
            
            for endpoint in endpoints:
                for _ in range(requests_per_endpoint * endpoint["weight"] // 100):
                    if endpoint["method"] == "GET":
                        task = self._make_get_request(session, endpoint["url"], headers)
                    else:
                        task = self._make_post_request(
                            session, endpoint["url"], headers, endpoint.get("data", {})
                        )
                    tasks.append(task)
            
            # Executar todas as requests em paralelo
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for response in responses:
                if isinstance(response, Exception):
                    results["errors"] += 1
                    self.errors.append(str(response))
                else:
                    results["success"] += 1
                    results["response_times"].append(response.get("response_time", 0))
        
        return results
    
    async def _make_get_request(self, session: aiohttp.ClientSession, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Faz request GET"""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}{url}", headers=headers) as response:
                await response.read()  # Consumir resposta
                return {
                    "status": response.status,
                    "response_time": time.time() - start_time
                }
        except Exception as e:
            raise Exception(f"GET {url}: {e}")
    
    async def _make_post_request(self, session: aiohttp.ClientSession, url: str, headers: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Faz request POST"""
        start_time = time.time()
        try:
            async with session.post(f"{self.base_url}{url}", headers=headers, json=data) as response:
                await response.read()  # Consumir resposta
                return {
                    "status": response.status,
                    "response_time": time.time() - start_time
                }
        except Exception as e:
            raise Exception(f"POST {url}: {e}")
    
    async def memory_stress_test(self, duration: int = 300) -> Dict[str, Any]:
        """Teste de stress de memória"""
        logger.info(f"Iniciando teste de stress de memória por {duration}s")
        
        start_memory = psutil.virtual_memory().used
        memory_allocations = []
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # Alocar blocos de memória
                chunk = bytearray(1024 * 1024)  # 1MB
                memory_allocations.append(chunk)
                
                # Limitar para evitar OOM
                if len(memory_allocations) > 500:  # 500MB
                    # Liberar metade
                    del memory_allocations[:250]
                    gc.collect()
                
                # Pequena pausa
                await asyncio.sleep(0.1)
                
                # Verificar se sistema está sob pressão
                memory = psutil.virtual_memory()
                if memory.percent > 95:
                    logger.warning("Memória crítica, parando teste")
                    break
        
        finally:
            # Limpeza
            del memory_allocations
            gc.collect()
        
        end_memory = psutil.virtual_memory().used
        
        return {
            "memory_allocated_mb": (end_memory - start_memory) / (1024**2),
            "test_duration": time.time() - start_time,
            "peak_memory_percent": max(stat["memory_percent"] for stat in self.monitor.stats[-100:])
        }
    
    async def connection_flood_test(self, max_connections: int = 1000) -> Dict[str, Any]:
        """Teste de flood de conexões"""
        logger.info(f"Iniciando teste de flood com {max_connections} conexões")
        
        successful_connections = 0
        failed_connections = 0
        
        async def create_connection(conn_id: int):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as session:
                    async with session.get(f"{self.base_url}/health") as response:
                        await response.read()
                        return True
            except Exception:
                return False
        
        # Criar conexões em lotes para não sobrecarregar
        batch_size = 50
        
        for i in range(0, max_connections, batch_size):
            batch_tasks = []
            for j in range(min(batch_size, max_connections - i)):
                task = create_connection(i + j)
                batch_tasks.append(task)
            
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in results:
                if result is True:
                    successful_connections += 1
                else:
                    failed_connections += 1
            
            # Pausa entre lotes
            await asyncio.sleep(0.5)
        
        return {
            "successful_connections": successful_connections,
            "failed_connections": failed_connections,
            "success_rate": successful_connections / max_connections * 100
        }
    
    async def run_comprehensive_stress_test(
        self,
        concurrent_users: int = 50,
        requests_per_user: int = 100,
        duration: int = 300
    ) -> Dict[str, Any]:
        """Executa teste de stress completo"""
        logger.info("🔥 Iniciando teste de stress completo")
        
        self.monitor.start_monitoring()
        test_start_time = time.time()
        
        try:
            # Fase 1: Criar tokens de autenticação
            logger.info(f"Criando {concurrent_users} sessões autenticadas...")
            auth_tasks = [
                self.create_auth_session(i) for i in range(concurrent_users)
            ]
            
            auth_results = await asyncio.gather(*auth_tasks, return_exceptions=True)
            valid_tokens = [token for token in auth_results if isinstance(token, str)]
            
            logger.info(f"✅ {len(valid_tokens)} sessões criadas com sucesso")
            
            if not valid_tokens:
                raise Exception("Nenhuma sessão autenticada criada")
            
            # Fase 2: Stress test de endpoints
            logger.info("Executando stress test de endpoints...")
            endpoint_tasks = [
                self.stress_endpoints(token, requests_per_user) 
                for token in valid_tokens
            ]
            
            endpoint_results = await asyncio.gather(*endpoint_tasks, return_exceptions=True)
            
            # Compilar resultados de endpoints
            total_success = sum(r["success"] for r in endpoint_results if isinstance(r, dict))
            total_errors = sum(r["errors"] for r in endpoint_results if isinstance(r, dict))
            all_response_times = []
            for r in endpoint_results:
                if isinstance(r, dict):
                    all_response_times.extend(r["response_times"])
            
            # Fase 3: Teste de memória
            logger.info("Executando teste de stress de memória...")
            memory_results = await self.memory_stress_test(duration=60)
            
            # Fase 4: Teste de conexões
            logger.info("Executando teste de flood de conexões...")
            connection_results = await self.connection_flood_test(max_connections=500)
            
            # Compilar resultados finais
            test_duration = time.time() - test_start_time
            peak_usage = self.monitor.get_peak_usage()
            
            results = {
                "test_summary": {
                    "environment": self.environment,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "duration": test_duration,
                    "concurrent_users": len(valid_tokens),
                    "planned_users": concurrent_users,
                    "requests_per_user": requests_per_user
                },
                "performance_metrics": {
                    "total_requests": total_success + total_errors,
                    "successful_requests": total_success,
                    "failed_requests": total_errors,
                    "success_rate": (total_success / (total_success + total_errors) * 100) if (total_success + total_errors) > 0 else 0,
                    "avg_response_time": sum(all_response_times) / len(all_response_times) if all_response_times else 0,
                    "min_response_time": min(all_response_times) if all_response_times else 0,
                    "max_response_time": max(all_response_times) if all_response_times else 0,
                    "requests_per_second": (total_success + total_errors) / test_duration if test_duration > 0 else 0
                },
                "resource_usage": peak_usage,
                "memory_stress": memory_results,
                "connection_flood": connection_results,
                "errors": self.errors[:100]  # Primeiros 100 erros
            }
            
            return results
            
        finally:
            self.monitor.stop_monitoring()
    
    def save_results(self, results: Dict[str, Any], output_file: Optional[str] = None):
        """Salva resultados do teste"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"stress_test_{self.environment}_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados salvos em: {output_path}")

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Stress Test TecnoCursos AI")
    parser.add_argument("--environment", choices=["production", "staging", "development"], default="staging")
    parser.add_argument("--users", type=int, default=50, help="Usuários concorrentes")
    parser.add_argument("--requests", type=int, default=100, help="Requests por usuário")
    parser.add_argument("--duration", type=int, default=300, help="Duração em segundos")
    parser.add_argument("--output", help="Arquivo de saída")
    
    args = parser.parse_args()
    
    # Configurar URL baseada no ambiente
    base_urls = {
        "production": "https://api.tecnocursos.ai",
        "staging": "https://staging-api.tecnocursos.ai",
        "development": "http://localhost:8000"
    }
    
    base_url = base_urls.get(args.environment, "http://localhost:8000")
    
    runner = StressTestRunner(base_url, args.environment)
    
    # Configurar handler para interrupção
    def signal_handler(signum, frame):
        logger.info("Teste interrompido pelo usuário")
        runner.monitor.stop_monitoring()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info(f"🔥 Iniciando stress test no ambiente: {args.environment}")
        logger.info(f"🎯 URL: {base_url}")
        logger.info(f"👥 Usuários concorrentes: {args.users}")
        logger.info(f"📊 Requests por usuário: {args.requests}")
        logger.info(f"⏱️  Duração: {args.duration}s")
        
        results = await runner.run_comprehensive_stress_test(
            concurrent_users=args.users,
            requests_per_user=args.requests,
            duration=args.duration
        )
        
        # Exibir resumo
        summary = results["test_summary"]
        performance = results["performance_metrics"]
        resources = results["resource_usage"]
        
        print("\n" + "="*80)
        print("🔥 STRESS TEST RESULTS")
        print("="*80)
        print(f"Environment: {summary['environment']}")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Users: {summary['concurrent_users']}/{summary['planned_users']}")
        print(f"Total Requests: {performance['total_requests']}")
        print(f"Success Rate: {performance['success_rate']:.2f}%")
        print(f"Avg Response Time: {performance['avg_response_time']:.2f}ms")
        print(f"Requests/second: {performance['requests_per_second']:.2f}")
        print(f"Peak CPU: {resources.get('peak_cpu_percent', 0):.2f}%")
        print(f"Peak Memory: {resources.get('peak_memory_percent', 0):.2f}%")
        print(f"Peak Process Memory: {resources.get('peak_process_memory_mb', 0):.2f}MB")
        print("="*80)
        
        # Salvar resultados
        runner.save_results(results, args.output)
        
        # Exit code baseado no sucesso
        if performance['success_rate'] < 95:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Erro durante stress test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 