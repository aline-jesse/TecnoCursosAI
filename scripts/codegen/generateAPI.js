#!/usr/bin/env node

/**
 * Gerador de Código para APIs REST
 * TecnoCursos AI - API Code Generation System
 * 
 * Baseado nas melhores práticas de code generation:
 * - Geração determinística de endpoints
 * - Validação automática
 * - Documentação OpenAPI
 * - Testes de integração
 */

const fs = require('fs');
const path = require('path');
const prettier = require('prettier');

/**
 * Configuração do sistema de geração
 */
const CONFIG = {
  apiDir: path.resolve(__dirname, '../../app/routers'),
  outputDir: path.resolve(__dirname, '../../app/routers/generated'),
  prettierConfig: path.resolve(__dirname, '../../.prettierrc')
};

/**
 * Template para router FastAPI
 */
const generateRouter = (entityName, operations = []) => {
  const entityNameLower = entityName.toLowerCase();
  const entityNamePlural = `${entityNameLower}s`;
  
  const imports = [
    'from fastapi import APIRouter, HTTPException, Depends, status',
    'from sqlalchemy.orm import Session',
    'from typing import List, Optional',
    'from pydantic import BaseModel',
    'from datetime import datetime',
    'import logging'
  ];

  const models = `
class ${entityName}Base(BaseModel):
    """Modelo base para ${entityName}"""
    name: str
    description: Optional[str] = None
    is_active: bool = True

class ${entityName}Create(${entityName}Base):
    """Modelo para criação de ${entityName}"""
    pass

class ${entityName}Update(BaseModel):
    """Modelo para atualização de ${entityName}"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ${entityName}Response(${entityName}Base):
    """Modelo de resposta para ${entityName}"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
`;

  const operationsCode = operations.map(op => {
    switch (op.type) {
      case 'list':
        return `
@router.get("/${entityNamePlural}", response_model=List[${entityName}Response])
async def list_${entityNamePlural}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os ${entityNamePlural}"""
    try:
        ${entityNamePlural} = db.query(${entityName}Model).offset(skip).limit(limit).all()
        return ${entityNamePlural}
    except Exception as e:
        logging.error(f"Erro ao listar ${entityNamePlural}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor"
        )`;

      case 'get':
        return `
@router.get("/${entityNamePlural}/{${entityNameLower}_id}", response_model=${entityName}Response)
async def get_${entityNameLower}(
    ${entityNameLower}_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um ${entityNameLower} específico"""
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
            detail=f"Erro interno do servidor"
        )`;

      case 'create':
        return `
@router.post("/${entityNamePlural}", response_model=${entityName}Response, status_code=status.HTTP_201_CREATED)
async def create_${entityNameLower}(
    ${entityNameLower}: ${entityName}Create,
    db: Session = Depends(get_db)
):
    """Cria um novo ${entityNameLower}"""
    try:
        db_${entityNameLower} = ${entityName}Model(**${entityNameLower}.dict())
        db.add(db_${entityNameLower})
        db.commit()
        db.refresh(db_${entityNameLower})
        return db_${entityNameLower}
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao criar ${entityNameLower}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor"
        )`;

      case 'update':
        return `
@router.put("/${entityNamePlural}/{${entityNameLower}_id}", response_model=${entityName}Response)
async def update_${entityNameLower}(
    ${entityNameLower}_id: int,
    ${entityNameLower}_update: ${entityName}Update,
    db: Session = Depends(get_db)
):
    """Atualiza um ${entityNameLower}"""
    try:
        db_${entityNameLower} = db.query(${entityName}Model).filter(${entityName}Model.id == ${entityNameLower}_id).first()
        if not db_${entityNameLower}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="${entityName} não encontrado"
            )
        
        update_data = ${entityNameLower}_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_${entityNameLower}, field, value)
        
        db_${entityNameLower}.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_${entityNameLower})
        return db_${entityNameLower}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao atualizar ${entityNameLower}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor"
        )`;

      case 'delete':
        return `
@router.delete("/${entityNamePlural}/{${entityNameLower}_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_${entityNameLower}(
    ${entityNameLower}_id: int,
    db: Session = Depends(get_db)
):
    """Remove um ${entityNameLower}"""
    try:
        db_${entityNameLower} = db.query(${entityName}Model).filter(${entityName}Model.id == ${entityNameLower}_id).first()
        if not db_${entityNameLower}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="${entityName} não encontrado"
            )
        
        db.delete(db_${entityNameLower})
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao deletar ${entityNameLower}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor"
        )`;

      default:
        return '';
    }
  }).join('\n');

  return `${imports.join('\n')}

from app.database import get_db
from app.models.${entityNameLower} import ${entityName}Model

router = APIRouter(prefix="/api/${entityNamePlural}", tags=["${entityNamePlural}"])

${models}

${operationsCode}
`;
};

