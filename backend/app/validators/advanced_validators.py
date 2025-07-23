"""
Sistema Avançado de Validação - TecnoCursos AI
==============================================

Validadores robustos para garantir integridade e segurança dos dados:
- Validação de schemas complexos
- Sanitização automática de dados
- Validação de segurança (XSS, SQL Injection, etc.)
- Validação de tipos de arquivo e conteúdo
- Validação de dados de negócio específicos
- Validação de performance e limites
"""

import re
import hashlib
import mimetypes
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator, ValidationError
import magic
import bleach
from urllib.parse import urlparse

from app.logger import get_logger

logger = get_logger("validators")

class ValidationResult:
    """Resultado de validação"""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None, sanitized_data: Any = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.sanitized_data = sanitized_data

class SecurityValidator:
    """Validador de segurança para prevenir ataques"""
    
    # Padrões de detecção de ataques
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r"(\w*((\%27)|(')|(\-\-)|(\%23)|(#))*(\w)*(\s)*"
        r"((\%6F)|o|(\%4F))((\%72)|r|(\%52))*\w*)",
        r"(\w*((\%27)|(')|(\-\-)|(\%23)|(#))*(\w)*(\s)*"
        r"((\%75)|u|(\%55))((\%6E)|n|(\%4E))((\%69)|i|(\%49))((\%6F)|o|(\%4F))((\%6E)|n|(\%4E))*\w*)",
        r"(\w*((\%27)|(')|(\-\-)|(\%23)|(#))*(\w)*(\s)*"
        r"((\%73)|s|(\%53))((\%65)|e|(\%45))((\%6C)|l|(\%4C))((\%65)|e|(\%45))((\%63)|c|(\%43))((\%74)|t|(\%54))*\w*)",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',
        r'\.\.\\',
        r'%2e%2e%2f',
        r'%2e%2e\\',
        r'..%2f',
        r'..%5c',
    ]
    
    @classmethod
    def check_xss(cls, text: str) -> List[str]:
        """Verificar tentativas de XSS"""
        issues = []
        text_lower = text.lower()
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(f"Possível XSS detectado: padrão '{pattern}'")
        
        return issues
    
    @classmethod
    def check_sql_injection(cls, text: str) -> List[str]:
        """Verificar tentativas de SQL Injection"""
        issues = []
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Possível SQL Injection detectado: padrão suspeito")
        
        return issues
    
    @classmethod
    def check_path_traversal(cls, text: str) -> List[str]:
        """Verificar tentativas de path traversal"""
        issues = []
        
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Possível path traversal detectado: padrão '{pattern}'")
        
        return issues
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitizar HTML removendo tags perigosas"""
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'i', 'b', 
            'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre'
        ]
        
        allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }
        
        return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)

class FileValidator:
    """Validador de arquivos"""
    
    ALLOWED_MIME_TYPES = {
        'pdf': ['application/pdf'],
        'pptx': [
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.ms-powerpoint'
        ],
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        'audio': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg'],
        'video': ['video/mp4', 'video/avi', 'video/mov', 'video/webm']
    }
    
    MAX_FILE_SIZES = {
        'pdf': 50 * 1024 * 1024,      # 50MB
        'pptx': 100 * 1024 * 1024,    # 100MB
        'image': 10 * 1024 * 1024,    # 10MB
        'audio': 200 * 1024 * 1024,   # 200MB
        'video': 1024 * 1024 * 1024,  # 1GB
    }
    
    @classmethod
    def validate_file_type(cls, file_content: bytes, expected_type: str) -> ValidationResult:
        """Validar tipo de arquivo pelo conteúdo (magic numbers)"""
        try:
            # Detectar tipo real do arquivo
            detected_mime = magic.from_buffer(file_content, mime=True)
            
            # Verificar se o tipo detectado está na lista permitida
            allowed_mimes = cls.ALLOWED_MIME_TYPES.get(expected_type, [])
            
            if detected_mime not in allowed_mimes:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Tipo de arquivo inválido. Detectado: {detected_mime}, Esperado: {allowed_mimes}"]
                )
            
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            logger.error(f"❌ Erro na validação de tipo de arquivo: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Erro ao validar tipo de arquivo: {str(e)}"]
            )
    
    @classmethod
    def validate_file_size(cls, file_size: int, file_type: str) -> ValidationResult:
        """Validar tamanho do arquivo"""
        max_size = cls.MAX_FILE_SIZES.get(file_type, 10 * 1024 * 1024)  # 10MB default
        
        if file_size > max_size:
            return ValidationResult(
                is_valid=False,
                errors=[f"Arquivo muito grande. Tamanho: {file_size/1024/1024:.1f}MB, Máximo: {max_size/1024/1024:.1f}MB"]
            )
        
        return ValidationResult(is_valid=True)
    
    @classmethod
    def validate_filename(cls, filename: str) -> ValidationResult:
        """Validar nome do arquivo"""
        errors = []
        warnings = []
        
        # Verificar caracteres perigosos
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/', '\0']
        for char in dangerous_chars:
            if char in filename:
                errors.append(f"Caractere perigoso detectado no nome do arquivo: {char}")
        
        # Verificar nomes reservados (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
            'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
            'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            errors.append(f"Nome de arquivo reservado: {filename}")
        
        # Verificar tamanho do nome
        if len(filename) > 255:
            errors.append("Nome do arquivo muito longo (máximo 255 caracteres)")
        
        # Verificar extensão dupla suspeita
        if filename.count('.') > 1:
            warnings.append("Nome de arquivo com múltiplas extensões pode ser suspeito")
        
        # Sanitizar nome
        sanitized_filename = re.sub(r'[<>:"/|?*\\]', '_', filename)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized_filename
        )

class TextValidator:
    """Validador de texto e conteúdo"""
    
    @classmethod
    def validate_text_content(cls, text: str, max_length: int = 10000) -> ValidationResult:
        """Validar conteúdo de texto"""
        errors = []
        warnings = []
        
        # Verificar tamanho
        if len(text) > max_length:
            errors.append(f"Texto muito longo. Tamanho: {len(text)}, Máximo: {max_length}")
        
        # Verificar segurança
        security_issues = []
        security_issues.extend(SecurityValidator.check_xss(text))
        security_issues.extend(SecurityValidator.check_sql_injection(text))
        
        if security_issues:
            errors.extend(security_issues)
        
        # Verificar encoding
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            errors.append("Texto contém caracteres inválidos")
        
        # Verificar spam/conteúdo suspeito
        spam_indicators = [
            r'(?i)(viagra|cialis|lottery|winner|congratulations)',
            r'(?i)(click here|free money|urgent|act now)',
            r'(?i)(nigerian prince|inheritance|million dollars)'
        ]
        
        for pattern in spam_indicators:
            if re.search(pattern, text):
                warnings.append("Conteúdo pode ser spam ou suspeito")
                break
        
        # Sanitizar
        sanitized_text = SecurityValidator.sanitize_html(text)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized_text
        )
    
    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        """Validar endereço de email"""
        try:
            validated_email = validate_email(email)
            return ValidationResult(
                is_valid=True,
                sanitized_data=validated_email.email
            )
        except EmailNotValidError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Email inválido: {str(e)}"]
            )
    
    @classmethod
    def validate_url(cls, url: str) -> ValidationResult:
        """Validar URL"""
        try:
            parsed = urlparse(url)
            
            errors = []
            
            # Verificar esquema
            if parsed.scheme not in ['http', 'https']:
                errors.append("URL deve usar protocolo HTTP ou HTTPS")
            
            # Verificar se tem domínio
            if not parsed.netloc:
                errors.append("URL deve ter um domínio válido")
            
            # Verificar caracteres suspeitos
            suspicious_chars = ['<', '>', '"', "'", '`']
            for char in suspicious_chars:
                if char in url:
                    errors.append(f"URL contém caractere suspeito: {char}")
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                sanitized_data=url.strip()
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Erro ao validar URL: {str(e)}"]
            )

class BusinessValidator:
    """Validador de regras de negócio específicas"""
    
    @classmethod
    def validate_project_data(cls, project_data: Dict[str, Any]) -> ValidationResult:
        """Validar dados de projeto"""
        errors = []
        warnings = []
        
        # Validar nome do projeto
        name = project_data.get('name', '')
        if not name or len(name.strip()) < 3:
            errors.append("Nome do projeto deve ter pelo menos 3 caracteres")
        
        if len(name) > 100:
            errors.append("Nome do projeto muito longo (máximo 100 caracteres)")
        
        # Validar descrição
        description = project_data.get('description', '')
        if description and len(description) > 1000:
            errors.append("Descrição muito longa (máximo 1000 caracteres)")
        
        # Validar segurança do conteúdo
        content_validation = TextValidator.validate_text_content(f"{name} {description}")
        if not content_validation.is_valid:
            errors.extend(content_validation.errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def validate_upload_data(cls, upload_data: Dict[str, Any]) -> ValidationResult:
        """Validar dados de upload"""
        errors = []
        warnings = []
        
        # Validar nome do arquivo
        filename = upload_data.get('filename', '')
        filename_validation = FileValidator.validate_filename(filename)
        
        if not filename_validation.is_valid:
            errors.extend(filename_validation.errors)
        
        warnings.extend(filename_validation.warnings)
        
        # Validar tamanho se fornecido
        file_size = upload_data.get('size')
        file_type = upload_data.get('type', 'unknown')
        
        if file_size:
            size_validation = FileValidator.validate_file_size(file_size, file_type)
            if not size_validation.is_valid:
                errors.extend(size_validation.errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def validate_tts_request(cls, tts_data: Dict[str, Any]) -> ValidationResult:
        """Validar solicitação de TTS"""
        errors = []
        warnings = []
        
        # Validar texto
        text = tts_data.get('text', '')
        if not text or len(text.strip()) < 1:
            errors.append("Texto é obrigatório para TTS")
        
        if len(text) > 5000:  # Limite para TTS
            errors.append("Texto muito longo para TTS (máximo 5000 caracteres)")
        
        # Validar configurações de voz
        voice_settings = tts_data.get('voice_settings', {})
        speed = voice_settings.get('speed', 1.0)
        
        if not (0.5 <= speed <= 2.0):
            errors.append("Velocidade da voz deve estar entre 0.5 e 2.0")
        
        pitch = voice_settings.get('pitch', 1.0)
        if not (0.5 <= pitch <= 2.0):
            errors.append("Tom da voz deve estar entre 0.5 e 2.0")
        
        # Validar segurança do texto
        content_validation = TextValidator.validate_text_content(text, max_length=5000)
        if not content_validation.is_valid:
            errors.extend(content_validation.errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data={'text': content_validation.sanitized_data} if content_validation.sanitized_data else None
        )

class AdvancedValidatorService:
    """Serviço principal de validação"""
    
    def __init__(self):
        self.validators = {
            'security': SecurityValidator,
            'file': FileValidator,
            'text': TextValidator,
            'business': BusinessValidator
        }
        
        logger.info("✅ Advanced Validator Service inicializado")
    
    def validate_request_data(self, data: Dict[str, Any], validation_rules: List[str]) -> ValidationResult:
        """Validar dados de requisição com múltiplas regras"""
        all_errors = []
        all_warnings = []
        sanitized_data = data.copy()
        
        for rule in validation_rules:
            if rule == "project":
                result = BusinessValidator.validate_project_data(data)
            elif rule == "upload":
                result = BusinessValidator.validate_upload_data(data)
            elif rule == "tts":
                result = BusinessValidator.validate_tts_request(data)
            else:
                continue
            
            if not result.is_valid:
                all_errors.extend(result.errors)
            
            all_warnings.extend(result.warnings)
            
            if result.sanitized_data:
                sanitized_data.update(result.sanitized_data)
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            sanitized_data=sanitized_data
        )
    
    def validate_file_upload(self, file_content: bytes, filename: str, expected_type: str) -> ValidationResult:
        """Validação completa de upload de arquivo"""
        all_errors = []
        all_warnings = []
        
        # Validar nome do arquivo
        name_result = FileValidator.validate_filename(filename)
        if not name_result.is_valid:
            all_errors.extend(name_result.errors)
        all_warnings.extend(name_result.warnings)
        
        # Validar tipo do arquivo
        type_result = FileValidator.validate_file_type(file_content, expected_type)
        if not type_result.is_valid:
            all_errors.extend(type_result.errors)
        
        # Validar tamanho
        size_result = FileValidator.validate_file_size(len(file_content), expected_type)
        if not size_result.is_valid:
            all_errors.extend(size_result.errors)
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            sanitized_data={
                'filename': name_result.sanitized_data,
                'validated_type': expected_type,
                'size': len(file_content)
            }
        )

# Instância global do serviço
validator_service = AdvancedValidatorService()

# Decoradores para validação automática
def validate_input(*validation_rules):
    """Decorador para validação automática de entrada"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extrair dados da request (implementar conforme necessário)
            request_data = kwargs.get('data', {})
            
            # Validar
            result = validator_service.validate_request_data(request_data, validation_rules)
            
            if not result.is_valid:
                raise ValueError(f"Validação falhou: {', '.join(result.errors)}")
            
            # Usar dados sanitizados
            if result.sanitized_data:
                kwargs['data'] = result.sanitized_data
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    print("🛡️ SISTEMA AVANÇADO DE VALIDAÇÃO - TECNOCURSOS AI")
    print("=" * 60)
    
    print("\n🔍 VALIDADORES IMPLEMENTADOS:")
    validators = [
        "SecurityValidator - Detecção de XSS, SQL Injection, Path Traversal",
        "FileValidator - Validação de tipos, tamanhos e nomes de arquivo",
        "TextValidator - Validação de conteúdo, emails, URLs",
        "BusinessValidator - Regras específicas de negócio"
    ]
    
    for i, validator in enumerate(validators, 1):
        print(f"   ✅ {i}. {validator}")
    
    print("\n🎯 RECURSOS:")
    features = [
        "Sanitização automática de dados",
        "Detecção de ataques de segurança",
        "Validação de magic numbers em arquivos",
        "Validação de encoding e caracteres",
        "Regras de negócio personalizáveis",
        "Decoradores para validação automática",
        "Relatórios detalhados de validação",
        "Sistema de warnings e erros"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"   🚀 {i}. {feature}")
    
    print("\n✨ SISTEMA DE VALIDAÇÃO IMPLEMENTADO!") 