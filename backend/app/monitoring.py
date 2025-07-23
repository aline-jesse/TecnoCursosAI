"""
Sistema de Monitoramento - TecnoCursosAI
Health checks avançados, métricas de sistema e monitoramento
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db, engine
from .models import User, Project, FileUpload, Video
from .config import get_settings
from .logger import get_logger, log_performance_metric

logger = get_logger("monitoring")
settings = get_settings()

class HealthStatus(BaseModel):
    """Schema para status de saúde"""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    uptime_seconds: float
    checks: Dict[str, Any]

class SystemMetrics(BaseModel):
    """Schema para métricas do sistema"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    active_connections: int
    total_requests: int
    avg_response_time: float

class DatabaseHealth(BaseModel):
    """Schema para saúde do banco de dados"""
    connected: bool
    pool_size: int
    checked_out: int
    overflow: int
    response_time_ms: float

class HealthMonitor:
    """Monitor de saúde da aplicação"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.total_response_time = 0.0
        self.last_health_check = None
        
    def record_request(self, response_time: float):
        """Registrar métricas de requisição"""
        self.request_count += 1
        self.total_response_time += response_time
        
    def get_uptime(self) -> float:
        """Obter tempo de atividade em segundos"""
        return time.time() - self.start_time
        
    def get_avg_response_time(self) -> float:
        """Obter tempo médio de resposta"""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    async def check_database_health(self) -> DatabaseHealth:
        """Verificar saúde do banco de dados"""
        try:
            start_time = time.time()
            
            # Testar conexão simples
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Obter informações do pool de conexões
            pool = engine.pool
            pool_size = pool.size()
            checked_out = pool.checkedout()
            overflow = pool.overflow()
            
            return DatabaseHealth(
                connected=True,
                pool_size=pool_size,
                checked_out=checked_out,
                overflow=overflow,
                response_time_ms=round(response_time_ms, 2)
            )
            
        except Exception as e:
            logger.error("Erro no health check do banco", error=str(e))
            return DatabaseHealth(
                connected=False,
                pool_size=0,
                checked_out=0,
                overflow=0,
                response_time_ms=0.0
            )
    
    def get_system_metrics(self) -> SystemMetrics:
        """Obter métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Rede
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Conexões ativas
            connections = len(psutil.net_connections())
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=round(disk_percent, 2),
                network_io=network_io,
                active_connections=connections,
                total_requests=self.request_count,
                avg_response_time=round(self.get_avg_response_time(), 3)
            )
            
        except Exception as e:
            logger.error("Erro ao obter métricas do sistema", error=str(e))
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_io={},
                active_connections=0,
                total_requests=self.request_count,
                avg_response_time=0.0
            )
    
    async def check_application_health(self) -> Dict[str, Any]:
        """Verificar saúde da aplicação"""
        checks = {}
        
        try:
            # Verificar diretórios essenciais
            import os
            essential_dirs = [
                settings.upload_path,
                settings.video_path,
                settings.thumbnail_path,
                "logs"
            ]
            
            for directory in essential_dirs:
                checks[f"directory_{directory.replace('/', '_')}"] = {
                    "status": "ok" if os.path.exists(directory) else "error",
                    "exists": os.path.exists(directory),
                    "writable": os.access(directory, os.W_OK) if os.path.exists(directory) else False
                }
            
            # Verificar espaço em disco
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free // (1024**3)
            
            checks["disk_space"] = {
                "status": "ok" if free_gb > 1 else "warning" if free_gb > 0.5 else "error",
                "free_gb": free_gb,
                "total_gb": total // (1024**3),
                "used_percent": (used / total) * 100
            }
            
            # Verificar dependências críticas
            try:
                import PyPDF2, pymysql, jwt, bcrypt
                checks["dependencies"] = {
                    "status": "ok",
                    "PyPDF2": True,
                    "pymysql": True,
                    "jwt": True,
                    "bcrypt": True
                }
            except ImportError as e:
                checks["dependencies"] = {
                    "status": "error",
                    "missing": str(e)
                }
            
        except Exception as e:
            checks["application_check_error"] = {
                "status": "error",
                "error": str(e)
            }
        
        return checks
    
    async def perform_full_health_check(self) -> HealthStatus:
        """Executar verificação completa de saúde"""
        start_time = time.time()
        
        try:
            # Verificar banco de dados
            db_health = await self.check_database_health()
            
            # Verificar aplicação
            app_checks = await self.check_application_health()
            
            # Obter métricas do sistema
            system_metrics = self.get_system_metrics()
            
            # Determinar status geral
            overall_status = "healthy"
            
            if not db_health.connected:
                overall_status = "unhealthy"
            elif (system_metrics.cpu_percent > 90 or 
                  system_metrics.memory_percent > 90 or 
                  system_metrics.disk_percent > 90):
                overall_status = "degraded"
            elif db_health.response_time_ms > 1000:
                overall_status = "degraded"
            
            # Verificar checks da aplicação
            for check_name, check_data in app_checks.items():
                if isinstance(check_data, dict) and check_data.get("status") == "error":
                    overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
            
            # Compilar resultado
            checks = {
                "database": db_health.dict(),
                "system_metrics": system_metrics.dict(),
                "application": app_checks,
                "uptime_seconds": self.get_uptime(),
                "check_duration_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            health_status = HealthStatus(
                status=overall_status,
                timestamp=datetime.now(),
                uptime_seconds=self.get_uptime(),
                checks=checks
            )
            
            # Log métricas de performance
            log_performance_metric(
                "health_check_duration",
                time.time() - start_time,
                "seconds"
            )
            
            self.last_health_check = health_status
            return health_status
            
        except Exception as e:
            logger.error("Erro no health check completo", error=str(e), exc_info=True)
            
            return HealthStatus(
                status="unhealthy",
                timestamp=datetime.now(),
                uptime_seconds=self.get_uptime(),
                checks={"error": str(e)}
            )

