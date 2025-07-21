#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Processamento em Lote TTS - TecnoCursos AI
===================================================

Sistema avançado para processamento em lote de múltiplos textos,
otimização de recursos e gerenciamento de filas.
"""

import asyncio
import os
import uuid
import time
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import logging

# Imports condicionais
try:
    from app.utils import generate_narration, TTS_AVAILABLE
    from services.tts_service import TTSConfig, TTSProvider
    TTS_UTILS_AVAILABLE = True
except ImportError:
    TTS_UTILS_AVAILABLE = False
    print("⚠️ Utilities TTS não disponíveis")

logger = logging.getLogger(__name__)

class BatchStatus(Enum):
    """Status do processamento em lote"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """Status de tarefa individual"""
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TTSTask:
    """Tarefa individual de TTS"""
    id: str
    text: str
    output_path: str
    voice: Optional[str] = None
    provider: str = "auto"
    language: str = "pt"
    status: TaskStatus = TaskStatus.WAITING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict] = None
    duration: float = 0.0
    file_size: int = 0
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class BatchRequest:
    """Requisição de processamento em lote"""
    id: str
    user_id: Optional[str] = None
    tasks: List[TTSTask] = field(default_factory=list)
    status: BatchStatus = BatchStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_directory: str = ""
    progress: float = 0.0
    total_duration: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    metadata: Dict = field(default_factory=dict)
    webhook_url: Optional[str] = None
    callback: Optional[Callable] = None

class TTSBatchProcessor:
    """Processador em lote para TTS"""
    
    def __init__(self, max_concurrent_tasks: int = 3, cache_dir: str = "cache/tts_batch"):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado interno
        self.active_batches: Dict[str, BatchRequest] = {}
        self.task_queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.is_running = False
        self.workers: List[asyncio.Task] = []
        
        # Métricas
        self.total_processed = 0
        self.total_errors = 0
        self.start_time = time.time()
        
    async def start_workers(self):
        """Iniciar workers de processamento"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Criar workers
        for i in range(self.max_concurrent_tasks):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
            
        logger.info(f"Iniciados {len(self.workers)} workers TTS")
        
    async def stop_workers(self):
        """Parar workers de processamento"""
        self.is_running = False
        
        # Cancelar workers
        for worker in self.workers:
            worker.cancel()
            
        # Aguardar conclusão
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Workers TTS parados")
        
    async def create_batch(
        self,
        texts: List[str],
        output_directory: str = None,
        voice: Optional[str] = None,
        provider: str = "auto",
        language: str = "pt",
        user_id: Optional[str] = None,
        webhook_url: Optional[str] = None
    ) -> str:
        """
        Criar novo lote de processamento
        
        Args:
            texts: Lista de textos para processar
            output_directory: Diretório de saída
            voice: Voz específica a usar
            provider: Provedor TTS
            language: Idioma
            user_id: ID do usuário
            webhook_url: URL para webhook de notificação
            
        Returns:
            ID do lote criado
        """
        
        if not TTS_UTILS_AVAILABLE:
            raise RuntimeError("Serviços TTS não disponíveis")
            
        # Gerar ID único
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        
        # Configurar diretório de saída
        if not output_directory:
            output_directory = str(self.cache_dir / batch_id)
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        
        # Criar tarefas
        tasks = []
        for i, text in enumerate(texts):
            if not text or not text.strip():
                continue
                
            task_id = f"{batch_id}_task_{i:03d}"
            filename = f"narration_{i:03d}.mp3"
            output_path = os.path.join(output_directory, filename)
            
            task = TTSTask(
                id=task_id,
                text=text.strip(),
                output_path=output_path,
                voice=voice,
                provider=provider,
                language=language
            )
            tasks.append(task)
        
        # Criar requisição de lote
        batch = BatchRequest(
            id=batch_id,
            user_id=user_id,
            tasks=tasks,
            output_directory=output_directory,
            webhook_url=webhook_url,
            metadata={
                "total_texts": len(texts),
                "valid_tasks": len(tasks),
                "voice": voice,
                "provider": provider,
                "language": language
            }
        )
        
        # Armazenar lote
        self.active_batches[batch_id] = batch
        
        # Salvar estado
        await self._save_batch_state(batch)
        
        logger.info(f"Lote criado: {batch_id} com {len(tasks)} tarefas")
        
        return batch_id
        
    async def start_batch_processing(self, batch_id: str) -> bool:
        """Iniciar processamento de um lote"""
        
        if batch_id not in self.active_batches:
            logger.error(f"Lote não encontrado: {batch_id}")
            return False
            
        batch = self.active_batches[batch_id]
        
        if batch.status != BatchStatus.PENDING:
            logger.warning(f"Lote {batch_id} já está em processamento ou concluído")
            return False
            
        # Atualizar status
        batch.status = BatchStatus.PROCESSING
        batch.started_at = datetime.now()
        
        # Adicionar tarefas à fila
        for task in batch.tasks:
            await self.task_queue.put((batch_id, task))
            
        await self._save_batch_state(batch)
        
        logger.info(f"Iniciado processamento do lote: {batch_id}")
        
        return True
        
    async def _worker(self, worker_name: str):
        """Worker para processar tarefas TTS"""
        
        logger.info(f"Worker {worker_name} iniciado")
        
        try:
            while self.is_running:
                try:
                    # Aguardar tarefa com timeout
                    batch_id, task = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                    
                    # Processar tarefa
                    await self._process_task(batch_id, task, worker_name)
                    
                except asyncio.TimeoutError:
                    continue  # Timeout normal, continuar loop
                except Exception as e:
                    logger.error(f"Erro no worker {worker_name}: {e}")
                    
        except asyncio.CancelledError:
            logger.info(f"Worker {worker_name} cancelado")
            raise
        except Exception as e:
            logger.error(f"Erro fatal no worker {worker_name}: {e}")
            
    async def _process_task(self, batch_id: str, task: TTSTask, worker_name: str):
        """Processar tarefa individual"""
        
        async with self.semaphore:
            if batch_id not in self.active_batches:
                return
                
            batch = self.active_batches[batch_id]
            
            # Atualizar status da tarefa
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
            
            logger.info(f"[{worker_name}] Processando tarefa {task.id}")
            
            try:
                # Executar geração TTS
                result = await generate_narration(
                    text=task.text,
                    output_path=task.output_path,
                    voice=task.voice,
                    provider=task.provider,
                    language=task.language
                )
                
                # Atualizar resultado
                task.result = result
                task.completed_at = datetime.now()
                
                if result['success']:
                    task.status = TaskStatus.COMPLETED
                    task.duration = result['duration']
                    
                    # Obter tamanho do arquivo
                    if os.path.exists(result['audio_path']):
                        task.file_size = os.path.getsize(result['audio_path'])
                    
                    batch.success_count += 1
                    batch.total_duration += task.duration
                    
                    logger.info(f"[{worker_name}] Tarefa {task.id} concluída com sucesso")
                    
                else:
                    task.status = TaskStatus.FAILED
                    task.error = result['error']
                    batch.failure_count += 1
                    
                    logger.error(f"[{worker_name}] Tarefa {task.id} falhou: {task.error}")
                    
                    # Retry se necessário
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.WAITING
                        await self.task_queue.put((batch_id, task))
                        logger.info(f"Tentativa {task.retry_count}/{task.max_retries} para tarefa {task.id}")
                        return
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = f"Exceção: {str(e)}"
                task.completed_at = datetime.now()
                batch.failure_count += 1
                
                logger.error(f"[{worker_name}] Exceção na tarefa {task.id}: {e}")
                
            # Atualizar progresso do lote
            completed_tasks = sum(1 for t in batch.tasks if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED])
            batch.progress = (completed_tasks / len(batch.tasks)) * 100
            
            # Verificar se o lote foi concluído
            if completed_tasks == len(batch.tasks):
                await self._complete_batch(batch)
                
            # Salvar estado
            await self._save_batch_state(batch)
            
            # Atualizar métricas globais
            self.total_processed += 1
            if task.status == TaskStatus.FAILED:
                self.total_errors += 1
                
    async def _complete_batch(self, batch: BatchRequest):
        """Completar processamento do lote"""
        
        batch.status = BatchStatus.COMPLETED
        batch.completed_at = datetime.now()
        batch.progress = 100.0
        
        # Gerar relatório
        report = await self._generate_batch_report(batch)
        
        # Salvar relatório
        report_path = os.path.join(batch.output_directory, "batch_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
        logger.info(f"Lote {batch.id} concluído: {batch.success_count} sucessos, {batch.failure_count} falhas")
        
        # Executar callback se definido
        if batch.callback:
            try:
                await batch.callback(batch, report)
            except Exception as e:
                logger.error(f"Erro no callback do lote {batch.id}: {e}")
                
        # Enviar webhook se definido
        if batch.webhook_url:
            await self._send_webhook(batch, report)
            
    async def _send_webhook(self, batch: BatchRequest, report: Dict):
        """Enviar webhook de notificação"""
        try:
            import aiohttp
            
            payload = {
                "batch_id": batch.id,
                "status": batch.status.value,
                "user_id": batch.user_id,
                "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
                "success_count": batch.success_count,
                "failure_count": batch.failure_count,
                "total_duration": batch.total_duration,
                "progress": batch.progress,
                "report": report
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    batch.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook enviado com sucesso para lote {batch.id}")
                    else:
                        logger.warning(f"Webhook falhou para lote {batch.id}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erro ao enviar webhook para lote {batch.id}: {e}")
            
    async def _generate_batch_report(self, batch: BatchRequest) -> Dict:
        """Gerar relatório detalhado do lote"""
        
        # Estatísticas por status
        status_stats = {}
        for status in TaskStatus:
            count = sum(1 for task in batch.tasks if task.status == status)
            status_stats[status.value] = count
            
        # Estatísticas por provedor
        provider_stats = {}
        for task in batch.tasks:
            if task.result and task.result.get('provider_used'):
                provider = task.result['provider_used']
                if provider not in provider_stats:
                    provider_stats[provider] = {"count": 0, "total_duration": 0.0}
                provider_stats[provider]["count"] += 1
                provider_stats[provider]["total_duration"] += task.duration
                
        # Tempo de processamento
        processing_time = None
        if batch.started_at and batch.completed_at:
            processing_time = (batch.completed_at - batch.started_at).total_seconds()
            
        # Arquivos gerados
        generated_files = []
        total_size = 0
        for task in batch.tasks:
            if task.status == TaskStatus.COMPLETED and os.path.exists(task.output_path):
                file_info = {
                    "task_id": task.id,
                    "filename": os.path.basename(task.output_path),
                    "path": task.output_path,
                    "size": task.file_size,
                    "duration": task.duration,
                    "provider": task.result.get('provider_used') if task.result else None
                }
                generated_files.append(file_info)
                total_size += task.file_size
                
        # Erros por categoria
        error_categories = {}
        for task in batch.tasks:
            if task.status == TaskStatus.FAILED and task.error:
                error_key = task.error[:50]  # Primeiros 50 caracteres
                error_categories[error_key] = error_categories.get(error_key, 0) + 1
                
        report = {
            "batch_id": batch.id,
            "user_id": batch.user_id,
            "created_at": batch.created_at,
            "started_at": batch.started_at,
            "completed_at": batch.completed_at,
            "processing_time_seconds": processing_time,
            "status": batch.status.value,
            "progress": batch.progress,
            "summary": {
                "total_tasks": len(batch.tasks),
                "success_count": batch.success_count,
                "failure_count": batch.failure_count,
                "total_duration": batch.total_duration,
                "total_file_size": total_size,
                "average_task_duration": batch.total_duration / max(batch.success_count, 1)
            },
            "status_breakdown": status_stats,
            "provider_stats": provider_stats,
            "generated_files": generated_files,
            "error_categories": error_categories,
            "metadata": batch.metadata
        }
        
        return report
        
    async def _save_batch_state(self, batch: BatchRequest):
        """Salvar estado do lote"""
        try:
            state_file = self.cache_dir / f"{batch.id}_state.json"
            
            # Serializar estado
            state = {
                "id": batch.id,
                "user_id": batch.user_id,
                "status": batch.status.value,
                "created_at": batch.created_at.isoformat(),
                "started_at": batch.started_at.isoformat() if batch.started_at else None,
                "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
                "output_directory": batch.output_directory,
                "progress": batch.progress,
                "success_count": batch.success_count,
                "failure_count": batch.failure_count,
                "total_duration": batch.total_duration,
                "metadata": batch.metadata,
                "webhook_url": batch.webhook_url,
                "tasks": [
                    {
                        "id": task.id,
                        "text": task.text[:100] + "..." if len(task.text) > 100 else task.text,
                        "output_path": task.output_path,
                        "voice": task.voice,
                        "provider": task.provider,
                        "language": task.language,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat(),
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "error": task.error,
                        "duration": task.duration,
                        "file_size": task.file_size,
                        "retry_count": task.retry_count
                    }
                    for task in batch.tasks
                ]
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao salvar estado do lote {batch.id}: {e}")
            
    async def get_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Obter status detalhado de um lote"""
        
        if batch_id not in self.active_batches:
            # Tentar carregar do cache
            await self._load_batch_state(batch_id)
            
        if batch_id not in self.active_batches:
            return None
            
        batch = self.active_batches[batch_id]
        
        return {
            "id": batch.id,
            "status": batch.status.value,
            "progress": batch.progress,
            "success_count": batch.success_count,
            "failure_count": batch.failure_count,
            "total_tasks": len(batch.tasks),
            "total_duration": batch.total_duration,
            "created_at": batch.created_at,
            "started_at": batch.started_at,
            "completed_at": batch.completed_at,
            "output_directory": batch.output_directory,
            "metadata": batch.metadata
        }
        
    async def _load_batch_state(self, batch_id: str):
        """Carregar estado do lote do cache"""
        try:
            state_file = self.cache_dir / f"{batch_id}_state.json"
            
            if not state_file.exists():
                return
                
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            # Reconstruir objeto BatchRequest
            # (implementação simplificada - em produção seria mais robusta)
            logger.info(f"Estado do lote {batch_id} carregado do cache")
            
        except Exception as e:
            logger.error(f"Erro ao carregar estado do lote {batch_id}: {e}")
            
    async def cancel_batch(self, batch_id: str) -> bool:
        """Cancelar processamento de um lote"""
        
        if batch_id not in self.active_batches:
            return False
            
        batch = self.active_batches[batch_id]
        
        if batch.status in [BatchStatus.COMPLETED, BatchStatus.CANCELLED]:
            return False
            
        batch.status = BatchStatus.CANCELLED
        batch.completed_at = datetime.now()
        
        # Cancelar tarefas pendentes
        for task in batch.tasks:
            if task.status == TaskStatus.WAITING:
                task.status = TaskStatus.SKIPPED
                
        await self._save_batch_state(batch)
        
        logger.info(f"Lote {batch_id} cancelado")
        
        return True
        
    def get_processor_stats(self) -> Dict:
        """Obter estatísticas do processador"""
        
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "total_processed": self.total_processed,
            "total_errors": self.total_errors,
            "success_rate": (self.total_processed - self.total_errors) / max(self.total_processed, 1) * 100,
            "active_batches": len(self.active_batches),
            "queue_size": self.task_queue.qsize(),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "workers_running": len([w for w in self.workers if not w.done()]),
            "is_running": self.is_running
        }


# Instância global do processador
tts_batch_processor = TTSBatchProcessor()

# Funções de conveniência
async def create_tts_batch(
    texts: List[str],
    output_directory: str = None,
    voice: Optional[str] = None,
    provider: str = "auto",
    language: str = "pt",
    user_id: Optional[str] = None,
    webhook_url: Optional[str] = None
) -> str:
    """Criar e iniciar novo lote TTS"""
    
    # Garantir que workers estão rodando
    if not tts_batch_processor.is_running:
        await tts_batch_processor.start_workers()
        
    # Criar lote
    batch_id = await tts_batch_processor.create_batch(
        texts=texts,
        output_directory=output_directory,
        voice=voice,
        provider=provider,
        language=language,
        user_id=user_id,
        webhook_url=webhook_url
    )
    
    # Iniciar processamento
    await tts_batch_processor.start_batch_processing(batch_id)
    
    return batch_id

async def get_tts_batch_status(batch_id: str) -> Optional[Dict]:
    """Obter status de um lote TTS"""
    return await tts_batch_processor.get_batch_status(batch_id)

async def cancel_tts_batch(batch_id: str) -> bool:
    """Cancelar lote TTS"""
    return await tts_batch_processor.cancel_batch(batch_id)

def get_tts_processor_stats() -> Dict:
    """Obter estatísticas do processador TTS"""
    return tts_batch_processor.get_processor_stats() 