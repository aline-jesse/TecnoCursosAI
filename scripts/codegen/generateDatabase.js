#!/usr/bin/env node

/**
 * Gerador de Código para Modelos de Banco de Dados
 * TecnoCursos AI - Database Code Generation System
 *
 * Baseado nas melhores práticas de code generation:
 * - Geração determinística de modelos
 * - Migrações automáticas
 * - Relacionamentos configuráveis
 * - Validações automáticas
 */

const fs = require('fs');
const path = require('path');
const prettier = require('prettier');

/**
 * Configuração do sistema de geração
 */
const CONFIG = {
  modelsDir: path.resolve(__dirname, '../../app/models'),
  migrationsDir: path.resolve(__dirname, '../../alembic/versions'),
  outputDir: path.resolve(__dirname, '../../app/models/generated'),
  prettierConfig: path.resolve(__dirname, '../../.prettierrc'),
};

/**
 * Template para modelo SQLAlchemy
 */
const generateSQLAlchemyModel = (entityName, fields = []) => {
  const entityNameLower = entityName.toLowerCase();

  const imports = [
    'from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float',
    'from sqlalchemy.orm import relationship',
    'from sqlalchemy.ext.declarative import declarative_base',
    'from datetime import datetime',
    'from typing import Optional',
  ];

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

  return `${imports.join('\n')}

Base = declarative_base()

class ${entityName}Model(Base):
    """Modelo SQLAlchemy para ${entityName}"""
    __tablename__ = "${entityNameLower}s"
    
    id = Column(Integer, primary_key=True, index=True)
${fieldsCode}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
${relationships}
    def __repr__(self):
        return f"<${entityName}Model(id={self.id})>"
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
${fields.map(field => `            '${field.name}': self.${field.name},`).join('\n')}
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
`;
};

/**
 * Template para modelo Pydantic
 */
const generatePydanticModel = (entityName, fields = []) => {
  const entityNameLower = entityName.toLowerCase();

  const fieldsCode = fields
    .map(field => {
      switch (field.type) {
        case 'string':
          return `    ${field.name}: str`;
        case 'text':
          return `    ${field.name}: Optional[str] = None`;
        case 'integer':
          return `    ${field.name}: int`;
        case 'float':
          return `    ${field.name}: float`;
        case 'boolean':
          return `    ${field.name}: bool = ${field.default || false}`;
        case 'datetime':
          return `    ${field.name}: Optional[datetime] = None`;
        case 'foreign_key':
          return `    ${field.name}_id: int`;
        default:
          return `    ${field.name}: str`;
      }
    })
    .join('\n');

  return `from pydantic import BaseModel
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
${fields.map(field => `    ${field.name}: Optional[${field.type === 'string' ? 'str' : field.type === 'integer' ? 'int' : field.type === 'float' ? 'float' : field.type === 'boolean' ? 'bool' : 'str'}] = None`).join('\n')}

class ${entityName}Response(${entityName}Base):
    """Modelo de resposta para ${entityName}"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
`;
};

/**
 * Template para migração Alembic
 */
const generateMigration = (entityName, fields = []) => {
  const entityNameLower = entityName.toLowerCase();
  const tableName = `${entityNameLower}s`;

  const columns = fields
    .map(field => {
      switch (field.type) {
        case 'string':
          return `        sa.Column('${field.name}', sa.String(${field.length || 255}), nullable=${field.nullable !== false})`;
        case 'text':
          return `        sa.Column('${field.name}', sa.Text(), nullable=${field.nullable !== false})`;
        case 'integer':
          return `        sa.Column('${field.name}', sa.Integer(), nullable=${field.nullable !== false})`;
        case 'float':
          return `        sa.Column('${field.name}', sa.Float(), nullable=${field.nullable !== false})`;
        case 'boolean':
          return `        sa.Column('${field.name}', sa.Boolean(), default=${field.default || false}, nullable=${field.nullable !== false})`;
        case 'datetime':
          return `        sa.Column('${field.name}', sa.DateTime(), nullable=${field.nullable !== false})`;
        case 'foreign_key':
          return `        sa.Column('${field.name}_id', sa.Integer(), sa.ForeignKey('${field.reference_table}.id'), nullable=${field.nullable !== false})`;
        default:
          return `        sa.Column('${field.name}', sa.String(255), nullable=${field.nullable !== false})`;
      }
    })
    .join(',\n');

  const indexes = fields
    .filter(field => field.index)
    .map(
      field =>
        `        sa.Index('ix_${tableName}_${field.name}', '${field.name}')`
    )
    .join(',\n');

  return `"""Create ${tableName} table

Revision ID: ${generateRevisionId()}
Revises: 
Create Date: ${new Date().toISOString()}

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '${generateRevisionId()}'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('${tableName}',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
${columns},
        sa.PrimaryKeyConstraint('id')
    )
${indexes ? `    op.create_index(op.f('ix_${tableName}_id'), '${tableName}', ['id'], unique=False)\n${indexes}` : `    op.create_index(op.f('ix_${tableName}_id'), '${tableName}', ['id'], unique=False)`}

def downgrade():
    op.drop_index(op.f('ix_${tableName}_id'), table_name='${tableName}')
${
  indexes
    ? `${indexes
        .split('\n')
        .map(
          idx =>
            `    op.drop_index(op.f('${idx.split("'")[1]}'), table_name='${tableName}')`
        )
        .join('\n')}\n`
    : ''
}    op.drop_table('${tableName}')
`;
};