class MetricsCollector:
    """Coletor de métricas da aplicação"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history = 1000  # Manter últimas 1000 métricas
    
    async def collect_database_metrics(self, db: Session) -> Dict[str, Any]:
        """Coletar métricas do banco de dados"""
        try:
            metrics = {}
            
            # Contar registros por tabela
            metrics["users_count"] = db.query(User).count()
            metrics["projects_count"] = db.query(Project).count()
            metrics["files_count"] = db.query(FileUpload).count()
            metrics["videos_count"] = db.query(Video).count()
            
            # Calcular storage usado
            from sqlalchemy import func
            total_storage = db.query(func.sum(FileUpload.file_size)).scalar() or 0
            metrics["total_storage_bytes"] = total_storage
            metrics["total_storage_mb"] = round(total_storage / (1024 * 1024), 2)
            
            # Usuários ativos na última semana
            week_ago = datetime.now() - timedelta(days=7)
            active_users = db.query(User).filter(
                User.last_login >= week_ago,
                User.is_active == True
            ).count()
            metrics["active_users_week"] = active_users
            
            # Projetos criados hoje
            today = datetime.now().date()
            projects_today = db.query(Project).filter(
                func.date(Project.created_at) == today
            ).count()
            metrics["projects_created_today"] = projects_today
            
            return metrics
            
        except Exception as e:
            logger.error("Erro ao coletar métricas do banco", error=str(e))
            return {}
    
    def add_metric(self, name: str, value: Any, timestamp: datetime = None):
        """Adicionar métrica ao histórico"""
        if timestamp is None:
            timestamp = datetime.now()
        
        metric = {
            "name": name,
            "value": value,
            "timestamp": timestamp
        }
        
        self.metrics_history.append(metric)
        
        # Manter apenas as últimas métricas
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_recent_metrics(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Obter métricas recentes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            metric for metric in self.metrics_history
            if metric["timestamp"] >= cutoff
        ]

# Instâncias globais
health_monitor = HealthMonitor()
metrics_collector = MetricsCollector()

def get_health_monitor() -> HealthMonitor:
    """Obter instância do monitor de saúde"""
    return health_monitor

def get_metrics_collector() -> MetricsCollector:
    """Obter instância do coletor de métricas"""
    return metrics_collector

if __name__ == "__main__":
    """Testar sistema de monitoramento"""
    import asyncio
    
    async def test_monitoring():
        print("🔧 Testando sistema de monitoramento...")
        
        monitor = HealthMonitor()
        
        # Testar health check
        health = await monitor.perform_full_health_check()
        print(f"✅ Health check: {health.status}")
        print(f"📊 Uptime: {health.uptime_seconds:.2f}s")
        
        # Testar métricas do sistema
        metrics = monitor.get_system_metrics()
        print(f"🖥️ CPU: {metrics.cpu_percent}%")
        print(f"💾 Memory: {metrics.memory_percent}%")
        print(f"💽 Disk: {metrics.disk_percent}%")
        
        print("🎉 Sistema de monitoramento testado com sucesso!")
    
    asyncio.run(test_monitoring()) 