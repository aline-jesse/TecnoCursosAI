#!/bin/bash

# ============================================================================
# SCRIPT DE DEPLOYMENT PRODUÇÃO - TECNOCURSOS AI
# ============================================================================
#
# Script automatizado para deployment em produção seguindo
# as melhores práticas de DevOps e FastAPI deployment:
#
# - Zero-downtime deployment
# - Health checks automáticos
# - Rollback automático em caso de falha
# - Backup automático antes do deploy
# - Notificações via Slack/Discord
# - Logs estruturados
# - Verificações de segurança
#
# Uso:
#   ./scripts/deploy_production.sh [version] [--force] [--skip-tests]
#
# Autor: TecnoCursos AI System
# Data: 17/01/2025
# ============================================================================

set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURAÇÕES E VARIÁVEIS
# ============================================================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_ROOT/deploy"
BACKUP_DIR="/opt/tecnocursos/backups"
LOG_DIR="/opt/tecnocursos/logs"

# Configurações de deployment
VERSION="${1:-latest}"
FORCE_DEPLOY="${2:-false}"
SKIP_TESTS="${3:-false}"
DEPLOYMENT_ID="deploy_$(date +%Y%m%d_%H%M%S)"
DEPLOY_LOG="$LOG_DIR/deploy_$DEPLOYMENT_ID.log"

# URLs e endpoints
HEALTH_CHECK_URL="https://tecnocursos.ai/health"
SMOKE_TEST_URL="https://tecnocursos.ai/api/health"
METRICS_URL="https://tecnocursos.ai/api/metrics"

# Timeouts
HEALTH_CHECK_TIMEOUT=300  # 5 minutos
ROLLBACK_TIMEOUT=180      # 3 minutos
CONTAINER_START_TIMEOUT=120 # 2 minutos

# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$DEPLOY_LOG"
}

log_info() { log "INFO" "${BLUE}$*${NC}"; }
log_warn() { log "WARN" "${YELLOW}$*${NC}"; }
log_error() { log "ERROR" "${RED}$*${NC}"; }
log_success() { log "SUCCESS" "${GREEN}$*${NC}"; }
log_debug() { log "DEBUG" "${PURPLE}$*${NC}"; }

cleanup() {
    log_info "🧹 Executando cleanup..."
    # Remover containers temporários se existirem
    docker container prune -f > /dev/null 2>&1 || true
    # Remover imagens dangling
    docker image prune -f > /dev/null 2>&1 || true
}

trap cleanup EXIT

# ============================================================================
# VERIFICAÇÕES PRÉ-DEPLOYMENT
# ============================================================================

check_prerequisites() {
    log_info "🔍 Verificando pré-requisitos..."
    
    # Verificar se Docker está rodando
    if ! docker info > /dev/null 2>&1; then
        log_error "❌ Docker não está rodando"
        exit 1
    fi
    
    # Verificar se Docker Compose está disponível
    if ! command -v docker-compose > /dev/null 2>&1; then
        log_error "❌ Docker Compose não encontrado"
        exit 1
    fi
    
    # Verificar se arquivo .env existe
    if [[ ! -f "$PROJECT_ROOT/.env.production" ]]; then
        log_error "❌ Arquivo .env.production não encontrado"
        exit 1
    fi
    
    # Verificar espaço em disco
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local required_space=5000000  # 5GB em KB
    
    if [[ $available_space -lt $required_space ]]; then
        log_error "❌ Espaço em disco insuficiente. Necessário: 5GB, Disponível: $((available_space/1024/1024))GB"
        exit 1
    fi
    
    # Verificar RAM disponível
    local available_ram=$(free -m | awk 'NR==2{print $7}')
    local required_ram=2048  # 2GB
    
    if [[ $available_ram -lt $required_ram ]]; then
        log_warn "⚠️  RAM disponível baixa: ${available_ram}MB (recomendado: ${required_ram}MB)"
    fi
    
    log_success "✅ Pré-requisitos verificados"
}

