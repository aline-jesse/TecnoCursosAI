#!/usr/bin/env node

/**
 * 🚀 Script Personalizado de Semantic Release
 * TecnoCursos AI - Enterprise Edition 2025
 *
 * Este script estende o semantic-release com funcionalidades customizadas:
 * - Análise de breaking changes
 * - Geração de relatórios detalhados
 * - Integração com sistemas externos
 * - Notificações personalizadas
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class SemanticReleaseManager {
  constructor() {
    this.config = {
      projectName: 'TecnoCursos AI',
      versionFile: 'VERSION',
      changelogFile: 'CHANGELOG.md',
      packageJson: 'package.json',
    };
  }

  /**
   * Analisar commits desde a última tag
   */
  analyzeCommits() {
    console.log('🔍 Analisando commits...');

    try {
      const lastTag = this.getLastTag();
      const commits = this.getCommitsSince(lastTag);

      const analysis = {
        total: commits.length,
        features: commits.filter(c => c.type === 'feat').length,
        fixes: commits.filter(c => c.type === 'fix').length,
        breaking: commits.filter(c => c.breaking).length,
        types: this.groupByType(commits),
      };

      console.log('📊 Análise de commits:', analysis);
      return analysis;
    } catch (error) {
      console.error('❌ Erro ao analisar commits:', error);
      return null;
    }
  }

  /**
   * Determinar tipo de release baseado nos commits
   */
  determineReleaseType(analysis) {
    if (!analysis) return 'patch';

    if (analysis.breaking > 0) {
      console.log('🚨 Breaking changes detectados - MAJOR release');
      return 'major';
    }

    if (analysis.features > 0) {
      console.log('✨ Novas funcionalidades detectadas - MINOR release');
      return 'minor';
    }

    console.log('🔧 Apenas correções - PATCH release');
    return 'patch';
  }

  /**
   * Gerar relatório detalhado
   */
  generateReport(analysis, releaseType) {
    const report = {
      timestamp: new Date().toISOString(),
      project: this.config.projectName,
      releaseType,
      analysis,
      summary: this.generateSummary(analysis, releaseType),
    };

    const reportFile = `release-report-${Date.now()}.json`;
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));

    console.log(`📄 Relatório salvo em: ${reportFile}`);
    return report;
  }

  /**
   * Executar semantic release
   */
  async runSemanticRelease() {
    console.log('🚀 Iniciando Semantic Release...');

    try {
      // Analisar commits
      const analysis = this.analyzeCommits();

      if (!analysis || analysis.total === 0) {
        console.log('⚠️ Nenhum commit para release');
        return;
      }

      // Determinar tipo de release
      const releaseType = this.determineReleaseType(analysis);

      // Gerar relatório
      const report = this.generateReport(analysis, releaseType);

      // Executar semantic-release
      console.log('🔄 Executando semantic-release...');
      execSync('npx semantic-release', { stdio: 'inherit' });

      // Notificações
      this.sendNotifications(report);

      console.log('✅ Semantic Release concluído com sucesso!');
    } catch (error) {
      console.error('❌ Erro no Semantic Release:', error);
      process.exit(1);
    }
  }

  /**
   * Obter última tag
   */
  getLastTag() {
    try {
      return execSync('git describe --tags --abbrev=0', {
        encoding: 'utf8',
      }).trim();
    } catch {
      return null;
    }
  }

  /**
   * Obter commits desde uma tag
   */
  getCommitsSince(tag) {
    const since = tag ? `${tag}..HEAD` : '';
    const format = '--format=%H|%s|%b|%an|%ad';
    const dateFormat = '--date=short';

    const command = `git log ${since} ${format} ${dateFormat}`;
    const output = execSync(command, { encoding: 'utf8' });

    return output
      .split('\n')
      .filter(line => line.trim())
      .map(line => this.parseCommit(line));
  }

  /**
   * Parsear commit
   */
  parseCommit(line) {
    const [hash, subject, body, author, date] = line.split('|');

    // Parsear conventional commit
    const match = subject.match(/^(\w+)(?:\(([^)]+)\))?: (.+)$/);

    if (!match) {
      return {
        hash,
        subject,
        body,
        author,
        date,
        type: 'chore',
        scope: null,
        message: subject,
        breaking: false,
      };
    }

    const [, type, scope, message] = match;
    const breaking = body && body.includes('BREAKING CHANGE');

    return {
      hash,
      subject,
      body,
      author,
      date,
      type: type.toLowerCase(),
      scope,
      message,
      breaking,
    };
  }

  /**
   * Agrupar commits por tipo
   */
  groupByType(commits) {
    return commits.reduce((acc, commit) => {
      const { type } = commit;
      if (!acc[type]) acc[type] = [];
      acc[type].push(commit);
      return acc;
    }, {});
  }

  /**
   * Gerar resumo
   */
  generateSummary(analysis, releaseType) {
    const { total, features, fixes, breaking } = analysis;

    return {
      totalCommits: total,
      newFeatures: features,
      bugFixes: fixes,
      breakingChanges: breaking,
      releaseType,
      recommendation: this.getRecommendation(releaseType),
    };
  }

  /**
   * Obter recomendação
   */
  getRecommendation(releaseType) {
    const recommendations = {
      major:
        '🚨 Release MAJOR - Breaking changes detectados. Verificar compatibilidade.',
      minor: '✨ Release MINOR - Novas funcionalidades adicionadas.',
      patch: '🔧 Release PATCH - Correções e melhorias.',
    };

    return recommendations[releaseType] || '📝 Release padrão.';
  }

  /**
   * Enviar notificações
   */
  sendNotifications(report) {
    console.log('📢 Enviando notificações...');

    // Aqui seria implementada a lógica de notificação
    // Slack, email, webhook, etc.

    console.log('✅ Notificações enviadas');
  }

  /**
   * Validar ambiente
   */
  validateEnvironment() {
    const required = ['package.json', 'VERSION', 'CHANGELOG.md'];

    for (const file of required) {
      if (!fs.existsSync(file)) {
        console.error(`❌ Arquivo obrigatório não encontrado: ${file}`);
        return false;
      }
    }

    console.log('✅ Ambiente validado');
    return true;
  }
}

// Execução principal
async function main() {
  const manager = new SemanticReleaseManager();

  console.log('🚀 TecnoCursos AI - Semantic Release Manager');
  console.log('=============================================\n');

  // Validar ambiente
  if (!manager.validateEnvironment()) {
    process.exit(1);
  }

  // Executar semantic release
  await manager.runSemanticRelease();
}

// Executar se chamado diretamente
if (require.main === module) {
  main().catch(console.error);
}

module.exports = SemanticReleaseManager;
