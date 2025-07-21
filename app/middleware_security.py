"""
Middleware de segurança avançado para TecnoCursos AI
Inclui rate limiting, proteção CORS, validação JWT, anti-bot e monitoramento de segurança
"""

import time
import json
import hashlib
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from collections import defaultdict, deque
import asyncio
import re
import base64
from urllib.parse import urlparse

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
from passlib.context import CryptContext
import user_agents

from app.config import get_settings
from app.logger import get_logger, log_security_event, log_performance_metric
from app.database import get_db
from app.models import User

settings = get_settings()
logger = get_logger("security_middleware")

class SecurityMetrics:
    """Coletor de métricas de segurança"""
    
    def __init__(self):
        self.blocked_requests = 0
        self.rate_limited_requests = 0
        self.suspicious_activity = 0
        self.failed_auth_attempts = 0
        self.bot_requests = 0
        self.security_events = []
    
    def record_blocked_request(self, reason: str, ip: str):
        """Registrar requisição bloqueada"""
        self.blocked_requests += 1
        self.security_events.append({
            'type': 'blocked_request',
            'reason': reason,
            'ip': ip,
            'timestamp': datetime.now().isoformat()
        })
        
        # Manter apenas últimos 1000 eventos
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def record_rate_limit(self, ip: str):
        """Registrar rate limit aplicado"""
        self.rate_limited_requests += 1
        self.record_blocked_request('rate_limit', ip)
    
    def record_suspicious_activity(self, activity: str, ip: str):
        """Registrar atividade suspeita"""
        self.suspicious_activity += 1
        self.record_blocked_request(f'suspicious: {activity}', ip)
    
    def record_failed_auth(self, ip: str):
        """Registrar falha de autenticação"""
        self.failed_auth_attempts += 1
        self.record_blocked_request('failed_auth', ip)
    
    def record_bot_request(self, ip: str, user_agent: str):
        """Registrar requisição de bot"""
        self.bot_requests += 1
        self.record_blocked_request(f'bot: {user_agent[:50]}', ip)

# Instância global de métricas
security_metrics = SecurityMetrics()

class RateLimiter:
    """Sistema de rate limiting com sliding window"""
    
    def __init__(self):
        # Janelas deslizantes por IP
        self.windows: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Configurações de rate limit por endpoint
        self.limits = {
            'default': {'requests': 100, 'window': 60},  # 100 req/min
            'auth': {'requests': 10, 'window': 60},      # 10 req/min para auth
            'upload': {'requests': 20, 'window': 60},    # 20 uploads/min
            'search': {'requests': 50, 'window': 60},    # 50 buscas/min
            'api': {'requests': 200, 'window': 60},      # 200 API calls/min
        }
        
        # IPs em blacklist temporária
        self.blacklisted_ips: Dict[str, datetime] = {}
        
        # IPs em whitelist
        self.whitelisted_ips: Set[str] = {
            '127.0.0.1',
            '::1',
            '10.0.0.0/8',
            '172.16.0.0/12',
            '192.168.0.0/16'
        }
    
    def _get_limit_key(self, path: str) -> str:
        """Determinar tipo de limite baseado no path"""
        if '/auth/' in path or '/login' in path:
            return 'auth'
        elif '/upload' in path:
            return 'upload'
        elif '/search' in path:
            return 'search'
        elif '/api/' in path:
            return 'api'
        else:
            return 'default'
    
    def _is_whitelisted(self, ip: str) -> bool:
        """Verificar se IP está na whitelist"""
        try:
            client_ip = ipaddress.ip_address(ip)
            for whitelist_entry in self.whitelisted_ips:
                if '/' in whitelist_entry:
                    if client_ip in ipaddress.ip_network(whitelist_entry):
                        return True
                elif str(client_ip) == whitelist_entry:
                    return True
            return False
        except:
            return False
    
    def is_allowed(self, ip: str, path: str) -> tuple[bool, Optional[str]]:
        """Verificar se requisição é permitida"""
        # Verificar whitelist
        if self._is_whitelisted(ip):
            return True, None
        
        # Verificar blacklist temporária
        if ip in self.blacklisted_ips:
            if datetime.now() < self.blacklisted_ips[ip]:
                return False, "IP temporariamente bloqueado"
            else:
                del self.blacklisted_ips[ip]
        
        # Determinar limite
        limit_key = self._get_limit_key(path)
        limit_config = self.limits[limit_key]
        
        now = time.time()
        window_start = now - limit_config['window']
        
        # Limpar entradas antigas da janela
        client_window = self.windows[ip]
        while client_window and client_window[0] < window_start:
            client_window.popleft()
        
        # Verificar limite
        if len(client_window) >= limit_config['requests']:
            # Adicionar à blacklist por 5 minutos na terceira violação consecutiva
            if len(client_window) >= limit_config['requests'] * 3:
                self.blacklisted_ips[ip] = datetime.now() + timedelta(minutes=5)
                logger.warning(f"IP {ip} blacklisted por excesso de requisições")
            
            return False, f"Rate limit excedido: {limit_config['requests']} req/{limit_config['window']}s"
        
        # Adicionar requisição atual
        client_window.append(now)
        return True, None
    
    def cleanup_old_entries(self):
        """Limpar entradas antigas para economizar memória"""
        cutoff = time.time() - 3600  # 1 hora
        
        for ip in list(self.windows.keys()):
            window = self.windows[ip]
            while window and window[0] < cutoff:
                window.popleft()
            
            if not window:
                del self.windows[ip]

