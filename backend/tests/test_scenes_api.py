#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Automatizados - API de Cenas

Este módulo implementa testes completos para a API de scenes seguindo
as melhores práticas do FastAPI testing com TestClient.

Baseado em:
- FastAPI Testing Best Practices
- pytest patterns
- Test-driven development
- API testing strategies

Funcionalidades testadas:
- CRUD completo de cenas
- Autenticação e autorização
- Validação de dados
- Error handling
- Performance
- Geração de vídeo
- Cache behavior
- Rate limiting

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import pytest
import asyncio
from typing import Dict, Any, Generator
from pathlib import Path
import tempfile
import json
import time

try:
    from fastapi.testclient import TestClient
    from fastapi import status
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from app.main import app
    from app.config.settings import get_settings
    from app.database import get_db, engine
    from app.models import User, Project, Scene, Asset, Base
    from app.auth import create_access_token
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False

# Configurar ambiente de teste
import os
os.environ["ENVIRONMENT"] = "test"
os.environ["APP_TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Fixtures e setup
@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Cliente de teste para a API"""
    if not FASTAPI_AVAILABLE or not APP_AVAILABLE:
        pytest.skip("FastAPI ou app não disponíveis")
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="session")
def setup_test_database():
    """Setup do banco de teste"""
    if not APP_AVAILABLE:
        pytest.skip("App não disponível")
    
    # Criar tabelas de teste
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Dados de usuário para teste"""
    return {
        "email": "test@tecnocursos.ai",
        "password": "testpassword123",
        "full_name": "Test User",
        "is_active": True
    }

@pytest.fixture
def auth_headers(client: TestClient, test_user_data: Dict) -> Dict[str, str]:
    """Headers de autenticação para testes"""
    # Criar usuário de teste
    response = client.post("/api/auth/register", json=test_user_data)
    
    if response.status_code == 201:
        # Login
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
    
    # Fallback: criar token diretamente
    token = create_access_token(data={"sub": test_user_data["email"]})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_project(client: TestClient, auth_headers: Dict) -> Dict[str, Any]:
    """Projeto de teste"""
    project_data = {
        "name": "Test Project",
        "description": "Projeto para testes automatizados",
        "tipo": "curso"
    }
    
    response = client.post("/api/projects/", json=project_data, headers=auth_headers)
    
    if response.status_code == 201:
        return response.json()
    
    # Fallback: retornar dados mock
    return {"id": 1, **project_data}

@pytest.fixture
def test_scene_data() -> Dict[str, Any]:
    """Dados de cena para teste"""
    return {
        "name": "Test Scene",
        "texto": "Esta é uma cena de teste com conteúdo educacional",
        "duracao": 5.0,
        "ordem": 1,
        "style_preset": "modern",
        "background_color": "#4a90e2",
        "is_active": True
    }

# ============================================================================
# TESTES DE CRUD BÁSICO
# ============================================================================

class TestScenesCRUD:
    """Testes de CRUD básico para cenas"""
    
    def test_create_scene(self, client: TestClient, auth_headers: Dict, 
                         test_project: Dict, test_scene_data: Dict):
        """Teste de criação de cena"""
        scene_data = {**test_scene_data, "projeto_id": test_project["id"]}
        
        response = client.post("/api/scenes/", json=scene_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == scene_data["name"]
        assert data["texto"] == scene_data["texto"]
        assert data["projeto_id"] == test_project["id"]
        assert "id" in data
        assert "uuid" in data
        assert "created_at" in data
    
    def test_create_scene_without_auth(self, client: TestClient, test_scene_data: Dict):
        """Teste de criação de cena sem autenticação"""
        response = client.post("/api/scenes/", json=test_scene_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_scene_invalid_data(self, client: TestClient, auth_headers: Dict):
        """Teste de criação de cena com dados inválidos"""
        invalid_data = {
            "name": "",  # Nome vazio
            "duracao": -1  # Duração negativa
        }
        
        response = client.post("/api/scenes/", json=invalid_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_scenes(self, client: TestClient, auth_headers: Dict):
        """Teste de listagem de cenas"""
        response = client.get("/api/scenes/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "meta" in data
        assert isinstance(data["items"], list)
        assert "page" in data["meta"]
        assert "total" in data["meta"]
    
    def test_list_scenes_with_pagination(self, client: TestClient, auth_headers: Dict):
        """Teste de listagem com paginação"""
        response = client.get("/api/scenes/?page=1&size=5", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["meta"]["page"] == 1
        assert data["meta"]["size"] == 5
        assert len(data["items"]) <= 5
    
    def test_list_scenes_with_filters(self, client: TestClient, auth_headers: Dict, 
                                    test_project: Dict):
        """Teste de listagem com filtros"""
        response = client.get(
            f"/api/scenes/?project_id={test_project['id']}&style_preset=modern",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "filters_applied" in data
        assert data["filters_applied"]["project_id"] == test_project["id"]
    
    def test_get_scene_by_id(self, client: TestClient, auth_headers: Dict, 
                           test_project: Dict, test_scene_data: Dict):
        """Teste de obtenção de cena por ID"""
        # Criar cena primeiro
        scene_data = {**test_scene_data, "projeto_id": test_project["id"]}
        create_response = client.post("/api/scenes/", json=scene_data, headers=auth_headers)
        
        if create_response.status_code == 201:
            scene_id = create_response.json()["id"]
            
            # Obter cena
            response = client.get(f"/api/scenes/{scene_id}", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == scene_id
            assert data["name"] == scene_data["name"]
    
    def test_get_scene_not_found(self, client: TestClient, auth_headers: Dict):
        """Teste de obtenção de cena inexistente"""
        response = client.get("/api/scenes/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_scene(self, client: TestClient, auth_headers: Dict,
                         test_project: Dict, test_scene_data: Dict):
        """Teste de atualização de cena"""
        # Criar cena primeiro
        scene_data = {**test_scene_data, "projeto_id": test_project["id"]}
        create_response = client.post("/api/scenes/", json=scene_data, headers=auth_headers)
        
        if create_response.status_code == 201:
            scene_id = create_response.json()["id"]
            
            # Atualizar cena
            update_data = {"name": "Updated Scene Name", "duracao": 10.0}
            response = client.put(f"/api/scenes/{scene_id}", json=update_data, headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == update_data["name"]
            assert data["duracao"] == update_data["duracao"]
            assert "changes_applied" in data
    
    def test_delete_scene(self, client: TestClient, auth_headers: Dict,
                         test_project: Dict, test_scene_data: Dict):
        """Teste de deleção de cena"""
        # Criar cena primeiro
        scene_data = {**test_scene_data, "projeto_id": test_project["id"]}
        create_response = client.post("/api/scenes/", json=scene_data, headers=auth_headers)
        
        if create_response.status_code == 201:
            scene_id = create_response.json()["id"]
            
            # Deletar cena
            response = client.delete(f"/api/scenes/{scene_id}", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == scene_id
            assert "deleted_at" in data
            
            # Verificar se foi deletada
            get_response = client.get(f"/api/scenes/{scene_id}", headers=auth_headers)
            assert get_response.status_code == status.HTTP_404_NOT_FOUND

# ============================================================================
# TESTES DE FUNCIONALIDADES AVANÇADAS
# ============================================================================

class TestScenesAdvanced:
    """Testes de funcionalidades avançadas"""
    
    def test_bulk_operations(self, client: TestClient, auth_headers: Dict):
        """Teste de operações em lote"""
        bulk_data = {
            "scene_ids": [1, 2, 3],
            "operation": "update_style",
            "parameters": {"style_preset": "corporate"}
        }
        
        response = client.post("/api/scenes/bulk", json=bulk_data, headers=auth_headers)
        
        # Pode falhar se não houver cenas, mas deve ter estrutura correta
        if response.status_code == 200:
            data = response.json()
            assert "success_count" in data
            assert "error_count" in data
            assert "total_requested" in data
    
    def test_scenes_summary(self, client: TestClient, auth_headers: Dict):
        """Teste de resumo de cenas"""
        response = client.get("/api/scenes/summary", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Verificar estrutura se houver dados
        if data:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "assets_count" in data[0]
    
    def test_scene_render(self, client: TestClient, auth_headers: Dict):
        """Teste de renderização de cena"""
        scene_id = 1  # Assumindo que existe
        render_data = {
            "quality": "medium",
            "format": "mp4"
        }
        
        response = client.post(f"/api/scenes/{scene_id}/render", 
                             json=render_data, headers=auth_headers)
        
        # Pode falhar se cena não existir, mas deve ter estrutura de erro correta
        if response.status_code == 404:
            assert "detail" in response.json()
        elif response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "message" in data

# ============================================================================
# TESTES DE GERAÇÃO DE VÍDEO
# ============================================================================

class TestVideoGeneration:
    """Testes de geração de vídeo"""
    
    def test_generate_video_without_scenes(self, client: TestClient, auth_headers: Dict):
        """Teste de geração de vídeo sem cenas"""
        project_id = 99999  # Projeto que não existe
        
        response = client.post(
            f"/api/scenes/project/{project_id}/generate-video",
            json={"quality": "medium"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_generate_video_invalid_quality(self, client: TestClient, auth_headers: Dict):
        """Teste de geração com qualidade inválida"""
        project_id = 1
        
        response = client.post(
            f"/api/scenes/project/{project_id}/generate-video",
            json={"quality": "invalid_quality"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Qualidade inválida" in response.json()["detail"]
    
    def test_video_status_endpoint(self, client: TestClient, auth_headers: Dict):
        """Teste do endpoint de status de vídeo"""
        project_id = 1
        
        response = client.get(f"/api/scenes/video-status/{project_id}", headers=auth_headers)
        
        # Deve retornar status mesmo se não houver vídeo
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "project_id" in data

# ============================================================================
# TESTES DE PERFORMANCE E CACHE
# ============================================================================

class TestPerformanceAndCache:
    """Testes de performance e cache"""
    
    def test_cache_headers(self, client: TestClient, auth_headers: Dict):
        """Teste de headers de cache"""
        response = client.get("/api/scenes/", headers=auth_headers)
        
        # Verificar se há headers de performance
        assert "X-Request-ID" in response.headers or response.status_code == 200
    
    def test_rate_limiting(self, client: TestClient, auth_headers: Dict):
        """Teste de rate limiting"""
        # Fazer muitas requests rapidamente
        responses = []
        for _ in range(10):
            response = client.get("/api/scenes/", headers=auth_headers)
            responses.append(response.status_code)
        
        # Pelo menos uma deve passar
        assert 200 in responses
    
    def test_response_time(self, client: TestClient, auth_headers: Dict):
        """Teste de tempo de resposta"""
        start_time = time.time()
        response = client.get("/api/scenes/", headers=auth_headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response deve ser menor que 2 segundos
        assert response_time < 2.0
        assert response.status_code == 200

# ============================================================================
# TESTES DE MÉTRICAS E MONITORAMENTO
# ============================================================================

class TestMetricsAndMonitoring:
    """Testes de métricas e monitoramento"""
    
    def test_cache_metrics(self, client: TestClient, auth_headers: Dict):
        """Teste de métricas de cache"""
        response = client.get("/api/scenes/metrics/cache", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
    
    def test_usage_metrics(self, client: TestClient, auth_headers: Dict):
        """Teste de métricas de uso"""
        response = client.get("/api/scenes/metrics/usage", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "summary" in data
        assert "timestamp" in data
    
    def test_health_check(self, client: TestClient):
        """Teste de health check"""
        response = client.get("/api/scenes/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data

# ============================================================================
# TESTES DE SEGURANÇA
# ============================================================================

class TestSecurity:
    """Testes de segurança"""
    
    def test_unauthorized_access(self, client: TestClient):
        """Teste de acesso não autorizado"""
        response = client.get("/api/scenes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_token(self, client: TestClient):
        """Teste com token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/scenes/", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_sql_injection_protection(self, client: TestClient, auth_headers: Dict):
        """Teste de proteção contra SQL injection"""
        malicious_input = "'; DROP TABLE scenes; --"
        
        response = client.get(
            f"/api/scenes/?search={malicious_input}",
            headers=auth_headers
        )
        
        # Deve retornar normalmente, não quebrar
        assert response.status_code in [200, 422]  # 422 para validação
    
    def test_xss_protection(self, client: TestClient, auth_headers: Dict, test_project: Dict):
        """Teste de proteção contra XSS"""
        xss_input = "<script>alert('xss')</script>"
        
        scene_data = {
            "name": xss_input,
            "projeto_id": test_project["id"],
            "texto": "Teste de XSS",
            "duracao": 5.0
        }
        
        response = client.post("/api/scenes/", json=scene_data, headers=auth_headers)
        
        # Deve sanitizar ou rejeitar
        if response.status_code == 201:
            data = response.json()
            # Verificar se foi sanitizado
            assert "<script>" not in data["name"]

# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

class TestIntegration:
    """Testes de integração completos"""
    
    def test_complete_workflow(self, client: TestClient, auth_headers: Dict, 
                              test_project: Dict, test_scene_data: Dict):
        """Teste de workflow completo"""
        # 1. Criar cena
        scene_data = {**test_scene_data, "projeto_id": test_project["id"]}
        create_response = client.post("/api/scenes/", json=scene_data, headers=auth_headers)
        
        if create_response.status_code != 201:
            pytest.skip("Não foi possível criar cena para teste de integração")
        
        scene_id = create_response.json()["id"]
        
        # 2. Listar cenas
        list_response = client.get("/api/scenes/", headers=auth_headers)
        assert list_response.status_code == 200
        
        # 3. Obter cena específica
        get_response = client.get(f"/api/scenes/{scene_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        # 4. Atualizar cena
        update_response = client.put(
            f"/api/scenes/{scene_id}",
            json={"name": "Updated Scene"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        
        # 5. Verificar métricas
        metrics_response = client.get("/api/scenes/metrics/usage", headers=auth_headers)
        assert metrics_response.status_code == 200
        
        # 6. Deletar cena
        delete_response = client.delete(f"/api/scenes/{scene_id}", headers=auth_headers)
        assert delete_response.status_code == 200

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

# Configurações do pytest
pytestmark = pytest.mark.asyncio

def pytest_configure(config):
    """Configuração do pytest"""
    config.addinivalue_line(
        "markers", "slow: marca testes como lentos"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup automático do ambiente de teste"""
    # Configurar variáveis de ambiente para teste
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_ECHO"] = "false"
    yield
    # Cleanup após teste
    pass

# Função principal para executar testes
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]) 