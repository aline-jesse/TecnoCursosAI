"""
Serviço de Processamento Assíncrono de Áudios
============================================

Sistema avançado para processamento assíncrono de arquivos grandes:
- Fila de processamento com prioridades
- Workers paralelos para processamento
- Notificações de progresso em tempo real
- Retry automático em caso de falhas
- Monitoramento de recursos do sistema

Funcionalidades:
1. Processamento em background para arquivos grandes
2. Sistema de filas com Redis ou memória
3. Workers escaláveis
4. WebSocket para notificações em tempo real
5. Políticas de retry inteligentes
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Dependências opcionais
try:
    import redis
    _redis_available = True
except ImportError:
    _redis_available = False

try:
    import psutil
    _psutil_available = True
except ImportError:
    _psutil_available = False

from app.config import get_settings
from app.database import get_db_session
from app.models import Audio, User, FileUpload

logger = logging.getLogger(__name__)
settings = get_settings()

class ProcessingStatus(Enum):
    """Status do processamento assíncrono"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"

class Priority(Enum):
    """Prioridades de processamento"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class ProcessingTask:
    """Tarefa de processamento assíncrono"""
    id: str
    user_id: int
    file_upload_id: int
    file_path: str
    extracted_text: str
    output_path: str
    
    # Configurações TTS
    voice: str = "v2/pt_speaker_0"
    provider: str = "auto"
    
    # Metadados da tarefa
    priority: Priority = Priority.NORMAL
    status: ProcessingStatus = ProcessingStatus.QUEUED
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progresso e resultado
    progress: float = 0.0
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Resultado
    audio_id: Optional[int] = None
    audio_path: Optional[str] = None
    duration: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Converter para dicionário"""
        data = asdict(self)
        # Converter enums e datetime para strings
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProcessingTask':
        """Criar a partir de dicionário"""
        # Converter strings de volta para enums e datetime
        if 'priority' in data:
            data['priority'] = Priority(data['priority'])
        if 'status' in data:
            data['status'] = ProcessingStatus(data['status'])
        for field in ['created_at', 'started_at', 'completed_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)

class AsyncAudioProcessor:
    """Processador assíncrono de áudios"""
    
    def __init__(self):
        self.tasks: Dict[str, ProcessingTask] = {}
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.max_workers = 3
        self.worker_semaphore = asyncio.Semaphore(self.max_workers)
        
        # Callbacks para notificações
        self.progress_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        
        # Redis para persistência (se disponível)
        self.redis_client = None
        if _redis_available:
            try:
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'redis_host', 'localhost'),
                    port=getattr(settings, 'redis_port', 6379),
                    db=getattr(settings, 'redis_db', 0),
                    decode_responses=True
                )
                # Testar conexão
                self.redis_client.ping()
                logger.info("✅ Conectado ao Redis para processamento assíncrono")
            except Exception as e:
                logger.warning(f"⚠️ Redis não disponível, usando memória: {e}")
                self.redis_client = None
    
    async def start(self):
        """Iniciar o serviço de processamento"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🚀 Iniciando serviço de processamento assíncrono")
        
        # Carregar tarefas persistidas
        await self._load_persisted_tasks()
        
        # Iniciar workers
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"✅ {self.max_workers} workers iniciados")
    
    async def stop(self):
        """Parar o serviço de processamento"""
        if not self.is_running:
            return
        
        logger.info("🛑 Parando serviço de processamento assíncrono")
        self.is_running = False
        
        # Persistir tarefas pendentes
        await self._persist_tasks()
        
        # Cancelar workers
        for worker in self.workers:
            worker.cancel()
        
        # Aguardar finalização
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("✅ Serviço de processamento parado")
    
    async def submit_task(
        self,
        user_id: int,
        file_upload_id: int,
        file_path: str,
        extracted_text: str,
        output_path: str,
        voice: str = "v2/pt_speaker_0",
        provider: str = "auto",
        priority: Priority = Priority.NORMAL
    ) -> str:
        """
        Submeter tarefa para processamento assíncrono
        
        Returns:
            Task ID para acompanhamento
        """
        task_id = str(uuid.uuid4())
        
        task = ProcessingTask(
            id=task_id,
            user_id=user_id,
            file_upload_id=file_upload_id,
            file_path=file_path,
            extracted_text=extracted_text,
            output_path=output_path,
            voice=voice,
            provider=provider,
            priority=priority
        )
        
        # Adicionar à fila
        self.tasks[task_id] = task
        await self._persist_task(task)
        
        logger.info(f"📝 Tarefa submetida: {task_id} (prioridade: {priority.name})")
        
        # Notificar sobre nova tarefa
        await self._notify_progress(task)
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Obter status de uma tarefa"""
        task = self.tasks.get(task_id)
        if not task:
            # Tentar carregar do Redis
            task = await self._load_task(task_id)
        
        if task:
            return task.to_dict()
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancelar uma tarefa"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            return False
        
        task.status = ProcessingStatus.CANCELLED
        await self._persist_task(task)
        
        logger.info(f"❌ Tarefa cancelada: {task_id}")
        await self._notify_progress(task)
        
        return True
    
    async def get_user_tasks(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Obter tarefas de um usuário"""
        user_tasks = []
        
        for task in self.tasks.values():
            if task.user_id == user_id:
                user_tasks.append(task.to_dict())
        
        # Ordenar por data de criação (mais recentes primeiro)
        user_tasks.sort(key=lambda x: x['created_at'], reverse=True)
        
        return user_tasks[:limit]
    
    async def get_queue_stats(self) -> Dict:
        """Obter estatísticas da fila"""
        stats = {
            "total_tasks": len(self.tasks),
            "by_status": {},
            "by_priority": {},
            "avg_processing_time": 0.0,
            "active_workers": len([w for w in self.workers if not w.done()]),
            "system_resources": {}
        }
        
        # Contar por status e prioridade
        for task in self.tasks.values():
            status = task.status.value
            priority = task.priority.name
            
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        # Calcular tempo médio de processamento
        completed_tasks = [t for t in self.tasks.values() if t.status == ProcessingStatus.COMPLETED]
        if completed_tasks:
            processing_times = []
            for task in completed_tasks:
                if task.started_at and task.completed_at:
                    duration = (task.completed_at - task.started_at).total_seconds()
                    processing_times.append(duration)
            
            if processing_times:
                stats["avg_processing_time"] = sum(processing_times) / len(processing_times)
        
        # Recursos do sistema (se psutil disponível)
        if _psutil_available:
            stats["system_resources"] = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        
        return stats
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Limpar tarefas antigas da memória"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        old_task_ids = []
        for task_id, task in self.tasks.items():
            if task.completed_at and task.completed_at < cutoff_time:
                old_task_ids.append(task_id)
        
        for task_id in old_task_ids:
            del self.tasks[task_id]
            if self.redis_client:
                try:
                    self.redis_client.delete(f"audio_task:{task_id}")
                except Exception as e:
                    logger.error(f"Erro ao remover tarefa do Redis: {e}")
        
        if old_task_ids:
            logger.info(f"🧹 {len(old_task_ids)} tarefas antigas removidas da memória")
    
    # Métodos privados
    async def _worker_loop(self, worker_name: str):
        """Loop principal do worker"""
        logger.info(f"👷 Worker {worker_name} iniciado")
        
        while self.is_running:
            try:
                # Buscar próxima tarefa
                task = await self._get_next_task()
                
                if task:
                    async with self.worker_semaphore:
                        await self._process_task(task, worker_name)
                else:
                    # Não há tarefas, aguardar um pouco
                    await asyncio.sleep(1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no worker {worker_name}: {e}", exc_info=True)
                await asyncio.sleep(5)  # Aguardar antes de continuar
        
        logger.info(f"👷 Worker {worker_name} finalizado")
    
    async def _get_next_task(self) -> Optional[ProcessingTask]:
        """Obter próxima tarefa para processamento"""
        # Filtrar tarefas que podem ser processadas
        eligible_tasks = []
        
        for task in self.tasks.values():
            if task.status == ProcessingStatus.QUEUED:
                eligible_tasks.append(task)
            elif task.status == ProcessingStatus.RETRY:
                # Verificar se já passou o tempo de retry
                if task.started_at:
                    retry_delay = 60 * (2 ** task.retry_count)  # Backoff exponencial
                    if datetime.now() > task.started_at + timedelta(seconds=retry_delay):
                        eligible_tasks.append(task)
        
        if not eligible_tasks:
            return None
        
        # Ordenar por prioridade e depois por data de criação
        eligible_tasks.sort(
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )
        
        return eligible_tasks[0]
    
    async def _process_task(self, task: ProcessingTask, worker_name: str):
        """Processar uma tarefa específica"""
        logger.info(f"🔄 {worker_name} processando tarefa {task.id}")
        
        # Atualizar status
        task.status = ProcessingStatus.PROCESSING
        task.started_at = datetime.now()
        task.progress = 0.0
        await self._persist_task(task)
        await self._notify_progress(task)
        
        try:
            # Importar função de geração de narração
            from app.utils import generate_narration_sync
            
            # Simular progresso durante processamento
            await self._update_progress(task, 10.0)
            
            # Gerar narração
            result = generate_narration_sync(
                text=task.extracted_text,
                output_path=task.output_path,
                voice=task.voice,
                provider=task.provider
            )
            
            await self._update_progress(task, 80.0)
            
            if result.get('success'):
                # Salvar no banco de dados
                await self._save_audio_to_db(task, result)
                await self._update_progress(task, 100.0)
                
                # Marcar como concluída
                task.status = ProcessingStatus.COMPLETED
                task.completed_at = datetime.now()
                task.audio_path = result.get('audio_path')
                task.duration = result.get('duration')
                
                logger.info(f"✅ Tarefa {task.id} concluída com sucesso")
                
            else:
                raise Exception(result.get('error', 'Erro desconhecido na geração'))
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar tarefa {task.id}: {e}")
            
            task.error_message = str(e)
            task.retry_count += 1
            
            if task.retry_count <= task.max_retries:
                task.status = ProcessingStatus.RETRY
                logger.info(f"🔄 Tarefa {task.id} será tentada novamente ({task.retry_count}/{task.max_retries})")
            else:
                task.status = ProcessingStatus.FAILED
                task.completed_at = datetime.now()
                logger.error(f"💀 Tarefa {task.id} falhou definitivamente")
        
        await self._persist_task(task)
        await self._notify_progress(task)
        await self._notify_completion(task)
    
    async def _save_audio_to_db(self, task: ProcessingTask, result: Dict):
        """Salvar áudio no banco de dados"""
        db = next(get_db_session())
        try:
            # Importar modelo
            from app.models import Audio
            
            # Calcular tamanho do arquivo
            audio_path = Path(task.output_path)
            file_size = audio_path.stat().st_size if audio_path.exists() else 0
            
            # Criar registro de áudio
            db_audio = Audio(
                uuid=str(uuid.uuid4()),
                title=f"Narração processada assincronamente",
                description=f"Gerada a partir da tarefa {task.id}",
                filename=audio_path.name,
                file_path=str(audio_path),
                file_size=file_size,
                duration=result.get('duration'),
                format="mp3",
                bitrate=result.get('metadata', {}).get('bitrate', '128k'),
                sample_rate=result.get('metadata', {}).get('sample_rate'),
                extracted_text=task.extracted_text,
                text_length=len(task.extracted_text),
                tts_provider=result.get('provider', task.provider),
                voice_type=task.voice,
                status="completed",
                generation_progress=100.0,
                processing_time=result.get('processing_time'),
                cache_hit=result.get('cache_hit', False),
                user_id=task.user_id,
                source_file_id=task.file_upload_id,
                completed_at=datetime.now()
            )
            
            db.add(db_audio)
            db.commit()
            db.refresh(db_audio)
            
            task.audio_id = db_audio.id
            
        finally:
            db.close()
    
    async def _update_progress(self, task: ProcessingTask, progress: float):
        """Atualizar progresso da tarefa"""
        task.progress = progress
        await self._persist_task(task)
        await self._notify_progress(task)
    
    async def _persist_task(self, task: ProcessingTask):
        """Persistir tarefa no Redis (se disponível)"""
        if self.redis_client:
            try:
                key = f"audio_task:{task.id}"
                data = json.dumps(task.to_dict())
                self.redis_client.setex(key, 86400, data)  # 24 horas TTL
            except Exception as e:
                logger.error(f"Erro ao persistir tarefa {task.id}: {e}")
    
    async def _load_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Carregar tarefa do Redis"""
        if self.redis_client:
            try:
                key = f"audio_task:{task_id}"
                data = self.redis_client.get(key)
                if data:
                    task_dict = json.loads(data)
                    return ProcessingTask.from_dict(task_dict)
            except Exception as e:
                logger.error(f"Erro ao carregar tarefa {task_id}: {e}")
        return None
    
    async def _persist_tasks(self):
        """Persistir todas as tarefas"""
        for task in self.tasks.values():
            await self._persist_task(task)
    
    async def _load_persisted_tasks(self):
        """Carregar tarefas persistidas"""
        if self.redis_client:
            try:
                keys = self.redis_client.keys("audio_task:*")
                for key in keys:
                    task_id = key.split(":")[-1]
                    task = await self._load_task(task_id)
                    if task:
                        self.tasks[task_id] = task
                
                if keys:
                    logger.info(f"📥 {len(keys)} tarefas carregadas do Redis")
            except Exception as e:
                logger.error(f"Erro ao carregar tarefas persistidas: {e}")
    
    async def _notify_progress(self, task: ProcessingTask):
        """Notificar callbacks sobre progresso"""
        for callback in self.progress_callbacks:
            try:
                await callback(task)
            except Exception as e:
                logger.error(f"Erro em callback de progresso: {e}")
    
    async def _notify_completion(self, task: ProcessingTask):
        """Notificar callbacks sobre conclusão"""
        if task.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            for callback in self.completion_callbacks:
                try:
                    await callback(task)
                except Exception as e:
                    logger.error(f"Erro em callback de conclusão: {e}")
    
    def add_progress_callback(self, callback: Callable):
        """Adicionar callback para notificações de progresso"""
        self.progress_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable):
        """Adicionar callback para notificações de conclusão"""
        self.completion_callbacks.append(callback)

# Instância global do processador
async_processor = AsyncAudioProcessor()

# Funções de conveniência
async def submit_async_audio_task(
    user_id: int,
    file_upload_id: int,
    file_path: str,
    extracted_text: str,
    output_path: str,
    voice: str = "v2/pt_speaker_0",
    provider: str = "auto",
    priority: Priority = Priority.NORMAL
) -> str:
    """Submeter tarefa de processamento assíncrono"""
    return await async_processor.submit_task(
        user_id, file_upload_id, file_path, extracted_text, 
        output_path, voice, provider, priority
    )

async def get_async_task_status(task_id: str) -> Optional[Dict]:
    """Obter status de tarefa assíncrona"""
    return await async_processor.get_task_status(task_id)

async def start_async_processor():
    """Iniciar processador assíncrono"""
    await async_processor.start()

async def stop_async_processor():
    """Parar processador assíncrono"""
    await async_processor.stop() 