/**
 * Gerador de ID de revisão
 */
const generateRevisionId = () => {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 5);
  return `${timestamp}_${random}`;
};

/**
 * Gerador de modelo baseado em configuração
 */
const generateModel = async config => {
  const { name, fields = [], description = '' } = config;

  const modelDir = path.join(CONFIG.outputDir, name);

  // Gerar modelo SQLAlchemy
  await createTsFile({
    directory: modelDir,
    fileName: 'model',
    content: generateSQLAlchemyModel(name, fields),
    extension: 'py',
    generatedBy: 'scripts/codegen/generateDatabase.js',
  });

  // Gerar modelo Pydantic
  await createTsFile({
    directory: modelDir,
    fileName: 'schema',
    content: generatePydanticModel(name, fields),
    extension: 'py',
    generatedBy: 'scripts/codegen/generateDatabase.js',
  });

  // Gerar migração
  await createTsFile({
    directory: CONFIG.migrationsDir,
    fileName: `${generateRevisionId()}_create_${name.toLowerCase()}_table`,
    content: generateMigration(name, fields),
    extension: 'py',
    generatedBy: 'scripts/codegen/generateDatabase.js',
  });

  // Gerar testes
  await createTsFile({
    directory: path.join(modelDir, 'tests'),
    fileName: `test_${name.toLowerCase()}`,
    content: generateModelTests(name, fields),
    extension: 'py',
    generatedBy: 'scripts/codegen/generateDatabase.js',
  });

  // Gerar README
  const readmeContent = `# Modelo ${name}

${description}

## Campos

${fields.map(field => `- \`${field.name}\` (${field.type}): ${field.description || 'Sem descrição'}`).join('\n')}

## Uso

\`\`\`python
from app.models.generated.${name.toLowerCase()}.model import ${name}Model
from app.models.generated.${name.toLowerCase()}.schema import ${name}Create, ${name}Update, ${name}Response

# Criar novo ${name}
${nameLower} = ${name}Model(name="Exemplo")
db.add(${nameLower})
db.commit()
\`\`\`

## Migrações

Execute as migrações com:

\`\`\`bash
alembic upgrade head
\`\`\`

## Testes

Execute os testes com:

\`\`\`bash
python -m pytest app/models/generated/${name.toLowerCase()}/tests/ -v
\`\`\`

---

*Este modelo foi gerado automaticamente pelo sistema de code generation.*`;

  await createTsFile({
    directory: modelDir,
    fileName: 'README',
    content: readmeContent,
    extension: 'md',
    generatedBy: 'scripts/codegen/generateDatabase.js',
  });
};

/**
 * Template para testes de modelo
 */
const generateModelTests = (entityName, fields = []) => {
  const entityNameLower = entityName.toLowerCase();

  return `import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.generated.${entityNameLower}.model import ${entityName}Model
from app.models.generated.${entityNameLower}.schema import ${entityName}Create, ${entityName}Update

class Test${entityName}Model(unittest.TestCase):
    """Testes para modelo ${entityName}"""
    
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        ${entityName}Model.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        self.session.close()
    
    def test_create_${entityNameLower}(self):
        """Testa criação de ${entityNameLower}"""
        ${entityNameLower} = ${entityName}Model(
${fields.map(field => `            ${field.name}="${field.type === 'string' ? 'Test' : field.type === 'integer' ? '1' : field.type === 'boolean' ? 'True' : 'Test'}"`).join(',\n            ')}
        )
        self.session.add(${entityNameLower})
        self.session.commit()
        
        self.assertIsNotNone(${entityNameLower}.id)
        self.assertIsNotNone(${entityNameLower}.created_at)
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        ${entityNameLower} = ${entityName}Model(
${fields.map(field => `            ${field.name}="${field.type === 'string' ? 'Test' : field.type === 'integer' ? '1' : field.type === 'boolean' ? 'True' : 'Test'}"`).join(',\n            ')}
        )
        self.session.add(${entityNameLower})
        self.session.commit()
        
        data = ${entityNameLower}.to_dict()
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
`;
};

