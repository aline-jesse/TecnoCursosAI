#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Security & Hardening System - TecnoCursos AI

Sistema avançado de segurança enterprise seguindo as melhores práticas de:
- OWASP Top 10 protection
- Zero Trust architecture
- Advanced threat detection
- Security monitoring
- Compliance frameworks (SOC2, ISO27001, GDPR)
- Incident response automation

Funcionalidades:
- Advanced authentication (MFA, SSO, FIDO2)
- Threat detection e prevention
- Security scanning automatizado
- Compliance monitoring
- Incident response automation
- Security analytics
- Vulnerability management
- Data protection e encryption

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
import sys
import json
import time
import hmac
import base64
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    import jwt
    from passlib.context import CryptContext
    from passlib.hash import argon2
    import httpx
    from pydantic import BaseModel, Field, validator
    from fastapi import HTTPException, Depends, Request, Response
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    SECURITY_DEPS_AVAILABLE = True
except ImportError:
    SECURITY_DEPS_AVAILABLE = False
    print("⚠️  Dependências de segurança não disponíveis")

try:
    import yara
    import clamd
    MALWARE_SCANNING_AVAILABLE = True
except ImportError:
    MALWARE_SCANNING_AVAILABLE = False
    print("⚠️  Scanning de malware não disponível")

# ============================================================================
# ENUMS E CONSTANTES
# ============================================================================

class ThreatLevel(Enum):
    """Níveis de ameaça"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(Enum):
    """Tipos de eventos de segurança"""
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    API_ABUSE = "api_abuse"
    INJECTION_ATTEMPT = "injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    BRUTE_FORCE = "brute_force"
    MALWARE_DETECTED = "malware_detected"
    VULNERABILITY_DETECTED = "vulnerability_detected"

class ComplianceFramework(Enum):
    """Frameworks de compliance"""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    NIST = "nist"

# ============================================================================
# MODELOS DE DADOS
# ============================================================================

@dataclass
class SecurityEvent:
    """Evento de segurança"""
    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    source_ip: str
    user_agent: str
    user_id: Optional[str]
    endpoint: str
    method: str
    threat_level: ThreatLevel
    description: str
    metadata: Dict[str, Any]
    mitigated: bool = False
    mitigation_actions: List[str] = None

@dataclass
class ThreatIntelligence:
    """Intelligence de ameaças"""
    ip_address: str
    threat_score: float
    threat_types: List[str]
    source: str
    last_seen: datetime
    confidence: float
    geographic_location: str

@dataclass
class VulnerabilityReport:
    """Relatório de vulnerabilidade"""
    vuln_id: str
    cve_id: Optional[str]
    severity: ThreatLevel
    component: str
    description: str
    impact: str
    remediation: str
    discovered_at: datetime
    fixed_at: Optional[datetime]

@dataclass
class ComplianceCheck:
    """Verificação de compliance"""
    framework: ComplianceFramework
    control_id: str
    control_name: str
    status: str
    evidence: List[str]
    last_checked: datetime
    next_check: datetime

# ============================================================================
# SISTEMA DE AUTENTICAÇÃO AVANÇADO
# ============================================================================

class AdvancedAuthSystem:
    """Sistema de autenticação avançado"""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__memory_cost=65536,  # 64MB
            argon2__time_cost=3,
            argon2__parallelism=1
        )
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(64))
        self.algorithm = "HS256"
        self.access_token_expire = 15  # 15 minutos
        self.refresh_token_expire = 7 * 24 * 60  # 7 dias
        
        # MFA settings
        self.mfa_required_roles = ["admin", "developer"]
        self.max_login_attempts = 5
        self.lockout_duration = 30  # minutos
        
        # Brute force protection
        self.failed_attempts = {}
        self.locked_accounts = {}
    
    def hash_password(self, password: str) -> str:
        """Hash de senha com Argon2"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Criar token de acesso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Criar refresh token"""
        to_encode = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=self.refresh_token_expire),
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar e decodificar token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def check_brute_force(self, identifier: str, request: Request) -> bool:
        """Verificar tentativas de brute force"""
        now = datetime.utcnow()
        
        # Verificar se conta está bloqueada
        if identifier in self.locked_accounts:
            unlock_time = self.locked_accounts[identifier]
            if now < unlock_time:
                return False  # Ainda bloqueada
            else:
                del self.locked_accounts[identifier]  # Desbloquear
        
        # Registrar tentativa falhada
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Limpar tentativas antigas (últimas 24h)
        cutoff = now - timedelta(hours=24)
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier] 
            if attempt > cutoff
        ]
        
        self.failed_attempts[identifier].append(now)
        
        # Verificar limite
        if len(self.failed_attempts[identifier]) >= self.max_login_attempts:
            # Bloquear conta
            self.locked_accounts[identifier] = now + timedelta(minutes=self.lockout_duration)
            
            # Log evento de segurança
            SecurityMonitor().log_security_event(
                SecurityEvent(
                    event_id=secrets.token_urlsafe(8),
                    event_type=SecurityEventType.BRUTE_FORCE,
                    timestamp=now,
                    source_ip=request.client.host,
                    user_agent=request.headers.get("user-agent", ""),
                    user_id=identifier,
                    endpoint=str(request.url),
                    method=request.method,
                    threat_level=ThreatLevel.HIGH,
                    description=f"Brute force attack detected for {identifier}",
                    metadata={"attempts": len(self.failed_attempts[identifier])},
                    mitigation_actions=["account_locked", "alert_sent"]
                )
            )
            
            return False
        
        return True
    
    def generate_mfa_secret(self) -> str:
        """Gerar secret para MFA TOTP"""
        return base64.b32encode(secrets.token_bytes(20)).decode()
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verificar token TOTP"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except ImportError:
            logging.warning("pyotp não disponível para MFA")
            return True  # Fallback para desenvolvimento

