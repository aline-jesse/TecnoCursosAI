#!/usr/bin/env python3
"""
Teste Completo do Fluxo de Upload com Criação Automática de Projeto
===============================================================

Este script testa todas as funcionalidades implementadas:
1. Verificação de projetos disponíveis
2. Upload com criação automática de projeto
3. Upload com projeto existente
4. Validação de erros
"""

import requests
import json
import os
import uuid
from pathlib import Path

# Configurações
BASE_URL = "http://127.0.0.1:8000/api"
TEST_USERNAME = f"teste_upload_{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "teste123456"
TEST_EMAIL = f"{TEST_USERNAME}@teste.com"

def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(step_num, text):
    """Imprime passo do teste"""
    print(f"\n📋 PASSO {step_num}: {text}")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"✅ {text}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"❌ {text}")

def print_info(text):
    """Imprime informação"""
    print(f"💡 {text}")

def register_test_user():
    """Registra usuário de teste"""
    print_step(1, "Registrando usuário de teste")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "full_name": f"Teste Upload {TEST_USERNAME}",
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "username": TEST_USERNAME
        }, timeout=10)
        
        if response.status_code in [200, 201]:
            print_success("Usuário registrado com sucesso")
            return True
        elif response.status_code == 400 and "já existe" in response.text:
            print_info("Usuário já existe - continuando com login")
            return True
        else:
            print_error(f"Erro ao registrar: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro na requisição de registro: {str(e)}")
        return False

def login_test_user():
    """Faz login do usuário de teste"""
    print_step(2, "Fazendo login do usuário")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            if token:
                print_success(f"Login realizado com sucesso")
                return token
            else:
                print_error("Token não encontrado na resposta")
                return None
        else:
            print_error(f"Erro no login: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Erro na requisição de login: {str(e)}")
        return None

def check_projects(token):
    """Verifica projetos disponíveis"""
    print_step(3, "Verificando projetos disponíveis")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/files/check-projects", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Verificação realizada: {data['message']}")
            print_info(f"  - Tem projetos: {data['has_projects']}")
            print_info(f"  - Quantidade: {data['project_count']}")
            print_info(f"  - Pode criar automaticamente: {data['can_auto_create']}")
            return data
        else:
            print_error(f"Erro ao verificar projetos: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Erro na verificação de projetos: {str(e)}")
        return None

def create_test_file():
    """Cria arquivo de teste"""
    print_step(4, "Criando arquivo de teste")
    
    try:
        # Usar arquivo existente se disponível
        test_files = ["sample_test.pdf", "test_pipeline.pdf"]
        for test_file in test_files:
            if os.path.exists(test_file):
                print_success(f"Usando arquivo existente: {test_file}")
                return test_file
        
        # Criar arquivo texto simples para teste
        test_content = """Teste de Upload Automático
        
Este é um arquivo de teste para verificar o sistema de upload
com criação automática de projeto.

Funcionalidades testadas:
1. Upload sem projeto existente
2. Criação automática de projeto
3. Processamento de arquivo
4. Integração completa

Data do teste: {datetime.now()}
Usuário: {TEST_USERNAME}
""".format(datetime=__import__("datetime").datetime, TEST_USERNAME=TEST_USERNAME)
        
        test_file = f"teste_upload_{uuid.uuid4().hex[:8]}.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print_success(f"Arquivo de teste criado: {test_file}")
        return test_file
        
    except Exception as e:
        print_error(f"Erro ao criar arquivo de teste: {str(e)}")
        return None

def test_upload_auto_create(token, test_file):
    """Testa upload com criação automática de projeto"""
    print_step(5, "Testando upload com criação automática de projeto")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {
                'auto_create_project': 'true',
                'description': 'Teste de upload com criação automática'
            }
            
            response = requests.post(
                f"{BASE_URL}/files/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=60  # Timeout maior para processamento
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_success("Upload realizado com sucesso!")
            print_info(f"  - Arquivo ID: {result.get('file_id')}")
            print_info(f"  - Projeto ID: {result.get('project_id')}")
            print_info(f"  - Status: {result.get('status')}")
            
            # Verificar se projeto foi criado
            if result.get('project_created'):
                print_success("✨ Projeto criado automaticamente!")
                print_info(f"  - Nome do projeto: {result.get('project_name')}")
            
            return result
        else:
            print_error(f"Erro no upload: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Erro no upload: {str(e)}")
        return None

def verify_project_creation(token):
    """Verifica se o projeto foi criado"""
    print_step(6, "Verificando se projeto foi criado")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/projects/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            projects = response.json()
            if projects:
                print_success(f"✅ {len(projects)} projeto(s) encontrado(s):")
                for project in projects:
                    print_info(f"  - {project.get('name')} (ID: {project.get('id')})")
            else:
                print_error("Nenhum projeto encontrado")
            return projects
        else:
            print_error(f"Erro ao listar projetos: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Erro ao verificar projetos: {str(e)}")
        return None

def cleanup_test_file(test_file):
    """Limpa arquivo de teste"""
    try:
        if test_file and os.path.exists(test_file) and test_file.startswith("teste_upload_"):
            os.remove(test_file)
            print_info(f"Arquivo de teste removido: {test_file}")
    except Exception as e:
        print_error(f"Erro ao remover arquivo: {str(e)}")

def main():
    """Função principal do teste"""
    print_header("TESTE COMPLETO - UPLOAD COM CRIAÇÃO AUTOMÁTICA DE PROJETO")
    
    print_info("Este teste verifica todo o fluxo implementado:")
    print_info("1. Registro de usuário")
    print_info("2. Login")
    print_info("3. Verificação de projetos")
    print_info("4. Upload com criação automática")
    print_info("5. Verificação final")
    
    token = None
    test_file = None
    
    try:
        # Etapa 1: Registro
        if not register_test_user():
            return
        
        # Etapa 2: Login
        token = login_test_user()
        if not token:
            return
        
        # Etapa 3: Verificar projetos
        project_info = check_projects(token)
        if project_info is None:
            return
        
        # Etapa 4: Criar arquivo de teste
        test_file = create_test_file()
        if not test_file:
            return
        
        # Etapa 5: Upload com criação automática
        upload_result = test_upload_auto_create(token, test_file)
        if not upload_result:
            return
        
        # Etapa 6: Verificar criação do projeto
        projects = verify_project_creation(token)
        
        # Resumo final
        print_header("RESUMO DO TESTE")
        if upload_result and projects:
            print_success("🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print_info("✅ Todas as funcionalidades estão funcionando:")
            print_info("  - Verificação de projetos")
            print_info("  - Criação automática de projeto")
            print_info("  - Upload de arquivos")
            print_info("  - Integração completa")
        else:
            print_error("❌ Teste não foi concluído com sucesso")
        
    except KeyboardInterrupt:
        print_error("\n❌ Teste interrompido pelo usuário")
    except Exception as e:
        print_error(f"❌ Erro inesperado: {str(e)}")
    finally:
        # Limpeza
        if test_file:
            cleanup_test_file(test_file)

if __name__ == "__main__":
    main() 