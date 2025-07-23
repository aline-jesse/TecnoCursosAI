"""
Sistema de Middleware - TecnoCursosAI
Middleware para logging, segurança, tratamento de erros e performance
"""

import time
import json
import uuid
from datetime import datetime
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware

try:
    from app.logger import get_logger
    # Fallback para funções específicas se não existirem
    try:
        from app.logger import log_api_request, log_security_event, log_performance_metric
    except ImportError:
        def log_api_request(*args, **kwargs): pass
        def log_security_event(*args, **kwargs): pass  
        def log_performance_metric(*args, **kwargs): pass
except ImportError:
    import logging
    get_logger = logging.getLogger
    def log_api_request(*args, **kwargs): pass
    def log_security_event(*args, **kwargs): pass
    def log_performance_metric(*args, **kwargs): pass

logger = get_logger("middleware")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requisições
    Registra todas as requisições HTTP com detalhes e métricas
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar ID único para a requisição
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Registrar início da requisição
        start_time = time.time()
        
        # Informações da requisição
        client_ip = self.get_client_ip(request)
        
        logger.info(
            "Requisição iniciada",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        try:
            # Processar requisição
            response = await call_next(request)
            
            # Calcular tempo de execução
            process_time = time.time() - start_time
            
            # Log da resposta
            logger.info(
                "Requisição concluída",
                request_id=request_id,
                status_code=response.status_code,
                process_time=process_time
            )
            
            # Adicionar headers de rastreamento
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log estruturado para análise
            log_api_request(request, response, process_time)
            
            # Registrar métrica de performance
            log_performance_metric(
                "api_request_duration",
                process_time,
                "seconds",
                {
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": response.status_code
                }
            )
            
            return response
            
        except Exception as e:
            # Calcular tempo até o erro
            process_time = time.time() - start_time
            
            # Log do erro
            logger.error(
                "Erro durante processamento da requisição",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
                process_time=process_time,
                exc_info=True
            )
            
            # Retornar resposta de erro
            return self.create_error_response(e, request_id)
    
    def get_client_ip(self, request: Request) -> str:
        """Obter IP real do cliente considerando proxies"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # IP direto
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def create_error_response(self, error: Exception, request_id: str) -> JSONResponse:
        """Criar resposta de erro padronizada"""
        
        if isinstance(error, HTTPException):
            status_code = error.status_code
            detail = error.detail
        else:
            status_code = 500
            detail = "Erro interno do servidor"
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": True,
                "message": detail,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            }
        )

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de segurança
    Implementa headers de segurança e proteções básicas
    """
    
    def __init__(self, app, security_headers: bool = True, rate_limit: bool = True):
        super().__init__(app)
        self.security_headers = security_headers
        self.rate_limit = rate_limit
        self.request_counts: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Aplicar rate limiting
        if self.rate_limit:
            client_ip = self.get_client_ip(request)
            if not self.check_rate_limit(client_ip):
                log_security_event(
                    "rate_limit_exceeded",
                    {"client_ip": client_ip, "path": request.url.path},
                    "WARNING"
                )
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded", "message": "Muitas requisições"}
                )
        
        # Validações de segurança
        security_issues = self.check_security_issues(request)
        if security_issues:
            log_security_event(
                "security_violation",
                {
                    "client_ip": self.get_client_ip(request),
                    "issues": security_issues,
                    "path": request.url.path
                },
                "ERROR"
            )
            return JSONResponse(
                status_code=400,
                content={"error": "Security violation", "issues": security_issues}
            )
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar headers de segurança
        if self.security_headers:
            self.add_security_headers(response)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Obter IP do cliente"""
        if hasattr(request.client, "host"):
            return request.client.host
        return "unknown"
    
    def check_rate_limit(self, client_ip: str, max_requests: int = 100, window: int = 60) -> bool:
        """Verificar rate limiting por IP"""
        now = time.time()
        
        # Inicializar lista de requisições para o IP se não existir
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Remover requisições antigas (fora da janela de tempo)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if now - req_time < window
        ]
        
        # Verificar se excedeu o limite
        if len(self.request_counts[client_ip]) >= max_requests:
            return False
        
        # Adicionar requisição atual
        self.request_counts[client_ip].append(now)
        return True
    
    def check_security_issues(self, request: Request) -> list:
        """Verificar problemas de segurança na requisição"""
        issues = []
        
        # Verificar tamanho do payload
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 100 * 1024 * 1024:  # 100MB
            issues.append("payload_too_large")
        
        # Verificar headers suspeitos
        suspicious_headers = ["X-Forwarded-Host", "X-Original-URL", "X-Rewrite-URL"]
        for header in suspicious_headers:
            if header.lower() in [h.lower() for h in request.headers.keys()]:
                issues.append(f"suspicious_header_{header.lower()}")
        
        # Verificar padrões de injeção na URL
        url_str = str(request.url).lower()
        injection_patterns = ["<script", "javascript:", "data:", "vbscript:", "../", "..\\"]
        for pattern in injection_patterns:
            if pattern in url_str:
                issues.append(f"injection_pattern_{pattern.replace(':', '').replace('<', '').replace('/', '_')}")
        
        return issues
    
    def add_security_headers(self, response: Response):
        """Adicionar headers de segurança"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value