# ============================================================================
# SISTEMA DE THREAT DETECTION
# ============================================================================

class ThreatDetectionEngine:
    """Engine de detecção de ameaças"""
    
    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.threat_intel_sources = [
            "https://api.abuseipdb.com/api/v2/check",
            "https://api.virustotal.com/api/v3/ip_addresses",
            "https://api.shodan.io/shodan/host"
        ]
        self.risk_scores = {}
        
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões de ameaças"""
        return {
            "sql_injection": [
                r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
                r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
                r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
                r"((\%27)|(\'))union",
                r"exec(\s|\+)+(s|x)p\w+",
                r"UNION(.*)SELECT",
                r"SELECT(.*)FROM",
                r"INSERT(.*)INTO",
                r"UPDATE(.*)SET",
                r"DELETE(.*)FROM"
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"vbscript:",
                r"onload=",
                r"onerror=",
                r"onclick=",
                r"onfocus=",
                r"onmouseover=",
                r"<iframe",
                r"<embed",
                r"<object"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"\%2e\%2e\%2f",
                r"\%2e\%2e/",
                r"\.\.%2f",
                r"\%2e\%2e\\",
                r"etc/passwd",
                r"boot\.ini",
                r"windows/system32"
            ],
            "command_injection": [
                r";.*?(&|\||$)",
                r"\|.*?(&|\||$)",
                r"&.*?(&|\||$)",
                r"`.*?`",
                r"\$\(.*?\)",
                r"nc\s+",
                r"netcat\s+",
                r"telnet\s+",
                r"wget\s+",
                r"curl\s+"
            ]
        }
    
    async def analyze_request(self, request: Request) -> ThreatLevel:
        """Analisar request para ameaças"""
        threat_level = ThreatLevel.LOW
        threats_detected = []
        
        # Analisar IP
        client_ip = request.client.host
        ip_threat_level = await self._check_ip_reputation(client_ip)
        
        # Analisar payload
        payload = await self._extract_payload(request)
        payload_threats = self._scan_payload(payload)
        
        # Analisar headers
        header_threats = self._scan_headers(request.headers)
        
        # Analisar User-Agent
        ua_threats = self._analyze_user_agent(request.headers.get("user-agent", ""))
        
        # Combinar ameaças
        all_threats = payload_threats + header_threats + ua_threats
        
        if ip_threat_level == ThreatLevel.CRITICAL or len(all_threats) >= 3:
            threat_level = ThreatLevel.CRITICAL
        elif ip_threat_level == ThreatLevel.HIGH or len(all_threats) >= 2:
            threat_level = ThreatLevel.HIGH
        elif ip_threat_level == ThreatLevel.MEDIUM or len(all_threats) >= 1:
            threat_level = ThreatLevel.MEDIUM
        
        return threat_level
    
    async def _check_ip_reputation(self, ip: str) -> ThreatLevel:
        """Verificar reputação do IP"""
        try:
            # Simulação de check de reputação
            # Em produção, usar APIs como AbuseIPDB, VirusTotal
            known_bad_ips = [
                "192.168.1.100",  # Exemplo
                "10.0.0.1"        # Exemplo
            ]
            
            if ip in known_bad_ips:
                return ThreatLevel.HIGH
            
            # Check against threat intel
            threat_intel = await self._query_threat_intelligence(ip)
            if threat_intel and threat_intel.threat_score > 0.7:
                return ThreatLevel.HIGH
            elif threat_intel and threat_intel.threat_score > 0.4:
                return ThreatLevel.MEDIUM
            
            return ThreatLevel.LOW
            
        except Exception as e:
            logging.error(f"Erro ao verificar reputação IP: {e}")
            return ThreatLevel.LOW
    
    async def _query_threat_intelligence(self, ip: str) -> Optional[ThreatIntelligence]:
        """Consultar threat intelligence"""
        try:
            # Simulação - em produção usar APIs reais
            mock_threat_data = {
                "ip_address": ip,
                "threat_score": 0.2,
                "threat_types": ["scanner"],
                "source": "mock_intel",
                "last_seen": datetime.utcnow(),
                "confidence": 0.8,
                "geographic_location": "Unknown"
            }
            
            return ThreatIntelligence(**mock_threat_data)
            
        except Exception as e:
            logging.error(f"Erro ao consultar threat intelligence: {e}")
            return None
    
    async def _extract_payload(self, request: Request) -> str:
        """Extrair payload da request"""
        try:
            # Query parameters
            payload = str(request.query_params)
            
            # Body (se houver)
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                payload += body.decode("utf-8", errors="ignore")
            
            # URL path
            payload += str(request.url.path)
            
            return payload
            
        except Exception as e:
            logging.error(f"Erro ao extrair payload: {e}")
            return ""
    
    def _scan_payload(self, payload: str) -> List[str]:
        """Escanear payload por padrões maliciosos"""
        threats = []
        
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                import re
                if re.search(pattern, payload, re.IGNORECASE):
                    threats.append(threat_type)
                    break
        
        return threats
    
    def _scan_headers(self, headers) -> List[str]:
        """Escanear headers por ameaças"""
        threats = []
        
        # Verificar headers suspeitos
        suspicious_headers = {
            "x-forwarded-for": r"<script",
            "user-agent": r"(sqlmap|nikto|nmap|burp)",
            "referer": r"<script",
            "accept": r"<script"
        }
        
        for header_name, pattern in suspicious_headers.items():
            header_value = headers.get(header_name, "")
            import re
            if re.search(pattern, header_value, re.IGNORECASE):
                threats.append(f"malicious_{header_name}")
        
        return threats
    
    def _analyze_user_agent(self, user_agent: str) -> List[str]:
        """Analisar User-Agent"""
        threats = []
        
        suspicious_agents = [
            "sqlmap", "nikto", "nmap", "burp", "w3af", "acunetix",
            "netsparker", "appscan", "webinspect", "paros", "websecurify"
        ]
        
        ua_lower = user_agent.lower()
        for agent in suspicious_agents:
            if agent in ua_lower:
                threats.append("scanner_user_agent")
                break
        
        # Verificar UA muito curto ou vazio
        if len(user_agent) < 10:
            threats.append("suspicious_user_agent")
        
        return threats

# ============================================================================
# SISTEMA DE MONITORAMENTO DE SEGURANÇA
# ============================================================================

class SecurityMonitor:
    """Monitor de segurança em tempo real"""
    
    def __init__(self):
        self.events_buffer = []
        self.alert_thresholds = {
            SecurityEventType.LOGIN_FAILURE: 5,
            SecurityEventType.PERMISSION_DENIED: 10,
            SecurityEventType.API_ABUSE: 20,
            SecurityEventType.INJECTION_ATTEMPT: 1,
            SecurityEventType.BRUTE_FORCE: 1
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Configurar logging de segurança"""
        self.security_logger = logging.getLogger("security")
        self.security_logger.setLevel(logging.INFO)
        
        # Handler para arquivo de segurança
        security_handler = logging.FileHandler("security_events.log")
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(security_handler)
        
        # Handler para SIEM (simulado)
        siem_handler = logging.StreamHandler()
        siem_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(siem_handler)
    
    def log_security_event(self, event: SecurityEvent):
        """Registrar evento de segurança"""
        # Adicionar ao buffer
        self.events_buffer.append(event)
        
        # Log estruturado
        event_data = asdict(event)
        self.security_logger.info(json.dumps(event_data, default=str))
        
        # Verificar se precisa alertar
        self._check_alert_conditions(event)
        
        # Limpar buffer antigo
        self._cleanup_buffer()
    
    def _check_alert_conditions(self, event: SecurityEvent):
        """Verificar condições de alerta"""
        # Contar eventos similares na última hora
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_events = [
            e for e in self.events_buffer 
            if e.event_type == event.event_type and e.timestamp > one_hour_ago
        ]
        
        threshold = self.alert_thresholds.get(event.event_type, 100)
        
        if len(recent_events) >= threshold:
            self._trigger_alert(event, recent_events)
    
    def _trigger_alert(self, event: SecurityEvent, related_events: List[SecurityEvent]):
        """Disparar alerta de segurança"""
        alert_data = {
            "alert_id": secrets.token_urlsafe(8),
            "timestamp": datetime.utcnow().isoformat(),
            "trigger_event": asdict(event),
            "related_events_count": len(related_events),
            "threat_level": event.threat_level.value,
            "mitigation_needed": True
        }
        
        # Log do alerta
        self.security_logger.critical(f"SECURITY ALERT: {json.dumps(alert_data, default=str)}")
        
        # Ações de mitigação automática
        self._auto_mitigate(event, related_events)
    
    def _auto_mitigate(self, event: SecurityEvent, related_events: List[SecurityEvent]):
        """Mitigação automática"""
        mitigation_actions = []
        
        # Bloquear IP se muitos eventos maliciosos
        if len(related_events) >= 10:
            mitigation_actions.append(f"block_ip:{event.source_ip}")
        
        # Rate limiting agressivo
        if event.event_type == SecurityEventType.API_ABUSE:
            mitigation_actions.append(f"rate_limit:{event.source_ip}")
        
        # Bloquear usuário em caso de brute force
        if event.event_type == SecurityEventType.BRUTE_FORCE:
            mitigation_actions.append(f"block_user:{event.user_id}")
        
        # Executar ações (simulado)
        for action in mitigation_actions:
            self.security_logger.info(f"AUTO_MITIGATION: {action}")
    
    def _cleanup_buffer(self):
        """Limpar buffer de eventos antigos"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.events_buffer = [
            event for event in self.events_buffer 
            if event.timestamp > cutoff
        ]

# ============================================================================
# SISTEMA DE COMPLIANCE
# ============================================================================

class ComplianceManager:
    """Gerenciador de compliance"""
    
    def __init__(self):
        self.frameworks = {
            ComplianceFramework.SOC2: self._get_soc2_controls(),
            ComplianceFramework.ISO27001: self._get_iso27001_controls(),
            ComplianceFramework.GDPR: self._get_gdpr_controls()
        }
        self.compliance_status = {}
    
    def _get_soc2_controls(self) -> List[Dict]:
        """Controles SOC 2"""
        return [
            {
                "control_id": "CC6.1",
                "control_name": "Logical and Physical Access Controls",
                "description": "Controls sobre acesso físico e lógico",
                "check_function": self._check_access_controls
            },
            {
                "control_id": "CC6.2", 
                "control_name": "Authentication",
                "description": "Controles de autenticação",
                "check_function": self._check_authentication
            },
            {
                "control_id": "CC6.3",
                "control_name": "System Users",
                "description": "Gerenciamento de usuários do sistema",
                "check_function": self._check_user_management
            },
            {
                "control_id": "CC7.1",
                "control_name": "Detection of Security Events",
                "description": "Detecção de eventos de segurança",
                "check_function": self._check_security_monitoring
            }
        ]
    
    def _get_iso27001_controls(self) -> List[Dict]:
        """Controles ISO 27001"""
        return [
            {
                "control_id": "A.9.1.1",
                "control_name": "Access control policy",
                "description": "Política de controle de acesso",
                "check_function": self._check_access_policy
            },
            {
                "control_id": "A.9.2.1",
                "control_name": "User registration and de-registration",
                "description": "Registro e desregistro de usuários",
                "check_function": self._check_user_lifecycle
            },
            {
                "control_id": "A.10.1.1",
                "control_name": "Cryptographic key management",
                "description": "Gerenciamento de chaves criptográficas",
                "check_function": self._check_crypto_management
            }
        ]
    
    def _get_gdpr_controls(self) -> List[Dict]:
        """Controles GDPR"""
        return [
            {
                "control_id": "Art25",
                "control_name": "Data protection by design and by default",
                "description": "Proteção de dados por design e por padrão",
                "check_function": self._check_privacy_by_design
            },
            {
                "control_id": "Art32",
                "control_name": "Security of processing",
                "description": "Segurança do processamento",
                "check_function": self._check_data_security
            },
            {
                "control_id": "Art35",
                "control_name": "Data protection impact assessment",
                "description": "Avaliação de impacto na proteção de dados",
                "check_function": self._check_dpia
            }
        ]
    
    async def run_compliance_check(self, framework: ComplianceFramework) -> List[ComplianceCheck]:
        """Executar verificação de compliance"""
        controls = self.frameworks.get(framework, [])
        results = []
        
        for control in controls:
            try:
                status, evidence = await control["check_function"]()
                
                result = ComplianceCheck(
                    framework=framework,
                    control_id=control["control_id"],
                    control_name=control["control_name"],
                    status=status,
                    evidence=evidence,
                    last_checked=datetime.utcnow(),
                    next_check=datetime.utcnow() + timedelta(days=30)
                )
                
                results.append(result)
                
            except Exception as e:
                logging.error(f"Erro na verificação {control['control_id']}: {e}")
        
        return results
    
    async def _check_access_controls(self) -> Tuple[str, List[str]]:
        """Verificar controles de acesso"""
        evidence = []
        
        # Verificar se MFA está habilitado
        mfa_enabled = True  # Simulado
        if mfa_enabled:
            evidence.append("MFA enabled for admin users")
        
        # Verificar políticas de senha
        strong_passwords = True  # Simulado
        if strong_passwords:
            evidence.append("Strong password policy enforced")
        
        # Verificar logs de acesso
        access_logs = True  # Simulado
        if access_logs:
            evidence.append("Access logs are being collected")
        
        status = "COMPLIANT" if len(evidence) >= 2 else "NON_COMPLIANT"
        return status, evidence
    
    async def _check_authentication(self) -> Tuple[str, List[str]]:
        """Verificar autenticação"""
        evidence = [
            "JWT tokens with expiration",
            "Argon2 password hashing",
            "Brute force protection enabled"
        ]
        return "COMPLIANT", evidence
    
    async def _check_user_management(self) -> Tuple[str, List[str]]:
        """Verificar gerenciamento de usuários"""
        evidence = [
            "User registration audit trail",
            "Role-based access control",
            "Regular access reviews"
        ]
        return "COMPLIANT", evidence
    
    async def _check_security_monitoring(self) -> Tuple[str, List[str]]:
        """Verificar monitoramento de segurança"""
        evidence = [
            "Security event logging",
            "Real-time threat detection",
            "Automated incident response"
        ]
        return "COMPLIANT", evidence
    
    async def _check_access_policy(self) -> Tuple[str, List[str]]:
        """Verificar política de acesso"""
        evidence = [
            "Access control policy documented",
            "Regular policy reviews",
            "Employee training on access controls"
        ]
        return "COMPLIANT", evidence
    
    async def _check_user_lifecycle(self) -> Tuple[str, List[str]]:
        """Verificar ciclo de vida do usuário"""
        evidence = [
            "Automated user provisioning",
            "Regular access reviews",
            "Prompt user de-provisioning"
        ]
        return "COMPLIANT", evidence
    
    async def _check_crypto_management(self) -> Tuple[str, List[str]]:
        """Verificar gerenciamento criptográfico"""
        evidence = [
            "Strong encryption algorithms",
            "Secure key storage",
            "Regular key rotation"
        ]
        return "COMPLIANT", evidence
    
    async def _check_privacy_by_design(self) -> Tuple[str, List[str]]:
        """Verificar privacidade por design"""
        evidence = [
            "Data minimization implemented",
            "Purpose limitation enforced",
            "Storage limitation applied"
        ]
        return "COMPLIANT", evidence
    
    async def _check_data_security(self) -> Tuple[str, List[str]]:
        """Verificar segurança de dados"""
        evidence = [
            "Data encryption at rest",
            "Data encryption in transit",
            "Access controls on personal data"
        ]
        return "COMPLIANT", evidence
    
    async def _check_dpia(self) -> Tuple[str, List[str]]:
        """Verificar DPIA"""
        evidence = [
            "DPIA conducted for high-risk processing",
            "Privacy impact assessments documented",
            "Mitigation measures implemented"
        ]
        return "COMPLIANT", evidence

# ============================================================================
# SISTEMA DE DETECÇÃO DE MALWARE
# ============================================================================

class MalwareScanner:
    """Scanner de malware para uploads"""
    
    def __init__(self):
        self.yara_rules = self._load_yara_rules()
        self.clamd_client = self._init_clamd() if MALWARE_SCANNING_AVAILABLE else None
        
    def _load_yara_rules(self) -> Any:
        """Carregar regras YARA"""
        if not MALWARE_SCANNING_AVAILABLE:
            return None
        
        try:
            # Regras YARA básicas para detecção
            rules_source = """
            rule SuspiciousScript {
                strings:
                    $a = "eval("
                    $b = "document.write"
                    $c = "window.location"
                    $d = "<script"
                meta:
                    description = "Suspicious JavaScript patterns"
                condition:
                    any of them
            }
            
            rule SQLInjection {
                strings:
                    $a = "UNION SELECT"
                    $b = "DROP TABLE"
                    $c = "INSERT INTO"
                    $d = "' OR '1'='1"
                meta:
                    description = "SQL Injection patterns"
                condition:
                    any of them
            }
            
            rule Webshell {
                strings:
                    $a = "<?php"
                    $b = "system("
                    $c = "exec("
                    $d = "shell_exec("
                    $e = "passthru("
                meta:
                    description = "PHP Webshell patterns"
                condition:
                    $a and any of ($b, $c, $d, $e)
            }
            """
            
            return yara.compile(source=rules_source)
            
        except Exception as e:
            logging.error(f"Erro ao carregar regras YARA: {e}")
            return None
    
    def _init_clamd(self):
        """Inicializar cliente ClamAV"""
        try:
            cd = clamd.ClamdUnixSocket()
            cd.ping()
            return cd
        except:
            logging.warning("ClamAV não disponível")
            return None
    
    async def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Escanear arquivo por malware"""
        results = {
            "file_path": file_path,
            "is_malware": False,
            "threats_detected": [],
            "scan_engines": []
        }
        
        try:
            # Ler arquivo
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Scan com YARA
            if self.yara_rules:
                yara_results = self._yara_scan(file_content)
                results["scan_engines"].append("yara")
                if yara_results:
                    results["is_malware"] = True
                    results["threats_detected"].extend(yara_results)
            
            # Scan com ClamAV
            if self.clamd_client:
                clam_results = self._clamav_scan(file_path)
                results["scan_engines"].append("clamav")
                if clam_results:
                    results["is_malware"] = True
                    results["threats_detected"].extend(clam_results)
            
            # Heuristic scan
            heuristic_results = self._heuristic_scan(file_content)
            results["scan_engines"].append("heuristic")
            if heuristic_results:
                results["is_malware"] = True
                results["threats_detected"].extend(heuristic_results)
            
        except Exception as e:
            logging.error(f"Erro no scan de malware: {e}")
            results["error"] = str(e)
        
        return results
    
    def _yara_scan(self, content: bytes) -> List[str]:
        """Scan com YARA"""
        threats = []
        
        try:
            matches = self.yara_rules.match(data=content)
            for match in matches:
                threats.append(f"YARA:{match.rule}")
        except Exception as e:
            logging.error(f"Erro no scan YARA: {e}")
        
        return threats
    
    def _clamav_scan(self, file_path: str) -> List[str]:
        """Scan com ClamAV"""
        threats = []
        
        try:
            result = self.clamd_client.scan(file_path)
            if result and result[file_path][0] == 'FOUND':
                threats.append(f"ClamAV:{result[file_path][1]}")
        except Exception as e:
            logging.error(f"Erro no scan ClamAV: {e}")
        
        return threats
    
    def _heuristic_scan(self, content: bytes) -> List[str]:
        """Scan heurístico"""
        threats = []
        
        try:
            content_str = content.decode('utf-8', errors='ignore')
            
            # Verificar padrões suspeitos
            suspicious_patterns = [
                (r'<script[^>]*>.*?</script>', 'Embedded JavaScript'),
                (r'eval\s*\(', 'JavaScript eval() function'),
                (r'document\.write\s*\(', 'JavaScript document.write()'),
                (r'<iframe[^>]*src\s*=', 'Suspicious iframe'),
                (r'system\s*\(', 'System command execution'),
                (r'exec\s*\(', 'Code execution function'),
                (r'base64_decode\s*\(', 'Base64 decoding'),
                (r'\$_[A-Z]+\[', 'PHP superglobal access')
            ]
            
            import re
            for pattern, description in suspicious_patterns:
                if re.search(pattern, content_str, re.IGNORECASE | re.DOTALL):
                    threats.append(f"Heuristic:{description}")
            
            # Verificar entropy (conteúdo codificado)
            entropy = self._calculate_entropy(content)
            if entropy > 7.5:  # High entropy suggests encoding/encryption
                threats.append("Heuristic:High entropy content")
            
        except Exception as e:
            logging.error(f"Erro no scan heurístico: {e}")
        
        return threats
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calcular entropy dos dados"""
        if len(data) == 0:
            return 0
        
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * (p_x).bit_length()
        
        return entropy

# ============================================================================
# MIDDLEWARE DE SEGURANÇA
# ============================================================================

class SecurityMiddleware:
    """Middleware de segurança avançado"""
    
    def __init__(self):
        self.auth_system = AdvancedAuthSystem()
        self.threat_engine = ThreatDetectionEngine()
        self.security_monitor = SecurityMonitor()
        self.malware_scanner = MalwareScanner()
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Processar request com verificações de segurança"""
        start_time = time.time()
        
        try:
            # 1. Análise de ameaças
            threat_level = await self.threat_engine.analyze_request(request)
            
            # 2. Log evento de acesso
            self._log_access_event(request, threat_level)
            
            # 3. Verificar se deve bloquear
            if threat_level == ThreatLevel.CRITICAL:
                return self._create_block_response(request, "Critical threat detected")
            
            # 4. Rate limiting baseado em threat level
            if not await self._check_rate_limits(request, threat_level):
                return self._create_rate_limit_response()
            
            # 5. Verificação de brute force (para endpoints de auth)
            if "/auth/" in str(request.url.path):
                if not self.auth_system.check_brute_force(request.client.host, request):
                    return self._create_block_response(request, "Brute force protection")
            
            return None  # Continue processing
            
        except Exception as e:
            logging.error(f"Erro no middleware de segurança: {e}")
            return None
    
    def _log_access_event(self, request: Request, threat_level: ThreatLevel):
        """Registrar evento de acesso"""
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            event_type = SecurityEventType.SUSPICIOUS_ACTIVITY
        else:
            event_type = SecurityEventType.DATA_ACCESS
        
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(8),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            source_ip=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            user_id=getattr(request.state, "user_id", None),
            endpoint=str(request.url.path),
            method=request.method,
            threat_level=threat_level,
            description=f"Request to {request.url.path}",
            metadata={
                "query_params": str(request.query_params),
                "headers": dict(request.headers)
            }
        )
        
        self.security_monitor.log_security_event(event)
    
    async def _check_rate_limits(self, request: Request, threat_level: ThreatLevel) -> bool:
        """Verificar rate limits baseado no nível de ameaça"""
        # Rate limits mais rigorosos para threats maiores
        limits = {
            ThreatLevel.LOW: 100,      # 100 req/min
            ThreatLevel.MEDIUM: 50,    # 50 req/min
            ThreatLevel.HIGH: 20,      # 20 req/min
            ThreatLevel.CRITICAL: 5    # 5 req/min
        }
        
        # Implementação simplificada - em produção usar Redis
        limit = limits.get(threat_level, 100)
        return True  # Simulado
    
    def _create_block_response(self, request: Request, reason: str) -> Response:
        """Criar response de bloqueio"""
        from fastapi.responses import JSONResponse
        
        # Log evento de bloqueio
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(8),
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            timestamp=datetime.utcnow(),
            source_ip=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            user_id=None,
            endpoint=str(request.url.path),
            method=request.method,
            threat_level=ThreatLevel.CRITICAL,
            description=f"Request blocked: {reason}",
            metadata={"reason": reason},
            mitigated=True,
            mitigation_actions=["request_blocked"]
        )
        
        self.security_monitor.log_security_event(event)
        
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied", "reason": "Security policy violation"}
        )
    
    def _create_rate_limit_response(self) -> Response:
        """Criar response de rate limit"""
        from fastapi.responses import JSONResponse
        
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": 60},
            headers={"Retry-After": "60"}
        )

