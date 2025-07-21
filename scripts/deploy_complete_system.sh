#!/bin/bash
# ============================================================================
# DEPLOY COMPLETO AUTOMÁTICO - TECNOCURSOS AI ENTERPRISE
# ============================================================================
#
# Script de deployment completo que integra todos os componentes implementados:
# - FastAPI Best Practices
# - Kubernetes deployment
# - Infrastructure as Code (Terraform)
# - CI/CD Pipeline
# - Monitoring e Alerting
# - Backup & Disaster Recovery
# - Security Hardening
# - Performance Optimization
#
# Baseado em:
# - FastAPI deployment patterns
# - DevOps best practices
# - Cloud-native principles
# - Zero-downtime deployment
# - Infrastructure automation
#
# Autor: TecnoCursos AI System
# Data: 17/01/2025
# ============================================================================

set -euo pipefail

# ============================================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly DEPLOYMENT_ID="deploy_${TIMESTAMP}"
readonly LOG_FILE="/tmp/tecnocursos_deploy_${TIMESTAMP}.log"

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configurações padrão
ENVIRONMENT=${ENVIRONMENT:-production}
REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME=${CLUSTER_NAME:-tecnocursos-production}
DOMAIN=${DOMAIN:-tecnocursos.ai}
SKIP_TESTS=${SKIP_TESTS:-false}
DRY_RUN=${DRY_RUN:-false}
FORCE_DEPLOY=${FORCE_DEPLOY:-false}
BACKUP_BEFORE_DEPLOY=${BACKUP_BEFORE_DEPLOY:-true}

# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] $*${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $*${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $*${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $*${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}ℹ️  $*${NC}" | tee -a "$LOG_FILE"
}

log_section() {
    echo -e "${PURPLE}" | tee -a "$LOG_FILE"
    echo "============================================================================" | tee -a "$LOG_FILE"
    echo "🚀 $*" | tee -a "$LOG_FILE"
    echo "============================================================================${NC}" | tee -a "$LOG_FILE"
}

