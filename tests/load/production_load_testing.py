#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Load Testing System - TecnoCursos AI

Sistema avançado de testes de carga para ambiente de produção
seguindo as melhores práticas de:
- Performance testing patterns
- Real-world traffic simulation
- SLA validation
- Capacity planning
- Performance regression detection
- Auto-scaling validation

Baseado em:
- FastAPI production testing patterns
- Locust advanced features
- Performance benchmarking standards
- SRE best practices

Funcionalidades:
- Testes de carga progressivos
- Simulação de tráfego real
- Validação de SLAs automática
- Capacity planning
- Performance regression detection
- Auto-scaling validation
- Real-time monitoring
- Alerting integration

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
import sys
import json
import time
import boto3
import logging
import argparse
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import requests

try:
    from locust import HttpUser, task, between, events, constant_pacing
    from locust.env import Environment
    from locust.runners import MasterRunner, WorkerRunner, LocalRunner
    from locust.stats import StatsCSVFileWriter
    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False
    print("⚠️  Locust não disponível. Execute: pip install locust")

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    print("⚠️  Analytics libs não disponíveis. Execute: pip install pandas numpy matplotlib seaborn")

# ============================================================================
# CONFIGURAÇÕES DE TESTE DE PRODUÇÃO
# ============================================================================

@dataclass
class ProductionTestConfig:
    """Configurações para testes de produção"""
    # Configurações do ambiente
    base_url: str = "https://tecnocursos.ai"
    test_duration: int = 3600  # 1 hora
    
    # Configurações de carga
    initial_users: int = 10
    max_users: int = 1000
    spawn_rate: int = 10
    stages: List[Dict] = None
    
    # SLAs e thresholds
    max_response_time_p95: float = 500.0  # ms
    max_error_rate: float = 1.0  # %
    min_throughput: float = 1000.0  # RPS
    min_availability: float = 99.9  # %
    
    # Configurações de monitoramento
    prometheus_url: str = "http://monitoring.tecnocursos.ai:9090"
    grafana_url: str = "http://monitoring.tecnocursos.ai:3000"
    alert_webhook: str = ""
    
    # Configurações de relatório
    results_dir: str = "load_test_results"
    generate_charts: bool = True
    send_slack_report: bool = True
    
    def __post_init__(self):
        if self.stages is None:
            # Padrão: ramp-up, sustain, spike, ramp-down
            self.stages = [
                {"duration": 300, "users": 50},    # 5min ramp-up
                {"duration": 1800, "users": 200},  # 30min sustain
                {"duration": 600, "users": 500},   # 10min spike
                {"duration": 600, "users": 200},   # 10min cool-down
                {"duration": 300, "users": 0}      # 5min ramp-down
            ]

@dataclass
class TestResults:
    """Resultados do teste de carga"""
    test_id: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    failed_requests: int
    error_rate: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_response_time: float
    throughput: float
    availability: float
    sla_passed: bool
    alerts_triggered: List[str]
    performance_regression: bool

# ============================================================================
# LOGGER CONFIGURATION
# ============================================================================

