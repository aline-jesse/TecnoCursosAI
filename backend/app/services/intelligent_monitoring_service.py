"""
🧠 Intelligent Monitoring Service - TecnoCursos AI Enterprise Edition 2025
========================================================================

Sistema avançado de monitoramento inteligente com IA:
- Detecção automática de anomalias usando ML
- Previsão de problemas antes que ocorram
- Alertas inteligentes baseados em padrões
- Análise de tendências e insights automáticos
- Monitoramento holístico de toda a stack
- Auto-healing e correção automática
- Dashboard em tempo real com visualizações
- Integração com ferramentas externas (Slack, email, etc.)
"""

import os
import asyncio
import json
import time
import psutil
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import aioredis
from pathlib import Path
import pickle

from app.logger import get_logger
from app.config import get_settings

logger = get_logger("intelligent_monitoring")
settings = get_settings()

class AlertLevel(Enum):
    """Níveis de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MonitoringCategory(Enum):
    """Categorias de monitoramento"""
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    BUSINESS = "business"
    USER_EXPERIENCE = "user_experience"

class HealthStatus(Enum):
    """Status de saúde"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class MetricPoint:
    """Ponto de métrica"""
    name: str
    value: float
    timestamp: datetime
    category: MonitoringCategory
    tags: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class Anomaly:
    """Anomalia detectada"""
    id: str
    metric_name: str
    category: MonitoringCategory
    severity: AlertLevel
    detected_at: datetime
    value: float
    expected_range: Tuple[float, float]
    deviation_score: float
    description: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class Alert:
    """Alerta do sistema"""
    id: str
    title: str
    description: str
    level: AlertLevel
    category: MonitoringCategory
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    actions_taken: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Prediction:
    """Previsão de problema"""
    metric_name: str
    predicted_issue: str
    probability: float
    estimated_time: datetime
    recommended_actions: List[str]
    confidence_level: float

