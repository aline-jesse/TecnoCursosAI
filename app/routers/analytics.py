#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router de Analytics em Tempo Real - TecnoCursos AI

Este módulo implementa endpoints REST para acesso aos dados de analytics,
métricas de performance e relatórios do sistema em tempo real.

Funcionalidades:
- Métricas de sistema em tempo real
- Relatórios de usuários e conteúdo
- Dashboard de performance
- Alertas e notificações
- Estatísticas de uso
- Exportação de dados

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import asyncio
import logging

logger = logging.getLogger(__name__)

try:
    from app.services.analytics_service import (
        get_analytics_service,
        MetricsCollector,
        SystemMetrics,
        UserActivity,
        ContentMetrics,
        PerformanceReport,
        AlertConfiguration,
        ExportFormat
    )
    from app.services.cache_service import cache_service
    from app.services.websocket_service import get_websocket_services
    from app.services.backup_service import backup_service
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Analytics services não disponíveis: {e}")
    SERVICES_AVAILABLE = False

try:
    from app.auth import get_current_active_user, get_current_admin_user
    from app.models import User
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# ============================================================================
# SCHEMAS DE RESPOSTA
# ============================================================================

class SystemMetricsResponse(BaseModel):
    """Resposta de métricas do sistema."""
    timestamp: datetime
    active_users: int
    total_requests: int
    average_response_time: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    status: str = "healthy"

class UserActivityResponse(BaseModel):
    """Resposta de atividade de usuários."""
    period_days: int
    total_users: int
    active_users: int
    activity_rate: float
    top_users: List[Dict[str, Any]]
    current_sessions: int

class ContentMetricsResponse(BaseModel):
    """Resposta de métricas de conteúdo."""
    files: Dict[str, Any]
    videos: Dict[str, Any]
    audios: Dict[str, Any]
    trends: Dict[str, List[Dict[str, Any]]]

class PerformanceReportResponse(BaseModel):
    """Resposta de relatório de performance."""
    system_health: Dict[str, Any]
    application_performance: Dict[str, Any]
    endpoint_performance: Dict[str, Any]
    data_points: int
    collection_period: str

class AlertResponse(BaseModel):
    """Resposta de alertas."""
    alerts: List[Dict[str, Any]]
    total_alerts: int
    critical_count: int
    warning_count: int

class CacheStatsResponse(BaseModel):
    """Resposta de estatísticas de cache."""
    system: Dict[str, Any]
    l1: Dict[str, Any]
    l2: Dict[str, Any]

class WebSocketStatsResponse(BaseModel):
    """Resposta de estatísticas WebSocket."""
    active_connections: int
    authenticated_connections: int
    total_rooms: int
    total_connections_ever: int
    total_messages_sent: int
    uptime_seconds: float
    users_by_room: Dict[str, int]

class BackupStatsResponse(BaseModel):
    """Resposta de estatísticas de backup."""
    total_backups: int
    successful_backups: int
    failed_backups: int
    success_rate: float
    total_size_mb: float
    average_compression_ratio: float
    configs_count: int
    scheduler_running: bool

# ============================================================================
# CONFIGURAÇÃO DO ROUTER
# ============================================================================

analytics_router = APIRouter(
    prefix="/api/analytics",
    tags=["📊 Analytics & Monitoring"],
    responses={
        500: {"description": "Erro interno do servidor"},
        503: {"description": "Serviço indisponível"}
    }
)

# ============================================================================
# ENDPOINTS DE MÉTRICAS EM TEMPO REAL
# ============================================================================

