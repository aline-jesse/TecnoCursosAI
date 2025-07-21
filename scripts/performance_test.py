#!/usr/bin/env python3
"""
Testes de Performance - TecnoCursos AI
Executa testes de carga, stress e performance da aplicação
"""

import sys
import time
import json
import asyncio
import argparse
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import matplotlib.pyplot as plt
from locust import HttpUser, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging


# Configurações de teste
TEST_CONFIGS = {
    "development": {
        "base_url": "http://localhost:8000",
        "users": 10,
        "spawn_rate": 2,
        "duration": 60
    },
    "staging": {
        "base_url": "https://staging.tecnocursos.ai",
        "users": 50,
        "spawn_rate": 5,
        "duration": 300
    },
    "production": {
        "base_url": "https://tecnocursos.ai",
        "users": 100,
        "spawn_rate": 10,
        "duration": 600
    }
}


class PerformanceMetrics:
    """Coleta e análise de métricas de performance"""
    
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "error_rates": [],
            "throughput": [],
            "cpu_usage": [],
            "memory_usage": [],
            "concurrent_users": [],
            "timestamps": []
        }
        self.start_time = None
        self.end_time = None
    
    def start_monitoring(self):
        """Inicia monitoramento de métricas"""
        self.start_time = datetime.now()
        
    def stop_monitoring(self):
        """Para monitoramento de métricas"""
        self.end_time = datetime.now()
    
    def add_response_time(self, response_time: float):
        """Adiciona tempo de resposta"""
        self.metrics["response_times"].append(response_time)
        self.metrics["timestamps"].append(datetime.now())
    
    def add_error_rate(self, error_rate: float):
        """Adiciona taxa de erro"""
        self.metrics["error_rates"].append(error_rate)
    
    def add_system_metrics(self):
        """Adiciona métricas do sistema"""
        self.metrics["cpu_usage"].append(psutil.cpu_percent())
        self.metrics["memory_usage"].append(psutil.virtual_memory().percent)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calcula estatísticas das métricas"""
        if not self.metrics["response_times"]:
            return {}
        
        response_times = self.metrics["response_times"]
        
        return {
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            "total_requests": len(response_times),
            "response_time": {
                "min": min(response_times),
                "max": max(response_times),
                "avg": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": self._percentile(response_times, 95),
                "p99": self._percentile(response_times, 99)
            },
            "throughput": {
                "rps": len(response_times) / ((self.end_time - self.start_time).total_seconds()) if self.end_time else 0
            },
            "errors": {
                "total": sum(1 for rt in response_times if rt < 0),
                "rate": sum(1 for rt in response_times if rt < 0) / len(response_times) * 100
            },
            "system": {
                "avg_cpu": statistics.mean(self.metrics["cpu_usage"]) if self.metrics["cpu_usage"] else 0,
                "avg_memory": statistics.mean(self.metrics["memory_usage"]) if self.metrics["memory_usage"] else 0
            }
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcula percentil"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def generate_report(self, output_file: str = "performance_report.html"):
        """Gera relatório HTML"""
        stats = self.get_statistics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório de Performance - TecnoCursos AI</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .error {{ color: red; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Performance</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            
            <div class="metric">
                <h2>Resumo Geral</h2>
                <p><strong>Duração do teste:</strong> {stats.get('duration', 0):.2f} segundos</p>
                <p><strong>Total de requisições:</strong> {stats.get('total_requests', 0)}</p>
                <p><strong>Throughput:</strong> {stats.get('throughput', {}).get('rps', 0):.2f} req/s</p>
                <p><strong>Taxa de erro:</strong> {stats.get('errors', {}).get('rate', 0):.2f}%</p>
            </div>
            
            <div class="metric">
                <h2>Tempos de Resposta</h2>
                <table>
                    <tr><th>Métrica</th><th>Valor (ms)</th></tr>
                    <tr><td>Mínimo</td><td>{stats.get('response_time', {}).get('min', 0) * 1000:.2f}</td></tr>
                    <tr><td>Máximo</td><td>{stats.get('response_time', {}).get('max', 0) * 1000:.2f}</td></tr>
                    <tr><td>Média</td><td>{stats.get('response_time', {}).get('avg', 0) * 1000:.2f}</td></tr>
                    <tr><td>Mediana</td><td>{stats.get('response_time', {}).get('median', 0) * 1000:.2f}</td></tr>
                    <tr><td>P95</td><td>{stats.get('response_time', {}).get('p95', 0) * 1000:.2f}</td></tr>
                    <tr><td>P99</td><td>{stats.get('response_time', {}).get('p99', 0) * 1000:.2f}</td></tr>
                </table>
            </div>
            
            <div class="metric">
                <h2>Recursos do Sistema</h2>
                <p><strong>CPU média:</strong> {stats.get('system', {}).get('avg_cpu', 0):.2f}%</p>
                <p><strong>Memória média:</strong> {stats.get('system', {}).get('avg_memory', 0):.2f}%</p>
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Relatório salvo em: {output_file}")


class TecnoCursosUser(HttpUser):
    """Usuário Locust para testes de carga"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Executa login no início"""
        self.login()
    
    def login(self):
        """Faz login na aplicação"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@tecnocursos.ai",
            "password": "testpassword"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    @task(3)
    def view_dashboard(self):
        """Visualiza dashboard"""
        self.client.get("/api/v1/stats/dashboard")
    
    @task(2)
    def list_projects(self):
        """Lista projetos"""
        self.client.get("/api/v1/projects/")
    
    @task(2)
    def list_files(self):
        """Lista arquivos"""
        self.client.get("/api/v1/files/")
    
    @task(1)
    def create_project(self):
        """Cria projeto"""
        self.client.post("/api/v1/projects/", json={
            "title": f"Projeto Teste {time.time()}",
            "description": "Projeto criado durante teste de carga"
        })
    
    @task(1)
    def view_user_profile(self):
        """Visualiza perfil do usuário"""
        self.client.get("/api/v1/users/me")
    
    @task(1)
    def health_check(self):
        """Verifica health check"""
        self.client.get("/health")


class APITester:
    """Testador de API específico"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.metrics = PerformanceMetrics()
    
    async def setup(self):
        """Configuração inicial"""
        await self.login()
    
    async def login(self):
        """Faz login para obter token"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/auth/login", json={
                "email": "test@tecnocursos.ai",
                "password": "testpassword"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                return True
            
        except Exception as e:
            print(f"Erro no login: {e}")
        
        return False
    
    async def test_endpoint(self, method: str, endpoint: str, data: dict = None) -> Tuple[float, int]:
        """Testa um endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                return -1, 400
            
            response_time = time.time() - start_time
            return response_time, response.status_code
            
        except Exception as e:
            print(f"Erro ao testar {endpoint}: {e}")
            return -1, 500
    
    async def run_endpoint_tests(self, tests: List[Dict], concurrent_users: int = 10):
        """Executa testes de endpoints com usuários concorrentes"""
        self.metrics.start_monitoring()
        
        async def run_test_sequence():
            for test in tests:
                response_time, status_code = await self.test_endpoint(
                    test["method"],
                    test["endpoint"],
                    test.get("data")
                )
                
                self.metrics.add_response_time(response_time)
                if status_code >= 400:
                    print(f"Erro {status_code} em {test['endpoint']}")
                
                # Monitorar recursos do sistema
                self.metrics.add_system_metrics()
                
                # Pequena pausa entre requisições
                await asyncio.sleep(0.1)
        
        # Executar testes com usuários concorrentes
        tasks = [run_test_sequence() for _ in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        self.metrics.stop_monitoring()
        return self.metrics.get_statistics()


def run_locust_test(host: str, users: int, spawn_rate: int, duration: int):
    """Executa teste Locust"""
    setup_logging("INFO", None)
    
    # Configurar ambiente Locust
    env = Environment(user_classes=[TecnoCursosUser])
    env.create_local_runner()
    
    # Configurar estatísticas
    gevent = None
    try:
        import gevent
    except ImportError:
        pass
    
    if gevent:
        gevent.spawn(stats_printer(env.stats))
        gevent.spawn(stats_history, env.runner)
    
    # Executar teste
    env.runner.start(users, spawn_rate=spawn_rate)
    
    if gevent:
        gevent.sleep(duration)
    else:
        time.sleep(duration)
    
    env.runner.stop()
    
    # Coletar estatísticas
    stats = env.stats
    
    return {
        "total_requests": stats.total.num_requests,
        "total_failures": stats.total.num_failures,
        "avg_response_time": stats.total.avg_response_time,
        "min_response_time": stats.total.min_response_time,
        "max_response_time": stats.total.max_response_time,
        "rps": stats.total.current_rps,
        "failure_rate": stats.total.fail_ratio * 100
    }


async def run_stress_test(base_url: str, max_users: int = 100, step: int = 10, duration: int = 30):
    """Executa teste de stress aumentando gradualmente a carga"""
    print("Iniciando teste de stress...")
    
    results = []
    
    for users in range(step, max_users + 1, step):
        print(f"Testando com {users} usuários...")
        
        tester = APITester(base_url)
        await tester.setup()
        
        # Definir testes básicos
        tests = [
            {"method": "GET", "endpoint": "/health"},
            {"method": "GET", "endpoint": "/api/v1/stats/dashboard"},
            {"method": "GET", "endpoint": "/api/v1/projects/"},
            {"method": "GET", "endpoint": "/api/v1/files/"}
        ]
        
        # Executar teste com número atual de usuários
        start_time = time.time()
        stats = await tester.run_endpoint_tests(tests, users)
        end_time = time.time()
        
        results.append({
            "users": users,
            "duration": end_time - start_time,
            "avg_response_time": stats.get("response_time", {}).get("avg", 0),
            "error_rate": stats.get("errors", {}).get("rate", 0),
            "throughput": stats.get("throughput", {}).get("rps", 0)
        })
        
        # Parar se taxa de erro for muito alta
        if stats.get("errors", {}).get("rate", 0) > 50:
            print(f"Taxa de erro muito alta ({stats.get('errors', {}).get('rate', 0):.2f}%), parando teste.")
            break
        
        # Pausa entre testes
        await asyncio.sleep(5)
    
    return results


def generate_charts(results: List[Dict], output_dir: str = "charts"):
    """Gera gráficos dos resultados"""
    Path(output_dir).mkdir(exist_ok=True)
    
    if not results:
        return
    
    users = [r["users"] for r in results]
    response_times = [r["avg_response_time"] * 1000 for r in results]  # Convert to ms
    error_rates = [r["error_rate"] for r in results]
    throughput = [r["throughput"] for r in results]
    
    # Gráfico de tempo de resposta
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(users, response_times, 'b-o')
    plt.title('Tempo de Resposta vs Usuários')
    plt.xlabel('Usuários Concorrentes')
    plt.ylabel('Tempo de Resposta (ms)')
    plt.grid(True)
    
    # Gráfico de taxa de erro
    plt.subplot(2, 2, 2)
    plt.plot(users, error_rates, 'r-o')
    plt.title('Taxa de Erro vs Usuários')
    plt.xlabel('Usuários Concorrentes')
    plt.ylabel('Taxa de Erro (%)')
    plt.grid(True)
    
    # Gráfico de throughput
    plt.subplot(2, 2, 3)
    plt.plot(users, throughput, 'g-o')
    plt.title('Throughput vs Usuários')
    plt.xlabel('Usuários Concorrentes')
    plt.ylabel('Requisições por Segundo')
    plt.grid(True)
    
    # Gráfico combinado
    plt.subplot(2, 2, 4)
    plt.plot(users, response_times, 'b-', label='Tempo Resposta (ms)')
    plt.plot(users, [t * 10 for t in throughput], 'g-', label='Throughput x10')
    plt.plot(users, [e * 10 for e in error_rates], 'r-', label='Erro % x10')
    plt.title('Métricas Combinadas')
    plt.xlabel('Usuários Concorrentes')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/performance_charts.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gráficos salvos em: {output_dir}/performance_charts.png")


async def main():
    parser = argparse.ArgumentParser(description="Testes de Performance - TecnoCursos AI")
    parser.add_argument("--environment", choices=["development", "staging", "production"],
                       default="development", help="Ambiente para teste")
    parser.add_argument("--test-type", choices=["load", "stress", "endurance", "spike"],
                       default="load", help="Tipo de teste")
    parser.add_argument("--users", type=int, help="Número de usuários concorrentes")
    parser.add_argument("--duration", type=int, help="Duração do teste em segundos")
    parser.add_argument("--test-mode", action="store_true", help="Modo de teste rápido para CI")
    parser.add_argument("--output-dir", default="performance_results", help="Diretório de saída")
    
    args = parser.parse_args()
    
    # Configuração baseada no ambiente
    config = TEST_CONFIGS[args.environment]
    
    if args.test_mode:
        config.update({"users": 5, "duration": 30})
    
    if args.users:
        config["users"] = args.users
    if args.duration:
        config["duration"] = args.duration
    
    print(f"Executando teste de {args.test_type} no ambiente {args.environment}")
    print(f"Configuração: {config}")
    
    # Criar diretório de saída
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    if args.test_type == "load":
        print("Executando teste de carga...")
        results = run_locust_test(
            config["base_url"],
            config["users"],
            config["spawn_rate"],
            config["duration"]
        )
    
    elif args.test_type == "stress":
        print("Executando teste de stress...")
        stress_results = await run_stress_test(
            config["base_url"],
            config["users"],
            config["spawn_rate"],
            config["duration"]
        )
        
        # Gerar gráficos dos resultados de stress
        generate_charts(stress_results, str(output_dir))
        
        # Salvar resultados JSON
        with open(output_dir / "stress_test_results.json", "w") as f:
            json.dump(stress_results, f, indent=2)
        
        results = {"stress_test_results": stress_results}
    
    elif args.test_type == "endurance":
        print("Executando teste de resistência...")
        # Teste de longa duração com carga constante
        results = run_locust_test(
            config["base_url"],
            config["users"] // 2,  # Carga mais baixa por mais tempo
            config["spawn_rate"],
            config["duration"] * 3  # 3x mais tempo
        )
    
    elif args.test_type == "spike":
        print("Executando teste de pico...")
        # Teste com picos súbitos de carga
        spike_results = []
        
        for spike in [config["users"] // 4, config["users"], config["users"] * 2]:
            print(f"Pico de {spike} usuários...")
            spike_result = run_locust_test(
                config["base_url"],
                spike,
                spike * 2,  # Spawn rate alto para pico rápido
                60  # 1 minuto por pico
            )
            spike_result["spike_users"] = spike
            spike_results.append(spike_result)
        
        results = {"spike_test_results": spike_results}
    
    # Salvar resultados
    results_file = output_dir / f"{args.test_type}_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Gerar relatório
    metrics = PerformanceMetrics()
    report_file = output_dir / f"{args.test_type}_performance_report.html"
    metrics.generate_report(str(report_file))
    
    print(f"\nResultados salvos em: {output_dir}")
    print(f"Relatório: {report_file}")
    
    # Resumo no console
    print("\n=== RESUMO DOS RESULTADOS ===")
    if isinstance(results, dict) and "total_requests" in results:
        print(f"Total de requisições: {results['total_requests']}")
        print(f"Total de falhas: {results['total_failures']}")
        print(f"Tempo médio de resposta: {results['avg_response_time']:.2f}ms")
        print(f"RPS: {results['rps']:.2f}")
        print(f"Taxa de falha: {results['failure_rate']:.2f}%")
    
    return results


if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        results = asyncio.run(main())
        
        # Exit code baseado nos resultados
        if isinstance(results, dict) and results.get("failure_rate", 0) > 10:
            print("\nTeste falhou: Taxa de erro muito alta!")
            sys.exit(1)
        else:
            print("\nTeste concluído com sucesso!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\nErro durante o teste: {e}")
        sys.exit(1) 