check_environment() {
    log_info "🌍 Verificando ambiente de produção..."
    
    # Carregar variáveis de ambiente
    if [[ -f "$PROJECT_ROOT/.env.production" ]]; then
        source "$PROJECT_ROOT/.env.production"
    fi
    
    # Verificar variáveis críticas
    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "MYSQL_PASSWORD"
        "MYSQL_ROOT_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "❌ Variável de ambiente obrigatória não definida: $var"
            exit 1
        fi
    done
    
    # Verificar se não estamos usando valores padrão em produção
    if [[ "${SECRET_KEY:-}" == "your-secret-key-change-in-production" ]]; then
        log_error "❌ SECRET_KEY padrão não pode ser usado em produção"
        exit 1
    fi
    
    log_success "✅ Ambiente de produção verificado"
}

# ============================================================================
# TESTES PRÉ-DEPLOYMENT
# ============================================================================

run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warn "⚠️  Testes ignorados (--skip-tests)"
        return 0
    fi
    
    log_info "🧪 Executando testes..."
    
    # Testes unitários
    log_info "  📋 Executando testes unitários..."
    if ! python -m pytest tests/ -v --tb=short; then
        log_error "❌ Testes unitários falharam"
        exit 1
    fi
    
    # Testes de integração
    log_info "  🔗 Executando testes de integração..."
    if ! python -m pytest tests/integration/ -v; then
        log_error "❌ Testes de integração falharam"
        exit 1
    fi
    
    # Testes de segurança
    log_info "  🔒 Executando testes de segurança..."
    if command -v bandit > /dev/null 2>&1; then
        bandit -r app/ -f json -o bandit-report.json || log_warn "⚠️  Vulnerabilidades encontradas no código"
    fi
    
    log_success "✅ Todos os testes passaram"
}

# ============================================================================
# BACKUP
# ============================================================================

create_backup() {
    log_info "💾 Criando backup pré-deployment..."
    
    # Criar diretório de backup se não existir
    mkdir -p "$BACKUP_DIR"
    
    # Backup do banco de dados
    local backup_file="$BACKUP_DIR/pre_deploy_${DEPLOYMENT_ID}.sql"
    
    if docker-compose -f "$DEPLOY_DIR/docker-compose.production.yml" exec -T mysql mysqldump \
        -u root -p"${MYSQL_ROOT_PASSWORD}" tecnocursos_production > "$backup_file"; then
        log_success "✅ Backup do banco criado: $backup_file"
    else
        log_error "❌ Falha ao criar backup do banco"
        exit 1
    fi
    
    # Backup dos arquivos estáticos
    if [[ -d "/opt/tecnocursos/static" ]]; then
        tar -czf "$BACKUP_DIR/static_${DEPLOYMENT_ID}.tar.gz" -C "/opt/tecnocursos" static/
        log_success "✅ Backup dos arquivos estáticos criado"
    fi
    
    # Backup das configurações
    cp "$PROJECT_ROOT/.env.production" "$BACKUP_DIR/env_${DEPLOYMENT_ID}.backup"
    
    log_success "✅ Backup completo criado"
}

# ============================================================================
# DEPLOYMENT
# ============================================================================

