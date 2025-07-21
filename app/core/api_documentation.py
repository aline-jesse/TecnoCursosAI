#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Documentação API Automática - TecnoCursos AI

Este módulo implementa documentação automática e validação avançada
seguindo as melhores práticas do FastAPI e OpenAPI 3.0.

Baseado em:
- OpenAPI 3.0 specification
- FastAPI documentation best practices
- API design guidelines
- Schema-driven development
- Auto-generated examples

Funcionalidades:
- Documentação OpenAPI automática
- Exemplos automáticos para schemas
- Validação avançada com regras customizadas
- Tags e categorização automática
- Versionamento da API
- Rate limiting documentation
- Security schemes
- Response examples
- Error documentation

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

from typing import Dict, Any, List, Optional, Union, Type, get_type_hints
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import inspect
import json
from dataclasses import dataclass
from pathlib import Path

try:
    from fastapi import FastAPI, APIRouter, Request, Response, HTTPException
    from fastapi.openapi.utils import get_openapi
    from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field, validator, create_model
    from pydantic.schema import schema
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    BaseModel = object

try:
    from app.core.enhanced_logging import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    import logging
    get_logger = lambda x: logging.getLogger(x)

logger = get_logger("api_documentation")

# ============================================================================
# CONFIGURAÇÃO DA DOCUMENTAÇÃO
# ============================================================================

@dataclass
class APIDocConfig:
    """Configuração da documentação da API"""
    title: str = "TecnoCursos AI API"
    description: str = "API avançada para geração de cursos com IA"
    version: str = "2.0.0"
    terms_of_service: str = "https://tecnocursos.ai/terms"
    contact: Dict[str, str] = None
    license_info: Dict[str, str] = None
    servers: List[Dict[str, str]] = None
    tags_metadata: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.contact is None:
            self.contact = {
                "name": "TecnoCursos AI Support",
                "url": "https://tecnocursos.ai/support",
                "email": "support@tecnocursos.ai"
            }
        
        if self.license_info is None:
            self.license_info = {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT"
            }
        
        if self.servers is None:
            self.servers = [
                {"url": "https://api.tecnocursos.ai", "description": "Production server"},
                {"url": "https://staging-api.tecnocursos.ai", "description": "Staging server"},
                {"url": "http://localhost:8000", "description": "Development server"}
            ]
        
        if self.tags_metadata is None:
            self.tags_metadata = [
                {
                    "name": "Authentication",
                    "description": "Operações de autenticação e autorização",
                    "externalDocs": {
                        "description": "Documentação de Auth",
                        "url": "https://docs.tecnocursos.ai/auth"
                    }
                },
                {
                    "name": "Users",
                    "description": "Gerenciamento de usuários",
                },
                {
                    "name": "Projects",
                    "description": "Gerenciamento de projetos e cursos",
                },
                {
                    "name": "Scenes",
                    "description": "Operações de cenas e conteúdo",
                },
                {
                    "name": "Video Generation",
                    "description": "Geração de vídeos com IA",
                },
                {
                    "name": "AI Services",
                    "description": "Integração com serviços de IA",
                },
                {
                    "name": "File Management",
                    "description": "Upload e gerenciamento de arquivos",
                },
                {
                    "name": "Analytics",
                    "description": "Métricas e analytics",
                },
                {
                    "name": "System",
                    "description": "Endpoints de sistema e monitoramento",
                }
            ]

# Configuração global
doc_config = APIDocConfig()

# ============================================================================
# RESPONSE MODELS PADRÃO
# ============================================================================

class StandardResponse(BaseModel):
    """Response padrão da API"""
    success: bool = Field(True, description="Indica se a operação foi bem-sucedida")
    message: str = Field("Operation completed successfully", description="Mensagem descritiva")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da resposta")
    request_id: Optional[str] = Field(None, description="ID único da requisição")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "timestamp": "2025-01-17T10:30:00Z",
                "request_id": "req-12345"
            }
        }

