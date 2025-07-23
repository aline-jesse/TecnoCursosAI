#!/usr/bin/env node

/**
 * Script de Automação de Correções de Código Definitivo
 * Baseado nas melhores práticas de automação de código
 *
 * Referências:
 * - https://blog.devsense.com/2024/code-fixes-auto-fix
 * - https://hackernoon.com/how-to-auto-correct-your-code-a-web-developer-guide-f12y32vn
 * - https://github.com/autofix-bot/autofix
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Iniciando automação de correções de código definitiva...');

// Configurações baseadas nas melhores práticas
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
    'no-unused-vars',
    'no-console',
  ],
  // Baseado no autofix-bot
  tiers: {
    0: ['format', 'typecheck'], // Sem rework necessário
    1: ['lint', 'stylelint'], // Algum rework pode ser necessário
    2: ['test'], // Experimental
  },
};

// Função para executar comandos com retry inteligente
function runCommandWithRetry(command, description, options = {}) {
  const {
    maxRetries = CONFIG.maxRetries,
    timeout = CONFIG.timeout,
    allowFailure = false,
    tier = 0,
  } = options;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(
        `\n📋 ${description} (tentativa ${attempt}/${maxRetries}) [Tier ${tier}]...`
      );

      const result = execSync(command, {
        stdio: 'inherit',
        timeout,
        encoding: 'utf8',
      });

      console.log(`✅ ${description} concluído com sucesso`);
      return { success: true, output: result, tier };
    } catch (error) {
      console.log(`⚠️  Tentativa ${attempt} falhou: ${error.message}`);

      if (attempt === maxRetries) {
        if (allowFailure) {
          console.log(
            `⚠️  ${description} falhou após ${maxRetries} tentativas, mas continuando...`
          );
          return { success: false, error: error.message, tier };
        } else {
          console.error(
            `❌ ${description} falhou após ${maxRetries} tentativas`
          );
          return { success: false, error: error.message, tier };
        }
      }

      // Backoff exponencial baseado no tier
      const delay = Math.pow(2, attempt + tier) * 1000;
      console.log(`⏳ Aguardando ${delay}ms antes da próxima tentativa...`);
      setTimeout(() => {}, delay);
    }
  }
}

// Função para verificar se arquivo existe
function fileExists(filePath) {
  return fs.existsSync(path.join(process.cwd(), filePath));
}

// Função para aplicar autofix inteligente baseado no autofix-bot
function applyIntelligentAutofix() {
  console.log('\n🧠 Aplicando autofix inteligente...');

  const autofixSteps = [
    // Tier 0 - Sem rework necessário
    {
      command: 'npm run format',
      description: 'Formatação automática com Prettier',
      tier: 0,
      allowFailure: false,
    },
    {
      command: 'npm run typecheck',
      description: 'Verificação de tipos TypeScript',
      tier: 0,
      allowFailure: true,
    },

    // Tier 1 - Algum rework pode ser necessário
    {
      command: 'npm run lint',
      description: 'Correção automática com ESLint',
      tier: 1,
      allowFailure: true,
    },
  ];

  // Adicionar Stylelint se configurado
  if (fileExists('stylelint.config.js')) {
    autofixSteps.push({
      command: 'npm run stylelint',
      description: 'Correção automática de CSS com Stylelint',
      tier: 1,
      allowFailure: true,
    });
  }

  return autofixSteps;
}

// Função para gerar relatório de qualidade avançado
function generateAdvancedQualityReport(results) {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalSteps: results.length,
      successfulSteps: results.filter(r => r.success).length,
      failedSteps: results.filter(r => !r.success).length,
      successRate: 0,
      tierBreakdown: {
        0: results.filter(r => r.tier === 0 && r.success).length,
        1: results.filter(r => r.tier === 1 && r.success).length,
        2: results.filter(r => r.tier === 2 && r.success).length,
      },
    },
    details: results,
    recommendations: [],
    nextSteps: [],
  };

  report.summary.successRate =
    (report.summary.successfulSteps / report.summary.totalSteps) * 100;

  // Gerar recomendações baseadas nos resultados e melhores práticas
  if (report.summary.successRate < 50) {
    report.recommendations.push(
      '🔧 Execute correções manuais nos arquivos problemáticos'
    );
    report.recommendations.push(
      '📚 Revise a documentação em README_AUTOMACAO.md'
    );
    report.recommendations.push('🎯 Foque nos erros críticos primeiro');
  } else if (report.summary.successRate < 80) {
    report.recommendations.push(
      '⚡ Algumas correções automáticas podem ser aplicadas manualmente'
    );
    report.recommendations.push('🎯 Foque nos erros críticos primeiro');
    report.recommendations.push(
      '🚀 Configure o VS Code para correções automáticas ao salvar'
    );
  } else {
    report.recommendations.push('🎉 Excelente! O código está bem estruturado');
    report.recommendations.push(
      '🚀 Configure o VS Code para correções automáticas ao salvar'
    );
    report.recommendations.push(
      '📊 Implemente monitoramento contínuo com SonarQube'
    );
  }

  // Próximos passos baseados nas melhores práticas
  report.nextSteps.push('1. Configure VS Code com extensões recomendadas');
  report.nextSteps.push('2. Implemente CI/CD com GitHub Actions');
  report.nextSteps.push('3. Configure monitoramento contínuo');
  report.nextSteps.push('4. Implemente code review automatizado');

  return report;
}

// Função para salvar relatório avançado
function saveAdvancedReport(report) {
  const reportPath = path.join(
    process.cwd(),
    'reports',
    'advanced-quality-report.json'
  );

  // Criar diretório se não existir
  const reportDir = path.dirname(reportPath);
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }

  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`📊 Relatório avançado salvo em: ${reportPath}`);
}

// Função para limpeza inteligente baseada no autofix-bot
function intelligentCleanup() {
  console.log('\n🧹 Executando limpeza inteligente...');

  const cleanupSteps = [
    'rm -rf node_modules/.cache',
    'rm -rf .eslintcache',
    'rm -rf .prettiercache',
    'rm -rf .stylelintcache',
    'rm -rf .tsbuildinfo',
  ];

  cleanupSteps.forEach(step => {
    try {
      execSync(step, { stdio: 'ignore' });
    } catch (error) {
      // Ignorar erros de limpeza
    }
  });

  console.log('✅ Limpeza inteligente concluída');
}

// Executar correções automáticas definitivas
async function autoFixUltimate() {
  // Limpeza inteligente
  intelligentCleanup();

  // Aplicar autofix inteligente
  const autofixSteps = applyIntelligentAutofix();
  const results = [];

  for (const step of autofixSteps) {
    const result = runCommandWithRetry(step.command, step.description, {
      maxRetries: step.tier === 0 ? 1 : 2,
      allowFailure: step.allowFailure,
      tier: step.tier,
    });

    results.push({
      step: step.description,
      command: step.command,
      ...result,
    });
  }

  // Gerar e salvar relatório avançado
  const report = generateAdvancedQualityReport(results);
  saveAdvancedReport(report);

  // Exibir resumo avançado
  console.log(`\n📊 Resumo da Automação Avançada:`);
  console.log(
    `   ✅ Etapas bem-sucedidas: ${report.summary.successfulSteps}/${report.summary.totalSteps}`
  );
  console.log(
    `   📈 Taxa de sucesso: ${report.summary.successRate.toFixed(1)}%`
  );
  console.log(
    `   🎯 Tier 0 (sem rework): ${report.summary.tierBreakdown[0]}/2`
  );
  console.log(
    `   🔧 Tier 1 (com rework): ${report.summary.tierBreakdown[1]}/${autofixSteps.filter(s => s.tier === 1).length}`
  );

  if (report.recommendations.length > 0) {
    console.log(`\n💡 Recomendações:`);
    report.recommendations.forEach(rec => console.log(`   ${rec}`));
  }

  if (report.nextSteps.length > 0) {
    console.log(`\n🚀 Próximos passos:`);
    report.nextSteps.forEach(step => console.log(`   ${step}`));
  }

  // Determinar sucesso baseado na taxa de sucesso e tier breakdown
  const isSuccess =
    report.summary.successRate >= 75 && report.summary.tierBreakdown[0] >= 1;

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
    console.log('📊 Relatório detalhado: reports/advanced-quality-report.json');
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

// Executar se chamado diretamente
if (require.main === module) {
  autoFixUltimate().catch(error => {
    console.error('❌ Erro durante a automação:', error);
    process.exit(1);
  });
}

module.exports = {
  autoFixUltimate,
  runCommandWithRetry,
  generateAdvancedQualityReport,
  intelligentCleanup,
  applyIntelligentAutofix,
};
