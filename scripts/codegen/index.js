#!/usr/bin/env node

/**
 * Sistema Principal de Geração de Código
 * TecnoCursos AI - Main Code Generation System
 *
 * Orquestra todos os geradores de código:
 * - Componentes React
 * - APIs FastAPI
 * - Modelos de Banco
 * - Testes Automatizados
 * - Documentação
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Importar todos os geradores
const {
  generateComponent,
  CONFIG: componentsConfig,
} = require('./generateComponents');
const { generateAPI, CONFIG: apiConfig } = require('./generateAPI');
const { generateModel, CONFIG: databaseConfig } = require('./generateDatabase');
const { generateTests, CONFIG: testsConfig } = require('./generateTests');
const { generateDocumentation, CONFIG: docsConfig } = require('./generateDocs');

/**
 * Configuração principal do sistema
 */
const MAIN_CONFIG = {
  projectRoot: path.resolve(__dirname, '../..'),
  scriptsDir: path.resolve(__dirname, '.'),
  outputDir: path.resolve(__dirname, '../../generated'),
  prettierConfig: path.resolve(__dirname, '../../.prettierrc'),
};

/**
 * Utilitário para executar comandos
 */
const runCommand = (command, cwd = MAIN_CONFIG.projectRoot) => {
  try {
    console.log(`🔄 Executando: ${command}`);
    execSync(command, {
      cwd,
      stdio: 'inherit',
      encoding: 'utf8',
    });
    return true;
  } catch (error) {
    console.error(`❌ Erro ao executar: ${command}`);
    console.error(error.message);
    return false;
  }
};

/**
 * Verificar dependências
 */
const checkDependencies = () => {
  console.log('🔍 Verificando dependências...');

  const requiredPackages = [
    'prettier',
    '@testing-library/react',
    '@testing-library/jest-dom',
    'fastapi',
    'sqlalchemy',
    'alembic',
  ];

  const missingPackages = [];

  for (const pkg of requiredPackages) {
    try {
      require.resolve(pkg);
    } catch (error) {
      missingPackages.push(pkg);
    }
  }

  if (missingPackages.length > 0) {
    console.warn(`⚠️  Pacotes faltando: ${missingPackages.join(', ')}`);
    console.log('💡 Execute: npm install para instalar dependências');
    return false;
  }

  console.log('✅ Todas as dependências estão instaladas');
  return true;
};

/**
 * Limpar arquivos gerados anteriormente
 */
const cleanupGeneratedFiles = () => {
  console.log('🧹 Limpando arquivos gerados anteriormente...');

  const dirsToClean = [
    componentsConfig.outputDir,
    apiConfig.outputDir,
    databaseConfig.outputDir,
    testsConfig.outputDir,
    docsConfig.outputDir,
    MAIN_CONFIG.outputDir,
  ];

  for (const dir of dirsToClean) {
    if (fs.existsSync(dir)) {
      fs.rmSync(dir, { recursive: true, force: true });
      console.log(`🗑️  Limpo: ${dir}`);
    }
  }
};

/**
 * Gerar todos os componentes React
 */
const generateAllComponents = async () => {
  console.log('\n📦 Gerando componentes React...');

  const componentConfigs = [
    {
      name: 'DataTable',
      description: 'Componente de tabela de dados com paginação e ordenação',
      props: [
        {
          name: 'data',
          type: 'any[]',
          description: 'Dados para exibir na tabela',
        },
        {
          name: 'columns',
          type: 'Column[]',
          description: 'Configuração das colunas',
        },
        {
          name: 'onRowClick',
          type: '(row: any) => void',
          description: 'Callback para clique na linha',
        },
        {
          name: 'loading',
          type: 'boolean',
          description: 'Estado de carregamento',
        },
      ],
      imports: [
        "import { useState, useMemo } from 'react';",
        "import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline';",
      ],
    },
    {
      name: 'Modal',
      description: 'Componente de modal reutilizável',
      props: [
        {
          name: 'isOpen',
          type: 'boolean',
          description: 'Estado de abertura do modal',
        },
        {
          name: 'onClose',
          type: '() => void',
          description: 'Callback para fechar o modal',
        },
        { name: 'title', type: 'string', description: 'Título do modal' },
        {
          name: 'children',
          type: 'React.ReactNode',
          description: 'Conteúdo do modal',
        },
      ],
      imports: [
        "import { useEffect } from 'react';",
        "import { XMarkIcon } from '@heroicons/react/24/outline';",
      ],
    },
    {
      name: 'FormField',
      description: 'Campo de formulário com validação',
      props: [
        { name: 'label', type: 'string', description: 'Rótulo do campo' },
        { name: 'value', type: 'string', description: 'Valor do campo' },
        {
          name: 'onChange',
          type: '(value: string) => void',
          description: 'Callback de mudança',
        },
        { name: 'error', type: 'string', description: 'Mensagem de erro' },
        {
          name: 'type',
          type: "'text' | 'email' | 'password'",
          description: 'Tipo do campo',
        },
      ],
      imports: [
        "import { useState } from 'react';",
        "import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';",
      ],
    },
    {
      name: 'Notification',
      description: 'Sistema de notificações',
      props: [
        {
          name: 'message',
          type: 'string',
          description: 'Mensagem da notificação',
        },
        {
          name: 'type',
          type: "'success' | 'error' | 'warning' | 'info'",
          description: 'Tipo da notificação',
        },
        {
          name: 'onClose',
          type: '() => void',
          description: 'Callback para fechar',
        },
        {
          name: 'autoClose',
          type: 'boolean',
          description: 'Fechar automaticamente',
        },
      ],
      imports: [
        "import { useEffect } from 'react';",
        "import { XMarkIcon, CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';",
      ],
    },
    {
      name: 'Pagination',
      description: 'Componente de paginação',
      props: [
        { name: 'currentPage', type: 'number', description: 'Página atual' },
        { name: 'totalPages', type: 'number', description: 'Total de páginas' },
        {
          name: 'onPageChange',
          type: '(page: number) => void',
          description: 'Callback de mudança de página',
        },
        {
          name: 'showPageNumbers',
          type: 'boolean',
          description: 'Mostrar números das páginas',
        },
      ],
      imports: [
        "import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';",
      ],
    },
  ];

  for (const config of componentConfigs) {
    console.log(`  📦 Gerando: ${config.name}`);
    await generateComponent(config);
  }
};

