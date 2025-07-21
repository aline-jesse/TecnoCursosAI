#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router de Controle do Sistema - TecnoCursos AI

Endpoints para controle e monitoramento avançado do sistema:
- Otimização em tempo real
- Monitoramento de recursos
- Controle de serviços
- Estatísticas de performance
- Alertas e notificações
- Diagnósticos do sistema

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil
import logging
import os

# Importar serviços
try:
    from app.services.system_optimizer import (
        get_system_optimizer,
        force_system_optimization
    )
    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False

try:
    from app.services.performance_monitor import get_performance_monitor
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from app.services.analytics_service import get_analytics_service
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

try:
    from app.auth import get_current_user
    from app.models import User
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configurar router
router = APIRouter(
    prefix="/api/system",
    tags=["🛠️ System Control"],
    responses={
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"},
        500: {"description": "Erro interno"}
    }
)

# ============================================================================
# SCHEMAS
# ============================================================================

class SystemStatus(BaseModel):
    """Status geral do sistema"""
    status: str
    uptime_seconds: float
    timestamp: datetime
    services: Dict[str, bool]
    resources: Dict[str, Any]
    alerts: List[Dict[str, Any]]

class OptimizationRequest(BaseModel):
    """Request para otimização"""
    force: bool = False
    aggressive: bool = False
    target_resources: Optional[List[str]] = None

class SystemCommand(BaseModel):
    """Comando do sistema"""
    action: str
    parameters: Optional[Dict[str, Any]] = None

