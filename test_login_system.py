#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de login do TecnoCursos AI
"""

import requests
import json
import sys
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "full_name": "Usuário de Teste",
    "email": "teste@tecnocursos.ai",
    "password": "senha123",
    "username": "teste_user"
}

class LoginTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        
    def print_result(self, test_name, success, details=""):
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"\n{test_name}: {status}")
        if details:
            print(f"   Detalhes: {details}")
    
    def test_health_check(self):
        """Testa se o servidor está online"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            self.print_result("Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_result("Health Check", False, f"Erro: {str(e)}")
            return False
    
    def test_register(self):
        """Testa o registro de novo usuário"""
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                json=TEST_USER
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.print_result("Registro", True, "Usuário criado com sucesso")
                return True
            elif response.status_code == 400:
                # Usuário já existe, tentar login
                self.print_result("Registro", True, "Usuário já existe")
                return True
            else:
                self.print_result("Registro", False, f"Status: {response.status_code}, Resposta: {response.text}")
                return False
                
        except Exception as e:
            self.print_result("Registro", False, f"Erro: {str(e)}")
            return False
    
    def test_login(self):
        """Testa o login com credenciais válidas"""
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                user_info = data.get("user", {})
                
                self.print_result(
                    "Login", 
                    True, 
                    f"Token recebido, Usuário: {user_info.get('email', 'N/A')}"
                )
                return True
            else:
                self.print_result("Login", False, f"Status: {response.status_code}, Resposta: {response.text}")
                return False
                
        except Exception as e:
            self.print_result("Login", False, f"Erro: {str(e)}")
            return False
    
    def test_invalid_login(self):
        """Testa login com credenciais inválidas"""
        try:
            login_data = {
                "email": "invalido@teste.com",
                "password": "senhaerrada"
            }
            
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            )
            
            success = response.status_code == 401
            self.print_result(
                "Login Inválido", 
                success, 
                f"Status: {response.status_code} (esperado 401)"
            )
            return success
            
        except Exception as e:
            self.print_result("Login Inválido", False, f"Erro: {str(e)}")
            return False
    
    def test_protected_endpoint(self):
        """Testa acesso a endpoint protegido"""
        if not self.access_token:
            self.print_result("Endpoint Protegido", False, "Token não disponível")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(f"{BASE_URL}/users/me", headers=headers)
            
            success = response.status_code == 200
            if success:
                user_data = response.json()
                self.print_result(
                    "Endpoint Protegido", 
                    True, 
                    f"Acesso autorizado, Email: {user_data.get('email', 'N/A')}"
                )
            else:
                self.print_result("Endpoint Protegido", False, f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.print_result("Endpoint Protegido", False, f"Erro: {str(e)}")
            return False
    
    def test_refresh_token(self):
        """Testa renovação do token"""
        if not self.refresh_token:
            self.print_result("Refresh Token", False, "Refresh token não disponível")
            return False
            
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get("access_token")
                self.print_result("Refresh Token", True, "Novo token gerado")
                return True
            else:
                self.print_result("Refresh Token", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Refresh Token", False, f"Erro: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 60)
        print("🔐 TESTE DO SISTEMA DE LOGIN - TECNOCURSOS AI")
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL Base: {BASE_URL}")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 0
        
        # Lista de testes
        tests = [
            self.test_health_check,
            self.test_register,
            self.test_login,
            self.test_invalid_login,
            self.test_protected_endpoint,
            self.test_refresh_token
        ]
        
        # Executar testes
        for test in tests:
            total_tests += 1
            if test():
                tests_passed += 1
        
        # Resumo
        print("\n" + "=" * 60)
        print(f"📊 RESUMO: {tests_passed}/{total_tests} testes passaram")
        print("=" * 60)
        
        return tests_passed == total_tests


if __name__ == "__main__":
    tester = LoginTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 