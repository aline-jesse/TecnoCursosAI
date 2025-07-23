"""
Serviço Avançado de Monitoramento de API - TecnoCursos AI
========================================================

Sistema completo de monitoramento e observabilidade:
- Coleta de métricas em tempo real
- Monitoramento de SLA e disponibilidade
- Alertas automáticos para problemas
- Análise de performance e bottlenecks
- Dashboards e relatórios
- Rastreamento de uso por usuário/endpoint
- Detecção de anomalias
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import logging

from app.logger import get_logger

logger = get_logger("api_monitoring")

class AlertLevel(Enum):
    """Níveis de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class MetricPoint:
    """Ponto de métrica"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = None

@dataclass
class APICall:
    """Chamada de API registrada"""
    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    error: Optional[str] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None

@dataclass
class Alert:
    """Alerta do sistema"""
    id: str
    level: AlertLevel
    title: str
    description: str
    timestamp: datetime
    metric: str
    value: float
    threshold: float
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None

class MetricsCollector:
    """Coletor de métricas"""
    
    def __init__(self, max_points: int = 10000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.api_calls: deque = deque(maxlen=max_points)
        self.alerts: List[Alert] = []
        self.max_points = max_points
        
        # Contadores
        self.request_count = defaultdict(int)
        self.error_count = defaultdict(int)
        self.status_code_count = defaultdict(int)
        
        # Configurações de alerta
        self.alert_thresholds = {
            "response_time_p95": 2000.0,  # 95th percentile > 2s
            "error_rate": 5.0,            # Error rate > 5%
            "requests_per_minute": 1000,   # > 1000 req/min
            "cpu_usage": 80.0,            # CPU > 80%
            "memory_usage": 85.0,         # Memory > 85%
        }
        
        logger.info("✅ Metrics Collector inicializado")

    def record_api_call(self, api_call: APICall):
        """Registrar chamada de API"""
        self.api_calls.append(api_call)
        
        # Atualizar contadores
        self.request_count[api_call.endpoint] += 1
        self.status_code_count[api_call.status_code] += 1
        
        if api_call.status_code >= 400:
            self.error_count[api_call.endpoint] += 1
        
        # Registrar métricas derivadas
        self.record_metric("response_time", api_call.response_time_ms, {
            "endpoint": api_call.endpoint,
            "method": api_call.method,
            "status": str(api_call.status_code)
        })
        
        self.record_metric("request_count", 1, {
            "endpoint": api_call.endpoint,
            "method": api_call.method
        })

    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Registrar métrica"""
        metric_point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {}
        )
        
        self.metrics[name].append(metric_point)

    def get_metric_summary(self, metric_name: str, time_window: timedelta = None) -> Dict[str, float]:
        """Obter resumo de métrica"""
        if metric_name not in self.metrics:
            return {}
        
        points = self.metrics[metric_name]
        
        # Filtrar por janela de tempo se especificada
        if time_window:
            cutoff_time = datetime.utcnow() - time_window
            points = [p for p in points if p.timestamp >= cutoff_time]
        
        if not points:
            return {}
        
        values = [p.value for p in points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
            "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
        }

