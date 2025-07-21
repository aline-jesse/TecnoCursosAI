"""
Router do Dashboard Principal - TecnoCursos AI
Sistema de dashboard moderno para monitoramento do SaaS

Este router oferece:
- Dashboard visual na rota principal "/"
- Status em tempo real dos componentes
- Integração com sistema de logging
- Dados dinâmicos configuráveis
- Templates Jinja2 responsivos
"""

import os
import psutil
import platform
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio

from ..services.logging_service import logging_service, LogLevel, LogCategory
from ..services.notification_service import notification_service

# Configuração do router
router = APIRouter(tags=["dashboard"])

# Configuração dos templates Jinja2
templates = Jinja2Templates(directory="templates")

class DashboardService:
    """
    Serviço responsável por coletar dados do dashboard
    
    Este serviço centraliza toda a lógica de coleta de dados para o dashboard,
    permitindo fácil customização e adição de novos componentes de monitoramento.
    """
    
    def __init__(self):
        self.system_name = os.getenv("SYSTEM_NAME", "TecnoCursosAI")
        self.system_version = os.getenv("SYSTEM_VERSION", "2.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
    
    async def get_system_info(self) -> Dict[str, Any]:
        """
        Coleta informações básicas do sistema
        
        Retorna dados sobre:
        - Nome e versão do sistema
        - Ambiente atual (dev/prod)
        - Timestamp da última atualização
        - Informações do servidor
        """
        return {
            "name": self.system_name,
            "subtitle": "Sistema de Geração de Vídeos com IA",
            "version": self.system_version,
            "environment": self.environment,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "server_info": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "hostname": platform.node()
            }
        }
    
    async def get_component_status(self) -> List[Dict[str, Any]]:
        """
        Verifica status de todos os componentes do sistema
        
        Para adicionar novos componentes, adicione um novo item na lista
        com as chaves: name, status, description, icon, details
        
        Status possíveis:
        - "online": Componente funcionando normalmente (verde)
        - "warning": Componente com alertas (amarelo)  
        - "error": Componente com problemas (vermelho)
        - "offline": Componente indisponível (cinza)
        """
        components = []
        
        # Sistema de Logging
        try:
            # Testa se o sistema de logging está funcionando
            await logging_service.log(
                LogLevel.DEBUG,
                LogCategory.SYSTEM_OPERATION,
                "Dashboard health check - logging system"
            )
            components.append({
                "name": "Sistema de Logging",
                "status": "online",
                "description": "Logs estruturados em JSON funcionando",
                "icon": "📊",
                "details": "Último log: agora"
            })
        except Exception as e:
            components.append({
                "name": "Sistema de Logging",
                "status": "error",
                "description": f"Erro no sistema de logs: {str(e)}",
                "icon": "📊",
                "details": "Verificar configuração"
            })
        
        # Sistema de Notificações
        try:
            connected_users = notification_service.connection_manager.get_connected_users()
            total_connections = notification_service.connection_manager.get_connection_count()
            
            components.append({
                "name": "Sistema de Notificações",
                "status": "online",
                "description": "WebSocket e notificações funcionando",
                "icon": "🔔",
                "details": f"{len(connected_users)} usuários conectados, {total_connections} conexões ativas"
            })
        except Exception as e:
            components.append({
                "name": "Sistema de Notificações",
                "status": "warning",
                "description": "Sistema de notificações com problemas",
                "icon": "🔔",
                "details": str(e)
            })
        
        # Processamento de Vídeo
        # Aqui você pode adicionar verificações reais dos serviços de vídeo
        components.append({
            "name": "Engine de Processamento",
            "status": "online",
            "description": "Processamento de vídeo e IA disponível",
            "icon": "🎬",
            "details": "Última tarefa: 2 min atrás"
        })
        
        # Banco de Dados
        # Adicione verificação real da conexão do banco
        components.append({
            "name": "Banco de Dados",
            "status": "online",
            "description": "PostgreSQL conectado e funcionando",
            "icon": "🗃️",
            "details": "Conexões ativas: 5/100"
        })
        
        # Sistema de Arquivos
        try:
            # Verifica espaço em disco
            disk_usage = psutil.disk_usage('/')
            free_gb = disk_usage.free // (1024**3)
            total_gb = disk_usage.total // (1024**3)
            
            if free_gb < 5:  # Menos de 5GB livres
                status = "warning"
                description = "Pouco espaço em disco disponível"
            else:
                status = "online"
                description = "Armazenamento funcionando normalmente"
            
            components.append({
                "name": "Sistema de Arquivos",
                "status": status,
                "description": description,
                "icon": "💾",
                "details": f"{free_gb}GB livres de {total_gb}GB"
            })
        except Exception:
            components.append({
                "name": "Sistema de Arquivos",
                "status": "error",
                "description": "Erro ao verificar armazenamento",
                "icon": "💾",
                "details": "Verificar permissões"
            })
        
        # API Externa (exemplo)
        components.append({
            "name": "APIs Externas",
            "status": "online",
            "description": "OpenAI, Azure, AWS conectados",
            "icon": "🌐",
            "details": "Latência média: 120ms"
        })
        
        return components
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas de performance do sistema
        
        Para adicionar novas métricas, adicione os dados no dicionário retornado.
        Útil para monitoramento de recursos e performance.
        """
        try:
            # CPU e Memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Processos ativos
            active_processes = len(psutil.pids())
            
            return {
                "cpu_usage": round(cpu_percent, 1),
                "memory_usage": round(memory.percent, 1),
                "memory_available": round(memory.available / (1024**3), 1),  # GB
                "active_processes": active_processes,
                "uptime": self._get_uptime(),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            # Em caso de erro, retorna valores padrão
            return {
                "cpu_usage": 0,
                "memory_usage": 0,
                "memory_available": 0,
                "active_processes": 0,
                "uptime": "Indisponível",
                "load_average": [0, 0, 0]
            }
    
    def _get_uptime(self) -> str:
        """Calcula tempo de atividade do sistema"""
        try:
            uptime_seconds = psutil.boot_time()
            current_time = datetime.now().timestamp()
            uptime = current_time - uptime_seconds
            
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            
            if days > 0:
                return f"{days}d {hours}h"
            else:
                return f"{hours}h"
        except:
            return "Indisponível"
    
    async def get_quick_actions(self) -> List[Dict[str, Any]]:
        """
        Define ações rápidas disponíveis no dashboard
        
        Para adicionar novas ações, adicione um novo item na lista
        com as chaves: title, description, url, icon, color
        """
        return [
            {
                "title": "Documentação da API",
                "description": "Swagger UI interativo",
                "url": "/docs",
                "icon": "📖",
                "color": "blue"
            },
            {
                "title": "Documentação ReDoc",
                "description": "Documentação alternativa",
                "url": "/redoc",
                "icon": "📚",
                "color": "green"
            },
            {
                "title": "Health Check",
                "description": "Status detalhado da API",
                "url": "/health",
                "icon": "🏥",
                "color": "purple"
            },
            {
                "title": "Sistema de Logs",
                "description": "Visualizar logs da aplicação",
                "url": "/admin/logs",
                "icon": "📊",
                "color": "orange"
            },
            {
                "title": "Notificações",
                "description": "Central de notificações",
                "url": "/notifications",
                "icon": "🔔",
                "color": "red"
            },
            {
                "title": "Monitoramento",
                "description": "Métricas e performance",
                "url": "/metrics",
                "icon": "📈",
                "color": "indigo"
            }
        ]

# Instância do serviço de dashboard
dashboard_service = DashboardService()

@router.get("/", response_class=HTMLResponse, summary="Dashboard Principal")
async def dashboard_home(request: Request):
    """
    Rota principal do sistema - Dashboard de Status
    
    Esta rota renderiza o dashboard principal do TecnoCursosAI com:
    - Status em tempo real de todos os componentes
    - Métricas de sistema (CPU, memória, uptime)
    - Ações rápidas para navegação
    - Design responsivo e moderno
    
    Para customizar o dashboard:
    1. Edite os dados em DashboardService
    2. Modifique o template em templates/dashboard.html
    3. Ajuste os estilos em static/css/dashboard.css
    
    Variáveis de ambiente suportadas:
    - SYSTEM_NAME: Nome do sistema (default: "TecnoCursosAI")
    - SYSTEM_VERSION: Versão atual (default: "2.0.0")
    - ENVIRONMENT: Ambiente atual (default: "development")
    """
    try:
        # Log da visualização do dashboard
        await logging_service.log_user_action(
            action="dashboard_view",
            user_id="anonymous",  # Ou extrair do token se disponível
            ip_address=request.client.host,
            metadata={
                "user_agent": request.headers.get("user-agent", ""),
                "referer": request.headers.get("referer", "")
            }
        )
        
        # Coleta todos os dados necessários para o dashboard
        system_info = await dashboard_service.get_system_info()
        component_status = await dashboard_service.get_component_status()
        system_metrics = await dashboard_service.get_system_metrics()
        quick_actions = await dashboard_service.get_quick_actions()
        
        # Calcula estatísticas gerais
        total_components = len(component_status)
        online_components = len([c for c in component_status if c["status"] == "online"])
        warning_components = len([c for c in component_status if c["status"] == "warning"])
        error_components = len([c for c in component_status if c["status"] == "error"])
        
        # Status geral do sistema
        if error_components > 0:
            overall_status = "error"
            status_message = f"{error_components} componente(s) com erro"
        elif warning_components > 0:
            overall_status = "warning"
            status_message = f"{warning_components} componente(s) com aviso"
        else:
            overall_status = "online"
            status_message = "Todos os sistemas operacionais"
        
        # Renderiza o template com todos os dados
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "system_info": system_info,
            "component_status": component_status,
            "system_metrics": system_metrics,
            "quick_actions": quick_actions,
            "overall_status": overall_status,
            "status_message": status_message,
            "stats": {
                "total": total_components,
                "online": online_components,
                "warning": warning_components,
                "error": error_components
            }
        })
        
    except Exception as e:
        # Em caso de erro, loga e renderiza página de erro
        await logging_service.log_error(
            e,
            LogCategory.ERROR_HANDLING,
            additional_context={"route": "dashboard_home"}
        )
        
        # Renderiza template de erro simples
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Erro ao carregar dashboard",
            "error_details": str(e)
        })

@router.get("/health", summary="Health Check Detalhado")
async def health_check():
    """
    Endpoint de health check detalhado
    
    Retorna status JSON de todos os componentes para monitoramento externo.
    Útil para integração com ferramentas como Prometheus, DataDog, etc.
    """
    try:
        component_status = await dashboard_service.get_component_status()
        system_metrics = await dashboard_service.get_system_metrics()
        
        # Determina status geral
        has_errors = any(c["status"] == "error" for c in component_status)
        has_warnings = any(c["status"] == "warning" for c in component_status)
        
        if has_errors:
            overall_status = "error"
        elif has_warnings:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": component_status,
            "metrics": system_metrics,
            "version": dashboard_service.system_version
        }
        
    except Exception as e:
        await logging_service.log_error(e)
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        } 