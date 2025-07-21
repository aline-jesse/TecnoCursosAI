#!/usr/bin/env python3
"""
Script de Monitoramento para TecnoCursosAI

Este script monitora:
- Saúde da aplicação FastAPI
- Uso de recursos do sistema (CPU, RAM, Disco)
- Status do banco de dados MySQL
- Logs de erro
- Performance das APIs
- Alertas por email/webhook
"""

import sys
import os
import time
import json
import psutil
import requests
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Adicionar o diretório pai ao path para importar os módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurações de monitoramento
MONITORING_CONFIG = {
    "api_url": "http://localhost:8000",
    "health_endpoint": "/health",
    "check_interval": 60,  # segundos
    "alert_thresholds": {
        "cpu_percent": 80,
        "memory_percent": 85,
        "disk_percent": 90,
        "response_time_ms": 2000,
        "error_rate_percent": 5
    },
    "log_files": [
        "logs/app.log",
        "logs/error.log",
        "logs/access.log"
    ],
    "email": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "",
        "password": "",
        "to_emails": ["admin@tecnocursos.ai"]
    },
    "webhook": {
        "enabled": False,
        "url": "https://hooks.slack.com/services/...",
        "channel": "#alerts"
    }
}


class SystemMonitor:
    """Monitor principal do sistema"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = MONITORING_CONFIG.copy()
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                self.config.update(custom_config)
        
        self.setup_logging()
        self.alerts_sent = {}  # Cache para evitar spam de alertas
        
    def setup_logging(self):
        """Configurar sistema de logs"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "monitor.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("SystemMonitor")
    
    def check_system_resources(self) -> Dict:
        """Verificar recursos do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Informações de rede
            network = psutil.net_io_counters()
            
            # Processos Python (FastAPI)
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            resources = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "python_processes": python_processes
            }
            
            return resources
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar recursos do sistema: {str(e)}")
            return {}
    
    def check_api_health(self) -> Dict:
        """Verificar saúde da API"""
        try:
            start_time = time.time()
            
            # Health check básico
            health_url = f"{self.config['api_url']}{self.config['health_endpoint']}"
            response = requests.get(health_url, timeout=10)
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                health_data = response.json()
                status = "healthy"
            else:
                health_data = {"error": f"HTTP {response.status_code}"}
                status = "unhealthy"
            
            # Testar outros endpoints críticos
            endpoints_to_test = [
                "/docs",
                "/auth/login",  # POST será diferente, mas GET deve retornar algo
            ]
            
            endpoint_results = {}
            for endpoint in endpoints_to_test:
                try:
                    test_start = time.time()
                    test_response = requests.get(f"{self.config['api_url']}{endpoint}", timeout=5)
                    test_time = (time.time() - test_start) * 1000
                    
                    endpoint_results[endpoint] = {
                        "status_code": test_response.status_code,
                        "response_time_ms": test_time,
                        "success": test_response.status_code < 500
                    }
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "error": str(e),
                        "success": False
                    }
            
            api_health = {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "response_time_ms": response_time,
                "health_data": health_data,
                "endpoint_tests": endpoint_results
            }
            
            return api_health
            
        except requests.exceptions.ConnectionError:
            self.logger.error("API não está respondendo - Connection Error")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "down",
                "error": "Connection refused"
            }
        except requests.exceptions.Timeout:
            self.logger.error("API timeout")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "timeout",
                "error": "Request timeout"
            }
        except Exception as e:
            self.logger.error(f"Erro ao verificar API: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def check_database_connection(self) -> Dict:
        """Verificar conexão com o banco de dados"""
        try:
            # Tentar fazer uma consulta simples via API health
            health_url = f"{self.config['api_url']}{self.config['health_endpoint']}"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                db_status = health_data.get("database", {})
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "connected" if db_status.get("connected") else "disconnected",
                    "details": db_status
                }
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "unknown",
                    "error": f"Health endpoint returned {response.status_code}"
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar banco de dados: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def check_log_errors(self) -> Dict:
        """Verificar logs por erros recentes"""
        error_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": 0,
            "error_files": {},
            "recent_errors": []
        }
        
        # Verificar últimos 10 minutos
        cutoff_time = datetime.now() - timedelta(minutes=10)
        
        for log_file in self.config["log_files"]:
            if not os.path.exists(log_file):
                continue
                
            try:
                file_errors = 0
                recent_lines = []
                
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    # Ler últimas 1000 linhas (mais eficiente)
                    lines = f.readlines()[-1000:]
                    
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['error', 'exception', 'critical', 'traceback']):
                            file_errors += 1
                            if len(recent_lines) < 10:  # Limitar a 10 erros mais recentes
                                recent_lines.append(line.strip())
                
                error_summary["error_files"][log_file] = {
                    "error_count": file_errors,
                    "recent_errors": recent_lines
                }
                error_summary["total_errors"] += file_errors
                
            except Exception as e:
                self.logger.error(f"Erro ao ler log {log_file}: {str(e)}")
                error_summary["error_files"][log_file] = {
                    "error": str(e)
                }
        
        return error_summary
    
    def analyze_performance_trends(self, history: List[Dict]) -> Dict:
        """Analisar tendências de performance"""
        if len(history) < 2:
            return {"trend": "insufficient_data"}
        
        # Analisar últimas 10 medições
        recent_history = history[-10:]
        
        # Tendências de CPU
        cpu_values = [h.get("system_resources", {}).get("cpu", {}).get("percent", 0) for h in recent_history]
        cpu_trend = "stable"
        if len(cpu_values) >= 3:
            if cpu_values[-1] > cpu_values[0] * 1.2:
                cpu_trend = "increasing"
            elif cpu_values[-1] < cpu_values[0] * 0.8:
                cpu_trend = "decreasing"
        
        # Tendências de memória
        memory_values = [h.get("system_resources", {}).get("memory", {}).get("percent", 0) for h in recent_history]
        memory_trend = "stable"
        if len(memory_values) >= 3:
            if memory_values[-1] > memory_values[0] * 1.1:
                memory_trend = "increasing"
            elif memory_values[-1] < memory_values[0] * 0.9:
                memory_trend = "decreasing"
        
        # Tendências de tempo de resposta
        api_response_times = [h.get("api_health", {}).get("response_time_ms", 0) for h in recent_history]
        response_time_trend = "stable"
        if len(api_response_times) >= 3:
            if api_response_times[-1] > api_response_times[0] * 1.3:
                response_time_trend = "degrading"
            elif api_response_times[-1] < api_response_times[0] * 0.7:
                response_time_trend = "improving"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "response_time_trend": response_time_trend,
            "avg_cpu": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "avg_memory": sum(memory_values) / len(memory_values) if memory_values else 0,
            "avg_response_time": sum(api_response_times) / len(api_response_times) if api_response_times else 0
        }
    
    def check_alerts(self, monitoring_data: Dict) -> List[Dict]:
        """Verificar se há alertas a serem enviados"""
        alerts = []
        thresholds = self.config["alert_thresholds"]
        
        # Verificar CPU
        cpu_percent = monitoring_data.get("system_resources", {}).get("cpu", {}).get("percent", 0)
        if cpu_percent > thresholds["cpu_percent"]:
            alerts.append({
                "type": "cpu_high",
                "severity": "warning",
                "message": f"CPU usage is {cpu_percent:.1f}% (threshold: {thresholds['cpu_percent']}%)",
                "value": cpu_percent,
                "threshold": thresholds["cpu_percent"]
            })
        
        # Verificar Memória
        memory_percent = monitoring_data.get("system_resources", {}).get("memory", {}).get("percent", 0)
        if memory_percent > thresholds["memory_percent"]:
            alerts.append({
                "type": "memory_high",
                "severity": "warning",
                "message": f"Memory usage is {memory_percent:.1f}% (threshold: {thresholds['memory_percent']}%)",
                "value": memory_percent,
                "threshold": thresholds["memory_percent"]
            })
        
        # Verificar Disco
        disk_percent = monitoring_data.get("system_resources", {}).get("disk", {}).get("percent", 0)
        if disk_percent > thresholds["disk_percent"]:
            alerts.append({
                "type": "disk_high",
                "severity": "critical",
                "message": f"Disk usage is {disk_percent:.1f}% (threshold: {thresholds['disk_percent']}%)",
                "value": disk_percent,
                "threshold": thresholds["disk_percent"]
            })
        
        # Verificar API
        api_status = monitoring_data.get("api_health", {}).get("status", "unknown")
        if api_status in ["down", "unhealthy", "timeout"]:
            alerts.append({
                "type": "api_down",
                "severity": "critical",
                "message": f"API is {api_status}",
                "value": api_status
            })
        
        # Verificar tempo de resposta
        response_time = monitoring_data.get("api_health", {}).get("response_time_ms", 0)
        if response_time > thresholds["response_time_ms"]:
            alerts.append({
                "type": "response_time_high",
                "severity": "warning",
                "message": f"API response time is {response_time:.0f}ms (threshold: {thresholds['response_time_ms']}ms)",
                "value": response_time,
                "threshold": thresholds["response_time_ms"]
            })
        
        # Verificar erros nos logs
        total_errors = monitoring_data.get("log_errors", {}).get("total_errors", 0)
        if total_errors > 10:  # Mais de 10 erros em 10 minutos
            alerts.append({
                "type": "log_errors_high",
                "severity": "warning",
                "message": f"High number of log errors: {total_errors} in last 10 minutes",
                "value": total_errors
            })
        
        return alerts
    
    def send_alert_email(self, alerts: List[Dict]):
        """Enviar alertas por email"""
        if not self.config["email"]["enabled"] or not alerts:
            return
        
        try:
            smtp_server = smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"])
            smtp_server.starttls()
            smtp_server.login(self.config["email"]["username"], self.config["email"]["password"])
            
            for alert in alerts:
                # Evitar spam - só enviar se não foi enviado na última hora
                alert_key = f"{alert['type']}_{alert.get('severity', 'unknown')}"
                last_sent = self.alerts_sent.get(alert_key, datetime.min)
                
                if datetime.now() - last_sent < timedelta(hours=1):
                    continue
                
                msg = MIMEMultipart()
                msg['From'] = self.config["email"]["username"]
                msg['To'] = ", ".join(self.config["email"]["to_emails"])
                msg['Subject'] = f"[TecnoCursosAI] {alert['severity'].upper()}: {alert['type']}"
                
                body = f"""
