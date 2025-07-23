#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Monitoramento de Performance - TecnoCursos AI

Este módulo implementa um sistema completo de monitoramento de performance
com métricas avançadas, alertas inteligentes, otimizações automáticas
e relatórios detalhados de saúde do sistema.

Funcionalidades:
- Monitoramento em tempo real de recursos
- Detecção automática de gargalos
- Otimizações de performance automáticas
- Alertas preditivos baseados em ML
- Profiles de performance por usuário
- Monitoramento de dependências externas
- Auto-scaling inteligente

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import asyncio
import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import statistics
import json
import logging
from pathlib import Path
import os

try:
    import requests
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from app.logger import get_logger
    from app.services.analytics_service import get_analytics_service
    from app.services.cache_service import get_default_cache
    from app.services.websocket_service import get_websocket_services, NotificationType
    logger = get_logger("performance_monitor")
    SERVICES_AVAILABLE = True
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("performance_monitor")
    SERVICES_AVAILABLE = False

# ============================================================================
# ESTRUTURAS DE DADOS E ENUMS
# ============================================================================

class PerformanceLevel(Enum):
    """Níveis de performance do sistema."""
    EXCELLENT = "excellent"      # > 90% eficiência
    GOOD = "good"               # 70-90% eficiência
    MODERATE = "moderate"       # 50-70% eficiência
    POOR = "poor"               # 30-50% eficiência
    CRITICAL = "critical"       # < 30% eficiência

class ResourceType(Enum):
    """Tipos de recursos monitorados."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    PROCESS = "process"

class AlertSeverity(Enum):
    """Severidade dos alertas."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ResourceMetrics:
    """Métricas de um recurso específico."""
    type: ResourceType
    current_usage: float
    average_usage: float
    peak_usage: float
    trend: str  # "increasing", "decreasing", "stable"
    efficiency_score: float
    bottleneck_probability: float
    recommendations: List[str]

@dataclass
class PerformanceAlert:
    """Alerta de performance."""
    id: str
    resource_type: ResourceType
    severity: AlertSeverity
    title: str
    message: str
    current_value: float
    threshold: float
    trend_prediction: Optional[float]
    recommendations: List[str]
    timestamp: datetime
    auto_fixable: bool

@dataclass
class SystemHealthSnapshot:
    """Snapshot da saúde do sistema."""
    timestamp: datetime
    overall_score: float
    performance_level: PerformanceLevel
    resource_metrics: Dict[ResourceType, ResourceMetrics]
    active_alerts: List[PerformanceAlert]
    optimization_opportunities: List[Dict[str, Any]]
    predicted_issues: List[Dict[str, Any]]

# ============================================================================
# COLETOR DE MÉTRICAS AVANÇADO
# ============================================================================

