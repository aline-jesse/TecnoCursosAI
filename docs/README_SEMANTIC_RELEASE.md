# 🚀 Semantic Release - TecnoCursos AI

## 📋 Visão Geral

O sistema de Semantic Release foi implementado para automatizar completamente o processo de versionamento e releases do projeto TecnoCursos AI. Este sistema garante versionamento consistente, geração automática de changelogs e integração perfeita com o pipeline CI/CD.

## ✨ Funcionalidades Implementadas

### 🔄 **Versionamento Automático**
- Análise inteligente de commits convencionais
- Determinação automática do tipo de release (MAJOR/MINOR/PATCH)
- Geração automática de tags Git
- Atualização automática de arquivos de versão

### 📝 **Changelog Automático**
- Geração automática de CHANGELOG.md
- Categorização inteligente de mudanças
- Suporte a emojis e formatação rica
- Histórico completo de releases

### 🔧 **Integração CI/CD**
- Workflow GitHub Actions automatizado
- Validação de commits antes do release
- Deploy automático após release
- Notificações integradas

### 🛡️ **Qualidade de Código**
- Validação de commits convencionais
- Linting e formatação automática
- Testes obrigatórios antes do release
- Análise de breaking changes

## 🚀 Como Usar

### **1. Instalação das Dependências**

```bash
# Instalar dependências do semantic release
npm install

# Configurar husky para hooks
npm run prepare
```

### **2. Fazer Commits Convencionais**

```bash
# Usar commitizen para commits padronizados
npm run commit

# Ou fazer commits manuais seguindo a convenção:
git commit -m "feat(api): adicionar endpoint de upload de vídeo"
git commit -m "fix(ui): corrigir bug no drag and drop"
git commit -m "docs(readme): atualizar documentação"
```

### **3. Executar Release**

```bash
# Preview do release (dry-run)
npm run release

# Release específico
npm run release:patch  # 0.1.0 → 0.1.1
npm run release:minor  # 0.1.0 → 0.2.0
npm run release:major  # 0.1.0 → 1.0.0

# Release automático (apenas na branch main)
npm run semantic-release
```

### **4. Script Personalizado**

```bash
# Usar script personalizado com análise avançada
node scripts/semantic-release.js
```

## 📊 Tipos de Commits Suportados

| Tipo | Descrição | Release |
|------|-----------|---------|
| `feat` | Nova funcionalidade | MINOR |
| `fix` | Correção de bug | PATCH |
| `docs` | Documentação | PATCH |
| `style` | Formatação | PATCH |
| `refactor` | Refatoração | PATCH |
| `perf` | Performance | PATCH |
| `test` | Testes | PATCH |
| `build` | Build system | PATCH |
| `ci` | CI/CD | PATCH |
| `chore` | Manutenção | PATCH |

### **Scopes Disponíveis**

- `api` - Endpoints da API
- `auth` - Autenticação
- `ui` - Interface do usuário
- `video` - Geração de vídeo
- `tts` - Text-to-Speech
- `upload` - Upload de arquivos
- `db` - Banco de dados
- `test` - Testes
- `docs` - Documentação
- `deps` - Dependências
- `ci` - CI/CD
- `build` - Build
- `release` - Release
- `security` - Segurança
- `performance` - Performance

## 🔧 Configuração

### **Arquivo .releaserc.json**

```json
{
  "branches": [
    "main",
    {
      "name": "develop",
      "prerelease": "beta"
    },
    {
      "name": "staging",
      "prerelease": "alpha"
    }
  ],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github",
    "@semantic-release/git"
  ]
}
```

### **Arquivo commitlint.config.js**

```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert']],
    'scope-enum': [2, 'always', ['api', 'auth', 'ui', 'video', 'tts', 'upload', 'db', 'test', 'docs', 'deps', 'ci', 'build', 'release', 'security', 'performance']]
  }
};
```

## 🔄 Workflow Automático

