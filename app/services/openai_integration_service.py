"""
Serviço de Integração OpenAI - TecnoCursos AI
===========================================

Integração completa com OpenAI GPT-4 para:
- Estruturação de conteúdo educacional
- Geração de scripts para narração
- Análise e melhoria de textos
- Criação de resumos e títulos
- Fallback inteligente para mocks

Funcionalidades:
- Rate limiting automático
- Retry com backoff exponencial
- Cache de respostas
- Monitoramento de uso e custos
- Validação de entrada e saída
- Logs detalhados
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import logging

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.config import settings, get_api_configs
from app.services.mock_integration_service import mock_service, MockResponse

logger = logging.getLogger(__name__)

@dataclass
class OpenAIUsage:
    """Informações de uso da API OpenAI"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float = 0.0
    model: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ContentStructureRequest:
    """Request para estruturação de conteúdo"""
    text: str
    content_type: str = "educational"  # educational, course, presentation
    target_audience: str = "general"   # general, beginner, intermediate, advanced
    language: str = "pt"
    max_sections: int = 10
    include_examples: bool = True

@dataclass
class NarrationScriptRequest:
    """Request para geração de script de narração"""
    content: str
    tone: str = "professional"  # professional, friendly, casual, academic
    duration_minutes: int = 5
    voice_style: str = "neutral"  # neutral, enthusiastic, calm
    include_pauses: bool = True

