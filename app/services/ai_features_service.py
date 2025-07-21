"""
Serviço de Features de IA - TecnoCursos AI
Sistema completo para auto-edição e sugestões inteligentes
"""

import os
import uuid
import json
import asyncio
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIFeatureType(Enum):
    """Tipos de features de IA"""
    AUTO_EDIT = "auto_edit"
    SCENE_ANALYSIS = "scene_analysis"
    TEXT_SUGGESTIONS = "text_suggestions"
    COLOR_GRADING = "color_grading"
    AUDIO_ANALYSIS = "audio_analysis"
    SMART_CROPPING = "smart_cropping"
    CONTENT_DETECTION = "content_detection"
    STYLE_TRANSFER = "style_transfer"
    VOICE_SYNTHESIS = "voice_synthesis"
    SMART_TRANSITIONS = "smart_transitions"

class ContentType(Enum):
    """Tipos de conteúdo"""
    EDUCATIONAL = "educational"
    CORPORATE = "corporate"
    MARKETING = "marketing"
    ENTERTAINMENT = "entertainment"
    SOCIAL_MEDIA = "social_media"
    PRESENTATION = "presentation"

@dataclass
class AIAnalysis:
    """Resultado de análise de IA"""
    id: str
    feature_type: AIFeatureType
    confidence: float
    suggestions: List[Dict[str, Any]]
    analysis_data: Dict[str, Any]
    processing_time: float
    created_at: datetime

@dataclass
class AITemplate:
    """Template gerado por IA"""
    id: str
    name: str
    content_type: ContentType
    scenes: List[Dict[str, Any]]
    suggested_duration: float
    style_guide: Dict[str, Any]
    description: str

