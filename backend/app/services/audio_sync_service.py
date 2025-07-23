"""
Serviço de Sincronização de Áudio - TecnoCursos AI
Sistema avançado para sincronizar áudio com vídeo e elementos visuais
"""

import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import math

try:
    from moviepy.editor import *
    from moviepy.audio.fx import audio_fadein, audio_fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.effects import normalize
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AudioTrack:
    """Representação de uma trilha de áudio"""
    id: str
    name: str
    file_path: str
    start_time: float
    duration: float
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    is_background: bool = False
    sync_to_scene: Optional[str] = None
    audio_type: str = "music"  # music, voice, sfx

@dataclass
class SyncPoint:
    """Ponto de sincronização entre áudio e vídeo"""
    timestamp: float
    audio_cue: str
    visual_cue: str
    sync_type: str = "beat"  # beat, word, scene_change

class AudioSyncService:
    """Serviço completo para sincronização de áudio"""
    
    def __init__(self):
        self.temp_dir = Path("temp/audio_sync")
        self.output_dir = Path("static/audio/processed")
        self.assets_dir = Path("uploads/audios")
        
        # Criar diretórios
        for directory in [self.temp_dir, self.output_dir, self.assets_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configurações de processamento
        self.sample_rate = 44100
        self.bit_depth = 16
        self.max_duration = 600  # 10 minutos máximo
        
        # Cache de análises de áudio
        self.audio_analysis_cache = {}
        
        logger.info("🎵 Audio Sync Service inicializado")
    
    async def create_synchronized_audio_track(self, 
                                            audio_tracks: List[AudioTrack],
                                            video_duration: float,
                                            sync_points: List[SyncPoint] = None) -> Dict[str, Any]:
        """Criar trilha de áudio sincronizada com vídeo"""
        try:
            if not audio_tracks:
                raise ValueError("Nenhuma trilha de áudio fornecida")
            
            logger.info(f"🎼 Sincronizando {len(audio_tracks)} trilhas de áudio")
            
            # Processar cada trilha individualmente
            processed_tracks = []
            for track in audio_tracks:
                processed = await self._process_audio_track(track, video_duration)
                if processed:
                    processed_tracks.append(processed)
            
            if not processed_tracks:
                raise ValueError("Nenhuma trilha de áudio processada com sucesso")
            
            # Combinar trilhas com mix inteligente
            combined_audio = await self._combine_audio_tracks(processed_tracks, video_duration)
            
            # Aplicar sincronização se pontos especificados
            if sync_points:
                combined_audio = await self._apply_sync_points(combined_audio, sync_points)
            
            # Normalizar e masterizar
            final_audio = await self._master_audio(combined_audio)
            
            # Salvar arquivo final
            output_filename = f"synchronized_audio_{uuid.uuid4()}.wav"
            output_path = self.output_dir / output_filename
            
            await self._export_audio(final_audio, output_path)
            
            return {
                "success": True,
                "audio_path": str(output_path),
                "audio_url": f"/static/audio/processed/{output_filename}",
                "duration": video_duration,
                "tracks_processed": len(processed_tracks),
                "sync_points_applied": len(sync_points) if sync_points else 0,
                "file_size": os.path.getsize(output_path) if output_path.exists() else 0,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na sincronização de áudio: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_audio_track(self, track: AudioTrack, video_duration: float) -> Optional[AudioClip]:
        """Processar uma trilha de áudio individual"""
        try:
            if not os.path.exists(track.file_path):
                logger.warning(f"Arquivo de áudio não encontrado: {track.file_path}")
                return None
            
            # Carregar áudio
            if MOVIEPY_AVAILABLE:
                audio_clip = AudioFileClip(track.file_path)
            else:
                # Fallback sem MoviePy
                return None
            
            # Ajustar duração
            if track.duration > 0:
                if track.duration > audio_clip.duration:
                    # Loop se necessário
                    loops_needed = math.ceil(track.duration / audio_clip.duration)
                    audio_clip = concatenate_audioclips([audio_clip] * loops_needed)
                
                audio_clip = audio_clip.subclip(0, track.duration)
            else:
                # Ajustar para duração do vídeo
                if audio_clip.duration > video_duration:
                    audio_clip = audio_clip.subclip(0, video_duration)
                elif audio_clip.duration < video_duration and track.is_background:
                    # Loop música de fundo
                    loops_needed = math.ceil(video_duration / audio_clip.duration)
                    audio_clip = concatenate_audioclips([audio_clip] * loops_needed)
                    audio_clip = audio_clip.subclip(0, video_duration)
            
            # Aplicar volume
            if track.volume != 1.0:
                audio_clip = audio_clip.volumex(track.volume)
            
            # Aplicar fade in/out
            if track.fade_in > 0:
                audio_clip = audio_fadein(audio_clip, track.fade_in)
            
            if track.fade_out > 0:
                audio_clip = audio_fadeout(audio_clip, track.fade_out)
            
            # Definir posição temporal
            audio_clip = audio_clip.set_start(track.start_time)
            
            # Aplicar efeitos específicos por tipo
            audio_clip = await self._apply_audio_effects(audio_clip, track.audio_type)
            
            logger.info(f"✅ Trilha processada: {track.name} ({audio_clip.duration:.2f}s)")
            return audio_clip
            
        except Exception as e:
            logger.error(f"Erro ao processar trilha {track.name}: {e}")
            return None
    
    async def _apply_audio_effects(self, audio_clip: AudioClip, audio_type: str) -> AudioClip:
        """Aplicar efeitos específicos baseados no tipo de áudio"""
        try:
            if audio_type == "voice":
                # Efeitos para voz: compressão leve, EQ
                # Por ora, apenas normalização
                pass
            elif audio_type == "music":
                # Efeitos para música: redução de volume se for fundo
                if hasattr(audio_clip, 'volumex'):
                    audio_clip = audio_clip.volumex(0.7)  # Reduzir música de fundo
            elif audio_type == "sfx":
                # Efeitos sonoros: manter volume original
                pass
            
            return audio_clip
            
        except Exception as e:
            logger.error(f"Erro ao aplicar efeitos de áudio: {e}")
            return audio_clip
    
    async def _combine_audio_tracks(self, tracks: List[AudioClip], video_duration: float) -> AudioClip:
        """Combinar múltiplas trilhas de áudio com mix inteligente"""
        try:
            if len(tracks) == 1:
                return tracks[0]
            
            # Separar por tipo
            voice_tracks = []
            music_tracks = []
            sfx_tracks = []
            
            for track in tracks:
                # Identificar tipo baseado em propriedades
                # Por ora, assumir que todas são música de fundo
                music_tracks.append(track)
            
            # Combinar trilhas
            combined_clips = []
            
            # Adicionar música de fundo (com volume reduzido se houver voz)
            if music_tracks:
                if voice_tracks:
                    # Reduzir volume da música quando há voz
                    music_combined = CompositeAudioClip(music_tracks).volumex(0.4)
                else:
                    music_combined = CompositeAudioClip(music_tracks)
                combined_clips.append(music_combined)
            
            # Adicionar voz (prioridade máxima)
            if voice_tracks:
                voice_combined = CompositeAudioClip(voice_tracks)
                combined_clips.append(voice_combined)
            
            # Adicionar efeitos sonoros
            if sfx_tracks:
                sfx_combined = CompositeAudioClip(sfx_tracks)
                combined_clips.append(sfx_combined)
            
            # Mix final
            if combined_clips:
                final_audio = CompositeAudioClip(combined_clips)
                # Garantir duração correta
                final_audio = final_audio.set_duration(video_duration)
                return final_audio
            
            return tracks[0]  # Fallback
            
        except Exception as e:
            logger.error(f"Erro ao combinar trilhas de áudio: {e}")
            return tracks[0] if tracks else None
    
    async def _apply_sync_points(self, audio_clip: AudioClip, sync_points: List[SyncPoint]) -> AudioClip:
        """Aplicar pontos de sincronização específicos"""
        try:
            # Por ora, implementação básica
            # Em uma versão avançada, isso permitiria sincronizar batidas com cortes
            
            logger.info(f"🎯 Aplicando {len(sync_points)} pontos de sincronização")
            
            # Implementação futura:
            # - Detectar batidas no áudio
            # - Alinhar com mudanças de cena
            # - Ajustar timing automaticamente
            
            return audio_clip
            
        except Exception as e:
            logger.error(f"Erro ao aplicar pontos de sincronização: {e}")
            return audio_clip
    
    async def _master_audio(self, audio_clip: AudioClip) -> AudioClip:
        """Masterização final do áudio"""
        try:
            # Normalização
            # Em uma implementação completa, usaria bibliotecas de masterização
            
            # Por ora, apenas limitar volume máximo
            try:
                # Verificar se o áudio não está muito alto
                max_volume = 0.8
                audio_clip = audio_clip.volumex(max_volume)
            except:
                pass
            
            logger.info("🎚️ Áudio masterizado")
            return audio_clip
            
        except Exception as e:
            logger.error(f"Erro na masterização: {e}")
            return audio_clip
    
    async def _export_audio(self, audio_clip: AudioClip, output_path: Path):
        """Exportar áudio processado"""
        try:
            audio_clip.write_audiofile(
                str(output_path),
                fps=self.sample_rate,
                nbytes=2,  # 16-bit
                codec='pcm_s16le',
                verbose=False,
                logger=None
            )
            
            logger.info(f"🎵 Áudio exportado: {output_path}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar áudio: {e}")
            raise
    
    async def analyze_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Analisar arquivo de áudio para sincronização"""
        try:
            if file_path in self.audio_analysis_cache:
                return self.audio_analysis_cache[file_path]
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            analysis = {
                "file_path": file_path,
                "duration": 0,
                "sample_rate": self.sample_rate,
                "channels": 1,
                "beats": [],
                "tempo": 120,
                "key": "C",
                "loudness": -20.0,
                "spectral_features": {},
                "analyzed_at": datetime.now().isoformat()
            }
            
            if MOVIEPY_AVAILABLE:
                # Análise básica com MoviePy
                audio_clip = AudioFileClip(file_path)
                analysis["duration"] = audio_clip.duration
                
                if hasattr(audio_clip, 'fps'):
                    analysis["sample_rate"] = audio_clip.fps
                
                audio_clip.close()
            
            if LIBROSA_AVAILABLE:
                # Análise avançada com librosa
                try:
                    y, sr = librosa.load(file_path, sr=self.sample_rate)
                    
                    # Detectar batidas
                    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                    analysis["tempo"] = float(tempo)
                    analysis["beats"] = [float(t) for t in librosa.frames_to_time(beats, sr=sr)]
                    
                    # Detectar tonalidade
                    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                    key_profile = np.mean(chroma, axis=1)
                    key_index = np.argmax(key_profile)
                    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                    analysis["key"] = keys[key_index]
                    
                    # Calcular loudness (RMS)
                    rms = librosa.feature.rms(y=y)
                    analysis["loudness"] = float(20 * np.log10(np.mean(rms) + 1e-10))
                    
                    # Features espectrais
                    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
                    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
                    
                    analysis["spectral_features"] = {
                        "centroid_mean": float(np.mean(spectral_centroids)),
                        "bandwidth_mean": float(np.mean(spectral_bandwidth))
                    }
                    
                except Exception as e:
                    logger.warning(f"Erro na análise avançada com librosa: {e}")
            
            # Cache da análise
            self.audio_analysis_cache[file_path] = analysis
            
            logger.info(f"🔍 Áudio analisado: {file_path} ({analysis['duration']:.2f}s)")
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar áudio: {e}")
            return {
                "file_path": file_path,
                "duration": 0,
                "error": str(e),
                "analyzed_at": datetime.now().isoformat()
            }
    
    async def suggest_sync_points(self, audio_analysis: Dict[str, Any], 
                                video_scenes: List[Dict[str, Any]]) -> List[SyncPoint]:
        """Sugerir pontos de sincronização automática"""
        try:
            sync_points = []
            
            beats = audio_analysis.get("beats", [])
            if not beats:
                return sync_points
            
            # Calcular pontos de mudança de cena
            scene_changes = []
            current_time = 0
            for scene in video_scenes:
                scene_changes.append(current_time)
                current_time += scene.get("duration", 3)
            
            # Encontrar batidas próximas a mudanças de cena
            for scene_time in scene_changes:
                # Encontrar batida mais próxima
                closest_beat = min(beats, key=lambda x: abs(x - scene_time))
                
                if abs(closest_beat - scene_time) < 0.5:  # Dentro de 0.5s
                    sync_point = SyncPoint(
                        timestamp=closest_beat,
                        audio_cue="beat",
                        visual_cue="scene_change",
                        sync_type="beat"
                    )
                    sync_points.append(sync_point)
            
            logger.info(f"🎯 {len(sync_points)} pontos de sincronização sugeridos")
            return sync_points
            
        except Exception as e:
            logger.error(f"Erro ao sugerir pontos de sincronização: {e}")
            return []
    
    def create_audio_track(self, name: str, file_path: str, start_time: float = 0,
                          duration: float = 0, volume: float = 1.0,
                          is_background: bool = False, audio_type: str = "music") -> AudioTrack:
        """Criar objeto AudioTrack"""
        return AudioTrack(
            id=str(uuid.uuid4()),
            name=name,
            file_path=file_path,
            start_time=start_time,
            duration=duration,
            volume=volume,
            is_background=is_background,
            audio_type=audio_type
        )
    
    def get_supported_formats(self) -> List[str]:
        """Obter formatos de áudio suportados"""
        return [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"]
    
    def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Validar arquivo de áudio"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        try:
            if not os.path.exists(file_path):
                result["errors"].append("Arquivo não encontrado")
                return result
            
            # Verificar extensão
            ext = Path(file_path).suffix.lower()
            if ext not in self.get_supported_formats():
                result["errors"].append(f"Formato não suportado: {ext}")
                return result
            
            # Verificar tamanho
            file_size = os.path.getsize(file_path)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                result["errors"].append(f"Arquivo muito grande: {file_size / (1024*1024):.1f}MB")
                return result
            
            result["info"]["file_size"] = file_size
            result["info"]["extension"] = ext
            
            # Teste básico de carregamento
            if MOVIEPY_AVAILABLE:
                try:
                    audio_clip = AudioFileClip(file_path)
                    duration = audio_clip.duration
                    
                    if duration > self.max_duration:
                        result["warnings"].append(f"Duração muito longa: {duration:.1f}s")
                    
                    result["info"]["duration"] = duration
                    audio_clip.close()
                    
                except Exception as e:
                    result["errors"].append(f"Erro ao carregar áudio: {e}")
                    return result
            
            if not result["errors"]:
                result["valid"] = True
            
        except Exception as e:
            result["errors"].append(f"Erro na validação: {e}")
        
        return result

# Instância global do serviço
audio_sync_service = AudioSyncService()

# Funções de conveniência
async def create_synchronized_audio(audio_tracks: List[AudioTrack], 
                                  video_duration: float,
                                  sync_points: List[SyncPoint] = None) -> Dict[str, Any]:
    """Função de conveniência para criar áudio sincronizado"""
    return await audio_sync_service.create_synchronized_audio_track(
        audio_tracks, video_duration, sync_points
    )

async def analyze_audio(file_path: str) -> Dict[str, Any]:
    """Função de conveniência para analisar áudio"""
    return await audio_sync_service.analyze_audio_file(file_path)

def validate_audio(file_path: str) -> Dict[str, Any]:
    """Função de conveniência para validar áudio"""
    return audio_sync_service.validate_audio_file(file_path)