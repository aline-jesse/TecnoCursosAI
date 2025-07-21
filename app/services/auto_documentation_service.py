"""
Sistema de Documentação Automática Avançada - TecnoCursos AI
==========================================================

Sistema abrangente de documentação incluindo:
- OpenAPI 3.0 completo e detalhado
- Geração automática de SDKs
- Code examples em múltiplas linguagens
- Documentação interativa com Swagger/ReDoc
- Versionamento de documentação
- API changelog automático
- Testing playground integrado

Autor: TecnoCursos AI Team
Data: 2024
"""

import json
import logging
import asyncio
import inspect
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Type, get_type_hints
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import re
import ast
import textwrap
from collections import defaultdict
import uuid

# Configuração de logging
logger = logging.getLogger(__name__)

class DocumentationType(Enum):
    """Tipos de documentação"""
    OPENAPI = "openapi"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    POSTMAN = "postman"
    INSOMNIA = "insomnia"

class CodeLanguage(Enum):
    """Linguagens para code examples"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CURL = "curl"
    PHP = "php"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUBY = "ruby"

class DocumentationSection(Enum):
    """Seções da documentação"""
    INTRODUCTION = "introduction"
    AUTHENTICATION = "authentication"
    QUICKSTART = "quickstart"
    ENDPOINTS = "endpoints"
    SCHEMAS = "schemas"
    EXAMPLES = "examples"
    SDK = "sdk"
    CHANGELOG = "changelog"
    TROUBLESHOOTING = "troubleshooting"

@dataclass
class EndpointDocumentation:
    """Documentação de um endpoint"""
    path: str
    method: str
    summary: str
    description: str
    tags: List[str]
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    examples: Dict[CodeLanguage, str]
    deprecated: bool = False
    version_added: Optional[str] = None
    version_deprecated: Optional[str] = None

@dataclass
class SchemaDocumentation:
    """Documentação de um schema"""
    name: str
    type: str
    description: str
    properties: Dict[str, Any]
    required: List[str]
    examples: List[Dict[str, Any]]
    version_added: Optional[str] = None

@dataclass
class CodeExample:
    """Exemplo de código"""
    language: CodeLanguage
    title: str
    description: str
    code: str
    endpoint: Optional[str] = None

class AutoDocumentationService:
    """
    Serviço de Documentação Automática
    
    Funcionalidades:
    - Geração automática de OpenAPI spec
    - Code examples em múltiplas linguagens
    - SDKs gerados automaticamente
    - Documentação interativa
    - Versionamento e changelog
    """
    
    def __init__(self):
        # Documentação dos endpoints
        self.endpoints: Dict[str, EndpointDocumentation] = {}
        
        # Schemas documentados
        self.schemas: Dict[str, SchemaDocumentation] = {}
        
        # Code examples
        self.code_examples: Dict[str, List[CodeExample]] = defaultdict(list)
        
        # Configurações
        self.api_info = {
            "title": "TecnoCursos AI API",
            "version": "2.0.0",
            "description": "API completa para upload de arquivos, geração de vídeos com avatar e narração por IA",
            "contact": {
                "name": "TecnoCursos AI Support",
                "email": "support@tecnocursos.ai",
                "url": "https://tecnocursos.ai/support"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            },
            "servers": [
                {
                    "url": "https://api.tecnocursos.ai/v2",
                    "description": "Production server"
                },
                {
                    "url": "https://staging-api.tecnocursos.ai/v2",
                    "description": "Staging server"
                }
            ]
        }
        
        # Cache de documentação gerada
        self.documentation_cache: Dict[str, Any] = {}
        
        # Changelog automático
        self.changelog_entries: List[Dict[str, Any]] = []
        
        # Inicializar documentação padrão
        self._initialize_default_documentation()
        
        logger.info("✅ Auto Documentation Service inicializado")
    
    def _initialize_default_documentation(self):
        """Inicializa documentação padrão dos endpoints"""
        
        # Documentar endpoints principais
        self._document_auth_endpoints()
        self._document_upload_endpoints()
        self._document_avatar_endpoints()
        self._document_admin_endpoints()
        
        # Documentar schemas principais
        self._document_common_schemas()
        
        # Gerar code examples
        self._generate_code_examples()
    
    def _document_auth_endpoints(self):
        """Documenta endpoints de autenticação"""
        
        # Login
        login_endpoint = EndpointDocumentation(
            path="/auth/login",
            method="POST",
            summary="Autenticar usuário",
            description="Autentica um usuário e retorna token JWT para acesso à API",
            tags=["Authentication"],
            parameters=[],
            request_body={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/LoginRequest"}
                    }
                }
            },
            responses={
                "200": {
                    "description": "Login realizado com sucesso",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AuthResponse"}
                        }
                    }
                },
                "401": {
                    "description": "Credenciais inválidas",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            },
            examples={},
            version_added="1.0.0"
        )
        self.endpoints["POST:/auth/login"] = login_endpoint
        
        # Register
        register_endpoint = EndpointDocumentation(
            path="/auth/register",
            method="POST",
            summary="Registrar novo usuário",
            description="Cria uma nova conta de usuário no sistema",
            tags=["Authentication"],
            parameters=[],
            request_body={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/RegisterRequest"}
                    }
                }
            },
            responses={
                "201": {
                    "description": "Usuário criado com sucesso",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UserResponse"}
                        }
                    }
                },
                "400": {
                    "description": "Dados inválidos",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            },
            examples={},
            version_added="1.0.0"
        )
        self.endpoints["POST:/auth/register"] = register_endpoint
    
    def _document_upload_endpoints(self):
        """Documenta endpoints de upload"""
        
        # Upload com narração
        upload_endpoint = EndpointDocumentation(
            path="/upload/with-narration",
            method="POST",
            summary="Upload de arquivo com narração automática",
            description="Faz upload de arquivo PDF ou PPTX e gera narração automática usando IA",
            tags=["Upload", "TTS"],
            parameters=[],
            request_body={
                "required": True,
                "content": {
                    "multipart/form-data": {
                        "schema": {"$ref": "#/components/schemas/UploadWithNarrationRequest"}
                    }
                }
            },
            responses={
                "200": {
                    "description": "Upload realizado com sucesso",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UploadResponse"}
                        }
                    }
                },
                "400": {
                    "description": "Arquivo inválido",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            },
            examples={},
            version_added="1.1.0"
        )
        self.endpoints["POST:/upload/with-narration"] = upload_endpoint
    
    def _document_avatar_endpoints(self):
        """Documenta endpoints de avatar"""
        
        # Gerar vídeo com avatar
        avatar_endpoint = EndpointDocumentation(
            path="/avatar/generate-video",
            method="POST",
            summary="Gerar vídeo com avatar",
            description="Gera vídeo com avatar virtual narrando o conteúdo fornecido",
            tags=["Avatar", "Video Generation"],
            parameters=[],
            request_body={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AvatarVideoRequest"}
                    }
                }
            },
            responses={
                "200": {
                    "description": "Vídeo gerado com sucesso",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/VideoResponse"}
                        }
                    }
                },
                "422": {
                    "description": "Parâmetros inválidos",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            },
            examples={},
            version_added="1.1.0"
        )
        self.endpoints["POST:/avatar/generate-video"] = avatar_endpoint
    
    def _document_admin_endpoints(self):
        """Documenta endpoints administrativos"""
        
        # Analytics
        analytics_endpoint = EndpointDocumentation(
            path="/admin/analytics/dashboard",
            method="GET",
            summary="Dashboard de analytics",
            description="Retorna dados completos do dashboard de analytics em tempo real",
            tags=["Admin", "Analytics"],
            parameters=[
                {
                    "name": "period",
                    "in": "query",
                    "description": "Período dos dados (24h, 7d, 30d)",
                    "required": False,
                    "schema": {"type": "string", "enum": ["24h", "7d", "30d"], "default": "24h"}
                }
            ],
            request_body=None,
            responses={
                "200": {
                    "description": "Dados do dashboard",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AnalyticsDashboard"}
                        }
                    }
                },
                "403": {
                    "description": "Acesso negado",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            },
            examples={},
            version_added="2.0.0"
        )
        self.endpoints["GET:/admin/analytics/dashboard"] = analytics_endpoint
    
    def _document_common_schemas(self):
        """Documenta schemas comuns"""
        
        # Schema de erro
        error_schema = SchemaDocumentation(
            name="ErrorResponse",
            type="object",
            description="Resposta padrão para erros da API",
            properties={
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Código do erro"},
                        "message": {"type": "string", "description": "Mensagem de erro"},
                        "details": {"type": "object", "description": "Detalhes adicionais"}
                    },
                    "required": ["code", "message"]
                },
                "timestamp": {"type": "string", "format": "date-time"},
                "path": {"type": "string", "description": "Caminho da requisição"}
            },
            required=["error", "timestamp"],
            examples=[
                {
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Email ou senha inválidos"
                    },
                    "timestamp": "2024-01-01T00:00:00Z",
                    "path": "/auth/login"
                }
            ],
            version_added="1.0.0"
        )
        self.schemas["ErrorResponse"] = error_schema
        
        # Schema de login
        login_schema = SchemaDocumentation(
            name="LoginRequest",
            type="object",
            description="Dados para autenticação de usuário",
            properties={
                "email": {"type": "string", "format": "email", "description": "Email do usuário"},
                "password": {"type": "string", "minLength": 6, "description": "Senha do usuário"}
            },
            required=["email", "password"],
            examples=[
                {
                    "email": "usuario@exemplo.com",
                    "password": "minhasenha123"
                }
            ],
            version_added="1.0.0"
        )
        self.schemas["LoginRequest"] = login_schema
        
        # Schema de resposta de auth
        auth_response_schema = SchemaDocumentation(
            name="AuthResponse",
            type="object",
            description="Resposta de autenticação bem-sucedida",
            properties={
                "access_token": {"type": "string", "description": "Token JWT de acesso"},
                "token_type": {"type": "string", "example": "Bearer"},
                "expires_in": {"type": "integer", "description": "Tempo de expiração em segundos"},
                "user": {"$ref": "#/components/schemas/User"}
            },
            required=["access_token", "token_type", "expires_in", "user"],
            examples=[
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "user": {
                        "id": 1,
                        "email": "usuario@exemplo.com",
                        "name": "Usuário Exemplo"
                    }
                }
            ],
            version_added="1.0.0"
        )
        self.schemas["AuthResponse"] = auth_response_schema
    
    def _generate_code_examples(self):
        """Gera exemplos de código para diferentes linguagens"""
        
        # Exemplo de login em Python
        python_login = CodeExample(
            language=CodeLanguage.PYTHON,
            title="Login com Python",
            description="Como fazer login usando Python requests",
            code='''
import requests
import json

# Configurar URL da API
api_url = "https://api.tecnocursos.ai/v2"

# Dados de login
login_data = {
    "email": "usuario@exemplo.com",
    "password": "minhasenha123"
}

# Fazer login
response = requests.post(
    f"{api_url}/auth/login",
    json=login_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    auth_data = response.json()
    access_token = auth_data["access_token"]
    print(f"Login realizado! Token: {access_token}")
    
    # Usar token para requisições autenticadas
    headers = {"Authorization": f"Bearer {access_token}"}
    
else:
    print(f"Erro no login: {response.text}")
            '''.strip(),
            endpoint="POST:/auth/login"
        )
        self.code_examples["POST:/auth/login"].append(python_login)
        
        # Exemplo de upload em cURL
        curl_upload = CodeExample(
            language=CodeLanguage.CURL,
            title="Upload com cURL",
            description="Upload de arquivo PDF com narração usando cURL",
            code='''
curl -X POST "https://api.tecnocursos.ai/v2/upload/with-narration" \\
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@documento.pdf" \\
  -F "voice=pt-BR-AntonioNeural" \\
  -F "speed=1.0" \\
  -F "generate_video=true"
            '''.strip(),
            endpoint="POST:/upload/with-narration"
        )
        self.code_examples["POST:/upload/with-narration"].append(curl_upload)
        
        # Exemplo de JavaScript/Node.js
        js_example = CodeExample(
            language=CodeLanguage.JAVASCRIPT,
            title="Upload com JavaScript",
            description="Upload de arquivo usando JavaScript/Node.js",
            code='''
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function uploadFile(filePath, accessToken) {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('voice', 'pt-BR-AntonioNeural');
    formData.append('speed', '1.0');
    formData.append('generate_video', 'true');
    
    try {
        const response = await axios.post(
            'https://api.tecnocursos.ai/v2/upload/with-narration',
            formData,
            {
                headers: {
                    ...formData.getHeaders(),
                    'Authorization': `Bearer ${accessToken}`
                }
            }
        );
        
        console.log('Upload realizado:', response.data);
        return response.data;
        
    } catch (error) {
        console.error('Erro no upload:', error.response?.data || error.message);
        throw error;
    }
}

// Usar a função
uploadFile('./documento.pdf', 'SEU_TOKEN_AQUI')
    .then(result => console.log('Sucesso!', result))
    .catch(error => console.error('Erro:', error));
            '''.strip(),
            endpoint="POST:/upload/with-narration"
        )
        self.code_examples["POST:/upload/with-narration"].append(js_example)
    
    async def generate_openapi_spec(self, version: str = "2.0.0") -> Dict[str, Any]:
        """Gera especificação OpenAPI completa"""
        
        # Cache key
        cache_key = f"openapi_{version}"
        if cache_key in self.documentation_cache:
            return self.documentation_cache[cache_key]
        
        # Base spec
        spec = {
            "openapi": "3.0.3",
            "info": {
                **self.api_info,
                "version": version
            },
            "servers": self.api_info["servers"],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "Token JWT obtido através do endpoint de login"
                    }
                },
                "responses": {
                    "UnauthorizedError": {
                        "description": "Token de acesso inválido ou expirado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}],
            "tags": [
                {"name": "Authentication", "description": "Endpoints de autenticação"},
                {"name": "Upload", "description": "Upload de arquivos"},
                {"name": "TTS", "description": "Text-to-Speech e narração"},
                {"name": "Avatar", "description": "Geração de vídeos com avatar"},
                {"name": "Video Generation", "description": "Processamento de vídeos"},
                {"name": "Admin", "description": "Endpoints administrativos"},
                {"name": "Analytics", "description": "Métricas e analytics"}
            ]
        }
        
        # Adicionar paths
        for endpoint_key, endpoint_doc in self.endpoints.items():
            method, path = endpoint_key.split(":", 1)
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            # Converter para formato OpenAPI
            path_item = {
                "summary": endpoint_doc.summary,
                "description": endpoint_doc.description,
                "tags": endpoint_doc.tags,
                "responses": endpoint_doc.responses
            }
            
            if endpoint_doc.parameters:
                path_item["parameters"] = endpoint_doc.parameters
            
            if endpoint_doc.request_body:
                path_item["requestBody"] = endpoint_doc.request_body
            
            if endpoint_doc.deprecated:
                path_item["deprecated"] = True
            
            # Adicionar exemplos se disponíveis
            if endpoint_key in self.code_examples:
                path_item["x-code-examples"] = [
                    {
                        "lang": example.language.value,
                        "source": example.code,
                        "label": example.title
                    }
                    for example in self.code_examples[endpoint_key]
                ]
            
            spec["paths"][path][method.lower()] = path_item
        
        # Adicionar schemas
        for schema_name, schema_doc in self.schemas.items():
            spec["components"]["schemas"][schema_name] = {
                "type": schema_doc.type,
                "description": schema_doc.description,
                "properties": schema_doc.properties,
                "required": schema_doc.required
            }
            
            if schema_doc.examples:
                spec["components"]["schemas"][schema_name]["examples"] = schema_doc.examples
        
        # Cache resultado
        self.documentation_cache[cache_key] = spec
        
        return spec
    
    async def generate_sdk_code(self, language: CodeLanguage) -> str:
        """Gera código SDK para uma linguagem específica"""
        
        if language == CodeLanguage.PYTHON:
            return await self._generate_python_sdk()
        elif language == CodeLanguage.JAVASCRIPT:
            return await self._generate_javascript_sdk()
        elif language == CodeLanguage.TYPESCRIPT:
            return await self._generate_typescript_sdk()
        else:
            raise ValueError(f"SDK não suportado para linguagem: {language.value}")
    
    async def _generate_python_sdk(self) -> str:
        """Gera SDK Python"""
        
        sdk_code = '''
"""
TecnoCursos AI Python SDK
========================

