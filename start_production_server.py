#!/usr/bin/env python3
"""
TecnoCursos AI - Production Server Launcher
Script inteligente para iniciar o servidor principal em produção
"""

import os
import sys
import time
import socket
import subprocess
import signal
from pathlib import Path

def check_port_available(port):
    """Verifica se uma porta está disponível"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except socket.error:
        return False

def kill_process_on_port(port):
    """Tenta finalizar processo rodando na porta especificada"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        print(f"🔄 Finalizando processo {pid} na porta {port}")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        time.sleep(2)
                        return True
        else:  # Linux/Mac
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip()
                print(f"🔄 Finalizando processo {pid} na porta {port}")
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(2)
                return True
    except Exception as e:
        print(f"⚠️ Erro ao finalizar processo: {e}")
    return False

def find_available_port(start_port=8000, max_attempts=10):
    """Encontra uma porta disponível"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            return port
    return None

def start_main_server():
    """Inicia o servidor principal do backend"""
    print("🚀 TecnoCursos AI - Production Server")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("backend/app/main.py").exists():
        print("❌ Erro: backend/app/main.py não encontrado")
        print("💡 Execute este script na raiz do projeto TecnoCursosAI")
        return False
    
    # Portas preferenciais
    preferred_ports = [8000, 8001, 8002, 8003]
    selected_port = None
    
    # Tentar encontrar uma porta disponível
    for port in preferred_ports:
        if check_port_available(port):
            selected_port = port
            break
        else:
            print(f"⚠️ Porta {port} está ocupada")
            
            # Perguntar se quer finalizar o processo
            if port == 8000:  # Só pergunta para a porta principal
                try:
                    choice = input(f"🤔 Finalizar processo na porta {port}? (s/N): ").lower()
                    if choice == 's':
                        if kill_process_on_port(port):
                            if check_port_available(port):
                                selected_port = port
                                break
                except KeyboardInterrupt:
                    print("\n👋 Cancelado pelo usuário")
                    return False
    
    # Se não encontrou porta, procurar uma disponível
    if selected_port is None:
        selected_port = find_available_port(8004)
        
    if selected_port is None:
        print("❌ Erro: Nenhuma porta disponível encontrada")
        return False
    
    print(f"✅ Usando porta: {selected_port}")
    
    # Configurar variáveis de ambiente
    os.environ["PORT"] = str(selected_port)
    
    # Adicionar backend ao path
    backend_path = Path("backend").absolute()
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    try:
        print("🔄 Iniciando servidor principal...")
        
        # Importar e configurar uvicorn
        import uvicorn
        from app.main import app
        
        # Configurações do servidor
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=selected_port,
            reload=False,  # Produção sem reload
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        print(f"🌐 Servidor iniciado em: http://localhost:{selected_port}")
        print(f"📚 Documentação em: http://localhost:{selected_port}/docs")
        print(f"❤️ Health check em: http://localhost:{selected_port}/api/health")
        print("\n🔥 Pressione Ctrl+C para parar o servidor")
        
        # Executar servidor
        server.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("\n💡 Dica: Execute 'python test_backend_fixed.py' para diagnosticar problemas")
        return False

def show_server_info():
    """Mostra informações sobre os servidores disponíveis"""
    print("\n📋 Servidores Disponíveis:")
    print("-" * 30)
    print("1. 🚀 Server Principal (main.py) - Funcionalidades completas")
    print("2. ⚡ Server Fase 4 (server_simple_fase4.py) - Endpoints específicos")
    print("3. 📊 Monitoring Dashboard (system/monitoring_dashboard.py)")
    print("\n💡 Este script inicia o servidor principal com todas as funcionalidades")

if __name__ == "__main__":
    show_server_info()
    success = start_main_server()
    sys.exit(0 if success else 1) 