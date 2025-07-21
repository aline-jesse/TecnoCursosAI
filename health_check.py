#!/usr/bin/env python3
"""
Script de verificação de saúde do sistema TecnoCursos AI
Monitora todos os componentes em tempo real
"""

import requests
import time
import sys
import socket
from datetime import datetime

def print_banner():
    """Imprime banner do sistema"""
    print("=" * 60)
    print("🏥 TECNOCURSOS AI - VERIFICAÇÃO DE SAÚDE DO SISTEMA")
    print("=" * 60)
    print("📅 Data/Hora:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🎯 Objetivo: Monitoramento completo do sistema")
    print("=" * 60)

def find_server_port(start_port=8000, max_attempts=10):
    """Encontra a porta onde o servidor está rodando"""
    for port in range(start_port, start_port + max_attempts):
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                return port
        except requests.exceptions.RequestException:
            continue
    return None

def check_server_health(port):
    """Verifica saúde do servidor"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor: ONLINE (Porta {port})")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Versão: {data.get('version', 'unknown')}")
            print(f"   Serviço: {data.get('service', 'unknown')}")
            return True
        else:
            print(f"❌ Servidor: ERRO (Status {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor: OFFLINE ({e})")
        return False

def check_api_endpoints(port):
    """Verifica endpoints da API"""
    endpoints = [
        ("/api/health", "Health API"),
        ("/api/status", "Status API"),
        ("/api/projects", "Projects API"),
        ("/api/videos", "Videos API"),
        ("/api/audios", "Audios API")
    ]
    
    print("\n🔧 Verificando endpoints da API:")
    all_ok = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:{port}{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: Status {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException:
            print(f"   ❌ {name}: Erro de conexão")
            all_ok = False
    
    return all_ok

def check_static_files(port):
    """Verifica arquivos estáticos"""
    files = [
        ("/", "Index HTML"),
        ("/src/App.jsx", "App Component"),
        ("/src/index.css", "CSS Styles"),
        ("/static/favicon.ico", "Favicon")
    ]
    
    print("\n📁 Verificando arquivos estáticos:")
    all_ok = True
    
    for file_path, name in files:
        try:
            response = requests.get(f"http://localhost:{port}{file_path}", timeout=3)
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: Status {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException:
            print(f"   ❌ {name}: Erro de conexão")
            all_ok = False
    
    return all_ok

def check_frontend(port):
    """Verifica frontend React"""
    try:
        response = requests.get(f"http://localhost:{port}/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "React" in content and "App" in content:
                print(f"✅ Frontend React: OK")
                return True
            else:
                print(f"❌ Frontend React: React não encontrado")
                return False
        else:
            print(f"❌ Frontend React: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend React: Erro de conexão ({e})")
        return False

def check_cors_support(port):
    """Verifica suporte a CORS"""
    try:
        response = requests.options(f"http://localhost:{port}/api/health", timeout=3)
        if response.status_code == 200:
            print(f"✅ CORS Support: OK")
            return True
        else:
            print(f"❌ CORS Support: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS Support: Erro de conexão ({e})")
        return False

def check_error_handling(port):
    """Verifica tratamento de erros"""
    try:
        response = requests.get(f"http://localhost:{port}/api/nonexistent", timeout=3)
        if response.status_code == 404:
            print(f"✅ Error Handling: OK")
            return True
        else:
            print(f"❌ Error Handling: Status inesperado {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error Handling: Erro de conexão ({e})")
        return False

def generate_health_report(results):
    """Gera relatório de saúde"""
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE SAÚDE DO SISTEMA")
    print("=" * 60)
    
    total_checks = len(results)
    passed_checks = sum(1 for _, result in results if result)
    
    for check_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{check_name}: {status}")
    
    print(f"\n🎯 Taxa de Sucesso: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
    
    if passed_checks == total_checks:
        print("\n🎉 SISTEMA 100% SAUDÁVEL!")
        print("✅ Todos os componentes estão funcionando corretamente")
        return True
    else:
        print(f"\n⚠️  {total_checks-passed_checks} problema(s) detectado(s)")
        print("🔧 Verifique os logs e tente reiniciar o sistema")
        return False

def continuous_monitoring(port):
    """Monitoramento contínuo"""
    print(f"\n📊 Monitoramento contínuo na porta {port}")
    print("💡 Pressione Ctrl+C para parar")
    
    try:
        while True:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Sistema OK - {time.strftime('%H:%M:%S')}")
                else:
                    print(f"⚠️  Sistema com problemas - {time.strftime('%H:%M:%S')}")
            except:
                print(f"❌ Sistema offline - {time.strftime('%H:%M:%S')}")
            
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n👋 Monitoramento parado")

def main():
    """Função principal"""
    print_banner()
    
    # Encontra servidor
    print("🔍 Procurando servidor...")
    port = find_server_port()
    if port is None:
        print("❌ Servidor não encontrado!")
        print("💡 Execute: python simple_server.py")
        return 1
    
    print(f"✅ Servidor encontrado na porta {port}")
    
    # Executa verificações
    results = [
        ("Servidor Health", lambda: check_server_health(port)),
        ("API Endpoints", lambda: check_api_endpoints(port)),
        ("Arquivos Estáticos", lambda: check_static_files(port)),
        ("Frontend React", lambda: check_frontend(port)),
        ("CORS Support", lambda: check_cors_support(port)),
        ("Error Handling", lambda: check_error_handling(port))
    ]
    
    for check_name, check_func in results:
        print(f"\n🔍 Verificando: {check_name}")
        result = check_func()
        results[results.index((check_name, check_func))] = (check_name, result)
    
    # Gera relatório
    system_healthy = generate_health_report(results)
    
    if system_healthy:
        print(f"\n🌐 URLs disponíveis:")
        print(f"   🎬 Editor: http://localhost:{port}")
        print(f"   🔗 Health: http://localhost:{port}/health")
        print(f"   📚 Docs: http://localhost:{port}/docs")
        print(f"   🔧 API: http://localhost:{port}/api/health")
        
        # Pergunta sobre monitoramento
        try:
            response = input("\n📊 Iniciar monitoramento contínuo? (s/n): ").lower()
            if response in ['s', 'sim', 'y', 'yes']:
                continuous_monitoring(port)
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
    
    return 0 if system_healthy else 1

if __name__ == "__main__":
    sys.exit(main()) 