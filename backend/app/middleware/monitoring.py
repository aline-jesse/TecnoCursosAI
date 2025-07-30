"""
Middleware de Monitoramento e Analytics - TecnoCursos AI
Sistema de coleta de métricas e análise de performance
"""

import time
import asyncio
import psutil
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json

from ..core.logging import get_logger, log_request_start, log_request_end
from ..core.cache import cache_manager

logger = get_logger("monitoring")

class PerformanceMetrics:
    """Coletor de métricas de performance"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        
        # Métricas de request
        self.request_times: deque = deque(maxlen=max_samples)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.status_codes: Dict[int, int] = defaultdict(int)
        self.endpoint_metrics: Dict[str, Dict] = defaultdict(lambda: {
            "count": 0,
            "total_time": 0,
            "avg_time": 0,
            "min_time": float('inf'),
            "max_time": 0,
            "error_count": 0
        })
        
        # Métricas de sistema
        self.system_metrics: Dict[str, deque] = {
            "cpu_percent": deque(maxlen=100),
            "memory_percent": deque(maxlen=100),
            "disk_usage": deque(maxlen=100),
            "active_connections": deque(maxlen=100)
        }
        
        # Métricas de negócio
        self.business_metrics: Dict[str, int] = defaultdict(int)
        
        # Lock para thread safety
        self._lock = asyncio.Lock()
    
    async def record_request(
        self, 
        method: str, 
        path: str, 
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None
    ):
        """Registra métricas de request"""
        async with self._lock:
            # Métricas gerais
            self.request_times.append(duration_ms)
            self.request_counts[f"{method} {path}"] += 1
            self.status_codes[status_code] += 1
            
            # Métricas por endpoint
            endpoint_key = f"{method} {path}"
            metrics = self.endpoint_metrics[endpoint_key]
            
            metrics["count"] += 1
            metrics["total_time"] += duration_ms
            metrics["avg_time"] = metrics["total_time"] / metrics["count"]
            metrics["min_time"] = min(metrics["min_time"], duration_ms)
            metrics["max_time"] = max(metrics["max_time"], duration_ms)
            
            if status_code >= 400:
                metrics["error_count"] += 1
            
            # Log requests lentos
            if duration_ms > 1000:  # > 1 segundo
                logger.warning("Slow request detected", extra={
                    "method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "status_code": status_code,
                    "user_id": user_id
                })
    
    async def record_system_metrics(self):
        """Registra métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            async with self._lock:
                self.system_metrics["cpu_percent"].append(cpu_percent)
                self.system_metrics["memory_percent"].append(memory_percent)
                self.system_metrics["disk_usage"].append(disk_usage)
        
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def record_business_metric(self, metric_name: str, value: int = 1):
        """Registra métricas de negócio"""
        async with self._lock:
            self.business_metrics[metric_name] += value
    
    async def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        async with self._lock:
            # Estatísticas de request
            request_stats = {}
            if self.request_times:
                times = list(self.request_times)
                request_stats = {
                    "total_requests": len(times),
                    "avg_response_time": sum(times) / len(times),
                    "min_response_time": min(times),
                    "max_response_time": max(times),
                    "p95_response_time": sorted(times)[int(len(times) * 0.95)] if times else 0,
                    "p99_response_time": sorted(times)[int(len(times) * 0.99)] if times else 0
                }
            
            # Estatísticas do sistema
            system_stats = {}
            for metric, values in self.system_metrics.items():
                if values:
                    system_stats[metric] = {
                        "current": values[-1],
                        "avg": sum(values) / len(values),
                        "max": max(values),
                        "min": min(values)
                    }
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "request_metrics": request_stats,
                "system_metrics": system_stats,
                "status_codes": dict(self.status_codes),
                "top_endpoints": dict(list(
                    sorted(
                        self.endpoint_metrics.items(),
                        key=lambda x: x[1]["count"],
                        reverse=True
                    )[:10]
                )),
                "business_metrics": dict(self.business_metrics)
            }

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware para monitoramento de requests"""
    
    def __init__(self, app, metrics: PerformanceMetrics):
        super().__init__(app)
        self.metrics = metrics
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Pular monitoramento para endpoints de sistema
        skip_paths = ["/health", "/metrics", "/favicon.ico", "/docs", "/redoc", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Extrair informações do usuário
        user_id = None
        if hasattr(request.state, 'user') and request.state.user:
            user_id = str(request.state.user.id)
        
        # Iniciar rastreamento
        start_time = time.time()
        request_id = log_request_start(
            request.method, 
            request.url.path, 
            user_id
        )
        
        # Adicionar request_id ao estado
        request.state.request_id = request_id
        
        try:
            # Processar request
            response = await call_next(request)
            
            # Calcular duração
            duration_ms = (time.time() - start_time) * 1000
            
            # Registrar métricas
            await self.metrics.record_request(
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                user_id
            )
            
            # Log fim do request
            log_request_end(
                request_id,
                response.status_code,
                duration_ms,
                response.headers.get("content-length")
            )
            
            # Adicionar headers de monitoring
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            return response
        
        except Exception as e:
            # Erro no processamento
            duration_ms = (time.time() - start_time) * 1000
            
            # Registrar erro
            await self.metrics.record_request(
                request.method,
                request.url.path,
                500,
                duration_ms,
                user_id
            )
            
            log_request_end(request_id, 500, duration_ms)
            
            logger.error("Request processing error", extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "user_id": user_id
            })
            
            raise

class HealthMonitor:
    """Monitor de saúde do sistema"""
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
        self.checks: Dict[str, Callable] = {}
        self.last_check_time = None
        self.health_status = "healthy"
        self.alerts: List[Dict] = []
    
    def add_check(self, name: str, check_func: Callable):
        """Adiciona verificação de saúde"""
        self.checks[name] = check_func
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Executa todas as verificações de saúde"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "message": "OK" if result else "Check failed"
                }
                
                if not result:
                    overall_healthy = False
            
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "message": str(e)
                }
                overall_healthy = False
        
        # Verificações automáticas do sistema
        await self._check_system_resources(results)
        
        self.health_status = "healthy" if overall_healthy else "unhealthy"
        self.last_check_time = datetime.utcnow()
        
        return {
            "status": self.health_status,
            "timestamp": self.last_check_time.isoformat(),
            "checks": results,
            "system": await self._get_system_info()
        }
    
    async def _check_system_resources(self, results: Dict):
        """Verifica recursos do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            results["cpu"] = {
                "status": "healthy" if cpu_percent < 80 else "warning",
                "usage_percent": cpu_percent,
                "message": f"CPU usage: {cpu_percent}%"
            }
            
            # Memória
            memory = psutil.virtual_memory()
            results["memory"] = {
                "status": "healthy" if memory.percent < 85 else "warning",
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "message": f"Memory usage: {memory.percent}%"
            }
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            results["disk"] = {
                "status": "healthy" if disk_percent < 90 else "warning",
                "usage_percent": round(disk_percent, 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "message": f"Disk usage: {disk_percent:.1f}%"
            }
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                "python_version": psutil.PYTHON,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 2)
            }
        except Exception:
            return {}

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        self.alerts: List[Dict] = []
        self.alert_thresholds = {
            "response_time_p95": 2000,  # 2 segundos
            "error_rate": 0.05,         # 5%
            "cpu_usage": 80,            # 80%
            "memory_usage": 85,         # 85%
            "disk_usage": 90            # 90%
        }
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """Verifica condições de alerta"""
        current_time = datetime.utcnow()
        
        # Verificar tempo de resposta
        if metrics.get("request_metrics", {}).get("p95_response_time", 0) > self.alert_thresholds["response_time_p95"]:
            await self._create_alert(
                "high_response_time",
                f"P95 response time is {metrics['request_metrics']['p95_response_time']:.2f}ms",
                "warning"
            )
        
        # Verificar taxa de erro
        total_requests = sum(metrics.get("status_codes", {}).values())
        error_requests = sum(
            count for status, count in metrics.get("status_codes", {}).items()
            if status >= 400
        )
        
        if total_requests > 0:
            error_rate = error_requests / total_requests
            if error_rate > self.alert_thresholds["error_rate"]:
                await self._create_alert(
                    "high_error_rate",
                    f"Error rate is {error_rate:.2%}",
                    "critical"
                )
        
        # Verificar recursos do sistema
        system_metrics = metrics.get("system_metrics", {})
        
        for resource in ["cpu_percent", "memory_percent", "disk_usage"]:
            if resource in system_metrics:
                current_value = system_metrics[resource].get("current", 0)
                threshold_key = resource.replace("_percent", "_usage")
                
                if current_value > self.alert_thresholds.get(threshold_key, 100):
                    await self._create_alert(
                        f"high_{resource}",
                        f"{resource.replace('_', ' ').title()} is {current_value}%",
                        "warning"
                    )
    
    async def _create_alert(self, alert_type: str, message: str, severity: str):
        """Cria novo alerta"""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        
        # Manter apenas últimos 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.warning(f"Alert created: {alert_type}", extra=alert)
    
    def get_active_alerts(self) -> List[Dict]:
        """Retorna alertas ativos (não confirmados)"""
        return [alert for alert in self.alerts if not alert["acknowledged"]]

