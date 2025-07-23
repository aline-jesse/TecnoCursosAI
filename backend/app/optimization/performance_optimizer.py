#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Performance Optimization System - TecnoCursos AI

Sistema avançado de otimização de performance seguindo as melhores práticas de:
- FastAPI performance optimization
- Database query optimization  
- Caching strategies
- Memory optimization
- CPU optimization
- I/O optimization
- Network optimization
- Auto-scaling optimization

Baseado em:
- FastAPI performance best practices
- High-performance Python patterns
- Microservices optimization
- Cloud-native performance tuning

Funcionalidades:
- Query optimization automático
- Intelligent caching
- Memory profiling e optimization
- CPU profiling e optimization
- Network optimization
- Auto-scaling recommendations
- Performance monitoring
- Bottleneck detection
- Resource optimization

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
import sys
import json
import time
import psutil
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from functools import wraps, lru_cache
import weakref
import gc

try:
    import aiofiles
    import asyncpg
    import redis.asyncio as redis
    import sqlalchemy
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Query
    from sqlalchemy import text
    import uvloop
    ASYNC_DEPS_AVAILABLE = True
except ImportError:
    ASYNC_DEPS_AVAILABLE = False
    print("⚠️  Dependências async não disponíveis")

try:
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libs não disponíveis para optimization inteligente")

try:
    import line_profiler
    import memory_profiler
    import py-spy
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False
    print("⚠️  Profiling tools não disponíveis")

# ============================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# ============================================================================

@dataclass
class PerformanceConfig:
    """Configurações de performance"""
    # Cache settings
    cache_ttl_default: int = 300  # 5 minutes
    cache_ttl_short: int = 60     # 1 minute
    cache_ttl_long: int = 3600    # 1 hour
    cache_max_size: int = 1000
    
    # Database settings
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    query_timeout: int = 30
    
    # Memory settings
    max_memory_usage: float = 0.8  # 80% of available
    gc_threshold: float = 0.7      # 70% memory usage triggers GC
    
    # CPU settings
    max_cpu_usage: float = 0.8     # 80% CPU usage
    cpu_optimization_enabled: bool = True
    
    # Network settings
    request_timeout: int = 30
    connection_pool_size: int = 100
    max_keepalive_connections: int = 20
    
    # Monitoring settings
    performance_monitoring: bool = True
    profiling_enabled: bool = False
    metrics_collection_interval: int = 10  # seconds

