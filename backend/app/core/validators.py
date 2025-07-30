"""
Sistema de Validação Robusta - TecnoCursos AI
Validadores customizados com Pydantic e sanitização de dados
"""

import re
import bleach
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, validator, Field, root_validator
from pydantic.validators import str_validator
from email_validator import validate_email, EmailNotValidError
import magic
from pathlib import Path

class ValidationError(Exception):
    """Erro customizado de validação"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)

class SanitizedStr(str):
    """String sanitizada automaticamente"""
    
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        # Sanitização básica
        sanitized = bleach.clean(
            v,
            tags=[],  # Remover todas as tags HTML
            attributes={},
            protocols=[],
            strip=True
        )
        
        # Remover caracteres de controle
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)
        
        # Normalizar espaços
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return cls(sanitized)

class StrongPassword(str):
    """Validador para senhas fortes"""
    
    min_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special: bool = True
    
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        errors = []
        
        # Comprimento mínimo
        if len(v) < cls.min_length:
            errors.append(f"Senha deve ter pelo menos {cls.min_length} caracteres")
        
        # Letra maiúscula
        if cls.require_uppercase and not re.search(r'[A-Z]', v):
            errors.append("Senha deve conter pelo menos uma letra maiúscula")
        
        # Letra minúscula
        if cls.require_lowercase and not re.search(r'[a-z]', v):
            errors.append("Senha deve conter pelo menos uma letra minúscula")
        
        # Números
        if cls.require_numbers and not re.search(r'[0-9]', v):
            errors.append("Senha deve conter pelo menos um número")
        
        # Caracteres especiais
        if cls.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append("Senha deve conter pelo menos um caractere especial")
        
        # Padrões comuns fracos
        weak_patterns = [
            r'123456', r'password', r'qwerty', r'abc123',
            r'admin', r'letmein', r'welcome', r'monkey'
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, v.lower()):
                errors.append("Senha contém padrões muito comuns")
                break
        
        if errors:
            raise ValidationError("; ".join(errors), "password", "WEAK_PASSWORD")
        
        return cls(v)

class SafeFilename(str):
    """Validador para nomes de arquivo seguros"""
    
    max_length: int = 255
    allowed_extensions: List[str] = [
        '.pdf', '.doc', '.docx', '.txt', '.md',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        '.mp4', '.avi', '.mov', '.mkv',
        '.mp3', '.wav', '.ogg', '.flac'
    ]
    
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        original = v
        
        # Remover caracteres perigosos
        v = re.sub(r'[^\w\s\-_\.]', '', v)
        
        # Normalizar espaços
        v = re.sub(r'\s+', '_', v)
        
        # Remover pontos duplos (path traversal)
        v = re.sub(r'\.\.+', '.', v)
        
        # Verificar comprimento
        if len(v) > cls.max_length:
            raise ValidationError(
                f"Nome do arquivo muito longo (máximo {cls.max_length} caracteres)",
                "filename",
                "FILENAME_TOO_LONG"
            )
        
        # Verificar extensão
        if cls.allowed_extensions:
            extension = Path(v).suffix.lower()
            if extension and extension not in cls.allowed_extensions:
                raise ValidationError(
                    f"Extensão de arquivo não permitida: {extension}",
                    "filename",
                    "INVALID_EXTENSION"
                )
        
        # Verificar nomes reservados (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = Path(v).stem.upper()
        if name_without_ext in reserved_names:
            raise ValidationError(
                f"Nome de arquivo reservado: {name_without_ext}",
                "filename",
                "RESERVED_FILENAME"
            )
        
        return cls(v)

class ValidatedEmail(str):
    """Email validado e normalizado"""
    
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        try:
            # Validar email
            valid = validate_email(v)
            # Retornar email normalizado
            return cls(valid.email)
        
        except EmailNotValidError as e:
            raise ValidationError(
                f"Email inválido: {str(e)}",
                "email",
                "INVALID_EMAIL"
            )

class PhoneNumber(str):
    """Validador para números de telefone brasileiros"""
    
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        # Remover formatação
        clean = re.sub(r'[^\d]', '', v)
        
        # Validar formato brasileiro
        if len(clean) == 11 and clean.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24', '27', '28')):
            # Celular: (XX) 9XXXX-XXXX
            if clean[2] == '9':
                formatted = f"({clean[:2]}) {clean[2]}{clean[3:7]}-{clean[7:]}"
                return cls(formatted)
        
        elif len(clean) == 10 and clean.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24', '27', '28')):
            # Fixo: (XX) XXXX-XXXX
            formatted = f"({clean[:2]}) {clean[2:6]}-{clean[6:]}"
            return cls(formatted)
        
        raise ValidationError(
            "Número de telefone inválido. Use formato: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX",
            "phone",
            "INVALID_PHONE"
        )

class CPF(str):
    """Validador para CPF brasileiro"""
    
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        # Remover formatação
        cpf = re.sub(r'[^\d]', '', v)
        
        # Verificar se tem 11 dígitos
        if len(cpf) != 11:
            raise ValidationError("CPF deve ter 11 dígitos", "cpf", "INVALID_CPF")
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            raise ValidationError("CPF inválido", "cpf", "INVALID_CPF")
        
        # Calcular dígitos verificadores
        def calculate_digit(cpf_digits, weights):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # Primeiro dígito
        first_digit = calculate_digit(cpf[:9], range(10, 1, -1))
        if first_digit != int(cpf[9]):
            raise ValidationError("CPF inválido", "cpf", "INVALID_CPF")
        
        # Segundo dígito
        second_digit = calculate_digit(cpf[:10], range(11, 1, -1))
        if second_digit != int(cpf[10]):
            raise ValidationError("CPF inválido", "cpf", "INVALID_CPF")
        
        # Formatar CPF
        formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cls(formatted)

class FileValidator:
    """Validador para arquivos enviados"""
    
    def __init__(
        self,
        max_size: int = 100 * 1024 * 1024,  # 100MB
        allowed_types: List[str] = None,
        allowed_extensions: List[str] = None,
        scan_content: bool = True
    ):
        self.max_size = max_size
        self.allowed_types = allowed_types or [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png',
            'video/mp4',
            'audio/mpeg'
        ]
        self.allowed_extensions = allowed_extensions or [
            '.pdf', '.doc', '.docx', '.txt',
            '.jpg', '.jpeg', '.png',
            '.mp4', '.avi', '.mp3', '.wav'
        ]
        self.scan_content = scan_content
    
    def validate_file(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Valida arquivo enviado"""
        errors = []
        file_info = {
            'valid': True,
            'size': 0,
            'mime_type': None,
            'extension': None,
            'safe_filename': None,
            'errors': errors
        }
        
        try:
            # Verificar se arquivo existe
            path = Path(file_path)
            if not path.exists():
                errors.append("Arquivo não encontrado")
                file_info['valid'] = False
                return file_info
            
            # Tamanho do arquivo
            file_size = path.stat().st_size
            file_info['size'] = file_size
            
            if file_size > self.max_size:
                errors.append(f"Arquivo muito grande. Máximo: {self.max_size // (1024*1024)}MB")
                file_info['valid'] = False
            
            # Tipo MIME real do arquivo
            if self.scan_content:
                mime_type = magic.from_file(file_path, mime=True)
                file_info['mime_type'] = mime_type
                
                if mime_type not in self.allowed_types:
                    errors.append(f"Tipo de arquivo não permitido: {mime_type}")
                    file_info['valid'] = False
            
            # Extensão do arquivo
            extension = path.suffix.lower()
            file_info['extension'] = extension
            
            if extension not in self.allowed_extensions:
                errors.append(f"Extensão não permitida: {extension}")
                file_info['valid'] = False
            
            # Validar nome do arquivo
            try:
                safe_filename = SafeFilename.validate(original_filename)
                file_info['safe_filename'] = safe_filename
            except ValidationError as e:
                errors.append(f"Nome do arquivo inválido: {e.message}")
                file_info['valid'] = False
            
            # Verificações de segurança específicas
            self._security_checks(file_path, file_info)
            
        except Exception as e:
            errors.append(f"Erro ao validar arquivo: {str(e)}")
            file_info['valid'] = False
        
        return file_info
    
    def _security_checks(self, file_path: str, file_info: Dict[str, Any]):
        """Verificações de segurança específicas"""
        
        # Verificar assinatura de arquivo
        with open(file_path, 'rb') as f:
            header = f.read(512)  # Primeiros 512 bytes
        
        # Verificar se é realmente um arquivo do tipo declarado
        file_signatures = {
            'application/pdf': [b'%PDF'],
            'image/jpeg': [b'\xff\xd8\xff'],
            'image/png': [b'\x89PNG\r\n\x1a\n'],
            'application/zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08']
        }
        
        mime_type = file_info.get('mime_type')
        if mime_type in file_signatures:
            valid_signature = any(
                header.startswith(sig) 
                for sig in file_signatures[mime_type]
            )
            
            if not valid_signature:
                file_info['errors'].append(
                    f"Assinatura de arquivo inválida para {mime_type}"
                )
                file_info['valid'] = False

