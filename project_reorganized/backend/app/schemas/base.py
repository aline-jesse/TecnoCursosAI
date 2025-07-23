"""
Schemas básicos do TecnoCursos AI
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Schema base para herança"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthCheck(BaseSchema):
    """Schema para health check"""
    status: str = Field(..., description="Status da aplicação")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="Versão da aplicação")
    uptime_seconds: float = Field(..., description="Tempo de funcionamento em segundos")
    database_status: str = Field(..., description="Status do banco de dados")
    services_status: Optional[Dict[str, str]] = Field(None, description="Status dos serviços")


class SystemStatus(BaseSchema):
    """Schema para status detalhado do sistema"""
    total_users: int = Field(0, description="Total de usuários")
    total_projects: int = Field(0, description="Total de projetos")
    total_files: int = Field(0, description="Total de arquivos")
    system_load: float = Field(0.0, description="Carga do sistema")
    memory_usage: float = Field(0.0, description="Uso de memória (%)")
    disk_usage: float = Field(0.0, description="Uso de disco (%)")
    timestamp: datetime = Field(default_factory=datetime.now)


class ApiResponse(BaseSchema):
    """Schema padrão para respostas da API"""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem de resposta")
    data: Optional[Any] = Field(None, description="Dados da resposta")
    errors: Optional[List[str]] = Field(None, description="Lista de erros")
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseSchema):
    """Schema para respostas de erro"""
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes do erro")
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginationParams(BaseSchema):
    """Parâmetros de paginação"""
    page: int = Field(1, ge=1, description="Número da página")
    size: int = Field(10, ge=1, le=100, description="Tamanho da página")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseSchema):
    """Resposta paginada"""
    items: List[Any] = Field(..., description="Itens da página")
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")
    
    @classmethod
    def create(cls, items: List[Any], total: int, page: int, size: int):
        """Criar resposta paginada"""
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        ) 