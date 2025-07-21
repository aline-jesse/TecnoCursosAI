# Regras do Cursor - TecnoCursos AI

Este diretório contém as regras personalizadas do Cursor AI para o projeto TecnoCursos AI, um sistema SaaS completo para geração de vídeos educacionais com IA.

## 📋 Regras Disponíveis

### 1. **project-structure.mdc** - Estrutura Geral do Projeto
- **Aplicação**: Sempre ativa
- **Descrição**: Visão geral da arquitetura, arquivos principais e padrões de desenvolvimento
- **Arquivos**: Todos os arquivos do projeto
- **Conteúdo**: Estrutura backend (FastAPI), frontend (React), configurações e diretórios principais

### 2. **backend-patterns.mdc** - Padrões Backend
- **Aplicação**: Arquivos Python (`app/**/*.py`, `*.py`)
- **Descrição**: Convenções de código para desenvolvimento backend com FastAPI
- **Conteúdo**: 
  - Estrutura de imports
  - Padrões de endpoints
  - Modelos SQLAlchemy
  - Schemas Pydantic
  - Tratamento de erros
  - Autenticação JWT
  - Banco de dados

### 3. **frontend-patterns.mdc** - Padrões Frontend
- **Aplicação**: Arquivos React/TypeScript (`src/**/*.{js,jsx,ts,tsx}`)
- **Descrição**: Convenções de código para desenvolvimento frontend com React
- **Conteúdo**:
  - Estrutura de componentes
  - Custom hooks
  - Store Zustand
  - Estilização TailwindCSS
  - Tratamento de erros
  - Performance e testes

### 4. **api-integration.mdc** - Integração Frontend-Backend
- **Aplicação**: Serviços de API (`src/services/*.{js,ts}`, `app/routers/*.py`)
- **Descrição**: Padrões para integração entre frontend e backend
- **Conteúdo**:
  - Padrões de API REST
  - Autenticação JWT
  - Tratamento de erros
  - WebSocket integration
  - Upload de arquivos

### 5. **testing-patterns.mdc** - Padrões de Testes
- **Aplicação**: Arquivos de teste (`tests/**/*.py`, `src/**/*.test.{js,jsx,ts,tsx}`, `**/*test*.py`)
- **Descrição**: Padrões para testes backend e frontend
- **Conteúdo**:
  - Testes backend com Pytest
  - Testes frontend com Jest/React Testing Library
  - Testes de integração
  - Cobertura de testes
  - Mock e fixtures

### 6. **deployment-patterns.mdc** - Padrões de Deploy
- **Aplicação**: Arquivos de deploy (`docker-compose.yml`, `Dockerfile*`, `deploy/*`, `k8s/*`, `terraform/*`)
- **Descrição**: Padrões para deploy e produção
- **Conteúdo**:
  - Configuração Docker
  - Docker Compose
  - Kubernetes
  - Terraform
  - CI/CD Pipeline
  - Monitoramento
  - Variáveis de ambiente

### 7. **security-patterns.mdc** - Padrões de Segurança
- **Aplicação**: Arquivos de segurança (`app/security/*.py`, `app/auth.py`, `app/middleware/*.py`)
- **Descrição**: Padrões de segurança e proteção
- **Conteúdo**:
  - Autenticação e autorização JWT
  - Rate limiting
  - Validação de dados
  - Sanitização de inputs
  - CORS e headers de segurança
  - Logging de segurança
  - Criptografia e hashing
  - Auditoria e compliance
  - Proteção contra ataques comuns

## 🚀 Como Usar

### Para Desenvolvedores
1. As regras são aplicadas automaticamente pelo Cursor AI
2. Regras específicas se aplicam aos arquivos correspondentes
3. A regra `project-structure.mdc` é sempre aplicada para contexto geral

### Para Novos Desenvolvedores
1. Leia `project-structure.mdc` para entender a arquitetura
2. Consulte as regras específicas para cada área de desenvolvimento
3. Siga os padrões estabelecidos para manter consistência

### Para Manutenção
1. Atualize as regras conforme o projeto evolui
2. Adicione novas regras para novas tecnologias ou padrões
3. Mantenha as regras sincronizadas com as melhores práticas do projeto

## 📁 Estrutura de Arquivos

```
.cursor/rules/
├── README.md                    # Este arquivo
├── project-structure.mdc        # Estrutura geral do projeto
├── backend-patterns.mdc         # Padrões backend (FastAPI)
├── frontend-patterns.mdc        # Padrões frontend (React)
├── api-integration.mdc          # Integração frontend-backend
├── testing-patterns.mdc         # Padrões de testes
├── deployment-patterns.mdc      # Padrões de deploy
└── security-patterns.mdc        # Padrões de segurança
```

## 🔧 Tecnologias Principais

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados
- **JWT**: Autenticação com tokens
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e sessões

### Frontend
- **React 18**: Framework frontend
- **TypeScript**: Tipagem estática
- **TailwindCSS**: Framework CSS
- **Zustand**: Gerenciamento de estado
- **Axios**: Cliente HTTP
- **React Router**: Roteamento

### DevOps
- **Docker**: Containerização
- **Kubernetes**: Orquestração
- **Terraform**: Infraestrutura como código
- **GitHub Actions**: CI/CD
- **Prometheus/Grafana**: Monitoramento

## 📊 Métricas de Qualidade

### Cobertura de Testes
- **Backend**: Mínimo 80% de cobertura
- **Frontend**: Mínimo 70% de cobertura
- **Integração**: Testes E2E obrigatórios

### Performance
- **Backend**: Response time < 200ms (95th percentile)
- **Frontend**: First Contentful Paint < 1.5s
- **Database**: Query time < 100ms

### Segurança
- **Autenticação**: JWT com refresh tokens
- **Validação**: Input sanitization obrigatório
- **Rate Limiting**: 60 requests/minuto por IP
- **HTTPS**: Obrigatório em produção

## 🤝 Contribuição

Para adicionar ou modificar regras:

1. **Crie nova regra**: Adicione arquivo `.mdc` no diretório `.cursor/rules/`
2. **Configure metadados**: Use frontmatter com `alwaysApply`, `globs` ou `description`
3. **Documente**: Atualize este README.md
4. **Teste**: Verifique se a regra funciona corretamente

### Exemplo de Nova Regra
```markdown
---
globs: app/services/*.py
---
# Padrões para Serviços de IA

## Convenções
- Sempre usar async/await
- Implementar retry logic
- Logging estruturado obrigatório
- Tratamento de erros específicos
```

## 📞 Suporte

Para dúvidas sobre as regras ou sugestões de melhorias:

1. Consulte a documentação do projeto
2. Verifique os exemplos de código nas regras
3. Entre em contato com a equipe de desenvolvimento

---

**Última atualização**: Julho 2025  
**Versão**: 1.0.0  
**Projeto**: TecnoCursos AI Enterprise Edition 2025 