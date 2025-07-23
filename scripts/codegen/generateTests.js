#!/usr/bin/env node

/**
 * Gerador de Código para Testes Automatizados
 * TecnoCursos AI - Test Code Generation System
 *
 * Baseado nas melhores práticas de code generation:
 * - Geração determinística de testes
 * - Cobertura completa
 * - Mocks automáticos
 * - Testes de integração
 */

const fs = require('fs');
const path = require('path');
const prettier = require('prettier');

/**
 * Configuração do sistema de geração
 */
const CONFIG = {
  testsDir: path.resolve(__dirname, '../../tests'),
  outputDir: path.resolve(__dirname, '../../tests/generated'),
  prettierConfig: path.resolve(__dirname, '../../.prettierrc'),
};

/**
 * Template para testes unitários React
 */
const generateReactTests = (componentName, props = []) => {
  const propsTests = props
    .map(prop => {
      switch (prop.type) {
        case 'string':
          return `
  test('renderiza com prop ${prop.name}', () => {
    render(<${componentName} ${prop.name}="test value" />);
    expect(screen.getByText('test value')).toBeInTheDocument();
  });`;
        case 'boolean':
          return `
  test('renderiza com prop ${prop.name}', () => {
    render(<${componentName} ${prop.name}={true} />);
    expect(screen.getByTestId('${componentName.toLowerCase()}-${prop.name}')).toBeInTheDocument();
  });`;
        case 'function':
          return `
  test('chama ${prop.name} quando clicado', () => {
    const mock${prop.name.charAt(0).toUpperCase() + prop.name.slice(1)} = jest.fn();
    render(<${componentName} ${prop.name}={mock${prop.name.charAt(0).toUpperCase() + prop.name.slice(1)}} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(mock${prop.name.charAt(0).toUpperCase() + prop.name.slice(1)}).toHaveBeenCalledTimes(1);
  });`;
        default:
          return `
  test('renderiza com prop ${prop.name}', () => {
    render(<${componentName} ${prop.name}="test" />);
    expect(screen.getByTestId('${componentName.toLowerCase()}-${prop.name}')).toBeInTheDocument();
  });`;
      }
    })
    .join('');

  return `import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ${componentName} from '../${componentName}';

describe('${componentName} Component', () => {
  test('renderiza o componente corretamente', () => {
    render(<${componentName} />);
    expect(screen.getByText('${componentName}')).toBeInTheDocument();
  });

  test('aplica classes CSS corretas', () => {
    render(<${componentName} />);
    const container = screen.getByText('${componentName}').parentElement;
    expect(container).toHaveClass('${componentName.toLowerCase()}-container');
  });
${propsTests}
  
  test('testa acessibilidade', () => {
    render(<${componentName} />);
    const element = screen.getByRole('main');
    expect(element).toBeInTheDocument();
  });
});`;
};

/**
 * Template para testes de API
 */
const generateAPITests = (apiName, endpoints = []) => {
  const endpointTests = endpoints
    .map(endpoint => {
      switch (endpoint.method) {
        case 'GET':
          return `
  def test_get_${endpoint.name}(self):
      """Testa endpoint GET ${endpoint.path}"""
      response = self.client.get('${endpoint.path}')
      self.assertEqual(response.status_code, ${endpoint.expectedStatus || 200})
      self.assertIsInstance(response.json(), ${endpoint.expectedType || 'dict'})`;
        case 'POST':
          return `
  def test_post_${endpoint.name}(self):
      """Testa endpoint POST ${endpoint.path}"""
      data = ${JSON.stringify(endpoint.sampleData || {})}
      response = self.client.post('${endpoint.path}', json=data)
      self.assertEqual(response.status_code, ${endpoint.expectedStatus || 201})
      self.assertIn('id', response.json())`;
        case 'PUT':
          return `
  def test_put_${endpoint.name}(self):
      """Testa endpoint PUT ${endpoint.path}"""
      # Criar item primeiro
      create_data = ${JSON.stringify(endpoint.sampleData || {})}
      create_response = self.client.post('${endpoint.path.replace('/{id}', '')}', json=create_data)
      item_id = create_response.json()['id']
      
      # Atualizar item
      update_data = ${JSON.stringify(endpoint.updateData || {})}
      response = self.client.put(f'${endpoint.path}', json=update_data)
      self.assertEqual(response.status_code, ${endpoint.expectedStatus || 200})`;
        case 'DELETE':
          return `
  def test_delete_${endpoint.name}(self):
      """Testa endpoint DELETE ${endpoint.path}"""
      # Criar item primeiro
      create_data = ${JSON.stringify(endpoint.sampleData || {})}
      create_response = self.client.post('${endpoint.path.replace('/{id}', '')}', json=create_data)
      item_id = create_response.json()['id']
      
      # Deletar item
      response = self.client.delete(f'${endpoint.path}')
      self.assertEqual(response.status_code, ${endpoint.expectedStatus || 204})`;
        default:
          return '';
      }
    })
    .join('\n');

  return `import unittest
from fastapi.testclient import TestClient
from app.main import app

class Test${apiName}API(unittest.TestCase):
    """Testes para API ${apiName}"""
    
    def setUp(self):
        self.client = TestClient(app)
    
    def tearDown(self):
        # Limpar dados de teste se necessário
        pass
${endpointTests}
    
    def test_api_health(self):
        """Testa saúde da API"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'healthy'})`;
};

