#!/bin/bash
# ===============================================================
# ENTRYPOINT SCRIPT - TECNOCURSOS AI PRODUCTION
# ===============================================================
# Script otimizado de inicialização para container de produção
# Inclui: health checks, migrações, configurações dinâmicas
# ===============================================================

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
APP_NAME="TecnoCursos AI"
LOG_LEVEL=${LOG_LEVEL:-INFO}
ENVIRONMENT=${ENVIRONMENT:-production}
MIGRATION_TIMEOUT=${MIGRATION_TIMEOUT:-300}
HEALTH_CHECK_TIMEOUT=${HEALTH_CHECK_TIMEOUT:-30}

# Função de logging
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)
            echo -e "${GREEN}[${timestamp}] INFO:${NC} ${message}"
            ;;
        WARN)
            echo -e "${YELLOW}[${timestamp}] WARN:${NC} ${message}"
            ;;
        ERROR)
            echo -e "${RED}[${timestamp}] ERROR:${NC} ${message}"
            ;;
        DEBUG)
            if [ "$LOG_LEVEL" = "DEBUG" ]; then
                echo -e "${BLUE}[${timestamp}] DEBUG:${NC} ${message}"
            fi
            ;;
    esac
}

# Função para verificar variáveis obrigatórias
check_required_env() {
    log INFO "Verificando variáveis de ambiente obrigatórias..."
    
    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log ERROR "Variáveis de ambiente obrigatórias não definidas:"
        for var in "${missing_vars[@]}"; do
            log ERROR "  - $var"
        done
        exit 1
    fi
    
    log INFO "✅ Todas as variáveis obrigatórias estão definidas"
}

# Função para aguardar disponibilidade do banco
wait_for_database() {
    log INFO "Aguardando disponibilidade do banco de dados..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
try:
    engine = create_engine('$DATABASE_URL')
    engine.execute('SELECT 1')
    print('Database is ready!')
    sys.exit(0)
except OperationalError as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error: {e}')
    sys.exit(1)
" 2>/dev/null; then
            log INFO "✅ Banco de dados está disponível"
            return 0
        fi
        
        log WARN "Banco de dados não disponível (tentativa $attempt/$max_attempts)"
        attempt=$((attempt + 1))
        sleep 5
    done
    
    log ERROR "❌ Timeout aguardando banco de dados"
    exit 1
}

# Função para verificar/executar migrações
run_migrations() {
    log INFO "Verificando migrações do banco de dados..."
    
    # Verificar se alembic está configurado
    if [ ! -f "alembic.ini" ]; then
        log WARN "alembic.ini não encontrado, pulando migrações"
        return 0
    fi
    
    # Verificar versão atual
    local current_version
    current_version=$(python -c "
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

try:
    engine = create_engine('$DATABASE_URL')
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
    print(current_rev or 'None')
except Exception as e:
    print('None')
" 2>/dev/null || echo "None")
    
    log INFO "Versão atual do banco: $current_version"
    
    # Executar migrações se necessário
    timeout $MIGRATION_TIMEOUT python -c "
from alembic.config import Config
from alembic import command
import sys

try:
    alembic_cfg = Config('alembic.ini')
    command.upgrade(alembic_cfg, 'head')
    print('Migrations completed successfully')
except Exception as e:
    print(f'Migration failed: {e}')
    sys.exit(1)
" || {
        log ERROR "❌ Falha nas migrações do banco de dados"
        exit 1
    }
    
    log INFO "✅ Migrações executadas com sucesso"
}

