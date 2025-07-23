#!/usr/bin/env node

/**
 * Gerador de Código para Documentação Automática
 * TecnoCursos AI - Documentation Code Generation System
 *
 * Baseado nas melhores práticas de code generation:
 * - Documentação automática de APIs
 * - Exemplos de uso
 * - Diagramas de arquitetura
 * - Guias de desenvolvimento
 */

const fs = require('fs');
const path = require('path');
const prettier = require('prettier');

/**
 * Configuração do sistema de geração
 */
const CONFIG = {
  docsDir: path.resolve(__dirname, '../../docs'),
  outputDir: path.resolve(__dirname, '../../docs/generated'),
  prettierConfig: path.resolve(__dirname, '../../.prettierrc'),
};

/**
 * Template para documentação de API OpenAPI
 */
const generateOpenAPIDoc = (apiName, endpoints = []) => {
  const paths = endpoints
    .map(endpoint => {
      const { path } = endpoint;
      const method = endpoint.method.toLowerCase();
      const summary = endpoint.summary || `${endpoint.method} ${endpoint.name}`;
      const description =
        endpoint.description ||
        `Operação ${endpoint.method} para ${endpoint.name}`;

      return `  ${path}:
    ${method}:
      tags:
        - ${apiName}
      summary: ${summary}
      description: ${description}
      parameters:
${
  endpoint.parameters
    ? endpoint.parameters
        .map(
          param => `        - name: ${param.name}
          in: ${param.in}
          required: ${param.required || false}
          schema:
            type: ${param.type}
          description: ${param.description || ''}`
        )
        .join('\n')
    : `        - name: id
          in: path
          required: true
          schema:
            type: integer
          description: ID do ${apiName.toLowerCase()}`
}
      responses:
        ${endpoint.expectedStatus || 200}:
          description: Sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/${apiName}Response'
        ${endpoint.errorStatus || 400}:
          description: Erro de validação
        ${endpoint.notFoundStatus || 404}:
          description: Não encontrado
        ${endpoint.serverErrorStatus || 500}:
          description: Erro interno do servidor`;
    })
    .join('\n\n');

  return `openapi: 3.0.0
info:
  title: ${apiName} API
  description: API para gerenciamento de ${apiName.toLowerCase()}s
  version: 1.0.0
  contact:
    name: TecnoCursos AI Team
    email: support@tecnocursos.ai

servers:
  - url: http://localhost:8000
    description: Servidor de desenvolvimento
  - url: https://api.tecnocursos.ai
    description: Servidor de produção

paths:
${paths}

components:
  schemas:
    ${apiName}Base:
      type: object
      properties:
        name:
          type: string
          description: Nome do ${apiName.toLowerCase()}
        description:
          type: string
          description: Descrição do ${apiName.toLowerCase()}
        is_active:
          type: boolean
          description: Status ativo
          default: true
      required:
        - name

    ${apiName}Create:
      allOf:
        - $ref: '#/components/schemas/${apiName}Base'

    ${apiName}Update:
      type: object
      properties:
        name:
          type: string
          description: Nome do ${apiName.toLowerCase()}
        description:
          type: string
          description: Descrição do ${apiName.toLowerCase()}
        is_active:
          type: boolean
          description: Status ativo

    ${apiName}Response:
      allOf:
        - $ref: '#/components/schemas/${apiName}Base'
        - type: object
          properties:
            id:
              type: integer
              description: ID único
            created_at:
              type: string
              format: date-time
              description: Data de criação
            updated_at:
              type: string
              format: date-time
              description: Data de atualização
          required:
            - id
            - created_at
            - updated_at`;
};

/**
 * Template para documentação de componente React
 */
const generateReactDoc = (componentName, props = []) => {
  const propsTable = props
    .map(prop => {
      return `| ${prop.name} | ${prop.type} | ${prop.required ? 'Sim' : 'Não'} | ${prop.default || '-'} | ${prop.description || ''} |`;
    })
    .join('\n');

  const examples =
    props.length > 0
      ? `
## Exemplos de Uso

### Uso Básico
\`\`\`jsx
import ${componentName} from './${componentName}';

<${componentName} />
\`\`\`

### Com Props
\`\`\`jsx
<${componentName}
${props.map(prop => `  ${prop.name}={${prop.example || prop.default || 'value'}}`).join('\n')}
/>
\`\`\``
      : '';

  return `# ${componentName}

Componente React para ${componentName.toLowerCase()}.

## Props

| Prop | Tipo | Obrigatório | Padrão | Descrição |
|------|------|-------------|--------|-----------|
${propsTable}

## Uso

\`\`\`jsx
import ${componentName} from './${componentName}';

function App() {
  return (
    <div>
      <${componentName} />
    </div>
  );
}
\`\`\`
${examples}

## Estilos

O componente usa CSS Modules e pode ser customizado através de classes CSS.

## Acessibilidade

- Suporte completo a navegação por teclado
- Atributos ARIA apropriados
- Contraste de cores adequado

## Testes

Execute os testes com:

\`\`\`bash
npm test -- --testPathPattern=${componentName}
\`\`\`

## Changelog

### v1.0.0
- Implementação inicial
- Suporte a todas as props básicas
- Testes unitários completos`;
};

