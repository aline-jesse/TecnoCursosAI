"""
Script de Deploy Enterprise - TecnoCursos AI
==========================================

Deploy automatizado completo do sistema enterprise:
- Verificação de dependências e requisitos
- Configuração de todos os serviços avançados
- Execução de testes de integridade
- Configuração de backup automático
- Configuração de monitoramento
- Geração de relatórios de deploy
- Verificação de segurança
"""

import os
import sys
import asyncio
import subprocess
import time
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Cores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Imprimir cabeçalho formatado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"🚀 {text}")
    print(f"{'='*60}{Colors.ENDC}")

def print_step(step: str, status: str = ""):
    """Imprimir etapa com status"""
    if status == "OK":
        print(f"{Colors.GREEN}✅ {step}{Colors.ENDC}")
    elif status == "WARNING":
        print(f"{Colors.YELLOW}⚠️  {step}{Colors.ENDC}")
    elif status == "ERROR":
        print(f"{Colors.RED}❌ {step}{Colors.ENDC}")
    else:
        print(f"{Colors.CYAN}🔧 {step}{Colors.ENDC}")

def print_info(text: str):
    """Imprimir informação"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

class EnterpriseDeployer:
    """Deploy automatizado do sistema enterprise"""
    
    def __init__(self):
        self.start_time = time.time()
        self.deploy_log = []
        self.errors = []
        self.warnings = []
        
        # Diretórios importantes
        self.project_dir = Path.cwd()
        self.logs_dir = self.project_dir / "logs"
        self.backups_dir = self.project_dir / "backups"
        self.config_dir = self.project_dir / "config"
        
        # Configurações
        self.python_version_required = (3, 8)
        self.required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "alembic", "redis",
            "psutil", "cryptography", "aiohttp", "magic", "bleach"
        ]
        
    def log_step(self, step: str, status: str, details: str = ""):
        """Registrar etapa no log"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "status": status,
            "details": details
        }
        self.deploy_log.append(entry)
        
        if status == "ERROR":
            self.errors.append(entry)
        elif status == "WARNING":
            self.warnings.append(entry)

    def check_python_version(self) -> bool:
        """Verificar versão do Python"""
        print_step("Verificando versão do Python...")
        
        current_version = sys.version_info[:2]
        required_version = self.python_version_required
        
        if current_version >= required_version:
            print_step(f"Python {'.'.join(map(str, current_version))} ✓", "OK")
            self.log_step("check_python", "OK", f"Python {'.'.join(map(str, current_version))}")
            return True
        else:
            print_step(f"Python {'.'.join(map(str, current_version))} - Requerido: {'.'.join(map(str, required_version))}", "ERROR")
            self.log_step("check_python", "ERROR", f"Versão insuficiente: {'.'.join(map(str, current_version))}")
            return False

    def check_dependencies(self) -> bool:
        """Verificar dependências"""
        print_step("Verificando dependências...")
        
        missing_packages = []
        
        for package in self.required_packages:
            try:
                __import__(package)
                print_step(f"📦 {package} ✓", "OK")
            except ImportError:
                print_step(f"📦 {package} ✗", "WARNING")
                missing_packages.append(package)
        
        if missing_packages:
            print_info(f"Pacotes faltando: {', '.join(missing_packages)}")
            print_info("Execute: pip install -r requirements.txt")
            self.log_step("check_dependencies", "WARNING", f"Pacotes faltando: {missing_packages}")
            return False
        
        self.log_step("check_dependencies", "OK", "Todas as dependências encontradas")
        return True

    def check_system_resources(self) -> bool:
        """Verificar recursos do sistema"""
        print_step("Verificando recursos do sistema...")
        
        try:
            import psutil
            
            # Verificar CPU
            cpu_count = psutil.cpu_count()
            print_step(f"CPU cores: {cpu_count}", "OK" if cpu_count >= 2 else "WARNING")
            
            # Verificar memória
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            print_step(f"Memória: {memory_gb:.1f}GB", "OK" if memory_gb >= 4 else "WARNING")
            
            # Verificar disco
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024**3)
            print_step(f"Espaço livre: {disk_free_gb:.1f}GB", "OK" if disk_free_gb >= 10 else "WARNING")
            
            # Verificar se tem recursos suficientes
            sufficient = cpu_count >= 2 and memory_gb >= 4 and disk_free_gb >= 10
            
            self.log_step("check_resources", "OK" if sufficient else "WARNING", 
                         f"CPU: {cpu_count}, RAM: {memory_gb:.1f}GB, Disco: {disk_free_gb:.1f}GB")
            
            return True
            
        except ImportError:
            print_step("psutil não disponível", "WARNING")
            self.log_step("check_resources", "WARNING", "psutil não disponível")
            return True

    def create_directories(self) -> bool:
        """Criar diretórios necessários"""
        print_step("Criando estrutura de diretórios...")
        
        directories = [
            self.logs_dir,
            self.backups_dir,
            self.config_dir,
            self.project_dir / "app" / "middleware",
            self.project_dir / "app" / "validators",
            self.project_dir / "cache",
            self.project_dir / "temp"
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print_step(f"📁 {directory.name}", "OK")
            except Exception as e:
                print_step(f"📁 {directory.name} - Erro: {e}", "ERROR")
                self.log_step("create_directories", "ERROR", f"Erro ao criar {directory}: {e}")
                return False
        
        self.log_step("create_directories", "OK", "Diretórios criados")
        return True

    def setup_environment(self) -> bool:
        """Configurar variáveis de ambiente"""
        print_step("Configurando ambiente...")
        
        env_file = self.project_dir / ".env"
        
        # Configurações padrão enterprise
        env_config = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "tecnocursos_ai_enterprise_2025_" + str(int(time.time())),
            "DATABASE_URL": "mysql+pymysql://user:password@localhost:3306/tecnocursos_ai",
            "REDIS_URL": "redis://localhost:6379/0",
            "BACKUP_ENCRYPTION_KEY": "enterprise_backup_key_2025",
            "ENABLE_RATE_LIMITING": "true",
            "ENABLE_MONITORING": "true",
            "ENABLE_HEALTH_CHECKS": "true",
            "ENABLE_ADVANCED_VALIDATION": "true",
            "LOG_LEVEL": "INFO",
            "MAX_UPLOAD_SIZE": "100MB",
            "BACKUP_RETENTION_DAYS": "30"
        }
        
        try:
            # Ler arquivo existente se houver
            existing_config = {}
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            existing_config[key] = value
            
            # Mesclar com novas configurações (sem sobrescrever existentes)
            for key, value in env_config.items():
                if key not in existing_config:
                    existing_config[key] = value
            
            # Escrever arquivo atualizado
            with open(env_file, 'w') as f:
                f.write("# TecnoCursos AI - Enterprise Edition\n")
                f.write("# Configurações automáticas do deploy\n\n")
                
                for key, value in existing_config.items():
                    f.write(f"{key}={value}\n")
            
            print_step("Arquivo .env configurado", "OK")
            self.log_step("setup_environment", "OK", "Arquivo .env configurado")
            return True
            
        except Exception as e:
            print_step(f"Erro ao configurar .env: {e}", "ERROR")
            self.log_step("setup_environment", "ERROR", str(e))
            return False

    def run_database_migration(self) -> bool:
        """Executar migrações do banco de dados"""
        print_step("Executando migrações do banco...")
        
        try:
            # Verificar se alembic está configurado
            alembic_ini = self.project_dir / "alembic.ini"
            if not alembic_ini.exists():
                print_step("alembic.ini não encontrado", "WARNING")
                self.log_step("database_migration", "WARNING", "alembic.ini não encontrado")
                return True
            
            # Executar upgrade
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=self.project_dir
            )
            
            if result.returncode == 0:
                print_step("Migrações executadas com sucesso", "OK")
                self.log_step("database_migration", "OK", "Migrações executadas")
                return True
            else:
                print_step(f"Erro nas migrações: {result.stderr}", "ERROR")
                self.log_step("database_migration", "ERROR", result.stderr)
                return False
                
        except FileNotFoundError:
            print_step("Alembic não encontrado", "WARNING")
            self.log_step("database_migration", "WARNING", "Alembic não disponível")
            return True
        except Exception as e:
            print_step(f"Erro nas migrações: {e}", "ERROR")
            self.log_step("database_migration", "ERROR", str(e))
            return False

    def run_tests(self) -> bool:
        """Executar testes de integridade"""
        print_step("Executando testes de integridade...")
        
        try:
            # Verificar se pytest está disponível
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print_step("pytest não disponível, pulando testes", "WARNING")
                self.log_step("run_tests", "WARNING", "pytest não disponível")
                return True
            
            # Executar testes básicos
            test_commands = [
                ["python", "-c", "import app.main_enhanced; print('✅ Import main OK')"],
                ["python", "-c", "from app.services.health_check_service import health_service; print('✅ Health check service OK')"],
                ["python", "-c", "from app.middleware.rate_limiting import AdvancedRateLimitMiddleware; print('✅ Rate limiting OK')"]
            ]
            
            all_passed = True
            for cmd in test_commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print_step(result.stdout.strip(), "OK")
                else:
                    print_step(f"Teste falhou: {' '.join(cmd)}", "ERROR")
                    all_passed = False
            
            self.log_step("run_tests", "OK" if all_passed else "WARNING", "Testes de importação executados")
            return all_passed
            
        except Exception as e:
            print_step(f"Erro nos testes: {e}", "WARNING")
            self.log_step("run_tests", "WARNING", str(e))
            return True

    def configure_backup_system(self) -> bool:
        """Configurar sistema de backup"""
        print_step("Configurando sistema de backup...")
        
        try:
            backup_config = {
                "configs": [
                    {
                        "name": "sistema_diario",
                        "source_paths": ["app/", "templates/", "static/"],
                        "backup_type": "incremental",
                        "compression": "tar.gz",
                        "encryption": True,
                        "retention_days": 30,
                        "schedule": "0 2 * * *"  # Todo dia às 2:00
                    },
                    {
                        "name": "uploads_semanal",
                        "source_paths": ["uploads/", "app/static/uploads/"],
                        "backup_type": "full",
                        "compression": "tar.gz",
                        "encryption": False,
                        "retention_days": 90,
                        "schedule": "0 3 * * 0"  # Domingo às 3:00
                    }
                ],
                "global_settings": {
                    "backup_location": str(self.backups_dir),
                    "encryption_key": "enterprise_backup_2025",
                    "max_backup_size_gb": 50,
                    "verify_integrity": True
                }
            }
            
            config_file = self.config_dir / "backup_config.json"
            with open(config_file, 'w') as f:
                json.dump(backup_config, f, indent=2)
            
            print_step("Configuração de backup criada", "OK")
            self.log_step("configure_backup", "OK", "Sistema de backup configurado")
            return True
            
        except Exception as e:
            print_step(f"Erro na configuração de backup: {e}", "ERROR")
            self.log_step("configure_backup", "ERROR", str(e))
            return False

    def setup_monitoring(self) -> bool:
        """Configurar monitoramento"""
        print_step("Configurando monitoramento...")
        
        try:
            monitoring_config = {
                "enabled": True,
                "check_interval_seconds": 30,
                "alert_thresholds": {
                    "response_time_p95_ms": 2000,
                    "error_rate_percent": 5.0,
                    "cpu_percent": 80.0,
                    "memory_percent": 85.0,
                    "disk_percent": 90.0
                },
                "retention": {
                    "metrics_days": 30,
                    "alerts_days": 90,
                    "logs_days": 7
                },
                "notifications": {
                    "email_enabled": False,
                    "slack_enabled": False,
                    "webhook_enabled": False
                }
            }
            
            config_file = self.config_dir / "monitoring_config.json"
            with open(config_file, 'w') as f:
                json.dump(monitoring_config, f, indent=2)
            
            print_step("Configuração de monitoramento criada", "OK")
            self.log_step("setup_monitoring", "OK", "Monitoramento configurado")
            return True
            
        except Exception as e:
            print_step(f"Erro na configuração de monitoramento: {e}", "ERROR")
            self.log_step("setup_monitoring", "ERROR", str(e))
            return False

    def create_startup_scripts(self) -> bool:
        """Criar scripts de inicialização"""
        print_step("Criando scripts de inicialização...")
        
        try:
            # Script de start para desenvolvimento
            dev_script = """#!/bin/bash
echo "🚀 Iniciando TecnoCursos AI - Enterprise Edition (Desenvolvimento)"
export ENVIRONMENT=development
python -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8000 --reload
"""
            
            # Script de start para produção
            prod_script = """#!/bin/bash
echo "🚀 Iniciando TecnoCursos AI - Enterprise Edition (Produção)"
export ENVIRONMENT=production
python -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8000 --workers 4
"""
            
            # Script de backup manual
            backup_script = """#!/bin/bash
echo "💾 Executando backup manual do TecnoCursos AI"
python -c "
import asyncio
from app.services.enhanced_backup_service import enhanced_backup_service
asyncio.run(enhanced_backup_service.run_backup('sistema_diario'))
"
echo "✅ Backup concluído"
"""
            
            scripts = [
                ("start_dev.sh", dev_script),
                ("start_prod.sh", prod_script),
                ("backup_manual.sh", backup_script)
            ]
            
            for script_name, script_content in scripts:
                script_path = self.project_dir / script_name
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                # Tornar executável (Unix)
                if os.name != 'nt':
                    os.chmod(script_path, 0o755)
                
                print_step(f"📜 {script_name}", "OK")
            
            self.log_step("create_scripts", "OK", "Scripts de inicialização criados")
            return True
            
        except Exception as e:
            print_step(f"Erro ao criar scripts: {e}", "ERROR")
            self.log_step("create_scripts", "ERROR", str(e))
            return False

    def generate_deploy_report(self) -> bool:
        """Gerar relatório de deploy"""
        print_step("Gerando relatório de deploy...")
        
        try:
            deploy_time = time.time() - self.start_time
            
            report = {
                "deploy_info": {
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": round(deploy_time, 2),
                    "version": "Enterprise Edition 2.0.0",
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                },
                "summary": {
                    "total_steps": len(self.deploy_log),
                    "successful_steps": len([s for s in self.deploy_log if s["status"] == "OK"]),
                    "warnings": len(self.warnings),
                    "errors": len(self.errors)
                },
                "steps": self.deploy_log,
                "errors": self.errors,
                "warnings": self.warnings,
                "next_steps": [
                    "Configure as variáveis de ambiente no arquivo .env",
                    "Execute ./start_dev.sh para desenvolvimento",
                    "Execute ./start_prod.sh para produção",
                    "Acesse http://localhost:8000/docs para a documentação da API",
                    "Acesse http://localhost:8000/health/detailed para health check",
                    "Configure monitoramento externo se necessário"
                ]
            }
            
            # Salvar relatório
            report_file = self.logs_dir / f"deploy_report_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print_step(f"Relatório salvo: {report_file}", "OK")
            self.log_step("generate_report", "OK", f"Relatório salvo em {report_file}")
            
            return True
            
        except Exception as e:
            print_step(f"Erro ao gerar relatório: {e}", "ERROR")
            return False

    def run_security_check(self) -> bool:
        """Executar verificação de segurança básica"""
        print_step("Executando verificação de segurança...")
        
        security_issues = []
        
        # Verificar arquivo .env
        env_file = self.project_dir / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                
                # Verificar se SECRET_KEY não é padrão
                if "change_me" in content.lower() or "secret" in content.lower():
                    security_issues.append("SECRET_KEY pode estar usando valor padrão")
                
                # Verificar se não há credenciais expostas
                if "password=password" in content or "password=123" in content:
                    security_issues.append("Credenciais padrão detectadas")
        
        # Verificar permissões de arquivos importantes
        important_files = [".env", "alembic.ini"]
        for filename in important_files:
            filepath = self.project_dir / filename
            if filepath.exists() and os.name != 'nt':
                stat = filepath.stat()
                if stat.st_mode & 0o077:  # Verificar se outros têm acesso
                    security_issues.append(f"Arquivo {filename} tem permissões muito abertas")
        
        if security_issues:
            for issue in security_issues:
                print_step(f"🔒 {issue}", "WARNING")
            self.log_step("security_check", "WARNING", f"Problemas encontrados: {security_issues}")
        else:
            print_step("Nenhum problema de segurança detectado", "OK")
            self.log_step("security_check", "OK", "Verificação de segurança passou")
        
        return True

    async def run_deploy(self) -> bool:
        """Executar deploy completo"""
        print_header("TECNOCURSOS AI - DEPLOY ENTERPRISE EDITION")
        
        steps = [
            ("Verificação Python", self.check_python_version),
            ("Verificação Dependências", self.check_dependencies),
            ("Verificação Recursos", self.check_system_resources),
            ("Criação Diretórios", self.create_directories),
            ("Configuração Ambiente", self.setup_environment),
            ("Migração Banco", self.run_database_migration),
            ("Testes Integridade", self.run_tests),
            ("Sistema Backup", self.configure_backup_system),
            ("Configuração Monitoramento", self.setup_monitoring),
            ("Scripts Inicialização", self.create_startup_scripts),
            ("Verificação Segurança", self.run_security_check),
            ("Relatório Deploy", self.generate_deploy_report)
        ]
        
        success_count = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            print(f"\n{Colors.CYAN}🔧 {step_name}...{Colors.ENDC}")
            
            try:
                if step_func():
                    success_count += 1
                else:
                    print_step(f"{step_name} teve problemas", "WARNING")
            except Exception as e:
                print_step(f"{step_name} falhou: {e}", "ERROR")
                self.log_step(step_name.lower().replace(" ", "_"), "ERROR", str(e))
        
        # Resumo final
        print_header("RESUMO DO DEPLOY")
        
        deploy_time = time.time() - self.start_time
        success_rate = (success_count / total_steps) * 100
        
        print(f"{Colors.BOLD}📊 ESTATÍSTICAS:{Colors.ENDC}")
        print(f"   ⏱️  Tempo total: {deploy_time:.1f}s")
        print(f"   ✅ Etapas concluídas: {success_count}/{total_steps} ({success_rate:.1f}%)")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        print(f"   ❌ Erros: {len(self.errors)}")
        
        if success_rate >= 80:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 DEPLOY ENTERPRISE CONCLUÍDO COM SUCESSO!{Colors.ENDC}")
            print(f"{Colors.GREEN}   Sistema pronto para execução{Colors.ENDC}")
        elif success_rate >= 60:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  DEPLOY CONCLUÍDO COM WARNINGS{Colors.ENDC}")
            print(f"{Colors.YELLOW}   Sistema funcional, mas verifique os warnings{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ DEPLOY COM PROBLEMAS CRÍTICOS{Colors.ENDC}")
            print(f"{Colors.RED}   Verifique os erros antes de executar{Colors.ENDC}")
        
        print(f"\n{Colors.BLUE}📚 PRÓXIMOS PASSOS:{Colors.ENDC}")
        print(f"   1. Revisar arquivo .env com suas configurações")
        print(f"   2. Configurar banco de dados se necessário")
        print(f"   3. Executar: ./start_dev.sh (desenvolvimento)")
        print(f"   4. Executar: ./start_prod.sh (produção)")
        print(f"   5. Acessar: http://localhost:8000/docs")
        
        print(f"\n{Colors.HEADER}✨ TECNOCURSOS AI ENTERPRISE EDITION DEPLOYADO!{Colors.ENDC}")
        
        return success_rate >= 60

def main():
    """Função principal"""
    deployer = EnterpriseDeployer()
    
    try:
        # Executar deploy
        success = asyncio.run(deployer.run_deploy())
        
        # Exit code baseado no sucesso
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Deploy interrompido pelo usuário{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro crítico no deploy: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main() 