/**
 * Template para testes de banco de dados
 */
const generateDatabaseTests = (modelName, fields = []) => {
  const fieldTests = fields
    .map(field => {
      switch (field.type) {
        case 'string':
          return `
    def test_${field.name}_field(self):
        """Testa campo ${field.name}"""
        ${modelNameLower} = ${modelName}Model(${field.name}="test value")
        self.assertEqual(${modelNameLower}.${field.name}, "test value")`;
        case 'integer':
          return `
    def test_${field.name}_field(self):
        """Testa campo ${field.name}"""
        ${modelNameLower} = ${modelName}Model(${field.name}=123)
        self.assertEqual(${modelNameLower}.${field.name}, 123)`;
        case 'boolean':
          return `
    def test_${field.name}_field(self):
        """Testa campo ${field.name}"""
        ${modelNameLower} = ${modelName}Model(${field.name}=True)
        self.assertTrue(${modelNameLower}.${field.name})`;
        default:
          return `
    def test_${field.name}_field(self):
        """Testa campo ${field.name}"""
        ${modelNameLower} = ${modelName}Model(${field.name}="test")
        self.assertEqual(${modelNameLower}.${field.name}, "test")`;
      }
    })
    .join('');

  return `import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.${modelName.toLowerCase()} import ${modelName}Model

class Test${modelName}Model(unittest.TestCase):
    """Testes para modelo ${modelName}"""
    
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        ${modelName}Model.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        self.session.close()
    
    def test_create_${modelNameLower}(self):
        """Testa criação de ${modelNameLower}"""
        ${modelNameLower} = ${modelName}Model(
${fields.map(field => `            ${field.name}="${field.type === 'string' ? 'Test' : field.type === 'integer' ? '1' : field.type === 'boolean' ? 'True' : 'Test'}"`).join(',\n            ')}
        )
        self.session.add(${modelNameLower})
        self.session.commit()
        
        self.assertIsNotNone(${modelNameLower}.id)
        self.assertIsNotNone(${modelNameLower}.created_at)
${fieldTests}
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        ${modelNameLower} = ${modelName}Model(
${fields.map(field => `            ${field.name}="${field.type === 'string' ? 'Test' : field.type === 'integer' ? '1' : field.type === 'boolean' ? 'True' : 'Test'}"`).join(',\n            ')}
        )
        self.session.add(${modelNameLower})
        self.session.commit()
        
        data = ${modelNameLower}.to_dict()
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)`;
};

/**
 * Template para testes de integração
 */
