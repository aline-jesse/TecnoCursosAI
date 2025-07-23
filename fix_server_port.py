#!/usr/bin/env python3
"""
Correção de Porta do Servidor - TecnoCursos AI
Script para resolver problemas de porta e facilitar acesso
"""

import psutil
import time
import subprocess
import webbrowser
from typing import Optional

class ServerPortFixer:
    """Corrige problemas de porta do servidor"""
    
    def __init__(self):
        self.current_server_pid = None
        self.current_port = None
        
    def find_current_server(self) -> Optional[dict]:
        """Encontra o servidor Python atual"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any(keyword in ' '.join(cmdline).lower() 
                                         for keyword in ['server_simple_fase4', 'uvicorn', 'fastapi']):
                            return {
                                "pid": proc.info['pid'],
                                "cmdline": ' '.join(cmdline) if cmdline else "",
                                "process": proc
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️ Erro ao buscar servidor: {e}")
        
        return None
    
    def kill_current_server(self):
        """Para o servidor atual"""
        server = self.find_current_server()
        
        if server:
            try:
                print(f"🔄 Parando servidor atual (PID {server['pid']})...")
                server['process'].terminate()
                
                # Aguardar processo finalizar
                try:
                    server['process'].wait(timeout=5)
                    print("✅ Servidor parado com sucesso")
                    return True
                except psutil.TimeoutExpired:
                    print("⚠️ Forçando finalização...")
                    server['process'].kill()
                    return True
                    
            except Exception as e:
                print(f"❌ Erro ao parar servidor: {e}")
                return False
        else:
            print("ℹ️ Nenhum servidor encontrado para parar")
            return True
    
    def start_server_on_port(self, port: int = 8000):
        """Inicia servidor na porta especificada"""
        try:
            print(f"🚀 Iniciando servidor na porta {port}...")
            
            # Modificar server_simple_fase4.py para usar a porta correta
            with open("server_simple_fase4.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Substituir porta no código
            if "port=8001" in content:
                content = content.replace("port=8001", f"port={port}")
                with open("server_simple_fase4.py", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Porta atualizada para {port} no código")
            
            # Iniciar servidor
            process = subprocess.Popen(
                ["python", "server_simple_fase4.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar alguns segundos para inicialização
            print("⏳ Aguardando inicialização...")
            time.sleep(3)
            
            # Verificar se processo ainda está rodando
            if process.poll() is None:
                print(f"✅ Servidor iniciado na porta {port}")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Erro ao iniciar servidor:")
                if stderr:
                    print(f"   Erro: {stderr.decode('utf-8', errors='ignore')}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            return False
    
    def open_browser_to_server(self, port: int = 8000):
        """Abre o navegador na URL do servidor"""
        urls_to_try = [
            f"http://localhost:{port}/docs",  # Documentação API
            f"http://localhost:{port}/api/health",  # Health check
            f"http://localhost:{port}/"  # Home
        ]
        
        print("🌐 Abrindo navegador...")
        for url in urls_to_try:
            try:
                webbrowser.open(url)
                print(f"✅ Navegador aberto em: {url}")
                break
            except Exception as e:
                print(f"⚠️ Erro ao abrir {url}: {e}")
                continue
    
    def show_available_urls(self, port: int = 8001):
        """Mostra URLs disponíveis"""
        print(f"\n🌐 URLs Disponíveis na Porta {port}:")
        print(f"   🏠 Home: http://localhost:{port}/")
        print(f"   ❤️ Health: http://localhost:{port}/api/health")
        print(f"   📚 Docs: http://localhost:{port}/docs")
        print(f"   🎬 Export: http://localhost:{port}/api/video/export/formats")
        print(f"   🎤 TTS: http://localhost:{port}/api/tts/voices")
        print(f"   🎭 Avatar: http://localhost:{port}/api/avatar/styles")
        print(f"   📊 Analytics: http://localhost:{port}/api/analytics")
    
    def run_port_fix(self):
        """Executa correção de porta"""
        print("🔧 TecnoCursos AI - Correção de Porta do Servidor")
        print("=" * 55)
        
        # Verificar servidor atual
        server = self.find_current_server()
        
        if server:
            print(f"🔍 Servidor encontrado (PID {server['pid']})")
            print("📋 Opções disponíveis:")
            print("   1. Usar servidor atual na porta 8001 (RECOMENDADO)")
            print("   2. Reiniciar servidor na porta 8000")
            print("   3. Apenas mostrar URLs funcionais")
            
            while True:
                try:
                    choice = input("\n🤔 Escolha uma opção (1-3): ").strip()
                    
                    if choice == "1":
                        print("\n✅ Usando servidor atual na porta 8001")
                        self.show_available_urls(8001)
                        self.open_browser_to_server(8001)
                        break
                    
                    elif choice == "2":
                        print("\n🔄 Reiniciando servidor na porta 8000...")
                        if self.kill_current_server():
                            time.sleep(2)
                            if self.start_server_on_port(8000):
                                self.show_available_urls(8000)
                                self.open_browser_to_server(8000)
                            else:
                                print("❌ Falha ao reiniciar servidor")
                                print("💡 Use a opção 1 para continuar com porta 8001")
                        break
                    
                    elif choice == "3":
                        print("\n📋 URLs funcionais atuais:")
                        self.show_available_urls(8001)
                        break
                    
                    else:
                        print("❌ Opção inválida. Digite 1, 2 ou 3.")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Saindo...")
                    break
                except Exception as e:
                    print(f"❌ Erro: {e}")
                    break
        else:
            print("❌ Nenhum servidor encontrado rodando")
            print("🚀 Iniciando novo servidor...")
            if self.start_server_on_port(8000):
                self.show_available_urls(8000)
                self.open_browser_to_server(8000)

def main():
    """Função principal"""
    fixer = ServerPortFixer()
    
    try:
        fixer.run_port_fix()
        
    except Exception as e:
        print(f"\n❌ Erro durante correção: {e}")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main() 