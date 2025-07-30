#!/usr/bin/env python3
"""
Teste Health Check - TecnoCursos AI
Verifica se o endpoint /health está funcionando
"""

import requests
import json
import time
import subprocess
import sys
import threading

def test_health_endpoint(url="http://localhost:8001/health"):
    """Testa o endpoint de health"""
    try:
        print(f"🔍 Testando health check em: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ SUCESSO: Health check respondeu!")
            
            data = response.json()
            print(f"📊 Status: {data.get('status', 'unknown')}")
            print(f"🔧 Serviço: {data.get('service', 'unknown')}")
            print(f"🏷️ Versão: {data.get('version', 'unknown')}")
            print(f"⏰ Timestamp: {data.get('timestamp', 'unknown')}")
            
            return True
            
        elif response.status_code == 404:
            print("❌ ERRO 404: Endpoint /health não encontrado!")
            print("💡 O servidor não tem a rota /health configurada")
            return False
            
        else:
            print(f"❌ ERRO: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor!")
        print("💡 Verifique se o backend está rodando na porta 8001")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout - servidor demorou para responder")
        return False
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

def start_server_and_test():
    """Inicia o servidor e testa health check"""
    print("=" * 50)
    print("🚀 INICIANDO SERVIDOR E TESTANDO HEALTH CHECK")
    print("=" * 50)
    
    # Tentar instalar dependências
    print("📦 Instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "requests"], 
                      check=True, capture_output=True)
        print("✅ Dependências instaladas!")
    except:
        print("⚠️ Algumas dependências podem já estar instaladas")
    
    # Iniciar servidor em background
    print("\n🚀 Iniciando servidor backend...")
    
    try:
        server_process = subprocess.Popen([
            sys.executable, "backend_with_health.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Servidor iniciado!")
        print("⏳ Aguardando servidor ficar disponível...")
        
        # Aguardar alguns segundos para o servidor inicializar
        time.sleep(3)
        
        # Testar health check várias vezes
        max_attempts = 10
        for attempt in range(max_attempts):
            print(f"\n🧪 Tentativa {attempt + 1}/{max_attempts}")
            
            if test_health_endpoint():
                print("\n🎉 SUCESSO TOTAL!")
                print("✅ Health check está funcionando perfeitamente!")
                
                # Teste adicional dos outros endpoints
                print("\n🔍 Testando outros endpoints...")
                
                # Testar página principal
                try:
                    response = requests.get("http://localhost:8001/", timeout=5)
                    if response.status_code == 200:
                        print("✅ Página principal: OK")
                    else:
                        print(f"⚠️ Página principal: Status {response.status_code}")
                except:
                    print("❌ Página principal: Erro")
                
                # Testar API status
                try:
                    response = requests.get("http://localhost:8001/api/status", timeout=5)
                    if response.status_code == 200:
                        print("✅ API Status: OK")
                    else:
                        print(f"⚠️ API Status: Status {response.status_code}")
                except:
                    print("❌ API Status: Erro")
                
                print("\n" + "=" * 50)
                print("🌐 URLS DISPONÍVEIS:")
                print("   • Backend: http://localhost:8001")
                print("   • Health: http://localhost:8001/health")
                print("   • Docs: http://localhost:8001/docs")
                print("   • Status: http://localhost:8001/api/status")
                print("=" * 50)
                
                # Manter servidor rodando
                print("\n💡 Servidor rodando! Pressione Ctrl+C para parar...")
                try:
                    server_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Parando servidor...")
                    server_process.terminate()
                    print("✅ Servidor parado!")
                
                return True
            
            else:
                print(f"⚠️ Tentativa {attempt + 1} falhou, tentando novamente...")
                time.sleep(2)
        
        print("\n❌ FALHA: Health check não funcionou após todas as tentativas")
        server_process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ ERRO ao iniciar servidor: {e}")
        return False

def quick_test():
    """Teste rápido se o servidor já está rodando"""
    print("🔍 Verificação rápida se servidor já está rodando...")
    
    if test_health_endpoint():
        print("\n🎉 Servidor já está rodando e health check funciona!")
        return True
    else:
        print("\n⚠️ Servidor não está rodando ou health check não funciona")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE HEALTH CHECK - TECNOCURSOS AI")
    print("=" * 50)
    
    # Primeiro, testar se já está rodando
    if not quick_test():
        # Se não estiver, iniciar e testar
        start_server_and_test()
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