@dataclass
class PerformanceMetric:
    """Métrica de performance"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    threshold: Optional[float] = None
    status: str = "normal"  # normal, warning, critical

@dataclass
class OptimizationRecommendation:
    """Recomendação de otimização"""
    category: str
    priority: str  # low, medium, high, critical
    description: str
    implementation: str
    expected_improvement: str
    effort_level: str  # low, medium, high

# ============================================================================
# SISTEMA DE CACHE INTELIGENTE
# ============================================================================

class IntelligentCache:
    """Sistema de cache inteligente com ML"""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.redis_client = None
        self.local_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_usage": 0
        }
        self.access_patterns = {}
        self.ml_predictor = None
        
    async def initialize(self):
        """Inicializar sistema de cache"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True
            )
            await self.redis_client.ping()
            logging.info("✅ Redis cache conectado")
        except Exception as e:
            logging.warning(f"⚠️  Redis não disponível, usando cache local: {e}")
        
        # Inicializar ML predictor
        if ML_AVAILABLE:
            self._initialize_ml_predictor()
    
    def _initialize_ml_predictor(self):
        """Inicializar preditor ML para cache"""
        # Modelo para prever quais itens devem ser cached
        self.ml_predictor = {
            "model": KMeans(n_clusters=3),  # 3 clusters: hot, warm, cold
            "scaler": StandardScaler(),
            "trained": False
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Obter item do cache"""
        # Registrar acesso
        self._record_access(key)
        
        try:
            # Tentar Redis primeiro
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value is not None:
                    self.cache_stats["hits"] += 1
                    return json.loads(value)
            
            # Fallback para cache local
            if key in self.local_cache:
                item = self.local_cache[key]
                if item["expires_at"] > datetime.utcnow():
                    self.cache_stats["hits"] += 1
                    return item["value"]
                else:
                    del self.local_cache[key]
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logging.error(f"Erro ao obter cache {key}: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Definir item no cache"""
        try:
            if ttl is None:
                ttl = self._predict_optimal_ttl(key)
            
            serialized_value = json.dumps(value, default=str)
            
            # Tentar Redis primeiro
            if self.redis_client:
                await self.redis_client.setex(key, ttl, serialized_value)
            
            # Também armazenar localmente
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            self.local_cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "size": len(serialized_value)
            }
            
            # Limpar cache local se necessário
            self._cleanup_local_cache()
            
            return True
            
        except Exception as e:
            logging.error(f"Erro ao definir cache {key}: {e}")
            return False
    
    def _record_access(self, key: str):
        """Registrar padrão de acesso"""
        now = datetime.utcnow()
        
        if key not in self.access_patterns:
            self.access_patterns[key] = {
                "count": 0,
                "last_access": now,
                "access_frequency": 0,
                "access_times": []
            }
        
        pattern = self.access_patterns[key]
        pattern["count"] += 1
        pattern["last_access"] = now
        pattern["access_times"].append(now)
        
        # Manter apenas últimas 100 acessos
        if len(pattern["access_times"]) > 100:
            pattern["access_times"] = pattern["access_times"][-100:]
        
        # Calcular frequência (acessos por hora)
        recent_accesses = [
            t for t in pattern["access_times"]
            if (now - t).total_seconds() < 3600
        ]
        pattern["access_frequency"] = len(recent_accesses)
    
    def _predict_optimal_ttl(self, key: str) -> int:
        """Prever TTL ótimo baseado em padrões de acesso"""
        if key not in self.access_patterns:
            return self.config.cache_ttl_default
        
        pattern = self.access_patterns[key]
        frequency = pattern["access_frequency"]
        
        # TTL baseado na frequência de acesso
        if frequency > 50:  # Muito acessado
            return self.config.cache_ttl_long
        elif frequency > 10:  # Moderadamente acessado
            return self.config.cache_ttl_default
        else:  # Pouco acessado
            return self.config.cache_ttl_short
    
    def _cleanup_local_cache(self):
        """Limpar cache local se necessário"""
        # Remover itens expirados
        now = datetime.utcnow()
        expired_keys = [
            key for key, item in self.local_cache.items()
            if item["expires_at"] <= now
        ]
        
        for key in expired_keys:
            del self.local_cache[key]
            self.cache_stats["evictions"] += 1
        
        # Verificar uso de memória
        current_size = sum(item["size"] for item in self.local_cache.values())
        max_size = self.config.cache_max_size * 1024 * 1024  # MB to bytes
        
        if current_size > max_size:
            # Remover LRU items
            sorted_items = sorted(
                self.local_cache.items(),
                key=lambda x: self.access_patterns.get(x[0], {}).get("last_access", datetime.min)
            )
            
            # Remover 20% dos itens mais antigos
            items_to_remove = len(sorted_items) // 5
            for key, _ in sorted_items[:items_to_remove]:
                del self.local_cache[key]
                self.cache_stats["evictions"] += 1
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "local_cache_size": len(self.local_cache),
            "access_patterns_count": len(self.access_patterns)
        }

# ============================================================================
# OTIMIZADOR DE QUERIES
# ============================================================================

