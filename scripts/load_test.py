#!/usr/bin/env python3
"""
LOAD TESTING - TECNOCURSOS AI
=============================
Sistema avançado de teste de carga usando Locust
"""

import json
import time
import random
import string
from typing import Dict, Any, Optional
from pathlib import Path
import argparse
import logging
from datetime import datetime

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner
import requests

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TecnoCursosUser(HttpUser):
    """Usuário simulado para testes de carga"""
    
    wait_time = between(1, 5)  # Aguarda entre 1-5 segundos entre tarefas
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token = None
        self.user_id = None
        self.project_id = None
        self.scene_id = None
        
    def on_start(self):
        """Executado quando usuário inicia"""
        self.register_user()
        self.login_user()
    
    def register_user(self):
        """Registra um novo usuário"""
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        
        user_data = {
            "name": f"Load Test User {random_suffix}",
            "email": f"loadtest_{timestamp}_{random_suffix}@test.com",
            "password": "LoadTest123!",
            "confirm_password": "LoadTest123!"
        }
        
        with self.client.post(
            "/api/v1/auth/register",
            json=user_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                self.user_id = data.get("id") or data.get("user_id")
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}")
    
    def login_user(self):
        """Faz login do usuário"""
        if not self.user_id:
            return
        
        # Tentar login com credenciais padrão primeiro
        login_data = {
            "username": "admin@tecnocursos.ai",
            "password": "admin123"
        }
        
        with self.client.post(
            "/api/v1/auth/login",
            data=login_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.client.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @task(10)
    def view_health(self):
        """Verifica health endpoint (alta frequência)"""
        self.client.get("/health")
    
    @task(8)
    def view_dashboard(self):
        """Acessa dashboard principal"""
        if self.auth_token:
            self.client.get("/api/v1/dashboard")
    
    @task(6)
    def list_projects(self):
        """Lista projetos do usuário"""
        if self.auth_token:
            self.client.get("/api/v1/projects")
    
    @task(5)
    def create_project(self):
        """Cria um novo projeto"""
        if not self.auth_token:
            return
        
        project_data = {
            "name": f"Load Test Project {random.randint(1000, 9999)}",
            "description": "Projeto criado durante teste de carga",
            "type": "video"
        }
        
        with self.client.post(
            "/api/v1/projects",
            json=project_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                self.project_id = data.get("id")
                response.success()
            else:
                response.failure(f"Project creation failed: {response.status_code}")
    
    @task(4)
    def list_scenes(self):
        """Lista cenas disponíveis"""
        if self.auth_token:
            self.client.get("/api/v1/scenes")
    
    @task(3)
    def create_scene(self):
        """Cria uma nova cena"""
        if not self.auth_token or not self.project_id:
            return
        
        scene_data = {
            "name": f"Load Test Scene {random.randint(100, 999)}",
            "project_id": self.project_id,
            "type": "presentation",
            "duration": random.randint(30, 300)
        }
        
        with self.client.post(
            "/api/v1/scenes",
            json=scene_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                self.scene_id = data.get("id")
                response.success()
            else:
                response.failure(f"Scene creation failed: {response.status_code}")
    
    @task(3)
    def list_assets(self):
        """Lista assets da biblioteca"""
        if self.auth_token:
            params = {
                "page": 1,
                "limit": 20,
                "type": random.choice(["image", "video", "audio", "document"])
            }
            self.client.get("/api/v1/assets", params=params)
    
    @task(2)
    def upload_file(self):
        """Simula upload de arquivo pequeno"""
        if not self.auth_token:
            return
        
        # Criar arquivo de teste pequeno
        test_content = f"Load test file content {random.randint(1000, 9999)}"
        
        files = {
            'file': ('test_file.txt', test_content, 'text/plain')
        }
        data = {
            'type': 'document'
        }
        
        with self.client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"File upload failed: {response.status_code}")
    
    @task(2)
    def generate_tts(self):
        """Gera áudio TTS"""
        if not self.auth_token:
            return
        
        tts_data = {
            "text": f"Este é um teste de carga número {random.randint(1, 1000)}",
            "voice": random.choice(["nova", "alloy", "echo"]),
            "speed": random.choice([0.8, 1.0, 1.2])
        }
        
        with self.client.post(
            "/api/v1/tts/synthesize",
            json=tts_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"TTS generation failed: {response.status_code}")
    
    @task(1)
    def generate_avatar_video(self):
        """Gera vídeo com avatar (operação pesada)"""
        if not self.auth_token:
            return
        
        avatar_data = {
            "text": f"Vídeo de teste de carga {random.randint(1, 100)}",
            "voice": "nova",
            "avatar_style": random.choice(["teacher", "professional", "casual"])
        }
        
        with self.client.post(
            "/api/v1/avatar/generate",
            json=avatar_data,
            catch_response=True,
            timeout=60  # Operação mais demorada
        ) as response:
            if response.status_code in [200, 201, 202]:  # Aceitar async
                response.success()
            else:
                response.failure(f"Avatar video failed: {response.status_code}")
    
    @task(1)
    def stress_database(self):
        """Operações que estressam o banco de dados"""
        if not self.auth_token:
            return
        
        # Busca complexa
        search_params = {
            "q": random.choice(["python", "javascript", "curso", "tutorial"]),
            "type": "project",
            "sort": "created_at",
            "order": "desc",
            "limit": 50
        }
        
        self.client.get("/api/v1/search", params=search_params)

class AdminUser(HttpUser):
    """Usuário administrativo para testes específicos"""
    
    wait_time = between(2, 8)
    weight = 1  # Menor peso (menos usuários admin)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token = None
    
    def on_start(self):
        """Login como admin"""
        login_data = {
            "username": "admin@tecnocursos.ai",
            "password": "admin123"
        }
        
        with self.client.post("/api/v1/auth/login", data=login_data) as response:
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.client.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
    
    @task(5)
    def view_analytics(self):
        """Visualiza analytics do sistema"""
        if self.auth_token:
            self.client.get("/api/v1/admin/analytics")
    
    @task(3)
    def view_system_stats(self):
        """Visualiza estatísticas do sistema"""
        if self.auth_token:
            self.client.get("/api/v1/admin/stats")
    
    @task(2)
    def manage_users(self):
        """Gerencia usuários"""
        if self.auth_token:
            self.client.get("/api/v1/admin/users")
    
    @task(1)
    def system_health_detailed(self):
        """Health check detalhado"""
        if self.auth_token:
            self.client.get("/api/v1/admin/health/detailed")

# Eventos para coleta de métricas personalizadas
@events.request.add_listener
def request_handler(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Handler personalizado para requests"""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")

@events.quitting.add_listener
def quitting_handler(environment, **kwargs):
    """Handler executado ao finalizar testes"""
    if isinstance(environment.runner, MasterRunner):
        logger.info("Load test completed - generating report...")
        generate_load_test_report(environment)

def generate_load_test_report(environment):
    """Gera relatório detalhado do teste de carga"""
    stats = environment.runner.stats
    
    report = {
        "summary": {
            "total_requests": stats.total.num_requests,
            "total_failures": stats.total.num_failures,
            "average_response_time": round(stats.total.avg_response_time, 2),
            "min_response_time": stats.total.min_response_time,
            "max_response_time": stats.total.max_response_time,
            "requests_per_second": round(stats.total.current_rps, 2),
            "failure_rate": round(stats.total.fail_ratio * 100, 2),
            "test_duration": round(time.time() - stats.start_time, 2)
        },
        "endpoints": {},
        "errors": {}
    }
    
    # Estatísticas por endpoint
    for name, entry in stats.entries.items():
        if entry.num_requests > 0:
            report["endpoints"][name] = {
                "requests": entry.num_requests,
                "failures": entry.num_failures,
                "avg_response_time": round(entry.avg_response_time, 2),
                "min_response_time": entry.min_response_time,
                "max_response_time": entry.max_response_time,
                "rps": round(entry.current_rps, 2),
                "failure_rate": round(entry.fail_ratio * 100, 2)
            }
    
    # Erros encontrados
    for error, count in stats.errors.items():
        report["errors"][str(error)] = count
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"load_test_report_{timestamp}.json")
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Load test report saved: {report_path}")
    
    # Log resumo no console
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    print(f"Total Requests: {report['summary']['total_requests']}")
    print(f"Total Failures: {report['summary']['total_failures']}")
    print(f"Failure Rate: {report['summary']['failure_rate']}%")
    print(f"Average Response Time: {report['summary']['average_response_time']}ms")
    print(f"Requests/second: {report['summary']['requests_per_second']}")
    print(f"Test Duration: {report['summary']['test_duration']}s")
    print("="*60)

def run_load_test(
    host: str,
    users: int = 10,
    spawn_rate: int = 2,
    duration: int = 300,
    test_mode: bool = False
):
    """Executa teste de carga programaticamente"""
    import subprocess
    import sys
    
    if test_mode:
        users = 2
        spawn_rate = 1
        duration = 60
    
    cmd = [
        sys.executable, "-m", "locust",
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{duration}s",
        "--headless",
        "--print-stats",
        "--html", f"load_test_report_{int(time.time())}.html",
        "--csv", f"load_test_results_{int(time.time())}",
        "--logfile", f"load_test_{int(time.time())}.log"
    ]
    
    logger.info(f"Starting load test: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        logger.info("Load test completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Load test failed: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Load Test TecnoCursos AI")
    parser.add_argument("--host", default="http://localhost:8000", help="URL base da API")
    parser.add_argument("--users", type=int, default=10, help="Número de usuários simultâneos")
    parser.add_argument("--spawn-rate", type=int, default=2, help="Taxa de criação de usuários/segundo")
    parser.add_argument("--duration", type=int, default=300, help="Duração do teste em segundos")
    parser.add_argument("--test-mode", action="store_true", help="Modo de teste rápido")
    parser.add_argument("--environment", default="staging", help="Ambiente de teste")
    
    args = parser.parse_args()
    
    # Configurar host baseado no ambiente
    if args.environment == "production":
        args.host = "https://api.tecnocursos.ai"
    elif args.environment == "staging":
        args.host = "https://staging-api.tecnocursos.ai"
    
    logger.info(f"Iniciando load test no ambiente: {args.environment}")
    logger.info(f"Host: {args.host}")
    logger.info(f"Usuários: {args.users}")
    logger.info(f"Duração: {args.duration}s")
    
    success = run_load_test(
        host=args.host,
        users=args.users,
        spawn_rate=args.spawn_rate,
        duration=args.duration,
        test_mode=args.test_mode
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 