/**
 * Template para modelo SQLAlchemy
 */
const generateModel = (entityName) => {
  const entityNameLower = entityName.toLowerCase();
  
  return `from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ${entityName}Model(Base):
    """Modelo SQLAlchemy para ${entityName}"""
    __tablename__ = "${entityNameLower}s"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<${entityName}Model(id={self.id}, name='{self.name}')>"
`;
};

/**
 * Template para testes de API
 */
const generateAPITests = (entityName, operations = []) => {
  const entityNameLower = entityName.toLowerCase();
  const entityNamePlural = `${entityNameLower}s`;
  
  const testCases = operations.map(op => {
    switch (op.type) {
      case 'list':
        return `
    def test_list_${entityNamePlural}(self):
        """Testa listagem de ${entityNamePlural}"""
        response = self.client.get(f"/api/${entityNamePlural}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)`;

      case 'get':
        return `
    def test_get_${entityNameLower}(self):
        """Testa obtenção de ${entityNameLower} específico"""
        # Criar ${entityNameLower} primeiro
        create_data = {"name": "Test ${entityName}", "description": "Test description"}
        create_response = self.client.post(f"/api/${entityNamePlural}", json=create_data)
        self.assertEqual(create_response.status_code, 201)
        
        ${entityNameLower}_id = create_response.json()["id"]
        response = self.client.get(f"/api/${entityNamePlural}/{${entityNameLower}_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Test ${entityName}")`;

      case 'create':
        return `
    def test_create_${entityNameLower}(self):
        """Testa criação de ${entityNameLower}"""
        data = {"name": "New ${entityName}", "description": "New description"}
        response = self.client.post(f"/api/${entityNamePlural}", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "New ${entityName}")`;

      case 'update':
        return `
    def test_update_${entityNameLower}(self):
        """Testa atualização de ${entityNameLower}"""
        # Criar ${entityNameLower} primeiro
        create_data = {"name": "Original ${entityName}"}
        create_response = self.client.post(f"/api/${entityNamePlural}", json=create_data)
        ${entityNameLower}_id = create_response.json()["id"]
        
        update_data = {"name": "Updated ${entityName}"}
        response = self.client.put(f"/api/${entityNamePlural}/{${entityNameLower}_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Updated ${entityName}")`;

      case 'delete':
        return `
    def test_delete_${entityNameLower}(self):
        """Testa remoção de ${entityNameLower}"""
        # Criar ${entityNameLower} primeiro
        create_data = {"name": "To Delete ${entityName}"}
        create_response = self.client.post(f"/api/${entityNamePlural}", json=create_data)
        ${entityNameLower}_id = create_response.json()["id"]
        
        response = self.client.delete(f"/api/${entityNamePlural}/{${entityNameLower}_id}")
        self.assertEqual(response.status_code, 204)`;

      default:
        return '';
    }
  }).join('\n');

  return `import unittest
from fastapi.testclient import TestClient
from app.main import app

class Test${entityName}API(unittest.TestCase):
    """Testes para API de ${entityName}"""
    
    def setUp(self):
        self.client = TestClient(app)
    
    def tearDown(self):
        # Limpar dados de teste se necessário
        pass
${testCases}
    
    def test_api_health(self):
        """Testa saúde da API"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'healthy'})`;
};

/**
 * Gerador de API baseado em configuração
 */
const generateAPI = async (config) => {
  const {
    name,
    operations = ['list', 'get', 'create', 'update', 'delete'],
    description = ''
  } = config;

  const apiDir = path.join(CONFIG.outputDir, name);
  
  // Gerar router
  await createTsFile({
    directory: apiDir,
    fileName: 'router',
    content: generateRouter(name, operations),
    extension: 'py',
    generatedBy: 'scripts/codegen/generateAPI.js'
  });

  // Gerar modelo
  await createTsFile({
    directory: apiDir,
    fileName: 'model',
    content: generateModel(name),
    extension: 'py',
    generatedBy: 'scripts/codegen/generateAPI.js'
  });

  // Gerar testes
  await createTsFile({
    directory: path.join(apiDir, 'tests'),
    fileName: `test_${name.toLowerCase()}`,
    content: generateAPITests(name, operations),
    extension: 'py',
    generatedBy: 'scripts/codegen/generateAPI.js'
  });

  // Gerar README
  const readmeContent = `# API ${name}

${description}

## Endpoints

${operations.map(op => {
  switch (op) {
    case 'list': return '- `GET /api/${name.toLowerCase()}s` - Lista todos os ${name.toLowerCase()}s';
    case 'get': return '- `GET /api/${name.toLowerCase()}s/{id}` - Obtém um ${name.toLowerCase()} específico';
    case 'create': return '- `POST /api/${name.toLowerCase()}s` - Cria um novo ${name.toLowerCase()}`;
    case 'update': return '- `PUT /api/${name.toLowerCase()}s/{id}` - Atualiza um ${name.toLowerCase()}`;
    case 'delete': return '- `DELETE /api/${name.toLowerCase()}s/{id}` - Remove um ${name.toLowerCase()}`;
    default: return '';
  }
}).join('\n')}