Alert Details:
- Type: {alert['type']}
- Severity: {alert['severity']}
- Message: {alert['message']}
- Timestamp: {datetime.now().isoformat()}
- Server: {os.uname().nodename if hasattr(os, 'uname') else 'Unknown'}

This is an automated alert from TecnoCursosAI monitoring system.
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                smtp_server.send_message(msg)
                self.alerts_sent[alert_key] = datetime.now()
                
                self.logger.info(f"Alert email sent: {alert['type']}")
            
            smtp_server.quit()
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email de alerta: {str(e)}")
    
    def send_webhook_alert(self, alerts: List[Dict]):
        """Enviar alertas via webhook (Slack, Discord, etc.)"""
        if not self.config["webhook"]["enabled"] or not alerts:
            return
        
        try:
            for alert in alerts:
                payload = {
                    "text": f"🚨 TecnoCursosAI Alert",
                    "attachments": [{
                        "color": "danger" if alert['severity'] == 'critical' else "warning",
                        "fields": [
                            {"title": "Type", "value": alert['type'], "short": True},
                            {"title": "Severity", "value": alert['severity'], "short": True},
                            {"title": "Message", "value": alert['message'], "short": False},
                            {"title": "Timestamp", "value": datetime.now().isoformat(), "short": True}
                        ]
                    }]
                }
                
                response = requests.post(self.config["webhook"]["url"], json=payload, timeout=10)
                
                if response.status_code == 200:
                    self.logger.info(f"Webhook alert sent: {alert['type']}")
                else:
                    self.logger.error(f"Webhook failed: {response.status_code}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao enviar webhook: {str(e)}")
    
    def run_monitoring_cycle(self) -> Dict:
        """Executar um ciclo completo de monitoramento"""
        self.logger.info("Iniciando ciclo de monitoramento...")
        
        monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "system_resources": self.check_system_resources(),
            "api_health": self.check_api_health(),
            "database": self.check_database_connection(),
            "log_errors": self.check_log_errors()
        }
        
        # Verificar alertas
        alerts = self.check_alerts(monitoring_data)
        
        if alerts:
            self.logger.warning(f"Encontrados {len(alerts)} alertas")
            for alert in alerts:
                self.logger.warning(f"Alert: {alert['message']}")
            
            # Enviar notificações
            self.send_alert_email(alerts)
            self.send_webhook_alert(alerts)
        
        monitoring_data["alerts"] = alerts
        
        return monitoring_data
    
    def save_monitoring_data(self, data: Dict, history_file: str = "logs/monitoring_history.jsonl"):
        """Salvar dados de monitoramento em arquivo"""
        try:
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, default=str) + '\n')
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados de monitoramento: {str(e)}")
    
    def run_continuous_monitoring(self):
        """Executar monitoramento contínuo"""
        self.logger.info("Iniciando monitoramento contínuo...")
        self.logger.info(f"Intervalo de verificação: {self.config['check_interval']} segundos")
        
        monitoring_history = []
        
        try:
            while True:
                try:
                    # Executar ciclo de monitoramento
                    monitoring_data = self.run_monitoring_cycle()
                    
                    # Salvar em arquivo
                    self.save_monitoring_data(monitoring_data)
                    
                    # Manter histórico em memória (últimas 100 medições)
                    monitoring_history.append(monitoring_data)
                    if len(monitoring_history) > 100:
                        monitoring_history.pop(0)
                    
                    # Analisar tendências
                    if len(monitoring_history) >= 5:
                        trends = self.analyze_performance_trends(monitoring_history)
                        self.logger.info(f"Tendências: CPU={trends.get('cpu_trend')}, "
                                       f"Memory={trends.get('memory_trend')}, "
                                       f"Response={trends.get('response_time_trend')}")
                    
                    # Aguardar próximo ciclo
                    time.sleep(self.config['check_interval'])
                    
                except KeyboardInterrupt:
                    self.logger.info("Monitoramento interrompido pelo usuário")
                    break
                except Exception as e:
                    self.logger.error(f"Erro no ciclo de monitoramento: {str(e)}")
                    time.sleep(self.config['check_interval'])
                    
        except Exception as e:
            self.logger.error(f"Erro crítico no monitoramento: {str(e)}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Monitor do Sistema TecnoCursosAI")
    
    parser.add_argument(
        "--config",
        help="Arquivo de configuração JSON personalizado"
    )
    
    parser.add_argument(
        "--single-run",
        action="store_true",
        help="Executar uma única verificação e sair"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Intervalo entre verificações em segundos (padrão: 60)"
    )
    
    args = parser.parse_args()
    
    # Criar monitor
    monitor = SystemMonitor(args.config)
    
    # Atualizar intervalo se especificado
    if args.interval:
        monitor.config["check_interval"] = args.interval
    
    if args.single_run:
        # Executar uma única verificação
        monitoring_data = monitor.run_monitoring_cycle()
        print(json.dumps(monitoring_data, indent=2, default=str))
    else:
        # Executar monitoramento contínuo
        monitor.run_continuous_monitoring()


if __name__ == "__main__":
    main() 