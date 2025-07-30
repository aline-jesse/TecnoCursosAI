"""
Fixture e configurações comuns para testes - TecnoCursos AI
"""

import os
import tempfile
import asyncio
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configurar variáveis de ambiente para teste
os.environ.update({
    "ENVIRONMENT": "testing",
    "DEBUG": "true",
    "SECRET_KEY": "test-secret-key-very-secure",
    "JWT_SECRET_KEY": "test-jwt-secret-key",
    "DATABASE_URL": "sqlite:///./test_tecnocursos.db",
    "REDIS_URL": "",  # Usar cache em memória
    "LOG_LEVEL": "DEBUG",
    "TESTING": "true"
})

from app.core.settings import get_settings
from app.core.database import get_db, Base
from app.core.cache import AdvancedCacheManager
from app.security.auth_manager import SecureAuthManager
from app.core.notifications import NotificationManager

# Configurações de teste
TEST_DATABASE_URL = "sqlite:///./test_tecnocursos.db"

@pytest.fixture(scope="session")
def event_loop():
    """Event loop para toda a sessão de teste"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_settings():
    """Configurações para ambiente de teste"""
    settings = get_settings()
    # Forçar configurações de teste
    settings.environment = "testing"
    settings.debug = True
    settings.database.url = TEST_DATABASE_URL
    settings.redis.url = None  # Cache em memória
    return settings

@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Engine de banco para testes"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        poolclass=StaticPool,
        echo=False  # Reduzir logs durante testes
    )
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    # Remover arquivo de teste se existir
    db_file = Path("test_tecnocursos.db")
    if db_file.exists():
        db_file.unlink()

@pytest.fixture
def test_session(test_engine):
    """Sessão de banco para teste individual"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def override_get_db(test_session):
    """Override da função get_db para usar sessão de teste"""
    def _override_get_db():
        try:
            yield test_session
        finally:
            pass
    return _override_get_db

@pytest.fixture
async def cache_manager():
    """Cache manager para testes"""
    manager = AdvancedCacheManager(
        redis_url=None,  # Usar cache em memória
        max_memory_items=1000
    )
    yield manager
    # Cleanup
    manager.memory_cache.clear()

@pytest.fixture
def auth_manager():
    """Auth manager para testes"""
    return SecureAuthManager(
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30
    )

@pytest.fixture
async def notification_manager():
    """Notification manager para testes"""
    manager = NotificationManager()
    
    # Mock dos providers para não enviar notificações reais
    manager.email_provider = Mock()
    manager.sms_provider = Mock()
    manager.slack_provider = Mock()
    
    await manager.start()
    yield manager
    await manager.stop()

@pytest.fixture
def temp_upload_dir():
    """Diretório temporário para uploads de teste"""
    with tempfile.TemporaryDirectory() as temp_dir:
        upload_dir = Path(temp_dir) / "uploads"
        upload_dir.mkdir(exist_ok=True)
        yield upload_dir

@pytest.fixture
def mock_file_upload():
    """Mock de arquivo para upload"""
    from fastapi import UploadFile
    from io import BytesIO
    
    content = b"Test file content for testing purposes"
    file_obj = BytesIO(content)
    
    return UploadFile(
        filename="test_file.txt",
        file=file_obj,
        size=len(content),
        headers={"content-type": "text/plain"}
    )

@pytest.fixture
def mock_request():
    """Mock de request HTTP"""
    from unittest.mock import Mock
    
    request = Mock()
    request.method = "GET"
    request.url.path = "/api/test"
    request.client.host = "127.0.0.1"
    request.headers = {"User-Agent": "test-agent"}
    request.headers.get = lambda key, default=None: request.headers.get(key, default)
    
    return request

