"""
Testes para API Principal - TecnoCursosAI
Testes básicos de integração e funcionamento
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.database import get_db, Base
from app.models import User

# Configurar banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override da dependência do banco para testes"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente de teste
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Setup do banco de dados para testes"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    """Criar usuário de teste"""
    db = TestingSessionLocal()
    user = User(
        name="Usuário Teste",
        email="teste@exemplo.com",
        is_active=True,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()
    db.close()

def test_root_endpoint():
    """Testar endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "TecnoCursosAI API está funcionando!" in response.json()["message"]

def test_health_check():
    """Testar health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_invalid_file():
    """Testar upload com arquivo inválido"""
    # Criar arquivo temporário com extensão inválida
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(b"conteudo de teste")
        tmp.flush()
        
        with open(tmp.name, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("test.txt", f, "text/plain")},
                data={
                    "project_name": "Projeto Teste",
                    "description": "Descrição teste"
                }
            )
    
    os.unlink(tmp.name)
    assert response.status_code == 400
    assert "não suportado" in response.json()["detail"]

def test_projects_list_empty(setup_database):
    """Testar listagem de projetos vazia"""
    response = client.get("/projects")
    # Sem autenticação, deve retornar 401 ou similar
    assert response.status_code in [401, 403]

def test_openapi_docs():
    """Testar documentação OpenAPI"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "TecnoCursosAI" in response.json()["info"]["title"]

if __name__ == "__main__":
    pytest.main([__file__]) 