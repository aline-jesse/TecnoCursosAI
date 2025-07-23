/**
 * Template Base para APIs FastAPI
 * TecnoCursos AI - API Template
 */

const routerTemplate = (entityName, operations = []) => {
  const entityNameLower = entityName.toLowerCase();
  const entityNamePlural = `${entityNameLower}s`;

  const imports = [
    'from fastapi import APIRouter, HTTPException, Depends, status, Query',
    'from sqlalchemy.orm import Session',
    'from typing import List, Optional, Dict, Any',
    'from pydantic import BaseModel, Field',
    'from datetime import datetime',
    'import logging',
    'from app.database import get_db',
    'from app.models.${entityNameLower} import ${entityName}Model',
    'from app.schemas.${entityNameLower} import ${entityName}Create, ${entityName}Update, ${entityName}Response',
  ];

  const operationsCode = operations
    .map(op => {
      switch (op.type) {
        case 'list':
          return `
@router.get("/${entityNamePlural}", response_model=List[${entityName}Response])
async def list_${entityNamePlural}(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Termo de busca"),
    sort_by: Optional[str] = Query("created_at", description="Campo para ordenação"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Ordem de classificação"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os ${entityNamePlural} com paginação e filtros
    """
    try:
        query = db.query(${entityName}Model)
        
        # Aplicar filtro de busca
        if search:
            query = query.filter(${entityName}Model.name.ilike(f"%{search}%"))
        
        # Aplicar ordenação
        if hasattr(${entityName}Model, sort_by):
            order_column = getattr(${entityName}Model, sort_by)
            if sort_order == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        # Aplicar paginação
        ${entityNamePlural} = query.offset(skip).limit(limit).all()
        
        return ${entityNamePlural}
    except Exception as e:
        logging.error(f"Erro ao listar ${entityNamePlural}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )`;

        case 'get':
          return `
@router.get("/${entityNamePlural}/{${entityNameLower}_id}", response_model=${entityName}Response)
async def get_${entityNameLower}(
    ${entityNameLower}_id: int = Field(..., description="ID do ${entityNameLower}"),
    db: Session = Depends(get_db)
):
    """
    Obtém um ${entityNameLower} específico por ID
    """
    try:
        ${entityNameLower} = db.query(${entityName}Model).filter(${entityName}Model.id == ${entityNameLower}_id).first()
        if not ${entityNameLower}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="${entityName} não encontrado"
            )
        return ${entityNameLower}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro ao obter ${entityNameLower}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )`;

        case 'create':
          return `
@router.post("/${entityNamePlural}", response_model=${entityName}Response, status_code=status.HTTP_201_CREATED)
async def create_${entityNameLower}(
    ${entityNameLower}: ${entityName}Create,
    db: Session = Depends(get_db)
):
    """
    Cria um novo ${entityNameLower}
    """
    try:
        # Verificar se já existe um ${entityNameLower} com o mesmo nome
        existing_${entityNameLower} = db.query(${entityName}Model).filter(
            ${entityName}Model.name == ${entityNameLower}.name
        ).first()
        
        if existing_${entityNameLower}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um ${entityNameLower} com este nome"
            )
        
        db_${entityNameLower} = ${entityName}Model(**${entityNameLower}.dict())
        db.add(db_${entityNameLower})
        db.commit()
        db.refresh(db_${entityNameLower})
        
        logging.info(f"${entityNameLower} criado com ID: {db_${entityNameLower}.id}")
        return db_${entityNameLower}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao criar ${entityNameLower}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )`;

        case 'update':
          return `
@router.put("/${entityNamePlural}/{${entityNameLower}_id}", response_model=${entityName}Response)
async def update_${entityNameLower}(
    ${entityNameLower}_id: int = Field(..., description="ID do ${entityNameLower}"),
    ${entityNameLower}_update: ${entityName}Update,
    db: Session = Depends(get_db)
):
    """
    Atualiza um ${entityNameLower} existente
    """
    try:
        db_${entityNameLower} = db.query(${entityName}Model).filter(${entityName}Model.id == ${entityNameLower}_id).first()
        if not db_${entityNameLower}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="${entityName} não encontrado"
            )
        
        # Verificar se o novo nome já existe (se estiver sendo atualizado)
        if ${entityNameLower}_update.name and ${entityNameLower}_update.name != db_${entityNameLower}.name:
            existing_${entityNameLower} = db.query(${entityName}Model).filter(
                ${entityName}Model.name == ${entityNameLower}_update.name,
                ${entityName}Model.id != ${entityNameLower}_id
            ).first()
            
            if existing_${entityNameLower}:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um ${entityNameLower} com este nome"
                )
        
        # Atualizar campos
        update_data = ${entityNameLower}_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_${entityNameLower}, field, value)
        
        db_${entityNameLower}.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_${entityNameLower})
        
        logging.info(f"${entityNameLower} atualizado com ID: {db_${entityNameLower}.id}")
        return db_${entityNameLower}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao atualizar ${entityNameLower}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )`;

        case 'delete':
          return `
@router.delete("/${entityNamePlural}/{${entityNameLower}_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_${entityNameLower}(
    ${entityNameLower}_id: int = Field(..., description="ID do ${entityNameLower}"),
    db: Session = Depends(get_db)
):
    """
    Remove um ${entityNameLower} por ID
    """
    try:
        db_${entityNameLower} = db.query(${entityName}Model).filter(${entityName}Model.id == ${entityNameLower}_id).first()
        if not db_${entityNameLower}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="${entityName} não encontrado"
            )
        
        db.delete(db_${entityNameLower})
        db.commit()
        
        logging.info(f"${entityNameLower} removido com ID: {${entityNameLower}_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao deletar ${entityNameLower}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )`;

        default:
          return '';
      }
    })
    .join('\n');

  return `${imports.join('\n')}

router = APIRouter(prefix="/api/${entityNamePlural}", tags=["${entityNamePlural}"])

${operationsCode}

# Endpoint de saúde específico da API
@router.get("/health")
async def ${entityNameLower}_health():
    """
    Verifica a saúde da API de ${entityNamePlural}
    """
    return {
        "status": "healthy",
        "service": "${entityName} API",
        "timestamp": datetime.utcnow().isoformat()
    }`;
};

