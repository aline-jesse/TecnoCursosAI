#!/bin/bash

# Script de Deploy Automático - TecnoCursos AI
# Versão: 2.0
# Deploy seguro com validações e rollback automático

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="tecnocursos-ai"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
PRODUCTION_HOST="${PRODUCTION_HOST:-your-server.com}"
STAGING_HOST="${STAGING_HOST:-staging.your-server.com}"
BACKUP_RETENTION_DAYS=30

# Funções utilitárias
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    local deps=("docker" "docker-compose" "git" "ssh" "rsync" "jq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "Dependência não encontrada: $dep"
            exit 1
        fi
    done
    
    log_success "Todas as dependências encontradas"
}

# Validar configuração
validate_config() {
    log_info "Validando configuração..."
    
    if [[ ! -f "docker-compose.production.yml" ]]; then
        log_error "Arquivo docker-compose.production.yml não encontrado"
        exit 1
    fi
    
    if [[ ! -f ".env.production" ]]; then
        log_error "Arquivo .env.production não encontrado"
        exit 1
    fi
    
    # Verificar variáveis essenciais
    local required_vars=("DATABASE_URL" "SECRET_KEY" "JWT_SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env.production; then
            log_error "Variável de ambiente obrigatória não encontrada: $var"
            exit 1
        fi
    done
    
    log_success "Configuração validada"
}

# Executar testes
run_tests() {
    log_info "Executando testes..."
    
    # Testes unitários
    if ! python -m pytest tests/ -v --tb=short; then
        log_error "Testes unitários falharam"
        exit 1
    fi
    
    # Testes de integração
    if ! python -m pytest tests/ -m integration -v; then
        log_error "Testes de integração falharam"
        exit 1
    fi
    
    # Verificação de qualidade de código
    if command -v flake8 &> /dev/null; then
        if ! flake8 app/ --max-line-length=88 --extend-ignore=E203,W503; then
            log_warning "Problemas de estilo de código encontrados"
        fi
    fi
    
    # Verificação de segurança
    if command -v bandit &> /dev/null; then
        if ! bandit -r app/ -f json -o security-report.json; then
            log_warning "Problemas de segurança potenciais encontrados"
        fi
    fi
    
    log_success "Todos os testes passaram"
}

# Build das imagens Docker
build_images() {
    log_info "Construindo imagens Docker..."
    
    # Tag com timestamp para versionamento
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local git_commit=$(git rev-parse --short HEAD)
    export IMAGE_TAG="${timestamp}_${git_commit}"
    
    # Build da imagem de produção
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Tag para latest
    docker tag "${PROJECT_NAME}:${IMAGE_TAG}" "${PROJECT_NAME}:latest"
    
    log_success "Imagens construídas com sucesso (tag: ${IMAGE_TAG})"
}

# Criar backup
create_backup() {
    local environment=$1
    log_info "Criando backup do ambiente ${environment}..."
    
    local backup_dir="backups/deploy_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup do banco de dados
    if [[ "$environment" == "production" ]]; then
        ssh "${DEPLOY_USER}@${PRODUCTION_HOST}" "docker-compose exec -T db pg_dump -U postgres tecnocursos" > "$backup_dir/database.sql"
    else
        ssh "${DEPLOY_USER}@${STAGING_HOST}" "docker-compose exec -T db pg_dump -U postgres tecnocursos" > "$backup_dir/database.sql"
    fi
    
    # Backup dos arquivos de upload
    if [[ "$environment" == "production" ]]; then
        rsync -avz "${DEPLOY_USER}@${PRODUCTION_HOST}:/app/uploads/" "$backup_dir/uploads/"
    else
        rsync -avz "${DEPLOY_USER}@${STAGING_HOST}:/app/uploads/" "$backup_dir/uploads/"
    fi
    
    # Backup da configuração
    cp .env.production "$backup_dir/"
    cp docker-compose.production.yml "$backup_dir/"
    
    log_success "Backup criado: $backup_dir"
    echo "$backup_dir" > .last_backup
}

# Deploy para ambiente
deploy_to_environment() {
    local environment=$1
    local host
    
    if [[ "$environment" == "production" ]]; then
        host="$PRODUCTION_HOST"
    else
        host="$STAGING_HOST"
    fi
    
    log_info "Fazendo deploy para ${environment} (${host})..."
    
    # Criar backup antes do deploy
    create_backup "$environment"
    
    # Transferir arquivos
    rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
        ./ "${DEPLOY_USER}@${host}:/app/"
    
    # Executar deploy no servidor
    ssh "${DEPLOY_USER}@${host}" << EOF
        cd /app
        
        # Parar serviços
        docker-compose -f docker-compose.production.yml down
        
        # Atualizar imagens
        docker-compose -f docker-compose.production.yml pull
        
        # Executar migrações
        docker-compose -f docker-compose.production.yml run --rm backend alembic upgrade head
        
        # Iniciar serviços
        docker-compose -f docker-compose.production.yml up -d
        
        # Aguardar inicialização
        sleep 30
        
        # Verificar saúde dos serviços
        curl -f http://localhost/health || exit 1
EOF
    
    log_success "Deploy para ${environment} concluído"
}

# Verificar saúde do deploy
verify_deployment() {
    local environment=$1
    local host
    
    if [[ "$environment" == "production" ]]; then
        host="$PRODUCTION_HOST"
    else
        host="$STAGING_HOST"
    fi
    
    log_info "Verificando saúde do deploy..."
    
    # Aguardar serviços ficarem prontos
    sleep 60
    
    # Verificar endpoint de saúde
    if ! curl -f "http://${host}/health" --max-time 30; then
        log_error "Verificação de saúde falhou"
        return 1
    fi
    
    # Verificar métricas básicas
    if ! curl -f "http://${host}/metrics" --max-time 30; then
        log_warning "Endpoint de métricas não disponível"
    fi
    
    # Verificar logs por erros
    ssh "${DEPLOY_USER}@${host}" "docker-compose logs --tail=100 | grep -i error || true"
    
    log_success "Deploy verificado com sucesso"
}

# Rollback
rollback_deployment() {
    local environment=$1
    local backup_path
    
    if [[ -f .last_backup ]]; then
        backup_path=$(cat .last_backup)
    else
        log_error "Nenhum backup encontrado para rollback"
        exit 1
    fi
    
    log_warning "Executando rollback para ${environment}..."
    
    local host
    if [[ "$environment" == "production" ]]; then
        host="$PRODUCTION_HOST"
    else
        host="$STAGING_HOST"
    fi
    
    # Restaurar configuração
    scp "$backup_path/.env.production" "${DEPLOY_USER}@${host}:/app/"
    scp "$backup_path/docker-compose.production.yml" "${DEPLOY_USER}@${host}:/app/"
    
    # Restaurar banco de dados
    ssh "${DEPLOY_USER}@${host}" "docker-compose exec -T db psql -U postgres -d tecnocursos < /tmp/backup.sql" < "$backup_path/database.sql"
    
    # Restaurar uploads
    rsync -avz "$backup_path/uploads/" "${DEPLOY_USER}@${host}:/app/uploads/"
    
    # Reiniciar serviços
    ssh "${DEPLOY_USER}@${host}" "cd /app && docker-compose -f docker-compose.production.yml restart"
    
    log_success "Rollback concluído"
}

# Limpeza de backups antigos
cleanup_old_backups() {
    log_info "Limpando backups antigos..."
    
    find backups/ -type d -mtime +$BACKUP_RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Limpeza de backups concluída"
}

# Menu principal
show_menu() {
    echo
    echo "======================================"
    echo "   TecnoCursos AI - Deploy Manager"
    echo "======================================"
    echo
    echo "Escolha uma opção:"
    echo "1) Deploy para Staging"
    echo "2) Deploy para Production"
    echo "3) Rollback Staging"
    echo "4) Rollback Production"
    echo "5) Executar apenas testes"
    echo "6) Build das imagens"
    echo "7) Verificar configuração"
    echo "8) Limpeza de backups"
    echo "9) Sair"
    echo
}

# Função principal
main() {
    check_dependencies
    
    if [[ $# -eq 0 ]]; then
        # Modo interativo
        while true; do
            show_menu
            read -p "Digite sua escolha [1-9]: " choice
            
            case $choice in
                1)
                    validate_config
                    run_tests
                    build_images
                    deploy_to_environment "staging"
                    verify_deployment "staging"
                    ;;
                2)
                    echo
                    read -p "⚠️  Confirmar deploy para PRODUCTION? [y/N]: " confirm
                    if [[ $confirm == [yY] ]]; then
                        validate_config
                        run_tests
                        build_images
                        deploy_to_environment "production"
                        verify_deployment "production"
                    fi
                    ;;
                3)
                    rollback_deployment "staging"
                    ;;
                4)
                    echo
                    read -p "⚠️  Confirmar rollback de PRODUCTION? [y/N]: " confirm
                    if [[ $confirm == [yY] ]]; then
                        rollback_deployment "production"
                    fi
                    ;;
                5)
                    run_tests
                    ;;
                6)
                    build_images
                    ;;
                7)
                    validate_config
                    ;;
                8)
                    cleanup_old_backups
                    ;;
                9)
                    log_info "Saindo..."
                    exit 0
                    ;;
                *)
                    log_error "Opção inválida"
                    ;;
            esac
            
            echo
            read -p "Pressione Enter para continuar..."
        done
    else
        # Modo comando
        case $1 in
            "staging")
                validate_config
                run_tests
                build_images
                deploy_to_environment "staging"
                verify_deployment "staging"
                ;;
            "production")
                validate_config
                run_tests
                build_images
                deploy_to_environment "production"
                verify_deployment "production"
                ;;
            "test")
                run_tests
                ;;
            "build")
                build_images
                ;;
            "rollback")
                if [[ $# -lt 2 ]]; then
                    log_error "Uso: $0 rollback [staging|production]"
                    exit 1
                fi
                rollback_deployment "$2"
                ;;
            *)
                echo "Uso: $0 [staging|production|test|build|rollback]"
                exit 1
                ;;
        esac
    fi
}

# Trap para cleanup em caso de erro
trap 'log_error "Deploy interrompido"; exit 1' INT TERM

# Executar função principal
main "$@"