SDK oficial para integração com a API TecnoCursos AI.
Facilita upload de arquivos, geração de narração e vídeos com avatar.

Instalação:
    pip install tecnocursos-ai

Uso básico:
    from tecnocursos_ai import TecnoCursosClient
    
    client = TecnoCursosClient(api_key="seu_token_aqui")
    result = client.upload_with_narration("documento.pdf")
"""

import requests
import json
from typing import Optional, Dict, Any, IO
from pathlib import Path

class TecnoCursosClient:
    """Cliente principal da API TecnoCursos AI"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.tecnocursos.ai/v2"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "TecnoCursos-Python-SDK/2.0.0"
        })
    
    def upload_with_narration(
        self,
        file_path: str,
        voice: str = "pt-BR-AntonioNeural",
        speed: float = 1.0,
        generate_video: bool = True
    ) -> Dict[str, Any]:
        """
        Faz upload de arquivo com narração automática
        
        Args:
            file_path: Caminho para o arquivo PDF ou PPTX
            voice: Voz para narração (padrão: pt-BR-AntonioNeural)
            speed: Velocidade da narração (0.5 a 2.0)
            generate_video: Se deve gerar vídeo automaticamente
            
        Returns:
            Dict com informações do upload e narração
        """
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {
                'voice': voice,
                'speed': str(speed),
                'generate_video': str(generate_video).lower()
            }
            
            response = self.session.post(
                f"{self.base_url}/upload/with-narration",
                files=files,
                data=data
            )
            
            response.raise_for_status()
            return response.json()
    
    def generate_avatar_video(
        self,
        text: str,
        avatar_style: str = "professional",
        voice: str = "pt-BR-AntonioNeural"
    ) -> Dict[str, Any]:
        """
        Gera vídeo com avatar virtual
        
        Args:
            text: Texto para o avatar narrar
            avatar_style: Estilo do avatar (professional, educational, tech, minimal)
            voice: Voz para narração
            
        Returns:
            Dict com informações do vídeo gerado
        """
        
        data = {
            "text": text,
            "avatar_style": avatar_style,
            "voice": voice
        }
        
        response = self.session.post(
            f"{self.base_url}/avatar/generate-video",
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_analytics_dashboard(self, period: str = "24h") -> Dict[str, Any]:
        """
        Obtém dados do dashboard de analytics
        
        Args:
            period: Período dos dados (24h, 7d, 30d)
            
        Returns:
            Dict com métricas e dados de analytics
        """
        
        params = {"period": period}
        response = self.session.get(
            f"{self.base_url}/admin/analytics/dashboard",
            params=params
        )
        
        response.raise_for_status()
        return response.json()

# Exemplo de uso
if __name__ == "__main__":
    client = TecnoCursosClient(api_key="seu_token_aqui")
    
    # Upload com narração
    result = client.upload_with_narration(
        file_path="documento.pdf",
        voice="pt-BR-FranciscaNeural"
    )
    print("Upload realizado:", result)
    
    # Gerar vídeo com avatar
    video = client.generate_avatar_video(
        text="Bem-vindos ao curso de Python!",
        avatar_style="educational"
    )
    print("Vídeo gerado:", video)
        '''.strip()
        
        return sdk_code
    
    async def _generate_javascript_sdk(self) -> str:
        """Gera SDK JavaScript/Node.js"""
        
        sdk_code = '''
/**
 * TecnoCursos AI JavaScript SDK
 * ============================
 * 
 * SDK oficial para integração com a API TecnoCursos AI.
 * Suporta Node.js e browsers modernos.
 * 
 * Instalação:
 *   npm install tecnocursos-ai
 * 
 * Uso:
 *   const TecnoCursos = require('tecnocursos-ai');
 *   const client = new TecnoCursos.Client('seu_token_aqui');
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class TecnoCursosClient {
    /**
     * Cliente principal da API TecnoCursos AI
     * @param {string} apiKey - Token de acesso da API
     * @param {string} baseUrl - URL base da API
     */
    constructor(apiKey, baseUrl = 'https://api.tecnocursos.ai/v2') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replace(/\\/$/, '');
        
        this.http = axios.create({
            baseURL: this.baseUrl,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'User-Agent': 'TecnoCursos-JS-SDK/2.0.0'
            }
        });
    }
    
    /**
     * Upload de arquivo com narração automática
     * @param {string} filePath - Caminho para o arquivo
     * @param {Object} options - Opções de upload
     * @returns {Promise<Object>} Resultado do upload
     */
    async uploadWithNarration(filePath, options = {}) {
        const {
            voice = 'pt-BR-AntonioNeural',
            speed = 1.0,
            generateVideo = true
        } = options;
        
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));
        formData.append('voice', voice);
        formData.append('speed', speed.toString());
        formData.append('generate_video', generateVideo.toString());
        
        const response = await this.http.post('/upload/with-narration', formData, {
            headers: formData.getHeaders()
        });
        
        return response.data;
    }
    
    /**
     * Gera vídeo com avatar virtual
     * @param {string} text - Texto para narração
     * @param {Object} options - Opções do avatar
     * @returns {Promise<Object>} Informações do vídeo gerado
     */
    async generateAvatarVideo(text, options = {}) {
        const {
            avatarStyle = 'professional',
            voice = 'pt-BR-AntonioNeural'
        } = options;
        
        const data = {
            text,
            avatar_style: avatarStyle,
            voice
        };
        
        const response = await this.http.post('/avatar/generate-video', data);
        return response.data;
    }
    
    /**
     * Obtém dados do dashboard de analytics
     * @param {string} period - Período dos dados (24h, 7d, 30d)
     * @returns {Promise<Object>} Dados de analytics
     */
    async getAnalyticsDashboard(period = '24h') {
        const response = await this.http.get('/admin/analytics/dashboard', {
            params: { period }
        });
        
        return response.data;
    }
}