class PerformanceAnalyzer:
    """Analisador de performance"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        
    def analyze_response_times(self, time_window: timedelta = timedelta(minutes=15)) -> Dict[str, Any]:
        """Analisar tempos de resposta"""
        summary = self.collector.get_metric_summary("response_time", time_window)
        
        if not summary:
            return {"status": "no_data"}
        
        # Classificar performance
        p95 = summary.get("p95", 0)
        if p95 < 500:
            performance_grade = "excellent"
        elif p95 < 1000:
            performance_grade = "good"
        elif p95 < 2000:
            performance_grade = "acceptable"
        else:
            performance_grade = "poor"
        
        return {
            "performance_grade": performance_grade,
            "summary": summary,
            "recommendations": self._get_performance_recommendations(summary)
        }
    
    def analyze_error_rates(self, time_window: timedelta = timedelta(minutes=15)) -> Dict[str, Any]:
        """Analisar taxas de erro"""
        cutoff_time = datetime.utcnow() - time_window
        
        recent_calls = [call for call in self.collector.api_calls if call.timestamp >= cutoff_time]
        
        if not recent_calls:
            return {"status": "no_data"}
        
        total_calls = len(recent_calls)
        error_calls = sum(1 for call in recent_calls if call.status_code >= 400)
        error_rate = (error_calls / total_calls) * 100
        
        # Analisar por endpoint
        endpoint_stats = defaultdict(lambda: {"total": 0, "errors": 0})
        
        for call in recent_calls:
            endpoint_stats[call.endpoint]["total"] += 1
            if call.status_code >= 400:
                endpoint_stats[call.endpoint]["errors"] += 1
        
        endpoint_error_rates = {}
        for endpoint, stats in endpoint_stats.items():
            endpoint_error_rates[endpoint] = (stats["errors"] / stats["total"]) * 100
        
        return {
            "overall_error_rate": error_rate,
            "total_requests": total_calls,
            "error_requests": error_calls,
            "endpoint_error_rates": dict(endpoint_error_rates),
            "status": "healthy" if error_rate < 1 else "degraded" if error_rate < 5 else "unhealthy"
        }
    
    def detect_anomalies(self, metric_name: str) -> List[Dict[str, Any]]:
        """Detectar anomalias em métricas"""
        if metric_name not in self.collector.metrics:
            return []
        
        points = list(self.collector.metrics[metric_name])
        if len(points) < 30:  # Necessário histórico mínimo
            return []
        
        # Usar últimos 30 pontos como baseline
        baseline_values = [p.value for p in points[-30:]]
        mean_baseline = statistics.mean(baseline_values)
        std_baseline = statistics.stdev(baseline_values)
        
        # Detectar pontos fora de 2 desvios padrão
        anomalies = []
        threshold = 2 * std_baseline
        
        for point in points[-10:]:  # Verificar últimos 10 pontos
            if abs(point.value - mean_baseline) > threshold:
                anomalies.append({
                    "timestamp": point.timestamp.isoformat(),
                    "value": point.value,
                    "expected_range": [mean_baseline - threshold, mean_baseline + threshold],
                    "deviation": abs(point.value - mean_baseline),
                    "severity": "high" if abs(point.value - mean_baseline) > 3 * std_baseline else "medium"
                })
        
        return anomalies
    
    def _get_performance_recommendations(self, summary: Dict[str, float]) -> List[str]:
        """Obter recomendações de performance"""
        recommendations = []
        
        p95 = summary.get("p95", 0)
        mean = summary.get("mean", 0)
        
        if p95 > 2000:
            recommendations.append("Otimizar endpoints com maior latência")
            recommendations.append("Implementar cache para reduzir tempo de resposta")
            
        if mean > 1000:
            recommendations.append("Revisar queries de banco de dados")
            recommendations.append("Considerar otimização de código")
            
        if summary.get("max", 0) > 10000:
            recommendations.append("Investigar timeout em endpoints")
            recommendations.append("Implementar rate limiting mais rigoroso")
        
        return recommendations

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.active_alerts = []
        self.alert_history = []
        self.alert_callbacks = []
        
    def check_thresholds(self):
        """Verificar thresholds e gerar alertas"""
        # Verificar response time P95
        rt_summary = self.collector.get_metric_summary("response_time", timedelta(minutes=5))
        if rt_summary and rt_summary.get("p95", 0) > self.collector.alert_thresholds["response_time_p95"]:
            self._create_alert(
                "high_response_time",
                AlertLevel.WARNING,
                "Alto tempo de resposta",
                f"P95 de tempo de resposta: {rt_summary['p95']:.1f}ms",
                "response_time_p95",
                rt_summary["p95"],
                self.collector.alert_thresholds["response_time_p95"]
            )
        
        # Verificar error rate
        analyzer = PerformanceAnalyzer(self.collector)
        error_analysis = analyzer.analyze_error_rates(timedelta(minutes=5))
        
        if error_analysis.get("overall_error_rate", 0) > self.collector.alert_thresholds["error_rate"]:
            self._create_alert(
                "high_error_rate",
                AlertLevel.CRITICAL,
                "Alta taxa de erro",
                f"Taxa de erro: {error_analysis['overall_error_rate']:.1f}%",
                "error_rate",
                error_analysis["overall_error_rate"],
                self.collector.alert_thresholds["error_rate"]
            )
    
    def _create_alert(
        self, 
        alert_id: str, 
        level: AlertLevel, 
        title: str, 
        description: str,
        metric: str,
        value: float,
        threshold: float
    ):
        """Criar alerta"""
        # Verificar se alerta já existe
        existing = next((a for a in self.active_alerts if a.id == alert_id and not a.is_resolved), None)
        
        if existing:
            return  # Não duplicar alertas
        
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            description=description,
            timestamp=datetime.utcnow(),
            metric=metric,
            value=value,
            threshold=threshold
        )
        
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        
        # Executar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"❌ Erro em callback de alerta: {e}")
        
        logger.warning(f"🚨 ALERTA CRIADO: {title} - {description}")
    
    def resolve_alert(self, alert_id: str):
        """Resolver alerta"""
        alert = next((a for a in self.active_alerts if a.id == alert_id and not a.is_resolved), None)
        
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            logger.info(f"✅ Alerta resolvido: {alert.title}")

class SLAMonitor:
    """Monitor de SLA"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.sla_targets = {
            "availability": 99.9,      # 99.9% uptime
            "response_time_p95": 1000, # P95 < 1s
            "error_rate": 0.1          # < 0.1% error rate
        }
    
    def calculate_sla_metrics(self, time_window: timedelta = timedelta(days=1)) -> Dict[str, Any]:
        """Calcular métricas de SLA"""
        cutoff_time = datetime.utcnow() - time_window
        recent_calls = [call for call in self.collector.api_calls if call.timestamp >= cutoff_time]
        
        if not recent_calls:
            return {"status": "no_data"}
        
        # Calcular disponibilidade
        total_requests = len(recent_calls)
        successful_requests = sum(1 for call in recent_calls if call.status_code < 500)
        availability = (successful_requests / total_requests) * 100
        
        # Calcular response time P95
        response_times = [call.response_time_ms for call in recent_calls]
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
        
        # Calcular error rate
        error_requests = sum(1 for call in recent_calls if call.status_code >= 400)
        error_rate = (error_requests / total_requests) * 100
        
        # Verificar compliance com SLA
        sla_compliance = {
            "availability": availability >= self.sla_targets["availability"],
            "response_time": p95_response_time <= self.sla_targets["response_time_p95"],
            "error_rate": error_rate <= self.sla_targets["error_rate"]
        }
        
        overall_compliance = all(sla_compliance.values())
        
        return {
            "time_window_hours": time_window.total_seconds() / 3600,
            "availability": {
                "value": availability,
                "target": self.sla_targets["availability"],
                "compliant": sla_compliance["availability"]
            },
            "response_time_p95": {
                "value": p95_response_time,
                "target": self.sla_targets["response_time_p95"],
                "compliant": sla_compliance["response_time"]
            },
            "error_rate": {
                "value": error_rate,
                "target": self.sla_targets["error_rate"],
                "compliant": sla_compliance["error_rate"]
            },
            "overall_compliance": overall_compliance,
            "total_requests": total_requests
        }

