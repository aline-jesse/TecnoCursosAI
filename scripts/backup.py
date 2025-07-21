#!/usr/bin/env python3
"""
Script de Backup Completo para TecnoCursosAI

Este script cria backups completos do sistema incluindo:
- Banco de dados MySQL
- Arquivos estáticos (uploads, videos, thumbnails)
- Configurações do sistema
- Logs da aplicação
"""

import os
import sys
import shutil
import subprocess
import datetime
import json
import zipfile
import argparse
from pathlib import Path
from typing import Optional

# Adicionar o diretório pai ao path para importar os módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.config import settings
except ImportError:
    print("⚠️  Configurações não encontradas. Usando valores padrão.")
    settings = None


class BackupManager:
    """Gerenciador de backups do sistema"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Diretórios do projeto
        self.project_root = Path(__file__).parent.parent
        self.app_dir = self.project_root / "app"
        self.static_dir = self.project_root / "app" / "static"
        self.logs_dir = self.project_root / "logs"
        
        # Timestamp para o backup
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"tecnocursos_backup_{self.timestamp}"
        self.backup_path = self.backup_dir / self.backup_name
        
    def create_backup_directory(self):
        """Criar diretório para o backup atual"""
        print(f"📁 Criando diretório de backup: {self.backup_path}")
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
    def backup_database(self) -> bool:
        """Fazer backup do banco de dados MySQL"""
        print("💾 Fazendo backup do banco de dados...")
        
        if not settings:
            print("⚠️  Configurações não disponíveis. Pulando backup do banco.")
            return False
            
        try:
            # Extrair informações de conexão
            db_url = settings.DATABASE_URL
            if not db_url or not db_url.startswith("mysql"):
                print("⚠️  URL do banco não configurada ou não é MySQL. Pulando backup.")
                return False
            
            # Parsear URL do banco (mysql://user:password@host:port/database)
            import urllib.parse
            parsed = urllib.parse.urlparse(db_url)
            
            username = parsed.username
            password = parsed.password
            hostname = parsed.hostname or "localhost"
            port = parsed.port or 3306
            database = parsed.path.lstrip('/')
            
            # Comando mysqldump
            dump_file = self.backup_path / f"database_{self.timestamp}.sql"
            
            cmd = [
                "mysqldump",
                f"--host={hostname}",
                f"--port={port}",
                f"--user={username}",
                f"--password={password}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--complete-insert",
                "--extended-insert",
                "--add-drop-table",
                "--add-locks",
                "--create-options",
                database
            ]
            
            print(f"   Executando: mysqldump para {database}")
            
            with open(dump_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                print(f"✅ Backup do banco criado: {dump_file}")
                
                # Criar arquivo com informações do backup
                info_file = self.backup_path / "database_info.json"
                db_info = {
                    "timestamp": self.timestamp,
                    "database": database,
                    "hostname": hostname,
                    "port": port,
                    "username": username,
                    "dump_file": dump_file.name,
                    "file_size": dump_file.stat().st_size if dump_file.exists() else 0
                }
                
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(db_info, f, indent=2, default=str)
                    
                return True
            else:
                print(f"❌ Erro no backup do banco: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no backup do banco de dados: {str(e)}")
            return False
    
    def backup_static_files(self) -> bool:
        """Fazer backup dos arquivos estáticos"""
        print("📎 Fazendo backup dos arquivos estáticos...")
        
        try:
            static_backup_dir = self.backup_path / "static"
            
            if self.static_dir.exists():
                print(f"   Copiando: {self.static_dir} -> {static_backup_dir}")
                shutil.copytree(self.static_dir, static_backup_dir)
                
                # Contar arquivos e calcular tamanho total
                total_files = 0
                total_size = 0
                
                for root, dirs, files in os.walk(static_backup_dir):
                    total_files += len(files)
                    for file in files:
                        file_path = Path(root) / file
                        total_size += file_path.stat().st_size
                
                print(f"✅ Arquivos estáticos copiados: {total_files} arquivos, {total_size / (1024*1024):.2f} MB")
                
                # Criar arquivo com informações dos arquivos
                files_info = {
                    "timestamp": self.timestamp,
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024*1024), 2),
                    "directories": []
                }
                
                for item in static_backup_dir.iterdir():
                    if item.is_dir():
                        files_info["directories"].append(item.name)
                
                info_file = self.backup_path / "static_info.json"
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(files_info, f, indent=2, default=str)
                
                return True
            else:
                print("⚠️  Diretório de arquivos estáticos não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro no backup dos arquivos estáticos: {str(e)}")
            return False
    
    def backup_logs(self) -> bool:
        """Fazer backup dos logs"""
        print("📋 Fazendo backup dos logs...")
        
        try:
            logs_backup_dir = self.backup_path / "logs"
            
            if self.logs_dir.exists():
                print(f"   Copiando: {self.logs_dir} -> {logs_backup_dir}")
                shutil.copytree(self.logs_dir, logs_backup_dir)
                print("✅ Logs copiados com sucesso")
                return True
            else:
                print("⚠️  Diretório de logs não encontrado")
                # Criar diretório vazio para manter estrutura
                logs_backup_dir.mkdir(exist_ok=True)
                return True
                
        except Exception as e:
            print(f"❌ Erro no backup dos logs: {str(e)}")
            return False
    
    def backup_configuration(self) -> bool:
        """Fazer backup das configurações"""
        print("⚙️  Fazendo backup das configurações...")
        
        try:
            config_backup_dir = self.backup_path / "config"
            config_backup_dir.mkdir(exist_ok=True)
            
            # Arquivos de configuração importantes
            config_files = [
                "env.example",
                "requirements.txt",
                "docker-compose.yml",
                "Dockerfile",
                "alembic.ini",
                "pytest.ini",
                "README.md",
                ".gitignore"
            ]
            
            copied_files = []
            for config_file in config_files:
                source_file = self.project_root / config_file
                if source_file.exists():
                    dest_file = config_backup_dir / config_file
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(config_file)
                    print(f"   📄 {config_file}")
            
            # Backup do diretório alembic (migrações)
            alembic_dir = self.project_root / "alembic"
            if alembic_dir.exists():
                alembic_backup_dir = config_backup_dir / "alembic"
                shutil.copytree(alembic_dir, alembic_backup_dir)
                print("   📁 alembic/")
            
            # Criar arquivo com informações das configurações
            config_info = {
                "timestamp": self.timestamp,
                "copied_files": copied_files,
                "has_alembic": alembic_dir.exists()
            }
            
            if settings:
                config_info.update({
                    "environment": getattr(settings, 'ENVIRONMENT', 'unknown'),
                    "debug": getattr(settings, 'DEBUG', False),
                    "port": getattr(settings, 'PORT', 8000)
                })
            
            info_file = config_backup_dir / "config_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(config_info, f, indent=2, default=str)
            
            print(f"✅ Configurações copiadas: {len(copied_files)} arquivos")
            return True
            
        except Exception as e:
            print(f"❌ Erro no backup das configurações: {str(e)}")
            return False
    
    def create_backup_manifest(self) -> bool:
        """Criar manifesto do backup"""
        print("📋 Criando manifesto do backup...")
        
        try:
            manifest = {
                "backup_info": {
                    "name": self.backup_name,
                    "timestamp": self.timestamp,
                    "created_at": datetime.datetime.now().isoformat(),
                    "version": "1.0",
                    "system": "TecnoCursosAI"
                },
                "components": {
                    "database": (self.backup_path / "database_info.json").exists(),
                    "static_files": (self.backup_path / "static_info.json").exists(),
                    "logs": (self.backup_path / "logs").exists(),
                    "configuration": (self.backup_path / "config").exists()
                },
                "restore_instructions": {
                    "database": "Use mysql < database_*.sql para restaurar o banco",
                    "static_files": "Copie o diretório static/ para app/static/",
                    "logs": "Copie o diretório logs/ para ./logs/",
                    "configuration": "Revise os arquivos em config/ antes de usar"
                }
            }
            
            # Calcular tamanho total do backup
            total_size = 0
            for root, dirs, files in os.walk(self.backup_path):
                for file in files:
                    file_path = Path(root) / file
                    total_size += file_path.stat().st_size
            
            manifest["backup_info"]["total_size_bytes"] = total_size
            manifest["backup_info"]["total_size_mb"] = round(total_size / (1024*1024), 2)
            
            manifest_file = self.backup_path / "MANIFEST.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, default=str)
            
            print(f"✅ Manifesto criado: {manifest_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar manifesto: {str(e)}")
            return False
    
    def compress_backup(self, compress_format: str = "zip") -> Optional[Path]:
        """Comprimir o backup"""
        print(f"🗜️  Comprimindo backup ({compress_format})...")
        
        try:
            if compress_format == "zip":
                archive_path = self.backup_dir / f"{self.backup_name}.zip"
                
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(self.backup_path):
                        for file in files:
                            file_path = Path(root) / file
                            arc_name = file_path.relative_to(self.backup_path)
                            zipf.write(file_path, arc_name)
                
                # Remover diretório não comprimido
                shutil.rmtree(self.backup_path)
                
                archive_size = archive_path.stat().st_size
                print(f"✅ Backup comprimido: {archive_path}")
                print(f"   Tamanho: {archive_size / (1024*1024):.2f} MB")
                
                return archive_path
            else:
                print(f"❌ Formato de compressão não suportado: {compress_format}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na compressão: {str(e)}")
            return None
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Limpar backups antigos"""
        print(f"🧹 Limpando backups com mais de {keep_days} dias...")
        
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob("tecnocursos_backup_*.zip"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    removed_count += 1
                    print(f"   🗑️  Removido: {backup_file.name}")
            
            if removed_count == 0:
                print("   ✅ Nenhum backup antigo para remover")
            else:
                print(f"   ✅ {removed_count} backups antigos removidos")
                
        except Exception as e:
            print(f"❌ Erro na limpeza de backups: {str(e)}")
    
    def create_full_backup(self, compress: bool = True, cleanup: bool = True, keep_days: int = 30) -> bool:
        """Criar backup completo do sistema"""
        print("🚀 Iniciando backup completo do TecnoCursosAI...")
        print(f"📅 Timestamp: {self.timestamp}")
        print("=" * 60)
        
        success = True
        
        try:
            # Criar diretório de backup
            self.create_backup_directory()
            
            # Fazer backup de cada componente
            components = [
                ("Banco de Dados", self.backup_database),
                ("Arquivos Estáticos", self.backup_static_files),
                ("Logs", self.backup_logs),
                ("Configurações", self.backup_configuration),
                ("Manifesto", self.create_backup_manifest)
            ]
            
            for component_name, backup_function in components:
                print(f"\n📦 {component_name}:")
                component_success = backup_function()
                success = success and component_success
            
            print("\n" + "=" * 60)
            
            if success:
                print("✅ Backup completo criado com sucesso!")
                
                # Comprimir se solicitado
                if compress:
                    archive_path = self.compress_backup()
                    if archive_path:
                        print(f"📦 Arquivo de backup: {archive_path}")
                
                # Limpar backups antigos se solicitado
                if cleanup:
                    self.cleanup_old_backups(keep_days)
                
                return True
            else:
                print("⚠️  Backup concluído com alguns erros")
                return False
                
        except Exception as e:
            print(f"❌ Erro crítico durante o backup: {str(e)}")
            return False


def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description="Script de Backup do TecnoCursosAI")
    
    parser.add_argument(
        "--backup-dir",
        default="backups",
        help="Diretório onde salvar os backups (padrão: backups)"
    )
    
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Não comprimir o backup"
    )
    
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Não limpar backups antigos"
    )
    
    parser.add_argument(
        "--keep-days",
        type=int,
        default=30,
        help="Dias para manter backups antigos (padrão: 30)"
    )
    
    args = parser.parse_args()
    
    # Criar gerenciador de backup
    backup_manager = BackupManager(args.backup_dir)
    
    # Executar backup
    success = backup_manager.create_full_backup(
        compress=not args.no_compress,
        cleanup=not args.no_cleanup,
        keep_days=args.keep_days
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 