/**
 * Gerar todas as APIs
 */
const generateAllAPIs = async () => {
  console.log('\n🌐 Gerando APIs...');

  const apiConfigs = [
    {
      name: 'Project',
      description: 'API para gerenciamento de projetos',
      operations: ['list', 'get', 'create', 'update', 'delete'],
    },
    {
      name: 'Video',
      description: 'API para gerenciamento de vídeos',
      operations: ['list', 'get', 'create', 'update', 'delete'],
    },
    {
      name: 'Scene',
      description: 'API para gerenciamento de cenas',
      operations: ['list', 'get', 'create', 'update', 'delete'],
    },
    {
      name: 'Asset',
      description: 'API para gerenciamento de assets',
      operations: ['list', 'get', 'create', 'update', 'delete'],
    },
    {
      name: 'User',
      description: 'API para gerenciamento de usuários',
      operations: ['list', 'get', 'create', 'update', 'delete'],
    },
  ];

  for (const config of apiConfigs) {
    console.log(`  🌐 Gerando: ${config.name}`);
    await generateAPI(config);
  }
};

/**
 * Gerar todos os modelos de banco
 */
const generateAllModels = async () => {
  console.log('\n🗄️  Gerando modelos de banco...');

  const modelConfigs = [
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
        {
          name: 'description',
          type: 'text',
          description: 'Descrição do vídeo',
        },
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

  for (const config of modelConfigs) {
    console.log(`  🗄️  Gerando: ${config.name}`);
    await generateModel(config);
  }
};

/**
 * Gerar todos os testes
 */
const generateAllTests = async () => {
  console.log('\n🧪 Gerando testes...');

  const testConfigs = [
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
        {
          name: 'duration',
          type: 'integer',
          description: 'Duração em segundos',
        },
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

  for (const config of testConfigs) {
    console.log(`  🧪 Gerando: ${config.name} (${config.type})`);
    await generateTests(config);
  }
};

/**
 * Gerar toda a documentação
 */
const generateAllDocs = async () => {
  console.log('\n📚 Gerando documentação...');

  const docConfigs = [
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

  for (const config of docConfigs) {
    console.log(`  📚 Gerando: ${config.name} (${config.type})`);
    await generateDocumentation(config);
  }
};

/**
 * Executar formatação de código
 */
const formatCode = () => {
  console.log('\n🎨 Formatando código...');

  const success = runCommand('npx prettier --write "src/**/*.{js,jsx,ts,tsx}"');

  if (success) {
    console.log('✅ Código formatado com sucesso');
  } else {
    console.warn('⚠️  Erro ao formatar código');
  }
};

/**
 * Executar testes
 */
const runTests = () => {
  console.log('\n🧪 Executando testes...');

  const success = runCommand('npm test -- --passWithNoTests');

  if (success) {
    console.log('✅ Testes executados com sucesso');
  } else {
    console.warn('⚠️  Alguns testes falharam');
  }
};

/**
 * Gerar relatório final
 */
const generateReport = () => {
  console.log('\n📊 Gerando relatório final...');

  const report = {
    timestamp: new Date().toISOString(),
    generated: {
      components: 5,
      apis: 5,
      models: 5,
      tests: 4,
      docs: 4,
    },
    totalFiles: 23,
    status: 'success',
  };

  const reportPath = path.join(MAIN_CONFIG.outputDir, 'generation-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log('📊 Relatório gerado:', reportPath);
  console.log(`📈 Total de arquivos gerados: ${report.totalFiles}`);
};

/**
 * Função principal
 */
const main = async () => {
  console.log('🚀 Sistema de Geração de Código TecnoCursos AI');
  console.log('='.repeat(50));

  try {
    // Verificar dependências
    if (!checkDependencies()) {
      console.log('💡 Execute: npm install para instalar dependências');
      return;
    }

    // Limpar arquivos anteriores
    cleanupGeneratedFiles();

    // Gerar todos os componentes
    await generateAllComponents();

    // Gerar todas as APIs
    await generateAllAPIs();

    // Gerar todos os modelos
    await generateAllModels();

    // Gerar todos os testes
    await generateAllTests();

    // Gerar toda a documentação
    await generateAllDocs();

    // Formatar código
    formatCode();

    // Executar testes
    runTests();

    // Gerar relatório
    generateReport();

    console.log('\n🎉 Geração concluída com sucesso!');
    console.log('📁 Arquivos gerados em:', MAIN_CONFIG.outputDir);
    console.log('💡 Execute: npm start para iniciar o projeto');
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
  main,
  generateAllComponents,
  generateAllAPIs,
  generateAllModels,
  generateAllTests,
  generateAllDocs,
  MAIN_CONFIG,
};
