"""
Sistema de Load Balancing e Escalabilidade Horizontal - TecnoCursos AI
=====================================================================

Sistema avançado de balanceamento de carga incluindo:
- Load balancing algorithms (Round Robin, Weighted, Least Connections)
- Auto-scaling baseado em métricas
- Health checks automáticos
- Circuit breakers para falhas
- Distribuição geográfica
- Session affinity/sticky sessions
- Rate limiting distribuído

Autor: TecnoCursos AI Team
Data: 2024
"""

import json
import logging
import asyncio
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import hashlib
import statistics
from collections import defaultdict, deque
import threading
import uuid
import aiohttp

# Configuração de logging
logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Algoritmos de load balancing"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    GEOGRAPHIC = "geographic"
    RANDOM = "random"

class ServerStatus(Enum):
    """Status do servidor"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"

class CircuitBreakerState(Enum):
    """Estados do circuit breaker"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open" # Testing if recovered

class ScalingAction(Enum):
    """Ações de scaling"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NONE = "none"

@dataclass
class ServerInstance:
    """Instância de servidor"""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    status: ServerStatus = ServerStatus.HEALTHY
    last_health_check: Optional[datetime] = None
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_count: int = 0
    total_requests: int = 0
    region: Optional[str] = None
    zone: Optional[str] = None
    
    @property
    def is_available(self) -> bool:
        return self.status in [ServerStatus.HEALTHY, ServerStatus.DRAINING]
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def error_rate(self) -> float:
        return (self.error_count / self.total_requests * 100) if self.total_requests > 0 else 0.0

@dataclass
class CircuitBreaker:
    """Circuit breaker para um servidor"""
    server_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    recovery_timeout: timedelta = timedelta(seconds=30)
    last_failure_time: Optional[datetime] = None
    half_open_max_calls: int = 3
    half_open_calls: int = 0

@dataclass
class HealthCheck:
    """Configuração de health check"""
    endpoint: str = "/health"
    interval: timedelta = timedelta(seconds=30)
    timeout: timedelta = timedelta(seconds=5)
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    expected_status: int = 200

@dataclass
class AutoScalingConfig:
    """Configuração de auto-scaling"""
    min_instances: int = 2
    max_instances: int = 10
    target_cpu_percent: float = 70.0
    target_response_time: float = 1000.0  # ms
    scale_up_cooldown: timedelta = timedelta(minutes=5)
    scale_down_cooldown: timedelta = timedelta(minutes=10)
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0

class LoadBalancingService:
    """
    Serviço de Load Balancing e Auto-Scaling
    
    Funcionalidades:
    - Distribuição inteligente de carga
    - Health monitoring contínuo
    - Auto-scaling baseado em métricas
    - Circuit breakers para resiliência
    - Session affinity
    """
    
    def __init__(self):
        # Servidores registrados
        self.servers: Dict[str, ServerInstance] = {}
        self.server_groups: Dict[str, List[str]] = defaultdict(list)
        
        # Load balancing
        self.algorithm = LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN
        self.round_robin_counter = 0
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Health checks
        self.health_check_config = HealthCheck()
        self.health_check_active = False
        self.health_check_thread: Optional[threading.Thread] = None
        
        # Auto-scaling
        self.auto_scaling_config = AutoScalingConfig()
        self.last_scale_action: Dict[str, datetime] = {}
        
        # Session affinity
        self.session_affinity: Dict[str, str] = {}  # session_id -> server_id
        self.sticky_sessions_enabled = False
        
        # Métricas
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "requests_per_second": 0.0
        }
        
        # Request tracking
        self.request_history: deque = deque(maxlen=1000)
        
        logger.info("✅ Load Balancing Service inicializado")
    
    async def register_server(
        self,
        server_id: str,
        host: str,
        port: int,
        weight: int = 1,
        max_connections: int = 1000,
        region: Optional[str] = None,
        zone: Optional[str] = None,
        group: str = "default"
    ) -> ServerInstance:
        """Registra novo servidor no pool"""
        
        server = ServerInstance(
            id=server_id,
            host=host,
            port=port,
            weight=weight,
            max_connections=max_connections,
            region=region,
            zone=zone
        )
        
        self.servers[server_id] = server
        self.server_groups[group].append(server_id)
        
        # Criar circuit breaker
        self.circuit_breakers[server_id] = CircuitBreaker(server_id=server_id)
        
        logger.info(f"Servidor registrado: {server_id} ({host}:{port})")
        return server
    
    async def unregister_server(self, server_id: str):
        """Remove servidor do pool"""
        
        if server_id in self.servers:
            # Drenar conexões existentes
            await self._drain_server(server_id)
            
            # Remover das estruturas
            del self.servers[server_id]
            del self.circuit_breakers[server_id]
            
            # Remover dos grupos
            for group_servers in self.server_groups.values():
                if server_id in group_servers:
                    group_servers.remove(server_id)
            
            logger.info(f"Servidor removido: {server_id}")
    
    async def select_server(
        self,
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None,
        group: str = "default"
    ) -> Optional[ServerInstance]:
        """Seleciona servidor usando o algoritmo configurado"""
        
        available_servers = await self._get_available_servers(group)
        if not available_servers:
            logger.warning(f"Nenhum servidor disponível no grupo {group}")
            return None
        
        # Session affinity
        if self.sticky_sessions_enabled and session_id:
            if session_id in self.session_affinity:
                server_id = self.session_affinity[session_id]
                if server_id in available_servers:
                    return self.servers[server_id]
        
        # Aplicar algoritmo de balanceamento
        selected_server = await self._apply_load_balancing_algorithm(
            available_servers, client_ip
        )
        
        # Registrar session affinity se necessário
        if self.sticky_sessions_enabled and session_id and selected_server:
            self.session_affinity[session_id] = selected_server.id
        
        return selected_server
    
    async def _get_available_servers(self, group: str) -> List[ServerInstance]:
        """Retorna servidores disponíveis de um grupo"""
        
        server_ids = self.server_groups.get(group, [])
        available_servers = []
        
        for server_id in server_ids:
            server = self.servers.get(server_id)
            if not server:
                continue
            
            # Verificar circuit breaker
            circuit_breaker = self.circuit_breakers.get(server_id)
            if circuit_breaker and circuit_breaker.state == CircuitBreakerState.OPEN:
                continue
            
            # Verificar status e capacidade
            if server.is_available and server.current_connections < server.max_connections:
                available_servers.append(server)
        
        return available_servers
    
    async def _apply_load_balancing_algorithm(
        self,
        servers: List[ServerInstance],
        client_ip: Optional[str] = None
    ) -> Optional[ServerInstance]:
        """Aplica algoritmo de balanceamento selecionado"""
        
        if not servers:
            return None
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin_select(servers)
        
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(servers)
        
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select(servers)
        
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(servers)
        
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash_select(servers, client_ip or "")
        
        elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
            return random.choice(servers)
        
        else:
            return self._round_robin_select(servers)
    
    def _round_robin_select(self, servers: List[ServerInstance]) -> ServerInstance:
        """Round robin simples"""
        self.round_robin_counter = (self.round_robin_counter + 1) % len(servers)
        return servers[self.round_robin_counter]
    
    def _weighted_round_robin_select(self, servers: List[ServerInstance]) -> ServerInstance:
        """Round robin ponderado"""
        total_weight = sum(server.weight for server in servers)
        random_weight = random.randint(1, total_weight)
        
        current_weight = 0
        for server in servers:
            current_weight += server.weight
            if random_weight <= current_weight:
                return server
        
        return servers[0]  # Fallback
    
    def _least_connections_select(self, servers: List[ServerInstance]) -> ServerInstance:
        """Menor número de conexões"""
        return min(servers, key=lambda s: s.current_connections)
    
    def _least_response_time_select(self, servers: List[ServerInstance]) -> ServerInstance:
        """Menor tempo de resposta"""
        return min(servers, key=lambda s: s.avg_response_time)
    
    def _ip_hash_select(self, servers: List[ServerInstance], client_ip: str) -> ServerInstance:
        """Hash do IP do cliente"""
        if not client_ip:
            return servers[0]
        
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return servers[hash_value % len(servers)]
    
    async def record_request_result(
        self,
        server_id: str,
        response_time: float,
        success: bool,
        status_code: Optional[int] = None
    ):
        """Registra resultado de uma requisição"""
        
        server = self.servers.get(server_id)
        if not server:
            return
        
        # Atualizar métricas do servidor
        server.total_requests += 1
        server.response_times.append(response_time)
        
        if not success:
            server.error_count += 1
            await self._handle_server_error(server_id)
        else:
            await self._handle_server_success(server_id)
        
        # Atualizar métricas globais
        self.metrics["total_requests"] += 1
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        # Registrar no histórico
        self.request_history.append({
            "timestamp": datetime.now(),
            "server_id": server_id,
            "response_time": response_time,
            "success": success,
            "status_code": status_code
        })
    
    async def _handle_server_error(self, server_id: str):
        """Trata erro de servidor"""
        
        circuit_breaker = self.circuit_breakers.get(server_id)
        if not circuit_breaker:
            return
        
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = datetime.now()
        
        # Verificar se deve abrir circuit breaker
        if (circuit_breaker.state == CircuitBreakerState.CLOSED and
            circuit_breaker.failure_count >= circuit_breaker.failure_threshold):
            
            circuit_breaker.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker ABERTO para servidor {server_id}")
        
        elif circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            circuit_breaker.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker voltou para ABERTO: {server_id}")
    
    async def _handle_server_success(self, server_id: str):
        """Trata sucesso de servidor"""
        
        circuit_breaker = self.circuit_breakers.get(server_id)
        if not circuit_breaker:
            return
        
        if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            circuit_breaker.half_open_calls += 1
            
            if circuit_breaker.half_open_calls >= circuit_breaker.half_open_max_calls:
                circuit_breaker.state = CircuitBreakerState.CLOSED
                circuit_breaker.failure_count = 0
                circuit_breaker.half_open_calls = 0
                logger.info(f"Circuit breaker FECHADO para servidor {server_id}")
        
        elif circuit_breaker.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            circuit_breaker.failure_count = max(0, circuit_breaker.failure_count - 1)
    
    async def start_health_checks(self):
        """Inicia health checks contínuos"""
        
        if self.health_check_active:
            return
        
        self.health_check_active = True
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()
        
        logger.info("Health checks iniciados")
    
    async def stop_health_checks(self):
        """Para health checks"""
        
        self.health_check_active = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        
        logger.info("Health checks parados")
    
    def _health_check_loop(self):
        """Loop de health checks"""
        
        while self.health_check_active:
            try:
                asyncio.run(self._perform_health_checks())
                time.sleep(self.health_check_config.interval.total_seconds())
            except Exception as e:
                logger.error(f"Erro no health check: {e}")
                time.sleep(30)  # Retry after 30s on error
    
    async def _perform_health_checks(self):
        """Executa health checks em todos os servidores"""
        
        tasks = []
        for server_id, server in self.servers.items():
            task = self._check_server_health(server)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_server_health(self, server: ServerInstance):
        """Verifica saúde de um servidor específico"""
        
        url = f"http://{server.host}:{server.port}{self.health_check_config.endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(
                        total=self.health_check_config.timeout.total_seconds()
                    )
                ) as response:
                    
                    server.last_health_check = datetime.now()
                    
                    if response.status == self.health_check_config.expected_status:
                        if server.status == ServerStatus.UNHEALTHY:
                            server.status = ServerStatus.HEALTHY
                            logger.info(f"Servidor {server.id} voltou ao status HEALTHY")
                        
                        # Tentar recuperar circuit breaker
                        await self._try_recover_circuit_breaker(server.id)
                    
                    else:
                        await self._mark_server_unhealthy(server)
        
        except Exception as e:
            logger.error(f"Health check falhou para {server.id}: {e}")
            await self._mark_server_unhealthy(server)
    
    async def _mark_server_unhealthy(self, server: ServerInstance):
        """Marca servidor como não saudável"""
        
        if server.status == ServerStatus.HEALTHY:
            server.status = ServerStatus.UNHEALTHY
            logger.warning(f"Servidor {server.id} marcado como UNHEALTHY")
    
    async def _try_recover_circuit_breaker(self, server_id: str):
        """Tenta recuperar circuit breaker"""
        
        circuit_breaker = self.circuit_breakers.get(server_id)
        if not circuit_breaker:
            return
        
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            if (circuit_breaker.last_failure_time and
                datetime.now() - circuit_breaker.last_failure_time >= circuit_breaker.recovery_timeout):
                
                circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                circuit_breaker.half_open_calls = 0
                logger.info(f"Circuit breaker em HALF_OPEN para {server_id}")
    
    async def _drain_server(self, server_id: str):
        """Drena conexões de um servidor"""
        
        server = self.servers.get(server_id)
        if not server:
            return
        
        server.status = ServerStatus.DRAINING
        logger.info(f"Drenando servidor {server_id}")
        
        # Aguardar conexões terminarem (máximo 30s)
        max_wait = 30
        waited = 0
        
        while server.current_connections > 0 and waited < max_wait:
            await asyncio.sleep(1)
            waited += 1
        
        logger.info(f"Servidor {server_id} drenado")
    
    async def evaluate_auto_scaling(self, group: str = "default") -> ScalingAction:
        """Avalia necessidade de auto-scaling"""
        
        servers = [
            self.servers[sid] for sid in self.server_groups.get(group, [])
            if sid in self.servers
        ]
        
        if not servers:
            return ScalingAction.NONE
        
        # Verificar cooldown
        last_action_time = self.last_scale_action.get(group)
        if last_action_time:
            cooldown = self.auto_scaling_config.scale_up_cooldown
            if datetime.now() - last_action_time < cooldown:
                return ScalingAction.NONE
        
        # Calcular métricas médias
        avg_cpu = self._calculate_avg_cpu_usage(servers)
        avg_response_time = self._calculate_avg_response_time(servers)
        avg_connections = self._calculate_avg_connections(servers)
        
        # Decidir ação de scaling
        if (avg_cpu > self.auto_scaling_config.scale_up_threshold or
            avg_response_time > self.auto_scaling_config.target_response_time):
            
            if len(servers) < self.auto_scaling_config.max_instances:
                return ScalingAction.SCALE_UP
        
        elif (avg_cpu < self.auto_scaling_config.scale_down_threshold and
              avg_response_time < self.auto_scaling_config.target_response_time / 2):
            
            if len(servers) > self.auto_scaling_config.min_instances:
                return ScalingAction.SCALE_DOWN
        
        return ScalingAction.NONE
    
    def _calculate_avg_cpu_usage(self, servers: List[ServerInstance]) -> float:
        """Calcula uso médio de CPU (simulado)"""
        # Em produção, isso viria de métricas reais
        return sum(min(90, server.current_connections / server.max_connections * 100) 
                  for server in servers) / len(servers)
    
    def _calculate_avg_response_time(self, servers: List[ServerInstance]) -> float:
        """Calcula tempo médio de resposta"""
        response_times = [server.avg_response_time for server in servers if server.response_times]
        return statistics.mean(response_times) if response_times else 0.0
    
    def _calculate_avg_connections(self, servers: List[ServerInstance]) -> float:
        """Calcula média de conexões"""
        return sum(server.current_connections for server in servers) / len(servers)
    
    # === MÉTODOS PÚBLICOS ===
    
    def set_load_balancing_algorithm(self, algorithm: LoadBalancingAlgorithm):
        """Define algoritmo de load balancing"""
        self.algorithm = algorithm
        logger.info(f"Algoritmo de load balancing alterado para: {algorithm.value}")
    
    def enable_sticky_sessions(self, enabled: bool = True):
        """Habilita/desabilita sticky sessions"""
        self.sticky_sessions_enabled = enabled
        if not enabled:
            self.session_affinity.clear()
        logger.info(f"Sticky sessions: {'habilitadas' if enabled else 'desabilitadas'}")
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos servidores"""
        
        stats = {}
        for server_id, server in self.servers.items():
            circuit_breaker = self.circuit_breakers.get(server_id)
            
            stats[server_id] = {
                **asdict(server),
                "circuit_breaker_state": circuit_breaker.state.value if circuit_breaker else "unknown",
                "url": f"http://{server.host}:{server.port}"
            }
        
        return stats
    
    def get_load_balancing_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de load balancing"""
        
        # Calcular requests per second
        recent_requests = [
            r for r in self.request_history
            if datetime.now() - r["timestamp"] < timedelta(minutes=1)
        ]
        rps = len(recent_requests) / 60.0 if recent_requests else 0.0
        
        # Calcular tempo médio de resposta
        if recent_requests:
            avg_response_time = statistics.mean(r["response_time"] for r in recent_requests)
        else:
            avg_response_time = 0.0
        
        return {
            **self.metrics,
            "requests_per_second": rps,
            "avg_response_time": avg_response_time,
            "total_servers": len(self.servers),
            "healthy_servers": len([s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]),
            "algorithm": self.algorithm.value,
            "sticky_sessions_enabled": self.sticky_sessions_enabled,
            "active_sessions": len(self.session_affinity)
        }
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Retorna status dos circuit breakers"""
        
        return {
            server_id: {
                "state": cb.state.value,
                "failure_count": cb.failure_count,
                "last_failure": cb.last_failure_time.isoformat() if cb.last_failure_time else None
            }
            for server_id, cb in self.circuit_breakers.items()
        }

# === INSTÂNCIA GLOBAL ===
load_balancing_service = LoadBalancingService()

logger.info("✅ Load Balancing Service carregado com sucesso") 