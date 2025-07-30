# TecnoCursos AI - Inicializador PowerShell
# Execute este arquivo clicando com botão direito > "Executar com PowerShell"

Write-Host "🚀 INICIALIZANDO TecnoCursos AI" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Verificar Python
Write-Host "📋 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "🔧 Instale Python de: https://python.org" -ForegroundColor Yellow
    Read-Host "Pressione Enter para continuar"
    exit
}

# Instalar dependências
Write-Host ""
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
try {
    pip install fastapi uvicorn python-multipart pyjwt --quiet --user
    Write-Host "✅ Dependências instaladas" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao instalar dependências, continuando..." -ForegroundColor Yellow
}

# Verificar arquivo
Write-Host ""
Write-Host "📁 Verificando arquivos..." -ForegroundColor Yellow
if (Test-Path "simple_backend.py") {
    Write-Host "✅ Arquivo simple_backend.py encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Arquivo simple_backend.py não encontrado!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit
}

# Iniciar servidor
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "🌐 URL: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "❤️ Health: http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔑 CREDENCIAIS DE TESTE:" -ForegroundColor Yellow
Write-Host "   Admin: admin@tecnocursos.com / admin123" -ForegroundColor White
Write-Host "   User: user@tecnocursos.com / user123" -ForegroundColor White
Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "⌨️ Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Abrir navegador em background
Start-Process "http://127.0.0.1:8000"

# Executar servidor
try {
    python simple_backend.py
} catch {
    Write-Host ""
    Write-Host "❌ Erro ao iniciar servidor!" -ForegroundColor Red
    Write-Host "🔧 Tente executar manualmente:" -ForegroundColor Yellow
    Write-Host "   python simple_backend.py" -ForegroundColor White
    Write-Host "   ou" -ForegroundColor White
    Write-Host "   uvicorn simple_backend:app --host 127.0.0.1 --port 8000" -ForegroundColor White
}

Write-Host ""
Write-Host "✅ Servidor finalizado" -ForegroundColor Green
Read-Host "Pressione Enter para fechar"
