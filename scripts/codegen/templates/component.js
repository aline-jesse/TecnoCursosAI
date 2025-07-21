/**
 * Template Base para Componentes React
 * TecnoCursos AI - Component Template
 */

const componentTemplate = (componentName, props = [], imports = []) => {
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
 * 
 * @param props - Propriedades do componente
 * @returns JSX.Element
 */
const ${componentName}: React.FC<${props.length > 0 ? `${componentName}Props` : '{}'}> = (${propsDestructuring}) => {
  // Estados locais
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // Handlers
  const handleClick = React.useCallback(() => {
    console.log('${componentName} clicked');
  }, []);

  // Effects
  React.useEffect(() => {
    // Inicialização do componente
    return () => {
      // Cleanup
    };
  }, []);

  // Renderização condicional
  if (isLoading) {
    return (
      <div className="${componentName.toLowerCase()}-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="${componentName.toLowerCase()}-error">
        <p className="text-error-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="${componentName.toLowerCase()}-container">
      <h3 className="${componentName.toLowerCase()}-title">${componentName}</h3>
      <div className="${componentName.toLowerCase()}-content">
        {/* Conteúdo do componente */}
        <button 
          onClick={handleClick}
          className="${componentName.toLowerCase()}-button"
        >
          Clique aqui
        </button>
      </div>
    </div>
  );
};

export default ${componentName};`;
};

const cssTemplate = (componentName) => {
  return `.${componentName.toLowerCase()}-container {
  @apply p-4 border border-gray-200 rounded-lg bg-white shadow-soft;
}

.${componentName.toLowerCase()}-title {
  @apply text-lg font-semibold text-gray-900 mb-3;
}

.${componentName.toLowerCase()}-content {
  @apply space-y-2;
}

.${componentName.toLowerCase()}-button {
  @apply px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 
         focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 
         transition-colors duration-200;
}

.${componentName.toLowerCase()}-loading {
  @apply flex items-center justify-center p-4;
}

.${componentName.toLowerCase()}-error {
  @apply p-4 bg-error-50 border border-error-200 rounded-lg;
}

/* Responsividade */
@media (max-width: 768px) {
  .${componentName.toLowerCase()}-container {
    @apply p-3;
  }
  
  .${componentName.toLowerCase()}-title {
    @apply text-base;
  }
}`;
};

const testTemplate = (componentName) => {
  return `import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ${componentName} from '../${componentName}';

describe('${componentName} Component', () => {
  beforeEach(() => {
    // Setup antes de cada teste
  });

  afterEach(() => {
    // Cleanup após cada teste
  });

  test('renderiza o componente corretamente', () => {
    render(<${componentName} />);
    expect(screen.getByText('${componentName}')).toBeInTheDocument();
  });

  test('aplica classes CSS corretas', () => {
    render(<${componentName} />);
    const container = screen.getByText('${componentName}').parentElement;
    expect(container).toHaveClass('${componentName.toLowerCase()}-container');
  });

  test('executa ação ao clicar no botão', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    render(<${componentName} />);
    
    const button = screen.getByText('Clique aqui');
    fireEvent.click(button);
    
    expect(consoleSpy).toHaveBeenCalledWith('${componentName} clicked');
    consoleSpy.mockRestore();
  });

  test('testa acessibilidade', () => {
    render(<${componentName} />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  test('renderiza estado de loading', () => {
    // Mock do estado de loading
    jest.spyOn(React, 'useState').mockImplementation(() => [true, jest.fn()]);
    
    render(<${componentName} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('renderiza estado de erro', () => {
    // Mock do estado de erro
    jest.spyOn(React, 'useState').mockImplementation(() => ['Erro teste', jest.fn()]);
    
    render(<${componentName} />);
    expect(screen.getByText('Erro teste')).toBeInTheDocument();
  });
});`;
};

const storyTemplate = (componentName) => {
  return `import type { Meta, StoryObj } from '@storybook/react';
import ${componentName} from './${componentName}';

const meta: Meta<typeof ${componentName}> = {
  title: 'Components/${componentName}',
  component: ${componentName},
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    // Definição dos controles do Storybook
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    // Props padrão
  },
};

export const Loading: Story = {
  args: {
    // Props para estado de loading
  },
};

export const Error: Story = {
  args: {
    // Props para estado de erro
  },
};`;
};

module.exports = {
  componentTemplate,
  cssTemplate,
  testTemplate,
  storyTemplate,
}; 