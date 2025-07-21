#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 IMPORTS CENTRALIZADOS - TECNOCURSOS AI
========================================

Módulo que centraliza e padroniza todas as importações do sistema,
garantindo consistência e facilitando o gerenciamento de dependências.

Funcionalidades:
- Imports condicionais com fallbacks
- Verificação de disponibilidade de bibliotecas
- Mensagens de erro padronizadas
- Imports organizados por categoria
- Aliases padronizados

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import sys
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

# === CONFIGURAÇÃO DE LOGGING ===
logger = logging.getLogger(__name__)

# === DICIONÁRIO DE DISPONIBILIDADE ===
DEPENDENCIES_STATUS = {}

# === FUNÇÃO AUXILIAR PARA IMPORTS CONDICIONAIS ===

def safe_import(module_name: str, package_name: str = None, error_msg: str = None):
    """
    Importar módulo de forma segura com tratamento de erro
    
    Args:
        module_name: Nome do módulo a importar
        package_name: Nome do pacote para instalação (se diferente do módulo)
        error_msg: Mensagem de erro personalizada
        
    Returns:
        tuple: (module_object, is_available)
    """
    try:
        if '.' in module_name:
            # Import de submódulo
            parts = module_name.split('.')
            module = __import__(module_name, fromlist=[parts[-1]])
        else:
            module = __import__(module_name)
        
        DEPENDENCIES_STATUS[module_name] = True
        return module, True
        
    except ImportError as e:
        DEPENDENCIES_STATUS[module_name] = False
        
        package_name = package_name or module_name
        default_msg = f"⚠️ {module_name} não disponível - instale: pip install {package_name}"
        logger.warning(error_msg or default_msg)
        
        return None, False

# === IMPORTS BÁSICOS DO SISTEMA ===

# Sistema e Path
import os
import uuid
import time
import json
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable

# === IMPORTS DE WEB FRAMEWORK ===

# FastAPI e dependências
fastapi_module, FASTAPI_AVAILABLE = safe_import(
    'fastapi', 'fastapi', 
    "⚠️ FastAPI não disponível - instale: pip install fastapi uvicorn"
)

if FASTAPI_AVAILABLE:
    from fastapi import (
        FastAPI, APIRouter, HTTPException, Depends, Request, Response,
        BackgroundTasks, File, UploadFile, Form, Query, Body, Header,
        Cookie, Path as FastAPIPath, status
    )
    from fastapi.responses import (
        JSONResponse, HTMLResponse, FileResponse, RedirectResponse
    )
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.templating import Jinja2Templates
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
else:
    # Placeholders para quando FastAPI não estiver disponível
    FastAPI = None
    APIRouter = None
    HTTPException = None

# === IMPORTS DE BANCO DE DADOS ===

sqlalchemy_module, SQLALCHEMY_AVAILABLE = safe_import(
    'sqlalchemy', 'sqlalchemy',
    "⚠️ SQLAlchemy não disponível - instale: pip install sqlalchemy"
)

if SQLALCHEMY_AVAILABLE:
    from sqlalchemy import (
        create_engine, Column, Integer, String, Text, Boolean, DateTime,
        ForeignKey, Table, MetaData, func, and_, or_, desc, asc
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session, relationship
    from sqlalchemy.pool import StaticPool
else:
    # Placeholders
    Column = None
    Integer = None
    String = None

# === IMPORTS DE VALIDAÇÃO ===

pydantic_module, PYDANTIC_AVAILABLE = safe_import(
    'pydantic', 'pydantic',
    "⚠️ Pydantic não disponível - instale: pip install pydantic"
)

if PYDANTIC_AVAILABLE:
    from pydantic import BaseModel, Field, validator, root_validator
else:
    BaseModel = None

# === IMPORTS DE PROCESSAMENTO DE VÍDEO ===

moviepy_module, MOVIEPY_AVAILABLE = safe_import(
    'moviepy.editor', 'moviepy',
    "⚠️ MoviePy não disponível - instale: pip install moviepy"
)

if MOVIEPY_AVAILABLE:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ImageClip, TextClip, ColorClip,
        CompositeVideoClip, concatenate_videoclips, fadein, fadeout, resize
    )
    from moviepy.config import check_moviepy
    from moviepy.video.fx import resize as fx_resize
    from moviepy.audio.fx import audio_fadein, audio_fadeout
