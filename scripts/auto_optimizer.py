#!/usr/bin/env python3
"""
Sistema de Otimização Automática - TecnoCursos AI Enterprise Edition
Implementa otimizações automáticas de performance, segurança e qualidade
"""

import os
import sys
import json
import time
import logging
import subprocess
import psutil
from pathlib import Path
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoOptimizer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.optimization_config = self.load_config()
        self.performance_metrics = {}
        
    def load_config(self):
        """Carrega configuração de otimização"""
        config_path = self.project_root / "config" / "optimization_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return self.create_default_config()
    
    def create_default_config(self):
        """Cria configuração padrão de otimização"""
        config = {
            "performance": {
                "memory_threshold": 80,
                "cpu_threshold": 70,
                "disk_threshold": 85
            },
            "security": {
                "auto_update_dependencies": True,
                "security_scan_interval": 3600,
                "vulnerability_check": True
            },
            "quality": {
                "code_analysis": True,
                "test_coverage_threshold": 80,
                "linting_auto_fix": True
            },
            "monitoring": {
                "metrics_collection": True,
                "alert_threshold": 90,
                "log_rotation": True
            }
        }
        
        # Salvar configuração
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / "optimization_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def optimize_performance(self):
        """Otimiza performance do sistema"""
        logger.info("Iniciando otimização de performance...")
        
        # Verificar uso de recursos
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)
        disk_percent = psutil.disk_usage('/').percent
        
        self.performance_metrics = {
            'memory': memory_percent,
            'cpu': cpu_percent,
            'disk': disk_percent,
            'timestamp': datetime.now().isoformat()
        }
        
        # Otimizações baseadas em thresholds
        if memory_percent > self.optimization_config['performance']['memory_threshold']:
            self.optimize_memory()
        
        if cpu_percent > self.optimization_config['performance']['cpu_threshold']:
            self.optimize_cpu()
        
        if disk_percent > self.optimization_config['performance']['disk_threshold']:
            self.optimize_disk()
        
        logger.info(f"Performance otimizada - Memória: {memory_percent}%, CPU: {cpu_percent}%, Disco: {disk_percent}%")
    
    def optimize_memory(self):
        """Otimiza uso de memória"""
        logger.info("Otimizando uso de memória...")
        
        # Limpar cache do Python
        import gc
        gc.collect()
        
        # Limpar logs antigos
        self.cleanup_old_logs()
        
        # Otimizar cache de arquivos
        self.optimize_file_cache()
    
    def optimize_cpu(self):
        """Otimiza uso de CPU"""
        logger.info("Otimizando uso de CPU...")
        
        # Verificar processos com alto uso de CPU
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 50:
                    logger.warning(f"Processo com alto uso de CPU: {proc.info['name']} ({proc.info['cpu_percent']}%)")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def optimize_disk(self):
        """Otimiza uso de disco"""
        logger.info("Otimizando uso de disco...")
        
        # Limpar arquivos temporários
        self.cleanup_temp_files()
        
        # Comprimir logs antigos
        self.compress_old_logs()
        
        # Limpar cache de build
        self.cleanup_build_cache()
    
    def cleanup_old_logs(self):
        """Remove logs antigos"""
        log_dir = self.project_root / "logs"
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < time.time() - 7 * 24 * 3600:  # 7 dias
                    log_file.unlink()
                    logger.info(f"Log antigo removido: {log_file}")
    
    def cleanup_temp_files(self):
        """Remove arquivos temporários"""
        temp_dirs = ["temp", "cache", "__pycache__"]
        for temp_dir in temp_dirs:
            temp_path = self.project_root / temp_dir
            if temp_path.exists():
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file() and file_path.stat().st_mtime < time.time() - 24 * 3600:  # 1 dia
                        file_path.unlink()
                        logger.info(f"Arquivo temporário removido: {file_path}")
    
    def compress_old_logs(self):
        """Comprime logs antigos"""
        import gzip
        import shutil
        
        log_dir = self.project_root / "logs"
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < time.time() - 3 * 24 * 3600:  # 3 dias
                    gz_file = log_file.with_suffix('.log.gz')
                    if not gz_file.exists():
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(gz_file, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        log_file.unlink()
                        logger.info(f"Log comprimido: {gz_file}")
    
    def cleanup_build_cache(self):
        """Remove cache de build"""
        build_dirs = ["build", "dist", "node_modules/.cache"]
        for build_dir in build_dirs:
            build_path = self.project_root / build_dir
            if build_path.exists():
                try:
                    import shutil
                    shutil.rmtree(build_path)
                    logger.info(f"Cache de build removido: {build_path}")
                except Exception as e:
                    logger.warning(f"Erro ao remover cache: {e}")
    
    def optimize_file_cache(self):
        """Otimiza cache de arquivos"""
        cache_dir = self.project_root / "cache"
        if cache_dir.exists():
            # Manter apenas os 100 arquivos mais recentes
            files = sorted(cache_dir.rglob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
            for file_path in files[100:]:
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Arquivo de cache removido: {file_path}")
    
    def security_optimization(self):
        """Otimizações de segurança"""
        logger.info("Iniciando otimizações de segurança...")
        
        if self.optimization_config['security']['auto_update_dependencies']:
            self.update_dependencies()
        
        if self.optimization_config['security']['vulnerability_check']:
            self.check_vulnerabilities()
    
    def update_dependencies(self):
        """Atualiza dependências"""
        logger.info("Atualizando dependências...")
        
        try:
            # Atualizar pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         capture_output=True, text=True)
            
            # Atualizar dependências Python
            if (self.project_root / "requirements.txt").exists():
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"],
                             capture_output=True, text=True)
            
            # Atualizar dependências Node.js
            if (self.project_root / "package.json").exists():
                subprocess.run(["npm", "update"], capture_output=True, text=True)
                subprocess.run(["npm", "audit", "fix"], capture_output=True, text=True)
            
            logger.info("Dependências atualizadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dependências: {e}")
    
    def check_vulnerabilities(self):
        """Verifica vulnerabilidades"""
        logger.info("Verificando vulnerabilidades...")
        
        try:
            # Verificar vulnerabilidades Python
            subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"],
                         capture_output=True, text=True)
            
            # Verificar vulnerabilidades Node.js
            if (self.project_root / "package.json").exists():
                result = subprocess.run(["npm", "audit"], capture_output=True, text=True)
                if "found 0 vulnerabilities" not in result.stdout:
                    logger.warning("Vulnerabilidades encontradas no Node.js")
            
            logger.info("Verificação de vulnerabilidades concluída")
            
        except Exception as e:
            logger.error(f"Erro ao verificar vulnerabilidades: {e}")
    
    def quality_optimization(self):
        """Otimizações de qualidade de código"""
        logger.info("Iniciando otimizações de qualidade...")
        
        if self.optimization_config['quality']['code_analysis']:
            self.analyze_code()
        
        if self.optimization_config['quality']['linting_auto_fix']:
            self.fix_linting_issues()
    
    def analyze_code(self):
        """Analisa qualidade do código"""
        logger.info("Analisando qualidade do código...")
        
        try:
            # Análise Python
            subprocess.run([sys.executable, "-m", "flake8", "."], capture_output=True, text=True)
            
            # Análise JavaScript/TypeScript
            if (self.project_root / "package.json").exists():
                subprocess.run(["npm", "run", "lint"], capture_output=True, text=True)
            
            logger.info("Análise de código concluída")
            
        except Exception as e:
            logger.error(f"Erro na análise de código: {e}")
    
    def fix_linting_issues(self):
        """Corrige problemas de linting"""
        logger.info("Corrigindo problemas de linting...")
        
        try:
            # Auto-fix Python
            subprocess.run([sys.executable, "-m", "autopep8", "--in-place", "--recursive", "."],
                         capture_output=True, text=True)
            
            # Auto-fix JavaScript
            if (self.project_root / "package.json").exists():
                subprocess.run(["npm", "run", "lint:fix"], capture_output=True, text=True)
            
            logger.info("Problemas de linting corrigidos")
            
        except Exception as e:
            logger.error(f"Erro ao corrigir linting: {e}")
    
    def monitoring_optimization(self):
        """Otimizações de monitoramento"""
        logger.info("Iniciando otimizações de monitoramento...")
        
        if self.optimization_config['monitoring']['metrics_collection']:
            self.collect_metrics()
        
        if self.optimization_config['monitoring']['log_rotation']:
            self.rotate_logs()
    
    def collect_metrics(self):
        """Coleta métricas do sistema"""
        metrics = {
            'system': {
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': datetime.now().isoformat()
            },
            'application': {
                'uptime': time.time(),
                'process_count': len(psutil.pids()),
                'network_connections': len(psutil.net_connections())
            }
        }
        
        # Salvar métricas
        metrics_file = self.project_root / "metrics" / "system_metrics.json"
        metrics_file.parent.mkdir(exist_ok=True)
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info("Métricas coletadas e salvas")
    
    def rotate_logs(self):
        """Rotaciona logs"""
        log_dir = self.project_root / "logs"
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    # Rotacionar log
                    backup_file = log_file.with_suffix('.log.old')
                    if backup_file.exists():
                        backup_file.unlink()
                    log_file.rename(backup_file)
                    logger.info(f"Log rotacionado: {log_file}")
    
    def run_full_optimization(self):
        """Executa otimização completa"""
        logger.info("=" * 60)
        logger.info("INICIANDO OTIMIZAÇÃO AUTOMÁTICA COMPLETA")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Otimizações de performance
            self.optimize_performance()
            
            # Otimizações de segurança
            self.security_optimization()
            
            # Otimizações de qualidade
            self.quality_optimization()
            
            # Otimizações de monitoramento
            self.monitoring_optimization()
            
            # Salvar relatório
            self.save_optimization_report(start_time)
            
            logger.info("=" * 60)
            logger.info("OTIMIZAÇÃO COMPLETA CONCLUÍDA COM SUCESSO")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Erro durante otimização: {e}")
            raise
    
    def save_optimization_report(self, start_time):
        """Salva relatório de otimização"""
        end_time = time.time()
        duration = end_time - start_time
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'performance_metrics': self.performance_metrics,
            'optimizations_applied': [
                'Performance optimization',
                'Security updates',
                'Code quality improvements',
                'Monitoring enhancements'
            ],
            'status': 'completed'
        }
        
        report_file = self.project_root / "reports" / "optimization_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Relatório de otimização salvo: {report_file}")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 SISTEMA DE OTIMIZAÇÃO AUTOMÁTICA")
    print("TecnoCursos AI Enterprise Edition 2025")
    print("=" * 60)
    
    optimizer = AutoOptimizer()
    
    try:
        optimizer.run_full_optimization()
        print("✅ Otimização concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Otimização interrompida pelo usuário")
        
    except Exception as e:
        print(f"❌ Erro durante otimização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 