/**
 * Template para documentação de modelo de banco
 */
const generateDatabaseDoc = (modelName, fields = []) => {
  const fieldsTable = fields
    .map(field => {
      return `| ${field.name} | ${field.type} | ${field.nullable !== false ? 'Sim' : 'Não'} | ${field.default || '-'} | ${field.description || ''} |`;
    })
    .join('\n');

  const relationships = fields
    .filter(field => field.type === 'foreign_key')
    .map(field => `- \`${field.name}_id\` → \`${field.reference_table}.id\``)
    .join('\n');

  return `# Modelo ${modelName}

Modelo SQLAlchemy para ${modelName.toLowerCase()}.

## Tabela

\`\`\`sql
CREATE TABLE ${modelName.toLowerCase()}s (
  id INTEGER PRIMARY KEY,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
${fields.map(field => `  ${field.name} ${field.sqlType || 'VARCHAR(255)'}${field.nullable !== false ? ' NOT NULL' : ''}${field.default ? ` DEFAULT ${field.default}` : ''},`).join('\n')}
);
\`\`\`

## Campos

| Campo | Tipo | Nullable | Padrão | Descrição |
|-------|------|----------|--------|-----------|
${fieldsTable}

## Relacionamentos

${relationships || 'Nenhum relacionamento definido.'}

## Uso

\`\`\`python
from app.models.${modelName.toLowerCase()} import ${modelName}Model

# Criar novo ${modelName.toLowerCase()}
${modelNameLower} = ${modelName}Model(
${fields.map(field => `    ${field.name}="${field.type === 'string' ? 'Exemplo' : field.type === 'integer' ? '1' : field.type === 'boolean' ? 'True' : 'Exemplo'}",`).join('\n')}
)

# Salvar no banco
db.add(${modelNameLower})
db.commit()

# Buscar por ID
${modelNameLower} = db.query(${modelName}Model).filter(${modelName}Model.id == 1).first()

# Converter para dicionário
data = ${modelNameLower}.to_dict()
\`\`\`

## Migrações

Para criar uma nova migração:

\`\`\`bash
alembic revision --autogenerate -m "Add ${modelName} model"
alembic upgrade head
\`\`\`

## Índices

${
  fields
    .filter(field => field.index)
    .map(
      field =>
        `- \`ix_${modelName.toLowerCase()}s_${field.name}\` em \`${field.name}\``
    )
    .join('\n') || 'Nenhum índice personalizado definido.'
}`;
};

/**
 * Template para documentação de arquitetura
 */
const generateArchitectureDoc = (systemName, components = []) => {
  const componentsList = components
    .map(comp => {
      return `### ${comp.name}
${comp.description}

**Tecnologias:** ${comp.technologies.join(', ')}
**Responsabilidades:** ${comp.responsibilities.join(', ')}`;
    })
    .join('\n\n');

  return `# Arquitetura ${systemName}

Visão geral da arquitetura do sistema ${systemName}.

## Diagrama de Arquitetura

\`\`\`mermaid
graph TB
${components.map(comp => `    ${comp.id}[${comp.name}]`).join('\n')}
    
${components
  .map(comp =>
    comp.connections
      ? comp.connections.map(conn => `    ${comp.id} --> ${conn}`).join('\n')
      : ''
  )
  .filter(Boolean)
  .join('\n')}
\`\`\`

## Componentes

${componentsList}

## Fluxo de Dados

1. **Frontend** envia requisições para o **Backend**
2. **Backend** processa e valida os dados
3. **Backend** interage com o **Banco de Dados**
4. **Backend** retorna resposta para o **Frontend**

## Tecnologias

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Heroicons

### Backend
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic

### Banco de Dados
- PostgreSQL (produção)
- SQLite (desenvolvimento)

### Infraestrutura
- Docker
- Nginx
- Redis (cache)

## Padrões de Design

- **MVC**: Separação clara entre Model, View e Controller
- **Repository**: Abstração do acesso a dados
- **Dependency Injection**: Injeção de dependências
- **Observer**: Padrão para eventos e notificações

## Segurança

- Autenticação JWT
- Validação de entrada
- Sanitização de dados
- Rate limiting
- CORS configurado

## Performance

- Cache Redis
- Lazy loading
- Paginação
- Índices otimizados
- CDN para assets estáticos

## Monitoramento

- Logs estruturados
- Métricas Prometheus
- Health checks
- Error tracking

## Deploy

### Desenvolvimento
\`\`\`bash
docker-compose up -d
\`\`\`

### Produção
\`\`\`bash
docker-compose -f docker-compose.prod.yml up -d
\`\`\``;
};

