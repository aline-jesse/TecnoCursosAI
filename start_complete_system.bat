@echo off
title TecnoCursosAI - Sistema Completo
echo ===============================================
echo    TecnoCursosAI - Iniciando Sistema Completo
echo ===============================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não está instalado!
    echo Por favor, instale Python 3.13 ou superior
    pause
    exit /b 1
)

REM Verifica se Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js não está instalado!
    echo Por favor, instale Node.js
    pause
    exit /b 1
)

echo [1/4] Iniciando Backend (FastAPI)...
start /B cmd /c "cd /d %~dp0 && python start_production_server.py"

echo [2/4] Aguardando Backend inicializar...
timeout /t 5 /nobreak >nul

echo [3/4] Verificando Backend...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -ErrorAction Stop; Write-Host '[OK] Backend está rodando!' -ForegroundColor Green } catch { Write-Host '[ERRO] Backend não está respondendo!' -ForegroundColor Red }"

echo [4/4] Iniciando Frontend (React)...
start /B cmd /c "cd /d %~dp0frontend && npm start"

echo.
echo ===============================================
echo    Sistema Iniciado com Sucesso!
echo ===============================================
echo.
echo URLs Disponíveis:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/api/health
echo.
echo Aguardando 10 segundos para abrir o navegador...
timeout /t 10 /nobreak >nul

echo Abrindo aplicação no navegador...
start http://localhost:3000
start http://localhost:8000/docs

echo.
echo ===============================================
echo    Sistema está rodando!
echo    Pressione Ctrl+C para parar
echo ===============================================
echo.
pause 