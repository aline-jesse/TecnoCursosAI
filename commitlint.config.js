module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // Nova funcionalidade
        'fix',      // Correção de bug
        'docs',     // Documentação
        'style',    // Formatação
        'refactor', // Refatoração
        'perf',     // Performance
        'test',     // Testes
        'build',    // Build system
        'ci',       // CI/CD
        'chore',    // Manutenção
        'revert'    // Reverter commit
      ]
    ],
    'type-case': [2, 'always', 'lower'],
    'type-empty': [2, 'never'],
    'subject-case': [2, 'always', 'lower'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'header-max-length': [2, 'always', 72],
    'body-leading-blank': [2, 'always'],
    'body-max-line-length': [2, 'always', 100],
    'footer-leading-blank': [2, 'always'],
    'footer-max-line-length': [2, 'always', 100],
    'scope-enum': [
      2,
      'always',
      [
        'api',        // API endpoints
        'auth',       // Autenticação
        'ui',         // Interface do usuário
        'video',      // Geração de vídeo
        'tts',        // Text-to-Speech
        'upload',     // Upload de arquivos
        'db',         // Banco de dados
        'test',       // Testes
        'docs',       // Documentação
        'deps',       // Dependências
        'ci',         // CI/CD
        'build',      // Build
        'release',    // Release
        'security',   // Segurança
        'performance' // Performance
      ]
    ]
  },
  parserPreset: {
    parserOpts: {
      issuePrefixes: ['#']
    }
  }
}; 