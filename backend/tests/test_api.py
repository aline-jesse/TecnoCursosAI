"""
Testes automatizados para a API TecnoCursos AI
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, Project
from app.auth import create_access_token, get_password_hash

# Configurar banco de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

class TestHealthCheck:
    """Testes para health check"""
    
    def test_health_check(self, client, test_db):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert data["database"] is True

class TestAPIStatus:
    """Testes para status da API"""
    
    def test_api_status(self, client, test_db):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
        assert "endpoints" in data
        assert "database" in data
        assert "features" in data

class TestAuthentication:
    """Testes para autenticação"""
    
    def test_register_user(self, client, test_db):
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "password123",
            "confirm_password": "password123"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_existing_email(self, client, test_db, test_user):
        user_data = {
            "username": "anotheruser",
            "email": test_user.email,  # Email já existe
            "full_name": "Another User",
            "password": "password123",
            "confirm_password": "password123"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "já está em uso" in response.json()["detail"]
    
    def test_login_valid_credentials(self, client, test_db, test_user):
        login_data = {
            "email": test_user.email,
            "password": "testpass123"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_invalid_credentials(self, client, test_db):
        login_data = {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "incorretos" in response.json()["detail"]

class TestUserEndpoints:
    """Testes para endpoints de usuário"""
    
    def test_get_current_user_authenticated(self, client, test_db, test_user, auth_headers):
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
    
    def test_get_current_user_unauthenticated(self, client, test_db):
        response = client.get("/api/users/me")
        assert response.status_code == 401

class TestProjects:
    """Testes para projetos"""
    
    def test_create_project(self, client, test_db, test_user, auth_headers):
        project_data = {
            "name": "Test Project",
            "description": "Test project description",
            "category": "programming",
            "difficulty_level": "BEGINNER",
            "estimated_duration": 60,
            "is_public": True,
            "tags": ["python", "test"]
        }
        response = client.post("/api/projects", json=project_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["slug"] is not None
    
    def test_list_projects_authenticated(self, client, test_db, test_user, auth_headers):
        response = client.get("/api/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_projects_unauthenticated(self, client, test_db):
        response = client.get("/api/projects")
        assert response.status_code == 200
        # Deve retornar apenas projetos públicos
        data = response.json()
        assert isinstance(data, list)

class TestSystemStats:
    """Testes para estatísticas do sistema"""
    
    def test_system_stats(self, client, test_db):
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_projects" in data
        assert "total_files" in data
        assert "total_videos" in data
        assert "storage_used" in data

class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_404_endpoint(self, client, test_db):
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self, client, test_db):
        response = client.post(
            "/api/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

class TestSecurity:
    """Testes de segurança"""
    
    def test_password_validation(self, client, test_db):
        weak_password_data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "full_name": "Weak User",
            "password": "123",  # Senha muito fraca
            "confirm_password": "123"
        }
        response = client.post("/api/auth/register", json=weak_password_data)
        assert response.status_code == 422
    
    def test_sql_injection_attempt(self, client, test_db):
        malicious_data = {
            "email": "'; DROP TABLE users; --",
            "password": "anything"
        }
        response = client.post("/api/auth/login", json=malicious_data)
        # Deve falhar com credenciais inválidas, não com erro de SQL
        assert response.status_code == 401

# Testes de performance
class TestPerformance:
    """Testes básicos de performance"""
    
    def test_response_time_health_check(self, client, test_db):
        import time
        start_time = time.time()
        response = client.get("/api/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Deve responder em menos de 1 segundo
    
    def test_concurrent_requests(self, client, test_db):
        import concurrent.futures
        
        def make_request():
            return client.get("/api/health")
        
        # Fazer 10 requisições concorrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # Todas devem retornar 200
        for response in responses:
            assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 