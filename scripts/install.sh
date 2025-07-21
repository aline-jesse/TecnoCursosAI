#!/bin/bash

# Script de Instalação Completa - TecnoCursosAI
# Sistema de Upload e Processamento de Arquivos PDF/PPTX
# 
# Este script instala e configura todo o ambiente de produção:
# - Dependências do sistema
# - MySQL
# - Python e ambiente virtual
# - Nginx
# - Certificados SSL
# - Serviços systemd
# - Configurações de segurança

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="tecnocursos"
PROJECT_DIR="/opt/${PROJECT_NAME}"
SERVICE_USER="${PROJECT_NAME}"
MYSQL_ROOT_PASSWORD=""
MYSQL_DB_PASSWORD=""
DOMAIN="tecnocursos.ai"
EMAIL="admin@${DOMAIN}"

# Funções auxiliares
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

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script deve ser executado como root"
        exit 1
    fi
}

check_os() {
    if ! grep -q "Ubuntu\|Debian" /etc/os-release; then
        log_error "Este script é compatível apenas com Ubuntu/Debian"
        exit 1
    fi
    
    log_info "Sistema operacional: $(lsb_release -d | cut -f2)"
}

prompt_passwords() {
    log_info "Configuração de senhas do banco de dados"
    
    if [[ -z "$MYSQL_ROOT_PASSWORD" ]]; then
        while true; do
            read -s -p "Digite a senha para o root do MySQL: " MYSQL_ROOT_PASSWORD
            echo
            read -s -p "Confirme a senha: " password_confirm
            echo
            
            if [[ "$MYSQL_ROOT_PASSWORD" == "$password_confirm" ]]; then
                break
            else
                log_error "Senhas não coincidem. Tente novamente."
            fi
        done
    fi
    
    if [[ -z "$MYSQL_DB_PASSWORD" ]]; then
        MYSQL_DB_PASSWORD=$(openssl rand -base64 32)
        log_info "Senha do banco de dados gerada automaticamente"
    fi
}

install_system_dependencies() {
    log_info "Atualizando sistema e instalando dependências..."
    
    apt-get update
    apt-get upgrade -y
    
    # Dependências básicas
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        ufw \
        fail2ban \
        htop \
        tree \
        vim \
        nano
    
    log_success "Dependências básicas instaladas"
}

install_python() {
    log_info "Instalando Python 3.11 e dependências..."
    
    # Adicionar repositório Python
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get update
    
    # Instalar Python 3.11
    apt-get install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip \
        build-essential \
        libmysqlclient-dev \
        pkg-config
    
    # Criar link simbólico
    ln -sf /usr/bin/python3.11 /usr/bin/python3
    
    log_success "Python 3.11 instalado"
}

install_mysql() {
    log_info "Instalando MySQL Server..."
    
    # Configurar senha antes da instalação
    debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQL_ROOT_PASSWORD"
    debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD"
    
    apt-get install -y mysql-server mysql-client
    
    # Configurar MySQL
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS tecnocursos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'tecnocursos'@'localhost' IDENTIFIED BY '$MYSQL_DB_PASSWORD';
GRANT ALL PRIVILEGES ON tecnocursos.* TO 'tecnocursos'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    # Configurar MySQL para performance
    cat > /etc/mysql/mysql.conf.d/tecnocursos.cnf <<EOF
[mysqld]
# TecnoCursosAI MySQL Configuration
max_connections = 200
innodb_buffer_pool_size = 512M
innodb_log_file_size = 64M
innodb_file_per_table = 1
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
EOF
    
    systemctl restart mysql
    systemctl enable mysql
    
    log_success "MySQL instalado e configurado"
}