const generateIntegrationTests = (testName, scenarios = []) => {
  const scenarioTests = scenarios
    .map(scenario => {
      return `
  def test_${scenario.name}(self):
      """Testa cenário: ${scenario.description}"""
      # Setup
${scenario.setup.map(step => `      ${step}`).join('\n')}
      
      # Execute
${scenario.execute.map(step => `      ${step}`).join('\n')}
      
      # Assert
${scenario.assert.map(assertion => `      ${assertion}`).join('\n')}`;
    })
    .join('');

  return `import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db

class Test${testName}Integration(unittest.TestCase):
    """Testes de integração para ${testName}"""
    
    def setUp(self):
        self.client = TestClient(app)
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        self.session.close()
    
    def test_health_check(self):
        """Testa verificação de saúde da aplicação"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'healthy'})
${scenarioTests}
    
    def test_database_connection(self):
        """Testa conexão com banco de dados"""
        try:
            self.session.execute('SELECT 1')
            self.assertTrue(True)
        except Exception as e:
            self.fail(f'Falha na conexão com banco: {e}')`;
};

/**
 * Gerador de testes baseado em configuração
 */
const generateTests = async config => {
  const {
    name,
    type,
    props = [],
    endpoints = [],
    fields = [],
    scenarios = [],
    description = '',
  } = config;

  const testDir = path.join(CONFIG.outputDir, type, name);

  let testContent = '';
  let extension = 'js';

  switch (type) {
    case 'react':
      testContent = generateReactTests(name, props);
      extension = 'js';
      break;
    case 'api':
      testContent = generateAPITests(name, endpoints);
      extension = 'py';
      break;
    case 'database':
      testContent = generateDatabaseTests(name, fields);
      extension = 'py';
      break;
    case 'integration':
      testContent = generateIntegrationTests(name, scenarios);
      extension = 'py';
      break;
    default:
      throw new Error(`Tipo de teste não suportado: ${type}`);
  }

  // Gerar arquivo de teste
  await createTsFile({
    directory: testDir,
    fileName: `test_${name.toLowerCase()}`,
    content: testContent,
    extension,
    generatedBy: 'scripts/codegen/generateTests.js',
  });

  // Gerar arquivo de configuração de teste
  const configContent = `{
  "name": "${name}",
  "type": "${type}",
  "description": "${description}",
  "props": ${JSON.stringify(props, null, 2)},
  "endpoints": ${JSON.stringify(endpoints, null, 2)},
  "fields": ${JSON.stringify(fields, null, 2)},
  "scenarios": ${JSON.stringify(scenarios, null, 2)}
}`;

  await createTsFile({
    directory: testDir,
    fileName: 'test.config',
    content: configContent,
    extension: 'json',
    generatedBy: 'scripts/codegen/generateTests.js',
  });

  // Gerar README
  const readmeContent = `# Testes ${name}

${description}

## Tipo de Teste

${type.toUpperCase()}

## Execução

\`\`\`bash
# Testes React
npm test -- --testPathPattern=${name}

# Testes Python
python -m pytest tests/generated/${type}/${name}/ -v

# Testes de Integração
python -m pytest tests/generated/integration/${name}/ -v
\`\`\`

## Cobertura

- ✅ Renderização
- ✅ Props
- ✅ Eventos
- ✅ Acessibilidade
- ✅ Integração com API
- ✅ Banco de dados

---

*Estes testes foram gerados automaticamente pelo sistema de code generation.*`;

  await createTsFile({
    directory: testDir,
    fileName: 'README',
    content: readmeContent,
    extension: 'md',
    generatedBy: 'scripts/codegen/generateTests.js',
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
    extension = 'js',
    generatedBy,
  } = params;

  // Criar diretório se não existir
  fs.mkdirSync(directory, { recursive: true });

  // Formatar código com Prettier
  let formattedContent = content;
  try {
    const config = await prettier.resolveConfig(CONFIG.prettierConfig);
    formattedContent = await prettier.format(
      `// Este arquivo foi gerado automaticamente por ${generatedBy}\n// Não edite manualmente - use o sistema de geração\n\n${content}`,
      {
        ...config,
        parser:
          extension === 'js' ? 'babel' : extension === 'py' ? 'python' : 'json',
      }
    );
  } catch (error) {
    // Se prettier não estiver disponível, usar conteúdo original
    formattedContent = `// Este arquivo foi gerado automaticamente por ${generatedBy}\n// Não edite manualmente - use o sistema de geração\n\n${content}`;
  }

  const filePath = `${directory}/${fileName}.${extension}`;
  fs.writeFileSync(filePath, formattedContent);

  console.log(`✅ Arquivo gerado: ${filePath}`);
  return filePath;
};

/**
 * Configurações de testes para gerar
 */
const TEST_CONFIGS = [
  {
    name: 'Toolbar',
    type: 'react',
    description: 'Testes para componente Toolbar',
    props: [
      {
        name: 'onUndo',
        type: 'function',
        description: 'Callback para desfazer',
      },
      {
        name: 'onRedo',
        type: 'function',
        description: 'Callback para refazer',
      },
      {
        name: 'canUndo',
        type: 'boolean',
        description: 'Estado de habilitação desfazer',
      },
      {
        name: 'canRedo',
        type: 'boolean',
        description: 'Estado de habilitação refazer',
      },
    ],
  },
  {
    name: 'VideoAPI',
    type: 'api',
    description: 'Testes para API de vídeos',
    endpoints: [
      {
        method: 'GET',
        name: 'list_videos',
        path: '/api/videos',
        expectedStatus: 200,
      },
      {
        method: 'POST',
        name: 'create_video',
        path: '/api/videos',
        expectedStatus: 201,
        sampleData: { title: 'Test Video', description: 'Test Description' },
      },
      {
        method: 'GET',
        name: 'get_video',
        path: '/api/videos/{id}',
        expectedStatus: 200,
      },
      {
        method: 'PUT',
        name: 'update_video',
        path: '/api/videos/{id}',
        expectedStatus: 200,
        updateData: { title: 'Updated Video' },
      },
      {
        method: 'DELETE',
        name: 'delete_video',
        path: '/api/videos/{id}',
        expectedStatus: 204,
      },
    ],
  },
  {
    name: 'VideoModel',
    type: 'database',
    description: 'Testes para modelo de vídeo',
    fields: [
      { name: 'title', type: 'string', description: 'Título do vídeo' },
      {
        name: 'description',
        type: 'string',
        description: 'Descrição do vídeo',
      },
      { name: 'duration', type: 'integer', description: 'Duração em segundos' },
      { name: 'is_active', type: 'boolean', description: 'Vídeo ativo' },
    ],
  },
  {
    name: 'VideoWorkflow',
    type: 'integration',
    description: 'Testes de integração para workflow de vídeo',
    scenarios: [
      {
        name: 'create_and_process_video',
        description: 'Criar e processar um vídeo completo',
        setup: [
          'video_data = {"title": "Test Video", "description": "Test Description"}',
          'project_data = {"name": "Test Project", "description": "Test Project Description"}',
        ],
        execute: [
          'project_response = self.client.post("/api/projects", json=project_data)',
          'project_id = project_response.json()["id"]',
          'video_data["project_id"] = project_id',
          'video_response = self.client.post("/api/videos", json=video_data)',
        ],
        assert: [
          'self.assertEqual(video_response.status_code, 201)',
          'self.assertIn("id", video_response.json())',
          'self.assertEqual(video_response.json()["title"], "Test Video")',
        ],
      },
    ],
  },
];

/**
 * Função principal de geração
 */
const main = async () => {
  console.log('🚀 Iniciando geração de testes...');

  try {
    // Criar diretório de saída
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });

    // Gerar cada teste
    for (const config of TEST_CONFIGS) {
      console.log(`📦 Gerando teste: ${config.name} (${config.type})`);
      await generateTests(config);
    }

    // Gerar arquivo de índice
    const indexContent = TEST_CONFIGS.map(
      config =>
        `export { default as ${config.name}Test } from './${config.type}/${config.name}/test_${config.name.toLowerCase()}.${config.type === 'react' ? 'js' : 'py'}';`
    ).join('\n');

    await createTsFile({
      directory: CONFIG.outputDir,
      fileName: 'index',
      content: indexContent,
      extension: 'js',
      generatedBy: 'scripts/codegen/generateTests.js',
    });

    console.log('✅ Geração de testes concluída com sucesso!');
    console.log(`📁 Testes gerados em: ${CONFIG.outputDir}`);
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
  generateTests,
  createTsFile,
  CONFIG,
};
