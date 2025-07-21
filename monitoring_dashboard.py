#!/usr/bin/env python3
"""
Dashboard de Monitoramento em Tempo Real - TecnoCursos AI
Monitora sistema, uploads, background processing e métricas
"""

import time
import json
import requests
import threading
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringDashboard:
    """Dashboard de monitoramento em tempo real"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics = {
            "system": {},
            "uploads": {},
            "background": {},
            "api": {},
            "errors": []
        }
        self.running = False
        self.update_interval = 5  # segundos
        
    def start_monitoring(self):
        """Inicia o monitoramento"""
        self.running = True
        logger.info("🚀 Iniciando dashboard de monitoramento...")
        
        # Thread principal de monitoramento
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Thread de exibição
        display_thread = threading.Thread(target=self._display_loop)
        display_thread.daemon = True
        display_thread.start()
        
        logger.info("✅ Dashboard iniciado com sucesso")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        logger.info("🛑 Dashboard parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Coletar métricas do sistema
                self._collect_system_metrics()
                
                # Coletar métricas de upload
                self._collect_upload_metrics()
                
                # Coletar métricas de background
                self._collect_background_metrics()
                
                # Coletar métricas da API
                self._collect_api_metrics()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                self.metrics["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                })
                time.sleep(self.update_interval)
    
    def _collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.metrics["system"] = {
                    "status": data.get("status", "unknown"),
                    "version": data.get("version", "unknown"),
                    "uptime": data.get("uptime_seconds", 0),
                    "services": data.get("services_status", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                self.metrics["system"] = {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.metrics["system"] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _collect_upload_metrics(self):
        """Coleta métricas de upload"""
        try:
            response = requests.get(f"{self.base_url}/api/upload/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.metrics["uploads"] = data
            else:
                self.metrics["uploads"] = {
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.metrics["uploads"] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _collect_background_metrics(self):
        """Coleta métricas de background processing"""
        try:
            response = requests.get(f"{self.base_url}/api/background/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.metrics["background"] = data
            else:
                self.metrics["background"] = {
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.metrics["background"] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _collect_api_metrics(self):
        """Coleta métricas da API"""
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.metrics["api"] = data
            else:
                self.metrics["api"] = {
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.metrics["api"] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _display_loop(self):
        """Loop de exibição do dashboard"""
        while self.running:
            self._display_dashboard()
            time.sleep(2)
    
    def _display_dashboard(self):
        """Exibe o dashboard no console"""
        # Limpar console (Windows)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("🎬 TECNOCURSOS AI - DASHBOARD DE MONITORAMENTO")
        print("=" * 80)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print()
        
        # Status do Sistema
        print("🔧 STATUS DO SISTEMA")
        print("-" * 40)
        system = self.metrics.get("system", {})
        if system:
            status = system.get("status", "unknown")
            version = system.get("version", "unknown")
            uptime = system.get("uptime", 0)
            services = system.get("services", {})
            
            print(f"Status: {'✅ Online' if status == 'healthy' else '❌ Offline'}")
            print(f"Versão: {version}")
            print(f"Uptime: {uptime:.1f}s")
            print("Serviços:")
            for service, status in services.items():
                icon = "✅" if status == "healthy" else "❌"
                print(f"  {icon} {service}: {status}")
        else:
            print("❌ Dados não disponíveis")
        print()
        
        # Métricas de Upload
        print("📤 MÉTRICAS DE UPLOAD")
        print("-" * 40)
        uploads = self.metrics.get("uploads", {})
        if "error" not in uploads:
            total_files = uploads.get("total_files", 0)
            total_size = uploads.get("total_size", 0)
            by_type = uploads.get("by_type", {})
            
            print(f"Total de arquivos: {total_files}")
            print(f"Tamanho total: {total_size / (1024*1024):.2f} MB")
            print("Por tipo:")
            for file_type, stats in by_type.items():
                count = stats.get("count", 0)
                size = stats.get("size", 0)
                print(f"  📁 {file_type}: {count} arquivos ({size / (1024*1024):.2f} MB)")
        else:
            print(f"❌ Erro: {uploads.get('error', 'Desconhecido')}")
        print()
        
        # Métricas de Background
        print("⚡ PROCESSAMENTO EM BACKGROUND")
        print("-" * 40)
        background = self.metrics.get("background", {})
        if "error" not in background:
            total_tasks = background.get("total_tasks", 0)
            pending_tasks = background.get("pending_tasks", 0)
            running_tasks = background.get("running_tasks", 0)
            completed_tasks = background.get("completed_tasks", 0)
            failed_tasks = background.get("failed_tasks", 0)
            active_workers = background.get("active_workers", 0)
            queue_size = background.get("queue_size", 0)
            
            print(f"Total de tarefas: {total_tasks}")
            print(f"Pendentes: {pending_tasks}")
            print(f"Executando: {running_tasks}")
            print(f"Concluídas: {completed_tasks}")
            print(f"Falharam: {failed_tasks}")
            print(f"Workers ativos: {active_workers}")
            print(f"Fila: {queue_size}")
        else:
            print(f"❌ Erro: {background.get('error', 'Desconhecido')}")
        print()
        
        # Métricas da API
        print("🔌 MÉTRICAS DA API")
        print("-" * 40)
        api = self.metrics.get("api", {})
        if "error" not in api:
            total_users = api.get("total_users", 0)
            total_projects = api.get("total_projects", 0)
            total_files = api.get("total_files", 0)
            total_videos = api.get("total_videos", 0)
            
            print(f"Usuários: {total_users}")
            print(f"Projetos: {total_projects}")
            print(f"Arquivos: {total_files}")
            print(f"Vídeos: {total_videos}")
        else:
            print(f"❌ Erro: {api.get('error', 'Desconhecido')}")
        print()
        
        # Erros Recentes
        errors = self.metrics.get("errors", [])
        if errors:
            print("⚠️ ERROS RECENTES")
            print("-" * 40)
            for error in errors[-5:]:  # Últimos 5 erros
                timestamp = error.get("timestamp", "")
                error_msg = error.get("error", "")
                print(f"🕐 {timestamp}: {error_msg}")
            print()
        
        print("=" * 80)
        print("Pressione Ctrl+C para parar o monitoramento")
        print("=" * 80)
    
    def get_metrics(self) -> Dict:
        """Retorna as métricas atuais"""
        return self.metrics.copy()
    
    def export_metrics(self, filename: str = None):
        """Exporta métricas para arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Métricas exportadas para {filename}")

# Instância global
dashboard = MonitoringDashboard()

def start_dashboard(base_url: str = "http://localhost:8000"):
    """Inicia o dashboard de monitoramento"""
    global dashboard
    dashboard = MonitoringDashboard(base_url)
    dashboard.start_monitoring()

def stop_dashboard():
    """Para o dashboard de monitoramento"""
    global dashboard
    dashboard.stop_monitoring()

def get_current_metrics() -> Dict:
    """Obtém métricas atuais"""
    return dashboard.get_metrics()

def export_current_metrics(filename: str = None):
    """Exporta métricas atuais"""
    dashboard.export_metrics(filename)

if __name__ == "__main__":
    import os
    
    print("🎬 TecnoCursos AI - Dashboard de Monitoramento")
    print("=" * 50)
    
    try:
        # Iniciar dashboard
        start_dashboard()
        
        # Manter rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Parando dashboard...")
        stop_dashboard()
        print("✅ Dashboard parado")
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
        stop_dashboard() 