# Instâncias globais
performance_metrics = PerformanceMetrics()
health_monitor = HealthMonitor(performance_metrics)
alert_manager = AlertManager()

# Task para coleta de métricas do sistema
async def system_metrics_collector():
    """Task em background para coletar métricas do sistema"""
    while True:
        try:
            await performance_metrics.record_system_metrics()
            
            # Verificar alertas a cada 5 minutos
            metrics_summary = await performance_metrics.get_summary()
            await alert_manager.check_alerts(metrics_summary)
            
        except Exception as e:
            logger.error(f"Error in system metrics collector: {e}")
        
        await asyncio.sleep(60)  # Coletar a cada minuto

# Funções de conveniência
def get_monitoring_middleware(app):
    """Cria middleware de monitoramento"""
    return MonitoringMiddleware(app, performance_metrics)

async def get_metrics_summary():
    """Retorna resumo das métricas"""
    return await performance_metrics.get_summary()

async def get_health_status():
    """Retorna status de saúde"""
    return await health_monitor.run_health_checks()

def get_active_alerts():
    """Retorna alertas ativos"""
    return alert_manager.get_active_alerts()

async def record_business_event(event_name: str, value: int = 1):
    """Registra evento de negócio"""
    await performance_metrics.record_business_metric(event_name, value)
