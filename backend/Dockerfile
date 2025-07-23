# ===============================================================
# DOCKERFILE PARA TECNOCURSOSAI - SAAS UPLOAD DE ARQUIVOS
# Multi-stage build para otimização de tamanho e segurança
# ===============================================================

# ===== ESTÁGIO 1: BUILD =====
FROM python:3.11-slim as builder

# Metadados da imagem
LABEL maintainer="TecnoCursosAI <suporte@tecnocursosai.com>"
LABEL description="SaaS para upload de arquivos e geração de vídeos com IA"
LABEL version="1.0.0"

# Configurar variáveis de ambiente para build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema para build
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser

# Configurar diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===== ESTÁGIO 2: RUNTIME =====
FROM python:3.11-slim

# Configurar variáveis de ambiente para runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    PORT=8000

# Instalar dependências de runtime mínimas
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar usuário não-root
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser

# Criar diretórios necessários
RUN mkdir -p /app /app/logs /app/static/uploads /app/static/videos /app/static/thumbnails /app/app /app/scripts /app/database /app/docs && \
    chown -R appuser:appuser /app

# Configurar diretório de trabalho
WORKDIR /app

# Copiar dependências Python do estágio de build
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Garantir permissões corretas
RUN chown -R appuser:appuser /app && \
    chmod +x /app/start.sh

# Mudar para usuário não-root
USER appuser

# Expor porta da aplicação
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Comando padrão para iniciar aplicação
CMD ["sh", "/app/scripts/start.sh"] 