#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Métricas Prometheus - TecnoCursos AI

Este módulo implementa coleta e exposição de métricas seguindo
as melhores práticas de observabilidade para aplicações FastAPI.

Baseado em:
- Prometheus metrics best practices
- FastAPI monitoring patterns
- SRE (Site Reliability Engineering) guidelines
- OpenTelemetry standards

Funcionalidades:
- Métricas HTTP (latência, status codes, throughput)
- Métricas de aplicação (usuários, projetos, vídeos)
- Métricas de sistema (CPU, memória, disco)
- Métricas de banco de dados
- Métricas de cache Redis
- Custom metrics para business logic
- Health checks avançados

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import wraps
import psutil
import os

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Info, Enum,
        CollectorRegistry, generate_latest,
        multiprocess, values
    )
    from prometheus_client.metrics import MetricWrapperBase
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Fallback classes
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def time(self): return self
        def labels(self, *args, **kwargs): return self
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def dec(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self

try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from app.database import get_db
    from app.logger import get_logger
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    get_logger = lambda x: logging.getLogger(x)

logger = get_logger("prometheus_metrics")

# ============================================================================
# CONFIGURAÇÃO DE MÉTRICAS
# ============================================================================

@dataclass
class MetricsConfig:
    """Configuração das métricas"""
    app_name: str = "tecnocursos_ai"
    namespace: str = "tecnocursos"
    enabled: bool = True
    collect_interval: int = 15  # segundos
    retention_days: int = 30
    custom_labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.custom_labels is None:
            self.custom_labels = {}

# Configuração global
metrics_config = MetricsConfig()

# Registry para métricas multiprocesso
if PROMETHEUS_AVAILABLE:
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

# ============================================================================
# MÉTRICAS HTTP
# ============================================================================

# Contador de requests HTTP
http_requests_total = Counter(
    name='http_requests_total',
    documentation='Total HTTP requests',
    labelnames=['method', 'endpoint', 'status_code', 'user_type'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Histograma de latência HTTP
http_request_duration_seconds = Histogram(
    name='http_request_duration_seconds',
    documentation='HTTP request duration in seconds',
    labelnames=['method', 'endpoint', 'status_code'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Tamanho das respostas HTTP
http_response_size_bytes = Histogram(
    name='http_response_size_bytes',
    documentation='HTTP response size in bytes',
    labelnames=['method', 'endpoint', 'status_code'],
    buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Requests ativas
http_requests_active = Gauge(
    name='http_requests_active',
    documentation='Number of active HTTP requests',
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# ============================================================================
# MÉTRICAS DE APLICAÇÃO
# ============================================================================

# Usuários
users_total = Gauge(
    name='users_total',
    documentation='Total number of users',
    labelnames=['status'],  # active, inactive, pending
    registry=registry if PROMETHEUS_AVAILABLE else None
)

users_online = Gauge(
    name='users_online',
    documentation='Number of users currently online',
    registry=registry if PROMETHEUS_AVAILABLE else None
)

user_sessions = Gauge(
    name='user_sessions_active',
    documentation='Number of active user sessions',
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Projetos
projects_total = Gauge(
    name='projects_total',
    documentation='Total number of projects',
    labelnames=['status', 'type'],  # draft, published, archived + course, presentation
    registry=registry if PROMETHEUS_AVAILABLE else None
)

projects_created = Counter(
    name='projects_created_total',
    documentation='Total projects created',
    labelnames=['type', 'user_type'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Cenas
scenes_total = Gauge(
    name='scenes_total',
    documentation='Total number of scenes',
    labelnames=['status'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

scenes_processed = Counter(
    name='scenes_processed_total',
    documentation='Total scenes processed',
    labelnames=['operation', 'status'],  # create, update, delete + success, error
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Vídeos
videos_generated = Counter(
    name='videos_generated_total',
    documentation='Total videos generated',
    labelnames=['quality', 'status', 'duration_range'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

video_generation_duration = Histogram(
    name='video_generation_duration_seconds',
    documentation='Video generation duration in seconds',
    labelnames=['quality', 'scene_count_range'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1200, 3600],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

video_files_size = Histogram(
    name='video_files_size_bytes',
    documentation='Generated video file sizes',
    labelnames=['quality', 'duration_range'],
    buckets=[1024*1024, 5*1024*1024, 10*1024*1024, 50*1024*1024, 100*1024*1024, 500*1024*1024],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# ============================================================================
# MÉTRICAS DE SISTEMA
# ============================================================================

# CPU
cpu_usage_percent = Gauge(
    name='cpu_usage_percent',
    documentation='CPU usage percentage',
    registry=registry if PROMETHEUS_AVAILABLE else None
)

cpu_load_average = Gauge(
    name='cpu_load_average',
    documentation='CPU load average',
    labelnames=['period'],  # 1m, 5m, 15m
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Memória
memory_usage_bytes = Gauge(
    name='memory_usage_bytes',
    documentation='Memory usage in bytes',
    labelnames=['type'],  # total, available, used, free
    registry=registry if PROMETHEUS_AVAILABLE else None
)

memory_usage_percent = Gauge(
    name='memory_usage_percent',
    documentation='Memory usage percentage',
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# Disco
disk_usage_bytes = Gauge(
    name='disk_usage_bytes',
    documentation='Disk usage in bytes',
    labelnames=['mountpoint', 'type'],  # total, used, free
    registry=registry if PROMETHEUS_AVAILABLE else None
)

disk_usage_percent = Gauge(
    name='disk_usage_percent',
    documentation='Disk usage percentage',
    labelnames=['mountpoint'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# ============================================================================
# MÉTRICAS DE BANCO DE DADOS
# ============================================================================

database_connections = Gauge(
    name='database_connections_active',
    documentation='Number of active database connections',
    registry=registry if PROMETHEUS_AVAILABLE else None
)

database_query_duration = Histogram(
    name='database_query_duration_seconds',
    documentation='Database query duration in seconds',
    labelnames=['operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

database_queries_total = Counter(
    name='database_queries_total',
    documentation='Total database queries',
    labelnames=['operation', 'table', 'status'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

database_size_bytes = Gauge(
    name='database_size_bytes',
    documentation='Database size in bytes',
    labelnames=['database', 'table'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# ============================================================================
# MÉTRICAS DE CACHE (REDIS)
# ============================================================================

cache_operations_total = Counter(
    name='cache_operations_total',
    documentation='Total cache operations',
    labelnames=['operation', 'status'],  # get, set, delete + hit, miss, error
    registry=registry if PROMETHEUS_AVAILABLE else None
)

cache_hit_ratio = Gauge(
    name='cache_hit_ratio',
    documentation='Cache hit ratio',
    labelnames=['cache_type'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

cache_memory_usage_bytes = Gauge(
    name='cache_memory_usage_bytes',
    documentation='Cache memory usage in bytes',
    registry=registry if PROMETHEUS_AVAILABLE else None
)

cache_keys_total = Gauge(
    name='cache_keys_total',
    documentation='Total number of cache keys',
    labelnames=['pattern'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# ============================================================================
# MÉTRICAS DE IA E SERVIÇOS EXTERNOS
# ============================================================================

ai_requests_total = Counter(
    name='ai_requests_total',
    documentation='Total AI service requests',
    labelnames=['service', 'operation', 'status'],  # openai, azure, d_id + tts, avatar, image + success, error
    registry=registry if PROMETHEUS_AVAILABLE else None
)

ai_request_duration = Histogram(
    name='ai_request_duration_seconds',
    documentation='AI service request duration',
    labelnames=['service', 'operation'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

ai_tokens_consumed = Counter(
    name='ai_tokens_consumed_total',
    documentation='Total AI tokens consumed',
    labelnames=['service', 'operation', 'model'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

ai_cost_estimated = Counter(
    name='ai_cost_estimated_total',
    documentation='Estimated AI service costs',
    labelnames=['service', 'operation'],
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# ============================================================================
# MÉTRICAS DE NEGÓCIO
# ============================================================================

business_conversions = Counter(
    name='business_conversions_total',
    documentation='Business conversions',
    labelnames=['type', 'source'],  # signup, subscription, purchase + web, api, mobile
    registry=registry if PROMETHEUS_AVAILABLE else None
)

business_revenue = Counter(
    name='business_revenue_total',
    documentation='Total revenue',
    labelnames=['type', 'currency'],  # subscription, one_time + BRL, USD
    registry=registry if PROMETHEUS_AVAILABLE else None
)

business_errors = Counter(
    name='business_errors_total',
    documentation='Business logic errors',
    labelnames=['type', 'severity'],  # payment, upload, generation + low, medium, high, critical
    registry=registry if PROMETHEUS_AVAILABLE else None
)

# ============================================================================
# MIDDLEWARE DE MÉTRICAS
# ============================================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware para coleta automática de métricas HTTP
    """
    
    def __init__(self, app, config: MetricsConfig = None):
        super().__init__(app)
        self.config = config or metrics_config
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.config.enabled:
            return await call_next(request)
        
        # Incrementar requests ativos
        http_requests_active.inc()
        
        # Dados do request
        method = request.method
        path = request.url.path
        start_time = time.time()
        
        # Determinar endpoint (remover IDs para agrupamento)
        endpoint = self._get_endpoint_label(path)
        
        # Determinar tipo de usuário
        user_type = self._get_user_type(request)
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            status_code = 500
            raise
        
        finally:
            # Decrementar requests ativos
            http_requests_active.dec()
            
            # Calcular duração
            duration = time.time() - start_time
            
            # Calcular tamanho da resposta
            response_size = len(response.body) if hasattr(response, 'body') else 0
            
            # Registrar métricas
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                user_type=user_type
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(duration)
            
            http_response_size_bytes.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(response_size)
        
        return response
    
    def _get_endpoint_label(self, path: str) -> str:
        """Normalizar path para agrupamento de métricas"""
        # Remover IDs numéricos e UUIDs
        import re
        
        # Padrões para normalização
        patterns = [
            (r'/\d+', '/{id}'),                    # IDs numéricos
            (r'/[0-9a-f-]{36}', '/{uuid}'),        # UUIDs
            (r'/[0-9a-f]{8,}', '/{hash}'),         # Hashes
        ]
        
        normalized = path
        for pattern, replacement in patterns:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized
    
    def _get_user_type(self, request: Request) -> str:
        """Determinar tipo de usuário"""
        # TODO: Implementar lógica baseada em JWT ou sessão
        auth_header = request.headers.get("authorization", "")
        
        if not auth_header:
            return "anonymous"
        
        # Placeholder - implementar extração de role do JWT
        return "authenticated"

# ============================================================================
# COLETORES DE MÉTRICAS
# ============================================================================

class SystemMetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.enabled = True
        
    async def collect_metrics(self):
        """Coletar métricas do sistema"""
        if not self.enabled:
            return
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_usage_percent.set(cpu_percent)
            
            # Load average (apenas Unix)
            if hasattr(os, 'getloadavg'):
                load_1, load_5, load_15 = os.getloadavg()
                cpu_load_average.labels(period='1m').set(load_1)
                cpu_load_average.labels(period='5m').set(load_5)
                cpu_load_average.labels(period='15m').set(load_15)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_usage_bytes.labels(type='total').set(memory.total)
            memory_usage_bytes.labels(type='available').set(memory.available)
            memory_usage_bytes.labels(type='used').set(memory.used)
            memory_usage_bytes.labels(type='free').set(memory.free)
            memory_usage_percent.set(memory.percent)
            
            # Disco
            disk_usage = psutil.disk_usage('/')
            disk_usage_bytes.labels(mountpoint='/', type='total').set(disk_usage.total)
            disk_usage_bytes.labels(mountpoint='/', type='used').set(disk_usage.used)
            disk_usage_bytes.labels(mountpoint='/', type='free').set(disk_usage.free)
            
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            disk_usage_percent.labels(mountpoint='/').set(disk_percent)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")

class ApplicationMetricsCollector:
    """Coletor de métricas da aplicação"""
    
    def __init__(self):
        self.enabled = DATABASE_AVAILABLE
        
    async def collect_metrics(self):
        """Coletar métricas da aplicação"""
        if not self.enabled:
            return
        
        try:
            # TODO: Implementar consultas ao banco para métricas de negócio
            # Por enquanto, valores simulados
            
            # Usuários (simulado)
            users_total.labels(status='active').set(1250)
            users_total.labels(status='inactive').set(350)
            users_total.labels(status='pending').set(45)
            users_online.set(127)
            user_sessions.set(89)
            
            # Projetos (simulado)
            projects_total.labels(status='draft', type='course').set(245)
            projects_total.labels(status='published', type='course').set(456)
            projects_total.labels(status='archived', type='course').set(123)
            
            # Cenas (simulado)
            scenes_total.labels(status='active').set(3456)
            scenes_total.labels(status='inactive').set(789)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas da aplicação: {e}")

# ============================================================================
# FUNCÕES UTILITÁRIAS PARA MÉTRICAS
# ============================================================================

def track_ai_request(service: str, operation: str, duration: float, 
                    status: str = "success", tokens: int = 0, cost: float = 0.0):
    """Registrar métrica de request de IA"""
    ai_requests_total.labels(service=service, operation=operation, status=status).inc()
    ai_request_duration.labels(service=service, operation=operation).observe(duration)
    
    if tokens > 0:
        ai_tokens_consumed.labels(service=service, operation=operation, model="default").inc(tokens)
    
    if cost > 0:
        ai_cost_estimated.labels(service=service, operation=operation).inc(cost)

def track_video_generation(quality: str, duration: float, scene_count: int, 
                          file_size: int, status: str = "success"):
    """Registrar métrica de geração de vídeo"""
    # Determinar ranges
    duration_range = get_duration_range(duration)
    scene_count_range = get_scene_count_range(scene_count)
    
    videos_generated.labels(
        quality=quality,
        status=status,
        duration_range=duration_range
    ).inc()
    
    video_generation_duration.labels(
        quality=quality,
        scene_count_range=scene_count_range
    ).observe(duration)
    
    video_files_size.labels(
        quality=quality,
        duration_range=duration_range
    ).observe(file_size)

def track_database_query(operation: str, table: str, duration: float, status: str = "success"):
    """Registrar métrica de query do banco"""
    database_queries_total.labels(operation=operation, table=table, status=status).inc()
    database_query_duration.labels(operation=operation, table=table).observe(duration)

def track_cache_operation(operation: str, status: str, cache_type: str = "default"):
    """Registrar métrica de operação de cache"""
    cache_operations_total.labels(operation=operation, status=status).inc()

def track_business_event(event_type: str, value: float = 1.0, **labels):
    """Registrar evento de negócio"""
    if event_type == "conversion":
        business_conversions.labels(**labels).inc(value)
    elif event_type == "revenue":
        business_revenue.labels(**labels).inc(value)
    elif event_type == "error":
        business_errors.labels(**labels).inc(value)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_duration_range(seconds: float) -> str:
    """Obter range de duração"""
    if seconds < 10:
        return "0-10s"
    elif seconds < 30:
        return "10-30s"
    elif seconds < 60:
        return "30-60s"
    elif seconds < 300:
        return "1-5m"
    elif seconds < 600:
        return "5-10m"
    else:
        return "10m+"

def get_scene_count_range(count: int) -> str:
    """Obter range de número de cenas"""
    if count <= 5:
        return "1-5"
    elif count <= 10:
        return "6-10"
    elif count <= 20:
        return "11-20"
    elif count <= 50:
        return "21-50"
    else:
        return "50+"

# ============================================================================
# DECORATORS PARA MÉTRICAS
# ============================================================================

def track_execution_time(metric: Histogram, labels: Dict[str, str] = None):
    """Decorator para rastrear tempo de execução"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with metric.labels(**(labels or {})).time():
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with metric.labels(**(labels or {})).time():
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def count_calls(metric: Counter, labels: Dict[str, str] = None):
    """Decorator para contar chamadas"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                metric.labels(status="success", **(labels or {})).inc()
                return result
            except Exception as e:
                metric.labels(status="error", **(labels or {})).inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                metric.labels(status="success", **(labels or {})).inc()
                return result
            except Exception as e:
                metric.labels(status="error", **(labels or {})).inc()
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# ============================================================================
# INICIALIZAÇÃO E EXPOSIÇÃO DE MÉTRICAS
# ============================================================================

async def start_metrics_collection():
    """Iniciar coleta periódica de métricas"""
    if not metrics_config.enabled:
        return
    
    system_collector = SystemMetricsCollector()
    app_collector = ApplicationMetricsCollector()
    
    async def collect_loop():
        while True:
            try:
                await system_collector.collect_metrics()
                await app_collector.collect_metrics()
                await asyncio.sleep(metrics_config.collect_interval)
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {e}")
                await asyncio.sleep(5)  # Retry em 5 segundos
    
    # Iniciar em background
    asyncio.create_task(collect_loop())
    logger.info("✅ Coleta de métricas iniciada")

def get_metrics() -> str:
    """Obter métricas formatadas para Prometheus"""
    if not PROMETHEUS_AVAILABLE:
        return "# Prometheus não disponível\n"
    
    return generate_latest(registry).decode('utf-8')

def get_metrics_summary() -> Dict[str, Any]:
    """Obter resumo das métricas principais"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics_enabled": metrics_config.enabled,
        "prometheus_available": PROMETHEUS_AVAILABLE,
        "collection_interval": metrics_config.collect_interval,
        "total_metrics": len([m for m in registry._collector_to_names.keys()]) if PROMETHEUS_AVAILABLE else 0
    } 