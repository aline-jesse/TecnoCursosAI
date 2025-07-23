from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import time

router = APIRouter(prefix="/api", tags=["preview"])

# --- MODELOS ---
class ExportVideoRequest(BaseModel):
    scenes: list
    quality: str
    format: str
    fps: int

class ExportVideoResponse(BaseModel):
    status: str
    videoUrl: str
    exportId: str
    message: Optional[str] = None

class RegenerateNarrationRequest(BaseModel):
    text: str
    sceneId: str
    voice: Optional[str] = "default"

class RegenerateNarrationResponse(BaseModel):
    status: str
    narrationUrl: str
    message: Optional[str] = None

# --- ENDPOINTS ---
@router.post("/export-video", response_model=ExportVideoResponse)
async def export_video(req: ExportVideoRequest):
    # Simula processamento
    export_id = str(uuid.uuid4())
    time.sleep(1)  # Simula delay
    return ExportVideoResponse(
        status="success",
        videoUrl=f"/static/exports/{export_id}.mp4",
        exportId=export_id,
        message="Exportação simulada com sucesso."
    )

@router.post("/regenerate-narration", response_model=RegenerateNarrationResponse)
async def regenerate_narration(req: RegenerateNarrationRequest):
    # Simula processamento
    narration_id = str(uuid.uuid4())
    time.sleep(0.5)  # Simula delay
    return RegenerateNarrationResponse(
        status="success",
        narrationUrl=f"/static/narrations/{narration_id}.mp3",
        message="Narração IA simulada com sucesso."
    ) 