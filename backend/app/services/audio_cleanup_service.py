"""
Serviço de Limpeza Automática de Áudios
======================================

Este serviço realiza limpeza automática de:
- Arquivos de áudio órfãos (sem registro no banco)
- Registros de áudio com arquivos físicos inexistentes
- Áudios antigos baseado em política de retenção
- Cache de áudios não utilizados

Funcionalidades:
1. Limpeza de arquivos órfãos
2. Validação de integridade
3. Política de retenção por idade
4. Otimização de espaço em disco
5. Relatórios de limpeza
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db_session
from app.models import Audio, User
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class AudioCleanupService:
    """Serviço para limpeza automática de áudios"""
    
    def __init__(self):
        self.audio_dir = Path(settings.static_directory) / "audios"
        self.cleanup_stats = {
            "orphaned_files_removed": 0,
            "orphaned_records_removed": 0,
            "old_files_removed": 0,
            "space_freed_mb": 0.0,
            "errors": []
        }
    
    async def run_full_cleanup(
        self,
        max_age_days: int = 90,
        dry_run: bool = False
    ) -> Dict:
        """
        Executar limpeza completa do sistema de áudios
        
        Args:
            max_age_days: Idade máxima em dias para manter áudios
            dry_run: Se True, apenas simula a limpeza sem deletar arquivos
            
        Returns:
            Relatório detalhado da limpeza
        """
        logger.info(f"Iniciando limpeza {'simulada' if dry_run else 'real'} de áudios")
        logger.info(f"Política de retenção: {max_age_days} dias")
        
        start_time = datetime.now()
        self.cleanup_stats = {
            "orphaned_files_removed": 0,
            "orphaned_records_removed": 0,
            "old_files_removed": 0,
            "space_freed_mb": 0.0,
            "errors": []
        }
        
        try:
            # 1. Limpar arquivos órfãos (arquivos sem registro no banco)
            await self._cleanup_orphaned_files(dry_run)
            
            # 2. Limpar registros órfãos (registros sem arquivo físico)
            await self._cleanup_orphaned_records(dry_run)
            
            # 3. Limpar arquivos antigos baseado na política de retenção
            await self._cleanup_old_files(max_age_days, dry_run)
            
            # 4. Otimizar diretório de áudios
            await self._optimize_audio_directory(dry_run)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            report = {
                "success": True,
                "dry_run": dry_run,
                "duration_seconds": duration,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "stats": self.cleanup_stats,
                "summary": self._generate_summary()
            }
            
            logger.info(f"Limpeza concluída em {duration:.2f}s")
            logger.info(f"Espaço liberado: {self.cleanup_stats['space_freed_mb']:.2f} MB")
            
            return report
            
        except Exception as e:
            logger.error(f"Erro durante limpeza: {e}", exc_info=True)
            self.cleanup_stats["errors"].append(str(e))
            return {
                "success": False,
                "error": str(e),
                "stats": self.cleanup_stats
            }
    
    async def _cleanup_orphaned_files(self, dry_run: bool) -> None:
        """Limpar arquivos de áudio que não têm registro no banco"""
        logger.info("Iniciando limpeza de arquivos órfãos")
        
        if not self.audio_dir.exists():
            logger.warning(f"Diretório de áudios não existe: {self.audio_dir}")
            return
        
        # Obter todos os arquivos MP3 no diretório
        audio_files = list(self.audio_dir.glob("*.mp3"))
        logger.info(f"Encontrados {len(audio_files)} arquivos de áudio")
        
        if not audio_files:
            return
        
        # Obter todos os caminhos de arquivo registrados no banco
        db = next(get_db_session())
        try:
            registered_paths = set()
            audios = db.query(Audio.file_path).all()
            for audio in audios:
                if audio.file_path:
                    registered_paths.add(Path(audio.file_path).name)
            
            logger.info(f"Encontrados {len(registered_paths)} arquivos registrados no banco")
            
            # Identificar arquivos órfãos
            orphaned_files = []
            for file_path in audio_files:
                if file_path.name not in registered_paths:
                    orphaned_files.append(file_path)
            
            logger.info(f"Encontrados {len(orphaned_files)} arquivos órfãos")
            
            # Remover arquivos órfãos
            for file_path in orphaned_files:
                try:
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    
                    if not dry_run:
                        file_path.unlink()
                        logger.info(f"Arquivo órfão removido: {file_path.name}")
                    else:
                        logger.info(f"[DRY RUN] Removeria arquivo órfão: {file_path.name}")
                    
                    self.cleanup_stats["orphaned_files_removed"] += 1
                    self.cleanup_stats["space_freed_mb"] += file_size_mb
                    
                except Exception as e:
                    error_msg = f"Erro ao remover arquivo órfão {file_path.name}: {e}"
                    logger.error(error_msg)
                    self.cleanup_stats["errors"].append(error_msg)
                    
        finally:
            db.close()
    
    async def _cleanup_orphaned_records(self, dry_run: bool) -> None:
        """Limpar registros de áudio que não têm arquivo físico"""
        logger.info("Iniciando limpeza de registros órfãos")
        
        db = next(get_db_session())
        try:
            # Buscar todos os registros de áudio
            audios = db.query(Audio).all()
            logger.info(f"Verificando {len(audios)} registros de áudio")
            
            orphaned_records = []
            for audio in audios:
                if audio.file_path:
                    file_path = Path(audio.file_path)
                    if not file_path.exists():
                        orphaned_records.append(audio)
            
            logger.info(f"Encontrados {len(orphaned_records)} registros órfãos")
            
            # Remover registros órfãos
            for audio in orphaned_records:
                try:
                    if not dry_run:
                        db.delete(audio)
                        logger.info(f"Registro órfão removido: {audio.title} (ID: {audio.id})")
                    else:
                        logger.info(f"[DRY RUN] Removeria registro órfão: {audio.title} (ID: {audio.id})")
                    
                    self.cleanup_stats["orphaned_records_removed"] += 1
                    
                except Exception as e:
                    error_msg = f"Erro ao remover registro órfão {audio.id}: {e}"
                    logger.error(error_msg)
                    self.cleanup_stats["errors"].append(error_msg)
            
            if not dry_run and orphaned_records:
                db.commit()
                
        finally:
            db.close()
    
    async def _cleanup_old_files(self, max_age_days: int, dry_run: bool) -> None:
        """Limpar arquivos antigos baseado na política de retenção"""
        logger.info(f"Iniciando limpeza de arquivos antigos (>{max_age_days} dias)")
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        db = next(get_db_session())
        try:
            # Buscar áudios antigos
            old_audios = db.query(Audio).filter(
                Audio.created_at < cutoff_date
            ).all()
            
            logger.info(f"Encontrados {len(old_audios)} áudios antigos")
            
            for audio in old_audios:
                try:
                    file_size_mb = 0.0
                    
                    # Remover arquivo físico se existir
                    if audio.file_path:
                        file_path = Path(audio.file_path)
                        if file_path.exists():
                            file_size_mb = file_path.stat().st_size / (1024 * 1024)
                            
                            if not dry_run:
                                file_path.unlink()
                                logger.info(f"Arquivo antigo removido: {file_path.name}")
                            else:
                                logger.info(f"[DRY RUN] Removeria arquivo antigo: {file_path.name}")
                    
                    # Remover registro do banco
                    if not dry_run:
                        db.delete(audio)
                        logger.info(f"Registro antigo removido: {audio.title} (ID: {audio.id})")
                    else:
                        logger.info(f"[DRY RUN] Removeria registro antigo: {audio.title} (ID: {audio.id})")
                    
                    self.cleanup_stats["old_files_removed"] += 1
                    self.cleanup_stats["space_freed_mb"] += file_size_mb
                    
                except Exception as e:
                    error_msg = f"Erro ao remover áudio antigo {audio.id}: {e}"
                    logger.error(error_msg)
                    self.cleanup_stats["errors"].append(error_msg)
            
            if not dry_run and old_audios:
                db.commit()
                
        finally:
            db.close()
    
    async def _optimize_audio_directory(self, dry_run: bool) -> None:
        """Otimizar estrutura do diretório de áudios"""
        logger.info("Iniciando otimização do diretório de áudios")
        
        if not self.audio_dir.exists():
            return
        
        try:
            # Remover diretórios vazios
            for item in self.audio_dir.iterdir():
                if item.is_dir() and not any(item.iterdir()):
                    if not dry_run:
                        item.rmdir()
                        logger.info(f"Diretório vazio removido: {item.name}")
                    else:
                        logger.info(f"[DRY RUN] Removeria diretório vazio: {item.name}")
            
            # Verificar permissões e propriedades
            if not dry_run:
                # Ajustar permissões se necessário
                for file_path in self.audio_dir.glob("*.mp3"):
                    if file_path.stat().st_mode & 0o777 != 0o644:
                        file_path.chmod(0o644)
            
        except Exception as e:
            error_msg = f"Erro durante otimização: {e}"
            logger.error(error_msg)
            self.cleanup_stats["errors"].append(error_msg)
    
    def _generate_summary(self) -> str:
        """Gerar resumo textual da limpeza"""
        summary_parts = []
        
        if self.cleanup_stats["orphaned_files_removed"] > 0:
            summary_parts.append(f"{self.cleanup_stats['orphaned_files_removed']} arquivos órfãos removidos")
        
        if self.cleanup_stats["orphaned_records_removed"] > 0:
            summary_parts.append(f"{self.cleanup_stats['orphaned_records_removed']} registros órfãos removidos")
        
        if self.cleanup_stats["old_files_removed"] > 0:
            summary_parts.append(f"{self.cleanup_stats['old_files_removed']} arquivos antigos removidos")
        
        if self.cleanup_stats["space_freed_mb"] > 0:
            summary_parts.append(f"{self.cleanup_stats['space_freed_mb']:.2f} MB de espaço liberado")
        
        if self.cleanup_stats["errors"]:
            summary_parts.append(f"{len(self.cleanup_stats['errors'])} erros encontrados")
        
        if not summary_parts:
            return "Nenhuma limpeza necessária"
        
        return "; ".join(summary_parts)
    
    async def get_cleanup_recommendations(self) -> Dict:
        """Obter recomendações de limpeza sem executar"""
        logger.info("Analisando sistema para recomendações de limpeza")
        
        recommendations = {
            "total_audios": 0,
            "total_size_mb": 0.0,
            "orphaned_files": 0,
            "orphaned_records": 0,
            "old_files_30_days": 0,
            "old_files_90_days": 0,
            "potential_savings_mb": 0.0,
            "recommendations": []
        }
        
        try:
            # Análise de arquivos
            if self.audio_dir.exists():
                audio_files = list(self.audio_dir.glob("*.mp3"))
                recommendations["total_audios"] = len(audio_files)
                
                total_size = sum(f.stat().st_size for f in audio_files)
                recommendations["total_size_mb"] = total_size / (1024 * 1024)
            
            # Análise do banco
            db = next(get_db_session())
            try:
                # Contar registros órfãos
                audios = db.query(Audio).all()
                orphaned_count = 0
                for audio in audios:
                    if audio.file_path and not Path(audio.file_path).exists():
                        orphaned_count += 1
                recommendations["orphaned_records"] = orphaned_count
                
                # Contar arquivos antigos
                cutoff_30 = datetime.now() - timedelta(days=30)
                cutoff_90 = datetime.now() - timedelta(days=90)
                
                old_30_count = db.query(Audio).filter(Audio.created_at < cutoff_30).count()
                old_90_count = db.query(Audio).filter(Audio.created_at < cutoff_90).count()
                
                recommendations["old_files_30_days"] = old_30_count
                recommendations["old_files_90_days"] = old_90_count
                
            finally:
                db.close()
            
            # Gerar recomendações
            if recommendations["orphaned_files"] > 0:
                recommendations["recommendations"].append(
                    f"Remover {recommendations['orphaned_files']} arquivos órfãos"
                )
            
            if recommendations["orphaned_records"] > 0:
                recommendations["recommendations"].append(
                    f"Limpar {recommendations['orphaned_records']} registros órfãos"
                )
            
            if recommendations["old_files_90_days"] > 0:
                recommendations["recommendations"].append(
                    f"Considerar remover {recommendations['old_files_90_days']} áudios com mais de 90 dias"
                )
            
            if not recommendations["recommendations"]:
                recommendations["recommendations"].append("Sistema limpo, nenhuma ação necessária")
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}", exc_info=True)
            recommendations["error"] = str(e)
        
        return recommendations

# Instância global do serviço
cleanup_service = AudioCleanupService()

# Funções de conveniência
async def run_audio_cleanup(max_age_days: int = 90, dry_run: bool = False) -> Dict:
    """Executar limpeza automática de áudios"""
    return await cleanup_service.run_full_cleanup(max_age_days, dry_run)

async def get_cleanup_recommendations() -> Dict:
    """Obter recomendações de limpeza"""
    return await cleanup_service.get_cleanup_recommendations()

# Script de linha de comando
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Limpeza automática de áudios")
    parser.add_argument("--max-age", type=int, default=90, help="Idade máxima em dias")
    parser.add_argument("--dry-run", action="store_true", help="Simular limpeza sem deletar")
    parser.add_argument("--recommendations", action="store_true", help="Mostrar apenas recomendações")
    
    args = parser.parse_args()
    
    async def main():
        if args.recommendations:
            recommendations = await get_cleanup_recommendations()
            print("=== RECOMENDAÇÕES DE LIMPEZA ===")
            print(f"Total de áudios: {recommendations['total_audios']}")
            print(f"Tamanho total: {recommendations['total_size_mb']:.2f} MB")
            print("\nRecomendações:")
            for rec in recommendations["recommendations"]:
                print(f"  - {rec}")
        else:
            report = await run_audio_cleanup(args.max_age, args.dry_run)
            print("=== RELATÓRIO DE LIMPEZA ===")
            print(f"Sucesso: {report['success']}")
            print(f"Duração: {report.get('duration_seconds', 0):.2f}s")
            print(f"Resumo: {report['stats']}")
    
    asyncio.run(main()) 