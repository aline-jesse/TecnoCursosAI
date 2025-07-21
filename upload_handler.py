#!/usr/bin/env python3
"""
Upload Handler - TecnoCursos AI
Sistema de upload e processamento de arquivos
"""

import os
import json
import logging
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import shutil

# Configurar logging
logger = logging.getLogger(__name__)

# Configurações
UPLOAD_DIR = Path("uploads")
STATIC_DIR = Path("static")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'.pdf', '.pptx', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.mp4', '.mp3', '.wav'}

def create_upload_directories():
    """Cria diretórios necessários para upload"""
    directories = [
        "uploads/videos",
        "uploads/audios", 
        "uploads/images",
        "uploads/documents",
        "uploads/temp",
        "static/videos",
        "static/audios",
        "static/thumbnails"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Diretorio criado: {directory}")

def validate_file(file_data: bytes, filename: str) -> Dict[str, Any]:
    """Valida arquivo enviado"""
    result = {
        "valid": False,
        "error": None,
        "file_type": None,
        "file_size": len(file_data)
    }
    
    # Verificar tamanho
    if len(file_data) > MAX_FILE_SIZE:
        result["error"] = f"Arquivo muito grande: {len(file_data) / (1024*1024):.1f}MB > {MAX_FILE_SIZE / (1024*1024)}MB"
        return result
    
    # Verificar extensão
    file_extension = Path(filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        result["error"] = f"Tipo de arquivo não suportado: {file_extension}"
        return result
    
    result["file_type"] = file_extension
    result["valid"] = True
    return result

def handle_upload_request(file_data: bytes, filename: str) -> Dict[str, Any]:
    """Processa upload de arquivo"""
    try:
        # Criar diretórios se não existirem
        create_upload_directories()
        
        # Validar arquivo
        validation = validate_file(file_data, filename)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"]
            }
        
        # Gerar UUID único
        file_uuid = str(uuid.uuid4())
        file_extension = Path(filename).suffix.lower()
        safe_filename = f"{file_uuid}{file_extension}"
        
        # Determinar diretório de destino
        if file_extension in ['.pdf', '.pptx', '.docx', '.txt']:
            dest_dir = UPLOAD_DIR / "documents"
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            dest_dir = UPLOAD_DIR / "images"
        elif file_extension in ['.mp4']:
            dest_dir = UPLOAD_DIR / "videos"
        elif file_extension in ['.mp3', '.wav']:
            dest_dir = UPLOAD_DIR / "audios"
        else:
            dest_dir = UPLOAD_DIR / "temp"
        
        # Salvar arquivo
        file_path = dest_dir / safe_filename
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Calcular hash
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Criar metadados
        metadata = {
            "original_filename": filename,
            "uuid": file_uuid,
            "file_size": len(file_data),
            "file_type": file_extension,
            "upload_date": datetime.now().isoformat(),
            "file_hash": file_hash,
            "file_path": str(file_path)
        }
        
        logger.info(f"Arquivo enviado: {filename} -> {file_path}")
        
        return {
            "success": True,
            "file_info": {
                "filename": filename,
                "uuid": file_uuid,
                "size": len(file_data),
                "type": file_extension,
                "path": str(file_path)
            },
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no upload: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def handle_list_request() -> Dict[str, Any]:
    """Lista arquivos enviados"""
    try:
        files = []
        
        # Procurar em todos os diretórios de upload
        for upload_type in ["videos", "audios", "images", "documents", "temp"]:
            upload_path = UPLOAD_DIR / upload_type
            if upload_path.exists():
                for file_path in upload_path.iterdir():
                    if file_path.is_file():
                        stat = file_path.stat()
                        files.append({
                            "filename": file_path.name,
                            "type": upload_type,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "path": str(file_path)
                        })
        
        return {
            "success": True,
            "files": files,
            "total_count": len(files)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar arquivos: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def handle_delete_request(file_path: str) -> Dict[str, Any]:
    """Deleta arquivo"""
    try:
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return {
                "success": False,
                "error": "Arquivo não encontrado"
            }
        
        # Verificar se está dentro dos diretórios permitidos
        if not str(file_path_obj).startswith(str(UPLOAD_DIR)):
            return {
                "success": False,
                "error": "Acesso negado"
            }
        
        # Deletar arquivo
        file_path_obj.unlink()
        
        logger.info(f"Arquivo deletado: {file_path}")
        
        return {
            "success": True,
            "message": "Arquivo deletado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao deletar arquivo: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def handle_stats_request() -> Dict[str, Any]:
    """Retorna estatísticas dos uploads"""
    try:
        stats = {
            "total_files": 0,
            "total_size": 0,
            "files_by_type": {},
            "files_by_directory": {}
        }
        
        # Calcular estatísticas
        for upload_type in ["videos", "audios", "images", "documents", "temp"]:
            upload_path = UPLOAD_DIR / upload_type
            if upload_path.exists():
                dir_files = 0
                dir_size = 0
                
                for file_path in upload_path.iterdir():
                    if file_path.is_file():
                        stat = file_path.stat()
                        file_size = stat.st_size
                        file_extension = file_path.suffix.lower()
                        
                        stats["total_files"] += 1
                        stats["total_size"] += file_size
                        dir_files += 1
                        dir_size += file_size
                        
                        # Contar por tipo
                        if file_extension not in stats["files_by_type"]:
                            stats["files_by_type"][file_extension] = 0
                        stats["files_by_type"][file_extension] += 1
                
                stats["files_by_directory"][upload_type] = {
                    "count": dir_files,
                    "size": dir_size
                }
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao calcular estatísticas: {e}")
        return {
            "success": False,
            "error": str(e)
        } 