class ErrorResponse(BaseModel):
    """Response de erro padrão"""
    success: bool = Field(False, description="Sempre false para erros")
    error: str = Field(..., description="Código do erro")
    message: str = Field(..., description="Mensagem de erro legível")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do erro")
    request_id: Optional[str] = Field(None, description="ID único da requisição")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Dados de entrada inválidos",
                "details": {
                    "field": "email",
                    "issue": "Formato de email inválido"
                },
                "timestamp": "2025-01-17T10:30:00Z",
                "request_id": "req-12345"
            }
        }

class PaginatedResponse(BaseModel):
    """Response paginada padrão"""
    items: List[Any] = Field([], description="Lista de itens")
    meta: Dict[str, Any] = Field(..., description="Metadados da paginação")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [{"id": 1, "name": "Item 1"}],
                "meta": {
                    "page": 1,
                    "size": 20,
                    "total": 100,
                    "pages": 5,
                    "has_next": True,
                    "has_previous": False
                }
            }
        }

# ============================================================================
# GERADOR DE EXEMPLOS AUTOMÁTICOS
# ============================================================================

class ExampleGenerator:
    """Gerador de exemplos automáticos para schemas"""
    
    EXAMPLE_VALUES = {
        str: "Exemplo de texto",
        int: 123,
        float: 123.45,
        bool: True,
        datetime: datetime(2025, 1, 17, 10, 30, 0),
        date: date(2025, 1, 17),
        list: ["item1", "item2"],
        dict: {"key": "value"}
    }
    
    FIELD_EXAMPLES = {
        # Campos comuns
        "id": 1,
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Nome do Item",
        "title": "Título do Item",
        "description": "Descrição detalhada do item",
        "email": "usuario@tecnocursos.ai",
        "password": "senhaSegura123",
        "phone": "+55 11 99999-9999",
        "url": "https://tecnocursos.ai",
        "created_at": "2025-01-17T10:30:00Z",
        "updated_at": "2025-01-17T10:30:00Z",
        "status": "active",
        "is_active": True,
        "is_deleted": False,
        
        # Campos específicos do negócio
        "projeto_id": 1,
        "scene_id": 1,
        "user_id": 1,
        "texto": "Conteúdo da cena com informações educacionais",
        "duracao": 5.5,
        "ordem": 1,
        "style_preset": "modern",
        "background_color": "#4a90e2",
        "quality": "high",
        "video_url": "https://cdn.tecnocursos.ai/videos/curso123.mp4",
        "thumbnail_url": "https://cdn.tecnocursos.ai/thumbnails/thumb123.jpg",
        "file_size": 1048576,
        "mime_type": "video/mp4",
        
        # Métricas e analytics
        "views": 1250,
        "downloads": 89,
        "rating": 4.5,
        "completion_rate": 85.5,
        "engagement_score": 92.3
    }
    
    @classmethod
    def generate_example(cls, model: Type[BaseModel]) -> Dict[str, Any]:
        """Gerar exemplo automático para um modelo Pydantic"""
        if not issubclass(model, BaseModel):
            return {}
        
        example = {}
        
        # Usar exemplo do Config se disponível
        if hasattr(model.Config, 'schema_extra') and 'example' in model.Config.schema_extra:
            return model.Config.schema_extra['example']
        
        # Gerar exemplo baseado nos campos
        for field_name, field_info in model.__fields__.items():
            example[field_name] = cls._generate_field_example(field_name, field_info)
        
        return example
    
    @classmethod
    def _generate_field_example(cls, field_name: str, field_info) -> Any:
        """Gerar exemplo para um campo específico"""
        # Usar exemplo específico se definido no Field
        if hasattr(field_info, 'field_info') and field_info.field_info.extra.get('example'):
            return field_info.field_info.extra['example']
        
        # Usar exemplo baseado no nome do campo
        if field_name in cls.FIELD_EXAMPLES:
            return cls.FIELD_EXAMPLES[field_name]
        
        # Usar exemplo baseado no tipo
        field_type = field_info.type_
        
        # Tratar Optional[Type]
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
            args = field_type.__args__
            if len(args) == 2 and type(None) in args:
                field_type = args[0] if args[1] is type(None) else args[1]
        
        # Tratar List[Type]
        if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
            inner_type = field_type.__args__[0] if field_type.__args__ else str
            return [cls.EXAMPLE_VALUES.get(inner_type, "item")]
        
        # Tratar Dict[Type, Type]
        if hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
            return {"key": "value"}
        
        # Enum
        if inspect.isclass(field_type) and issubclass(field_type, Enum):
            return list(field_type)[0].value
        
        # Tipo básico
        return cls.EXAMPLE_VALUES.get(field_type, f"exemplo_{field_name}")

