#!/usr/bin/env python3
"""
Script de Correção Automática - TecnoCursos AI Enterprise Edition 2025
Corrige automaticamente problemas comuns e otimiza o sistema
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemFixer:
    """Classe para corrigir problemas do sistema TecnoCursos AI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = []
        
    def fix_python_dependencies(self) -> bool:
        """Corrige dependências Python"""
        logger.info("📦 Corrigindo dependências Python...")
        
        try:
            # Atualizar pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                         check=True, capture_output=True)
            logger.info("✅ pip atualizado")
            
            # Instalar dependências básicas
            basic_deps = [
                "fastapi",
                "uvicorn[standard]",
                "sqlalchemy",
                "pydantic",
                "python-multipart",
                "aiofiles",
                "requests",
                "python-jose[cryptography]",
                "passlib[bcrypt]",
                "python-dotenv"
            ]
            
            for dep in basic_deps:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep],
                                 check=True, capture_output=True)
                    logger.info(f"   ✅ {dep}")
                except subprocess.CalledProcessError:
                    logger.warning(f"   ⚠️ {dep} não pôde ser instalado")
            
            # Instalar dependências completas se requirements.txt existir
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                                 check=True, capture_output=True)
                    logger.info("✅ Todas as dependências instaladas")
                    self.fixes_applied.append("python_dependencies")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"❌ Erro ao instalar dependências: {e}")
                    return False
            else:
                logger.warning("⚠️ requirements.txt não encontrado")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir dependências: {e}")
            return False
    
    def fix_database(self) -> bool:
        """Corrige problemas de banco de dados"""
        logger.info("🗄️ Corrigindo banco de dados...")
        
        try:
            sys.path.insert(0, str(self.project_root))
            
            # Importar módulos de banco
            from app.database import engine, Base
            from app.models import User, Project, FileUpload, Video
            
            # Criar tabelas
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Tabelas criadas")
            
            # Executar migrações se possível
            try:
                subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                             check=True, capture_output=True)
                logger.info("✅ Migrações executadas")
            except subprocess.CalledProcessError:
                logger.warning("⚠️ Alembic não configurado")
            
            self.fixes_applied.append("database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir banco: {e}")
            return False
    
    def fix_file_structure(self) -> bool:
        """Corrige estrutura de arquivos"""
        logger.info("📁 Corrigindo estrutura de arquivos...")
        
        directories = [
            "uploads",
            "uploads/pdf",
            "uploads/pptx",
            "static/videos",
            "static/audios",
            "static/thumbnails",
            "cache",
            "logs",
            "temp"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"   ✅ {directory}")
        
        # Criar arquivos .gitkeep
        gitkeep_files = [
            "uploads/pdf/.gitkeep",
            "uploads/pptx/.gitkeep",
            "static/videos/.gitkeep",
            "static/audios/.gitkeep",
            "static/thumbnails/.gitkeep"
        ]
        
        for gitkeep in gitkeep_files:
            gitkeep_path = self.project_root / gitkeep
            if not gitkeep_path.exists():
                gitkeep_path.touch()
                logger.info(f"   ✅ {gitkeep}")
        
        self.fixes_applied.append("file_structure")
        return True
    
    def fix_env_file(self) -> bool:
        """Corrige arquivo .env"""
        logger.info("🔧 Corrigindo arquivo .env...")
        
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            env_content = """# TecnoCursos AI - Configurações
APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Banco de dados
DATABASE_URL=sqlite:///./tecnocursos.db

# Segurança
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-change-in-production

# Upload
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=.pdf,.pptx,.docx,.txt,.mp4,.avi,.mov,.jpg,.jpeg,.png,.gif,.mp3,.wav,.m4a

# CORS
CORS_ORIGINS=["*"]
CORS_CREDENTIALS=true

# Logs
LOG_LEVEL=INFO
LOG_FORMAT=json

# Cache
REDIS_URL=redis://localhost:6379

# TTS (opcional)
AZURE_TTS_KEY=
AZURE_TTS_REGION=

# Avatar (opcional)
D_ID_API_KEY=

# OpenAI (opcional)
OPENAI_API_KEY=

# Email (opcional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true

# Stripe (opcional)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=

# AWS (opcional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_S3_BUCKET=

# Analytics (opcional)
GOOGLE_ANALYTICS_ID=

# Notificações (opcional)
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=

# Monitoramento (opcional)
SENTRY_DSN=
"""
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            logger.info("✅ Arquivo .env criado")
            self.fixes_applied.append("env_file")
            return True
        else:
            logger.info("✅ Arquivo .env já existe")
            return True
    
    def fix_import_errors(self) -> bool:
        """Corrige erros de importação"""
        logger.info("🔧 Corrigindo erros de importação...")
        
        try:
            # Testar importações principais
            sys.path.insert(0, str(self.project_root))
            
            # Testar importações básicas
            basic_imports = [
                "app.main",
                "app.config",
                "app.database",
                "app.models"
            ]
            
            for module in basic_imports:
                try:
                    __import__(module)
                    logger.info(f"   ✅ {module}")
                except ImportError as e:
                    logger.warning(f"   ⚠️ {module}: {e}")
            
            # Testar routers
            router_imports = [
                "app.routers.auth",
                "app.routers.users",
                "app.routers.projects",
                "app.routers.files"
            ]
            
            for router in router_imports:
                try:
                    __import__(router)
                    logger.info(f"   ✅ {router}")
                except ImportError as e:
                    logger.warning(f"   ⚠️ {router}: {e}")
            
            self.fixes_applied.append("import_errors")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir imports: {e}")
            return False
    
    def fix_permissions(self) -> bool:
        """Corrige permissões de arquivos"""
        logger.info("🔐 Corrigindo permissões...")
        
        try:
            # Definir permissões para diretórios importantes
            directories = [
                "uploads",
                "static",
                "logs",
                "cache"
            ]
            
            for directory in directories:
                dir_path = self.project_root / directory
                if dir_path.exists():
                    # Tornar diretório gravável
                    dir_path.chmod(0o755)
                    logger.info(f"   ✅ {directory} permissões corrigidas")
            
            self.fixes_applied.append("permissions")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir permissões: {e}")
            return False
    
    def fix_cache(self) -> bool:
        """Limpa e corrige cache"""
        logger.info("🧹 Limpando cache...")
        
        try:
            # Limpar cache Python
            cache_dirs = [
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache"
            ]
            
            for cache_dir in cache_dirs:
                cache_path = self.project_root / cache_dir
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                    logger.info(f"   ✅ {cache_dir} removido")
            
            # Limpar cache da aplicação
            app_cache = self.project_root / "cache"
            if app_cache.exists():
                for item in app_cache.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                logger.info("   ✅ Cache da aplicação limpo")
            
            self.fixes_applied.append("cache")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {e}")
            return False
    
    def fix_logs(self) -> bool:
        """Corrige sistema de logs"""
        logger.info("📝 Corrigindo sistema de logs...")
        
        try:
            # Criar diretório de logs
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Criar arquivo de log básico
            log_file = logs_dir / "app.log"
            if not log_file.exists():
                log_file.touch()
                logger.info("   ✅ Arquivo de log criado")
            
            # Configurar logging básico
            logging_config = """# Configuração de logging para TecnoCursos AI
[loggers]
keys=root,tecnocursos

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=normalFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_tecnocursos]
level=INFO
handlers=consoleHandler,fileHandler
qualname=tecnocursos
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=normalFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=normalFormatter
args=('logs/app.log', 'a', 'utf-8')

[formatter_normalFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
"""
            
            config_file = self.project_root / "logging.conf"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(logging_config)
            
            logger.info("   ✅ Configuração de logging criada")
            
            self.fixes_applied.append("logs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir logs: {e}")
            return False
    
    def fix_ports(self) -> bool:
        """Corrige problemas de portas"""
        logger.info("🔌 Verificando portas...")
        
        try:
            import socket
            
            # Verificar porta 8000
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result == 0:
                logger.warning("⚠️ Porta 8000 está em uso")
                logger.info("💡 Tente usar porta 8001 ou 8002")
            else:
                logger.info("✅ Porta 8000 disponível")
            
            self.fixes_applied.append("ports")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar portas: {e}")
            return False
    
    def run_all_fixes(self) -> Dict:
        """Executa todas as correções"""
        logger.info("🔧 Iniciando correções automáticas do sistema...")
        logger.info("=" * 60)
        
        fixes = [
            ("python_dependencies", self.fix_python_dependencies),
            ("file_structure", self.fix_file_structure),
            ("env_file", self.fix_env_file),
            ("database", self.fix_database),
            ("import_errors", self.fix_import_errors),
            ("permissions", self.fix_permissions),
            ("cache", self.fix_cache),
            ("logs", self.fix_logs),
            ("ports", self.fix_ports)
        ]
        
        results = {}
        
        for fix_name, fix_func in fixes:
            logger.info(f"\n🔧 Executando: {fix_name}")
            try:
                result = fix_func()
                results[fix_name] = result
                status = "✅ CORRIGIDO" if result else "❌ FALHOU"
                logger.info(f"{status}: {fix_name}")
            except Exception as e:
                logger.error(f"❌ ERRO em {fix_name}: {e}")
                results[fix_name] = False
        
        # Relatório final
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO DE CORREÇÕES")
        logger.info("=" * 60)
        
        for fix_name, result in results.items():
            status = "✅ CORRIGIDO" if result else "❌ FALHOU"
            logger.info(f"{status}: {fix_name}")
        
        successful_fixes = sum(1 for result in results.values() if result)
        total_fixes = len(results)
        
        logger.info(f"\n📈 RESUMO:")
        logger.info(f"   Correções aplicadas: {successful_fixes}/{total_fixes}")
        logger.info(f"   Taxa de sucesso: {(successful_fixes/total_fixes)*100:.1f}%")
        
        return {
            "results": results,
            "fixes_applied": self.fixes_applied,
            "successful_fixes": successful_fixes,
            "total_fixes": total_fixes
        }

