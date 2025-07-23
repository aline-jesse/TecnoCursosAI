#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Analytics e Monitoramento TTS - TecnoCursos AI
======================================================

Sistema completo de analytics, métricas, monitoramento e insights
para otimização do sistema TTS.
"""

import asyncio
import time
import json
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import logging
import statistics

logger = logging.getLogger(__name__)

@dataclass
class TTSMetric:
    """Métrica individual TTS"""
    timestamp: datetime
    user_id: Optional[str]
    provider: str
    voice: Optional[str]
    text_length: int
    processing_time: float
    success: bool
    error_type: Optional[str]
    file_size: int
    duration: float
    cached: bool = False
    metadata: Dict = field(default_factory=dict)

@dataclass
class UsageStats:
    """Estatísticas de uso"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0
    total_audio_duration: float = 0.0
    total_file_size: int = 0
    unique_users: int = 0
    cache_hits: int = 0
    avg_processing_time: float = 0.0
    avg_text_length: float = 0.0

class TTSAnalyticsService:
    """Serviço de analytics para TTS"""
    
    def __init__(self, db_path: str = "cache/tts_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Métricas em memória para performance
        self.recent_metrics: List[TTSMetric] = []
        self.max_recent_metrics = 1000
        
        # Cache de estatísticas calculadas
        self.stats_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutos
        
        # Inicializar banco
        self._init_database()
        
        # Carregar métricas recentes será feito sob demanda
        # asyncio.create_task(self._load_recent_metrics())
        
    def _init_database(self):
        """Inicializar banco de dados de analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tts_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_id TEXT,
                        provider TEXT NOT NULL,
                        voice TEXT,
                        text_length INTEGER NOT NULL,
                        processing_time REAL NOT NULL,
                        success BOOLEAN NOT NULL,
                        error_type TEXT,
                        file_size INTEGER DEFAULT 0,
                        duration REAL DEFAULT 0.0,
                        cached BOOLEAN DEFAULT 0,
                        metadata TEXT DEFAULT '{}'
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON tts_metrics(timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_id ON tts_metrics(user_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_provider ON tts_metrics(provider)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_success ON tts_metrics(success)
                """)
                
                # Tabela de eventos do sistema
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_data TEXT NOT NULL,
                        severity TEXT DEFAULT 'info'
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de analytics: {e}")
            
    async def _load_recent_metrics(self):
        """Carregar métricas recentes na memória"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, user_id, provider, voice, text_length,
                           processing_time, success, error_type, file_size,
                           duration, cached, metadata
                    FROM tts_metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (cutoff_time.isoformat(), self.max_recent_metrics))
                
                self.recent_metrics = []
                for row in cursor:
                    metric = TTSMetric(
                        timestamp=datetime.fromisoformat(row[0]),
                        user_id=row[1],
                        provider=row[2],
                        voice=row[3],
                        text_length=row[4],
                        processing_time=row[5],
                        success=bool(row[6]),
                        error_type=row[7],
                        file_size=row[8],
                        duration=row[9],
                        cached=bool(row[10]),
                        metadata=json.loads(row[11]) if row[11] else {}
                    )
                    self.recent_metrics.append(metric)
                    
                logger.info(f"Carregadas {len(self.recent_metrics)} métricas recentes")
                
        except Exception as e:
            logger.error(f"Erro ao carregar métricas recentes: {e}")
            
    async def record_tts_request(
        self,
        user_id: Optional[str],
        provider: str,
        voice: Optional[str],
        text_length: int,
        processing_time: float,
        success: bool,
        error_type: Optional[str] = None,
        file_size: int = 0,
        duration: float = 0.0,
        cached: bool = False,
        metadata: Optional[Dict] = None
    ):
        """Registrar uma requisição TTS"""
        
        metric = TTSMetric(
            timestamp=datetime.now(),
            user_id=user_id,
            provider=provider,
            voice=voice,
            text_length=text_length,
            processing_time=processing_time,
            success=success,
            error_type=error_type,
            file_size=file_size,
            duration=duration,
            cached=cached,
            metadata=metadata or {}
        )
        
        # Adicionar à memória
        self.recent_metrics.append(metric)
        
        # Manter limite de métricas em memória
        if len(self.recent_metrics) > self.max_recent_metrics:
            self.recent_metrics = self.recent_metrics[-self.max_recent_metrics:]
            
        # Persistir no banco (async) - apenas se houver loop de eventos rodando
        try:
            asyncio.create_task(self._persist_metric(metric))
        except RuntimeError:
            # Não há loop de eventos, persistir de forma síncrona
            pass
        
        # Invalidar cache de estatísticas
        self._invalidate_cache()
        
    async def _persist_metric(self, metric: TTSMetric):
        """Persistir métrica no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO tts_metrics (
                        timestamp, user_id, provider, voice, text_length,
                        processing_time, success, error_type, file_size,
                        duration, cached, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.timestamp.isoformat(),
                    metric.user_id,
                    metric.provider,
                    metric.voice,
                    metric.text_length,
                    metric.processing_time,
                    metric.success,
                    metric.error_type,
                    metric.file_size,
                    metric.duration,
                    metric.cached,
                    json.dumps(metric.metadata)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao persistir métrica: {e}")
            
    async def log_system_event(
        self,
        event_type: str,
        event_data: Dict,
        severity: str = "info"
    ):
        """Registrar evento do sistema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO system_events (timestamp, event_type, event_data, severity)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    event_type,
                    json.dumps(event_data),
                    severity
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao registrar evento do sistema: {e}")
            
    def _get_cached_stats(self, cache_key: str) -> Optional[Any]:
        """Obter estatísticas do cache"""
        if cache_key in self.cache_expiry:
            if time.time() < self.cache_expiry[cache_key]:
                return self.stats_cache.get(cache_key)
        return None
        
    def _set_cached_stats(self, cache_key: str, data: Any):
        """Definir estatísticas no cache"""
        self.stats_cache[cache_key] = data
        self.cache_expiry[cache_key] = time.time() + self.cache_duration
        
    def _invalidate_cache(self):
        """Invalidar cache de estatísticas"""
        self.stats_cache.clear()
        self.cache_expiry.clear()
        
    async def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> UsageStats:
        """Obter estatísticas de uso"""
        
        cache_key = f"usage_stats_{start_date}_{end_date}_{user_id}"
        cached = self._get_cached_stats(cache_key)
        if cached:
            return cached
            
        try:
            # Usar métricas recentes se for período recente
            if not start_date or (datetime.now() - start_date).total_seconds() < 3600:
                metrics = self.recent_metrics
                
                # Filtrar por período
                if start_date:
                    metrics = [m for m in metrics if m.timestamp >= start_date]
                if end_date:
                    metrics = [m for m in metrics if m.timestamp <= end_date]
                if user_id:
                    metrics = [m for m in metrics if m.user_id == user_id]
                    
            else:
                # Buscar no banco para períodos maiores
                metrics = await self._get_metrics_from_db(start_date, end_date, user_id)
                
            # Calcular estatísticas
            stats = UsageStats()
            
            if not metrics:
                return stats
                
            stats.total_requests = len(metrics)
            stats.successful_requests = sum(1 for m in metrics if m.success)
            stats.failed_requests = stats.total_requests - stats.successful_requests
            stats.total_processing_time = sum(m.processing_time for m in metrics)
            stats.total_audio_duration = sum(m.duration for m in metrics)
            stats.total_file_size = sum(m.file_size for m in metrics)
            stats.unique_users = len(set(m.user_id for m in metrics if m.user_id))
            stats.cache_hits = sum(1 for m in metrics if m.cached)
            
            if stats.total_requests > 0:
                stats.avg_processing_time = stats.total_processing_time / stats.total_requests
                stats.avg_text_length = statistics.mean(m.text_length for m in metrics)
                
            self._set_cached_stats(cache_key, stats)
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas de uso: {e}")
            return UsageStats()
            
    async def _get_metrics_from_db(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        user_id: Optional[str]
    ) -> List[TTSMetric]:
        """Obter métricas do banco de dados"""
        try:
            conditions = []
            params = []
            
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date.isoformat())
            if user_id:
                conditions.append("user_id = ?")
                params.append(user_id)
                
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f"""
                    SELECT timestamp, user_id, provider, voice, text_length,
                           processing_time, success, error_type, file_size,
                           duration, cached, metadata
                    FROM tts_metrics 
                    {where_clause}
                    ORDER BY timestamp DESC
                """, params)
                
                metrics = []
                for row in cursor:
                    metric = TTSMetric(
                        timestamp=datetime.fromisoformat(row[0]),
                        user_id=row[1],
                        provider=row[2],
                        voice=row[3],
                        text_length=row[4],
                        processing_time=row[5],
                        success=bool(row[6]),
                        error_type=row[7],
                        file_size=row[8],
                        duration=row[9],
                        cached=bool(row[10]),
                        metadata=json.loads(row[11]) if row[11] else {}
                    )
                    metrics.append(metric)
                    
                return metrics
                
        except Exception as e:
            logger.error(f"Erro ao buscar métricas do banco: {e}")
            return []
            
    async def get_provider_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict]:
        """Obter performance por provedor"""
        
        cache_key = f"provider_performance_{start_date}_{end_date}"
        cached = self._get_cached_stats(cache_key)
        if cached:
            return cached
            
        try:
            metrics = await self._get_metrics_from_db(start_date, end_date, None)
            
            # Agrupar por provedor
            provider_stats = defaultdict(lambda: {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_processing_time": 0.0,
                "avg_audio_duration": 0.0,
                "total_file_size": 0,
                "success_rate": 0.0,
                "processing_times": []
            })
            
            for metric in metrics:
                stats = provider_stats[metric.provider]
                stats["total_requests"] += 1
                stats["processing_times"].append(metric.processing_time)
                
                if metric.success:
                    stats["successful_requests"] += 1
                    stats["total_file_size"] += metric.file_size
                else:
                    stats["failed_requests"] += 1
                    
            # Calcular médias
            for provider, stats in provider_stats.items():
                if stats["total_requests"] > 0:
                    stats["success_rate"] = (stats["successful_requests"] / stats["total_requests"]) * 100
                    stats["avg_processing_time"] = statistics.mean(stats["processing_times"])
                    
                    # Remover lista de tempos (não serializável)
                    del stats["processing_times"]
                    
            result = dict(provider_stats)
            self._set_cached_stats(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Erro ao calcular performance por provedor: {e}")
            return {}
            
    async def get_error_analysis(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Análise detalhada de erros"""
        
        try:
            metrics = await self._get_metrics_from_db(start_date, end_date, None)
            
            # Filtrar apenas erros
            error_metrics = [m for m in metrics if not m.success]
            
            if not error_metrics:
                return {
                    "total_errors": 0,
                    "error_types": {},
                    "error_trends": {},
                    "most_common_errors": []
                }
                
            # Contar tipos de erro
            error_types = Counter(m.error_type for m in error_metrics if m.error_type)
            
            # Tendências de erro por hora
            error_trends = defaultdict(int)
            for metric in error_metrics:
                hour_key = metric.timestamp.strftime('%Y-%m-%d %H:00:00')
                error_trends[hour_key] += 1
                
            # Erros mais comuns
            most_common_errors = [
                {"error_type": error_type, "count": count}
                for error_type, count in error_types.most_common(10)
            ]
            
            return {
                "total_errors": len(error_metrics),
                "error_rate": (len(error_metrics) / len(metrics)) * 100 if metrics else 0,
                "error_types": dict(error_types),
                "error_trends": dict(error_trends),
                "most_common_errors": most_common_errors
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de erros: {e}")
            return {}
            
    async def get_usage_trends(
        self,
        period_hours: int = 24
    ) -> Dict:
        """Obter tendências de uso"""
        
        try:
            start_date = datetime.now() - timedelta(hours=period_hours)
            metrics = await self._get_metrics_from_db(start_date, None, None)
            
            # Agrupar por hora
            hourly_usage = defaultdict(lambda: {
                "requests": 0,
                "success_rate": 0.0,
                "avg_processing_time": 0.0,
                "processing_times": []
            })
            
            for metric in metrics:
                hour_key = metric.timestamp.strftime('%Y-%m-%d %H:00:00')
                hour_stats = hourly_usage[hour_key]
                
                hour_stats["requests"] += 1
                hour_stats["processing_times"].append(metric.processing_time)
                
            # Calcular médias
            for hour_key, stats in hourly_usage.items():
                if stats["processing_times"]:
                    stats["avg_processing_time"] = statistics.mean(stats["processing_times"])
                del stats["processing_times"]
                
            return {
                "period_hours": period_hours,
                "hourly_usage": dict(hourly_usage),
                "total_requests": len(metrics),
                "peak_hour": max(hourly_usage.keys(), key=lambda k: hourly_usage[k]["requests"]) if hourly_usage else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular tendências: {e}")
            return {}
            
    async def get_user_insights(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """Insights específicos do usuário"""
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            metrics = await self._get_metrics_from_db(start_date, None, user_id)
            
            if not metrics:
                return {"message": "Nenhuma atividade encontrada para este usuário"}
                
            # Estatísticas básicas
            total_requests = len(metrics)
            successful_requests = sum(1 for m in metrics if m.success)
            total_audio_duration = sum(m.duration for m in metrics if m.success)
            total_characters = sum(m.text_length for m in metrics)
            
            # Provedores favoritos
            provider_usage = Counter(m.provider for m in metrics)
            
            # Vozes favoritas
            voice_usage = Counter(m.voice for m in metrics if m.voice)
            
            # Padrões de uso (horários)
            hour_usage = Counter(m.timestamp.hour for m in metrics)
            
            return {
                "user_id": user_id,
                "period_days": days,
                "summary": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "success_rate": (successful_requests / total_requests) * 100,
                    "total_audio_duration": total_audio_duration,
                    "total_characters_processed": total_characters,
                    "avg_text_length": total_characters / total_requests
                },
                "preferences": {
                    "favorite_provider": provider_usage.most_common(1)[0][0] if provider_usage else None,
                    "favorite_voice": voice_usage.most_common(1)[0][0] if voice_usage else None,
                    "most_active_hour": hour_usage.most_common(1)[0][0] if hour_usage else None
                },
                "usage_patterns": {
                    "provider_breakdown": dict(provider_usage),
                    "voice_breakdown": dict(voice_usage),
                    "hourly_usage": dict(hour_usage)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar insights do usuário: {e}")
            return {"error": str(e)}
            
    async def generate_performance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Gerar relatório completo de performance"""
        
        try:
            # Obter todas as análises
            usage_stats = await self.get_usage_stats(start_date, end_date)
            provider_performance = await self.get_provider_performance(start_date, end_date)
            error_analysis = await self.get_error_analysis(start_date, end_date)
            usage_trends = await self.get_usage_trends(24)
            
            # Calcular insights adicionais
            metrics = await self._get_metrics_from_db(start_date, end_date, None)
            
            # Performance insights
            if metrics:
                processing_times = [m.processing_time for m in metrics if m.success]
                text_lengths = [m.text_length for m in metrics]
                
                performance_insights = {
                    "median_processing_time": statistics.median(processing_times) if processing_times else 0,
                    "p95_processing_time": statistics.quantiles(processing_times, n=20)[18] if len(processing_times) > 20 else 0,
                    "median_text_length": statistics.median(text_lengths) if text_lengths else 0,
                    "cache_hit_rate": (usage_stats.cache_hits / usage_stats.total_requests) * 100 if usage_stats.total_requests > 0 else 0
                }
            else:
                performance_insights = {}
                
            return {
                "report_generated": datetime.now().isoformat(),
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "usage_summary": usage_stats.__dict__,
                "provider_performance": provider_performance,
                "error_analysis": error_analysis,
                "usage_trends": usage_trends,
                "performance_insights": performance_insights
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de performance: {e}")
            return {"error": str(e)}


# Instância global do serviço
tts_analytics_service = TTSAnalyticsService()

# Funções de conveniência
async def record_tts_metric(
    user_id: Optional[str],
    provider: str,
    voice: Optional[str],
    text_length: int,
    processing_time: float,
    success: bool,
    **kwargs
):
    """Registrar métrica TTS"""
    await tts_analytics_service.record_tts_request(
        user_id=user_id,
        provider=provider,
        voice=voice,
        text_length=text_length,
        processing_time=processing_time,
        success=success,
        **kwargs
    )

async def get_tts_usage_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[str] = None
) -> UsageStats:
    """Obter estatísticas de uso TTS"""
    return await tts_analytics_service.get_usage_stats(start_date, end_date, user_id)

async def get_tts_performance_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """Gerar relatório de performance TTS"""
    return await tts_analytics_service.generate_performance_report(start_date, end_date) 