class OpenAIIntegrationService:
    """Serviço principal de integração OpenAI"""
    
    def __init__(self):
        self.config = get_api_configs().get("openai", {})
        self.enabled = self.config.get("enabled", False) and OPENAI_AVAILABLE
        self.usage_history: List[OpenAIUsage] = []
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Rate limiting
        self.requests_per_minute = 50
        self.requests_history = []
        
        # Pricing (GPT-4 Turbo - valores aproximados)
        self.pricing = {
            "gpt-4-turbo-preview": {
                "input": 0.01 / 1000,   # $0.01 per 1K tokens
                "output": 0.03 / 1000   # $0.03 per 1K tokens
            },
            "gpt-3.5-turbo": {
                "input": 0.0015 / 1000,
                "output": 0.002 / 1000
            }
        }
        
        if self.enabled:
            self.client = AsyncOpenAI(
                api_key=self.config["api_key"],
                organization=self.config.get("org_id"),
                timeout=self.config.get("timeout", 60)
            )
            logger.info("✅ OpenAI Integration Service inicializado")
        else:
            self.client = None
            logger.warning("⚠️ OpenAI não disponível - usando mocks")
    
    def _calculate_cost(self, usage: Dict, model: str) -> float:
        """Calcula custo da requisição"""
        if model not in self.pricing:
            return 0.0
        
        pricing = self.pricing[model]
        input_cost = usage.get("prompt_tokens", 0) * pricing["input"]
        output_cost = usage.get("completion_tokens", 0) * pricing["output"]
        
        return input_cost + output_cost
    
    def _get_cache_key(self, data: Dict) -> str:
        """Gera chave de cache para a requisição"""
        cache_string = json.dumps(data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Verifica se cache ainda é válido"""
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    async def _check_rate_limit(self):
        """Verifica e aplica rate limiting"""
        now = time.time()
        # Remove requests mais antigos que 1 minuto
        self.requests_history = [
            req_time for req_time in self.requests_history 
            if now - req_time < 60
        ]
        
        if len(self.requests_history) >= self.requests_per_minute:
            wait_time = 60 - (now - self.requests_history[0])
            if wait_time > 0:
                logger.warning(f"🚦 Rate limit atingido, aguardando {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self.requests_history.append(now)
    
    async def _make_openai_request(self, messages: List[Dict], **kwargs) -> Dict:
        """Faz requisição para OpenAI com retry e error handling"""
        if not self.enabled:
            # Fallback para mock
            prompt = messages[-1]["content"] if messages else ""
            mock_response = await mock_service.mock_openai_completion(prompt, **kwargs)
            return mock_response.data
        
        await self._check_rate_limit()
        
        # Parâmetros padrão
        params = {
            "model": kwargs.get("model", self.config.get("model", "gpt-4-turbo-preview")),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 4000)),
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0)
        }
        
        # Verificar cache
        cache_key = self._get_cache_key(params)
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                logger.debug("📦 Resposta OpenAI obtida do cache")
                return cached_data
        
        # Retry com backoff exponencial
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(**params)
                
                # Converter para dict
                response_dict = response.model_dump()
                
                # Registrar uso
                usage_info = OpenAIUsage(
                    prompt_tokens=response_dict["usage"]["prompt_tokens"],
                    completion_tokens=response_dict["usage"]["completion_tokens"],
                    total_tokens=response_dict["usage"]["total_tokens"],
                    cost_usd=self._calculate_cost(response_dict["usage"], params["model"]),
                    model=params["model"]
                )
                self.usage_history.append(usage_info)
                
                # Cache da resposta
                self.cache[cache_key] = (response_dict, datetime.now())
                
                logger.info(f"✅ OpenAI request successful - tokens: {usage_info.total_tokens}, cost: ${usage_info.cost_usd:.4f}")
                return response_dict
                
            except openai.RateLimitError as e:
                wait_time = 2 ** attempt
                logger.warning(f"🚦 Rate limit error, aguardando {wait_time}s")
                await asyncio.sleep(wait_time)
                
            except openai.APIError as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ OpenAI API error após {max_retries} tentativas: {e}")
                    # Fallback para mock
                    prompt = messages[-1]["content"] if messages else ""
                    mock_response = await mock_service.mock_openai_completion(prompt, **kwargs)
                    return mock_response.data
                
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado na OpenAI: {e}")
                # Fallback para mock
                prompt = messages[-1]["content"] if messages else ""
                mock_response = await mock_service.mock_openai_completion(prompt, **kwargs)
                return mock_response.data
        
        # Se chegou aqui, todas as tentativas falharam
        logger.error("❌ Todas as tentativas OpenAI falharam, usando mock")
        prompt = messages[-1]["content"] if messages else ""
        mock_response = await mock_service.mock_openai_completion(prompt, **kwargs)
        return mock_response.data
    
    async def structure_educational_content(self, request: ContentStructureRequest) -> Dict[str, Any]:
        """Estrutura conteúdo educacional usando IA"""
        
        prompt = f"""
Como especialista em design educacional, estruture o seguinte conteúdo:

CONTEÚDO:
{request.text}

PARÂMETROS:
- Tipo: {request.content_type}
- Público-alvo: {request.target_audience}
- Idioma: {request.language}
- Máximo de seções: {request.max_sections}
- Incluir exemplos: {'Sim' if request.include_examples else 'Não'}

INSTRUÇÕES:
1. Crie uma estrutura hierárquica clara
2. Sugira títulos envolventes para cada seção
3. Inclua objetivos de aprendizagem
4. {('Adicione exemplos práticos quando apropriado' if request.include_examples else 'Foque apenas na estrutura conceitual')}
5. Mantenha linguagem adequada ao público-alvo

FORMATO DE RESPOSTA (JSON):
{{
    "title": "Título principal sugerido",
    "learning_objectives": ["objetivo1", "objetivo2"],
    "structure": [
        {{
            "section": "Título da seção",
            "subsections": ["subseção1", "subseção2"],
            "key_points": ["ponto1", "ponto2"],
            "examples": ["exemplo1"] // se aplicável
        }}
    ],
    "estimated_duration": "tempo estimado em minutos",
    "difficulty_level": "iniciante/intermediário/avançado"
}}
"""
        
        messages = [
            {"role": "system", "content": "Você é um especialista em design educacional e estruturação de conteúdo didático."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._make_openai_request(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Tentar parsear JSON
            try:
                structured_content = json.loads(content)
                return {
                    "success": True,
                    "data": structured_content,
                    "tokens_used": response["usage"]["total_tokens"],
                    "cost": self._calculate_cost(response["usage"], response["model"])
                }
            except json.JSONDecodeError:
                # Se não conseguir parsear JSON, retornar texto
                return {
                    "success": True,
                    "data": {"raw_content": content},
                    "tokens_used": response["usage"]["total_tokens"],
                    "cost": self._calculate_cost(response["usage"], response["model"])
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na estruturação de conteúdo: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def generate_narration_script(self, request: NarrationScriptRequest) -> Dict[str, Any]:
        """Gera script de narração otimizado para TTS"""
        
        prompt = f"""
Como especialista em roteiros para narração e TTS, crie um script baseado no conteúdo:

CONTEÚDO:
{request.content}

PARÂMETROS:
- Tom: {request.tone}
- Duração alvo: {request.duration_minutes} minutos
- Estilo de voz: {request.voice_style}
- Incluir pausas: {'Sim' if request.include_pauses else 'Não'}

INSTRUÇÕES:
1. Adapte o conteúdo para narração falada (evite textos muito técnicos)
2. Use linguagem natural e fluida
3. Inclua marcadores de pausa onde apropriado: [PAUSA_CURTA], [PAUSA_MÉDIA], [PAUSA_LONGA]
4. Mantenha ritmo adequado para {request.duration_minutes} minutos
5. Use tom {request.tone} e estilo {request.voice_style}
6. Divida em segmentos de até 200 caracteres para melhor processamento TTS

FORMATO DE RESPOSTA (JSON):
{{
    "script_segments": [
        {{
            "segment_number": 1,
            "text": "Texto do segmento",
            "pause_after": "curta/média/longa/nenhuma",
            "estimated_duration": "segundos"
        }}
    ],
    "total_estimated_duration": "minutos",
    "word_count": 000,
    "reading_speed": "palavras por minuto",
    "tone_analysis": "análise do tom aplicado"
}}
"""
        
        messages = [
            {"role": "system", "content": "Você é um especialista em roteiros para narração e síntese de voz."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._make_openai_request(messages)
            content = response["choices"][0]["message"]["content"]
            
            try:
                script_data = json.loads(content)
                return {
                    "success": True,
                    "data": script_data,
                    "tokens_used": response["usage"]["total_tokens"],
                    "cost": self._calculate_cost(response["usage"], response["model"])
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": {"raw_script": content},
                    "tokens_used": response["usage"]["total_tokens"],
                    "cost": self._calculate_cost(response["usage"], response["model"])
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na geração de script: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def improve_text_quality(self, text: str, improvement_type: str = "general") -> Dict[str, Any]:
        """Melhora qualidade e clareza do texto"""
        
        improvement_prompts = {
            "general": "Melhore a clareza, coesão e qualidade geral do texto",
            "educational": "Adapte para fins educacionais, melhorando didática",
            "professional": "Torne mais profissional e adequado para ambiente corporativo",
            "simplify": "Simplifique para ser mais acessível",
            "academic": "Adapte para padrões acadêmicos"
        }
        
        prompt = f"""
{improvement_prompts.get(improvement_type, improvement_prompts["general"])}:

TEXTO ORIGINAL:
{text}

INSTRUÇÕES:
1. Mantenha o significado original
2. Melhore clareza e fluidez
3. Corrija erros gramaticais
4. Otimize estrutura das frases
5. {improvement_prompts.get(improvement_type, "Melhore qualidade geral")}

Retorne apenas o texto melhorado, sem explicações adicionais.
"""
        
        messages = [
            {"role": "system", "content": "Você é um especialista em revisão e melhoria de textos."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._make_openai_request(messages, temperature=0.3)
            improved_text = response["choices"][0]["message"]["content"].strip()
            
            return {
                "success": True,
                "original_text": text,
                "improved_text": improved_text,
                "improvement_type": improvement_type,
                "tokens_used": response["usage"]["total_tokens"],
                "cost": self._calculate_cost(response["usage"], response["model"])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na melhoria de texto: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text,
                "improved_text": text  # Retorna original em caso de erro
            }
    
    async def generate_title_and_summary(self, content: str, max_title_length: int = 100) -> Dict[str, Any]:
        """Gera título e resumo para o conteúdo"""
        
        prompt = f"""
Analise o conteúdo e gere:

CONTEÚDO:
{content}

TAREFAS:
1. Título envolvente (máximo {max_title_length} caracteres)
2. Resumo conciso (2-3 frases)
3. Palavras-chave principais (5-8 palavras)
4. Categoria de conteúdo
5. Nível de dificuldade

FORMATO JSON:
{{
    "title": "Título sugerido",
    "summary": "Resumo do conteúdo",
    "keywords": ["palavra1", "palavra2"],
    "category": "categoria",
    "difficulty": "iniciante/intermediário/avançado",
    "estimated_reading_time": "minutos"
}}
"""
        
        messages = [
            {"role": "system", "content": "Você é um especialista em análise de conteúdo e criação de metadados."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._make_openai_request(messages, temperature=0.5)
            content_analysis = response["choices"][0]["message"]["content"]
            
            try:
                analysis_data = json.loads(content_analysis)
                return {
                    "success": True,
                    "data": analysis_data,
                    "tokens_used": response["usage"]["total_tokens"],
                    "cost": self._calculate_cost(response["usage"], response["model"])
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": {"raw_analysis": content_analysis},
                    "tokens_used": response["usage"]["total_tokens"],
                    "cost": self._calculate_cost(response["usage"], response["model"])
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na análise de conteúdo: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def get_usage_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Retorna estatísticas de uso dos últimos X dias"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [
            usage for usage in self.usage_history 
            if usage.timestamp >= cutoff_date
        ]
        
        if not recent_usage:
            return {
                "period_days": days,
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_tokens_per_request": 0,
                "models_used": []
            }
        
        total_tokens = sum(usage.total_tokens for usage in recent_usage)
        total_cost = sum(usage.cost_usd for usage in recent_usage)
        models_used = list(set(usage.model for usage in recent_usage))
        
        return {
            "period_days": days,
            "total_requests": len(recent_usage),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_tokens_per_request": total_tokens / len(recent_usage),
            "avg_cost_per_request": total_cost / len(recent_usage),
            "models_used": models_used,
            "daily_breakdown": self._get_daily_breakdown(recent_usage)
        }
    
    def _get_daily_breakdown(self, usage_list: List[OpenAIUsage]) -> List[Dict]:
        """Quebra uso por dia"""
        daily_data = {}
        
        for usage in usage_list:
            date_key = usage.timestamp.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
            
            daily_data[date_key]["requests"] += 1
            daily_data[date_key]["tokens"] += usage.total_tokens
            daily_data[date_key]["cost"] += usage.cost_usd
        
        return list(daily_data.values())
    
    def health_check(self) -> Dict[str, Any]:
        """Health check do serviço OpenAI"""
        return {
            "service": "OpenAI Integration",
            "enabled": self.enabled,
            "api_available": OPENAI_AVAILABLE,
            "cache_entries": len(self.cache),
            "usage_history_count": len(self.usage_history),
            "recent_requests": len([
                req for req in self.requests_history 
                if time.time() - req < 300  # últimos 5 minutos
            ]),
            "status": "healthy" if self.enabled else "mock_mode"
        }

# Instância global do serviço
openai_service = OpenAIIntegrationService()

# Funções de conveniência
async def structure_content(text: str, content_type: str = "educational", **kwargs) -> Dict[str, Any]:
    """Função de conveniência para estruturação de conteúdo"""
    request = ContentStructureRequest(
        text=text,
        content_type=content_type,
        **kwargs
    )
    return await openai_service.structure_educational_content(request)

async def generate_script(content: str, tone: str = "professional", **kwargs) -> Dict[str, Any]:
    """Função de conveniência para geração de script"""
    request = NarrationScriptRequest(
        content=content,
        tone=tone,
        **kwargs
    )
    return await openai_service.generate_narration_script(request)

async def improve_text(text: str, improvement_type: str = "general") -> Dict[str, Any]:
    """Função de conveniência para melhoria de texto"""
    return await openai_service.improve_text_quality(text, improvement_type)

async def analyze_content(content: str, **kwargs) -> Dict[str, Any]:
    """Função de conveniência para análise de conteúdo"""
    return await openai_service.generate_title_and_summary(content, **kwargs)

if __name__ == "__main__":
    # Teste do serviço
    import asyncio
    
    async def test_openai_service():
        print("🤖 Testando OpenAI Integration Service...")
        
        test_content = """
        Python é uma linguagem de programação de alto nível, interpretada e de propósito geral.
        Foi criada por Guido van Rossum e lançada pela primeira vez em 1991.
        Python enfatiza a legibilidade do código e sua sintaxe permite que os programadores
        expressem conceitos em menos linhas de código.
        """
        
        # Teste estruturação
        result = await structure_content(test_content, "course")
        print(f"✅ Estruturação: {result['success']}")
        
        # Teste script
        result = await generate_script(test_content, "friendly")
        print(f"✅ Script: {result['success']}")
        
        # Teste melhoria
        result = await improve_text(test_content, "educational")
        print(f"✅ Melhoria: {result['success']}")
        
        # Estatísticas
        stats = openai_service.get_usage_statistics()
        print(f"📊 Requests: {stats['total_requests']}")
        
        # Health check
        health = openai_service.health_check()
        print(f"🏥 Status: {health['status']}")
    
    asyncio.run(test_openai_service()) 