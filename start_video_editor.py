#!/usr/bin/env python3
"""
Inicializador do Sistema de Editor de Vídeo
Configura e inicia tanto o backend quanto o frontend
"""

import os
import sys
import subprocess
import asyncio
import time
import signal
import platform
from pathlib import Path
from typing import Dict, List, Optional

class VideoEditorStarter:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.processes: Dict[str, subprocess.Popen] = {}
        self.is_windows = platform.system() == "Windows"
        
    def check_dependencies(self) -> bool:
        """Verifica se todas as dependências estão instaladas"""
        print("🔍 Verificando dependências...")
        
        # Verificar Python
        try:
            import sys
            if sys.version_info < (3, 8):
                print("❌ Python 3.8+ é necessário")
                return False
            print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        except Exception as e:
            print(f"❌ Erro ao verificar Python: {e}")
            return False
        
        # Verificar Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Node.js {version}")
            else:
                print("❌ Node.js não encontrado")
                return False
        except FileNotFoundError:
            print("❌ Node.js não está instalado")
            return False
        
        # Verificar FFmpeg
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ FFmpeg instalado")
            else:
                print("❌ FFmpeg não encontrado")
                print("📝 Instale FFmpeg: https://ffmpeg.org/download.html")
                return False
        except FileNotFoundError:
            print("❌ FFmpeg não está instalado")
            print("📝 Instale FFmpeg: https://ffmpeg.org/download.html")
            return False
        
        return True
    
    def install_backend_deps(self) -> bool:
        """Instala dependências do backend"""
        print("📦 Instalando dependências do backend...")
        
        try:
            # Verificar se venv existe
            venv_dir = self.backend_dir / "venv"
            if not venv_dir.exists():
                print("🏗️ Criando ambiente virtual...")
                subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            
            # Ativar venv e instalar dependências
            if self.is_windows:
                pip_path = venv_dir / "Scripts" / "pip.exe"
                python_path = venv_dir / "Scripts" / "python.exe"
            else:
                pip_path = venv_dir / "bin" / "pip"
                python_path = venv_dir / "bin" / "python"
            
            # Instalar requirements básicos
            requirements_files = [
                "requirements.txt",
                "requirements_video.txt"
            ]
            
            for req_file in requirements_files:
                req_path = self.backend_dir / req_file
                if req_path.exists():
                    print(f"📦 Instalando {req_file}...")
                    subprocess.run([str(pip_path), "install", "-r", str(req_path)], check=True)
            
            print("✅ Dependências do backend instaladas")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências do backend: {e}")
            return False
    
    def install_frontend_deps(self) -> bool:
        """Instala dependências do frontend"""
        print("📦 Instalando dependências do frontend...")
        
        try:
            os.chdir(self.frontend_dir)
            
            # Verificar se node_modules existe
            if not (self.frontend_dir / "node_modules").exists():
                print("📦 Executando npm install...")
                subprocess.run(["npm", "install"], check=True)
            
            print("✅ Dependências do frontend instaladas")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências do frontend: {e}")
            return False
        finally:
            os.chdir(self.root_dir)
    
    def setup_database(self) -> bool:
        """Configura o banco de dados"""
        print("🗄️ Configurando banco de dados...")
        
        try:
            # Executar migrações do Alembic
            if self.is_windows:
                python_path = self.backend_dir / "venv" / "Scripts" / "python.exe"
            else:
                python_path = self.backend_dir / "venv" / "bin" / "python"
            
            os.chdir(self.backend_dir)
            
            # Executar migrações
            subprocess.run([str(python_path), "-m", "alembic", "upgrade", "head"], check=True)
            
            print("✅ Banco de dados configurado")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao configurar banco de dados: {e}")
            return False
        finally:
            os.chdir(self.root_dir)
    
    def create_directories(self):
        """Cria diretórios necessários"""
        print("📁 Criando diretórios...")
        
        directories = [
            self.root_dir / "uploads",
            self.root_dir / "exports", 
            self.root_dir / "temp",
            self.root_dir / "logs",
            self.root_dir / "media",
            self.backend_dir / "app" / "static",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print("✅ Diretórios criados")
    
    def start_backend(self) -> bool:
        """Inicia o servidor backend"""
        print("🚀 Iniciando servidor backend...")
        
        try:
            if self.is_windows:
                python_path = self.backend_dir / "venv" / "Scripts" / "python.exe"
            else:
                python_path = self.backend_dir / "venv" / "bin" / "python"
            
            os.chdir(self.backend_dir)
            
            # Comando para iniciar FastAPI com uvicorn
            cmd = [
                str(python_path), 
                "-m", "uvicorn", 
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ]
            
            self.processes["backend"] = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar alguns segundos para o servidor iniciar
            time.sleep(3)
            
            if self.processes["backend"].poll() is None:
                print("✅ Servidor backend iniciado na porta 8000")
                return True
            else:
                print("❌ Falha ao iniciar servidor backend")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            return False
        finally:
            os.chdir(self.root_dir)
    
    def start_frontend(self) -> bool:
        """Inicia o servidor frontend"""
        print("🎨 Iniciando servidor frontend...")
        
        try:
            os.chdir(self.frontend_dir)
            
            # Comando para iniciar Next.js
            cmd = ["npm", "run", "dev"]
            
            self.processes["frontend"] = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar alguns segundos para o servidor iniciar
            time.sleep(5)
            
            if self.processes["frontend"].poll() is None:
                print("✅ Servidor frontend iniciado na porta 3000")
                return True
            else:
                print("❌ Falha ao iniciar servidor frontend")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar frontend: {e}")
            return False
        finally:
            os.chdir(self.root_dir)
    
    def start_redis(self) -> bool:
        """Inicia o Redis se necessário"""
        print("🔄 Verificando Redis...")
        
        try:
            # Tentar conectar ao Redis
            result = subprocess.run(
                ["redis-cli", "ping"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "PONG" in result.stdout:
                print("✅ Redis já está rodando")
                return True
            else:
                print("🚀 Iniciando Redis...")
                
                # Tentar iniciar Redis
                if self.is_windows:
                    # No Windows, pode ser necessário especificar o caminho
                    redis_cmd = ["redis-server"]
                else:
                    redis_cmd = ["redis-server", "--daemonize", "yes"]
                
                self.processes["redis"] = subprocess.Popen(
                    redis_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                time.sleep(2)
                print("✅ Redis iniciado")
                return True
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️ Redis não encontrado - cache em memória será usado")
            return True
        except Exception as e:
            print(f"⚠️ Erro com Redis: {e} - cache em memória será usado")
            return True
    
    def show_status(self):
        """Mostra o status dos serviços"""
        print("\n" + "="*50)
        print("🎬 EDITOR DE VÍDEO TECNOCURSOS AI")
        print("="*50)
        print(f"🌐 Frontend: http://localhost:3000")
        print(f"🔧 Backend API: http://localhost:8000")
        print(f"📚 Documentação API: http://localhost:8000/docs")
        print("="*50)
        print("📋 Para parar os serviços: Ctrl+C")
        print("="*50)
    
    def stop_services(self):
        """Para todos os serviços"""
        print("\n🛑 Parando serviços...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"🛑 Parando {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"⚠️ Erro ao parar {name}: {e}")
        
        print("✅ Todos os serviços foram parados")
    
    def handle_signal(self, signum, frame):
        """Handler para sinais do sistema"""
        self.stop_services()
        sys.exit(0)
    
    async def main(self):
        """Função principal"""
        print("🎬 INICIALIZANDO EDITOR DE VÍDEO TECNOCURSOS AI")
        print("="*50)
        
        # Registrar handler para Ctrl+C
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
        # 1. Verificar dependências
        if not self.check_dependencies():
            print("❌ Dependências não atendidas")
            return False
        
        # 2. Criar diretórios
        self.create_directories()
        
        # 3. Instalar dependências
        if not self.install_backend_deps():
            return False
        
        if not self.install_frontend_deps():
            return False
        
        # 4. Configurar banco de dados
        if not self.setup_database():
            return False
        
        # 5. Iniciar Redis
        self.start_redis()
        
        # 6. Iniciar backend
        if not self.start_backend():
            return False
        
        # 7. Iniciar frontend
        if not self.start_frontend():
            return False
        
        # 8. Mostrar status
        self.show_status()
        
        # 9. Aguardar indefinidamente
        try:
            while True:
                # Verificar se os processos ainda estão rodando
                for name, process in self.processes.items():
                    if process and process.poll() is not None:
                        print(f"⚠️ Processo {name} parou inesperadamente")
                        return False
                
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.stop_services()
        
        return True

def main():
    """Ponto de entrada"""
    starter = VideoEditorStarter()
    
    try:
        # Executar a função principal
        result = asyncio.run(starter.main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        starter.stop_services()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        starter.stop_services()
        sys.exit(1)

if __name__ == "__main__":
    main()