class AdvancedAPIMonitoringService:
    """
    Serviço principal de monitoramento de API
    """
    
    def __init__(self):
        self.collector = MetricsCollector()
        self.analyzer = PerformanceAnalyzer(self.collector)
        self.alert_manager = AlertManager(self.collector)
        self.sla_monitor = SLAMonitor(self.collector)
        
        # Configurar verificação periódica de alertas
        self.monitoring_task = None
        
        logger.info("✅ Advanced API Monitoring Service inicializado")
    
    async def start_monitoring(self, check_interval: int = 60):
        """Iniciar monitoramento contínuo"""
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(check_interval)
        )
        logger.info(f"🚀 Monitoramento iniciado com intervalo de {check_interval}s")
    
    async def stop_monitoring(self):
        """Parar monitoramento"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            logger.info("⏹️ Monitoramento parado")
    
    async def _monitoring_loop(self, interval: int):
        """Loop principal de monitoramento"""
        while True:
            try:
                # Verificar thresholds de alerta
                self.alert_manager.check_thresholds()
                
                # Detectar anomalias
                anomalies = self.analyzer.detect_anomalies("response_time")
                if anomalies:
                    logger.warning(f"🔍 {len(anomalies)} anomalias detectadas em response_time")
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                await asyncio.sleep(interval)
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        error: Optional[str] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None
    ):
        """Registrar requisição"""
        api_call = APICall(
            timestamp=datetime.utcnow(),
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_id=user_id,
            ip_address=ip_address,
            error=error,
            request_size=request_size,
            response_size=response_size
        )
        
        self.collector.record_api_call(api_call)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard"""
        # Métricas dos últimos 15 minutos
        time_window = timedelta(minutes=15)
        
        response_time_analysis = self.analyzer.analyze_response_times(time_window)
        error_analysis = self.analyzer.analyze_error_rates(time_window)
        sla_metrics = self.sla_monitor.calculate_sla_metrics(timedelta(hours=24))
        
        # Top endpoints por volume
        cutoff_time = datetime.utcnow() - time_window
        recent_calls = [call for call in self.collector.api_calls if call.timestamp >= cutoff_time]
        
        endpoint_counts = defaultdict(int)
        for call in recent_calls:
            endpoint_counts[call.endpoint] += 1
        
        top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "time_window_minutes": 15,
            "response_time_analysis": response_time_analysis,
            "error_analysis": error_analysis,
            "sla_metrics": sla_metrics,
            "top_endpoints": top_endpoints,
            "active_alerts": len([a for a in self.alert_manager.active_alerts if not a.is_resolved]),
            "total_requests_15min": len(recent_calls),
            "requests_per_minute": len(recent_calls) / 15
        }
    
    def get_detailed_report(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Gerar relatório detalhado"""
        cutoff_time = datetime.utcnow() - time_window
        calls_in_window = [call for call in self.collector.api_calls if call.timestamp >= cutoff_time]
        
        # Análise por endpoint
        endpoint_analysis = defaultdict(lambda: {
            "count": 0, "errors": 0, "response_times": [],
            "status_codes": defaultdict(int)
        })
        
        for call in calls_in_window:
            analysis = endpoint_analysis[call.endpoint]
            analysis["count"] += 1
            analysis["response_times"].append(call.response_time_ms)
            analysis["status_codes"][call.status_code] += 1
            
            if call.status_code >= 400:
                analysis["errors"] += 1
        
        # Calcular estatísticas por endpoint
        endpoint_stats = {}
        for endpoint, analysis in endpoint_analysis.items():
            if analysis["response_times"]:
                endpoint_stats[endpoint] = {
                    "requests": analysis["count"],
                    "error_rate": (analysis["errors"] / analysis["count"]) * 100,
                    "avg_response_time": statistics.mean(analysis["response_times"]),
                    "p95_response_time": statistics.quantiles(analysis["response_times"], n=20)[18] 
                                       if len(analysis["response_times"]) >= 20 
                                       else max(analysis["response_times"]),
                    "status_codes": dict(analysis["status_codes"])
                }
        
        return {
            "report_period": {
                "start": cutoff_time.isoformat(),
                "end": datetime.utcnow().isoformat(),
                "duration_hours": time_window.total_seconds() / 3600
            },
            "summary": {
                "total_requests": len(calls_in_window),
                "unique_endpoints": len(endpoint_analysis),
                "total_errors": sum(1 for call in calls_in_window if call.status_code >= 400),
                "avg_requests_per_hour": len(calls_in_window) / (time_window.total_seconds() / 3600)
            },
            "endpoint_analysis": endpoint_stats,
            "sla_compliance": self.sla_monitor.calculate_sla_metrics(time_window),
            "alerts_in_period": [
                asdict(alert) for alert in self.alert_manager.alert_history
                if alert.timestamp >= cutoff_time
            ]
        }

# Instância global do serviço
monitoring_service = AdvancedAPIMonitoringService()

# Função para integração com middleware
def track_api_call(request, response, response_time_ms: float, error: Optional[str] = None):
    """Função helper para tracking de chamadas de API"""
    monitoring_service.record_request(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        response_time_ms=response_time_ms,
        user_id=getattr(request.state, 'user_id', None),
        ip_address=request.client.host if request.client else None,
        error=error,
        request_size=int(request.headers.get('content-length', 0)),
        response_size=len(response.body) if hasattr(response, 'body') else None
    )

if __name__ == "__main__":
    async def demo_monitoring():
        print("📊 SISTEMA AVANÇADO DE MONITORAMENTO DE API - TECNOCURSOS AI")
        print("=" * 60)
        
        # Simular algumas requisições
        service = AdvancedAPIMonitoringService()
        
        print("\n🚀 Simulando requisições...")
        
        # Simular requisições normais
        for i in range(100):
            service.record_request(
                endpoint="/api/files/upload",
                method="POST",
                status_code=200,
                response_time_ms=500 + (i % 200),
                user_id=f"user_{i % 10}"
            )
        
        # Simular alguns erros
        for i in range(10):
            service.record_request(
                endpoint="/api/auth/login",
                method="POST", 
                status_code=401,
                response_time_ms=100,
                error="Invalid credentials"
            )
        
        # Obter dados do dashboard
        dashboard = service.get_dashboard_data()
        
        print(f"\n📈 DASHBOARD ({dashboard['time_window_minutes']} min):")
        print(f"   Total de requisições: {dashboard['total_requests_15min']}")
        print(f"   Req/min: {dashboard['requests_per_minute']:.1f}")
        print(f"   Alertas ativos: {dashboard['active_alerts']}")
        
        if dashboard['response_time_analysis'].get('performance_grade'):
            print(f"   Performance: {dashboard['response_time_analysis']['performance_grade']}")
        
        if dashboard['error_analysis'].get('overall_error_rate'):
            print(f"   Taxa de erro: {dashboard['error_analysis']['overall_error_rate']:.1f}%")
        
        print("\n🏆 TOP ENDPOINTS:")
        for endpoint, count in dashboard['top_endpoints'][:5]:
            print(f"   📍 {endpoint}: {count} requests")
        
        print("\n✨ MONITORAMENTO DEMONSTRADO!")
    
    # Executar demo
    asyncio.run(demo_monitoring()) 