#!/usr/bin/env python3
"""
Script de Inicialização Completa - TecnoCursos AI Enterprise Edition
Inicia servidor, processador em background e dashboard de monitoramento
"""

import subprocess
import time
import threading
import sys
import os
from pathlib import Path

def print_banner():
    """Exibe banner do sistema"""
    print("=" * 80)
    print("TECNOCURSOS AI - ENTERPRISE EDITION 2025")
    print("=" * 80)
    print("Sistema de Editor de Video Inteligente")
    print("Versao: 2.1.0")
    print("Python 3.13.4")
    print("=" * 80)

def check_dependencies():
    """Verifica dependências"""
    print("Verificando dependencias...")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Python 3.8+ e necessario")
        return False
    
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar arquivos essenciais
    essential_files = [
        "simple_server.py",
        "upload_handler.py", 
        "background_processor.py",
        "monitoring_dashboard.py",
        "index.html",
        "config.json"
    ]
    
    for file in essential_files:
        if not Path(file).exists():
            print(f"Arquivo nao encontrado: {file}")
            return False
        print(f"OK {file}")
    
    return True

def create_directories():
    """Cria diretórios necessários"""
    print("Criando diretorios...")
    
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
        "cache",
        "logs",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"OK {directory}")
    
    print("Diretorios criados")

def start_server():
    """Inicia o servidor principal"""
    print("Iniciando servidor principal...")
    
    try:
        # Iniciar servidor em background
        process = subprocess.Popen(
            [sys.executable, "simple_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar inicialização
        time.sleep(3)
        
        if process.poll() is None:
            print("Servidor iniciado com sucesso")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"Erro ao iniciar servidor: {stderr}")
            return None
            
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        return None

def start_monitoring():
    """Inicia o dashboard de monitoramento"""
    print("Iniciando dashboard de monitoramento...")
    
    try:
        # Iniciar dashboard em background
        process = subprocess.Popen(
            [sys.executable, "monitoring_dashboard.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar inicialização
        time.sleep(2)
        
        if process.poll() is None:
            print("Dashboard iniciado com sucesso")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"Erro ao iniciar dashboard: {stderr}")
            return None
            
    except Exception as e:
        print(f"Erro ao iniciar dashboard: {e}")
        return None

def test_endpoints():
    """Testa endpoints principais"""
    print("Testando endpoints...")
    
    import requests
    
    endpoints = [
        ("/health", "Health Check"),
        ("/api/health", "API Health"),
        ("/api/status", "API Status"),
        ("/api/projects", "Projects"),
        ("/api/videos", "Videos"),
        ("/api/audios", "Audios")
    ]
    
    base_url = "http://localhost:8000"
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"OK {name}: OK")
            else:
                print(f"ERRO {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"ERRO {name}: Erro - {e}")

def show_system_info():
    """Exibe informações do sistema"""
    print("\n" + "=" * 80)
    print("INFORMACOES DO SISTEMA")
    print("=" * 80)
    
    print("URLs de Acesso:")
    print("  Editor: http://localhost:8000")
    print("  Health: http://localhost:8000/health")
    print("  Docs: http://localhost:8000/docs")
    print("  API: http://localhost:8000/api/health")
    print("  Upload: http://localhost:8000/api/upload/files")
    print("  Background: http://localhost:8000/api/background/stats")
    
    print("\nEndpoints Disponiveis:")
    print("  GET /health - Health check do sistema")
    print("  GET /api/health - Health check da API")
    print("  GET /api/status - Status do sistema")
    print("  GET /api/projects - Lista de projetos")
    print("  GET /api/videos - Lista de videos")
    print("  GET /api/audios - Lista de audios")
    print("  POST /api/upload - Upload de arquivos")
    print("  GET /api/upload/files - Lista de uploads")
    print("  GET /api/upload/stats - Estatisticas de upload")
    print("  POST /api/background/task - Submeter tarefa")
    print("  GET /api/background/tasks - Lista de tarefas")
    print("  GET /api/background/stats - Estatisticas de background")
    
    print("\nEstrutura de Diretorios:")
    print("  uploads/ - Arquivos enviados")
    print("  static/ - Arquivos estaticos")
    print("  cache/ - Cache do sistema")
    print("  logs/ - Logs do sistema")
    
    print("\nFuncionalidades:")
    print("  Servidor HTTP nativo Python")
    print("  API RESTful completa")
    print("  Sistema de upload avancado")
    print("  Processamento em background")
    print("  Dashboard de monitoramento")
    print("  Interface de editor profissional")
    print("  Health checks automaticos")
    print("  Logs detalhados")
    
    print("=" * 80)

def main():
    """Função principal"""
    print_banner()
    
    # Verificar dependências
    if not check_dependencies():
        print("Falha na verificacao de dependencias")
        return
    
    # Criar diretórios
    create_directories()
    
    # Iniciar servidor
    server_process = start_server()
    if not server_process:
        print("Falha ao iniciar servidor")
        return
    
    # Aguardar inicialização completa
    print("Aguardando inicializacao completa...")
    time.sleep(5)
    
    # Testar endpoints
    test_endpoints()
    
    # Iniciar monitoramento
    monitoring_process = start_monitoring()
    
    # Exibir informações
    show_system_info()
    
    print("\nSISTEMA INICIADO COM SUCESSO!")
    print("Dashboard de monitoramento disponivel")
    print("Acesse http://localhost:8000 para usar o editor")
    print("\nPressione Ctrl+C para parar o sistema...")
    
    try:
        # Manter sistema rodando
        while True:
            time.sleep(1)
            
            # Verificar se processos ainda estão rodando
            if server_process and server_process.poll() is not None:
                print("Servidor parou inesperadamente")
                break
                
            if monitoring_process and monitoring_process.poll() is not None:
                print("Dashboard parou inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\nParando sistema...")
        
        # Parar processos
        if server_process:
            server_process.terminate()
            print("Servidor parado")
            
        if monitoring_process:
            monitoring_process.terminate()
            print("Dashboard parado")
            
        print("Sistema parado com sucesso")

if __name__ == "__main__":
    main() 