const schemaTemplate = (entityName, fields = []) => {
  const entityNameLower = entityName.toLowerCase();

  const fieldsCode = fields
    .map(field => {
      switch (field.type) {
        case 'string':
          return `    ${field.name}: str = Field(..., description="${field.description || 'Campo de texto'}")`;
        case 'text':
          return `    ${field.name}: Optional[str] = Field(None, description="${field.description || 'Campo de texto longo'}")`;
        case 'integer':
          return `    ${field.name}: int = Field(..., description="${field.description || 'Campo numérico'}")`;
        case 'float':
          return `    ${field.name}: float = Field(..., description="${field.description || 'Campo decimal'}")`;
        case 'boolean':
          return `    ${field.name}: bool = Field(${field.default || false}, description="${field.description || 'Campo booleano'}")`;
        case 'datetime':
          return `    ${field.name}: Optional[datetime] = Field(None, description="${field.description || 'Data e hora'}")`;
        case 'foreign_key':
          return `    ${field.name}_id: int = Field(..., description="${field.description || 'ID de referência'}")`;
        default:
          return `    ${field.name}: str = Field(..., description="${field.description || 'Campo de texto'}")`;
      }
    })
    .join('\n');

  return `from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ${entityName}Base(BaseModel):
    """Modelo base para ${entityName}"""
${fieldsCode}

class ${entityName}Create(${entityName}Base):
    """Modelo para criação de ${entityName}"""
    pass

class ${entityName}Update(BaseModel):
    """Modelo para atualização de ${entityName}"""
${fields
  .map(field => {
    const fieldType =
      field.type === 'string'
        ? 'str'
        : field.type === 'integer'
          ? 'int'
          : field.type === 'float'
            ? 'float'
            : field.type === 'boolean'
              ? 'bool'
              : field.type === 'datetime'
                ? 'datetime'
                : 'str';
    return `    ${field.name}: Optional[${fieldType}] = Field(None, description="${field.description || 'Campo opcional'}")`;
  })
  .join('\n')}

class ${entityName}Response(${entityName}Base):
    """Modelo de resposta para ${entityName}"""
    id: int = Field(..., description="ID único")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }`;
};

const modelTemplate = (entityName, fields = []) => {
  const entityNameLower = entityName.toLowerCase();

  const fieldsCode = fields
    .map(field => {
      switch (field.type) {
        case 'string':
          return `    ${field.name} = Column(String(${field.length || 255}), nullable=${field.nullable !== false}, index=${field.index || false})`;
        case 'text':
          return `    ${field.name} = Column(Text, nullable=${field.nullable !== false})`;
        case 'integer':
          return `    ${field.name} = Column(Integer, nullable=${field.nullable !== false}, index=${field.index || false})`;
        case 'float':
          return `    ${field.name} = Column(Float, nullable=${field.nullable !== false})`;
        case 'boolean':
          return `    ${field.name} = Column(Boolean, default=${field.default || false}, nullable=${field.nullable !== false})`;
        case 'datetime':
          return `    ${field.name} = Column(DateTime, default=datetime.utcnow, nullable=${field.nullable !== false})`;
        case 'foreign_key':
          return `    ${field.name}_id = Column(Integer, ForeignKey('${field.reference_table}.id'), nullable=${field.nullable !== false})`;
        default:
          return `    ${field.name} = Column(String(255), nullable=${field.nullable !== false})`;
      }
    })
    .join('\n');

  const relationships = fields
    .filter(field => field.type === 'foreign_key')
    .map(
      field =>
        `    ${field.name} = relationship("${field.reference_model}", back_populates="${entityNameLower}s")`
    )
    .join('\n');

  return `from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ${entityName}Model(Base):
    """Modelo SQLAlchemy para ${entityName}"""
    __tablename__ = "${entityNameLower}s"
    
    id = Column(Integer, primary_key=True, index=True)
${fieldsCode}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
${relationships}
    
    # Índices para performance
    __table_args__ = (
        Index('ix_${entityNameLower}s_name', 'name'),
        Index('ix_${entityNameLower}s_created_at', 'created_at'),
        Index('ix_${entityNameLower}s_updated_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<${entityName}Model(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
${fields.map(field => `            '${field.name}': self.${field.name},`).join('\n')}
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }`;
};

module.exports = {
  routerTemplate,
  schemaTemplate,
  modelTemplate,
};
