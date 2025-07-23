# Documentação dos Scripts - TecnoCursosAI

## Visão Geral

Esta documentação descreve os scripts utilitários disponíveis no diretório `scripts/` que auxiliam no desenvolvimento, deploy, manutenção e testes do sistema TecnoCursosAI.

## Scripts de Desenvolvimento

### `scripts/install_dependencies.py`
Script para instalação automática de dependências.

**Uso:**
```bash
python scripts/install_dependencies.py
```

**Funcionalidades:**
- Instala dependências Python do backend
- Instala dependências Node.js do frontend
- Configura ambiente virtual
- Verifica versões das dependências

### `scripts/fix_all_issues_automatically.py`
Script para correção automática de problemas comuns.

**Uso:**
```bash
python scripts/fix_all_issues_automatically.py
```

**Funcionalidades:**
- Corrige imports quebrados
- Atualiza configurações
- Repara dependências
- Limpa cache e arquivos temporários

### `scripts/fix_frontend_automatically.py`
Script específico para correção de problemas do frontend.

**Uso:**
```bash
python scripts/fix_frontend_automatically.py
```

**Funcionalidades:**
- Corrige problemas de TypeScript
- Atualiza dependências React
- Repara configurações de build
- Limpa cache do npm

## Scripts de Teste

### `scripts/test_system_complete.py`
Script para execução completa de testes do sistema.

**Uso:**
```bash
python scripts/test_system_complete.py
```

**Funcionalidades:**
- Executa testes do backend
- Executa testes do frontend
- Testa integração entre componentes
- Gera relatório de cobertura

### `scripts/test_upload_pipeline_completo.py`
Script para teste do pipeline de upload.

**Uso:**
```bash
python scripts/test_upload_pipeline_completo.py
```

**Funcionalidades:**
- Testa upload de arquivos
- Verifica processamento
- Testa geração de vídeos
- Valida resultados

### `scripts/test_avatar_completo.py`
Script para teste do sistema de avatares.

**Uso:**
```bash
python scripts/test_avatar_completo.py
```

**Funcionalidades:**
- Testa geração de avatares
- Verifica integração com TTS
- Testa diferentes estilos
- Valida qualidade do vídeo

## Scripts de Deploy

### `scripts/deploy_enterprise.py`
Script para deploy em ambiente enterprise.

**Uso:**
```bash
python scripts/deploy_enterprise.py
```

**Funcionalidades:**
- Configura ambiente de produção
- Deploy com Docker
- Configuração de banco de dados
- Setup de monitoramento

### `scripts/deploy_complete_system.sh`
Script shell para deploy completo.

**Uso:**
```bash
bash scripts/deploy_complete_system.sh
```

**Funcionalidades:**
- Deploy automatizado
- Configuração de serviços
- Backup automático
- Health checks

### `scripts/build_production.js`
Script Node.js para build de produção.

**Uso:**
```bash
node scripts/build_production.js
```

**Funcionalidades:**
- Build otimizado do frontend
- Minificação de assets
- Geração de bundles
- Configuração de CDN

## Scripts de Backup e Restauração

### `scripts/auto_backup.py`
Script para backup automático do sistema.

**Uso:**
```bash
python scripts/auto_backup.py
```

**Funcionalidades:**
- Backup do banco de dados
- Backup de arquivos de upload
- Backup de configurações
- Compressão e criptografia

### `scripts/backup_and_restore.py`
Script para backup e restauração.

**Uso:**
```bash
python scripts/backup_and_restore.py --mode backup
python scripts/backup_and_restore.py --mode restore --file backup.zip
```

**Funcionalidades:**
- Backup completo do sistema
- Restauração seletiva
- Validação de integridade
- Logs detalhados

### `scripts/mysql_backup.sh` / `scripts/mysql_backup.ps1`
Scripts para backup específico do MySQL.

**Uso (Linux/Mac):**
```bash
bash scripts/mysql_backup.sh backup -u root -p senha -h localhost -d tecnocursosai
```

**Uso (Windows):**
```powershell
powershell scripts/mysql_backup.ps1 -Mode backup -User root -Pass senha -Host localhost -Database tecnocursosai
```

## Scripts de Monitoramento

### `scripts/system_monitor.py`
Script para monitoramento do sistema.

**Uso:**
```bash
python scripts/system_monitor.py
```

**Funcionalidades:**
- Monitoramento de recursos
- Alertas de performance
- Logs de sistema
- Métricas de uso

### `scripts/health_check.py`
Script para verificação de saúde do sistema.

**Uso:**
```bash
python scripts/health_check.py
```

**Funcionalidades:**
- Verifica serviços
- Testa conectividade
- Valida configurações
- Gera relatório de status

### `scripts/monitor.py`
Script de monitoramento avançado.