module.exports = { TecnoCursosClient };

// Exemplo de uso
if (require.main === module) {
    const client = new TecnoCursosClient('seu_token_aqui');
    
    // Upload com narração
    client.uploadWithNarration('./documento.pdf', {
        voice: 'pt-BR-FranciscaNeural'
    }).then(result => {
        console.log('Upload realizado:', result);
    }).catch(error => {
        console.error('Erro:', error.message);
    });
}
        '''.strip()
        
        return sdk_code
    
    def add_endpoint_documentation(
        self,
        path: str,
        method: str,
        summary: str,
        description: str,
        tags: List[str],
        **kwargs
    ):
        """Adiciona documentação de endpoint"""
        
        endpoint_key = f"{method.upper()}:{path}"
        
        endpoint_doc = EndpointDocumentation(
            path=path,
            method=method.upper(),
            summary=summary,
            description=description,
            tags=tags,
            parameters=kwargs.get('parameters', []),
            request_body=kwargs.get('request_body'),
            responses=kwargs.get('responses', {}),
            examples={},
            deprecated=kwargs.get('deprecated', False),
            version_added=kwargs.get('version_added')
        )
        
        self.endpoints[endpoint_key] = endpoint_doc
        
        # Invalidar cache
        self.documentation_cache.clear()
        
        logger.info(f"Documentação adicionada: {endpoint_key}")
    
    def add_code_example(
        self,
        endpoint: str,
        language: CodeLanguage,
        title: str,
        code: str,
        description: str = ""
    ):
        """Adiciona exemplo de código para um endpoint"""
        
        example = CodeExample(
            language=language,
            title=title,
            description=description,
            code=code.strip(),
            endpoint=endpoint
        )
        
        self.code_examples[endpoint].append(example)
        
        # Invalidar cache
        self.documentation_cache.clear()
        
        logger.info(f"Exemplo de código adicionado: {endpoint} ({language.value})")
    
    def get_documentation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da documentação"""
        
        total_examples = sum(len(examples) for examples in self.code_examples.values())
        languages_covered = set()
        for examples in self.code_examples.values():
            languages_covered.update(example.language for example in examples)
        
        return {
            "total_endpoints": len(self.endpoints),
            "total_schemas": len(self.schemas),
            "total_code_examples": total_examples,
            "languages_covered": len(languages_covered),
            "cache_entries": len(self.documentation_cache),
            "api_version": self.api_info["version"]
        }

# === INSTÂNCIA GLOBAL ===
auto_documentation_service = AutoDocumentationService()

logger.info("✅ Auto Documentation Service carregado com sucesso") 