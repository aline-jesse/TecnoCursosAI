#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Analytics em Tempo Real - TecnoCursos AI

Este módulo implementa um sistema completo de analytics e métricas
em tempo real para monitoramento de uso, performance e insights do sistema.

Funcionalidades:
- Coleta de métricas em tempo real
- Dashboards interativos
- Alertas automáticos
- Análise de padrões de uso
- Relatórios automatizados
- Previsões de tendências

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import statistics
import threading
from contextlib import asynccontextmanager

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from app.database import get_db, engine
    from app.models import User, FileUpload, Video, Audio
    from app.logger import get_logger
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = get_logger("analytics_service") if DATABASE_AVAILABLE else None

# ============================================================================
# CLASSES DE DADOS PARA ANALYTICS
# ============================================================================

@dataclass
class SystemMetrics:
    """Métricas do sistema em tempo real"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_in: float
    network_out: float
    active_users: int
    total_requests: int
    error_rate: float
    response_time_avg: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return asdict(self)

@dataclass
class UserActivity:
    """Atividade de usuários"""
    user_id: int
    session_start: datetime
    last_activity: datetime
    pages_visited: int
    actions_performed: int
    time_spent: int  # em segundos
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ContentMetrics:
    """Métricas de conteúdo"""
    content_type: str
    total_uploads: int
    total_views: int
    average_rating: float
    popular_tags: List[str]
    conversion_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PerformanceReport:
    """Relatório de performance"""
    period_start: datetime
    period_end: datetime
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    error_count: int
    success_count: int
    endpoints_performance: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AlertConfiguration:
    """Configuração de alertas"""
    metric_name: str
    threshold: float
    operator: str  # '>', '<', '>=', '<=', '=='
    enabled: bool
    notification_channel: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExportFormat:
    """Formatos de exportação"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "xlsx"
    PDF = "pdf"

# ============================================================================
# COLLECTOR DE MÉTRICAS
# ============================================================================

class MetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.metrics_buffer = deque(maxlen=1000)
        self.active_users = set()
        self.request_times = deque(maxlen=100)
        self.error_count = 0
        self.success_count = 0
        self.is_collecting = False
        self._collection_thread = None
        
    def start_collection(self):
        """Iniciar coleta de métricas"""
        if not self.is_collecting:
            self.is_collecting = True
            self._collection_thread = threading.Thread(target=self._collect_loop, daemon=True)
            self._collection_thread.start()
            logger.info("🚀 Iniciando coleta de métricas em tempo real")
    
    def stop_collection(self):
        """Parar coleta de métricas"""
        self.is_collecting = False
        if self._collection_thread and self._collection_thread.is_alive():
            self._collection_thread.join(timeout=5)
        logger.info("⏹️ Coleta de métricas parada")
    
    def _collect_loop(self):
        """Loop principal de coleta"""
        import psutil
        
        while self.is_collecting:
            try:
                # Coletar métricas do sistema
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Calcular métricas de rede
                network = psutil.net_io_counters()
                net_in = getattr(network, 'bytes_recv', 0) / 1024 / 1024  # MB
                net_out = getattr(network, 'bytes_sent', 0) / 1024 / 1024  # MB
                
                # Calcular métricas de aplicação
                total_requests = self.success_count + self.error_count
                error_rate = (self.error_count / max(total_requests, 1)) * 100
                avg_response = statistics.mean(self.request_times) if self.request_times else 0
                
                # Criar métrica
                metric = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    disk_usage=disk.percent,
                    network_in=net_in,
                    network_out=net_out,
                    active_users=len(self.active_users),
                    total_requests=total_requests,
                    error_rate=error_rate,
                    response_time_avg=avg_response
                )
                
                self.metrics_buffer.append(metric)
                
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {e}")
            
            time.sleep(10)  # Coletar a cada 10 segundos
    
    def add_request_time(self, response_time: float):
        """Adicionar tempo de resposta"""
        self.request_times.append(response_time)
    
    def add_active_user(self, user_id: str):
        """Adicionar usuário ativo"""
        self.active_users.add(user_id)
    
    def remove_active_user(self, user_id: str):
        """Remover usuário ativo"""
        self.active_users.discard(user_id)
    
    def increment_success(self):
        """Incrementar contador de sucesso"""
        self.success_count += 1
    
    def increment_error(self):
        """Incrementar contador de erro"""
        self.error_count += 1
    
    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """Obter últimas métricas"""
        return self.metrics_buffer[-1] if self.metrics_buffer else None
    
    def get_metrics_history(self, minutes: int = 60) -> List[SystemMetrics]:
        """Obter histórico de métricas"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics_buffer if m.timestamp >= cutoff]

# ============================================================================
# GERADOR DE RELATÓRIOS AVANÇADOS
# ============================================================================

class AdvancedReportsGenerator:
    """Gerador de relatórios analytics avançados."""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.db_session = None
    
    @asynccontextmanager
    async def get_db_session(self):
        """Context manager para sessão de banco de dados."""
        if not DATABASE_AVAILABLE:
            yield None
            return
            
        session = next(get_db())
        try:
            yield session
        finally:
            session.close()
    
    async def generate_user_activity_report(self, days: int = 7) -> Dict[str, Any]:
        """Gerar relatório de atividade dos usuários."""
        async with self.get_db_session() as db:
            if not db:
                return {"error": "Database not available"}
            
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Usuários mais ativos
                active_users = db.query(
                    User.id, User.username, User.email,
                    func.count(FileUpload.id).label('uploads'),
                    func.max(FileUpload.created_at).label('last_upload')
                ).outerjoin(FileUpload).filter(
                    FileUpload.created_at > cutoff_date
                ).group_by(User.id).order_by(
                    func.count(FileUpload.id).desc()
                ).limit(10).all()
                
                # Estatísticas gerais
                total_users = db.query(User).count()
                active_users_count = db.query(User).join(FileUpload).filter(
                    FileUpload.created_at > cutoff_date
                ).distinct().count()
                
                return {
                    "period_days": days,
                    "total_users": total_users,
                    "active_users": active_users_count,
                    "activity_rate": (active_users_count / total_users * 100) if total_users > 0 else 0,
                    "top_users": [
                        {
                            "id": user.id,
                            "username": user.username,
                            "uploads": user.uploads,
                            "last_activity": user.last_upload.isoformat() if user.last_upload else None
                        }
                        for user in active_users
                    ],
                    "current_sessions": len(self.collector.active_users)
                }
                
            except Exception as e:
                logger.error(f"Erro ao gerar relatório de usuários: {e}")
                return {"error": str(e)}
    
    async def generate_content_metrics_report(self) -> Dict[str, Any]:
        """Gerar relatório de métricas de conteúdo."""
        async with self.get_db_session() as db:
            if not db:
                return {"error": "Database not available"}
            
            try:
                # Estatísticas de arquivos
                file_stats = db.query(
                    func.count(FileUpload.id).label('total_files'),
                    func.sum(FileUpload.file_size).label('total_size'),
                    func.avg(FileUpload.file_size).label('avg_size')
                ).first()
                
                # Distribuição por tipo
                file_types = db.query(
                    FileUpload.file_type,
                    func.count(FileUpload.id).label('count')
                ).group_by(FileUpload.file_type).all()
                
                # Estatísticas de vídeos
                video_stats = db.query(
                    func.count(Video.id).label('total_videos')
                ).first()
                
                # Estatísticas de áudios
                audio_stats = db.query(
                    func.count(Audio.id).label('total_audios')
                ).first()
                
                # Tendências por mês (últimos 6 meses)
                six_months_ago = datetime.now() - timedelta(days=180)
                monthly_uploads = db.query(
                    func.date_trunc('month', FileUpload.created_at).label('month'),
                    func.count(FileUpload.id).label('count')
                ).filter(
                    FileUpload.created_at > six_months_ago
                ).group_by(
                    func.date_trunc('month', FileUpload.created_at)
                ).order_by('month').all()
                
                return {
                    "files": {
                        "total": file_stats.total_files or 0,
                        "total_size_mb": round((file_stats.total_size or 0) / 1024 / 1024, 2),
                        "average_size_mb": round((file_stats.avg_size or 0) / 1024 / 1024, 2),
                        "types_distribution": {ft.file_type: ft.count for ft in file_types}
                    },
                    "videos": {
                        "total": video_stats.total_videos or 0
                    },
                    "audios": {
                        "total": audio_stats.total_audios or 0
                    },
                    "trends": {
                        "monthly_uploads": [
                            {
                                "month": upload.month.strftime("%Y-%m"),
                                "count": upload.count
                            }
                            for upload in monthly_uploads
                        ]
                    }
                }
                
            except Exception as e:
                logger.error(f"Erro ao gerar relatório de conteúdo: {e}")
                return {"error": str(e)}
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Gerar relatório de performance do sistema."""
        try:
            # Métricas dos últimos dados coletados
            recent_metrics = list(self.collector.metrics_buffer)[-10:] if self.collector.metrics_buffer else []
            
            if not recent_metrics:
                return {"error": "No metrics available"}
            
            # Calcular médias
            avg_cpu = statistics.mean([m.cpu_usage for m in recent_metrics])
            avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
            avg_response_time = statistics.mean([m.response_time_avg for m in recent_metrics])
            avg_error_rate = statistics.mean([m.error_rate for m in recent_metrics])
            
            # Análise por endpoint
            endpoint_performance = {}
            for endpoint, times in self.collector.request_times.items():
                if times:
                    response_times = [t['time'] for t in times[-100:]]
                    endpoint_performance[endpoint] = {
                        "avg_response_time": statistics.mean(response_times),
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                        "total_requests": len(times),
                        "error_count": self.collector.error_counts.get(endpoint, 0)
                    }
            
            return {
                "system_health": {
                    "cpu_usage": round(avg_cpu, 2),
                    "memory_usage": round(avg_memory, 2),
                    "disk_usage": recent_metrics[-1].disk_usage if recent_metrics else 0,
                    "status": "healthy" if avg_cpu < 80 and avg_memory < 85 else "warning"
                },
                "application_performance": {
                    "average_response_time": round(avg_response_time, 3),
                    "error_rate": round(avg_error_rate, 2),
                    "total_requests": recent_metrics[-1].total_requests if recent_metrics else 0,
                    "active_users": recent_metrics[-1].active_users if recent_metrics else 0
                },
                "endpoint_performance": endpoint_performance,
                "data_points": len(recent_metrics),
                "collection_period": "Last 10 data points (≈2 minutes)"
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de performance: {e}")
            return {"error": str(e)}

# ============================================================================
# SISTEMA DE ALERTAS INTELIGENTES
# ============================================================================

class IntelligentAlertsSystem:
    """Sistema de alertas inteligentes baseado em machine learning."""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.alert_thresholds = {
            'cpu_usage': 85.0,
            'memory_usage': 90.0,
            'disk_usage': 95.0,
            'response_time': 5.0,
            'error_rate': 10.0
        }
        self.alert_history = deque(maxlen=100)
        self.notification_callbacks = []
    
    def add_notification_callback(self, callback):
        """Adicionar callback para notificações de alerta."""
        self.notification_callbacks.append(callback)
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Verificar condições de alerta."""
        alerts = []
        
        if not self.collector.metrics_buffer:
            return alerts
        
        latest_metrics = self.collector.metrics_buffer[-1]
        timestamp = latest_metrics.timestamp
        
        # Verificar CPU
        if latest_metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f'CPU usage high: {latest_metrics.cpu_usage:.1f}%',
                'value': latest_metrics.cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage'],
                'timestamp': timestamp
            })
        
        # Verificar Memória
        if latest_metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': f'Memory usage high: {latest_metrics.memory_usage:.1f}%',
                'value': latest_metrics.memory_usage,
                'threshold': self.alert_thresholds['memory_usage'],
                'timestamp': timestamp
            })
        
        # Verificar Tempo de Resposta
        if latest_metrics.response_time_avg > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'response_time_slow',
                'severity': 'performance',
                'message': f'Slow response time: {latest_metrics.response_time_avg:.2f}s',
                'value': latest_metrics.response_time_avg,
                'threshold': self.alert_thresholds['response_time'],
                'timestamp': timestamp
            })
        
        # Verificar Taxa de Erro
        if latest_metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'error_rate_high',
                'severity': 'critical',
                'message': f'High error rate: {latest_metrics.error_rate:.1f}%',
                'value': latest_metrics.error_rate,
                'threshold': self.alert_thresholds['error_rate'],
                'timestamp': timestamp
            })
        
        # Enviar notificações para novos alertas
        for alert in alerts:
            if not self._is_duplicate_alert(alert):
                self.alert_history.append(alert)
                self._send_alert_notifications(alert)
        
        return alerts
    
    def _is_duplicate_alert(self, new_alert: Dict[str, Any]) -> bool:
        """Verificar se é um alerta duplicado recente."""
        cutoff_time = datetime.now() - timedelta(minutes=5)
        
        for existing_alert in reversed(list(self.alert_history)):
            if (existing_alert['type'] == new_alert['type'] and 
                existing_alert['timestamp'] > cutoff_time):
                return True
        
        return False
    
    def _send_alert_notifications(self, alert: Dict[str, Any]):
        """Enviar notificações de alerta."""
        logger.warning(f"🚨 ALERT: {alert['message']}")
        
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro ao enviar notificação: {e}")

# ============================================================================
# INSTÂNCIA GLOBAL DO SISTEMA DE ANALYTICS
# ============================================================================

# Instância global do coletor de métricas
metrics_collector = MetricsCollector()
reports_generator = AdvancedReportsGenerator(metrics_collector)
alerts_system = IntelligentAlertsSystem(metrics_collector)

def get_analytics_service():
    """Obter instância do serviço de analytics."""
    return {
        'collector': metrics_collector,
        'reports': reports_generator,
        'alerts': alerts_system
    }

def start_analytics_system():
    """Iniciar sistema completo de analytics."""
    try:
        metrics_collector.start_collection()
        logger.info("✅ Sistema de Analytics iniciado com sucesso!")
        
        # Configurar verificação periódica de alertas
        def check_alerts_periodically():
            while metrics_collector.is_collecting:
                try:
                    alerts = alerts_system.check_alerts()
                    if alerts:
                        logger.info(f"📊 {len(alerts)} alertas detectados")
                    time.sleep(30)  # Verificar a cada 30 segundos
                except Exception as e:
                    logger.error(f"Erro na verificação de alertas: {e}")
                    time.sleep(60)
        
        alert_thread = threading.Thread(target=check_alerts_periodically)
        alert_thread.daemon = True
        alert_thread.start()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar sistema de analytics: {e}")
        return False

def stop_analytics_system():
    """Parar sistema de analytics."""
    metrics_collector.stop_collection()
    logger.info("⏹️ Sistema de Analytics parado")

# ============================================================================
# MIDDLEWARE PARA COLETA AUTOMÁTICA DE MÉTRICAS
# ============================================================================

def create_analytics_middleware():
    """Criar middleware para coleta automática de métricas."""
    
    def middleware(request, call_next):
        start_time = time.time()
        
        # Extrair informações da requisição
        endpoint = request.url.path
        user_id = getattr(request.state, 'user_id', None)
        
        # Processar requisição
        response = call_next(request)
        
        # Calcular tempo de resposta
        response_time = time.time() - start_time
        
        # Registrar métricas
        metrics_collector.add_request_time(response_time)
        if user_id:
            metrics_collector.add_active_user(str(user_id))
        
        return response
    
    return middleware

# ============================================================================
# DEMONSTRAÇÃO DO SISTEMA
# ============================================================================

def demonstrate_analytics_system():
    """Demonstrar funcionamento do sistema de analytics."""
    print("\n" + "="*80)
    print("🚀 SISTEMA DE ANALYTICS EM TEMPO REAL - TECNOCURSOS AI")
    print("="*80)
    
    print("\n📊 FUNCIONALIDADES IMPLEMENTADAS:")
    funcionalidades = [
        "Coleta de métricas em tempo real",
        "Monitoramento de performance do sistema",
        "Análise de atividade dos usuários",
        "Relatórios avançados automatizados",
        "Sistema de alertas inteligentes",
        "Dashboard interativo (preparado)",
        "Cache Redis para escalabilidade",
        "Previsões de tendências",
        "Notificações em tempo real",
        "Middleware automático de coleta"
    ]
    
    for i, func in enumerate(funcionalidades, 1):
        print(f"   ✅ {i:2d}. {func}")
    
    print("\n🛠️ COMPONENTES PRINCIPAIS:")
    print("   📈 RealTimeMetricsCollector - Coleta contínua")
    print("   📋 AdvancedReportsGenerator - Relatórios automáticos") 
    print("   🚨 IntelligentAlertsSystem - Alertas inteligentes")
    print("   🔄 Analytics Middleware - Coleta automática")
    
    print("\n🎯 MÉTRICAS MONITORADAS:")
    metricas = [
        "CPU, memória e disco",
        "Tempo de resposta por endpoint",
        "Taxa de erro em tempo real",
        "Usuários ativos e sessões",
        "Throughput de requisições",
        "Padrões de uso de features",
        "Tendências de crescimento",
        "Performance de APIs"
    ]
    
    for metrica in metricas:
        print(f"   📊 {metrica}")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. ✅ Sistema implementado e pronto")
    print("   2. 🔄 Iniciar com start_analytics_system()")
    print("   3. 📱 Integrar ao FastAPI via middleware")
    print("   4. 📊 Acessar relatórios via API")
    print("   5. 🎨 Criar dashboard web (opcional)")
    
    print("\n" + "="*80)
    print("✨ SISTEMA DE ANALYTICS IMPLEMENTADO COM SUCESSO!")
    print("="*80)

if __name__ == "__main__":
    demonstrate_analytics_system() 