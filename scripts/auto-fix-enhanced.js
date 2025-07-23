#!/usr/bin/env node

/**
 * Script de Automação de Correções de Código Aprimorado
 * Implementa correções inteligentes baseadas nas melhores práticas
 *
 * Referências:
 * - https://tech.holidayextras.com/effortlessly-improve-typescript-code-with-vs-codes-eslint-autofix-813b36be7d54
 * - https://react-japan.dev/en/blog/eslint-fix-on-save
 * - https://autofix.ci/
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Iniciando automação de correções de código aprimorada...');

// Configurações
const CONFIG = {
  maxRetries: 3,
  timeout: 30000,
  allowWarnings: true,
  fixableRules: [
    'prettier/prettier',
    '@typescript-eslint/prefer-const',
    'no-var',
    'prefer-const',
    'import/order',
  ],
};

// Função para executar comandos com retry e timeout
function runCommandWithRetry(command, description, options = {}) {
  const {
    maxRetries = CONFIG.maxRetries,
    timeout = CONFIG.timeout,
    allowFailure = false,
  } = options;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(
        `\n📋 ${description} (tentativa ${attempt}/${maxRetries})...`
      );

      const result = execSync(command, {
        stdio: 'inherit',
        timeout,
        encoding: 'utf8',
      });

      console.log(`✅ ${description} concluído com sucesso`);
      return { success: true, output: result };
    } catch (error) {
      console.log(`⚠️  Tentativa ${attempt} falhou: ${error.message}`);

      if (attempt === maxRetries) {
        if (allowFailure) {
          console.log(
            `⚠️  ${description} falhou após ${maxRetries} tentativas, mas continuando...`
          );
          return { success: false, error: error.message };
        } else {
          console.error(
            `❌ ${description} falhou após ${maxRetries} tentativas`
          );
          return { success: false, error: error.message };
        }
      }

      // Aguardar antes da próxima tentativa
      const delay = Math.pow(2, attempt) * 1000;
      console.log(`⏳ Aguardando ${delay}ms antes da próxima tentativa...`);
      setTimeout(() => {}, delay);
    }
  }
}

// Função para verificar se arquivo existe
function fileExists(filePath) {
  return fs.existsSync(path.join(process.cwd(), filePath));
}

// Função para gerar relatório de qualidade
function generateQualityReport(results) {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalSteps: results.length,
      successfulSteps: results.filter(r => r.success).length,
      failedSteps: results.filter(r => !r.success).length,
      successRate: 0,
    },
    details: results,
    recommendations: [],
  };

  report.summary.successRate =
    (report.summary.successfulSteps / report.summary.totalSteps) * 100;

  // Gerar recomendações baseadas nos resultados
  if (report.summary.successRate < 50) {
    report.recommendations.push(
      '🔧 Considere executar correções manuais nos arquivos problemáticos'
    );
    report.recommendations.push(
      '📚 Revise a documentação em README_AUTOMACAO.md'
    );
  } else if (report.summary.successRate < 80) {
    report.recommendations.push(
      '⚡ Algumas correções automáticas podem ser aplicadas manualmente'
    );
    report.recommendations.push('🎯 Foque nos erros críticos primeiro');
  } else {
    report.recommendations.push('🎉 Excelente! O código está bem estruturado');
    report.recommendations.push(
      '🚀 Configure o VS Code para correções automáticas ao salvar'
    );
  }

  return report;
}

// Função para salvar relatório
function saveReport(report) {
  const reportPath = path.join(process.cwd(), 'reports', 'quality-report.json');

  // Criar diretório se não existir
  const reportDir = path.dirname(reportPath);
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }

  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`📊 Relatório salvo em: ${reportPath}`);
}

// Executar correções automáticas aprimoradas
async function autoFixEnhanced() {
  const steps = [
    {
      command: 'npm run typecheck',
      description: 'Verificação de tipos TypeScript',
      allowFailure: true,
      maxRetries: 2,
    },
    {
      command: 'npm run lint',
      description: 'Correção automática com ESLint',
      allowFailure: true,
      maxRetries: 2,
    },
    {
      command: 'npm run format',
      description: 'Formatação com Prettier',
      allowFailure: false,
      maxRetries: 1,
    },
  ];

  // Adicionar Stylelint se configurado
  if (fileExists('stylelint.config.js')) {
    steps.push({
      command: 'npm run stylelint',
      description: 'Correção automática de CSS com Stylelint',
      allowFailure: true,
      maxRetries: 2,
    });
  }

  const results = [];

  for (const step of steps) {
    const result = runCommandWithRetry(step.command, step.description, {
      maxRetries: step.maxRetries,
      allowFailure: step.allowFailure,
    });

    results.push({
      step: step.description,
      command: step.command,
      ...result,
    });
  }

  // Gerar e salvar relatório
  const report = generateQualityReport(results);
  saveReport(report);

  // Exibir resumo
  console.log(`\n📊 Resumo da Automação:`);
  console.log(
    `   ✅ Etapas bem-sucedidas: ${report.summary.successfulSteps}/${report.summary.totalSteps}`
  );
  console.log(
    `   📈 Taxa de sucesso: ${report.summary.successRate.toFixed(1)}%`
  );

  if (report.recommendations.length > 0) {
    console.log(`\n💡 Recomendações:`);
    report.recommendations.forEach(rec => console.log(`   ${rec}`));
  }

  // Determinar sucesso baseado na taxa de sucesso
  const isSuccess = report.summary.successRate >= 75;

  if (isSuccess) {
    console.log('\n🎉 Automação de correções aplicada com sucesso!');
    console.log('\n🚀 Próximos passos recomendados:');
    console.log(
      '   1. Configure o VS Code para correções automáticas ao salvar'
    );
    console.log('   2. Instale as extensões: ESLint, Prettier, Stylelint');
    console.log('   3. Configure "editor.codeActionsOnSave" no settings.json');
    console.log('   4. Configure "editor.formatOnSave": true');
    console.log('\n📚 Documentação completa: README_AUTOMACAO.md');
    console.log('📊 Relatório detalhado: reports/quality-report.json');
  } else {
    console.log(
      '\n⚠️  Algumas correções falharam. Verifique o relatório para detalhes.'
    );
    console.log(
      '💡 Dica: Execute "npm run lint" para ver detalhes dos problemas.'
    );
    process.exit(1);
  }
}

// Função para limpeza automática
function cleanup() {
  console.log('\n🧹 Executando limpeza automática...');

  const cleanupSteps = [
    'rm -rf node_modules/.cache',
    'rm -rf .eslintcache',
    'rm -rf .prettiercache',
  ];

  cleanupSteps.forEach(step => {
    try {
      execSync(step, { stdio: 'ignore' });
    } catch (error) {
      // Ignorar erros de limpeza
    }
  });

  console.log('✅ Limpeza concluída');
}

// Executar se chamado diretamente
if (require.main === module) {
  // Executar limpeza antes da automação
  cleanup();

  // Executar automação
  autoFixEnhanced().catch(error => {
    console.error('❌ Erro durante a automação:', error);
    process.exit(1);
  });
}

module.exports = {
  autoFixEnhanced,
  runCommandWithRetry,
  generateQualityReport,
  cleanup,
};
