#!/usr/bin/env python3
"""
Teste completo do sistema de upload com narração
Testa todas as funcionalidades implementadas
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Configurações de teste
BASE_URL = "http://localhost:8001"
TEST_PDF = "sample_test.pdf"

# Usuário único baseado no timestamp
timestamp = int(time.time())
TEST_USER = {
    "username": f"test_user_{timestamp}", 
    "email": f"test_{timestamp}@example.com", 
    "password": "test123456@Test"
}

class UploadNarrationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
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
    
    def test_pdf_exists(self):
        """Verifica se o arquivo PDF de teste existe"""
        try:
            exists = os.path.exists(TEST_PDF)
            size = os.path.getsize(TEST_PDF) if exists else 0
            
            self.log_test(
                "PDF Test File Exists", 
                exists,
                f"File size: {size} bytes" if exists else "File not found",
                {"file": TEST_PDF, "size": size}
            )
            return exists
        except Exception as e:
            self.log_test("PDF Test File Exists", False, str(e))
            return False
    
    def test_server_running(self):
        """Verifica se o servidor está rodando"""
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200
            
            self.log_test(
                "Server Running", 
                success,
                f"Status: {response.status_code}",
                {"status_code": response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("Server Running", False, str(e))
            return False
    
    def test_user_registration(self):
        """Testa o registro de usuário"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=TEST_USER
            )
            
            success = response.status_code in [200, 201, 409]  # 409 = usuário já existe
            message = "User registered" if response.status_code in [200, 201] else "User already exists"
            
            self.log_test(
                "User Registration",
                success,
                f"{message} (Status: {response.status_code})",
                {"status_code": response.status_code}
            )
            return success
        except Exception as e:
            self.log_test("User Registration", False, str(e))
            return False
    
    def test_user_login(self):
        """Testa o login do usuário"""
        try:
            # Tentar login com formato form data
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            # Se não funcionar, tentar com JSON
            if response.status_code != 200:
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json={
                        "username": TEST_USER["username"],
                        "password": TEST_USER["password"]
                    }
                )
            
            # Se ainda não funcionar, tentar endpoint diferente
            if response.status_code != 200:
                response = self.session.post(
                    f"{self.base_url}/auth/token",
                    data={
                        "username": TEST_USER["username"],
                        "password": TEST_USER["password"],
                        "grant_type": "password"
                    }
                )
            
            success = response.status_code == 200
            if success:
                try:
                    data = response.json()
                    self.auth_token = data.get("access_token") or data.get("token")
                    if self.auth_token:
                        self.session.headers.update({
                            "Authorization": f"Bearer {self.auth_token}"
                        })
                except:
                    pass
                
            self.log_test(
                "User Login",
                success,
                f"Status: {response.status_code}",
                {"status_code": response.status_code, "token_received": bool(self.auth_token)}
            )
            return success
        except Exception as e:
            self.log_test("User Login", False, str(e))
            return False
    
    def test_upload_with_narration(self):
        """Testa o upload de arquivo com geração de narração"""
        try:
            if not self.auth_token:
                self.log_test("Upload with Narration", False, "No auth token available")
                return False
            
            with open(TEST_PDF, 'rb') as file:
                files = {
                    'file': (TEST_PDF, file, 'application/pdf')
                }
                data = {
                    'title': 'Test PDF Upload with Narration',
                    'description': 'Testing automatic narration generation',
                    'generate_narration': 'true'
                }
                
                print("🔄 Uploading file and generating narration...")
                response = self.session.post(
                    f"{self.base_url}/files/upload",
                    files=files,
                    data=data
                )
            
            success = response.status_code == 200
            
            if success:
                result_data = response.json()
                
                # Verificar se a resposta contém os campos esperados
                expected_fields = [
                    'file_info', 'text_extraction', 'audio_generation'
                ]
                
                all_fields_present = all(field in result_data for field in expected_fields)
                
                if all_fields_present:
                    audio_info = result_data.get('audio_generation', {})
                    audio_filename = audio_info.get('filename')
                    
                    message = f"Upload successful. Audio: {audio_filename}"
                else:
                    message = "Upload successful but missing expected fields"
                    success = False
                
                self.log_test(
                    "Upload with Narration",
                    success,
                    message,
                    {
                        "status_code": response.status_code,
                        "response_keys": list(result_data.keys()),
                        "audio_filename": result_data.get('audio_generation', {}).get('filename')
                    }
                )
                
                return success, result_data if success else None
            else:
                self.log_test(
                    "Upload with Narration",
                    False,
                    f"Upload failed with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text[:500]}
                )
                return False, None
                
        except Exception as e:
            self.log_test("Upload with Narration", False, str(e))
            return False, None
    
    def test_audio_list(self):
        """Testa a listagem de áudios"""
        try:
            response = self.session.get(f"{self.base_url}/audios/")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                audio_count = len(data.get('audios', []))
                message = f"Found {audio_count} audio(s)"
            else:
                message = f"Failed with status {response.status_code}"
                
            self.log_test(
                "Audio List",
                success,
                message,
                {"status_code": response.status_code, "audio_count": audio_count if success else 0}
            )
            return success
        except Exception as e:
            self.log_test("Audio List", False, str(e))
            return False
    
    def test_audio_search(self):
        """Testa a busca de áudios"""
        try:
            response = self.session.get(f"{self.base_url}/audios/search?q=test")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                results_count = len(data.get('results', []))
                message = f"Search returned {results_count} result(s)"
            else:
                message = f"Failed with status {response.status_code}"
                
            self.log_test(
                "Audio Search",
                success,
                message,
                {"status_code": response.status_code, "results_count": results_count if success else 0}
            )
            return success
        except Exception as e:
            self.log_test("Audio Search", False, str(e))
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 Iniciando testes do sistema de upload com narração\n")
        
        # Testes de pré-requisitos
        if not self.test_pdf_exists():
            print("❌ Arquivo PDF de teste não encontrado. Abortando testes.")
            return False
        
        if not self.test_server_running():
            print("❌ Servidor não está rodando. Inicie o servidor com: uvicorn app.main:app --reload")
            return False
        
        # Testes de autenticação
        self.test_user_registration()
        if not self.test_user_login():
            print("❌ Falha no login. Não é possível continuar com testes autenticados.")
            return False
        
        # Testes principais
        upload_success, upload_data = self.test_upload_with_narration()
        self.test_audio_list()
        self.test_audio_search()
        
        # Resumo dos resultados
        self.print_summary()
        
        return upload_success
    
    def print_summary(self):
        """Imprime um resumo dos resultados"""
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60)
        
        passed = sum(1 for test in self.test_results if test["success"])
        total = len(self.test_results)
        
        print(f"Total de testes: {total}")
        print(f"Passou: {passed}")
        print(f"Falhou: {total - passed}")
        print(f"Taxa de sucesso: {(passed/total)*100:.1f}%\n")
        
        # Detalhes dos testes que falharam
        failed_tests = [test for test in self.test_results if not test["success"]]
        if failed_tests:
            print("❌ TESTES QUE FALHARAM:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
        else:
            print("✅ TODOS OS TESTES PASSARAM!")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    tester = UploadNarrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1) 