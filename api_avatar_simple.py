#!/usr/bin/env python3
"""
API Simples para Sistema Avatar - TecnoCursosAI
FastAPI endpoint para geração de vídeos avatar
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import asyncio
from pathlib import Path
import json
import time
import os

# Sistema de avatar simples
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips

app = FastAPI(
    title="TecnoCursos AI - Avatar API",
    description="API para geração de vídeos com avatar virtual",
    version="1.0.0"
)

# Modelos Pydantic
class SlideContent(BaseModel):
    title: str
    content: str

class AvatarVideoRequest(BaseModel):
    title: str
    slides: List[SlideContent]
    narration_text: Optional[str] = None
    avatar_style: str = "professional"  # professional, friendly, teacher
    video_quality: str = "hd"  # sd, hd, fullhd

class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, error
    progress: float  # 0.0 to 100.0
    message: str
    created_at: str
    completed_at: Optional[str] = None
    video_url: Optional[str] = None
    error_details: Optional[str] = None

# Armazenamento em memória para jobs (em produção usar Redis/DB)
jobs_storage: Dict[str, JobStatus] = {}

def create_avatar_image(style: str = "professional") -> Image.Image:
    """Criar imagem do avatar baseada no estilo"""
    width, height = 400, 600
    
    # Cores baseadas no estilo
    colors = {
        "professional": {
            "skin": (220, 180, 140),
            "hair": (101, 67, 33),
            "shirt": (50, 100, 150),
            "bg": (240, 240, 250)
        },
        "friendly": {
            "skin": (230, 190, 150),
            "hair": (139, 69, 19),
            "shirt": (34, 139, 34),
            "bg": (255, 248, 220)
        },
        "teacher": {
            "skin": (210, 170, 130),
            "hair": (64, 64, 64),
            "shirt": (128, 0, 128),
            "bg": (245, 245, 245)
        }
    }
    
    color_scheme = colors.get(style, colors["professional"])
    
    img = Image.new('RGB', (width, height), color=color_scheme["bg"])
    draw = ImageDraw.Draw(img)
    
    # Desenhar cabeça
    head_center = (width // 2, height // 3)
    head_radius = 80
    draw.ellipse([
        head_center[0] - head_radius, head_center[1] - head_radius,
        head_center[0] + head_radius, head_center[1] + head_radius
    ], fill=color_scheme["skin"], outline=(180, 140, 100))
    
    # Olhos
    eye_y = head_center[1] - 20
    left_eye = (head_center[0] - 25, eye_y)
    right_eye = (head_center[0] + 25, eye_y)
    
    for eye_pos in [left_eye, right_eye]:
        draw.ellipse([
            eye_pos[0] - 8, eye_pos[1] - 8,
            eye_pos[0] + 8, eye_pos[1] + 8
        ], fill=(0, 0, 0))
        
        # Pupila
        draw.ellipse([
            eye_pos[0] - 3, eye_pos[1] - 3,
            eye_pos[0] + 3, eye_pos[1] + 3
        ], fill=(255, 255, 255))
    
    # Boca (sorriso para friendly/teacher)
    mouth_center = (head_center[0], head_center[1] + 30)
    if style in ["friendly", "teacher"]:
        draw.arc([
            mouth_center[0] - 20, mouth_center[1] - 10,
            mouth_center[0] + 20, mouth_center[1] + 10
        ], start=0, end=180, fill=(0, 0, 0), width=3)
    else:
        draw.line([
            mouth_center[0] - 15, mouth_center[1],
            mouth_center[0] + 15, mouth_center[1]
        ], fill=(0, 0, 0), width=2)
    
    # Cabelo
    hair_top = head_center[1] - head_radius
    draw.arc([
        head_center[0] - head_radius, hair_top - 20,
        head_center[0] + head_radius, head_center[1] + 20
    ], start=0, end=180, fill=color_scheme["hair"], width=25)
    
    # Corpo
    body_top = head_center[1] + head_radius + 20
    body_width = 120
    body_height = 200
    draw.rectangle([
        head_center[0] - body_width // 2, body_top,
        head_center[0] + body_width // 2, body_top + body_height
    ], fill=color_scheme["shirt"], outline=(30, 70, 120))
    
    return img

def create_slide_image(title: str, content: str, size: tuple = (1280, 720)) -> Image.Image:
    """Criar imagem do slide"""
    width, height = size
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Tentar fontes
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        text_font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            text_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    
    # Título
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    
    draw.text((title_x, 80), title, fill=(25, 25, 112), font=title_font)
    
    # Linha divisória
    draw.line([(100, 160), (width - 100, 160)], fill=(200, 200, 200), width=2)
    
    # Conteúdo
    content_lines = content.split('\n')
    y_pos = 220
    
    for line in content_lines:
        if line.strip():
            draw.text((150, y_pos), line, fill=(51, 51, 51), font=text_font)
            y_pos += 40
    
    return img

async def generate_avatar_video_async(
    job_id: str,
    title: str,
    slides: List[SlideContent],
    avatar_style: str,
    video_quality: str
):
    """Gerar vídeo avatar de forma assíncrona"""
    try:
        # Atualizar status
        jobs_storage[job_id].status = "processing"
        jobs_storage[job_id].progress = 10.0
        jobs_storage[job_id].message = "Criando avatar..."
        
        # Criar avatar
        avatar_img = create_avatar_image(avatar_style)
        avatar_path = f"temp_avatar_{job_id}.png"
        avatar_img.save(avatar_path)
        
        jobs_storage[job_id].progress = 30.0
        jobs_storage[job_id].message = "Criando slides..."
        
        # Criar slides
        slide_paths = []
        for i, slide in enumerate(slides):
            slide_img = create_slide_image(slide.title, slide.content)
            slide_path = f"temp_slide_{job_id}_{i}.png"
            slide_img.save(slide_path)
            slide_paths.append(slide_path)
        
        jobs_storage[job_id].progress = 60.0
        jobs_storage[job_id].message = "Gerando vídeo..."
        
        # Qualidades de vídeo
        qualities = {
            "sd": (640, 480),
            "hd": (1280, 720),
            "fullhd": (1920, 1080)
        }
        
        resolution = qualities.get(video_quality, qualities["hd"])
        
        # Criar clips
        clips = []
        
        # Avatar no início (2 segundos)
        avatar_clip = ImageClip(avatar_path, duration=2).resize(resolution)
        clips.append(avatar_clip)
        
        # Slides (3 segundos cada)
        for slide_path in slide_paths:
            slide_clip = ImageClip(slide_path, duration=3).resize(resolution)
            clips.append(slide_clip)
        
        jobs_storage[job_id].progress = 80.0
        jobs_storage[job_id].message = "Finalizando vídeo..."
        
        # Concatenar clips
        final_video = concatenate_videoclips(clips)
        
        # Salvar vídeo
        output_path = f"video_{job_id}.mp4"
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Limpar arquivos temporários
        os.remove(avatar_path)
        for slide_path in slide_paths:
            os.remove(slide_path)
        
        # Atualizar status de conclusão
        jobs_storage[job_id].status = "completed"
        jobs_storage[job_id].progress = 100.0
        jobs_storage[job_id].message = "Vídeo criado com sucesso!"
        jobs_storage[job_id].completed_at = time.strftime("%Y-%m-%d %H:%M:%S")
        jobs_storage[job_id].video_url = f"/download/{job_id}"
        
    except Exception as e:
        jobs_storage[job_id].status = "error"
        jobs_storage[job_id].message = "Erro na geração do vídeo"
        jobs_storage[job_id].error_details = str(e)

@app.get("/")
async def root():
    """Página inicial da API"""
    return {
        "message": "TecnoCursos AI - Avatar API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "POST /generate - Gerar vídeo avatar",
            "status": "GET /status/{job_id} - Status do job",
            "download": "GET /download/{job_id} - Download do vídeo",
            "health": "GET /health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "jobs_count": len(jobs_storage)
    }

@app.post("/generate", response_model=JobStatus)
async def generate_avatar_video(
    request: AvatarVideoRequest,
    background_tasks: BackgroundTasks
):
    """Gerar vídeo avatar (processamento em background)"""
    
    # Validações
    if not request.slides:
        raise HTTPException(status_code=400, detail="Pelo menos um slide é necessário")
    
    if len(request.slides) > 10:
        raise HTTPException(status_code=400, detail="Máximo de 10 slides permitidos")
    
    # Criar job
    job_id = str(uuid.uuid4())
    
    job = JobStatus(
        job_id=job_id,
        status="pending",
        progress=0.0,
        message="Job criado, aguardando processamento...",
        created_at=time.strftime("%Y-%m-%d %H:%M:%S")
    )
    
    jobs_storage[job_id] = job
    
    # Adicionar à fila de background
    background_tasks.add_task(
        generate_avatar_video_async,
        job_id,
        request.title,
        request.slides,
        request.avatar_style,
        request.video_quality
    )
    
    return job

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Obter status do job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    return jobs_storage[job_id]

@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download do vídeo gerado"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs_storage[job_id]
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Vídeo não está pronto. Status: {job.status}")
    
    video_path = f"video_{job_id}.mp4"
    
    if not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"avatar_video_{job_id}.mp4"
    )

@app.get("/jobs")
async def list_jobs():
    """Listar todos os jobs"""
    return {
        "total": len(jobs_storage),
        "jobs": list(jobs_storage.values())
    }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Deletar job e arquivo de vídeo"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    # Remover arquivo de vídeo se existir
    video_path = f"video_{job_id}.mp4"
    if Path(video_path).exists():
        os.remove(video_path)
    
    # Remover job
    del jobs_storage[job_id]
    
    return {"message": "Job deletado com sucesso"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_avatar_simple:app", host="0.0.0.0", port=8003, reload=True) 