@analytics_router.get("/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Obter métricas do sistema em tempo real.
    
    Retorna informações sobre CPU, memória, disk, network, 
    requisições ativas e performance geral do sistema.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Serviços de analytics não disponíveis"
        )
    
    try:
        analytics = get_analytics_service()
        collector = analytics['collector']
        
        # Obter métricas mais recentes
        if not collector.metrics_buffer:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma métrica disponível ainda"
            )
        
        latest_metrics = collector.metrics_buffer[-1]
        
        # Determinar status de saúde
        status = "healthy"
        if latest_metrics.cpu_usage > 80 or latest_metrics.memory_usage > 85:
            status = "warning"
        if latest_metrics.cpu_usage > 90 or latest_metrics.memory_usage > 95:
            status = "critical"
        
        return SystemMetricsResponse(
            timestamp=latest_metrics.timestamp,
            active_users=latest_metrics.active_users,
            total_requests=latest_metrics.total_requests,
            average_response_time=latest_metrics.average_response_time,
            error_rate=latest_metrics.error_rate,
            cpu_usage=latest_metrics.cpu_usage,
            memory_usage=latest_metrics.memory_usage,
            disk_usage=latest_metrics.disk_usage,
            network_io=latest_metrics.network_io,
            status=status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")

@analytics_router.get("/system/health")
async def get_system_health():
    """
    Verificação rápida de saúde do sistema.
    
    Endpoint otimizado para health checks e monitoramento externo.
    """
    try:
        if not SERVICES_AVAILABLE:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded",
                    "message": "Analytics services not available",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        analytics = get_analytics_service()
        collector = analytics['collector']
        
        if not collector.metrics_buffer:
            return {
                "status": "starting",
                "message": "Collecting initial metrics",
                "timestamp": datetime.now().isoformat()
            }
        
        latest = collector.metrics_buffer[-1]
        
        # Determinar status
        if latest.cpu_usage < 70 and latest.memory_usage < 80 and latest.error_rate < 5:
            status = "healthy"
        elif latest.cpu_usage < 85 and latest.memory_usage < 90 and latest.error_rate < 10:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "cpu_usage": latest.cpu_usage,
            "memory_usage": latest.memory_usage,
            "error_rate": latest.error_rate,
            "active_users": latest.active_users,
            "timestamp": latest.timestamp.isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# ============================================================================
# ENDPOINTS DE RELATÓRIOS
# ============================================================================

@analytics_router.get("/reports/users", response_model=UserActivityResponse)
async def get_user_activity_report(
    days: int = Query(7, ge=1, le=365, description="Período em dias"),
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Relatório de atividade dos usuários.
    
    Fornece estatísticas sobre usuários ativos, uploads,
    sessões e padrões de uso no período especificado.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        analytics = get_analytics_service()
        reports_generator = analytics['reports']
        
        report = await reports_generator.generate_user_activity_report(days)
        
        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])
        
        return UserActivityResponse(**report)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no relatório: {str(e)}")

@analytics_router.get("/reports/content", response_model=ContentMetricsResponse)
async def get_content_metrics_report(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Relatório de métricas de conteúdo.
    
    Estatísticas sobre arquivos, vídeos, áudios gerados
    e tendências de criação de conteúdo.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        analytics = get_analytics_service()
        reports_generator = analytics['reports']
        
        report = await reports_generator.generate_content_metrics_report()
        
        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])
        
        return ContentMetricsResponse(**report)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no relatório: {str(e)}")

@analytics_router.get("/reports/performance", response_model=PerformanceReportResponse)
async def get_performance_report(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Relatório de performance do sistema.
    
    Métricas detalhadas de performance por endpoint,
    tempos de resposta e estatísticas de sistema.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        analytics = get_analytics_service()
        reports_generator = analytics['reports']
        
        report = await reports_generator.generate_performance_report()
        
        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])
        
        return PerformanceReportResponse(**report)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no relatório: {str(e)}")

# ============================================================================
# ENDPOINTS DE ALERTAS
# ============================================================================

