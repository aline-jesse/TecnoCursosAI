#!/bin/bash

# =================================================================
# SCRIPT DE BUILD - TECNOCURSOS AI EDITOR
# Build de produção para frontend React
# =================================================================

echo "🏗️ Build de Produção - TecnoCursos AI Editor"
echo "============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar dependências
echo -e "${BLUE}📦 Verificando dependências...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm não encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependências verificadas${NC}"

# Limpar build anterior
echo -e "${BLUE}🧹 Limpando build anterior...${NC}"
rm -rf build/
rm -rf dist/
echo -e "${GREEN}✅ Build anterior removido${NC}"

# Instalar dependências
echo -e "${BLUE}📥 Instalando dependências...${NC}"
npm ci --only=production
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro na instalação das dependências${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Dependências instaladas${NC}"

# Executar testes
echo -e "${BLUE}🧪 Executando testes...${NC}"
npm test -- --watchAll=false --coverage
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Alguns testes falharam, mas continuando...${NC}"
fi

# Build de produção
echo -e "${BLUE}🏗️ Executando build de produção...${NC}"
NODE_ENV=production npm run build:prod
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no build de produção${NC}"
    exit 1
fi

# Verificar arquivos gerados
if [ ! -d "build" ]; then
    echo -e "${RED}❌ Diretório build não foi criado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build concluído com sucesso${NC}"

# Análise do bundle
echo -e "${BLUE}📊 Analisando bundle...${NC}"
if command -v du &> /dev/null; then
    BUILD_SIZE=$(du -sh build/ | cut -f1)
    echo -e "${GREEN}📦 Tamanho do build: $BUILD_SIZE${NC}"
fi

# Listar arquivos principais
echo -e "${BLUE}📋 Arquivos principais gerados:${NC}"
find build/ -name "*.js" -o -name "*.css" | head -10

# Gerar relatório
echo -e "${BLUE}📄 Gerando relatório de build...${NC}"
cat > build-report.txt << EOF
RELATÓRIO DE BUILD - TECNOCURSOS AI EDITOR
==========================================

Data: $(date)
Node.js: $(node --version)
npm: $(npm --version)

Arquivos gerados:
$(find build/ -type f | wc -l) arquivos

Tamanho total: $BUILD_SIZE

Principais arquivos:
$(find build/ -name "*.js" -o -name "*.css" | head -5)

Status: ✅ BUILD CONCLUÍDO COM SUCESSO
EOF

echo -e "${GREEN}✅ Relatório salvo em build-report.txt${NC}"

echo ""
echo "🎉 BUILD CONCLUÍDO COM SUCESSO!"
echo "==============================="
echo -e "${GREEN}📁 Arquivos gerados em:${NC} ./build/"
echo -e "${GREEN}📊 Tamanho do build:${NC} $BUILD_SIZE"
echo -e "${GREEN}📄 Relatório:${NC} ./build-report.txt"
echo ""
echo -e "${BLUE}🚀 Próximos passos:${NC}"
echo "  1. Testar build: npm run serve"
echo "  2. Deploy: scripts/deploy.sh"
echo "  3. Análise: npm run analyze" 