**Uso:**
```bash
python scripts/monitor.py
```

**Funcionalidades:**
- Monitoramento em tempo real
- Dashboard de métricas
- Alertas automáticos
- Integração com Prometheus

## Scripts de Performance

### `scripts/performance_test.py`
Script para testes de performance.

**Uso:**
```bash
python scripts/performance_test.py
```

**Funcionalidades:**
- Testes de carga
- Análise de performance
- Benchmark de componentes
- Relatórios detalhados

### `scripts/stress_test.py`
Script para testes de stress.

**Uso:**
```bash
python scripts/stress_test.py
```

**Funcionalidades:**
- Testes de limite
- Simulação de carga alta
- Análise de gargalos
- Recomendações de otimização

### `scripts/load_test.py`
Script para testes de carga.

**Uso:**
```bash
python scripts/load_test.py
```

**Funcionalidades:**
- Simulação de usuários
- Testes de concorrência
- Análise de throughput
- Métricas de resposta

## Scripts de Manutenção

### `scripts/auto_optimizer.py`
Script para otimização automática.

**Uso:**
```bash
python scripts/auto_optimizer.py
```

**Funcionalidades:**
- Otimização de código
- Limpeza de cache
- Compressão de assets
- Análise de performance

### `scripts/cleanup_temp_files.py`
Script para limpeza de arquivos temporários.

**Uso:**
```bash
python scripts/cleanup_temp_files.py
```

**Funcionalidades:**
- Remove arquivos temporários
- Limpa cache
- Otimiza espaço em disco
- Logs de limpeza

## Scripts de Diagnóstico

### `scripts/diagnose.py`
Script para diagnóstico de problemas.

**Uso:**
```bash
python scripts/diagnose.py
```

**Funcionalidades:**
- Análise de logs
- Verificação de configurações
- Detecção de problemas
- Sugestões de correção

### `scripts/fix_port_issue.py`
Script para correção de problemas de porta.

**Uso:**
```bash
python scripts/fix_port_issue.py
```

**Funcionalidades:**
- Libera portas ocupadas
- Configura portas alternativas
- Verifica conflitos
- Logs de correção

## Scripts de Inicialização

### `scripts/start.sh` / `scripts/start.bat`
Scripts para inicialização do sistema.

**Uso (Linux/Mac):**
```bash
bash scripts/start.sh
```

**Uso (Windows):**
```cmd
scripts/start.bat
```

**Funcionalidades:**
- Inicializa backend
- Inicializa frontend
- Configura ambiente
- Verifica dependências

### `scripts/start_servers.bat`
Script para inicialização de múltiplos servidores.

**Uso:**
```cmd
scripts/start_servers.bat
```

**Funcionalidades:**
- Inicializa backend e frontend
- Configura proxy reverso
- Inicializa banco de dados
- Monitoramento de processos

## Scripts de Demonstração

### `scripts/demo_sistema_completo.py`
Script de demonstração do sistema.

**Uso:**
```bash
python scripts/demo_sistema_completo.py
```

**Funcionalidades:**
- Demonstra funcionalidades
- Testes automatizados
- Exemplos de uso
- Validação de features

### `scripts/demo_avatar_completo.py`
Script de demonstração de avatares.

**Uso:**
```bash
python scripts/demo_avatar_completo.py
```

**Funcionalidades:**
- Demonstra geração de avatares
- Testa diferentes estilos
- Valida qualidade
- Exemplos práticos

## Configuração e Uso

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- MySQL/PostgreSQL
- Docker (para alguns scripts)

### Variáveis de Ambiente
```bash
export DATABASE_URL="mysql://user:pass@localhost/tecnocursosai"
export SECRET_KEY="your-secret-key"
export ENVIRONMENT="development"
```

### Logs
Todos os scripts geram logs detalhados em:
- `logs/scripts/` - Logs de execução
- `logs/errors/` - Logs de erro
- `logs/performance/` - Logs de performance

### Agendamento
Para execução automática, use cron (Linux/Mac) ou Task Scheduler (Windows):

```bash
# Backup diário às 2h da manhã
0 2 * * * python /path/to/scripts/auto_backup.py

# Monitoramento a cada 5 minutos
*/5 * * * * python /path/to/scripts/health_check.py
```

## Troubleshooting

### Problemas Comuns

1. **Erro de permissão**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Dependências faltando**
   ```bash
   python scripts/install_dependencies.py
   ```

3. **Porta ocupada**
   ```bash
   python scripts/fix_port_issue.py
   ```

4. **Problemas de banco**
   ```bash
   python scripts/fix_database_issues.py
   ```

### Suporte
Para problemas com scripts, consulte:
- Logs em `logs/scripts/`
- Documentação específica de cada script
- Issues no repositório do projeto 