class BaseValidator(BaseModel):
    """Classe base para validadores com funcionalidades comuns"""
    
    class Config:
        # Configurações globais
        validate_assignment = True
        use_enum_values = True
        allow_population_by_field_name = True
        
        # Campos personalizados
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    
    @root_validator(pre=True)
    def sanitize_strings(cls, values):
        """Sanitiza automaticamente todos os campos string"""
        if isinstance(values, dict):
            for key, value in values.items():
                if isinstance(value, str) and len(value.strip()) > 0:
                    # Sanitização básica para prevenir XSS
                    values[key] = bleach.clean(
                        value.strip(),
                        tags=[],
                        attributes={},
                        strip=True
                    )
        return values
    
    def validate_and_sanitize(self) -> Dict[str, Any]:
        """Retorna dados validados e sanitizados"""
        return self.dict(exclude_unset=True)

# Validadores específicos para o domínio
class UserValidator(BaseValidator):
    """Validador para dados de usuário"""
    
    username: SanitizedStr = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_-]+$')
    email: ValidatedEmail = Field(...)
    full_name: SanitizedStr = Field(..., min_length=2, max_length=100)
    password: Optional[StrongPassword] = None
    phone: Optional[PhoneNumber] = None
    cpf: Optional[CPF] = None
    bio: Optional[SanitizedStr] = Field(None, max_length=500)
    
    @validator('username')
    def validate_username(cls, v):
        # Verificar se não é um nome reservado
        reserved = ['admin', 'root', 'api', 'www', 'mail', 'support']
        if v.lower() in reserved:
            raise ValidationError("Nome de usuário reservado", "username", "RESERVED_USERNAME")
        return v