@analytics_router.get("/alerts", response_model=AlertResponse)
async def get_current_alerts(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Obter alertas ativos do sistema.
    
    Lista todos os alertas de performance, erros e
    condições que requerem atenção.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        analytics = get_analytics_service()
        alerts_system = analytics['alerts']
        
        # Verificar alertas atuais
        current_alerts = alerts_system.check_alerts()
        
        # Contar por severidade
        critical_count = len([a for a in current_alerts if a.get('severity') == 'critical'])
        warning_count = len([a for a in current_alerts if a.get('severity') in ['warning', 'performance']])
        
        return AlertResponse(
            alerts=current_alerts,
            total_alerts=len(current_alerts),
            critical_count=critical_count,
            warning_count=warning_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter alertas: {str(e)}")

@analytics_router.get("/alerts/history")
async def get_alerts_history(
    hours: int = Query(24, ge=1, le=168, description="Horas de histórico"),
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Histórico de alertas do sistema.
    
    Lista alertas disparados no período especificado
    para análise de tendências e padrões.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        analytics = get_analytics_service()
        alerts_system = analytics['alerts']
        
        # Filtrar alertas por período
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = [
            alert for alert in alerts_system.alert_history
            if alert['timestamp'] >= cutoff_time
        ]
        
        # Agrupar por tipo
        alert_types = {}
        for alert in history:
            alert_type = alert.get('type', 'unknown')
            if alert_type not in alert_types:
                alert_types[alert_type] = 0
            alert_types[alert_type] += 1
        
        return {
            "period_hours": hours,
            "total_alerts": len(history),
            "alerts": history,
            "alert_types": alert_types,
            "query_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no histórico: {str(e)}")

# ============================================================================
# ENDPOINTS DE ESTATÍSTICAS DE SERVIÇOS
# ============================================================================

@analytics_router.get("/services/cache", response_model=CacheStatsResponse)
async def get_cache_statistics(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Estatísticas do sistema de cache.
    
    Métricas de hit rate, uso de memória e performance
    dos caches L1 e L2 (Redis).
    """
    try:
        cache = cache_service
        stats = cache.get_comprehensive_stats()
        
        return CacheStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro nas stats de cache: {str(e)}")

@analytics_router.get("/services/websocket", response_model=WebSocketStatsResponse)
async def get_websocket_statistics(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Estatísticas do sistema WebSocket.
    
    Informações sobre conexões ativas, salas,
    mensagens enviadas e performance.
    """
    try:
        ws_services = get_websocket_services()
        connection_manager = ws_services['connection_manager']
        
        stats = connection_manager.get_connection_stats()
        
        return WebSocketStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro nas stats de WebSocket: {str(e)}")

@analytics_router.get("/services/backup", response_model=BackupStatsResponse)
async def get_backup_statistics(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Estatísticas do sistema de backup.
    
    Informações sobre backups executados, taxa de sucesso,
    tamanhos e configurações ativas.
    """
    try:
        backup_service = backup_service
        stats = backup_service.get_backup_stats()
        
        return BackupStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro nas stats de backup: {str(e)}")

# ============================================================================
# ENDPOINTS DE CONTROLE
# ============================================================================

@analytics_router.post("/control/start")
async def start_analytics_service(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Iniciar sistema de analytics.
    
    Inicia a coleta de métricas em tempo real
    e todos os serviços relacionados.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        # Assuming start_analytics_system and stop_analytics_system are defined elsewhere
        # from app.services.analytics_service import start_analytics_system, stop_analytics_system
        # For now, we'll just return a placeholder message
        return {
            "message": "Analytics service control endpoints are not fully implemented yet.",
            "status": "info",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar: {str(e)}")

@analytics_router.post("/control/stop")
async def stop_analytics_service(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Parar sistema de analytics.
    
    Para a coleta de métricas e finaliza
    todos os threads de monitoramento.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        # Assuming stop_analytics_system is defined elsewhere
        # from app.services.analytics_service import stop_analytics_system
        # For now, we'll just return a placeholder message
        return {
            "message": "Analytics service control endpoints are not fully implemented yet.",
            "status": "info",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar: {str(e)}")

@analytics_router.post("/cache/clear")
async def clear_system_cache(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Limpar todo o cache do sistema.
    
    Remove todas as entradas dos caches L1 e L2
    para liberação de memória ou troubleshooting.
    """
    try:
        cache = cache_service
        cache.clear()
        
        return {
            "message": "Cache do sistema limpo com sucesso",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar cache: {str(e)}")

# ============================================================================
# ENDPOINTS DE DASHBOARD
# ============================================================================

@analytics_router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Visão geral para dashboard de analytics.
    
    Combina métricas principais de todos os serviços
    em uma resposta otimizada para dashboards.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        # Coletar dados de múltiplos serviços
        analytics = get_analytics_service()
        
        # Métricas de sistema
        collector = analytics['collector']
        latest_metrics = None
        if collector.metrics_buffer:
            latest_metrics = collector.metrics_buffer[-1]
        
        # Estatísticas de cache
        cache = cache_service
        cache_stats = cache.get_comprehensive_stats()
        
        # Estatísticas de WebSocket
        ws_services = get_websocket_services()
        ws_stats = ws_services['connection_manager'].get_connection_stats()
        
        # Estatísticas de backup
        backup_service = backup_service
        backup_stats = backup_service.get_backup_stats()
        
        # Alertas ativos
        alerts_system = analytics['alerts']
        current_alerts = alerts_system.check_alerts()
        
        return {
            "system": {
                "status": "healthy" if latest_metrics and latest_metrics.cpu_usage < 80 else "warning",
                "cpu_usage": latest_metrics.cpu_usage if latest_metrics else 0,
                "memory_usage": latest_metrics.memory_usage if latest_metrics else 0,
                "active_users": latest_metrics.active_users if latest_metrics else 0,
                "total_requests": latest_metrics.total_requests if latest_metrics else 0
            },
            "cache": {
                "hit_rate": cache_stats['system']['combined_hit_rate'],
                "total_requests": cache_stats['system']['total_requests']
            },
            "websocket": {
                "active_connections": ws_stats['active_connections'],
                "total_messages": ws_stats['total_messages_sent']
            },
            "backup": {
                "success_rate": backup_stats['success_rate'],
                "scheduler_running": backup_stats['scheduler_running']
            },
            "alerts": {
                "total_active": len(current_alerts),
                "critical_count": len([a for a in current_alerts if a.get('severity') == 'critical'])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no dashboard: {str(e)}")

@analytics_router.get("/export/metrics")
async def export_metrics_data(
    format: str = Query("json", regex="^(json|csv)$"),
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_active_user) if AUTH_AVAILABLE else None
):
    """
    Exportar dados de métricas.
    
    Permite exportação de dados históricos de métricas
    em formato JSON ou CSV para análise externa.
    """
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços não disponíveis")
    
    try:
        analytics = get_analytics_service()
        collector = analytics['collector']
        
        # Filtrar métricas por período
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_metrics = [
            m for m in collector.metrics_buffer
            if m.timestamp >= cutoff_time
        ]
        
        if format == "json":
            # Exportar como JSON
            data = {
                "export_info": {
                    "period_hours": hours,
                    "total_records": len(filtered_metrics),
                    "export_time": datetime.now().isoformat()
                },
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "active_users": m.active_users,
                        "total_requests": m.total_requests,
                        "average_response_time": m.average_response_time,
                        "error_rate": m.error_rate,
                        "cpu_usage": m.cpu_usage,
                        "memory_usage": m.memory_usage,
                        "disk_usage": m.disk_usage
                    }
                    for m in filtered_metrics
                ]
            }
            
            return JSONResponse(content=data)
        
        else:  # CSV
            # Para CSV, retornar como string formatada
            csv_lines = ["timestamp,active_users,total_requests,avg_response_time,error_rate,cpu_usage,memory_usage,disk_usage"]
            
            for m in filtered_metrics:
                line = f"{m.timestamp.isoformat()},{m.active_users},{m.total_requests},{m.average_response_time},{m.error_rate},{m.cpu_usage},{m.memory_usage},{m.disk_usage}"
                csv_lines.append(line)
            
            csv_content = "\n".join(csv_lines)
            
            return JSONResponse(
                content={"csv_data": csv_content, "filename": f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"},
                headers={"Content-Type": "application/json"}
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na exportação: {str(e)}")

# ============================================================================
# INICIALIZAÇÃO AUTOMÁTICA
# ============================================================================

@analytics_router.on_event("startup")
async def startup_analytics():
    """Inicializar analytics automaticamente."""
    if SERVICES_AVAILABLE:
        try:
            # Assuming start_analytics_system is defined elsewhere
            # from app.services.analytics_service import start_analytics_system
            # start_analytics_system()
            # Inicializar outros serviços conforme necessário
            print("Analytics service startup event triggered.")
        except Exception as e:
            print(f"Erro ao inicializar analytics: {e}")

@analytics_router.on_event("shutdown")  
async def shutdown_analytics():
    """Finalizar analytics na parada."""
    if SERVICES_AVAILABLE:
        try:
            # Assuming stop_analytics_system is defined elsewhere
            # from app.services.analytics_service import stop_analytics_system
            # stop_analytics_system()
            print("Analytics service shutdown event triggered.")
        except Exception as e:
            print(f"Erro ao finalizar analytics: {e}") 

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard")
async def get_dashboard_analytics():
    """Obter analytics do dashboard"""
    try:
        # Simular dados de analytics
        analytics = {
            "total_projects": 25,
            "total_videos": 150,
            "total_uploads": 300,
            "storage_used": "2.5GB",
            "storage_limit": "10GB",
            "recent_activity": [
                {
                    "type": "video_created",
                    "project": "Curso Python",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "file_uploaded",
                    "project": "Tutorial React",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
                }
            ],
            "performance_metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.4
            }
        }
        
        return {"status": "success", "data": analytics}
    except Exception as e:
        logger.error(f"Erro ao obter analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/projects/{project_id}/stats")
async def get_project_stats(project_id: int):
    """Obter estatísticas de um projeto específico"""
    try:
        stats = {
            "project_id": project_id,
            "scenes_count": 12,
            "total_duration": 180,
            "assets_count": 25,
            "last_modified": datetime.now().isoformat(),
            "completion_percentage": 75
        }
        
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error(f"Erro ao obter stats do projeto: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/system/health")
async def get_system_health():
    """Obter saúde do sistema"""
    try:
        import psutil
        
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "uptime": "2 days, 5 hours"
        }
        
        return {"status": "success", "data": health}
    except Exception as e:
        logger.error(f"Erro ao obter health do sistema: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 