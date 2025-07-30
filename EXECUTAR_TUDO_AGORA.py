#!/usr/bin/env python3
"""
TecnoCursos AI - Executor Final
Sistema completo de inicialização
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

class TecnoCursosLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.root_dir = Path(__file__).parent
        
    def print_header(self):
        print("=" * 60)
        print("🎯 TECNOCURSOS AI - SISTEMA DE INICIALIZACAO")
        print("=" * 60)
        print()
        
    def check_structure(self):
        """Verifica estrutura de arquivos"""
        print("🔍 Verificando estrutura do projeto...")
        
        required_files = [
            "backend/main.py",
            "frontend/package.json"
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} não encontrado")
                return False
        
        print()
        return True
        
    def install_backend_deps(self):
        """Instala dependências do backend"""
        print("📦 Instalando dependências do backend...")
        
        deps = [
            "fastapi",
            "uvicorn[standard]", 
            "python-multipart",
            "jinja2",
            "aiofiles",
            "requests",
            "psutil"
        ]
        
        try:
            for dep in deps:
                print(f"   Instalando {dep}...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
            
            print("✅ Dependências do backend instaladas!")
            print()
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            return False
            
    def install_frontend_deps(self):
        """Instala dependências do frontend"""
        print("📦 Instalando dependências do frontend...")
        
        frontend_dir = self.root_dir / "frontend"
        
        try:
            os.chdir(frontend_dir)
            subprocess.run(["npm", "install"], check=True, capture_output=True)
            os.chdir(self.root_dir)
            
            print("✅ Dependências do frontend instaladas!")
            print()
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências do frontend: {e}")
            os.chdir(self.root_dir)
            return False
            
    def start_backend(self):
        """Inicia o backend"""
        print("🚀 Iniciando Backend (FastAPI)...")
        
        backend_dir = self.root_dir / "backend"
        
        try:
            os.chdir(backend_dir)
            
            # Comando para iniciar o backend
            cmd = [
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8001",
                "--reload"
            ]
            
            # Iniciar em nova janela no Windows
            if os.name == 'nt':
                cmd_str = " ".join(cmd)
                subprocess.Popen(f'start "Backend - TecnoCursos AI" cmd /c "{cmd_str} && pause"', shell=True)
            else:
                # Linux/Mac
                self.backend_process = subprocess.Popen(cmd)
            
            os.chdir(self.root_dir)
            print("✅ Backend iniciado em http://localhost:8001")
            print()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            os.chdir(self.root_dir)
            return False
            
    def start_frontend(self):
        """Inicia o frontend"""
        print("🎨 Iniciando Frontend (React)...")
        
        frontend_dir = self.root_dir / "frontend"
        
        try:
            os.chdir(frontend_dir)
            
            # Comando para iniciar o frontend
            cmd = ["npm", "run", "start"]
            
            # Iniciar em nova janela no Windows
            if os.name == 'nt':
                cmd_str = " ".join(cmd)
                subprocess.Popen(f'start "Frontend - TecnoCursos AI" cmd /c "{cmd_str} && pause"', shell=True)
            else:
                # Linux/Mac
                self.frontend_process = subprocess.Popen(cmd)
            
            os.chdir(self.root_dir)
            print("✅ Frontend iniciado em http://localhost:3000")
            print()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar frontend: {e}")
            os.chdir(self.root_dir)
            return False
            
    def show_success_message(self):
        """Mostra mensagem de sucesso"""
        print("=" * 60)
        print("🎉 SISTEMA TECNOCURSOS AI INICIADO COM SUCESSO!")
        print("=" * 60)
        print()
        print("🌐 Acessos disponíveis:")
        print("   Frontend:  http://localhost:3000")
        print("   Backend:   http://localhost:8001")
        print("   API Docs:  http://localhost:8001/docs")
        print("   Health:    http://localhost:8001/health")
        print()
        print("💡 Dicas:")
        print("   - O sistema está rodando em janelas separadas")
        print("   - Para parar, feche as janelas do Backend e Frontend")
        print("   - Aguarde alguns segundos para os serviços iniciarem")
        print()
        print("=" * 60)
        
    def open_browser(self):
        """Abre o navegador nos endereços"""
        print("🌐 Abrindo navegador...")
        
        time.sleep(3)  # Aguardar serviços iniciarem
        
        try:
            webbrowser.open("http://localhost:3000")
            time.sleep(1)
            webbrowser.open("http://localhost:8001/docs")
            print("✅ Navegador aberto!")
        except:
            print("ℹ️  Abra manualmente: http://localhost:3000")
            
    def run(self):
        """Executa o launcher completo"""
        self.print_header()
        
        # Verificações
        if not self.check_structure():
            print("❌ Estrutura de arquivos inválida")
            input("Pressione Enter para sair...")
            return
            
        # Instalação de dependências
        if not self.install_backend_deps():
            print("❌ Falha na instalação do backend")
            input("Pressione Enter para sair...")
            return
            
        if not self.install_frontend_deps():
            print("❌ Falha na instalação do frontend")
            input("Pressione Enter para sair...")
            return
            
        # Inicialização dos serviços
        if not self.start_backend():
            print("❌ Falha ao iniciar backend")
            input("Pressione Enter para sair...")
            return
            
        time.sleep(3)  # Aguardar backend
        
        if not self.start_frontend():
            print("❌ Falha ao iniciar frontend")
            input("Pressione Enter para sair...")
            return
            
        # Sucesso
        self.show_success_message()
        self.open_browser()
        
        print("\nPressione Enter para finalizar este script...")
        input("(Os serviços continuarão rodando em outras janelas)")

def main():
    """Função principal"""
    launcher = TecnoCursosLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
