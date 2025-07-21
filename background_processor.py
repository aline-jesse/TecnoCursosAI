#!/usr/bin/env python3
"""
Background Processor - TecnoCursos AI
Sistema de processamento em background para tarefas assíncronas
"""

import threading
import queue
import time
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Tipos de tarefas disponíveis"""
    CUSTOM = "custom"
    FILE_PROCESSING = "file_processing"
    VIDEO_GENERATION = "video_generation"
    AUDIO_PROCESSING = "audio_processing"
    IMAGE_PROCESSING = "image_processing"
    TEXT_EXTRACTION = "text_extraction"
    TTS_GENERATION = "tts_generation"

class TaskStatus(Enum):
    """Status das tarefas"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    """Representa uma tarefa em background"""
    
    def __init__(self, task_id: str, task_type: TaskType, parameters: Dict[str, Any]):
        self.task_id = task_id
        self.task_type = task_type
        self.parameters = parameters
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.progress = 0.0
        self.worker_id = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte tarefa para dicionário"""
        return {
            "task_id": self.task_id,
            "type": self.task_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "worker_id": self.worker_id
        }

class BackgroundProcessor:
    """Processador de tarefas em background"""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self.tasks: Dict[str, Task] = {}
        self.workers: List[threading.Thread] = []
        self.running = False
        self.lock = threading.Lock()
        
        # Handlers para diferentes tipos de tarefas
        self.task_handlers = {
            TaskType.CUSTOM: self._handle_custom_task,
            TaskType.FILE_PROCESSING: self._handle_file_processing,
            TaskType.VIDEO_GENERATION: self._handle_video_generation,
            TaskType.AUDIO_PROCESSING: self._handle_audio_processing,
            TaskType.IMAGE_PROCESSING: self._handle_image_processing,
            TaskType.TEXT_EXTRACTION: self._handle_text_extraction,
            TaskType.TTS_GENERATION: self._handle_tts_generation
        }
    
    def start(self):
        """Inicia o processador"""
        if self.running:
            logger.warning("Processador já está rodando")
            return
        
        self.running = True
        logger.info(f"Iniciando processador com {self.num_workers} workers")
        
        # Criar workers
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True,
                name=f"Worker-{i}"
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info("Processador iniciado com sucesso")
    
    def stop(self):
        """Para o processador"""
        if not self.running:
            return
        
        logger.info("Parando processador...")
        self.running = False
        
        # Aguardar workers terminarem
        for worker in self.workers:
            worker.join(timeout=5)
        
        logger.info("Processador parado")
    
    def submit_task(self, task_type: TaskType, parameters: Dict[str, Any]) -> str:
        """Submete uma nova tarefa"""
        task_id = str(uuid.uuid4())
        task = Task(task_id, task_type, parameters)
        
        with self.lock:
            self.tasks[task_id] = task
            self.task_queue.put(task)
        
        logger.info(f"Tarefa submetida: {task_id} ({task_type.value})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de uma tarefa"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                return task.to_dict()
        return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Obtém todas as tarefas"""
        with self.lock:
            return [task.to_dict() for task in self.tasks.values()]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancela uma tarefa"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Tarefa cancelada: {task_id}")
                return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do processador"""
        with self.lock:
            total_tasks = len(self.tasks)
            pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            cancelled = sum(1 for t in self.tasks.values() if t.status == TaskStatus.CANCELLED)
            
            return {
                "total_tasks": total_tasks,
                "pending": pending,
                "running": running,
                "completed": completed,
                "failed": failed,
                "cancelled": cancelled,
                "queue_size": self.task_queue.qsize(),
                "workers": len(self.workers),
                "running": self.running
            }
    
    def _worker_loop(self, worker_id: int):
        """Loop principal do worker"""
        logger.info(f"Worker {worker_id} iniciado")
        
        while self.running:
            try:
                # Pegar tarefa da fila com timeout
                task = self.task_queue.get(timeout=1)
                
                # Processar tarefa
                self._process_task(task, worker_id)
                
                # Marcar tarefa como concluída
                self.task_queue.task_done()
                
            except queue.Empty:
                # Timeout - continuar loop
                continue
            except Exception as e:
                logger.error(f"Erro no worker {worker_id}: {e}")
        
        logger.info(f"Worker {worker_id} finalizado")
    
    def _process_task(self, task: Task, worker_id: int):
        """Processa uma tarefa"""
        try:
            # Atualizar status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task.worker_id = worker_id
            
            logger.info(f"🔄 Processando tarefa {task.task_id} ({task.task_type.value})")
            
            # Obter handler para o tipo de tarefa
            handler = self.task_handlers.get(task.task_type, self._handle_custom_task)
            
            # Executar tarefa
            result = handler(task)
            
            # Atualizar resultado
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 100.0
            
            logger.info(f"✅ Tarefa {task.task_id} concluída com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na tarefa {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
    
    def _handle_custom_task(self, task: Task) -> Dict[str, Any]:
        """Handler para tarefas customizadas"""
        # Simular processamento
        time.sleep(2)
        task.progress = 50.0
        time.sleep(2)
        
        return {
            "message": "Tarefa customizada executada",
            "parameters": task.parameters,
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_file_processing(self, task: Task) -> Dict[str, Any]:
        """Handler para processamento de arquivos"""
        file_path = task.parameters.get("file_path")
        if not file_path:
            raise ValueError("file_path é obrigatório")
        
        # Simular processamento de arquivo
        task.progress = 25.0
        time.sleep(1)
        
        task.progress = 50.0
        time.sleep(1)
        
        task.progress = 75.0
        time.sleep(1)
        
        return {
            "message": "Arquivo processado com sucesso",
            "file_path": file_path,
            "processed_at": datetime.now().isoformat()
        }
    
    def _handle_video_generation(self, task: Task) -> Dict[str, Any]:
        """Handler para geração de vídeos"""
        # Simular geração de vídeo
        task.progress = 10.0
        time.sleep(1)
        
        task.progress = 30.0
        time.sleep(1)
        
        task.progress = 60.0
        time.sleep(1)
        
        task.progress = 90.0
        time.sleep(1)
        
        return {
            "message": "Vídeo gerado com sucesso",
            "video_path": f"/static/videos/video_{task.task_id}.mp4",
            "duration": 30.0,
            "generated_at": datetime.now().isoformat()
        }
    
    def _handle_audio_processing(self, task: Task) -> Dict[str, Any]:
        """Handler para processamento de áudio"""
        # Simular processamento de áudio
        task.progress = 20.0
        time.sleep(1)
        
        task.progress = 60.0
        time.sleep(1)
        
        task.progress = 100.0
        
        return {
            "message": "Áudio processado com sucesso",
            "audio_path": f"/static/audios/audio_{task.task_id}.mp3",
            "duration": 15.0,
            "processed_at": datetime.now().isoformat()
        }
    
    def _handle_image_processing(self, task: Task) -> Dict[str, Any]:
        """Handler para processamento de imagens"""
        # Simular processamento de imagem
        task.progress = 40.0
        time.sleep(1)
        
        task.progress = 80.0
        time.sleep(1)
        
        return {
            "message": "Imagem processada com sucesso",
            "image_path": f"/static/images/image_{task.task_id}.jpg",
            "processed_at": datetime.now().isoformat()
        }
    
    def _handle_text_extraction(self, task: Task) -> Dict[str, Any]:
        """Handler para extração de texto"""
        # Simular extração de texto
        task.progress = 30.0
        time.sleep(1)
        
        task.progress = 70.0
        time.sleep(1)
        
        return {
            "message": "Texto extraído com sucesso",
            "text_length": 1500,
            "pages": 3,
            "extracted_at": datetime.now().isoformat()
        }
    
    def _handle_tts_generation(self, task: Task) -> Dict[str, Any]:
        """Handler para geração de TTS"""
        text = task.parameters.get("text", "")
        
        # Simular geração de TTS
        task.progress = 20.0
        time.sleep(1)
        
        task.progress = 50.0
        time.sleep(1)
        
        task.progress = 80.0
        time.sleep(1)
        
        return {
            "message": "TTS gerado com sucesso",
            "text_length": len(text),
            "audio_path": f"/static/audios/tts_{task.task_id}.mp3",
            "duration": len(text) / 10.0,  # Estimativa
            "generated_at": datetime.now().isoformat()
        }

# Instância global do processador
_processor = None

def start_background_processor(num_workers: int = 4):
    """Inicia o processador em background"""
    global _processor
    if _processor is None:
        _processor = BackgroundProcessor(num_workers)
    _processor.start()

def stop_background_processor():
    """Para o processador em background"""
    global _processor
    if _processor:
        _processor.stop()

def submit_background_task(task_type: TaskType, parameters: Dict[str, Any]) -> str:
    """Submete uma tarefa em background"""
    global _processor
    if not _processor:
        raise RuntimeError("Processador não iniciado")
    return _processor.submit_task(task_type, parameters)

def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Obtém status de uma tarefa"""
    global _processor
    if not _processor:
        return None
    return _processor.get_task_status(task_id)

def get_all_tasks() -> List[Dict[str, Any]]:
    """Obtém todas as tarefas"""
    global _processor
    if not _processor:
        return []
    return _processor.get_all_tasks()

def cancel_task(task_id: str) -> bool:
    """Cancela uma tarefa"""
    global _processor
    if not _processor:
        return False
    return _processor.cancel_task(task_id)

def get_processor_stats() -> Dict[str, Any]:
    """Obtém estatísticas do processador"""
    global _processor
    if not _processor:
        return {
            "total_tasks": 0,
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "queue_size": 0,
            "workers": 0,
            "running": False
        }
    return _processor.get_stats()

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 Testando processador em background...")
    
    # Iniciar processador
    start_background_processor(2)
    
    # Submeter algumas tarefas
    task1 = submit_background_task(TaskType.FILE_PROCESSING, {"file_path": "/test/file1.pdf"})
    task2 = submit_background_task(TaskType.VIDEO_GENERATION, {"template": "professional"})
    task3 = submit_background_task(TaskType.TTS_GENERATION, {"text": "Olá, mundo!"})
    
    print(f"Tarefas submetidas: {task1}, {task2}, {task3}")
    
    # Aguardar um pouco
    time.sleep(5)
    
    # Verificar status
    stats = get_processor_stats()
    print(f"Estatísticas: {stats}")
    
    # Parar processador
    stop_background_processor()
    
    print("✅ Teste concluído!") 