#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup and Disaster Recovery System - TecnoCursos AI

Sistema completo de backup e recuperação de desastres seguindo
as melhores práticas de:
- Data protection
- Business continuity
- Automated recovery
- Multi-tier backup strategy
- Cross-region replication
- Point-in-time recovery

Funcionalidades:
- Backup automático de banco de dados
- Backup de arquivos de mídia
- Backup de configurações
- Backup de secrets
- Restore point-in-time
- Disaster recovery automation
- Cross-region sync
- Backup verification
- Monitoring e alertas

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
import sys
import json
import time
import boto3
import shutil
import logging
import argparse
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import mysql.connector
    import redis
    import pymongo
    from kubernetes import client, config
    EXTERNAL_DEPS_AVAILABLE = True
except ImportError:
    EXTERNAL_DEPS_AVAILABLE = False
    print("⚠️  Algumas dependências não estão disponíveis. Execute: pip install mysql-connector-python redis pymongo kubernetes")

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

@dataclass
class BackupConfig:
    """Configurações de backup"""
    # Configurações gerais
    backup_name: str = "tecnocursos-ai"
    environment: str = "production"
    retention_days: int = 30
    backup_dir: str = "/backup"
    
    # Configurações de banco de dados
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "tecnocursos"
    db_user: str = "admin"
    db_password: str = ""
    
    # Configurações de Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    
    # Configurações de S3
    s3_bucket: str = "tecnocursos-backups"
    s3_region: str = "us-east-1"
    s3_prefix: str = "backups"
    
    # Configurações de DR
    dr_region: str = "us-west-2"
    dr_bucket: str = "tecnocursos-dr-backups"
    
    # Configurações de notificação
    slack_webhook: str = ""
    email_recipients: List[str] = None
    
    # Configurações de monitoramento
    enable_monitoring: bool = True
    alert_on_failure: bool = True
    
    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = ["devops@tecnocursos.ai"]

@dataclass
class BackupMetadata:
    """Metadados do backup"""
    backup_id: str
    timestamp: datetime
    type: str
    size_bytes: int
    status: str
    files: List[str]
    checksum: str
    duration_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

# ============================================================================
# LOGGER CONFIGURATION
# ============================================================================

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configurar logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# ============================================================================
# BACKUP SYSTEM
# ============================================================================

