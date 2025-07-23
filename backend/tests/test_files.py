"""
Testes para upload e gerenciamento de arquivos
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, Project, FileUpload
from app.auth import get_password_hash

# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_files.db"

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
def test_project(test_user):
    """Criar projeto de teste"""
    db = TestingSessionLocal()
    project = Project(
        title="Projeto Teste",
        description="Descrição do projeto teste",
        category="programacao",
        owner_id=test_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    db.close()
    return project


@pytest.fixture
def auth_headers(test_user):
    """Obter headers de autenticação"""
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestFileUpload:
    """Testes para upload de arquivos"""
    
    def create_test_file(self, content: bytes, filename: str):
        """Criar arquivo de teste temporário"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_upload_pdf_file(self, setup_database, test_project, auth_headers):
        """Testar upload de arquivo PDF"""
        # Criar arquivo PDF de teste
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        temp_file = self.create_test_file(pdf_content, ".pdf")
        
        try:
            with open(temp_file, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"project_id": test_project.id}
                
                response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            assert response.status_code == 201
            result = response.json()
            assert result["filename"].endswith(".pdf")
            assert result["file_type"] == "PDF"
            assert result["project_id"] == test_project.id
            assert "file_url" in result
        
        finally:
            os.unlink(temp_file)
    
    def test_upload_pptx_file(self, setup_database, test_project, auth_headers):
        """Testar upload de arquivo PPTX"""
        # Criar arquivo PPTX de teste (simplified)
        pptx_content = b"PK\x03\x04" + b"fake pptx content"
        temp_file = self.create_test_file(pptx_content, ".pptx")
        
        try:
            with open(temp_file, "rb") as f:
                files = {"file": ("presentation.pptx", f, "application/vnd.openxmlformats-officedocument.presentationml.presentation")}
                data = {"project_id": test_project.id}
                
                response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            assert response.status_code == 201
            result = response.json()
            assert result["filename"].endswith(".pptx")
            assert result["file_type"] == "PPTX"
            assert result["project_id"] == test_project.id
        
        finally:
            os.unlink(temp_file)
    
    def test_upload_invalid_file_type(self, setup_database, test_project, auth_headers):
        """Testar upload de tipo de arquivo inválido"""
        # Criar arquivo de tipo não suportado
        invalid_content = b"invalid file content"
        temp_file = self.create_test_file(invalid_content, ".exe")
        
        try:
            with open(temp_file, "rb") as f:
                files = {"file": ("malware.exe", f, "application/x-executable")}
                data = {"project_id": test_project.id}
                
                response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            assert response.status_code == 400
            assert "Invalid file type" in response.json()["detail"]
        
        finally:
            os.unlink(temp_file)
    
    def test_upload_file_too_large(self, setup_database, test_project, auth_headers):
        """Testar upload de arquivo muito grande"""
        # Criar arquivo muito grande (simular)
        large_content = b"x" * (50 * 1024 * 1024 + 1)  # 50MB + 1 byte
        temp_file = self.create_test_file(large_content, ".pdf")
        
        try:
            with open(temp_file, "rb") as f:
                files = {"file": ("large.pdf", f, "application/pdf")}
                data = {"project_id": test_project.id}
                
                response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            assert response.status_code == 413
        
        finally:
            os.unlink(temp_file)
    
    def test_upload_without_authentication(self, setup_database, test_project):
        """Testar upload sem autenticação"""
        pdf_content = b"%PDF-1.4\ntest content"
        temp_file = self.create_test_file(pdf_content, ".pdf")
        
        try:
            with open(temp_file, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"project_id": test_project.id}
                
                response = client.post(
                    "/files/upload",
                    files=files,
                    data=data
                )
            
            assert response.status_code == 401
        
        finally:
            os.unlink(temp_file)
    
    def test_upload_to_nonexistent_project(self, setup_database, auth_headers):
        """Testar upload para projeto inexistente"""
        pdf_content = b"%PDF-1.4\ntest content"
        temp_file = self.create_test_file(pdf_content, ".pdf")
        
        try:
            with open(temp_file, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"project_id": 99999}
                
                response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            assert response.status_code == 404
            assert "Project not found" in response.json()["detail"]
        
        finally:
            os.unlink(temp_file)