class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware de monitoramento de performance
    Coleta métricas de performance e otimizações
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular métricas
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_diff = end_memory - start_memory
        
        # Log de métricas
        logger.debug(
            "Métricas de performance",
            endpoint=request.url.path,
            method=request.method,
            execution_time=execution_time,
            memory_usage=memory_diff,
            status_code=response.status_code
        )
        
        # Adicionar headers de performance
        response.headers["X-Execution-Time"] = str(execution_time)
        response.headers["X-Memory-Usage"] = str(memory_diff)
        
        # Alertar sobre performance ruim
        if execution_time > 2.0:  # Mais de 2 segundos
            logger.warning(
                "Requisição lenta detectada",
                endpoint=request.url.path,
                execution_time=execution_time
            )
        
        return response
    
    def get_memory_usage(self) -> float:
        """Obter uso de memória atual (simplificado)"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para tratamento centralizado de erros
    Captura e trata todas as exceções não tratadas
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # HTTP exceptions são tratadas pelo FastAPI
            raise e
            
        except ValueError as e:
            logger.error("Erro de valor", error=str(e), exc_info=True)
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Dados inválidos",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except PermissionError as e:
            logger.error("Erro de permissão", error=str(e), exc_info=True)
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Acesso negado",
                    "message": "Você não tem permissão para esta operação",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except FileNotFoundError as e:
            logger.error("Arquivo não encontrado", error=str(e), exc_info=True)
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Recurso não encontrado",
                    "message": "O arquivo ou recurso solicitado não foi encontrado",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            # Erro interno não tratado
            logger.exception("Erro interno não tratado")
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Erro interno do servidor",
                    "message": "Um erro inesperado ocorreu. Tente novamente mais tarde.",
                    "timestamp": datetime.now().isoformat()
                }
            )

def setup_middleware(app):
    """
    Configurar todos os middlewares na aplicação
    
    Args:
        app: Instância do FastAPI
    """
    
    # Middleware de compressão (primeiro para comprimir respostas)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Middleware de segurança
    app.add_middleware(SecurityMiddleware, security_headers=True, rate_limit=True)
    
    # Middleware de performance
    app.add_middleware(PerformanceMiddleware)
    
    # Middleware de tratamento de erros
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Middleware de logging (último para capturar tudo)
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Middlewares configurados com sucesso")

def setup_cors(app, origins: list = None, credentials: bool = True):
    """
    Configurar CORS
    
    Args:
        app: Instância do FastAPI
        origins: Lista de origens permitidas
        credentials: Permitir credenciais
    """
    
    if origins is None:
        origins = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    logger.info("CORS configurado", origins=origins)

def setup_trusted_hosts(app, allowed_hosts: list = None):
    """
    Configurar hosts confiáveis
    
    Args:
        app: Instância do FastAPI
        allowed_hosts: Lista de hosts permitidos
    """
    
    if allowed_hosts is None:
        allowed_hosts = ["localhost", "127.0.0.1", "*.tecnocursosai.com"]
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )
    
    logger.info("Trusted hosts configurados", hosts=allowed_hosts)

if __name__ == "__main__":
    """Testar middlewares"""
    from fastapi import FastAPI
    
    app = FastAPI()
    
    # Configurar middlewares
    setup_middleware(app)
    setup_cors(app)
    setup_trusted_hosts(app)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "Teste do middleware"}
    
    @app.get("/test-error")
    async def test_error():
        raise ValueError("Erro de teste")
    
    print("✅ Middlewares configurados para teste!") 