"""
Testes para o sistema de autenticação
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User
from app.auth import get_password_hash, verify_password, create_access_token

# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

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

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Criar usuário de teste"""
    db = TestingSessionLocal()
    hashed_password = get_password_hash("testpassword")
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def admin_user():
    """Criar usuário admin de teste"""
    db = TestingSessionLocal()
    hashed_password = get_password_hash("adminpassword")
    user = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


class TestPasswordUtils:
    """Testes para funções de manipulação de senhas"""
    
    def test_password_hashing(self):
        """Testar hash de senha"""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_password_verification(self):
        """Testar verificação de senha"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False
        assert verify_password("", hashed) is False


class TestTokenGeneration:
    """Testes para geração de tokens JWT"""
    
    def test_create_access_token(self):
        """Testar criação de token de acesso"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens são longos
    
    def test_create_token_with_expiration(self):
        """Testar criação de token com expiração personalizada"""
        from datetime import timedelta
        
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None
        assert isinstance(token, str)


class TestAuthenticationEndpoints:
    """Testes para endpoints de autenticação"""
    
    def test_register_user(self, setup_database):
        """Testar registro de usuário"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "securepassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data  # Senha não deve ser retornada
    
    def test_register_duplicate_user(self, setup_database, test_user):
        """Testar registro de usuário duplicado"""
        user_data = {
            "username": test_user.username,
            "email": "different@example.com",
            "full_name": "Different User",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_duplicate_email(self, setup_database, test_user):
        """Testar registro com email duplicado"""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,
            "full_name": "Different User",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, setup_database, test_user):
        """Testar login bem-sucedido"""
        login_data = {
            "username": test_user.username,
            "password": "testpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_username(self, setup_database):
        """Testar login com usuário inválido"""
        login_data = {
            "username": "nonexistentuser",
            "password": "anypassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, setup_database, test_user):
        """Testar login com senha inválida"""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, setup_database):
        """Testar login com usuário inativo"""
        # Criar usuário inativo
        db = TestingSessionLocal()
        hashed_password = get_password_hash("password")
        inactive_user = User(
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password=hashed_password,
            is_active=False
        )
        db.add(inactive_user)
        db.commit()
        db.close()
        
        login_data = {
            "username": "inactiveuser",
            "password": "password"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]


class TestProtectedEndpoints:
    """Testes para endpoints protegidos"""
    
    def get_auth_headers(self, user):
        """Obter headers de autenticação para um usuário"""
        login_data = {
            "username": user.username,
            "password": "testpassword" if user.username == "testuser" else "adminpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_current_user(self, setup_database, test_user):
        """Testar obtenção do usuário atual"""
        headers = self.get_auth_headers(test_user)
        
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
    
    def test_protected_endpoint_without_token(self, setup_database):
        """Testar endpoint protegido sem token"""
        response = client.get("/users/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_protected_endpoint_invalid_token(self, setup_database):
        """Testar endpoint protegido com token inválido"""
        headers = {"Authorization": "Bearer invalidtoken"}
        
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_admin_endpoint_regular_user(self, setup_database, test_user):
        """Testar endpoint admin com usuário regular"""
        headers = self.get_auth_headers(test_user)
        
        response = client.get("/admin/users", headers=headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_admin_endpoint_admin_user(self, setup_database, admin_user):
        """Testar endpoint admin com usuário admin"""
        headers = self.get_auth_headers(admin_user)
        
        response = client.get("/admin/users", headers=headers)
        
        assert response.status_code == 200


class TestTokenRefresh:
    """Testes para refresh de tokens"""
    
    def test_refresh_token(self, setup_database, test_user):
        """Testar refresh de token"""
        # Fazer login para obter tokens
        login_data = {
            "username": test_user.username,
            "password": "testpassword"
        }
        
        login_response = client.post("/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Usar refresh token para obter novo access token
        refresh_data = {"refresh_token": refresh_token}
        
        response = client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_invalid_token(self, setup_database):
        """Testar refresh com token inválido"""
        refresh_data = {"refresh_token": "invalidtoken"}
        
        response = client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__]) 