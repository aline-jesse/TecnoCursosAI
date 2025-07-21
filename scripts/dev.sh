#!/bin/bash

# =================================================================
# SCRIPT DE DESENVOLVIMENTO - TECNOCURSOS AI EDITOR
# Inicia frontend React e backend FastAPI simultaneamente
# =================================================================

echo "🚀 Iniciando TecnoCursos AI Editor - Modo Desenvolvimento"
echo "========================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para verificar se uma porta está em uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Porta em uso
    else
        return 1  # Porta livre
    fi
}

# Função para matar processos em uma porta
kill_port() {
    local port=$1
    echo -e "${YELLOW}Matando processos na porta $port...${NC}"
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 1
}

# Verificar dependências
echo -e "${BLUE}📦 Verificando dependências...${NC}"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado. Instale Node.js v16 ou superior.${NC}"
    exit 1
fi

# Verificar Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python não encontrado. Instale Python 3.8 ou superior.${NC}"
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm não encontrado. Instale npm.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependências verificadas${NC}"

# Verificar portas
FRONTEND_PORT=3000
BACKEND_PORT=8000

if check_port $FRONTEND_PORT; then
    echo -e "${YELLOW}⚠️ Porta $FRONTEND_PORT (frontend) em uso${NC}"
    read -p "Deseja matar o processo? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port $FRONTEND_PORT
    else
        echo -e "${RED}❌ Cancelado pelo usuário${NC}"
        exit 1
    fi
fi

if check_port $BACKEND_PORT; then
    echo -e "${YELLOW}⚠️ Porta $BACKEND_PORT (backend) em uso${NC}"
    read -p "Deseja matar o processo? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port $BACKEND_PORT
    else
        echo -e "${RED}❌ Cancelado pelo usuário${NC}"
        exit 1
    fi
fi

# Instalar dependências se necessário
echo -e "${BLUE}📥 Verificando instalação de dependências...${NC}"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependências npm...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro na instalação das dependências npm${NC}"
        exit 1
    fi
fi

# Verificar se venv existe
if [ ! -d "venv" ] && [ ! -d ".venv" ] && [ ! -d "env" ]; then
    echo -e "${YELLOW}🐍 Criando ambiente virtual Python...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${BLUE}🐍 Ativando ambiente virtual Python...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "env" ]; then
        source env/bin/activate
    fi
fi

# Função para cleanup ao sair
cleanup() {
    echo -e "\n${YELLOW}🔄 Finalizando processos...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    echo -e "${GREEN}✅ Processos finalizados${NC}"
    exit 0
}

# Trap para cleanup
trap cleanup SIGINT SIGTERM

# Iniciar backend
echo -e "${BLUE}🔧 Iniciando backend FastAPI na porta $BACKEND_PORT...${NC}"
(
    cd ../
    python tecnocursos_server.py &
    BACKEND_PID=$!
    
    # Aguardar backend inicializar
    echo "Aguardando backend inicializar..."
    sleep 5
    
    # Verificar se backend está rodando
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Backend iniciado com sucesso (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}❌ Falha ao iniciar backend${NC}"
        exit 1
    fi
    
    wait $BACKEND_PID
) &

# Aguardar um pouco antes de iniciar frontend
sleep 3

# Iniciar frontend
echo -e "${BLUE}⚛️ Iniciando frontend React na porta $FRONTEND_PORT...${NC}"
(
    BROWSER=none npm start &
    FRONTEND_PID=$!
    
    # Aguardar frontend inicializar
    echo "Aguardando frontend inicializar..."
    sleep 10
    
    # Verificar se frontend está rodando
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Frontend iniciado com sucesso (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${RED}❌ Falha ao iniciar frontend${NC}"
        exit 1
    fi
    
    wait $FRONTEND_PID
) &

# Aguardar ambos os serviços inicializarem
sleep 5

echo ""
echo "🎉 SISTEMA INICIADO COM SUCESSO!"
echo "================================="
echo -e "${GREEN}🌐 Frontend (React):${NC} http://localhost:$FRONTEND_PORT"
echo -e "${GREEN}🔧 Backend (FastAPI):${NC} http://localhost:$BACKEND_PORT"
echo -e "${GREEN}📚 API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}💚 Health Check:${NC} http://localhost:$BACKEND_PORT/api/health"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "  - Frontend: Terminal atual"
echo "  - Backend: Terminal atual"
echo ""
echo -e "${YELLOW}⌨️ Comandos:${NC}"
echo "  - Ctrl+C: Parar todos os serviços"
echo "  - Ctrl+Z: Suspender (não recomendado)"
echo ""
echo -e "${BLUE}🔄 Aguardando... (Ctrl+C para parar)${NC}"

# Aguardar até que o usuário pare manualmente
wait 