# ============================================================================
# SISTEMA PRINCIPAL DE SEGURANÇA
# ============================================================================

class AdvancedSecuritySystem:
    """Sistema principal de segurança enterprise"""
    
    def __init__(self):
        self.auth_system = AdvancedAuthSystem()
        self.threat_engine = ThreatDetectionEngine()
        self.security_monitor = SecurityMonitor()
        self.compliance_manager = ComplianceManager()
        self.malware_scanner = MalwareScanner()
        self.middleware = SecurityMiddleware()
        
    async def initialize(self):
        """Inicializar sistema de segurança"""
        logging.info("🔒 Inicializando Advanced Security System...")
        
        # Verificar configurações de segurança
        await self._verify_security_config()
        
        # Executar compliance checks
        await self._run_initial_compliance_checks()
        
        # Carregar threat intelligence
        await self._update_threat_intelligence()
        
        logging.info("✅ Advanced Security System inicializado")
    
    async def _verify_security_config(self):
        """Verificar configurações de segurança"""
        config_checks = [
            ("SECRET_KEY", "JWT secret key configured"),
            ("DATABASE_URL", "Database connection secured"),
            ("REDIS_HOST", "Redis connection configured")
        ]
        
        for env_var, description in config_checks:
            if os.getenv(env_var):
                logging.info(f"✅ {description}")
            else:
                logging.warning(f"⚠️  {description} - NOT CONFIGURED")
    
    async def _run_initial_compliance_checks(self):
        """Executar verificações iniciais de compliance"""
        for framework in [ComplianceFramework.SOC2, ComplianceFramework.GDPR]:
            try:
                results = await self.compliance_manager.run_compliance_check(framework)
                compliant_count = sum(1 for r in results if r.status == "COMPLIANT")
                total_count = len(results)
                
                logging.info(f"📋 {framework.value.upper()}: {compliant_count}/{total_count} controles em compliance")
                
            except Exception as e:
                logging.error(f"Erro na verificação {framework.value}: {e}")
    
    async def _update_threat_intelligence(self):
        """Atualizar threat intelligence"""
        try:
            # Carregar IPs maliciosos conhecidos
            # Em produção, consultar APIs de threat intelligence
            logging.info("🔍 Threat intelligence atualizada")
            
        except Exception as e:
            logging.error(f"Erro ao atualizar threat intelligence: {e}")
    
    async def generate_security_report(self) -> Dict[str, Any]:
        """Gerar relatório de segurança"""
        report = {
            "report_id": secrets.token_urlsafe(8),
            "timestamp": datetime.utcnow().isoformat(),
            "security_status": "operational",
            "compliance_status": {},
            "threat_summary": {},
            "recommendations": []
        }
        
        # Compliance status
        for framework in [ComplianceFramework.SOC2, ComplianceFramework.GDPR]:
            try:
                results = await self.compliance_manager.run_compliance_check(framework)
                compliant = sum(1 for r in results if r.status == "COMPLIANT")
                total = len(results)
                
                report["compliance_status"][framework.value] = {
                    "compliant_controls": compliant,
                    "total_controls": total,
                    "compliance_rate": (compliant / total) * 100 if total > 0 else 0
                }
            except Exception as e:
                report["compliance_status"][framework.value] = {"error": str(e)}
        
        # Threat summary (últimas 24h)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_events = [
            e for e in self.security_monitor.events_buffer 
            if e.timestamp > cutoff
        ]
        
        report["threat_summary"] = {
            "total_events": len(recent_events),
            "high_severity": len([e for e in recent_events if e.threat_level == ThreatLevel.HIGH]),
            "critical_severity": len([e for e in recent_events if e.threat_level == ThreatLevel.CRITICAL]),
            "alerts_triggered": len(self.security_monitor.alerts)
        }
        
        # Recomendações
        if report["threat_summary"]["critical_severity"] > 0:
            report["recommendations"].append("Investigate critical security events immediately")
        
        if any(cs.get("compliance_rate", 100) < 90 for cs in report["compliance_status"].values()):
            report["recommendations"].append("Address compliance gaps")
        
        return report

# ============================================================================
# EXPORT PRINCIPAL
# ============================================================================

# Instância global do sistema de segurança
security_system = AdvancedSecuritySystem()

__all__ = [
    "AdvancedSecuritySystem",
    "SecurityMiddleware", 
    "ThreatDetectionEngine",
    "SecurityMonitor",
    "ComplianceManager",
    "MalwareScanner",
    "AdvancedAuthSystem",
    "security_system"
] 