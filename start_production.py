#!/usr/bin/env python3
"""
Script de Inicialização Otimizado - TecnoCursos AI
Versão de Produção
"""

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path

def setup_environment():
    """Configura variáveis de ambiente"""
    os.environ.setdefault('ENVIRONMENT', 'production')
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '8000')
    os.environ.setdefault('WORKERS', '4')
    os.environ.setdefault('LOG_LEVEL', 'info')

def check_dependencies():
    """Verifica dependências"""
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
    """Inicia servidor com configuração otimizada"""
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
    """Inicia processador em background"""
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
    """Handler para sinais de parada"""
    print("\n🛑 Parando sistema...")
    sys.exit(0)

def main():
    """Função principal"""
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
    
    print("\n✅ Sistema iniciado com sucesso!")
    print("📊 Dashboard: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/health")
    print("\nPressione Ctrl+C para parar...")
    
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
        print("\n🛑 Parando sistema...")
        
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
