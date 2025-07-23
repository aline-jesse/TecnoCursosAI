#!/usr/bin/env node

/**
 * Script de Automação de Correções de Código
 * Baseado nas melhores práticas de ESLint fix-on-save
 *
 * Referências:
 * - https://tech.holidayextras.com/effortlessly-improve-typescript-code-with-vs-codes-eslint-autofix-813b36be7d54
 * - https://react-japan.dev/en/blog/eslint-fix-on-save
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Iniciando automação de correções de código...');

// Função para executar comandos com tratamento de erro
function runCommand(command, description, allowFailure = false) {
  try {
    console.log(`\n📋 ${description}...`);
    execSync(command, { stdio: 'inherit' });
    console.log(`✅ ${description} concluído com sucesso`);
    return true;
  } catch (error) {
    if (allowFailure) {
      console.log(`⚠️  ${description} falhou, mas continuando...`);
      return false;
    } else {
      console.error(`❌ Erro em ${description}:`, error.message);
      return false;
    }
  }
}

// Função para verificar se arquivo existe
function fileExists(filePath) {
  return fs.existsSync(path.join(process.cwd(), filePath));
}

// Executar correções automáticas
async function autoFix() {
  const steps = [
    {
      command: 'npm run typecheck',
      description: 'Verificação de tipos TypeScript',
      allowFailure: true,
    },
    {
      command: 'npm run lint',
      description: 'Correção automática com ESLint',
      allowFailure: true,
    },
    {
      command: 'npm run format',
      description: 'Formatação com Prettier',
      allowFailure: false,
    },
  ];

  // Adicionar Stylelint se configurado
  if (fileExists('stylelint.config.js')) {
    steps.push({
      command: 'npm run stylelint',
      description: 'Correção automática de CSS com Stylelint',
      allowFailure: true,
    });
  }

  let successCount = 0;
  const totalSteps = steps.length;

  for (const step of steps) {
    if (runCommand(step.command, step.description, step.allowFailure)) {
      successCount++;
    }
  }

  console.log(
    `\n📊 Resumo: ${successCount}/${totalSteps} etapas concluídas com sucesso`
  );

  if (successCount >= totalSteps - 1) {
    // Permitir 1 falha
    console.log('🎉 Automação de correções aplicada com sucesso!');
    console.log('\n💡 Próximos passos recomendados:');
    console.log(
      '   1. Configure o VS Code para correções automáticas ao salvar'
    );
    console.log('   2. Instale as extensões: ESLint, Prettier, Stylelint');
    console.log('   3. Configure "editor.codeActionsOnSave" no settings.json');
    console.log('   4. Configure "editor.formatOnSave": true');
    console.log('\n📚 Documentação completa: README_AUTOMACAO.md');
  } else {
    console.log('⚠️  Algumas correções falharam. Verifique os erros acima.');
    console.log(
      '💡 Dica: Execute "npm run lint" para ver detalhes dos problemas.'
    );
    process.exit(1);
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  autoFix();
}

module.exports = { autoFix, runCommand };