## Modelo de Dados

\`\`\`json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "is_active": true,
  "created_at": "2025-07-19T10:00:00Z",
  "updated_at": "2025-07-19T10:00:00Z"
}
\`\`\`

## Testes

Execute os testes com:

\`\`\`bash
python -m pytest tests/test_${name.toLowerCase()}.py -v
\`\`\`

---

*Esta API foi gerada automaticamente pelo sistema de code generation.*`;

  await createTsFile({
    directory: apiDir,
    fileName: 'README',
    content: readmeContent,
    extension: 'md',
    generatedBy: 'scripts/codegen/generateAPI.js'
  });
};

/**
 * Utilitário para criar arquivos Python
 */
const createTsFile = async (params) => {
  const {
    directory,
    fileName,
    content,
    extension = 'py',
    generatedBy
  } = params;

  // Criar diretório se não existir
  fs.mkdirSync(directory, { recursive: true });

  // Formatar código com Prettier (se disponível)
  let formattedContent = content;
  try {
    const config = await prettier.resolveConfig(CONFIG.prettierConfig);
    formattedContent = await prettier.format(
      `# Este arquivo foi gerado automaticamente por ${generatedBy}\n# Não edite manualmente - use o sistema de geração\n\n${content}`,
      {
        ...config,
        parser: 'python'
      }
    );
  } catch (error) {
    // Se prettier não estiver disponível, usar conteúdo original
    formattedContent = `# Este arquivo foi gerado automaticamente por ${generatedBy}\n# Não edite manualmente - use o sistema de geração\n\n${content}`;
  }

  const filePath = `${directory}/${fileName}.${extension}`;
  fs.writeFileSync(filePath, formattedContent);
  
  console.log(`✅ Arquivo gerado: ${filePath}`);
  return filePath;
};

/**
 * Configurações de APIs para gerar
 */
const API_CONFIGS = [
  {
    name: 'Project',
    description: 'API para gerenciamento de projetos',
    operations: ['list', 'get', 'create', 'update', 'delete']
  },
  {
    name: 'Video',
    description: 'API para gerenciamento de vídeos',
    operations: ['list', 'get', 'create', 'update', 'delete']
  },
  {
    name: 'Scene',
    description: 'API para gerenciamento de cenas',
    operations: ['list', 'get', 'create', 'update', 'delete']
  },
  {
    name: 'Asset',
    description: 'API para gerenciamento de assets',
    operations: ['list', 'get', 'create', 'update', 'delete']
  },
  {
    name: 'User',
    description: 'API para gerenciamento de usuários',
    operations: ['list', 'get', 'create', 'update', 'delete']
  }
];

/**
 * Função principal de geração
 */
const main = async () => {
  console.log('🚀 Iniciando geração de APIs...');
  
  try {
    // Criar diretório de saída
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    
    // Gerar cada API
    for (const config of API_CONFIGS) {
      console.log(`📦 Gerando API: ${config.name}`);
      await generateAPI(config);
    }
    
    // Gerar arquivo de índice
    const indexContent = API_CONFIGS.map(config => 
      `from .${config.name.toLowerCase()}.router import router as ${config.name.toLowerCase()}_router`
    ).join('\n');
    
    await createTsFile({
      directory: CONFIG.outputDir,
      fileName: 'index',
      content: indexContent,
      extension: 'py',
      generatedBy: 'scripts/codegen/generateAPI.js'
    });
    
    console.log('✅ Geração de APIs concluída com sucesso!');
    console.log(`📁 APIs geradas em: ${CONFIG.outputDir}`);
    
  } catch (error) {
    console.error('❌ Erro durante a geração:', error);
    process.exit(1);
  }
};

// Executar se chamado diretamente
if (require.main === module) {
  main();
}

module.exports = {
  generateAPI,
  createTsFile,
  CONFIG
}; 