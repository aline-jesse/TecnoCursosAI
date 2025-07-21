#!/usr/bin/env node

/**
 * Sistema de Geração de Código para Componentes React
 * TecnoCursos AI - Code Generation System
 * 
 * Baseado nas melhores práticas de code generation:
 * - Geração determinística de código
 * - Templates reutilizáveis
 * - Integração com TypeScript
 * - Documentação automática
 */

const fs = require('fs');
const path = require('path');
const prettier = require('prettier');

/**
 * Configuração do sistema de geração
 */
const CONFIG = {
  componentsDir: path.resolve(__dirname, '../../src/components'),
  templatesDir: path.resolve(__dirname, './templates'),
  outputDir: path.resolve(__dirname, '../../src/components/generated'),
  prettierConfig: path.resolve(__dirname, '../../.prettierrc')
};

/**
 * Utilitário para criar arquivos TypeScript/React
 */
const createTsFile = async (params) => {
  const {
    directory,
    fileName,
    content,
    extension = 'tsx',
    generatedBy
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
        parser: extension === 'tsx' ? 'typescript' : extension === 'css' ? 'css' : 'typescript'
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
 * Template para componentes React
 */
const generateReactComponent = (componentName, props = [], imports = []) => {
  const propsInterface = props.length > 0 
    ? `interface ${componentName}Props {\n  ${props.map(p => `${p.name}: ${p.type}`).join('\n  ')}\n}`
    : '';

  const propsDestructuring = props.length > 0 
    ? `{ ${props.map(p => p.name).join(', ') } }: ${componentName}Props`
    : '';

  return `import React from 'react';
import './${componentName}.css';

${imports.join('\n')}

${propsInterface}

/**
 * Componente ${componentName}
 * Gerado automaticamente pelo sistema de code generation
 */
const ${componentName}: React.FC<${props.length > 0 ? `${componentName}Props` : '{}'}> = (${propsDestructuring}) => {
  return (
    <div className="${componentName.toLowerCase()}-container">
      <h3>${componentName}</h3>
      {/* Conteúdo do componente */}
    </div>
  );
};

export default ${componentName};`;
};

/**
 * Template para arquivos CSS
 */
const generateCSS = (componentName) => {
  return `.${componentName.toLowerCase()}-container {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
}

.${componentName.toLowerCase()}-container h3 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 18px;
  font-weight: 600;
}`;
};

/**
 * Template para testes unitários
 */
const generateTest = (componentName) => {
  return `import React from 'react';
import { render, screen } from '@testing-library/react';
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
});`;
};

/**
 * Gerador de componentes baseado em configuração
 */
const generateComponent = async (config) => {
  const {
    name,
    props = [],
    imports = [],
    description = ''
  } = config;

  const componentDir = path.join(CONFIG.outputDir, name);
  
  // Gerar componente principal
  await createTsFile({
    directory: componentDir,
    fileName: name,
    content: generateReactComponent(name, props, imports),
    extension: 'tsx',
    generatedBy: 'scripts/codegen/generateComponents.js'
  });

  // Gerar CSS
  await createTsFile({
    directory: componentDir,
    fileName: name,
    content: generateCSS(name),
    extension: 'css',
    generatedBy: 'scripts/codegen/generateComponents.js'
  });

  // Gerar teste
  await createTsFile({
    directory: path.join(componentDir, '__tests__'),
    fileName: `${name}.test`,
    content: generateTest(name),
    extension: 'tsx',
    generatedBy: 'scripts/codegen/generateComponents.js'
  });

  // Gerar README
  const readmeContent = `# ${name}

${description}

## Props

${props.length > 0 ? props.map(p => `- \`${p.name}\` (${p.type}): ${p.description || 'Sem descrição'}`).join('\n') : 'Este componente não aceita props.'}

## Uso

\`\`\`tsx
import ${name} from './${name}';

<${name} ${props.map(p => `${p.name}={value}`).join(' ')} />
\`\`\`

## Testes

Execute os testes com:

\`\`\`bash
npm test -- --testPathPattern=${name}.test.tsx
\`\`\`

---

*Este componente foi gerado automaticamente pelo sistema de code generation.*`;

  await createTsFile({
    directory: componentDir,
    fileName: 'README',
    content: readmeContent,
    extension: 'md',
    generatedBy: 'scripts/codegen/generateComponents.js'
  });
};