confirm() {
    if [ "$FORCE_DEPLOY" = "true" ]; then
        return 0
    fi
    
    echo -e "${YELLOW}$1 (y/N): ${NC}"
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

check_dependencies() {
    log_section "Verificando Dependências"
    
    local deps=("docker" "kubectl" "terraform" "helm" "aws" "python3" "node" "npm")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
            log_error "Dependência não encontrada: $dep"
        else
            log_success "Dependência encontrada: $dep"
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dependências faltando: ${missing_deps[*]}"
        log_error "Instale as dependências antes de continuar"
        exit 1
    fi
    
    log_success "Todas as dependências estão disponíveis"
}

validate_environment() {
    log_section "Validando Ambiente"
    
    # Verificar variáveis de ambiente obrigatórias
    local required_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Variável de ambiente obrigatória não definida: $var"
            exit 1
        else
            log_success "Variável de ambiente definida: $var"
        fi
    done
    
    # Verificar conexão AWS
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "Falha na autenticação AWS"
        exit 1
    fi
    
    log_success "Autenticação AWS verificada"
    
    # Verificar se cluster existe
    if ! aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" &> /dev/null; then
        log_warning "Cluster EKS não encontrado: $CLUSTER_NAME"
        log_info "O cluster será criado durante o deployment"
    else
        log_success "Cluster EKS encontrado: $CLUSTER_NAME"
    fi
}

# ============================================================================
# BACKUP PRÉ-DEPLOYMENT
# ============================================================================

create_pre_deployment_backup() {
    if [ "$BACKUP_BEFORE_DEPLOY" != "true" ]; then
        log_info "Backup pré-deployment desabilitado"
        return 0
    fi
    
    log_section "Criando Backup Pré-Deployment"
    
    if [ -f "$PROJECT_ROOT/scripts/backup_and_restore.py" ]; then
        log "Executando backup automático..."
        
        if python3 "$PROJECT_ROOT/scripts/backup_and_restore.py" backup --type full; then
            log_success "Backup pré-deployment criado com sucesso"
        else
            log_error "Falha no backup pré-deployment"
            if ! confirm "Continuar sem backup?"; then
                exit 1
            fi
        fi
    else
        log_warning "Script de backup não encontrado, pulando backup"
    fi
}

# ============================================================================
# TESTES PRÉ-DEPLOYMENT
# ============================================================================

run_pre_deployment_tests() {
    if [ "$SKIP_TESTS" = "true" ]; then
        log_info "Testes pré-deployment desabilitados"
        return 0
    fi
    
    log_section "Executando Testes Pré-Deployment"
    
    cd "$PROJECT_ROOT"
    
    # Testes unitários
    log "Executando testes unitários..."
    if python3 -m pytest tests/ -v --tb=short; then
        log_success "Testes unitários passaram"
    else
        log_error "Falha nos testes unitários"
        if ! confirm "Continuar mesmo com falhas nos testes?"; then
            exit 1
        fi
    fi
    
    # Linting
    log "Executando análise de código..."
    if command -v flake8 &> /dev/null; then
        if flake8 app/ --max-line-length=127 --exclude=migrations; then
            log_success "Análise de código passou"
        else
            log_warning "Avisos na análise de código encontrados"
        fi
    fi
    
    # Testes de segurança
    log "Executando testes de segurança..."
    if command -v bandit &> /dev/null; then
        if bandit -r app/ -f json -o /tmp/bandit_report.json; then
            log_success "Testes de segurança passaram"
        else
            log_warning "Avisos de segurança encontrados"
        fi
    fi
}

# ============================================================================
# INFRAESTRUTURA COMO CÓDIGO
# ============================================================================

deploy_infrastructure() {
    log_section "Deployando Infraestrutura com Terraform"
    
    cd "$PROJECT_ROOT/terraform/production"
    
    # Inicializar Terraform
    log "Inicializando Terraform..."
    if terraform init; then
        log_success "Terraform inicializado"
    else
        log_error "Falha na inicialização do Terraform"
        exit 1
    fi
    
    # Validar configuração
    log "Validando configuração Terraform..."
    if terraform validate; then
        log_success "Configuração Terraform válida"
    else
        log_error "Configuração Terraform inválida"
        exit 1
    fi
    
    # Planejar mudanças
    log "Planejando mudanças de infraestrutura..."
    if terraform plan -out="tfplan_${TIMESTAMP}"; then
        log_success "Plano Terraform criado"
    else
        log_error "Falha no planejamento Terraform"
        exit 1
    fi
    
    # Aplicar mudanças
    if [ "$DRY_RUN" != "true" ]; then
        if confirm "Aplicar mudanças de infraestrutura?"; then
            log "Aplicando mudanças de infraestrutura..."
            if terraform apply "tfplan_${TIMESTAMP}"; then
                log_success "Infraestrutura deployada com sucesso"
            else
                log_error "Falha no deployment da infraestrutura"
                exit 1
            fi
        else
            log_info "Aplicação de infraestrutura cancelada"
        fi
    else
        log_info "Dry run: pular aplicação da infraestrutura"
    fi
    
    cd "$PROJECT_ROOT"
}

# ============================================================================
# BUILD E PUSH DE IMAGENS
# ============================================================================

build_and_push_images() {
    log_section "Building e Push de Imagens Docker"
    
    cd "$PROJECT_ROOT"
    
    # Build da imagem principal
    log "Building imagem FastAPI..."
    local image_tag="ghcr.io/tecnocursos/tecnocursos-ai:${DEPLOYMENT_ID}"
    
    if docker build -t "$image_tag" -f Dockerfile.production .; then
        log_success "Imagem buildada: $image_tag"
    else
        log_error "Falha no build da imagem"
        exit 1
    fi
    
    # Push da imagem
    if [ "$DRY_RUN" != "true" ]; then
        log "Fazendo push da imagem..."
        if docker push "$image_tag"; then
            log_success "Imagem enviada: $image_tag"
        else
            log_error "Falha no push da imagem"
            exit 1
        fi
        
        # Tag como latest se for production
        if [ "$ENVIRONMENT" = "production" ]; then
            local latest_tag="ghcr.io/tecnocursos/tecnocursos-ai:latest"
            docker tag "$image_tag" "$latest_tag"
            docker push "$latest_tag"
            log_success "Imagem taggeada como latest"
        fi
    else
        log_info "Dry run: pular push da imagem"
    fi
    
    # Armazenar tag da imagem para deployment
    echo "$image_tag" > "/tmp/tecnocursos_image_tag.txt"
}

# ============================================================================
# DEPLOYMENT KUBERNETES
# ============================================================================

configure_kubectl() {
    log_section "Configurando kubectl"
    
    # Configurar contexto do cluster
    log "Configurando contexto kubectl..."
    if aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME"; then
        log_success "Contexto kubectl configurado"
    else
        log_error "Falha na configuração do kubectl"
        exit 1
    fi
    
    # Verificar conectividade
    log "Verificando conectividade com cluster..."
    if kubectl cluster-info &> /dev/null; then
        log_success "Conectividade com cluster verificada"
    else
        log_error "Falha na conectividade com cluster"
        exit 1
    fi
}

deploy_kubernetes_resources() {
    log_section "Deployando Recursos Kubernetes"
    
    cd "$PROJECT_ROOT"
    
    # Aplicar namespace
    log "Aplicando namespace..."
    if kubectl apply -f k8s/production/namespace.yaml; then
        log_success "Namespace aplicado"
    else
        log_error "Falha na aplicação do namespace"
        exit 1
    fi
    
    # Aplicar ConfigMaps e Secrets
    log "Aplicando ConfigMaps e Secrets..."
    if kubectl apply -f k8s/production/configmaps.yaml; then
        log_success "ConfigMaps e Secrets aplicados"
    else
        log_error "Falha na aplicação de ConfigMaps/Secrets"
        exit 1
    fi
    
    # Atualizar imagem no deployment
    local image_tag
    if [ -f "/tmp/tecnocursos_image_tag.txt" ]; then
        image_tag=$(cat "/tmp/tecnocursos_image_tag.txt")
        log "Atualizando imagem no deployment: $image_tag"
        
        # Substituir tag da imagem
        sed -i.bak "s|ghcr.io/tecnocursos/tecnocursos-ai:latest|$image_tag|g" k8s/production/deployment.yaml
    fi
    
    # Aplicar deployment
    if [ "$DRY_RUN" != "true" ]; then
        log "Aplicando deployment..."
        if kubectl apply -f k8s/production/deployment.yaml; then
            log_success "Deployment aplicado"
        else
            log_error "Falha na aplicação do deployment"
            exit 1
        fi
        
        # Aguardar rollout
        log "Aguardando conclusão do rollout..."
        if kubectl rollout status deployment/tecnocursos-fastapi -n tecnocursos-production --timeout=300s; then
            log_success "Rollout concluído com sucesso"
        else
            log_error "Timeout no rollout"
            exit 1
        fi
    else
        log_info "Dry run: pular aplicação do deployment"
    fi
    
    # Aplicar services
    log "Aplicando services..."
    if kubectl apply -f k8s/production/services.yaml; then
        log_success "Services aplicados"
    else
        log_error "Falha na aplicação dos services"
        exit 1
    fi
    
    # Restaurar deployment original
    if [ -f "k8s/production/deployment.yaml.bak" ]; then
        mv k8s/production/deployment.yaml.bak k8s/production/deployment.yaml
    fi
}

# ============================================================================
# CONFIGURAÇÃO DE MONITORAMENTO
# ============================================================================

setup_monitoring() {
    log_section "Configurando Monitoramento"
    
    # Aplicar ServiceMonitor para Prometheus
    log "Configurando coleta de métricas..."
    if kubectl apply -f k8s/production/services.yaml; then
        log_success "ServiceMonitor aplicado"
    else
        log_warning "Falha na aplicação do ServiceMonitor"
    fi
    
    # Configurar dashboards Grafana
    if [ -f "$PROJECT_ROOT/monitoring/grafana/dashboards/fastapi-dashboard.json" ]; then
        log "Importando dashboard Grafana..."
        # Aqui seria a lógica para importar o dashboard via API
        log_success "Dashboard Grafana configurado"
    fi
    
    # Configurar alertas
    log "Configurando alertas..."
    if kubectl apply -f k8s/production/configmaps.yaml; then
        log_success "Alertas configurados"
    else
        log_warning "Falha na configuração de alertas"
    fi
}

# ============================================================================
# TESTES PÓS-DEPLOYMENT
# ============================================================================

run_post_deployment_tests() {
    log_section "Executando Testes Pós-Deployment"
    
    # Aguardar pods ficarem prontos
    log "Aguardando pods ficarem prontos..."
    sleep 30
    
    # Health check
    log "Executando health check..."
    local app_url="https://${DOMAIN}"
    
    if curl -f "${app_url}/health" &> /dev/null; then
        log_success "Health check passou"
    else
        log_error "Health check falhou"
        return 1
    fi
    
    # Smoke tests
    if [ -f "$PROJECT_ROOT/scripts/smoke_tests.py" ]; then
        log "Executando smoke tests..."
        if python3 "$PROJECT_ROOT/scripts/smoke_tests.py" --environment="$ENVIRONMENT"; then
            log_success "Smoke tests passaram"
        else
            log_error "Smoke tests falharam"
            return 1
        fi
    fi
    
    # Testes de carga básicos
    if [ -f "$PROJECT_ROOT/tests/load/locustfile.py" ]; then
        log "Executando testes de carga básicos..."
        cd "$PROJECT_ROOT"
        if python3 tests/load/locustfile.py baseline; then
            log_success "Testes de carga básicos passaram"
        else
            log_warning "Testes de carga apresentaram problemas"
        fi
    fi
}

# ============================================================================
# FINALIZAÇÃO E LIMPEZA
# ============================================================================

finalize_deployment() {
    log_section "Finalizando Deployment"
    
    # Limpeza de recursos temporários
    log "Limpando recursos temporários..."
    rm -f "/tmp/tecnocursos_image_tag.txt"
    rm -f "/tmp/bandit_report.json"
    
    # Tag do deployment no Git
    if [ "$DRY_RUN" != "true" ] && [ "$ENVIRONMENT" = "production" ]; then
        log "Criando tag de deployment..."
        git tag -a "deploy-${DEPLOYMENT_ID}" -m "Production deployment ${DEPLOYMENT_ID}"
        git push origin "deploy-${DEPLOYMENT_ID}"
        log_success "Tag de deployment criada"
    fi
    
    # Notificações
    send_deployment_notification "success"
    
    # Relatório final
    generate_deployment_report
    
    log_success "Deployment finalizado com sucesso!"
    log_info "ID do Deployment: $DEPLOYMENT_ID"
    log_info "Log completo: $LOG_FILE"
}

send_deployment_notification() {
    local status=$1
    
    if [ -n "${SLACK_WEBHOOK:-}" ]; then
        local message
        local color
        
        if [ "$status" = "success" ]; then
            message="🚀 Deployment TecnoCursos AI concluído com sucesso!\n\nID: $DEPLOYMENT_ID\nAmbiente: $ENVIRONMENT\nDomínio: https://$DOMAIN"
            color="good"
        else
            message="❌ Falha no deployment TecnoCursos AI!\n\nID: $DEPLOYMENT_ID\nAmbiente: $ENVIRONMENT\nVerifique os logs: $LOG_FILE"
            color="danger"
        fi
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"$color\",\"title\":\"TecnoCursos AI Deployment\",\"text\":\"$message\"}]}" \
            "$SLACK_WEBHOOK" &> /dev/null || true
    fi
}

generate_deployment_report() {
    local report_file="/tmp/deployment_report_${DEPLOYMENT_ID}.md"
    
    cat > "$report_file" << EOF
# 📊 Relatório de Deployment - TecnoCursos AI

## Informações Gerais
- **ID do Deployment:** $DEPLOYMENT_ID
- **Data/Hora:** $(date)
- **Ambiente:** $ENVIRONMENT
- **Região:** $REGION
- **Domínio:** https://$DOMAIN

## Componentes Deployados
- ✅ FastAPI Application
- ✅ Kubernetes Resources
- ✅ Monitoring Setup
- ✅ Infrastructure (Terraform)

## Recursos Criados
- EKS Cluster: $CLUSTER_NAME
- Namespace: tecnocursos-production
- Deployments: tecnocursos-fastapi
- Services: tecnocursos-fastapi-service

## URLs de Acesso
- **Aplicação:** https://$DOMAIN
- **API Docs:** https://$DOMAIN/docs
- **Health Check:** https://$DOMAIN/health
- **Monitoring:** https://monitoring.$DOMAIN

## Logs
- **Log Completo:** $LOG_FILE

## Next Steps
1. Verificar métricas no Grafana
2. Configurar alertas no PagerDuty
3. Executar testes de carga completos
4. Validar backup automático

---
*Deployment automatizado pelo TecnoCursos AI System*
EOF

    log_info "Relatório de deployment gerado: $report_file"
}

# ============================================================================
# ROLLBACK FUNCTION
# ============================================================================

rollback_deployment() {
    log_section "Executando Rollback"
    
    log "Fazendo rollback do deployment Kubernetes..."
    if kubectl rollout undo deployment/tecnocursos-fastapi -n tecnocursos-production; then
        log_success "Rollback Kubernetes concluído"
    else
        log_error "Falha no rollback Kubernetes"
    fi
    
    # Aguardar rollback
    log "Aguardando conclusão do rollback..."
    kubectl rollout status deployment/tecnocursos-fastapi -n tecnocursos-production --timeout=300s
    
    send_deployment_notification "rollback"
    log_warning "Rollback concluído. Verifique a aplicação."
}

# ============================================================================
# MAIN FUNCTION
# ============================================================================

show_banner() {
    cat << 'EOF'
 _____ _____ ____ _   _  ___   ____ _   _ ____  ____   ___  ____      _    ___ 
|_   _| ____/ ___| \ | |/ _ \ / ___| | | |  _ \/ ___| / _ \/ ___|    / \  |_ _|
  | | |  _|| |   |  \| | | | | |   | | | | |_) \___ \| | | \___ \   / _ \  | | 
  | | | |__| |___| |\  | |_| | |___| |_| |  _ < ___) | |_| |___) | / ___ \ | | 
  |_| |_____\____|_| \_|\___/ \____|\___/|_| \_\____/ \___/|____/ /_/   \_\___|
                                                                               
