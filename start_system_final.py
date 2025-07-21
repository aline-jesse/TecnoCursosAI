#!/usr/bin/env python3
"""
Script de Inicialização Completa - TecnoCursos AI
Enterprise Edition 2025
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path
from datetime import datetime

class SystemStarter:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def print_status(self, message, status="INFO"):
        """Imprime status com cores"""
        colors = {
            "SUCCESS": "🟢",
            "ERROR": "🔴", 
            "WARNING": "🟡",
            "INFO": "🔵"
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{colors.get(status, '🔵')} [{timestamp}] {message}")
    
    def create_directories(self):
        """Cria diretórios necessários"""
        self.print_status("📁 Criando diretórios...", "INFO")
        
        directories = [
            "uploads",
            "uploads/pdf", 
            "uploads/pptx",
            "static/videos",
            "static/audios",
            "static/thumbnails",
            "cache",
            "logs",
            "temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        self.print_status("✅ Diretórios criados", "SUCCESS")
    
    def install_dependencies(self):
        """Instala dependências Python"""
        self.print_status("📦 Verificando dependências Python...", "INFO")
        
        try:
            # Verificar se requirements.txt existe
            if not Path("requirements.txt").exists():
                self.print_status("⚠️ requirements.txt não encontrado", "WARNING")
                return True
            
            # Instalar dependências
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_status("✅ Dependências Python instaladas", "SUCCESS")
                return True
            else:
                self.print_status(f"⚠️ Erro ao instalar dependências: {result.stderr}", "WARNING")
                return True  # Continuar mesmo com erro
                
        except Exception as e:
            self.print_status(f"⚠️ Erro ao instalar dependências: {e}", "WARNING")
            return True
    
    def start_backend(self):
        """Inicia o servidor backend"""
        self.print_status("🚀 Iniciando servidor backend...", "INFO")
        
        try:
            # Comando para iniciar o servidor
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", "127.0.0.1", 
                "--port", "8000",
                "--reload"
            ]
            
            # Iniciar processo
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(("Backend", process))
            self.print_status("✅ Servidor backend iniciado", "SUCCESS")
            
            # Aguardar um pouco para o servidor inicializar
            time.sleep(3)
            
            return True
            
        except Exception as e:
            self.print_status(f"❌ Erro ao iniciar backend: {e}", "ERROR")
            return False
    
    def start_frontend(self):
        """Inicia o servidor frontend React"""
        self.print_status("🎨 Iniciando servidor frontend...", "INFO")
        
        try:
            # Verificar se node_modules existe
            if not Path("node_modules").exists():
                self.print_status("⚠️ node_modules não encontrado, tentando instalar...", "WARNING")
                
                # Tentar instalar dependências
                install_cmd = ["npm", "install", "--legacy-peer-deps"]
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.print_status("⚠️ Erro ao instalar dependências do frontend", "WARNING")
                    return False
            
            # Iniciar servidor React
            cmd = ["npm", "start"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(("Frontend", process))
            self.print_status("✅ Servidor frontend iniciado", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.print_status(f"⚠️ Erro ao iniciar frontend: {e}", "WARNING")
            return False
    
    def test_system(self):
        """Testa se o sistema está funcionando"""
        self.print_status("🧪 Testando sistema...", "INFO")
        
        try:
            import requests
            
            # Testar backend
            response = requests.get("http://127.0.0.1:8000/api/health", timeout=10)
            if response.status_code == 200:
                self.print_status("✅ Backend funcionando", "SUCCESS")
            else:
                self.print_status(f"❌ Backend retornou status {response.status_code}", "ERROR")
                return False
            
            # Testar documentação
            response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
            if response.status_code == 200:
                self.print_status("✅ Documentação disponível", "SUCCESS")
            else:
                self.print_status("⚠️ Documentação não disponível", "WARNING")
            
            return True
            
        except Exception as e:
            self.print_status(f"❌ Erro ao testar sistema: {e}", "ERROR")
            return False
    
    def show_status(self):
        """Mostra status dos serviços"""
        print("\n" + "="*60)
        print("📊 STATUS DOS SERVIÇOS")
        print("="*60)
        
        for name, process in self.processes:
            if process.poll() is None:
                print(f"✅ {name}: Rodando (PID: {process.pid})")
            else:
                print(f"❌ {name}: Parado")
        
        print("\n🌐 URLs:")
        print("   Backend: http://127.0.0.1:8000")
        print("   Documentação: http://127.0.0.1:8000/docs")
        print("   Frontend: http://localhost:3000")
        
        print("\n💡 Comandos úteis:")
        print("   Testar sistema: python test_system_complete.py")
        print("   Parar sistema: Ctrl+C")
    
    def cleanup(self):
        """Limpa processos ao encerrar"""
        self.print_status("🔄 Encerrando sistema...", "INFO")
        
        for name, process in self.processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                    self.print_status(f"✅ {name} encerrado", "SUCCESS")
                else:
                    self.print_status(f"⚠️ {name} já estava parado", "WARNING")
            except Exception as e:
                self.print_status(f"❌ Erro ao encerrar {name}: {e}", "ERROR")
    
    def signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        self.print_status("🛑 Recebido sinal de interrupção", "WARNING")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Executa o sistema completo"""
        # Configurar handler de sinais
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 TecnoCursos AI - Enterprise Edition 2025")
        print("="*60)
        
        # Criar diretórios
        self.create_directories()
        
        # Instalar dependências
        self.install_dependencies()
        
        # Iniciar backend
        if not self.start_backend():
            self.print_status("❌ Falha ao iniciar backend", "ERROR")
            return False
        
        # Aguardar backend inicializar
        time.sleep(5)
        
        # Testar sistema
        if not self.test_system():
            self.print_status("❌ Sistema não está funcionando corretamente", "ERROR")
            return False
        
        # Tentar iniciar frontend (opcional)
        self.start_frontend()
        
        # Mostrar status
        self.show_status()
        
        # Loop principal
        try:
            while self.running:
                time.sleep(1)
                
                # Verificar se processos ainda estão rodando
                for name, process in self.processes:
                    if process.poll() is not None:
                        self.print_status(f"⚠️ {name} parou inesperadamente", "WARNING")
                        self.running = False
                        break
                        
        except KeyboardInterrupt:
            self.print_status("🛑 Interrupção solicitada pelo usuário", "WARNING")
        finally:
            self.cleanup()

def main():
    """Função principal"""
    starter = SystemStarter()
    
    try:
        starter.run()
        return 0
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 