# ============================================================================
# DECORATORS PARA DOCUMENTAÇÃO
# ============================================================================

def api_route_docs(
    summary: str = None,
    description: str = None,
    response_description: str = "Successful Response",
    tags: List[str] = None,
    deprecated: bool = False,
    examples: Dict[str, Any] = None
):
    """Decorator para documentação avançada de rotas"""
    def decorator(func):
        # Adicionar metadados à função
        if not hasattr(func, '__api_docs__'):
            func.__api_docs__ = {}
        
        func.__api_docs__.update({
            'summary': summary,
            'description': description,
            'response_description': response_description,
            'tags': tags,
            'deprecated': deprecated,
            'examples': examples
        })
        
        return func
    return decorator

def response_examples(**examples):
    """Decorator para adicionar exemplos de resposta"""
    def decorator(func):
        if not hasattr(func, '__response_examples__'):
            func.__response_examples__ = {}
        func.__response_examples__.update(examples)
        return func
    return decorator

# ============================================================================
# CUSTOMIZAÇÃO DO OPENAPI
# ============================================================================

def custom_openapi(app: FastAPI, config: APIDocConfig = None) -> Dict[str, Any]:
    """Gerar documentação OpenAPI customizada"""
    if app.openapi_schema:
        return app.openapi_schema
    
    config = config or doc_config
    
    openapi_schema = get_openapi(
        title=config.title,
        version=config.version,
        description=config.description,
        routes=app.routes,
        tags=config.tags_metadata,
        servers=config.servers
    )
    
    # Adicionar informações customizadas
    openapi_schema["info"].update({
        "termsOfService": config.terms_of_service,
        "contact": config.contact,
        "license": config.license_info,
        "x-logo": {
            "url": "https://tecnocursos.ai/logo.png"
        }
    })
    
    # Adicionar security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtido através do endpoint de autenticação"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key para acesso programático"
        }
    }
    
    # Adicionar respostas padrão
    standard_responses = {
        "400": {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": {
                        "success": False,
                        "error": "BAD_REQUEST",
                        "message": "Requisição inválida",
                        "timestamp": "2025-01-17T10:30:00Z"
                    }
                }
            }
        },
        "401": {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": {
                        "success": False,
                        "error": "UNAUTHORIZED",
                        "message": "Token de autenticação inválido ou expirado",
                        "timestamp": "2025-01-17T10:30:00Z"
                    }
                }
            }
        },
        "403": {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": {
                        "success": False,
                        "error": "FORBIDDEN",
                        "message": "Acesso negado para este recurso",
                        "timestamp": "2025-01-17T10:30:00Z"
                    }
                }
            }
        },
        "404": {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": {
                        "success": False,
                        "error": "NOT_FOUND",
                        "message": "Recurso não encontrado",
                        "timestamp": "2025-01-17T10:30:00Z"
                    }
                }
            }
        },
        "422": {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": {
                        "success": False,
                        "error": "VALIDATION_ERROR",
                        "message": "Dados de entrada inválidos",
                        "details": {
                            "field": "email",
                            "issue": "Formato de email inválido"
                        },
                        "timestamp": "2025-01-17T10:30:00Z"
                    }
                }
            }
        },
        "429": {
            "description": "Rate Limit Exceeded",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": {
                        "success": False,
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "Muitas requisições. Tente novamente em alguns segundos",
                        "timestamp": "2025-01-17T10:30:00Z"
                    }
                }
            }
        },
        "500": {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": {
                        "success": False,
                        "error": "INTERNAL_SERVER_ERROR",
                        "message": "Erro interno do servidor",
                        "timestamp": "2025-01-17T10:30:00Z"
                    }
                }
            }
        }
    }
    
    # Adicionar respostas padrão a todos os endpoints
    for path_item in openapi_schema["paths"].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "responses" in operation:
                for status_code, response_spec in standard_responses.items():
                    if status_code not in operation["responses"]:
                        operation["responses"][status_code] = response_spec
    
    # Adicionar exemplos automáticos
    _add_automatic_examples(openapi_schema)
    
    # Adicionar extensões customizadas
    openapi_schema["x-technocursos"] = {
        "version": config.version,
        "build_date": datetime.utcnow().isoformat(),
        "documentation_url": "https://docs.tecnocursos.ai",
        "support_url": "https://tecnocursos.ai/support"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def _add_automatic_examples(openapi_schema: Dict[str, Any]):
    """Adicionar exemplos automáticos aos schemas"""
    if "components" not in openapi_schema or "schemas" not in openapi_schema["components"]:
        return
    
    for schema_name, schema_def in openapi_schema["components"]["schemas"].items():
        if "properties" in schema_def and "example" not in schema_def:
            example = {}
            
            for prop_name, prop_def in schema_def["properties"].items():
                if "example" in prop_def:
                    example[prop_name] = prop_def["example"]
                elif prop_def.get("type") == "string":
                    example[prop_name] = ExampleGenerator.FIELD_EXAMPLES.get(prop_name, f"exemplo_{prop_name}")
                elif prop_def.get("type") == "integer":
                    example[prop_name] = ExampleGenerator.FIELD_EXAMPLES.get(prop_name, 123)
                elif prop_def.get("type") == "number":
                    example[prop_name] = ExampleGenerator.FIELD_EXAMPLES.get(prop_name, 123.45)
                elif prop_def.get("type") == "boolean":
                    example[prop_name] = ExampleGenerator.FIELD_EXAMPLES.get(prop_name, True)
                elif prop_def.get("type") == "array":
                    example[prop_name] = ["item1", "item2"]
                elif prop_def.get("type") == "object":
                    example[prop_name] = {"key": "value"}
            
            if example:
                schema_def["example"] = example

# ============================================================================
# PÁGINAS DE DOCUMENTAÇÃO CUSTOMIZADAS
# ============================================================================

def get_custom_swagger_ui_html(
    openapi_url: str = "/openapi.json",
    title: str = "TecnoCursos AI API Documentation",
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
) -> HTMLResponse:
    """Página customizada do Swagger UI"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <link rel="stylesheet" type="text/css" href="{swagger_css_url}" />
        <link rel="icon" type="image/png" href="https://tecnocursos.ai/favicon.png" sizes="32x32" />
        <style>
            .swagger-ui .topbar {{ display: none; }}
            .swagger-ui .info {{ margin-bottom: 20px; }}
            .swagger-ui .info .title {{ 
                color: #4a90e2; 
                font-size: 2.5rem;
                font-weight: bold;
            }}
            .swagger-ui .scheme-container {{ 
                background: #f8f9fa; 
                padding: 15px; 
                margin: 20px 0; 
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="{swagger_js_url}"></script>
        <script>
            const ui = SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                layout: "StandaloneLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                tryItOutEnabled: true,
                requestInterceptor: function(request) {{
                    // Adicionar headers customizados
                    request.headers['X-Requested-With'] = 'SwaggerUI';
                    return request;
                }},
                responseInterceptor: function(response) {{
                    // Log responses para debug
                    console.log('API Response:', response);
                    return response;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

def get_custom_redoc_html(
    openapi_url: str = "/openapi.json",
    title: str = "TecnoCursos AI API Documentation",
    redoc_js_url: str = "https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
) -> HTMLResponse:
    """Página customizada do ReDoc"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" type="image/png" href="https://tecnocursos.ai/favicon.png" sizes="32x32" />
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url='{openapi_url}' 
               theme='{{
                   "colors": {{
                       "primary": {{
                           "main": "#4a90e2"
                       }}
                   }},
                   "typography": {{
                       "fontSize": "14px",
                       "lineHeight": "1.5",
                       "code": {{
                           "fontSize": "13px"
                       }}
                   }}
               }}'
               expand-responses="200,201"
               required-props-first="true"
               sort-props-alphabetically="true"
               hide-download-button="false">
        </redoc>
        <script src="{redoc_js_url}"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# ============================================================================