build_and_deploy() {
    log_info "🏗️  Construindo e fazendo deploy da versão $VERSION..."
    
    # Navegar para o diretório de deploy
    cd "$DEPLOY_DIR"
    
    # Pull das imagens base
    log_info "  📥 Fazendo pull das imagens base..."
    docker-compose -f docker-compose.production.yml pull
    
    # Build das imagens da aplicação
    log_info "  🔨 Construindo imagens da aplicação..."
    if ! docker-compose -f docker-compose.production.yml build --no-cache fastapi-app-1 fastapi-app-2; then
        log_error "❌ Falha no build das imagens"
        exit 1
    fi
    
    # Deployment com zero downtime
    log_info "  🚀 Iniciando deployment zero-downtime..."
    
    # 1. Atualizar um container por vez
    log_info "    📦 Atualizando fastapi-app-1..."
    docker-compose -f docker-compose.production.yml up -d --no-deps fastapi-app-1
    
    # Aguardar health check
    wait_for_health_check "fastapi-app-1"
    
    # 2. Atualizar segundo container
    log_info "    📦 Atualizando fastapi-app-2..."
    docker-compose -f docker-compose.production.yml up -d --no-deps fastapi-app-2
    
    # Aguardar health check
    wait_for_health_check "fastapi-app-2"
    
    # 3. Atualizar outros serviços
    log_info "    📦 Atualizando outros serviços..."
    docker-compose -f docker-compose.production.yml up -d
    
    log_success "✅ Deployment concluído"
}

wait_for_health_check() {
    local container_name=$1
    local timeout=$CONTAINER_START_TIMEOUT
    local interval=10
    local elapsed=0
    
    log_info "    ⏳ Aguardando health check para $container_name..."
    
    while [[ $elapsed -lt $timeout ]]; do
        if docker inspect --format='{{.State.Health.Status}}' "tecnocursos-${container_name}" | grep -q "healthy"; then
            log_success "    ✅ $container_name está saudável"
            return 0
        fi
        
        sleep $interval
        elapsed=$((elapsed + interval))
        log_debug "    ⏳ Aguardando... ($elapsed/${timeout}s)"
    done
    
    log_error "❌ Timeout no health check para $container_name"
    return 1
}

# ============================================================================
# VERIFICAÇÕES PÓS-DEPLOYMENT
# ============================================================================

run_smoke_tests() {
    log_info "🔥 Executando smoke tests..."
    
    local tests=(
        "$HEALTH_CHECK_URL:Health Check"
        "$SMOKE_TEST_URL:API Health"
        "https://tecnocursos.ai/api/docs:API Documentation"
    )
    
    for test in "${tests[@]}"; do
        local url="${test%:*}"
        local name="${test#*:}"
        
        log_info "  🧪 Testando $name..."
        
        local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$url" || echo "000")
        
        if [[ "$response" == "200" ]]; then
            log_success "    ✅ $name: OK ($response)"
        else
            log_error "    ❌ $name: FALHOU ($response)"
            return 1
        fi
    done
    
    log_success "✅ Todos os smoke tests passaram"
}

check_performance() {
    log_info "⚡ Verificando performance..."
    
    # Teste de latência
    local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$HEALTH_CHECK_URL")
    local response_time_ms=$(echo "$response_time * 1000" | bc)
    
    if (( $(echo "$response_time > 2.0" | bc -l) )); then
        log_warn "⚠️  Latência alta: ${response_time_ms}ms"
    else
        log_success "✅ Latência OK: ${response_time_ms}ms"
    fi
    
    # Verificar uso de recursos
    log_info "  📊 Verificando uso de recursos..."
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | \
        grep tecnocursos | while read -r line; do
        log_info "    $line"
    done
    
    log_success "✅ Verificação de performance concluída"
}

# ============================================================================
# ROLLBACK
# ============================================================================

rollback() {
    log_error "🔄 Iniciando rollback..."
    
    # Parar containers atuais
    docker-compose -f "$DEPLOY_DIR/docker-compose.production.yml" down
    
    # Restaurar backup do banco
    local backup_file="$BACKUP_DIR/pre_deploy_${DEPLOYMENT_ID}.sql"
    if [[ -f "$backup_file" ]]; then
        log_info "  📥 Restaurando backup do banco..."
        docker-compose -f "$DEPLOY_DIR/docker-compose.production.yml" up -d mysql
        sleep 30  # Aguardar MySQL inicializar
        docker-compose -f "$DEPLOY_DIR/docker-compose.production.yml" exec -T mysql \
            mysql -u root -p"${MYSQL_ROOT_PASSWORD}" tecnocursos_production < "$backup_file"
    fi
    
    # Subir versão anterior
    log_info "  🔄 Subindo versão anterior..."
    git checkout HEAD~1  # Voltar para commit anterior
    docker-compose -f "$DEPLOY_DIR/docker-compose.production.yml" up -d --build
    
    log_warn "⚠️  Rollback concluído"
    send_notification "❌ Deployment falhou. Rollback executado para TecnoCursos AI."
}

