#!/bin/bash

# ============================================================================
# 🚀 TecnoCursos AI - Script de Deployment Completo
# Deploy Frontend React + Backend FastAPI em ambiente de produção
# ============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de logging
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

# Verificar se está rodando como root (para instalações do sistema)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Rodando como root. Certifique-se de que isso é necessário."
    fi
}

# Detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get >/dev/null; then
            DISTRO="ubuntu"
        elif command -v yum >/dev/null; then
            DISTRO="centos"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    fi
    
    log_info "Sistema detectado: $OS ($DISTRO)"
}

# Verificar dependências necessárias
check_dependencies() {
    log_info "Verificando dependências..."
    
    # Node.js
    if ! command -v node >/dev/null; then
        log_error "Node.js não encontrado. Instale o Node.js 18+ primeiro."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
    if [[ $NODE_VERSION -lt 18 ]]; then
        log_error "Node.js versão 18+ necessária. Versão atual: $NODE_VERSION"
        exit 1
    fi
    
    # Python
    if ! command -v python3 >/dev/null; then
        log_error "Python 3 não encontrado. Instale Python 3.8+ primeiro."
        exit 1
    fi
    
    # npm
    if ! command -v npm >/dev/null; then
        log_error "npm não encontrado. Instale npm primeiro."
        exit 1
    fi
    
    # pip
    if ! command -v pip3 >/dev/null; then
        log_error "pip3 não encontrado. Instale pip3 primeiro."
        exit 1
    fi
    
    log_success "Todas as dependências encontradas!"
}

# Configurar ambiente Python
setup_python_env() {
    log_info "Configurando ambiente Python..."
    
    # Criar ambiente virtual se não existir
    if [[ ! -d "venv" ]]; then
        log_info "Criando ambiente virtual Python..."
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual
    log_info "Ativando ambiente virtual..."
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    # Atualizar pip
    log_info "Atualizando pip..."
    pip install --upgrade pip
    
    # Instalar dependências
    log_info "Instalando dependências Python..."
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        log_error "requirements.txt não encontrado!"
        exit 1
    fi
    
    log_success "Ambiente Python configurado!"
}

# Configurar ambiente Node.js
setup_node_env() {
    log_info "Configurando ambiente Node.js..."
    
    # Verificar se existe package.json
    if [[ ! -f "package.json" ]]; then
        log_error "package.json não encontrado no diretório atual!"
        exit 1
    fi
    
    # Instalar dependências
    log_info "Instalando dependências Node.js..."
    npm install
    
    log_success "Ambiente Node.js configurado!"
}

# Build do frontend
build_frontend() {
    log_info "Fazendo build do frontend React..."
    
    # Verificar se estamos no diretório correto
    if [[ ! -f "next.config.js" ]]; then
        log_error "next.config.js não encontrado. Certifique-se de estar no diretório do frontend."
        exit 1
    fi
    
    # Configurar variáveis de ambiente para produção
    if [[ ! -f ".env.production" ]]; then
        log_info "Criando arquivo .env.production..."
        cat > .env.production << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NODE_ENV=production
EOF
    fi
    
    # Build
    log_info "Executando build do Next.js..."
    npm run build
    
    log_success "Build do frontend concluído!"
}

# Configurar banco de dados
setup_database() {
    log_info "Configurando banco de dados..."
    
    # Ativar ambiente virtual
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    # Verificar se existe arquivo de migração
    if [[ -d "alembic" ]]; then
        log_info "Executando migrações do banco..."
        alembic upgrade head
    else
        log_warning "Pasta alembic não encontrada. Criando tabelas diretamente..."
        python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('Tabelas criadas com sucesso!')
"
    fi
    
    log_success "Banco de dados configurado!"
}