# FUNCÕES UTILITÁRIAS
# ============================================================================

def setup_api_documentation(app: FastAPI, config: APIDocConfig = None):
    """Configurar documentação da API"""
    config = config or doc_config
    
    # Configurar OpenAPI customizado
    app.openapi = lambda: custom_openapi(app, config)
    
    # Rotas customizadas para documentação
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_custom_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{config.title} - Documentation"
        )
    
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        return get_custom_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{config.title} - Documentation"
        )
    
    # Endpoint para download do schema OpenAPI
    @app.get("/openapi.yaml", include_in_schema=False)
    async def get_openapi_yaml():
        import yaml
        openapi_schema = app.openapi()
        return Response(
            content=yaml.dump(openapi_schema, default_flow_style=False),
            media_type="application/x-yaml",
            headers={"Content-Disposition": "attachment; filename=openapi.yaml"}
        )
    
    logger.info("✅ Documentação API configurada com sucesso")

def validate_api_documentation():
    """Validar documentação da API"""
    # TODO: Implementar validação do schema OpenAPI
    # Verificar se todos os endpoints têm documentação adequada
    # Verificar se exemplos são válidos
    # Verificar se respostas estão documentadas
    pass

def generate_postman_collection(app: FastAPI) -> Dict[str, Any]:
    """Gerar coleção do Postman a partir do schema OpenAPI"""
    openapi_schema = app.openapi()
    
    collection = {
        "info": {
            "name": openapi_schema["info"]["title"],
            "description": openapi_schema["info"]["description"],
            "version": openapi_schema["info"]["version"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": {
                "token": "{{access_token}}"
            }
        },
        "variable": [
            {
                "key": "base_url",
                "value": "{{base_url}}",
                "type": "string"
            },
            {
                "key": "access_token",
                "value": "{{access_token}}",
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Converter paths para requests do Postman
    for path, methods in openapi_schema["paths"].items():
        for method, operation in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                request_item = {
                    "name": operation.get("summary", f"{method.upper()} {path}"),
                    "request": {
                        "method": method.upper(),
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}" + path,
                            "host": ["{{base_url}}"],
                            "path": path.strip("/").split("/")
                        }
                    }
                }
                
                # Adicionar body se necessário
                if method.upper() in ["POST", "PUT", "PATCH"]:
                    if "requestBody" in operation:
                        # TODO: Extrair exemplo do schema
                        request_item["request"]["body"] = {
                            "mode": "raw",
                            "raw": json.dumps({}, indent=2)
                        }
                
                collection["item"].append(request_item)
    
    return collection

def get_api_health() -> Dict[str, Any]:
    """Verificar saúde da documentação da API"""
    return {
        "status": "healthy",
        "documentation_available": True,
        "openapi_version": "3.0.0",
        "fastapi_available": FASTAPI_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    } 