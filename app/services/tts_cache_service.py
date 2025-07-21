#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cache Inteligente TTS - TecnoCursos AI
===============================================

Cache avançado para otimizar performance, reduzir custos e melhorar
experiência do usuário com TTS.
"""

import hashlib
import os
import json
import time
import asyncio
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sqlite3
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Entrada do cache TTS"""
    cache_key: str
    text_hash: str
    original_text: str
    audio_path: str
    provider: str
    voice: Optional[str]
    language: str
    duration: float
    file_size: int
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    metadata: Dict = field(default_factory=dict)

class TTSCacheManager:
    """Gerenciador de cache para TTS"""
    
    def __init__(self, cache_dir: str = "cache/tts", max_size_gb: float = 5.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)  # GB para bytes
        self.db_path = self.cache_dir / "tts_cache.db"
        self.lock = Lock()
        
        # Estatísticas
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Inicializar banco de dados
        self._init_database()
        
        # Carregar estatísticas
        self._load_stats()
        
    def _init_database(self):
        """Inicializar banco de dados SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        cache_key TEXT PRIMARY KEY,
                        text_hash TEXT NOT NULL,
                        original_text TEXT NOT NULL,
                        audio_path TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        voice TEXT,
                        language TEXT NOT NULL,
                        duration REAL NOT NULL,
                        file_size INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        last_accessed TEXT NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        metadata TEXT DEFAULT '{}'
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_text_hash ON cache_entries(text_hash)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_stats (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de cache: {e}")
            
    def _generate_cache_key(
        self,
        text: str,
        provider: str,
        voice: Optional[str] = None,
        language: str = "pt"
    ) -> str:
        """Gerar chave única para cache"""
        
        # Normalizar texto
        normalized_text = text.strip().lower()
        
        # Criar string para hash
        cache_string = f"{normalized_text}|{provider}|{voice or 'default'}|{language}"
        
        # Gerar hash
        cache_key = hashlib.sha256(cache_string.encode('utf-8')).hexdigest()[:16]
        
        return cache_key
        
    def _generate_text_hash(self, text: str) -> str:
        """Gerar hash do texto"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    async def get_cached_audio(
        self,
        text: str,
        provider: str,
        voice: Optional[str] = None,
        language: str = "pt"
    ) -> Optional[Dict]:
        """Buscar áudio no cache"""
        
        cache_key = self._generate_cache_key(text, provider, voice, language)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM cache_entries WHERE cache_key = ?
                """, (cache_key,))
                
                row = cursor.fetchone()
                
                if not row:
                    self.misses += 1
                    return None
                    
                # Verificar se arquivo ainda existe
                audio_path = row[3]  # audio_path column
                if not os.path.exists(audio_path):
                    # Remover entrada inválida
                    await self._remove_cache_entry(cache_key)
                    self.misses += 1
                    return None
                    
                # Atualizar acesso
                now = datetime.now().isoformat()
                conn.execute("""
                    UPDATE cache_entries 
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE cache_key = ?
                """, (now, cache_key))
                conn.commit()
                
                self.hits += 1
                
                # Construir resultado
                result = {
                    'success': True,
                    'audio_path': row[3],
                    'duration': row[7],
                    'provider_used': row[4],
                    'cached': True,
                    'cache_key': cache_key,
                    'metadata': json.loads(row[12]) if row[12] else {}
                }
                
                logger.info(f"Cache HIT para chave {cache_key[:8]}... (texto: {text[:50]}...)")
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao buscar no cache: {e}")
            self.misses += 1
            return None
            
    async def store_audio(
        self,
        text: str,
        provider: str,
        audio_path: str,
        duration: float,
        voice: Optional[str] = None,
        language: str = "pt",
        metadata: Optional[Dict] = None
    ) -> bool:
        """Armazenar áudio no cache"""
        
        try:
            # Verificar se arquivo existe
            if not os.path.exists(audio_path):
                logger.warning(f"Arquivo não existe para cache: {audio_path}")
                return False
                
            cache_key = self._generate_cache_key(text, provider, voice, language)
            text_hash = self._generate_text_hash(text)
            
            # Obter informações do arquivo
            file_size = os.path.getsize(audio_path)
            
            # Criar nova localização no cache
            cache_filename = f"{cache_key}.mp3"
            cache_audio_path = str(self.cache_dir / cache_filename)
            
            # Copiar arquivo para cache
            import shutil
            shutil.copy2(audio_path, cache_audio_path)
            
            # Armazenar entrada no banco
            now = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries (
                        cache_key, text_hash, original_text, audio_path, provider,
                        voice, language, duration, file_size, created_at,
                        last_accessed, access_count, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cache_key, text_hash, text[:500],  # Limitar texto a 500 chars
                    cache_audio_path, provider, voice, language,
                    duration, file_size, now, now, 1,
                    json.dumps(metadata or {})
                ))
                conn.commit()
                
            logger.info(f"Áudio armazenado no cache: {cache_key[:8]}... ({file_size} bytes)")
            
            # Verificar e limpar cache se necessário
            await self._cleanup_cache_if_needed()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {e}")
            return False
            
    async def _remove_cache_entry(self, cache_key: str):
        """Remover entrada do cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Obter caminho do arquivo
                cursor = conn.execute("""
                    SELECT audio_path FROM cache_entries WHERE cache_key = ?
                """, (cache_key,))
                
                row = cursor.fetchone()
                if row:
                    audio_path = row[0]
                    
                    # Remover arquivo
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        
                    # Remover entrada do banco
                    conn.execute("""
                        DELETE FROM cache_entries WHERE cache_key = ?
                    """, (cache_key,))
                    conn.commit()
                    
                    logger.info(f"Entrada de cache removida: {cache_key[:8]}...")
                    
        except Exception as e:
            logger.error(f"Erro ao remover entrada do cache: {e}")
            
    async def _cleanup_cache_if_needed(self):
        """Limpar cache se necessário"""
        
        current_size = await self._get_cache_size()
        
        if current_size > self.max_size_bytes:
            logger.info(f"Cache excedeu limite ({current_size / 1024**3:.2f} GB). Iniciando limpeza...")
            await self._cleanup_cache()
            
    async def _get_cache_size(self) -> int:
        """Obter tamanho atual do cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT SUM(file_size) FROM cache_entries")
                result = cursor.fetchone()
                return result[0] if result[0] else 0
        except Exception as e:
            logger.error(f"Erro ao obter tamanho do cache: {e}")
            return 0
            
    async def _cleanup_cache(self):
        """Limpar cache usando estratégia LRU"""
        try:
            target_size = int(self.max_size_bytes * 0.8)  # Limpar até 80% do limite
            
            with sqlite3.connect(self.db_path) as conn:
                # Ordenar por último acesso (LRU)
                cursor = conn.execute("""
                    SELECT cache_key, file_size, audio_path
                    FROM cache_entries
                    ORDER BY last_accessed ASC
                """)
                
                current_size = await self._get_cache_size()
                removed_count = 0
                
                for row in cursor:
                    if current_size <= target_size:
                        break
                        
                    cache_key, file_size, audio_path = row
                    
                    # Remover arquivo
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        
                    # Remover entrada do banco
                    conn.execute("""
                        DELETE FROM cache_entries WHERE cache_key = ?
                    """, (cache_key,))
                    
                    current_size -= file_size
                    removed_count += 1
                    self.evictions += 1
                    
                conn.commit()
                
                logger.info(f"Cache limpo: {removed_count} entradas removidas")
                
        except Exception as e:
            logger.error(f"Erro na limpeza do cache: {e}")
            
    async def get_cache_stats(self) -> Dict:
        """Obter estatísticas do cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estatísticas básicas
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_entries,
                        SUM(file_size) as total_size,
                        AVG(duration) as avg_duration,
                        SUM(access_count) as total_accesses
                    FROM cache_entries
                """)
                
                stats = cursor.fetchone()
                
                # Estatísticas por provedor
                cursor = conn.execute("""
                    SELECT provider, COUNT(*), SUM(file_size)
                    FROM cache_entries
                    GROUP BY provider
                """)
                
                provider_stats = {row[0]: {"count": row[1], "size": row[2]} for row in cursor}
                
                # Entradas mais acessadas
                cursor = conn.execute("""
                    SELECT original_text, access_count, provider
                    FROM cache_entries
                    ORDER BY access_count DESC
                    LIMIT 5
                """)
                
                popular_entries = [
                    {"text": row[0][:100], "accesses": row[1], "provider": row[2]}
                    for row in cursor
                ]
                
                hit_rate = (self.hits / (self.hits + self.misses)) * 100 if (self.hits + self.misses) > 0 else 0
                
                return {
                    "total_entries": stats[0] if stats[0] else 0,
                    "total_size_bytes": stats[1] if stats[1] else 0,
                    "total_size_mb": (stats[1] / 1024**2) if stats[1] else 0,
                    "avg_duration": stats[2] if stats[2] else 0,
                    "total_accesses": stats[3] if stats[3] else 0,
                    "hits": self.hits,
                    "misses": self.misses,
                    "hit_rate": hit_rate,
                    "evictions": self.evictions,
                    "max_size_gb": self.max_size_bytes / 1024**3,
                    "provider_breakdown": provider_stats,
                    "popular_entries": popular_entries
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
            
    async def find_similar_audio(
        self,
        text: str,
        similarity_threshold: float = 0.8,
        max_results: int = 5
    ) -> List[Dict]:
        """Encontrar áudios similares usando similaridade de texto"""
        
        try:
            # Simplificado: busca por substring e palavras-chave
            text_lower = text.lower()
            keywords = set(text_lower.split())
            
            results = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT cache_key, original_text, audio_path, provider, duration, access_count
                    FROM cache_entries
                    ORDER BY access_count DESC
                    LIMIT 50
                """)
                
                for row in cursor:
                    cache_key, original_text, audio_path, provider, duration, access_count = row
                    
                    # Calcular similaridade simples
                    other_keywords = set(original_text.lower().split())
                    
                    if not keywords or not other_keywords:
                        continue
                        
                    intersection = len(keywords.intersection(other_keywords))
                    union = len(keywords.union(other_keywords))
                    
                    jaccard_similarity = intersection / union if union > 0 else 0
                    
                    if jaccard_similarity >= similarity_threshold:
                        results.append({
                            "cache_key": cache_key,
                            "text": original_text[:200],
                            "audio_path": audio_path,
                            "provider": provider,
                            "duration": duration,
                            "similarity": jaccard_similarity,
                            "access_count": access_count
                        })
                        
                        if len(results) >= max_results:
                            break
                            
            # Ordenar por similaridade
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar áudios similares: {e}")
            return []
            
    async def preload_common_phrases(self, phrases: List[str], provider: str = "gtts"):
        """Pré-carregar frases comuns no cache"""
        
        logger.info(f"Pré-carregando {len(phrases)} frases no cache...")
        
        try:
            from app.utils import generate_narration
            
            for i, phrase in enumerate(phrases):
                # Verificar se já está no cache
                cached = await self.get_cached_audio(phrase, provider)
                
                if cached:
                    logger.info(f"Frase {i+1}/{len(phrases)} já está no cache")
                    continue
                    
                # Gerar áudio
                temp_path = f"temp_preload_{i}.mp3"
                
                result = await generate_narration(
                    text=phrase,
                    output_path=temp_path,
                    provider=provider
                )
                
                if result['success']:
                    # Armazenar no cache
                    await self.store_audio(
                        text=phrase,
                        provider=provider,
                        audio_path=result['audio_path'],
                        duration=result['duration']
                    )
                    
                    # Limpar arquivo temporário
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
                    logger.info(f"Frase {i+1}/{len(phrases)} pré-carregada com sucesso")
                    
                else:
                    logger.warning(f"Falha ao pré-carregar frase {i+1}: {result['error']}")
                    
                # Pequena pausa para não sobrecarregar
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Erro no pré-carregamento: {e}")
            
    def _load_stats(self):
        """Carregar estatísticas persistidas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT key, value FROM cache_stats")
                
                for key, value in cursor:
                    if key == "hits":
                        self.hits = int(value)
                    elif key == "misses":
                        self.misses = int(value)
                    elif key == "evictions":
                        self.evictions = int(value)
                        
        except Exception as e:
            logger.error(f"Erro ao carregar estatísticas: {e}")
            
    def _save_stats(self):
        """Salvar estatísticas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = [
                    ("hits", str(self.hits)),
                    ("misses", str(self.misses)),
                    ("evictions", str(self.evictions))
                ]
                
                for key, value in stats:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_stats (key, value) VALUES (?, ?)
                    """, (key, value))
                    
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
            
    async def clear_cache(self) -> bool:
        """Limpar todo o cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Obter todos os arquivos
                cursor = conn.execute("SELECT audio_path FROM cache_entries")
                
                for row in cursor:
                    audio_path = row[0]
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        
                # Limpar banco
                conn.execute("DELETE FROM cache_entries")
                conn.commit()
                
                logger.info("Cache completamente limpo")
                
                return True
                
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
            
    def __del__(self):
        """Destructor - salvar estatísticas"""
        try:
            self._save_stats()
        except:
            pass


# Instância global do cache
tts_cache_manager = TTSCacheManager()

# Funções de conveniência
async def get_cached_tts_audio(
    text: str,
    provider: str,
    voice: Optional[str] = None,
    language: str = "pt"
) -> Optional[Dict]:
    """Buscar áudio TTS no cache"""
    return await tts_cache_manager.get_cached_audio(text, provider, voice, language)

async def store_tts_audio(
    text: str,
    provider: str,
    audio_path: str,
    duration: float,
    voice: Optional[str] = None,
    language: str = "pt",
    metadata: Optional[Dict] = None
) -> bool:
    """Armazenar áudio TTS no cache"""
    return await tts_cache_manager.store_audio(
        text, provider, audio_path, duration, voice, language, metadata
    )

async def get_tts_cache_stats() -> Dict:
    """Obter estatísticas do cache TTS"""
    return await tts_cache_manager.get_cache_stats()

async def clear_tts_cache() -> bool:
    """Limpar cache TTS"""
    return await tts_cache_manager.clear_cache() 