class BotDetector:
    """Detector de bots e crawlers"""
    
    def __init__(self):
        # User agents conhecidos de bots
        self.bot_patterns = [
            r'googlebot',
            r'bingbot',
            r'slurp',
            r'crawler',
            r'spider',
            r'bot\b',
            r'curl',
            r'wget',
            r'python-requests',
            r'scrapy',
            r'postman',
            r'insomnia',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.bot_patterns]
        
        # Padrões suspeitos de comportamento
        self.suspicious_patterns = [
            r'\.php$',  # Tentativas de acessar arquivos PHP
            r'wp-admin',  # WordPress admin
            r'\.env',   # Arquivos de configuração
            r'admin\.php',
            r'shell\.php',
            r'\.git/',
            r'config\.json',
        ]
        
        self.suspicious_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
    
    def is_bot_user_agent(self, user_agent: str) -> bool:
        """Verificar se user agent é de bot"""
        if not user_agent:
            return True
        
        for pattern in self.compiled_patterns:
            if pattern.search(user_agent):
                return True
        
        return False
    
    def is_suspicious_request(self, path: str, user_agent: str = None) -> tuple[bool, str]:
        """Verificar se requisição é suspeita"""
        # Verificar path suspeito
        for pattern in self.suspicious_compiled:
            if pattern.search(path):
                return True, f"Suspicious path: {path}"
        
        # Verificar user agent muito simples ou vazio
        if not user_agent or len(user_agent) < 10:
            return True, "Missing or too simple user agent"
        
        # Verificar se user agent é muito genérico
        if user_agent.lower() in ['user-agent', 'mozilla', 'browser']:
            return True, "Generic user agent"
        
        return False, ""
    
    def analyze_behavior(self, ip: str, requests_history: List[Dict]) -> tuple[bool, str]:
        """Analisar comportamento para detectar bots"""
        if len(requests_history) < 5:
            return False, ""
        
        # Verificar frequência muito alta
        recent_requests = [req for req in requests_history if time.time() - req['timestamp'] < 60]
        if len(recent_requests) > 30:  # Mais de 30 req/min
            return True, "High frequency requests"
        
        # Verificar padrões de path muito regulares
        paths = [req['path'] for req in recent_requests]
        unique_paths = set(paths)
        if len(unique_paths) < len(paths) * 0.3:  # Menos de 30% de paths únicos
            return True, "Repetitive path patterns"
        
        # Verificar user agents muito variados (possível rotação)
        user_agents = set(req.get('user_agent', '') for req in recent_requests)
        if len(user_agents) > len(recent_requests) * 0.8:  # Mais de 80% de UAs únicos
            return True, "User agent rotation detected"
        
        return False, ""