else:
    # Placeholders
    VideoFileClip = None
    AudioFileClip = None
    ImageClip = None

# === IMPORTS DE PROCESSAMENTO DE IMAGEM ===

pil_module, PIL_AVAILABLE = safe_import(
    'PIL', 'pillow',
    "⚠️ PIL não disponível - instale: pip install pillow"
)

if PIL_AVAILABLE:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    from PIL.ExifTags import TAGS as EXIF_TAGS
else:
    # Placeholders
    Image = None
    ImageDraw = None

# === IMPORTS CIENTÍFICOS ===

numpy_module, NUMPY_AVAILABLE = safe_import(
    'numpy', 'numpy',
    "⚠️ NumPy não disponível - instale: pip install numpy"
)

if NUMPY_AVAILABLE:
    import numpy as np
else:
    np = None

pandas_module, PANDAS_AVAILABLE = safe_import(
    'pandas', 'pandas',
    "⚠️ Pandas não disponível - instale: pip install pandas"
)

if PANDAS_AVAILABLE:
    import pandas as pd
else:
    pd = None

# === IMPORTS DE PROCESSAMENTO DE DOCUMENTOS ===

# PyPDF2
pypdf2_module, PYPDF2_AVAILABLE = safe_import(
    'PyPDF2', 'PyPDF2',
    "⚠️ PyPDF2 não disponível - instale: pip install PyPDF2"
)

if PYPDF2_AVAILABLE:
    from PyPDF2 import PdfReader, PdfWriter
else:
    PdfReader = None

# Python-PPTX
python_pptx_module, PYTHON_PPTX_AVAILABLE = safe_import(
    'pptx', 'python-pptx',
    "⚠️ python-pptx não disponível - instale: pip install python-pptx"
)

if PYTHON_PPTX_AVAILABLE:
    from pptx import Presentation
    from pptx.util import Inches, Pt
else:
    Presentation = None

# Python-DOCX
python_docx_module, PYTHON_DOCX_AVAILABLE = safe_import(
    'docx', 'python-docx',
    "⚠️ python-docx não disponível - instale: pip install python-docx"
)

if PYTHON_DOCX_AVAILABLE:
    from docx import Document as DocxDocument
else:
    DocxDocument = None

# PyMuPDF (fitz)
fitz_module, FITZ_AVAILABLE = safe_import(
    'fitz', 'pymupdf',
    "⚠️ PyMuPDF não disponível - instale: pip install pymupdf"
)

if FITZ_AVAILABLE:
    import fitz
else:
    fitz = None

# === IMPORTS DE TTS (TEXT-TO-SPEECH) ===

# Google TTS
gtts_module, GTTS_AVAILABLE = safe_import(
    'gtts', 'gtts',
    "⚠️ gTTS não disponível - instale: pip install gtts"
)

if GTTS_AVAILABLE:
    from gtts import gTTS
else:
    gTTS = None

# === IMPORTS DE IA ===

# OpenAI
openai_module, OPENAI_AVAILABLE = safe_import(
    'openai', 'openai',
    "⚠️ OpenAI não disponível - instale: pip install openai"
)

if OPENAI_AVAILABLE:
    import openai
    from openai import AsyncOpenAI
else:
    openai = None
    AsyncOpenAI = None

# Transformers (Hugging Face)
transformers_module, TRANSFORMERS_AVAILABLE = safe_import(
    'transformers', 'transformers',
    "⚠️ Transformers não disponível - instale: pip install transformers"
)

if TRANSFORMERS_AVAILABLE:
    from transformers import pipeline, AutoModel, AutoTokenizer
else:
    pipeline = None

# === IMPORTS DE AUTENTICAÇÃO E SEGURANÇA ===

