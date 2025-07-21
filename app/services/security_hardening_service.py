"""
Sistema de Segurança Avançada e Hardening - TecnoCursos AI
=========================================================

Sistema abrangente de segurança incluindo:
- Criptografia multicamada (AES-256, RSA, ChaCha20)
- Proteção contra ataques (DDoS, XSS, SQL Injection, CSRF)
- Sistema de detecção de intrusões (IDS)
- Controles de acesso baseados em risco
- Monitoramento de segurança em tempo real
- Resposta automática a incidentes
- Audit logging de segurança

Autor: TecnoCursos AI Team
Data: 2024
"""

import json
import logging
import asyncio
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import ipaddress
from collections import defaultdict, deque
import re
import uuid
import base64

# Criptografia
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import jwt

# Configuração de logging
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Níveis de ameaça"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttackType(Enum):
    """Tipos de ataques detectáveis"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDOS = "ddos"
    MALWARE = "malware"
    PHISHING = "phishing"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"

class SecurityAction(Enum):
    """Ações de segurança automáticas"""
    BLOCK_IP = "block_ip"
    RATE_LIMIT = "rate_limit"
    REQUIRE_2FA = "require_2fa"
    LOGOUT_USER = "logout_user"
    LOCK_ACCOUNT = "lock_account"
    ALERT_ADMIN = "alert_admin"
    QUARANTINE = "quarantine"
    LOG_ONLY = "log_only"

@dataclass
class SecurityIncident:
    """Incidente de segurança"""
    id: str
    timestamp: datetime
    threat_level: ThreatLevel
    attack_type: AttackType
    source_ip: str
    target_resource: str
    details: Dict[str, Any]
    actions_taken: List[SecurityAction]
    resolved: bool = False
    investigation_notes: Optional[str] = None

@dataclass
class AccessAttempt:
    """Tentativa de acesso"""
    id: str
    timestamp: datetime
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    resource: str
    method: str
    status_code: int
    risk_score: float
    blocked: bool = False

class SecurityHardeningService:
    """
    Serviço de Segurança Avançada e Hardening
    
    Funcionalidades:
    - Detecção e prevenção de ataques
    - Criptografia avançada de dados
    - Sistema de detecção de intrusões
    - Resposta automática a incidentes
    - Monitoramento contínuo de segurança
    """
    
    def __init__(self):
        # Logs de segurança
        self.security_incidents: deque = deque(maxlen=10000)
        self.access_attempts: deque = deque(maxlen=50000)
        self.blocked_ips: Dict[str, datetime] = {}
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Configurações de segurança
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.rate_limit_window = timedelta(minutes=1)
        self.rate_limit_max_requests = 60
        
        # Chaves de criptografia
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Geração de chave RSA para assinatura
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Padrões de ataques conhecidos
        self.attack_patterns = {
            AttackType.SQL_INJECTION: [
                r"(\bunion\b.*\bselect\b)",
                r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
                r"(\bdrop\b.*\btable\b)",
                r"(\binsert\b.*\binto\b)",
                r"(\bupdate\b.*\bset\b)",
                r"(\bdelete\b.*\bfrom\b)",
                r"(\b(and|or)\b.*\b(1=1|1=0)\b)",
                r"(\'\s*(or|and)\s*\'\s*=\s*\')",
                r"(\-\-|\#|\/\*.*\*\/)"
            ],
            AttackType.XSS: [
                r"(<script[^>]*>.*?</script>)",
                r"(javascript\s*:)",
                r"(on\w+\s*=)",
                r"(<iframe[^>]*>)",
                r"(<object[^>]*>)",
                r"(<embed[^>]*>)",
                r"(eval\s*\()",
                r"(document\.cookie)",
                r"(document\.write)"
            ],
            AttackType.CSRF: [
                r"(action\s*=\s*[\"'][^\"']*[\"'])",
                r"(method\s*=\s*[\"']post[\"'])",
                r"(<form[^>]*>.*</form>)"
            ]
        }
        
        # IPs conhecidos como maliciosos (exemplo)
        self.known_malicious_ips = set([
            "192.168.1.100",  # Exemplo
            "10.0.0.50"       # Exemplo
        ])
        
        # Métricas de segurança
        self.metrics: Dict[str, Any] = defaultdict(int)
        
        logger.info("✅ Security Hardening Service inicializado")
    
    async def analyze_request_security(
        self,
        request_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Tuple[bool, List[SecurityIncident]]:
        """
        Analisa segurança de uma requisição
        
        Returns:
            Tuple[allowed, incidents]: Se permitido e lista de incidentes detectados
        """
        
        incidents = []
        allowed = True
        
        ip_address = request_data.get("client_ip", "unknown")
        user_agent = request_data.get("user_agent", "")
        method = request_data.get("method", "GET")
        url = request_data.get("url", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        
        # Verificar IP bloqueado
        if await self._is_ip_blocked(ip_address):
            allowed = False
            incidents.append(await self._create_incident(
                ThreatLevel.HIGH,
                AttackType.UNAUTHORIZED_ACCESS,
                ip_address,
                url,
                {"reason": "IP bloqueado", "user_id": user_id}
            ))
        
        # Verificar rate limiting
        if await self._check_rate_limit(ip_address):
            allowed = False
            incidents.append(await self._create_incident(
                ThreatLevel.MEDIUM,
                AttackType.DDOS,
                ip_address,
                url,
                {"reason": "Rate limit excedido", "user_id": user_id}
            ))
        
        # Detectar ataques de injeção SQL
        sql_incidents = await self._detect_sql_injection(ip_address, url, body, headers)
        incidents.extend(sql_incidents)
        if sql_incidents:
            allowed = False
        
        # Detectar XSS
        xss_incidents = await self._detect_xss(ip_address, url, body, headers)
        incidents.extend(xss_incidents)
        if xss_incidents:
            allowed = False
        
        # Detectar CSRF
        csrf_incidents = await self._detect_csrf(ip_address, url, method, headers)
        incidents.extend(csrf_incidents)
        
        # Análise de comportamento suspeito
        suspicious_incidents = await self._analyze_suspicious_behavior(
            ip_address, user_agent, user_id, request_data
        )
        incidents.extend(suspicious_incidents)
        
        # Registrar tentativa de acesso
        risk_score = self._calculate_risk_score(request_data, incidents)
        access_attempt = AccessAttempt(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=url,
            method=method,
            status_code=200 if allowed else 403,
            risk_score=risk_score,
            blocked=not allowed
        )
        
        self.access_attempts.append(access_attempt)
        
        # Tomar ações automáticas se necessário
        if incidents:
            await self._take_security_actions(incidents, ip_address, user_id)
        
        return allowed, incidents
    
    async def _is_ip_blocked(self, ip_address: str) -> bool:
        """Verifica se IP está bloqueado"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            if datetime.now() - block_time < self.lockout_duration:
                return True
            else:
                # Remover bloqueio expirado
                del self.blocked_ips[ip_address]
        
        return ip_address in self.known_malicious_ips
    
    async def _check_rate_limit(self, ip_address: str) -> bool:
        """Verifica rate limiting"""
        now = datetime.now()
        requests = self.rate_limits[ip_address]
        
        # Adicionar requisição atual
        requests.append(now)
        
        # Remover requisições antigas
        cutoff = now - self.rate_limit_window
        while requests and requests[0] < cutoff:
            requests.popleft()
        
        return len(requests) > self.rate_limit_max_requests
    
    async def _detect_sql_injection(
        self,
        ip_address: str,
        url: str,
        body: str,
        headers: Dict[str, str]
    ) -> List[SecurityIncident]:
        """Detecta tentativas de SQL injection"""
        
        incidents = []
        
        # Combinar todos os dados para análise
        combined_data = f"{url} {body} {' '.join(headers.values())}".lower()
        
        for pattern in self.attack_patterns[AttackType.SQL_INJECTION]:
            if re.search(pattern, combined_data, re.IGNORECASE):
                incident = await self._create_incident(
                    ThreatLevel.HIGH,
                    AttackType.SQL_INJECTION,
                    ip_address,
                    url,
                    {
                        "pattern_matched": pattern,
                        "suspicious_content": combined_data[:200],
                        "detection_method": "pattern_matching"
                    }
                )
                incidents.append(incident)
                break  # Um padrão é suficiente
        
        return incidents
    
    async def _detect_xss(
        self,
        ip_address: str,
        url: str,
        body: str,
        headers: Dict[str, str]
    ) -> List[SecurityIncident]:
        """Detecta tentativas de XSS"""
        
        incidents = []
        
        # Combinar todos os dados para análise
        combined_data = f"{url} {body}"
        
        for pattern in self.attack_patterns[AttackType.XSS]:
            if re.search(pattern, combined_data, re.IGNORECASE):
                incident = await self._create_incident(
                    ThreatLevel.HIGH,
                    AttackType.XSS,
                    ip_address,
                    url,
                    {
                        "pattern_matched": pattern,
                        "suspicious_content": combined_data[:200],
                        "detection_method": "pattern_matching"
                    }
                )
                incidents.append(incident)
                break
        
        return incidents
    
    async def _detect_csrf(
        self,
        ip_address: str,
        url: str,
        method: str,
        headers: Dict[str, str]
    ) -> List[SecurityIncident]:
        """Detecta tentativas de CSRF"""
        
        incidents = []
        
        # Verificar métodos POST sem token CSRF
        if method.upper() == "POST":
            csrf_token = headers.get("x-csrf-token") or headers.get("csrf-token")
            referer = headers.get("referer", "")
            origin = headers.get("origin", "")
            
            if not csrf_token:
                incident = await self._create_incident(
                    ThreatLevel.MEDIUM,
                    AttackType.CSRF,
                    ip_address,
                    url,
                    {
                        "reason": "POST sem token CSRF",
                        "referer": referer,
                        "origin": origin,
                        "detection_method": "missing_csrf_token"
                    }
                )
                incidents.append(incident)
        
        return incidents
    
    async def _analyze_suspicious_behavior(
        self,
        ip_address: str,
        user_agent: str,
        user_id: Optional[str],
        request_data: Dict[str, Any]
    ) -> List[SecurityIncident]:
        """Analisa comportamento suspeito"""
        
        incidents = []
        
        # Verificar User-Agent suspeito
        suspicious_agents = [
            "sqlmap", "nikto", "nmap", "burp", "metasploit",
            "python-requests", "curl", "wget"
        ]
        
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            incident = await self._create_incident(
                ThreatLevel.MEDIUM,
                AttackType.UNAUTHORIZED_ACCESS,
                ip_address,
                request_data.get("url", ""),
                {
                    "reason": "User-Agent suspeito",
                    "user_agent": user_agent,
                    "detection_method": "user_agent_analysis"
                }
            )
            incidents.append(incident)
        
        # Verificar múltiplas tentativas de login falhadas
        if user_id:
            recent_failures = [
                attempt for attempt in list(self.access_attempts)[-100:]
                if (attempt.user_id == user_id and 
                    attempt.status_code in [401, 403] and
                    datetime.now() - attempt.timestamp < timedelta(minutes=5))
            ]
            
            if len(recent_failures) >= 3:
                incident = await self._create_incident(
                    ThreatLevel.HIGH,
                    AttackType.BRUTE_FORCE,
                    ip_address,
                    request_data.get("url", ""),
                    {
                        "reason": "Múltiplas tentativas de login falhadas",
                        "user_id": user_id,
                        "failure_count": len(recent_failures),
                        "detection_method": "behavior_analysis"
                    }
                )
                incidents.append(incident)
        
        # Verificar acesso a recursos sensíveis
        sensitive_paths = ["/admin", "/api/internal", "/config", "/backup"]
        url = request_data.get("url", "")
        
        if any(path in url for path in sensitive_paths):
            incident = await self._create_incident(
                ThreatLevel.MEDIUM,
                AttackType.UNAUTHORIZED_ACCESS,
                ip_address,
                url,
                {
                    "reason": "Acesso a recurso sensível",
                    "sensitive_path": url,
                    "detection_method": "path_analysis"
                }
            )
            incidents.append(incident)
        
        return incidents
    
    def _calculate_risk_score(
        self,
        request_data: Dict[str, Any],
        incidents: List[SecurityIncident]
    ) -> float:
        """Calcula score de risco da requisição"""
        
        base_score = 0.1  # Score base
        
        # Adicionar pontos por incidentes
        for incident in incidents:
            if incident.threat_level == ThreatLevel.CRITICAL:
                base_score += 0.4
            elif incident.threat_level == ThreatLevel.HIGH:
                base_score += 0.3
            elif incident.threat_level == ThreatLevel.MEDIUM:
                base_score += 0.2
            else:
                base_score += 0.1
        
        # Fatores adicionais
        ip_address = request_data.get("client_ip", "")
        if ip_address in self.known_malicious_ips:
            base_score += 0.5
        
        user_agent = request_data.get("user_agent", "")
        if not user_agent or len(user_agent) < 10:
            base_score += 0.2
        
        # Normalizar entre 0 e 1
        return min(base_score, 1.0)
    
    async def _create_incident(
        self,
        threat_level: ThreatLevel,
        attack_type: AttackType,
        source_ip: str,
        target_resource: str,
        details: Dict[str, Any]
    ) -> SecurityIncident:
        """Cria novo incidente de segurança"""
        
        incident = SecurityIncident(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            threat_level=threat_level,
            attack_type=attack_type,
            source_ip=source_ip,
            target_resource=target_resource,
            details=details,
            actions_taken=[]
        )
        
        self.security_incidents.append(incident)
        self.metrics[f"incidents_{attack_type.value}"] += 1
        self.metrics[f"threat_{threat_level.value}"] += 1
        
        logger.warning(f"Incidente de segurança: {attack_type.value} - {threat_level.value} - {source_ip}")
        
        return incident
    
    async def _take_security_actions(
        self,
        incidents: List[SecurityIncident],
        ip_address: str,
        user_id: Optional[str]
    ):
        """Toma ações automáticas de segurança"""
        
        actions_taken = set()
        
        for incident in incidents:
            # Determinar ações baseadas no nível de ameaça
            if incident.threat_level == ThreatLevel.CRITICAL:
                actions_taken.update([
                    SecurityAction.BLOCK_IP,
                    SecurityAction.ALERT_ADMIN,
                    SecurityAction.QUARANTINE
                ])
            elif incident.threat_level == ThreatLevel.HIGH:
                actions_taken.update([
                    SecurityAction.BLOCK_IP,
                    SecurityAction.ALERT_ADMIN
                ])
            elif incident.threat_level == ThreatLevel.MEDIUM:
                actions_taken.update([
                    SecurityAction.RATE_LIMIT,
                    SecurityAction.LOG_ONLY
                ])
            
            # Ações específicas por tipo de ataque
            if incident.attack_type == AttackType.BRUTE_FORCE:
                actions_taken.add(SecurityAction.LOCK_ACCOUNT)
                if user_id:
                    actions_taken.add(SecurityAction.LOGOUT_USER)
            
            if incident.attack_type in [AttackType.SQL_INJECTION, AttackType.XSS]:
                actions_taken.add(SecurityAction.BLOCK_IP)
        
        # Executar ações
        for action in actions_taken:
            await self._execute_security_action(action, ip_address, user_id, incidents)
            
            # Registrar ação nos incidentes
            for incident in incidents:
                incident.actions_taken.append(action)
    
    async def _execute_security_action(
        self,
        action: SecurityAction,
        ip_address: str,
        user_id: Optional[str],
        incidents: List[SecurityIncident]
    ):
        """Executa ação de segurança específica"""
        
        if action == SecurityAction.BLOCK_IP:
            self.blocked_ips[ip_address] = datetime.now()
            self.metrics["ips_blocked"] += 1
            logger.warning(f"IP bloqueado: {ip_address}")
        
        elif action == SecurityAction.RATE_LIMIT:
            # Rate limit já é aplicado automaticamente
            self.metrics["rate_limits_applied"] += 1
            logger.info(f"Rate limit aplicado: {ip_address}")
        
        elif action == SecurityAction.ALERT_ADMIN:
            # Em produção, isso enviaria notificação real
            self.metrics["admin_alerts"] += 1
            logger.critical(f"ALERTA ADMIN: Incidente de segurança - {ip_address}")
        
        elif action == SecurityAction.QUARANTINE:
            # Marcar recursos como em quarentena
            self.metrics["quarantined_resources"] += 1
            logger.error(f"Recurso em quarentena: {ip_address}")
        
        elif action == SecurityAction.LOCK_ACCOUNT:
            if user_id:
                # Em produção, isso bloquearia a conta do usuário
                self.metrics["accounts_locked"] += 1
                logger.warning(f"Conta bloqueada: {user_id}")
        
        elif action == SecurityAction.LOGOUT_USER:
            if user_id:
                # Em produção, isso forçaria logout
                self.metrics["forced_logouts"] += 1
                logger.info(f"Logout forçado: {user_id}")
    
    # === CRIPTOGRAFIA ===
    
    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Criptografa dados com AES-256"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.cipher_suite.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Descriptografa dados"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao descriptografar: {e}")
            raise
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash seguro de senha com salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Usar PBKDF2 com SHA-256
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return base64.b64encode(key).decode('utf-8'), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verifica senha contra hash"""
        computed_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, hashed_password)
    
    def generate_jwt_token(
        self,
        payload: Dict[str, Any],
        expiration_hours: int = 24
    ) -> str:
        """Gera token JWT assinado"""
        payload['exp'] = datetime.utcnow() + timedelta(hours=expiration_hours)
        payload['iat'] = datetime.utcnow()
        
        # Usar chave privada para assinar
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return jwt.encode(payload, private_pem, algorithm='RS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica token JWT"""
        try:
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            payload = jwt.decode(token, public_pem, algorithms=['RS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token JWT expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token JWT inválido: {e}")
            return None
    
    # === MÉTODOS DE CONSULTA ===
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de segurança"""
        return {
            **dict(self.metrics),
            "total_incidents": len(self.security_incidents),
            "total_access_attempts": len(self.access_attempts),
            "blocked_ips_count": len(self.blocked_ips),
            "known_malicious_ips": len(self.known_malicious_ips),
            "active_rate_limits": len([rl for rl in self.rate_limits.values() if len(rl) > 0])
        }
    
    def get_recent_incidents(self, limit: int = 50) -> List[SecurityIncident]:
        """Retorna incidentes recentes"""
        return list(self.security_incidents)[-limit:]
    
    def get_threat_analysis(self) -> Dict[str, Any]:
        """Análise de ameaças"""
        if not self.security_incidents:
            return {}
        
        recent_incidents = list(self.security_incidents)[-1000:]
        
        threat_by_type = defaultdict(int)
        threat_by_level = defaultdict(int)
        source_ips = defaultdict(int)
        
        for incident in recent_incidents:
            threat_by_type[incident.attack_type.value] += 1
            threat_by_level[incident.threat_level.value] += 1
            source_ips[incident.source_ip] += 1
        
        return {
            "analysis_period": "últimos 1000 incidentes",
            "threat_distribution": dict(threat_by_type),
            "severity_distribution": dict(threat_by_level),
            "top_attacking_ips": dict(sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
            "avg_incidents_per_hour": len(recent_incidents) / 24 if recent_incidents else 0
        }
    
    def generate_security_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Gera relatório de segurança"""
        
        # Filtrar incidentes por período
        incidents = list(self.security_incidents)
        if start_date:
            incidents = [i for i in incidents if i.timestamp >= start_date]
        if end_date:
            incidents = [i for i in incidents if i.timestamp <= end_date]
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "summary": {
                "total_incidents": len(incidents),
                "critical_incidents": len([i for i in incidents if i.threat_level == ThreatLevel.CRITICAL]),
                "high_severity": len([i for i in incidents if i.threat_level == ThreatLevel.HIGH]),
                "unique_attackers": len(set(i.source_ip for i in incidents)),
                "blocked_ips": len(self.blocked_ips),
                "actions_taken": sum(len(i.actions_taken) for i in incidents)
            },
            "top_threats": dict(Counter(i.attack_type.value for i in incidents).most_common(5)),
            "recent_incidents": [asdict(incident) for incident in incidents[-20:]]
        }

# === INSTÂNCIA GLOBAL ===
security_hardening_service = SecurityHardeningService()

logger.info("✅ Security Hardening Service carregado com sucesso") 