#!/usr/bin/env python3
"""
Configuração de Produção - TecnoCursos AI Enterprise Edition
Resolve problemas de porta e otimiza para produção
"""

import os
import sys
import socket
import subprocess
import time
import psutil
from pathlib import Path

class ProductionConfig:
    def __init__(self):
        self.base_port = 8000
        self.max_port_attempts = 10
        self.config_file = "config.json"
        
    def find_available_port(self, start_port=8000):
        """Encontra uma porta disponível"""
        for port in range(start_port, start_port + self.max_port_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return None
    
    def kill_process_on_port(self, port):
        """Mata processo que está usando a porta"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections']:
                        if conn.laddr.port == port:
                            print(f"Matando processo {proc.info['name']} (PID: {proc.info['pid']}) na porta {port}")
                            proc.terminate()
                            time.sleep(2)
                            if proc.is_running():
                                proc.kill()
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Erro ao matar processo: {e}")
        return False
    
    def check_port_status(self, port):
        """Verifica status da porta"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    def create_production_config(self):
        """Cria configuração de produção"""
        config = {
            "production": {
                "host": "0.0.0.0",
                "port": self.find_available_port(),
                "workers": 4,
                "log_level": "info",
                "reload": False,
                "access_log": True,
                "timeout": 60,
                "max_requests": 1000,
                "max_requests_jitter": 100
            },
            "development": {
                "host": "127.0.0.1",
                "port": self.find_available_port(8001),
                "workers": 1,
                "log_level": "debug",
                "reload": True,
                "access_log": True,
                "timeout": 30,
                "max_requests": 100,
                "max_requests_jitter": 10
            },
            "database": {
                "url": "sqlite:///./tecnocursos.db",
                "pool_size": 20,
                "max_overflow": 30,
                "pool_pre_ping": True
            },
            "security": {
                "secret_key": os.environ.get("SECRET_KEY", "your-secret-key-change-in-production"),
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
                "cors_origins": ["*"],
                "rate_limit": {
                    "requests_per_minute": 60,
                    "burst": 100
                }
            },
            "storage": {
                "upload_dir": "./uploads",
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "allowed_extensions": [".pdf", ".pptx", ".jpg", ".png", ".mp4", ".mp3", ".wav"],
                "temp_dir": "./temp"
            },
            "ai_services": {
                "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
                "d_id_api_key": os.environ.get("D_ID_API_KEY", ""),
                "azure_speech_key": os.environ.get("AZURE_SPEECH_KEY", ""),
                "azure_speech_region": os.environ.get("AZURE_SPEECH_REGION", "")
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 9090,
                "health_check_interval": 30,
                "log_retention_days": 30
            },
            "background_processing": {
                "enabled": True,
                "worker_count": 4,
                "queue_size": 100,
                "task_timeout": 300
            }
        }
        
        # Salvar configuração
        import json
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuração salva em {self.config_file}")
        return config
    
    def setup_directories(self):
        """Configura diretórios necessários"""
        directories = [
            "uploads",
            "uploads/videos",
            "uploads/audios",
            "uploads/images",
            "uploads/documents",
            "static",
            "static/videos",
            "static/audios",
            "static/thumbnails",
            "static/css",
            "static/js",
            "cache",
            "cache/tts",
            "cache/tts_batch",
            "logs",
            "temp",
            "backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Diretório criado: {directory}")
    
    def create_environment_file(self):
        """Cria arquivo .env para variáveis de ambiente"""
        env_content = """# TecnoCursos AI - Variáveis de Ambiente
# Copie este arquivo para .env e configure suas chaves

# Configurações do Servidor
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info
ENVIRONMENT=production

# Segurança
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# APIs de IA
OPENAI_API_KEY=your-openai-api-key
D_ID_API_KEY=your-d-id-api-key
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-azure-region

# Banco de Dados
DATABASE_URL=sqlite:///./tecnocursos.db

# Monitoramento
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# Upload
MAX_FILE_SIZE=104857600
UPLOAD_DIR=./uploads
TEMP_DIR=./temp

# Background Processing
WORKER_COUNT=4
QUEUE_SIZE=100
TASK_TIMEOUT=300
"""
        
        with open("env.example", 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo env.example criado")
    
    def create_startup_script(self):
        """Cria script de inicialização otimizado"""
        script_content = """#!/usr/bin/env python3
\"\"\"
Script de Inicialização Otimizado - TecnoCursos AI
Versão de Produção
\"\"\"

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path

def setup_environment():
    \"\"\"Configura variáveis de ambiente\"\"\"
    os.environ.setdefault('ENVIRONMENT', 'production')
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '8000')
    os.environ.setdefault('WORKERS', '4')
    os.environ.setdefault('LOG_LEVEL', 'info')

def check_dependencies():
    \"\"\"Verifica dependências\"\"\"
    required_files = [
        "simple_server.py",
        "background_processor.py",
        "config.json"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Arquivo não encontrado: {file}")
            return False
        print(f"✅ {file}")
    
    return True

def start_server():
    \"\"\"Inicia servidor com configuração otimizada\"\"\"
    try:
        # Configurar variáveis de ambiente
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        # Comando para produção
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "simple_server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "4",
            "--log-level", "info",
            "--access-log",
            "--timeout-keep-alive", "60",
            "--limit-concurrency", "1000",
            "--limit-max-requests", "1000"
        ]
        
        print("🚀 Iniciando servidor de produção...")
        process = subprocess.Popen(cmd, env=env)
        
        # Aguardar inicialização
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Servidor iniciado com sucesso")
            return process
        else:
            print("❌ Erro ao iniciar servidor")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def start_background_processor():
    \"\"\"Inicia processador em background\"\"\"
    try:
        cmd = [sys.executable, "background_processor.py"]
        process = subprocess.Popen(cmd)
        
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Processador em background iniciado")
            return process
        else:
            print("❌ Erro ao iniciar processador")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar processador: {e}")
        return None

def signal_handler(signum, frame):
    \"\"\"Handler para sinais de parada\"\"\"
    print("\\n🛑 Parando sistema...")
    sys.exit(0)

def main():
    \"\"\"Função principal\"\"\"
    print("=" * 60)
    print("TECNOCURSOS AI - PRODUÇÃO")
    print("=" * 60)
    
    # Configurar handler de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Falha na verificação de dependências")
        sys.exit(1)
    
    # Configurar ambiente
    setup_environment()
    
    # Iniciar servidor
    server_process = start_server()
    if not server_process:
        print("❌ Falha ao iniciar servidor")
        sys.exit(1)
    
    # Iniciar processador
    processor_process = start_background_processor()
    
    print("\\n✅ Sistema iniciado com sucesso!")
    print("📊 Dashboard: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/health")
    print("\\nPressione Ctrl+C para parar...")
    
    try:
        # Manter sistema rodando
        while True:
            time.sleep(1)
            
            # Verificar se processos ainda estão rodando
            if server_process and server_process.poll() is not None:
                print("❌ Servidor parou inesperadamente")
                break
                
            if processor_process and processor_process.poll() is not None:
                print("❌ Processador parou inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\\n🛑 Parando sistema...")
        
        # Parar processos
        if server_process:
            server_process.terminate()
            print("✅ Servidor parado")
            
        if processor_process:
            processor_process.terminate()
            print("✅ Processador parado")
            
        print("✅ Sistema parado com sucesso")

if __name__ == "__main__":
    main()
"""
        
        with open("start_production.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Tornar executável
        os.chmod("start_production.py", 0o755)
        print("✅ Script de inicialização criado: start_production.py")
    
    def create_docker_compose(self):
        """Cria docker-compose para produção"""
        docker_compose = """version: '3.8'

services:
  tecnocursos:
    build: .
    container_name: tecnocursos-ai
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - HOST=0.0.0.0
      - PORT=8000
      - WORKERS=4
      - LOG_LEVEL=info
    volumes:
      - ./uploads:/app/uploads
      - ./static:/app/static
      - ./logs:/app/logs
      - ./cache:/app/cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - tecnocursos-network

  nginx:
    image: nginx:alpine
    container_name: tecnocursos-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/tecnocursos.conf:/etc/nginx/conf.d/default.conf
      - ./static:/var/www/tecnocursos/static
    depends_on:
      - tecnocursos
    restart: unless-stopped
    networks:
      - tecnocursos-network

  redis:
    image: redis:alpine
    container_name: tecnocursos-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - tecnocursos-network

volumes:
  redis_data:

networks:
  tecnocursos-network:
    driver: bridge
"""
        
        with open("docker-compose.production.yml", 'w', encoding='utf-8') as f:
            f.write(docker_compose)
        
        print("✅ Docker Compose criado: docker-compose.production.yml")
    
    def run_setup(self):
        """Executa configuração completa"""
        print("🔧 Configurando TecnoCursos AI para Produção...")
        
        # Verificar porta
        port = self.find_available_port()
        if port != self.base_port:
            print(f"⚠️ Porta {self.base_port} ocupada, usando porta {port}")
            if self.kill_process_on_port(self.base_port):
                print(f"✅ Processo na porta {self.base_port} finalizado")
        
        # Criar configurações
        self.create_production_config()
        self.setup_directories()
        self.create_environment_file()
        self.create_startup_script()
        self.create_docker_compose()
        
        print("\\n🎉 Configuração de produção concluída!")
        print("\\n📋 Próximos passos:")
        print("1. Configure as variáveis de ambiente em .env")
        print("2. Execute: python start_production.py")
        print("3. Ou use Docker: docker-compose -f docker-compose.production.yml up")
        print("\\n🔗 URLs:")
        print(f"   Dashboard: http://localhost:{port}")
        print(f"   API Docs: http://localhost:{port}/docs")
        print(f"   Health: http://localhost:{port}/health")

if __name__ == "__main__":
    config = ProductionConfig()
    config.run_setup() 