# PyJWT
jwt_module, JWT_AVAILABLE = safe_import(
    'jwt', 'pyjwt',
    "⚠️ PyJWT não disponível - instale: pip install pyjwt"
)

if JWT_AVAILABLE:
    import jwt
else:
    jwt = None

# Passlib
passlib_module, PASSLIB_AVAILABLE = safe_import(
    'passlib.context', 'passlib',
    "⚠️ Passlib não disponível - instale: pip install passlib"
)

if PASSLIB_AVAILABLE:
    from passlib.context import CryptContext
    from passlib.hash import bcrypt
else:
    CryptContext = None

# Cryptography
cryptography_module, CRYPTOGRAPHY_AVAILABLE = safe_import(
    'cryptography.fernet', 'cryptography',
    "⚠️ Cryptography não disponível - instale: pip install cryptography"
)

if CRYPTOGRAPHY_AVAILABLE:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
else:
    Fernet = None

# === IMPORTS DE CACHE E REDIS ===

redis_module, REDIS_AVAILABLE = safe_import(
    'redis', 'redis',
    "⚠️ Redis não disponível - instale: pip install redis"
)

if REDIS_AVAILABLE:
    import redis
    redis_async_module, REDIS_ASYNC_AVAILABLE = safe_import(
        'redis.asyncio', 'redis[asyncio]',
        "⚠️ Redis async não disponível"
    )
    if REDIS_ASYNC_AVAILABLE:
        import redis.asyncio as redis_async
    else:
        redis_async = None
else:
    redis = None
    redis_async = None

# === IMPORTS DE HTTP ===

# Requests
requests_module, REQUESTS_AVAILABLE = safe_import(
    'requests', 'requests',
    "⚠️ Requests não disponível - instale: pip install requests"
)

if REQUESTS_AVAILABLE:
    import requests
else:
    requests = None

# HTTPX
httpx_module, HTTPX_AVAILABLE = safe_import(
    'httpx', 'httpx',
    "⚠️ HTTPX não disponível - instale: pip install httpx"
)

if HTTPX_AVAILABLE:
    import httpx
else:
    httpx = None

# AioHTTP
aiohttp_module, AIOHTTP_AVAILABLE = safe_import(
    'aiohttp', 'aiohttp',
    "⚠️ AioHTTP não disponível - instale: pip install aiohttp"
)

if AIOHTTP_AVAILABLE:
    import aiohttp
else:
    aiohttp = None

# === IMPORTS DE EMAIL ===

# SendGrid
sendgrid_module, SENDGRID_AVAILABLE = safe_import(
    'sendgrid', 'sendgrid',
    "⚠️ SendGrid não disponível - instale: pip install sendgrid"
)

if SENDGRID_AVAILABLE:
    import sendgrid
    from sendgrid.helpers.mail import Mail
else:
    sendgrid = None

# === IMPORTS DE MONITORAMENTO ===

# PSUtil
psutil_module, PSUTIL_AVAILABLE = safe_import(
    'psutil', 'psutil',
    "⚠️ PSUtil não disponível - instale: pip install psutil"
)

if PSUTIL_AVAILABLE:
    import psutil
else:
    psutil = None

# === IMPORTS DE TESTES ===

pytest_module, PYTEST_AVAILABLE = safe_import(
    'pytest', 'pytest',
    "⚠️ Pytest não disponível - instale: pip install pytest"
)

if PYTEST_AVAILABLE:
    import pytest
else:
    pytest = None

# === DICIONÁRIO DE DISPONIBILIDADE CONSOLIDADO ===