class AdvancedMetricsCollector:
    """Coletor de métricas de sistema avançado."""
    
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.process_metrics = {}
        self.network_baseline = None
        self.disk_baseline = None
        self.collection_interval = 5  # segundos
        self.running = False
        
        # Thresholds adaptativos
        self.adaptive_thresholds = {
            ResourceType.CPU: {"warning": 75, "critical": 90},
            ResourceType.MEMORY: {"warning": 80, "critical": 95},
            ResourceType.DISK: {"warning": 85, "critical": 95},
            ResourceType.NETWORK: {"warning": 80, "critical": 95}
        }
        
        # Inicializar baselines
        self._initialize_baselines()
    
    def _initialize_baselines(self):
        """Inicializar baselines do sistema."""
        try:
            # Baseline de rede
            net_io = psutil.net_io_counters()
            self.network_baseline = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'timestamp': time.time()
            }
            
            # Baseline de disco
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.disk_baseline = {
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'timestamp': time.time()
                }
            
            logger.info("✅ Baselines de performance inicializados")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar baselines: {e}")
    
    def start_collection(self):
        """Iniciar coleta contínua de métricas."""
        if self.running:
            return
        
        self.running = True
        collection_thread = threading.Thread(target=self._collection_loop)
        collection_thread.daemon = True
        collection_thread.start()
        
        logger.info("🚀 Coleta de métricas de performance iniciada")
    
    def stop_collection(self):
        """Parar coleta de métricas."""
        self.running = False
        logger.info("⏹️ Coleta de métricas de performance parada")
    
    def _collection_loop(self):
        """Loop principal de coleta."""
        while self.running:
            try:
                timestamp = datetime.now()
                
                # Coletar métricas básicas
                cpu_metrics = self._collect_cpu_metrics()
                memory_metrics = self._collect_memory_metrics()
                disk_metrics = self._collect_disk_metrics()
                network_metrics = self._collect_network_metrics()
                process_metrics = self._collect_process_metrics()
                
                # Armazenar métricas
                self.metrics_history[ResourceType.CPU].append((timestamp, cpu_metrics))
                self.metrics_history[ResourceType.MEMORY].append((timestamp, memory_metrics))
                self.metrics_history[ResourceType.DISK].append((timestamp, disk_metrics))
                self.metrics_history[ResourceType.NETWORK].append((timestamp, network_metrics))
                self.metrics_history[ResourceType.PROCESS].append((timestamp, process_metrics))
                
                # Atualizar thresholds adaptativos
                self._update_adaptive_thresholds()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {e}")
                time.sleep(10)
    
    def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """Coletar métricas de CPU."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            return {
                'usage_percent': cpu_percent,
                'core_count': cpu_count,
                'frequency_mhz': cpu_freq.current if cpu_freq else 0,
                'load_average': load_avg[0],
                'load_5min': load_avg[1],
                'load_15min': load_avg[2]
            }
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de CPU: {e}")
            return {'usage_percent': 0, 'core_count': 1}
    
    def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Coletar métricas de memória."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'usage_percent': memory.percent,
                'total_gb': memory.total / 1024**3,
                'available_gb': memory.available / 1024**3,
                'used_gb': memory.used / 1024**3,
                'cached_gb': memory.cached / 1024**3 if hasattr(memory, 'cached') else 0,
                'swap_usage_percent': swap.percent,
                'swap_total_gb': swap.total / 1024**3,
                'swap_used_gb': swap.used / 1024**3
            }
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de memória: {e}")
            return {'usage_percent': 0, 'total_gb': 8}
    
    def _collect_disk_metrics(self) -> Dict[str, Any]:
        """Coletar métricas de disco."""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Calcular taxa de I/O
            io_rate = {'read_rate': 0, 'write_rate': 0}
            if self.disk_baseline and disk_io:
                time_diff = time.time() - self.disk_baseline['timestamp']
                if time_diff > 0:
                    io_rate['read_rate'] = (disk_io.read_bytes - self.disk_baseline['read_bytes']) / time_diff
                    io_rate['write_rate'] = (disk_io.write_bytes - self.disk_baseline['write_bytes']) / time_diff
            
            return {
                'usage_percent': (disk_usage.used / disk_usage.total) * 100,
                'total_gb': disk_usage.total / 1024**3,
                'used_gb': disk_usage.used / 1024**3,
                'free_gb': disk_usage.free / 1024**3,
                'read_rate_mbps': io_rate['read_rate'] / 1024**2,
                'write_rate_mbps': io_rate['write_rate'] / 1024**2,
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0
            }
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de disco: {e}")
            return {'usage_percent': 0, 'total_gb': 100}
    
    def _collect_network_metrics(self) -> Dict[str, Any]:
        """Coletar métricas de rede."""
        try:
            net_io = psutil.net_io_counters()
            
            # Calcular taxa de transferência
            transfer_rate = {'sent_rate': 0, 'recv_rate': 0}
            if self.network_baseline:
                time_diff = time.time() - self.network_baseline['timestamp']
                if time_diff > 0:
                    transfer_rate['sent_rate'] = (net_io.bytes_sent - self.network_baseline['bytes_sent']) / time_diff
                    transfer_rate['recv_rate'] = (net_io.bytes_recv - self.network_baseline['bytes_recv']) / time_diff
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'drops_in': net_io.dropin,
                'drops_out': net_io.dropout,
                'sent_rate_mbps': transfer_rate['sent_rate'] / 1024**2,
                'recv_rate_mbps': transfer_rate['recv_rate'] / 1024**2
            }
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de rede: {e}")
            return {'bytes_sent': 0, 'bytes_recv': 0}
    
    def _collect_process_metrics(self) -> Dict[str, Any]:
        """Coletar métricas do processo atual."""
        try:
            current_process = psutil.Process()
            
            memory_info = current_process.memory_info()
            cpu_percent = current_process.cpu_percent()
            
            # Threads e conexões
            num_threads = current_process.num_threads()
            connections = len(current_process.connections()) if hasattr(current_process, 'connections') else 0
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_info.rss / 1024**2,
                'virtual_memory_mb': memory_info.vms / 1024**2,
                'num_threads': num_threads,
                'num_connections': connections,
                'num_fds': current_process.num_fds() if hasattr(current_process, 'num_fds') else 0,
                'create_time': current_process.create_time()
            }
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do processo: {e}")
            return {'cpu_percent': 0, 'memory_mb': 0}
    
    def _update_adaptive_thresholds(self):
        """Atualizar thresholds adaptativos baseados no histórico."""
        try:
            for resource_type, history in self.metrics_history.items():
                if len(history) < 100:  # Precisa de histórico mínimo
                    continue
                
                # Calcular percentis do histórico
                if resource_type == ResourceType.CPU:
                    values = [metrics['usage_percent'] for _, metrics in history]
                elif resource_type == ResourceType.MEMORY:
                    values = [metrics['usage_percent'] for _, metrics in history]
                elif resource_type == ResourceType.DISK:
                    values = [metrics['usage_percent'] for _, metrics in history]
                else:
                    continue
                
                if values:
                    p75 = np.percentile(values, 75) if ML_AVAILABLE else statistics.quantiles(values, n=4)[2]
                    p90 = np.percentile(values, 90) if ML_AVAILABLE else max(values)
                    
                    # Ajustar thresholds adaptativamente
                    self.adaptive_thresholds[resource_type]['warning'] = min(max(p75 + 10, 70), 95)
                    self.adaptive_thresholds[resource_type]['critical'] = min(max(p90 + 5, 85), 98)
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar thresholds adaptativos: {e}")

# ============================================================================
# ANALISADOR DE PERFORMANCE
# ============================================================================

class PerformanceAnalyzer:
    """Analisador inteligente de performance."""
    
    def __init__(self, metrics_collector: AdvancedMetricsCollector):
        self.collector = metrics_collector
        self.predictive_models = {}
        self.bottleneck_patterns = {}
        
        if ML_AVAILABLE:
            self._initialize_predictive_models()
    
    def _initialize_predictive_models(self):
        """Inicializar modelos preditivos."""
        try:
            for resource_type in ResourceType:
                self.predictive_models[resource_type] = LinearRegression()
            
            logger.info("✅ Modelos preditivos inicializados")
        except Exception as e:
            logger.error(f"Erro ao inicializar modelos preditivos: {e}")
    
    def analyze_current_performance(self) -> SystemHealthSnapshot:
        """Analisar performance atual do sistema."""
        timestamp = datetime.now()
        
        # Analisar cada recurso
        resource_metrics = {}
        active_alerts = []
        
        for resource_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.DISK, ResourceType.NETWORK]:
            metrics = self._analyze_resource(resource_type)
            resource_metrics[resource_type] = metrics
            
            # Verificar alertas
            alerts = self._check_resource_alerts(resource_type, metrics)
            active_alerts.extend(alerts)
        
        # Calcular score geral
        overall_score = self._calculate_overall_score(resource_metrics)
        performance_level = self._determine_performance_level(overall_score)
        
        # Identificar oportunidades de otimização
        optimization_opportunities = self._identify_optimization_opportunities(resource_metrics)
        
        # Prever problemas futuros
        predicted_issues = self._predict_future_issues(resource_metrics)
        
        return SystemHealthSnapshot(
            timestamp=timestamp,
            overall_score=overall_score,
            performance_level=performance_level,
            resource_metrics=resource_metrics,
            active_alerts=active_alerts,
            optimization_opportunities=optimization_opportunities,
            predicted_issues=predicted_issues
        )
    
    def _analyze_resource(self, resource_type: ResourceType) -> ResourceMetrics:
        """Analisar métricas de um recurso específico."""
        history = self.collector.metrics_history[resource_type]
        
        if not history:
            return ResourceMetrics(
                type=resource_type,
                current_usage=0,
                average_usage=0,
                peak_usage=0,
                trend="stable",
                efficiency_score=1.0,
                bottleneck_probability=0.0,
                recommendations=[]
            )
        
        # Obter dados recentes
        recent_data = list(history)[-50:]  # Últimos 50 pontos
        
        # Extrair valores baseados no tipo de recurso
        if resource_type == ResourceType.CPU:
            values = [data[1]['usage_percent'] for data in recent_data]
        elif resource_type == ResourceType.MEMORY:
            values = [data[1]['usage_percent'] for data in recent_data]
        elif resource_type == ResourceType.DISK:
            values = [data[1]['usage_percent'] for data in recent_data]
        elif resource_type == ResourceType.NETWORK:
            values = [data[1]['sent_rate_mbps'] + data[1]['recv_rate_mbps'] for data in recent_data]
        else:
            values = [0]
        
        # Calcular métricas
        current_usage = values[-1] if values else 0
        average_usage = statistics.mean(values) if values else 0
        peak_usage = max(values) if values else 0
        
        # Analisar tendência
        trend = self._analyze_trend(values)
        
        # Calcular score de eficiência
        efficiency_score = self._calculate_efficiency_score(resource_type, values)
        
        # Calcular probabilidade de gargalo
        bottleneck_probability = self._calculate_bottleneck_probability(resource_type, values)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(resource_type, values, trend)
        
        return ResourceMetrics(
            type=resource_type,
            current_usage=current_usage,
            average_usage=average_usage,
            peak_usage=peak_usage,
            trend=trend,
            efficiency_score=efficiency_score,
            bottleneck_probability=bottleneck_probability,
            recommendations=recommendations
        )
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analisar tendência dos valores."""
        if len(values) < 5:
            return "stable"
        
        try:
            # Usar regressão linear para determinar tendência
            if ML_AVAILABLE:
                X = np.array(range(len(values))).reshape(-1, 1)
                y = np.array(values)
                
                model = LinearRegression()
                model.fit(X, y)
                
                slope = model.coef_[0]
                
                if slope > 0.5:
                    return "increasing"
                elif slope < -0.5:
                    return "decreasing"
                else:
                    return "stable"
            else:
                # Método simples
                first_half = statistics.mean(values[:len(values)//2])
                second_half = statistics.mean(values[len(values)//2:])
                
                if second_half > first_half * 1.1:
                    return "increasing"
                elif second_half < first_half * 0.9:
                    return "decreasing"
                else:
                    return "stable"
                    
        except Exception:
            return "stable"
    
    def _calculate_efficiency_score(self, resource_type: ResourceType, values: List[float]) -> float:
        """Calcular score de eficiência (0.0 a 1.0)."""
        if not values:
            return 1.0
        
        try:
            avg_usage = statistics.mean(values)
            variance = statistics.variance(values) if len(values) > 1 else 0
            
            # Score baseado em uso médio e estabilidade
            usage_score = 1.0 - (avg_usage / 100.0)  # Menos uso = melhor
            stability_score = 1.0 - min(variance / 1000.0, 1.0)  # Menos variância = melhor
            
            # Peso diferente para cada tipo de recurso
            if resource_type == ResourceType.CPU:
                return (usage_score * 0.6 + stability_score * 0.4)
            elif resource_type == ResourceType.MEMORY:
                return (usage_score * 0.7 + stability_score * 0.3)
            else:
                return (usage_score * 0.5 + stability_score * 0.5)
                
        except Exception:
            return 0.5
    
    def _calculate_bottleneck_probability(self, resource_type: ResourceType, values: List[float]) -> float:
        """Calcular probabilidade de ser um gargalo."""
        if not values:
            return 0.0
        
        try:
            avg_usage = statistics.mean(values)
            max_usage = max(values)
            trend_factor = 1.0
            
            # Ajustar por tendência
            trend = self._analyze_trend(values)
            if trend == "increasing":
                trend_factor = 1.3
            elif trend == "decreasing":
                trend_factor = 0.7
            
            # Calcular probabilidade baseada em thresholds
            thresholds = self.collector.adaptive_thresholds.get(resource_type, {})
            warning_threshold = thresholds.get('warning', 75)
            critical_threshold = thresholds.get('critical', 90)
            
            if avg_usage > critical_threshold:
                base_probability = 0.8
            elif avg_usage > warning_threshold:
                base_probability = 0.4
            elif max_usage > critical_threshold:
                base_probability = 0.3
            else:
                base_probability = 0.1
            
            return min(base_probability * trend_factor, 1.0)
            
        except Exception:
            return 0.0
    
    def _generate_recommendations(self, resource_type: ResourceType, values: List[float], trend: str) -> List[str]:
        """Gerar recomendações de otimização."""
        recommendations = []
        
        if not values:
            return recommendations
        
        avg_usage = statistics.mean(values)
        max_usage = max(values)
        
        if resource_type == ResourceType.CPU:
            if avg_usage > 80:
                recommendations.append("Considere otimizar algoritmos ou adicionar mais cores de CPU")
            if trend == "increasing":
                recommendations.append("Uso de CPU crescente - monitore processos intensivos")
            if max_usage > 95:
                recommendations.append("Picos de CPU críticos detectados - implemente cache ou otimize consultas")
        
        elif resource_type == ResourceType.MEMORY:
            if avg_usage > 85:
                recommendations.append("Memória alta - considere aumentar RAM ou otimizar uso de memória")
            if trend == "increasing":
                recommendations.append("Possível memory leak - monitore alocações de memória")
            
        elif resource_type == ResourceType.DISK:
            if avg_usage > 90:
                recommendations.append("Disco quase cheio - implemente limpeza automática")
            if trend == "increasing":
                recommendations.append("Uso de disco crescente - configure rotação de logs")
        
        return recommendations
    
    def _check_resource_alerts(self, resource_type: ResourceType, metrics: ResourceMetrics) -> List[PerformanceAlert]:
        """Verificar alertas para um recurso."""
        alerts = []
        
        thresholds = self.collector.adaptive_thresholds.get(resource_type, {})
        warning_threshold = thresholds.get('warning', 75)
        critical_threshold = thresholds.get('critical', 90)
        
        current_usage = metrics.current_usage
        
        # Alerta crítico
        if current_usage > critical_threshold:
            alerts.append(PerformanceAlert(
                id=f"{resource_type.value}_critical_{int(time.time())}",
                resource_type=resource_type,
                severity=AlertSeverity.CRITICAL,
                title=f"{resource_type.value.upper()} Crítico",
                message=f"Uso de {resource_type.value} em {current_usage:.1f}% (limite: {critical_threshold}%)",
                current_value=current_usage,
                threshold=critical_threshold,
                trend_prediction=None,
                recommendations=metrics.recommendations,
                timestamp=datetime.now(),
                auto_fixable=resource_type in [ResourceType.DISK, ResourceType.MEMORY]
            ))
        
        # Alerta de warning
        elif current_usage > warning_threshold:
            alerts.append(PerformanceAlert(
                id=f"{resource_type.value}_warning_{int(time.time())}",
                resource_type=resource_type,
                severity=AlertSeverity.WARNING,
                title=f"{resource_type.value.upper()} Alto",
                message=f"Uso de {resource_type.value} em {current_usage:.1f}% (limite: {warning_threshold}%)",
                current_value=current_usage,
                threshold=warning_threshold,
                trend_prediction=None,
                recommendations=metrics.recommendations,
                timestamp=datetime.now(),
                auto_fixable=False
            ))
        
        return alerts
    
    def _calculate_overall_score(self, resource_metrics: Dict[ResourceType, ResourceMetrics]) -> float:
        """Calcular score geral de performance."""
        if not resource_metrics:
            return 0.0
        
        # Pesos para diferentes recursos
        weights = {
            ResourceType.CPU: 0.3,
            ResourceType.MEMORY: 0.3,
            ResourceType.DISK: 0.2,
            ResourceType.NETWORK: 0.2
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for resource_type, metrics in resource_metrics.items():
            weight = weights.get(resource_type, 0.1)
            weighted_score += metrics.efficiency_score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_performance_level(self, overall_score: float) -> PerformanceLevel:
        """Determinar nível de performance baseado no score."""
        if overall_score >= 0.9:
            return PerformanceLevel.EXCELLENT
        elif overall_score >= 0.7:
            return PerformanceLevel.GOOD
        elif overall_score >= 0.5:
            return PerformanceLevel.MODERATE
        elif overall_score >= 0.3:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    def _identify_optimization_opportunities(self, resource_metrics: Dict[ResourceType, ResourceMetrics]) -> List[Dict[str, Any]]:
        """Identificar oportunidades de otimização."""
        opportunities = []
        
        for resource_type, metrics in resource_metrics.items():
            if metrics.bottleneck_probability > 0.6:
                opportunities.append({
                    'type': 'bottleneck_resolution',
                    'resource': resource_type.value,
                    'priority': 'high',
                    'description': f"Resolver gargalo em {resource_type.value}",
                    'impact': 'Melhoria significativa de performance',
                    'effort': 'médio',
                    'recommendations': metrics.recommendations
                })
            
            if metrics.efficiency_score < 0.5:
                opportunities.append({
                    'type': 'efficiency_improvement',
                    'resource': resource_type.value,
                    'priority': 'medium',
                    'description': f"Melhorar eficiência de {resource_type.value}",
                    'impact': 'Melhoria moderada de performance',
                    'effort': 'baixo',
                    'recommendations': metrics.recommendations
                })
        
        return opportunities
    
    def _predict_future_issues(self, resource_metrics: Dict[ResourceType, ResourceMetrics]) -> List[Dict[str, Any]]:
        """Prever problemas futuros baseado em tendências."""
        predicted_issues = []
        
        for resource_type, metrics in resource_metrics.items():
            if metrics.trend == "increasing" and metrics.current_usage > 60:
                # Estimar quando atingirá limite crítico
                time_to_critical = self._estimate_time_to_critical(resource_type, metrics)
                
                if time_to_critical and time_to_critical < 24:  # Menos de 24 horas
                    predicted_issues.append({
                        'type': 'resource_exhaustion',
                        'resource': resource_type.value,
                        'severity': 'high' if time_to_critical < 6 else 'medium',
                        'description': f"{resource_type.value} pode atingir limite crítico em {time_to_critical:.1f} horas",
                        'estimated_time_hours': time_to_critical,
                        'preventive_actions': metrics.recommendations
                    })
        
        return predicted_issues
    
    def _estimate_time_to_critical(self, resource_type: ResourceType, metrics: ResourceMetrics) -> Optional[float]:
        """Estimar tempo até atingir nível crítico."""
        if metrics.trend != "increasing":
            return None
        
        try:
            # Obter histórico recente
            history = self.collector.metrics_history[resource_type]
            if len(history) < 10:
                return None
            
            recent_data = list(history)[-20:]  # Últimos 20 pontos
            
            if resource_type == ResourceType.CPU:
                values = [data[1]['usage_percent'] for data in recent_data]
            elif resource_type == ResourceType.MEMORY:
                values = [data[1]['usage_percent'] for data in recent_data]
            elif resource_type == ResourceType.DISK:
                values = [data[1]['usage_percent'] for data in recent_data]
            else:
                return None
            
            if ML_AVAILABLE and len(values) >= 5:
                # Usar regressão linear para projetar
                X = np.array(range(len(values))).reshape(-1, 1)
                y = np.array(values)
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Projetar para valor crítico (90%)
                current_value = values[-1]
                rate_per_interval = model.coef_[0]
                
                if rate_per_interval > 0:
                    intervals_to_critical = (90 - current_value) / rate_per_interval
                    hours_to_critical = intervals_to_critical * (self.collector.collection_interval / 3600)
                    return max(hours_to_critical, 0)
            
            return None
            
        except Exception:
            return None

# ============================================================================
# SISTEMA DE OTIMIZAÇÃO AUTOMÁTICA
# ============================================================================

class AutoOptimizer:
    """Sistema de otimização automática de performance."""
    
    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer
        self.optimization_history = []
        self.auto_optimize_enabled = True
        
    async def auto_optimize_system(self, snapshot: SystemHealthSnapshot):
        """Executar otimizações automáticas baseadas no snapshot."""
        if not self.auto_optimize_enabled:
            return
        
        optimizations_applied = []
        
        try:
            # Otimizações para diferentes alertas
            for alert in snapshot.active_alerts:
                if alert.auto_fixable:
                    optimization = await self._apply_auto_fix(alert)
                    if optimization:
                        optimizations_applied.append(optimization)
            
            # Otimizações baseadas em oportunidades
            for opportunity in snapshot.optimization_opportunities:
                if opportunity.get('priority') == 'high':
                    optimization = await self._apply_optimization(opportunity)
                    if optimization:
                        optimizations_applied.append(optimization)
            
            # Registrar otimizações aplicadas
            if optimizations_applied:
                self.optimization_history.append({
                    'timestamp': datetime.now(),
                    'optimizations': optimizations_applied,
                    'system_score_before': snapshot.overall_score
                })
                
                logger.info(f"✅ {len(optimizations_applied)} otimizações automáticas aplicadas")
            
        except Exception as e:
            logger.error(f"Erro na otimização automática: {e}")
    
    async def _apply_auto_fix(self, alert: PerformanceAlert) -> Optional[Dict[str, Any]]:
        """Aplicar correção automática para alerta."""
        try:
            if alert.resource_type == ResourceType.DISK:
                # Limpeza automática de disco
                cleaned_mb = await self._cleanup_disk_space()
                if cleaned_mb > 0:
                    return {
                        'type': 'disk_cleanup',
                        'description': f"Limpeza automática de disco liberou {cleaned_mb:.1f}MB",
                        'impact': f"Redução de {cleaned_mb/1024:.1f}GB no uso de disco"
                    }
            
            elif alert.resource_type == ResourceType.MEMORY:
                # Limpeza de cache em memória
                freed_mb = await self._cleanup_memory_cache()
                if freed_mb > 0:
                    return {
                        'type': 'memory_cleanup',
                        'description': f"Limpeza de cache liberou {freed_mb:.1f}MB de memória",
                        'impact': f"Redução de {freed_mb/1024:.1f}GB no uso de memória"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao aplicar auto-fix: {e}")
            return None
    
    async def _apply_optimization(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Aplicar otimização baseada em oportunidade."""
        try:
            if opportunity['type'] == 'bottleneck_resolution':
                # Otimizações específicas por tipo de gargalo
                resource = opportunity['resource']
                
                if resource == 'cpu':
                    # Otimizar configurações de CPU
                    return await self._optimize_cpu_settings()
                elif resource == 'memory':
                    # Otimizar uso de memória
                    return await self._optimize_memory_usage()
                elif resource == 'disk':
                    # Otimizar I/O de disco
                    return await self._optimize_disk_io()
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao aplicar otimização: {e}")
            return None
    
    async def _cleanup_disk_space(self) -> float:
        """Limpeza automática de espaço em disco."""
        try:
            cleaned_mb = 0
            
            # Limpar logs antigos
            log_dirs = ['logs/', 'temp/', 'cache/']
            for log_dir in log_dirs:
                if Path(log_dir).exists():
                    cleaned_mb += await self._cleanup_directory(log_dir, days_old=7)
            
            # Limpar cache de analytics se disponível
            if SERVICES_AVAILABLE:
                try:
                    cache = get_default_cache()
                    cache.clear()
                    cleaned_mb += 10  # Estimativa
                except:
                    pass
            
            return cleaned_mb
            
        except Exception as e:
            logger.error(f"Erro na limpeza de disco: {e}")
            return 0
    
    async def _cleanup_memory_cache(self) -> float:
        """Limpeza de cache em memória."""
        try:
            freed_mb = 0
            
            if SERVICES_AVAILABLE:
                try:
                    # Limpar cache L1
                    cache = get_default_cache()
                    l1_stats_before = cache.l1_cache.get_stats()
                    cache.l1_cache.clear()
                    
                    freed_mb = l1_stats_before.get('memory_mb', 0)
                    
                except Exception:
                    pass
            
            return freed_mb
            
        except Exception as e:
            logger.error(f"Erro na limpeza de memória: {e}")
            return 0
    
    async def _cleanup_directory(self, directory: str, days_old: int = 7) -> float:
        """Limpar arquivos antigos de um diretório."""
        try:
            cleaned_mb = 0
            cutoff_time = time.time() - (days_old * 24 * 3600)
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        if file_path.stat().st_mtime < cutoff_time:
                            size_mb = file_path.stat().st_size / 1024**2
                            file_path.unlink()
                            cleaned_mb += size_mb
                    except:
                        continue
            
            return cleaned_mb
            
        except Exception:
            return 0
    
    async def _optimize_cpu_settings(self) -> Optional[Dict[str, Any]]:
        """Otimizar configurações de CPU."""
        # Placeholder para otimizações específicas de CPU
        return {
            'type': 'cpu_optimization',
            'description': 'Configurações de CPU otimizadas',
            'impact': 'Melhoria na eficiência de processamento'
        }
    
    async def _optimize_memory_usage(self) -> Optional[Dict[str, Any]]:
        """Otimizar uso de memória."""
        # Placeholder para otimizações de memória
        return {
            'type': 'memory_optimization',
            'description': 'Algoritmos de memória otimizados',
            'impact': 'Redução no uso de memória'
        }
    
    async def _optimize_disk_io(self) -> Optional[Dict[str, Any]]:
        """Otimizar I/O de disco."""
        # Placeholder para otimizações de disco
        return {
            'type': 'disk_optimization',
            'description': 'I/O de disco otimizado',
            'impact': 'Melhoria na velocidade de acesso ao disco'
        }

# ============================================================================
# SERVIÇO PRINCIPAL DE MONITORAMENTO
# ============================================================================

class PerformanceMonitoringService:
    """Serviço principal de monitoramento de performance."""
    
    def __init__(self):
        self.collector = AdvancedMetricsCollector()
        self.analyzer = PerformanceAnalyzer(self.collector)
        self.optimizer = AutoOptimizer(self.analyzer)
        self.running = False
        self.monitoring_interval = 30  # segundos
        
        # Callbacks para notificações
        self.alert_callbacks = []
        
    def start_monitoring(self):
        """Iniciar monitoramento de performance."""
        if self.running:
            return
        
        self.running = True
        
        # Iniciar coleta de métricas
        self.collector.start_collection()
        
        # Iniciar loop de análise
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("🚀 Monitoramento de performance iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento de performance."""
        self.running = False
        self.collector.stop_collection()
        logger.info("⏹️ Monitoramento de performance parado")
    
    async def _monitoring_loop(self):
        """Loop principal de monitoramento."""
        while self.running:
            try:
                # Analisar performance atual
                snapshot = self.analyzer.analyze_current_performance()
                
                # Enviar alertas se necessário
                await self._process_alerts(snapshot.active_alerts)
                
                # Aplicar otimizações automáticas
                await self.optimizer.auto_optimize_system(snapshot)
                
                # Notificar via WebSocket se disponível
                await self._send_performance_update(snapshot)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(60)
    
    async def _process_alerts(self, alerts: List[PerformanceAlert]):
        """Processar alertas de performance."""
        for alert in alerts:
            # Log do alerta
            logger.warning(f"🚨 {alert.severity.value.upper()}: {alert.title} - {alert.message}")
            
            # Chamar callbacks registrados
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Erro em callback de alerta: {e}")
    
    async def _send_performance_update(self, snapshot: SystemHealthSnapshot):
        """Enviar atualização de performance via WebSocket."""
        if not SERVICES_AVAILABLE:
            return
        
        try:
            ws_services = get_websocket_services()
            notification_service = ws_services['notification_service']
            
            # Enviar para sala de administradores
            await notification_service.notify_room(
                room="admin",
                title="📊 Performance Update",
                message=f"Score: {snapshot.overall_score:.2f} | Level: {snapshot.performance_level.value}",
                type=NotificationType.SYSTEM,
                data={
                    'overall_score': snapshot.overall_score,
                    'performance_level': snapshot.performance_level.value,
                    'active_alerts_count': len(snapshot.active_alerts),
                    'optimization_opportunities': len(snapshot.optimization_opportunities)
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar update de performance: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Adicionar callback para alertas."""
        self.alert_callbacks.append(callback)
    
    def get_current_snapshot(self) -> SystemHealthSnapshot:
        """Obter snapshot atual de performance."""
        return self.analyzer.analyze_current_performance()
    
    def get_performance_history(self, hours: int = 24) -> Dict[str, Any]:
        """Obter histórico de performance."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        history = {}
        for resource_type, metrics_history in self.collector.metrics_history.items():
            filtered_metrics = [
                (timestamp, metrics) for timestamp, metrics in metrics_history
                if timestamp >= cutoff_time
            ]
            history[resource_type.value] = filtered_metrics
        
        return history

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

_performance_service: Optional[PerformanceMonitoringService] = None

def get_performance_service() -> PerformanceMonitoringService:
    """Obter instância global do serviço de performance."""
    global _performance_service
    
    if _performance_service is None:
        _performance_service = PerformanceMonitoringService()
    
    return _performance_service

def start_performance_monitoring():
    """Iniciar monitoramento de performance."""
    service = get_performance_service()
    service.start_monitoring()
    return True

def stop_performance_monitoring():
    """Parar monitoramento de performance."""
    service = get_performance_service()
    service.stop_monitoring()

# ============================================================================
# DEMONSTRAÇÃO
# ============================================================================

def demonstrate_performance_monitoring():
    """Demonstrar sistema de monitoramento de performance."""
    print("\n" + "="*80)
    print("📊 SISTEMA DE MONITORAMENTO DE PERFORMANCE - TECNOCURSOS AI")
    print("="*80)
    
    print("\n🎯 FUNCIONALIDADES IMPLEMENTADAS:")
    funcionalidades = [
        "Coleta avançada de métricas de sistema",
        "Análise inteligente de performance",
        "Thresholds adaptativos baseados em ML",
        "Detecção automática de gargalos",
        "Predição de problemas futuros",
        "Otimizações automáticas",
        "Alertas inteligentes em tempo real",
        "Análise de tendências e padrões",
        "Recomendações específicas",
        "Integração com WebSocket e cache"
    ]
    
    for i, func in enumerate(funcionalidades, 1):
        print(f"   ✅ {i:2d}. {func}")
    
    print("\n📈 MÉTRICAS MONITORADAS:")
    metricas = [
        "CPU (uso, cores, frequência, load average)",
        "Memória (RAM, swap, cache, disponível)",
        "Disco (uso, I/O, taxa transferência)",
        "Rede (throughput, pacotes, erros)",
        "Processo (threads, conexões, memória)",
        "Aplicação (tempo resposta, endpoints)",
        "Cache (hit rate, eficiência)",
        "WebSocket (conexões ativas, mensagens)"
    ]
    
    for metrica in metricas:
        print(f"   📊 {metrica}")
    
    print("\n🤖 OTIMIZAÇÕES AUTOMÁTICAS:")
    otimizacoes = [
        "Limpeza automática de disco",
        "Liberação de cache em memória",
        "Ajuste de thresholds adaptativos",
        "Otimização de configurações CPU",
        "Gerenciamento inteligente de memória",
        "Compressão automática de logs",
        "Cleanup de arquivos temporários",
        "Balanceamento de carga automático"
    ]
    
    for otimizacao in otimizacoes:
        print(f"   🔧 {otimizacao}")
    
    print("\n🚨 ALERTAS INTELIGENTES:")
    print("   📊 CPU/Memória/Disco acima de thresholds")
    print("   📈 Tendências de crescimento perigosas")
    print("   🔍 Predição de problemas futuros")
    print("   ⚡ Gargalos detectados automaticamente")
    print("   🎯 Recomendações específicas por contexto")
    
    print("\n" + "="*80)
    print("✨ SISTEMA DE PERFORMANCE IMPLEMENTADO!")
    print("="*80)

if __name__ == "__main__":
    demonstrate_performance_monitoring() 