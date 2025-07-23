import os
from typing import List, Optional
from app.services.tts_service import generate_tts_narration
from app.services.avatar_service import generate_avatar_video
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from app.models import Scene, Asset, Project
import logging
from fastapi import BackgroundTasks
import shutil

def process_scene_with_ia(scene: Scene, assets: List[Asset], tts_model: str = "coqui", avatar_model: str = "hunyuan3d2") -> dict:
    """
    Processa uma cena: gera narração TTS, avatar (se necessário), une assets e retorna caminho do vídeo da cena.
    """
    logging.info(f"[Pipeline IA] Processando cena {scene.id} - '{getattr(scene, 'nome', scene.name) if hasattr(scene, 'nome') else scene.name}")
    output_dir = f"app/static/videos/generated/scene_{scene.id}"
    os.makedirs(output_dir, exist_ok=True)
    # 1. Gerar narração TTS
    tts_path = os.path.join(output_dir, "narration.mp3")
    logging.info(f"[Pipeline IA] Gerando TTS para cena {scene.id}...")
    generate_tts_narration(scene.texto or "", tts_path, model=tts_model)
    # 2. Gerar avatar IA (se necessário)
    avatar_path = None
    if hasattr(scene, "avatar") and scene.avatar:
        avatar_path = os.path.join(output_dir, "avatar.mp4")
        logging.info(f"[Pipeline IA] Gerando avatar IA para cena {scene.id}...")
        generate_avatar_video(scene.texto or "", tts_path, avatar_path, model=avatar_model)
    # 3. Gerar vídeo da cena (imagem de fundo + áudio + assets)
    bg_img = None
    for asset in assets:
        if asset.tipo == "image" and asset.camada == 0:
            bg_img = asset.caminho_arquivo
            break
    if not bg_img:
        bg_img = "app/static/backgrounds/default_bg.png"
    duration = AudioFileClip(tts_path).duration
    logging.info(f"[Pipeline IA] Gerando vídeo da cena {scene.id}...")
    clip = ImageClip(bg_img).set_duration(duration).set_audio(AudioFileClip(tts_path))
    # TODO: adicionar outros assets (imagens, overlays, etc) como layers
    scene_video_path = os.path.join(output_dir, "scene_final.mp4")
    clip.write_videofile(scene_video_path, fps=24, codec="libx264", audio_codec="aac")
    logging.info(f"[Pipeline IA] Cena {scene.id} processada com sucesso: {scene_video_path}")
    return {"scene_id": scene.id, "video_path": scene_video_path, "tts_path": tts_path, "avatar_path": avatar_path}

def export_project_video_with_ia(project: Project, scenes: List[Scene], all_assets: List[Asset], tts_model: str = "coqui", avatar_model: str = "hunyuan3d2") -> str:
    """
    Exporta vídeo final do projeto: processa cada cena com IA, une vídeos e retorna caminho do MP4 final.
    """
    logging.info(f"[Pipeline IA] Exportando vídeo final do projeto {project.id} - '{project.name}'")
    scene_videos = []
    temp_dirs = []
    for scene in scenes:
        scene_assets = [a for a in all_assets if a.scene_id == scene.id]
        result = process_scene_with_ia(scene, scene_assets, tts_model, avatar_model)
        scene_videos.append(result["video_path"])
        temp_dirs.append(os.path.dirname(result["video_path"]))
    # Unir vídeos das cenas
    logging.info(f"[Pipeline IA] Unindo vídeos das cenas...")
    clips = [AudioFileClip(v) if v.endswith(".mp3") else ImageClip(v) for v in scene_videos]
    video_clips = [c if hasattr(c, 'set_audio') else c for c in clips]
    final_clip = concatenate_videoclips(video_clips, method="compose")
    output_dir = f"app/static/videos/generated/project_{project.id}"
    os.makedirs(output_dir, exist_ok=True)
    final_video_path = os.path.join(output_dir, "final_project_video.mp4")
    final_clip.write_videofile(final_video_path, fps=24, codec="libx264", audio_codec="aac")
    logging.info(f"[Pipeline IA] Exportação finalizada: {final_video_path}")
    # Limpeza de arquivos temporários
    for d in temp_dirs:
        try:
            shutil.rmtree(d, ignore_errors=True)
            logging.info(f"[Pipeline IA] Limpou temporários: {d}")
        except Exception as e:
            logging.warning(f"[Pipeline IA] Falha ao limpar temporários {d}: {e}")
    return final_video_path

def export_project_video_with_ia_async(
    project: Project,
    scenes: List[Scene],
    all_assets: List[Asset],
    tts_model: str = "coqui",
    avatar_model: str = "hunyuan3d2",
    callback: callable = None
) -> str:
    """
    Exporta vídeo final do projeto de forma assíncrona/background.
    """
    def task():
        final_video_path = export_project_video_with_ia(project, scenes, all_assets, tts_model, avatar_model)
        if callback:
            callback(final_video_path)
    return task