class ProjectValidator(BaseValidator):
    """Validador para dados de projeto"""
    
    name: SanitizedStr = Field(..., min_length=3, max_length=100)
    description: Optional[SanitizedStr] = Field(None, max_length=1000)
    category: Optional[SanitizedStr] = Field(None, max_length=50)
    tags: Optional[List[SanitizedStr]] = Field(None, max_items=10)
    difficulty_level: Optional[str] = Field('beginner', regex=r'^(beginner|intermediate|advanced)$')
    estimated_duration: Optional[int] = Field(None, ge=1, le=10080)  # 1 min a 1 semana
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Limitar tamanho de cada tag
            for tag in v:
                if len(tag) > 30:
                    raise ValidationError("Tag muito longa (máximo 30 caracteres)", "tags", "TAG_TOO_LONG")
        return v

# Função utilitária para validação customizada
def validate_data(data: Dict[str, Any], validator_class: type) -> Dict[str, Any]:
    """Valida dados usando um validador específico"""
    try:
        validated = validator_class(**data)
        return {
            'valid': True,
            'data': validated.validate_and_sanitize(),
            'errors': []
        }
    except ValidationError as e:
        return {
            'valid': False,
            'data': None,
            'errors': [{'field': e.field, 'message': e.message, 'code': e.code}]
        }
    except Exception as e:
        return {
            'valid': False,
            'data': None,
            'errors': [{'field': None, 'message': str(e), 'code': 'VALIDATION_ERROR'}]
        }

# Instance global do validador de arquivos
file_validator = FileValidator()
