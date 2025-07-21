#!/usr/bin/env python3
"""
🔍 SISTEMA DE MONITORAMENTO AVANÇADO
TecnoCursos AI Enterprise Edition 2025
=======================================

Sistema de monitoramento em tempo real que:
✅ Monitora performance do sistema
✅ Detecta problemas automaticamente
✅ Gera relatórios detalhados
✅ Alerta sobre falhas
✅ Otimiza recursos

Autor: TecnoCursos AI Assistant
Data: 2025-01-16
"""

import psutil
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

# Configurar logging com suporte a Unicode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/system_monitor.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor avançado do sistema TecnoCursos AI"""
    
    def __init__(self):
        self.running = False
        self.metrics = {}
        self.alerts = []
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'network_errors': 10,
            'response_time_ms': 1000
        }
        self.monitoring_interval = 30  # segundos
        
    def get_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Rede
            network = psutil.net_io_counters()
            
            # Processos Python
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
            
            # Verificar portas em uso
            ports_in_use = []
            for port in [8000, 8001, 8002, 8003]:
                try:
                    import socket
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        s.close()
                        ports_in_use.append({'port': port, 'status': 'available'})
                except OSError:
                    ports_in_use.append({'port': port, 'status': 'in_use'})
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_gb': memory.used / (1024**3),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'python_processes': python_processes,
                'ports': ports_in_use,
                'uptime_seconds': time.time() - psutil.boot_time()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas: {e}")
            return None
    
    def check_alerts(self, metrics):
        """Verifica se há alertas baseados nas métricas"""
        alerts = []
        
        if not metrics:
            return alerts
        
        # CPU
        if metrics['cpu']['percent'] > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'warning',
                'message': f"CPU usage high: {metrics['cpu']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Memória
        if metrics['memory']['percent'] > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'warning',
                'message': f"Memory usage high: {metrics['memory']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Disco
        if metrics['disk']['percent'] > self.thresholds['disk_percent']:
            alerts.append({
                'type': 'warning',
                'message': f"Disk usage high: {metrics['disk']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Processos Python
        for proc in metrics['python_processes']:
            if proc['cpu_percent'] > 50:
                alerts.append({
                    'type': 'info',
                    'message': f"Python process {proc['name']} (PID {proc['pid']}) using {proc['cpu_percent']:.1f}% CPU",
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    def save_metrics(self, metrics):
        """Salva métricas em arquivo JSON"""
        try:
            metrics_file = Path('metrics/system_metrics.json')
            metrics_file.parent.mkdir(exist_ok=True)
            
            # Carregar métricas existentes
            if metrics_file.exists():
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    existing_metrics = json.load(f)
            else:
                existing_metrics = {'history': []}
            
            # Adicionar nova métrica
            existing_metrics['history'].append(metrics)
            
            # Manter apenas as últimas 1000 métricas
            if len(existing_metrics['history']) > 1000:
                existing_metrics['history'] = existing_metrics['history'][-1000:]
            
            # Salvar
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(existing_metrics, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")
    
    def generate_report(self):
        """Gera relatório de performance"""
        try:
            metrics_file = Path('metrics/system_metrics.json')
            if not metrics_file.exists():
                return "Nenhuma métrica disponível"
            
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data.get('history'):
                return "Nenhuma métrica disponível"
            
            # Últimas 10 métricas
            recent_metrics = data['history'][-10:]
            
            # Calcular médias
            cpu_avg = sum(m['cpu']['percent'] for m in recent_metrics) / len(recent_metrics)
            memory_avg = sum(m['memory']['percent'] for m in recent_metrics) / len(recent_metrics)
            disk_avg = sum(m['disk']['percent'] for m in recent_metrics) / len(recent_metrics)
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'cpu_average_percent': round(cpu_avg, 2),
                    'memory_average_percent': round(memory_avg, 2),
                    'disk_average_percent': round(disk_avg, 2),
                    'total_metrics_collected': len(data['history'])
                },
                'alerts': self.alerts[-10:],  # Últimos 10 alertas
                'recommendations': self.generate_recommendations(recent_metrics)
            }
            
            # Salvar relatório
            report_file = Path('reports/performance_report.json')
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return f"Erro ao gerar relatório: {e}"
    
    def generate_recommendations(self, metrics):
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        cpu_avg = sum(m['cpu']['percent'] for m in metrics) / len(metrics)
        memory_avg = sum(m['memory']['percent'] for m in metrics) / len(metrics)
        disk_avg = sum(m['disk']['percent'] for m in metrics) / len(metrics)
        
        if cpu_avg > 70:
            recommendations.append({
                'type': 'performance',
                'message': 'CPU usage is high. Consider optimizing processes or adding more CPU resources.',
                'priority': 'high'
            })
        
        if memory_avg > 80:
            recommendations.append({
                'type': 'memory',
                'message': 'Memory usage is high. Consider increasing RAM or optimizing memory usage.',
                'priority': 'high'
            })
        
        if disk_avg > 85:
            recommendations.append({
                'type': 'storage',
                'message': 'Disk usage is high. Consider cleaning up files or expanding storage.',
                'priority': 'medium'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'status',
                'message': 'System performance is within normal parameters.',
                'priority': 'low'
            })
        
        return recommendations
    
    def monitor_system(self):
        """Loop principal de monitoramento"""
        logger.info("Iniciando monitoramento do sistema...")
        
        while self.running:
            try:
                # Coletar métricas
                metrics = self.get_system_metrics()
                
                if metrics:
                    # Verificar alertas
                    new_alerts = self.check_alerts(metrics)
                    self.alerts.extend(new_alerts)
                    
                    # Salvar métricas
                    self.save_metrics(metrics)
                    
                    # Log de status
                    logger.info(f"CPU: {metrics['cpu']['percent']:.1f}% | "
                              f"Memory: {metrics['memory']['percent']:.1f}% | "
                              f"Disk: {metrics['disk']['percent']:.1f}%")
                    
                    # Gerar relatório a cada 10 minutos
                    if len(self.alerts) % 20 == 0:  # Aproximadamente a cada 10 minutos
                        self.generate_report()
                
                # Aguardar próximo ciclo
                time.sleep(self.monitoring_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro durante monitoramento: {e}")
                time.sleep(5)  # Aguardar antes de tentar novamente
    
    def start_monitoring(self):
        """Inicia o monitoramento"""
        self.running = True
        
        # Iniciar thread de monitoramento
        monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        monitor_thread.start()
        
        logger.info("Sistema de monitoramento iniciado")
        return monitor_thread
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        logger.info("Sistema de monitoramento parado")
    
    def get_status(self):
        """Retorna status atual do sistema"""
        metrics = self.get_system_metrics()
        if not metrics:
            return {"status": "error", "message": "Não foi possível coletar métricas"}
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "alerts_count": len(self.alerts),
            "recent_alerts": self.alerts[-5:]  # Últimos 5 alertas
        }

def main():
    """Função principal"""
    print("=" * 80)
    print("🔍 SISTEMA DE MONITORAMENTO AVANÇADO")
    print("TecnoCursos AI Enterprise Edition 2025")
    print("=" * 80)
    
    # Criar monitor
    monitor = SystemMonitor()
    
    try:
        # Iniciar monitoramento
        monitor_thread = monitor.start_monitoring()
        
        print("✅ Monitoramento iniciado com sucesso")
        print("📊 Métricas sendo coletadas a cada 30 segundos")
        print("📈 Relatórios gerados automaticamente")
        print("🔔 Alertas configurados")
        print("\nPressione Ctrl+C para parar...")
        
        # Manter programa rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Parando monitoramento...")
        monitor.stop_monitoring()
        
        # Gerar relatório final
        final_report = monitor.generate_report()
        print("📋 Relatório final gerado")
        
        print("✅ Monitoramento parado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 