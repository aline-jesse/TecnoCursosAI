"""
Sistema de Backup e Recovery - TecnoCursos AI
Backup automático de banco de dados, arquivos e configurações
"""

import os
import shutil
import sqlite3
import asyncio
import gzip
import json
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import schedule
import threading
from dataclasses import dataclass, asdict
import hashlib

from ..core.logging import get_logger
from ..core.settings import get_settings
from ..core.cache import cache_manager

logger = get_logger("backup")
settings = get_settings()

@dataclass
class BackupConfig:
    """Configuração de backup"""
    enabled: bool = True
    backup_dir: str = "./backups"
    retention_days: int = 30
    compression: bool = True
    
    # Tipos de backup
    database_backup: bool = True
    files_backup: bool = True
    config_backup: bool = True
    logs_backup: bool = False
    
    # Agendamento
    schedule_database: str = "daily"  # daily, weekly, hourly
    schedule_files: str = "daily"
    
    # Configurações específicas
    max_backup_size_gb: int = 10
    verify_backups: bool = True
    encrypt_backups: bool = False
    encryption_key: Optional[str] = None

class BackupManager:
    """Gerenciador de backups"""
    
    def __init__(self, config: BackupConfig = None):
        self.config = config or BackupConfig()
        self.backup_dir = Path(self.config.backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadados dos backups
        self.backup_registry = {}
        self.load_backup_registry()
        
        # Scheduler para backups automáticos
        self.scheduler_thread = None
        self.running = False
    
    def load_backup_registry(self):
        """Carrega registro de backups"""
        registry_file = self.backup_dir / "backup_registry.json"
        try:
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    self.backup_registry = json.load(f)
        except Exception as e:
            logger.error(f"Error loading backup registry: {e}")
            self.backup_registry = {}
    
    def save_backup_registry(self):
        """Salva registro de backups"""
        registry_file = self.backup_dir / "backup_registry.json"
        try:
            with open(registry_file, 'w') as f:
                json.dump(self.backup_registry, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving backup registry: {e}")
    
    async def create_database_backup(self) -> Dict[str, Any]:
        """Cria backup do banco de dados"""
        logger.info("Starting database backup")
        
        backup_info = {
            "type": "database",
            "timestamp": datetime.utcnow(),
            "status": "in_progress",
            "file_path": None,
            "file_size": 0,
            "checksum": None,
            "error": None
        }
        
        try:
            # Nome do arquivo de backup
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"database_backup_{timestamp}.sql"
            
            if self.config.compression:
                backup_filename += ".gz"
            
            backup_path = self.backup_dir / backup_filename
            
            # Fazer backup baseado no tipo de banco
            if settings.database.url.startswith("sqlite"):
                await self._backup_sqlite(backup_path)
            elif settings.database.url.startswith("postgresql"):
                await self._backup_postgresql(backup_path)
            elif settings.database.url.startswith("mysql"):
                await self._backup_mysql(backup_path)
            else:
                raise ValueError(f"Unsupported database type: {settings.database.url}")
            
            # Calcular checksum
            backup_info["checksum"] = await self._calculate_checksum(backup_path)
            backup_info["file_path"] = str(backup_path)
            backup_info["file_size"] = backup_path.stat().st_size
            backup_info["status"] = "completed"
            
            logger.info(f"Database backup completed: {backup_path}")
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
        
        # Registrar backup
        backup_id = f"db_{int(backup_info['timestamp'].timestamp())}"
        self.backup_registry[backup_id] = backup_info
        self.save_backup_registry()
        
        return backup_info
    
    async def _backup_sqlite(self, backup_path: Path):
        """Backup específico para SQLite"""
        db_path = settings.database.url.replace("sqlite:///", "")
        
        if self.config.compression:
            with gzip.open(backup_path, 'wt') as gz_file:
                # Fazer dump do banco
                conn = sqlite3.connect(db_path)
                for line in conn.iterdump():
                    gz_file.write(f"{line}\n")
                conn.close()
        else:
            with open(backup_path, 'w') as backup_file:
                conn = sqlite3.connect(db_path)
                for line in conn.iterdump():
                    backup_file.write(f"{line}\n")
                conn.close()
    
    async def _backup_postgresql(self, backup_path: Path):
        """Backup específico para PostgreSQL"""
        import subprocess
        
        # Extrair dados de conexão da URL
        # postgresql://user:password@host:port/database
        url_parts = settings.database.url.replace("postgresql://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        
        env = os.environ.copy()
        env["PGPASSWORD"] = user_pass[1] if len(user_pass) > 1 else ""
        
        cmd = [
            "pg_dump",
            "-h", host_db[0].split(":")[0],
            "-p", host_db[0].split(":")[1] if ":" in host_db[0] else "5432",
            "-U", user_pass[0],
            "-d", host_db[1],
            "--no-password"
        ]
        
        if self.config.compression:
            with gzip.open(backup_path, 'wt') as gz_file:
                process = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, env=env
                )
                if process.returncode != 0:
                    raise Exception(f"pg_dump failed: {process.stderr}")
                gz_file.write(process.stdout)
        else:
            with open(backup_path, 'w') as backup_file:
                process = subprocess.run(
                    cmd, stdout=backup_file, stderr=subprocess.PIPE,
                    text=True, env=env
                )
                if process.returncode != 0:
                    raise Exception(f"pg_dump failed: {process.stderr}")
    
    async def _backup_mysql(self, backup_path: Path):
        """Backup específico para MySQL"""
        import subprocess
        
        # Similar ao PostgreSQL, mas usando mysqldump
        # mysql://user:password@host:port/database
        url_parts = settings.database.url.replace("mysql://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        
        cmd = [
            "mysqldump",
            "-h", host_db[0].split(":")[0],
            "-P", host_db[0].split(":")[1] if ":" in host_db[0] else "3306",
            "-u", user_pass[0],
            f"-p{user_pass[1]}" if len(user_pass) > 1 else "",
            host_db[1]
        ]
        
        if self.config.compression:
            with gzip.open(backup_path, 'wt') as gz_file:
                process = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True
                )
                if process.returncode != 0:
                    raise Exception(f"mysqldump failed: {process.stderr}")
                gz_file.write(process.stdout)
        else:
            with open(backup_path, 'w') as backup_file:
                process = subprocess.run(
                    cmd, stdout=backup_file, stderr=subprocess.PIPE,
                    text=True
                )
                if process.returncode != 0:
                    raise Exception(f"mysqldump failed: {process.stderr}")
    
    async def create_files_backup(self) -> Dict[str, Any]:
        """Cria backup dos arquivos"""
        logger.info("Starting files backup")
        
        backup_info = {
            "type": "files",
            "timestamp": datetime.utcnow(),
            "status": "in_progress",
            "file_path": None,
            "file_size": 0,
            "checksum": None,
            "files_count": 0,
            "error": None
        }
        
        try:
            # Nome do arquivo de backup
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"files_backup_{timestamp}.tar.gz"
            backup_path = self.backup_dir / backup_filename
            
            # Diretórios para backup
            backup_dirs = [
                settings.files.upload_dir,
                settings.files.video_output_dir,
                settings.files.audio_output_dir
            ]
            
            files_count = 0
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for dir_path in backup_dirs:
                    dir_path = Path(dir_path)
                    if dir_path.exists():
                        for file_path in dir_path.rglob("*"):
                            if file_path.is_file():
                                # Adicionar arquivo ao backup
                                arcname = file_path.relative_to(dir_path.parent)
                                tar.add(file_path, arcname=arcname)
                                files_count += 1
                                
                                # Log progresso a cada 100 arquivos
                                if files_count % 100 == 0:
                                    logger.info(f"Backed up {files_count} files")
            
            backup_info["checksum"] = await self._calculate_checksum(backup_path)
            backup_info["file_path"] = str(backup_path)
            backup_info["file_size"] = backup_path.stat().st_size
            backup_info["files_count"] = files_count
            backup_info["status"] = "completed"
            
            logger.info(f"Files backup completed: {files_count} files, {backup_path}")
            
        except Exception as e:
            logger.error(f"Files backup failed: {e}")
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
        
        # Registrar backup
        backup_id = f"files_{int(backup_info['timestamp'].timestamp())}"
        self.backup_registry[backup_id] = backup_info
        self.save_backup_registry()
        
        return backup_info
    
    async def create_config_backup(self) -> Dict[str, Any]:
        """Cria backup das configurações"""
        logger.info("Starting config backup")
        
        backup_info = {
            "type": "config",
            "timestamp": datetime.utcnow(),
            "status": "in_progress",
            "file_path": None,
            "file_size": 0,
            "checksum": None,
            "error": None
        }
        
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"config_backup_{timestamp}.json"
            
            if self.config.compression:
                backup_filename += ".gz"
            
            backup_path = self.backup_dir / backup_filename
            
            # Coletar configurações (sem dados sensíveis)
            config_data = {
                "app_settings": settings.to_dict(),
                "backup_config": asdict(self.config),
                "backup_registry_summary": {
                    "total_backups": len(self.backup_registry),
                    "last_database_backup": self._get_last_backup("database"),
                    "last_files_backup": self._get_last_backup("files")
                },
                "system_info": {
                    "python_version": os.sys.version,
                    "platform": os.name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Salvar configurações
            if self.config.compression:
                with gzip.open(backup_path, 'wt') as gz_file:
                    json.dump(config_data, gz_file, indent=2, default=str)
            else:
                with open(backup_path, 'w') as config_file:
                    json.dump(config_data, config_file, indent=2, default=str)
            
            backup_info["checksum"] = await self._calculate_checksum(backup_path)
            backup_info["file_path"] = str(backup_path)
            backup_info["file_size"] = backup_path.stat().st_size
            backup_info["status"] = "completed"
            
            logger.info(f"Config backup completed: {backup_path}")
            
        except Exception as e:
            logger.error(f"Config backup failed: {e}")
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
        
        # Registrar backup
        backup_id = f"config_{int(backup_info['timestamp'].timestamp())}"
        self.backup_registry[backup_id] = backup_info
        self.save_backup_registry()
        
        return backup_info
    
    async def create_full_backup(self) -> Dict[str, Any]:
        """Cria backup completo (banco + arquivos + config)"""
        logger.info("Starting full backup")
        
        full_backup_info = {
            "type": "full",
            "timestamp": datetime.utcnow(),
            "status": "in_progress",
            "components": {},
            "total_size": 0,
            "error": None
        }
        
        try:
            # Backup do banco de dados
            if self.config.database_backup:
                db_backup = await self.create_database_backup()
                full_backup_info["components"]["database"] = db_backup
                if db_backup["status"] == "completed":
                    full_backup_info["total_size"] += db_backup["file_size"]
            
            # Backup dos arquivos
            if self.config.files_backup:
                files_backup = await self.create_files_backup()
                full_backup_info["components"]["files"] = files_backup
                if files_backup["status"] == "completed":
                    full_backup_info["total_size"] += files_backup["file_size"]
            
            # Backup das configurações
            if self.config.config_backup:
                config_backup = await self.create_config_backup()
                full_backup_info["components"]["config"] = config_backup
                if config_backup["status"] == "completed":
                    full_backup_info["total_size"] += config_backup["file_size"]
            
            # Verificar se todos os backups foram bem-sucedidos
            all_successful = all(
                component["status"] == "completed"
                for component in full_backup_info["components"].values()
            )
            
            full_backup_info["status"] = "completed" if all_successful else "partial"
            
            logger.info(f"Full backup {full_backup_info['status']}: {full_backup_info['total_size']} bytes")
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            full_backup_info["status"] = "failed"
            full_backup_info["error"] = str(e)
        
        # Registrar backup completo
        backup_id = f"full_{int(full_backup_info['timestamp'].timestamp())}"
        self.backup_registry[backup_id] = full_backup_info
        self.save_backup_registry()
        
        return full_backup_info
    
    async def restore_database_backup(self, backup_id: str) -> bool:
        """Restaura backup do banco de dados"""
        logger.info(f"Starting database restore from backup: {backup_id}")
        
        if backup_id not in self.backup_registry:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        backup_info = self.backup_registry[backup_id]
        
        if backup_info["type"] not in ["database", "full"]:
            logger.error(f"Invalid backup type for database restore: {backup_info['type']}")
            return False
        
        try:
            backup_path = Path(backup_info["file_path"])
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Verificar checksum
            current_checksum = await self._calculate_checksum(backup_path)
            if current_checksum != backup_info["checksum"]:
                logger.error("Backup file integrity check failed")
                return False
            
            # Restaurar baseado no tipo de banco
            if settings.database.url.startswith("sqlite"):
                await self._restore_sqlite(backup_path)
            elif settings.database.url.startswith("postgresql"):
                await self._restore_postgresql(backup_path)
            elif settings.database.url.startswith("mysql"):
                await self._restore_mysql(backup_path)
            else:
                raise ValueError(f"Unsupported database type: {settings.database.url}")
            
            logger.info("Database restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    async def _restore_sqlite(self, backup_path: Path):
        """Restaura backup específico do SQLite"""
        db_path = settings.database.url.replace("sqlite:///", "")
        
        # Fazer backup do banco atual
        current_db = Path(db_path)
        if current_db.exists():
            backup_current = current_db.with_suffix(".bak")
            shutil.copy2(current_db, backup_current)
        
        try:
            # Restaurar banco
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Limpar banco atual
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("BEGIN TRANSACTION")
            
            # Obter todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            
            # Restaurar do backup
            if backup_path.suffix == ".gz":
                with gzip.open(backup_path, 'rt') as backup_file:
                    sql_script = backup_file.read()
            else:
                with open(backup_path, 'r') as backup_file:
                    sql_script = backup_file.read()
            
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Restaurar backup do banco atual se houve erro
            if 'backup_current' in locals() and backup_current.exists():
                shutil.copy2(backup_current, current_db)
            raise e
    
    async def cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        logger.info("Starting backup cleanup")
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
        removed_count = 0
        total_size_removed = 0
        
        backups_to_remove = []
        
        for backup_id, backup_info in self.backup_registry.items():
            backup_date = datetime.fromisoformat(backup_info["timestamp"].replace("Z", "+00:00"))
            
            if backup_date < cutoff_date:
                backups_to_remove.append((backup_id, backup_info))
        
        for backup_id, backup_info in backups_to_remove:
            try:
                # Remover arquivo de backup
                if "file_path" in backup_info and backup_info["file_path"]:
                    backup_path = Path(backup_info["file_path"])
                    if backup_path.exists():
                        file_size = backup_path.stat().st_size
                        backup_path.unlink()
                        total_size_removed += file_size
                
                # Remover do registro
                del self.backup_registry[backup_id]
                removed_count += 1
                
            except Exception as e:
                logger.error(f"Error removing backup {backup_id}: {e}")
        
        if removed_count > 0:
            self.save_backup_registry()
            logger.info(f"Removed {removed_count} old backups, freed {total_size_removed / (1024*1024):.2f} MB")
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum SHA256 de um arquivo"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _get_last_backup(self, backup_type: str) -> Optional[str]:
        """Obtém timestamp do último backup de um tipo específico"""
        last_backup = None
        last_timestamp = None
        
        for backup_id, backup_info in self.backup_registry.items():
            if backup_info["type"] == backup_type and backup_info["status"] == "completed":
                timestamp = datetime.fromisoformat(backup_info["timestamp"].replace("Z", "+00:00"))
                if last_timestamp is None or timestamp > last_timestamp:
                    last_timestamp = timestamp
                    last_backup = backup_info["timestamp"]
        
        return last_backup
    
    def start_scheduler(self):
        """Inicia agendador de backups automáticos"""
        if self.running:
            return
        
        self.running = True
        
        # Configurar agendamentos
        if self.config.schedule_database == "daily":
            schedule.every().day.at("02:00").do(self._scheduled_database_backup)
        elif self.config.schedule_database == "weekly":
            schedule.every().sunday.at("02:00").do(self._scheduled_database_backup)
        elif self.config.schedule_database == "hourly":
            schedule.every().hour.do(self._scheduled_database_backup)
        
        if self.config.schedule_files == "daily":
            schedule.every().day.at("03:00").do(self._scheduled_files_backup)
        elif self.config.schedule_files == "weekly":
            schedule.every().sunday.at("03:00").do(self._scheduled_files_backup)
        
        # Cleanup diário
        schedule.every().day.at("04:00").do(self._scheduled_cleanup)
        
        # Thread para executar agendamentos
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                asyncio.sleep(60)  # Verificar a cada minuto
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Backup scheduler started")
    
    def stop_scheduler(self):
        """Para agendador de backups"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Backup scheduler stopped")
    
    def _scheduled_database_backup(self):
        """Backup agendado do banco de dados"""
        asyncio.create_task(self.create_database_backup())
    
    def _scheduled_files_backup(self):
        """Backup agendado dos arquivos"""
        asyncio.create_task(self.create_files_backup())
    
    def _scheduled_cleanup(self):
        """Cleanup agendado"""
        asyncio.create_task(self.cleanup_old_backups())
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Retorna status dos backups"""
        total_backups = len(self.backup_registry)
        successful_backups = sum(
            1 for backup in self.backup_registry.values()
            if backup["status"] == "completed"
        )
        
        total_size = sum(
            backup.get("file_size", 0)
            for backup in self.backup_registry.values()
            if backup["status"] == "completed"
        )
        
        return {
            "enabled": self.config.enabled,
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "success_rate": successful_backups / total_backups if total_backups > 0 else 0,
            "total_size_mb": total_size / (1024 * 1024),
            "last_database_backup": self._get_last_backup("database"),
            "last_files_backup": self._get_last_backup("files"),
            "last_config_backup": self._get_last_backup("config"),
            "retention_days": self.config.retention_days,
            "scheduler_running": self.running
        }

# Instância global do gerenciador de backup
backup_manager = BackupManager()

# Funções de conveniência
async def create_database_backup():
    """Cria backup do banco de dados"""
    return await backup_manager.create_database_backup()

async def create_files_backup():
    """Cria backup dos arquivos"""
    return await backup_manager.create_files_backup()

async def create_full_backup():
    """Cria backup completo"""
    return await backup_manager.create_full_backup()

async def restore_database(backup_id: str):
    """Restaura backup do banco de dados"""
    return await backup_manager.restore_database_backup(backup_id)

def start_backup_scheduler():
    """Inicia agendador de backups"""
    backup_manager.start_scheduler()

def stop_backup_scheduler():
    """Para agendador de backups"""
    backup_manager.stop_scheduler()

def get_backup_status():
    """Retorna status dos backups"""
    return backup_manager.get_backup_status()
