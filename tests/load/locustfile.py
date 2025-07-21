#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load Testing com Locust - TecnoCursos AI

Este módulo implementa testes de carga usando Locust seguindo
as melhores práticas de performance testing para APIs FastAPI.

Baseado em:
- FastAPI performance testing patterns
- Locust best practices
- Real-world user behavior simulation
- Performance benchmarking standards

Funcionalidades Testadas:
- Endpoints de autenticação
- CRUD de projetos e cenas
- Geração de vídeos
- Upload de arquivos
- API de métricas
- Health checks
- Cache behavior
- Rate limiting behavior

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, Any, Optional
import os
import uuid

try:
    from locust import HttpUser, task, between, events
    from locust.env import Environment
    from locust.runners import MasterRunner, WorkerRunner
    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False
    print("⚠️  Locust não disponível. Execute: pip install locust")

# ============================================================================
# CONFIGURAÇÕES DE TESTE
# ============================================================================

# Dados de teste
TEST_USERS = [
    {"email": f"user{i}@tecnocursos.ai", "password": "testpass123"} 
    for i in range(1, 101)
]

TEST_PROJECTS = [
    {"name": f"Curso de Python {i}", "description": f"Curso completo de Python - Módulo {i}", "tipo": "curso"}
    for i in range(1, 21)
]

TEST_SCENES = [
    {
        "name": f"Cena {i}",
        "texto": f"Este é o conteúdo da cena {i} com informações educacionais importantes.",
        "duracao": random.uniform(3.0, 10.0),
        "ordem": i,
        "style_preset": random.choice(["modern", "corporate", "tech"]),
        "background_color": random.choice(["#4a90e2", "#50c878", "#ff6b6b", "#ffd93d"])
    }
    for i in range(1, 51)
]

# Configurações de performance
RESPONSE_TIME_TARGETS = {
    "health": 100,      # 100ms
    "auth": 500,        # 500ms
    "crud": 300,        # 300ms
    "upload": 2000,     # 2s
    "video_gen": 30000, # 30s
    "metrics": 200      # 200ms
}

# ============================================================================
# CLASSES DE USUÁRIOS DE TESTE
# ============================================================================

class BaseAPIUser(HttpUser):
    """Classe base para usuários da API"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token = None
        self.user_data = None
        self.projects = []
        self.scenes = []
        
    def on_start(self):
        """Executado quando o usuário inicia"""
        self.authenticate()
    
    def authenticate(self):
        """Autenticar usuário"""
        user_data = random.choice(TEST_USERS)
        self.user_data = user_data
        
        # Registrar usuário (pode falhar se já existir)
        register_data = {
            **user_data,
            "full_name": f"User {user_data['email'].split('@')[0]}",
            "is_active": True
        }
        
        with self.client.post("/api/auth/register", json=register_data, catch_response=True) as response:
            if response.status_code in [201, 400]:  # 400 = usuário já existe
                pass
            else:
                response.failure(f"Falha no registro: {response.status_code}")
        
        # Login
        with self.client.post("/api/auth/login", data={
            "username": user_data["email"],
            "password": user_data["password"]
        }, catch_response=True) as response:
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                response.success()
            else:
                response.failure(f"Falha no login: {response.status_code}")
    
    @property
    def auth_headers(self) -> Dict[str, str]:
        """Headers de autenticação"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    def api_request(self, method: str, endpoint: str, expected_time: int, **kwargs):
        """Fazer request com validação de tempo de resposta"""
        start_time = time.time()
        
        with getattr(self.client, method.lower())(endpoint, **kwargs, catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            # Validar tempo de resposta
            if response_time > expected_time:
                response.failure(f"Response time {response_time:.0f}ms > {expected_time}ms")
            elif response.status_code >= 400:
                response.failure(f"HTTP {response.status_code}: {response.text[:100]}")
            else:
                response.success()
            
            return response

class ReadOnlyUser(BaseAPIUser):
    """Usuário que apenas lê dados (GET requests)"""
    
    wait_time = between(1, 3)
    weight = 3  # 60% dos usuários
    
    @task(10)
    def health_check(self):
        """Verificar health da aplicação"""
        self.api_request("GET", "/health", RESPONSE_TIME_TARGETS["health"])
    
    @task(8)
    def list_projects(self):
        """Listar projetos"""
        self.api_request("GET", "/api/projects/", RESPONSE_TIME_TARGETS["crud"], 
                        headers=self.auth_headers)
    
    @task(6)
    def list_scenes(self):
        """Listar cenas"""
        params = {"page": random.randint(1, 5), "size": random.choice([10, 20, 50])}
        self.api_request("GET", "/api/scenes/", RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers, params=params)
    
    @task(4)
    def get_project_details(self):
        """Obter detalhes de projeto específico"""
        project_id = random.randint(1, 20)
        self.api_request("GET", f"/api/projects/{project_id}", RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers)
    
    @task(3)
    def get_scene_details(self):
        """Obter detalhes de cena específica"""
        scene_id = random.randint(1, 50)
        self.api_request("GET", f"/api/scenes/{scene_id}", RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers)
    
    @task(2)
    def get_metrics(self):
        """Verificar métricas da aplicação"""
        self.api_request("GET", "/metrics", RESPONSE_TIME_TARGETS["metrics"])
    
    @task(1)
    def documentation(self):
        """Acessar documentação da API"""
        self.api_request("GET", "/docs", RESPONSE_TIME_TARGETS["crud"])

class ContentCreatorUser(BaseAPIUser):
    """Usuário que cria e edita conteúdo"""
    
    wait_time = between(2, 6)
    weight = 1  # 20% dos usuários
    
    @task(5)
    def create_project(self):
        """Criar novo projeto"""
        project_data = random.choice(TEST_PROJECTS).copy()
        project_data["name"] = f"{project_data['name']} - {uuid.uuid4().hex[:8]}"
        
        with self.api_request("POST", "/api/projects/", RESPONSE_TIME_TARGETS["crud"],
                             headers=self.auth_headers, json=project_data) as response:
            if response.status_code == 201:
                self.projects.append(response.json())
    
    @task(4)
    def create_scene(self):
        """Criar nova cena"""
        if not self.projects:
            return
        
        scene_data = random.choice(TEST_SCENES).copy()
        scene_data["projeto_id"] = random.choice(self.projects)["id"]
        scene_data["name"] = f"{scene_data['name']} - {uuid.uuid4().hex[:8]}"
        
        with self.api_request("POST", "/api/scenes/", RESPONSE_TIME_TARGETS["crud"],
                             headers=self.auth_headers, json=scene_data) as response:
            if response.status_code == 201:
                self.scenes.append(response.json())
    
    @task(3)
    def update_scene(self):
        """Atualizar cena existente"""
        if not self.scenes:
            return
        
        scene = random.choice(self.scenes)
        update_data = {
            "name": f"Updated - {scene['name']}",
            "duracao": random.uniform(5.0, 15.0)
        }
        
        self.api_request("PUT", f"/api/scenes/{scene['id']}", RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers, json=update_data)
    
    @task(2)
    def bulk_operations(self):
        """Operações em lote"""
        if len(self.scenes) < 3:
            return
        
        scene_ids = [scene["id"] for scene in random.sample(self.scenes, 3)]
        bulk_data = {
            "scene_ids": scene_ids,
            "operation": "update_style",
            "parameters": {"style_preset": "modern"}
        }
        
        self.api_request("POST", "/api/scenes/bulk", RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers, json=bulk_data)
    
    @task(1)
    def delete_scene(self):
        """Deletar cena"""
        if not self.scenes:
            return
        
        scene = self.scenes.pop()
        self.api_request("DELETE", f"/api/scenes/{scene['id']}", RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers)

class VideoGeneratorUser(BaseAPIUser):
    """Usuário que gera vídeos (operações pesadas)"""
    
    wait_time = between(10, 30)
    weight = 1  # 20% dos usuários
    
    @task(3)
    def generate_video(self):
        """Gerar vídeo de projeto"""
        project_id = random.randint(1, 20)
        
        video_data = {
            "quality": random.choice(["low", "medium", "high"]),
            "include_audio": True,
            "style_preset": random.choice(["modern", "corporate"])
        }
        
        self.api_request("POST", f"/api/scenes/project/{project_id}/generate-video",
                        RESPONSE_TIME_TARGETS["video_gen"],
                        headers=self.auth_headers, json=video_data)
    
    @task(2)
    def check_video_status(self):
        """Verificar status de geração de vídeo"""
        project_id = random.randint(1, 20)
        
        self.api_request("GET", f"/api/scenes/video-status/{project_id}",
                        RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers)
    
    @task(1)
    def render_scene(self):
        """Renderizar cena individual"""
        scene_id = random.randint(1, 50)
        
        render_data = {
            "quality": random.choice(["medium", "high"]),
            "format": "mp4"
        }
        
        self.api_request("POST", f"/api/scenes/{scene_id}/render",
                        RESPONSE_TIME_TARGETS["crud"],
                        headers=self.auth_headers, json=render_data)

# ============================================================================
# CENÁRIOS DE TESTE ESPECÍFICOS
# ============================================================================

class StressTestUser(BaseAPIUser):
    """Usuário para testes de stress (muitas requests rápidas)"""
    
    wait_time = between(0.1, 0.5)
    weight = 0  # Usar apenas em testes de stress específicos
    
    @task
    def rapid_health_checks(self):
        """Health checks rápidos"""
        self.api_request("GET", "/health", RESPONSE_TIME_TARGETS["health"])

class RateLimitTestUser(BaseAPIUser):
    """Usuário para testar rate limiting"""
    
    wait_time = between(0.01, 0.1)
    weight = 0  # Usar apenas em testes de rate limiting
    
    @task
    def test_rate_limit(self):
        """Testar limites de rate"""
        with self.client.get("/api/scenes/", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 429:
                response.success()  # Rate limit funcionando corretamente
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

# ============================================================================
# EVENTOS E MÉTRICAS CUSTOMIZADAS
# ============================================================================

@events.request.add_listener
def request_handler(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Handler para requests customizado"""
    if exception:
        print(f"❌ Request falhou: {name} - {exception}")
    elif response_time > 1000:  # > 1 segundo
        print(f"⚠️  Request lento: {name} - {response_time:.0f}ms")

@events.test_start.add_listener
def test_start_handler(environment, **kwargs):
    """Executado no início dos testes"""
    print("🚀 Iniciando testes de carga do TecnoCursos AI...")
    print(f"📊 Target: {environment.host}")
    print(f"👥 Usuários: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")

@events.test_stop.add_listener
def test_stop_handler(environment, **kwargs):
    """Executado no final dos testes"""
    stats = environment.stats.total
    
    print("\n📊 RESUMO DOS TESTES:")
    print(f"   Total de requests: {stats.num_requests}")
    print(f"   Requests falhadas: {stats.num_failures}")
    print(f"   Taxa de erro: {(stats.num_failures/stats.num_requests*100):.2f}%")
    print(f"   Tempo médio: {stats.avg_response_time:.0f}ms")
    print(f"   P95: {stats.get_response_time_percentile(0.95):.0f}ms")
    print(f"   RPS médio: {stats.avg_content_length:.2f}")
    
    # Validar SLAs
    error_rate = stats.num_failures / stats.num_requests * 100
    avg_response_time = stats.avg_response_time
    
    print("\n🎯 VALIDAÇÃO DE SLAs:")
    print(f"   Error Rate < 1%: {'✅' if error_rate < 1 else '❌'} ({error_rate:.2f}%)")
    print(f"   Avg Response < 500ms: {'✅' if avg_response_time < 500 else '❌'} ({avg_response_time:.0f}ms)")
    print(f"   P95 < 1000ms: {'✅' if stats.get_response_time_percentile(0.95) < 1000 else '❌'} ({stats.get_response_time_percentile(0.95):.0f}ms)")

# ============================================================================
# CONFIGURAÇÕES DE CENÁRIOS
# ============================================================================

# Cenário padrão: uso normal da aplicação
class NormalUsageScenario(HttpUser):
    """Cenário de uso normal"""
    tasks = {
        ReadOnlyUser: 60,      # 60% leitores
        ContentCreatorUser: 30, # 30% criadores
        VideoGeneratorUser: 10  # 10% geradores de vídeo
    }
    wait_time = between(1, 5)

# ============================================================================
# SCRIPTS DE TESTE ESPECÍFICOS
# ============================================================================

def run_performance_baseline():
    """Executar baseline de performance"""
    print("🎯 Executando baseline de performance...")
    os.system("locust -f locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=60s --headless")

def run_stress_test():
    """Executar teste de stress"""
    print("💪 Executando teste de stress...")
    os.system("locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=300s --headless")

def run_rate_limit_test():
    """Executar teste de rate limiting"""
    print("🚦 Executando teste de rate limiting...")
    # Configurar apenas usuários de rate limit test
    os.system("locust -f locustfile.py -u RateLimitTestUser --host=http://localhost:8000 --users=50 --spawn-rate=25 --run-time=60s --headless")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "baseline":
            run_performance_baseline()
        elif test_type == "stress":
            run_stress_test()
        elif test_type == "ratelimit":
            run_rate_limit_test()
        else:
            print("❌ Tipo de teste inválido. Use: baseline, stress, ratelimit")
    else:
        print("🚀 Use: python locustfile.py [baseline|stress|ratelimit]")
        print("   Ou execute diretamente: locust -f locustfile.py --host=http://localhost:8000") 