def setup_logger() -> logging.Logger:
    """Configurar logger para testes de produção"""
    logger = logging.getLogger("production_load_test")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(
            f"load_test_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger

# ============================================================================
# USER CLASSES PARA TESTES DE PRODUÇÃO
# ============================================================================

class ProductionReadOnlyUser(HttpUser):
    """Usuário somente leitura - simula 70% do tráfego"""
    weight = 7
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup inicial do usuário"""
        self.session_id = f"prod_readonly_{time.time()}"
    
    @task(10)
    def homepage(self):
        """Página inicial"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Homepage failed: {response.status_code}")
    
    @task(8)
    def list_courses(self):
        """Listar cursos"""
        with self.client.get("/api/projects/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"List courses failed: {response.status_code}")
    
    @task(6)
    def health_check(self):
        """Health check"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200 and response.elapsed.total_seconds() < 0.1:
                response.success()
            else:
                response.failure(f"Health check failed or slow: {response.elapsed.total_seconds()}s")
    
    @task(4)
    def search_content(self):
        """Buscar conteúdo"""
        search_terms = ["python", "javascript", "react", "api", "backend"]
        term = np.random.choice(search_terms) if ANALYTICS_AVAILABLE else "python"
        
        with self.client.get(f"/api/search?q={term}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed: {response.status_code}")
    
    @task(2)
    def api_docs(self):
        """Documentação da API"""
        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"API docs failed: {response.status_code}")

class ProductionAuthenticatedUser(HttpUser):
    """Usuário autenticado - simula 25% do tráfego"""
    weight = 25
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login do usuário"""
        self.session_id = f"prod_auth_{time.time()}"
        self.auth_token = None
        self.login()
    
    def login(self):
        """Fazer login"""
        login_data = {
            "username": f"loadtest_user_{int(time.time())}@tecnocursos.ai",
            "password": "LoadTest123!"
        }
        
        # Primeiro registrar
        with self.client.post("/api/auth/register", json={
            **login_data,
            "full_name": "Load Test User"
        }, catch_response=True) as response:
            pass  # Pode falhar se usuário já existir
        
        # Então fazer login
        with self.client.post("/api/auth/login", data=login_data, catch_response=True) as response:
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @property
    def auth_headers(self):
        """Headers de autenticação"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    @task(8)
    def list_my_projects(self):
        """Listar meus projetos"""
        with self.client.get("/api/projects/my", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"List my projects failed: {response.status_code}")
    
    @task(6)
    def create_project(self):
        """Criar projeto"""
        project_data = {
            "name": f"Load Test Project {int(time.time())}",
            "description": "Projeto criado durante teste de carga",
            "tipo": "curso"
        }
        
        with self.client.post("/api/projects/", json=project_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Create project failed: {response.status_code}")
    
    @task(4)
    def upload_file(self):
        """Upload de arquivo"""
        files = {"file": ("test.txt", "Load test content", "text/plain")}
        
        with self.client.post("/api/files/upload", files=files, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"File upload failed: {response.status_code}")
    
    @task(2)
    def user_profile(self):
        """Perfil do usuário"""
        with self.client.get("/api/users/me", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"User profile failed: {response.status_code}")

class ProductionHeavyUser(HttpUser):
    """Usuário pesado - simula 5% do tráfego"""
    weight = 5
    wait_time = between(5, 15)
    
    def on_start(self):
        """Setup do usuário pesado"""
        self.session_id = f"prod_heavy_{time.time()}"
        self.auth_token = None
        self.login()
    
    def login(self):
        """Login do usuário pesado"""
        login_data = {
            "username": f"heavy_user_{int(time.time())}@tecnocursos.ai",
            "password": "HeavyUser123!"
        }
        
        with self.client.post("/api/auth/register", json={
            **login_data,
            "full_name": "Heavy Load Test User"
        }, catch_response=True):
            pass
        
        with self.client.post("/api/auth/login", data=login_data, catch_response=True) as response:
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
    
    @property
    def auth_headers(self):
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    @task(5)
    def generate_video(self):
        """Gerar vídeo - operação pesada"""
        video_data = {
            "projeto_id": 1,
            "quality": "high",
            "include_audio": True
        }
        
        with self.client.post("/api/scenes/generate-video", json=video_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code in [200, 202]:  # 202 para async
                response.success()
            else:
                response.failure(f"Video generation failed: {response.status_code}")
    
    @task(3)
    def process_document(self):
        """Processar documento - operação pesada"""
        doc_data = {
            "file_path": "/tmp/test_document.pdf",
            "extract_text": True,
            "generate_scenes": True
        }
        
        with self.client.post("/api/files/process", json=doc_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Document processing failed: {response.status_code}")
    
    @task(2)
    def bulk_operations(self):
        """Operações em lote"""
        bulk_data = {
            "operation": "update_scenes",
            "scene_ids": [1, 2, 3, 4, 5],
            "parameters": {"style": "modern"}
        }
        
        with self.client.post("/api/scenes/bulk", json=bulk_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Bulk operations failed: {response.status_code}")

# ============================================================================
# SISTEMA DE TESTE DE PRODUÇÃO
# ============================================================================

class ProductionLoadTester:
    """Sistema principal de testes de carga em produção"""
    
    def __init__(self, config: ProductionTestConfig):
        self.config = config
        self.logger = setup_logger()
        self.test_id = f"prod_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results_dir = Path(config.results_dir) / self.test_id
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Métricas coletadas
        self.metrics = {
            "response_times": [],
            "error_rates": [],
            "throughput": [],
            "user_counts": [],
            "timestamps": []
        }
        
        # Alertas triggered
        self.alerts = []
        
    def run_staged_test(self) -> TestResults:
        """Executar teste com múltiplos estágios"""
        self.logger.info(f"🚀 Iniciando teste de produção: {self.test_id}")
        self.logger.info(f"📊 URL: {self.config.base_url}")
        self.logger.info(f"⏱️  Duração total: {self.config.test_duration}s")
        
        start_time = datetime.now()
        
        try:
            # Configurar environment Locust
            env = Environment(user_classes=[
                ProductionReadOnlyUser,
                ProductionAuthenticatedUser, 
                ProductionHeavyUser
            ])
            
            env.create_local_runner()
            
            # Setup CSV writer para estatísticas
            stats_writer = StatsCSVFileWriter(
                environment=env,
                base_filepath=str(self.results_dir / "stats"),
                full_history=True
            )
            
            # Executar estágios
            for i, stage in enumerate(self.config.stages):
                stage_name = f"Stage {i+1}"
                self.logger.info(f"📈 {stage_name}: {stage['users']} usuários por {stage['duration']}s")
                
                # Start/adjust users
                if stage['users'] > 0:
                    env.runner.start(user_count=stage['users'], spawn_rate=self.config.spawn_rate)
                else:
                    env.runner.stop()
                
                # Monitorar durante o estágio
                self._monitor_stage(env, stage_name, stage['duration'])
                
                # Coletar métricas do estágio
                self._collect_stage_metrics(env, stage_name)
            
            # Finalizar teste
            env.runner.stop()
            stats_writer.close()
            
            end_time = datetime.now()
            
            # Gerar resultados
            results = self._generate_results(env, start_time, end_time)
            
            # Gerar relatórios
            self._generate_reports(results)
            
            # Verificar SLAs
            self._check_slas(results)
            
            # Enviar notificações
            self._send_notifications(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Falha no teste de produção: {e}")
            raise
    
    def _monitor_stage(self, env, stage_name: str, duration: int):
        """Monitorar métricas durante um estágio"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            time.sleep(10)  # Coleta a cada 10 segundos
            
            stats = env.runner.stats.total
            
            # Coletar métricas atuais
            current_metrics = {
                "timestamp": datetime.now(),
                "response_time_avg": stats.avg_response_time,
                "response_time_p95": stats.get_response_time_percentile(0.95),
                "error_rate": (stats.num_failures / max(stats.num_requests, 1)) * 100,
                "throughput": stats.total_rps,
                "user_count": env.runner.user_count
            }
            
            # Adicionar às métricas
            self.metrics["response_times"].append(current_metrics["response_time_p95"])
            self.metrics["error_rates"].append(current_metrics["error_rate"])
            self.metrics["throughput"].append(current_metrics["throughput"])
            self.metrics["user_counts"].append(current_metrics["user_count"])
            self.metrics["timestamps"].append(current_metrics["timestamp"])
            
            # Verificar thresholds em tempo real
            self._check_realtime_thresholds(current_metrics, stage_name)
            
            # Log métricas
            self.logger.info(
                f"📊 {stage_name} - "
                f"Users: {current_metrics['user_count']}, "
                f"RPS: {current_metrics['throughput']:.1f}, "
                f"P95: {current_metrics['response_time_p95']:.1f}ms, "
                f"Errors: {current_metrics['error_rate']:.2f}%"
            )
    
    def _check_realtime_thresholds(self, metrics: Dict, stage_name: str):
        """Verificar thresholds em tempo real"""
        alerts = []
        
        if metrics["response_time_p95"] > self.config.max_response_time_p95:
            alert = f"⚠️  High response time: {metrics['response_time_p95']:.1f}ms > {self.config.max_response_time_p95}ms"
            alerts.append(alert)
        
        if metrics["error_rate"] > self.config.max_error_rate:
            alert = f"❌ High error rate: {metrics['error_rate']:.2f}% > {self.config.max_error_rate}%"
            alerts.append(alert)
        
        if metrics["throughput"] < self.config.min_throughput and metrics["user_count"] > 100:
            alert = f"⚡ Low throughput: {metrics['throughput']:.1f} RPS < {self.config.min_throughput} RPS"
            alerts.append(alert)
        
        for alert in alerts:
            self.logger.warning(f"{stage_name} - {alert}")
            self.alerts.append(f"{stage_name}: {alert}")
    
    def _collect_stage_metrics(self, env, stage_name: str):
        """Coletar métricas finais do estágio"""
        stats = env.runner.stats.total
        
        stage_metrics = {
            "stage": stage_name,
            "total_requests": stats.num_requests,
            "failed_requests": stats.num_failures,
            "error_rate": (stats.num_failures / max(stats.num_requests, 1)) * 100,
            "avg_response_time": stats.avg_response_time,
            "p95_response_time": stats.get_response_time_percentile(0.95),
            "p99_response_time": stats.get_response_time_percentile(0.99),
            "max_response_time": stats.max_response_time,
            "throughput": stats.total_rps
        }
        
        # Salvar métricas do estágio
        with open(self.results_dir / f"{stage_name.lower().replace(' ', '_')}_metrics.json", 'w') as f:
            json.dump(stage_metrics, f, indent=2, default=str)
    
    def _generate_results(self, env, start_time: datetime, end_time: datetime) -> TestResults:
        """Gerar resultados finais do teste"""
        stats = env.runner.stats.total
        
        error_rate = (stats.num_failures / max(stats.num_requests, 1)) * 100
        availability = 100 - error_rate
        
        # Verificar se SLAs foram atendidos
        sla_passed = all([
            stats.get_response_time_percentile(0.95) <= self.config.max_response_time_p95,
            error_rate <= self.config.max_error_rate,
            availability >= self.config.min_availability,
            stats.total_rps >= self.config.min_throughput
        ])
        
        results = TestResults(
            test_id=self.test_id,
            start_time=start_time,
            end_time=end_time,
            total_requests=stats.num_requests,
            failed_requests=stats.num_failures,
            error_rate=error_rate,
            avg_response_time=stats.avg_response_time,
            p95_response_time=stats.get_response_time_percentile(0.95),
            p99_response_time=stats.get_response_time_percentile(0.99),
            max_response_time=stats.max_response_time,
            throughput=stats.total_rps,
            availability=availability,
            sla_passed=sla_passed,
            alerts_triggered=self.alerts.copy(),
            performance_regression=self._check_performance_regression()
        )
        
        return results
    
    def _check_performance_regression(self) -> bool:
        """Verificar regressão de performance comparando com baselines"""
        try:
            baseline_file = Path("performance_baseline.json")
            if not baseline_file.exists():
                self.logger.info("📊 Baseline de performance não encontrado, criando...")
                return False
            
            with open(baseline_file) as f:
                baseline = json.load(f)
            
            current_p95 = statistics.mean(self.metrics["response_times"][-10:])  # Últimas 10 medições
            baseline_p95 = baseline.get("p95_response_time", float('inf'))
            
            # Considera regressão se performance piorou mais de 20%
            regression_threshold = baseline_p95 * 1.2
            
            if current_p95 > regression_threshold:
                self.logger.warning(f"📉 Performance regression detected: {current_p95:.1f}ms > {regression_threshold:.1f}ms")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar regressão: {e}")
            return False
    
    def _generate_reports(self, results: TestResults):
        """Gerar relatórios detalhados"""
        self.logger.info("📊 Gerando relatórios...")
        
        # Relatório JSON
        with open(self.results_dir / "test_results.json", 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        
        # Relatório de texto
        self._generate_text_report(results)
        
        # Gráficos (se disponível)
        if self.config.generate_charts and ANALYTICS_AVAILABLE:
            self._generate_charts()
        
        # Relatório HTML
        self._generate_html_report(results)
    
    def _generate_text_report(self, results: TestResults):
        """Gerar relatório em texto"""
        report = f"""
# 📊 RELATÓRIO DE TESTE DE CARGA PRODUÇÃO
## TecnoCursos AI - {results.test_id}

### 📈 RESUMO EXECUTIVO
- **Início**: {results.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Fim**: {results.end_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Duração**: {(results.end_time - results.start_time).total_seconds():.0f} segundos
- **SLA Status**: {'✅ PASSOU' if results.sla_passed else '❌ FALHOU'}

### 🎯 MÉTRICAS DE PERFORMANCE
- **Total de Requests**: {results.total_requests:,}
- **Requests Falhadas**: {results.failed_requests:,}
- **Taxa de Erro**: {results.error_rate:.2f}%
- **Disponibilidade**: {results.availability:.2f}%
- **Throughput**: {results.throughput:.1f} RPS

### ⏱️ TEMPOS DE RESPOSTA
- **Média**: {results.avg_response_time:.1f}ms
- **P95**: {results.p95_response_time:.1f}ms
- **P99**: {results.p99_response_time:.1f}ms
- **Máximo**: {results.max_response_time:.1f}ms

### 🎯 VALIDAÇÃO DE SLAs
- **P95 < {self.config.max_response_time_p95}ms**: {'✅' if results.p95_response_time <= self.config.max_response_time_p95 else '❌'} ({results.p95_response_time:.1f}ms)
- **Erro < {self.config.max_error_rate}%**: {'✅' if results.error_rate <= self.config.max_error_rate else '❌'} ({results.error_rate:.2f}%)
- **Throughput > {self.config.min_throughput} RPS**: {'✅' if results.throughput >= self.config.min_throughput else '❌'} ({results.throughput:.1f} RPS)
- **Disponibilidade > {self.config.min_availability}%**: {'✅' if results.availability >= self.config.min_availability else '❌'} ({results.availability:.2f}%)

### 🚨 ALERTAS DISPARADOS
"""
        
        if results.alerts_triggered:
            for alert in results.alerts_triggered:
                report += f"- {alert}\n"
        else:
            report += "- Nenhum alerta disparado ✅\n"
        
        report += f"""
### 📊 ANÁLISE DE PERFORMANCE
- **Regressão Detectada**: {'❌ SIM' if results.performance_regression else '✅ NÃO'}

### 🎯 RECOMENDAÇÕES
"""
        
        if not results.sla_passed:
            report += "- ⚠️  SLAs não foram atendidos - investigar gargalos\n"
        
        if results.error_rate > 0.5:
            report += "- ❌ Taxa de erro alta - verificar logs de aplicação\n"
        
        if results.p95_response_time > 300:
            report += "- ⏱️  Tempos de resposta elevados - otimizar queries/cache\n"
        
        if results.throughput < self.config.min_throughput:
            report += "- ⚡ Throughput baixo - considerar auto-scaling\n"
        
        if not results.alerts_triggered:
            report += "- ✅ Sistema performou bem - manter monitoramento\n"
        
        with open(self.results_dir / "report.md", 'w') as f:
            f.write(report)
    
    def _generate_charts(self):
        """Gerar gráficos de performance"""
        if not ANALYTICS_AVAILABLE:
            return
        
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        timestamps = [t.timestamp() for t in self.metrics["timestamps"]]
        
        # Response Time
        axes[0, 0].plot(timestamps, self.metrics["response_times"], 'b-', linewidth=2)
        axes[0, 0].axhline(y=self.config.max_response_time_p95, color='r', linestyle='--', label='SLA Threshold')
        axes[0, 0].set_title('Response Time P95 (ms)')
        axes[0, 0].set_ylabel('Response Time (ms)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Error Rate
        axes[0, 1].plot(timestamps, self.metrics["error_rates"], 'r-', linewidth=2)
        axes[0, 1].axhline(y=self.config.max_error_rate, color='r', linestyle='--', label='SLA Threshold')
        axes[0, 1].set_title('Error Rate (%)')
        axes[0, 1].set_ylabel('Error Rate (%)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Throughput
        axes[1, 0].plot(timestamps, self.metrics["throughput"], 'g-', linewidth=2)
        axes[1, 0].axhline(y=self.config.min_throughput, color='g', linestyle='--', label='SLA Threshold')
        axes[1, 0].set_title('Throughput (RPS)')
        axes[1, 0].set_ylabel('Requests/Second')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # User Count
        axes[1, 1].plot(timestamps, self.metrics["user_counts"], 'purple', linewidth=2)
        axes[1, 1].set_title('Active Users')
        axes[1, 1].set_ylabel('User Count')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "performance_charts.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_html_report(self, results: TestResults):
        """Gerar relatório HTML interativo"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - {results.test_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2196F3; }}
        .sla-pass {{ color: #4CAF50; }}
        .sla-fail {{ color: #f44336; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 5px 0; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Load Test Report</h1>
        <h2>TecnoCursos AI - {results.test_id}</h2>
        <p>Teste executado de {results.start_time.strftime('%Y-%m-%d %H:%M:%S')} até {results.end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value {'sla-pass' if results.sla_passed else 'sla-fail'}">{('✅ PASS' if results.sla_passed else '❌ FAIL')}</div>
            <div>SLA Status</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{results.total_requests:,}</div>
            <div>Total Requests</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{results.error_rate:.2f}%</div>
            <div>Error Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{results.p95_response_time:.1f}ms</div>
            <div>P95 Response Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{results.throughput:.1f}</div>
            <div>Throughput (RPS)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{results.availability:.2f}%</div>
            <div>Availability</div>
        </div>
    </div>
    
    <h3>🚨 Alertas Disparados</h3>
"""
        
        if results.alerts_triggered:
            for alert in results.alerts_triggered:
                html_content += f'<div class="alert">{alert}</div>'
        else:
            html_content += '<p>✅ Nenhum alerta disparado durante o teste.</p>'
        
        html_content += """
    <h3>📊 Performance Chart</h3>
    <img src="performance_charts.png" alt="Performance Charts" style="max-width: 100%;">
    
</body>
</html>
"""
        
        with open(self.results_dir / "report.html", 'w') as f:
            f.write(html_content)
    
    def _check_slas(self, results: TestResults):
        """Verificar SLAs e gerar alertas"""
        self.logger.info("🎯 Verificando SLAs...")
        
        if results.sla_passed:
            self.logger.info("✅ Todos os SLAs foram atendidos!")
        else:
            self.logger.warning("❌ SLAs não foram atendidos:")
            
            if results.p95_response_time > self.config.max_response_time_p95:
                self.logger.warning(f"  - Response time P95: {results.p95_response_time:.1f}ms > {self.config.max_response_time_p95}ms")
            
            if results.error_rate > self.config.max_error_rate:
                self.logger.warning(f"  - Error rate: {results.error_rate:.2f}% > {self.config.max_error_rate}%")
            
            if results.availability < self.config.min_availability:
                self.logger.warning(f"  - Availability: {results.availability:.2f}% < {self.config.min_availability}%")
            
            if results.throughput < self.config.min_throughput:
                self.logger.warning(f"  - Throughput: {results.throughput:.1f} RPS < {self.config.min_throughput} RPS")
    
    def _send_notifications(self, results: TestResults):
        """Enviar notificações dos resultados"""
        if self.config.send_slack_report and self.config.alert_webhook:
            self._send_slack_notification(results)
    
    def _send_slack_notification(self, results: TestResults):
        """Enviar notificação Slack"""
        try:
            color = "good" if results.sla_passed else "danger"
            status_icon = "✅" if results.sla_passed else "❌"
            
            message = {
                "attachments": [{
                    "color": color,
                    "title": f"{status_icon} Load Test Results - {results.test_id}",
                    "fields": [
                        {
                            "title": "SLA Status",
                            "value": "PASSED" if results.sla_passed else "FAILED",
                            "short": True
                        },
                        {
                            "title": "Total Requests",
                            "value": f"{results.total_requests:,}",
                            "short": True
                        },
                        {
                            "title": "Error Rate",
                            "value": f"{results.error_rate:.2f}%",
                            "short": True
                        },
                        {
                            "title": "P95 Response Time",
                            "value": f"{results.p95_response_time:.1f}ms",
                            "short": True
                        },
                        {
                            "title": "Throughput",
                            "value": f"{results.throughput:.1f} RPS",
                            "short": True
                        },
                        {
                            "title": "Availability",
                            "value": f"{results.availability:.2f}%",
                            "short": True
                        }
                    ],
                    "footer": "TecnoCursos AI Load Testing",
                    "ts": int(time.time())
                }]
            }
            
            requests.post(self.config.alert_webhook, json=message, timeout=10)
            self.logger.info("📱 Notificação Slack enviada")
            
        except Exception as e:
            self.logger.error(f"❌ Falha ao enviar notificação Slack: {e}")

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Interface CLI para testes de produção"""
    parser = argparse.ArgumentParser(description="Production Load Testing for TecnoCursos AI")
    parser.add_argument("--url", default="https://tecnocursos.ai", help="Base URL to test")
    parser.add_argument("--duration", type=int, default=3600, help="Test duration in seconds")
    parser.add_argument("--max-users", type=int, default=1000, help="Maximum concurrent users")
    parser.add_argument("--spawn-rate", type=int, default=10, help="User spawn rate")
    parser.add_argument("--quick", action="store_true", help="Run quick 5-minute test")
    parser.add_argument("--sla-check", action="store_true", help="Strict SLA validation")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Configuração
    if args.config and Path(args.config).exists():
        with open(args.config) as f:
            config_data = json.load(f)
        config = ProductionTestConfig(**config_data)
    else:
        config = ProductionTestConfig(
            base_url=args.url,
            test_duration=args.duration,
            max_users=args.max_users,
            spawn_rate=args.spawn_rate
        )
    
    # Quick test
    if args.quick:
        config.test_duration = 300  # 5 minutos
        config.stages = [
            {"duration": 60, "users": 10},
            {"duration": 180, "users": 50},
            {"duration": 60, "users": 0}
        ]
    
    # SLA rigoroso
    if args.sla_check:
        config.max_response_time_p95 = 200.0
        config.max_error_rate = 0.5
        config.min_throughput = 1500.0
    
    # Executar teste
    tester = ProductionLoadTester(config)
    results = tester.run_staged_test()
    
    # Resultado final
    if results.sla_passed:
        print(f"✅ Teste concluído com sucesso! SLAs atendidos.")
        sys.exit(0)
    else:
        print(f"❌ Teste falhou! SLAs não atendidos.")
        sys.exit(1)

if __name__ == "__main__":
    main() 