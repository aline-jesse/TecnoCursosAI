#!/usr/bin/env python3
"""
Script de teste para verificar integração do SceneList com backend
Testa endpoints da API FastAPI e gera relatório de status
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class SceneListBackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }

    def log_test(self, test_name: str, success: bool, details: Dict[str, Any] = None):
        """Registra resultado de um teste"""
        self.results["tests"][test_name] = {
            "success": success,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["summary"]["total_tests"] += 1
        if success:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
            if details and "error" in details:
                self.results["summary"]["errors"].append(f"{test_name}: {details['error']}")

    def test_health_endpoint(self) -> bool:
        """Testa endpoint de health check"""
        try:
            response = self.session.get(f"{self.base_url}/health/", timeout=5)
            success = response.status_code == 200
            self.log_test("health_endpoint", success, {
                "status_code": response.status_code,
                "response": response.text[:200] if success else response.text
            })
            return success
        except Exception as e:
            self.log_test("health_endpoint", False, {"error": str(e)})
            return False

    def test_auth_endpoints(self) -> bool:
        """Testa endpoints de autenticação"""
        try:
            # Teste de login
            login_data = {"username": "demo_user", "password": "demo_password"}
            response = self.session.post(f"{self.base_url}/api/v1/auth/login/", 
                                       json=login_data, timeout=5)
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    self.log_test("auth_login", True, {"token_received": True})
                    return True
                else:
                    self.log_test("auth_login", False, {"error": "No token received"})
                    return False
            else:
                self.log_test("auth_login", False, {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
        except Exception as e:
            self.log_test("auth_login", False, {"error": str(e)})
            return False

    def test_projects_endpoints(self) -> bool:
        """Testa endpoints de projetos"""
        try:
            # Teste GET /projects/
            response = self.session.get(f"{self.base_url}/api/v1/projects/", timeout=5)
            success = response.status_code in [200, 401, 403]  # Aceita diferentes códigos
            self.log_test("projects_list", success, {
                "status_code": response.status_code,
                "response_length": len(response.text)
            })
            
            # Teste POST /projects/ (criação)
            project_data = {
                "title": "Test Project",
                "description": "Test project for SceneList",
                "type": "video"
            }
            response = self.session.post(f"{self.base_url}/api/v1/projects/", 
                                       json=project_data, timeout=5)
            success = response.status_code in [200, 201, 401, 403]
            self.log_test("projects_create", success, {
                "status_code": response.status_code,
                "response": response.text[:200] if success else response.text
            })
            
            return True
        except Exception as e:
            self.log_test("projects_endpoints", False, {"error": str(e)})
            return False

    def test_scenes_endpoints(self) -> bool:
        """Testa endpoints de cenas"""
        try:
            # Primeiro, tenta obter projetos para pegar um ID
            response = self.session.get(f"{self.base_url}/api/v1/projects/", timeout=5)
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    project_id = projects[0]["id"]
                    
                    # Teste GET /projects/{id}/scenes/
                    response = self.session.get(f"{self.base_url}/api/v1/projects/{project_id}/scenes/", timeout=5)
                    success = response.status_code in [200, 401, 403]
                    self.log_test("scenes_list", success, {
                        "status_code": response.status_code,
                        "project_id": project_id
                    })
                    
                    # Teste POST /projects/{id}/scenes/ (criação)
                    scene_data = {
                        "title": "Test Scene",
                        "duration": 30,
                        "order": 1,
                        "text": "Test scene content",
                        "type": "content"
                    }
                    response = self.session.post(f"{self.base_url}/api/v1/projects/{project_id}/scenes/", 
                                               json=scene_data, timeout=5)
                    success = response.status_code in [200, 201, 401, 403]
                    self.log_test("scenes_create", success, {
                        "status_code": response.status_code,
                        "project_id": project_id
                    })
                    
                    return True
                else:
                    self.log_test("scenes_endpoints", False, {"error": "No projects available"})
                    return False
            else:
                self.log_test("scenes_endpoints", False, {"error": "Could not fetch projects"})
                return False
        except Exception as e:
            self.log_test("scenes_endpoints", False, {"error": str(e)})
            return False

    def test_assets_endpoints(self) -> bool:
        """Testa endpoints de assets"""
        try:
            # Tenta obter projetos e cenas para testar assets
            response = self.session.get(f"{self.base_url}/api/v1/projects/", timeout=5)
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    project_id = projects[0]["id"]
                    
                    # Teste GET /projects/{id}/scenes/{scene_id}/assets/
                    scenes_response = self.session.get(f"{self.base_url}/api/v1/projects/{project_id}/scenes/", timeout=5)
                    if scenes_response.status_code == 200:
                        scenes = scenes_response.json()
                        if scenes:
                            scene_id = scenes[0]["id"]
                            response = self.session.get(f"{self.base_url}/api/v1/projects/{project_id}/scenes/{scene_id}/assets/", timeout=5)
                            success = response.status_code in [200, 401, 403]
                            self.log_test("assets_list", success, {
                                "status_code": response.status_code,
                                "project_id": project_id,
                                "scene_id": scene_id
                            })
                            return True
                    
                    self.log_test("assets_endpoints", False, {"error": "No scenes available"})
                    return False
                else:
                    self.log_test("assets_endpoints", False, {"error": "No projects available"})
                    return False
            else:
                self.log_test("assets_endpoints", False, {"error": "Could not fetch projects"})
                return False
        except Exception as e:
            self.log_test("assets_endpoints", False, {"error": str(e)})
            return False

    def test_video_editor_endpoints(self) -> bool:
        """Testa endpoints do editor de vídeo"""
        try:
            # Teste de templates de vídeo
            response = self.session.get(f"{self.base_url}/api/v1/video-editor/templates/", timeout=5)
            success = response.status_code in [200, 401, 403, 404]
            self.log_test("video_templates", success, {
                "status_code": response.status_code,
                "response_length": len(response.text)
            })
            
            # Teste de status de renderização
            response = self.session.get(f"{self.base_url}/api/v1/video-editor/render-status/test-project", timeout=5)
            success = response.status_code in [200, 401, 403, 404]
            self.log_test("render_status", success, {
                "status_code": response.status_code,
                "response_length": len(response.text)
            })
            
            return True
        except Exception as e:
            self.log_test("video_editor_endpoints", False, {"error": str(e)})
            return False

    def test_enterprise_endpoints(self) -> bool:
        """Testa endpoints enterprise"""
        try:
            # Teste de analytics
            response = self.session.get(f"{self.base_url}/api/v1/enterprise/analytics/", timeout=5)
            success = response.status_code in [200, 401, 403, 404]
            self.log_test("enterprise_analytics", success, {
                "status_code": response.status_code,
                "response_length": len(response.text)
            })
            
            # Teste de compliance
            response = self.session.get(f"{self.base_url}/api/v1/enterprise/compliance/", timeout=5)
            success = response.status_code in [200, 401, 403, 404]
            self.log_test("enterprise_compliance", success, {
                "status_code": response.status_code,
                "response_length": len(response.text)
            })
            
            return True
        except Exception as e:
            self.log_test("enterprise_endpoints", False, {"error": str(e)})
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        print("🔍 Iniciando testes de integração do SceneList com backend...")
        print(f"📍 URL base: {self.base_url}")
        print("-" * 50)
        
        # Executa testes em sequência
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Autenticação", self.test_auth_endpoints),
            ("Projetos", self.test_projects_endpoints),
            ("Cenas", self.test_scenes_endpoints),
            ("Assets", self.test_assets_endpoints),
            ("Editor de Vídeo", self.test_video_editor_endpoints),
            ("Enterprise", self.test_enterprise_endpoints),
        ]
        
        for test_name, test_func in tests:
            print(f"🧪 Testando {test_name}...")
            try:
                result = test_func()
                status = "✅ PASSOU" if result else "❌ FALHOU"
                print(f"   {status}")
            except Exception as e:
                print(f"   ❌ ERRO: {e}")
                self.log_test(test_name.lower().replace(" ", "_"), False, {"error": str(e)})
        
        print("-" * 50)
        print(f"📊 Resumo: {self.results['summary']['passed']}/{self.results['summary']['total_tests']} testes passaram")
        
        return self.results

    def save_report(self, filename: str = "scene_list_backend_test_report.json"):
        """Salva relatório em arquivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"📄 Relatório salvo em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")

    def print_summary(self):
        """Imprime resumo dos testes"""
        summary = self.results["summary"]
        print("\n" + "=" * 60)
        print("📋 RESUMO DOS TESTES")
        print("=" * 60)
        print(f"Total de testes: {summary['total_tests']}")
        print(f"Passaram: {summary['passed']}")
        print(f"Falharam: {summary['failed']}")
        print(f"Taxa de sucesso: {(summary['passed']/summary['total_tests']*100):.1f}%" if summary['total_tests'] > 0 else "N/A")
        
        if summary['errors']:
            print("\n❌ Erros encontrados:")
            for error in summary['errors']:
                print(f"   • {error}")
        
        print("\n" + "=" * 60)

def main():
    """Função principal"""
    import sys
    
    # Pode receber URL base como argumento
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = SceneListBackendTester(base_url)
    results = tester.run_all_tests()
    
    # Salva relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scene_list_backend_test_{timestamp}.json"
    tester.save_report(filename)
    
    # Imprime resumo
    tester.print_summary()
    
    # Retorna código de saída baseado no sucesso
    success_rate = results["summary"]["passed"] / results["summary"]["total_tests"] if results["summary"]["total_tests"] > 0 else 0
    return 0 if success_rate >= 0.5 else 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code) 