install_nginx() {
    log_info "Instalando Nginx..."
    
    apt-get install -y nginx
    
    # Remover configuração padrão
    rm -f /etc/nginx/sites-enabled/default
    
    # Criar diretórios
    mkdir -p /var/www/${PROJECT_NAME}/errors
    mkdir -p /var/cache/nginx/${PROJECT_NAME}
    
    # Páginas de erro customizadas
    cat > /var/www/${PROJECT_NAME}/errors/404.html <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>404 - Página não encontrada</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>404 - Página não encontrada</h1>
    <p>A página que você está procurando não existe.</p>
    <a href="/">Voltar ao início</a>
</body>
</html>
EOF
    
    cat > /var/www/${PROJECT_NAME}/errors/50x.html <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>500 - Erro interno</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #d32f2f; }
    </style>
</head>
<body>
    <h1>500 - Erro interno do servidor</h1>
    <p>Ocorreu um erro interno. Nossa equipe foi notificada.</p>
    <a href="/">Voltar ao início</a>
</body>
</html>
EOF
    
    # Copiar configuração do Nginx
    if [[ -f "nginx/tecnocursos.conf" ]]; then
        cp nginx/tecnocursos.conf /etc/nginx/sites-available/${PROJECT_NAME}
        ln -sf /etc/nginx/sites-available/${PROJECT_NAME} /etc/nginx/sites-enabled/
    else
        log_warning "Arquivo de configuração nginx/tecnocursos.conf não encontrado"
    fi
    
    # Testar configuração
    nginx -t
    
    systemctl restart nginx
    systemctl enable nginx
    
    log_success "Nginx instalado e configurado"
}

create_user() {
    log_info "Criando usuário do sistema..."
    
    # Criar grupo e usuário
    groupadd -f ${SERVICE_USER}
    useradd -r -g ${SERVICE_USER} -d ${PROJECT_DIR} -s /bin/bash ${SERVICE_USER} 2>/dev/null || true
    
    # Criar diretórios
    mkdir -p ${PROJECT_DIR}
    mkdir -p ${PROJECT_DIR}/logs
    mkdir -p ${PROJECT_DIR}/backups
    
    log_success "Usuário ${SERVICE_USER} criado"
}

install_application() {
    log_info "Instalando aplicação..."
    
    # Copiar arquivos do projeto
    cp -r . ${PROJECT_DIR}/
    
    # Criar ambiente virtual
    cd ${PROJECT_DIR}
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Instalar dependências
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Criar arquivo .env
    cat > ${PROJECT_DIR}/.env <<EOF
# TecnoCursosAI Production Environment
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$(openssl rand -base64 32)
DATABASE_URL=mysql://tecnocursos:${MYSQL_DB_PASSWORD}@localhost/tecnocursos
PORT=8000
HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# File Upload
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=pdf,pptx
UPLOAD_DIR=app/static/uploads

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email (configure conforme necessário)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=noreply@${DOMAIN}

# Monitoring
ENABLE_MONITORING=true
ALERT_EMAIL=${EMAIL}
EOF
    
    # Configurar permissões
    chown -R ${SERVICE_USER}:${SERVICE_USER} ${PROJECT_DIR}
    chmod -R 755 ${PROJECT_DIR}
    chmod -R 775 ${PROJECT_DIR}/app/static
    chmod -R 775 ${PROJECT_DIR}/logs
    chmod 600 ${PROJECT_DIR}/.env
    
    log_success "Aplicação instalada"
}

setup_database() {
    log_info "Configurando banco de dados..."
    
    cd ${PROJECT_DIR}
    source venv/bin/activate
    
    # Executar migrações
    alembic upgrade head
    
    # Inicializar dados
    if [[ -f "scripts/init_data.py" ]]; then
        python scripts/init_data.py
    fi
    
    log_success "Banco de dados configurado"
}

install_systemd_service() {
    log_info "Instalando serviço systemd..."
    
    # Copiar arquivo de serviço
    if [[ -f "systemd/tecnocursos.service" ]]; then
        cp systemd/tecnocursos.service /etc/systemd/system/
        
        # Recarregar systemd
        systemctl daemon-reload
        systemctl enable tecnocursos.service
        
        log_success "Serviço systemd instalado"
    else
        log_warning "Arquivo systemd/tecnocursos.service não encontrado"
    fi
}

setup_ssl() {
    log_info "Configurando SSL com Let's Encrypt..."
    
    # Instalar certbot
    apt-get install -y certbot python3-certbot-nginx
    
    # Obter certificado (apenas se o domínio resolver)
    if dig +short ${DOMAIN} >/dev/null 2>&1; then
        certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --email ${EMAIL} --agree-tos --non-interactive
        log_success "SSL configurado para ${DOMAIN}"
    else
        log_warning "Domínio ${DOMAIN} não resolve. SSL não configurado."
        log_info "Configure manualmente: certbot --nginx -d ${DOMAIN}"
    fi
}

setup_firewall() {
    log_info "Configurando firewall..."
    
    # Configurar UFW
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Permitir conexões necessárias
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Ativar firewall
    ufw --force enable
    
    log_success "Firewall configurado"
}

