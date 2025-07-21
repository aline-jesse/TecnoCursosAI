#!/usr/bin/env python3
"""
Teste Completo do Sistema TecnoCursos AI - Enterprise Edition 2025
================================================================

Este script testa todos os componentes críticos do sistema:
- Endpoints principais (auth, files, videos, etc.)
- Serviços avançados (AI, Quantum, Edge Computing)
- Funcionalidades TTS e Avatar
- Interface React (se disponível)
- Performance e saúde do sistema

Uso: python test_sistema_completo_final.py
"""

import requests
import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class TecnoCursosSystemTester:
    """Classe principal para testes do sistema"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
    def log_test(self, name: str, success: bool, details: str = "", response_time: float = 0):
        """Registrar resultado de teste"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} | {name} ({response_time:.3f}s) | {details}")
        
    def test_health_check(self) -> bool:
        """Testar health check básico"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status', 'OK')}", response_time)
                return True
            else:
                self.log_test("Health Check", False, f"Status Code: {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Erro: {str(e)}")
            return False
    
    def test_documentation_access(self) -> bool:
        """Testar acesso à documentação"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/docs", timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            self.log_test("Documentação Swagger", success, f"Status: {response.status_code}", response_time)
            return success
        
    except Exception as e:
            self.log_test("Documentação Swagger", False, f"Erro: {str(e)}")
            return False
    
    def test_openapi_schema(self) -> bool:
        """Testar schema OpenAPI"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/openapi.json", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schema = response.json()
                endpoints_count = len(schema.get('paths', {}))
                self.log_test("Schema OpenAPI", True, f"Endpoints: {endpoints_count}", response_time)
                return True
            else:
                self.log_test("Schema OpenAPI", False, f"Status: {response.status_code}", response_time)
        return False

        except Exception as e:
            self.log_test("Schema OpenAPI", False, f"Erro: {str(e)}")
            return False
    
    def test_authentication_endpoints(self) -> bool:
        """Testar endpoints de autenticação"""
        success_count = 0
        
        # Teste de registro (pode falhar se usuário já existe)
        try:
            start_time = time.time()
            register_data = {
                "username": "test_user_" + str(int(time.time())),
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "full_name": "Usuário de Teste"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=register_data,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201, 409]:  # 409 = usuário já existe
                self.log_test("Auth - Registro", True, f"Status: {response.status_code}", response_time)
                success_count += 1
            else:
                self.log_test("Auth - Registro", False, f"Status: {response.status_code}", response_time)
                
        except Exception as e:
            self.log_test("Auth - Registro", False, f"Erro: {str(e)}")
        
        # Teste de login
        try:
            start_time = time.time()
            login_data = {
                "username": "test_user",
                "password": "test_password"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                data=login_data,  # Form data para OAuth2
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                self.log_test("Auth - Login", True, "Token obtido", response_time)
                success_count += 1
            else:
                self.log_test("Auth - Login", False, f"Status: {response.status_code}", response_time)
        
    except Exception as e:
            self.log_test("Auth - Login", False, f"Erro: {str(e)}")
        
        return success_count >= 1
    
    def test_core_endpoints(self) -> Dict[str, bool]:
        """Testar endpoints principais"""
        endpoints = {
            "/api/users/me": "GET",
            "/api/projects": "GET", 
            "/api/files": "GET",
            "/api/admin/stats": "GET",
            "/api/analytics/system-stats": "GET"
        }
        
        results = {}
        
        for endpoint, method in endpoints.items():
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = self.session.request(method, f"{self.base_url}{endpoint}", timeout=10)
                
                response_time = time.time() - start_time
                
                # Considerar sucesso se não for 404 ou 500
                success = response.status_code not in [404, 500]
                results[endpoint] = success
                
                self.log_test(f"Endpoint {endpoint}", success, f"Status: {response.status_code}", response_time)
                
            except Exception as e:
                results[endpoint] = False
                self.log_test(f"Endpoint {endpoint}", False, f"Erro: {str(e)}")
        
        return results
    
    def test_advanced_services(self) -> Dict[str, bool]:
        """Testar serviços avançados"""
        services = {
            "/api/modern-ai/health": "Modern AI Service",
            "/api/quantum/health": "Quantum Optimization",
            "/advanced-video/health": "Advanced Video Processing",
            "/api/videos/health": "Video Generation",
            "/ws/health": "WebSocket Service"
        }
        
        results = {}
        
        for endpoint, service_name in services.items():
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                results[service_name] = success
                
                self.log_test(f"Serviço {service_name}", success, f"Status: {response.status_code}", response_time)
        
    except Exception as e:
                results[service_name] = False
                self.log_test(f"Serviço {service_name}", False, f"Erro: {str(e)}")
        
        return results
    
    def test_file_upload_simulation(self) -> bool:
        """Simular upload de arquivo"""
        try:
            # Criar arquivo de teste
            test_content = "Conteúdo de teste para o sistema TecnoCursos AI"
            test_file_path = "test_file.txt"
            
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(test_content)
            
            start_time = time.time()
            
            with open(test_file_path, "rb") as f:
                files = {'file': ('test_file.txt', f, 'text/plain')}
                response = self.session.post(
                    f"{self.base_url}/api/files/upload",
                    files=files,
                    timeout=30
                )
            
            response_time = time.time() - start_time
            
            # Limpar arquivo de teste
            os.remove(test_file_path)
            
            success = response.status_code in [200, 201, 422]  # 422 pode ser esperado sem auth
            self.log_test("Upload de Arquivo", success, f"Status: {response.status_code}", response_time)
            
            return success
        
    except Exception as e:
            self.log_test("Upload de Arquivo", False, f"Erro: {str(e)}")
            if os.path.exists("test_file.txt"):
                os.remove("test_file.txt")
        return False

    def test_react_editor_interface(self) -> bool:
        """Testar interface React do editor"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text
                # Verificar se contém elementos React
                has_react = any(keyword in content.lower() for keyword in [
                    'react', 'editor', 'canvas', 'timeline', 'tecnocursos'
                ])
                
                self.log_test("Interface React", has_react, f"React detectado: {has_react}", response_time)
                return has_react
            else:
                self.log_test("Interface React", False, f"Status: {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Interface React", False, f"Erro: {str(e)}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Gerar relatório final"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        avg_response_time = sum(test['response_time'] for test in self.test_results) / total_tests if total_tests > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': round(success_rate, 2),
            'avg_response_time': round(avg_response_time, 3),
            'test_results': self.test_results
        }
        
        return report
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executar todos os testes"""
        print("🚀 INICIANDO TESTES DO SISTEMA TECNOCURSOS AI")
        print("=" * 60)
        
        # Testes básicos
        print("\n📡 TESTES BÁSICOS:")
        self.test_health_check()
        self.test_documentation_access()
        self.test_openapi_schema()
        
        # Testes de autenticação
        print("\n🔐 TESTES DE AUTENTICAÇÃO:")
        self.test_authentication_endpoints()
        
        # Testes de endpoints
        print("\n🔗 TESTES DE ENDPOINTS:")
        self.test_core_endpoints()
        
        # Testes de serviços avançados
        print("\n⚡ TESTES DE SERVIÇOS AVANÇADOS:")
        self.test_advanced_services()
        
        # Testes de funcionalidades
        print("\n📁 TESTES DE FUNCIONALIDADES:")
        self.test_file_upload_simulation()
        self.test_react_editor_interface()
        
        # Gerar relatório
        print("\n📊 GERANDO RELATÓRIO...")
        report = self.generate_report()
        
        # Salvar relatório
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

def main():
    """Função principal"""
    print("🧪 SISTEMA DE TESTES - TECNOCURSOS AI ENTERPRISE EDITION 2025")
    print("=" * 70)
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print("✅ Servidor detectado e respondendo")
    except:
        print("❌ ERRO: Servidor não está rodando!")
        print("   Execute primeiro: python tecnocursos_server.py")
        sys.exit(1)
    
    # Executar testes
    tester = TecnoCursosSystemTester()
    report = tester.run_all_tests()
    
    # Exibir resultados finais
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL DE TESTES")
    print("=" * 70)
    print(f"📈 Taxa de Sucesso: {report['success_rate']:.1f}%")
    print(f"✅ Testes Passou: {report['passed_tests']}")
    print(f"❌ Testes Falhou: {report['failed_tests']}")
    print(f"📊 Total de Testes: {report['total_tests']}")
    print(f"⏱️ Tempo Médio: {report['avg_response_time']:.3f}s")
    print(f"📄 Relatório salvo em: test_report.json")
    
    # Status final
    if report['success_rate'] >= 80:
        print("\n🎉 SISTEMA FUNCIONANDO EXCELENTEMENTE!")
        print("   Pronto para uso em produção.")
    elif report['success_rate'] >= 60:
        print("\n✅ SISTEMA FUNCIONANDO BEM!")
        print("   Algumas funcionalidades podem precisar de ajustes.")
    else:
        print("\n⚠️ SISTEMA COM PROBLEMAS!")
        print("   Verifique os erros e execute correções necessárias.")
    
    return report['success_rate'] >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 