/**
 * Utilitário para criar arquivos Python
 */
const createTsFile = async params => {
  const {
    directory,
    fileName,
    content,
    extension = 'py',
    generatedBy,
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
        parser: 'python',
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
 * Configurações de modelos para gerar
 */
const MODEL_CONFIGS = [
  {
    name: 'Project',
    description: 'Modelo para projetos de vídeo',
    fields: [
      {
        name: 'name',
        type: 'string',
        length: 255,
        description: 'Nome do projeto',
      },
      {
        name: 'description',
        type: 'text',
        description: 'Descrição do projeto',
      },
      {
        name: 'status',
        type: 'string',
        length: 50,
        description: 'Status do projeto',
      },
      {
        name: 'is_active',
        type: 'boolean',
        default: true,
        description: 'Projeto ativo',
      },
    ],
  },
  {
    name: 'Video',
    description: 'Modelo para vídeos',
    fields: [
      {
        name: 'title',
        type: 'string',
        length: 255,
        description: 'Título do vídeo',
      },
      { name: 'description', type: 'text', description: 'Descrição do vídeo' },
      { name: 'duration', type: 'float', description: 'Duração em segundos' },
      {
        name: 'file_path',
        type: 'string',
        length: 500,
        description: 'Caminho do arquivo',
      },
      {
        name: 'project_id',
        type: 'foreign_key',
        reference_table: 'projects',
        reference_model: 'Project',
        description: 'Projeto relacionado',
      },
    ],
  },
  {
    name: 'Scene',
    description: 'Modelo para cenas de vídeo',
    fields: [
      {
        name: 'title',
        type: 'string',
        length: 255,
        description: 'Título da cena',
      },
      { name: 'duration', type: 'float', description: 'Duração da cena' },
      { name: 'order', type: 'integer', description: 'Ordem da cena' },
      {
        name: 'video_id',
        type: 'foreign_key',
        reference_table: 'videos',
        reference_model: 'Video',
        description: 'Vídeo relacionado',
      },
    ],
  },
  {
    name: 'Asset',
    description: 'Modelo para assets (imagens, áudios, etc.)',
    fields: [
      {
        name: 'name',
        type: 'string',
        length: 255,
        description: 'Nome do asset',
      },
      {
        name: 'type',
        type: 'string',
        length: 50,
        description: 'Tipo do asset',
      },
      {
        name: 'file_path',
        type: 'string',
        length: 500,
        description: 'Caminho do arquivo',
      },
      { name: 'size', type: 'integer', description: 'Tamanho em bytes' },
      {
        name: 'scene_id',
        type: 'foreign_key',
        reference_table: 'scenes',
        reference_model: 'Scene',
        description: 'Cena relacionada',
      },
    ],
  },
  {
    name: 'User',
    description: 'Modelo para usuários',
    fields: [
      {
        name: 'username',
        type: 'string',
        length: 100,
        description: 'Nome de usuário',
      },
      {
        name: 'email',
        type: 'string',
        length: 255,
        description: 'Email do usuário',
      },
      {
        name: 'password_hash',
        type: 'string',
        length: 255,
        description: 'Hash da senha',
      },
      {
        name: 'is_active',
        type: 'boolean',
        default: true,
        description: 'Usuário ativo',
      },
      { name: 'last_login', type: 'datetime', description: 'Último login' },
    ],
  },
];

/**
 * Função principal de geração
 */
const main = async () => {
  console.log('🚀 Iniciando geração de modelos de banco...');

  try {
    // Criar diretório de saída
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });

    // Gerar cada modelo
    for (const config of MODEL_CONFIGS) {
      console.log(`📦 Gerando modelo: ${config.name}`);
      await generateModel(config);
    }

    // Gerar arquivo de índice
    const indexContent = MODEL_CONFIGS.map(
      config =>
        `from .${config.name.toLowerCase()}.model import ${config.name}Model`
    ).join('\n');

    await createTsFile({
      directory: CONFIG.outputDir,
      fileName: 'index',
      content: indexContent,
      extension: 'py',
      generatedBy: 'scripts/codegen/generateDatabase.js',
    });

    console.log('✅ Geração de modelos concluída com sucesso!');
    console.log(`📁 Modelos gerados em: ${CONFIG.outputDir}`);
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
  generateModel,
  createTsFile,
  CONFIG,
};
