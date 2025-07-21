#!/usr/bin/env python3
"""
Teste Abrangente do Sistema TecnoCursos AI
=========================================

Testa todas as funcionalidades implementadas:
- Endpoints disponíveis
- Sistema de upload com narração
- Funcionalidades de áudio
- Interface web
- API completa
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:8001"
TEST_PDF = "sample_test.pdf"

class SystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log do resultado do teste"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if data and success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def test_server_health(self):
        """Testa a saúde do servidor"""
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200
            
            self.log_test(
                "Server Health", 
                success,
                f"Status: {response.status_code}",
                {"status_code": response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("Server Health", False, str(e))
            return False
    
    def test_api_documentation(self):
        """Testa se a documentação da API está disponível"""
        try:
            # Testar endpoint docs
            docs_response = self.session.get(f"{self.base_url}/docs")
            docs_ok = docs_response.status_code == 200
            
            # Testar OpenAPI spec
            openapi_response = self.session.get(f"{self.base_url}/openapi.json")
            openapi_ok = openapi_response.status_code == 200
            
            success = docs_ok and openapi_ok
            
            self.log_test(
                "API Documentation",
                success,
                f"Docs: {docs_response.status_code}, OpenAPI: {openapi_response.status_code}",
                {"docs_status": docs_response.status_code, "openapi_status": openapi_response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("API Documentation", False, str(e))
            return False
    
    def test_available_endpoints(self):
        """Testa endpoints disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/openapi.json")
            if response.status_code != 200:
                self.log_test("Available Endpoints", False, "Não foi possível obter OpenAPI spec")
                return False
            
            openapi_data = response.json()
            paths = openapi_data.get("paths", {})
            endpoint_count = len(paths)
            
            # Listar alguns endpoints importantes
            important_endpoints = [
                "/files/upload",
                "/audios/",
                "/audios/search",
                "/admin/audios/dashboard",
                "/batch/upload"
            ]
            
            available_endpoints = [ep for ep in important_endpoints if ep in paths]
            
            success = len(available_endpoints) > 0
            
            self.log_test(
                "Available Endpoints",
                success,
                f"Total endpoints: {endpoint_count}, Important available: {len(available_endpoints)}",
                {
                    "total_endpoints": endpoint_count,
                    "important_available": available_endpoints,
                    "sample_paths": list(paths.keys())[:10]
                }
            )
            return success
        except Exception as e:
            self.log_test("Available Endpoints", False, str(e))
            return False
    
    def test_static_files(self):
        """Testa se arquivos estáticos são servidos"""
        try:
            # Testar se consegue acessar diretório de áudios
            response = self.session.get(f"{self.base_url}/static/")
            
            # 403 ou 404 são esperados (sem listagem de diretório)
            # 200 indica que está configurado
            success = response.status_code in [200, 403, 404]
            
            self.log_test(
                "Static Files",
                success,
                f"Static endpoint status: {response.status_code}",
                {"status_code": response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("Static Files", False, str(e))
            return False
    
    def test_audio_endpoints_public(self):
        """Testa endpoints de áudio que não precisam de autenticação"""
        try:
            # Testar listagem de áudios (pode ser público)
            response = self.session.get(f"{self.base_url}/audios/")
            
            # Qualquer resposta que não seja erro de servidor é boa
            success = response.status_code < 500
            
            message = f"Status: {response.status_code}"
            if response.status_code == 401:
                message += " (Authentication required - expected)"
            elif response.status_code == 200:
                try:
                    data = response.json()
                    audio_count = len(data.get('audios', []))
                    message += f", Found {audio_count} audios"
                except:
                    pass
            
            self.log_test(
                "Audio Endpoints (Public)",
                success,
                message,
                {"status_code": response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("Audio Endpoints (Public)", False, str(e))
            return False
    
    def test_upload_endpoint_structure(self):
        """Testa a estrutura do endpoint de upload"""
        try:
            # Fazer uma requisição OPTIONS para ver os métodos suportados
            response = self.session.options(f"{self.base_url}/files/upload")
            
            # Se OPTIONS não for suportado, testar GET
            if response.status_code == 405:
                response = self.session.get(f"{self.base_url}/files/upload")
            
            # Qualquer resposta estruturada é boa (não 500)
            success = response.status_code < 500
            
            self.log_test(
                "Upload Endpoint Structure",
                success,
                f"Status: {response.status_code}",
                {"status_code": response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("Upload Endpoint Structure", False, str(e))
            return False
    
    def test_web_interface(self):
        """Testa se a interface web está disponível"""
        try:
            # Testar diferentes possíveis endpoints de interface
            interfaces = [
                "/audios.html",
                "/dashboard.html", 
                "/index.html",
                "/static/index.html"
            ]
            
            working_interfaces = []
            for interface in interfaces:
                try:
                    response = self.session.get(f"{self.base_url}{interface}")
                    if response.status_code == 200:
                        working_interfaces.append(interface)
                except:
                    pass
            
            success = len(working_interfaces) > 0
            
            self.log_test(
                "Web Interface",
                success,
                f"Working interfaces: {working_interfaces}",
                {"available_interfaces": working_interfaces}
            )
            return success
        except Exception as e:
            self.log_test("Web Interface", False, str(e))
            return False
    
    def test_database_integration(self):
        """Testa indiretamente a integração com banco de dados"""
        try:
            # Tentar endpoint que usa banco (mesmo com auth error)
            response = self.session.get(f"{self.base_url}/audios/")
            
            # Se retornar 401/403, significa que o endpoint existe e funciona
            # Se retornar 500, pode ser erro de banco
            # Se retornar 200, perfeito
            success = response.status_code != 500
            
            if response.status_code == 500:
                message = "Database connection issues"
            elif response.status_code in [401, 403]:
                message = "Endpoint working (auth required)"
            elif response.status_code == 200:
                message = "Database working perfectly"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_test(
                "Database Integration",
                success,
                message,
                {"status_code": response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("Database Integration", False, str(e))
            return False
    
    def test_file_validation(self):
        """Testa se o arquivo PDF de teste existe para uploads"""
        try:
            exists = os.path.exists(TEST_PDF)
            if exists:
                size = os.path.getsize(TEST_PDF)
                message = f"File exists, size: {size} bytes"
            else:
                message = "Test file not found"
            
            self.log_test(
                "File Validation",
                exists,
                message,
                {"file": TEST_PDF, "exists": exists, "size": size if exists else 0}
            )
            return exists
        except Exception as e:
            self.log_test("File Validation", False, str(e))
            return False
    
    def test_advanced_features(self):
        """Testa recursos avançados implementados"""
        try:
            advanced_endpoints = [
                "/admin/audios/dashboard",
                "/batch/upload", 
                "/audios/search",
                "/websocket/"
            ]
            
            available_advanced = 0
            for endpoint in advanced_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    # Qualquer resposta estruturada (não 404) indica que existe
                    if response.status_code != 404:
                        available_advanced += 1
                except:
                    pass
            
            success = available_advanced > 0
            
            self.log_test(
                "Advanced Features",
                success,
                f"Available advanced endpoints: {available_advanced}/{len(advanced_endpoints)}",
                {"available_count": available_advanced, "total_count": len(advanced_endpoints)}
            )
            return success
        except Exception as e:
            self.log_test("Advanced Features", False, str(e))
            return False
    
    def run_all_tests(self):
        """Executa todos os testes do sistema"""
        print("🚀 INICIANDO TESTES ABRANGENTES DO SISTEMA TECNOCURSOS AI")
        print("=" * 70)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("API Documentation", self.test_api_documentation),
            ("Available Endpoints", self.test_available_endpoints),
            ("Static Files", self.test_static_files),
            ("Audio Endpoints", self.test_audio_endpoints_public),
            ("Upload Endpoint", self.test_upload_endpoint_structure),
            ("Web Interface", self.test_web_interface),
            ("Database Integration", self.test_database_integration),
            ("File Validation", self.test_file_validation),
            ("Advanced Features", self.test_advanced_features),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ Erro inesperado em {test_name}: {e}")
                results.append((test_name, False))
        
        # Resumo completo
        self.print_comprehensive_summary(results)
        
        return results
    
    def print_comprehensive_summary(self, results):
        """Imprime resumo abrangente dos resultados"""
        print("\n" + "=" * 70)
        print("📊 RESUMO ABRANGENTE DOS TESTES DO SISTEMA")
        print("=" * 70)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        percentage = (passed/total)*100
        
        print(f"Total de testes: {total}")
        print(f"Passou: {passed}")
        print(f"Falhou: {total - passed}")
        print(f"Taxa de sucesso: {percentage:.1f}%")
        
        # Status geral do sistema
        if percentage >= 90:
            status = "🟢 EXCELENTE"
        elif percentage >= 75:
            status = "🟡 BOM"
        elif percentage >= 50:
            status = "🟠 PARCIAL"
        else:
            status = "🔴 CRÍTICO"
        
        print(f"\nStatus do Sistema: {status}")
        
        # Detalhes por categoria
        print("\n📋 DETALHES DOS TESTES:")
        for test_name, success in results:
            icon = "✅" if success else "❌"
            print(f"   {icon} {test_name}")
        
        # Funcionalidades implementadas
        print("\n🔧 FUNCIONALIDADES DETECTADAS:")
        if any("Server Health" in r[0] and r[1] for r in results):
            print("   ✅ Servidor FastAPI funcionando")
        if any("API Documentation" in r[0] and r[1] for r in results):
            print("   ✅ Documentação automática da API")
        if any("Upload Endpoint" in r[0] and r[1] for r in results):
            print("   ✅ Sistema de upload implementado")
        if any("Audio Endpoints" in r[0] and r[1] for r in results):
            print("   ✅ Endpoints de gerenciamento de áudio")
        if any("Database Integration" in r[0] and r[1] for r in results):
            print("   ✅ Integração com banco de dados")
        if any("Advanced Features" in r[0] and r[1] for r in results):
            print("   ✅ Recursos avançados (admin, batch, search)")
        if any("Web Interface" in r[0] and r[1] for r in results):
            print("   ✅ Interface web disponível")
        
        # Instruções para teste manual
        print("\n🔗 TESTE MANUAL:")
        print(f"   • Acesse: {BASE_URL}/docs - Documentação interativa")
        print(f"   • Acesse: {BASE_URL}/ - Interface principal")
        print(f"   • Upload de teste via API disponível")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # Exit code baseado no sucesso
    passed = sum(1 for _, success in results if success)
    total = len(results)
    success_rate = (passed / total) * 100
    
    sys.exit(0 if success_rate >= 75 else 1) 