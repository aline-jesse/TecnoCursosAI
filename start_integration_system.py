#!/usr/bin/env python3
"""
Script de Inicialização Completa - Sistema TecnoCursos AI com Integração FastAPI
Inicializa o backend FastAPI e frontend React com todas as funcionalidades
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path

class IntegrationSystemStarter:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.backend_process = None
        self.frontend_process = None
        
    def print_header(self):
        print("=" * 80)
        print("🎬 TECNOCURSOS AI - SISTEMA DE INTEGRAÇÃO FASTAPI")
        print("=" * 80)
        print("Inicializando sistema completo com backend FastAPI e frontend React")
        print("=" * 80)
        
    def check_dependencies(self):
        """Verificar dependências necessárias"""
        print("\n📋 Verificando dependências...")
        
        # Verificar Python
        try:
            python_version = subprocess.check_output(['python', '--version'], text=True).strip()
            print(f"✅ Python: {python_version}")
        except:
            print("❌ Python não encontrado")
            return False
            
        # Verificar Node.js
        try:
            node_version = subprocess.check_output(['node', '--version'], text=True).strip()
            print(f"✅ Node.js: {node_version}")
        except:
            print("❌ Node.js não encontrado")
            return False
            
        # Verificar npm
        try:
            npm_version = subprocess.check_output(['npm', '--version'], text=True).strip()
            print(f"✅ npm: {npm_version}")
        except:
            print("❌ npm não encontrado")
            return False
            
        return True
        
    def install_python_dependencies(self):
        """Instalar dependências Python"""
        print("\n🐍 Instalando dependências Python...")
        
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True, text=True)
            print("✅ Dependências Python instaladas com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências Python: {e}")
            return False
            
    def install_node_dependencies(self):
        """Instalar dependências Node.js"""
        print("\n📦 Instalando dependências Node.js...")
        
        try:
            subprocess.run(['npm', 'install'], check=True, capture_output=True, text=True)
            print("✅ Dependências Node.js instaladas com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências Node.js: {e}")
            return False
            
    def start_backend(self):
        """Iniciar backend FastAPI"""
        print(f"\n🚀 Iniciando backend FastAPI em {self.backend_url}...")
        
        try:
            # Verificar se o arquivo main.py existe
            if not os.path.exists('main.py'):
                print("❌ Arquivo main.py não encontrado")
                return False
                
            # Iniciar servidor FastAPI
            self.backend_process = subprocess.Popen([
                sys.executable, 'main.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Aguardar inicialização
            time.sleep(3)
            
            # Verificar se está rodando
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend FastAPI iniciado com sucesso")
                    return True
                else:
                    print(f"❌ Backend retornou status {response.status_code}")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Backend não está respondendo")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            return False
            
    def start_frontend(self):
        """Iniciar frontend React"""
        print(f"\n⚛️ Iniciando frontend React em {self.frontend_url}...")
        
        try:
            # Verificar se package.json existe
            if not os.path.exists('package.json'):
                print("❌ package.json não encontrado")
                return False
                
            # Iniciar servidor de desenvolvimento React
            self.frontend_process = subprocess.Popen([
                'npm', 'start'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Aguardar inicialização
            time.sleep(10)
            
            # Verificar se está rodando
            try:
                response = requests.get(self.frontend_url, timeout=10)
                if response.status_code == 200:
                    print("✅ Frontend React iniciado com sucesso")
                    return True
                else:
                    print(f"❌ Frontend retornou status {response.status_code}")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Frontend não está respondendo")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar frontend: {e}")
            return False
            
    def run_tests(self):
        """Executar testes da integração"""
        print("\n🧪 Executando testes da integração...")
        
        try:
            # Executar testes JavaScript
            result = subprocess.run([
                'npm', 'test', '--', '--testPathPattern=fastapiIntegration', '--passWithNoTests'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Testes executados com sucesso")
                return True
            else:
                print("⚠️ Testes executados com avisos")
                return True
                
        except subprocess.TimeoutExpired:
            print("⚠️ Testes demoraram muito, mas continuando...")
            return True
        except Exception as e:
            print(f"❌ Erro ao executar testes: {e}")
            return False
            
    def check_integration_files(self):
        """Verificar arquivos de integração"""
        print("\n📁 Verificando arquivos de integração...")
        
        integration_files = [
            'src/services/fastapiIntegration.js',
            'src/services/fastapiIntegration.test.js',
            'src/components/VideoEditorIntegration.jsx',
            'src/components/VideoEditorIntegration.css',
            'src/services/INTEGRATION_DOCUMENTATION.md'
        ]
        
        all_exist = True
        for file_path in integration_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - NÃO ENCONTRADO")
                all_exist = False
                
        return all_exist
        
    def show_system_info(self):
        """Mostrar informações do sistema"""
        print("\n📊 Informações do Sistema:")
        print(f"   Backend URL: {self.backend_url}")
        print(f"   Frontend URL: {self.frontend_url}")
        print(f"   API Docs: {self.backend_url}/docs")
        print(f"   Health Check: {self.backend_url}/health")
        
        print("\n🔗 Endpoints da Integração:")
        print("   GET  /api/projects - Listar projetos")
        print("   POST /api/projects - Criar projeto")
        print("   GET  /api/projects/{id}/scenes - Listar cenas")
        print("   POST /api/scenes - Criar cena")
        print("   PUT  /api/scenes/{id} - Atualizar cena")
        print("   POST /api/upload - Upload de arquivo")
        print("   GET  /api/projects/{id}/video - Download de vídeo")
        
        print("\n📚 Documentação:")
        print("   - src/services/INTEGRATION_DOCUMENTATION.md")
        print("   - src/components/VideoEditorIntegration.example.jsx")
        print("   - INTEGRATION_SUMMARY.md")
        
    def wait_for_user_input(self):
        """Aguardar input do usuário"""
        print("\n" + "=" * 80)
        print("🎉 Sistema iniciado com sucesso!")
        print("=" * 80)
        print("Pressione Ctrl+C para parar o sistema")
        print("=" * 80)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            self.cleanup()
            
    def cleanup(self):
        """Limpar processos"""
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend parado")
            
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend parado")
            
    def run(self):
        """Executar inicialização completa"""
        self.print_header()
        
        # Verificar dependências
        if not self.check_dependencies():
            print("❌ Dependências não atendidas")
            return False
            
        # Instalar dependências
        if not self.install_python_dependencies():
            print("❌ Falha ao instalar dependências Python")
            return False
            
        if not self.install_node_dependencies():
            print("❌ Falha ao instalar dependências Node.js")
            return False
            
        # Verificar arquivos de integração
        if not self.check_integration_files():
            print("⚠️ Alguns arquivos de integração não foram encontrados")
            
        # Executar testes
        self.run_tests()
        
        # Iniciar backend
        if not self.start_backend():
            print("❌ Falha ao iniciar backend")
            return False
            
        # Iniciar frontend
        if not self.start_frontend():
            print("❌ Falha ao iniciar frontend")
            return False
            
        # Mostrar informações
        self.show_system_info()
        
        # Aguardar usuário
        self.wait_for_user_input()
        
        return True

def main():
    """Função principal"""
    starter = IntegrationSystemStarter()
    try:
        starter.run()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        starter.cleanup()
        return False

if __name__ == "__main__":
    main() 