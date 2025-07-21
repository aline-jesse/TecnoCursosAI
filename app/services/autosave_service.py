"""
Serviço de Auto-save Automático - TecnoCursos AI
Sistema completo para salvamento automático com versionamento e recuperação
"""

import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import gzip
import hashlib
from dataclasses import dataclass

try:
    from sqlalchemy.orm import Session
    from app.database import get_db_session
    from app.models import Project, User
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class AutoSaveVersion:
    """Versão de auto-save"""
    id: str
    project_id: int
    user_id: int
    version_number: int
    data: Dict[str, Any]
    data_hash: str
    file_size: int
    created_at: datetime
    is_manual: bool = False
    description: Optional[str] = None

class AutoSaveService:
    """Serviço completo para auto-save automático"""
    
    def __init__(self):
        self.save_dir = Path("data/autosave")
        self.versions_dir = self.save_dir / "versions"
        self.temp_dir = self.save_dir / "temp"
        
        # Criar diretórios
        for directory in [self.save_dir, self.versions_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configurações
        self.autosave_interval = 30  # segundos
        self.max_versions_per_project = 50
        self.max_age_days = 30
        self.compression_enabled = True
        self.min_changes_threshold = 5  # mínimo de mudanças para salvar
        
        # Estado interno
        self.active_sessions = {}  # {user_id: {project_id: session_data}}
        self.save_queue = asyncio.Queue()
        self.is_running = False
        
        # Cache de projetos
        self.project_cache = {}
        
        logger.info("💾 Auto-save Service inicializado")
    
    async def start_service(self):
        """Iniciar serviço de auto-save"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Iniciar workers
        asyncio.create_task(self._autosave_worker())
        asyncio.create_task(self._cleanup_worker())
        
        logger.info("🔄 Serviço de auto-save iniciado")
    
    async def stop_service(self):
        """Parar serviço de auto-save"""
        self.is_running = False
        logger.info("⏹️ Serviço de auto-save parado")
    
    async def register_session(self, user_id: int, project_id: int, 
                             initial_data: Dict[str, Any] = None):
        """Registrar sessão de edição"""
        try:
            session_id = str(uuid.uuid4())
            
            if user_id not in self.active_sessions:
                self.active_sessions[user_id] = {}
            
            self.active_sessions[user_id][project_id] = {
                "session_id": session_id,
                "started_at": datetime.now(),
                "last_save": datetime.now(),
                "last_data": initial_data or {},
                "changes_count": 0,
                "save_count": 0,
                "is_active": True
            }
            
            logger.info(f"📝 Sessão registrada: user={user_id}, project={project_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Erro ao registrar sessão: {e}")
            return None
    
    async def unregister_session(self, user_id: int, project_id: int):
        """Desregistrar sessão de edição"""
        try:
            if user_id in self.active_sessions and project_id in self.active_sessions[user_id]:
                # Fazer save final antes de desregistrar
                await self.manual_save(user_id, project_id, "Sessão finalizada")
                
                # Remover sessão
                del self.active_sessions[user_id][project_id]
                
                if not self.active_sessions[user_id]:
                    del self.active_sessions[user_id]
                
                logger.info(f"🔚 Sessão finalizada: user={user_id}, project={project_id}")
            
        except Exception as e:
            logger.error(f"Erro ao desregistrar sessão: {e}")
    
    async def update_project_data(self, user_id: int, project_id: int, 
                                data: Dict[str, Any]):
        """Atualizar dados do projeto (trigger para auto-save)"""
        try:
            if user_id not in self.active_sessions or project_id not in self.active_sessions[user_id]:
                await self.register_session(user_id, project_id, data)
                return
            
            session = self.active_sessions[user_id][project_id]
            
            # Verificar se houve mudanças significativas
            changes_count = self._count_changes(session["last_data"], data)
            session["changes_count"] += changes_count
            session["last_data"] = data.copy()
            
            # Adicionar à fila de save se necessário
            if session["changes_count"] >= self.min_changes_threshold:
                await self.save_queue.put({
                    "user_id": user_id,
                    "project_id": project_id,
                    "data": data,
                    "timestamp": datetime.now(),
                    "is_manual": False
                })
                
                session["changes_count"] = 0
            
            logger.debug(f"📊 Dados atualizados: {changes_count} mudanças")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dados: {e}")
    
    async def manual_save(self, user_id: int, project_id: int, 
                         description: str = "Save manual"):
        """Realizar save manual"""
        try:
            if user_id in self.active_sessions and project_id in self.active_sessions[user_id]:
                session = self.active_sessions[user_id][project_id]
                data = session["last_data"]
                
                await self.save_queue.put({
                    "user_id": user_id,
                    "project_id": project_id,
                    "data": data,
                    "timestamp": datetime.now(),
                    "is_manual": True,
                    "description": description
                })
                
                logger.info(f"💾 Save manual solicitado: {description}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro no save manual: {e}")
            return False
    
    async def _autosave_worker(self):
        """Worker para processar auto-saves"""
        while self.is_running:
            try:
                # Processar fila de saves
                try:
                    save_request = await asyncio.wait_for(
                        self.save_queue.get(), 
                        timeout=1.0
                    )
                    await self._process_save_request(save_request)
                except asyncio.TimeoutError:
                    pass
                
                # Auto-save baseado em tempo
                await self._check_time_based_saves()
                
                await asyncio.sleep(5)  # Check a cada 5 segundos
                
            except Exception as e:
                logger.error(f"Erro no worker de auto-save: {e}")
                await asyncio.sleep(10)
    
    async def _process_save_request(self, save_request: Dict[str, Any]):
        """Processar request de save"""
        try:
            user_id = save_request["user_id"]
            project_id = save_request["project_id"]
            data = save_request["data"]
            is_manual = save_request.get("is_manual", False)
            description = save_request.get("description")
            
            # Criar versão
            version = await self._create_version(
                user_id, project_id, data, is_manual, description
            )
            
            if version:
                # Atualizar sessão
                if user_id in self.active_sessions and project_id in self.active_sessions[user_id]:
                    session = self.active_sessions[user_id][project_id]
                    session["last_save"] = datetime.now()
                    session["save_count"] += 1
                
                # Atualizar projeto no banco se disponível
                if SQLALCHEMY_AVAILABLE:
                    await self._update_database_project(project_id, data)
                
                logger.info(f"✅ Auto-save realizado: v{version.version_number}")
            
        except Exception as e:
            logger.error(f"Erro ao processar save: {e}")
    
    async def _create_version(self, user_id: int, project_id: int, 
                           data: Dict[str, Any], is_manual: bool = False,
                           description: str = None) -> Optional[AutoSaveVersion]:
        """Criar nova versão do projeto"""
        try:
            # Calcular hash dos dados
            data_json = json.dumps(data, sort_keys=True)
            data_hash = hashlib.md5(data_json.encode()).hexdigest()
            
            # Verificar se é diferente da última versão
            existing_versions = await self.get_project_versions(project_id, limit=1)
            if existing_versions and existing_versions[0].data_hash == data_hash:
                logger.debug("📋 Dados inalterados, skip save")
                return None
            
            # Obter próximo número de versão
            version_number = len(await self.get_project_versions(project_id)) + 1
            
            # Criar objeto de versão
            version = AutoSaveVersion(
                id=str(uuid.uuid4()),
                project_id=project_id,
                user_id=user_id,
                version_number=version_number,
                data=data,
                data_hash=data_hash,
                file_size=len(data_json),
                created_at=datetime.now(),
                is_manual=is_manual,
                description=description
            )
            
            # Salvar arquivo
            await self._save_version_file(version)
            
            # Limpar versões antigas se necessário
            await self._cleanup_old_versions(project_id)
            
            return version
            
        except Exception as e:
            logger.error(f"Erro ao criar versão: {e}")
            return None
    
    async def _save_version_file(self, version: AutoSaveVersion):
        """Salvar arquivo de versão"""
        try:
            version_filename = f"project_{version.project_id}_v{version.version_number}_{version.id}.json"
            
            if self.compression_enabled:
                version_filename += ".gz"
                version_path = self.versions_dir / version_filename
                
                # Salvar comprimido
                version_data = {
                    "id": version.id,
                    "project_id": version.project_id,
                    "user_id": version.user_id,
                    "version_number": version.version_number,
                    "data": version.data,
                    "data_hash": version.data_hash,
                    "file_size": version.file_size,
                    "created_at": version.created_at.isoformat(),
                    "is_manual": version.is_manual,
                    "description": version.description
                }
                
                with gzip.open(version_path, 'wt', encoding='utf-8') as f:
                    json.dump(version_data, f, indent=2)
            else:
                version_path = self.versions_dir / version_filename
                
                version_data = {
                    "id": version.id,
                    "project_id": version.project_id,
                    "user_id": version.user_id,
                    "version_number": version.version_number,
                    "data": version.data,
                    "data_hash": version.data_hash,
                    "file_size": version.file_size,
                    "created_at": version.created_at.isoformat(),
                    "is_manual": version.is_manual,
                    "description": version.description
                }
                
                with open(version_path, 'w', encoding='utf-8') as f:
                    json.dump(version_data, f, indent=2)
            
            logger.debug(f"💾 Versão salva: {version_filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo de versão: {e}")
            raise
    
    async def get_project_versions(self, project_id: int, 
                                 limit: int = None) -> List[AutoSaveVersion]:
        """Obter versões do projeto"""
        try:
            versions = []
            
            # Buscar arquivos de versão
            pattern = f"project_{project_id}_v*.json*"
            version_files = list(self.versions_dir.glob(pattern))
            
            # Ordenar por data de modificação (mais recente primeiro)
            version_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for version_file in version_files[:limit] if limit else version_files:
                try:
                    version = await self._load_version_file(version_file)
                    if version:
                        versions.append(version)
                except Exception as e:
                    logger.warning(f"Erro ao carregar versão {version_file}: {e}")
            
            return versions
            
        except Exception as e:
            logger.error(f"Erro ao obter versões: {e}")
            return []
    
    async def _load_version_file(self, version_file: Path) -> Optional[AutoSaveVersion]:
        """Carregar arquivo de versão"""
        try:
            if version_file.suffix == '.gz':
                with gzip.open(version_file, 'rt', encoding='utf-8') as f:
                    version_data = json.load(f)
            else:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
            
            return AutoSaveVersion(
                id=version_data["id"],
                project_id=version_data["project_id"],
                user_id=version_data["user_id"],
                version_number=version_data["version_number"],
                data=version_data["data"],
                data_hash=version_data["data_hash"],
                file_size=version_data["file_size"],
                created_at=datetime.fromisoformat(version_data["created_at"]),
                is_manual=version_data.get("is_manual", False),
                description=version_data.get("description")
            )
            
        except Exception as e:
            logger.error(f"Erro ao carregar versão: {e}")
            return None
    
    async def restore_version(self, project_id: int, version_id: str, 
                            user_id: int) -> Optional[Dict[str, Any]]:
        """Restaurar versão específica"""
        try:
            versions = await self.get_project_versions(project_id)
            
            target_version = next((v for v in versions if v.id == version_id), None)
            if not target_version:
                logger.warning(f"Versão não encontrada: {version_id}")
                return None
            
            # Criar nova versão como backup antes de restaurar
            if user_id in self.active_sessions and project_id in self.active_sessions[user_id]:
                current_data = self.active_sessions[user_id][project_id]["last_data"]
                await self._create_version(
                    user_id, project_id, current_data, True, 
                    f"Backup antes de restaurar v{target_version.version_number}"
                )
            
            # Restaurar dados
            restored_data = target_version.data
            
            # Atualizar sessão ativa
            if user_id in self.active_sessions and project_id in self.active_sessions[user_id]:
                self.active_sessions[user_id][project_id]["last_data"] = restored_data
                self.active_sessions[user_id][project_id]["changes_count"] = 0
            
            logger.info(f"🔄 Versão restaurada: v{target_version.version_number}")
            return restored_data
            
        except Exception as e:
            logger.error(f"Erro ao restaurar versão: {e}")
            return None
    
    async def _check_time_based_saves(self):
        """Verificar saves baseados em tempo"""
        try:
            current_time = datetime.now()
            
            for user_id, projects in self.active_sessions.items():
                for project_id, session in projects.items():
                    if not session["is_active"]:
                        continue
                    
                    # Verificar se passou do intervalo de auto-save
                    time_since_save = current_time - session["last_save"]
                    if time_since_save.total_seconds() >= self.autosave_interval:
                        
                        # Só salvar se houver mudanças
                        if session["changes_count"] > 0:
                            await self.save_queue.put({
                                "user_id": user_id,
                                "project_id": project_id,
                                "data": session["last_data"],
                                "timestamp": current_time,
                                "is_manual": False,
                                "description": "Auto-save por tempo"
                            })
            
        except Exception as e:
            logger.error(f"Erro no check de saves por tempo: {e}")
    
    async def _cleanup_worker(self):
        """Worker para limpeza de versões antigas"""
        while self.is_running:
            try:
                await self._cleanup_old_versions_all()
                await asyncio.sleep(3600)  # Executar a cada hora
                
            except Exception as e:
                logger.error(f"Erro no worker de limpeza: {e}")
                await asyncio.sleep(1800)  # Retry em 30 min
    
    async def _cleanup_old_versions(self, project_id: int):
        """Limpar versões antigas de um projeto"""
        try:
            versions = await self.get_project_versions(project_id)
            
            # Remover versões em excesso
            if len(versions) > self.max_versions_per_project:
                # Manter versões manuais e remover automáticas antigas
                auto_versions = [v for v in versions if not v.is_manual]
                auto_versions.sort(key=lambda x: x.created_at)
                
                to_remove = len(auto_versions) - (self.max_versions_per_project - 
                                                len([v for v in versions if v.is_manual]))
                
                if to_remove > 0:
                    for version in auto_versions[:to_remove]:
                        await self._delete_version_file(version)
            
            # Remover versões muito antigas
            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
            old_versions = [v for v in versions if v.created_at < cutoff_date and not v.is_manual]
            
            for version in old_versions:
                await self._delete_version_file(version)
            
        except Exception as e:
            logger.error(f"Erro na limpeza de versões: {e}")
    
    async def _cleanup_old_versions_all(self):
        """Limpar versões antigas de todos os projetos"""
        try:
            # Obter todos os IDs de projeto dos arquivos
            project_ids = set()
            for version_file in self.versions_dir.glob("project_*.json*"):
                try:
                    parts = version_file.stem.split('_')
                    if len(parts) >= 2:
                        project_id = int(parts[1])
                        project_ids.add(project_id)
                except:
                    pass
            
            # Limpar cada projeto
            for project_id in project_ids:
                await self._cleanup_old_versions(project_id)
            
            logger.info(f"🧹 Limpeza concluída: {len(project_ids)} projetos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza geral: {e}")
    
    async def _delete_version_file(self, version: AutoSaveVersion):
        """Deletar arquivo de versão"""
        try:
            version_filename = f"project_{version.project_id}_v{version.version_number}_{version.id}.json"
            
            # Tentar versão comprimida primeiro
            version_path = self.versions_dir / (version_filename + ".gz")
            if version_path.exists():
                version_path.unlink()
            else:
                # Tentar versão não comprimida
                version_path = self.versions_dir / version_filename
                if version_path.exists():
                    version_path.unlink()
            
            logger.debug(f"🗑️ Versão removida: v{version.version_number}")
            
        except Exception as e:
            logger.error(f"Erro ao deletar versão: {e}")
    
    async def _update_database_project(self, project_id: int, data: Dict[str, Any]):
        """Atualizar projeto no banco de dados"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return
            
            db = get_db_session()
            project = db.query(Project).filter(Project.id == project_id).first()
            
            if project:
                project.metadata = {
                    **project.metadata,
                    **data,
                    "last_autosave": datetime.now().isoformat()
                }
                db.commit()
            
            db.close()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar projeto no banco: {e}")
    
    def _count_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> int:
        """Contar mudanças entre dois datasets"""
        try:
            old_json = json.dumps(old_data, sort_keys=True)
            new_json = json.dumps(new_data, sort_keys=True)
            
            if old_json == new_json:
                return 0
            
            # Contagem simples baseada em diferença de tamanho
            # Em produção, poderia usar algoritmo mais sofisticado
            size_diff = abs(len(new_json) - len(old_json))
            return max(1, size_diff // 100)  # 1 mudança a cada 100 chars de diff
            
        except Exception as e:
            logger.error(f"Erro ao contar mudanças: {e}")
            return 1
    
    def get_session_info(self, user_id: int, project_id: int) -> Optional[Dict[str, Any]]:
        """Obter informações da sessão"""
        try:
            if user_id in self.active_sessions and project_id in self.active_sessions[user_id]:
                session = self.active_sessions[user_id][project_id]
                
                return {
                    "session_id": session["session_id"],
                    "started_at": session["started_at"].isoformat(),
                    "last_save": session["last_save"].isoformat(),
                    "changes_count": session["changes_count"],
                    "save_count": session["save_count"],
                    "is_active": session["is_active"],
                    "next_autosave_in": max(0, self.autosave_interval - 
                                          (datetime.now() - session["last_save"]).total_seconds())
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter info da sessão: {e}")
            return None

# Instância global do serviço
autosave_service = AutoSaveService()

# Funções de conveniência
async def start_autosave():
    """Iniciar serviço de auto-save"""
    await autosave_service.start_service()

async def register_editing_session(user_id: int, project_id: int, initial_data: Dict[str, Any] = None):
    """Registrar sessão de edição"""
    return await autosave_service.register_session(user_id, project_id, initial_data)

async def update_project(user_id: int, project_id: int, data: Dict[str, Any]):
    """Atualizar dados do projeto"""
    await autosave_service.update_project_data(user_id, project_id, data)

async def manual_save_project(user_id: int, project_id: int, description: str = "Save manual"):
    """Realizar save manual"""
    return await autosave_service.manual_save(user_id, project_id, description)