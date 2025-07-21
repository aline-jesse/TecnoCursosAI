#!/bin/bash

# ============================================
# INSTALAÇÃO AUTOMÁTICA - EDITOR REACT ANIMAKER
# TecnoCursos AI - Sistema Completo
# ============================================

echo "🎬 Instalando Editor de Vídeo React tipo Animaker..."
echo "=================================================="

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale Node.js 18+ antes de continuar."
    echo "   Download: https://nodejs.org/"
    exit 1
fi

# Verificar versão do Node.js
NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js versão 18+ é necessária. Versão atual: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detectado"

# Instalar dependências
echo ""
echo "📦 Instalando dependências do projeto..."
npm install

# Verificar se a instalação foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Criar arquivo de ambiente se não existir
if [ ! -f ".env.local" ]; then
    echo ""
    echo "⚙️  Criando arquivo de configuração..."
    cat > .env.local << EOL
# Editor React - TecnoCursos AI
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Configurações do editor
NEXT_PUBLIC_EDITOR_NAME="TecnoCursos AI Editor"
NEXT_PUBLIC_EDITOR_VERSION="1.0.0"

# Features flags (opcional)
NEXT_PUBLIC_ENABLE_COLLABORATION=false
NEXT_PUBLIC_ENABLE_CLOUD_SAVE=false
NEXT_PUBLIC_ENABLE_TEMPLATES=true
EOL
    echo "✅ Arquivo .env.local criado"
else
    echo "⚙️  Arquivo .env.local já existe"
fi

# Verificar se TailwindCSS está configurado
echo ""
echo "🎨 Verificando configuração do TailwindCSS..."
if [ -f "tailwind.config.js" ]; then
    echo "✅ TailwindCSS configurado"
else
    echo "❌ Configuração do TailwindCSS não encontrada"
fi

# Verificar se TypeScript está configurado
echo ""
echo "📝 Verificando configuração do TypeScript..."
if [ -f "tsconfig.json" ]; then
    echo "✅ TypeScript configurado"
else
    echo "❌ Configuração do TypeScript não encontrada"
fi

# Build do projeto para verificar se tudo está funcionando
echo ""
echo "🔨 Testando build do projeto..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build realizado com sucesso!"
    
    # Limpar build de teste
    rm -rf .next
    
    echo ""
    echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "=================================================="
    echo ""
    echo "🚀 Para iniciar o editor:"
    echo "   npm run dev"
    echo ""
    echo "🌐 Acesse o editor em:"
    echo "   http://localhost:3000/editor"
    echo ""
    echo "📚 Documentação completa:"
    echo "   README_EDITOR_REACT.md"
    echo ""
    echo "🛠️  Comandos disponíveis:"
    echo "   npm run dev      - Servidor de desenvolvimento"
    echo "   npm run build    - Build para produção"
    echo "   npm run start    - Servidor de produção"
    echo "   npm run lint     - Verificar código"
    echo "   npm run type-check - Verificar tipos TypeScript"
    echo ""
    echo "⚙️  Configurações:"
    echo "   - Backend API: $NEXT_PUBLIC_API_URL"
    echo "   - WebSocket: $NEXT_PUBLIC_WS_URL"
    echo ""
    echo "✨ O Editor React tipo Animaker está pronto para uso!"
    
else
    echo "❌ Erro no build do projeto"
    echo ""
    echo "🔍 Possíveis soluções:"
    echo "   1. Verifique se todas as dependências foram instaladas"
    echo "   2. Verifique a configuração do TypeScript"
    echo "   3. Execute: npm install --force"
    echo "   4. Execute: npm audit fix"
    echo ""
    exit 1
fi 