/**
 * Gerador de documentação baseado em configuração
 */
const generateDocumentation = async config => {
  const {
    name,
    type,
    description = '',
    props = [],
    endpoints = [],
    fields = [],
    components = [],
  } = config;

  const docDir = path.join(CONFIG.outputDir, type, name);

  let docContent = '';
  let extension = 'md';

  switch (type) {
    case 'openapi':
      docContent = generateOpenAPIDoc(name, endpoints);
      extension = 'yaml';
      break;
    case 'react':
      docContent = generateReactDoc(name, props);
      extension = 'md';
      break;
    case 'database':
      docContent = generateDatabaseDoc(name, fields);
      extension = 'md';
      break;
    case 'architecture':
      docContent = generateArchitectureDoc(name, components);
      extension = 'md';
      break;
    default:
      throw new Error(`Tipo de documentação não suportado: ${type}`);
  }

  // Gerar arquivo de documentação
  await createTsFile({
    directory: docDir,
    fileName: name.toLowerCase(),
    content: docContent,
    extension,
    generatedBy: 'scripts/codegen/generateDocs.js',
  });

  // Gerar arquivo de configuração
  const configContent = `{
  "name": "${name}",
  "type": "${type}",
  "description": "${description}",
  "props": ${JSON.stringify(props, null, 2)},
  "endpoints": ${JSON.stringify(endpoints, null, 2)},
  "fields": ${JSON.stringify(fields, null, 2)},
  "components": ${JSON.stringify(components, null, 2)}
}`;

  await createTsFile({
    directory: docDir,
    fileName: 'doc.config',
    content: configContent,
    extension: 'json',
    generatedBy: 'scripts/codegen/generateDocs.js',
  });
};

/**
 * Utilitário para criar arquivos
 */
const createTsFile = async params => {
  const {
    directory,
    fileName,
    content,
    extension = 'md',
    generatedBy,
  } = params;

  // Criar diretório se não existir
  fs.mkdirSync(directory, { recursive: true });

  // Formatar conteúdo se necessário
  let formattedContent = content;
  if (extension === 'json' || extension === 'yaml') {
    try {
      const config = await prettier.resolveConfig(CONFIG.prettierConfig);
      formattedContent = await prettier.format(
        `# Este arquivo foi gerado automaticamente por ${generatedBy}\n# Não edite manualmente - use o sistema de geração\n\n${content}`,
        {
          ...config,
          parser: extension === 'json' ? 'json' : 'yaml',
        }
      );
    } catch (error) {
      formattedContent = `# Este arquivo foi gerado automaticamente por ${generatedBy}\n# Não edite manualmente - use o sistema de geração\n\n${content}`;
    }
  }

  const filePath = `${directory}/${fileName}.${extension}`;
  fs.writeFileSync(filePath, formattedContent);

  console.log(`✅ Arquivo gerado: ${filePath}`);
  return filePath;
};

/**
 * Configurações de documentação para gerar
 */