class TestFileManagement:
    """Testes para gerenciamento de arquivos"""
    
    def test_list_files(self, setup_database, test_project, auth_headers):
        """Testar listagem de arquivos"""
        response = client.get(
            f"/files/project/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_file_details(self, setup_database, test_project, auth_headers):
        """Testar obtenção de detalhes do arquivo"""
        # Primeiro fazer upload de um arquivo
        pdf_content = b"%PDF-1.4\ntest content"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(pdf_content)
        temp_file.close()
        
        try:
            # Upload
            with open(temp_file.name, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"project_id": test_project.id}
                
                upload_response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            file_id = upload_response.json()["id"]
            
            # Obter detalhes
            response = client.get(
                f"/files/{file_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            file_data = response.json()
            assert file_data["id"] == file_id
            assert file_data["file_type"] == "PDF"
            assert file_data["project_id"] == test_project.id
        
        finally:
            os.unlink(temp_file.name)
    
    def test_delete_file(self, setup_database, test_project, auth_headers):
        """Testar exclusão de arquivo"""
        # Primeiro fazer upload de um arquivo
        pdf_content = b"%PDF-1.4\ntest content"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(pdf_content)
        temp_file.close()
        
        try:
            # Upload
            with open(temp_file.name, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"project_id": test_project.id}
                
                upload_response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            file_id = upload_response.json()["id"]
            
            # Excluir
            response = client.delete(
                f"/files/{file_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert "successfully deleted" in response.json()["message"]
            
            # Verificar se foi excluído
            get_response = client.get(
                f"/files/{file_id}",
                headers=auth_headers
            )
            assert get_response.status_code == 404
        
        finally:
            os.unlink(temp_file.name)


class TestFileProcessing:
    """Testes para processamento de arquivos"""
    
    def test_file_processing_status(self, setup_database, test_project, auth_headers):
        """Testar status de processamento de arquivo"""
        # Upload de arquivo
        pdf_content = b"%PDF-1.4\ntest content"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(pdf_content)
        temp_file.close()
        
        try:
            with open(temp_file.name, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"project_id": test_project.id}
                
                upload_response = client.post(
                    "/files/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            file_id = upload_response.json()["id"]
            
            # Verificar status de processamento
            response = client.get(
                f"/files/{file_id}/processing-status",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            status_data = response.json()
            assert "processing_status" in status_data
            assert "processing_progress" in status_data
        
        finally:
            os.unlink(temp_file.name)


class TestFileValidation:
    """Testes para validação de arquivos"""
    
    def test_validate_pdf_file(self):
        """Testar validação de arquivo PDF"""
        from app.utils import validate_file_type
        
        # PDF válido
        assert validate_file_type("document.pdf", "application/pdf") is True
        
        # PDF com MIME type incorreto
        assert validate_file_type("document.pdf", "text/plain") is False
        
        # Extensão incorreta
        assert validate_file_type("document.txt", "application/pdf") is False
    
    def test_validate_pptx_file(self):
        """Testar validação de arquivo PPTX"""
        from app.utils import validate_file_type
        
        # PPTX válido
        pptx_mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        assert validate_file_type("presentation.pptx", pptx_mime) is True
        
        # PPTX com MIME type incorreto
        assert validate_file_type("presentation.pptx", "text/plain") is False
    
    def test_get_file_category(self):
        """Testar categorização de arquivos"""
        from app.utils import get_file_category
        
        assert get_file_category("document.pdf") == "PDF"
        assert get_file_category("presentation.pptx") == "PPTX"
        assert get_file_category("image.jpg") == "IMAGE"
        assert get_file_category("video.mp4") == "VIDEO"
        assert get_file_category("unknown.xyz") == "OTHER"


if __name__ == "__main__":
    pytest.main([__file__]) 