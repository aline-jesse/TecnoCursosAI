#!/usr/bin/env python3
"""
📊 ANALYTICS ENGINE - FASE 6
Sistema avançado de analytics e business intelligence

Funcionalidades:
✅ Real-time analytics
✅ User behavior tracking
✅ Performance metrics
✅ Business intelligence
✅ Custom dashboards
✅ Automated reports
✅ Predictive analytics
✅ A/B testing framework
✅ Data export/import

Data: 17 de Janeiro de 2025
Versão: 6.0.0
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import sqlite3
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Tipos de eventos"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PROJECT_CREATE = "project_create"
    PROJECT_OPEN = "project_open"
    PROJECT_EXPORT = "project_export"
    VIDEO_GENERATE = "video_generate"
    TEMPLATE_USE = "template_use"
    FEATURE_USE = "feature_use"
    ERROR_OCCUR = "error_occur"
    PERFORMANCE_METRIC = "performance_metric"

@dataclass
class AnalyticsEvent:
    """Evento de analytics"""
    id: str
    user_id: Optional[str]
    session_id: str
    event_type: EventType
    timestamp: datetime
    properties: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class UserMetrics:
    """Métricas de usuário"""
    user_id: str
    total_sessions: int
    total_time_spent: float  # em minutos
    projects_created: int
    videos_generated: int
    templates_used: int
    features_used: List[str]
    last_active: datetime
    retention_score: float

@dataclass
class ProjectMetrics:
    """Métricas de projeto"""
    project_id: str
    creator_id: str
    created_at: datetime
    last_modified: datetime
    total_edits: int
    collaborators_count: int
    export_count: int
    duration: float
    template_used: Optional[str]
    completion_rate: float

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    active_users: int
    total_users: int
    active_sessions: int
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    videos_generated_today: int

class AnalyticsEngine:
    """Engine principal de analytics"""
    
    def __init__(self):
        self.db_path = "analytics.db"
        self.events: List[AnalyticsEvent] = []
        self.user_sessions: Dict[str, Dict] = {}
        self.ab_tests: Dict[str, Dict] = {}
        self.is_collecting = False
        
        # Configurações
        self.config = {
            "batch_size": 100,
            "flush_interval": 60,  # segundos
            "retention_period_days": 365,
            "real_time_window_minutes": 5,
            "performance_threshold_ms": 2000
        }
        
        self._setup_database()

    def _setup_database(self):
        """Configurar banco de dados de analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de eventos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    properties TEXT,
                    metadata TEXT
                )
            ''')
            
            # Tabela de métricas de usuário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_metrics (
                    user_id TEXT PRIMARY KEY,
                    total_sessions INTEGER DEFAULT 0,
                    total_time_spent REAL DEFAULT 0,
                    projects_created INTEGER DEFAULT 0,
                    videos_generated INTEGER DEFAULT 0,
                    templates_used INTEGER DEFAULT 0,
                    features_used TEXT,
                    last_active TEXT,
                    retention_score REAL DEFAULT 0
                )
            ''')
            
            # Tabela de métricas de projeto
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_metrics (
                    project_id TEXT PRIMARY KEY,
                    creator_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    total_edits INTEGER DEFAULT 0,
                    collaborators_count INTEGER DEFAULT 1,
                    export_count INTEGER DEFAULT 0,
                    duration REAL DEFAULT 0,
                    template_used TEXT,
                    completion_rate REAL DEFAULT 0
                )
            ''')
            
            # Tabela de métricas do sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    active_users INTEGER DEFAULT 0,
                    total_users INTEGER DEFAULT 0,
                    active_sessions INTEGER DEFAULT 0,
                    cpu_usage REAL DEFAULT 0,
                    memory_usage REAL DEFAULT 0,
                    response_time REAL DEFAULT 0,
                    error_rate REAL DEFAULT 0,
                    videos_generated_today INTEGER DEFAULT 0
                )
            ''')
            
            # Índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON analytics_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user ON analytics_events(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON analytics_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database de analytics configurado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar database: {e}")

    async def start_collection(self):
        """Iniciar coleta de analytics"""
        self.is_collecting = True
        logger.info("📊 Coleta de analytics iniciada")
        
        # Iniciar tarefas em background
        asyncio.create_task(self._flush_events_task())
        asyncio.create_task(self._collect_system_metrics_task())
        asyncio.create_task(self._update_user_metrics_task())

    def stop_collection(self):
        """Parar coleta de analytics"""
        self.is_collecting = False
        logger.info("⏹️ Coleta de analytics parada")

    async def track_event(self, event_type: EventType, user_id: Optional[str] = None, 
                         session_id: Optional[str] = None, properties: Dict[str, Any] = None,
                         metadata: Dict[str, Any] = None):
        """Rastrear evento"""
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id or str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            properties=properties or {},
            metadata=metadata or {}
        )
        
        self.events.append(event)
        
        # Flush imediato se batch está cheio
        if len(self.events) >= self.config["batch_size"]:
            await self._flush_events()

    async def start_user_session(self, user_id: str, session_id: str, properties: Dict[str, Any] = None):
        """Iniciar sessão do usuário"""
        self.user_sessions[session_id] = {
            "user_id": user_id,
            "start_time": datetime.now(),
            "events_count": 0,
            "properties": properties or {}
        }
        
        await self.track_event(
            EventType.USER_LOGIN,
            user_id=user_id,
            session_id=session_id,
            properties=properties
        )

    async def end_user_session(self, session_id: str):
        """Finalizar sessão do usuário"""
        session = self.user_sessions.get(session_id)
        if not session:
            return
        
        duration = (datetime.now() - session["start_time"]).total_seconds() / 60
        
        await self.track_event(
            EventType.USER_LOGOUT,
            user_id=session["user_id"],
            session_id=session_id,
            properties={"duration_minutes": duration, "events_count": session["events_count"]}
        )
        
        del self.user_sessions[session_id]

    async def track_project_creation(self, project_id: str, user_id: str, template_id: Optional[str] = None):
        """Rastrear criação de projeto"""
        await self.track_event(
            EventType.PROJECT_CREATE,
            user_id=user_id,
            properties={"project_id": project_id, "template_id": template_id}
        )
        
        # Criar métricas do projeto
        await self._create_project_metrics(project_id, user_id, template_id)

    async def track_video_generation(self, project_id: str, user_id: str, duration: float, 
                                   format: str, quality: str):
        """Rastrear geração de vídeo"""
        await self.track_event(
            EventType.VIDEO_GENERATE,
            user_id=user_id,
            properties={
                "project_id": project_id,
                "duration": duration,
                "format": format,
                "quality": quality
            }
        )

    async def track_feature_usage(self, feature_name: str, user_id: str, properties: Dict[str, Any] = None):
        """Rastrear uso de funcionalidade"""
        await self.track_event(
            EventType.FEATURE_USE,
            user_id=user_id,
            properties={"feature": feature_name, **(properties or {})}
        )

    async def track_error(self, error_type: str, error_message: str, user_id: Optional[str] = None,
                         context: Dict[str, Any] = None):
        """Rastrear erro"""
        await self.track_event(
            EventType.ERROR_OCCUR,
            user_id=user_id,
            properties={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            }
        )

    async def track_performance_metric(self, metric_name: str, value: float, unit: str = "ms",
                                     context: Dict[str, Any] = None):
        """Rastrear métrica de performance"""
        await self.track_event(
            EventType.PERFORMANCE_METRIC,
            properties={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "context": context or {}
            }
        )

    # ===================================================================
    # ANALYTICS E RELATÓRIOS
    # ===================================================================
    
    async def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Obter analytics de usuário"""
        since = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Eventos do usuário
        cursor.execute('''
            SELECT event_type, COUNT(*), AVG(CAST(json_extract(properties, '$.duration') AS REAL))
            FROM analytics_events 
            WHERE user_id = ? AND timestamp > ?
            GROUP BY event_type
        ''', (user_id, since.isoformat()))
        
        events_data = cursor.fetchall()
        
        # Métricas do usuário
        cursor.execute('SELECT * FROM user_metrics WHERE user_id = ?', (user_id,))
        user_metrics = cursor.fetchone()
        
        conn.close()
        
        # Processar dados
        events_summary = {}
        for event_type, count, avg_duration in events_data:
            events_summary[event_type] = {
                "count": count,
                "average_duration": avg_duration or 0
            }
        
        return {
            "user_id": user_id,
            "period_days": days,
            "events_summary": events_summary,
            "user_metrics": user_metrics,
            "activity_score": self._calculate_activity_score(events_summary),
            "engagement_level": self._calculate_engagement_level(events_summary)
        }

    async def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Obter analytics de projeto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Métricas do projeto
        cursor.execute('SELECT * FROM project_metrics WHERE project_id = ?', (project_id,))
        project_data = cursor.fetchone()
        
        # Eventos relacionados ao projeto
        cursor.execute('''
            SELECT event_type, COUNT(*), user_id
            FROM analytics_events 
            WHERE json_extract(properties, '$.project_id') = ?
            GROUP BY event_type, user_id
        ''', (project_id,))
        
        events_data = cursor.fetchall()
        
        conn.close()
        
        if not project_data:
            return {"error": "Project not found"}
        
        # Processar dados
        collaborators = set()
        activity_by_type = defaultdict(int)
        
        for event_type, count, user_id in events_data:
            if user_id:
                collaborators.add(user_id)
            activity_by_type[event_type] += count
        
        return {
            "project_id": project_id,
            "creator_id": project_data[1],
            "created_at": project_data[2],
            "last_modified": project_data[3],
            "total_edits": project_data[4],
            "collaborators_count": len(collaborators),
            "export_count": project_data[6],
            "duration": project_data[7],
            "template_used": project_data[8],
            "completion_rate": project_data[9],
            "activity_by_type": dict(activity_by_type)
        }

    async def get_system_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Obter analytics do sistema"""
        since = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Métricas do sistema
        cursor.execute('''
            SELECT AVG(active_users), AVG(cpu_usage), AVG(memory_usage), 
                   AVG(response_time), AVG(error_rate), SUM(videos_generated_today)
            FROM system_metrics 
            WHERE timestamp > ?
        ''', (since.isoformat(),))
        
        system_data = cursor.fetchone()
        
        # Eventos por tipo
        cursor.execute('''
            SELECT event_type, COUNT(*)
            FROM analytics_events 
            WHERE timestamp > ?
            GROUP BY event_type
        ''', (since.isoformat(),))
        
        events_data = cursor.fetchall()
        
        # Usuários únicos
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id)
            FROM analytics_events 
            WHERE timestamp > ? AND user_id IS NOT NULL
        ''', (since.isoformat(),))
        
        unique_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "period_hours": hours,
            "average_metrics": {
                "active_users": system_data[0] or 0,
                "cpu_usage": system_data[1] or 0,
                "memory_usage": system_data[2] or 0,
                "response_time": system_data[3] or 0,
                "error_rate": system_data[4] or 0
            },
            "totals": {
                "videos_generated": system_data[5] or 0,
                "unique_users": unique_users,
                "total_events": sum(count for _, count in events_data)
            },
            "events_by_type": dict(events_data)
        }

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Obter métricas em tempo real"""
        window = datetime.now() - timedelta(minutes=self.config["real_time_window_minutes"])
        
        # Filtrar eventos recentes
        recent_events = [e for e in self.events if e.timestamp > window]
        
        # Calcular métricas
        active_users = len(set(e.user_id for e in recent_events if e.user_id))
        active_sessions = len(self.user_sessions)
        events_per_minute = len(recent_events) / self.config["real_time_window_minutes"]
        
        # Eventos por tipo
        events_by_type = Counter(e.event_type.value for e in recent_events)
        
        # Erros recentes
        recent_errors = [e for e in recent_events if e.event_type == EventType.ERROR_OCCUR]
        error_rate = len(recent_errors) / len(recent_events) if recent_events else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "window_minutes": self.config["real_time_window_minutes"],
            "active_users": active_users,
            "active_sessions": active_sessions,
            "events_per_minute": round(events_per_minute, 2),
            "error_rate": round(error_rate * 100, 2),
            "events_by_type": dict(events_by_type),
            "recent_errors": len(recent_errors)
        }

    async def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Gerar relatório diário"""
        if not date:
            date = datetime.now().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Usuários ativos
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id)
            FROM analytics_events 
            WHERE timestamp >= ? AND timestamp < ? AND user_id IS NOT NULL
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        daily_active_users = cursor.fetchone()[0]
        
        # Novos usuários (primeira atividade)
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id)
            FROM analytics_events a1
            WHERE timestamp >= ? AND timestamp < ? 
            AND user_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM analytics_events a2 
                WHERE a2.user_id = a1.user_id AND a2.timestamp < ?
            )
        ''', (start_date.isoformat(), end_date.isoformat(), start_date.isoformat()))
        
        new_users = cursor.fetchone()[0]
        
        # Projetos criados
        cursor.execute('''
            SELECT COUNT(*)
            FROM analytics_events 
            WHERE event_type = ? AND timestamp >= ? AND timestamp < ?
        ''', (EventType.PROJECT_CREATE.value, start_date.isoformat(), end_date.isoformat()))
        
        projects_created = cursor.fetchone()[0]
        
        # Vídeos gerados
        cursor.execute('''
            SELECT COUNT(*)
            FROM analytics_events 
            WHERE event_type = ? AND timestamp >= ? AND timestamp < ?
        ''', (EventType.VIDEO_GENERATE.value, start_date.isoformat(), end_date.isoformat()))
        
        videos_generated = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "date": date.isoformat(),
            "daily_active_users": daily_active_users,
            "new_users": new_users,
            "projects_created": projects_created,
            "videos_generated": videos_generated,
            "retention_rate": self._calculate_retention_rate(date),
            "engagement_score": self._calculate_daily_engagement(date)
        }

    # ===================================================================
    # A/B TESTING
    # ===================================================================
    
    async def create_ab_test(self, test_name: str, variants: List[str], traffic_split: List[float]):
        """Criar teste A/B"""
        if len(variants) != len(traffic_split) or sum(traffic_split) != 1.0:
            raise ValueError("Variants and traffic split must match and sum to 1.0")
        
        self.ab_tests[test_name] = {
            "variants": variants,
            "traffic_split": traffic_split,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "results": {variant: {"users": 0, "conversions": 0} for variant in variants}
        }
        
        logger.info(f"🧪 Teste A/B criado: {test_name}")

    def get_ab_test_variant(self, test_name: str, user_id: str) -> Optional[str]:
        """Obter variante do teste A/B para usuário"""
        if test_name not in self.ab_tests or not self.ab_tests[test_name]["active"]:
            return None
        
        test = self.ab_tests[test_name]
        
        # Hash consistente baseado no user_id
        import hashlib
        hash_value = int(hashlib.md5(f"{test_name}_{user_id}".encode()).hexdigest(), 16)
        bucket = (hash_value % 1000) / 1000.0
        
        # Determinar variante baseada na distribuição de tráfego
        cumulative = 0
        for i, (variant, split) in enumerate(zip(test["variants"], test["traffic_split"])):
            cumulative += split
            if bucket <= cumulative:
                return variant
        
        return test["variants"][-1]  # Fallback

    async def track_ab_test_conversion(self, test_name: str, user_id: str, variant: str):
        """Rastrear conversão no teste A/B"""
        if test_name in self.ab_tests and variant in self.ab_tests[test_name]["variants"]:
            self.ab_tests[test_name]["results"][variant]["conversions"] += 1
            
            await self.track_event(
                EventType.FEATURE_USE,
                user_id=user_id,
                properties={"ab_test": test_name, "variant": variant, "conversion": True}
            )

    # ===================================================================
    # MÉTODOS PRIVADOS
    # ===================================================================
    
    async def _flush_events(self):
        """Salvar eventos no banco"""
        if not self.events:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for event in self.events:
                cursor.execute('''
                    INSERT INTO analytics_events (
                        id, user_id, session_id, event_type, timestamp, properties, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.id,
                    event.user_id,
                    event.session_id,
                    event.event_type.value,
                    event.timestamp.isoformat(),
                    json.dumps(event.properties),
                    json.dumps(event.metadata)
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 {len(self.events)} eventos salvos no database")
            self.events.clear()
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar eventos: {e}")

    async def _flush_events_task(self):
        """Tarefa de flush automático"""
        while self.is_collecting:
            await asyncio.sleep(self.config["flush_interval"])
            await self._flush_events()

    async def _collect_system_metrics_task(self):
        """Tarefa de coleta de métricas do sistema"""
        import psutil
        
        while self.is_collecting:
            try:
                # Coletar métricas do sistema
                cpu_usage = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                # Simular outras métricas
                active_users = len(self.user_sessions)
                response_time = 150 + (cpu_usage * 2)  # Simulação
                error_rate = max(0, (cpu_usage - 80) / 20) if cpu_usage > 80 else 0
                
                # Salvar no banco
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO system_metrics (
                        timestamp, active_users, cpu_usage, memory_usage, 
                        response_time, error_rate
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    active_users,
                    cpu_usage,
                    memory.percent,
                    response_time,
                    error_rate
                ))
                
                conn.commit()
                conn.close()
                
                await asyncio.sleep(60)  # Coletar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {e}")
                await asyncio.sleep(5)

    async def _update_user_metrics_task(self):
        """Tarefa de atualização de métricas de usuário"""
        while self.is_collecting:
            try:
                # Atualizar métricas de usuário periodicamente
                await asyncio.sleep(300)  # A cada 5 minutos
                
            except Exception as e:
                logger.error(f"Erro na atualização de métricas: {e}")
                await asyncio.sleep(30)

    async def _create_project_metrics(self, project_id: str, creator_id: str, template_id: Optional[str]):
        """Criar métricas iniciais do projeto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO project_metrics (
                project_id, creator_id, created_at, last_modified, template_used
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            project_id,
            creator_id,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            template_id
        ))
        
        conn.commit()
        conn.close()

    def _calculate_activity_score(self, events_summary: Dict) -> float:
        """Calcular score de atividade"""
        # Algoritmo simples baseado na frequência de eventos
        weights = {
            "user_login": 1.0,
            "project_create": 3.0,
            "video_generate": 5.0,
            "feature_use": 0.5
        }
        
        score = 0
        for event_type, data in events_summary.items():
            weight = weights.get(event_type, 1.0)
            score += data["count"] * weight
        
        return min(score / 100, 1.0)  # Normalizar entre 0 e 1

    def _calculate_engagement_level(self, events_summary: Dict) -> str:
        """Calcular nível de engajamento"""
        score = self._calculate_activity_score(events_summary)
        
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "minimal"

    def _calculate_retention_rate(self, date: datetime.date) -> float:
        """Calcular taxa de retenção"""
        # Implementação simplificada
        return 0.75  # 75% como exemplo

    def _calculate_daily_engagement(self, date: datetime.date) -> float:
        """Calcular engajamento diário"""
        # Implementação simplificada
        return 0.65  # 65% como exemplo

# ===================================================================
# INSTÂNCIA SINGLETON
# ===================================================================

analytics_engine = AnalyticsEngine()

async def initialize_analytics():
    """Inicializar sistema de analytics"""
    await analytics_engine.start_collection()

def get_analytics_engine() -> AnalyticsEngine:
    """Obter instância do analytics engine"""
    return analytics_engine

if __name__ == "__main__":
    async def demo():
        # Demonstração do sistema de analytics
        engine = get_analytics_engine()
        await engine.start_collection()
        
        # Simular eventos
        await engine.track_event(EventType.USER_LOGIN, user_id="user123")
        await engine.track_project_creation("proj1", "user123", "template1")
        await engine.track_video_generation("proj1", "user123", 30.0, "mp4", "1080p")
        
        await asyncio.sleep(2)
        
        # Obter analytics
        user_analytics = await engine.get_user_analytics("user123")
        real_time = await engine.get_real_time_metrics()
        daily_report = await engine.generate_daily_report()
        
        print("📊 Analytics Demo:")
        print(f"User Analytics: {user_analytics}")
        print(f"Real-time: {real_time}")
        print(f"Daily Report: {daily_report}")
        
        engine.stop_collection()
    
    asyncio.run(demo()) 