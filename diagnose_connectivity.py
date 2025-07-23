#!/usr/bin/env python3
"""
Diagnóstico Rápido de Conectividade - TecnoCursos AI
Identifica problemas de acesso às URLs do sistema
"""

import socket
import requests
import psutil
import time
import subprocess
from typing import List, Dict, Any

class ConnectivityDiagnoser:
    """Diagnosticador de conectividade do sistema"""
    
    def __init__(self):
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ports_status": {},
            "server_processes": [],
            "connectivity_tests": {},
            "recommendations": []
        }
    
    def check_port_status(self, port: int) -> Dict[str, Any]:
        """Verifica status de uma porta específica"""
        try:
            # Verificar se porta está em uso
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                return {"status": "OPEN", "accessible": True}
            else:
                return {"status": "CLOSED", "accessible": False}
                
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "accessible": False}
    
    def find_python_servers(self) -> List[Dict[str, Any]]:
        """Encontra processos Python que podem ser servidores"""
        servers = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any(keyword in ' '.join(cmdline).lower() 
                                         for keyword in ['uvicorn', 'fastapi', 'server', 'app']):
                            
                            # Tentar extrair porta da linha de comando
                            port = None
                            for i, arg in enumerate(cmdline):
                                if '--port' in arg and i + 1 < len(cmdline):
                                    try:
                                        port = int(cmdline[i + 1])
                                    except:
                                        pass
                                elif ':' in arg and arg.count(':') == 1:
                                    try:
                                        port = int(arg.split(':')[1])
                                    except:
                                        pass
                            
                            servers.append({
                                "pid": proc.info['pid'],
                                "cmdline": ' '.join(cmdline) if cmdline else "",
                                "port": port,
                                "name": proc.info['name']
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"⚠️ Erro ao buscar processos: {e}")
        
        return servers
    
    def test_url_connectivity(self, url: str) -> Dict[str, Any]:
        """Testa conectividade para uma URL específica"""
        try:
            response = requests.get(url, timeout=5)
            return {
                "url": url,
                "status_code": response.status_code,
                "accessible": True,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content)
            }
        except requests.exceptions.ConnectionError:
            return {
                "url": url,
                "error": "Connection refused - Servidor não está rodando nesta URL",
                "accessible": False
            }
        except requests.exceptions.Timeout:
            return {
                "url": url,
                "error": "Timeout - Servidor demorou para responder",
                "accessible": False
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "accessible": False
            }
    
    def scan_common_ports(self) -> Dict[int, Dict[str, Any]]:
        """Escaneia portas comuns para servidores web"""
        common_ports = [8000, 8001, 8002, 8003, 8004, 8005, 3000, 5000, 9000]
        port_status = {}
        
        for port in common_ports:
            port_status[port] = self.check_port_status(port)
            
        return port_status
    
    def generate_test_urls(self, open_ports: List[int]) -> List[str]:
        """Gera URLs de teste baseadas nas portas abertas"""
        urls = []
        
        for port in open_ports:
            base_url = f"http://localhost:{port}"
            test_urls = [
                f"{base_url}/",
                f"{base_url}/api/health",
                f"{base_url}/docs",
                f"{base_url}/api/info"
            ]
            urls.extend(test_urls)
            
        return urls
    
    def run_complete_diagnosis(self):
        """Executa diagnóstico completo de conectividade"""
        print("🔍 TecnoCursos AI - Diagnóstico de Conectividade")
        print("=" * 55)
        
        # 1. Verificar portas
        print("🔌 Verificando portas...")
        self.results["ports_status"] = self.scan_common_ports()
        
        # 2. Encontrar servidores Python
        print("🐍 Procurando servidores Python...")
        self.results["server_processes"] = self.find_python_servers()
        
        # 3. Testar conectividade
        print("🌐 Testando conectividade...")
        open_ports = [port for port, status in self.results["ports_status"].items() 
                     if status.get("accessible", False)]
        
        if open_ports:
            test_urls = self.generate_test_urls(open_ports)
            for url in test_urls:
                self.results["connectivity_tests"][url] = self.test_url_connectivity(url)
        
        # 4. Gerar recomendações
        self.generate_recommendations()
        
        # 5. Mostrar resultados
        self.print_diagnosis_results()
    
    def generate_recommendations(self):
        """Gera recomendações baseadas no diagnóstico"""
        recommendations = []
        
        # Verificar se há portas abertas
        open_ports = [port for port, status in self.results["ports_status"].items() 
                     if status.get("accessible", False)]
        
        if not open_ports:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Nenhum servidor detectado",
                "solution": "Execute: python start_production_server.py",
                "command": "python start_production_server.py"
            })
        else:
            # Verificar se URLs estão acessíveis
            accessible_urls = [url for url, result in self.results["connectivity_tests"].items() 
                             if result.get("accessible", False)]
            
            if not accessible_urls:
                recommendations.append({
                    "priority": "MEDIUM",
                    "issue": "Servidor rodando mas URLs não acessíveis",
                    "solution": "Verificar se servidor inicializou completamente",
                    "command": "python test_backend_fixed.py"
                })
            else:
                recommendations.append({
                    "priority": "INFO",
                    "issue": "Sistema funcionando",
                    "solution": f"Use: {accessible_urls[0]}",
                    "url": accessible_urls[0]
                })
        
        # Verificar processos Python suspeitos
        if len(self.results["server_processes"]) > 1:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "Múltiplos servidores Python detectados",
                "solution": "Possível conflito de porta - finalizar processos extras",
                "command": "Finalizar processos duplicados"
            })
        
        self.results["recommendations"] = recommendations
    
    def print_diagnosis_results(self):
        """Mostra resultados do diagnóstico"""
        print("\n" + "=" * 55)
        print("📊 RESULTADOS DO DIAGNÓSTICO")
        print("=" * 55)
        
        # Status das portas
        print("\n🔌 Status das Portas:")
        for port, status in self.results["ports_status"].items():
            icon = "✅" if status.get("accessible") else "❌"
            print(f"   {icon} Porta {port}: {status['status']}")
        
        # Processos encontrados
        if self.results["server_processes"]:
            print(f"\n🐍 Servidores Python Encontrados ({len(self.results['server_processes'])}):")
            for server in self.results["server_processes"]:
                port_info = f"(porta {server['port']})" if server['port'] else "(porta não identificada)"
                print(f"   🔧 PID {server['pid']}: {server['name']} {port_info}")
                if len(server['cmdline']) > 80:
                    print(f"      Comando: {server['cmdline'][:80]}...")
                else:
                    print(f"      Comando: {server['cmdline']}")
        else:
            print("\n🐍 Nenhum servidor Python encontrado")
        
        # Testes de conectividade
        if self.results["connectivity_tests"]:
            print(f"\n🌐 Testes de Conectividade:")
            accessible_count = 0
            for url, result in self.results["connectivity_tests"].items():
                if result.get("accessible"):
                    accessible_count += 1
                    print(f"   ✅ {url} - Status {result.get('status_code', 'OK')}")
                else:
                    print(f"   ❌ {url} - {result.get('error', 'Falha')}")
            
            print(f"\n📈 Resumo: {accessible_count}/{len(self.results['connectivity_tests'])} URLs acessíveis")
        
        # Recomendações
        if self.results["recommendations"]:
            print(f"\n💡 Recomendações:")
            for rec in self.results["recommendations"]:
                priority_icon = "🔴" if rec["priority"] == "HIGH" else "🟡" if rec["priority"] == "MEDIUM" else "🟢"
                print(f"   {priority_icon} {rec['issue']}")
                print(f"      Solução: {rec['solution']}")
                if "command" in rec:
                    print(f"      Comando: {rec['command']}")
                if "url" in rec:
                    print(f"      URL: {rec['url']}")
                print()

def main():
    """Função principal"""
    diagnoser = ConnectivityDiagnoser()
    
    try:
        diagnoser.run_complete_diagnosis()
        
        # Salvar resultados
        import json
        with open("connectivity_diagnosis.json", "w", encoding="utf-8") as f:
            json.dump(diagnoser.results, f, indent=2, ensure_ascii=False)
        
        print("💾 Resultados salvos em: connectivity_diagnosis.json")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante diagnóstico: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPressione Enter para sair...") 