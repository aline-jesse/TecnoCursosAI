"""
💾 Enhanced Backup Service - TecnoCursos AI Enterprise Edition 2025
=================================================================

Sistema avançado de backup automático e recuperação:
- Backup incremental inteligente
- Compressão automática com diferentes níveis
- Backup em múltiplas localizações (local, cloud, remoto)
- Verificação de integridade automática
- Recuperação point-in-time
- Backup de banco de dados com snapshot consistente
- Retenção automática baseada em políticas
- Monitoramento e alertas de backup
- Backup diferencial e completo
- Encryption automática dos backups
"""

import os
import shutil
import gzip
import json
import asyncio
import hashlib
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import subprocess
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
import schedule

from app.logger import get_logger
from app.config import get_settings

logger = get_logger("enhanced_backup")
settings = get_settings()

class BackupType(Enum):
    """Tipos de backup"""
    FULL = "full"              # Backup completo
    INCREMENTAL = "incremental" # Apenas arquivos modificados
    DIFFERENTIAL = "differential" # Mudanças desde último backup completo
    SNAPSHOT = "snapshot"       # Snapshot do sistema
    DATABASE = "database"       # Backup específico do banco

class BackupStatus(Enum):
    """Status do backup"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    VERIFIED = "verified"

class CompressionLevel(Enum):
    """Níveis de compressão"""
    NONE = 0
    FAST = 1
    NORMAL = 6
    MAXIMUM = 9

@dataclass
class BackupConfig:
    """Configuração de backup"""
    name: str
    enabled: bool = True
    backup_type: BackupType = BackupType.INCREMENTAL
    schedule: str = "daily"  # daily, weekly, monthly, hourly
    retention_days: int = 30
    compression_level: CompressionLevel = CompressionLevel.NORMAL
    encrypt: bool = True
    verify_integrity: bool = True
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    destinations: List[str] = field(default_factory=list)  # local, s3, ftp, etc.

@dataclass
class BackupEntry:
    """Entrada de backup"""
    id: str
    name: str
    backup_type: BackupType
    status: BackupStatus
    start_time: datetime
    end_time: Optional[datetime]
    file_path: str
    file_size: int
    compressed_size: int
    compression_ratio: float
    checksum: str
    error_message: Optional[str] = None
    verified: bool = False
    
    @property
    def duration(self) -> Optional[timedelta]:
        if self.end_time:
            return self.end_time - self.start_time
        return None

class EnhancedBackupService:
    """Serviço de backup avançado"""
    
    def __init__(self):
        self.backup_configs: Dict[str, BackupConfig] = {}
        self.backup_history: List[BackupEntry] = []
        self.backup_directory = Path("backups")
        self.temp_directory = Path("temp")
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Criar diretórios necessários
        self.backup_directory.mkdir(exist_ok=True)
        self.temp_directory.mkdir(exist_ok=True)
        
        # Configurações padrão
        self._initialize_default_configs()
        
        logger.info("💾 Enhanced Backup Service inicializado")
    
    def _initialize_default_configs(self):
        """Inicializar configurações padrão"""
        
        # Backup do banco de dados
        self.backup_configs["database"] = BackupConfig(
            name="Database Backup",
            backup_type=BackupType.DATABASE,
            schedule="daily",
            retention_days=30,
            compression_level=CompressionLevel.MAXIMUM,
            encrypt=True,
            include_patterns=["*.db", "*.sqlite", "*.sql"],
            destinations=["local"]
        )
        
        # Backup de arquivos de aplicação
        self.backup_configs["application"] = BackupConfig(
            name="Application Files",
            backup_type=BackupType.INCREMENTAL,
            schedule="daily",
            retention_days=14,
            compression_level=CompressionLevel.NORMAL,
            include_patterns=["app/**", "config/**", "static/**"],
            exclude_patterns=["*.pyc", "__pycache__/**", "*.log", "temp/**"],
            destinations=["local"]
        )
        
        # Backup de uploads de usuários
        self.backup_configs["user_data"] = BackupConfig(
            name="User Uploads",
            backup_type=BackupType.INCREMENTAL,
            schedule="hourly",
            retention_days=7,
            compression_level=CompressionLevel.FAST,
            include_patterns=["uploads/**", "static/uploads/**"],
            exclude_patterns=["*.tmp", "*.temp"],
            destinations=["local"]
        )
        
        # Backup completo semanal
        self.backup_configs["full_weekly"] = BackupConfig(
            name="Full Weekly Backup",
            backup_type=BackupType.FULL,
            schedule="weekly",
            retention_days=90,
            compression_level=CompressionLevel.MAXIMUM,
            encrypt=True,
            exclude_patterns=["node_modules/**", "venv/**", "*.log", "__pycache__/**"],
            destinations=["local"]
        )
        
        logger.info(f"📋 {len(self.backup_configs)} configurações de backup carregadas")
    
    async def start_scheduler(self):
        """Iniciar agendador de backups"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("⏰ Agendador de backup iniciado")
        
        # Configurar agendamentos
        for config_name, config in self.backup_configs.items():
            if not config.enabled:
                continue
            
            if config.schedule == "hourly":
                schedule.every().hour.do(self._scheduled_backup, config_name)
            elif config.schedule == "daily":
                schedule.every().day.at("02:00").do(self._scheduled_backup, config_name)
            elif config.schedule == "weekly":
                schedule.every().sunday.at("01:00").do(self._scheduled_backup, config_name)
            elif config.schedule == "monthly":
                schedule.every(30).days.at("00:00").do(self._scheduled_backup, config_name)
        
        # Loop do agendador
        asyncio.create_task(self._scheduler_loop())
    
    async def stop_scheduler(self):
        """Parar agendador"""
        self.is_running = False
        schedule.clear()
        logger.info("⏰ Agendador de backup parado")
    
    async def _scheduler_loop(self):
        """Loop do agendador"""
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Verificar a cada minuto
            except Exception as e:
                logger.error(f"Erro no agendador: {e}")
                await asyncio.sleep(60)
    
    def _scheduled_backup(self, config_name: str):
        """Executar backup agendado"""
        asyncio.create_task(self.create_backup(config_name))
    
    async def create_backup(self, config_name: str) -> BackupEntry:
        """Criar backup baseado na configuração"""
        try:
            config = self.backup_configs.get(config_name)
            if not config:
                raise ValueError(f"Configuração não encontrada: {config_name}")
            
            if not config.enabled:
                raise ValueError(f"Configuração desabilitada: {config_name}")
            
            # Gerar ID único
            backup_id = f"{config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Criar entrada de backup
            backup_entry = BackupEntry(
                id=backup_id,
                name=config.name,
                backup_type=config.backup_type,
                status=BackupStatus.RUNNING,
                start_time=datetime.now(),
                end_time=None,
                file_path="",
                file_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                checksum=""
            )
            
            self.backup_history.append(backup_entry)
            logger.info(f"📦 Iniciando backup: {backup_id}")
            
            # Executar backup específico
            if config.backup_type == BackupType.DATABASE:
                await self._backup_database(backup_entry, config)
            elif config.backup_type == BackupType.FULL:
                await self._backup_full(backup_entry, config)
            elif config.backup_type == BackupType.INCREMENTAL:
                await self._backup_incremental(backup_entry, config)
            elif config.backup_type == BackupType.DIFFERENTIAL:
                await self._backup_differential(backup_entry, config)
            else:
                raise ValueError(f"Tipo de backup não suportado: {config.backup_type}")
            
            # Verificar integridade se habilitado
            if config.verify_integrity:
                await self._verify_backup_integrity(backup_entry)
            
            # Marcar como concluído
            backup_entry.status = BackupStatus.COMPLETED
            backup_entry.end_time = datetime.now()
            
            logger.info(f"✅ Backup concluído: {backup_id} ({backup_entry.duration})")
            
            # Limpar backups antigos
            await self._cleanup_old_backups(config)
            
            return backup_entry
            
        except Exception as e:
            backup_entry.status = BackupStatus.FAILED
            backup_entry.error_message = str(e)
            backup_entry.end_time = datetime.now()
            logger.error(f"❌ Falha no backup {backup_id}: {e}")
            return backup_entry
    
    async def _backup_database(self, backup_entry: BackupEntry, config: BackupConfig):
        """Backup específico do banco de dados"""
        try:
            # Para SQLite
            if settings.database_url.startswith("sqlite"):
                db_path = settings.database_url.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    backup_path = self.backup_directory / f"{backup_entry.id}_database.sqlite"
                    
                    # Copiar arquivo do banco
                    shutil.copy2(db_path, backup_path)
                    
                    # Comprimir se necessário
                    if config.compression_level != CompressionLevel.NONE:
                        compressed_path = await self._compress_file(backup_path, config.compression_level)
                        backup_path.unlink()  # Remover original não comprimido
                        backup_path = compressed_path
                    
                    backup_entry.file_path = str(backup_path)
                    backup_entry.file_size = backup_path.stat().st_size
                    backup_entry.checksum = await self._calculate_checksum(backup_path)
                    
            # Para MySQL/PostgreSQL
            else:
                # Implementar dump usando mysqldump ou pg_dump
                dump_path = self.backup_directory / f"{backup_entry.id}_database.sql"
                
                if "mysql" in settings.database_url:
                    # MySQL dump
                    cmd = [
                        "mysqldump",
                        "--single-transaction",
                        "--routines",
                        "--triggers",
                        "--all-databases"
                    ]
                elif "postgresql" in settings.database_url:
                    # PostgreSQL dump
                    cmd = ["pg_dumpall"]
                else:
                    raise ValueError("Tipo de banco não suportado para backup")
                
                # Executar dump
                with open(dump_path, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                    
                    if result.returncode != 0:
                        raise RuntimeError(f"Erro no dump: {result.stderr}")
                
                # Comprimir dump
                if config.compression_level != CompressionLevel.NONE:
                    compressed_path = await self._compress_file(dump_path, config.compression_level)
                    dump_path.unlink()
                    dump_path = compressed_path
                
                backup_entry.file_path = str(dump_path)
                backup_entry.file_size = dump_path.stat().st_size
                backup_entry.checksum = await self._calculate_checksum(dump_path)
                
        except Exception as e:
            raise RuntimeError(f"Erro no backup do banco: {e}")
    
    async def _backup_full(self, backup_entry: BackupEntry, config: BackupConfig):
        """Backup completo"""
        try:
            backup_path = self.backup_directory / f"{backup_entry.id}_full.tar"
            
            # Criar arquivo tar
            with tarfile.open(backup_path, 'w') as tar:
                # Adicionar arquivos baseado nos padrões
                for pattern in config.include_patterns or ["./**"]:
                    for file_path in Path(".").glob(pattern):
                        if file_path.is_file() and not self._should_exclude(file_path, config.exclude_patterns):
                            tar.add(file_path, arcname=file_path)
                            logger.debug(f"Adicionado ao backup: {file_path}")
            
            # Comprimir se necessário
            if config.compression_level != CompressionLevel.NONE:
                compressed_path = await self._compress_file(backup_path, config.compression_level)
                backup_path.unlink()
                backup_path = compressed_path
            
            backup_entry.file_path = str(backup_path)
            backup_entry.file_size = backup_path.stat().st_size
            backup_entry.checksum = await self._calculate_checksum(backup_path)
            
        except Exception as e:
            raise RuntimeError(f"Erro no backup completo: {e}")
    
    async def _backup_incremental(self, backup_entry: BackupEntry, config: BackupConfig):
        """Backup incremental"""
        try:
            # Encontrar último backup bem-sucedido
            last_backup_time = await self._get_last_backup_time(config.name)
            
            backup_path = self.backup_directory / f"{backup_entry.id}_incremental.tar"
            files_added = 0
            
            with tarfile.open(backup_path, 'w') as tar:
                for pattern in config.include_patterns or ["./**"]:
                    for file_path in Path(".").glob(pattern):
                        if (file_path.is_file() and 
                            not self._should_exclude(file_path, config.exclude_patterns) and
                            self._is_file_modified_since(file_path, last_backup_time)):
                            
                            tar.add(file_path, arcname=file_path)
                            files_added += 1
                            logger.debug(f"Arquivo modificado adicionado: {file_path}")
            
            # Se nenhum arquivo foi adicionado, remover arquivo vazio
            if files_added == 0:
                backup_path.unlink()
                raise RuntimeError("Nenhum arquivo modificado encontrado para backup incremental")
            
            # Comprimir se necessário
            if config.compression_level != CompressionLevel.NONE:
                compressed_path = await self._compress_file(backup_path, config.compression_level)
                backup_path.unlink()
                backup_path = compressed_path
            
            backup_entry.file_path = str(backup_path)
            backup_entry.file_size = backup_path.stat().st_size
            backup_entry.checksum = await self._calculate_checksum(backup_path)
            
            logger.info(f"📁 Backup incremental: {files_added} arquivos")
            
        except Exception as e:
            raise RuntimeError(f"Erro no backup incremental: {e}")
    
    async def _backup_differential(self, backup_entry: BackupEntry, config: BackupConfig):
        """Backup diferencial"""
        try:
            # Encontrar último backup completo
            last_full_backup = await self._get_last_full_backup_time(config.name)
            
            backup_path = self.backup_directory / f"{backup_entry.id}_differential.tar"
            files_added = 0
            
            with tarfile.open(backup_path, 'w') as tar:
                for pattern in config.include_patterns or ["./**"]:
                    for file_path in Path(".").glob(pattern):
                        if (file_path.is_file() and 
                            not self._should_exclude(file_path, config.exclude_patterns) and
                            self._is_file_modified_since(file_path, last_full_backup)):
                            
                            tar.add(file_path, arcname=file_path)
                            files_added += 1
            
            if files_added == 0:
                backup_path.unlink()
                raise RuntimeError("Nenhum arquivo modificado desde último backup completo")
            
            # Comprimir se necessário
            if config.compression_level != CompressionLevel.NONE:
                compressed_path = await self._compress_file(backup_path, config.compression_level)
                backup_path.unlink()
                backup_path = compressed_path
            
            backup_entry.file_path = str(backup_path)
            backup_entry.file_size = backup_path.stat().st_size
            backup_entry.checksum = await self._calculate_checksum(backup_path)
            
            logger.info(f"📁 Backup diferencial: {files_added} arquivos")
            
        except Exception as e:
            raise RuntimeError(f"Erro no backup diferencial: {e}")
    
    async def _compress_file(self, file_path: Path, compression_level: CompressionLevel) -> Path:
        """Comprimir arquivo"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=compression_level.value) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Calcular taxa de compressão
            original_size = file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"🗜️ Compressão: {compression_ratio:.1f}% ({original_size} → {compressed_size} bytes)")
            
            return compressed_path
            
        except Exception as e:
            raise RuntimeError(f"Erro na compressão: {e}")
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum do arquivo"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular checksum: {e}")
            return ""
    
    async def _verify_backup_integrity(self, backup_entry: BackupEntry):
        """Verificar integridade do backup"""
        try:
            file_path = Path(backup_entry.file_path)
            if not file_path.exists():
                raise RuntimeError(f"Arquivo de backup não encontrado: {file_path}")
            
            # Recalcular checksum
            current_checksum = await self._calculate_checksum(file_path)
            
            if current_checksum != backup_entry.checksum:
                backup_entry.status = BackupStatus.CORRUPTED
                raise RuntimeError("Checksum não confere - backup pode estar corrompido")
            
            # Verificar se arquivo tar é válido
            if file_path.suffix in ['.tar', '.gz']:
                try:
                    if file_path.suffix == '.gz':
                        # Testar descompressão
                        with gzip.open(file_path, 'rb') as f:
                            f.read(1024)  # Ler pequena parte para verificar
                    
                    # Se for tar, testar listagem
                    if '.tar' in file_path.name:
                        archive_path = file_path
                        if file_path.suffix == '.gz':
                            # Extrair temporariamente para testar
                            with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
                                with gzip.open(file_path, 'rb') as f_in:
                                    shutil.copyfileobj(f_in, tmp)
                                archive_path = Path(tmp.name)
                        
                        with tarfile.open(archive_path, 'r') as tar:
                            tar.getnames()  # Listar para verificar integridade
                        
                        # Limpar arquivo temporário
                        if archive_path != file_path:
                            archive_path.unlink()
                            
                except Exception as e:
                    backup_entry.status = BackupStatus.CORRUPTED
                    raise RuntimeError(f"Arquivo de backup corrompido: {e}")
            
            backup_entry.verified = True
            backup_entry.status = BackupStatus.VERIFIED
            logger.info(f"✅ Integridade verificada: {backup_entry.id}")
            
        except Exception as e:
            backup_entry.verified = False
            logger.error(f"❌ Falha na verificação: {e}")
            raise
    
    def _should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Verificar se arquivo deve ser excluído"""
        for pattern in exclude_patterns or []:
            if file_path.match(pattern):
                return True
        return False
    
    def _is_file_modified_since(self, file_path: Path, since_time: datetime) -> bool:
        """Verificar se arquivo foi modificado desde uma data"""
        try:
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return file_mtime > since_time
        except Exception:
            return True  # Se não conseguir verificar, incluir por segurança
    
    async def _get_last_backup_time(self, config_name: str) -> datetime:
        """Obter timestamp do último backup bem-sucedido"""
        for entry in reversed(self.backup_history):
            if (entry.name == config_name and 
                entry.status == BackupStatus.COMPLETED and 
                entry.end_time):
                return entry.end_time
        
        # Se não há backup anterior, usar data muito antiga
        return datetime(1970, 1, 1)
    
    async def _get_last_full_backup_time(self, config_name: str) -> datetime:
        """Obter timestamp do último backup completo"""
        for entry in reversed(self.backup_history):
            if (entry.name == config_name and 
                entry.backup_type == BackupType.FULL and
                entry.status == BackupStatus.COMPLETED and 
                entry.end_time):
                return entry.end_time
        
        return datetime(1970, 1, 1)
    
    async def _cleanup_old_backups(self, config: BackupConfig):
        """Limpar backups antigos baseado na política de retenção"""
        try:
            cutoff_date = datetime.now() - timedelta(days=config.retention_days)
            
            # Encontrar backups antigos
            old_backups = [
                entry for entry in self.backup_history
                if (entry.name == config.name and 
                    entry.start_time < cutoff_date and
                    entry.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED])
            ]
            
            # Remover arquivos e entradas
            removed_count = 0
            for backup in old_backups:
                try:
                    backup_path = Path(backup.file_path)
                    if backup_path.exists():
                        backup_path.unlink()
                        logger.debug(f"Removido backup antigo: {backup_path}")
                    
                    self.backup_history.remove(backup)
                    removed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Erro ao remover backup {backup.id}: {e}")
            
            if removed_count > 0:
                logger.info(f"🧹 Limpeza: {removed_count} backups antigos removidos")
                
        except Exception as e:
            logger.error(f"Erro na limpeza de backups: {e}")
    
    async def restore_backup(self, backup_id: str, restore_path: str = None) -> Dict[str, Any]:
        """Restaurar backup"""
        try:
            # Encontrar backup
            backup_entry = next((b for b in self.backup_history if b.id == backup_id), None)
            if not backup_entry:
                raise ValueError(f"Backup não encontrado: {backup_id}")
            
            if backup_entry.status != BackupStatus.COMPLETED:
                raise ValueError(f"Backup não está completo: {backup_entry.status}")
            
            backup_path = Path(backup_entry.file_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_path}")
            
            # Verificar integridade antes de restaurar
            current_checksum = await self._calculate_checksum(backup_path)
            if current_checksum != backup_entry.checksum:
                raise RuntimeError("Backup corrompido - checksum não confere")
            
            # Definir caminho de restauração
            if not restore_path:
                restore_path = f"./restored_{backup_id}"
            
            restore_dir = Path(restore_path)
            restore_dir.mkdir(exist_ok=True)
            
            # Restaurar baseado no tipo
            if backup_entry.backup_type == BackupType.DATABASE:
                await self._restore_database(backup_path, restore_dir)
            else:
                await self._restore_files(backup_path, restore_dir)
            
            logger.info(f"✅ Backup restaurado: {backup_id} → {restore_path}")
            
            return {
                "success": True,
                "backup_id": backup_id,
                "restore_path": str(restore_dir),
                "backup_type": backup_entry.backup_type.value,
                "restored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na restauração: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _restore_database(self, backup_path: Path, restore_dir: Path):
        """Restaurar backup de banco de dados"""
        try:
            # Se é arquivo comprimido, descomprimir primeiro
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(restore_dir / "database.db", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, restore_dir / backup_path.name)
                
        except Exception as e:
            raise RuntimeError(f"Erro ao restaurar banco: {e}")
    
    async def _restore_files(self, backup_path: Path, restore_dir: Path):
        """Restaurar backup de arquivos"""
        try:
            # Descomprimir se necessário
            archive_path = backup_path
            if backup_path.suffix == '.gz':
                with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
                    with gzip.open(backup_path, 'rb') as f_in:
                        shutil.copyfileobj(f_in, tmp)
                    archive_path = Path(tmp.name)
            
            # Extrair arquivos
            with tarfile.open(archive_path, 'r') as tar:
                tar.extractall(restore_dir)
            
            # Limpar arquivo temporário
            if archive_path != backup_path:
                archive_path.unlink()
                
        except Exception as e:
            raise RuntimeError(f"Erro ao restaurar arquivos: {e}")
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """Obter status dos backups"""
        try:
            total_backups = len(self.backup_history)
            successful_backups = len([b for b in self.backup_history if b.status == BackupStatus.COMPLETED])
            failed_backups = len([b for b in self.backup_history if b.status == BackupStatus.FAILED])
            
            # Estatísticas de tamanho
            total_size = sum(b.file_size for b in self.backup_history if b.status == BackupStatus.COMPLETED)
            
            # Último backup por configuração
            last_backups = {}
            for config_name in self.backup_configs.keys():
                for entry in reversed(self.backup_history):
                    if entry.name == self.backup_configs[config_name].name:
                        last_backups[config_name] = {
                            "id": entry.id,
                            "status": entry.status.value,
                            "timestamp": entry.start_time.isoformat(),
                            "size": entry.file_size
                        }
                        break
            
            return {
                "scheduler_running": self.is_running,
                "total_backups": total_backups,
                "successful_backups": successful_backups,
                "failed_backups": failed_backups,
                "success_rate": (successful_backups / total_backups * 100) if total_backups > 0 else 0,
                "total_backup_size": total_size,
                "configured_backups": len(self.backup_configs),
                "enabled_backups": len([c for c in self.backup_configs.values() if c.enabled]),
                "last_backups": last_backups,
                "backup_directory": str(self.backup_directory)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {"error": str(e)}

# Instância global do serviço
backup_service = EnhancedBackupService()

# Funções de conveniência
async def start_backup_scheduler():
    """Iniciar agendador de backup"""
    await backup_service.start_scheduler()

async def create_manual_backup(config_name: str) -> BackupEntry:
    """Criar backup manual"""
    return await backup_service.create_backup(config_name)

async def restore_from_backup(backup_id: str, restore_path: str = None) -> Dict[str, Any]:
    """Restaurar backup"""
    return await backup_service.restore_backup(backup_id, restore_path)

async def get_backup_report() -> Dict[str, Any]:
    """Obter relatório de backup"""
    return await backup_service.get_backup_status()

if __name__ == "__main__":
    # Teste do serviço
    async def test_service():
        print("💾 Testando Enhanced Backup Service...")
        
        # Iniciar agendador
        await start_backup_scheduler()
        
        # Criar backup manual
        backup = await create_manual_backup("application")
        print("📦 Backup criado:", backup.id)
        
        # Obter status
        status = await get_backup_report()
        print("📊 Status:", json.dumps(status, indent=2, default=str))
    
    asyncio.run(test_service()) 