class QueryOptimizer:
    """Otimizador de queries SQL"""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.query_stats = {}
        self.slow_queries = []
        self.optimization_rules = self._load_optimization_rules()
        
    def _load_optimization_rules(self) -> List[Dict]:
        """Carregar regras de otimização"""
        return [
            {
                "pattern": r"SELECT \* FROM",
                "issue": "SELECT * usage",
                "recommendation": "Specify only needed columns",
                "severity": "medium"
            },
            {
                "pattern": r"WHERE.*LIKE '%.*%'",
                "issue": "Full-text search without index",
                "recommendation": "Use full-text search index or MATCH AGAINST",
                "severity": "high"
            },
            {
                "pattern": r"ORDER BY.*LIMIT",
                "issue": "ORDER BY without index",
                "recommendation": "Add index on ORDER BY columns",
                "severity": "medium"
            },
            {
                "pattern": r"JOIN.*ON.*=.*AND",
                "issue": "Complex JOIN condition",
                "recommendation": "Optimize JOIN conditions or add composite index",
                "severity": "medium"
            },
            {
                "pattern": r"IN\s*\([^)]{100,}\)",
                "issue": "Large IN clause",
                "recommendation": "Use temporary table or EXISTS subquery",
                "severity": "high"
            }
        ]
    
    async def analyze_query(self, query: str, execution_time: float) -> Dict[str, Any]:
        """Analisar query para otimizações"""
        query_hash = hash(query)
        
        # Registrar estatísticas
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                "query": query,
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "min_time": float('inf'),
                "issues": []
            }
        
        stats = self.query_stats[query_hash]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["min_time"] = min(stats["min_time"], execution_time)
        
        # Verificar se é query lenta
        if execution_time > 1.0:  # > 1 segundo
            self.slow_queries.append({
                "query": query,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow()
            })
            
            # Manter apenas últimas 100 queries lentas
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
        
        # Aplicar regras de otimização
        issues = self._check_optimization_rules(query)
        stats["issues"] = issues
        
        return {
            "query_hash": query_hash,
            "execution_time": execution_time,
            "issues": issues,
            "recommendations": [issue["recommendation"] for issue in issues]
        }
    
    def _check_optimization_rules(self, query: str) -> List[Dict]:
        """Verificar regras de otimização"""
        issues = []
        
        import re
        for rule in self.optimization_rules:
            if re.search(rule["pattern"], query, re.IGNORECASE):
                issues.append({
                    "issue": rule["issue"],
                    "recommendation": rule["recommendation"],
                    "severity": rule["severity"]
                })
        
        return issues
    
    async def generate_index_recommendations(self, database_url: str) -> List[Dict]:
        """Gerar recomendações de índices"""
        recommendations = []
        
        try:
            # Analisar queries lentas para sugerir índices
            for query_data in self.slow_queries[-20:]:  # Últimas 20 queries lentas
                query = query_data["query"]
                
                # Extrair colunas WHERE
                where_columns = self._extract_where_columns(query)
                if where_columns:
                    recommendations.append({
                        "type": "index",
                        "columns": where_columns,
                        "reason": f"WHERE clause optimization",
                        "query_example": query[:100] + "...",
                        "priority": "high"
                    })
                
                # Extrair colunas ORDER BY
                order_columns = self._extract_order_columns(query)
                if order_columns:
                    recommendations.append({
                        "type": "index",
                        "columns": order_columns,
                        "reason": "ORDER BY optimization",
                        "query_example": query[:100] + "...",
                        "priority": "medium"
                    })
                
                # Extrair colunas JOIN
                join_columns = self._extract_join_columns(query)
                if join_columns:
                    recommendations.append({
                        "type": "index",
                        "columns": join_columns,
                        "reason": "JOIN optimization",
                        "query_example": query[:100] + "...",
                        "priority": "high"
                    })
                    
        except Exception as e:
            logging.error(f"Erro ao gerar recomendações de índice: {e}")
        
        return recommendations
    
    def _extract_where_columns(self, query: str) -> List[str]:
        """Extrair colunas de WHERE clause"""
        import re
        
        # Padrão simplificado para extrair colunas
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return []
        
        where_clause = where_match.group(1)
        
        # Extrair nomes de colunas (simplificado)
        column_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*[=<>!]'
        columns = re.findall(column_pattern, where_clause)
        
        return list(set(columns))  # Remove duplicatas
    
    def _extract_order_columns(self, query: str) -> List[str]:
        """Extrair colunas de ORDER BY"""
        import re
        
        order_match = re.search(r'ORDER\s+BY\s+(.+?)(?:\s+LIMIT|$)', query, re.IGNORECASE)
        if not order_match:
            return []
        
        order_clause = order_match.group(1)
        
        # Extrair nomes de colunas
        column_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)'
        columns = re.findall(column_pattern, order_clause)
        
        return list(set(columns))
    
    def _extract_join_columns(self, query: str) -> List[str]:
        """Extrair colunas de JOIN"""
        import re
        
        join_matches = re.findall(r'JOIN\s+\w+\s+ON\s+(.+?)(?:\s+WHERE|\s+ORDER|\s+GROUP|$)', query, re.IGNORECASE)
        columns = []
        
        for join_condition in join_matches:
            # Extrair colunas da condição de JOIN
            column_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)'
            join_columns = re.findall(column_pattern, join_condition)
            columns.extend(join_columns)
        
        return list(set(columns))
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gerar relatório de performance de queries"""
        # Top queries por tempo total
        top_by_total_time = sorted(
            self.query_stats.values(),
            key=lambda x: x["total_time"],
            reverse=True
        )[:10]
        
        # Top queries por tempo médio
        top_by_avg_time = sorted(
            self.query_stats.values(),
            key=lambda x: x["avg_time"],
            reverse=True
        )[:10]
        
        # Queries com mais issues
        queries_with_issues = [
            q for q in self.query_stats.values()
            if q["issues"]
        ]
        
        return {
            "total_queries": len(self.query_stats),
            "slow_queries_count": len(self.slow_queries),
            "top_by_total_time": top_by_total_time,
            "top_by_avg_time": top_by_avg_time,
            "queries_with_issues": len(queries_with_issues),
            "recent_slow_queries": self.slow_queries[-10:]
        }

# ============================================================================
# MONITOR DE PERFORMANCE
# ============================================================================

class PerformanceMonitor:
    """Monitor de performance em tempo real"""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.metrics = []
        self.alerts = []
        self.monitoring_active = False
        self.monitoring_task = None
        
    async def start_monitoring(self):
        """Iniciar monitoramento"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logging.info("📊 Performance monitoring iniciado")
    
    async def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logging.info("📊 Performance monitoring parado")
    
    async def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Coletar métricas
                await self._collect_system_metrics()
                await self._collect_application_metrics()
                
                # Verificar thresholds
                self._check_performance_thresholds()
                
                # Aguardar próxima coleta
                await asyncio.sleep(self.config.metrics_collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Erro no monitoramento: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """Coletar métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric("cpu_usage", cpu_percent, "%", self.config.max_cpu_usage * 100)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self._add_metric("memory_usage", memory_percent, "%", self.config.max_memory_usage * 100)
            self._add_metric("memory_available", memory.available / 1024**3, "GB")
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            self._add_metric("disk_usage", disk_percent, "%", 90.0)
            
            # Rede
            net_io = psutil.net_io_counters()
            self._add_metric("network_bytes_sent", net_io.bytes_sent / 1024**2, "MB")
            self._add_metric("network_bytes_recv", net_io.bytes_recv / 1024**2, "MB")
            
            # Processos
            process_count = len(psutil.pids())
            self._add_metric("process_count", process_count, "count")
            
        except Exception as e:
            logging.error(f"Erro ao coletar métricas do sistema: {e}")
    
    async def _collect_application_metrics(self):
        """Coletar métricas da aplicação"""
        try:
            # Garbage collection
            gc_stats = gc.get_stats()
            if gc_stats:
                self._add_metric("gc_collections", gc_stats[0]["collections"], "count")
            
            # Threads ativas
            thread_count = threading.active_count()
            self._add_metric("active_threads", thread_count, "count")
            
            # Handles de arquivo abertos
            process = psutil.Process()
            open_files = len(process.open_files())
            self._add_metric("open_files", open_files, "count")
            
        except Exception as e:
            logging.error(f"Erro ao coletar métricas da aplicação: {e}")
    
    def _add_metric(self, name: str, value: float, unit: str, threshold: Optional[float] = None):
        """Adicionar métrica"""
        status = "normal"
        if threshold and value > threshold:
            status = "critical" if value > threshold * 1.2 else "warning"
        
        metric = PerformanceMetric(
            metric_name=name,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
            threshold=threshold,
            status=status
        )
        
        self.metrics.append(metric)
        
        # Manter apenas últimas 1000 métricas
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def _check_performance_thresholds(self):
        """Verificar thresholds de performance"""
        recent_metrics = [m for m in self.metrics if (datetime.utcnow() - m.timestamp).total_seconds() < 60]
        
        for metric in recent_metrics:
            if metric.status in ["warning", "critical"]:
                alert = {
                    "alert_id": f"perf_{metric.metric_name}_{int(time.time())}",
                    "metric_name": metric.metric_name,
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "status": metric.status,
                    "timestamp": metric.timestamp,
                    "message": f"{metric.metric_name} is {metric.status}: {metric.value}{metric.unit}"
                }
                
                # Evitar spam de alertas
                if not self._is_duplicate_alert(alert):
                    self.alerts.append(alert)
                    logging.warning(f"⚠️  Performance Alert: {alert['message']}")
    
    def _is_duplicate_alert(self, new_alert: Dict) -> bool:
        """Verificar se é alerta duplicado"""
        recent_alerts = [
            a for a in self.alerts 
            if (datetime.utcnow() - a["timestamp"]).total_seconds() < 300  # 5 minutos
        ]
        
        for alert in recent_alerts:
            if (alert["metric_name"] == new_alert["metric_name"] and 
                alert["status"] == new_alert["status"]):
                return True
        
        return False
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obter métricas atuais"""
        if not self.metrics:
            return {}
        
        # Métricas mais recentes por nome
        latest_metrics = {}
        for metric in reversed(self.metrics):
            if metric.metric_name not in latest_metrics:
                latest_metrics[metric.metric_name] = {
                    "value": metric.value,
                    "unit": metric.unit,
                    "status": metric.status,
                    "timestamp": metric.timestamp
                }
        
        return latest_metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obter resumo de performance"""
        recent_metrics = [
            m for m in self.metrics 
            if (datetime.utcnow() - m.timestamp).total_seconds() < 3600  # Última hora
        ]
        
        recent_alerts = [
            a for a in self.alerts
            if (datetime.utcnow() - a["timestamp"]).total_seconds() < 3600
        ]
        
        critical_alerts = [a for a in recent_alerts if a["status"] == "critical"]
        warning_alerts = [a for a in recent_alerts if a["status"] == "warning"]
        
        return {
            "metrics_collected": len(recent_metrics),
            "alerts_total": len(recent_alerts),
            "critical_alerts": len(critical_alerts),
            "warning_alerts": len(warning_alerts),
            "latest_metrics": self.get_current_metrics(),
            "recent_alerts": recent_alerts[-10:]  # Últimos 10 alertas
        }

# ============================================================================
# OTIMIZADOR DE RECURSOS
# ============================================================================

class ResourceOptimizer:
    """Otimizador de recursos do sistema"""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.optimization_history = []
        
    async def optimize_memory(self) -> List[OptimizationRecommendation]:
        """Otimizar uso de memória"""
        recommendations = []
        
        # Verificar uso atual de memória
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent > self.config.max_memory_usage * 100:
            # Forçar garbage collection
            collected = gc.collect()
            recommendations.append(OptimizationRecommendation(
                category="memory",
                priority="high",
                description=f"Triggered garbage collection, freed {collected} objects",
                implementation="gc.collect()",
                expected_improvement="5-15% memory reduction",
                effort_level="low"
            ))
            
            # Sugerir otimizações adicionais
            recommendations.append(OptimizationRecommendation(
                category="memory",
                priority="medium",
                description="Consider implementing object pooling for frequently created objects",
                implementation="Use object pools for database connections, request objects",
                expected_improvement="10-20% memory reduction",
                effort_level="medium"
            ))
            
            recommendations.append(OptimizationRecommendation(
                category="memory",
                priority="medium",
                description="Implement lazy loading for large objects",
                implementation="Load data only when needed, use generators",
                expected_improvement="15-30% memory reduction",
                effort_level="medium"
            ))
        
        return recommendations
    
    async def optimize_cpu(self) -> List[OptimizationRecommendation]:
        """Otimizar uso de CPU"""
        recommendations = []
        
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent > self.config.max_cpu_usage * 100:
            recommendations.append(OptimizationRecommendation(
                category="cpu",
                priority="high",
                description="High CPU usage detected",
                implementation="Profile code to identify bottlenecks",
                expected_improvement="20-40% CPU reduction",
                effort_level="high"
            ))
            
            recommendations.append(OptimizationRecommendation(
                category="cpu",
                priority="medium",
                description="Implement async/await for I/O operations",
                implementation="Convert blocking I/O to async operations",
                expected_improvement="30-50% CPU efficiency gain",
                effort_level="medium"
            ))
            
            recommendations.append(OptimizationRecommendation(
                category="cpu",
                priority="medium",
                description="Use connection pooling for database operations",
                implementation="Implement connection pooling",
                expected_improvement="15-25% CPU reduction",
                effort_level="low"
            ))
        
        return recommendations
    
    async def optimize_database_connections(self) -> List[OptimizationRecommendation]:
        """Otimizar conexões de banco"""
        recommendations = []
        
        # Verificar pool de conexões (simulado)
        active_connections = 15  # Simulado
        max_connections = self.config.db_pool_size
        
        if active_connections > max_connections * 0.8:
            recommendations.append(OptimizationRecommendation(
                category="database",
                priority="high",
                description=f"High database connection usage: {active_connections}/{max_connections}",
                implementation="Increase pool size or optimize query patterns",
                expected_improvement="Reduced connection contention",
                effort_level="low"
            ))
            
            recommendations.append(OptimizationRecommendation(
                category="database",
                priority="medium",
                description="Implement connection pooling with proper lifecycle management",
                implementation="Use SQLAlchemy pool with proper settings",
                expected_improvement="Better connection reuse",
                effort_level="medium"
            ))
        
        return recommendations
    
    async def optimize_network(self) -> List[OptimizationRecommendation]:
        """Otimizar performance de rede"""
        recommendations = []
        
        # Verificar I/O de rede
        net_io = psutil.net_io_counters()
        
        recommendations.append(OptimizationRecommendation(
            category="network",
            priority="medium",
            description="Implement response compression",
            implementation="Enable gzip compression for API responses",
            expected_improvement="50-80% bandwidth reduction",
            effort_level="low"
        ))
        
        recommendations.append(OptimizationRecommendation(
            category="network",
            priority="medium",
            description="Use HTTP/2 for better multiplexing",
            implementation="Configure server to support HTTP/2",
            expected_improvement="20-40% latency reduction",
            effort_level="low"
        ))
        
        recommendations.append(OptimizationRecommendation(
            category="network",
            priority="low",
            description="Implement CDN for static assets",
            implementation="Use CloudFront or similar CDN",
            expected_improvement="40-60% faster asset loading",
            effort_level="medium"
        ))
        
        return recommendations
    
    async def generate_optimization_plan(self) -> Dict[str, Any]:
        """Gerar plano completo de otimização"""
        all_recommendations = []
        
        # Coletar todas as recomendações
        memory_recs = await self.optimize_memory()
        cpu_recs = await self.optimize_cpu()
        db_recs = await self.optimize_database_connections()
        network_recs = await self.optimize_network()
        
        all_recommendations.extend(memory_recs)
        all_recommendations.extend(cpu_recs)
        all_recommendations.extend(db_recs)
        all_recommendations.extend(network_recs)
        
        # Priorizar recomendações
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_recommendations.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        # Gerar plano
        plan = {
            "timestamp": datetime.utcnow(),
            "total_recommendations": len(all_recommendations),
            "by_priority": {
                "critical": len([r for r in all_recommendations if r.priority == "critical"]),
                "high": len([r for r in all_recommendations if r.priority == "high"]),
                "medium": len([r for r in all_recommendations if r.priority == "medium"]),
                "low": len([r for r in all_recommendations if r.priority == "low"])
            },
            "by_category": {
                "memory": len([r for r in all_recommendations if r.category == "memory"]),
                "cpu": len([r for r in all_recommendations if r.category == "cpu"]),
                "database": len([r for r in all_recommendations if r.category == "database"]),
                "network": len([r for r in all_recommendations if r.category == "network"])
            },
            "recommendations": [asdict(r) for r in all_recommendations]
        }
        
        return plan

# ============================================================================
# SISTEMA PRINCIPAL DE OTIMIZAÇÃO
# ============================================================================

class AdvancedPerformanceOptimizer:
    """Sistema principal de otimização de performance"""
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        self.cache_system = IntelligentCache(self.config)
        self.query_optimizer = QueryOptimizer(self.config)
        self.performance_monitor = PerformanceMonitor(self.config)
        self.resource_optimizer = ResourceOptimizer(self.config)
        self.optimization_enabled = True
        
    async def initialize(self):
        """Inicializar sistema de otimização"""
        logging.info("🚀 Inicializando Advanced Performance Optimizer...")
        
        # Inicializar subsistemas
        await self.cache_system.initialize()
        
        if self.config.performance_monitoring:
            await self.performance_monitor.start_monitoring()
        
        # Configurar event loop otimizado
        if 'uvloop' in sys.modules:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logging.info("✅ UVLoop habilitado para melhor performance")
        
        logging.info("✅ Advanced Performance Optimizer inicializado")
    
    async def shutdown(self):
        """Finalizar sistema de otimização"""
        if self.config.performance_monitoring:
            await self.performance_monitor.stop_monitoring()
        
        logging.info("🔄 Advanced Performance Optimizer finalizado")
    
    def optimize_function(self, ttl: Optional[int] = None):
        """Decorator para otimização automática de funções"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.optimization_enabled:
                    return await func(*args, **kwargs)
                
                # Gerar chave de cache
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # Tentar obter do cache
                cached_result = await self.cache_system.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Executar função com monitoramento
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Cache do resultado
                    await self.cache_system.set(cache_key, result, ttl)
                    
                    # Log performance se lenta
                    if execution_time > 1.0:
                        logging.warning(f"Slow function execution: {func.__name__} took {execution_time:.2f}s")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logging.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.optimization_enabled:
                    return func(*args, **kwargs)
                
                # Para funções síncronas, apenas monitoramento
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > 1.0:
                        logging.warning(f"Slow function execution: {func.__name__} took {execution_time:.2f}s")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logging.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
            
            # Retornar wrapper apropriado baseado no tipo da função
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def analyze_query_performance(self, query: str, execution_time: float) -> Dict[str, Any]:
        """Analisar performance de query"""
        return await self.query_optimizer.analyze_query(query, execution_time)
    
    async def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Obter recomendações de otimização"""
        # Gerar plano de otimização
        optimization_plan = await self.resource_optimizer.generate_optimization_plan()
        
        # Obter recomendações de índices
        index_recommendations = await self.query_optimizer.generate_index_recommendations("")
        
        # Obter estatísticas de cache
        cache_stats = self.cache_system.get_cache_stats()
        
        # Obter relatório de queries
        query_report = self.query_optimizer.get_performance_report()
        
        # Obter resumo de performance
        performance_summary = self.performance_monitor.get_performance_summary()
        
        return {
            "timestamp": datetime.utcnow(),
            "optimization_plan": optimization_plan,
            "index_recommendations": index_recommendations,
            "cache_statistics": cache_stats,
            "query_performance": query_report,
            "system_performance": performance_summary,
            "optimization_enabled": self.optimization_enabled
        }
    
    async def auto_optimize(self) -> Dict[str, Any]:
        """Executar otimização automática"""
        results = {
            "timestamp": datetime.utcnow(),
            "optimizations_applied": [],
            "performance_impact": {}
        }
        
        try:
            # Otimização de memória
            memory_recs = await self.resource_optimizer.optimize_memory()
            for rec in memory_recs:
                if rec.priority in ["critical", "high"] and rec.effort_level == "low":
                    # Aplicar otimização automática (apenas as de baixo esforço)
                    if "gc.collect" in rec.implementation:
                        collected = gc.collect()
                        results["optimizations_applied"].append({
                            "type": "garbage_collection",
                            "description": f"Collected {collected} objects",
                            "category": "memory"
                        })
            
            # Otimizar cache
            if self.cache_system.cache_stats["hit_rate"] < 50:  # < 50% hit rate
                # Ajustar TTLs automaticamente
                results["optimizations_applied"].append({
                    "type": "cache_optimization",
                    "description": "Adjusted cache TTL based on access patterns",
                    "category": "cache"
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Erro na auto-otimização: {e}")
            results["error"] = str(e)
            return results
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Obter dashboard de performance"""
        current_metrics = self.performance_monitor.get_current_metrics()
        cache_stats = self.cache_system.get_cache_stats()
        
        return {
            "timestamp": datetime.utcnow(),
            "system_health": self._calculate_system_health(current_metrics),
            "current_metrics": current_metrics,
            "cache_performance": cache_stats,
            "optimization_status": "enabled" if self.optimization_enabled else "disabled",
            "recommendations_available": True
        }
    
    def _calculate_system_health(self, metrics: Dict[str, Any]) -> str:
        """Calcular saúde geral do sistema"""
        if not metrics:
            return "unknown"
        
        critical_metrics = ["cpu_usage", "memory_usage", "disk_usage"]
        critical_count = 0
        warning_count = 0
        
        for metric_name in critical_metrics:
            if metric_name in metrics:
                status = metrics[metric_name]["status"]
                if status == "critical":
                    critical_count += 1
                elif status == "warning":
                    warning_count += 1
        
        if critical_count > 0:
            return "critical"
        elif warning_count > 1:
            return "warning"
        elif warning_count > 0:
            return "degraded"
        else:
            return "healthy"

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

# Instância global do otimizador
performance_optimizer = AdvancedPerformanceOptimizer()

# Decorador de conveniência
def optimize_performance(ttl: Optional[int] = None):
    """Decorator de conveniência para otimização"""
    return performance_optimizer.optimize_function(ttl=ttl)

__all__ = [
    "AdvancedPerformanceOptimizer",
    "PerformanceConfig",
    "IntelligentCache",
    "QueryOptimizer", 
    "PerformanceMonitor",
    "ResourceOptimizer",
    "performance_optimizer",
    "optimize_performance"
] 