class JWTManager:
    """Gerenciador JWT com funcionalidades avançadas"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(minutes=30)
        self.refresh_token_expire = timedelta(days=7)
        
        # Cache de tokens revogados
        self.revoked_tokens: Set[str] = set()
        
        # Cache de usuários
        self.user_cache: Dict[int, Dict] = {}
        self.cache_ttl = 300  # 5 minutos
    
    def create_access_token(self, user_id: int, additional_claims: Dict = None) -> str:
        """Criar token de acesso"""
        now = datetime.utcnow()
        expire = now + self.access_token_expire
        
        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "jti": self._generate_jti(user_id, "access", now)
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Criar token de refresh"""
        now = datetime.utcnow()
        expire = now + self.refresh_token_expire
        
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "jti": self._generate_jti(user_id, "refresh", now)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verificar e decodificar token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar se token foi revogado
            jti = payload.get("jti")
            if jti in self.revoked_tokens:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.debug("Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.debug(f"Token inválido: {e}")
            return None
    
    def revoke_token(self, token: str):
        """Revogar token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            jti = payload.get("jti")
            if jti:
                self.revoked_tokens.add(jti)
                logger.info(f"Token revogado: {jti}")
        except Exception as e:
            logger.error(f"Erro ao revogar token: {e}")
    
    def _generate_jti(self, user_id: int, token_type: str, timestamp: datetime) -> str:
        """Gerar JWT ID único"""
        data = f"{user_id}:{token_type}:{timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def cleanup_revoked_tokens(self):
        """Limpar tokens revogados expirados"""
        # TODO: Implementar limpeza baseada em timestamp de expiração
        pass

class SecurityHeadersMiddleware:
    """Middleware para adicionar headers de segurança"""
    
    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'",
        }
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Adicionar headers de segurança
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Adicionar header customizado
        response.headers["X-TecnoCursos-Security"] = "enabled"
        
        return response

class ComprehensiveSecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de segurança abrangente"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        self.bot_detector = BotDetector()
        self.jwt_manager = JWTManager()
        
        # Histórico de requisições por IP
        self.request_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # Última limpeza
        self.last_cleanup = time.time()
        
        # Paths que não requerem autenticação
        self.public_paths = {
            '/',
            '/health',
            '/docs',
            '/openapi.json',
            '/login.html',
            '/static/',
        }
        
        # Paths críticos que requerem proteção extra
        self.critical_paths = {
            '/api/admin/',
            '/api/users/',
            '/api/auth/',
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Extrair informações da requisição
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        path = request.url.path
        method = request.method
        
        try:
            # 1. Rate Limiting
            allowed, rate_message = self.rate_limiter.is_allowed(client_ip, path)
            if not allowed:
                security_metrics.record_rate_limit(client_ip)
                log_security_event("rate_limit_exceeded", {"ip": client_ip, "path": path})
                return self._create_error_response(429, "Rate limit exceeded")
            
            # 2. Bot Detection
            if self.bot_detector.is_bot_user_agent(user_agent):
                if not self._is_allowed_bot_path(path):
                    security_metrics.record_bot_request(client_ip, user_agent)
                    return self._create_error_response(403, "Bot access denied")
            
            # 3. Suspicious Activity Detection
            is_suspicious, suspicion_reason = self.bot_detector.is_suspicious_request(path, user_agent)
            if is_suspicious:
                security_metrics.record_suspicious_activity(suspicion_reason, client_ip)
                log_security_event("suspicious_request", {
                    "ip": client_ip,
                    "path": path,
                    "reason": suspicion_reason,
                    "user_agent": user_agent
                })
                return self._create_error_response(403, "Suspicious request blocked")
            
            # 4. Análise comportamental
            self._record_request(client_ip, path, user_agent, method)
            is_bot_behavior, behavior_reason = self.bot_detector.analyze_behavior(
                client_ip, 
                self.request_history[client_ip]
            )
            if is_bot_behavior:
                security_metrics.record_suspicious_activity(behavior_reason, client_ip)
                return self._create_error_response(403, "Automated behavior detected")
            
            # 5. Validação de headers obrigatórios para paths críticos
            if any(critical_path in path for critical_path in self.critical_paths):
                if not self._validate_critical_headers(request):
                    return self._create_error_response(400, "Missing required headers")
            
            # 6. Prosseguir com a requisição
            response = await call_next(request)
            
            # 7. Log de performance
            processing_time = time.time() - start_time
            log_performance_metric("request_processing_time", processing_time)
            
            # 8. Adicionar headers de segurança
            self._add_security_headers(response, request)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no middleware de segurança: {e}")
            return self._create_error_response(500, "Internal security error")
        finally:
            # Limpeza periódica
            if time.time() - self.last_cleanup > 300:  # A cada 5 minutos
                await self._periodic_cleanup()
                self.last_cleanup = time.time()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrair IP real do cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _record_request(self, ip: str, path: str, user_agent: str, method: str):
        """Registrar requisição no histórico"""
        request_data = {
            'timestamp': time.time(),
            'path': path,
            'user_agent': user_agent,
            'method': method
        }
        
        history = self.request_history[ip]
        history.append(request_data)
        
        # Manter apenas últimas 100 requisições por IP
        if len(history) > 100:
            history[:] = history[-100:]
    
    def _is_allowed_bot_path(self, path: str) -> bool:
        """Verificar se path é permitido para bots"""
        allowed_bot_paths = [
            '/robots.txt',
            '/sitemap.xml',
            '/health',
            '/',
        ]
        
        return any(path.startswith(allowed_path) for allowed_path in allowed_bot_paths)
    
    def _validate_critical_headers(self, request: Request) -> bool:
        """Validar headers obrigatórios para paths críticos"""
        required_headers = ["user-agent", "accept"]
        
        for header in required_headers:
            if not request.headers.get(header):
                return False
        
        return True
    
    def _add_security_headers(self, response: Response, request: Request):
        """Adicionar headers de segurança"""
        # Headers básicos de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS apenas para HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Adicionar timestamp de processamento
        response.headers["X-Response-Time"] = str(int(time.time() * 1000))
    
    def _create_error_response(self, status_code: int, message: str) -> JSONResponse:
        """Criar resposta de erro padronizada"""
        return JSONResponse(
            status_code=status_code,
            content={
                "error": message,
                "timestamp": datetime.now().isoformat(),
                "status": status_code
            },
            headers={
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
        )
    
    async def _periodic_cleanup(self):
        """Limpeza periódica de dados antigos"""
        try:
            # Limpar histórico de requisições antigas
            cutoff_time = time.time() - 3600  # 1 hora
            
            for ip in list(self.request_history.keys()):
                history = self.request_history[ip]
                # Remover requisições antigas
                self.request_history[ip] = [
                    req for req in history if req['timestamp'] > cutoff_time
                ]
                
                # Remover IP se não houver histórico
                if not self.request_history[ip]:
                    del self.request_history[ip]
            
            # Limpar entradas antigas do rate limiter
            self.rate_limiter.cleanup_old_entries()
            
            # Limpar tokens revogados
            self.jwt_manager.cleanup_revoked_tokens()
            
            logger.info("Limpeza de segurança executada")
            
        except Exception as e:
            logger.error(f"Erro na limpeza de segurança: {e}")

# Instâncias globais
security_middleware = ComprehensiveSecurityMiddleware
security_headers_middleware = SecurityHeadersMiddleware()
jwt_manager = JWTManager()

# Funções de conveniência
def get_security_metrics() -> Dict[str, Any]:
    """Obter métricas de segurança"""
    return {
        'blocked_requests': security_metrics.blocked_requests,
        'rate_limited_requests': security_metrics.rate_limited_requests,
        'suspicious_activity': security_metrics.suspicious_activity,
        'failed_auth_attempts': security_metrics.failed_auth_attempts,
        'bot_requests': security_metrics.bot_requests,
        'recent_events': security_metrics.security_events[-10:],  # Últimos 10 eventos
    }

def create_tokens(user_id: int) -> Dict[str, str]:
    """Criar par de tokens para usuário"""
    return {
        'access_token': jwt_manager.create_access_token(user_id),
        'refresh_token': jwt_manager.create_refresh_token(user_id),
        'token_type': 'bearer'
    }

def verify_token(token: str) -> Optional[int]:
    """Verificar token e retornar user_id"""
    payload = jwt_manager.verify_token(token)
    if payload:
        return int(payload.get('sub'))
    return None 