class AIFeaturesService:
    """Serviço completo para features de IA"""
    
    def __init__(self):
        self.data_dir = Path("data/ai_features")
        self.models_dir = self.data_dir / "models"
        self.cache_dir = self.data_dir / "cache"
        
        # Criar diretórios
        for directory in [self.data_dir, self.models_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configurações OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key and OPENAI_AVAILABLE:
            openai.api_key = self.openai_api_key
        
        # Cache de análises
        self.analysis_cache = {}
        
        # Templates de prompt para IA
        self.prompts = self._load_ai_prompts()
        
        # Estilos visuais predefinidos
        self.visual_styles = self._load_visual_styles()
        
        logger.info("🤖 AI Features Service inicializado")
    
    def _load_ai_prompts(self) -> Dict[str, str]:
        """Carregar prompts para IA"""
        return {
            "auto_edit": """
                Você é um editor de vídeo profissional. Analise o seguinte projeto de vídeo e sugira melhorias:
                
                Projeto: {project_data}
                Objetivo: {content_type}
                Duração alvo: {target_duration} segundos
                
                Forneça sugestões específicas para:
                1. Estrutura das cenas
                2. Timing e ritmo
                3. Transições apropriadas
                4. Elementos visuais
                5. Texto e títulos
                
                Responda em formato JSON com as sugestões.
            """,
            
            "scene_analysis": """
                Analise esta cena de vídeo e sugira melhorias:
                
                Cena: {scene_data}
                Contexto: {context}
                
                Identifique:
                1. Problemas visuais
                2. Oportunidades de melhoria
                3. Elementos em falta
                4. Sugestões de texto
                5. Recomendações de cores
                
                Formato de resposta: JSON estruturado.
            """,
            
            "text_suggestions": """
                Gere sugestões de texto para esta cena educacional:
                
                Tópico: {topic}
                Audiência: {audience}
                Duração: {duration} segundos
                Estilo: {style}
                
                Crie:
                1. Título principal (máximo 50 caracteres)
                2. Subtítulo (máximo 80 caracteres)
                3. Pontos-chave (3-5 bullets)
                4. Call-to-action
                
                Resposta em JSON.
            """,
            
            "content_optimization": """
                Otimize este conteúdo para {platform}:
                
                Conteúdo atual: {content}
                Objetivo: {goal}
                Audiência: {target_audience}
                
                Sugira:
                1. Ajustes no formato
                2. Duração ideal
                3. Elementos de engajamento
                4. Hashtags/palavras-chave
                5. Momentos de call-to-action
            """
        }
    
    def _load_visual_styles(self) -> Dict[str, Dict[str, Any]]:
        """Carregar estilos visuais predefinidos"""
        return {
            "modern_minimal": {
                "colors": ["#ffffff", "#f8f9fa", "#6c757d", "#343a40"],
                "fonts": ["Inter", "Roboto", "Open Sans"],
                "transitions": ["fade", "slide_up"],
                "pace": "medium",
                "description": "Estilo limpo e moderno"
            },
            "corporate_professional": {
                "colors": ["#ffffff", "#f8f9fa", "#0d6efd", "#198754"],
                "fonts": ["Arial", "Helvetica", "Segoe UI"],
                "transitions": ["crossfade", "wipe_right"],
                "pace": "slow",
                "description": "Estilo corporativo profissional"
            },
            "creative_dynamic": {
                "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"],
                "fonts": ["Montserrat", "Poppins", "Nunito"],
                "transitions": ["zoom_in", "slide_left", "circle_in"],
                "pace": "fast",
                "description": "Estilo criativo e dinâmico"
            },
            "educational_friendly": {
                "colors": ["#ffffff", "#e3f2fd", "#2196f3", "#ff9800"],
                "fonts": ["Open Sans", "Lato", "Source Sans Pro"],
                "transitions": ["fade", "slide_down"],
                "pace": "medium",
                "description": "Estilo educacional amigável"
            }
        }
    
    async def analyze_project_with_ai(self, project_data: Dict[str, Any], 
                                     content_type: ContentType = ContentType.EDUCATIONAL) -> AIAnalysis:
        """Analisar projeto completo com IA"""
        try:
            start_time = datetime.now()
            
            # Cache key
            cache_key = f"project_analysis_{hash(str(project_data))}"
            
            if cache_key in self.analysis_cache:
                logger.info("📋 Usando análise em cache")
                return self.analysis_cache[cache_key]
            
            # Preparar prompt
            target_duration = sum(scene.get("duration", 3) for scene in project_data.get("scenes", []))
            
            if OPENAI_AVAILABLE and self.openai_api_key:
                suggestions = await self._analyze_with_openai(project_data, content_type, target_duration)
            else:
                suggestions = await self._analyze_with_rules(project_data, content_type, target_duration)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            analysis = AIAnalysis(
                id=str(uuid.uuid4()),
                feature_type=AIFeatureType.AUTO_EDIT,
                confidence=0.85,
                suggestions=suggestions,
                analysis_data={
                    "content_type": content_type.value,
                    "total_scenes": len(project_data.get("scenes", [])),
                    "total_duration": target_duration,
                    "complexity_score": self._calculate_complexity(project_data)
                },
                processing_time=processing_time,
                created_at=datetime.now()
            )
            
            # Cache do resultado
            self.analysis_cache[cache_key] = analysis
            
            logger.info(f"🤖 Análise IA concluída em {processing_time:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise IA: {e}")
            # Fallback para análise baseada em regras
            return await self._analyze_with_rules(project_data, content_type, target_duration)
    
    async def _analyze_with_openai(self, project_data: Dict[str, Any], 
                                  content_type: ContentType, target_duration: float) -> List[Dict[str, Any]]:
        """Análise usando OpenAI GPT"""
        try:
            prompt = self.prompts["auto_edit"].format(
                project_data=json.dumps(project_data, indent=2)[:2000],  # Limitar tamanho
                content_type=content_type.value,
                target_duration=target_duration
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em edição de vídeo educacional."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Tentar parsear JSON
            try:
                suggestions = json.loads(ai_response)
                if isinstance(suggestions, dict):
                    # Converter para lista de sugestões
                    formatted_suggestions = []
                    for category, items in suggestions.items():
                        if isinstance(items, list):
                            for item in items:
                                formatted_suggestions.append({
                                    "type": category,
                                    "suggestion": item,
                                    "priority": "medium",
                                    "confidence": 0.8
                                })
                    return formatted_suggestions
                return suggestions
            except:
                # Se não conseguir parsear, criar sugestões baseadas no texto
                return self._parse_text_suggestions(ai_response)
            
        except Exception as e:
            logger.error(f"Erro na análise OpenAI: {e}")
            raise
    
    async def _analyze_with_rules(self, project_data: Dict[str, Any], 
                                 content_type: ContentType, target_duration: float) -> List[Dict[str, Any]]:
        """Análise baseada em regras (fallback)"""
        try:
            suggestions = []
            scenes = project_data.get("scenes", [])
            
            # Análise de estrutura
            if len(scenes) < 3:
                suggestions.append({
                    "type": "structure",
                    "suggestion": "Considere adicionar mais cenas para melhor estrutura narrativa",
                    "priority": "high",
                    "confidence": 0.9,
                    "action": "add_scene",
                    "details": "Projetos educacionais se beneficiam de introdução, desenvolvimento e conclusão"
                })
            
            # Análise de duração
            for i, scene in enumerate(scenes):
                duration = scene.get("duration", 3)
                if duration < 2:
                    suggestions.append({
                        "type": "timing",
                        "suggestion": f"Cena {i+1} muito rápida. Considere aumentar para pelo menos 3 segundos",
                        "priority": "medium",
                        "confidence": 0.8,
                        "action": "extend_duration",
                        "scene_id": scene.get("id"),
                        "suggested_duration": 3
                    })
                elif duration > 10:
                    suggestions.append({
                        "type": "timing",
                        "suggestion": f"Cena {i+1} muito longa. Considere dividir em cenas menores",
                        "priority": "medium",
                        "confidence": 0.7,
                        "action": "split_scene",
                        "scene_id": scene.get("id"),
                        "suggested_duration": 6
                    })
            
            # Análise de elementos
            for i, scene in enumerate(scenes):
                elements = scene.get("elements", [])
                if not elements:
                    suggestions.append({
                        "type": "content",
                        "suggestion": f"Cena {i+1} está vazia. Adicione elementos visuais",
                        "priority": "high",
                        "confidence": 0.9,
                        "action": "add_elements",
                        "scene_id": scene.get("id"),
                        "suggested_elements": ["text", "image"]
                    })
                
                # Verificar se há texto
                has_text = any(el.get("type") == "text" for el in elements)
                if not has_text and content_type == ContentType.EDUCATIONAL:
                    suggestions.append({
                        "type": "content",
                        "suggestion": f"Cena {i+1} sem texto explicativo. Adicione títulos ou descrições",
                        "priority": "medium",
                        "confidence": 0.8,
                        "action": "add_text",
                        "scene_id": scene.get("id")
                    })
            
            # Sugestões de estilo
            style_suggestions = self._suggest_visual_style(content_type, scenes)
            suggestions.extend(style_suggestions)
            
            # Sugestões de transições
            transition_suggestions = self._suggest_transitions(scenes)
            suggestions.extend(transition_suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro na análise por regras: {e}")
            return []
    
    def _suggest_visual_style(self, content_type: ContentType, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sugerir estilo visual baseado no tipo de conteúdo"""
        suggestions = []
        
        # Mapear tipo de conteúdo para estilo
        content_to_style = {
            ContentType.EDUCATIONAL: "educational_friendly",
            ContentType.CORPORATE: "corporate_professional",
            ContentType.MARKETING: "creative_dynamic",
            ContentType.PRESENTATION: "modern_minimal"
        }
        
        recommended_style = content_to_style.get(content_type, "modern_minimal")
        style_data = self.visual_styles[recommended_style]
        
        suggestions.append({
            "type": "style",
            "suggestion": f"Aplicar estilo {style_data['description']}",
            "priority": "low",
            "confidence": 0.7,
            "action": "apply_style",
            "style_data": {
                "colors": style_data["colors"],
                "fonts": style_data["fonts"],
                "transitions": style_data["transitions"]
            }
        })
        
        return suggestions
    
    def _suggest_transitions(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sugerir transições entre cenas"""
        suggestions = []
        
        if len(scenes) <= 1:
            return suggestions
        
        # Análise simples de transições
        for i in range(len(scenes) - 1):
            current_scene = scenes[i]
            next_scene = scenes[i + 1]
            
            # Sugerir transição baseada no conteúdo
            current_has_text = any(el.get("type") == "text" for el in current_scene.get("elements", []))
            next_has_text = any(el.get("type") == "text" for el in next_scene.get("elements", []))
            
            if current_has_text and next_has_text:
                suggested_transition = "fade"
            elif not current_has_text and next_has_text:
                suggested_transition = "slide_up"
            else:
                suggested_transition = "crossfade"
            
            suggestions.append({
                "type": "transition",
                "suggestion": f"Usar transição '{suggested_transition}' entre cenas {i+1} e {i+2}",
                "priority": "low",
                "confidence": 0.6,
                "action": "set_transition",
                "from_scene": current_scene.get("id"),
                "to_scene": next_scene.get("id"),
                "transition_type": suggested_transition,
                "duration": 0.5
            })
        
        return suggestions
    
    async def generate_text_suggestions(self, topic: str, audience: str = "estudantes", 
                                      duration: float = 5.0, style: str = "educacional") -> List[Dict[str, Any]]:
        """Gerar sugestões de texto para um tópico"""
        try:
            if OPENAI_AVAILABLE and self.openai_api_key:
                return await self._generate_text_with_openai(topic, audience, duration, style)
            else:
                return await self._generate_text_with_templates(topic, audience, duration, style)
            
        except Exception as e:
            logger.error(f"Erro ao gerar texto: {e}")
            return await self._generate_text_with_templates(topic, audience, duration, style)
    
    async def _generate_text_with_openai(self, topic: str, audience: str, 
                                        duration: float, style: str) -> List[Dict[str, Any]]:
        """Gerar texto usando OpenAI"""
        try:
            prompt = self.prompts["text_suggestions"].format(
                topic=topic,
                audience=audience,
                duration=duration,
                style=style
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em conteúdo educacional."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            ai_response = response.choices[0].message.content
            
            # Tentar parsear resposta
            try:
                return json.loads(ai_response)
            except:
                return self._parse_text_response(ai_response)
            
        except Exception as e:
            logger.error(f"Erro no texto OpenAI: {e}")
            raise
    
    async def _generate_text_with_templates(self, topic: str, audience: str,
                                          duration: float, style: str) -> List[Dict[str, Any]]:
        """Gerar texto usando templates (fallback)"""
        try:
            suggestions = []
            
            # Template básico baseado no tópico
            title_templates = [
                f"Aprenda sobre {topic}",
                f"Guia completo: {topic}",
                f"Tudo sobre {topic}",
                f"Dominando {topic}"
            ]
            
            subtitle_templates = [
                f"Conceitos essenciais para {audience}",
                f"Informações práticas e aplicáveis",
                f"Conhecimento que faz a diferença",
                f"Do básico ao avançado"
            ]
            
            # Gerar sugestões
            for i, title in enumerate(title_templates[:2]):
                suggestions.append({
                    "type": "title",
                    "text": title,
                    "confidence": 0.7 - (i * 0.1),
                    "style_suggestions": {
                        "font_size": 48 if duration > 3 else 36,
                        "font_weight": "bold",
                        "color": "#ffffff"
                    }
                })
            
            for i, subtitle in enumerate(subtitle_templates[:2]):
                suggestions.append({
                    "type": "subtitle",
                    "text": subtitle,
                    "confidence": 0.6 - (i * 0.1),
                    "style_suggestions": {
                        "font_size": 24,
                        "font_style": "italic",
                        "color": "#e0e0e0"
                    }
                })
            
            # Pontos-chave genéricos
            key_points = [
                "Conceitos fundamentais",
                "Aplicações práticas",
                "Dicas importantes",
                "Exemplos reais"
            ]
            
            suggestions.append({
                "type": "bullet_points",
                "text": key_points,
                "confidence": 0.5,
                "style_suggestions": {
                    "font_size": 18,
                    "line_height": 1.4
                }
            })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro nos templates de texto: {e}")
            return []
    
    async def auto_enhance_image(self, image_path: str) -> Dict[str, Any]:
        """Auto-melhorar imagem usando IA"""
        try:
            if not PIL_AVAILABLE:
                return {"success": False, "error": "PIL não disponível"}
            
            # Carregar imagem
            img = Image.open(image_path)
            
            # Aplicar melhorias automáticas
            enhanced_img = img.copy()
            
            # Auto-contraste
            enhancer = ImageEnhance.Contrast(enhanced_img)
            enhanced_img = enhancer.enhance(1.1)
            
            # Auto-nitidez
            enhanced_img = enhanced_img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Auto-saturação
            enhancer = ImageEnhance.Color(enhanced_img)
            enhanced_img = enhancer.enhance(1.05)
            
            # Salvar resultado
            output_path = image_path.replace(".", "_enhanced.")
            enhanced_img.save(output_path, quality=95, optimize=True)
            
            return {
                "success": True,
                "enhanced_path": output_path,
                "improvements": [
                    "Contraste otimizado",
                    "Nitidez aprimorada", 
                    "Cores realçadas"
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro no enhancement de imagem: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_ai_template(self, content_type: ContentType, topic: str,
                                 target_duration: float = 30) -> AITemplate:
        """Gerar template completo usando IA"""
        try:
            # Determinar número de cenas baseado na duração
            num_scenes = max(3, min(8, int(target_duration / 5)))
            scene_duration = target_duration / num_scenes
            
            scenes = []
            
            # Gerar cenas
            for i in range(num_scenes):
                scene_type = "intro" if i == 0 else "outro" if i == num_scenes - 1 else "content"
                
                scene = {
                    "id": f"scene_{i+1}",
                    "title": f"Cena {i+1}",
                    "type": scene_type,
                    "duration": scene_duration,
                    "elements": []
                }
                
                # Adicionar elementos baseados no tipo
                if scene_type == "intro":
                    scene["elements"] = [
                        {
                            "type": "text",
                            "text": f"Introdução: {topic}",
                            "x": 100,
                            "y": 200,
                            "font_size": 48,
                            "color": "#ffffff"
                        }
                    ]
                elif scene_type == "outro":
                    scene["elements"] = [
                        {
                            "type": "text",
                            "text": "Obrigado pela atenção!",
                            "x": 100,
                            "y": 200,
                            "font_size": 36,
                            "color": "#ffffff"
                        }
                    ]
                else:
                    scene["elements"] = [
                        {
                            "type": "text",
                            "text": f"Tópico {i}: {topic}",
                            "x": 100,
                            "y": 150,
                            "font_size": 32,
                            "color": "#ffffff"
                        }
                    ]
                
                scenes.append(scene)
            
            # Selecionar estilo baseado no tipo de conteúdo
            style_name = {
                ContentType.EDUCATIONAL: "educational_friendly",
                ContentType.CORPORATE: "corporate_professional",
                ContentType.MARKETING: "creative_dynamic"
            }.get(content_type, "modern_minimal")
            
            style_guide = self.visual_styles[style_name]
            
            template = AITemplate(
                id=str(uuid.uuid4()),
                name=f"Template IA: {topic}",
                content_type=content_type,
                scenes=scenes,
                suggested_duration=target_duration,
                style_guide=style_guide,
                description=f"Template gerado automaticamente para {content_type.value}"
            )
            
            logger.info(f"🎨 Template IA gerado: {num_scenes} cenas, {target_duration}s")
            return template
            
        except Exception as e:
            logger.error(f"Erro ao gerar template IA: {e}")
            raise
    
    def _calculate_complexity(self, project_data: Dict[str, Any]) -> float:
        """Calcular score de complexidade do projeto"""
        try:
            score = 0
            scenes = project_data.get("scenes", [])
            
            # Fator: número de cenas
            score += len(scenes) * 0.1
            
            # Fator: elementos por cena
            total_elements = sum(len(scene.get("elements", [])) for scene in scenes)
            score += total_elements * 0.05
            
            # Fator: tipos de elementos únicos
            element_types = set()
            for scene in scenes:
                for element in scene.get("elements", []):
                    element_types.add(element.get("type", "unknown"))
            score += len(element_types) * 0.15
            
            # Fator: duração total
            total_duration = sum(scene.get("duration", 3) for scene in scenes)
            score += min(total_duration / 60, 1.0) * 0.2  # Max 1 ponto para duração
            
            return min(score, 1.0)  # Normalizar para 0-1
            
        except Exception as e:
            logger.error(f"Erro ao calcular complexidade: {e}")
            return 0.5
    
    def _parse_text_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """Parsear sugestões de texto da resposta IA"""
        try:
            suggestions = []
            
            # Tentar extrair títulos
            title_matches = re.findall(r'título[:\s]*([^\n]+)', text, re.IGNORECASE)
            for title in title_matches:
                suggestions.append({
                    "type": "title",
                    "text": title.strip(),
                    "confidence": 0.7
                })
            
            # Tentar extrair bullets
            bullet_matches = re.findall(r'[•\-\*]\s*([^\n]+)', text)
            if bullet_matches:
                suggestions.append({
                    "type": "bullet_points", 
                    "text": [bullet.strip() for bullet in bullet_matches],
                    "confidence": 0.6
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro ao parsear texto: {e}")
            return []
    
    def _parse_text_response(self, response: str) -> List[Dict[str, Any]]:
        """Parsear resposta de texto não-JSON"""
        try:
            lines = response.strip().split('\n')
            suggestions = []
            
            current_type = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detectar seções
                if 'título' in line.lower():
                    current_type = "title"
                elif 'subtítulo' in line.lower():
                    current_type = "subtitle"
                elif 'pontos' in line.lower() or 'bullets' in line.lower():
                    current_type = "bullet_points"
                elif line.startswith(('1.', '2.', '3.', '-', '•')):
                    if current_type == "bullet_points":
                        current_content.append(line[2:].strip() if line[1] == '.' else line[1:].strip())
                elif ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        suggestions.append({
                            "type": current_type or "text",
                            "text": parts[1].strip(),
                            "confidence": 0.6
                        })
            
            if current_content and current_type == "bullet_points":
                suggestions.append({
                    "type": "bullet_points",
                    "text": current_content,
                    "confidence": 0.6
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro ao parsear resposta: {e}")
            return []

# Instância global do serviço
ai_features_service = AIFeaturesService()

# Funções de conveniência
async def analyze_project_ai(project_data: Dict[str, Any], content_type: str = "educational"):
    """Analisar projeto com IA"""
    content_type_enum = ContentType(content_type)
    return await ai_features_service.analyze_project_with_ai(project_data, content_type_enum)

async def generate_text_ai(topic: str, audience: str = "estudantes"):
    """Gerar texto com IA"""
    return await ai_features_service.generate_text_suggestions(topic, audience)

async def create_ai_template(content_type: str, topic: str, duration: float = 30):
    """Criar template com IA"""
    content_type_enum = ContentType(content_type)
    return await ai_features_service.generate_ai_template(content_type_enum, topic, duration)