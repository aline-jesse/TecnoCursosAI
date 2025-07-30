"""
Suite de Testes Automatizados - TecnoCursos AI
Testes unitários, integração e performance
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
import sqlite3
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest_asyncio

# Imports da aplicação
from app.core.settings import AppSettings, Environment
from app.core.cache import AdvancedCacheManager
from app.core.logging import configure_logging, get_logger
from app.core.validators import (
    StrongPassword, SafeFilename, ValidatedEmail, 
    CPF, PhoneNumber, FileValidator, validate_data, UserValidator
)
from app.security.auth_manager import SecureAuthManager
from app.security.rate_limiter import AdvancedRateLimiter, RateLimitConfig
from app.core.backup import BackupManager, BackupConfig
from app.core.notifications import NotificationManager, NotificationType
from app.middleware.monitoring import PerformanceMetrics, HealthMonitor
from app.core.query_optimizer import OptimizedQueries

# Configuração de teste
@pytest.fixture(scope="session")
def test_settings():
    """Configurações para teste"""
    return AppSettings(
        environment=Environment.TESTING,
        debug=True,
        database_url="sqlite:///./test_tecnocursos.db",
        secret_key="test-secret-key",
        jwt_secret_key="test-jwt-secret",
        redis_url=None  # Usar cache em memória para testes
    )

@pytest.fixture(scope="session")
def event_loop():
    """Event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def cache_manager():
    """Cache manager para testes"""
    manager = AdvancedCacheManager(redis_url=None, max_memory_items=100)
    yield manager
    # Cleanup
    manager.memory_cache.clear()

