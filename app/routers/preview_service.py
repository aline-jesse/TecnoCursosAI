"""
Serviço de Preview em Tempo Real - TecnoCursos AI
Gera previews instantâneos de cenas e elementos do editor
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import os
import uuid
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import logging

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Project

logger = logging.getLogger(__name__)

router = APIRouter()

class PreviewService:
    """Serviço para geração de previews em tempo real"""
    
    def __init__(self):
        self.temp_dir = Path("temp/previews")
        self.assets_dir = Path("uploads")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de preview
        self.preview_size = (640, 360)  # Tamanho reduzido para performance
        self.background_color = "#1a202c"
        
        # Cache de previews
        self.preview_cache = {}
        
        # Conexões WebSocket ativas
        self.active_connections: List[WebSocket] = []
    
    async def generate_scene_preview(self, scene_data: Dict[str, Any]) -> str:
        """Gerar preview de uma cena"""
        try:
            # Criar chave de cache
            cache_key = self._generate_cache_key(scene_data)
            
            # Verificar cache
            if cache_key in self.preview_cache:
                return self.preview_cache[cache_key]
            
            # Criar imagem base
            img = Image.new("RGB", self.preview_size, self._hex_to_rgb(self.background_color))
            draw = ImageDraw.Draw(img)
            
            # Adicionar gradiente sutil
            self._add_gradient(img, draw)
            
            # Processar elementos da cena
            elements = scene_data.get("elements", [])
            for element in elements:
                await self._add_element_to_preview(img, element)
            
            # Adicionar título se presente
            title = scene_data.get("title", "")
            if title:
                self._add_title_to_preview(img, draw, title)
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            img_data = base64.b64encode(buffer.getvalue()).decode()
            preview_url = f"data:image/jpeg;base64,{img_data}"
            
            # Salvar no cache
            self.preview_cache[cache_key] = preview_url
            
            return preview_url
            
        except Exception as e:
            logger.error(f"Erro ao gerar preview da cena: {e}")
            return self._generate_error_preview()
    
    async def generate_element_preview(self, element_data: Dict[str, Any]) -> str:
        """Gerar preview de um elemento específico"""
        try:
            element_type = element_data.get("type", "unknown")
            
            if element_type == "image":
                return await self._preview_image_element(element_data)
            elif element_type == "video":
                return await self._preview_video_element(element_data)
            elif element_type == "text":
                return await self._preview_text_element(element_data)
            elif element_type == "audio":
                return await self._preview_audio_element(element_data)
            else:
                return self._generate_placeholder_preview(element_type)
                
        except Exception as e:
            logger.error(f"Erro ao gerar preview do elemento: {e}")
            return self._generate_error_preview()
    
    async def generate_timeline_preview(self, timeline_data: List[Dict[str, Any]]) -> str:
        """Gerar preview da timeline completa"""
        try:
            # Criar imagem da timeline
            timeline_width = max(800, len(timeline_data) * 120)
            timeline_height = 80
            
            img = Image.new("RGB", (timeline_width, timeline_height), "#2d3748")
            draw = ImageDraw.Draw(img)
            
            # Desenhar clips da timeline
            x_offset = 10
            for i, clip in enumerate(timeline_data):
                clip_width = max(60, clip.get("duration", 3) * 20)
                
                # Cor baseada no tipo
                clip_type = clip.get("type", "scene")
                color = self._get_clip_color(clip_type)
                
                # Desenhar clip
                draw.rectangle(
                    [x_offset, 20, x_offset + clip_width, 60],
                    fill=color,
                    outline="#4fc3f7",
                    width=1
                )
                
                # Adicionar texto
                title = clip.get("title", f"Clip {i+1}")
                try:
                    font = ImageFont.load_default()
                    text_bbox = draw.textbbox((0, 0), title, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = x_offset + (clip_width - text_width) // 2
                    draw.text((text_x, 35), title, fill="white", font=font)
                except:
                    draw.text((x_offset + 5, 35), title[:8], fill="white")
                
                x_offset += clip_width + 5
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            logger.error(f"Erro ao gerar preview da timeline: {e}")
            return self._generate_error_preview()
    
    async def _add_element_to_preview(self, img: Image.Image, element: Dict[str, Any]):
        """Adicionar elemento ao preview"""
        try:
            element_type = element.get("type", "unknown")
            x = int(element.get("x", 0) * self.preview_size[0] / 1920)  # Escalar posição
            y = int(element.get("y", 0) * self.preview_size[1] / 1080)
            width = int(element.get("width", 100) * self.preview_size[0] / 1920)
            height = int(element.get("height", 50) * self.preview_size[1] / 1080)
            
            draw = ImageDraw.Draw(img)
            
            if element_type == "image":
                # Tentar carregar imagem real
                asset_path = element.get("asset_path")
                if asset_path and os.path.exists(asset_path):
                    try:
                        element_img = Image.open(asset_path)
                        element_img = element_img.resize((width, height))
                        img.paste(element_img, (x, y))
                        return
                    except:
                        pass
                
                # Fallback: retângulo colorido
                draw.rectangle([x, y, x + width, y + height], fill="#10b981", outline="#059669")
                
            elif element_type == "video":
                draw.rectangle([x, y, x + width, y + height], fill="#8b5cf6", outline="#7c3aed")
                # Adicionar ícone de play
                play_x = x + width // 2 - 8
                play_y = y + height // 2 - 8
                draw.polygon([(play_x, play_y), (play_x + 16, play_y + 8), (play_x, play_y + 16)], fill="white")
                
            elif element_type == "text":
                draw.rectangle([x, y, x + width, y + height], fill="#f59e0b", outline="#d97706")
                text = element.get("text", "Texto")[:10]
                try:
                    font = ImageFont.load_default()
                    draw.text((x + 5, y + 5), text, fill="white", font=font)
                except:
                    draw.text((x + 5, y + 5), text, fill="white")
                    
            elif element_type == "audio":
                draw.rectangle([x, y, x + width, y + height], fill="#ef4444", outline="#dc2626")
                # Adicionar ondas sonoras
                for i in range(3):
                    wave_x = x + 5 + i * 5
                    draw.line([(wave_x, y + 5), (wave_x, y + height - 5)], fill="white", width=2)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar elemento ao preview: {e}")
    
    async def _preview_image_element(self, element_data: Dict[str, Any]) -> str:
        """Preview específico para elemento de imagem"""
        try:
            asset_path = element_data.get("asset_path")
            if asset_path and os.path.exists(asset_path):
                # Carregar e redimensionar imagem
                img = Image.open(asset_path)
                img.thumbnail((200, 150), Image.Resampling.LANCZOS)
                
                # Converter para base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_data = base64.b64encode(buffer.getvalue()).decode()
                
                return f"data:image/jpeg;base64,{img_data}"
            
            return self._generate_placeholder_preview("image")
            
        except Exception as e:
            logger.error(f"Erro no preview de imagem: {e}")
            return self._generate_error_preview()
    
    async def _preview_video_element(self, element_data: Dict[str, Any]) -> str:
        """Preview específico para elemento de vídeo"""
        try:
            # Para vídeo, gerar thumbnail do primeiro frame
            asset_path = element_data.get("asset_path")
            if asset_path and os.path.exists(asset_path):
                try:
                    # Tentar extrair frame com moviepy (se disponível)
                    from moviepy.editor import VideoFileClip
                    
                    clip = VideoFileClip(asset_path)
                    frame = clip.get_frame(0)  # Primeiro frame
                    
                    # Converter numpy array para PIL Image
                    img = Image.fromarray(frame)
                    img.thumbnail((200, 150), Image.Resampling.LANCZOS)
                    
                    # Adicionar ícone de play
                    draw = ImageDraw.Draw(img)
                    width, height = img.size
                    play_x = width // 2 - 15
                    play_y = height // 2 - 15
                    draw.polygon([(play_x, play_y), (play_x + 30, play_y + 15), (play_x, play_y + 30)], 
                               fill="white", outline="black")
                    
                    # Converter para base64
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=85)
                    img_data = base64.b64encode(buffer.getvalue()).decode()
                    
                    clip.close()
                    return f"data:image/jpeg;base64,{img_data}"
                    
                except ImportError:
                    # MoviePy não disponível
                    pass
                except Exception as e:
                    logger.warning(f"Erro ao extrair frame do vídeo: {e}")
            
            return self._generate_placeholder_preview("video")
            
        except Exception as e:
            logger.error(f"Erro no preview de vídeo: {e}")
            return self._generate_error_preview()
    
    async def _preview_text_element(self, element_data: Dict[str, Any]) -> str:
        """Preview específico para elemento de texto"""
        try:
            text = element_data.get("text", "Texto")
            font_size = element_data.get("font_size", 24)
            color = element_data.get("color", "#ffffff")
            
            # Criar imagem para o texto
            img = Image.new("RGBA", (300, 100), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                # Tentar usar fonte personalizada
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Desenhar texto
            draw.text((10, 20), text[:30], fill=self._hex_to_rgb(color), font=font)
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            logger.error(f"Erro no preview de texto: {e}")
            return self._generate_error_preview()
    
    async def _preview_audio_element(self, element_data: Dict[str, Any]) -> str:
        """Preview específico para elemento de áudio"""
        try:
            # Gerar waveform visual para áudio
            img = Image.new("RGB", (200, 60), "#2d3748")
            draw = ImageDraw.Draw(img)
            
            # Simular waveform
            import random
            for i in range(0, 200, 3):
                height = random.randint(5, 50)
                draw.line([(i, 30 - height//2), (i, 30 + height//2)], fill="#4fc3f7", width=2)
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            logger.error(f"Erro no preview de áudio: {e}")
            return self._generate_error_preview()
    
    def _add_title_to_preview(self, img: Image.Image, draw: ImageDraw.Draw, title: str):
        """Adicionar título ao preview"""
        try:
            font = ImageFont.load_default()
            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Posição centralizada na parte inferior
            x = (self.preview_size[0] - text_width) // 2
            y = self.preview_size[1] - text_height - 20
            
            # Fundo semi-transparente para o texto
            draw.rectangle([x - 5, y - 5, x + text_width + 5, y + text_height + 5], 
                         fill=(0, 0, 0, 128))
            
            # Desenhar texto
            draw.text((x, y), title, fill="white", font=font)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar título: {e}")
    
    def _add_gradient(self, img: Image.Image, draw: ImageDraw.Draw):
        """Adicionar gradiente sutil ao background"""
        try:
            width, height = img.size
            for i in range(height // 2):
                alpha = i / (height // 2) * 0.1
                color = tuple(max(0, min(255, int(c * (1 + alpha)))) 
                             for c in self._hex_to_rgb(self.background_color))
                draw.line([(0, i), (width, i)], fill=color)
        except Exception as e:
            logger.error(f"Erro ao adicionar gradiente: {e}")
    
    def _generate_cache_key(self, scene_data: Dict[str, Any]) -> str:
        """Gerar chave única para cache do preview"""
        # Criar hash baseado nos dados relevantes da cena
        import hashlib
        
        relevant_data = {
            "title": scene_data.get("title", ""),
            "elements": scene_data.get("elements", []),
            "background": scene_data.get("background_color", self.background_color)
        }
        
        data_str = json.dumps(relevant_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Converter cor hex para RGB"""
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _get_clip_color(self, clip_type: str) -> str:
        """Obter cor baseada no tipo de clip"""
        colors = {
            "scene": "#667eea",
            "audio": "#ef4444",
            "video": "#8b5cf6",
            "image": "#10b981",
            "text": "#f59e0b"
        }
        return colors.get(clip_type, "#6b7280")
    
    def _generate_placeholder_preview(self, element_type: str) -> str:
        """Gerar preview placeholder"""
        try:
            img = Image.new("RGB", (150, 100), "#4a5568")
            draw = ImageDraw.Draw(img)
            
            # Ícone baseado no tipo
            icons = {
                "image": "🖼️",
                "video": "🎬",
                "audio": "🎵",
                "text": "📝",
                "unknown": "❓"
            }
            
            icon = icons.get(element_type, "❓")
            draw.text((60, 40), icon, fill="white")
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            logger.error(f"Erro ao gerar placeholder: {e}")
            return self._generate_error_preview()
    
    def _generate_error_preview(self) -> str:
        """Gerar preview de erro"""
        try:
            img = Image.new("RGB", (150, 100), "#ef4444")
            draw = ImageDraw.Draw(img)
            draw.text((50, 40), "ERRO", fill="white")
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
        except:
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # WebSocket para updates em tempo real
    async def connect_websocket(self, websocket: WebSocket):
        """Conectar WebSocket para updates em tempo real"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect_websocket(self, websocket: WebSocket):
        """Desconectar WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast_preview_update(self, preview_data: Dict[str, Any]):
        """Broadcast de update de preview para todos os clientes conectados"""
        if self.active_connections:
            message = json.dumps({
                "type": "preview_update",
                "data": preview_data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Enviar para todas as conexões ativas
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Remover conexões desconectadas
            for connection in disconnected:
                self.active_connections.remove(connection)

# Instância global do serviço
preview_service = PreviewService()

# ============================================================================
# ENDPOINTS DA API
# ============================================================================

@router.post("/scene/preview")
async def generate_scene_preview(
    scene_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Gerar preview de uma cena"""
    try:
        preview_url = await preview_service.generate_scene_preview(scene_data)
        
        return {
            "success": True,
            "preview_url": preview_url,
            "cache_key": preview_service._generate_cache_key(scene_data),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar preview da cena: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/element/preview")
async def generate_element_preview(
    element_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Gerar preview de um elemento"""
    try:
        preview_url = await preview_service.generate_element_preview(element_data)
        
        return {
            "success": True,
            "preview_url": preview_url,
            "element_type": element_data.get("type", "unknown"),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar preview do elemento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/timeline/preview")
async def generate_timeline_preview(
    timeline_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Gerar preview da timeline"""
    try:
        clips = timeline_data.get("clips", [])
        preview_url = await preview_service.generate_timeline_preview(clips)
        
        return {
            "success": True,
            "preview_url": preview_url,
            "clips_count": len(clips),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar preview da timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/preview/live")
async def websocket_preview_updates(websocket: WebSocket):
    """WebSocket para updates de preview em tempo real"""
    await preview_service.connect_websocket(websocket)
    
    try:
        while True:
            # Receber dados do cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "scene_update":
                # Gerar preview da cena atualizada
                scene_data = message.get("scene_data", {})
                preview_url = await preview_service.generate_scene_preview(scene_data)
                
                # Broadcast do preview atualizado
                await preview_service.broadcast_preview_update({
                    "scene_id": scene_data.get("id"),
                    "preview_url": preview_url
                })
                
            elif message.get("type") == "element_update":
                # Gerar preview do elemento atualizado
                element_data = message.get("element_data", {})
                preview_url = await preview_service.generate_element_preview(element_data)
                
                # Broadcast do preview atualizado
                await preview_service.broadcast_preview_update({
                    "element_id": element_data.get("id"),
                    "preview_url": preview_url
                })
                
    except WebSocketDisconnect:
        preview_service.disconnect_websocket(websocket)
    except Exception as e:
        logger.error(f"Erro no WebSocket de preview: {e}")
        preview_service.disconnect_websocket(websocket)

@router.get("/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Obter estatísticas do cache de previews"""
    return {
        "success": True,
        "cache_size": len(preview_service.preview_cache),
        "active_connections": len(preview_service.active_connections),
        "stats": {
            "total_previews_cached": len(preview_service.preview_cache),
            "websocket_connections": len(preview_service.active_connections)
        }
    }

@router.delete("/cache/clear")
async def clear_preview_cache(current_user: User = Depends(get_current_user)):
    """Limpar cache de previews"""
    preview_service.preview_cache.clear()
    
    return {
        "success": True,
        "message": "Cache de previews limpo",
        "cleared_at": datetime.now().isoformat()
    }