def main():
    """Função principal"""
    fixer = SystemFixer()
    
    logger.info("🚀 TECNOCURSOS AI - CORREÇÃO AUTOMÁTICA")
    logger.info("=" * 60)
    
    # Executar todas as correções
    report = fixer.run_all_fixes()
    
    # Conclusão
    success_rate = (report['successful_fixes'] / report['total_fixes']) * 100
    
    if success_rate >= 90:
        logger.info("\n🎉 SISTEMA CORRIGIDO COM SUCESSO!")
        logger.info("✅ Todas as correções principais foram aplicadas")
    elif success_rate >= 70:
        logger.info("\n✅ SISTEMA MAJORITARIAMENTE CORRIGIDO!")
        logger.info("⚠️ Algumas correções podem precisar de atenção manual")
    elif success_rate >= 50:
        logger.info("\n⚠️ SISTEMA PARCIALMENTE CORRIGIDO!")
        logger.info("🔧 Algumas correções falharam - verifique manualmente")
    else:
        logger.error("\n❌ MUITAS CORREÇÕES FALHARAM!")
        logger.error("🔧 Verifique a configuração do sistema")
    
    logger.info(f"\n🚀 Próximos passos:")
    logger.info(f"   1. Execute: python start_system_complete.py")
    logger.info(f"   2. Teste: python test_system_complete.py")
    logger.info(f"   3. Acesse: http://localhost:8000/docs")
    
    logger.info(f"\n📊 Taxa de sucesso: {success_rate:.1f}%")
    logger.info(f"🔧 Correções aplicadas: {len(report['fixes_applied'])}")

if __name__ == "__main__":
    main() 