AVAILABLE_MODULES = {
    # Web Framework
    'fastapi': FASTAPI_AVAILABLE,
    
    # Banco de Dados
    'sqlalchemy': SQLALCHEMY_AVAILABLE,
    'pydantic': PYDANTIC_AVAILABLE,
    
    # Processamento de Mídia
    'moviepy': MOVIEPY_AVAILABLE,
    'pil': PIL_AVAILABLE,
    'numpy': NUMPY_AVAILABLE,
    'pandas': PANDAS_AVAILABLE,
    
    # Processamento de Documentos
    'pypdf2': PYPDF2_AVAILABLE,
    'python_pptx': PYTHON_PPTX_AVAILABLE,
    'python_docx': PYTHON_DOCX_AVAILABLE,
    'fitz': FITZ_AVAILABLE,
    
    # TTS e IA
    'gtts': GTTS_AVAILABLE,
    'openai': OPENAI_AVAILABLE,
    'transformers': TRANSFORMERS_AVAILABLE,
    
    # Segurança
    'jwt': JWT_AVAILABLE,
    'passlib': PASSLIB_AVAILABLE,
    'cryptography': CRYPTOGRAPHY_AVAILABLE,
    
    # Cache e HTTP
    'redis': REDIS_AVAILABLE,
    'requests': REQUESTS_AVAILABLE,
    'httpx': HTTPX_AVAILABLE,
    'aiohttp': AIOHTTP_AVAILABLE,
    
    # Email e Monitoramento
    'sendgrid': SENDGRID_AVAILABLE,
    'psutil': PSUTIL_AVAILABLE,
    
    # Testes
    'pytest': PYTEST_AVAILABLE
}

# === FUNÇÕES DE VERIFICAÇÃO ===

def check_dependencies() -> Dict[str, bool]:
    """Verificar status de todas as dependências"""
    return AVAILABLE_MODULES.copy()

def check_required_dependencies(required: List[str]) -> Dict[str, bool]:
    """Verificar dependências obrigatórias"""
    return {dep: AVAILABLE_MODULES.get(dep, False) for dep in required}

def get_missing_dependencies(required: List[str]) -> List[str]:
    """Obter lista de dependências faltantes"""
    return [dep for dep in required if not AVAILABLE_MODULES.get(dep, False)]

def check_video_dependencies() -> bool:
    """Verificar se dependências de vídeo estão disponíveis"""
    return MOVIEPY_AVAILABLE and PIL_AVAILABLE and NUMPY_AVAILABLE

def check_ai_dependencies() -> bool:
    """Verificar se dependências de IA estão disponíveis"""
    return OPENAI_AVAILABLE or TRANSFORMERS_AVAILABLE

def check_database_dependencies() -> bool:
    """Verificar se dependências de banco estão disponíveis"""
    return SQLALCHEMY_AVAILABLE and PYDANTIC_AVAILABLE

def check_web_dependencies() -> bool:
    """Verificar se dependências web estão disponíveis"""
    return FASTAPI_AVAILABLE and PYDANTIC_AVAILABLE

def get_dependency_report() -> str:
    """Gerar relatório de dependências"""
    report = ["📊 RELATÓRIO DE DEPENDÊNCIAS - TECNOCURSOS AI", "=" * 50]
    
    categories = {
        "🌐 Web Framework": ['fastapi'],
        "🗄️ Banco de Dados": ['sqlalchemy', 'pydantic'],
        "🎬 Processamento de Mídia": ['moviepy', 'pil', 'numpy', 'pandas'],
        "📄 Documentos": ['pypdf2', 'python_pptx', 'python_docx', 'fitz'],
        "🤖 IA e TTS": ['gtts', 'openai', 'transformers'],
        "🔐 Segurança": ['jwt', 'passlib', 'cryptography'],
        "🌐 HTTP e Cache": ['redis', 'requests', 'httpx', 'aiohttp'],
        "📧 Email e Monitoramento": ['sendgrid', 'psutil'],
        "🧪 Testes": ['pytest']
    }
    
    for category, deps in categories.items():
        report.append(f"\n{category}:")
        for dep in deps:
            status = "✅" if AVAILABLE_MODULES.get(dep, False) else "❌"
            report.append(f"  {status} {dep}")
    
    # Resumo
    total_deps = len(AVAILABLE_MODULES)
    available_deps = sum(AVAILABLE_MODULES.values())
    report.append(f"\n📈 RESUMO:")
    report.append(f"  Disponíveis: {available_deps}/{total_deps} ({available_deps/total_deps*100:.1f}%)")
    
    return "\n".join(report)

# === ALIASES PADRONIZADOS ===

