#!/usr/bin/env python3
"""
Script para resolver problema de porta ocupada
TecnoCursos AI Enterprise Edition
"""

import os
import sys
import socket
import subprocess
import time
import psutil
import signal
from pathlib import Path

def find_process_on_port(port):
    """Encontra processo usando a porta"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Erro ao procurar processo: {e}")
    return None

def kill_process_safely(process):
    """Mata processo de forma segura"""
    try:
        print(f"Matando processo {process.info['name']} (PID: {process.info['pid']})")
        process.terminate()
        time.sleep(3)
        
        if process.is_running():
            print("Processo não respondeu ao terminate, forçando kill...")
            process.kill()
            time.sleep(1)
        
        if not process.is_running():
            print("✅ Processo finalizado com sucesso")
            return True
        else:
            print("❌ Não foi possível finalizar o processo")
            return False
            
    except Exception as e:
        print(f"Erro ao matar processo: {e}")
        return False

def check_port_available(port):
    """Verifica se porta está disponível"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0
    except:
        return False

def find_available_port(start_port=8000, max_attempts=10):
    """Encontra porta disponível"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            return port
    return None

def start_server_with_port(port):
    """Inicia servidor na porta especificada"""
    try:
        # Configurar variáveis de ambiente
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['HOST'] = '0.0.0.0'
        
        # Comando para iniciar servidor
        cmd = [
            sys.executable, "simple_server.py"
        ]
        
        print(f"🚀 Iniciando servidor na porta {port}...")
        process = subprocess.Popen(cmd, env=env)
        
        # Aguardar inicialização
        time.sleep(5)
        
        if process.poll() is None:
            print(f"✅ Servidor iniciado com sucesso na porta {port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erro ao iniciar servidor: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def main():
    """Função principal"""
    print("🔧 Resolvendo problema de porta ocupada...")
    print("=" * 50)
    
    target_port = 8000
    
    # Verificar se porta está ocupada
    if check_port_available(target_port):
        print(f"✅ Porta {target_port} está disponível")
        port = target_port
    else:
        print(f"⚠️ Porta {target_port} está ocupada")
        
        # Encontrar processo usando a porta
        process = find_process_on_port(target_port)
        
        if process:
            print(f"📋 Processo encontrado: {process.info['name']} (PID: {process.info['pid']})")
            
            # Perguntar se deve matar o processo
            response = input("Deseja finalizar o processo? (s/n): ").lower().strip()
            
            if response in ['s', 'sim', 'y', 'yes']:
                if kill_process_safely(process):
                    time.sleep(2)
                    if check_port_available(target_port):
                        print(f"✅ Porta {target_port} liberada")
                        port = target_port
                    else:
                        print(f"❌ Porta {target_port} ainda ocupada")
                        port = find_available_port(target_port + 1)
                else:
                    print("Usando porta alternativa...")
                    port = find_available_port(target_port + 1)
            else:
                print("Usando porta alternativa...")
                port = find_available_port(target_port + 1)
        else:
            print("Processo não encontrado, usando porta alternativa...")
            port = find_available_port(target_port + 1)
    
    if port is None:
        print("❌ Nenhuma porta disponível encontrada")
        return
    
    print(f"🎯 Usando porta: {port}")
    
    # Iniciar servidor
    server_process = start_server_with_port(port)
    
    if server_process:
        print(f"\n🎉 Sistema iniciado com sucesso!")
        print(f"📊 Dashboard: http://localhost:{port}")
        print(f"📖 Documentação: http://localhost:{port}/docs")
        print(f"💚 Health Check: http://localhost:{port}/health")
        print(f"🔗 API: http://localhost:{port}/api/health")
        print("\nPressione Ctrl+C para parar...")
        
        try:
            # Manter sistema rodando
            while True:
                time.sleep(1)
                
                # Verificar se processo ainda está rodando
                if server_process.poll() is not None:
                    print("❌ Servidor parou inesperadamente")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            
            # Parar processo
            if server_process:
                server_process.terminate()
                print("✅ Servidor parado")
                
            print("✅ Sistema parado com sucesso")
    else:
        print("❌ Falha ao iniciar servidor")

if __name__ == "__main__":
    main() 