/**
 * Configurações de componentes para gerar
 */
const COMPONENT_CONFIGS = [
  {
    name: 'DataTable',
    description: 'Componente de tabela de dados com paginação e ordenação',
    props: [
      { name: 'data', type: 'any[]', description: 'Dados para exibir na tabela' },
      { name: 'columns', type: 'Column[]', description: 'Configuração das colunas' },
      { name: 'onRowClick', type: '(row: any) => void', description: 'Callback para clique na linha' },
      { name: 'loading', type: 'boolean', description: 'Estado de carregamento' }
    ],
    imports: [
      'import { useState, useMemo } from \'react\';',
      'import { ChevronUpIcon, ChevronDownIcon } from \'@heroicons/react/24/outline\';'
    ]
  },
  {
    name: 'Modal',
    description: 'Componente de modal reutilizável',
    props: [
      { name: 'isOpen', type: 'boolean', description: 'Estado de abertura do modal' },
      { name: 'onClose', type: '() => void', description: 'Callback para fechar o modal' },
      { name: 'title', type: 'string', description: 'Título do modal' },
      { name: 'children', type: 'React.ReactNode', description: 'Conteúdo do modal' }
    ],
    imports: [
      'import { useEffect } from \'react\';',
      'import { XMarkIcon } from \'@heroicons/react/24/outline\';'
    ]
  },
  {
    name: 'FormField',
    description: 'Campo de formulário com validação',
    props: [
      { name: 'label', type: 'string', description: 'Rótulo do campo' },
      { name: 'value', type: 'string', description: 'Valor do campo' },
      { name: 'onChange', type: '(value: string) => void', description: 'Callback de mudança' },
      { name: 'error', type: 'string', description: 'Mensagem de erro' },
      { name: 'type', type: '\'text\' | \'email\' | \'password\'', description: 'Tipo do campo' }
    ],
    imports: [
      'import { useState } from \'react\';',
      'import { EyeIcon, EyeSlashIcon } from \'@heroicons/react/24/outline\';'
    ]
  },
  {
    name: 'Notification',
    description: 'Sistema de notificações',
    props: [
      { name: 'message', type: 'string', description: 'Mensagem da notificação' },
      { name: 'type', type: '\'success\' | \'error\' | \'warning\' | \'info\'', description: 'Tipo da notificação' },
      { name: 'onClose', type: '() => void', description: 'Callback para fechar' },
      { name: 'autoClose', type: 'boolean', description: 'Fechar automaticamente' }
    ],
    imports: [
      'import { useEffect } from \'react\';',
      'import { XMarkIcon, CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from \'@heroicons/react/24/outline\';'
    ]
  },
  {
    name: 'Pagination',
    description: 'Componente de paginação',
    props: [
      { name: 'currentPage', type: 'number', description: 'Página atual' },
      { name: 'totalPages', type: 'number', description: 'Total de páginas' },
      { name: 'onPageChange', type: '(page: number) => void', description: 'Callback de mudança de página' },
      { name: 'showPageNumbers', type: 'boolean', description: 'Mostrar números das páginas' }
    ],
    imports: [
      'import { ChevronLeftIcon, ChevronRightIcon } from \'@heroicons/react/24/outline\';'
    ]
  }
];

/**
 * Função principal de geração
 */
const main = async () => {
  console.log('🚀 Iniciando geração de componentes...');
  
  try {
    // Criar diretório de saída
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    
    // Gerar cada componente
    for (const config of COMPONENT_CONFIGS) {
      console.log(`📦 Gerando componente: ${config.name}`);
      await generateComponent(config);
    }
    
    // Gerar arquivo de índice
    const indexContent = COMPONENT_CONFIGS.map(config => 
      `export { default as ${config.name} } from './${config.name}/${config.name}';`
    ).join('\n');
    
    await createTsFile({
      directory: CONFIG.outputDir,
      fileName: 'index',
      content: indexContent,
      extension: 'ts',
      generatedBy: 'scripts/codegen/generateComponents.js'
    });
    
    console.log('✅ Geração concluída com sucesso!');
    console.log(`📁 Componentes gerados em: ${CONFIG.outputDir}`);
    
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
  generateComponent,
  createTsFile,
  CONFIG
}; 