# Configurar Nginx (se disponível)
setup_nginx() {
    if command -v nginx >/dev/null; then
        log_info "Configurando Nginx..."
        
        # Criar configuração do Nginx
        if [[ ! -f "/etc/nginx/sites-available/tecnocursos" ]]; then
            log_info "Criando configuração do Nginx..."
            
            sudo tee /etc/nginx/sites-available/tecnocursos > /dev/null << 'EOF'
server {
    listen 80;
    server_name localhost;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Assets estáticos
    location /assets/ {
        alias /var/www/tecnocursos/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
            
            # Habilitar site
            sudo ln -sf /etc/nginx/sites-available/tecnocursos /etc/nginx/sites-enabled/
            
            # Testar configuração
            sudo nginx -t
            
            # Recarregar Nginx
            sudo systemctl reload nginx
            
            log_success "Nginx configurado!"
        else
            log_info "Configuração do Nginx já existe."
        fi
    else
        log_warning "Nginx não encontrado. Pule esta etapa se não for necessário."
    fi
}

# Criar serviços systemd
create_systemd_services() {
    if command -v systemctl >/dev/null; then
        log_info "Criando serviços systemd..."
        
        # Serviço do backend
        sudo tee /etc/systemd/system/tecnocursos-backend.service > /dev/null << EOF
[Unit]
Description=TecnoCursos AI Backend (FastAPI)
After=network.target

[Service]
Type=exec
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

        # Serviço do frontend
        sudo tee /etc/systemd/system/tecnocursos-frontend.service > /dev/null << EOF
[Unit]
Description=TecnoCursos AI Frontend (Next.js)
After=network.target

[Service]
Type=exec
User=$USER
WorkingDirectory=$(pwd)
Environment=NODE_ENV=production
ExecStart=$(which npm) start
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

        # Recarregar systemd
        sudo systemctl daemon-reload
        
        # Habilitar serviços
        sudo systemctl enable tecnocursos-backend.service
        sudo systemctl enable tecnocursos-frontend.service
        
        log_success "Serviços systemd criados!"
    else
        log_warning "systemctl não disponível. Serviços não foram criados."
    fi
}

# Iniciar serviços
start_services() {
    log_info "Iniciando serviços..."
    
    if command -v systemctl >/dev/null; then
        # Iniciar via systemd
        sudo systemctl start tecnocursos-backend.service
        sudo systemctl start tecnocursos-frontend.service
        
        # Verificar status
        sleep 3
        if systemctl is-active --quiet tecnocursos-backend.service; then
            log_success "Backend iniciado com sucesso!"
        else
            log_error "Falha ao iniciar backend. Verifique os logs: journalctl -u tecnocursos-backend.service"
        fi
        
        if systemctl is-active --quiet tecnocursos-frontend.service; then
            log_success "Frontend iniciado com sucesso!"
        else
            log_error "Falha ao iniciar frontend. Verifique os logs: journalctl -u tecnocursos-frontend.service"
        fi
    else
        # Iniciar manualmente (desenvolvimento)
        log_info "Iniciando serviços em modo desenvolvimento..."
        
        # Ativar ambiente virtual
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
        
        # Iniciar backend em background
        log_info "Iniciando backend..."
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        
        # Aguardar backend inicializar
        sleep 5
        
        # Iniciar frontend em background
        log_info "Iniciando frontend..."
        nohup npm start > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > frontend.pid
        
        log_success "Serviços iniciados em modo desenvolvimento!"
        log_info "Backend PID: $BACKEND_PID (log: backend.log)"
        log_info "Frontend PID: $FRONTEND_PID (log: frontend.log)"
    fi
}

# Função principal
main() {
    log_info "🚀 Iniciando deployment do TecnoCursos AI..."
    
    # Verificações iniciais
    check_root
    detect_os
    check_dependencies
    
    # Setup dos ambientes
    setup_python_env
    setup_node_env
    
    # Build do frontend
    build_frontend
    
    # Configurar banco de dados
    setup_database
    
    # Configurações de produção (opcionais)
    if [[ "$1" == "--production" ]]; then
        setup_nginx
        create_systemd_services
    fi
    
    # Iniciar serviços
    start_services
    
    # Informações finais
    echo ""
    log_success "🎉 Deployment concluído com sucesso!"
    echo ""
    log_info "📍 URLs de acesso:"
    log_info "   Frontend: http://localhost:3000"
    log_info "   Backend:  http://localhost:8000"
    log_info "   API Docs: http://localhost:8000/docs"
    echo ""
    
    if [[ "$1" == "--production" ]]; then
        log_info "🔧 Comandos úteis para produção:"
        log_info "   Verificar status: sudo systemctl status tecnocursos-backend.service"
        log_info "   Ver logs backend: journalctl -u tecnocursos-backend.service -f"
        log_info "   Ver logs frontend: journalctl -u tecnocursos-frontend.service -f"
        log_info "   Reiniciar: sudo systemctl restart tecnocursos-backend.service"
    else
        log_info "🔧 Comandos úteis para desenvolvimento:"
        log_info "   Parar backend: kill \$(cat backend.pid)"
        log_info "   Parar frontend: kill \$(cat frontend.pid)"
        log_info "   Ver logs backend: tail -f backend.log"
        log_info "   Ver logs frontend: tail -f frontend.log"
    fi
    
    echo ""
    log_info "Para modo produção, execute: $0 --production"
}

# Executar função principal
main "$@" 