### **1. Validação de Commits**
```yaml
validate-commits:
  - Checkout código
  - Validar commits com commitlint
  - Verificar formatação
  - Executar linting
```

### **2. Semantic Release**
```yaml
semantic-release:
  - Analisar commits
  - Determinar tipo de release
  - Gerar changelog
  - Criar tag Git
  - Publicar no GitHub
```

### **3. Deploy Automático**
```yaml
auto-deploy:
  - Deploy para produção
  - Health check
  - Atualizar métricas
```

## 📈 Relatórios e Métricas

### **Análise de Commits**
```javascript
{
  "total": 15,
  "features": 3,
  "fixes": 8,
  "breaking": 0,
  "types": {
    "feat": 3,
    "fix": 8,
    "docs": 2,
    "test": 2
  }
}
```

### **Relatório de Release**
```javascript
{
  "timestamp": "2025-01-17T10:30:00Z",
  "project": "TecnoCursos AI",
  "releaseType": "minor",
  "analysis": { /* análise de commits */ },
  "summary": {
    "totalCommits": 15,
    "newFeatures": 3,
    "bugFixes": 8,
    "breakingChanges": 0,
    "recommendation": "✨ Release MINOR - Novas funcionalidades adicionadas."
  }
}
```

## 🛠️ Scripts Disponíveis

### **Package.json Scripts**
```json
{
  "semantic-release": "semantic-release",
  "release": "semantic-release --dry-run",
  "release:patch": "semantic-release --dry-run --release-as patch",
  "release:minor": "semantic-release --dry-run --release-as minor",
  "release:major": "semantic-release --dry-run --release-as major",
  "changelog": "conventional-changelog -p angular -i CHANGELOG.md -s",
  "commit": "git-cz",
  "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
  "format": "prettier --write \"src/**/*.{js,jsx,ts,tsx,json,css,md}\""
}
```

## 🔍 Troubleshooting

### **Problemas Comuns**

1. **Commit rejeitado**
   ```bash
   # Verificar formato do commit
   npx commitlint --from HEAD~1 --to HEAD --verbose
   ```

2. **Release não executado**
   ```bash
   # Verificar se há commits para release
   git log --oneline $(git describe --tags --abbrev=0)..HEAD
   ```

3. **Erro de permissão**
   ```bash
   # Verificar permissões do GitHub Token
   # Garantir que o token tem permissões de write
   ```

### **Debug Mode**
```bash
# Ativar debug do semantic-release
DEBUG=semantic-release:* npm run semantic-release
```

## 📚 Recursos Adicionais

### **Documentação Oficial**
- [Semantic Release](https://semantic-release.gitbook.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Commitizen](https://github.com/commitizen/cz-cli)

### **Ferramentas Relacionadas**
- [Commitlint](https://commitlint.js.org/)
- [Husky](https://typicode.github.io/husky/)
- [Lint-staged](https://github.com/okonet/lint-staged)
- [Prettier](https://prettier.io/)

## 🎯 Próximos Passos

### **Melhorias Planejadas**
1. **Integração com Slack** - Notificações automáticas
2. **Análise de Performance** - Métricas de impacto
3. **Rollback Automático** - Em caso de falha
4. **Multi-ambiente** - Releases para diferentes ambientes
5. **Analytics** - Métricas detalhadas de releases

### **Configurações Avançadas**
1. **Pré-releases** - Alpha/Beta releases
2. **Hotfixes** - Releases de emergência
3. **Changelog Customizado** - Templates personalizados
4. **Integração Externa** - Jira, Trello, etc.

---

## 🎉 Conclusão

O sistema de Semantic Release está completamente implementado e funcionando. Ele garante:

- ✅ **Versionamento consistente** e automático
- ✅ **Changelog sempre atualizado**
- ✅ **Qualidade de código** mantida
- ✅ **Deploy automatizado** e seguro
- ✅ **Transparência total** do processo

**O projeto TecnoCursos AI agora possui um sistema de release enterprise-grade! 🚀** 