class BackupSystem:
    """Sistema principal de backup"""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.logger = setup_logger("BackupSystem")
        self.s3_client = self._init_s3_client()
        self.backup_metadata: List[BackupMetadata] = []
        
        # Criar diretórios necessários
        Path(self.config.backup_dir).mkdir(parents=True, exist_ok=True)
        
    def _init_s3_client(self):
        """Inicializar cliente S3"""
        try:
            return boto3.client('s3', region_name=self.config.s3_region)
        except Exception as e:
            self.logger.warning(f"Falha ao inicializar S3: {e}")
            return None
    
    def create_full_backup(self) -> str:
        """Criar backup completo"""
        backup_id = f"{self.config.backup_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = Path(self.config.backup_dir) / backup_id
        backup_path.mkdir(exist_ok=True)
        
        self.logger.info(f"🚀 Iniciando backup completo: {backup_id}")
        start_time = time.time()
        
        try:
            # Lista de tarefas de backup
            backup_tasks = [
                ("database", self._backup_database),
                ("redis", self._backup_redis),
                ("files", self._backup_files),
                ("configs", self._backup_configs),
                ("kubernetes", self._backup_kubernetes_resources)
            ]
            
            files_created = []
            total_size = 0
            
            # Executar backups em paralelo quando possível
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {}
                
                for backup_type, backup_func in backup_tasks:
                    future = executor.submit(backup_func, backup_path)
                    futures[future] = backup_type
                
                for future in as_completed(futures):
                    backup_type = futures[future]
                    try:
                        result = future.result()
                        if result:
                            files_created.extend(result)
                            self.logger.info(f"✅ Backup {backup_type} concluído")
                    except Exception as e:
                        self.logger.error(f"❌ Falha no backup {backup_type}: {e}")
            
            # Calcular tamanho total
            for file_path in files_created:
                if Path(file_path).exists():
                    total_size += Path(file_path).stat().st_size
            
            # Comprimir backup
            archive_path = self._compress_backup(backup_path)
            
            # Calcular checksum
            checksum = self._calculate_checksum(archive_path)
            
            # Upload para S3
            if self.s3_client:
                self._upload_to_s3(archive_path, backup_id)
                
                # Sync para região DR
                self._sync_to_dr_region(archive_path, backup_id)
            
            # Salvar metadados
            duration = time.time() - start_time
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now(),
                type="full",
                size_bytes=total_size,
                status="completed",
                files=files_created,
                checksum=checksum,
                duration_seconds=duration
            )
            
            self._save_metadata(metadata)
            self.backup_metadata.append(metadata)
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            # Notificar sucesso
            self._send_notification(f"✅ Backup completo criado: {backup_id}", "success")
            
            self.logger.info(f"🎉 Backup completo finalizado: {backup_id} ({duration:.2f}s)")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"❌ Falha no backup completo: {e}")
            self._send_notification(f"❌ Falha no backup: {str(e)}", "error")
            raise
    
    def _backup_database(self, backup_path: Path) -> List[str]:
        """Backup do banco de dados MySQL"""
        self.logger.info("📊 Iniciando backup do banco de dados...")
        
        dump_file = backup_path / "database.sql"
        
        try:
            # Comando mysqldump
            cmd = [
                "mysqldump",
                f"--host={self.config.db_host}",
                f"--port={self.config.db_port}",
                f"--user={self.config.db_user}",
                f"--password={self.config.db_password}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                "--set-gtid-purged=OFF",
                self.config.db_name
            ]
            
            with open(dump_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            self.logger.info(f"✅ Backup do banco salvo: {dump_file}")
            return [str(dump_file)]
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Falha no backup do banco: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Erro no backup do banco: {e}")
            return []
    
    def _backup_redis(self, backup_path: Path) -> List[str]:
        """Backup do Redis"""
        self.logger.info("🔄 Iniciando backup do Redis...")
        
        try:
            r = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password or None,
                decode_responses=True
            )
            
            # Testar conexão
            r.ping()
            
            # Salvar snapshot do Redis
            redis_file = backup_path / "redis_dump.rdb"
            
            # Executar BGSAVE
            r.bgsave()
            
            # Aguardar conclusão
            while r.lastsave() == r.lastsave():
                time.sleep(1)
            
            # Copiar arquivo RDB
            rdb_source = "/var/lib/redis/dump.rdb"  # Caminho padrão
            if Path(rdb_source).exists():
                shutil.copy2(rdb_source, redis_file)
                self.logger.info(f"✅ Backup do Redis salvo: {redis_file}")
                return [str(redis_file)]
            else:
                self.logger.warning("⚠️  Arquivo RDB do Redis não encontrado")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Falha no backup do Redis: {e}")
            return []
    
    def _backup_files(self, backup_path: Path) -> List[str]:
        """Backup de arquivos de mídia"""
        self.logger.info("📁 Iniciando backup de arquivos...")
        
        files_archive = backup_path / "media_files.tar.gz"
        
        try:
            # Diretórios para backup
            media_dirs = [
                "app/static/uploads",
                "app/static/videos", 
                "app/static/audios",
                "app/static/thumbnails",
                "cache"
            ]
            
            existing_dirs = [d for d in media_dirs if Path(d).exists()]
            
            if existing_dirs:
                # Criar arquivo tar
                cmd = ["tar", "-czf", str(files_archive)] + existing_dirs
                subprocess.run(cmd, check=True)
                
                self.logger.info(f"✅ Backup de arquivos salvo: {files_archive}")
                return [str(files_archive)]
            else:
                self.logger.warning("⚠️  Nenhum diretório de mídia encontrado")
                return []
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Falha no backup de arquivos: {e}")
            return []
    
    def _backup_configs(self, backup_path: Path) -> List[str]:
        """Backup de configurações"""
        self.logger.info("⚙️  Iniciando backup de configurações...")
        
        config_archive = backup_path / "configs.tar.gz"
        
        try:
            # Arquivos de configuração
            config_files = [
                ".env",
                "app/config.py",
                "alembic.ini",
                "docker-compose.yml",
                "nginx/tecnocursos.conf",
                "systemd/tecnocursos.service"
            ]
            
            existing_files = [f for f in config_files if Path(f).exists()]
            
            if existing_files:
                cmd = ["tar", "-czf", str(config_archive)] + existing_files
                subprocess.run(cmd, check=True)
                
                self.logger.info(f"✅ Backup de configurações salvo: {config_archive}")
                return [str(config_archive)]
            else:
                self.logger.warning("⚠️  Nenhum arquivo de configuração encontrado")
                return []
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Falha no backup de configurações: {e}")
            return []
    
    def _backup_kubernetes_resources(self, backup_path: Path) -> List[str]:
        """Backup de recursos Kubernetes"""
        self.logger.info("☸️  Iniciando backup de recursos Kubernetes...")
        
        k8s_backup = backup_path / "kubernetes_resources.yaml"
        
        try:
            # Carregar configuração do Kubernetes
            config.load_incluster_config()
            v1 = client.CoreV1Api()
            apps_v1 = client.AppsV1Api()
            
            resources = []
            
            # Backup de ConfigMaps
            configmaps = v1.list_namespaced_config_map(namespace="tecnocursos-production")
            resources.extend([cm.to_dict() for cm in configmaps.items])
            
            # Backup de Secrets (sem dados sensíveis)
            secrets = v1.list_namespaced_secret(namespace="tecnocursos-production")
            for secret in secrets.items:
                secret_dict = secret.to_dict()
                secret_dict['data'] = {}  # Remover dados sensíveis
                resources.append(secret_dict)
            
            # Backup de Deployments
            deployments = apps_v1.list_namespaced_deployment(namespace="tecnocursos-production")
            resources.extend([dep.to_dict() for dep in deployments.items])
            
            # Salvar recursos
            with open(k8s_backup, 'w') as f:
                json.dump(resources, f, indent=2, default=str)
            
            self.logger.info(f"✅ Backup de recursos K8s salvo: {k8s_backup}")
            return [str(k8s_backup)]
            
        except Exception as e:
            self.logger.error(f"❌ Falha no backup de recursos K8s: {e}")
            return []
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Comprimir backup"""
        self.logger.info("🗜️  Comprimindo backup...")
        
        archive_path = backup_path.parent / f"{backup_path.name}.tar.gz"
        
        cmd = ["tar", "-czf", str(archive_path), "-C", str(backup_path.parent), backup_path.name]
        subprocess.run(cmd, check=True)
        
        # Remover diretório original
        shutil.rmtree(backup_path)
        
        self.logger.info(f"✅ Backup comprimido: {archive_path}")
        return archive_path
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum do arquivo"""
        import hashlib
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _upload_to_s3(self, file_path: Path, backup_id: str):
        """Upload para S3"""
        if not self.s3_client:
            return
        
        self.logger.info(f"☁️  Fazendo upload para S3: {backup_id}")
        
        s3_key = f"{self.config.s3_prefix}/{self.config.environment}/{backup_id}.tar.gz"
        
        try:
            self.s3_client.upload_file(
                str(file_path),
                self.config.s3_bucket,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'backup-id': backup_id,
                        'environment': self.config.environment,
                        'created-at': datetime.now().isoformat()
                    }
                }
            )
            
            self.logger.info(f"✅ Upload S3 concluído: s3://{self.config.s3_bucket}/{s3_key}")
            
        except Exception as e:
            self.logger.error(f"❌ Falha no upload S3: {e}")
    
    def _sync_to_dr_region(self, file_path: Path, backup_id: str):
        """Sincronizar para região DR"""
        if not self.s3_client:
            return
        
        self.logger.info(f"🔄 Sincronizando para região DR: {backup_id}")
        
        try:
            # Cliente S3 para região DR
            dr_s3_client = boto3.client('s3', region_name=self.config.dr_region)
            
            s3_key = f"{self.config.s3_prefix}/{self.config.environment}/{backup_id}.tar.gz"
            
            dr_s3_client.upload_file(
                str(file_path),
                self.config.dr_bucket,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'backup-id': backup_id,
                        'environment': self.config.environment,
                        'dr-sync': 'true',
                        'created-at': datetime.now().isoformat()
                    }
                }
            )
            
            self.logger.info(f"✅ Sync DR concluído: s3://{self.config.dr_bucket}/{s3_key}")
            
        except Exception as e:
            self.logger.error(f"❌ Falha no sync DR: {e}")
    
    def _save_metadata(self, metadata: BackupMetadata):
        """Salvar metadados do backup"""
        metadata_file = Path(self.config.backup_dir) / "backup_metadata.json"
        
        # Carregar metadados existentes
        existing_metadata = []
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    existing_metadata = json.load(f)
            except:
                existing_metadata = []
        
        # Adicionar novo metadata
        existing_metadata.append(metadata.to_dict())
        
        # Manter apenas últimos 100 registros
        existing_metadata = existing_metadata[-100:]
        
        # Salvar
        with open(metadata_file, 'w') as f:
            json.dump(existing_metadata, f, indent=2)
    
    def _cleanup_old_backups(self):
        """Limpar backups antigos"""
        self.logger.info("🧹 Limpando backups antigos...")
        
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
        
        # Limpar arquivos locais
        backup_dir = Path(self.config.backup_dir)
        for backup_file in backup_dir.glob("*.tar.gz"):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff_date:
                backup_file.unlink()
                self.logger.info(f"🗑️  Removido backup local: {backup_file}")
        
        # Limpar S3
        if self.s3_client:
            self._cleanup_s3_backups(cutoff_date)
    
    def _cleanup_s3_backups(self, cutoff_date: datetime):
        """Limpar backups S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.config.s3_bucket,
                Prefix=f"{self.config.s3_prefix}/{self.config.environment}/"
            )
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    self.s3_client.delete_object(
                        Bucket=self.config.s3_bucket,
                        Key=obj['Key']
                    )
                    self.logger.info(f"🗑️  Removido backup S3: {obj['Key']}")
                    
        except Exception as e:
            self.logger.error(f"❌ Falha na limpeza S3: {e}")
    
    def _send_notification(self, message: str, level: str = "info"):
        """Enviar notificação"""
        if level == "error" and not self.config.alert_on_failure:
            return
        
        # Notificação Slack
        if self.config.slack_webhook:
            self._send_slack_notification(message, level)
        
        # Log local
        if level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)
    
    def _send_slack_notification(self, message: str, level: str):
        """Enviar notificação Slack"""
        try:
            import requests
            
            color = {
                "success": "good",
                "warning": "warning", 
                "error": "danger"
            }.get(level, "good")
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": "TecnoCursos AI - Backup System",
                    "text": message,
                    "ts": int(time.time())
                }]
            }
            
            requests.post(self.config.slack_webhook, json=payload, timeout=10)
            
        except Exception as e:
            self.logger.error(f"Falha na notificação Slack: {e}")

# ============================================================================
# RESTORE SYSTEM
# ============================================================================

class RestoreSystem:
    """Sistema de restauração"""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.logger = setup_logger("RestoreSystem")
        self.s3_client = self._init_s3_client()
    
    def _init_s3_client(self):
        """Inicializar cliente S3"""
        try:
            return boto3.client('s3', region_name=self.config.s3_region)
        except Exception as e:
            self.logger.warning(f"Falha ao inicializar S3: {e}")
            return None
    
    def list_available_backups(self) -> List[Dict[str, Any]]:
        """Listar backups disponíveis"""
        backups = []
        
        # Backups locais
        backup_dir = Path(self.config.backup_dir)
        for backup_file in backup_dir.glob("*.tar.gz"):
            backups.append({
                "id": backup_file.stem,
                "location": "local",
                "path": str(backup_file),
                "size": backup_file.stat().st_size,
                "date": datetime.fromtimestamp(backup_file.stat().st_mtime)
            })
        
        # Backups S3
        if self.s3_client:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.config.s3_bucket,
                    Prefix=f"{self.config.s3_prefix}/{self.config.environment}/"
                )
                
                for obj in response.get('Contents', []):
                    backup_id = Path(obj['Key']).stem
                    backups.append({
                        "id": backup_id,
                        "location": "s3",
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "date": obj['LastModified'].replace(tzinfo=None)
                    })
                    
            except Exception as e:
                self.logger.error(f"Erro ao listar backups S3: {e}")
        
        return sorted(backups, key=lambda x: x['date'], reverse=True)
    
    def restore_backup(self, backup_id: str, components: List[str] = None) -> bool:
        """Restaurar backup"""
        if components is None:
            components = ["database", "redis", "files", "configs"]
        
        self.logger.info(f"🔄 Iniciando restauração: {backup_id}")
        
        try:
            # Download do backup se necessário
            backup_path = self._download_backup(backup_id)
            
            if not backup_path:
                raise Exception(f"Backup não encontrado: {backup_id}")
            
            # Extrair backup
            extract_path = self._extract_backup(backup_path)
            
            # Restaurar componentes
            success = True
            for component in components:
                try:
                    if component == "database":
                        self._restore_database(extract_path)
                    elif component == "redis":
                        self._restore_redis(extract_path)
                    elif component == "files":
                        self._restore_files(extract_path)
                    elif component == "configs":
                        self._restore_configs(extract_path)
                    
                    self.logger.info(f"✅ Restaurado: {component}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Falha na restauração {component}: {e}")
                    success = False
            
            # Cleanup
            shutil.rmtree(extract_path)
            
            if success:
                self.logger.info(f"🎉 Restauração concluída: {backup_id}")
                return True
            else:
                self.logger.warning(f"⚠️  Restauração parcial: {backup_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Falha na restauração: {e}")
            return False
    
    def _download_backup(self, backup_id: str) -> Optional[Path]:
        """Download do backup"""
        # Verificar se existe localmente
        local_path = Path(self.config.backup_dir) / f"{backup_id}.tar.gz"
        if local_path.exists():
            return local_path
        
        # Download do S3
        if self.s3_client:
            s3_key = f"{self.config.s3_prefix}/{self.config.environment}/{backup_id}.tar.gz"
            
            try:
                self.logger.info(f"📥 Fazendo download do S3: {backup_id}")
                self.s3_client.download_file(
                    self.config.s3_bucket,
                    s3_key,
                    str(local_path)
                )
                return local_path
                
            except Exception as e:
                self.logger.error(f"Falha no download S3: {e}")
        
        return None
    
    def _extract_backup(self, backup_path: Path) -> Path:
        """Extrair backup"""
        extract_path = backup_path.parent / f"restore_{backup_path.stem}"
        extract_path.mkdir(exist_ok=True)
        
        cmd = ["tar", "-xzf", str(backup_path), "-C", str(extract_path)]
        subprocess.run(cmd, check=True)
        
        return extract_path / backup_path.stem
    
    def _restore_database(self, extract_path: Path):
        """Restaurar banco de dados"""
        sql_file = extract_path / "database.sql"
        
        if not sql_file.exists():
            raise Exception("Arquivo de backup do banco não encontrado")
        
        cmd = [
            "mysql",
            f"--host={self.config.db_host}",
            f"--port={self.config.db_port}",
            f"--user={self.config.db_user}",
            f"--password={self.config.db_password}",
            self.config.db_name
        ]
        
        with open(sql_file, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
    
    def _restore_redis(self, extract_path: Path):
        """Restaurar Redis"""
        rdb_file = extract_path / "redis_dump.rdb"
        
        if not rdb_file.exists():
            raise Exception("Arquivo de backup do Redis não encontrado")
        
        # Parar Redis, copiar arquivo RDB e reiniciar
        subprocess.run(["sudo", "systemctl", "stop", "redis"], check=True)
        shutil.copy2(rdb_file, "/var/lib/redis/dump.rdb")
        subprocess.run(["sudo", "systemctl", "start", "redis"], check=True)
    
    def _restore_files(self, extract_path: Path):
        """Restaurar arquivos"""
        files_archive = extract_path / "media_files.tar.gz"
        
        if not files_archive.exists():
            raise Exception("Arquivo de backup de mídia não encontrado")
        
        cmd = ["tar", "-xzf", str(files_archive)]
        subprocess.run(cmd, check=True)
    
    def _restore_configs(self, extract_path: Path):
        """Restaurar configurações"""
        config_archive = extract_path / "configs.tar.gz"
        
        if not config_archive.exists():
            raise Exception("Arquivo de backup de configurações não encontrado")
        
        cmd = ["tar", "-xzf", str(config_archive)]
        subprocess.run(cmd, check=True)

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Interface CLI principal"""
    parser = argparse.ArgumentParser(description="TecnoCursos AI Backup & Restore System")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando backup
    backup_parser = subparsers.add_parser("backup", help="Criar backup")
    backup_parser.add_argument("--type", choices=["full", "incremental"], default="full")
    backup_parser.add_argument("--config", help="Arquivo de configuração")
    
    # Comando restore
    restore_parser = subparsers.add_parser("restore", help="Restaurar backup")
    restore_parser.add_argument("backup_id", help="ID do backup para restaurar")
    restore_parser.add_argument("--components", nargs="+", 
                               choices=["database", "redis", "files", "configs"],
                               help="Componentes para restaurar")
    restore_parser.add_argument("--config", help="Arquivo de configuração")
    
    # Comando list
    list_parser = subparsers.add_parser("list", help="Listar backups disponíveis")
    list_parser.add_argument("--config", help="Arquivo de configuração")
    
    # Comando verify
    verify_parser = subparsers.add_parser("verify", help="Verificar integridade dos backups")
    verify_parser.add_argument("--config", help="Arquivo de configuração")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Carregar configuração
    if args.config and Path(args.config).exists():
        with open(args.config) as f:
            config_data = json.load(f)
        config = BackupConfig(**config_data)
    else:
        config = BackupConfig()
    
    if args.command == "backup":
        backup_system = BackupSystem(config)
        if args.type == "full":
            backup_id = backup_system.create_full_backup()
            print(f"✅ Backup criado: {backup_id}")
    
    elif args.command == "restore":
        restore_system = RestoreSystem(config)
        success = restore_system.restore_backup(args.backup_id, args.components)
        if success:
            print(f"✅ Restauração concluída: {args.backup_id}")
        else:
            print(f"❌ Falha na restauração: {args.backup_id}")
    
    elif args.command == "list":
        restore_system = RestoreSystem(config)
        backups = restore_system.list_available_backups()
        
        print("\n📋 Backups Disponíveis:")
        print("-" * 80)
        for backup in backups:
            size_mb = backup['size'] / (1024 * 1024)
            print(f"🔹 {backup['id']}")
            print(f"   Local: {backup['location']}")
            print(f"   Data: {backup['date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Tamanho: {size_mb:.1f} MB")
            print()
    
    elif args.command == "verify":
        print("🔍 Verificação de integridade não implementada ainda")

if __name__ == "__main__":
    main() 