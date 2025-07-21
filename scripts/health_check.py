#!/usr/bin/env python3
"""
HEALTH CHECK AVANÇADO - TECNOCURSOS AI
=====================================
Sistema completo de verificação de saúde para produção
"""

import asyncio
import aiohttp
import psutil
import logging
import json
import time
import sys
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

class HealthChecker:
    """Sistema avançado de health check"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.start_time = time.time()
        self.checks = []
        self.results = {}
        
        # URLs baseadas no ambiente
        self.base_urls = {
            "production": "https://api.tecnocursos.ai",
            "staging": "https://staging-api.tecnocursos.ai",
            "development": "http://localhost:8000"
        }
        self.base_url = self.base_urls.get(environment, "http://localhost:8000")
    
    async def check_database(self) -> Dict[str, Any]:
        """Verifica conectividade e performance do banco"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/health/database",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": duration,
                            "details": data,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "response_time": duration,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Verifica conectividade e performance do Redis"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/health/redis",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": duration,
                            "details": data,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "response_time": duration,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_external_apis(self) -> Dict[str, Any]:
        """Verifica APIs externas críticas"""
        api_checks = {}
        
        # OpenAI API
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/health/openai",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    duration = time.time() - start_time
                    api_checks["openai"] = {
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "response_time": duration,
                        "http_status": response.status
                    }
        except Exception as e:
            api_checks["openai"] = {"status": "error", "error": str(e)}
        
        # D-ID API
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/health/d_id",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    duration = time.time() - start_time
                    api_checks["d_id"] = {
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "response_time": duration,
                        "http_status": response.status
                    }
        except Exception as e:
            api_checks["d_id"] = {"status": "error", "error": str(e)}
        
        # ElevenLabs API
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.base_url}/health/elevenlabs",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    duration = time.time() - start_time
                    api_checks["elevenlabs"] = {
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "response_time": duration,
                        "http_status": response.status
                    }
        except Exception as e:
            api_checks["elevenlabs"] = {"status": "error", "error": str(e)}
        
        return {
            "status": "healthy" if all(
                check.get("status") == "healthy" 
                for check in api_checks.values()
            ) else "degraded",
            "details": api_checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Verifica recursos do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024 ** 3)  # GB
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024 ** 3)  # GB
            
            # Processos
            process_count = len(psutil.pids())
            
            # Load average (Unix only)
            load_avg = None
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                pass  # Windows doesn't have load average
            
            # Determinar status geral
            status = "healthy"
            alerts = []
            
            if cpu_percent > 90:
                status = "warning"
                alerts.append(f"CPU usage high: {cpu_percent}%")
            
            if memory_percent > 90:
                status = "critical"
                alerts.append(f"Memory usage critical: {memory_percent}%")
            elif memory_percent > 80:
                status = "warning"
                alerts.append(f"Memory usage high: {memory_percent}%")
            
            if disk_percent > 90:
                status = "critical"
                alerts.append(f"Disk usage critical: {disk_percent}%")
            elif disk_percent > 85:
                status = "warning"
                alerts.append(f"Disk usage high: {disk_percent}%")
            
            return {
                "status": status,
                "alerts": alerts,
                "details": {
                    "cpu": {
                        "usage_percent": cpu_percent,
                        "count": cpu_count,
                        "load_average": load_avg
                    },
                    "memory": {
                        "usage_percent": memory_percent,
                        "available_gb": round(memory_available, 2),
                        "total_gb": round(memory.total / (1024 ** 3), 2)
                    },
                    "disk": {
                        "usage_percent": disk_percent,
                        "free_gb": round(disk_free, 2),
                        "total_gb": round(disk.total / (1024 ** 3), 2)
                    },
                    "processes": {
                        "count": process_count
                    }
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_api_endpoints(self) -> Dict[str, Any]:
        """Verifica endpoints críticos da API"""
        endpoints = [
            "/health",
            "/api/v1/users/me",
            "/api/v1/projects",
            "/api/v1/scenes",
            "/api/v1/assets",
            "/metrics"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    async with session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        duration = time.time() - start_time
                        
                        results[endpoint] = {
                            "status": "healthy" if response.status < 500 else "unhealthy",
                            "http_status": response.status,
                            "response_time": duration
                        }
            except Exception as e:
                results[endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
        
        overall_status = "healthy"
        if any(result.get("status") == "error" for result in results.values()):
            overall_status = "error"
        elif any(result.get("status") == "unhealthy" for result in results.values()):
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "details": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Executa todas as verificações em paralelo"""
        logger.info(f"Iniciando health check para ambiente: {self.environment}")
        
        # Executar checks em paralelo
        tasks = [
            self.check_database(),
            self.check_redis(),
            self.check_external_apis(),
            self.check_api_endpoints(),
        ]
        
        # Adicionar check de recursos do sistema (síncrono)
        system_check = self.check_system_resources()
        
        # Aguardar checks assíncronos
        db_result, redis_result, api_result, endpoints_result = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        
        # Compilar resultados
        results = {
            "overall": {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": self.environment,
                "duration": time.time() - self.start_time
            },
            "checks": {
                "database": db_result if not isinstance(db_result, Exception) else {
                    "status": "error", "error": str(db_result)
                },
                "redis": redis_result if not isinstance(redis_result, Exception) else {
                    "status": "error", "error": str(redis_result)
                },
                "external_apis": api_result if not isinstance(api_result, Exception) else {
                    "status": "error", "error": str(api_result)
                },
                "api_endpoints": endpoints_result if not isinstance(endpoints_result, Exception) else {
                    "status": "error", "error": str(endpoints_result)
                },
                "system_resources": system_check
            }
        }
        
        # Determinar status geral
        check_statuses = [
            check.get("status", "error") 
            for check in results["checks"].values()
        ]
        
        if "error" in check_statuses or "critical" in check_statuses:
            results["overall"]["status"] = "critical"
        elif "unhealthy" in check_statuses or "warning" in check_statuses:
            results["overall"]["status"] = "warning"
        elif "degraded" in check_statuses:
            results["overall"]["status"] = "degraded"
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_file: Optional[str] = None):
        """Salva resultados em arquivo"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"health_check_{self.environment}_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados salvos em: {output_path}")

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Health Check TecnoCursos AI")
    parser.add_argument(
        "--environment", 
        choices=["production", "staging", "development"],
        default="production",
        help="Ambiente a ser verificado"
    )
    parser.add_argument(
        "--output",
        help="Arquivo de saída para os resultados"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Execução contínua (a cada 60 segundos)"
    )
    parser.add_argument(
        "--alert-only",
        action="store_true",
        help="Mostra apenas alertas e problemas"
    )
    
    args = parser.parse_args()
    
    checker = HealthChecker(args.environment)
    
    if args.continuous:
        logger.info("Iniciando monitoramento contínuo...")
        while True:
            try:
                results = await checker.run_all_checks()
                
                # Log apenas se houver problemas ou não for alert-only
                if not args.alert_only or results["overall"]["status"] != "healthy":
                    print(json.dumps(results, indent=2, ensure_ascii=False))
                
                if args.output:
                    checker.save_results(results, args.output)
                
                # Aguardar 60 segundos
                await asyncio.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro durante verificação: {e}")
                await asyncio.sleep(10)
    else:
        # Execução única
        results = await checker.run_all_checks()
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        if args.output:
            checker.save_results(results, args.output)
        
        # Exit code baseado no status
        status = results["overall"]["status"]
        if status == "critical":
            sys.exit(2)
        elif status in ["warning", "unhealthy", "degraded"]:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 