@pytest.fixture
def test_user_data():
    """Dados de usuário para testes"""
    return {
        "id": "test-user-123",
        "username": "testuser",
        "email": "test@tecnocursos.ai",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def test_project_data():
    """Dados de projeto para testes"""
    return {
        "id": "test-project-123",
        "name": "Test Project",
        "description": "Project for testing",
        "user_id": "test-user-123",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def authenticated_headers(auth_manager, test_user_data):
    """Headers com token de autenticação"""
    token = auth_manager.create_access_token(test_user_data)
    return {"Authorization": f"Bearer {token}"}

# Fixtures para testes específicos

@pytest.fixture
def mock_openai_client():
    """Mock do cliente OpenAI"""
    with patch('app.services.ai_service.openai') as mock_openai:
        # Mock de resposta do chat completion
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Resposta de teste do OpenAI"))
        ]
        mock_openai.ChatCompletion.create.return_value = mock_response
        yield mock_openai

@pytest.fixture
def mock_elevenlabs_client():
    """Mock do cliente ElevenLabs"""
    with patch('app.services.audio_service.elevenlabs') as mock_elevenlabs:
        # Mock de resposta de geração de áudio
        mock_elevenlabs.generate.return_value = b"fake_audio_data"
        yield mock_elevenlabs

@pytest.fixture
def mock_redis():
    """Mock do Redis para testes"""
    with patch('app.core.cache.redis') as mock_redis:
        # Simular comportamento básico do Redis
        cache = {}
        
        def mock_get(key):
            return cache.get(key)
        
        def mock_set(key, value, ex=None):
            cache[key] = value
            return True
        
        def mock_delete(key):
            return cache.pop(key, None) is not None
        
        def mock_keys(pattern):
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                return [k for k in cache.keys() if k.startswith(prefix)]
            return []
        
        mock_redis.get = mock_get
        mock_redis.set = mock_set
        mock_redis.delete = mock_delete
        mock_redis.keys = mock_keys
        
        yield mock_redis

# Utilitários para testes

class TestDataBuilder:
    """Builder para criar dados de teste"""
    
    @staticmethod
    def create_user(
        username: str = "testuser",
        email: str = "test@example.com",
        **kwargs
    ) -> dict:
        """Criar dados de usuário"""
        data = {
            "username": username,
            "email": email,
            "full_name": f"Test {username.title()}",
            "password": "TestPassword123!",
            "is_active": True,
            "is_superuser": False
        }
        data.update(kwargs)
        return data
    
    @staticmethod
    def create_project(
        name: str = "Test Project",
        user_id: str = "test-user-123",
        **kwargs
    ) -> dict:
        """Criar dados de projeto"""
        data = {
            "name": name,
            "description": f"Description for {name}",
            "user_id": user_id,
            "status": "active",
            "settings": {
                "video_quality": "high",
                "audio_voice": "default",
                "language": "pt-BR"
            }
        }
        data.update(kwargs)
        return data

# Decoradores para testes

def requires_auth(func):
    """Decorador para testes que requerem autenticação"""
    func._requires_auth = True
    return func

def slow_test(func):
    """Decorador para testes lentos"""
    return pytest.mark.slow(func)

def integration_test(func):
    """Decorador para testes de integração"""
    return pytest.mark.integration(func)

def unit_test(func):
    """Decorador para testes unitários"""
    return pytest.mark.unit(func)

# Configuração de markers automaticos

def pytest_collection_modifyitems(config, items):
    """Adicionar markers automaticamente baseado no nome/localização"""
    for item in items:
        # Adicionar marker 'unit' por padrão
        if not any(marker.name in ['unit', 'integration', 'slow'] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Adicionar marker 'slow' para testes que demoram
        if 'slow' in item.name or 'performance' in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Adicionar marker 'integration' para testes na pasta integration
        if 'integration' in str(item.fspath):
            item.add_marker(pytest.mark.integration)

# Hooks do pytest

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup automático do ambiente de teste"""
    # Garantir que estamos em modo de teste
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("TESTING", "true")
    
    # Desabilitar alguns serviços em teste
    monkeypatch.setenv("SEND_EMAILS", "false")
    monkeypatch.setenv("SEND_SMS", "false")
    monkeypatch.setenv("SEND_SLACK", "false")

def pytest_sessionstart(session):
    """Executa no início da sessão de teste"""
    print("\n🧪 Iniciando testes do TecnoCursos AI...")
    
    # Criar diretórios necessários
    Path("reports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

def pytest_sessionfinish(session, exitstatus):
    """Executa no final da sessão de teste"""
    if exitstatus == 0:
        print("\n✅ Todos os testes passaram!")
    else:
        print(f"\n❌ Alguns testes falharam (exit status: {exitstatus})")
    
    # Cleanup final
    for file in Path(".").glob("test_*.db*"):
        try:
            file.unlink()
        except:
            pass