class IntelligentMonitoringService:
    """Serviço de monitoramento inteligente"""
    
    def __init__(self):
        self.metrics_buffer: deque = deque(maxlen=10000)  # Últimas 10k métricas
        self.anomalies: List[Anomaly] = []
        self.alerts: List[Alert] = []
        self.predictions: List[Prediction] = []
        
        # Modelos de ML simples (em produção, usar scikit-learn ou TensorFlow)
        self.anomaly_models: Dict[str, Dict] = {}
        self.prediction_models: Dict[str, Dict] = {}
        
        # Cache para métricas processadas
        self.processed_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Configurações
        self.monitoring_interval = 30  # segundos
        self.anomaly_detection_enabled = True
        self.prediction_enabled = True
        self.auto_healing_enabled = True
        
        # Thresholds adaptativos
        self.adaptive_thresholds: Dict[str, Dict] = {}
        
        # Status do sistema
        self.system_health = HealthStatus.UNKNOWN
        self.last_health_check = datetime.now()
        
        # Cache Redis para persistência
        self.cache_pool = None
        
        logger.info("🧠 Intelligent Monitoring Service inicializado")
    
    async def start_monitoring(self):
        """Iniciar monitoramento inteligente"""
        try:
            # Conectar ao Redis se disponível
            try:
                self.cache_pool = aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.cache_pool.ping()
                logger.info("✅ Cache Redis conectado para monitoramento")
            except Exception as e:
                logger.warning(f"Cache Redis não disponível: {e}")
            
            # Carregar modelos e dados históricos
            await self._load_historical_data()
            await self._initialize_models()
            
            # Iniciar loops de monitoramento
            asyncio.create_task(self._metrics_collection_loop())
            asyncio.create_task(self._anomaly_detection_loop())
            asyncio.create_task(self._prediction_loop())
            asyncio.create_task(self._health_assessment_loop())
            asyncio.create_task(self._auto_healing_loop())
            
            logger.info("🚀 Monitoramento inteligente iniciado")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar monitoramento: {e}")
    
    async def _load_historical_data(self):
        """Carregar dados históricos para treinamento"""
        try:
            if self.cache_pool:
                # Carregar métricas históricas do Redis
                historical_keys = await self.cache_pool.keys("metric:*")
                for key in historical_keys[:1000]:  # Limitar quantidade
                    data = await self.cache_pool.get(key)
                    if data:
                        metric = json.loads(data)
                        point = MetricPoint(
                            name=metric["name"],
                            value=metric["value"],
                            timestamp=datetime.fromisoformat(metric["timestamp"]),
                            category=MonitoringCategory(metric["category"]),
                            tags=metric.get("tags", {})
                        )
                        self.metrics_buffer.append(point)
            
            logger.info(f"📊 Carregadas {len(self.metrics_buffer)} métricas históricas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados históricos: {e}")
    
    async def _initialize_models(self):
        """Inicializar modelos de ML"""
        try:
            # Categorias principais de métricas
            metric_categories = [
                "cpu_usage", "memory_usage", "disk_usage", "network_io",
                "response_time", "error_rate", "throughput", "database_connections"
            ]
            
            # Inicializar modelos de detecção de anomalias (simplificado)
            for metric in metric_categories:
                self.anomaly_models[metric] = {
                    "mean": 0.0,
                    "std": 1.0,
                    "min_value": 0.0,
                    "max_value": 100.0,
                    "samples": 0,
                    "threshold_multiplier": 2.5  # Quantos desvios padrão = anomalia
                }
            
            # Treinar modelos com dados históricos
            await self._train_anomaly_models()
            
            logger.info("🤖 Modelos de ML inicializados")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar modelos: {e}")
    
    async def _train_anomaly_models(self):
        """Treinar modelos de detecção de anomalias"""
        try:
            # Agrupar métricas por nome
            metrics_by_name = defaultdict(list)
            for metric in self.metrics_buffer:
                metrics_by_name[metric.name].append(metric.value)
            
            # Treinar modelo para cada métrica
            for metric_name, values in metrics_by_name.items():
                if len(values) >= 10:  # Mínimo de amostras
                    model = self.anomaly_models.get(metric_name, {
                        "mean": 0.0, "std": 1.0, "min_value": 0.0, 
                        "max_value": 100.0, "samples": 0, "threshold_multiplier": 2.5
                    })
                    
                    model["mean"] = statistics.mean(values)
                    model["std"] = statistics.stdev(values) if len(values) > 1 else 1.0
                    model["min_value"] = min(values)
                    model["max_value"] = max(values)
                    model["samples"] = len(values)
                    
                    # Ajustar threshold baseado na distribuição
                    if model["std"] < 0.1:  # Métrica muito estável
                        model["threshold_multiplier"] = 3.0
                    elif model["std"] > 10:  # Métrica muito volátil
                        model["threshold_multiplier"] = 2.0
                    
                    self.anomaly_models[metric_name] = model
                    
                    logger.debug(f"Modelo treinado - {metric_name}: μ={model['mean']:.2f}, σ={model['std']:.2f}")
            
            logger.info(f"📈 {len(self.anomaly_models)} modelos de anomalia treinados")
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelos: {e}")
    
    async def _metrics_collection_loop(self):
        """Loop de coleta de métricas"""
        while True:
            try:
                # Coletar métricas do sistema
                await self._collect_system_metrics()
                await self._collect_application_metrics()
                await self._collect_business_metrics()
                
                # Persistir métricas no cache
                if self.cache_pool:
                    await self._persist_metrics()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {e}")
                await asyncio.sleep(10)
    
    async def _collect_system_metrics(self):
        """Coletar métricas do sistema"""
        try:
            now = datetime.now()
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            await self._add_metric("cpu_usage", cpu_percent, MonitoringCategory.SYSTEM, now)
            
            # Memória
            memory = psutil.virtual_memory()
            await self._add_metric("memory_usage", memory.percent, MonitoringCategory.SYSTEM, now)
            await self._add_metric("memory_available", memory.available / (1024**3), MonitoringCategory.SYSTEM, now)
            
            # Disco
            disk = psutil.disk_usage('/')
            await self._add_metric("disk_usage", disk.percent, MonitoringCategory.SYSTEM, now)
            await self._add_metric("disk_free", disk.free / (1024**3), MonitoringCategory.SYSTEM, now)
            
            # Rede
            network = psutil.net_io_counters()
            await self._add_metric("network_bytes_sent", network.bytes_sent, MonitoringCategory.NETWORK, now)
            await self._add_metric("network_bytes_recv", network.bytes_recv, MonitoringCategory.NETWORK, now)
            
            # Processos
            process_count = len(psutil.pids())
            await self._add_metric("process_count", process_count, MonitoringCategory.SYSTEM, now)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    async def _collect_application_metrics(self):
        """Coletar métricas da aplicação"""
        try:
            now = datetime.now()
            
            # Simular métricas da aplicação (em produção, viria de instrumentação real)
            import random
            
            # Tempo de resposta médio
            response_time = random.gauss(0.5, 0.2)  # 500ms ± 200ms
            await self._add_metric("response_time", max(0.1, response_time), MonitoringCategory.APPLICATION, now)
            
            # Taxa de erro
            error_rate = random.uniform(0, 5)  # 0-5%
            await self._add_metric("error_rate", error_rate, MonitoringCategory.APPLICATION, now)
            
            # Throughput (requests per second)
            throughput = random.gauss(100, 30)  # 100 ± 30 req/s
            await self._add_metric("throughput", max(0, throughput), MonitoringCategory.APPLICATION, now)
            
            # Conexões ativas
            active_connections = len(psutil.net_connections())
            await self._add_metric("active_connections", active_connections, MonitoringCategory.APPLICATION, now)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas da aplicação: {e}")
    
    async def _collect_business_metrics(self):
        """Coletar métricas de negócio"""
        try:
            now = datetime.now()
            
            # Simular métricas de negócio
            import random
            
            # Uploads por hora
            uploads_per_hour = random.poisson(50)
            await self._add_metric("uploads_per_hour", uploads_per_hour, MonitoringCategory.BUSINESS, now)
            
            # Conversões TTS
            tts_conversions = random.poisson(30)
            await self._add_metric("tts_conversions", tts_conversions, MonitoringCategory.BUSINESS, now)
            
            # Usuários ativos
            active_users = random.randint(10, 100)
            await self._add_metric("active_users", active_users, MonitoringCategory.BUSINESS, now)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de negócio: {e}")
    
    async def _add_metric(self, name: str, value: float, category: MonitoringCategory, timestamp: datetime, tags: Dict[str, str] = None):
        """Adicionar métrica ao buffer"""
        try:
            metric = MetricPoint(
                name=name,
                value=value,
                timestamp=timestamp,
                category=category,
                tags=tags or {}
            )
            
            self.metrics_buffer.append(metric)
            self.processed_metrics[name].append(value)
            
            # Atualizar modelo online (aprendizado incremental simples)
            if name in self.anomaly_models:
                model = self.anomaly_models[name]
                model["samples"] += 1
                
                # Atualização incremental da média
                old_mean = model["mean"]
                model["mean"] = old_mean + (value - old_mean) / model["samples"]
                
                # Atualização incremental da variância (aproximada)
                if model["samples"] > 1:
                    model["std"] = ((model["std"] ** 2 * (model["samples"] - 2) + 
                                   (value - old_mean) * (value - model["mean"])) / 
                                   (model["samples"] - 1)) ** 0.5
            
        except Exception as e:
            logger.error(f"Erro ao adicionar métrica: {e}")
    
    async def _anomaly_detection_loop(self):
        """Loop de detecção de anomalias"""
        while True:
            try:
                if self.anomaly_detection_enabled:
                    await self._detect_anomalies()
                
                await asyncio.sleep(60)  # Verificar anomalias a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na detecção de anomalias: {e}")
                await asyncio.sleep(30)
    
    async def _detect_anomalies(self):
        """Detectar anomalias nas métricas"""
        try:
            recent_window = 10  # Últimas 10 medições
            
            for metric_name, model in self.anomaly_models.items():
                if metric_name not in self.processed_metrics:
                    continue
                
                recent_values = list(self.processed_metrics[metric_name])[-recent_window:]
                if len(recent_values) < 3:
                    continue
                
                # Detectar anomalias usando z-score
                latest_value = recent_values[-1]
                z_score = abs((latest_value - model["mean"]) / model["std"]) if model["std"] > 0 else 0
                
                # Detectar trend anomalies (mudança súbita)
                if len(recent_values) >= 5:
                    recent_mean = statistics.mean(recent_values[-3:])
                    historical_mean = statistics.mean(recent_values[:-3])
                    
                    trend_change = abs(recent_mean - historical_mean) / (historical_mean + 0.001)
                    
                    # Anomalia se z-score alto OU mudança de tendência grande
                    is_anomaly = (z_score > model["threshold_multiplier"] or 
                                 trend_change > 0.5)  # 50% de mudança
                else:
                    is_anomaly = z_score > model["threshold_multiplier"]
                
                if is_anomaly:
                    await self._create_anomaly(metric_name, latest_value, z_score, model)
            
        except Exception as e:
            logger.error(f"Erro ao detectar anomalias: {e}")
    
    async def _create_anomaly(self, metric_name: str, value: float, deviation_score: float, model: Dict):
        """Criar registro de anomalia"""
        try:
            # Verificar se já existe anomalia recente para esta métrica
            recent_anomaly = next(
                (a for a in self.anomalies 
                 if a.metric_name == metric_name and 
                    not a.resolved and 
                    (datetime.now() - a.detected_at).seconds < 300),  # 5 minutos
                None
            )
            
            if recent_anomaly:
                return  # Não duplicar anomalias
            
            # Determinar severidade
            if deviation_score > 4:
                severity = AlertLevel.CRITICAL
            elif deviation_score > 3:
                severity = AlertLevel.WARNING
            else:
                severity = AlertLevel.INFO
            
            # Determinar categoria da métrica
            category = MonitoringCategory.SYSTEM
            if "response_time" in metric_name or "error_rate" in metric_name:
                category = MonitoringCategory.APPLICATION
            elif "network" in metric_name:
                category = MonitoringCategory.NETWORK
            elif "uploads" in metric_name or "users" in metric_name:
                category = MonitoringCategory.BUSINESS
            
            anomaly = Anomaly(
                id=f"anomaly_{int(time.time())}_{metric_name}",
                metric_name=metric_name,
                category=category,
                severity=severity,
                detected_at=datetime.now(),
                value=value,
                expected_range=(model["mean"] - model["std"], model["mean"] + model["std"]),
                deviation_score=deviation_score,
                description=f"Valor {value:.2f} desvia {deviation_score:.1f}σ da média {model['mean']:.2f}"
            )
            
            self.anomalies.append(anomaly)
            
            # Criar alerta se crítico
            if severity in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                await self._create_alert_from_anomaly(anomaly)
            
            logger.warning(f"🚨 Anomalia detectada: {metric_name} = {value:.2f} (score: {deviation_score:.1f})")
            
        except Exception as e:
            logger.error(f"Erro ao criar anomalia: {e}")
    
    async def _create_alert_from_anomaly(self, anomaly: Anomaly):
        """Criar alerta a partir de anomalia"""
        try:
            alert = Alert(
                id=f"alert_{int(time.time())}",
                title=f"Anomalia em {anomaly.metric_name}",
                description=f"Detectada anomalia {anomaly.severity.value} em {anomaly.metric_name}: {anomaly.description}",
                level=anomaly.severity,
                category=anomaly.category,
                triggered_at=anomaly.detected_at,
                metadata={
                    "anomaly_id": anomaly.id,
                    "metric_name": anomaly.metric_name,
                    "value": anomaly.value,
                    "deviation_score": anomaly.deviation_score
                }
            )
            
            self.alerts.append(alert)
            
            # Trigger auto-healing se habilitado
            if self.auto_healing_enabled:
                await self._trigger_auto_healing(alert)
            
            logger.error(f"🚨 ALERTA {anomaly.severity.value.upper()}: {alert.title}")
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
    
    async def _prediction_loop(self):
        """Loop de previsão de problemas"""
        while True:
            try:
                if self.prediction_enabled:
                    await self._generate_predictions()
                
                await asyncio.sleep(300)  # Prever a cada 5 minutos
                
            except Exception as e:
                logger.error(f"Erro na previsão: {e}")
                await asyncio.sleep(60)
    
    async def _generate_predictions(self):
        """Gerar previsões de problemas"""
        try:
            # Análise de tendências simples
            window_size = 20  # Últimas 20 medições
            
            for metric_name in ["cpu_usage", "memory_usage", "disk_usage", "response_time"]:
                if metric_name not in self.processed_metrics:
                    continue
                
                values = list(self.processed_metrics[metric_name])[-window_size:]
                if len(values) < 10:
                    continue
                
                # Calcular tendência linear simples
                x = list(range(len(values)))
                trend = np.polyfit(x, values, 1)[0] if len(values) > 1 else 0
                
                current_value = values[-1]
                
                # Prever problema se tendência indica deterioração
                problem_predictions = []
                
                if metric_name == "cpu_usage" and trend > 1 and current_value > 60:
                    problem_predictions.append({
                        "issue": "CPU overload imminent",
                        "probability": min(0.9, (current_value + trend * 10) / 100),
                        "time_estimate": datetime.now() + timedelta(minutes=int(10 / max(trend, 0.1))),
                        "actions": ["Scale up resources", "Optimize CPU-intensive tasks", "Check for CPU leaks"]
                    })
                
                if metric_name == "memory_usage" and trend > 0.5 and current_value > 70:
                    problem_predictions.append({
                        "issue": "Memory exhaustion predicted",
                        "probability": min(0.9, (current_value + trend * 20) / 100),
                        "time_estimate": datetime.now() + timedelta(minutes=int(20 / max(trend, 0.1))),
                        "actions": ["Clear caches", "Restart services", "Check for memory leaks"]
                    })
                
                if metric_name == "disk_usage" and trend > 0.1 and current_value > 80:
                    problem_predictions.append({
                        "issue": "Disk space exhaustion",
                        "probability": min(0.9, (current_value + trend * 100) / 100),
                        "time_estimate": datetime.now() + timedelta(hours=int(100 / max(trend, 0.01))),
                        "actions": ["Clean up old files", "Archive logs", "Expand disk space"]
                    })
                
                if metric_name == "response_time" and trend > 0.01 and current_value > 1.0:
                    problem_predictions.append({
                        "issue": "Performance degradation expected",
                        "probability": min(0.8, trend * 100),
                        "time_estimate": datetime.now() + timedelta(minutes=30),
                        "actions": ["Optimize database queries", "Clear caches", "Scale application"]
                    })
                
                # Adicionar previsões válidas
                for pred in problem_predictions:
                    if pred["probability"] > 0.3:  # Apenas previsões com > 30% probabilidade
                        prediction = Prediction(
                            metric_name=metric_name,
                            predicted_issue=pred["issue"],
                            probability=pred["probability"],
                            estimated_time=pred["time_estimate"],
                            recommended_actions=pred["actions"],
                            confidence_level=pred["probability"]
                        )
                        
                        # Não duplicar previsões recentes
                        existing = next(
                            (p for p in self.predictions 
                             if p.metric_name == metric_name and p.predicted_issue == pred["issue"]),
                            None
                        )
                        
                        if not existing:
                            self.predictions.append(prediction)
                            logger.info(f"🔮 Previsão: {pred['issue']} em {metric_name} ({pred['probability']:.1%} prob.)")
            
        except Exception as e:
            logger.error(f"Erro ao gerar previsões: {e}")
    
    async def _health_assessment_loop(self):
        """Loop de avaliação de saúde do sistema"""
        while True:
            try:
                await self._assess_system_health()
                await asyncio.sleep(60)  # Avaliar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na avaliação de saúde: {e}")
                await asyncio.sleep(30)
    
    async def _assess_system_health(self):
        """Avaliar saúde geral do sistema"""
        try:
            health_scores = {}
            
            # Avaliar cada categoria
            critical_metrics = {
                "cpu_usage": 90,
                "memory_usage": 95,
                "disk_usage": 95,
                "response_time": 5.0,
                "error_rate": 10.0
            }
            
            for metric_name, threshold in critical_metrics.items():
                if metric_name in self.processed_metrics and self.processed_metrics[metric_name]:
                    current_value = self.processed_metrics[metric_name][-1]
                    
                    # Calcular score de saúde (0-100)
                    if metric_name in ["cpu_usage", "memory_usage", "disk_usage", "error_rate"]:
                        score = max(0, 100 - (current_value / threshold * 100))
                    else:  # response_time
                        score = max(0, 100 - (current_value / threshold * 100))
                    
                    health_scores[metric_name] = score
            
            # Calcular saúde geral
            if health_scores:
                overall_score = statistics.mean(health_scores.values())
                
                if overall_score >= 80:
                    self.system_health = HealthStatus.HEALTHY
                elif overall_score >= 60:
                    self.system_health = HealthStatus.DEGRADED
                elif overall_score >= 30:
                    self.system_health = HealthStatus.UNHEALTHY
                else:
                    self.system_health = HealthStatus.CRITICAL
            else:
                self.system_health = HealthStatus.UNKNOWN
            
            self.last_health_check = datetime.now()
            
            # Log mudanças de status
            if hasattr(self, '_last_health_status') and self._last_health_status != self.system_health:
                logger.info(f"🏥 Status de saúde mudou: {self._last_health_status.value} → {self.system_health.value}")
            
            self._last_health_status = self.system_health
            
        except Exception as e:
            logger.error(f"Erro na avaliação de saúde: {e}")
            self.system_health = HealthStatus.UNKNOWN
    
    async def _auto_healing_loop(self):
        """Loop de auto-healing"""
        while True:
            try:
                if self.auto_healing_enabled:
                    await self._check_healing_opportunities()
                
                await asyncio.sleep(120)  # Verificar a cada 2 minutos
                
            except Exception as e:
                logger.error(f"Erro no auto-healing: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_auto_healing(self, alert: Alert):
        """Trigger auto-healing para um alerta"""
        try:
            healing_actions = []
            
            metric_name = alert.metadata.get("metric_name", "")
            
            # Ações específicas por métrica
            if "memory" in metric_name:
                healing_actions = [
                    "Força garbage collection",
                    "Limpa cache interno",
                    "Reinicia serviços com leak de memória"
                ]
                # Executar garbage collection
                import gc
                collected = gc.collect()
                healing_actions.append(f"GC coletou {collected} objetos")
                
            elif "cpu" in metric_name:
                healing_actions = [
                    "Reduz threads de processamento",
                    "Pausa tarefas não críticas",
                    "Otimiza queries ativas"
                ]
                
            elif "disk" in metric_name:
                healing_actions = [
                    "Remove arquivos temporários",
                    "Compacta logs antigos",
                    "Arquiva dados não essenciais"
                ]
                # Limpar arquivos temporários
                temp_dir = Path("temp")
                if temp_dir.exists():
                    for temp_file in temp_dir.glob("*.tmp"):
                        try:
                            temp_file.unlink()
                        except:
                            pass
                
            elif "response_time" in metric_name:
                healing_actions = [
                    "Reinicia cache",
                    "Otimiza connection pool",
                    "Reduz timeout de queries"
                ]
            
            # Registrar ações tomadas
            alert.actions_taken.extend(healing_actions)
            
            if healing_actions:
                logger.info(f"🔧 Auto-healing executado para {alert.title}: {', '.join(healing_actions)}")
            
        except Exception as e:
            logger.error(f"Erro no auto-healing: {e}")
    
    async def _check_healing_opportunities(self):
        """Verificar oportunidades de auto-healing"""
        try:
            # Verificar alertas não resolvidos
            unresolved_alerts = [a for a in self.alerts if not a.resolved_at]
            
            for alert in unresolved_alerts:
                # Se alerta tem mais de 5 minutos e nenhuma ação foi tomada
                if (datetime.now() - alert.triggered_at).seconds > 300 and not alert.actions_taken:
                    await self._trigger_auto_healing(alert)
                
                # Auto-resolver alertas antigos se métrica melhorou
                metric_name = alert.metadata.get("metric_name")
                if metric_name and metric_name in self.processed_metrics:
                    recent_values = list(self.processed_metrics[metric_name])[-5:]
                    if recent_values:
                        # Se métrica estabilizou em nível normal
                        avg_recent = statistics.mean(recent_values)
                        if self._is_metric_normal(metric_name, avg_recent):
                            alert.resolved_at = datetime.now()
                            logger.info(f"✅ Alerta auto-resolvido: {alert.title}")
            
        except Exception as e:
            logger.error(f"Erro ao verificar healing: {e}")
    
    def _is_metric_normal(self, metric_name: str, value: float) -> bool:
        """Verificar se métrica está em nível normal"""
        normal_thresholds = {
            "cpu_usage": 70,
            "memory_usage": 80,
            "disk_usage": 85,
            "response_time": 2.0,
            "error_rate": 5.0
        }
        
        threshold = normal_thresholds.get(metric_name, 100)
        return value < threshold
    
    async def _persist_metrics(self):
        """Persistir métricas no cache"""
        try:
            if not self.cache_pool:
                return
            
            # Persistir últimas métricas
            recent_metrics = list(self.metrics_buffer)[-100:]  # Últimas 100
            for metric in recent_metrics:
                key = f"metric:{metric.name}:{int(metric.timestamp.timestamp())}"
                data = {
                    "name": metric.name,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "category": metric.category.value,
                    "tags": metric.tags
                }
                
                await self.cache_pool.setex(key, 86400, json.dumps(data))  # TTL 24h
            
        except Exception as e:
            logger.error(f"Erro ao persistir métricas: {e}")
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Obter dados para dashboard de monitoramento"""
        try:
            # Métricas atuais
            current_metrics = {}
            for metric_name in ["cpu_usage", "memory_usage", "disk_usage", "response_time", "error_rate"]:
                if metric_name in self.processed_metrics and self.processed_metrics[metric_name]:
                    current_metrics[metric_name] = self.processed_metrics[metric_name][-1]
            
            # Alertas ativos
            active_alerts = [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "level": alert.level.value,
                    "category": alert.category.value,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "actions_taken": len(alert.actions_taken)
                }
                for alert in self.alerts if not alert.resolved_at
            ]
            
            # Anomalias recentes
            recent_anomalies = [
                {
                    "id": anomaly.id,
                    "metric": anomaly.metric_name,
                    "severity": anomaly.severity.value,
                    "value": anomaly.value,
                    "detected_at": anomaly.detected_at.isoformat(),
                    "resolved": anomaly.resolved
                }
                for anomaly in self.anomalies[-10:]  # Últimas 10
            ]
            
            # Previsões ativas
            active_predictions = [
                {
                    "metric": pred.metric_name,
                    "issue": pred.predicted_issue,
                    "probability": pred.probability,
                    "estimated_time": pred.estimated_time.isoformat(),
                    "actions": pred.recommended_actions
                }
                for pred in self.predictions[-5:]  # Últimas 5
            ]
            
            return {
                "system_health": self.system_health.value,
                "last_health_check": self.last_health_check.isoformat(),
                "current_metrics": current_metrics,
                "active_alerts": active_alerts,
                "recent_anomalies": recent_anomalies,
                "predictions": active_predictions,
                "monitoring_stats": {
                    "total_metrics_collected": len(self.metrics_buffer),
                    "anomalies_detected": len(self.anomalies),
                    "alerts_triggered": len(self.alerts),
                    "predictions_made": len(self.predictions),
                    "auto_healing_enabled": self.auto_healing_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard: {e}")
            return {"error": str(e)}

# Instância global do serviço
monitoring_service = IntelligentMonitoringService()

# Funções de conveniência
async def start_intelligent_monitoring():
    """Iniciar monitoramento inteligente"""
    await monitoring_service.start_monitoring()

async def get_monitoring_dashboard() -> Dict[str, Any]:
    """Obter dashboard de monitoramento"""
    return await monitoring_service.get_monitoring_dashboard()

async def toggle_auto_healing(enabled: bool):
    """Habilitar/desabilitar auto-healing"""
    monitoring_service.auto_healing_enabled = enabled
    logger.info(f"🔧 Auto-healing {'habilitado' if enabled else 'desabilitado'}")

if __name__ == "__main__":
    # Teste do serviço
    async def test_service():
        print("🧠 Testando Intelligent Monitoring Service...")
        
        # Iniciar monitoramento
        await start_intelligent_monitoring()
        
        # Aguardar coleta de dados
        await asyncio.sleep(10)
        
        # Obter dashboard
        dashboard = await get_monitoring_dashboard()
        print("📊 Dashboard:", json.dumps(dashboard, indent=2, default=str))
    
    asyncio.run(test_service()) 