# Função para configurar diretórios
setup_directories() {
    log INFO "Configurando diretórios da aplicação..."
    
    local dirs=(
        "/app/logs"
        "/app/uploads"
        "/app/cache"
        "/app/backups"
        "/tmp/prometheus"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log DEBUG "Criado diretório: $dir"
        fi
        
        # Verificar permissões
        if [ ! -w "$dir" ]; then
            log WARN "Sem permissão de escrita em: $dir"
        fi
    done
    
    log INFO "✅ Diretórios configurados"
}

# Função para configurar cache
setup_cache() {
    log INFO "Configurando sistema de cache..."
    
    # Verificar Redis se configurado
    if [ -n "${REDIS_HOST:-}" ]; then
        local redis_available=false
        
        # Tentar conectar ao Redis
        if python -c "
import redis
import sys
try:
    r = redis.Redis(host='$REDIS_HOST', port=${REDIS_PORT:-6379}, db=${REDIS_DB:-0})
    r.ping()
    print('Redis is available')
    sys.exit(0)
except Exception as e:
    print(f'Redis not available: {e}')
    sys.exit(1)
" 2>/dev/null; then
            redis_available=true
            log INFO "✅ Redis cache disponível"
        else
            log WARN "⚠️  Redis não disponível, usando cache local"
        fi
    else
        log INFO "Redis não configurado, usando cache local"
    fi
    
    # Limpar cache antigo se necessário
    if [ -d "/app/cache" ]; then
        find /app/cache -type f -mtime +7 -delete 2>/dev/null || true
        log DEBUG "Cache antigo limpo"
    fi
}

# Função para verificar APIs externas
check_external_apis() {
    log INFO "Verificando APIs externas..."
    
    local apis=(
        "OpenAI:OPENAI_API_KEY"
        "D-ID:D_ID_API_KEY"
        "ElevenLabs:ELEVENLABS_API_KEY"
        "Stripe:STRIPE_API_KEY"
    )
    
    for api_info in "${apis[@]}"; do
        local api_name=$(echo "$api_info" | cut -d: -f1)
        local env_var=$(echo "$api_info" | cut -d: -f2)
        
        if [ -n "${!env_var:-}" ]; then
            log INFO "✅ $api_name API configurada"
        else
            log WARN "⚠️  $api_name API não configurada ($env_var)"
        fi
    done
}

# Função para configurar monitoramento
setup_monitoring() {
    log INFO "Configurando monitoramento..."
    
    # Configurar Prometheus se disponível
    if [ -n "${PROMETHEUS_MULTIPROC_DIR:-}" ]; then
        mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
        # Limpar métricas antigas
        rm -f "$PROMETHEUS_MULTIPROC_DIR"/*.db 2>/dev/null || true
        log INFO "✅ Prometheus configurado"
    fi
    
    # Configurar logging
    export PYTHONPATH="${PYTHONPATH:-}:/app"
    log INFO "✅ Logging configurado"
}

# Função para health check interno
internal_health_check() {
    log INFO "Executando health check interno..."
    
    # Verificar se a aplicação consegue importar módulos principais
    python -c "
import sys
try:
    from app.main import app
    from app.database import get_db
    from app.config import settings
    print('Application modules loaded successfully')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error: {e}')
    sys.exit(1)
" || {
        log ERROR "❌ Falha no health check interno"
        exit 1
    }
    
    log INFO "✅ Health check interno passou"
}

# Função para configurar workers baseado em recursos
configure_workers() {
    log INFO "Configurando workers baseado em recursos disponíveis..."
    
    # Detectar CPU cores
    local cpu_cores
    cpu_cores=$(nproc 2>/dev/null || echo 1)
    
    # Detectar memória disponível (em GB)
    local memory_gb
    memory_gb=$(python -c "
import psutil
memory_bytes = psutil.virtual_memory().total
memory_gb = memory_bytes / (1024**3)
print(int(memory_gb))
" 2>/dev/null || echo 1)
    
    # Calcular workers otimizados
    local optimal_workers
    optimal_workers=$((cpu_cores * 2 + 1))
    
    # Limitar baseado na memória (assumindo ~512MB por worker)
    local memory_limit=$((memory_gb * 2))
    if [ $optimal_workers -gt $memory_limit ]; then
        optimal_workers=$memory_limit
    fi
    
    # Garantir mínimo e máximo
    if [ $optimal_workers -lt 2 ]; then
        optimal_workers=2
    elif [ $optimal_workers -gt 16 ]; then
        optimal_workers=16
    fi
    
    export MAX_WORKERS=${MAX_WORKERS:-$optimal_workers}
    
    log INFO "🔧 Recursos detectados: ${cpu_cores} CPU cores, ${memory_gb}GB RAM"
    log INFO "🔧 Workers configurados: $MAX_WORKERS"
}

# Função para aguardar dependências externas
wait_for_dependencies() {
    log INFO "Aguardando dependências externas..."
    
    # Lista de serviços para aguardar
    local dependencies=()
    
    # Adicionar Redis se configurado
    if [ -n "${REDIS_HOST:-}" ]; then
        dependencies+=("redis:${REDIS_HOST}:${REDIS_PORT:-6379}")
    fi
    
    # Aguardar cada dependência
    for dep in "${dependencies[@]}"; do
        local service=$(echo "$dep" | cut -d: -f1)
        local host=$(echo "$dep" | cut -d: -f2)
        local port=$(echo "$dep" | cut -d: -f3)
        
        log INFO "Aguardando $service em $host:$port..."
        
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
                log INFO "✅ $service está disponível"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log WARN "⚠️  Timeout aguardando $service, continuando mesmo assim"
                break
            fi
            
            log DEBUG "$service não disponível (tentativa $attempt/$max_attempts)"
            attempt=$((attempt + 1))
            sleep 2
        done
    done
}

# Função para limpeza no exit
cleanup() {
    log INFO "Realizando limpeza antes do exit..."
    
    # Limpar arquivos temporários
    rm -f /tmp/*.tmp 2>/dev/null || true
    
    # Limpar métricas do Prometheus
    if [ -n "${PROMETHEUS_MULTIPROC_DIR:-}" ]; then
        rm -f "$PROMETHEUS_MULTIPROC_DIR"/*.db 2>/dev/null || true
    fi
    
    log INFO "✅ Limpeza concluída"
}

# Configurar trap para limpeza
trap cleanup EXIT

# ===============================================================
# MAIN EXECUTION
# ===============================================================

main() {
    log INFO "🚀 Iniciando $APP_NAME ($ENVIRONMENT)"
    log INFO "🐳 Container PID: $$"
    
    # Verificações pré-inicialização
    check_required_env
    setup_directories
    configure_workers
    
    # Aguardar dependências
    wait_for_dependencies
    wait_for_database
    
    # Configurar aplicação
    run_migrations
    setup_cache
    setup_monitoring
    
    # Verificações finais
    check_external_apis
    internal_health_check
    
    log INFO "✅ Inicialização concluída com sucesso!"
    log INFO "🎯 Executando comando: $*"
    
    # Executar comando principal
    exec "$@"
}

# Verificar se script está sendo executado diretamente
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi 