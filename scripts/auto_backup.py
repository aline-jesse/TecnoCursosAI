#!/usr/bin/env python3
"""
Sistema de Backup Automático - TecnoCursos AI
Realiza backups automáticos do sistema
"""

import shutil
import os
import json
import time
from datetime import datetime
from pathlib import Path
import logging
import zipfile
import sqlite3

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoBackup:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        """Cria backup completo do sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"tecnocursos_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Criar diretório de backup
            backup_path.mkdir(exist_ok=True)
            
            # Backup de arquivos importantes
            self._backup_files(backup_path)
            
            # Backup do database
            self._backup_database(backup_path)
            
            # Backup de uploads
            self._backup_uploads(backup_path)
            
            # Criar arquivo de metadados
            self._create_metadata(backup_path, timestamp)
            
            # Compactar backup
            self._compress_backup(backup_path)
            
            logger.info(f"Backup criado com sucesso: {backup_name}")
            return backup_name
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None
    
    def _backup_files(self, backup_path):
        """Backup de arquivos importantes"""
        important_files = [
            "simple_server.py",
            "upload_handler.py",
            "background_processor.py",
            "config.json",
            "requirements.txt",
            "package.json",
            "index.html"
        ]
        
        files_dir = backup_path / "files"
        files_dir.mkdir(exist_ok=True)
        
        for file in important_files:
            if Path(file).exists():
                shutil.copy2(file, files_dir / file)
                logger.info(f"Arquivo backupado: {file}")
    
    def _backup_database(self, backup_path):
        """Backup do database SQLite"""
        db_file = "tecnocursos.db"
        if Path(db_file).exists():
            db_backup_path = backup_path / "database"
            db_backup_path.mkdir(exist_ok=True)
            
            # Copiar database
            shutil.copy2(db_file, db_backup_path / db_file)
            
            # Backup das tabelas
            self._backup_database_tables(db_backup_path)
            
            logger.info("Database backupado com sucesso")
    
    def _backup_database_tables(self, db_backup_path):
        """Backup das tabelas do database"""
        try:
            conn = sqlite3.connect("tecnocursos.db")
            cursor = conn.cursor()
            
            # Listar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            tables_data = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Obter nomes das colunas
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                tables_data[table_name] = {
                    "columns": columns,
                    "rows": rows
                }
            
            # Salvar dados das tabelas
            with open(db_backup_path / "tables_data.json", 'w', encoding='utf-8') as f:
                json.dump(tables_data, f, indent=2, ensure_ascii=False)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao fazer backup das tabelas: {e}")
    
    def _backup_uploads(self, backup_path):
        """Backup da pasta de uploads"""
        uploads_dir = Path("uploads")
        if uploads_dir.exists():
            uploads_backup = backup_path / "uploads"
            shutil.copytree(uploads_dir, uploads_backup, dirs_exist_ok=True)
            logger.info("Uploads backupados com sucesso")
    
    def _create_metadata(self, backup_path, timestamp):
        """Cria arquivo de metadados do backup"""
        metadata = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "version": "2.1.0",
            "system": "TecnoCursos AI",
            "backup_type": "full",
            "files_backed_up": [
                "simple_server.py",
                "upload_handler.py",
                "background_processor.py",
                "config.json",
                "requirements.txt",
                "package.json",
                "index.html",
                "tecnocursos.db",
                "uploads/"
            ]
        }
        
        with open(backup_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _compress_backup(self, backup_path):
        """Compacta o backup em arquivo ZIP"""
        zip_path = backup_path.parent / f"{backup_path.name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_path)
                    zipf.write(file_path, arcname)
        
        # Remover diretório não compactado
        shutil.rmtree(backup_path)
        
        logger.info(f"Backup compactado: {zip_path}")
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        for file in self.backup_dir.glob("*.zip"):
            try:
                with zipfile.ZipFile(file, 'r') as zipf:
                    # Tentar ler metadata
                    try:
                        with zipf.open("metadata.json") as f:
                            metadata = json.load(f)
                            backups.append({
                                "filename": file.name,
                                "size": file.stat().st_size,
                                "timestamp": metadata.get("timestamp", "unknown"),
                                "datetime": metadata.get("datetime", "unknown")
                            })
                    except:
                        backups.append({
                            "filename": file.name,
                            "size": file.stat().st_size,
                            "timestamp": "unknown",
                            "datetime": "unknown"
                        })
            except Exception as e:
                logger.error(f"Erro ao ler backup {file}: {e}")
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_backup(self, backup_filename):
        """Restaura um backup"""
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            logger.error(f"Backup não encontrado: {backup_filename}")
            return False
        
        try:
            # Criar diretório temporário
            temp_dir = Path("temp_restore")
            temp_dir.mkdir(exist_ok=True)
            
            # Extrair backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Restaurar arquivos
            self._restore_files(temp_dir)
            
            # Restaurar database
            self._restore_database(temp_dir)
            
            # Restaurar uploads
            self._restore_uploads(temp_dir)
            
            # Limpar diretório temporário
            shutil.rmtree(temp_dir)
            
            logger.info(f"Backup restaurado com sucesso: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def _restore_files(self, temp_dir):
        """Restaura arquivos do backup"""
        files_dir = temp_dir / "files"
        if files_dir.exists():
            for file in files_dir.iterdir():
                if file.is_file():
                    shutil.copy2(file, file.name)
                    logger.info(f"Arquivo restaurado: {file.name}")
    
    def _restore_database(self, temp_dir):
        """Restaura database do backup"""
        db_backup_dir = temp_dir / "database"
        if db_backup_dir.exists():
            db_file = db_backup_dir / "tecnocursos.db"
            if db_file.exists():
                shutil.copy2(db_file, "tecnocursos.db")
                logger.info("Database restaurado")
    
    def _restore_uploads(self, temp_dir):
        """Restaura uploads do backup"""
        uploads_backup = temp_dir / "uploads"
        if uploads_backup.exists():
            if Path("uploads").exists():
                shutil.rmtree("uploads")
            shutil.copytree(uploads_backup, "uploads")
            logger.info("Uploads restaurados")

def main():
    """Função principal"""
    backup_system = AutoBackup()
    
    print("=" * 60)
    print("SISTEMA DE BACKUP AUTOMÁTICO - TECNOCURSOS AI")
    print("=" * 60)
    
    while True:
        print("\nOpções:")
        print("1. Criar backup")
        print("2. Listar backups")
        print("3. Restaurar backup")
        print("4. Sair")
        
        choice = input("\nEscolha uma opção: ")
        
        if choice == "1":
            print("Criando backup...")
            backup_name = backup_system.create_backup()
            if backup_name:
                print(f"Backup criado: {backup_name}")
            else:
                print("Erro ao criar backup")
        
        elif choice == "2":
            print("\nBackups disponíveis:")
            backups = backup_system.list_backups()
            for i, backup in enumerate(backups, 1):
                size_mb = backup["size"] / (1024 * 1024)
                print(f"{i}. {backup['filename']} ({size_mb:.1f}MB) - {backup['datetime']}")
        
        elif choice == "3":
            backups = backup_system.list_backups()
            if not backups:
                print("Nenhum backup disponível")
                continue
            
            print("\nBackups disponíveis:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['filename']}")
            
            try:
                backup_choice = int(input("Escolha o backup para restaurar: ")) - 1
                if 0 <= backup_choice < len(backups):
                    backup_filename = backups[backup_choice]["filename"]
                    confirm = input(f"Confirmar restauração de {backup_filename}? (s/n): ")
                    if confirm.lower() == 's':
                        if backup_system.restore_backup(backup_filename):
                            print("Backup restaurado com sucesso!")
                        else:
                            print("Erro ao restaurar backup")
                    else:
                        print("Restauração cancelada")
                else:
                    print("Opção inválida")
            except ValueError:
                print("Opção inválida")
        
        elif choice == "4":
            print("Saindo...")
            break
        
        else:
            print("Opção inválida")

if __name__ == "__main__":
    main() 