const DOC_CONFIGS = [
  {
    name: 'VideoAPI',
    type: 'openapi',
    description: 'Documentação OpenAPI para API de vídeos',
    endpoints: [
      {
        method: 'GET',
        name: 'list_videos',
        path: '/api/videos',
        summary: 'Lista todos os vídeos',
        description: 'Retorna uma lista paginada de vídeos',
        parameters: [
          {
            name: 'skip',
            in: 'query',
            type: 'integer',
            description: 'Número de registros para pular',
          },
          {
            name: 'limit',
            in: 'query',
            type: 'integer',
            description: 'Número máximo de registros',
          },
        ],
      },
      {
        method: 'POST',
        name: 'create_video',
        path: '/api/videos',
        summary: 'Cria um novo vídeo',
        description: 'Cria um novo vídeo com os dados fornecidos',
      },
      {
        method: 'GET',
        name: 'get_video',
        path: '/api/videos/{id}',
        summary: 'Obtém um vídeo específico',
        description: 'Retorna os detalhes de um vídeo específico',
      },
      {
        method: 'PUT',
        name: 'update_video',
        path: '/api/videos/{id}',
        summary: 'Atualiza um vídeo',
        description: 'Atualiza os dados de um vídeo específico',
      },
      {
        method: 'DELETE',
        name: 'delete_video',
        path: '/api/videos/{id}',
        summary: 'Remove um vídeo',
        description: 'Remove um vídeo específico',
      },
    ],
  },
  {
    name: 'Toolbar',
    type: 'react',
    description: 'Documentação do componente Toolbar',
    props: [
      {
        name: 'onUndo',
        type: 'function',
        required: false,
        description: 'Callback para desfazer ação',
      },
      {
        name: 'onRedo',
        type: 'function',
        required: false,
        description: 'Callback para refazer ação',
      },
      {
        name: 'canUndo',
        type: 'boolean',
        required: false,
        default: false,
        description: 'Estado de habilitação desfazer',
      },
      {
        name: 'canRedo',
        type: 'boolean',
        required: false,
        default: false,
        description: 'Estado de habilitação refazer',
      },
    ],
  },
  {
    name: 'Video',
    type: 'database',
    description: 'Documentação do modelo Video',
    fields: [
      {
        name: 'title',
        type: 'string',
        nullable: false,
        description: 'Título do vídeo',
      },
      {
        name: 'description',
        type: 'text',
        nullable: true,
        description: 'Descrição do vídeo',
      },
      {
        name: 'duration',
        type: 'float',
        nullable: true,
        description: 'Duração em segundos',
      },
      {
        name: 'file_path',
        type: 'string',
        nullable: false,
        description: 'Caminho do arquivo',
      },
      {
        name: 'is_active',
        type: 'boolean',
        nullable: false,
        default: true,
        description: 'Vídeo ativo',
      },
    ],
  },
  {
    name: 'TecnoCursosAI',
    type: 'architecture',
    description: 'Documentação da arquitetura do sistema',
    components: [
      {
        id: 'frontend',
        name: 'Frontend React',
        description: 'Interface do usuário construída com React',
        technologies: ['React', 'TypeScript', 'Tailwind CSS'],
        responsibilities: [
          'Renderização de componentes',
          'Gerenciamento de estado',
          'Interação com API',
        ],
      },
      {
        id: 'backend',
        name: 'Backend FastAPI',
        description: 'API REST construída com FastAPI',
        technologies: ['FastAPI', 'SQLAlchemy', 'Pydantic'],
        responsibilities: [
          'Processamento de requisições',
          'Validação de dados',
          'Lógica de negócio',
        ],
      },
      {
        id: 'database',
        name: 'Banco de Dados',
        description: 'Armazenamento persistente de dados',
        technologies: ['PostgreSQL', 'SQLAlchemy', 'Alembic'],
        responsibilities: [
          'Persistência de dados',
          'Relacionamentos',
          'Migrações',
        ],
      },
      {
        id: 'cache',
        name: 'Cache Redis',
        description: 'Cache em memória para performance',
        technologies: ['Redis'],
        responsibilities: [
          'Cache de sessões',
          'Cache de dados',
          'Filas de processamento',
        ],
      },
    ],
  },
];

/**
 * Função principal de geração
 */
const main = async () => {
  console.log('🚀 Iniciando geração de documentação...');

  try {
    // Criar diretório de saída
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });

    // Gerar cada documentação
    for (const config of DOC_CONFIGS) {
      console.log(`📦 Gerando documentação: ${config.name} (${config.type})`);
      await generateDocumentation(config);
    }

    // Gerar arquivo de índice
    const indexContent = `# Documentação Gerada

Esta documentação foi gerada automaticamente pelo sistema de code generation.

## Arquivos Gerados

${DOC_CONFIGS.map(config => `- [${config.name}](./${config.type}/${config.name}/${config.name.toLowerCase()}.${config.type === 'openapi' ? 'yaml' : 'md'})`).join('\n')}

## Como Usar

1. **APIs**: Use os arquivos OpenAPI para gerar clientes automaticamente
2. **Componentes**: Consulte a documentação React para implementação
3. **Modelos**: Veja a estrutura do banco de dados
4. **Arquitetura**: Entenda a estrutura geral do sistema

## Atualização

Para atualizar a documentação, execute:

\`\`\`bash
node scripts/codegen/generateDocs.js
\`\`\`

---

*Documentação gerada automaticamente em ${new Date().toISOString()}*`;

    await createTsFile({
      directory: CONFIG.outputDir,
      fileName: 'README',
      content: indexContent,
      extension: 'md',
      generatedBy: 'scripts/codegen/generateDocs.js',
    });

    console.log('✅ Geração de documentação concluída com sucesso!');
    console.log(`📁 Documentação gerada em: ${CONFIG.outputDir}`);
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
  generateDocumentation,
  createTsFile,
  CONFIG,
};