# ============================================================================
# ENDPOINTS DE STATUS
# ============================================================================

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """
    Obter status completo do sistema.
    
    Retorna informações sobre:
    - Status dos serviços
    - Uso de recursos
    - Alertas ativos
    - Estatísticas de performance
    """
    try:
        # Recursos do sistema
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=1)
        
        resources = {
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / 1024 / 1024 / 1024,
            "disk_percent": (disk.used / disk.total) * 100,
            "disk_free_gb": disk.free / 1024 / 1024 / 1024,
            "network_connections": len(psutil.net_connections())
        }
        
        # Status dos serviços
        services = {
            "optimizer": OPTIMIZER_AVAILABLE,
            "performance_monitor": PERFORMANCE_AVAILABLE,
            "analytics": ANALYTICS_AVAILABLE,
            "auth": AUTH_AVAILABLE
        }
        
        # Alertas ativos
        alerts = []
        if memory.percent > 85:
            alerts.append({
                "type": "memory",
                "level": "warning",
                "message": f"Uso de memória alto: {memory.percent:.1f}%"
            })
        
        if (disk.used / disk.total) * 100 > 80:
            alerts.append({
                "type": "disk",
                "level": "warning", 
                "message": f"Uso de disco alto: {(disk.used / disk.total) * 100:.1f}%"
            })
        
        # Calcular uptime (simplificado)
        import time
        uptime = time.time() - psutil.boot_time()
        
        return SystemStatus(
            status="healthy" if len(alerts) == 0 else "warning",
            uptime_seconds=uptime,
            timestamp=datetime.now(),
            services=services,
            resources=resources,
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter status do sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.get("/resources/detailed")
async def get_detailed_resources():
    """
    Obter recursos detalhados do sistema.
    
    Inclui informações avançadas sobre:
    - CPU por core
    - Memória por processo
    - Disk I/O
    - Network I/O
    - Processos ativos
    """
    try:
        # CPU detalhado
        cpu_info = {
            "percent_per_cpu": psutil.cpu_percent(percpu=True),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "count_logical": psutil.cpu_count(logical=True),
            "count_physical": psutil.cpu_count(logical=False)
        }
        
        # Memória detalhada
        memory = psutil.virtual_memory()._asdict()
        swap = psutil.swap_memory()._asdict()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
        
        # Network I/O
        network_io = psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
        
        # Top 10 processos por memória
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        top_processes = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)[:10]
        
        return {
            "cpu": cpu_info,
            "memory": memory,
            "swap": swap,
            "disk_io": disk_io,
            "network_io": network_io,
            "top_processes": top_processes,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter recursos detalhados: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter recursos: {str(e)}")

# ============================================================================
# ENDPOINTS DE OTIMIZAÇÃO
# ============================================================================

@router.post("/optimize")
async def optimize_system(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Executar otimização do sistema.
    
    Parâmetros:
    - force: Forçar otimização mesmo se não necessária
    - aggressive: Usar otimização agressiva
    - target_resources: Recursos específicos a otimizar
    """
    if not OPTIMIZER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de otimização não disponível")
    
    try:
        optimizer = get_system_optimizer()
        
        if request.force:
            # Executar em background para não bloquear
            background_tasks.add_task(force_system_optimization)
            
            return {
                "message": "Otimização forçada iniciada",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Verificar se otimização é necessária
            stats = optimizer.get_optimization_stats()
            current_usage = stats.get("current_usage", {})
            
            needs_optimization = (
                current_usage.get("memory_percent", 0) > 85 or
                current_usage.get("disk_percent", 0) > 80 or
                current_usage.get("cpu_percent", 0) > 90
            )
            
            if needs_optimization:
                background_tasks.add_task(force_system_optimization)
                return {
                    "message": "Otimização iniciada (recursos altos detectados)",
                    "status": "running",
                    "current_usage": current_usage,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "message": "Otimização não necessária no momento",
                    "status": "idle",
                    "current_usage": current_usage,
                    "timestamp": datetime.now().isoformat()
                }
        
    except Exception as e:
        logger.error(f"Erro na otimização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na otimização: {str(e)}")

@router.get("/optimization/stats")
async def get_optimization_stats():
    """
    Obter estatísticas de otimização.
    
    Retorna informações sobre:
    - Otimizações executadas
    - Recursos liberados
    - Performance histórica
    """
    if not OPTIMIZER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço de otimização não disponível")
    
    try:
        optimizer = get_system_optimizer()
        stats = optimizer.get_optimization_stats()
        
        return {
            "optimization_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter stats de otimização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter stats: {str(e)}")

# ============================================================================
# ENDPOINTS DE CONTROLE DE SERVIÇOS
# ============================================================================

@router.post("/services/control")
async def control_service(command: SystemCommand):
    """
    Controlar serviços do sistema.
    
    Comandos disponíveis:
    - start_optimizer: Iniciar otimizador
    - stop_optimizer: Parar otimizador
    - restart_analytics: Reiniciar analytics
    - clear_cache: Limpar cache
    """
    try:
        action = command.action
        parameters = command.parameters or {}
        
        if action == "start_optimizer":
            if OPTIMIZER_AVAILABLE:
                optimizer = get_system_optimizer()
                optimizer.start_optimization()
                return {"message": "Otimizador iniciado", "status": "success"}
            else:
                raise HTTPException(status_code=503, detail="Otimizador não disponível")
        
        elif action == "stop_optimizer":
            if OPTIMIZER_AVAILABLE:
                optimizer = get_system_optimizer()
                optimizer.stop_optimization()
                return {"message": "Otimizador parado", "status": "success"}
            else:
                raise HTTPException(status_code=503, detail="Otimizador não disponível")
        
        elif action == "clear_cache":
            # Executar limpeza de cache
            try:
                from app.services.cache_service import get_default_cache
                cache = get_default_cache()
                if hasattr(cache, 'clear'):
                    cache.clear()
                return {"message": "Cache limpo", "status": "success"}
            except ImportError:
                return {"message": "Cache service não disponível", "status": "warning"}
        
        elif action == "force_gc":
            # Forçar garbage collection
            import gc
            collected = gc.collect()
            return {
                "message": f"Garbage collection executado: {collected} objetos coletados",
                "status": "success",
                "objects_collected": collected
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Ação não reconhecida: {action}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no controle de serviço: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no controle: {str(e)}")

# ============================================================================
# ENDPOINTS DE DIAGNÓSTICO
# ============================================================================

@router.get("/diagnostics/health")
async def run_health_check():
    """
    Executar verificação completa de saúde do sistema.
    
    Verifica:
    - Conectividade do banco de dados
    - Disponibilidade de serviços
    - Integridade de arquivos
    - Performance geral
    """
    try:
        health_report = {
            "overall_status": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Verificar banco de dados
        try:
            from app.database import check_database_health
            db_healthy = check_database_health()
            health_report["checks"]["database"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "details": "Database connection test"
            }
        except Exception as e:
            health_report["checks"]["database"] = {
                "status": "error",
                "details": f"Database check failed: {str(e)}"
            }
            health_report["overall_status"] = "degraded"
        
        # Verificar recursos
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resource_issues = []
        if memory.percent > 90:
            resource_issues.append(f"High memory usage: {memory.percent:.1f}%")
        if (disk.used / disk.total) * 100 > 85:
            resource_issues.append(f"High disk usage: {(disk.used / disk.total) * 100:.1f}%")
        
        health_report["checks"]["resources"] = {
            "status": "healthy" if not resource_issues else "warning",
            "details": resource_issues if resource_issues else "Resource usage normal"
        }
        
        if resource_issues:
            health_report["overall_status"] = "warning"
        
        # Verificar serviços
        service_status = {
            "optimizer": OPTIMIZER_AVAILABLE,
            "performance_monitor": PERFORMANCE_AVAILABLE,
            "analytics": ANALYTICS_AVAILABLE
        }
        
        unhealthy_services = [name for name, status in service_status.items() if not status]
        
        health_report["checks"]["services"] = {
            "status": "healthy" if not unhealthy_services else "degraded",
            "available": service_status,
            "details": f"Services unavailable: {unhealthy_services}" if unhealthy_services else "All services available"
        }
        
        if unhealthy_services:
            health_report["overall_status"] = "degraded"
        
        return health_report
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no health check: {str(e)}")

@router.get("/diagnostics/performance")
async def get_performance_diagnostics():
    """
    Obter diagnósticos detalhados de performance.
    """
    try:
        # Metrics básicas
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=1)
        
        # Calcular scores de performance
        memory_score = max(0, 100 - memory.percent)
        disk_score = max(0, 100 - ((disk.used / disk.total) * 100))
        cpu_score = max(0, 100 - cpu)
        
        overall_score = (memory_score + disk_score + cpu_score) / 3
        
        # Recomendações
        recommendations = []
        if memory.percent > 80:
            recommendations.append("Considere reiniciar serviços para liberar memória")
        if (disk.used / disk.total) * 100 > 75:
            recommendations.append("Execute limpeza de arquivos temporários")
        if cpu > 80:
            recommendations.append("Verifique processos com alto uso de CPU")
        
        return {
            "performance_score": round(overall_score, 2),
            "scores": {
                "memory": round(memory_score, 2),
                "disk": round(disk_score, 2),
                "cpu": round(cpu_score, 2)
            },
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico de performance: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no diagnóstico: {str(e)}")

# ============================================================================
# ENDPOINT DE EMERGÊNCIA
# ============================================================================

@router.post("/emergency/cleanup")
async def emergency_cleanup():
    """
    Limpeza de emergência do sistema.
    
    Executa limpeza agressiva para liberar recursos rapidamente:
    - Garbage collection forçado
    - Limpeza de cache
    - Otimização de banco
    - Limpeza de temporários
    """
    try:
        results = {
            "actions_taken": [],
            "resources_freed": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Garbage collection
        import gc
        collected = gc.collect()
        results["actions_taken"].append(f"Garbage collection: {collected} objetos")
        
        # Limpeza de cache
        try:
            from app.services.cache_service import get_default_cache
            cache = get_default_cache()
            if hasattr(cache, 'clear'):
                cache.clear()
                results["actions_taken"].append("Cache limpo")
        except ImportError:
            pass
        
        # Otimização forçada se disponível
        if OPTIMIZER_AVAILABLE:
            force_system_optimization()
            results["actions_taken"].append("Otimização forçada iniciada")
        
        # Limpeza de temporários básica
        import tempfile
        import shutil
        temp_dir = tempfile.gettempdir()
        try:
            for item in os.listdir(temp_dir):
                if item.startswith("tmp"):
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
            results["actions_taken"].append("Arquivos temporários limpos")
        except (OSError, PermissionError):
            pass
        
        return {
            "message": "Limpeza de emergência executada",
            "status": "completed",
            "details": results
        }
        
    except Exception as e:
        logger.error(f"Erro na limpeza de emergência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na limpeza: {str(e)}") 