@pytest.fixture
def temp_dir():
    """Diretório temporário para testes"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)

# ========== TESTES DE VALIDAÇÃO ==========

class TestValidators:
    """Testes dos validadores"""
    
    def test_strong_password_valid(self):
        """Testa senha forte válida"""
        valid_passwords = [
            "MinhaSenh@123",
            "Test!ng123",
            "SecureP@ssw0rd"
        ]
        
        for password in valid_passwords:
            result = StrongPassword.validate(password)
            assert result == password
    
    def test_strong_password_invalid(self):
        """Testa senhas fracas"""
        invalid_passwords = [
            "123456",           # Muito simples
            "password",         # Comum
            "abc",              # Muito curta
            "ONLYUPPERCASE",    # Só maiúsculas
            "onlylowercase",    # Só minúsculas
            "NoNumbers!",       # Sem números
            "NoSpecial123"      # Sem caracteres especiais
        ]
        
        for password in invalid_passwords:
            with pytest.raises(Exception):
                StrongPassword.validate(password)
    
    def test_safe_filename_valid(self):
        """Testa nomes de arquivo seguros"""
        valid_names = [
            "documento.pdf",
            "meu_arquivo.txt",
            "video-final.mp4",
            "apresentacao_2023.pptx"
        ]
        
        for filename in valid_names:
            result = SafeFilename.validate(filename)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_safe_filename_invalid(self):
        """Testa nomes de arquivo inseguros"""
        invalid_names = [
            "../../../etc/passwd",
            "arquivo<script>.txt",
            "CON.txt",               # Nome reservado Windows
            "arquivo.exe",           # Extensão não permitida
            "a" * 300 + ".txt"       # Muito longo
        ]
        
        for filename in invalid_names:
            with pytest.raises(Exception):
                SafeFilename.validate(filename)
    
    def test_validated_email(self):
        """Testa validação de email"""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "usuario@tecnocursos.ai"
        ]
        
        for email in valid_emails:
            result = ValidatedEmail.validate(email)
            assert "@" in result
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user space@domain.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(Exception):
                ValidatedEmail.validate(email)
    
    def test_cpf_validation(self):
        """Testa validação de CPF"""
        valid_cpfs = [
            "12345678909",
            "123.456.789-09",
            "111.444.777-35"
        ]
        
        for cpf in valid_cpfs:
            # Usar CPF válido real para teste
            continue  # Pular por enquanto
        
        invalid_cpfs = [
            "12345678901",        # Dígito verificador inválido
            "111.111.111-11",     # Todos iguais
            "123.456.789",        # Incompleto
            "abc.def.ghi-jk"      # Não numérico
        ]
        
        for cpf in invalid_cpfs:
            with pytest.raises(Exception):
                CPF.validate(cpf)
    
    def test_phone_number_validation(self):
        """Testa validação de telefone brasileiro"""
        valid_phones = [
            "(11) 99999-9999",
            "11999999999",
            "(21) 3333-4444",
            "2133334444"
        ]
        
        for phone in valid_phones:
            result = PhoneNumber.validate(phone)
            assert "(" in result and ")" in result and "-" in result
        
        invalid_phones = [
            "123456789",          # Muito curto
            "(99) 99999-9999",    # DDD inválido
            "abcd-efgh-ijkl"      # Não numérico
        ]
        
        for phone in invalid_phones:
            with pytest.raises(Exception):
                PhoneNumber.validate(phone)
    
    def test_user_validator(self):
        """Testa validador de usuário"""
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "TestPass123!"
        }
        
        result = validate_data(valid_data, UserValidator)
        assert result["valid"] is True
        assert result["data"]["username"] == "testuser"
        
        # Teste com dados inválidos
        invalid_data = {
            "username": "admin",  # Nome reservado
            "email": "invalid-email",
            "full_name": "",
            "password": "123"
        }
        
        result = validate_data(invalid_data, UserValidator)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

# ========== TESTES DE CACHE ==========

class TestCacheManager:
    """Testes do sistema de cache"""
    
    @pytest.mark.asyncio
    async def test_cache_set_get(self, cache_manager):
        """Testa operações básicas de cache"""
        key = "test_key"
        value = {"data": "test_value", "number": 123}
        
        # Set
        success = await cache_manager.set(key, value, ttl=60)
        assert success is True
        
        # Get
        result = await cache_manager.get(key)
        assert result == value
        
        # Get com default
        result = await cache_manager.get("nonexistent", "default")
        assert result == "default"
    
    @pytest.mark.asyncio
    async def test_cache_delete(self, cache_manager):
        """Testa remoção de cache"""
        key = "test_delete"
        value = "test_value"
        
        await cache_manager.set(key, value)
        result = await cache_manager.get(key)
        assert result == value
        
        success = await cache_manager.delete(key)
        assert success is True
        
        result = await cache_manager.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_pattern_clear(self, cache_manager):
        """Testa limpeza por padrão"""
        keys = ["user:1:profile", "user:1:settings", "user:2:profile"]
        
        for key in keys:
            await cache_manager.set(key, f"value_{key}")
        
        # Limpar padrão user:1:*
        count = await cache_manager.clear_pattern("user:1:*")
        assert count >= 2
        
        # Verificar que user:2 ainda existe
        result = await cache_manager.get("user:2:profile")
        assert result == "value_user:2:profile"
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self, cache_manager):
        """Testa expiração de TTL"""
        key = "test_ttl"
        value = "test_value"
        
        # Cache com TTL muito baixo
        await cache_manager.set(key, value, ttl=1)
        
        # Deve existir imediatamente
        result = await cache_manager.get(key)
        assert result == value
        
        # Esperar expirar
        await asyncio.sleep(2)
        
        # Não deve mais existir
        result = await cache_manager.get(key)
        assert result is None

# ========== TESTES DE AUTENTICAÇÃO ==========

class TestAuthManager:
    """Testes do gerenciador de autenticação"""
    
    @pytest.fixture
    def auth_manager(self):
        """Auth manager para testes"""
        return SecureAuthManager(
            secret_key="test-secret",
            algorithm="HS256",
            access_token_expire_minutes=30
        )
    
    def test_password_hashing(self, auth_manager):
        """Testa hash de senhas"""
        password = "MySecurePassword123!"
        
        # Hash
        hashed = auth_manager.hash_password(password)
        assert hashed != password
        assert len(hashed) > 0
        
        # Verificar
        assert auth_manager.verify_password(password, hashed) is True
        assert auth_manager.verify_password("wrong", hashed) is False
    
    def test_token_creation_validation(self, auth_manager):
        """Testa criação e validação de tokens"""
        user_data = {"user_id": "123", "username": "testuser"}
        
        # Criar token
        token = auth_manager.create_access_token(user_data)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Validar token
        payload = auth_manager.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == "123"
        assert payload["username"] == "testuser"
        
        # Token inválido
        invalid_payload = auth_manager.verify_token("invalid.token.here")
        assert invalid_payload is None
    
    def test_token_blacklist(self, auth_manager):
        """Testa blacklist de tokens"""
        user_data = {"user_id": "123", "username": "testuser"}
        token = auth_manager.create_access_token(user_data)
        
        # Token deve ser válido
        payload = auth_manager.verify_token(token)
        assert payload is not None
        
        # Adicionar à blacklist
        auth_manager.blacklist_token(token)
        
        # Token deve ser inválido agora
        payload = auth_manager.verify_token(token)
        assert payload is None

# ========== TESTES DE RATE LIMITING ==========

class TestRateLimiter:
    """Testes do rate limiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Rate limiter para testes"""
        return AdvancedRateLimiter(redis_client=None)  # Usar memória local
    
    @pytest.mark.asyncio
    async def test_rate_limiting_basic(self, rate_limiter):
        """Testa rate limiting básico"""
        from unittest.mock import Mock
        
        # Mock request
        request = Mock()
        request.method = "GET"
        request.url.path = "/api/test"
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = "test-agent"
        
        # Configurar limite baixo para teste
        rate_limiter.endpoint_configs["/api/test"] = RateLimitConfig(
            requests_per_minute=2,
            burst_limit=1,
            block_duration=60
        )
        
        # Primeira request - deve passar
        is_limited, info = await rate_limiter.is_rate_limited(request)
        assert is_limited is False
        assert "remaining" in info
        
        # Segunda request - deve passar
        is_limited, info = await rate_limiter.is_rate_limited(request)
        assert is_limited is False
        
        # Terceira request - deve ser limitada
        is_limited, info = await rate_limiter.is_rate_limited(request)
        assert is_limited is True
        assert "error" in info

# ========== TESTES DE BACKUP ==========

class TestBackupManager:
    """Testes do sistema de backup"""
    
    @pytest.fixture
    def backup_manager(self, temp_dir):
        """Backup manager para testes"""
        config = BackupConfig(
            backup_dir=str(temp_dir / "backups"),
            retention_days=7,
            compression=False  # Desabilitar compressão para testes
        )
        return BackupManager(config)
    
    @pytest.mark.asyncio
    async def test_database_backup_sqlite(self, backup_manager, temp_dir):
        """Testa backup de SQLite"""
        # Criar banco de teste
        test_db = temp_dir / "test.db"
        conn = sqlite3.connect(str(test_db))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'Test Data')")
        conn.commit()
        conn.close()
        
        # Mock settings para usar banco de teste
        with patch('app.core.backup.settings') as mock_settings:
            mock_settings.database.url = f"sqlite:///{test_db}"
            
            # Fazer backup
            result = await backup_manager.create_database_backup()
            
            assert result["status"] == "completed"
            assert result["file_path"] is not None
            assert Path(result["file_path"]).exists()
    
    @pytest.mark.asyncio
    async def test_files_backup(self, backup_manager, temp_dir):
        """Testa backup de arquivos"""
        # Criar arquivos de teste
        upload_dir = temp_dir / "uploads"
        upload_dir.mkdir()
        
        test_file = upload_dir / "test.txt"
        test_file.write_text("Test content")
        
        # Mock settings
        with patch('app.core.backup.settings') as mock_settings:
            mock_settings.files.upload_dir = str(upload_dir)
            mock_settings.files.video_output_dir = str(temp_dir / "videos")
            mock_settings.files.audio_output_dir = str(temp_dir / "audios")
            
            # Fazer backup
            result = await backup_manager.create_files_backup()
            
            assert result["status"] == "completed"
            assert result["files_count"] >= 1
            assert Path(result["file_path"]).exists()
    
    def test_backup_registry(self, backup_manager):
        """Testa registro de backups"""
        # Backup registry deve iniciar vazio
        assert len(backup_manager.backup_registry) == 0
        
        # Adicionar backup fictício
        backup_info = {
            "type": "test",
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        
        backup_manager.backup_registry["test_1"] = backup_info
        backup_manager.save_backup_registry()
        
        # Recarregar e verificar
        backup_manager.load_backup_registry()
        assert "test_1" in backup_manager.backup_registry

# ========== TESTES DE PERFORMANCE ==========

class TestPerformanceMetrics:
    """Testes de métricas de performance"""
    
    @pytest.fixture
    def metrics(self):
        """Métricas para teste"""
        return PerformanceMetrics(max_samples=100)
    
    @pytest.mark.asyncio
    async def test_request_recording(self, metrics):
        """Testa gravação de métricas de request"""
        # Gravar algumas requests
        await metrics.record_request("GET", "/api/test", 200, 150.0, "user123")
        await metrics.record_request("POST", "/api/test", 201, 300.0, "user456")
        await metrics.record_request("GET", "/api/slow", 200, 2000.0, "user123")
        
        # Verificar métricas
        summary = await metrics.get_summary()
        
        assert "request_metrics" in summary
        assert summary["request_metrics"]["total_requests"] == 3
        assert summary["request_metrics"]["avg_response_time"] > 0
        assert summary["request_metrics"]["max_response_time"] == 2000.0
        
        # Verificar contadores de endpoint
        assert "GET /api/test" in metrics.endpoint_metrics
        assert metrics.endpoint_metrics["GET /api/test"]["count"] == 1
        assert metrics.endpoint_metrics["GET /api/slow"]["max_time"] == 2000.0
    
    @pytest.mark.asyncio
    async def test_business_metrics(self, metrics):
        """Testa métricas de negócio"""
        # Gravar métricas de negócio
        await metrics.record_business_metric("user_registration", 1)
        await metrics.record_business_metric("video_generation", 3)
        await metrics.record_business_metric("user_registration", 2)
        
        # Verificar
        summary = await metrics.get_summary()
        
        assert summary["business_metrics"]["user_registration"] == 3
        assert summary["business_metrics"]["video_generation"] == 3

# ========== TESTES DE INTEGRAÇÃO ==========

class TestIntegration:
    """Testes de integração"""
    
    @pytest.mark.asyncio
    async def test_full_notification_flow(self):
        """Testa fluxo completo de notificação"""
        notification_manager = NotificationManager()
        
        # Iniciar sistema
        await notification_manager.start()
        
        try:
            # Enviar notificação
            notification_id = await notification_manager.send_notification(
                "project_created",
                user_id="test_user",
                variables={"project_name": "Test Project"}
            )
            
            assert notification_id is not None
            
            # Aguardar processamento
            await asyncio.sleep(0.1)
            
            # Verificar que foi processada
            # (implementar verificação conforme necessário)
            
        finally:
            await notification_manager.stop()
    
    @pytest.mark.asyncio
    async def test_cache_and_query_integration(self, cache_manager):
        """Testa integração cache + queries"""
        # Simular dados de consulta
        test_data = {
            "projects": [
                {"id": 1, "name": "Project 1"},
                {"id": 2, "name": "Project 2"}
            ]
        }
        
        # Cachear dados
        cache_key = "user:123:projects"
        await cache_manager.set(cache_key, test_data, ttl=300)
        
        # Buscar do cache
        cached_data = await cache_manager.get(cache_key)
        assert cached_data == test_data
        
        # Invalidar cache
        await cache_manager.clear_pattern("user:123:*")
        
        # Verificar que foi removido
        cached_data = await cache_manager.get(cache_key)
        assert cached_data is None

# ========== FIXTURE PARA APLICAÇÃO COMPLETA ==========

@pytest.fixture
async def test_app():
    """Aplicação completa para testes"""
    from app.main_optimized import app
    
    # Configurar para teste
    app.state.testing = True
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# ========== TESTES DE API ==========

class TestAPI:
    """Testes dos endpoints da API"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_app):
        """Testa endpoint de saúde"""
        response = await test_app.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, test_app):
        """Testa endpoint de métricas"""
        response = await test_app.get("/metrics")
        
        # Pode retornar 200 (dev/staging) ou 404 (production)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data

# Configuração do pytest
def pytest_configure():
    """Configuração do pytest"""
    # Configurar logging para testes
    configure_logging(log_level="DEBUG", enable_console=False)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