# ============================================================================
# NOTIFICAÇÕES
# ============================================================================

send_notification() {
    local message="$1"
    local webhook_url="${SLACK_WEBHOOK_URL:-}"
    
    if [[ -n "$webhook_url" ]]; then
        local payload=$(cat <<EOF
{
    "text": "$message",
    "username": "TecnoCursos Deploy Bot",
    "channel": "#deployments",
    "attachments": [
        {
            "color": "good",
            "fields": [
                {
                    "title": "Versão",
                    "value": "$VERSION",
                    "short": true
                },
                {
                    "title": "Deployment ID",
                    "value": "$DEPLOYMENT_ID",
                    "short": true
                },
                {
                    "title": "Timestamp",
                    "value": "$(date)",
                    "short": false
                }
            ]
        }
    ]
}
EOF
        )
        
        curl -X POST -H 'Content-type: application/json' \
            --data "$payload" "$webhook_url" > /dev/null 2>&1 || true
    fi
}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

main() {
    # Banner
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                    TECNOCURSOS AI DEPLOYMENT                     ║
║                         Production v2025                         ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    
    log_info "🚀 Iniciando deployment da versão $VERSION..."
    log_info "📝 Deployment ID: $DEPLOYMENT_ID"
    log_info "📄 Log: $DEPLOY_LOG"
    
    # Criar diretório de logs se não existir
    mkdir -p "$LOG_DIR"
    
    # Executar deployment
    if [[ "$FORCE_DEPLOY" != "true" ]]; then
        check_prerequisites
        check_environment
        run_tests
    else
        log_warn "⚠️  Deployment forçado - ignorando verificações"
    fi
    
    create_backup
    
    # Deployment com verificação de falhas
    if ! build_and_deploy; then
        rollback
        exit 1
    fi
    
    # Verificações pós-deployment
    sleep 30  # Aguardar serviços estabilizarem
    
    if ! run_smoke_tests; then
        rollback
        exit 1
    fi
    
    check_performance
    
    # Sucesso!
    local duration=$(($(date +%s) - $(date -d "$(head -1 "$DEPLOY_LOG" | cut -d' ' -f1-2)" +%s)))
    log_success "🎉 Deployment concluído com sucesso em ${duration}s!"
    
    # Enviar notificação de sucesso
    send_notification "✅ Deployment da versão $VERSION concluído com sucesso!"
    
    # Cleanup final
    log_info "🧹 Executando cleanup final..."
    docker system prune -f
    
    log_success "✅ Deployment de produção finalizado!"
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat << EOF
Uso: $0 [VERSION] [OPÇÕES]

ARGUMENTOS:
    VERSION     Versão a ser deployada (default: latest)

OPÇÕES:
    --force         Pular verificações pré-deployment
    --skip-tests    Pular execução de testes
    --help         Mostrar esta ajuda

EXEMPLOS:
    $0                           # Deploy latest
    $0 v2.1.0                   # Deploy versão específica
    $0 latest --force           # Deploy forçado
    $0 v2.1.0 --skip-tests     # Deploy sem testes

VARIÁVEIS DE AMBIENTE:
    SLACK_WEBHOOK_URL          URL do webhook para notificações
    MYSQL_ROOT_PASSWORD        Senha root do MySQL
    SECRET_KEY                 Chave secreta da aplicação

EOF
}

# ============================================================================
# ENTRADA DO SCRIPT
# ============================================================================

case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 