# Aliases comuns para compatibilidade
FastAPI_Router = APIRouter if FASTAPI_AVAILABLE else None
DB_Session = Session if SQLALCHEMY_AVAILABLE else None
PDF_Reader = PdfReader if PYPDF2_AVAILABLE else None
PPTX_Presentation = Presentation if PYTHON_PPTX_AVAILABLE else None
TTS_Engine = gTTS if GTTS_AVAILABLE else None

# === FUNÇÕES DE CONVENIÊNCIA ===

def require_dependency(dependency: str, error_msg: str = None):
    """
    Decorator para verificar dependência obrigatória
    
    Args:
        dependency: Nome da dependência
        error_msg: Mensagem de erro personalizada
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not AVAILABLE_MODULES.get(dependency, False):
                error = error_msg or f"Dependência {dependency} é obrigatória para esta função"
                raise ImportError(error)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def safe_import_function(module_name: str, function_name: str):
    """
    Importar função específica de forma segura
    
    Args:
        module_name: Nome do módulo
        function_name: Nome da função
        
    Returns:
        function or None
    """
    try:
        module = __import__(module_name, fromlist=[function_name])
        return getattr(module, function_name)
    except (ImportError, AttributeError):
        return None

# === INICIALIZAÇÃO ===

def initialize_imports():
    """Inicializar sistema de imports"""
    logger.info("🔗 Sistema de imports centralizado inicializado")
    
    # Log de dependências críticas faltantes
    critical_deps = ['fastapi', 'sqlalchemy', 'pydantic']
    missing_critical = get_missing_dependencies(critical_deps)
    
    if missing_critical:
        logger.error(f"❌ Dependências críticas faltantes: {missing_critical}")
    
    # Log de dependências opcionais faltantes
    optional_deps = ['moviepy', 'openai', 'redis']
    missing_optional = get_missing_dependencies(optional_deps)
    
    if missing_optional:
        logger.warning(f"⚠️ Dependências opcionais faltantes: {missing_optional}")

# Inicializar automaticamente
initialize_imports()

# === EXPORT ALL ===

__all__ = [
    # Status
    'AVAILABLE_MODULES', 'DEPENDENCIES_STATUS',
    
    # Verificação
    'check_dependencies', 'check_required_dependencies', 'get_missing_dependencies',
    'check_video_dependencies', 'check_ai_dependencies', 'check_database_dependencies',
    'check_web_dependencies', 'get_dependency_report',
    
    # FastAPI
    'FastAPI', 'APIRouter', 'HTTPException', 'Depends', 'Request', 'Response',
    'BackgroundTasks', 'File', 'UploadFile', 'Form', 'Query', 'Body',
    'JSONResponse', 'HTMLResponse', 'FileResponse',
    'CORSMiddleware', 'StaticFiles', 'Jinja2Templates',
    
    # SQLAlchemy
    'create_engine', 'Column', 'Integer', 'String', 'Text', 'Boolean',
    'DateTime', 'ForeignKey', 'declarative_base', 'sessionmaker', 'Session',
    'relationship', 'func', 'and_', 'or_',
    
    # Pydantic
    'BaseModel', 'Field', 'validator',
    
    # MoviePy
    'VideoFileClip', 'AudioFileClip', 'ImageClip', 'TextClip', 'ColorClip',
    'CompositeVideoClip', 'concatenate_videoclips', 'fadein', 'fadeout',
    
    # PIL
    'Image', 'ImageDraw', 'ImageFont', 'ImageFilter',
    
    # Científicos
    'np', 'pd',
    
    # Documentos
    'PdfReader', 'Presentation', 'DocxDocument', 'fitz',
    
    # TTS e IA
    'gTTS', 'openai', 'pipeline',
    
    # Segurança
    'jwt', 'CryptContext', 'Fernet',
    
    # HTTP
    'requests', 'httpx', 'aiohttp',
    
    # Cache
    'redis', 'redis_async',
    
    # Sistema
    'psutil',
    
    # Utilitários
    'require_dependency', 'safe_import_function'
] 