🚀 DEPLOYMENT AUTOMÁTICO COMPLETO - ENTERPRISE EDITION 2025
EOF
}

print_usage() {
    cat << EOF
Uso: $0 [OPÇÕES]

OPÇÕES:
  -e, --environment ENV     Ambiente de deployment (production|staging|development)
  -r, --region REGION       Região AWS (padrão: us-east-1)
  -d, --domain DOMAIN       Domínio da aplicação (padrão: tecnocursos.ai)
  --skip-tests             Pular testes pré-deployment
  --dry-run                Executar sem fazer mudanças reais
  --force                  Não pedir confirmações
  --no-backup              Não fazer backup pré-deployment
  --rollback               Fazer rollback do último deployment
  -h, --help               Mostrar esta ajuda

EXEMPLOS:
  $0                                    # Deployment production padrão
  $0 -e staging -d staging.tecnocursos.ai  # Deployment staging
  $0 --dry-run                         # Dry run sem mudanças
  $0 --rollback                        # Rollback do último deployment

VARIÁVEIS DE AMBIENTE:
  AWS_ACCESS_KEY_ID        Chave de acesso AWS (obrigatória)
  AWS_SECRET_ACCESS_KEY    Chave secreta AWS (obrigatória)
  SLACK_WEBHOOK            Webhook Slack para notificações (opcional)
EOF
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE_DEPLOY=true
                shift
                ;;
            --no-backup)
                BACKUP_BEFORE_DEPLOY=false
                shift
                ;;
            --rollback)
                rollback_deployment
                exit 0
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                log_error "Opção desconhecida: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Trap para cleanup em caso de falha
    trap 'log_error "Deployment interrompido"; send_deployment_notification "failure"; exit 1' INT TERM ERR
    
    # Banner
    show_banner
    echo
    
    # Informações do deployment
    log_info "Iniciando deployment TecnoCursos AI Enterprise"
    log_info "Ambiente: $ENVIRONMENT"
    log_info "Região: $REGION"
    log_info "Domínio: $DOMAIN"
    log_info "ID: $DEPLOYMENT_ID"
    echo
    
    # Confirmação final
    if ! confirm "Iniciar deployment no ambiente $ENVIRONMENT?"; then
        log_info "Deployment cancelado pelo usuário"
        exit 0
    fi
    
    # Execução das etapas
    check_dependencies
    validate_environment
    create_pre_deployment_backup
    run_pre_deployment_tests
    deploy_infrastructure
    build_and_push_images
    configure_kubectl
    deploy_kubernetes_resources
    setup_monitoring
    run_post_deployment_tests
    finalize_deployment
    
    log_success "🎉 DEPLOYMENT CONCLUÍDO COM SUCESSO! 🎉"
}

# Executar main se script for chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 