setup_fail2ban() {
    log_info "Configurando Fail2Ban..."
    
    # Configurar jail para Nginx
    cat > /etc/fail2ban/jail.d/nginx.conf <<EOF
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF
    
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    log_success "Fail2Ban configurado"
}

setup_monitoring() {
    log_info "Configurando monitoramento..."
    
    # Criar script de monitoramento como serviço
    cat > /etc/systemd/system/tecnocursos-monitor.service <<EOF
[Unit]
Description=TecnoCursosAI Monitoring Service
After=tecnocursos.service
Requires=tecnocursos.service

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${PROJECT_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=${PROJECT_DIR}/venv/bin/python scripts/monitor.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable tecnocursos-monitor.service
    
    log_success "Monitoramento configurado"
}

setup_logrotate() {
    log_info "Configurando rotação de logs..."
    
    cat > /etc/logrotate.d/tecnocursos <<EOF
${PROJECT_DIR}/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ${SERVICE_USER} ${SERVICE_USER}
    postrotate
        systemctl reload tecnocursos
    endscript
}

/var/log/nginx/tecnocursos*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx
    endscript
}
EOF
    
    log_success "Rotação de logs configurada"
}

setup_backup_cron() {
    log_info "Configurando backup automático..."
    
    # Criar script de backup diário
    cat > /etc/cron.d/tecnocursos-backup <<EOF
# TecnoCursosAI Backup Automático
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Backup diário às 02:00
0 2 * * * ${SERVICE_USER} cd ${PROJECT_DIR} && ${PROJECT_DIR}/venv/bin/python scripts/backup.py --keep-days 30

# Limpeza de logs antigos às 03:00
0 3 * * * ${SERVICE_USER} find ${PROJECT_DIR}/logs -name "*.log.*" -mtime +30 -delete
EOF
    
    log_success "Backup automático configurado"
}

start_services() {
    log_info "Iniciando serviços..."
    
    # Iniciar aplicação
    systemctl start tecnocursos.service
    systemctl start tecnocursos-monitor.service
    
    # Verificar status
    sleep 5
    
    if systemctl is-active --quiet tecnocursos.service; then
        log_success "TecnoCursosAI iniciado com sucesso"
    else
        log_error "Falha ao iniciar TecnoCursosAI"
        systemctl status tecnocursos.service
        exit 1
    fi
}

print_summary() {
    log_success "Instalação concluída com sucesso!"
    echo
    echo "==================== RESUMO ===================="
    echo "Projeto: TecnoCursosAI"
    echo "Diretório: ${PROJECT_DIR}"
    echo "Usuário: ${SERVICE_USER}"
    echo "Banco de dados: MySQL (tecnocursos)"
    echo "Servidor web: Nginx"
    echo
    echo "URLs:"
    echo "  - Aplicação: http://localhost:8080"
    echo "  - Documentação: http://localhost:8080/docs"
    echo "  - Health Check: http://localhost:8080/health"
    echo
    echo "Comandos úteis:"
    echo "  - Status: systemctl status tecnocursos"
    echo "  - Logs: journalctl -u tecnocursos -f"
    echo "  - Restart: systemctl restart tecnocursos"
    echo "  - Monitor: systemctl status tecnocursos-monitor"
    echo
    echo "Arquivos importantes:"
    echo "  - Configuração: ${PROJECT_DIR}/.env"
    echo "  - Logs: ${PROJECT_DIR}/logs/"
    echo "  - Uploads: ${PROJECT_DIR}/app/static/"
    echo "  - Backups: ${PROJECT_DIR}/backups/"
    echo
    echo "Credenciais padrão:"
    echo "  - Admin: admin@tecnocursos.ai / TecnoCursos2024!"
    echo "  - MySQL root: ${MYSQL_ROOT_PASSWORD}"
    echo "================================================="
    echo
    log_info "Verifique os logs em caso de problemas:"
    log_info "  journalctl -u tecnocursos -f"
}

main() {
    echo "========================================="
    echo "    TecnoCursosAI - Instalação Completa"
    echo "========================================="
    echo
    
    check_root
    check_os
    prompt_passwords
    
    log_info "Iniciando instalação..."
    
    install_system_dependencies
    install_python
    install_mysql
    install_nginx
    create_user
    install_application
    setup_database
    install_systemd_service
    setup_ssl
    setup_firewall
    setup_fail2ban
    setup_monitoring
    setup_logrotate
    setup_backup_cron
    start_services
    
    print_summary
}

# Executar instalação
main "$@" 